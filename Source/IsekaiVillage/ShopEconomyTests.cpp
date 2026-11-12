// Copyright Epic Games, Inc. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "VillageGolemTypes.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "BlacksmithForge.h"
#include "GolemSparring.h"
#include "SlimeRunicMagic.h"
#include "ShopForgeWidget.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FShopEconomyAndToolPartsTest, "IsekaiVillage.Village.ShopEconomyAndToolParts", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FShopEconomyAndToolPartsTest::RunTest(const FString& Parameters)
{
	const auto IV = UWorld::InitializationValues()
		.AllowAudioPlayback(false)
		.CreatePhysicsScene(true)
		.CreateNavigation(false)
		.CreateAISystem(false)
		.ShouldSimulatePhysics(false)
		.SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
	W->SetGameInstance(NewObject<UGameInstance>(GEngine));
	FURL URL;
	URL.AddOption(TEXT("game=/Script/Engine/GameModeBase"));
	W->SetGameMode(URL);

	FActorSpawnParameters P;
	P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AStaticMeshActor* Floor = W->SpawnActor<AStaticMeshActor>(FVector(0.f, 0.f, -50.f), FRotator::ZeroRotator, P);
	Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")));
	Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
	Floor->SetActorScale3D(FVector(120.f, 120.f, 1.f));

	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(1000.f, -500.f, 99.f), FRotator::ZeroRotator, P);
	if (Player) Player->DispatchBeginPlay();
	ABlacksmithForge* Forge = W->SpawnActor<ABlacksmithForge>(FVector(1000.f, -500.f, 99.f), FRotator::ZeroRotator, P);
	V->bUseAuthoredPlots = true;
	V->bUseGolemVillage = true;
	V->bUseOrganicGolemNeeds = true;
	V->SparringSlimeClass = ASlimeRunicMage::StaticClass();
	V->ConstructionSaveSlot = TEXT("Automation_ShopEconomy_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);

	FTownPlot Home;
	Home.Id = TEXT("Home");
	Home.Kind = ETownBuilding::House;
	Home.bBuilt = true;
	Home.BedBonus = 4;
	Home.BuildingClass = AStaticMeshActor::StaticClass();
	Home.StakeOffset = FVector(0.f, -500.f, 0.f);

	FTownPlot Shop = Home;
	Shop.Id = TEXT("Shop01");
	Shop.Kind = ETownBuilding::Shop;
	Shop.BedBonus = 0;
	Shop.Location = FVector(1000.f, 0.f, 0.f);

	FTownPlot Yard = Shop;
	Yard.Id = TEXT("Yard");
	Yard.Kind = ETownBuilding::Training;
	Yard.Location = FVector(2000.f, 0.f, 0.f);

	FTownPlot Smith = Shop;
	Smith.Id = TEXT("Smith01");
	Smith.Kind = ETownBuilding::Smith;
	Smith.Location = FVector(3000.f, 0.f, 0.f);

	V->AuthoredPlots = {Home, Shop, Yard};
	V->InitializeConstruction();
	V->ReconcileGolemPopulation();
	V->SaveVillageState(Player);

	TestEqual(TEXT("Shop starts with seeded Bread stock"), V->GetShopItemStock(Shop.Id, TEXT("Bread")), 2);
	TestFalse(TEXT("Crystal locked at low trust without Bank/VaultStock"), V->IsShopOfferUnlocked(TEXT("Crystal")));
	TestFalse(TEXT("ToolParts locked before Smith without VaultStock"), V->IsShopOfferUnlocked(TEXT("ToolParts")));

	// Staff the shopkeeper at the shop counter
	AVillageGolemCitizen* Keeper = nullptr;
	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It)
	{
		if (It->GetOwner() == V && It->WorkPlot == Shop.Id)
		{
			Keeper = *It;
			break;
		}
	}
	if (!TestNotNull(TEXT("Shopkeeper golem spawned"), Keeper))
	{
		V->bUseGolemVillage = false;
		W->DestroyWorld(false);
		GEngine->DestroyWorldContext(W);
		return false;
	}
	V->WindowIndex = 1;
	Keeper->SetActorLocation(Shop.Location + Shop.StakeOffset + Shop.StakeOffset.GetSafeNormal2D() * 150.f + FVector(0.f, 0.f, 99.f));
	Keeper->SetGoal(EVillagePlace::Shop, Shop.Location + Shop.StakeOffset + Shop.StakeOffset.GetSafeNormal2D() * 150.f);

	// 1. Multi-item buy/sell + unlocking + Sphere bonuses
	Player->Gather->AddItem(TEXT("Coin"), 50);
	Player->Gather->AddItem(TEXT("ToolParts"), 6);
	Player->Gather->AddItem(TEXT("Wood"), 5);
	TestTrue(TEXT("Buy Bread from shop"), V->TradeShopItem(Shop.Id, TEXT("Bread"), true, Player));
	TestEqual(TEXT("Player gained 1 Bread"), Player->Gather->GetCount(TEXT("Bread")), 1);
	TestEqual(TEXT("Shop Bread stock decremented"), V->GetShopItemStock(Shop.Id, TEXT("Bread")), 1);
	TestEqual(TEXT("Bread buy costs 5 Coins"), Player->Gather->GetCount(TEXT("Coin")), 45);

	// Unlock ToolParts by adding built Smith
	V->AuthoredPlots.Add(Smith);
	V->InitializeConstruction();
	V->ReconcileGolemPopulation();
	V->SaveVillageState(Player);
	TestTrue(TEXT("ToolParts unlocks with Smith"), V->IsShopOfferUnlocked(TEXT("ToolParts")));
	TestTrue(TEXT("Sell ToolParts at shop"), V->TradeShopItem(Shop.Id, TEXT("ToolParts"), false, Player));
	TestEqual(TEXT("ToolParts sold pays 6 Coins"), Player->Gather->GetCount(TEXT("Coin")), 51);
	TestEqual(TEXT("Shop ToolParts stock increased"), V->GetShopItemStock(Shop.Id, TEXT("ToolParts")), 2);

	// Test ShopHaggle + Gald% scaling across multiple items
	Player->UnlockedSphereNodes.Add(TEXT("Eco_Haggle"));
	Player->UnlockedSphereNodes.Add(TEXT("Eco_Gald1"));
	Player->RefreshSphereGridBonuses();
	TestEqual(TEXT("Haggle drops Bread buy from 5 to 4"), V->GetShopBuyPrice(TEXT("Bread"), Player), 4);
	TestTrue(TEXT("Buy Bread with ShopHaggle"), V->TradeShopItem(Shop.Id, TEXT("Bread"), true, Player));
	TestEqual(TEXT("Paid discounted 4 Coins"), Player->Gather->GetCount(TEXT("Coin")), 47);

	// Save & Reload preserves Shop Stock map
	const int32 SavedBreadStock = V->GetShopItemStock(Shop.Id, TEXT("Bread"));
	const int32 SavedPartsStock = V->GetShopItemStock(Shop.Id, TEXT("ToolParts"));
	TestTrue(TEXT("Save shop state"), V->SaveVillageState(Player));
	V->GolemShops[0].Stock.Reset();
	V->ReloadVillageState(Player);
	TestEqual(TEXT("Reload preserves Bread shop stock"), V->GetShopItemStock(Shop.Id, TEXT("Bread")), SavedBreadStock);
	TestEqual(TEXT("Reload preserves ToolParts shop stock"), V->GetShopItemStock(Shop.Id, TEXT("ToolParts")), SavedPartsStock);

	// New day restock with VaultStock (+2 bonus)
	Player->UnlockedSphereNodes.Add(TEXT("Eco_BulkVault"));
	Player->RefreshSphereGridBonuses();
	V->SaveVillageState(Player);
	V->WindowIndex = 7;
	V->Tick(V->WindowSeconds + 0.1f); // rolls to WindowIndex 0, DayIndex 2 -> restocks shops
	TestTrue(TEXT("Daily rollover increments DayIndex to 2"), V->DayIndex == 2);
	TestTrue(TEXT("Iron unlocks on Day 2"), V->IsShopOfferUnlocked(TEXT("Iron")));
	TestEqual(TEXT("Bread restocks to DailyTarget 4 + VaultStock 2 = 6"), V->GetShopItemStock(Shop.Id, TEXT("Bread")), 6);

	// 2. ToolParts Sink A: Wall reinforcement + RepairWall slip
	V->WallIntegrity = 20;
	FDayMission RepairSlip;
	RepairSlip.Kind = EDayMissionKind::RepairWall;
	RepairSlip.Need = 30;
	V->TodayMissions = {RepairSlip};
	const int32 SpBefore = Player->SpherePoints;
	TestTrue(TEXT("Reinforce wall with 1 ToolParts + 2 Wood"), V->ReinforceWallWithToolParts(Player));
	TestEqual(TEXT("Wall boosted +50 to 70"), V->WallIntegrity, 70);
	TestEqual(TEXT("RepairWall slip rewarded +1 SP"), Player->SpherePoints, SpBefore + 1);

	// 3. ToolParts Sink B: Blacksmith Tempering & Combat Scaling
	FHiredAdventurer Adv;
	Adv.GolemId = FGuid::NewGuid();
	Adv.AdventurerID = FName(*(TEXT("Golem_") + Adv.GolemId.ToString(EGuidFormats::Digits)));
	Adv.Name = FText::FromString(TEXT("Tempered Guard"));
	Adv.ClassId = TEXT("Tank");
	Adv.Drives.Interest = TEXT("Guard");
	Adv.bHasChosenBody = true;
	Adv.bInActiveParty = true;
	Player->PartyReserve->Reserve = {Adv};
	V->ReconcileGolemPopulation();

	TestTrue(TEXT("Temper +1 with 2 ToolParts"), Forge->TemperWithToolParts(Player, Adv.AdventurerID));
	TestEqual(TEXT("Adventurer TemperLevel reaches 1"), Player->PartyReserve->Reserve[0].TemperLevel, 1);

	Player->UnlockedSphereNodes.Add(TEXT("Craft_ForgeDisc"));
	Player->RefreshSphereGridBonuses();
	TestTrue(TEXT("Temper +2 costs 1 ToolParts with ForgeDiscount"), Forge->TemperWithToolParts(Player, Adv.AdventurerID));
	TestEqual(TEXT("Adventurer TemperLevel reaches max 2"), Player->PartyReserve->Reserve[0].TemperLevel, 2);
	TestFalse(TEXT("Cannot temper beyond +2"), Forge->TemperWithToolParts(Player, Adv.AdventurerID));

	// Verify TemperLevel persists across Save/Reload
	V->SaveVillageState(Player);
	Player->PartyReserve->Reserve[0].TemperLevel = 0;
	V->ReloadVillageState(Player);
	TestEqual(TEXT("TemperLevel persists across reload"), Player->PartyReserve->Reserve[0].TemperLevel, 2);

	// Verify TemperLevel boosts combat HP (+20), Attack (+8), and Damage Mitigation (-10%) in AGolemSparring
	Player->SetActorLocation(Yard.Location + Yard.StakeOffset + FVector(0.f, 0.f, 99.f));
	AGolemSparring* B = W->SpawnActor<AGolemSparring>(Yard.Location + Yard.StakeOffset + FVector(0.f, 0.f, 99.f), FRotator::ZeroRotator, P);
	TestTrue(TEXT("Start sparring with +2 tempered adventurer"), B->BeginSparring(V, Player));
	if (TestTrue(TEXT("Member spawned in sparring"), B->Members.Num() == 1))
	{
		B->Members[0].Actor->SetActorLocation(B->Members[0].Formation + FVector(0.f, 0.f, 99.f));
		B->Tick(0.1f);
		TestEqual(TEXT("Tempered +2 adds +20 HP to 120"), B->Members[0].MaxHealth, 120.f);
		TestEqual(TEXT("Assembly enters AwaitCommand"), B->Phase, FName(TEXT("AwaitCommand")));
		const float BeforeHit = B->Enemy->Health;
		TestTrue(TEXT("Execute Strike"), B->ExecuteAction(TEXT("Strike")));
		TestEqual(TEXT("Tempered +2 Strike deals 28 damage (20 base + 8)"), BeforeHit - B->Enemy->Health, 28.f);
		const float Taken = B->ReceiveDamage(B->Members[0].Actor, 20.f, B->Enemy);
		TestEqual(TEXT("Tempered +2 reduces 20 damage by 10% to 18"), Taken, 18.f);
	}
	B->CancelSparring();
	B->CancelSparring();

	V->bUseGolemVillage = false;
	UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
	W->DestroyWorld(false);
	GEngine->DestroyWorldContext(W);
	return true;
}
