// Copyright Epic Games, Inc. All Rights Reserved.

#include "IslandTerrainActor.h"
#include "UObject/ConstructorHelpers.h"
#include "Materials/MaterialInstanceDynamic.h"

AIslandTerrainActor::AIslandTerrainActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	// 1. Surrounding Ocean Water Plane
	OceanWaterPlane = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("OceanWaterPlane"));
	OceanWaterPlane->SetupAttachment(RootComponent);
	OceanWaterPlane->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
	OceanWaterPlane->SetRelativeScale3D(FVector(400.0f, 400.0f, 1.0f)); // 4km ocean expanse
	OceanWaterPlane->SetCollisionProfileName(TEXT("OverlapAll"));

	// 2. Main Organic Island Landmass (Middle Terraced Plateau)
	IslandLandmassMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("IslandLandmassMesh"));
	IslandLandmassMesh->SetupAttachment(RootComponent);
	IslandLandmassMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -40.0f));
	IslandLandmassMesh->SetRelativeScale3D(FVector(75.0f, 65.0f, 2.5f)); // ~300m organic body
	IslandLandmassMesh->SetCollisionProfileName(TEXT("BlockAll"));

	// 3. South Sandy Beach Cove (Gentle slope into the water)
	BeachCoveMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BeachCoveMesh"));
	BeachCoveMesh->SetupAttachment(RootComponent);
	BeachCoveMesh->SetRelativeLocation(FVector(-2200.0f, -400.0f, -15.0f));
	BeachCoveMesh->SetRelativeRotation(FRotator(2.5f, -15.0f, 0.0f));
	BeachCoveMesh->SetRelativeScale3D(FVector(35.0f, 38.0f, 0.8f));
	BeachCoveMesh->SetCollisionProfileName(TEXT("BlockAll"));

	// 4. Elevated Scenic Tower Plateau (North / Peak for player's tower)
	TowerPlateauMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("TowerPlateauMesh"));
	TowerPlateauMesh->SetupAttachment(RootComponent);
	TowerPlateauMesh->SetRelativeLocation(TowerPlateauLocation);
	TowerPlateauMesh->SetRelativeRotation(FRotator(0.0f, 10.0f, 0.0f));
	TowerPlateauMesh->SetRelativeScale3D(FVector(32.0f, 28.0f, 4.2f)); // Leveled high plateau
	TowerPlateauMesh->SetCollisionProfileName(TEXT("BlockAll"));

	// Load Engine Meshes (Cylinder / Cube / Plane)
	static ConstructorHelpers::FObjectFinder<UStaticMesh> CylMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (CylMesh.Succeeded())
	{
		IslandLandmassMesh->SetStaticMesh(CylMesh.Object);
		BeachCoveMesh->SetStaticMesh(CylMesh.Object);
		TowerPlateauMesh->SetStaticMesh(CylMesh.Object);
	}

	static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(TEXT("/Engine/BasicShapes/Plane.Plane"));
	if (PlaneMesh.Succeeded())
	{
		OceanWaterPlane->SetStaticMesh(PlaneMesh.Object);
	}
}

void AIslandTerrainActor::BeginPlay()
{
	Super::BeginPlay();
	SetupIslandMaterials();
}

void AIslandTerrainActor::SetupIslandMaterials()
{
	UMaterialInterface* BaseMat = Cast<UMaterialInterface>(StaticLoadObject(UMaterialInterface::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")));
	if (!BaseMat) return;

	// 1. Ocean Water Material (Vibrant Tropical Turquoise)
	if (OceanWaterPlane)
	{
		UMaterialInstanceDynamic* WaterMat = OceanWaterPlane->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat);
		if (WaterMat)
		{
			WaterMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.04f, 0.45f, 0.65f, 0.82f));
		}
	}

	// 2. Sandy Beach Material (Warm Golden Sand)
	if (BeachCoveMesh)
	{
		UMaterialInstanceDynamic* BeachMat = BeachCoveMesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat);
		if (BeachMat)
		{
			BeachMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.88f, 0.78f, 0.52f, 1.0f));
		}
	}

	// 3. Lush Green Island Grass Material
	if (IslandLandmassMesh)
	{
		UMaterialInstanceDynamic* GrassMat = IslandLandmassMesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat);
		if (GrassMat)
		{
			GrassMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.24f, 0.62f, 0.18f, 1.0f));
		}
	}

	// 4. Tower Plateau Surface (Clean stone / terrace grass)
	if (TowerPlateauMesh)
	{
		UMaterialInstanceDynamic* PlateauMat = TowerPlateauMesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat);
		if (PlateauMat)
		{
			PlateauMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.32f, 0.68f, 0.22f, 1.0f));
		}
	}
}
