// Copyright Epic Games, Inc. All Rights Reserved.

#include "Misc/AutomationTest.h"
#include "VillageRuntime.h"
#include "VillageCitizen.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "GolemSparring.h"
#include "TowerExpedition.h"
#include "SlimeRunicMagic.h"
#include "TownServiceWidget.h"
#include "Engine/World.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTownServicesAndGuildRankTest, "IsekaiVillage.Village.TownServicesAndGuildRank", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTownServicesAndGuildRankTest::RunTest(const FString& Parameters)
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
	Floor->SetActorScale3D(FVector(160.f, 160.f, 1.f));

	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(0.f, -500.f, 99.f), FRotator::ZeroRotator, P);
	if (Player) Player->DispatchBeginPlay();
	ATowerExpedition* Tower = W->SpawnActor<ATowerExpedition>(FVector(0.f, -500.f, 99.f), FRotator::ZeroRotator, P);

	V->bUseAuthoredPlots = true;
	V->bUseGolemVillage = true;
	V->bUseOrganicGolemNeeds = true;
	V->SparringSlimeClass = ASlimeRunicMage::StaticClass();
	V->ConstructionSaveSlot = TEXT("Automation_TownServices_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);

	auto MakePlot = [](FName Id, ETownBuilding Kind, float X, int32 Beds = 0)
	{
		FTownPlot Plot;
		Plot.Id = Id;
		Plot.Kind = Kind;
		Plot.bBuilt = true;
		Plot.BedBonus = Beds;
		Plot.Location = FVector(X, 0.f, 0.f);
		Plot.StakeOffset = FVector(0.f, -500.f, 0.f);
		Plot.BuildingClass = AStaticMeshActor::StaticClass();
		return Plot;
	};

	V->AuthoredPlots = {
		MakePlot(TEXT("Home"), ETownBuilding::House, 0.f, 4),
		MakePlot(TEXT("Guild"), ETownBuilding::Guild, 1000.f),
		MakePlot(TEXT("Inn"), ETownBuilding::Inn, 2000.f, 4),
		MakePlot(TEXT("Chapel"), ETownBuilding::Chapel, 3000.f),
		MakePlot(TEXT("Bank"), ETownBuilding::Bank, 4000.f),
		MakePlot(TEXT("Training"), ETownBuilding::Training, 5000.f),
		MakePlot(TEXT("Bath"), ETownBuilding::Bath, 6000.f),
		MakePlot(TEXT("Bell"), ETownBuilding::Bell, 7000.f),
		MakePlot(TEXT("Academy"), ETownBuilding::Academy, 8000.f),
		MakePlot(TEXT("Manor"), ETownBuilding::Manor, 9000.f),
		MakePlot(TEXT("Castle"), ETownBuilding::Castle, 10000.f)
	};
	V->InitializeConstruction();

	// Recruit 1 Tank adventurer
	FHiredAdventurer Adv;
	Adv.GolemId = FGuid::NewGuid();
	Adv.AdventurerID = FName(*(TEXT("Golem_") + Adv.GolemId.ToString(EGuidFormats::Digits)));
	Adv.Name = FText::FromString(TEXT("Aria Paladin"));
	Adv.ClassId = TEXT("Tank");
	Adv.Drives.Interest = TEXT("Guard");
	Adv.bHasChosenBody = true;
	Adv.bInActiveParty = true;
	Player->PartyReserve->Reserve = {Adv};
	V->ReconcileGolemPopulation();
	V->SaveVillageState(Player);

	// 1. Bank deposit + Manor TradeCharter + Inn Rest daily compounding
	Player->Gather->AddItem(TEXT("Coin"), 120);
	Player->Gather->AddItem(TEXT("Bread"), 5);
	Player->Gather->AddItem(TEXT("Iron"), 5);
	Player->Gather->AddItem(TEXT("Crystal"), 12);

	TestTrue(TEXT("Bank deposit 10 Coin x2 -> 20 in vault"),
		V->ExecuteServiceAction(ETownBuilding::Bank, TEXT("Deposit10"), Player)
		&& V->ExecuteServiceAction(ETownBuilding::Bank, TEXT("Deposit10"), Player));
	TestEqual(TEXT("BankVaultCoins is 20"), V->BankVaultCoins, 20);
	TestTrue(TEXT("Manor enacts TradeCharter"), V->ExecuteServiceAction(ETownBuilding::Manor, TEXT("EdictTrade"), Player));
	TestEqual(TEXT("ActiveRoyalEdict is TradeCharter"), V->ActiveRoyalEdict, FName(TEXT("TradeCharter")));

	// Drop MC HP/TP and golem fatigue to test Inn Rest recovery
	Player->CurrentHP = 30.f;
	Player->CurrentTP = 10.f;
	Player->PartyReserve->Reserve[0].Drives.Fatigue = 80.f;
	TestTrue(TEXT("Inn Rest advances to Day 2"), V->ExecuteServiceAction(ETownBuilding::Inn, TEXT("Rest"), Player));
	TestEqual(TEXT("Inn Rest increments DayIndex"), V->DayIndex, 2);
	TestEqual(TEXT("Inn Rest restores full HP"), Player->CurrentHP, Player->MaxHP);
	TestEqual(TEXT("Inn Rest restores full TP"), Player->CurrentTP, Player->MaxTP);
	TestEqual(TEXT("Inn Rest clears adventurer Fatigue"), Player->PartyReserve->Reserve[0].Drives.Fatigue, 0.f);
	// Bank Vault after TradeCharter day 1 rollover: 20 + Round(20*0.125=3) + Round(8*1.25=10) = 33
	TestEqual(TEXT("Bank Vault grew with interest & civic tax"), V->BankVaultCoins, 33);

	// 2. BuildDrive Edict cuts building Wood cost by extra 15%
	TestTrue(TEXT("Manor enacts BuildDrive"), V->ExecuteServiceAction(ETownBuilding::Manor, TEXT("EdictBuild"), Player));
	FTownPlot DiscountSample = MakePlot(TEXT("Extra"), ETownBuilding::House, 11000.f);
	DiscountSample.WoodCost = 20;
	TestEqual(TEXT("BuildDrive cuts 20 Wood to 17"), DiscountSample.WoodPrice(V->EffectiveBuildDiscount(Player)), 17);

	// 3. Manor GuildCampaign Edict boosts Training GroupDrill by 1.5x (25 -> 37.5)
	TestTrue(TEXT("Manor enacts GuildCampaign"), V->ExecuteServiceAction(ETownBuilding::Manor, TEXT("EdictGuild"), Player));
	const float PracticeBefore = Player->PartyReserve->Reserve[0].Drives.Practice.FindRef(TEXT("Guard"));
	TestTrue(TEXT("Training GroupDrill runs"), V->ExecuteServiceAction(ETownBuilding::Training, TEXT("GroupDrill"), Player));
	const float PracticeAfter = Player->PartyReserve->Reserve[0].Drives.Practice.FindRef(TEXT("Guard"));
	TestTrue(TEXT("GuildCampaign GroupDrill awards >= 30 Practice XP"), (PracticeAfter - PracticeBefore) >= 30.f);

	// 4. Bathhouse Soak (once/day guard)
	TestTrue(TEXT("Bathhouse Soak succeeds first time"), V->ExecuteServiceAction(ETownBuilding::Bath, TEXT("Soak"), Player));
	TestFalse(TEXT("Bathhouse Soak blocks repeat same day"), V->ExecuteServiceAction(ETownBuilding::Bath, TEXT("Soak"), Player));

	// 5. Civic Bell Ring + Trust boost (once/day guard)
	const int32 TrustBeforeBell = V->Trust;
	TestTrue(TEXT("Civic Bell rings once on Day 2"), V->ExecuteServiceAction(ETownBuilding::Bell, TEXT("Ring"), Player));
	TestEqual(TEXT("Bell boosts Trust by +1"), V->Trust, TrustBeforeBell + 1);
	TestFalse(TEXT("Bell cannot ring twice same day"), V->ExecuteServiceAction(ETownBuilding::Bell, TEXT("Ring"), Player));

	// 6. Academy Research Tiers 1 -> 2 -> 3 (Wizardbane Seal)
	TestTrue(TEXT("Academy Tier 1 succeeds"), V->ExecuteServiceAction(ETownBuilding::Academy, TEXT("ResearchNext"), Player));
	TestTrue(TEXT("Academy Tier 2 succeeds"), V->ExecuteServiceAction(ETownBuilding::Academy, TEXT("ResearchNext"), Player));
	TestTrue(TEXT("Academy Tier 3 succeeds"), V->ExecuteServiceAction(ETownBuilding::Academy, TEXT("ResearchNext"), Player));
	TestEqual(TEXT("Academy Research Level reaches 3"), V->AcademyResearchLevel, 3);
	TestFalse(TEXT("Academy caps at Tier 3"), V->ExecuteServiceAction(ETownBuilding::Academy, TEXT("ResearchNext"), Player));

	// 7. Chapel Blessing (Valor) + Castle Royal Audience + Guild Rank S progression
	TestTrue(TEXT("Chapel grants Valor blessing"), V->ExecuteServiceAction(ETownBuilding::Chapel, TEXT("BlessValor"), Player));
	V->Trust = 88;
	V->TowerFloor.HighestFloor = 65;
	TestTrue(TEXT("Castle holds Royal Audience"), V->ExecuteServiceAction(ETownBuilding::Castle, TEXT("RoyalAudience"), Player));
	TestEqual(TEXT("High Town + Academy T3 + Floor 65 promotes to Rank S (4)"), V->TownGuildRank, 4);
	TestEqual(TEXT("Rank S Name is S"), V->GetGuildRankName(), FString(TEXT("S")));
	Tower->Commander = Player;
	TestEqual(TEXT("TowerExpedition sees Rank S trips home (4)"), Tower->TripsHomeAllowed(), 4);

	// 8. Verify Save / Reload restores all T2 town services
	V->SaveVillageState(Player);
	const int32 SavedVault = V->BankVaultCoins;
	V->BankVaultCoins = 0;
	V->AcademyResearchLevel = 0;
	V->TownGuildRank = 0;
	V->ActiveChapelBlessing = NAME_None;
	V->ReloadVillageState(Player);
	TestEqual(TEXT("Reload restores BankVaultCoins"), V->BankVaultCoins, SavedVault);
	TestEqual(TEXT("Reload restores AcademyResearchLevel 3"), V->AcademyResearchLevel, 3);
	TestEqual(TEXT("Reload restores TownGuildRank S"), V->TownGuildRank, 4);
	TestEqual(TEXT("Reload restores Chapel Blessing"), V->ActiveChapelBlessing, FName(TEXT("Valor")));
	TestTrue(TEXT("Reload restores Bathhouse soak state"), V->bBathhouseSoakedToday);

	// 9. Verify combat modifiers from Town Services (Academy T3 + Bathhouse + Valor + Castle)
	Player->SetActorLocation(FVector(5000.f, -500.f, 99.f));
	AGolemSparring* B = W->SpawnActor<AGolemSparring>(FVector(5000.f, -500.f, 99.f), FRotator::ZeroRotator, P);
	TestTrue(TEXT("Start sparring with town service buffs"), B->BeginSparring(V, Player));
	if (TestTrue(TEXT("Member spawned cleanly"), B->Members.Num() == 1))
	{
		B->Members[0].Actor->SetActorLocation(B->Members[0].Formation + FVector(0.f, 0.f, 99.f));
		B->Tick(0.1f);
		// Base 100 + Bath 15 + AcademyT3 20 = 135 MaxHealth; TP = Base 40 + AcademyT1 15 = 55
		TestEqual(TEXT("Town buffs grant 135 MaxHealth (100+15+20)"), B->Members[0].MaxHealth, 135.f);
		TestEqual(TEXT("Academy T1 grants 55 starting TP (40+15)"), B->Members[0].TP, 55.f);
		// Strike base 20 * Valor(1.15) * AcademyT3(1.10) * Castle(1.10) = 27.83 dmg
		const float EnemyBefore = B->Enemy->Health;
		TestTrue(TEXT("Town-buffed Strike succeeds"), B->ExecuteAction(TEXT("Strike")));
		TestTrue(TEXT("Town-buffed Strike deals ~27.83 dmg"), FMath::IsNearlyEqual(EnemyBefore - B->Enemy->Health, 27.83f, 0.1f));
		// Incoming 20 dmg * (1 - (AcademyT3 0.12 + Castle 0.10 = 0.22)) = 15.6 dmg
		const float Taken = B->ReceiveDamage(B->Members[0].Actor, 20.f, B->Enemy);
		TestTrue(TEXT("AcademyT3 + Castle reduces 20 dmg to 15.6"), FMath::IsNearlyEqual(Taken, 15.6f, 0.05f));
	}
	B->CancelSparring();
	B->CancelSparring();

	Tower->Destroy();
	V->bUseGolemVillage = false;
	UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
	W->DestroyWorld(false);
	GEngine->DestroyWorldContext(W);
	return true;
}
