#include "VillageRuntime.h"
#include "RoomVolume.h"
#include "TowerExpedition.h"
#include "VillageGolemCitizen.h"
#include "LinchpinProp.h"
#include "TownConstructionSave.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Engine/Engine.h"

static FVector GolemHomeEntrance(const AVillageRuntime& Village, const FVillageGolemRecord& Record)
{
	const FTownPlot* Home = Village.FindPlot(Record.HomePlot);
	if (!Home) return Village.GetActorLocation();
	int32 Slot = 0;
	for (const FVillageGolemRecord& Other : Village.GolemResidents)
	{
		if (Other.Id == Record.Id) break;
		if (Other.HomePlot == Record.HomePlot) ++Slot;
	}
	const FVector Side = FVector::CrossProduct(FVector::UpVector, (-Home->StakeOffset).GetSafeNormal2D());
	const float Offset = Slot == 0 ? 0.f : ((Slot + 1) / 2) * 85.f * (Slot % 2 ? 1.f : -1.f);
	return Village.WorkerEntrance(*Home) + Side * Offset;
}

FVector AVillageRuntime::WorkerEntrance(const FTownPlot& Plot) const
{
	const FVector Front = Plot.Location + Plot.StakeOffset;
	const FVector Side = FVector::CrossProduct(FVector::UpVector, (Plot.Location - Front).GetSafeNormal2D());
	return Front + Side * 120.f;
}

bool AVillageRuntime::BuildStreetRoute(const FVector& From, const FVector& To, TArray<FVector>& Out) const
{
	Out.Reset();
	if (FVector::DistSquared2D(From, To) < FMath::Square(180.f)) { Out.Add(To); return true; }
	if (StreetNodes.IsEmpty()) return false; // No unsafe straight-line fallback.
	auto Nearest = [&](const FVector& Point)
	{
		int32 Best = INDEX_NONE; double Distance = UE_BIG_NUMBER;
		for (int32 I = 0; I < StreetNodes.Num(); ++I)
		{
			const double D = FVector::DistSquared2D(Point, StreetNodes[I]);
			if (D < Distance) { Best = I; Distance = D; }
		}
		return Best;
	};
	const int32 Start = Nearest(From), Finish = Nearest(To);
	// A worker outside the authored street network waits rather than crossing parcels.
	if (FVector::DistSquared2D(From, StreetNodes[Start]) > FMath::Square(500.f)
		|| FVector::DistSquared2D(To, StreetNodes[Finish]) > FMath::Square(500.f)) return false;
	TArray<TArray<int32>> Adjacency; Adjacency.SetNum(StreetNodes.Num());
	for (const FIntPoint& Edge : StreetEdges)
		if (StreetNodes.IsValidIndex(Edge.X) && StreetNodes.IsValidIndex(Edge.Y))
		{ Adjacency[Edge.X].Add(Edge.Y); Adjacency[Edge.Y].Add(Edge.X); }
	TArray<double> Costs; Costs.Init(UE_BIG_NUMBER, StreetNodes.Num());
	TArray<int32> Previous; Previous.Init(INDEX_NONE, StreetNodes.Num());
	TSet<int32> Open; Open.Add(Start); Costs[Start] = 0;
	while (!Open.IsEmpty())
	{
		int32 Current = INDEX_NONE; double Best = UE_BIG_NUMBER;
		for (int32 Candidate : Open)
		{
			const double Estimate = Costs[Candidate] + FVector::Dist2D(StreetNodes[Candidate], StreetNodes[Finish]);
			if (Estimate < Best) { Best = Estimate; Current = Candidate; }
		}
		if (Current == Finish) break;
		Open.Remove(Current);
		for (int32 Next : Adjacency[Current])
		{
			const double Cost = Costs[Current] + FVector::Dist2D(StreetNodes[Current], StreetNodes[Next]);
			if (Cost < Costs[Next]) { Costs[Next] = Cost; Previous[Next] = Current; Open.Add(Next); }
		}
	}
	if (Start != Finish && Previous[Finish] == INDEX_NONE) return false;
	TArray<int32> Reverse;
	for (int32 I = Finish; I != INDEX_NONE; I = Previous[I]) Reverse.Add(I);
	for (int32 I = Reverse.Num() - 1; I >= 0; --I) Out.Add(StreetNodes[Reverse[I]]);
	Out.Add(To);
	return true;
}

void AVillageRuntime::ReconcileGolemPopulation()
{
	if (!bUseGolemVillage || !GetWorld()) return;
	TMap<FName, int32> Beds;
	TSet<FName> Shops, Workplaces;
	const bool bHasHall = Plots.ContainsByPredicate([](const FTownPlot& P){ return P.bBuilt && !P.bScenery && P.Kind == ETownBuilding::Guild; });
	for (const FTownPlot& Plot : Plots)
	{
		if (!Plot.bBuilt || (Plot.bScenery && Plot.Kind != ETownBuilding::Farm)) continue;
		if (Plot.Kind == ETownBuilding::House) Beds.Add(Plot.Id, FMath::Max(0, Plot.BedBonus - (Plot.CatalogId == TEXT("InheritedHouse") ? 1 : 0)));
		if (Plot.Kind == ETownBuilding::Shop) Shops.Add(Plot.Id);
		if (Plot.Kind == ETownBuilding::Shop || Plot.Kind == ETownBuilding::Guild || (bHasHall && (Plot.Kind == ETownBuilding::Warehouse || Plot.Kind == ETownBuilding::Farm || Plot.Kind == ETownBuilding::Bakery || Plot.Kind == ETownBuilding::Smith))) Workplaces.Add(Plot.Id);
	}
	for (ARoomVolume* Room : DynamicRooms)
	{
		if (Room)
		{
			const FName RoomId = Room->GetFName();
			switch (Room->CurrentFunction)
			{
			case ERoomFunction::Inn:
				Beds.Add(RoomId, 2);
				Workplaces.Add(RoomId);
				break;
			case ERoomFunction::Shop:
				Shops.Add(RoomId);
				Workplaces.Add(RoomId);
				break;
			case ERoomFunction::Blacksmith:
			case ERoomFunction::Bakery:
			case ERoomFunction::Farmhouse:
			case ERoomFunction::AdventurersGuild:
				Workplaces.Add(RoomId);
				break;
			default:
				break;
			}
		}
	}
	TMap<FName,FHiredAdventurer*> Adventurers;
 if(bUseOrganicGolemNeeds)
 {
  TArray<FHiredAdventurer>* Roster=nullptr;
  if(VillagePlayer.IsValid() && bVillagePlayerRestored && VillagePlayer->PartyReserve)Roster=&VillagePlayer->PartyReserve->Reserve;
  else if(PendingVillageSave && PendingVillageSave->bHasPlayerProgress)Roster=&PendingVillageSave->PlayerReserve;
  if(Roster)for(FHiredAdventurer& A:*Roster)
  {
   if(A.bAssignedToRampage || A.AdventurerID.IsNone())continue;
   if(!A.GolemId.IsValid())A.GolemId=FGuid::NewGuid();
   UGolemNeedsLibrary::Initialize(A.Drives,A.GolemId);Adventurers.Add(A.AdventurerID,&A);
  }
 }
 TSet<FName> AssignedAdventurers;
 TSet<FName> AssignedWorkplaces;
	TSet<FGuid> Ids;
	GolemResidents.RemoveAll([&](const FVillageGolemRecord& Record)
	{
  if(!Record.Id.IsValid() || Ids.Contains(Record.Id))return true;
  if(!Record.AdventurerId.IsNone())
  {
   if(!Adventurers.Contains(Record.AdventurerId) || AssignedAdventurers.Contains(Record.AdventurerId))return true;
   AssignedAdventurers.Add(Record.AdventurerId);
  }
  else
  {
   if(!Workplaces.Contains(Record.WorkPlot) || AssignedWorkplaces.Contains(Record.WorkPlot))return true;
   AssignedWorkplaces.Add(Record.WorkPlot);
  }
  Ids.Add(Record.Id);return false;
	});
	auto TakeBed = [&](FName Preferred) -> FName
	{
		if (int32* Free = Beds.Find(Preferred); Free && *Free > 0) { --*Free; return Preferred; }
		for (const FTownPlot& Plot : Plots)
			if (int32* Free = Beds.Find(Plot.Id); Free && *Free > 0) { --*Free; return Plot.Id; }
		return NAME_None;
	};
	for (FVillageGolemRecord& Record : GolemResidents) Record.HomePlot = TakeBed(Record.HomePlot);
	TArray<FTownPlot> HiringOrder = Plots;
	HiringOrder.StableSort([](const FTownPlot& A, const FTownPlot& B){ return A.Kind == ETownBuilding::Guild && B.Kind != ETownBuilding::Guild; });
	for (const FTownPlot& Plot : HiringOrder)
	{
		if (!Workplaces.Contains(Plot.Id)) continue;
		if (Shops.Contains(Plot.Id) && !GolemShops.ContainsByPredicate([&](const FVillageShopState& State) { return State.Plot == Plot.Id; }))
		{ FVillageShopState State; State.Plot = Plot.Id; EnsureShopStock(State, false); GolemShops.Add(State); }
		if (AssignedWorkplaces.Contains(Plot.Id)) continue;
		const FName Home = TakeBed(NAME_None);
		if (Home.IsNone()) continue;
		FVillageGolemRecord Record; Record.Id = FGuid::NewGuid(); Record.HomePlot = Home; Record.WorkPlot = Plot.Id;
		Record.bFemale = GolemResidents.Num() % 2 != 0;
		Record.SupplyIndex = SupplySites.IsEmpty() ? 0 : GolemResidents.Num() % SupplySites.Num();
		Record.Name = FString::Printf(TEXT("%s %d"), Record.bFemale ? TEXT("Lumi") : TEXT("Niri"), GolemResidents.Num() + 1);
		GolemResidents.Add(Record); AssignedWorkplaces.Add(Plot.Id);
	}

 // Add off-duty roster members after preserving existing housing assignments.
 TArray<FName> AdventurerIds;Adventurers.GetKeys(AdventurerIds);AdventurerIds.Sort(FNameLexicalLess());
 for(FName Id:AdventurerIds)
 {
  if(AssignedAdventurers.Contains(Id))continue;
  const FName Home=TakeBed(NAME_None);if(Home.IsNone())continue;
  const FHiredAdventurer& A=*Adventurers[Id];FVillageGolemRecord R;
  R.Id=A.GolemId;R.AdventurerId=Id;R.Name=A.Name.ToString();R.HomePlot=Home;R.Drives=A.Drives;R.ClassId=A.ClassId;R.bFemale=A.bHasChosenBody?A.bFemaleBody:GolemResidents.Num()%2!=0;GolemResidents.Add(R);
 }
 for(FVillageGolemRecord& R:GolemResidents)
 {
  UGolemNeedsLibrary::Initialize(R.Drives,R.Id);
  if(FHiredAdventurer** A=Adventurers.Find(R.AdventurerId);A && (*A)->bHasChosenBody){R.ClassId=(*A)->ClassId;R.bFemale=(*A)->bFemaleBody;}
 }
	GolemShops.RemoveAll([&](const FVillageShopState& State) { return !Shops.Contains(State.Plot); });
	ShopWood = 0; ShopCoin = 0;
	for (FVillageShopState& State : GolemShops) { EnsureShopStock(State, false); ShopWood += State.Wood; ShopCoin += State.Coins; }
	TMap<FGuid, AVillageGolemCitizen*> Existing;
	for (TActorIterator<AVillageGolemCitizen> It(GetWorld()); It; ++It)
	{
		if (It->GetOwner() != this) continue;
		if (Existing.Contains(It->GolemId) || !GolemResidents.ContainsByPredicate([&](const FVillageGolemRecord& Record) { return Record.Id == It->GolemId && !Record.HomePlot.IsNone(); })) It->Destroy();
		else Existing.Add(It->GolemId, *It);
	}
	for (const FVillageGolemRecord& Record : GolemResidents)
	{
		const FTownPlot* Home = FindPlot(Record.HomePlot);
		if (!Home) continue;
		AVillageGolemCitizen* Citizen = Existing.FindRef(Record.Id);
		if (!Citizen)
		{
			FActorSpawnParameters Params; Params.Owner = this; Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButDontSpawnIfColliding;
			const FVector Position = Record.bHasPosition ? Record.Position : GolemHomeEntrance(*this, Record) + FVector(0, 0, 99);
			Citizen = GetWorld()->SpawnActor<AVillageGolemCitizen>(Position, FRotator::ZeroRotator, Params);
			if (Citizen) Citizen->Configure(this, Record);
		}
		if (Citizen) { Citizen->Mind.HomeId = Record.HomePlot; if(Citizen->AppearanceClass!=Record.ClassId || Citizen->bFemaleAppearance!=Record.bFemale)Citizen->Configure(this,Record); }
	}
}

const TArray<FVillageShopOffer>& AVillageRuntime::ShopCatalog()
{
	static const TArray<FVillageShopOffer> Offers = []()
	{
		TArray<FVillageShopOffer> List;
		auto Push = [&List](const TCHAR* Id, const TCHAR* Name, const TCHAR* Cat, int32 Buy, int32 Sell, int32 StartStock, int32 TargetStock, int32 MinDay = 1, bool bSmith = false, bool bLate = false)
		{
			FVillageShopOffer O;
			O.ItemId = FName(Id);
			O.DisplayName = Name;
			O.Category = Cat;
			O.BuyPrice = Buy;
			O.SellPrice = Sell;
			O.DefaultStock = StartStock;
			O.DailyTargetStock = TargetStock;
			O.MinDay = MinDay;
			O.bRequireSmith = bSmith;
			O.bRequireMidTrustOrBank = bLate;
			List.Add(O);
		};
		Push(TEXT("Wood"),      TEXT("Timber"),       TEXT("Material"),  2,  2, 4, 6);
		Push(TEXT("Stone"),     TEXT("Quarry Stone"), TEXT("Material"),  3,  2, 3, 5);
		Push(TEXT("Wheat"),     TEXT("Wheat Grain"),  TEXT("Supply"),    3,  2, 2, 4);
		Push(TEXT("Bread"),     TEXT("Field Bread"),  TEXT("Provision"), 5,  3, 2, 4);
		Push(TEXT("Fish"),      TEXT("River Fish"),   TEXT("Provision"), 4,  3, 1, 3);
		Push(TEXT("ToolParts"), TEXT("Tool Parts"),   TEXT("Craft"),     8,  6, 1, 3, 1, true, false);
		Push(TEXT("Iron"),      TEXT("Iron Ore"),     TEXT("Tower Ore"),10,  7, 1, 3, 2, false, false);
		Push(TEXT("Crystal"),   TEXT("Runic Crystal"),TEXT("Relic"),    24, 16, 0, 2, 1, false, true);
		return List;
	}();
	return Offers;
}

const FVillageShopOffer* AVillageRuntime::FindShopOffer(FName ItemId)
{
	return ShopCatalog().FindByPredicate([ItemId](const FVillageShopOffer& O) { return O.ItemId == ItemId; });
}

bool AVillageRuntime::IsShopOfferUnlocked(FName ItemId) const
{
	const FVillageShopOffer* O = FindShopOffer(ItemId);
	if (!O) return false;
	const AIsekaiVillageCharacter* Player = ActiveTownPlayer();
	const bool bVault = Player && Player->HasSphereSkill(TEXT("VaultStock"));
	if (DayIndex < O->MinDay && !bVault) return false;
	if (O->bRequireSmith && !HasBuilding(ETownBuilding::Smith) && !bVault) return false;
	if (O->bRequireMidTrustOrBank && Trust < 30 && !HasBuilding(ETownBuilding::Bank) && !bVault) return false;
	return true;
}

int32 AVillageRuntime::GetShopBuyPrice(FName ItemId, const AIsekaiVillageCharacter* Player) const
{
	const FVillageShopOffer* O = FindShopOffer(ItemId);
	const int32 Base = O ? O->BuyPrice : 2;
	const bool bHaggle = Player && Player->HasSphereSkill(TEXT("ShopHaggle"));
	return bHaggle ? FMath::Max(1, FMath::FloorToInt(static_cast<float>(Base) * 0.8f)) : Base;
}

int32 AVillageRuntime::GetShopSellPrice(FName ItemId, const AIsekaiVillageCharacter* Player) const
{
	const FVillageShopOffer* O = FindShopOffer(ItemId);
	const int32 RawSell = O ? O->SellPrice : 2;
	const bool bHaggle = Player && Player->HasSphereSkill(TEXT("ShopHaggle"));
	const int32 BaseSell = RawSell + (bHaggle ? FMath::Max(1, RawSell / 2) : 0);
	const int32 GaldBonus = Player ? Player->SphereTotals.GaldPercent : 0;
	return FMath::Max(BaseSell, FMath::RoundToInt(static_cast<float>(BaseSell) * (1.0f + static_cast<float>(GaldBonus) / 100.0f)));
}

int32 AVillageRuntime::GetShopItemStock(FName ShopPlot, FName ItemId) const
{
	const FVillageShopState* Shop = GolemShops.FindByPredicate([&](const FVillageShopState& S) { return S.Plot == ShopPlot; });
	if (!Shop) return 0;
	if (ItemId == TEXT("Wood"))
	{
		if (const int32* Found = Shop->Stock.Find(ItemId)) return FMath::Max(0, *Found);
		return FMath::Max(0, Shop->Wood);
	}
	return FMath::Max(0, Shop->Stock.FindRef(ItemId));
}

FString AVillageRuntime::ShopKeeperName(FName ShopPlot) const
{
	for (const FVillageGolemRecord& R : GolemResidents)
	{
		if (R.WorkPlot == ShopPlot && !R.HomePlot.IsNone()) return R.Name;
	}
	return TEXT("No keeper housed");
}

void AVillageRuntime::EnsureShopStock(FVillageShopState& Shop, bool bDailyRollover) const
{
	Shop.Wood = FMath::Max(0, Shop.Wood);
	Shop.Coins = FMath::Max(0, Shop.Coins);
	if (Shop.Stock.IsEmpty())
	{
		for (const FVillageShopOffer& O : ShopCatalog())
		{
			Shop.Stock.Add(O.ItemId, O.ItemId == TEXT("Wood") ? Shop.Wood : O.DefaultStock);
		}
		Shop.RestockDay = FMath::Max(1, Shop.RestockDay);
	}
	else
	{
		Shop.Stock.FindOrAdd(TEXT("Wood")) = Shop.Wood;
		for (const FVillageShopOffer& O : ShopCatalog())
		{
			if (!Shop.Stock.Contains(O.ItemId))
			{
				Shop.Stock.Add(O.ItemId, O.DefaultStock);
			}
		}
	}
	if (bDailyRollover && Shop.RestockDay < DayIndex)
	{
		Shop.RestockDay = DayIndex;
		const AIsekaiVillageCharacter* Player = ActiveTownPlayer();
		const int32 VaultBonus = (Player && Player->HasSphereSkill(TEXT("VaultStock"))) ? 2 : 0;
		const int32 CoinBoost = (HasBuilding(ETownBuilding::Bank) || Trust >= 35) ? 14 : 8;
		if (Shop.Coins < 50) Shop.Coins = FMath::Min(65, Shop.Coins + CoinBoost);
		for (const FVillageShopOffer& O : ShopCatalog())
		{
			if (!IsShopOfferUnlocked(O.ItemId)) continue;
			int32& Count = Shop.Stock.FindOrAdd(O.ItemId);
			Count = FMath::Max(Count, O.DailyTargetStock + VaultBonus);
		}
		Shop.Wood = FMath::Max(0, Shop.Stock.FindRef(TEXT("Wood")));
	}
}

FName AVillageRuntime::NearestBuiltShop(const FVector& Position) const
{
	FName Best = NAME_None; double Distance = FMath::Square(450.);
	for (const FVillageShopState& Shop : GolemShops)
		if (const FTownPlot* Plot = FindPlot(Shop.Plot))
		{
			const double D = FVector::DistSquared2D(Position, Plot->Location + Plot->StakeOffset);
			if (D <= Distance) { Best = Shop.Plot; Distance = D; }
		}
	return Best;
}

FName AVillageRuntime::NearestGolemShop(const FVector& Position) const
{
	return NearestBuiltShop(Position);
}

bool AVillageRuntime::IsShopStaffed(FName ShopPlot) const
{
	if ((!bUseOrganicGolemNeeds && WindowIndex == 7) || !GetWorld()) return false;
	for (TActorIterator<AVillageGolemCitizen> It(GetWorld()); It; ++It)
		if (It->GetOwner() == this && It->WorkPlot == ShopPlot && It->GoalPlace == EVillagePlace::Shop && It->AtGoal(130.f) && (!bUseOrganicGolemNeeds || !GolemResidents.ContainsByPredicate([&](const FVillageGolemRecord& R){return R.Id==It->GolemId && R.Drives.Activity!=TEXT("Work");}))) return true;
	return false;
}

bool AVillageRuntime::TradeShopItem(FName ShopPlot, FName ItemId, bool bBuy, AIsekaiVillageCharacter* Player)
{
	auto FailMsg = [&](const FString& Msg) { LastShopMessage = Msg; if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Yellow, Msg); return false; };
	if (!bUseGolemVillage || !Player || !Player->Gather || ShopPlot.IsNone() || NearestGolemShop(Player->GetActorLocation()) != ShopPlot)
	{
		return FailMsg(TEXT("Stand near the shop counter to trade."));
	}
	const FVillageShopOffer* Offer = FindShopOffer(ItemId);
	if (!Offer) return FailMsg(TEXT("Unknown store item."));
	if (bBuy && !IsShopOfferUnlocked(ItemId))
	{
		return FailMsg(FString::Printf(TEXT("%s unlocks later (Smith / Day / Bank or Vault Stock)."), *Offer->DisplayName));
	}
	FVillageShopState* Shop = GolemShops.FindByPredicate([&](const FVillageShopState& State) { return State.Plot == ShopPlot; });
	if (!Shop || !IsShopStaffed(ShopPlot))
	{
		return FailMsg(TEXT("Shop closed. A housed shopkeeper must be at work."));
	}
	EnsureShopStock(*Shop, false);
	int32& StockCount = Shop->Stock.FindOrAdd(ItemId);
	const int32 BuyPrice = GetShopBuyPrice(ItemId, Player);
	const int32 SellPay = GetShopSellPrice(ItemId, Player);
	if (bBuy)
	{
		if (StockCount <= 0 || Player->Gather->GetCount(TEXT("Coin")) < BuyPrice)
		{
			return FailMsg(FString::Printf(TEXT("Buying %s needs %d coin(s) and shop stock."), *Offer->DisplayName, BuyPrice));
		}
		Player->Gather->Consume(TEXT("Coin"), BuyPrice);
		Player->Gather->AddItem(ItemId, 1);
		--StockCount;
		Shop->Coins += BuyPrice;
		LastShopMessage = FString::Printf(TEXT("Bought 1 %s for %d coin(s)."), *Offer->DisplayName, BuyPrice);
	}
	else
	{
		if (Shop->Coins < SellPay || Player->Gather->GetCount(ItemId) < 1)
		{
			return FailMsg(FString::Printf(TEXT("Selling %s needs 1 in pack and %d coins in the shop till."), *Offer->DisplayName, SellPay));
		}
		Player->Gather->Consume(ItemId, 1);
		Player->Gather->AddItem(TEXT("Coin"), SellPay);
		++StockCount;
		Shop->Coins -= SellPay;
		if (ItemId == TEXT("Wood"))
		{
			++WoodSoldToday;
			for (FDayMission& Mission : TodayMissions) if (Mission.Kind == EDayMissionKind::StockStall && !Mission.bClaimed) Mission.Have = FMath::Min(Mission.Need, WoodSoldToday);
		}
		else
		{
			for (FDayMission& Mission : TodayMissions)
				if (Mission.Kind == EDayMissionKind::StockStall && !Mission.bClaimed)
					Mission.Have = FMath::Min(Mission.Need, Mission.Have + 1);
		}
		Trust = FMath::Min(99, Trust + 1);
		LastShopMessage = FString::Printf(TEXT("Sold 1 %s for %d coin(s)."), *Offer->DisplayName, SellPay);
	}
	if (ItemId == TEXT("Wood")) Shop->Wood = FMath::Max(0, StockCount);
	ShopWood = 0; ShopCoin = 0;
	for (const FVillageShopState& State : GolemShops) { ShopWood += State.Wood; ShopCoin += State.Coins; }
	if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Yellow, LastShopMessage);
	SaveVillageState(Player);
	return true;
}

bool AVillageRuntime::TradeWood(FName ShopPlot, bool bBuy, AIsekaiVillageCharacter* Player)
{
	return TradeShopItem(ShopPlot, TEXT("Wood"), bBuy, Player);
}

bool AVillageRuntime::ReinforceWallWithToolParts(AIsekaiVillageCharacter* Player)
{
	if (!Player || !Player->Gather) return false;
	if (WallIntegrity >= 100)
	{
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan, TEXT("Village walls are already at 100% integrity."));
		return false;
	}
	if (Player->Gather->GetCount(TEXT("ToolParts")) < 1 || Player->Gather->GetCount(TEXT("Wood")) < 2)
	{
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.2f, FColor::Orange, TEXT("Reinforcing walls needs 1 Tool Parts and 2 Wood."));
		return false;
	}
	Player->Gather->Consume(TEXT("ToolParts"), 1);
	Player->Gather->Consume(TEXT("Wood"), 2);
	WallIntegrity = FMath::Min(100, WallIntegrity + 50);
	Trust = FMath::Min(99, Trust + 2);
	for (FDayMission& Mission : TodayMissions)
	{
		if (Mission.Kind == EDayMissionKind::RepairWall && !Mission.bClaimed)
		{
			RewardMission(Player, Mission);
			break;
		}
	}
	if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.8f, FColor::Cyan,
		FString::Printf(TEXT("Reinforced village walls with Tool Parts! Wall %d%%  Trust %d"), WallIntegrity, Trust));
	SaveVillageState(Player);
	return true;
}

void AVillageRuntime::ReadVillageState(UTownConstructionSave* Saved)
{
	PendingVillageSave = Saved;
 TowerFloor=Saved?Saved->TowerFloor:FTowerFloorProgress();
	bVillagePlayerRestored = false;
	GolemResidents.Reset(); GolemShops.Reset(); HallSupplies.Reset();
	if (!Saved || !Saved->bHasVillageState) return;
	GolemResidents = Saved->Golems; GolemShops = Saved->Shops;
	if (Saved->bHasSupplies) { SupplySites = Saved->SupplySites; HallSupplies = Saved->HallSupplies; }
	for (FVillageSupplySite& Site : SupplySites) Site.Stock = FMath::Max(0, Site.Stock);
	for (auto& Pair : HallSupplies) Pair.Value = FMath::Max(0, Pair.Value);
	DayIndex = FMath::Max(1, Saved->VillageDay); WindowIndex = FMath::Clamp(Saved->VillageWindow, 0, 7);
	Weather = Saved->VillageWeather; Trust = FMath::Clamp(Saved->VillageTrust, 0, 99);
	FoodStock = FMath::Max(0, Saved->VillageFood); WoodSoldToday = FMath::Max(0, Saved->VillageWoodSold);
	TodayMissions = Saved->VillageMissions;
	if (Saved->bHasWallIntegrity) WallIntegrity = FMath::Clamp(Saved->VillageWallIntegrity, 0, 100);
	if (Saved->bHasTownServices)
	{
		BankVaultCoins = FMath::Max(0, Saved->BankVaultCoins);
		TownGuildRank = FMath::Clamp(Saved->TownGuildRank, 0, 4);
		AcademyResearchLevel = FMath::Clamp(Saved->AcademyResearchLevel, 0, 3);
		ActiveChapelBlessing = Saved->ActiveChapelBlessing;
		ActiveRoyalEdict = Saved->ActiveRoyalEdict;
		bBathhouseSoakedToday = Saved->bBathhouseSoakedToday;
		BellRungDay = FMath::Max(0, Saved->BellRungDay);
		StipendCollectedDay = FMath::Max(0, Saved->StipendCollectedDay);
		RoyalGrantDay = FMath::Max(0, Saved->RoyalGrantDay);
	}
	for (FVillageShopState& Shop : GolemShops) { EnsureShopStock(Shop, false); }
}

void AVillageRuntime::RestoreVillagePlayer()
{
	if (!bUseGolemVillage || bVillagePlayerRestored) return;
	AIsekaiVillageCharacter* Player = VillagePlayer.Get();
	if (!Player) Player = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
	if (!Player || !Player->Gather) return;
	VillagePlayer = Player;
	if (PendingVillageSave && PendingVillageSave->bHasVillageState && PendingVillageSave->bHasPlayerInventory)
	{
		Player->Gather->Stacks.Reset();
		for (const FGatherStack& Stack : PendingVillageSave->PlayerInventory) Player->Gather->AddItem(Stack.ItemId, Stack.Count);
		Player->Gather->AxeTier = PendingVillageSave->AxeTier; Player->Gather->PickaxeTier = PendingVillageSave->PickaxeTier;
	}
	if (PendingVillageSave && PendingVillageSave->bHasPlayerProgress)
	{
		const int32 MaxDisc = (Player->SphereGrid && Player->SphereGrid->DiscCount() > 0) ? (Player->SphereGrid->DiscCount() - 1) : 11;
		Player->UnlockedSphereNodes = PendingVillageSave->PlayerSphereNodes; Player->SpherePoints = FMath::Max(0, PendingVillageSave->PlayerSpherePoints);
		Player->SphereDisc = FMath::Clamp(PendingVillageSave->PlayerSphereDisc, 0, MaxDisc); Player->bSphereGridFlipped = PendingVillageSave->bPlayerGridFlipped;
		Player->bWorkFlipped = PendingVillageSave->bPlayerWorkFlipped; Player->bCenterBUnlocked = PendingVillageSave->bPlayerCenterBUnlocked;
		if (Player->PartyReserve) Player->PartyReserve->Reserve = PendingVillageSave->PlayerReserve;
		Player->RefreshSphereGridBonuses();
	}
	if(Player->PartyReserve)Player->PartyReserve->bUseGolemRoster=true;
	bVillagePlayerRestored = true;
}

void AVillageRuntime::WriteVillageState(UTownConstructionSave* Saved)
{
	if(VillagePlayer.IsValid() && VillagePlayer->PartyReserve)
  for(const FVillageGolemRecord& R:GolemResidents)if(!R.AdventurerId.IsNone())
   if(FHiredAdventurer* A=VillagePlayer->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==R.AdventurerId;}))A->Drives=R.Drives;
 Saved->bHasSupplies = true; Saved->SupplySites = SupplySites; Saved->HallSupplies = HallSupplies;
	Saved->bHasVillageState = true; Saved->Golems = GolemResidents; Saved->Shops = GolemShops;
	for (TActorIterator<AVillageGolemCitizen> It(GetWorld()); It; ++It)
		if (It->GetOwner() == this)
			if (FVillageGolemRecord* Record = Saved->Golems.FindByPredicate([&](const FVillageGolemRecord& R) { return R.Id == It->GolemId; }))
			{ Record->Position = It->GetActorLocation(); Record->bHasPosition = true; }
	Saved->TowerFloor=TowerFloor;
 if(auto* Tower=ATowerExpedition::Find(this))Tower->PreserveVillagePositions(Saved);
 GolemResidents = Saved->Golems;
	AIsekaiVillageCharacter* Player = VillagePlayer.Get();
	if (Player && Player->Gather && bVillagePlayerRestored)
	{
		Saved->bHasPlayerInventory = true; Saved->PlayerInventory = Player->Gather->Stacks;
		Saved->AxeTier = Player->Gather->AxeTier; Saved->PickaxeTier = Player->Gather->PickaxeTier;
		Saved->bHasPlayerProgress = true; Saved->PlayerSphereNodes = Player->UnlockedSphereNodes; Saved->PlayerSpherePoints = Player->SpherePoints;
		Saved->PlayerSphereDisc = Player->SphereDisc; Saved->bPlayerGridFlipped = Player->bSphereGridFlipped; Saved->bPlayerWorkFlipped = Player->bWorkFlipped; Saved->bPlayerCenterBUnlocked = Player->bCenterBUnlocked;
		if (Player->PartyReserve) Saved->PlayerReserve = Player->PartyReserve->Reserve;
	}
	else if (PendingVillageSave && PendingVillageSave->bHasPlayerInventory)
	{
		Saved->bHasPlayerInventory = true; Saved->PlayerInventory = PendingVillageSave->PlayerInventory;
		Saved->AxeTier = PendingVillageSave->AxeTier; Saved->PickaxeTier = PendingVillageSave->PickaxeTier;
		Saved->bHasPlayerProgress = PendingVillageSave->bHasPlayerProgress; Saved->PlayerSphereNodes = PendingVillageSave->PlayerSphereNodes; Saved->PlayerSpherePoints = PendingVillageSave->PlayerSpherePoints;
		Saved->PlayerSphereDisc = PendingVillageSave->PlayerSphereDisc; Saved->bPlayerGridFlipped = PendingVillageSave->bPlayerGridFlipped; Saved->bPlayerWorkFlipped = PendingVillageSave->bPlayerWorkFlipped; Saved->bPlayerCenterBUnlocked = PendingVillageSave->bPlayerCenterBUnlocked; Saved->PlayerReserve = PendingVillageSave->PlayerReserve;
	}
	Saved->VillageDay = DayIndex; Saved->VillageWindow = WindowIndex; Saved->VillageWeather = Weather;
	Saved->VillageTrust = Trust; Saved->VillageFood = FoodStock; Saved->VillageWoodSold = WoodSoldToday; Saved->VillageMissions = TodayMissions;
	Saved->bHasWallIntegrity = true;
	Saved->VillageWallIntegrity = WallIntegrity;
	Saved->bHasTownServices = true;
	Saved->BankVaultCoins = BankVaultCoins;
	Saved->TownGuildRank = TownGuildRank;
	Saved->AcademyResearchLevel = AcademyResearchLevel;
	Saved->ActiveChapelBlessing = ActiveChapelBlessing;
	Saved->ActiveRoyalEdict = ActiveRoyalEdict;
	Saved->bBathhouseSoakedToday = bBathhouseSoakedToday;
	Saved->BellRungDay = BellRungDay;
	Saved->StipendCollectedDay = StipendCollectedDay;
	Saved->RoyalGrantDay = RoyalGrantDay;
}

bool AVillageRuntime::SaveVillageState(AIsekaiVillageCharacter* Player)
{
	if (!bUseGolemVillage || ConstructionSaveSlot.IsEmpty()) return false;
	if (Player) VillagePlayer = Player;
	RestoreVillagePlayer();
	bLastVillageSaveSucceeded = SaveConstruction();
	return bLastVillageSaveSucceeded;
}

void AVillageRuntime::ReloadVillageState(AIsekaiVillageCharacter* Player)
{
	VillagePlayer = Player;
	// Reload recreates actors, avoiding stale positions or duplicate workers.
	for (TActorIterator<AVillageGolemCitizen> It(GetWorld()); It; ++It) if (It->GetOwner() == this) It->Destroy();
	InitializeConstruction(); RestoreVillagePlayer();
}

void AVillageRuntime::TickGolemVillage(float DeltaSeconds)
{
 RestoreVillagePlayer();
 const AIsekaiVillageCharacter* TownChar = ActiveTownPlayer();
 const int32 VaultRestock = (TownChar && TownChar->HasSphereSkill(TEXT("VaultStock"))) ? 2 : 0;
 for(FVillageSupplySite& Site:SupplySites)if(Site.DailyRestock>0 && Site.RestockDay<DayIndex){Site.Stock=FMath::Max(Site.Stock,Site.DailyRestock+VaultRestock);Site.RestockDay=DayIndex;}
	for (TActorIterator<AVillageGolemCitizen> It(GetWorld()); It; ++It)
	{
		if (It->GetOwner() != this) continue;
  if(It->ActorHasTag(TEXT("ElrhunTowerParty")))continue;
		if (AdvanceGolemNeeds(*It,DeltaSeconds)) continue;
		if (AdvanceHallCourier(*It, DeltaSeconds) || AdvanceProductionWorker(*It, DeltaSeconds)) continue;
		const FVillageGolemRecord* Record = GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R) { return R.Id == It->GolemId; });
		if (!Record) continue;
		const bool bRest = (WindowIndex == 7);
		if (bRest)
		{
			ALinchpinProp* BedProp = FindBedForGolem(*Record);
			if (BedProp)
			{
				It->SetGoal(EVillagePlace::House, BedProp->GetActorLocation());
				if (It->AtGoal(130.f))
				{
					It->SetWorkRoutine(EGolemWorkRoutine::Sleeping_In_Bed, BedProp);
				}
			}
			else
			{
				It->SetGoal(EVillagePlace::House, GolemHomeEntrance(*this, *Record));
			}
		}
		else
		{
			// Check if assigned to a dynamic room
			ARoomVolume* DynamicRoom = FindDynamicRoom(Record->WorkPlot);
			if (DynamicRoom)
			{
				FName PreferredTag = NAME_None;
				EGolemWorkRoutine DesiredRoutine = EGolemWorkRoutine::None;
				switch (DynamicRoom->CurrentFunction)
				{
				case ERoomFunction::Blacksmith:
					PreferredTag = TEXT("Anvil");
					DesiredRoutine = EGolemWorkRoutine::Blacksmith_Hammering;
					break;
				case ERoomFunction::Inn:
					PreferredTag = TEXT("Counter");
					DesiredRoutine = EGolemWorkRoutine::Innkeeper_Hosting;
					break;
				case ERoomFunction::Shop:
					PreferredTag = TEXT("Counter");
					DesiredRoutine = EGolemWorkRoutine::Shopkeeper_Trading;
					break;
				case ERoomFunction::Bakery:
					PreferredTag = TEXT("Oven");
					DesiredRoutine = EGolemWorkRoutine::Baker_Baking;
					break;
				case ERoomFunction::Farmhouse:
				case ERoomFunction::AdventurersGuild:
					PreferredTag = TEXT("Workbench");
					DesiredRoutine = EGolemWorkRoutine::Craftsman_Working;
					break;
				case ERoomFunction::AlchemistLab:
					PreferredTag = TEXT("Cauldron");
					DesiredRoutine = EGolemWorkRoutine::Alchemist_Brewing;
					break;
				case ERoomFunction::Enchanter:
					PreferredTag = TEXT("ArcaneTable");
					DesiredRoutine = EGolemWorkRoutine::Enchanter_Inscribing;
					break;
				case ERoomFunction::ArcaneForge:
					PreferredTag = TEXT("CelestialAnvil");
					DesiredRoutine = EGolemWorkRoutine::Blacksmith_Hammering;
					break;
				default:
					break;
				}

				ALinchpinProp* Station = FindLinchpinPropInRoom(Record->WorkPlot, PreferredTag);
				const FVector StationLoc = Station ? Station->GetActorLocation() : DynamicRoom->GetActorLocation();
				It->SetGoal(EVillagePlace::Shop, StationLoc);
				if (It->AtGoal(130.f))
				{
					It->SetWorkRoutine(DesiredRoutine, Station);
					if (DynamicRoom->CurrentFunction == ERoomFunction::Shop)
					{
						if (FVillageShopState* S = GolemShops.FindByPredicate([&](const FVillageShopState& X) { return X.Plot == Record->WorkPlot; }))
						{
							EnsureShopStock(*S, true);
						}
					}
				}
			}
			else
			{
				const FTownPlot* Target = FindPlot(Record->WorkPlot);
				if (Target)
				{
					const FVector Counter = Target->Location + Target->StakeOffset + Target->StakeOffset.GetSafeNormal2D() * 150.f;
					It->SetGoal(EVillagePlace::Shop, Counter);
					if (It->AtGoal(130.f))
					{
						if (FVillageShopState* S = GolemShops.FindByPredicate([&](const FVillageShopState& X) { return X.Plot == Target->Id; }))
						{
							EnsureShopStock(*S, true);
						}
					}
				}
			}
		}
	}
	VillageSaveAccrued += DeltaSeconds;
	if (VillageSaveAccrued >= 10.f && bVillagePlayerRestored) { ReconcileGolemPopulation(); SaveVillageState(VillagePlayer.Get()); VillageSaveAccrued = 0; }
}

void AVillageRuntime::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (bUseGolemVillage && bVillagePlayerRestored) SaveVillageState(VillagePlayer.Get());
	Super::EndPlay(EndPlayReason);
}

FText AVillageRuntime::GolemVillageLine() const
{
	int32 Housed = 0, Beds = 0, Staffed = 0;
	for (const FVillageGolemRecord& Record : GolemResidents) if (!Record.HomePlot.IsNone()) ++Housed;
	for (const FTownPlot& Plot : Plots)
		if (Plot.bBuilt && !Plot.bScenery && Plot.Kind == ETownBuilding::House) Beds += FMath::Max(0, Plot.BedBonus - (Plot.CatalogId == TEXT("InheritedHouse") ? 1 : 0));
	for (const FVillageShopState& Shop : GolemShops) if (IsShopStaffed(Shop.Plot)) ++Staffed;
	FString Supplies;
	TArray<FName> Items; HallSupplies.GetKeys(Items); Items.Sort(FNameLexicalLess());
	for (FName Item : Items) Supplies += FString::Printf(TEXT(" %s:%d"), *Item.ToString(), HallSupplies[Item]);
	return FText::FromString(Supplies + TEXT("  Hall T: collect | ") + FString::Printf(TEXT("Guild Rank %s (%d pts) | Golem homes %d/%d   Shops open %d/%d   F5 save   T/Y/U interact"), *GetGuildRankName(), GetGuildStandingScore(), Housed, Beds, Staffed, GolemShops.Num()));
}

static EVillagePlace SupplySitePlace(FName Item)
{
	if (Item == TEXT("Fish")) return EVillagePlace::Lake;
	if (Item == TEXT("Stone") || Item == TEXT("Copper") || Item == TEXT("Iron") || Item == TEXT("Crystal")) return EVillagePlace::Mine;
	return EVillagePlace::Forest;
}

// A hall owns one housed courier. Cargo is debited at the source and credited
// only after the same worker physically reaches the hall frontage.
bool AVillageRuntime::AdvanceHallCourier(AVillageGolemCitizen* Worker, float DeltaSeconds)
{
 if (!Worker || Worker->GetOwner() != this || !bUseGolemVillage) return false;
 const FTownPlot* Workplace = FindPlot(Worker->WorkPlot);
 if (!Workplace || !Workplace->bBuilt || Workplace->bScenery || (Workplace->Kind != ETownBuilding::Guild && Workplace->Kind != ETownBuilding::Warehouse)) return false;
 const FTownPlot* Hall = Workplace->Kind == ETownBuilding::Guild ? Workplace : Plots.FindByPredicate([](const FTownPlot& P){ return P.bBuilt && !P.bScenery && P.Kind == ETownBuilding::Guild; });
 if (!Hall) { Worker->SetHarvesting(false, EVillagePlace::Forest); Worker->SetGoal(EVillagePlace::Warehouse, WorkerEntrance(*Workplace)); return true; }
 FVillageGolemRecord* Record = GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R){ return R.Id == Worker->GolemId; });
 if (!Record || Record->HomePlot.IsNone()) return true;
 if (WindowIndex == 7 && !bUseOrganicGolemNeeds)
 {
  Record->GatherSeconds = 0;
  Worker->SetHarvesting(false, EVillagePlace::Forest);
  Worker->SetGoal(EVillagePlace::House, GolemHomeEntrance(*this, *Record));
  return true;
 }
 const FVector Counter = Hall->Location + Hall->StakeOffset + Hall->StakeOffset.GetSafeNormal2D() * 150.f;
 if (Record->CargoCount > 0 && !Record->Cargo.IsNone())
 {
  Worker->SetHarvesting(false, EVillagePlace::Forest);
  Worker->SetGoal(EVillagePlace::Guild, Counter);
  if (Worker->AtGoal(180.f))
  {
   HallSupplies.FindOrAdd(Record->Cargo) += Record->CargoCount;
   Record->Cargo = NAME_None; Record->CargoCount = 0; Record->GatherSeconds = 0;
   ++Record->SupplyIndex; Record->bHasSupplyGoal=false;
   SaveVillageState(VillagePlayer.Get());
  }
  return true;
 }
 const AIsekaiVillageCharacter* TownChar = ActiveTownPlayer();
 const float WorkerPaceMult = TownChar ? (1.0f + FMath::Max(0.0f, TownChar->SphereTotals.WorkerPacePercent) / 100.0f) : 1.0f;
 const int32 VaultRestock = (TownChar && TownChar->HasSphereSkill(TEXT("VaultStock"))) ? 2 : 0;
 const int32 CourierBonus = (TownChar && TownChar->HasSphereSkill(TEXT("HallCharter"))) ? 1 : 0;
 for (FVillageSupplySite& Site : SupplySites)
  if (Site.DailyRestock > 0 && Site.RestockDay < DayIndex) { Site.Stock = FMath::Max(Site.Stock, Site.DailyRestock + VaultRestock); Site.RestockDay = DayIndex; }
 if (!SupplySites.IsEmpty())
 {
  if(bUseOrganicGolemNeeds && !Record->bHasSupplyGoal)
  {
   double Best=-UE_BIG_NUMBER;int32 Choice=INDEX_NONE;
   for(int32 I=0;I<SupplySites.Num();++I)
   {
    const auto& Site=SupplySites[I];if(Site.Stock<=0 || Site.Item.IsNone())continue;
    int32 Incoming=0;
    for(const auto& Other:GolemResidents)
    {
     if(Other.Id==Record->Id)continue;
     if(Other.Cargo==Site.Item)Incoming+=Other.CargoCount;
     else if(Other.bHasSupplyGoal && SupplySites.IsValidIndex(Other.SupplyIndex) && SupplySites[Other.SupplyIndex].Item==Site.Item)Incoming+=3;
    }
    const double Score=(12-HallSupplies.FindRef(Site.Item)-Incoming)*5.0-FVector::Dist2D(Worker->GetActorLocation(),Site.Location)*.00005;
    if(Score>Best){Best=Score;Choice=I;}
   }
   if(Choice!=INDEX_NONE){Record->SupplyIndex=Choice;Record->bHasSupplyGoal=true;}
  }
  const int32 Start = FMath::Max(0, Record->SupplyIndex) % SupplySites.Num();
  for (int32 Offset = 0; Offset < SupplySites.Num(); ++Offset)
  {
   const int32 Index = (Start + Offset) % SupplySites.Num();
   FVillageSupplySite& Site = SupplySites[Index];
   if (Site.Stock <= 0 || Site.Item.IsNone()) continue;
   const EVillagePlace SitePlace = SupplySitePlace(Site.Item);
   Record->SupplyIndex = Index;
   Worker->SetGoal(SitePlace, Site.Location);
   if (Worker->AtGoal(100.f))
   {
    Worker->SetHarvesting(true, SitePlace);
    Record->GatherSeconds += FMath::Max(0.f, DeltaSeconds) * WorkerPaceMult;
    if(bUseOrganicGolemNeeds)UGolemNeedsLibrary::RecordPractice(Record->Drives,TEXT("Logistics"),FMath::Min(DeltaSeconds,1.f));
    if (Record->GatherSeconds >= 4.f)
    {
     Record->Cargo = Site.Item; Record->CargoCount = FMath::Min(3 + CourierBonus, Site.Stock);
     Site.Stock -= Record->CargoCount; Record->GatherSeconds = 0;
     Worker->SetHarvesting(false, SitePlace);
     Worker->SetGoal(EVillagePlace::Guild, Counter);
     SaveVillageState(VillagePlayer.Get());
    }
   }
   else
   {
    Worker->SetHarvesting(false, SitePlace);
    Record->GatherSeconds = 0;
   }
   return true;
  }
 }
 Worker->SetHarvesting(false, EVillagePlace::Forest);
 Record->GatherSeconds = 0;
 Worker->SetGoal(EVillagePlace::Guild, Counter);
 return true;
}

bool AVillageRuntime::WithdrawHallSupplies(AIsekaiVillageCharacter* Player)
{
 if (!bUseGolemVillage || !Player || !Player->Gather) return false;
 for (const FTownPlot& Plot : Plots)
 {
  if (!Plot.bBuilt || Plot.bScenery || Plot.Kind != ETownBuilding::Guild || FVector::DistSquared2D(Player->GetActorLocation(), Plot.Location + Plot.StakeOffset) > FMath::Square(450.f)) continue;
  int32 Total = 0;
  for (auto& Pair : HallSupplies)
  {
   if (Pair.Key.IsNone() || Pair.Value <= 0) continue;
   Total += Pair.Value; Player->Gather->AddItem(Pair.Key, Pair.Value); Pair.Value = 0;
  }
  if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 3.f, FColor::Cyan, Total > 0 ? TEXT("Collected the adventure hall supplies.") : TEXT("Hall store empty. Housed couriers bring supplies here."));
  if (Total > 0) SaveVillageState(Player);
  return true; // Consume the interaction even when empty: do not hire by accident.
 }
 return false;
}

// Production workers collect a recipe's ingredients at the hall, make one
// batch at their workplace, then carry the result back. No remote output.
bool AVillageRuntime::AdvanceProductionWorker(AVillageGolemCitizen* Worker, float DeltaSeconds)
{
 if (!Worker || Worker->GetOwner()!=this || !bUseGolemVillage) return false;
 const FTownPlot* Work=FindPlot(Worker->WorkPlot);
 if (!Work || !Work->bBuilt || (Work->bScenery && Work->Kind!=ETownBuilding::Farm) || (Work->Kind!=ETownBuilding::Farm && Work->Kind!=ETownBuilding::Bakery && Work->Kind!=ETownBuilding::Smith)) return false;
 FVillageGolemRecord* R=GolemResidents.FindByPredicate([&](const FVillageGolemRecord& G){ return G.Id==Worker->GolemId; });
 if (!R || R->HomePlot.IsNone()) return true;
 if (WindowIndex==7 && !bUseOrganicGolemNeeds) { R->GatherSeconds=0; Worker->SetGoal(EVillagePlace::House,GolemHomeEntrance(*this,*R)); return true; }
 const FTownPlot* Hall=Plots.FindByPredicate([](const FTownPlot& P){return P.bBuilt && !P.bScenery && P.Kind==ETownBuilding::Guild;});
 const FVector Workplace=Work->Location+Work->StakeOffset+Work->StakeOffset.GetSafeNormal2D()*150.f;
 const EVillagePlace Place=Work->Kind==ETownBuilding::Farm ? EVillagePlace::Farm : Work->Kind==ETownBuilding::Bakery ? EVillagePlace::Bakery : EVillagePlace::Smith;
 if (!Hall) { Worker->SetGoal(Place,Workplace); R->GatherSeconds=0; return true; }
 const FVector Counter=Hall->Location+Hall->StakeOffset+Hall->StakeOffset.GetSafeNormal2D()*150.f;
 if (R->CargoCount>0 && !R->Cargo.IsNone())
 {
  Worker->SetGoal(EVillagePlace::Guild,Counter);
  if(Worker->AtGoal(180.f)) { HallSupplies.FindOrAdd(R->Cargo)+=R->CargoCount; R->Cargo=NAME_None; R->CargoCount=0; SaveVillageState(VillagePlayer.Get()); }
  return true;
 }
 const bool Farm=Work->Kind==ETownBuilding::Farm;
 const FName Ingredient=Work->Kind==ETownBuilding::Bakery ? FName(TEXT("Wheat")) : FName(TEXT("Stone"));
 if(!Farm && !R->bHasWorkInputs)
 {
  if (HallSupplies.FindRef(Ingredient)<2 || HallSupplies.FindRef(TEXT("Wood"))<1)
  { Worker->SetGoal(Place,Workplace); R->GatherSeconds=0; return true; }
  Worker->SetGoal(EVillagePlace::Guild,Counter);
  if(Worker->AtGoal(180.f) && HallSupplies.FindRef(Ingredient)>=2 && HallSupplies.FindRef(TEXT("Wood"))>=1)
  {
   HallSupplies.FindOrAdd(Ingredient)-=2; --HallSupplies.FindOrAdd(TEXT("Wood"));
   R->bHasWorkInputs=true; R->GatherSeconds=0; SaveVillageState(VillagePlayer.Get());
  }
  return true;
 }
 Worker->SetGoal(Place,Workplace);
 if (!Worker->AtGoal(100.f)) { R->GatherSeconds=0; return true; }
 const AIsekaiVillageCharacter* TownChar = ActiveTownPlayer();
 const float WorkerPaceMult = TownChar ? (1.0f + FMath::Max(0.0f, TownChar->SphereTotals.WorkerPacePercent) / 100.0f) : 1.0f;
 const int32 OutputBonus = (TownChar && TownChar->HasSphereSkill(TEXT("HallCharter"))) ? 1 : 0;
 R->GatherSeconds+=FMath::Max(0.f,DeltaSeconds)*(bUseOrganicGolemNeeds ? UGolemNeedsLibrary::WorkMultiplier(R->Drives) : 1.f)*WorkerPaceMult;
 if(bUseOrganicGolemNeeds)UGolemNeedsLibrary::RecordPractice(R->Drives,TEXT("Craft"),FMath::Min(DeltaSeconds,1.f));
 if(R->GatherSeconds>=20.f)
 {
  R->Cargo=Farm ? FName(TEXT("Wheat")) : Work->Kind==ETownBuilding::Bakery ? FName(TEXT("Bread")) : FName(TEXT("ToolParts"));
  R->CargoCount=(Farm || Work->Kind==ETownBuilding::Bakery ? 2 : 1)+OutputBonus;
  R->bHasWorkInputs=false; R->GatherSeconds=0;
  Worker->SetGoal(EVillagePlace::Guild,Counter); SaveVillageState(VillagePlayer.Get());
 }
 return true;
}

FText AVillageRuntime::GolemWantLine(FGuid Id) const
{
 const FVillageGolemRecord* R=GolemResidents.FindByPredicate([&](const FVillageGolemRecord& X){return X.Id==Id;});
 if(!R)return FText::GetEmpty();
 const auto& D=R->Drives;
 FString Line=FString::Printf(TEXT("%s | %s Recharge need %.0f / Curiosity %.0f / Company %.0f"),*R->Name,*D.Reason,D.Fatigue,D.Curiosity,D.Loneliness);
 if(!D.LearningLog.IsEmpty())Line+=TEXT(" | ")+D.LearningLog.Last();
 return FText::FromString(Line);
}

bool AVillageRuntime::AdvanceGolemNeeds(AVillageGolemCitizen* Worker,float DeltaSeconds)
{
 if(!bUseGolemVillage || !Worker || Worker->GetOwner()!=this)return false;
 if(Worker->ActorHasTag(TEXT("ElrhunTowerParty")))return true;
 if(Worker->ActorHasTag(TEXT("ElrhunBattleAssembly")) || Worker->ActorHasTag(TEXT("ElrhunSparring")))return true;
 if(!bUseOrganicGolemNeeds)return false;
 FVillageGolemRecord* R=GolemResidents.FindByPredicate([&](const FVillageGolemRecord& X){return X.Id==Worker->GolemId;});
 if(!R || R->HomePlot.IsNone())return false;
 FGolemDriveState& S=R->Drives;UGolemNeedsLibrary::Initialize(S,R->Id);
 UGolemNeedsLibrary::Elapse(S,DeltaSeconds);const float D=FMath::IsFinite(DeltaSeconds)?FMath::Clamp(DeltaSeconds,0.f,1.f):0.f;
 auto Front=[](const FTownPlot& P){return P.Location+P.StakeOffset+P.StakeOffset.GetSafeNormal2D()*150.f;};
 auto Nearest=[&](ETownBuilding Kind)->const FTownPlot*{
  const FTownPlot* Best=nullptr;double Distance=UE_BIG_NUMBER;
  for(const FTownPlot& P:Plots)if(P.bBuilt && !P.bScenery && P.Kind==Kind){const double V=FVector::DistSquared2D(Worker->GetActorLocation(),Front(P));if(V<Distance){Best=&P;Distance=V;}}
  return Best;
 };
 const FTownPlot* Work=FindPlot(R->WorkPlot);const FTownPlot* Hall=Nearest(ETownBuilding::Guild);
 const FTownPlot* Study=S.Interest==TEXT("Magic") ? Nearest(ETownBuilding::Academy) : Nearest(ETownBuilding::Training);
 if(!Study)Study=Nearest(ETownBuilding::Training);
 const FTownPlot* Meeting=Nearest(ETownBuilding::Inn);if(!Meeting)Meeting=Hall;
 bool CanWork=Work && Work->bBuilt;float Urgency=.2f;
 if(CanWork && Work->Kind==ETownBuilding::Farm){Urgency=FMath::Clamp((12.f-HallSupplies.FindRef(TEXT("Wheat")))/12.f,0.f,1.f);CanWork=Hall && Urgency>0;}
 else if(CanWork && (Work->Kind==ETownBuilding::Bakery || Work->Kind==ETownBuilding::Smith))
 {
  const FName Ingredient=Work->Kind==ETownBuilding::Bakery ? FName(TEXT("Wheat")):FName(TEXT("Stone"));
  CanWork=Hall && (R->bHasWorkInputs || (HallSupplies.FindRef(Ingredient)>=2 && HallSupplies.FindRef(TEXT("Wood"))>=1));Urgency=.9f;
 }
 else if(CanWork && Work->Kind==ETownBuilding::Shop)
 {
  const AIsekaiVillageCharacter* TC = ActiveTownPlayer();
  Urgency = (TC && FVector::DistSquared2D(TC->GetActorLocation(), Front(*Work)) < FMath::Square(800.f)) ? 1.0f : 0.65f;
 }
 else if(CanWork && (Work->Kind==ETownBuilding::Guild || Work->Kind==ETownBuilding::Warehouse))
 {
  CanWork=Hall && SupplySites.ContainsByPredicate([](const FVillageSupplySite& Site){return !Site.Item.IsNone() && Site.Stock>0;});
  Urgency=HallSupplies.FindRef(TEXT("Wood"))<6 || HallSupplies.FindRef(TEXT("Stone"))<4 ? 1.f:.3f;
 }
 const bool Cargo=R->CargoCount>0 || R->bHasWorkInputs;CanWork|=Cargo;
 if(S.ThinkIn<=0 || S.Fatigue>=90 || (S.Activity==TEXT("Work") && !CanWork))UGolemNeedsLibrary::ChooseActivity(S,CanWork,Study!=nullptr,Meeting && GolemResidents.Num()>1,Cargo,Urgency,WindowIndex==7);
 if(S.Passives.Contains(TEXT("FleetFooted")) && !Worker->Tags.Contains(TEXT("FleetFootedApplied"))){Worker->WalkSpeed*=UGolemNeedsLibrary::WalkingMultiplier(S);Worker->Tags.Add(TEXT("FleetFootedApplied"));}
 bool Handled=S.Activity!=TEXT("Work");
 if (Handled) Worker->SetHarvesting(false, Worker->HarvestPlace);
 const AIsekaiVillageCharacter* TownChar = ActiveTownPlayer();
 const float WorkerPaceMult = TownChar ? (1.0f + FMath::Max(0.0f, TownChar->SphereTotals.WorkerPacePercent) / 100.0f) : 1.0f;
 if(S.Activity==TEXT("Rest"))
 {
  Worker->Mind.Mutex=ECitizenMutex::Sleep;Worker->SetGoal(EVillagePlace::House,GolemHomeEntrance(*this,*R));
  const float BathMult = (TownChar && TownChar->HasSphereSkill(TEXT("BathhouseRegen")) && HasBuilding(ETownBuilding::Bath)) ? 1.5f : 1.0f;
  if(Worker->AtGoal(150.f)){S.Fatigue=FMath::Max(0.f,S.Fatigue-D*1.2f*BathMult*WorkerPaceMult);S.ActivitySeconds+=D;}
 }
 else if(S.Activity==TEXT("Practice") && Study)
 {
  Worker->Mind.Mutex=ECitizenMutex::Train;Worker->SetGoal(EVillagePlace::Training,Front(*Study));
  const float StudyMult = (TownChar && TownChar->HasSphereSkill(TEXT("SoulImprint"))) ? 1.5f : 1.0f;
  if(Worker->AtGoal(130.f))
  {
   UGolemNeedsLibrary::RecordPractice(S,S.Interest,D*StudyMult);S.Curiosity=FMath::Max(0.f,S.Curiosity-D*.12f);S.Fatigue=FMath::Min(100.f,S.Fatigue+D*.08f*UGolemNeedsLibrary::FatigueMultiplier(S));S.ActivitySeconds+=D;
  }
 }
 else if(S.Activity==TEXT("Socialize") && Meeting)
 {
  Worker->Mind.Mutex=ECitizenMutex::Idle;Worker->SetGoal(EVillagePlace::Inn,Front(*Meeting));
  const float InnMult = (TownChar && TownChar->HasSphereSkill(TEXT("InnHospitality"))) ? 1.5f : 1.0f;
  if(Worker->AtGoal(180.f))
  {
   S.ActivitySeconds+=D;
   for(TActorIterator<AVillageGolemCitizen> It(GetWorld());It;++It)if(*It!=Worker && It->GetOwner()==this && FVector::DistSquared2D(It->GetActorLocation(),Worker->GetActorLocation())<FMath::Square(300.f))
   {S.Loneliness=FMath::Max(0.f,S.Loneliness-D*2.f*InnMult);break;}
   if(S.ActivitySeconds>=30.f){S.LeisureCooldown=90;S.Commitment=0;S.ThinkIn=0;}
  }
 }
 else Worker->Mind.Mutex=ECitizenMutex::Gather;
 // A route blockage never awards practice. Give an unreachable leisure trip a break.
 if(Handled && Worker->bRouteBlocked && !Worker->AtGoal(180.f))
 {
  S.ActivitySeconds+=D;if(S.ActivitySeconds>=30.f){S.LeisureCooldown=90;S.Commitment=0;S.ThinkIn=0;}
 }
 if(!R->AdventurerId.IsNone() && VillagePlayer.IsValid() && VillagePlayer->PartyReserve)
 {
  if(FHiredAdventurer* A=VillagePlayer->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==R->AdventurerId;}))A->Drives=S;
  VillagePlayer->PartyReserve->RefreshLearnedArtes();
 }
 return Handled;
}

bool AVillageRuntime::SetGolemNeeds(FGuid Id,float Fatigue,float Curiosity,float Loneliness,FName Interest)
{
 if(!bUseOrganicGolemNeeds || !FMath::IsFinite(Fatigue) || !FMath::IsFinite(Curiosity) || !FMath::IsFinite(Loneliness))return false;
 if(Interest!=TEXT("Guard") && Interest!=TEXT("Magic") && Interest!=TEXT("Aid") && Interest!=TEXT("Scout") && Interest!=TEXT("Logistics") && Interest!=TEXT("Craft"))return false;
 auto* R=GolemResidents.FindByPredicate([&](const FVillageGolemRecord& X){return X.Id==Id;});if(!R)return false;
 UGolemNeedsLibrary::Initialize(R->Drives,Id);auto& S=R->Drives;
 S.Fatigue=FMath::Clamp(Fatigue,0.f,100.f);S.Curiosity=FMath::Clamp(Curiosity,0.f,100.f);S.Loneliness=FMath::Clamp(Loneliness,0.f,100.f);S.Interest=Interest;S.Commitment=0;S.ThinkIn=0;
 if(!R->AdventurerId.IsNone() && VillagePlayer.IsValid() && VillagePlayer->PartyReserve)
  if(auto* A=VillagePlayer->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==R->AdventurerId;}))A->Drives=S;
 return true;
}
