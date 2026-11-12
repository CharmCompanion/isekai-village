#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "Engine/StaticMeshActor.h"
#include "EngineUtils.h"
#include "VillageRuntime.h"
#include "TownPlot.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "Kismet/GameplayStatics.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTownConstructionTest, "IsekaiVillage.Construction.AuthoredPlots", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FTownConstructionTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);
	FActorSpawnParameters P; P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
	AVillageRuntime* V = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector(0,0,500), FRotator::ZeroRotator, P);
	if (!TestNotNull(TEXT("Player created"), Player) || !TestNotNull(TEXT("Runtime created"), V)) { W->DestroyWorld(false); return false; }
	V->bUseAuthoredPlots = true;
	V->ConstructionSaveSlot = TEXT("Automation_ElRuhn_") + FGuid::NewGuid().ToString(EGuidFormats::Digits);
	FTownPlot House; House.Id=TEXT("SkyHouse01"); House.Location=FVector(1000,2000,100); House.StakeOffset=FVector(0,-300,0); House.WoodCost=8; House.BuildingClass=AStaticMeshActor::StaticClass(); House.BedBonus=2;
	FTownPlot Bank=House; Bank.Id=TEXT("SkyBank01"); Bank.Kind=ETownBuilding::Bank; Bank.Era=ETownEra::LargeTown; Bank.WoodCost=10; Bank.IronCost=4;
	V->AuthoredPlots={House,Bank,House}; // Duplicate IDs must never double-charge or double-spawn.
	V->InitializeConstruction(); TestEqual(TEXT("Unique authored IDs"), V->Plots.Num(), 2);
	Player->Gather->Stacks.Reset(); V->TryBuildPlot(House.Id, Player);
	Player->SphereBuildSpeed=0;
	TestFalse(TEXT("Insufficient resources leave plot unbuilt"),V->FindPlot(House.Id)->bBuilt);
	Player->Gather->AddItem(TEXT("Wood"),30); Player->Gather->AddItem(TEXT("Iron"),8);
	V->TryBuildPlot(Bank.Id,Player); TestFalse(TEXT("Era gate enforced"),V->FindPlot(Bank.Id)->bBuilt); TestEqual(TEXT("Locked plot charges nothing"),Player->Gather->GetCount(TEXT("Wood")),30);
	V->TryBuildPlot(House.Id,Player); TestTrue(TEXT("House built"),V->FindPlot(House.Id)->bBuilt); TestEqual(TEXT("House exact cost"),Player->Gather->GetCount(TEXT("Wood")),22);
	int32 Visuals=0;
	for(TActorIterator<AArchitectStake> It(W);It;++It) if(It->PlotId==House.Id) { TestTrue(TEXT("Authored building spawned"),IsValid(It->BuiltVisual)); TestEqual(TEXT("Interaction offset kept"),It->GetActorLocation(),House.Location+House.StakeOffset); ++Visuals; }
	TestEqual(TEXT("One stake per plot"),Visuals,1);
	V->InitializeConstruction(); TestTrue(TEXT("Purchase survives save reload"),V->FindPlot(House.Id)->bBuilt);
	V->TryBuildPlot(House.Id,Player); TestTrue(TEXT("House loft upgrades"),V->FindPlot(House.Id)->bUpgraded); TestEqual(TEXT("Loft exact cost"),Player->Gather->GetCount(TEXT("Wood")),16);
	V->TryBuildPlot(House.Id,Player); TestEqual(TEXT("Repeated completed interaction charges nothing"),Player->Gather->GetCount(TEXT("Wood")),16);
	V->InitializeConstruction(); TestEqual(TEXT("Saved loft adds bed only once"),V->FindPlot(House.Id)->BedBonus,3);
	// A land parcel's use comes from the player's choice, never its initial placeholder kind.
	FTownPlot Land=House; Land.Id=TEXT("UnassignedLand"); Land.bFlexibleUse=true; Land.DisplayName=FText::FromString(TEXT("Unassigned land"));
	Land.BuildingClass=nullptr;
	V->AuthoredPlots={Land}; V->BuildingCatalog={House,Bank};
	V->InitializeConstruction();
	TestTrue(TEXT("Select catalogue bank"),V->SelectBuilding(Bank.Id));
	V->TryBuildPlot(Land.Id,Player);
	TestFalse(TEXT("Locked selection leaves land unbuilt"),V->FindPlot(Land.Id)->bBuilt);
	TestTrue(TEXT("Locked selection leaves land unassigned"),V->FindPlot(Land.Id)->CatalogId.IsNone());
	const int32 BeforeCancel=Player->Gather->GetCount(TEXT("Wood"));
	V->CancelBuildingPlacement();
	TestEqual(TEXT("Cancelling spends nothing"),Player->Gather->GetCount(TEXT("Wood")),BeforeCancel);
	V->Trust=60; Player->UnlockedSphereNodes={TEXT("A"),TEXT("B"),TEXT("C"),TEXT("D")};
	V->SelectBuilding(Bank.Id); V->PlacementTurns=1; V->TryBuildPlot(Land.Id,Player);
	TestTrue(TEXT("Player choice assigns bank use"),V->FindPlot(Land.Id)->Kind==ETownBuilding::Bank && V->FindPlot(Land.Id)->bBuilt);
	TestEqual(TEXT("Chosen bank charges bank price"),Player->Gather->GetCount(TEXT("Wood")),BeforeCancel-10);
	V->InitializeConstruction();
	TestTrue(TEXT("Chosen use survives reload"),V->FindPlot(Land.Id)->Kind==ETownBuilding::Bank && V->HasBuilding(ETownBuilding::Bank));
	TestEqual(TEXT("Saved catalogue selection"),V->FindPlot(Land.Id)->CatalogId,Bank.Id);
	TestEqual(TEXT("Saved orientation"),V->FindPlot(Land.Id)->PlacementTurns,1);
	TestTrue(TEXT("Saved rotation restored"),FMath::IsNearlyEqual(V->FindPlot(Land.Id)->BuildingRotation.Yaw,90.0));
	V->SelectBuilding(House.Id); V->TryBuildPlot(Land.Id,Player);
	TestTrue(TEXT("Occupied land cannot be overwritten"),V->FindPlot(Land.Id)->Kind==ETownBuilding::Bank);
	TestEqual(TEXT("Occupied land charges nothing"),Player->Gather->GetCount(TEXT("Wood")),BeforeCancel-10);
	FTownPlot Land2=Land, Land3=Land; Land2.Id=TEXT("SecondParcel"); Land3.Id=TEXT("ThirdParcel");
	FTownPlot Deed=House; Deed.Id=TEXT("InheritedHouse"); Deed.WoodCost=0; Deed.bUniqueBuilding=true;
	V->AuthoredPlots={Land,Land2,Land3}; V->BuildingCatalog.Add(Deed);
	V->InitializeConstruction();
	TestTrue(TEXT("Vacant parcel has no building use"),V->FindPlot(Land2.Id)->Kind==ETownBuilding::Unassigned);
	V->SelectBuilding(Deed.Id); V->TryBuildPlot(Land2.Id,Player);
	TestTrue(TEXT("Inheritance placed on chosen parcel"),V->FindPlot(Land2.Id)->CatalogId==Deed.Id);
	TestEqual(TEXT("Inherited deed costs no wood"),Player->Gather->GetCount(TEXT("Wood")),BeforeCancel-10);
	V->InitializeConstruction(); V->SelectBuilding(Deed.Id); V->TryBuildPlot(Land3.Id,Player);
	TestFalse(TEXT("Unique inheritance cannot be claimed twice"),V->FindPlot(Land3.Id)->bBuilt);
	UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot,0);
	W->DestroyWorld(false); return true;
}
#endif
