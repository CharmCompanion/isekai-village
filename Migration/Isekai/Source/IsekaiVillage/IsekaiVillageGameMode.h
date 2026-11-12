// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IsekaiVillageGameMode.generated.h"

UCLASS(minimalapi)
class AIsekaiVillageGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AIsekaiVillageGameMode();

protected:
	virtual void BeginPlay() override;

	/** Spawns the gentle stylized terrain for the village map */
	void SpawnVillageTerrain();
};



