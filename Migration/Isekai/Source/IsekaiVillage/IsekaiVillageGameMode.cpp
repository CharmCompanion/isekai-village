// Copyright Epic Games, Inc. All Rights Reserved.

#include "IsekaiVillageGameMode.h"
#include "IsekaiVillageCharacter.h"
#include "IsekaiVillageHUD.h"
#include "MeshTerrainBuilder.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

AIsekaiVillageGameMode::AIsekaiVillageGameMode()
{
	DefaultPawnClass = AIsekaiVillageCharacter::StaticClass();
	HUDClass = AIsekaiVillageHUD::StaticClass();
}

void AIsekaiVillageGameMode::BeginPlay()
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

	// Set up the stylized terrain for the village map
	SpawnVillageTerrain();

	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		if (AIsekaiVillageHUD* HUD = Cast<AIsekaiVillageHUD>(PC->GetHUD()))
		{
			HUD->ShowLocationBanner(
				FText::FromString(TEXT("Isekai Village")),
				FText::FromString(TEXT("The Haven of Rebirth")),
				4.5f
			);
		}
	}
}

void AIsekaiVillageGameMode::SpawnVillageTerrain()
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
		Terrain->TerrainSize = 6000.0f;
		Terrain->TerrainResolution = 128;
		Terrain->HeightScale = 90.0f;
		Terrain->HeightOffset = 0.0f;
		Terrain->bGenerateWater = false;
		Terrain->bFlatArena = false;
		Terrain->bLoadFromR16File = false;
		Terrain->TerrainMaterialPath = TEXT("/Game/SoStylized/Materials/M_StylizedBasic.M_StylizedBasic");
		Terrain->GenerateTerrain();
	}
}