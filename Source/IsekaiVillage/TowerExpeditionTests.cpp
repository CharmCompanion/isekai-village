#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "TowerExpedition.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "GatherInventoryComponent.h"
#include "GolemSparring.h"
#include "SlimeRunicMagic.h"
#include "TownConstructionSave.h"
#include "BlacksmithForge.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

struct FTowerFixture
{
	UWorld* W=nullptr;AVillageRuntime* V=nullptr;AIsekaiVillageCharacter* P=nullptr;ATowerExpedition* T=nullptr;FString Slot;
	FTowerFixture()
	{
		const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
		W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);W->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/Engine.GameModeBase"));W->SetGameMode(URL);
		FActorSpawnParameters S;S.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		auto* Floor=W->SpawnActor<AStaticMeshActor>(FVector(0,0,-50),FRotator::ZeroRotator,S);Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Floor->SetActorScale3D(FVector(60,60,1));
		V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,S);P=W->SpawnActor<AIsekaiVillageCharacter>(FVector(0,-500,103),FRotator::ZeroRotator,S);T=W->SpawnActor<ATowerExpedition>(P->GetActorLocation(),FRotator::ZeroRotator,S);T->FloorOrigin=FVector(10000,0,1000);
		V->bUseAuthoredPlots=true;V->bUseGolemVillage=true;V->bUseOrganicGolemNeeds=true;V->SparringSlimeClass=ASlimeRunicMage::StaticClass();Slot=TEXT("Automation_Tower_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);V->ConstructionSaveSlot=Slot;
		FTownPlot Home;Home.Id=TEXT("Home");Home.Kind=ETownBuilding::House;Home.bBuilt=true;Home.BedBonus=4;Home.Location=FVector(1200,0,0);Home.StakeOffset=FVector(0,-500,0);Home.BuildingClass=AStaticMeshActor::StaticClass();
		FTownPlot Hall=Home;Hall.Id=TEXT("Hall");Hall.Kind=ETownBuilding::Guild;Hall.BedBonus=0;Hall.Location=FVector(-1200,0,0);V->AuthoredPlots={Home,Hall};V->InitializeConstruction();V->SaveVillageState(P);P->Gather->Stacks.Reset();
	}
	void Recruit(){P->PartyReserve->HireAdventurer(FText::FromString(TEXT("Expedition member")));V->ReconcileGolemPopulation();P->Gather->AddItem(TEXT("Bread"),8);P->Gather->AddItem(TEXT("Wood"),10);P->Gather->AddItem(TEXT("Stone"),10);}
	~FTowerFixture(){T->Destroy();V->bUseGolemVillage=false;UGameplayStatics::DeleteGameInSlot(Slot,0);W->DestroyWorld(false);GEngine->DestroyWorldContext(W);}
};

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerResourcesTest,"IsekaiVillage.Tower.ResourcesCampAndPersistence",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerResourcesTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;auto* T=F.T;auto* V=F.V;auto* P=F.P;
	TestFalse(TEXT("Cannot depart without a selected housed adventurer"),T->Depart(P));F.Recruit();P->Gather->Consume(TEXT("Bread"),8);
	TestFalse(TEXT("Missing provisions prevent departure"),T->Depart(P));P->Gather->AddItem(TEXT("Bread"),8);
	P->SetActorLocation(FVector(2000,-500,103));TestFalse(TEXT("Must use the actual tower gate"),T->Depart(P));P->SetActorLocation(T->GetActorLocation());
	if(!TestTrue(TEXT("Prepared party can depart"),T->Depart(P)))return false;
	TestEqual(TEXT("Provisions charged once"),P->Gather->GetCount(TEXT("Bread")),6);TestEqual(TEXT("One companion travels"),T->Companions.Num(),1);if(T->Companions.IsEmpty())return false;
	auto* A=T->Companions[0].Actor.Get();const FGuid Id=A->GolemId;const FVector Home=T->Companions[0].Home;const bool OriginalTick=T->Companions[0].bTickWasEnabled;
	TestTrue(TEXT("Expedition actors opt out of village wants and movement"),A->ActorHasTag(TEXT("ElrhunTowerParty")) && !A->IsActorTickEnabled());
	TestFalse(TEXT("Remote gathering rejected"),T->GatherDeposit(P,T->Deposits[0].Id));const auto Node=T->Deposits[0];P->SetActorLocation(T->FloorOrigin+Node.Offset+FVector(0,0,50));
	const int32 Stone=P->Gather->GetCount(TEXT("Stone"));TestTrue(TEXT("Physical deposit grants its seeded yield"),T->GatherDeposit(P,Node.Id));TestEqual(TEXT("Exact yield granted"),P->Gather->GetCount(TEXT("Stone")),Stone+Node.Yield);TestFalse(TEXT("Same-day duplicate gathering rejected"),T->GatherDeposit(P,Node.Id));
	const auto Other=T->Deposits[1];P->SetActorLocation(T->FloorOrigin+Other.Offset+FVector(0,0,50));V->ConstructionSaveSlot.Empty();const int32 Before=P->Gather->GetCount(TEXT("Stone"));TestFalse(TEXT("Unsaved resource action rolls back"),T->GatherDeposit(P,Other.Id));TestEqual(TEXT("Failed save grants no materials"),P->Gather->GetCount(TEXT("Stone")),Before);TestTrue(TEXT("Failed save preserves the deposit"),T->DepositAvailable(Other.Id));V->ConstructionSaveSlot=F.Slot;
	P->SetActorLocation(T->CampPoint());TestTrue(TEXT("Materials build a persistent camp"),T->UseCamp(P));TestEqual(TEXT("Camp wood charged exactly"),P->Gather->GetCount(TEXT("Wood")),6);P->PartyReserve->Reserve[0].Drives.Fatigue=70;for(auto& R:V->GolemResidents)if(R.Id==Id)R.Drives=P->PartyReserve->Reserve[0].Drives;
	TestTrue(TEXT("Established camp can rest the party"),T->UseCamp(P));TestEqual(TEXT("Rest reduces fatigue once"),P->PartyReserve->Reserve[0].Drives.Fatigue,35.f);TestFalse(TEXT("Repeated rest in one visit rejected"),T->UseCamp(P));
	V->SaveVillageState(P);auto* Saved=Cast<UTownConstructionSave>(UGameplayStatics::LoadGameFromSlot(F.Slot,0));TestNotNull(TEXT("Combined village/floor save exists"),Saved);if(!Saved)return false;
	TestTrue(TEXT("Camp and resource depletion persist together"),Saved->TowerFloor.bCampBuilt && Saved->TowerFloor.HarvestDays.Contains(Node.Id));
	const auto* Resident=Saved->Golems.FindByPredicate([&](const auto& R){return R.Id==Id;});TestTrue(TEXT("Village save keeps companion home coordinates, not remote tower positions"),Resident && Resident->Position.Equals(Home,1));
	TestTrue(TEXT("Camp return saves and restores the party"),T->ReturnToVillage(P));TestFalse(TEXT("Expedition flag cleared"),T->bInside);TestEqual(TEXT("Return restores the original actor tick state"),A->IsActorTickEnabled(),OriginalTick);TestFalse(TEXT("Return releases expedition ownership"),A->ActorHasTag(TEXT("ElrhunTowerParty")));TestTrue(TEXT("Return restores the original village position"),A->GetActorLocation().Equals(Home,1));
	const int32 Seed=V->TowerFloor.Seed;V->ReloadVillageState(P);TestEqual(TEXT("Seed survives reload"),V->TowerFloor.Seed,Seed);TestTrue(TEXT("Camp survives reload"),V->TowerFloor.bCampBuilt);TestFalse(TEXT("Gathered deposit stays depleted after reload"),T->DepositAvailable(Node.Id));++V->DayIndex;TestTrue(TEXT("Deposits renew on a later village day"),T->DepositAvailable(Node.Id));
	TestTrue(TEXT("Later expedition can depart"),T->Depart(P));TestTrue(TEXT("Established camp is the next arrival point"),P->GetActorLocation().Equals(T->CampPoint(),2));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerGuardianTest,"IsekaiVillage.Tower.GuardianAndModularPaths",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerGuardianTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;F.Recruit();auto* T=F.T;auto* P=F.P;auto* V=F.V;
	if(!TestTrue(TEXT("Expedition begins"),T->Depart(P)))return false;
	const auto Nodes=T->Deposits;int32 Instances=0;TInlineComponentArray<UInstancedStaticMeshComponent*> Meshes(T);for(auto* M:Meshes)Instances+=M->GetInstanceCount();T->BuildFloor();int32 Again=0;for(auto* M:Meshes)Again+=M->GetInstanceCount();TestEqual(TEXT("Rebuilding modules does not duplicate geometry"),Again,Instances);TestTrue(TEXT("Seeded resource coordinates remain stable"),T->Deposits[2].Offset.Equals(Nodes[2].Offset));
	FCollisionQueryParams Q;Q.AddIgnoredActor(P);for(const auto& C:T->Companions)Q.AddIgnoredActor(C.Actor);
	bool Supported=true;for(const auto& C:T->Connections)
	{const FVector A=T->FloorOrigin+T->Regions[C.X].Center,B=T->FloorOrigin+T->Regions[C.Y].Center;for(int32 I=0;I<=20;++I){const FVector Point=FMath::Lerp(A,B,I/20.f);FHitResult H;Supported&=F.W->LineTraceSingleByChannel(H,Point+FVector(0,0,100),Point-FVector(0,0,150),ECC_Visibility,Q) && H.ImpactNormal.Z>.9f;}}
	TestTrue(TEXT("All connected module centre lines have continuous supported ground"),Supported);
	const auto Crystal=T->Deposits[2];P->SetActorLocation(T->FloorOrigin+Crystal.Offset+FVector(0,0,50));TestFalse(TEXT("Crystal reward requires a guardian clear"),T->GatherDeposit(P,Crystal.Id));
	P->SetActorLocation(T->GuardianPoint());for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!TestTrue(TEXT("Present party can challenge the procedural guardian"),T->ChallengeGuardian(P)))return false;
	auto* B=T->GuardianBattle.Get();B->Tick(.1f);TestTrue(TEXT("Field encounter uses the existing command controller"),B->bFieldEncounter && B->Phase==TEXT("AwaitCommand"));
	for(int32 I=0;I<40 && B->Phase!=TEXT("Result");++I){if(B->Phase==TEXT("AwaitCommand"))B->ExecuteAction(TEXT("Strike"));else B->Tick(1.f);}
	TestTrue(TEXT("Actual combat can defeat the guardian"),B->bVictory);T->Tick(.1f);TestEqual(TEXT("Victory grants one saved visit clear"),V->TowerFloor.GuardianClearedVisit,V->TowerFloor.Visit);
	TestTrue(TEXT("Field combat never removes the village roster"),P->PartyReserve->Reserve.Num()==1);TestTrue(TEXT("Result releases combat while keeping expedition ownership"),T->Companions[0].Actor->ActorHasTag(TEXT("ElrhunTowerParty")) && !T->Companions[0].Actor->ActorHasTag(TEXT("ElrhunSparring")));
	B->CancelSparring();P->SetActorLocation(T->FloorOrigin+Crystal.Offset+FVector(0,0,50));TestTrue(TEXT("After closing victory, guarded crystals can be gathered"),T->GatherDeposit(P,Crystal.Id));TestEqual(TEXT("Crystal yield is exact"),P->Gather->GetCount(TEXT("Crystal")),Crystal.Yield);
	TestFalse(TEXT("Return is restricted to gate or built camp"),T->ReturnToVillage(P));
	return true;
}

static bool WinGuardian(FAutomationTestBase& Test,ATowerExpedition* T,AIsekaiVillageCharacter* P)
{
	P->SetActorLocation(T->GuardianPoint());for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!Test.TestTrue(TEXT("Party can challenge this floor's guardian"),T->ChallengeGuardian(P)))return false;
	auto* B=T->GuardianBattle.Get();B->Tick(.1f);if(!Test.TestTrue(TEXT("Guardian spawned"),IsValid(B->Enemy.Get())))return false;
	Test.TestTrue(TEXT("The guardian fight uses the saved floor plan"),B->bHasFloorPlan && B->FloorPlan.Floor==T->Village->TowerFloor.Floor);
	B->Enemy->Health=FMath::Min(B->Enemy->Health,20.f);
	for(int32 I=0;I<40 && B->Phase!=TEXT("Result");++I){if(B->Phase==TEXT("AwaitCommand"))B->ExecuteAction(TEXT("Strike"));else B->Tick(1.f);}
	T->Tick(.1f);const bool bWon=Test.TestTrue(TEXT("Guardian defeated"),B->bVictory) && Test.TestTrue(TEXT("Floor counts as cleared"),T->FloorCleared());
	B->CancelSparring();return bWon;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerRunTest,"IsekaiVillage.Tower.PortalsRunsAndRespawns",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerRunTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;F.Recruit();auto* T=F.T;auto* P=F.P;auto* V=F.V;auto& TF=V->TowerFloor;
	if(!TestTrue(TEXT("Run begins"),T->Depart(P)))return false;
	TestTrue(TEXT("A new run starts on floor 1 with an active run flag"),TF.Floor==1 && TF.bRunActive && TF.CurrentPlan.Floor==1);
	TestTrue(TEXT("Deposits are named per floor"),T->Deposits[0].Id==FName(TEXT("F1_Deposit0")));
	TestTrue(TEXT("No portals before the guardian falls"),T->AvailablePortals().IsEmpty());
	if(!WinGuardian(*this,T,P))return false;
	TestTrue(TEXT("Floor 1 clear opens Village and Forward only"),T->AvailablePortals()==TArray<ETowerPortal>({ETowerPortal::Village,ETowerPortal::Forward}));
	TestTrue(TEXT("The tower noticed the strikes"),UTowerAdaptationLibrary::NoticedHabits(TF.Memory,3,false).Contains(ETowerHabit::Physical));
	TestEqual(TEXT("Highest floor recorded"),TF.HighestFloor,1);

	P->SetActorLocation(T->PortalPoint(ETowerPortal::Forward));
	if(!TestTrue(TEXT("Forward portal moves on"),T->Interact(P)))return false;
	TestEqual(TEXT("Forward reaches floor 2"),TF.Floor,2);TestFalse(TEXT("A new floor starts uncleared"),T->FloorCleared());
	TestTrue(TEXT("Floor 2 deposits are separate"),T->Deposits[0].Id==FName(TEXT("F2_Deposit0")));
	TestTrue(TEXT("Floor 2 counters the strikes"),TF.CurrentPlan.Rules.Contains(FName(TEXT("Hardened"))));
	TestTrue(TEXT("The party arrives at the floor entry"),P->GetActorLocation().Equals(T->EntryPoint(),2));

	P->SetActorLocation(T->CampPoint());TestTrue(TEXT("Camp can be built during a run"),T->UseCamp(P));
	if(!WinGuardian(*this,T,P))return false;
	TestTrue(TEXT("A built camp adds the Camp portal"),T->AvailablePortals().Contains(ETowerPortal::Camp));
	P->SetActorLocation(T->PortalPoint(ETowerPortal::Camp));TestTrue(TEXT("Camp portal pauses at camp"),T->Interact(P) && P->GetActorLocation().Equals(T->CampPoint(),2));
	TestTrue(TEXT("Resting at camp works"),T->UseCamp(P));
	TestTrue(TEXT("Resting respawns the cleared floor's regular enemies"),!T->FloorCleared() && TF.CurrentPlan.bRespawn && TF.CampRests==1);

	TestTrue(TEXT("Trip home from camp"),T->ReturnToVillage(P));
	TestTrue(TEXT("A trip home keeps the run and camp"),!T->bInside && TF.bRunActive && TF.bCampBuilt && TF.TripsHomeUsed==1);
	TestTrue(TEXT("The run resumes"),T->Depart(P));TestTrue(TEXT("Resume arrives at camp on the same floor"),TF.Floor==2 && P->GetActorLocation().Equals(T->CampPoint(),2));
	TestFalse(TEXT("Rank D allows one trip home per run"),T->ReturnToVillage(P));
	P->PartyReserve->Reserve[0].Rank=1;TestEqual(TEXT("Rank C allows two trips"),T->TripsHomeAllowed(),2);P->PartyReserve->Reserve[0].Rank=0;

	const float Remembered=TF.Memory.Weights.FindRef(ETowerHabit::Physical);
	P->SetActorLocation(T->EntryPoint());TestTrue(TEXT("The arrival gate ends the run"),T->ReturnToVillage(P));
	TestTrue(TEXT("Ending the run loses the camp and trips"),!TF.bRunActive && !TF.bCampBuilt && TF.TripsHomeUsed==0 && TF.BossesDefeated.IsEmpty());
	TestEqual(TEXT("Ending the run keeps tower memory"),TF.Memory.Weights.FindRef(ETowerHabit::Physical),Remembered);
	TestTrue(TEXT("The gate can start from any cleared floor or the next one"),T->StartableFloors()==TArray<int32>({1,2,3}));
	TestTrue(TEXT("V at the gate changes the start floor"),T->CycleStartFloor(P) && TF.StartFloor==1);

	if(!TestTrue(TEXT("A new run begins on the chosen floor"),T->Depart(P) && TF.Floor==1))return false;
	const auto Node=T->Deposits[0];P->SetActorLocation(T->FloorOrigin+Node.Offset+FVector(0,0,50));const int32 StoneBefore=P->Gather->GetCount(TEXT("Stone"));
	TestTrue(TEXT("Gathering during a run"),T->GatherDeposit(P,Node.Id));
	P->SetActorLocation(T->GuardianPoint());for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!TestTrue(TEXT("Challenge for the failure case"),T->ChallengeGuardian(P)))return false;
	auto* B=T->GuardianBattle.Get();B->Tick(.1f);for(auto& M:B->Members)M.Health=1;
	for(int32 I=0;I<40 && B->Phase!=TEXT("Result");++I){if(B->Phase==TEXT("AwaitCommand"))B->ExecuteAction(TEXT("Defend"));else B->Tick(1.f);}
	TestTrue(TEXT("A full party defeat is recorded"),B->bPartyDefeated);
	T->Tick(1.1f);
	TestTrue(TEXT("A failed run sends the party home and ends the run"),!T->bInside && !TF.bRunActive && !TF.bCampBuilt);
	TestEqual(TEXT("A failed run loses half of this run's gathered items"),P->Gather->GetCount(TEXT("Stone")),StoneBefore+Node.Yield-Node.Yield/2);
	TestTrue(TEXT("Failure keeps tower memory"),TF.Memory.FloorsRecorded>=2);
	TestTrue(TEXT("Failure never removes the roster"),P->PartyReserve->Reserve.Num()==1);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerProgressionAndBossTest,"IsekaiVillage.Tower.FloorProgressionAndBossExams",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerProgressionAndBossTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;F.Recruit();auto* T=F.T;auto* P=F.P;auto* V=F.V;auto& TF=V->TowerFloor;
	TF.HighestFloor=2;TF.StartFloor=3;
	if(!TestTrue(TEXT("Depart to floor 3"),T->Depart(P)))return false;
	TestEqual(TEXT("Departed to floor 3"),TF.Floor,3);
	TestTrue(TEXT("Floor 3 deposits include Iron"),T->Deposits.ContainsByPredicate([](const auto& D){return D.Item==TEXT("Iron");}));
	const int32 InitialCrystals=P->Gather->GetCount(TEXT("Crystal"));
	TF.Floor=5;TF.CurrentPlan.bBoss=true;TF.CurrentPlan.Floor=5;
	T->BuildFloor();
	TestTrue(TEXT("Floor 5 is identified as a boss floor"),UTowerAdaptationLibrary::IsBossFloor(5,5));
	FTowerFloorLog BossLog;BossLog.Fights=1;BossLog.Actions=2;BossLog.PartySize=1;
	TestTrue(TEXT("Commit boss clear on floor 5"),T->CommitGuardianClear(BossLog));
	TestTrue(TEXT("BossesDefeated records floor 5"),TF.BossesDefeated.Contains(5));
	TestEqual(TEXT("Defeating a boss exam awards 5 bonus crystals to party"),P->Gather->GetCount(TEXT("Crystal")),InitialCrystals+5);
	TestEqual(TEXT("RunLoot tracks the bonus crystals"),TF.RunLoot.FindRef(TEXT("Crystal")),5);
	TF.Floor=10;TF.CurrentPlan.bBoss=true;TF.CurrentPlan.Floor=10;
	T->CommitGuardianClear(BossLog);
	TestTrue(TEXT("Floor 10 clear unlocks New Game Plus"),TF.bNewGamePlus);
	TestTrue(TEXT("Startable floors now includes Echo depths"),T->StartableFloors().Contains(-1));

	// Field Provisions (Bread sharing)
	P->PartyReserve->Reserve[0].Drives.Fatigue=50.f;
	const int32 BreadBefore=P->Gather->GetCount(TEXT("Bread"));
	TestTrue(TEXT("Share rations with party"),T->ShareRations(P));
	TestEqual(TEXT("One bread consumed"),P->Gather->GetCount(TEXT("Bread")),BreadBefore-1);
	TestEqual(TEXT("Fatigue reduced by 25"),P->PartyReserve->Reserve[0].Drives.Fatigue,25.f);
	P->Gather->Consume(TEXT("Bread"),P->Gather->GetCount(TEXT("Bread")));
	TestFalse(TEXT("Cannot share rations with 0 bread"),T->ShareRations(P));
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerForgeLoopTest,"IsekaiVillage.Tower.ForgeAndAdventurerGear",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerForgeLoopTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;F.Recruit();auto* T=F.T;auto* P=F.P;auto* V=F.V;
	FActorSpawnParameters S;S.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	auto* Forge=F.W->SpawnActor<ABlacksmithForge>(FVector(0,0,0),FRotator::ZeroRotator,S);
	TestNotNull(TEXT("Blacksmith forge spawns"),Forge);
	if(!Forge)return false;

	TestEqual(TEXT("Initial party member weapon tier is 0"),P->PartyReserve->Reserve[0].WeaponTier,0);
	TestEqual(TEXT("Initial party member armor tier is 0"),P->PartyReserve->Reserve[0].ArmorTier,0);

	P->Gather->Stacks.Reset();
	TestFalse(TEXT("Cannot forge without materials"),Forge->TryForgeAdventurerGear(P));

	// Add Iron & Wood for Iron Weapon
	P->Gather->AddItem(TEXT("Iron"),4);
	P->Gather->AddItem(TEXT("Wood"),2);
	TestTrue(TEXT("Forge Iron Weapon for adventurer"),Forge->TryForgeAdventurerGear(P));
	TestEqual(TEXT("Weapon tier is now 1"),P->PartyReserve->Reserve[0].WeaponTier,1);
	TestEqual(TEXT("Iron consumed"),P->Gather->GetCount(TEXT("Iron")),0);
	TestEqual(TEXT("Wood consumed"),P->Gather->GetCount(TEXT("Wood")),0);

	// Add Iron & Stone for Iron Armor
	P->Gather->AddItem(TEXT("Iron"),4);
	P->Gather->AddItem(TEXT("Stone"),2);
	TestTrue(TEXT("Forge Iron Armor for adventurer"),Forge->TryForgeAdventurerGear(P));
	TestEqual(TEXT("Armor tier is now 1"),P->PartyReserve->Reserve[0].ArmorTier,1);
	TestEqual(TEXT("Iron consumed"),P->Gather->GetCount(TEXT("Iron")),0);
	TestEqual(TEXT("Stone consumed"),P->Gather->GetCount(TEXT("Stone")),0);

	// Add Crystal & Iron for Runic Weapon
	P->Gather->AddItem(TEXT("Crystal"),4);
	P->Gather->AddItem(TEXT("Iron"),6);
	TestTrue(TEXT("Forge Runic Weapon for adventurer"),Forge->TryForgeAdventurerGear(P));
	TestEqual(TEXT("Weapon tier is now 2"),P->PartyReserve->Reserve[0].WeaponTier,2);

	// Add Crystal & Iron for Runic Armor
	P->Gather->AddItem(TEXT("Crystal"),4);
	P->Gather->AddItem(TEXT("Iron"),6);
	TestTrue(TEXT("Forge Runic Armor for adventurer"),Forge->TryForgeAdventurerGear(P));
	TestEqual(TEXT("Armor tier is now 2"),P->PartyReserve->Reserve[0].ArmorTier,2);

	// Test persistence across Save & Reload
	V->SaveVillageState(P);
	P->PartyReserve->Reserve[0].WeaponTier=0;
	P->PartyReserve->Reserve[0].ArmorTier=0;
	V->ReloadVillageState(P);
	TestEqual(TEXT("Weapon tier survives save/reload"),P->PartyReserve->Reserve[0].WeaponTier,2);
	TestEqual(TEXT("Armor tier survives save/reload"),P->PartyReserve->Reserve[0].ArmorTier,2);

	// Test combat stats in GolemSparring field encounter
	P->Gather->AddItem(TEXT("Bread"),4);
	P->SetActorLocation(T->GetActorLocation());
	if(!TestTrue(TEXT("Depart to tower"),T->Depart(P)))return false;
	P->SetActorLocation(T->GuardianPoint());
	for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!TestTrue(TEXT("Challenge guardian"),T->ChallengeGuardian(P)))return false;
	auto* B=T->GuardianBattle.Get();
	TestNotNull(TEXT("Guardian battle exists"),B);
	if(!B)return false;
	B->Tick(0.1f);
	TestEqual(TEXT("Sparring member weapon tier matches adventurer"),B->Members[0].WeaponTier,2);
	TestEqual(TEXT("Sparring member armor tier matches adventurer"),B->Members[0].ArmorTier,2);
	TestEqual(TEXT("Sparring member max health includes Runic Armor bonus (+50)"),B->Members[0].MaxHealth,150.f);
	TestEqual(TEXT("Sparring member health starts at max"),B->Members[0].Health,150.f);
	TestEqual(TEXT("Sparring member starting TP includes Runic Weapon bonus (+10)"),B->Members[0].TP,50.f);

	// Verify armor damage reduction in ReceiveDamage
	B->Phase=TEXT("EnemyTurn");
	const float DamageBefore=B->Members[0].Health;
	const float Taken=B->ReceiveDamage(B->Members[0].Actor,20.f,B->Enemy);
	TestEqual(TEXT("Runic Armor 20% passive guard mitigates 20 damage to 16"),Taken,16.f);
	TestEqual(TEXT("Health reduced by mitigated damage"),B->Members[0].Health,DamageBefore-16.f);

	B->CancelSparring();
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerBossMinionsTest,"IsekaiVillage.Tower.BossMinionsAndMultiTarget",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerBossMinionsTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;F.Recruit();auto* T=F.T;auto* P=F.P;auto* V=F.V;auto& TF=V->TowerFloor;
	TF.HighestFloor=4;TF.StartFloor=5;
	if(!TestTrue(TEXT("Depart to Floor 5 exam"),T->Depart(P)))return false;
	P->SetActorLocation(T->GuardianPoint());
	for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!TestTrue(TEXT("Challenge Floor 5 Boss"),T->ChallengeGuardian(P)))return false;
	auto* B=T->GuardianBattle.Get();TestNotNull(TEXT("Boss battle exists"),B);if(!B)return false;
	B->Tick(0.1f);
	TestEqual(TEXT("Floor 5 Boss spawns 1 minion acolyte"),B->Minions.Num(),1);
	TestEqual(TEXT("Floor 5 living minion count is 1"),B->LivingMinionCount(),1);
	TestTrue(TEXT("1 living minion grants 20% Boss Ward"),FMath::IsNearlyEqual(B->BossWardReduction(),0.20f,.01f));

	const float BossHPBefore=B->Enemy->Health;
	TestTrue(TEXT("Strike warded Boss"),B->ExecuteAction(TEXT("Strike")));
	const float DealtWarded=BossHPBefore-B->Enemy->Health;
	TestTrue(TEXT("Boss Ward reduces Strike damage"),DealtWarded>0.f && DealtWarded<20.f);

	for(int32 I=0;I<10 && B->Phase!=TEXT("AwaitCommand") && B->Phase!=TEXT("Result");++I)B->Tick(0.5f);
	TestEqual(TEXT("Party turn returns after boss/minion actions"),B->Phase,FName(TEXT("AwaitCommand")));

	TestTrue(TEXT("Cycle target moves to minion 0"),B->CycleEnemyTarget() && B->SelectedEnemyIndex==1);
	B->Minions[0].Actor->Health=10.f;
	TestTrue(TEXT("Strike defeats targeted minion"),B->ExecuteAction(TEXT("Strike")));
	TestEqual(TEXT("Living minions drops to 0"),B->LivingMinionCount(),0);
	TestEqual(TEXT("Boss Ward breaks cleanly to 0%"),B->BossWardReduction(),0.f);
	TestEqual(TEXT("Auto-retarget returns to living Boss"),B->SelectedEnemyIndex,0);
	TestFalse(TEXT("Victory waits until Boss falls too"),B->bVictory);

	for(int32 I=0;I<10 && B->Phase!=TEXT("AwaitCommand") && B->Phase!=TEXT("Result");++I)B->Tick(0.5f);
	B->Enemy->Health=10.f;
	TestTrue(TEXT("Final strike defeats Floor 5 Boss"),B->ExecuteAction(TEXT("Strike")));
	T->Tick(0.1f);
	TestTrue(TEXT("Floor 5 Boss encounter resolved in Victory"),B->bVictory && T->FloorCleared());
	B->CancelSparring();

	P->SetActorLocation(T->EntryPoint());
	TestTrue(TEXT("Return through arrival gate"),T->ReturnToVillage(P));
	TF.HighestFloor=9;TF.StartFloor=10;
	if(!TestTrue(TEXT("Depart to Floor 10 Runic Apex"),T->Depart(P)))return false;
	P->SetActorLocation(T->GuardianPoint());
	for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!TestTrue(TEXT("Challenge Floor 10 Boss"),T->ChallengeGuardian(P)))return false;
	auto* B10=T->GuardianBattle.Get();TestNotNull(TEXT("Floor 10 battle exists"),B10);if(!B10)return false;
	B10->Tick(0.1f);
	TestEqual(TEXT("Floor 10 Boss spawns 2 minion acolytes"),B10->Minions.Num(),2);
	TestTrue(TEXT("2 living minions grant 40% Boss Ward"),FMath::IsNearlyEqual(B10->BossWardReduction(),0.40f,.01f));
	TestTrue(TEXT("Cycle target 0 -> 1"),B10->CycleEnemyTarget() && B10->SelectedEnemyIndex==1);
	TestTrue(TEXT("Cycle target 1 -> 2"),B10->CycleEnemyTarget() && B10->SelectedEnemyIndex==2);
	TestTrue(TEXT("Cycle target 2 -> 0"),B10->CycleEnemyTarget() && B10->SelectedEnemyIndex==0);

	B10->Members[0].Health=300.f;B10->Enemy->Health=5.f;
	for(int32 I=0;I<20 && IsValid(B10->Enemy) && B10->Enemy->Health>0.f && B10->Phase!=TEXT("Result");++I){if(B10->Phase==TEXT("AwaitCommand"))B10->ExecuteAction(TEXT("Strike"));else B10->Tick(0.5f);}
	TestTrue(TEXT("Defeat Floor 10 Boss while minions live"),!IsValid(B10->Enemy) || B10->Enemy->Health<=0.f);
	TestFalse(TEXT("Victory requires defeating remaining minions"),B10->bVictory);
	TestTrue(TEXT("Selected target auto-advances to a living minion"),B10->SelectedEnemyIndex>=1 && B10->SelectedEnemyIndex<=2);
	B10->CancelSparring();
	return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerRelicAltarsTest,"IsekaiVillage.Tower.RelicAltarsAndBoons",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerRelicAltarsTest::RunTest(const FString& Parameters)
{
	FTowerFixture F;F.Recruit();auto* T=F.T;auto* P=F.P;auto* V=F.V;auto& TF=V->TowerFloor;
	if(!TestTrue(TEXT("Depart to Floor 1"),T->Depart(P)))return false;
	TestTrue(TEXT("Floor 1 Relic Altar starts available"),T->FloorAltarAvailable());
	TestFalse(TEXT("Cannot activate altar remotely"),T->ActivateAltar(P));

	P->SetActorLocation(T->AltarPoint());
	TestTrue(TEXT("Interact at Altar claims Floor 1 relic"),T->Interact(P));
	TestFalse(TEXT("Floor 1 Altar is now dormant"),T->FloorAltarAvailable());
	TestFalse(TEXT("Duplicate altar claim rejected"),T->ActivateAltar(P));
	TestEqual(TEXT("One relic active for this run"),TF.RunRelics.Num(),1);

	const ETowerRelic FirstRelic=TF.RunRelics[0];
	P->SetActorLocation(T->CampPoint());
	TestTrue(TEXT("Build camp for trip home"),T->UseCamp(P));
	TestTrue(TEXT("Trip home preserves run and relics"),T->ReturnToVillage(P));
	TF.RunRelics.Reset();TF.RelicClaimedFloors.Reset();
	V->ReloadVillageState(P);
	TestEqual(TEXT("RunRelics survive save/reload"),TF.RunRelics.Num(),1);
	TestEqual(TEXT("Same relic survives save/reload"),TF.RunRelics[0],FirstRelic);
	TestFalse(TEXT("Floor 1 altar stays claimed across reload"),T->FloorAltarAvailable());
	if(!TestTrue(TEXT("Resume run with active relics"),T->Depart(P)))return false;

	// Test QuarryBlessing deposit yield bonus (+1)
	if(!TF.RunRelics.Contains(ETowerRelic::QuarryBlessing))TF.RunRelics.Add(ETowerRelic::QuarryBlessing);
	const auto Node=T->Deposits[0];
	const int32 StoneBefore=P->Gather->GetCount(TEXT("Stone"));
	P->SetActorLocation(T->FloorOrigin+Node.Offset+FVector(0,0,50));
	TestTrue(TEXT("Gather Stone with QuarryBlessing"),T->GatherDeposit(P,Node.Id));
	TestEqual(TEXT("QuarryBlessing adds +1 bonus yield"),P->Gather->GetCount(TEXT("Stone")),StoneBefore+Node.Yield+1);

	// Test combat relics: RunicSurge, AegisOath, BerserkerBrand
	P->PartyReserve->Reserve[0].Drives.Interest=TEXT("Guard");
	for(ETowerRelic R:{ETowerRelic::RunicSurge,ETowerRelic::AegisOath,ETowerRelic::BerserkerBrand})
		TF.RunRelics.AddUnique(R);
	P->SetActorLocation(T->GuardianPoint());
	for(int32 I=0;I<T->Companions.Num();++I)T->Companions[I].Actor->SetActorLocation(T->GuardianPoint()+FVector(150.f*(I+1),0,0));
	if(!TestTrue(TEXT("Challenge guardian with relics active"),T->ChallengeGuardian(P)))return false;
	auto* B=T->GuardianBattle.Get();TestNotNull(TEXT("Guardian battle exists"),B);if(!B)return false;
	B->Tick(0.1f);
	TestEqual(TEXT("AegisOath adds +25 Max HP"),B->Members[0].MaxHealth,125.f);
	TestEqual(TEXT("RunicSurge adds +20 starting TP"),B->Members[0].TP,60.f);

	const float EnemyHPBefore=B->Enemy->Health;
	TestTrue(TEXT("Strike with BerserkerBrand deals +35% damage"),B->ExecuteAction(TEXT("Strike")));
	TestTrue(TEXT("Berserker Strike dealt 27 damage (20 * 1.35)"),FMath::IsNearlyEqual(EnemyHPBefore-B->Enemy->Health,27.f,.01f));
	TestTrue(TEXT("RunicSurge reduces turn delay by 15%"),B->Members[0].ReadyAt<90.f);

	B->Phase=TEXT("EnemyTurn");
	const float Taken=B->ReceiveDamage(B->Members[0].Actor,20.f,B->Enemy);
	TestTrue(TEXT("BerserkerBrand (+15% taken) + AegisOath (15% guard) yields 19.55 dmg"),FMath::IsNearlyEqual(Taken,19.55f,.05f));
	B->CancelSparring();
	B->CancelSparring();

	P->SetActorLocation(T->EntryPoint());
	TestTrue(TEXT("Ending the run safely clears temporary RunRelics"),T->EndRun(P,false));
	TestTrue(TEXT("RunRelics reset on run end"),TF.RunRelics.IsEmpty());
	TestTrue(TEXT("RelicClaimedFloors reset on run end"),TF.RelicClaimedFloors.IsEmpty());
	return true;
}
#endif
