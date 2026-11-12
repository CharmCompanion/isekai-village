// Copyright Epic Games, Inc. All Rights Reserved.

#include "OverworldGameMode.h"
#include "OverworldCharacter.h"
#include "OverworldHUD.h"
#include "MeshTerrainBuilder.h"
#include "IsekaiVillageTypes.h"
#include "Engine/TargetPoint.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

AOverworldGameMode::AOverworldGameMode()
{
	DefaultPawnClass = AOverworldCharacter::StaticClass();
	HUDClass = AOverworldHUD::StaticClass();
}

void AOverworldGameMode::BeginPlay()
{
	Super::BeginPlay();

	// Ensure bounded exposure so Lumen cached lighting never clips to pitch black
	bool bHasPostProcess = false;
	for (TActorIterator<APostProcessVolume> It(GetWorld()); It; ++It)
	{
		APostProcessVolume* PP = *It;
		if (PP && PP->bUnbound)
		{
			bHasPostProcess = true;
			PP->Settings.bOverride_AutoExposureMethod = true;
			PP->Settings.AutoExposureMethod = EAutoExposureMethod::AEM_Histogram;
			PP->Settings.bOverride_AutoExposureMinBrightness = true;
			PP->Settings.AutoExposureMinBrightness = 0.5f;
			PP->Settings.bOverride_AutoExposureMaxBrightness = true;
			PP->Settings.AutoExposureMaxBrightness = 3.0f;
			break;
		}
	}

	if (!bHasPostProcess && GetWorld())
	{
		FActorSpawnParameters SpawnParams;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		if (APostProcessVolume* PP = GetWorld()->SpawnActor<APostProcessVolume>(APostProcessVolume::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams))
		{
			PP->bUnbound = true;
			PP->Settings.bOverride_AutoExposureMethod = true;
			PP->Settings.AutoExposureMethod = EAutoExposureMethod::AEM_Histogram;
			PP->Settings.bOverride_AutoExposureMinBrightness = true;
			PP->Settings.AutoExposureMinBrightness = 0.5f;
			PP->Settings.bOverride_AutoExposureMaxBrightness = true;
			PP->Settings.AutoExposureMaxBrightness = 3.0f;
		}
	}

	// Set up the stylized mesh terrain for the overworld map (loads blockout heightmap)
	SpawnOverworldTerrain();
}

void AOverworldGameMode::SpawnOverworldTerrain()
{
	UWorld* World = GetWorld();
	if (!World) return;

	// Avoid double-spawning if a level designer already placed one
	for (TActorIterator<AMeshTerrainBuilder> It(World); It; ++It)
	{
		return;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AMeshTerrainBuilder* Terrain = World->SpawnActor<AMeshTerrainBuilder>(AMeshTerrainBuilder::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);
	if (Terrain)
	{
		Terrain->Biome = ETerrainBiome::Plains;
		Terrain->TerrainSize = 20000.0f;
		Terrain->TerrainResolution = 256;
		Terrain->HeightScale = 250.0f;
		Terrain->HeightOffset = -20.0f;
		Terrain->bGenerateWater = true;
		Terrain->WaterLevel = 5.0f;
		Terrain->bFlatArena = false;
		Terrain->bLoadFromR16File = true;
		Terrain->HeightmapPath = TEXT("IsekaiVillage/WorldBlockout/TerrainSource/IV_Terrain_Blockout_1009.r16");
		Terrain->TerrainMaterialPath = TEXT("/Game/SoStylized/Materials/M_StylizedBasic.M_StylizedBasic");
		Terrain->GenerateFromFileOrDefault();
	}
}