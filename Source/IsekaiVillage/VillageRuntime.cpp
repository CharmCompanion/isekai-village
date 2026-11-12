// Copyright Epic Games, Inc. All Rights Reserved.
#include "VillageRuntime.h"
#include "VillageCitizen.h"
#include "TownPlot.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "EngineUtils.h"
#include "Engine/Engine.h"
#include "TownConstructionSave.h"
#include "Kismet/GameplayStatics.h"
#include "Components/SceneComponent.h"
#include "Components/BoxComponent.h"
#include "RoomVolume.h"
#include "LinchpinProp.h"

AVillageRuntime* AVillageRuntime::Get(const UObject* WorldContextObject)
{
	if (!WorldContextObject) return nullptr;
	UWorld* World = GEngine ? GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::ReturnNull) : nullptr;
	if (!World) return nullptr;
	for (TActorIterator<AVillageRuntime> It(World); It; ++It)
	{
		return *It;
	}
	return nullptr;
}

void AVillageRuntime::RegisterDynamicRoom(ARoomVolume* Room)
{
	if (!Room) return;
	if (!DynamicRooms.Contains(Room))
	{
		DynamicRooms.Add(Room);
	}
	ReconcileGolemPopulation();
}

void AVillageRuntime::UnregisterDynamicRoom(ARoomVolume* Room)
{
	if (!Room) return;
	DynamicRooms.Remove(Room);
	ReconcileGolemPopulation();
}

ARoomVolume* AVillageRuntime::FindDynamicRoom(FName RoomId) const
{
	for (ARoomVolume* Room : DynamicRooms)
	{
		if (Room && Room->GetFName() == RoomId)
		{
			return Room;
		}
	}
	return nullptr;
}

ALinchpinProp* AVillageRuntime::FindLinchpinPropInRoom(FName RoomId, FName PreferredTag) const
{
	ARoomVolume* Room = FindDynamicRoom(RoomId);
	if (!Room || !Room->Bounds)
	{
		return nullptr;
	}

	const FBox Box(Room->GetActorLocation() - Room->Bounds->GetScaledBoxExtent(), Room->GetActorLocation() + Room->Bounds->GetScaledBoxExtent());
	ALinchpinProp* Fallback = nullptr;
	for (TActorIterator<ALinchpinProp> It(GetWorld()); It; ++It)
	{
		if (Box.IsInside(It->GetActorLocation()))
		{
			if (PreferredTag.IsNone() || It->LinchpinTag == PreferredTag)
			{
				return *It;
			}
			if (!Fallback)
			{
				Fallback = *It;
			}
		}
	}
	return Fallback;
}

ALinchpinProp* AVillageRuntime::FindBedForGolem(const FVillageGolemRecord& Record) const
{
	if (ARoomVolume* Room = FindDynamicRoom(Record.HomePlot))
	{
		if (ALinchpinProp* Bed = FindLinchpinPropInRoom(Record.HomePlot, TEXT("Bed")))
		{
			return Bed;
		}
	}

	for (TActorIterator<ALinchpinProp> It(GetWorld()); It; ++It)
	{
		if (It->LinchpinTag == TEXT("Bed"))
		{
			return *It;
		}
	}
	return nullptr;
}

AVillageRuntime::AVillageRuntime()
{
	PrimaryActorTick.bCanEverTick = true;
	RootComponent = CreateDefaultSubobject<USceneComponent>(TEXT("VillageOrigin"));
	bLargeTown = false;
}

void AVillageRuntime::BeginPlay()
{
	Super::BeginPlay();
	InitializeConstruction();
	if (!bUseGolemVillage) SeedStarter();
	if (TodayMissions.IsEmpty()) RefreshMissions();
}

void AVillageRuntime::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	UpdatePlacementPreview();
	if (bUseGolemVillage) TickGolemVillage(DeltaSeconds);
	Accrued += DeltaSeconds;
	VisitAccrued += DeltaSeconds;
	if (Accrued >= WindowSeconds)
	{
		Accrued = 0.0f;
		TickWindow();
	}
	if (!bUseGolemVillage && VisitAccrued >= 48.0f)
	{
		VisitAccrued = 0.0f;
		if (VisitorCount() < 4 && ResidentCount() < 10)
		{
			const ECitizenOrigin Origins[] = {
				ECitizenOrigin::Yozuan, ECitizenOrigin::Kelsin, ECitizenOrigin::Rabaric,
				ECitizenOrigin::Vylfod, ECitizenOrigin::Gosain, ECitizenOrigin::ElRuhn
			};
			const ECitizenTrait Traits[] = {
				ECitizenTrait::Brave, ECitizenTrait::Cautious, ECitizenTrait::Greedy,
				ECitizenTrait::Lazy, ECitizenTrait::Earnest, ECitizenTrait::Stoic, ECitizenTrait::Cheerful
			};
			SpawnPerson(ECitizenStatus::Visitor, Origins[VisitSeed % 6], Traits[VisitSeed % 7]);
			++VisitSeed;
		}
	}
}

const AIsekaiVillageCharacter* AVillageRuntime::ActiveTownPlayer() const
{
	if (VillagePlayer.IsValid() && VillagePlayer->GetWorld() == GetWorld())
	{
		return VillagePlayer.Get();
	}
	return GetWorld() ? Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(GetWorld(), 0)) : nullptr;
}

FVillageOffer AVillageRuntime::BuildOffer() const
{
	FVillageOffer O;
	O.Food = 0.20f + FMath::Clamp(FoodStock / 24.0f, 0.0f, 0.5f);
	O.Beds = 0.20f;
	O.Safety = 0.20f - CrimeHeat * 0.02f;
	O.Coin = 0.15f + ShopCoin / 120.0f;
	O.Purpose = 0.15f;
	O.Faith = 0.10f;
	if (HasBuilding(ETownBuilding::Bakery) || HasBuilding(ETownBuilding::Farm)) O.Food += 0.25f;
	if (HasBuilding(ETownBuilding::Bath)) O.Food += 0.10f;
	if (HasBuilding(ETownBuilding::Inn)) O.Beds += 0.20f;
	if (HasBuilding(ETownBuilding::House)) O.Beds += 0.15f;
	if (HasBuilding(ETownBuilding::Training)) O.Safety += 0.15f;
	if (HasBuilding(ETownBuilding::Bell)) O.Safety += 0.15f;
	if (HasBuilding(ETownBuilding::Castle)) O.Safety += 0.20f;
	if (HasBuilding(ETownBuilding::Shop)) O.Coin += 0.15f;
	if (HasBuilding(ETownBuilding::Bank)) O.Coin += 0.20f;
	if (HasBuilding(ETownBuilding::Warehouse)) O.Coin += 0.08f;
	if (HasBuilding(ETownBuilding::Guild)) O.Purpose += 0.20f;
	if (HasBuilding(ETownBuilding::Academy)) O.Purpose += 0.20f;
	if (HasBuilding(ETownBuilding::Castle)) O.Purpose += 0.15f;
	if (HasBuilding(ETownBuilding::Chapel)) O.Faith += 0.25f;
	if (FestivalDays > 0)
	{
		O.Food += 0.2f;
		O.Coin += 0.1f;
	}
	if (StrikeHours > 0)
	{
		O.Coin -= 0.25f;
		O.Purpose -= 0.1f;
	}
	if (Weather == EVillageWeather::Drought)
	{
		O.Food -= 0.25f;
	}
	if (const AIsekaiVillageCharacter* Player = ActiveTownPlayer())
	{
		if (Player->HasSphereSkill(TEXT("CivicWatch")))
		{
			O.Safety += 0.10f;
		}
		if (FestivalDays > 0 && Player->HasSphereSkill(TEXT("FestivalProlong")))
		{
			O.Food += 0.15f;
			O.Coin += 0.10f;
		}
		const float AttractMult = 1.0f + FMath::Max(0.0f, Player->SphereTotals.AttractionPercent) / 100.0f;
		if (AttractMult > 1.0f)
		{
			O.Food *= AttractMult;
			O.Beds *= AttractMult;
			O.Safety *= AttractMult;
			O.Coin *= AttractMult;
			O.Purpose *= AttractMult;
			O.Faith *= AttractMult;
		}
	}
	O.FreeBeds = FreeBeds();
	return O;
}

FVector AVillageRuntime::PlaceLoc(EVillagePlace Place) const
{
	if (bUseAuthoredPlots)
	{
		ETownBuilding Kind = ETownBuilding::House;
		bool bBuilding = true;
		switch (Place)
		{
		case EVillagePlace::House: Kind = ETownBuilding::House; break;
		case EVillagePlace::Inn: Kind = ETownBuilding::Inn; break;
		case EVillagePlace::Bakery: Kind = ETownBuilding::Bakery; break;
		case EVillagePlace::Farm: Kind = ETownBuilding::Farm; break;
		case EVillagePlace::Guild: Kind = ETownBuilding::Guild; break;
		case EVillagePlace::Training: Kind = ETownBuilding::Training; break;
		case EVillagePlace::Smith: Kind = ETownBuilding::Smith; break;
		case EVillagePlace::Shop: Kind = ETownBuilding::Shop; break;
		case EVillagePlace::Chapel: Kind = ETownBuilding::Chapel; break;
		case EVillagePlace::Warehouse: Kind = ETownBuilding::Warehouse; break;
		case EVillagePlace::Academy: Kind = ETownBuilding::Academy; break;
		case EVillagePlace::Bank: Kind = ETownBuilding::Bank; break;
		case EVillagePlace::Bath: Kind = ETownBuilding::Bath; break;
		case EVillagePlace::Bell: Kind = ETownBuilding::Bell; break;
		case EVillagePlace::Castle: Kind = ETownBuilding::Castle; break;
		default: bBuilding = false; break;
		}
		if (bBuilding)
			for (const FTownPlot& Plot : Plots)
				if (Plot.Kind == Kind && Plot.bBuilt) return Plot.Location + Plot.StakeOffset;
		// No wandering to legacy coordinates for an unbuilt service.
		return GetActorLocation();
	}
	switch (Place)
	{
	case EVillagePlace::House:
		for (const FTownPlot& Plot : Plots)
		{
			if (Plot.Kind == ETownBuilding::House && Plot.bBuilt && !Plot.bScenery)
			{
				return Plot.Location;
			}
		}
		return FVector(-13000.0f, -3000.0f, 2500.0f);
	case EVillagePlace::Inn: return FVector(19500.0f, -8500.0f, 2300.0f);
	case EVillagePlace::Bakery: return FVector(7000.0f, -8000.0f, 2500.0f);
	case EVillagePlace::Farm: return FVector(13000.0f, -9800.0f, 2500.0f);
	case EVillagePlace::Guild: return FVector(1000.0f, 10000.0f, 2650.0f);
	case EVillagePlace::Training: return FVector(-13000.0f, 5000.0f, 2580.0f);
	case EVillagePlace::Smith: return FVector(-15500.0f, -9500.0f, 2850.0f);
	case EVillagePlace::Shop: return FVector(7000.0f, -8000.0f, 2500.0f);
	case EVillagePlace::Chapel: return FVector(-7500.0f, 12500.0f, 2750.0f);
	case EVillagePlace::Warehouse: return FVector(6500.0f, -10500.0f, 2500.0f);
	case EVillagePlace::Forest: return FVector(-8000.0f, 18000.0f, 2850.0f);
	case EVillagePlace::Gate: return FVector(-2000.0f, -16000.0f, 2400.0f);
	case EVillagePlace::Academy: return FVector(1000.0f, 14000.0f, 2750.0f);
	case EVillagePlace::Bank: return FVector(5500.0f, 11500.0f, 2650.0f);
	case EVillagePlace::Bath: return FVector(11500.0f, 6500.0f, 2600.0f);
	case EVillagePlace::Bell: return FVector(-2000.0f, 9000.0f, 2560.0f);
	case EVillagePlace::Castle: return FVector(17000.0f, 14000.0f, 3350.0f);
	default: return FVector(0.0f, 0.0f, 2600.0f);
	}
}

int32 AVillageRuntime::ResidentCount() const
{
	int32 N = 0;
	for (AVillageCitizen* C : Living())
	{
		if (C->Mind.Status == ECitizenStatus::Resident) ++N;
	}
	return N;
}

int32 AVillageRuntime::VisitorCount() const
{
	int32 N = 0;
	for (AVillageCitizen* C : Living())
	{
		if (C->Mind.Status == ECitizenStatus::Visitor) ++N;
	}
	return N;
}

int32 AVillageRuntime::FreeBeds() const
{
	return FMath::Max(0, BedCapacity() - ResidentCount() - VisitorCount());
}

float AVillageRuntime::AverageFit() const
{
	TArray<AVillageCitizen*> People = Living();
	if (People.Num() == 0)
	{
		return 0.0f;
	}
	int32 Sum = 0;
	for (AVillageCitizen* C : People)
	{
		Sum += FitOf(C->Mind);
	}
	return static_cast<float>(Sum) / People.Num();
}

FText AVillageRuntime::WindowName() const
{
	static const TCHAR* Names[] = { TEXT("Wake"), TEXT("Meal"), TEXT("Labor"), TEXT("Labor"), TEXT("Road"), TEXT("Dusk"), TEXT("Night"), TEXT("Sleep") };
	return FText::FromString(Names[WindowIndex & 7]);
}

FText AVillageRuntime::CensusLine() const
{
	const TCHAR* W = TEXT("Clear");
	switch (Weather)
	{
	case EVillageWeather::Rain: W = TEXT("Rain"); break;
	case EVillageWeather::Heat: W = TEXT("Heat"); break;
	case EVillageWeather::Cold: W = TEXT("Cold"); break;
	case EVillageWeather::Fog: W = TEXT("Fog"); break;
	case EVillageWeather::Drought: W = TEXT("Drought"); break;
	default: break;
	}
	return FText::FromString(FString::Printf(
		TEXT("El Ruhn D%d %s  %s  %d res %d vis  shop W%d/O%d  Fit %.0f  Trust %d"),
		DayIndex, W, *WindowName().ToString(), ResidentCount(), VisitorCount(),
		ShopWood, ShopOre, AverageFit(), Trust));
}

AVillageCitizen* AVillageRuntime::SpawnPerson(ECitizenStatus Status, ECitizenOrigin Origin, ECitizenTrait Trait)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}
	const FVector At = PlaceLoc(Status == ECitizenStatus::Resident ? EVillagePlace::House : EVillagePlace::Gate);
	AVillageCitizen* C = World->SpawnActor<AVillageCitizen>(At, FRotator::ZeroRotator);
	if (!C)
	{
		return nullptr;
	}

	static const TCHAR* First[] = {
		TEXT("Toma"), TEXT("Mira"), TEXT("Soren"), TEXT("Lira"), TEXT("Kael"), TEXT("Yuna"),
		TEXT("Brann"), TEXT("Osa"), TEXT("Ryn"), TEXT("Vela"), TEXT("Daro"), TEXT("Nim")
	};
	C->Mind.DisplayName = FText::FromString(First[VisitSeed % 12]);
	C->Mind.Trait = Trait;
	C->Mind.Status = Status;
	C->Mind.Origin = Origin;
	C->Mind.Hunger = 35 + VisitSeed % 25;
	C->Mind.Rest = 50 + VisitSeed % 30;
	C->Mind.Safety = 45;
	C->Mind.Coin = 12 + VisitSeed % 20;
	C->Mind.Purpose = 35;
	C->Mind.VisitNightsLeft = 2 + VisitSeed % 3;
	if (Status == ECitizenStatus::Resident)
	{
		C->Mind.Job = ECitizenJob::Hauler;
		C->Mind.bHasChop = true;
		C->Mind.HomeId = FName(*FString::Printf(TEXT("Home_%d"), ResidentCount() % 4));
		C->Mind.BondTown = 25;
		C->SetGoal(EVillagePlace::House, PlaceLoc(EVillagePlace::House) + FVector(VisitSeed % 4 * 400.0f, 0.0f, 0.0f));
	}
	else
	{
		C->SetGoal(EVillagePlace::Inn, PlaceLoc(EVillagePlace::Inn));
	}
	C->Restyle();
	++VisitSeed;
	return C;
}

AVillageCitizen* AVillageRuntime::NearestCitizen(const FVector& World, float RadiusCm) const
{
	AVillageCitizen* Best = nullptr;
	float BestD = RadiusCm * RadiusCm;
	for (AVillageCitizen* C : Living())
	{
		const float D = FVector::DistSquared(C->GetActorLocation(), World);
		if (D < BestD)
		{
			BestD = D;
			Best = C;
		}
	}
	return Best;
}

AVillageCitizen* AVillageRuntime::NearestAt(EVillagePlace Place, float RadiusCm) const
{
	return NearestCitizen(PlaceLoc(Place), RadiusCm);
}

int32 AVillageRuntime::ResolveLootQty(const FLootDrop& Drop, ELootPresence Presence, float Luck, int32 Rank)
{
	if (!Drop.Allows(Presence) || Drop.ItemId.IsNone())
	{
		return 0;
	}
	int32 Qty = Drop.BaseQty;
	if (Rank >= 1) Qty += 1;
	if (Luck > 0.72f) Qty += 1;
	if (Drop.bBoundUnique) Qty = 1;
	return FMath::Max(0, Qty);
}

ELootPresence AVillageRuntime::PresenceFor(const AIsekaiVillageCharacter* Character)
{
	if (Character && Character->PartyReserve && Character->PartyReserve->GetActiveCompanionCount() > 0)
	{
		return ELootPresence::PlayerParty;
	}
	return ELootPresence::PlayerSolo;
}

FLootDrop AVillageRuntime::MakeDrop(FName ItemId, int32 BaseQty)
{
	FLootDrop Drop;
	Drop.ItemId = ItemId;
	Drop.BaseQty = BaseQty;
	Drop.bPlayerSolo = true;
	Drop.bPlayerParty = true;
	Drop.bAdventurerRun = true;
	if (ItemId == TEXT("Crystal"))
	{
		Drop.bPlayerSolo = false;
		Drop.bAdventurerRun = false;
		Drop.bPlayerParty = true;
	}
	else if (ItemId == TEXT("Relic"))
	{
		Drop.bPlayerParty = false;
		Drop.bAdventurerRun = false;
		Drop.bBoundUnique = true;
	}
	else if (ItemId == TEXT("GuildSeal"))
	{
		Drop.bPlayerSolo = false;
		Drop.bPlayerParty = false;
		Drop.bAdventurerRun = true;
	}
	return Drop;
}

int32 AVillageRuntime::RollPlayerDrop(AIsekaiVillageCharacter* Character, FName ItemId, int32 BaseQty)
{
	const FLootDrop Drop = MakeDrop(ItemId, BaseQty);
	const int32 Qty = ResolveLootQty(Drop, PresenceFor(Character), FMath::FRand(), 0);
	if (Qty <= 0 && GEngine)
	{
		if (ItemId == TEXT("Crystal"))
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Magenta, TEXT("Crystal needs a party you are on."));
		}
		else if (ItemId == TEXT("Relic"))
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Magenta, TEXT("That relic is yours alone."));
		}
		else if (ItemId == TEXT("GuildSeal"))
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Magenta, TEXT("Guild seals are adventurer-run only."));
		}
	}
	return Qty;
}

bool AVillageRuntime::IsNearShop(const FVector& Location) const
{
	if (bUseGolemVillage) return !NearestGolemShop(Location).IsNone();
	constexpr double RangeSquared = 450.0 * 450.0;
	if (!bUseAuthoredPlots) return FVector::DistSquared2D(Location, PlaceLoc(EVillagePlace::Shop)) <= RangeSquared;
	for (const FTownPlot& Plot : Plots)
		if (Plot.bBuilt && Plot.Kind == ETownBuilding::Shop && FVector::DistSquared2D(Location, Plot.Location + Plot.StakeOffset) <= RangeSquared) return true;
	return false;
}

bool AVillageRuntime::TryShopOffer(AIsekaiVillageCharacter* Player)
{
	if (bUseGolemVillage) return Player && TradeWood(NearestGolemShop(Player->GetActorLocation()), false, Player);
	if (!Player || !Player->Gather)
	{
		return false;
	}
	if (!IsNearShop(Player->GetActorLocation()))
	{
		return false;
	}
	if (Player->Gather->GetCount(TEXT("Wood")) > 0 && Player->Gather->Consume(TEXT("Wood"), 1))
	{
		++ShopWood;
		++WoodSoldToday;
		ShopCoin = FMath::Max(0, ShopCoin - 2);
		Trust += 1;
		for (FDayMission& Mission : TodayMissions)
		{
			if (Mission.Kind == EDayMissionKind::StockStall && !Mission.bClaimed)
			{
				Mission.Have = FMath::Min(Mission.Need, WoodSoldToday);
			}
		}
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow, TEXT("Sold 1 Wood to the stall."));
		return true;
	}
	if (ShopWood > 0)
	{
		--ShopWood;
		Player->Gather->AddItem(TEXT("Wood"), 1);
		ShopCoin += 2;
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow, TEXT("Bought 1 Wood from the stall."));
		return true;
	}
	if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("The stall has nothing to trade."));
	return true;
}

bool AVillageRuntime::TryBoard(AIsekaiVillageCharacter* Player)
{
	if (!Player || !Player->Gather)
	{
		return false;
	}
	for (FDayMission& Mission : TodayMissions)
	{
		if (Mission.bClaimed)
		{
			continue;
		}
		if (Mission.Kind == EDayMissionKind::CookMeals && Mission.Have < Mission.Need)
		{
			if (FoodStock <= 0)
			{
				if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("No food left to cook."));
				return true;
			}
			--FoodStock;
			++Mission.Have;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow,
					FString::Printf(TEXT("Cooked a meal  %d/%d"), Mission.Have, Mission.Need));
			}
			if (Mission.IsReady())
			{
				RewardMission(Player, Mission);
			}
			return true;
		}
		if (Mission.Kind == EDayMissionKind::FetchWood && Player->Gather->GetCount(TEXT("Wood")) >= Mission.Need)
		{
			Player->Gather->Consume(TEXT("Wood"), Mission.Need);
			Mission.Have = Mission.Need;
			RewardMission(Player, Mission);
			return true;
		}
		if (Mission.Kind == EDayMissionKind::RepairWall && Player->Gather->GetCount(TEXT("Wood")) >= 3)
		{
			Player->Gather->Consume(TEXT("Wood"), 3);
			WallIntegrity = FMath::Min(100, WallIntegrity + 30);
			Mission.Have = Mission.Need;
			RewardMission(Player, Mission);
			return true;
		}
		if (Mission.Kind == EDayMissionKind::StockStall)
		{
			Mission.Have = FMath::Min(Mission.Need, WoodSoldToday);
			if (Mission.IsReady())
			{
				RewardMission(Player, Mission);
				return true;
			}
		}
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Orange, TEXT("Board: bring what the slips ask, or cook if posted."));
	}
	return true;
}

FText AVillageRuntime::BoardLine() const
{
	FString Line;
	for (int32 i = 0; i < TodayMissions.Num(); ++i)
	{
		const FDayMission& Mission = TodayMissions[i];
		if (i > 0)
		{
			Line += TEXT("  |  ");
		}
		Line += FString::Printf(TEXT("%s %d/%d%s"),
			*Mission.Title().ToString(),
			Mission.Have,
			Mission.Need,
			Mission.bClaimed ? TEXT(" done") : TEXT(""));
	}
	return FText::FromString(Line);
}

void AVillageRuntime::RefreshMissions()
{
	TodayMissions.Reset();
	TArray<EDayMissionKind> Pool = {
		EDayMissionKind::FetchWood,
		EDayMissionKind::RepairWall,
		EDayMissionKind::CookMeals,
		EDayMissionKind::StockStall
	};
	const int32 Seed = DayIndex * 17 + VisitSeed;
	for (int32 i = 0; i < Pool.Num(); ++i)
	{
		const int32 J = (Seed + i * 3) % Pool.Num();
		Pool.Swap(i, J);
	}
	const int32 Count = FMath::Min(3, Pool.Num());
	for (int32 i = 0; i < Count; ++i)
	{
		FDayMission Mission;
		Mission.Kind = Pool[i];
		switch (Mission.Kind)
		{
		case EDayMissionKind::RepairWall: Mission.Need = 30; break;
		case EDayMissionKind::CookMeals: Mission.Need = 3; break;
		case EDayMissionKind::StockStall: Mission.Need = 3; break;
		default: Mission.Need = 5; break;
		}
		Mission.Have = (Mission.Kind == EDayMissionKind::StockStall) ? FMath::Min(Mission.Need, WoodSoldToday) : 0;
		TodayMissions.Add(Mission);
	}
}

void AVillageRuntime::RewardMission(AIsekaiVillageCharacter* Player, FDayMission& Mission)
{
	Mission.bClaimed = true;
	Mission.Have = Mission.Need;
	int32 TrustGain = 5;
	int32 CoinGain = 0;
	if (Player)
	{
		++Player->SpherePoints;
		if (Player->HasSphereSkill(TEXT("MissionReward+1")))
		{
			TrustGain += 2;
			CoinGain = 5;
			if (Player->Gather)
			{
				Player->Gather->AddItem(TEXT("Coin"), CoinGain);
			}
		}
		if (Mission.Kind == EDayMissionKind::RepairWall && Player->HasSphereSkill(TEXT("FieldRepair")))
		{
			WallIntegrity = FMath::Min(100, WallIntegrity + 15);
		}
	}
	Trust = FMath::Min(99, Trust + TrustGain);
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Cyan,
			FString::Printf(TEXT("Day slip done: %s  +1 SP  +%d Trust%s"), *Mission.Title().ToString(), TrustGain, CoinGain > 0 ? TEXT("  +5 Coin") : TEXT("")));
	}
}

void AVillageRuntime::TickWindow()
{
	const AIsekaiVillageCharacter* Player = ActiveTownPlayer();
	WindowIndex = (WindowIndex + 1) % 8;
	if (WindowIndex == 0)
	{
		++DayIndex;
		for (FVillageShopState& S : GolemShops) { EnsureShopStock(S, true); }
		const EVillageWeather Cycle[] = {
			EVillageWeather::Clear, EVillageWeather::Rain, EVillageWeather::Clear,
			EVillageWeather::Heat, EVillageWeather::Fog, EVillageWeather::Cold, EVillageWeather::Drought
		};
		Weather = Cycle[DayIndex % 7];
		const int32 FestMin = (Player && Player->HasSphereSkill(TEXT("FestivalProlong"))) ? 15 : 20;
		if (DayIndex % 7 == 0 && Trust >= FestMin)
		{
			FestivalDays = 1;
		}
		else
		{
			FestivalDays = FMath::Max(0, FestivalDays - 1);
		}
		if (FestivalDays > 0 && Player && Player->HasSphereSkill(TEXT("FestivalProlong")))
		{
			Trust = FMath::Min(99, Trust + 1);
		}
		bLargeTown = Trust >= 50;
		bKingdom = Trust >= 80;
		if (HasBuilding(ETownBuilding::Bath))
		{
			FoodStock += 1;
		}
		if (HasBuilding(ETownBuilding::Inn) && Player && Player->HasSphereSkill(TEXT("InnHospitality")))
		{
			FoodStock += 1;
		}
		if (Weather != EVillageWeather::Drought)
		{
			FoodStock += 2;
		}
		else
		{
			FoodStock = FMath::Max(0, FoodStock - 2);
		}
		StrikeHours = FMath::Max(0, StrikeHours - 8);
		const bool bCivicWatch = Player && Player->HasSphereSkill(TEXT("CivicWatch"));
		CrimeHeat = FMath::Max(0, CrimeHeat - (bCivicWatch ? 2 : 1));
		if (bCivicWatch)
		{
			WallIntegrity = FMath::Min(100, WallIntegrity + 3);
		}
		WoodSoldToday = 0;
		RefreshMissions();
		RollOverNewDay(const_cast<AIsekaiVillageCharacter*>(Player));
	}
	if (StrikeHours > 0)
	{
		--StrikeHours;
	}

	TArray<AVillageCitizen*> People = Living();
	int32 Unpaid = 0;
	for (AVillageCitizen* C : People)
	{
		TickCitizen(C);
		if (C && C->Mind.bUnpaid) ++Unpaid;
	}
	if (Unpaid >= 2)
	{
		StrikeHours = FMath::Max(StrikeHours, 3);
	}
	Trust = FMath::Clamp(Trust + (ResidentCount() > VisitorCount() ? 0 : 0), 0, 99);
}

void AVillageRuntime::TickCitizen(AVillageCitizen* C)
{
	if (!C || C->bUseStreetMovement)
	{
		return;
	}
	FCitizenMind& M = C->Mind;
	if (M.Status == ECitizenStatus::Leaving)
	{
		C->SetGoal(EVillagePlace::Gate, PlaceLoc(EVillagePlace::Gate));
		M.Mutex = ECitizenMutex::Idle;
		if (C->AtGoal(220.0f))
		{
			C->Destroy();
		}
		return;
	}
	if (M.Mutex == ECitizenMutex::Party)
	{
		C->SetGoal(EVillagePlace::Guild, PlaceLoc(EVillagePlace::Guild));
		return;
	}

	TickNeeds(M);
	ApplyWeatherNeeds(M);

	if (M.bSick)
	{
		const EVillagePlace Bed = M.Status == ECitizenStatus::Resident ? EVillagePlace::House : EVillagePlace::Inn;
		C->SetGoal(Bed, PlaceLoc(Bed));
		M.Mutex = ECitizenMutex::Sleep;
		if (C->AtGoal())
		{
			M.Rest = FMath::Min(100, M.Rest + 12);
			if (M.Rest > 55)
			{
				M.bSick = false;
			}
		}
		return;
	}

	switch (WindowIndex)
	{
	case 1:
		M.Mutex = ECitizenMutex::Food;
		C->SetGoal(EVillagePlace::Bakery, PlaceLoc(EVillagePlace::Bakery));
		if (C->AtGoal() && FoodStock > 0)
		{
			--FoodStock;
			M.Hunger = FMath::Max(0, M.Hunger - 28);
			M.Morale = FMath::Min(100, M.Morale + 4);
		}
		break;
	case 2:
	case 3:
		TickWork(C);
		break;
	case 4:
		TickWork(C);
		TickAmbush(C);
		break;
	case 5:
		M.Mutex = ECitizenMutex::Shop;
		C->SetGoal(EVillagePlace::Shop, PlaceLoc(EVillagePlace::Shop));
		if (C->AtGoal())
		{
			const int32 Wood = M.TakeAll(TEXT("Wood"));
			const int32 Ore = M.TakeAll(TEXT("Copper")) + M.TakeAll(TEXT("Iron"));
			if (StrikeHours > 0 || ShopCoin < Wood + Ore)
			{
				M.bUnpaid = true;
				M.bLastSaleFair = false;
				if (Wood > 0) M.AddBag(TEXT("Wood"), Wood);
			}
			else
			{
				ShopWood += Wood;
				ShopOre += Ore;
				const int32 Pay = Wood * 2 + Ore * 3;
				ShopCoin = FMath::Max(0, ShopCoin - Pay);
				M.Coin += Pay;
				M.bUnpaid = false;
				M.bLastSaleFair = true;
			}
		}
		PayRent(M);
		RollCrime(C);
		if (M.bHasAttack && M.TrainHours >= 3 && M.Job != ECitizenJob::Guard && M.Job != ECitizenJob::Adventurer)
		{
			if (M.Trait == ECitizenTrait::Cautious || M.Trait == ECitizenTrait::Stoic)
			{
				M.Job = ECitizenJob::Guard;
				M.bHasGuard = true;
			}
			else
			{
				M.Job = ECitizenJob::Adventurer;
			}
			C->Restyle();
			Trust = FMath::Min(99, Trust + 2);
		}
		else if (M.GatherXP >= 4 && M.Job == ECitizenJob::None)
		{
			M.Job = ECitizenJob::Hauler;
			C->Restyle();
		}
		else if (M.Trait == ECitizenTrait::Greedy && M.Job == ECitizenJob::None)
		{
			M.Job = ECitizenJob::Clerk;
			C->Restyle();
		}
		break;
	case 6:
		if (M.Trait == ECitizenTrait::Earnest || M.Rest < 40)
		{
			M.Mutex = ECitizenMutex::Chapel;
			C->SetGoal(EVillagePlace::Chapel, PlaceLoc(EVillagePlace::Chapel));
			if (C->AtGoal())
			{
				M.Morale = FMath::Min(100, M.Morale + 6);
				M.BondTown += 1;
			}
		}
		else
		{
			M.Mutex = ECitizenMutex::Idle;
			C->SetGoal(EVillagePlace::Inn, PlaceLoc(EVillagePlace::Inn));
		}
		if (bLargeTown && WindowIndex == 6)
		{
			CrimeHeat = FMath::Max(0, CrimeHeat - 1);
		}
		AgeAndGossip(M);
		break;
	case 7:
		M.Mutex = ECitizenMutex::Sleep;
		{
			const EVillagePlace Bed = (M.Status == ECitizenStatus::Resident) ? EVillagePlace::House : EVillagePlace::Inn;
			C->SetGoal(Bed, PlaceLoc(Bed));
		}
		if (C->AtGoal())
		{
			M.Rest = FMath::Min(100, M.Rest + 32);
			M.Wound = FMath::Max(0, M.Wound - 8);
		}
		TickStay(C);
		break;
	default:
		M.Mutex = ECitizenMutex::Idle;
		C->SetGoal(EVillagePlace::Inn, PlaceLoc(EVillagePlace::Inn));
		break;
	}
	RollIllness(M);
}

void AVillageRuntime::TickNeeds(FCitizenMind& M)
{
	M.Hunger = FMath::Clamp(M.Hunger + 6, 0, 100);
	M.Rest = FMath::Clamp(M.Rest - 4, 0, 100);
	if (M.Trait == ECitizenTrait::Lazy)
	{
		M.Rest = FMath::Clamp(M.Rest - 2, 0, 100);
	}
	if (M.Wound > 0)
	{
		M.Safety = FMath::Clamp(M.Safety - 3, 0, 100);
	}
}

void AVillageRuntime::TickWork(AVillageCitizen* C)
{
	FCitizenMind& M = C->Mind;
	if (StrikeHours > 0 && M.Job == ECitizenJob::Hauler)
	{
		M.Mutex = ECitizenMutex::Idle;
		C->SetGoal(EVillagePlace::Inn, PlaceLoc(EVillagePlace::Inn));
		return;
	}
	if (M.Job == ECitizenJob::Guard || M.bHasGuard)
	{
		M.Mutex = ECitizenMutex::Guard;
		C->SetGoal(EVillagePlace::Training, PlaceLoc(EVillagePlace::Training));
		if (C->AtGoal())
		{
			M.Safety = FMath::Min(100, M.Safety + 6);
			M.Purpose = FMath::Min(100, M.Purpose + 3);
			CrimeHeat = FMath::Max(0, CrimeHeat - 1);
		}
		return;
	}
	if (HasBuilding(ETownBuilding::Academy) && (M.Job == ECitizenJob::Adventurer || M.Job == ECitizenJob::Clerk) && FMath::RandHelper(100) < 22)
	{
		M.Mutex = ECitizenMutex::Train;
		C->SetGoal(EVillagePlace::Academy, PlaceLoc(EVillagePlace::Academy));
		if (C->AtGoal())
		{
			M.Purpose = FMath::Min(100, M.Purpose + 6);
			M.CombatXP += 2;
		}
		return;
	}
	if (M.Job == ECitizenJob::Adventurer && M.Rank >= 0 && FMath::RandHelper(100) < 18)
	{
		M.Mutex = ECitizenMutex::Tower;
		C->SetGoal(EVillagePlace::Gate, PlaceLoc(EVillagePlace::Gate));
		if (C->AtGoal())
		{
			const FLootDrop Seal = MakeDrop(TEXT("GuildSeal"), 1);
			const int32 Qty = ResolveLootQty(Seal, ELootPresence::AdventurerRun, FMath::FRand(), M.Rank);
			if (Qty > 0)
			{
				M.AddBag(TEXT("GuildSeal"), Qty);
			}
			FName Regional = TEXT("PalmFiber");
			if (M.Origin == ECitizenOrigin::Kelsin) Regional = TEXT("Iron");
			else if (M.Origin == ECitizenOrigin::Rabaric) Regional = TEXT("Copper");
			else if (M.Origin == ECitizenOrigin::Vylfod) Regional = TEXT("CrystalDust");
			else if (M.Origin == ECitizenOrigin::Gosain) Regional = TEXT("Silk");
			else if (M.Origin == ECitizenOrigin::ElRuhn) Regional = TEXT("Wood");
			M.AddBag(Regional, 1 + (Weather == EVillageWeather::Clear ? 1 : 0));
			M.CombatXP += 6;
			M.Rank = FMath::Min(3, M.CombatXP / 24);
			M.Purpose = FMath::Min(100, M.Purpose + 8);
		}
		return;
	}
	if (M.Job == ECitizenJob::Clerk || M.Trait == ECitizenTrait::Greedy)
	{
		M.Mutex = ECitizenMutex::Shop;
		C->SetGoal(EVillagePlace::Shop, PlaceLoc(EVillagePlace::Shop));
		if (C->AtGoal())
		{
			M.Purpose = FMath::Min(100, M.Purpose + 2);
			M.Coin += 1;
		}
		return;
	}
	if (M.bHasAttack && M.TrainHours < 3)
	{
		M.Mutex = ECitizenMutex::Train;
		C->SetGoal(EVillagePlace::Training, PlaceLoc(EVillagePlace::Training));
		if (C->AtGoal())
		{
			++M.TrainHours;
			M.CombatXP += 4;
			M.Purpose = FMath::Min(100, M.Purpose + 5);
		}
		return;
	}
	M.Mutex = ECitizenMutex::Gather;
	M.Job = (M.Job == ECitizenJob::None) ? ECitizenJob::Hauler : M.Job;
	C->SetGoal(EVillagePlace::Forest, PlaceLoc(EVillagePlace::Forest));
	if (C->AtGoal())
	{
		M.bHasChop = true;
		++M.GatherXP;
		int32 Qty = ResolveLootQty(MakeDrop(TEXT("Wood"), 2), ELootPresence::AdventurerRun, FMath::FRand(), M.Rank);
		if (Weather == EVillageWeather::Rain || Weather == EVillageWeather::Fog)
		{
			Qty = FMath::Max(1, Qty - 1);
		}
		M.AddBag(TEXT("Wood"), Qty);
		M.Rest = FMath::Max(0, M.Rest - 6);
	}
}

void AVillageRuntime::TickAmbush(AVillageCitizen* C)
{
	FCitizenMind& M = C->Mind;
	if (M.Mutex != ECitizenMutex::Gather || !C->AtGoal(260.0f))
	{
		return;
	}
	int32 Chance = 28;
	if (Weather == EVillageWeather::Fog || Weather == EVillageWeather::Rain) Chance += 12;
	if (M.Trait == ECitizenTrait::Cautious) Chance -= 8;
	if (M.Trait == ECitizenTrait::Brave) Chance += 6;
	if (FMath::RandHelper(100) >= Chance)
	{
		return;
	}
	M.bHasAttack = true;
	M.CombatXP += 8;
	M.Safety = FMath::Clamp(M.Safety - 18, 0, 100);
	M.Wound += (M.Trait == ECitizenTrait::Cautious) ? 14 : 7;
	M.Purpose = FMath::Min(100, M.Purpose + 10);
}

void AVillageRuntime::TickStay(AVillageCitizen* C)
{
	FCitizenMind& M = C->Mind;
	const int32 Fit = FitOf(M);
	if (M.Status == ECitizenStatus::Visitor)
	{
		--M.VisitNightsLeft;
		if (Fit >= 55 && FreeBeds() > 0 && M.VisitNightsLeft <= 1)
		{
			M.Status = ECitizenStatus::Resident;
			M.HomeId = FName(*FString::Printf(TEXT("Home_%d"), ResidentCount() % 4));
			M.BondTown += 12;
			Trust = FMath::Min(99, Trust + 2);
			C->Restyle();
		}
		else if (Fit < 35 || M.VisitNightsLeft <= 0)
		{
			M.Status = ECitizenStatus::Leaving;
		}
		return;
	}
	if (Fit < 22)
	{
		++M.LeaveStreak;
	}
	else
	{
		M.LeaveStreak = 0;
	}
	if (M.LeaveStreak >= 2)
	{
		M.Status = ECitizenStatus::Leaving;
		Trust = FMath::Max(0, Trust - 2);
	}
}

void AVillageRuntime::ApplyWeatherNeeds(FCitizenMind& M) const
{
	if (Weather == EVillageWeather::Heat) M.Rest = FMath::Clamp(M.Rest - 3, 0, 100);
	if (Weather == EVillageWeather::Cold) M.Hunger = FMath::Clamp(M.Hunger + 3, 0, 100);
	if (Weather == EVillageWeather::Drought) M.Hunger = FMath::Clamp(M.Hunger + 4, 0, 100);
}

void AVillageRuntime::PayRent(FCitizenMind& M)
{
	if (M.Status != ECitizenStatus::Resident)
	{
		return;
	}
	const int32 Rent = 2;
	if (M.Coin >= Rent)
	{
		M.Coin -= Rent;
		ShopCoin += Rent;
		M.Debt = FMath::Max(0, M.Debt - 1);
	}
	else
	{
		++M.Debt;
		M.bUnpaid = true;
		M.Morale = FMath::Max(0, M.Morale - 6);
	}
}

void AVillageRuntime::RollCrime(AVillageCitizen* C)
{
	FCitizenMind& M = C->Mind;
	if (M.Trait != ECitizenTrait::Greedy || M.Job == ECitizenJob::Guard)
	{
		return;
	}
	if (FMath::RandHelper(100) < 8 + CrimeHeat)
	{
		++CrimeHeat;
		M.Coin += 4;
		M.Safety = FMath::Max(0, M.Safety - 8);
		M.BondTown = FMath::Max(0, M.BondTown - 4);
	}
}

void AVillageRuntime::RollIllness(FCitizenMind& M)
{
	if (M.Rest < 18 || (Weather == EVillageWeather::Cold && M.Hunger > 70))
	{
		if (FMath::RandHelper(100) < 12)
		{
			M.bSick = true;
		}
	}
}

void AVillageRuntime::AgeAndGossip(FCitizenMind& M)
{
	++M.AgeDays;
	if (M.Trait == ECitizenTrait::Cheerful)
	{
		M.BondTown += 1;
		M.Morale = FMath::Min(100, M.Morale + 2);
	}
}

int32 AVillageRuntime::FitOf(const FCitizenMind& M) const
{
	const FVillageOffer O = BuildOffer();
	float Fit = 40.0f;
	Fit += (100 - M.Hunger) * 0.08f * O.Food;
	Fit += M.Rest * 0.07f * O.Beds;
	Fit += M.Safety * 0.08f * O.Safety;
	Fit += FMath::Min(80, M.Coin) * 0.04f * O.Coin;
	Fit += M.Purpose * 0.06f * O.Purpose;
	Fit += M.BondTown * 0.35f;
	Fit += M.BondPlayer * 0.25f;
	if (M.bUnpaid) Fit -= 14.0f;
	Fit -= M.Wound * 0.15f;
	Fit -= CrimeHeat * 1.5f;
	if (M.Trait == ECitizenTrait::Greedy) Fit += O.Coin * 8.0f;
	if (M.Trait == ECitizenTrait::Brave) Fit += O.Purpose * 6.0f;
	if (FreeBeds() <= 0 && M.Status == ECitizenStatus::Visitor) Fit -= 12.0f;
	return FMath::Clamp(FMath::RoundToInt(Fit), 0, 100);
}

static FTownPlot MakePlot(const TCHAR* Id, ETownBuilding Kind, ETownEra Era, float MX, float MY, float MZ, bool bStartBuilt, bool bScenery, int32 Wood, int32 Iron, int32 Crystal, int32 Beds)
{
	FTownPlot Plot;
	Plot.Id = Id;
	Plot.Kind = Kind;
	Plot.Era = Era;
	Plot.Location = FVector(MX * 100.0f, MY * 100.0f, MZ * 100.0f);
	Plot.bBuilt = bStartBuilt;
	Plot.bScenery = bScenery;
	Plot.WoodCost = Wood;
	Plot.IronCost = Iron;
	Plot.CrystalCost = Crystal;
	Plot.BedBonus = Beds;
	return Plot;
}

void AVillageRuntime::SeedPlots()
{
	Plots.Reset();
	if (bUseAuthoredPlots)
	{
		TSet<FName> Seen;
		for (const FTownPlot& Plot : AuthoredPlots)
		{
			if (Plot.Id.IsNone() || Seen.Contains(Plot.Id) || Plot.WoodCost < 0 || Plot.IronCost < 0 || Plot.CrystalCost < 0) continue;
			Seen.Add(Plot.Id);
			Plots.Add(Plot);
			if (Plot.bFlexibleUse && !Plot.bBuilt) Plots.Last().Kind = ETownBuilding::Unassigned;
		}
		return;
	}
	Plots.Add(MakePlot(TEXT("Inn"), ETownBuilding::Inn, ETownEra::Village, 195, -85, 22.2f, true, true, 0, 0, 0, 4));
	Plots.Add(MakePlot(TEXT("Shop"), ETownBuilding::Shop, ETownEra::Village, 70, -80, 24.65f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Smith"), ETownBuilding::Smith, ETownEra::Village, -155, -95, 27.76f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Guild"), ETownBuilding::Guild, ETownEra::Village, 10, 100, 25.73f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Chapel"), ETownBuilding::Chapel, ETownEra::Village, -75, 125, 26.77f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Yard"), ETownBuilding::Training, ETownEra::Village, -130, 50, 25.09f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Warehouse"), ETownBuilding::Warehouse, ETownEra::Village, 65, -105, 24.45f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Bakery"), ETownBuilding::Bakery, ETownEra::Village, 70, -80, 24.65f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("Farm"), ETownBuilding::Farm, ETownEra::Village, 130, -98, 24.5f, true, true, 0, 0, 0, 0));
	Plots.Add(MakePlot(TEXT("OldHomes"), ETownBuilding::House, ETownEra::Village, -130, -30, 24.44f, true, true, 0, 0, 0, 4));
	Plots.Add(MakePlot(TEXT("House_05"), ETownBuilding::House, ETownEra::Village, -100, 130, 27.9f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_06"), ETownBuilding::House, ETownEra::Village, 40, -110, 24.35f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_07"), ETownBuilding::House, ETownEra::Village, 90, -10, 25.2f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_08"), ETownBuilding::House, ETownEra::Village, 130, 10, 25.44f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_09"), ETownBuilding::House, ETownEra::Village, 190, -20, 24.01f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_10"), ETownBuilding::House, ETownEra::Village, -100, 50, 25.05f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_11"), ETownBuilding::House, ETownEra::Village, -70, 100, 25.58f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("House_12"), ETownBuilding::House, ETownEra::Village, 70, 140, 29.04f, false, false, 8, 0, 0, 2));
	Plots.Add(MakePlot(TEXT("Bank"), ETownBuilding::Bank, ETownEra::LargeTown, 55, 115, 26.27f, false, false, 10, 4, 0, 0));
	Plots.Add(MakePlot(TEXT("Bath"), ETownBuilding::Bath, ETownEra::LargeTown, 115, 65, 25.8f, false, false, 8, 3, 0, 0));
	Plots.Add(MakePlot(TEXT("Bell"), ETownBuilding::Bell, ETownEra::LargeTown, -20, 90, 25.57f, false, false, 6, 2, 0, 0));
	Plots.Add(MakePlot(TEXT("Academy"), ETownBuilding::Academy, ETownEra::LargeTown, 10, 140, 27.43f, false, false, 12, 6, 0, 0));
	Plots.Add(MakePlot(TEXT("Manor"), ETownBuilding::Manor, ETownEra::LargeTown, 120, 110, 27.84f, false, false, 14, 6, 0, 3));
	Plots.Add(MakePlot(TEXT("Castle"), ETownBuilding::Castle, ETownEra::Kingdom, 170, 140, 33.44f, false, false, 16, 8, 4, 6));
}

void AVillageRuntime::InitializeConstruction()
{
	UTownConstructionSave* LoadedVillage = nullptr;
	CancelBuildingPlacement();
	// Reinitialization is safe for editor automation and map-level resets.
	for (TActorIterator<AArchitectStake> It(GetWorld()); It; ++It)
	{
		if (It->GetOwner() != this) continue;
		if (IsValid(It->BuiltVisual)) It->BuiltVisual->Destroy();
		It->Destroy();
	}
	SeedPlots();
	LoftBedBonuses.Reset();
	if (bUseAuthoredPlots && !ConstructionSaveSlot.IsEmpty() && UGameplayStatics::DoesSaveGameExist(ConstructionSaveSlot, 0))
	{
		if (UTownConstructionSave* Saved = Cast<UTownConstructionSave>(UGameplayStatics::LoadGameFromSlot(ConstructionSaveSlot, 0)))
		{
			LoadedVillage = Saved;
			LoftBedBonuses = Saved->LoftBedBonuses;
			for (FTownPlot& Plot : Plots)
			{
				if (Plot.bScenery) continue;
				if (Plot.bFlexibleUse && Saved->BuiltPlots.Contains(Plot.Id))
				{
					const FName* Choice = Saved->PlotBuildingIds.Find(Plot.Id);
					if (!Choice || !ApplyCatalog(Plot, *Choice, Saved->PlotRotations.FindRef(Plot.Id))) continue;
				}
				Plot.bBuilt |= Saved->BuiltPlots.Contains(Plot.Id);
				if (Plot.bBuilt && !Plot.bUpgraded && Saved->UpgradedPlots.Contains(Plot.Id) && Plot.Kind == ETownBuilding::House)
				{
					Plot.bUpgraded = true;
					Plot.BedBonus += FMath::Max(1, Saved->LoftBedBonuses.FindRef(Plot.Id));
				}
			}
		}
	}
	SpawnPlotStakes();
	if (bUseGolemVillage) { ReadVillageState(LoadedVillage); ReconcileGolemPopulation(); RestoreVillagePlayer(); }
}

bool AVillageRuntime::SaveConstruction()
{
	if (!bUseAuthoredPlots || ConstructionSaveSlot.IsEmpty()) return false;
	UTownConstructionSave* Saved = Cast<UTownConstructionSave>(UGameplayStatics::CreateSaveGameObject(UTownConstructionSave::StaticClass()));
	Saved->LoftBedBonuses = LoftBedBonuses;
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.bScenery) continue;
		if (Plot.bBuilt) Saved->BuiltPlots.Add(Plot.Id);
		if (Plot.bBuilt && Plot.bFlexibleUse)
		{
			Saved->PlotBuildingIds.Add(Plot.Id, Plot.CatalogId);
			Saved->PlotRotations.Add(Plot.Id, Plot.PlacementTurns);
		}
		if (Plot.bUpgraded) Saved->UpgradedPlots.Add(Plot.Id);
	}
	if (bUseGolemVillage) WriteVillageState(Saved);
	const bool bSaved = UGameplayStatics::SaveGameToSlot(Saved, ConstructionSaveSlot, 0);
	if (!bSaved)
		UE_LOG(LogTemp, Warning, TEXT("Could not save construction to %s"), *ConstructionSaveSlot);
	if (bUseGolemVillage && bSaved) PendingVillageSave = Saved;
	return bSaved;
}

void AVillageRuntime::SpawnPlotStakes()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.bScenery)
		{
			continue;
		}
		FActorSpawnParameters Params;
		Params.Owner = this;
		Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		AArchitectStake* Stake = World->SpawnActor<AArchitectStake>(Plot.Location + Plot.StakeOffset, FRotator::ZeroRotator, Params);
		if (Stake)
		{
			Stake->PlotId = Plot.Id;
			Stake->Restyle(Plot);
		}
	}
}

void AVillageRuntime::RefreshPlotStakes()
{
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AArchitectStake> It(World); It; ++It)
		{
			if (const FTownPlot* Plot = FindPlot(It->PlotId))
			{
				if (It->GetOwner() && It->GetOwner() != this) continue;
				It->Restyle(*Plot);
			}
		}
	}
}

bool AVillageRuntime::HasBuilding(ETownBuilding Kind) const
{
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.Kind == Kind && Plot.bBuilt)
		{
			return true;
		}
	}
	return false;
}

const FTownPlot* AVillageRuntime::FindPlot(FName PlotId) const
{
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.Id == PlotId)
		{
			return &Plot;
		}
	}
	return nullptr;
}

FTownPlot* AVillageRuntime::FindPlot(FName PlotId)
{
	for (FTownPlot& Plot : Plots)
	{
		if (Plot.Id == PlotId)
		{
			return &Plot;
		}
	}
	return nullptr;
}

int32 AVillageRuntime::BedCapacity() const
{
	int32 Beds = 0;
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.bBuilt)
		{
			Beds += Plot.BedBonus;
		}
	}
	return Beds;
}

bool AVillageRuntime::EraOpen(ETownEra Era, const AIsekaiVillageCharacter* Player) const
{
	const int32 Nodes = (Player) ? Player->UnlockedSphereNodes.Num() : 0;
	const int32 EffectiveTrust = Trust + (Player ? Player->SphereTrustBonus : 0);
	if (Era == ETownEra::LargeTown)
	{
		return EffectiveTrust >= 50 && Nodes >= 4;
	}
	if (Era == ETownEra::Kingdom)
	{
		return EffectiveTrust >= 80 && Nodes >= 8;
	}
	return true;
}

bool AVillageRuntime::TryBuildPlot(FName PlotId, AIsekaiVillageCharacter* Player)
{
	if (bUseGolemVillage && Player) { VillagePlayer = Player; RestoreVillagePlayer(); }
	FTownPlot* Plot = FindPlot(PlotId);
	if (!Plot || !Player || !Player->Gather)
	{
		return false;
	}
	FTownPlot* Destination = Plot;
	FTownPlot Proposal = *Plot;
	if (Plot->bFlexibleUse && !Plot->bBuilt)
	{
		if (!bBuildingCatalogOpen) { ToggleBuildingCatalog(); return true; }
		const FTownPlot* Choice = SelectedBuilding();
		if (Choice && IsUniqueBuildingStanding(*Choice))
		{
			if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("This building already stands in the village."));
			return true;
		}
		if (!Choice || !ApplyCatalog(Proposal, Choice->Id, PlacementTurns))
		{
			if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("Choose a building that fits this land."));
			return true;
		}
		Plot = &Proposal; // Choosing/previewing never assigns a land use or charges resources.
	}
	auto WoodNeed = [Player](int32 Base)
	{
		const float Cut = FMath::Clamp(Player->SphereBuildSpeed, 0.0f, 50.0f) / 100.0f;
		return FMath::Max(1, FMath::RoundToInt(static_cast<float>(Base) * (1.0f - Cut)));
	};
	if (Plot->bBuilt && Plot->Kind == ETownBuilding::House && !Plot->bUpgraded)
	{
		const int32 LoftWood = WoodNeed(6);
		if (Player->Gather->GetCount(TEXT("Wood")) < LoftWood)
		{
			if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange,
				FString::Printf(TEXT("Upgrade needs %d Wood."), LoftWood));
			return true;
		}
		Player->Gather->Consume(TEXT("Wood"), LoftWood);
		Plot->bUpgraded = true;
		const int32 LoftGain = Player->HasSphereSkill(TEXT("LoftBeds+2")) ? 2 : 1;
		Plot->BedBonus += LoftGain;
		LoftBedBonuses.Add(Plot->Id, LoftGain);
		if (bUseGolemVillage) ReconcileGolemPopulation();
		SaveConstruction();
		RefreshPlotStakes();
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Cyan,
			FString::Printf(TEXT("House gained a loft. +%d %s."), LoftGain, LoftGain == 1 ? TEXT("bed") : TEXT("beds")));
		return true;
	}
	if (Plot->bBuilt)
	{
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::White, *Plot->Title().ToString());
		return true;
	}
	if (!EraOpen(Plot->Era, Player))
	{
		if (Plot->Era == ETownEra::Kingdom)
		{
			if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Orange, TEXT("Castle needs Trust 80 and 8 sphere nodes."));
		}
		else
		{
			if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Orange, TEXT("Large Town stone needs Trust 50 and 4 sphere nodes."));
		}
		return true;
	}
	const int32 PayWood = Plot->WoodPrice(EffectiveBuildDiscount(Player));
	if (Player->Gather->GetCount(TEXT("Wood")) < PayWood
		|| Player->Gather->GetCount(TEXT("Iron")) < Plot->IronCost
		|| Player->Gather->GetCount(TEXT("Crystal")) < Plot->CrystalCost)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Orange,
				FString::Printf(TEXT("Need %d Wood%s%s"),
					PayWood,
					Plot->IronCost > 0 ? *FString::Printf(TEXT(", %d Iron"), Plot->IronCost) : TEXT(""),
					Plot->CrystalCost > 0 ? *FString::Printf(TEXT(", %d Crystal"), Plot->CrystalCost) : TEXT("")));
		}
		return true;
	}
	if (PayWood > 0) Player->Gather->Consume(TEXT("Wood"), PayWood);
	if (Plot->IronCost > 0) Player->Gather->Consume(TEXT("Iron"), Plot->IronCost);
	if (Plot->CrystalCost > 0) Player->Gather->Consume(TEXT("Crystal"), Plot->CrystalCost);
	Plot->bBuilt = true;
	*Destination = *Plot;
	Trust = FMath::Min(99, Trust + 3);
	EvaluateGuildRank(Player);
	if (bUseGolemVillage) ReconcileGolemPopulation();
	SaveConstruction();
	RefreshPlotStakes();
	if (Player->PartyReserve)
	{
		int32 Extra = 0;
		if (HasBuilding(ETownBuilding::Academy)) ++Extra;
		if (HasBuilding(ETownBuilding::Castle)) ++Extra;
		Player->PartyReserve->ActivePartyCap = FMath::Max(Player->PartyReserve->ActivePartyCap, 2 + Extra);
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Cyan,
			FString::Printf(TEXT("Raised %s. Beds %d  Trust %d"), *Plot->Title().ToString(), BedCapacity(), Trust));
	}
	return true;
}

FText AVillageRuntime::ArchitectLine() const
{
	const FString EraName = GetSettlementEraName();
	if (bUseAuthoredPlots && !BuildingCatalog.IsEmpty())
	{
		int32 Vacant = 0, Developed = 0;
		for (const FTownPlot& Plot : Plots)
			if (Plot.bFlexibleUse) { if (Plot.bBuilt) ++Developed; else ++Vacant; }
		return FText::FromString(FString::Printf(TEXT("[%s] Land   %d free   %d developed   %d beds   |   %s"), *EraName, Vacant, Developed, BedCapacity(), *GetNextEraRequirementText()));
	}
	int32 Houses = 0;
	int32 HouseCap = 0;
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.Kind == ETownBuilding::House && !Plot.bScenery)
		{
			++HouseCap;
			if (Plot.bBuilt) ++Houses;
		}
	}
	return FText::FromString(FString::Printf(TEXT("[%s] Houses %d/%d   Beds %d   |   %s"),
		*EraName, Houses, HouseCap, BedCapacity(), *GetNextEraRequirementText()));
}

void AVillageRuntime::SeedStarter()
{
	SpawnPerson(ECitizenStatus::Resident, ECitizenOrigin::ElRuhn, ECitizenTrait::Earnest);
	SpawnPerson(ECitizenStatus::Resident, ECitizenOrigin::ElRuhn, ECitizenTrait::Stoic);
	SpawnPerson(ECitizenStatus::Visitor, ECitizenOrigin::Yozuan, ECitizenTrait::Brave);
}

TArray<AVillageCitizen*> AVillageRuntime::Living() const
{
	TArray<AVillageCitizen*> Out;
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageCitizen> It(World); It; ++It)
		{
			if (IsValid(*It)) Out.Add(*It);
		}
	}
	return Out;
}
