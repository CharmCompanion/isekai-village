// Copyright Epic Games, Inc. All Rights Reserved.
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "IsekaiVillageGameMode.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "MineRuntime.h"
#include "DungeonRuntime.h"
#include "MineOreVein.h"
#include "LakeFishingSpot.h"
#include "DayBoardCatalogWidgets.h"
#include "TownPlot.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FWorldLoopsAndFiveErasTest, "IsekaiVillage.Village.WorldLoopsAndFiveEras", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FWorldLoopsAndFiveErasTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues()
		.AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false)
		.CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	if (!TestNotNull(TEXT("World created"), W)) return false;

	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
	W->SetGameInstance(NewObject<UGameInstance>(GEngine));
	FURL URL;
	URL.AddOption(TEXT("game=/Script/Engine/GameModeBase"));
	W->SetGameMode(URL);

	FActorSpawnParameters P;
	P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	// 1. Verify Map_AnimeAdventure retired from MineRuntime & DungeonRuntime defaults
	AMineRuntime* MR = W->SpawnActor<AMineRuntime>(FVector(0, 0, -5000), FRotator::ZeroRotator, P);
	ADungeonRuntime* DR = W->SpawnActor<ADungeonRuntime>(FVector(0, 0, -8000), FRotator::ZeroRotator, P);
	TestTrue(TEXT("MineRuntime returns to Map_ElRuhnSky"), MR && MR->ReturnLevel.ToString().Contains(TEXT("Map_ElRuhnSky")));
	TestTrue(TEXT("DungeonRuntime returns to Map_ElRuhnSky"), DR && DR->ReturnLevel.ToString().Contains(TEXT("Map_ElRuhnSky")));

	// 2. Verify 5-Era Settlement Progression: Homestead -> Village -> Town -> Barony -> Kingdom
	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(0, 0, 200), FRotator::ZeroRotator, P);
	if (!TestNotNull(TEXT("Village created"), V) || !TestNotNull(TEXT("Player created"), Player)) { W->DestroyWorld(false); return false; }

	V->bUseAuthoredPlots = true;
	V->bUseGolemVillage = true;
	V->ConstructionSaveSlot = TEXT("AutoT3_World_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);

	FTownPlot Base;
	Base.WoodCost = 0; Base.BuildingClass = AStaticMeshActor::StaticClass();
	auto MakeSite = [&](const TCHAR* Id, ETownBuilding Kind, ETownEra Era, int32 Beds, FVector Loc)
	{
		FTownPlot S = Base; S.Id = Id; S.Kind = Kind; S.Era = Era; S.BedBonus = Beds; S.Location = Loc; S.StakeOffset = FVector(120, 0, 0);
		return S;
	};
	V->AuthoredPlots = {
		MakeSite(TEXT("Home1"), ETownBuilding::House, ETownEra::Village, 4, FVector(0, 0, 0)),
		MakeSite(TEXT("Guild1"), ETownBuilding::Guild, ETownEra::Village, 0, FVector(600, 0, 0)),
		MakeSite(TEXT("Shop1"), ETownBuilding::Shop, ETownEra::Village, 2, FVector(1200, 0, 0)),
		MakeSite(TEXT("Inn1"), ETownBuilding::Inn, ETownEra::Village, 4, FVector(1800, 0, 0)),
		MakeSite(TEXT("Manor1"), ETownBuilding::Manor, ETownEra::LargeTown, 3, FVector(2400, 0, 0)),
		MakeSite(TEXT("Castle1"), ETownBuilding::Castle, ETownEra::Kingdom, 6, FVector(3000, 0, 0)),
	};
	V->BuildingCatalog = V->AuthoredPlots;
	V->Trust = 5;
	V->InitializeConstruction();
	TestEqual(TEXT("Starts in Homestead era"), V->GetSettlementEra(Player), ESettlementEra::Homestead);
	TestEqual(TEXT("Homestead label"), V->GetSettlementEraName(Player), FString(TEXT("Homestead")));

	V->TryBuildPlot(TEXT("Home1"), Player);
	V->Trust = 14;
	TestEqual(TEXT("Advances to Village era"), V->GetSettlementEra(Player), ESettlementEra::Village);

	V->TryBuildPlot(TEXT("Guild1"), Player);
	V->TryBuildPlot(TEXT("Shop1"), Player);
	V->Trust = 32;
	Player->UnlockedSphereNodes = { TEXT("N1"), TEXT("N2") };
	TestEqual(TEXT("Advances to Town era"), V->GetSettlementEra(Player), ESettlementEra::Town);

	V->Trust = 54;
	Player->UnlockedSphereNodes = { TEXT("N1"), TEXT("N2"), TEXT("N3"), TEXT("N4") };
	V->TryBuildPlot(TEXT("Manor1"), Player);
	TestEqual(TEXT("Advances to Barony era"), V->GetSettlementEra(Player), ESettlementEra::Barony);

	V->Trust = 84;
	Player->UnlockedSphereNodes = { TEXT("N1"), TEXT("N2"), TEXT("N3"), TEXT("N4"), TEXT("N5"), TEXT("N6"), TEXT("N7"), TEXT("N8") };
	V->TryBuildPlot(TEXT("Castle1"), Player);
	TestEqual(TEXT("Advances to Kingdom era"), V->GetSettlementEra(Player), ESettlementEra::Kingdom);
	TestTrue(TEXT("Max era progress string notes Kingdom"), V->GetNextEraRequirementText(Player).Contains(TEXT("Kingdom")));

	// 3. Verify Lake Fishing Spot & Persistent MineOreVein Respawn
	ALakeFishingSpot* Spot = W->SpawnActor<ALakeFishingSpot>(FVector(4000, 0, 100), FRotator::ZeroRotator, P);
	TestNotNull(TEXT("FishingSpot spawned"), Spot);
	const int32 FishBefore = Player->Gather->GetCount(TEXT("Fish"));
	TestTrue(TEXT("High gather-level cast 1 catches Fish"), Spot->TryFish(Player));
	TestTrue(TEXT("High gather-level cast 2 catches Fish"), Spot->TryFish(Player));
	TestTrue(TEXT("Player gained Fish"), Player->Gather->GetCount(TEXT("Fish")) >= FishBefore + 2);
	TestEqual(TEXT("Catches remaining decremented by 2"), Spot->CatchesRemaining, Spot->MaxCatchesPerRestock - 2);
	Spot->ReplenishSpot();
	TestEqual(TEXT("ReplenishSpot restores full catches"), Spot->CatchesRemaining, Spot->MaxCatchesPerRestock);

	AMineOreVein* Vein = W->SpawnActor<AMineOreVein>(FVector(4500, 0, 100), FRotator::ZeroRotator, P);
	Vein->OreId = TEXT("Iron"); Vein->RequiredLevel = 1; Vein->RespawnSeconds = 30.0f;
	Player->Gather->PickaxeTier = EAxeTier::Steel; // 1 hit to mine
	TestTrue(TEXT("Persistent world vein mines cleanly"), Vein->TryMine(Player));
	TestTrue(TEXT("Respawning world vein stays alive but hidden"), IsValid(Vein) && !Vein->Mesh->IsVisible());

	// 4. Verify Worker Courier Resource Place Routing (Forest, Lake, Mine) & Harvesting State
	AVillageGolemCitizen* Courier = nullptr;
	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It)
	{
		if (It->GetOwner() == V && It->WorkPlot == TEXT("Guild1")) { Courier = *It; break; }
	}
	if (TestNotNull(TEXT("Hall courier spawned"), Courier))
	{
		FVillageSupplySite ForestSite; ForestSite.Item = TEXT("Wood"); ForestSite.Location = FVector(6000, 0, 0); ForestSite.Stock = 30; ForestSite.SiteTag = TEXT("Whispering Forest");
		FVillageSupplySite LakeSite; LakeSite.Item = TEXT("Fish"); LakeSite.Location = FVector(7000, 0, 0); LakeSite.Stock = 30; LakeSite.SiteTag = TEXT("SkyLake Pier");
		FVillageSupplySite MineSite; MineSite.Item = TEXT("Stone"); MineSite.Location = FVector(8000, 0, 0); MineSite.Stock = 30; MineSite.SiteTag = TEXT("Whisperwood Mine");
		V->SupplySites = { ForestSite, LakeSite, MineSite };

		// Move courier onto LakeSite and advance
		if (FVillageGolemRecord* Rec = V->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R){ return R.Id == Courier->GolemId; }))
		{
			Rec->SupplyIndex = 1; Rec->CargoCount = 0; Rec->Cargo = NAME_None;
		}
		Courier->SetActorLocation(LakeSite.Location);
		V->AdvanceHallCourier(Courier, 1.0f);
		TestTrue(TEXT("Courier enters harvesting state at Lake"), Courier->bHarvesting);
		TestEqual(TEXT("Courier resolves Lake EVillagePlace"), Courier->HarvestPlace, EVillagePlace::Lake);
		TestTrue(TEXT("OfferLine reflects SkyLake fishing"), Courier->OfferLine().ToString().Contains(TEXT("SkyLake")));

		// Finish harvesting Lake -> returning sets bHarvesting false
		V->AdvanceHallCourier(Courier, 3.5f);
		TestFalse(TEXT("Harvesting ends once cargo loaded"), Courier->bHarvesting);

		// Move courier onto MineSite
		if (FVillageGolemRecord* Rec = V->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R){ return R.Id == Courier->GolemId; }))
		{
			Rec->SupplyIndex = 2; Rec->CargoCount = 0; Rec->Cargo = NAME_None;
		}
		Courier->SetActorLocation(MineSite.Location);
		V->AdvanceHallCourier(Courier, 1.0f);
		TestEqual(TEXT("Courier resolves Mine EVillagePlace"), Courier->HarvestPlace, EVillagePlace::Mine);
		TestTrue(TEXT("OfferLine reflects Whisperwood Mine"), Courier->OfferLine().ToString().Contains(TEXT("Mine")));
	}

	// 5. Verify DayBoard direct commission completion & SP reward
	V->TodayMissions.Reset();
	FDayMission WoodTask; WoodTask.Kind = EDayMissionKind::FetchWood; WoodTask.Need = 5; WoodTask.Have = 0;
	V->TodayMissions.Add(WoodTask);
	Player->Gather->AddItem(TEXT("Wood"), 10);
	const int32 SPBefore = Player->SpherePoints;
	TestTrue(TEXT("TryCompleteMissionAtIndex completes FetchWood"), V->TryCompleteMissionAtIndex(0, Player));
	TestEqual(TEXT("Commission grants +1 SP"), Player->SpherePoints, SPBefore + 1);
	TestEqual(TEXT("FetchWood consumed 5 Wood"), Player->Gather->GetCount(TEXT("Wood")), 5);

	V->bUseGolemVillage = false;
	UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
	W->DestroyWorld(false);
	GEngine->DestroyWorldContext(W);
	return true;
}
#endif
