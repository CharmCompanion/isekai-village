#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "TownConstructionSave.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FVillageGolemLoopTest, "IsekaiVillage.Village.GolemShopLoop", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FVillageGolemLoopTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
	FActorSpawnParameters Spawn; Spawn.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, Spawn);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(0, 0, 200), FRotator::ZeroRotator, Spawn);
	V->bUseAuthoredPlots = true; V->bUseGolemVillage = true;
	V->ConstructionSaveSlot = TEXT("Automation_GolemVillage_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);
	FTownPlot House; House.Id = TEXT("Cottage"); House.Kind = ETownBuilding::House; House.BedBonus = 2; House.WoodCost = 8; House.BuildingClass = AStaticMeshActor::StaticClass();
	FTownPlot Shop = House; Shop.Id = TEXT("Shop"); Shop.Kind = ETownBuilding::Shop; Shop.BedBonus = 0;
	V->BuildingCatalog = {House, Shop};
	FTownPlot Land; Land.bFlexibleUse = true; Land.Kind = ETownBuilding::Unassigned; Land.BuildableSize = 2400;
	for (int32 I = 0; I < 4; ++I) { Land.Id = FName(*FString::Printf(TEXT("Parcel%d"), I)); Land.Location = FVector(I * 3000, 0, 0); Land.StakeOffset = FVector(0, -500, 0); V->AuthoredPlots.Add(Land); }
	V->InitializeConstruction(); Player->Gather->Stacks.Reset(); Player->Gather->AddItem(TEXT("Wood"), 80);
	V->SelectBuilding(TEXT("Shop")); V->TryBuildPlot(TEXT("Parcel0"), Player);
	TestEqual(TEXT("Shop without housing creates no resident"), V->GolemResidents.Num(), 0);
	TestEqual(TEXT("Unstaffed shop keeps its stock"), V->GolemShops[0].Wood, 4);
	V->SelectBuilding(TEXT("Cottage")); V->TryBuildPlot(TEXT("Parcel1"), Player);
	TestEqual(TEXT("Building housing staffs an existing shop"), V->GolemResidents.Num(), 1);
	const FGuid FirstId = V->GolemResidents[0].Id;
	const FString FirstName = V->GolemResidents[0].Name;
	TestEqual(TEXT("Resident remembers actual home plot"), V->GolemResidents[0].HomePlot, FName(TEXT("Parcel1")));
	V->ReconcileGolemPopulation(); V->ReconcileGolemPopulation();
	TestEqual(TEXT("Reconciliation does not duplicate residents"), V->GolemResidents.Num(), 1);
	V->SelectBuilding(TEXT("Shop")); V->TryBuildPlot(TEXT("Parcel2"), Player); V->SelectBuilding(TEXT("Shop")); V->TryBuildPlot(TEXT("Parcel3"), Player);
	TestEqual(TEXT("Two beds cannot house three workers"), V->GolemResidents.Num(), 2);
	V->TryBuildPlot(TEXT("Parcel1"), Player);
	TestEqual(TEXT("A loft's extra bed permits one more worker"), V->GolemResidents.Num(), 3);
	TestEqual(TEXT("Purchases and loft charge exact wood"), Player->Gather->GetCount(TEXT("Wood")), 42);
	int32 ActorCount = 0; AVillageGolemCitizen* Worker = nullptr;
	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It) { ++ActorCount; if (It->GolemId == FirstId) Worker = *It; }
	TestEqual(TEXT("One actor per assigned resident"), ActorCount, 3);
	if (!TestNotNull(TEXT("First worker exists"), Worker)) return false;
	const FTownPlot* Work = V->FindPlot(TEXT("Parcel0"));
	Player->SetActorLocation(Work->Location + Work->StakeOffset + FVector(0, 0, 99));
	TestFalse(TEXT("Cannot trade before worker reaches work"), V->TradeWood(Work->Id, false, Player));
	Worker->SetGoal(EVillagePlace::Shop, V->WorkerEntrance(*Work)); Worker->SetActorLocation(Worker->Goal + FVector(0, 0, 99));
	TestTrue(TEXT("Sell a wood at staffed shop"), V->TradeWood(Work->Id, false, Player));
	TestEqual(TEXT("Sale pays player two coins"), Player->Gather->GetCount(TEXT("Coin")), 2);
	TestEqual(TEXT("Sale removes one wood"), Player->Gather->GetCount(TEXT("Wood")), 41);
	TestEqual(TEXT("Shop pays from its own till"), V->GolemShops[0].Coins, 38);
	TestTrue(TEXT("Buy a wood with earned coins"), V->TradeWood(Work->Id, true, Player));
	TestEqual(TEXT("Purchase consumes coins"), Player->Gather->GetCount(TEXT("Coin")), 0);
	TestEqual(TEXT("Purchase returns wood"), Player->Gather->GetCount(TEXT("Wood")), 42);
	TestFalse(TEXT("Insufficient coins never grants stock"), V->TradeWood(Work->Id, true, Player));
	TestEqual(TEXT("Failed trade leaves stock untouched"), V->GolemShops[0].Wood, 4);
	V->GolemShops[0].Coins = 0;
	TestFalse(TEXT("Empty till cannot pay a sale"), V->TradeWood(Work->Id, false, Player));
	TestEqual(TEXT("Rejected sale keeps player's wood"), Player->Gather->GetCount(TEXT("Wood")), 42);
	V->GolemShops[0].Coins = 40;
	V->TradeWood(Work->Id, false, Player); V->DayIndex = 3; V->Trust = 31; Player->SpherePoints = 5;
	TestTrue(TEXT("Save complete village slice"), V->SaveVillageState(Player));
	Player->Gather->Stacks.Reset(); V->GolemShops[0].Wood = 999; V->DayIndex = 99; Player->SpherePoints = 99;
	V->ReloadVillageState(Player);
	TestEqual(TEXT("Reload keeps resident count"), V->GolemResidents.Num(), 3);
	TestEqual(TEXT("Reload preserves stable identity"), V->GolemResidents[0].Id, FirstId);
	TestEqual(TEXT("Reload preserves name"), V->GolemResidents[0].Name, FirstName);
	TestEqual(TEXT("Reload restores inventory"), Player->Gather->GetCount(TEXT("Wood")), 41);
	TestEqual(TEXT("Reload restores earned coins"), Player->Gather->GetCount(TEXT("Coin")), 2);
	TestEqual(TEXT("Reload restores shop stock"), V->GolemShops[0].Wood, 5);
	TestEqual(TEXT("Reload restores shop till"), V->GolemShops[0].Coins, 38);
	TestEqual(TEXT("Reload restores village day"), V->DayIndex, 3);
	TestEqual(TEXT("Reload restores trust"), V->Trust, 31);
	TestEqual(TEXT("Reload preserves existing grid points"), Player->SpherePoints, 5);
	ActorCount = 0; for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It) ++ActorCount;
	TestEqual(TEXT("Reload has no duplicate worker actors"), ActorCount, 3);
	TArray<FVector> Route;
	TestFalse(TEXT("No street graph means no unsafe direct walk"), V->BuildStreetRoute(FVector(0, 0, 0), FVector(1000, 0, 0), Route));
	V->StreetNodes = {FVector(0,0,0), FVector(0,1000,0), FVector(1000,1000,0), FVector(1000,0,0)};
	V->StreetEdges = {FIntPoint(0,1), FIntPoint(1,2), FIntPoint(2,3)};
	TestTrue(TEXT("Street route exists around reserved land"), V->BuildStreetRoute(FVector(0,0,0), FVector(1000,0,0), Route));
	TestTrue(TEXT("Street route follows bend instead of cutting across land"), Route.Contains(FVector(0,1000,0)) && Route.Contains(FVector(1000,1000,0)));
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	AStaticMeshActor* Ground = W->SpawnActor<AStaticMeshActor>(FVector(500,500,-50), FRotator::ZeroRotator, Spawn);
	Ground->GetStaticMeshComponent()->SetStaticMesh(Cube); Ground->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll")); Ground->SetActorScale3D(FVector(40,40,1));
	AStaticMeshActor* Obstacle = W->SpawnActor<AStaticMeshActor>(FVector(0,500,150), FRotator::ZeroRotator, Spawn);
	Obstacle->GetStaticMeshComponent()->SetStaticMesh(Cube); Obstacle->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll")); Obstacle->SetActorScale3D(FVector(2,2,3));
	for (TActorIterator<AVillageGolemCitizen> It(W); It; ++It) if (It->GolemId == FirstId) Worker = *It;
	Worker->SetActorLocation(FVector(0,0,99)); Worker->SetGoal(EVillagePlace::Shop, FVector(0,1000,0));
	Worker->Tick(1.f);
	TestTrue(TEXT("Worker can advance on clear street ground"), Worker->GetActorLocation().Y > 100);
	Worker->Tick(1.f); Worker->Tick(1.f);
	TestTrue(TEXT("Worker stops at a physical obstacle"), Worker->bRouteBlocked && Worker->GetActorLocation().Y < 400);
	Obstacle->Destroy(); Worker->Tick(1.f);
	TestTrue(TEXT("Worker resumes after obstacle clears"), !Worker->bRouteBlocked && Worker->GetActorLocation().Y > 300);
	AStaticMeshActor* Step = W->SpawnActor<AStaticMeshActor>(FVector(0,-350,6), FRotator::ZeroRotator, Spawn);
	Step->GetStaticMeshComponent()->SetStaticMesh(Cube); Step->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll")); Step->SetActorScale3D(FVector(4,5,.12));
	Worker->SetActorLocation(FVector(0,-130,111)); Worker->SetGoal(EVillagePlace::Shop, FVector(0,200,0));
	for (int32 I=0; I<10; ++I) Worker->Tick(.1f);
	TestTrue(TEXT("Worker crosses a small downward street seam without blocking"), Worker->GetActorLocation().Y > -20 && !Worker->bRouteBlocked);
	Step->Destroy();

 V->StreetNodes={FVector(0,0,0),FVector(1000,0,0)};V->StreetEdges={FIntPoint(0,1)};
 AVillageGolemCitizen* Oncoming=nullptr;
 for(TActorIterator<AVillageGolemCitizen> It(W);It;++It)if(*It!=Worker){Oncoming=*It;break;}
 if(Oncoming)
 {
  Worker->SetActorLocation(FVector(100,0,99));Oncoming->SetActorLocation(FVector(900,0,99));
  Worker->SetGoal(EVillagePlace::Shop,FVector(1000,0,0));Oncoming->SetGoal(EVillagePlace::Shop,FVector(0,0,0));
  for(int32 I=0;I<100;++I){Worker->Tick(.05f);Oncoming->Tick(.05f);}
  TestTrue(TEXT("Opposing workers pass with capsule collision enabled"),Worker->GetActorLocation().X>800 && Oncoming->GetActorLocation().X<200);
 }
	// Old construction saves still load; an absent inventory must not wipe the player.
	UTownConstructionSave* Old = Cast<UTownConstructionSave>(UGameplayStatics::CreateSaveGameObject(UTownConstructionSave::StaticClass()));
	Old->BuiltPlots = {TEXT("Parcel0"), TEXT("Parcel1")}; Old->PlotBuildingIds.Add(TEXT("Parcel0"), TEXT("Shop")); Old->PlotBuildingIds.Add(TEXT("Parcel1"), TEXT("Cottage"));
	UGameplayStatics::SaveGameToSlot(Old, V->ConstructionSaveSlot, 0); Player->Gather->AddItem(TEXT("Coin"), 5);
	V->ReloadVillageState(Player);
	TestTrue(TEXT("Old building purchases survive migration"), V->FindPlot(TEXT("Parcel0"))->bBuilt);
	TestEqual(TEXT("Old save does not erase existing inventory"), Player->Gather->GetCount(TEXT("Coin")), 7);
	TestEqual(TEXT("Old built shop and home gain a golem"), V->GolemResidents.Num(), 1);
	// Disable shutdown autosave before removing this test's unique save slot.
	V->bUseGolemVillage = false; UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot, 0);
	W->DestroyWorld(false); GEngine->DestroyWorldContext(W);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FVillageHallDeliveryTest, "IsekaiVillage.Village.HallDeliveries", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FVillageHallDeliveryTest::RunTest(const FString& Parameters)
{
 const auto IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W = UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);
 GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
 FActorSpawnParameters P; P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 AVillageRuntime* V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,P);
 auto* Player=W->SpawnActor<AIsekaiVillageCharacter>(FVector(0,0,99),FRotator::ZeroRotator,P);
 V->bUseGolemVillage=true; V->bUseAuthoredPlots=true;
 V->ConstructionSaveSlot=TEXT("Automation_HallDelivery_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);
 FTownPlot Hall; Hall.Id=TEXT("Hall"); Hall.Kind=ETownBuilding::Guild; Hall.bBuilt=true; Hall.BuildingClass=AStaticMeshActor::StaticClass(); Hall.StakeOffset=FVector(0,-500,0);
 V->AuthoredPlots={Hall}; V->InitializeConstruction();
 TestEqual(TEXT("Hall needs a free bed before creating courier"),V->GolemResidents.Num(),0);
 FTownPlot Home=Hall; Home.Id=TEXT("Home"); Home.Kind=ETownBuilding::House; Home.BedBonus=1; Home.Location=FVector(2000,0,0);
 V->AuthoredPlots.Add(Home); V->InitializeConstruction(); V->ReconcileGolemPopulation();
 TestEqual(TEXT("Housed hall creates exactly one courier"),V->GolemResidents.Num(),1);
 TestEqual(TEXT("Hall does not become a wood shop"),V->GolemShops.Num(),0);
 AVillageGolemCitizen* Courier=nullptr;
 for(TActorIterator<AVillageGolemCitizen> It(W);It;++It) if(It->GetOwner()==V) Courier=*It;
 if(!TestNotNull(TEXT("Courier actor exists"),Courier)) { V->bUseGolemVillage=false; W->DestroyWorld(false); GEngine->DestroyWorldContext(W); return false; }
 FVillageSupplySite Stone; Stone.Item=TEXT("Stone"); Stone.Location=FVector(3000,0,0); Stone.Stock=5;
 FVillageSupplySite Fish=Stone; Fish.Item=TEXT("Fish"); Fish.Location=FVector(4000,0,0); Fish.Stock=2;
 V->SupplySites={Stone,Fish}; V->WindowIndex=1;
 V->AdvanceHallCourier(Courier,5.f);
 TestEqual(TEXT("Remote sources cannot be gathered"),V->SupplySites[0].Stock,5);
 Courier->SetActorLocation(Stone.Location+FVector(0,0,99)); V->AdvanceHallCourier(Courier,2.f);
 TestEqual(TEXT("Gathering takes time"),V->SupplySites[0].Stock,5);
 V->AdvanceHallCourier(Courier,2.f);
 TestEqual(TEXT("Pickup debits source"),V->SupplySites[0].Stock,2);
 TestEqual(TEXT("Worker carries three stone"),V->GolemResidents[0].CargoCount,3);
 TestEqual(TEXT("Pickup does not credit hall remotely"),V->HallSupplies.FindRef(TEXT("Stone")),0);
 const FGuid Id=Courier->GolemId;
 TestTrue(TEXT("Cargo can be saved mid trip"),V->SaveVillageState(Player));
 V->ReloadVillageState(Player); Courier=nullptr;
 for(TActorIterator<AVillageGolemCitizen> It(W);It;++It) if(It->GetOwner()==V && It->GolemId==Id) Courier=*It;
 TestEqual(TEXT("Reload keeps cargo"),V->GolemResidents[0].CargoCount,3);
 TestEqual(TEXT("Reload keeps source depletion"),V->SupplySites[0].Stock,2);
 V->WindowIndex=7; V->AdvanceHallCourier(Courier,10.f);
 TestEqual(TEXT("Rest preserves undelivered cargo"),V->GolemResidents[0].CargoCount,3);
 V->WindowIndex=1; Courier->SetActorLocation(FVector(0,-650,99)); V->AdvanceHallCourier(Courier,1.f);
 TestEqual(TEXT("Arrival credits hall"),V->HallSupplies.FindRef(TEXT("Stone")),3);
 TestEqual(TEXT("Arrival clears cargo"),V->GolemResidents[0].CargoCount,0);
 V->AdvanceHallCourier(Courier,1.f);
 TestEqual(TEXT("Deposit cannot repeat"),V->HallSupplies.FindRef(TEXT("Stone")),3);
 Courier->SetActorLocation(Fish.Location+FVector(0,0,99)); V->AdvanceHallCourier(Courier,4.f);
 TestEqual(TEXT("Next trip collects a different resource"),V->GolemResidents[0].Cargo,FName(TEXT("Fish")));
 TestEqual(TEXT("Small source is not overdrawn"),V->SupplySites[1].Stock,0);
 Courier->SetActorLocation(FVector(0,-650,99)); V->AdvanceHallCourier(Courier,1.f);
 Player->SetActorLocation(FVector(10000,0,99));
 TestFalse(TEXT("Cannot withdraw from far away"),V->WithdrawHallSupplies(Player));
 Player->SetActorLocation(FVector(0,-500,99)); Player->Gather->Stacks.Reset();
 TestTrue(TEXT("Hall interaction collects delivered supplies"),V->WithdrawHallSupplies(Player));
 TestEqual(TEXT("Stone reaches inventory once"),Player->Gather->GetCount(TEXT("Stone")),3);
 TestEqual(TEXT("Fish reaches inventory"),Player->Gather->GetCount(TEXT("Fish")),2);
 V->WithdrawHallSupplies(Player);
 TestEqual(TEXT("Empty hall cannot duplicate items"),Player->Gather->GetCount(TEXT("Stone")),3);
 V->ReloadVillageState(Player);
 TestEqual(TEXT("Withdrawn store stays empty on reload"),V->HallSupplies.FindRef(TEXT("Stone")),0);
 TestEqual(TEXT("Collected fish survives reload"),Player->Gather->GetCount(TEXT("Fish")),2);
 V->bUseGolemVillage=false; UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot,0);
 W->DestroyWorld(false); GEngine->DestroyWorldContext(W); return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FVillageProductionTest, "IsekaiVillage.Village.WorkerProduction", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FVillageProductionTest::RunTest(const FString& Parameters)
{
 const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);
 GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
 FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 auto* V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,P);
 auto* Player=W->SpawnActor<AIsekaiVillageCharacter>(FVector::ZeroVector,FRotator::ZeroRotator,P);
 V->bUseAuthoredPlots=true;V->bUseGolemVillage=true;
 V->ConstructionSaveSlot=TEXT("Automation_WorkerProduction_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);
 FTownPlot Home;Home.Id=TEXT("Home");Home.bBuilt=true;Home.Kind=ETownBuilding::House;Home.BedBonus=5;Home.BuildingClass=AStaticMeshActor::StaticClass();Home.StakeOffset=FVector(0,-500,0);
 V->AuthoredPlots={Home};
 const ETownBuilding Kinds[]={ETownBuilding::Guild,ETownBuilding::Farm,ETownBuilding::Bakery,ETownBuilding::Smith,ETownBuilding::Warehouse};
 const FName Names[]={TEXT("Hall"),TEXT("Farm"),TEXT("Bakery"),TEXT("Smith"),TEXT("Warehouse")};
 for(int32 I=0;I<5;++I){FTownPlot Job=Home;Job.Id=Names[I];Job.Kind=Kinds[I];Job.bScenery=Kinds[I]==ETownBuilding::Farm;Job.BedBonus=0;Job.Location=FVector((I+1)*3000,0,0);V->AuthoredPlots.Add(Job);}
 V->InitializeConstruction();V->WindowIndex=1;
 TestEqual(TEXT("Five job buildings hire five housed workers"),V->GolemResidents.Num(),5);
 auto Worker=[&](FName Job)->AVillageGolemCitizen*{for(TActorIterator<AVillageGolemCitizen> It(W);It;++It)if(It->GetOwner()==V && It->WorkPlot==Job)return *It;return nullptr;};
 auto Record=[&](FName Job)->FVillageGolemRecord*{return V->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R){return R.WorkPlot==Job;});};
 auto AtWork=[&](AVillageGolemCitizen* A){const auto* Plot=V->FindPlot(A->WorkPlot);A->SetActorLocation(Plot->Location+Plot->StakeOffset+Plot->StakeOffset.GetSafeNormal2D()*150.f+FVector(0,0,99));};
 const FVector Hall=FVector(3000,-650,99);
 auto* Farmer=Worker(TEXT("Farm"));auto* Baker=Worker(TEXT("Bakery"));auto* Smith=Worker(TEXT("Smith"));
 if(!Farmer||!Baker||!Smith){AddError(TEXT("Missing production worker"));V->bUseGolemVillage=false;W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return false;}
 AtWork(Baker);V->AdvanceProductionWorker(Baker,100.f);
 TestFalse(TEXT("Baker cannot produce without inputs"),Record(TEXT("Bakery"))->bHasWorkInputs);
 TestEqual(TEXT("Unfunded production waits at workplace rather than blocking hall"),Baker->GoalPlace,EVillagePlace::Bakery);
 TestEqual(TEXT("No free bread"),V->HallSupplies.FindRef(TEXT("Bread")),0);
 AtWork(Farmer);V->AdvanceProductionWorker(Farmer,19.f);
 TestEqual(TEXT("Farm batch takes twenty work seconds"),Record(TEXT("Farm"))->CargoCount,0);
 V->AdvanceProductionWorker(Farmer,1.f);
 TestEqual(TEXT("Farmer carries wheat"),Record(TEXT("Farm"))->Cargo,FName(TEXT("Wheat")));
 TestEqual(TEXT("Wheat is not credited before return"),V->HallSupplies.FindRef(TEXT("Wheat")),0);
 Farmer->SetActorLocation(Hall);V->AdvanceProductionWorker(Farmer,1.f);
 TestEqual(TEXT("Farmer deposits two wheat"),V->HallSupplies.FindRef(TEXT("Wheat")),2);
 V->HallSupplies.Add(TEXT("Wood"),2);V->HallSupplies.Add(TEXT("Stone"),2);
 Baker->SetActorLocation(Hall);V->AdvanceProductionWorker(Baker,1.f);
 TestTrue(TEXT("Baker collects ingredients at hall"),Record(TEXT("Bakery"))->bHasWorkInputs);
 TestEqual(TEXT("Wheat reserved exactly once"),V->HallSupplies.FindRef(TEXT("Wheat")),0);
 TestEqual(TEXT("Recipe uses one wood"),V->HallSupplies.FindRef(TEXT("Wood")),1);
 V->SaveVillageState(Player);V->ReloadVillageState(Player);Baker=Worker(TEXT("Bakery"));Smith=Worker(TEXT("Smith"));
 TestTrue(TEXT("Carried recipe inputs survive reload"),Record(TEXT("Bakery"))->bHasWorkInputs);
 V->WindowIndex=7;V->AdvanceProductionWorker(Baker,40.f);
 TestEqual(TEXT("Rest cannot manufacture a batch"),Record(TEXT("Bakery"))->CargoCount,0);
 TestTrue(TEXT("Rest preserves ingredients"),Record(TEXT("Bakery"))->bHasWorkInputs);
 V->WindowIndex=1;AtWork(Baker);V->AdvanceProductionWorker(Baker,20.f);
 TestEqual(TEXT("Baker makes two bread"),Record(TEXT("Bakery"))->CargoCount,2);
 Baker->SetActorLocation(Hall);V->AdvanceProductionWorker(Baker,1.f);
 TestEqual(TEXT("Bread delivered to hall"),V->HallSupplies.FindRef(TEXT("Bread")),2);
 Smith->SetActorLocation(Hall);V->AdvanceProductionWorker(Smith,1.f);AtWork(Smith);V->AdvanceProductionWorker(Smith,20.f);
 TestEqual(TEXT("Smith makes tool parts from stone and wood"),Record(TEXT("Smith"))->Cargo,FName(TEXT("ToolParts")));
 TestEqual(TEXT("Smith debits stone"),V->HallSupplies.FindRef(TEXT("Stone")),0);
 Smith->SetActorLocation(Hall);V->AdvanceProductionWorker(Smith,1.f);
 TestEqual(TEXT("Tool parts delivered to hall"),V->HallSupplies.FindRef(TEXT("ToolParts")),1);
 auto* Hauler=Worker(TEXT("Warehouse"));FVillageSupplySite Site;Site.Item=TEXT("Fish");Site.Stock=0;Site.DailyRestock=6;Site.RestockDay=1;Site.Location=FVector(19000,0,0);V->SupplySites={Site};V->DayIndex=2;
 V->AdvanceHallCourier(Hauler,0.f);
 TestEqual(TEXT("Basic supply budget refills on a new day"),V->SupplySites[0].Stock,6);
 V->SupplySites[0].Stock=1;V->AdvanceHallCourier(Hauler,0.f);
 TestEqual(TEXT("Daily refill cannot repeat within same day"),V->SupplySites[0].Stock,1);
 TestEqual(TEXT("Warehouse hauler targets source"),Hauler->Goal,Site.Location);
 V->bUseGolemVillage=false;UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot,0);W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGolemWantsTest,"IsekaiVillage.Golems.WantsAndLearning",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGolemWantsTest::RunTest(const FString& Parameters)
{
 FGolemDriveState S;const FGuid Id=FGuid::NewGuid();UGolemNeedsLibrary::Initialize(S,Id);const float Personality=S.Diligence;UGolemNeedsLibrary::Initialize(S,FGuid::NewGuid());
 TestEqual(TEXT("Personality is initialized once"),S.Diligence,Personality);
 S.Fatigue=10;S.Curiosity=100;S.Loneliness=0;S.Commitment=0;
 TestEqual(TEXT("A curious free golem chooses practice"),UGolemNeedsLibrary::ChooseActivity(S,false,true,false,false,0,false),FName(TEXT("Practice")));
 TestEqual(TEXT("An existing delivery outranks optional practice"),UGolemNeedsLibrary::ChooseActivity(S,true,true,false,true,0,false),FName(TEXT("Work")));
 S.Fatigue=95;TestEqual(TEXT("Exhaustion interrupts even a delivery"),UGolemNeedsLibrary::ChooseActivity(S,true,true,false,true,1,false),FName(TEXT("Rest")));
 S.Fatigue=60;TestEqual(TEXT("Recharge continues rather than oscillating with cargo"),UGolemNeedsLibrary::ChooseActivity(S,true,true,false,true,1,false),FName(TEXT("Rest")));
 TestEqual(TEXT("Curiosity cannot interrupt recovery before a safe recharge"),UGolemNeedsLibrary::ChooseActivity(S,false,true,false,false,0,false),FName(TEXT("Rest")));
 S.Fatigue=10;S.Loneliness=100;S.Curiosity=0;S.Commitment=0;S.Activity=TEXT("Work");
 TestEqual(TEXT("Company can outweigh routine work"),UGolemNeedsLibrary::ChooseActivity(S,true,false,true,false,0,false),FName(TEXT("Socialize")));
 FGolemDriveState Learner,Other;
 TestFalse(TEXT("Failed actions do not teach"),UGolemNeedsLibrary::RecordPractice(Learner,TEXT("Guard"),5,false));
 TestFalse(TEXT("Unknown practice domains do not teach"),UGolemNeedsLibrary::RecordPractice(Learner,TEXT("Spam"),5));
 TestFalse(TEXT("Negative effort does not teach"),UGolemNeedsLibrary::RecordPractice(Learner,TEXT("Guard"),-5));
 for(int32 N=0;N<24;++N)UGolemNeedsLibrary::RecordPractice(Learner,TEXT("Guard"),5);
 TestTrue(TEXT("Guard practice unlocks Guard Stance"),Learner.Skills.Contains(TEXT("GuardStance")));
 TestTrue(TEXT("Skills belong to the practising individual"),Other.Skills.IsEmpty());
 for(int32 N=0;N<40;++N)UGolemNeedsLibrary::RecordPractice(Learner,TEXT("Guard"),5);
 TestEqual(TEXT("One unlock despite repeated practice"),Learner.Skills.Num(),1);
 TestTrue(TEXT("Continued effort unlocks a passive"),Learner.Passives.Contains(TEXT("EnduringCore")));
 TestEqual(TEXT("Enduring core has a real fatigue benefit"),UGolemNeedsLibrary::FatigueMultiplier(Learner),.75f);
 FGolemDriveState LongFrame;UGolemNeedsLibrary::RecordPractice(LongFrame,TEXT("Magic"),100000.f);
 TestEqual(TEXT("One huge event cannot unlock an entire skill"),LongFrame.Practice.FindRef(TEXT("Magic")),5.f);
 return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FAdventurerOrganicTest,"IsekaiVillage.Golems.AdventurerPracticePersistence",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FAdventurerOrganicTest::RunTest(const FString& Parameters)
{
 const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
 FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 auto* V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,P);auto* Player=W->SpawnActor<AIsekaiVillageCharacter>(FVector(0,3000,200),FRotator::ZeroRotator,P);
 V->bUseAuthoredPlots=true;V->bUseGolemVillage=true;V->bUseOrganicGolemNeeds=true;V->ConstructionSaveSlot=TEXT("Automation_Organic_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);
 FTownPlot Home;Home.Id=TEXT("Home");Home.Kind=ETownBuilding::House;Home.BedBonus=4;Home.bBuilt=true;Home.BuildingClass=AStaticMeshActor::StaticClass();Home.StakeOffset=FVector(0,-500,0);
 FTownPlot Hall=Home;Hall.Id=TEXT("Hall");Hall.Kind=ETownBuilding::Guild;Hall.BedBonus=0;Hall.Location=FVector(3000,0,0);
 FTownPlot Yard=Hall;Yard.Id=TEXT("Yard");Yard.Kind=ETownBuilding::Training;Yard.Location=FVector(1500,0,0);
 V->AuthoredPlots={Home,Hall,Yard};V->InitializeConstruction();V->SaveVillageState(Player);
 Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("Student")));Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("Peer")));
 UArteDataAsset* Arte=NewObject<UArteDataAsset>(Player);Player->PartyReserve->LearnedArteDefinitions.Add(TEXT("GuardStance"),Arte);
 V->ReconcileGolemPopulation();TestEqual(TEXT("Two housed roster members join the civilian worker"),V->GolemResidents.Num(),3);
 const FName Adventurer=Player->PartyReserve->Reserve[0].AdventurerID;
 auto Record=[&]()->FVillageGolemRecord*{return V->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R){return R.AdventurerId==Adventurer;});};
 AVillageGolemCitizen* A=nullptr;for(TActorIterator<AVillageGolemCitizen> It(W);It;++It)if(It->GolemId==Record()->Id)A=*It;
 if(!TestNotNull(TEXT("Reserve member has a village actor"),A)){V->bUseGolemVillage=false;W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return false;}
 Record()->Drives.Interest=TEXT("Guard");Record()->Drives.Curiosity=95;Record()->Drives.Fatigue=0;Record()->Drives.Loneliness=0;Record()->Drives.Commitment=0;
 V->AdvanceGolemNeeds(A,1.f);TestEqual(TEXT("Adventurer independently chooses the training yard"),Record()->Drives.Activity,FName(TEXT("Practice")));
 TestEqual(TEXT("No practice credit while travelling"),Record()->Drives.Practice.FindRef(TEXT("Guard")),0.f);
 A->SetActorLocation(A->Goal+FVector(0,0,99));for(int32 I=0;I<125;++I)V->AdvanceGolemNeeds(A,1.f);
 TestTrue(TEXT("Physical practice teaches a skill"),Record()->Drives.Skills.Contains(TEXT("GuardStance")));
 TestTrue(TEXT("Learned definitions enter existing known-artes list"),Player->PartyReserve->Reserve[0].KnownArtes.Contains(Arte));
 TestTrue(TEXT("Peer does not inherit someone else's unlock"),Player->PartyReserve->Reserve[1].Drives.Skills.IsEmpty());
 const FGuid StableId=Record()->Id;const float Practice=Record()->Drives.Practice.FindRef(TEXT("Guard"));
 Record()->Drives.Fatigue=95;V->AdvanceGolemNeeds(A,1.f);
 TestEqual(TEXT("Exhausted adventurer wants home"),Record()->Drives.Activity,FName(TEXT("Rest")));
 TestTrue(TEXT("Recharge does not happen while walking home"),Record()->Drives.Fatigue>=95);
 A->SetActorLocation(A->Goal+FVector(0,0,99));V->AdvanceGolemNeeds(A,1.f);
 TestTrue(TEXT("Arriving home restores energy"),Record()->Drives.Fatigue<95);
 TestEqual(TEXT("Recharge gives no practice credit"),Record()->Drives.Practice.FindRef(TEXT("Guard")),Practice);
 V->SaveVillageState(Player);V->ReloadVillageState(Player);
 TestEqual(TEXT("Adventurer identity survives reload"),Record()->Id,StableId);
 TestEqual(TEXT("Practice progress survives reload"),Record()->Drives.Practice.FindRef(TEXT("Guard")),Practice);
 TestTrue(TEXT("Personal unlock survives reload"),Player->PartyReserve->Reserve[0].Drives.Skills.Contains(TEXT("GuardStance")));
 TestTrue(TEXT("Personality survives reload"),Record()->Drives.bInitialized);
 V->bUseGolemVillage=false;UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot,0);W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return true;
}
#endif
