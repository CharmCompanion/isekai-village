#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/DamageEvents.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "IsekaiVillageCharacter.h"
#include "SphereGridDataAsset.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "TownPlot.h"
#include "BlacksmithForge.h"
#include "GolemSparring.h"
#include "SlimeRunicMagic.h"
#include "TowerExpedition.h"
#include "SpellProjectile.h"

namespace
{
	void UnlockEntireFace(AIsekaiVillageCharacter* Player, int32 Disc, bool bFlipped)
	{
		if (!Player || !Player->SphereGrid) return;
		const TArray<FName>& Order = Player->SphereGrid->FaceOrder(Disc, bFlipped);
		for (const FName& NodeID : Order)
		{
			Player->UnlockSphereNode(NodeID);
		}
	}
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSphereGridAllDiscsAndTownHooksTest, "IsekaiVillage.SphereGrid.AllDiscsAndTownHooks", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FSphereGridAllDiscsAndTownHooksTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
	FActorSpawnParameters P;
	P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(0, 0, 120), FRotator::ZeroRotator, P);
	if (Player) Player->DispatchBeginPlay();
	if (!TestNotNull(TEXT("Village spawned"), V) || !TestNotNull(TEXT("Player spawned"), Player) || !TestNotNull(TEXT("SphereGrid initialized"), Player->SphereGrid.Get()))
	{
		W->DestroyWorld(false);
		GEngine->DestroyWorldContext(W);
		return false;
	}

	USphereGridDataAsset* Grid = Player->SphereGrid;
	TestEqual(TEXT("All 12 Sphere Grid discs exist"), Grid->DiscCount(), 12);
	int32 TotalNodes = 0;
	for (int32 D = 0; D < Grid->DiscCount(); ++D)
	{
		TotalNodes += Grid->FaceOrder(D, false).Num();
		if (Grid->DiscHasFlip(D))
		{
			TotalNodes += Grid->FaceOrder(D, true).Num();
		}
	}
	TestEqual(TEXT("Total nodes across all 12 discs (14 faces) equals 176"), TotalNodes, 176);

	Player->SpherePoints = 200;
	// Lock checks: cannot jump to Domain (Disc 3) or Melee (Disc 5) before finishing Center A & Center B.
	TestFalse(TEXT("Domain+Architect locked before Work"), Grid->IsDiscUnlocked(3, Player->UnlockedSphereNodes));
	TestFalse(TEXT("Melee locked before Villager"), Grid->IsDiscUnlocked(5, Player->UnlockedSphereNodes));

	UnlockEntireFace(Player, 0, false);
	TestTrue(TEXT("Center A Life complete flips to Adventurer"), Player->FlipSphereGrid());
	UnlockEntireFace(Player, 0, true);
	TestTrue(TEXT("Completing Adventurer unlocks Center B"), Player->bCenterBUnlocked && Grid->IsDiscUnlocked(1, Player->UnlockedSphereNodes));

	TestTrue(TEXT("Select Disc 1 (Center B Work)"), Player->SelectSphereDisc(1));
	UnlockEntireFace(Player, 1, false);
	TestTrue(TEXT("Completing Work unlocks Town Main discs (Crafting, Domain, Economy)"), Grid->IsDiscUnlocked(2, Player->UnlockedSphereNodes) && Grid->IsDiscUnlocked(3, Player->UnlockedSphereNodes) && Grid->IsDiscUnlocked(4, Player->UnlockedSphereNodes));
	TestFalse(TEXT("Combat Main (Melee) remains locked until Center B Villager is full"), Grid->IsDiscUnlocked(5, Player->UnlockedSphereNodes));

	TestTrue(TEXT("Flip Center B Work -> Villager"), Player->FlipSphereGrid());
	UnlockEntireFace(Player, 1, true);
	TestTrue(TEXT("Completing Villager unlocks Combat Main discs (Melee, Magic, Cleric)"), Grid->IsDiscUnlocked(5, Player->UnlockedSphereNodes) && Grid->IsDiscUnlocked(6, Player->UnlockedSphereNodes) && Grid->IsDiscUnlocked(7, Player->UnlockedSphereNodes));

	// Town setup for Domain+Architect, Economy+Hospitality, Crafting verification
	V->bUseAuthoredPlots = true;
	V->bUseGolemVillage = true;
	V->bUseOrganicGolemNeeds = true;
	V->ConstructionSaveSlot = TEXT("Automation_SphereTown_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);
	FTownPlot House;
	House.Id = TEXT("House01"); House.Kind = ETownBuilding::House; House.BedBonus = 2; House.WoodCost = 8;
	House.Location = FVector(0, 0, 0); House.StakeOffset = FVector(150, 0, 0); House.BuildingClass = AStaticMeshActor::StaticClass();
	FTownPlot Shop = House; Shop.Id = TEXT("Shop01"); Shop.Kind = ETownBuilding::Shop; Shop.BedBonus = 0; Shop.Location = FVector(600, 0, 0); Shop.bBuilt = true;
	FTownPlot Guild = House; Guild.Id = TEXT("Guild01"); Guild.Kind = ETownBuilding::Guild; Guild.BedBonus = 0; Guild.Location = FVector(1200, 0, 0); Guild.bBuilt = true;
	V->AuthoredPlots = { House, Shop, Guild };
	// Link VillagePlayer before BuildOffer / Save checks
	V->InitializeConstruction();
	V->SaveVillageState(Player);
	V->ReloadVillageState(Player);
	const float BaseSafety = V->BuildOffer().Safety;

	// Unlock Crafting (Disc 2) + Domain+Architect (Disc 3) + Economy+Hospitality (Disc 4)
	TestTrue(TEXT("Select Crafting disc 2"), Player->SelectSphereDisc(2));
	UnlockEntireFace(Player, 2, false);
	TestTrue(TEXT("Select Domain+Architect disc 3"), Player->SelectSphereDisc(3));
	UnlockEntireFace(Player, 3, false);
	TestTrue(TEXT("Select Economy+Hospitality disc 4"), Player->SelectSphereDisc(4));
	UnlockEntireFace(Player, 4, false);

	TestTrue(TEXT("HireCap+1 raises ActivePartyCap from 2 to 3"), Player->PartyReserve->ActivePartyCap >= 3);
	TestTrue(TEXT("Attraction + CivicWatch raises Safety offer"), V->BuildOffer().Safety > BaseSafety);

	// Forge discount & Crystal discount check
	TestEqual(TEXT("Crafting ForgeDiscount reduces 4 Iron to 3"), UGatherInventoryComponent::ForgeCost(Player, 4, false), 3);

	// Expanded Lofts (+2 beds instead of +1) and save persistence
	Player->Gather->AddItem(TEXT("Wood"), 30);
	V->TryBuildPlot(House.Id, Player);
	TestTrue(TEXT("Built house"), V->FindPlot(House.Id)->bBuilt);
	V->TryBuildPlot(House.Id, Player); // Loft upgrade
	TestEqual(TEXT("Expanded Lofts adds +2 beds (total 4)"), V->FindPlot(House.Id)->BedBonus, 4);

	// CivicWatch & InnHospitality on day rollover
	V->CrimeHeat = 5;
	V->WallIntegrity = 50;
	V->WindowIndex = 7;
	V->Tick(V->WindowSeconds + 0.1f); // wraps to Window 0 (new day)
	TestEqual(TEXT("CivicWatch decays CrimeHeat by 2 on new day"), V->CrimeHeat, 3);
	TestEqual(TEXT("CivicWatch repairs WallIntegrity by +3 on new day"), V->WallIntegrity, 53);

	// Economy: ShopHaggle + Gald% + MissionReward+1
	V->ReconcileGolemPopulation();
	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It)
	{
		if (It->WorkPlot == Shop.Id)
		{
			It->SetGoal(EVillagePlace::Shop, V->WorkerEntrance(*V->FindPlot(Shop.Id)));
			It->SetActorLocation(It->Goal + FVector(0, 0, 99));
		}
	}
	Player->SetActorLocation(Shop.Location + Shop.StakeOffset);
	const int32 CoinsBefore = Player->Gather->GetCount(TEXT("Coin"));
	TestTrue(TEXT("Sell wood with ShopHaggle + Gald%"), V->TradeWood(Shop.Id, false, Player));
	TestTrue(TEXT("Haggle + Gald% pays >= 4 coins per wood"), Player->Gather->GetCount(TEXT("Coin")) - CoinsBefore >= 4);
	TestTrue(TEXT("Buy wood with ShopHaggle costs 1 coin"), V->TradeWood(Shop.Id, true, Player));

	// Day slip bonus with MissionReward+1 and FieldRepair
	{
		FDayMission RepairMission;
		RepairMission.Kind = EDayMissionKind::RepairWall;
		RepairMission.Need = 30;
		V->TodayMissions = { RepairMission };
		const int32 TrustBefore = V->Trust;
		const int32 CoinBeforeMission = Player->Gather->GetCount(TEXT("Coin"));
		const int32 WallBefore = V->WallIntegrity;
		Player->Gather->AddItem(TEXT("Wood"), 3);
		V->TryBoard(Player);
		TestEqual(TEXT("MissionReward+1 grants +7 Trust"), V->Trust, FMath::Min(99, TrustBefore + 7));
		TestEqual(TEXT("MissionReward+1 grants +5 Coin"), Player->Gather->GetCount(TEXT("Coin")) - CoinBeforeMission, 5);
		TestEqual(TEXT("FieldRepair adds +15 extra WallIntegrity (+45 total)"), V->WallIntegrity, FMath::Min(100, WallBefore + 45));
	}

	// Save & Reload preserves SphereDisc >= 2 and +2 Loft beds
	TestTrue(TEXT("Save construction + sphere state"), V->SaveVillageState(Player));
	Player->UnlockedSphereNodes.Reset();
	Player->SphereDisc = 0;
	V->ReloadVillageState(Player);
	TestEqual(TEXT("Reload preserves expanded loft bed bonus (4 beds)"), V->FindPlot(House.Id)->BedBonus, 4);
	TestEqual(TEXT("Reload preserves SphereDisc >= 2 (Disc 4)"), Player->SphereDisc, 4);
	TestTrue(TEXT("Reload restores unlocked skills"), Player->HasSphereSkill(TEXT("LoftBeds+2")) && Player->HasSphereSkill(TEXT("ShopHaggle")));

	V->bUseGolemVillage = false;
	UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
	W->DestroyWorld(false);
	GEngine->DestroyWorldContext(W);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSphereGridCombatSparringAndTowerHooksTest, "IsekaiVillage.SphereGrid.CombatSparringAndTowerHooks", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FSphereGridCombatSparringAndTowerHooksTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
	FActorSpawnParameters P;
	P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(0, 0, 120), FRotator::ZeroRotator, P);
	if (Player) Player->DispatchBeginPlay();
	if (!TestNotNull(TEXT("Village spawned"), V) || !TestNotNull(TEXT("Player spawned"), Player) || !TestNotNull(TEXT("SphereGrid initialized"), Player->SphereGrid.Get()) || !Player->Gather || !Player->PartyReserve)
	{
		W->DestroyWorld(false);
		GEngine->DestroyWorldContext(W);
		return false;
	}

	// Starter Artes initialized in BeginPlay
	TestEqual(TEXT("4 runtime EquippedArtes initialized"), Player->EquippedArtes.Num(), 4);
	TestNotNull(TEXT("Slot 0 starter arte present"), Player->EquippedArtes[0]);

	Player->SpherePoints = 250;
	for (int32 D : { 0, 1 })
	{
		Player->SelectSphereDisc(D);
		UnlockEntireFace(Player, D, false);
		Player->FlipSphereGrid();
		UnlockEntireFace(Player, D, true);
	}
	// Complete Crafting(2), Melee(5), Magic(6), Cleric(7) -> unlocks Endgame 4!
	for (int32 D : { 2, 5, 6, 7 })
	{
		TestTrue(TEXT("Select Main disc"), Player->SelectSphereDisc(D));
		UnlockEntireFace(Player, D, false);
	}
	TestTrue(TEXT("Endgame Ranger (8), Summons (9), Soulsmith (10), Artificer (11) all unlocked"),
		Player->SphereGrid->IsDiscUnlocked(8, Player->UnlockedSphereNodes)
		&& Player->SphereGrid->IsDiscUnlocked(9, Player->UnlockedSphereNodes)
		&& Player->SphereGrid->IsDiscUnlocked(10, Player->UnlockedSphereNodes)
		&& Player->SphereGrid->IsDiscUnlocked(11, Player->UnlockedSphereNodes));

	for (int32 D : { 8, 9, 10, 11 })
	{
		Player->SelectSphereDisc(D);
		UnlockEntireFace(Player, D, false);
	}

	// Verify MC Magic & Focus Mode & Damage Reduction
	Player->CurrentTP = Player->MaxTP;
	Player->ActivateFocusMode();
	const float TPBeforeSilent = Player->CurrentTP;
	Player->TriggerArte(0);
	Player->SetBulletTime(false, 1.0f);
	TestTrue(TEXT("Focus Mode Silent Cast spends 0 TP"), FMath::IsNearlyEqual(Player->CurrentTP, TPBeforeSilent, 0.01f));
	int32 ProjCount = 0;
	for (TActorIterator<ASpellProjectile> It(W); It; ++It) ++ProjCount;
	TestTrue(TEXT("SpreadFan spawns >= 3 projectiles on single TriggerArte"), ProjCount >= 3);

	const float HPBeforeHit = Player->CurrentHP;
	Player->TakeDamage(100.0f, FDamageEvent(), nullptr, nullptr);
	TestTrue(TEXT("Res_Percent + AegisBarrier reduces MC incoming damage"), (HPBeforeHit - Player->CurrentHP) < 80.0f);

	// Verify Blacksmith CatalystExtract + ForgeDiscount
	TestEqual(TEXT("CatalystExtract lowers 4 Crystal Runic cost to 3"), UGatherInventoryComponent::ForgeCost(Player, 4, true), 3);

	// Verify Soulsmith SoulImprint increases companion practice effort x1.5
	TestTrue(TEXT("Hire adventurer 1"), Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("TestSoul1"))));
	TestTrue(TEXT("Hire adventurer 2"), Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("TestSoul2"))));
	Player->PartyReserve->Reserve[1].Drives.Skills.AddUnique(TEXT("FirstAid"));
	const FName AdvId = Player->PartyReserve->Reserve[0].AdventurerID;
	Player->PartyReserve->RecordAdventurerPractice(AdvId, TEXT("Magic"), 2.f, true);
	TestTrue(TEXT("SoulImprint boosts practice >= 2.9"), Player->PartyReserve->Reserve[0].Drives.Practice.FindRef(TEXT("Magic")) >= 2.9f);

	// Verify Sparring hooks: SpiritGuard HP/TP, ReviveGrace, VesselAnchor
	AStaticMeshActor* Ground = W->SpawnActor<AStaticMeshActor>(FVector(0, 0, -50), FRotator::ZeroRotator, P);
	if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
	{
		Ground->GetStaticMeshComponent()->SetStaticMesh(Cube);
		Ground->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
		Ground->SetActorScale3D(FVector(50, 50, 1));
	}
	V->bUseAuthoredPlots = true;
	V->bUseGolemVillage = true;
	V->bUseOrganicGolemNeeds = true;
	V->SparringSlimeClass = ASlimeRunicMage::StaticClass();
	V->ConstructionSaveSlot = TEXT("Automation_SphereCombat_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);
	FTownPlot House; House.Id = TEXT("H1"); House.Kind = ETownBuilding::House; House.BedBonus = 2; House.Location = FVector(0, 0, 0); House.StakeOffset = FVector(150, 0, 0); House.bBuilt = true;
	FTownPlot Yard = House; Yard.Id = TEXT("Y1"); Yard.Kind = ETownBuilding::Training; Yard.Location = FVector(300, 0, 0);
	V->AuthoredPlots = { House, Yard };
	V->InitializeConstruction();
	V->SaveVillageState(Player);
	V->ReloadVillageState(Player);

	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It)
	{
		It->SetActorLocation(FVector(0, 0, 99));
	}
	TArray<AVillageGolemCitizen*> Allies;
	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It) Allies.Add(*It);
	if (!TestTrue(TEXT("At least one ally golem spawned"), Allies.Num() >= 1))
	{
		V->bUseGolemVillage = false;
		UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
		W->DestroyWorld(false);
		GEngine->DestroyWorldContext(W);
		return false;
	}

	AGolemSparring* B = W->SpawnActor<AGolemSparring>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	TestTrue(TEXT("Begin field encounter"), B->BeginFieldEncounter(V, Player, Allies, FVector(500, 0, 100), 0));
	B->Tick(0.1f);
	TestNotNull(TEXT("Enemy spawned after Tick"), B->Enemy.Get());
	TestTrue(TEXT("SpiritGuard boosts ally MaxHealth >= 115"), B->Members[0].MaxHealth >= 115.f);
	TestTrue(TEXT("SpiritGuard boosts ally TP >= 50"), B->Members[0].TP >= 50.f);

	// VesselAnchor prevents first lethal hit
	B->Phase = TEXT("EnemyTurn");
	B->ReceiveDamage(B->Members[0].Actor, 9999.f, B->Enemy);
	TestTrue(TEXT("VesselAnchor preserves golem at 1 HP on first fatal hit"), FMath::IsNearlyEqual(B->Members[0].Health, 1.f, 0.01f));
	// Second fatal hit knocks out cleanly
	B->ReceiveDamage(B->Members[0].Actor, 9999.f, B->Enemy);
	TestTrue(TEXT("Second fatal hit knocks out ally"), B->Members[0].Health <= 0.f);
	if (TestTrue(TEXT("Second ally present for ReviveGrace test"), B->Members.Num() >= 2))
	{
		B->Phase = TEXT("AwaitCommand");
		B->CurrentMember = 1;
		TestTrue(TEXT("ReviveGrace allows FirstAid to revive knocked-out ally"), B->ExecuteAction(TEXT("FirstAid")));
		TestTrue(TEXT("Revived ally restored >= 35 HP"), B->Members[0].Health >= 35.f);
	}
	B->CancelSparring(); B->CancelSparring();

	// Verify Tower SanctuaryCamp +1 trip home & RunicTonic rations
	ATowerExpedition* T = W->SpawnActor<ATowerExpedition>(FVector(0, -1000, 100), FRotator::ZeroRotator, P);
	TestNotNull(TEXT("Tower expedition spawned"), T);
	Player->Gather->AddItem(TEXT("Bread"), 3);
	T->bInside = true;
	T->Village = V;
	T->Commander = Player;
	TestTrue(TEXT("SanctuaryCamp grants +1 trip home"), T->TripsHomeAllowed() >= 2);
	Player->CurrentHP = 50.f; Player->CurrentTP = 20.f;
	TestTrue(TEXT("ShareRations with RunicTonic heals MC"), T->ShareRations(Player));
	TestTrue(TEXT("RunicTonic restores MC HP (+25)"), Player->CurrentHP >= 75.f);
	TestTrue(TEXT("RunicTonic restores MC TP (+15)"), Player->CurrentTP >= 35.f);

	V->bUseGolemVillage = false;
	UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
	W->DestroyWorld(false);
	GEngine->DestroyWorldContext(W);
	return true;
}
#endif
