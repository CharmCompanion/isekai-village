// Copyright Epic Games, Inc. All Rights Reserved.
#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "DebrisActor.h"
#include "BuildPiece.h"
#include "BuildEditComponent.h"
#include "RoomVolume.h"
#include "LinchpinProp.h"
#include "VillageRuntime.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "ProceduralMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FModularDebrisSalvageTest, "IsekaiVillage.Building.DebrisSalvage", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FModularDebrisSalvageTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	FActorSpawnParameters P; P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	ADebrisActor* Rubble = W->SpawnActor<ADebrisActor>(FVector(100.0f, 0.0f, 0.0f), FRotator::ZeroRotator, P);
	if (!TestNotNull(TEXT("Player exists"), Player) || !TestNotNull(TEXT("Debris exists"), Rubble))
	{
		W->DestroyWorld(false);
		return false;
	}

	Rubble->SetupDebris(EDebrisType::StoneRubble);
	TestEqual(TEXT("Initial rubble hits"), Rubble->HitsRemaining, 3);
	TestEqual(TEXT("Rubble primary loot is Stone"), Rubble->GetPrimaryLootId(), FName(TEXT("Stone")));

	// First two strikes
	TestTrue(TEXT("Strike 1 survives"), Rubble->TrySalvage(Player));
	TestEqual(TEXT("Hits after strike 1"), Rubble->HitsRemaining, 2);
	TestTrue(TEXT("Strike 2 survives"), Rubble->TrySalvage(Player));
	TestEqual(TEXT("Hits after strike 2"), Rubble->HitsRemaining, 1);

	// Final strike clears debris and grants loot
	TestTrue(TEXT("Strike 3 clears"), Rubble->TrySalvage(Player));
	TestTrue(TEXT("Rubble marked pending kill"), !IsValid(Rubble) || Rubble->IsActorBeingDestroyed());
	TestTrue(TEXT("Player received Stone"), Player->Gather->GetCount(TEXT("Stone")) >= 6);

	// Test RuinedStructure multi-drop bundle
	ADebrisActor* Ruin = W->SpawnActor<ADebrisActor>(FVector(250.0f, 0.0f, 0.0f), FRotator::ZeroRotator, P);
	Ruin->SetupDebris(EDebrisType::RuinedStructure);
	TestEqual(TEXT("Ruined structure hits"), Ruin->HitsRemaining, 5);
	while (Ruin->HitsRemaining > 1)
	{
		Ruin->TrySalvage(Player);
	}
	Ruin->TrySalvage(Player);
	TestTrue(TEXT("Player received Wood from ruin"), Player->Gather->GetCount(TEXT("Wood")) >= 6);
	TestTrue(TEXT("Player received Iron from ruin"), Player->Gather->GetCount(TEXT("Iron")) >= 3);

	W->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FModularBuildPieceGeometryTest, "IsekaiVillage.Building.BuildPieceGeometry", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FModularBuildPieceGeometryTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	FActorSpawnParameters P; P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	ABuildPiece* WallPiece = W->SpawnActor<ABuildPiece>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	if (!TestNotNull(TEXT("Wall piece spawned"), WallPiece))
	{
		W->DestroyWorld(false);
		return false;
	}

	WallPiece->PieceType = EBuildPieceType::Wall;
	WallPiece->MaterialConfig.ExteriorMaterial = EBuildMaterialStyle::FieldStone;
	WallPiece->MaterialConfig.InteriorMaterial = EBuildMaterialStyle::WallpaperStripes;
	WallPiece->MaterialConfig.TrimMaterial = EBuildMaterialStyle::WoodPlank;
	WallPiece->RebuildMesh();

	// Verify multi-section mesh generation (Section 0 = Exterior, Section 1 = Interior, Section 2 = Trim)
	TestEqual(TEXT("Wall has 3 procedural mesh sections"), WallPiece->Mesh->GetNumSections(), 3);

	// Test Wall Styles
	WallPiece->SetWallStyle(EBuildWallStyle::Diagonal45);
	TestEqual(TEXT("Wall style is Diagonal45"), WallPiece->WallStyle, EBuildWallStyle::Diagonal45);
	TestTrue(TEXT("Diagonal wall has sections"), WallPiece->Mesh->GetNumSections() >= 2);

	WallPiece->SetWallStyle(EBuildWallStyle::CurvedArc);
	TestEqual(TEXT("Wall style is CurvedArc"), WallPiece->WallStyle, EBuildWallStyle::CurvedArc);
	TestTrue(TEXT("Curved wall has sections"), WallPiece->Mesh->GetNumSections() >= 2);

	// Test Sub-grid quadrant removal
	WallPiece->PieceType = EBuildPieceType::Floor;
	WallPiece->RebuildMesh();
	TestTrue(TEXT("Floor initially has all 4 quadrants"), WallPiece->IsQuadrantActive(0) && WallPiece->IsQuadrantActive(1) && WallPiece->IsQuadrantActive(2) && WallPiece->IsQuadrantActive(3));
	WallPiece->ToggleQuadrant(0);
	TestFalse(TEXT("Quadrant 0 removed for stair opening"), WallPiece->IsQuadrantActive(0));
	TestTrue(TEXT("Quadrant 1 still present"), WallPiece->IsQuadrantActive(1));

	// Test Scale Multiplier
	WallPiece->SetScaleMultiplier(FVector(2.0f, 2.0f, 1.5f));
	TestEqual(TEXT("ScaleMultiplier X updated"), (float)WallPiece->ScaleMultiplier.X, 2.0f);
	TestEqual(TEXT("ScaleMultiplier Z updated"), (float)WallPiece->ScaleMultiplier.Z, 1.5f);

	// Test Snap Points
	const TArray<FVector> Snaps = WallPiece->GetSnapPoints();
	TestTrue(TEXT("Snap points generated"), Snaps.Num() >= 9);

	// Test FindBestSnap
	ABuildPiece* AdjacentPiece = W->SpawnActor<ABuildPiece>(FVector(390.0f, 0.0f, 0.0f), FRotator::ZeroRotator, P);
	AdjacentPiece->PieceType = EBuildPieceType::Floor;
	AdjacentPiece->SetScaleMultiplier(FVector(2.0f, 2.0f, 1.5f));
	AdjacentPiece->RebuildMesh();

	FVector OutSnapLoc;
	FRotator OutSnapRot;
	const bool bSnapped = ABuildPiece::FindBestSnap(AdjacentPiece, { WallPiece }, 150.0f, OutSnapLoc, OutSnapRot);
	TestTrue(TEXT("Magnetic snap aligned successfully"), bSnapped);

	W->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FModularRoomLinchpinWorkerTest, "IsekaiVillage.Building.RoomLinchpinWorker", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FModularRoomLinchpinWorkerTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	FActorSpawnParameters P; P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AVillageRuntime* Village = W->SpawnActor<AVillageRuntime>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	ARoomVolume* Room = W->SpawnActor<ARoomVolume>(FVector(1000.0f, 0.0f, 0.0f), FRotator::ZeroRotator, P);
	if (!TestNotNull(TEXT("Village spawned"), Village) || !TestNotNull(TEXT("Room spawned"), Room))
	{
		W->DestroyWorld(false);
		return false;
	}

	Village->bUseGolemVillage = true;
	Room->BeginPlay();
	TestEqual(TEXT("Empty room initially EmptyHall"), Room->CurrentFunction, ERoomFunction::EmptyHall);

	// Place linchpin props: Forge + Anvil
	ALinchpinProp* Forge = W->SpawnActor<ALinchpinProp>(FVector(1000.0f, 50.0f, 20.0f), FRotator::ZeroRotator, P);
	Forge->LinchpinTag = TEXT("Forge");
	ALinchpinProp* Anvil = W->SpawnActor<ALinchpinProp>(FVector(1000.0f, -50.0f, 20.0f), FRotator::ZeroRotator, P);
	Anvil->LinchpinTag = TEXT("Anvil");

	// Trigger room classification scan
	Room->RefreshFunction();
	TestEqual(TEXT("Room recognized as Blacksmith"), Room->CurrentFunction, ERoomFunction::Blacksmith);

	// Verify dynamic registration with AVillageRuntime
	TestTrue(TEXT("Room registered in Village DynamicRooms"), Village->DynamicRooms.Contains(Room));

	// Reconcile golem population and check workplace registration
	Village->ReconcileGolemPopulation();

	W->DestroyWorld(false);
	return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FBuildTemplateAndFreeCamTest, "IsekaiVillage.Building.TemplateAndFreeCam", EAutomationTestFlags::EditorContext | EAutomationTestFlags::EngineFilter)
bool FBuildTemplateAndFreeCamTest::RunTest(const FString& Parameters)
{
	const UWorld::InitializationValues IV = UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
	UWorld* W = UWorld::CreateWorld(EWorldType::Game, false, NAME_None, nullptr, true, ERHIFeatureLevel::Num, &IV);
	FActorSpawnParameters P;
	P.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AIsekaiVillageCharacter* Player = W->SpawnActor<AIsekaiVillageCharacter>(FVector::ZeroVector, FRotator::ZeroRotator, P);
	ABuildPiece* WallA = W->SpawnActor<ABuildPiece>(FVector(0.0f, 0.0f, 0.0f), FRotator(0.0f, 90.0f, 0.0f), P);
	ABuildPiece* WallB = W->SpawnActor<ABuildPiece>(FVector(400.0f, 0.0f, 0.0f), FRotator::ZeroRotator, P);
	ALinchpinProp* Anvil = W->SpawnActor<ALinchpinProp>(FVector(200.0f, 80.0f, 0.0f), FRotator::ZeroRotator, P);
	if (!TestNotNull(TEXT("Player"), Player) || !TestNotNull(TEXT("Wall A"), WallA) || !TestNotNull(TEXT("Wall B"), WallB) || !TestNotNull(TEXT("Anvil"), Anvil) || !TestNotNull(TEXT("Build edit"), Player->BuildEdit.Get()))
	{
		W->DestroyWorld(false);
		return false;
	}

	WallA->PieceType = EBuildPieceType::Wall;
	WallA->WallStyle = EBuildWallStyle::CurvedArc;
	WallA->SectionMask = 0x05;
	WallA->ScaleMultiplier = FVector(2.0f, 2.0f, 1.0f);
	WallB->PieceType = EBuildPieceType::Floor;
	Anvil->SetupProp(TEXT("Anvil"));

	const FVector Start = Player->GetActorLocation();
	Player->SetFreeBuildCam(true);
	TestTrue(TEXT("Free cam is on"), Player->bFreeBuildCam);
	TestEqual(TEXT("Movement is flying"), static_cast<int32>(Player->GetCharacterMovement()->MovementMode), static_cast<int32>(MOVE_Flying));
	TestEqual(TEXT("Capsule ignores the island"), static_cast<int32>(Player->GetCapsuleComponent()->GetCollisionEnabled()), static_cast<int32>(ECollisionEnabled::NoCollision));
	Player->SetActorLocation(Start + FVector(0.0f, 0.0f, 5000.0f));
	Player->SetFreeBuildCam(false);
	TestFalse(TEXT("Free cam is off"), Player->bFreeBuildCam);
	TestEqual(TEXT("Movement walks again"), static_cast<int32>(Player->GetCharacterMovement()->MovementMode), static_cast<int32>(MOVE_Walking));
	TestTrue(TEXT("No ground returns to the start"), Player->GetActorLocation().Equals(Start, 5.0f));

	UBuildEditComponent* Edit = Player->BuildEdit;
	Edit->ToggleSelectionActor(WallA);
	Edit->ToggleSelectionActor(WallB);
	Edit->ToggleSelectionActor(Anvil);
	TestEqual(TEXT("Three parts selected"), Edit->GetTemplateSelectionCount(), 3);
	const FString Saved = Edit->SaveTemplateNamed(TEXT("AutomationProbe_DeleteMe"));
	TestEqual(TEXT("Template file saved"), Saved, FString(TEXT("AutomationProbe_DeleteMe")));

	Edit->LoadedTemplates.Reset();
	Edit->ReloadBuildTemplates();
	const int32 Spawned = Edit->StampTemplateNamed(TEXT("AutomationProbe_DeleteMe"), FVector(10000.0f, 0.0f, 0.0f), 0.0f);
	TestEqual(TEXT("Stamp spawns every part"), Spawned, 3);

	ABuildPiece* CopyA = nullptr;
	for (TActorIterator<ABuildPiece> It(W); It; ++It)
	{
		if (FVector::DistSquared(It->GetActorLocation(), FVector(9800.0f, -26.6f, 0.0f)) < FMath::Square(30.0f) ||
			FMath::IsNearlyEqual(It->GetActorLocation().X, 9800.0f, 1.0f))
		{
			CopyA = *It;
		}
	}
	TestNotNull(TEXT("Copied wall exists"), CopyA);
	if (CopyA)
	{
		TestEqual(TEXT("Copied wall keeps its arc"), CopyA->WallStyle, EBuildWallStyle::CurvedArc);
		TestEqual(TEXT("Copied wall keeps its mask"), CopyA->SectionMask, static_cast<uint8>(0x05));
		TestTrue(TEXT("Copied wall keeps its scale"), CopyA->ScaleMultiplier.Equals(FVector(2.0f, 2.0f, 1.0f)));
		TestTrue(TEXT("Copied wall keeps its yaw"), FMath::IsNearlyEqual(CopyA->GetActorRotation().Yaw, 90.0f, 0.1f));
	}

	bool bFoundAnvil = false;
	for (TActorIterator<ALinchpinProp> It(W); It; ++It)
	{
		if (It->GetActorLocation().X > 5000.0f && It->LinchpinTag == TEXT("Anvil"))
		{
			bFoundAnvil = true;
		}
	}
	TestTrue(TEXT("Copied anvil keeps its tag"), bFoundAnvil);

	const FString ProbePath = FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("BuildTemplates"), TEXT("AutomationProbe_DeleteMe.json"));
	IFileManager::Get().Delete(*ProbePath);
	W->DestroyWorld(false);
	return true;
}
#endif
