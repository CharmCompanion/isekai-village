// Copyright Epic Games, Inc. All Rights Reserved.

#include "OverworldGameMode.h"
#include "OverworldCharacter.h"
#include "IsekaiVillageHUD.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"

AOverworldGameMode::AOverworldGameMode()
{
	DefaultPawnClass = AOverworldCharacter::StaticClass();
	HUDClass = AIsekaiVillageHUD::StaticClass();
}

void AOverworldGameMode::BeginPlay()
{
	Super::BeginPlay();

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
}
