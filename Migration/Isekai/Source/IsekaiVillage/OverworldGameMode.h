// Copyright Epic Games, Inc. All Rights Reserved.
// OverworldGameMode.h — GameMode for the scaled-down world map

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "OverworldGameMode.generated.h"

/**
 * Overworld GameMode — used on the world map.
 * Sets AOverworldCharacter as the default pawn.
 * Positions the player at the appropriate entry point based on transition data.
 */
UCLASS(minimalapi)
class AOverworldGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AOverworldGameMode();

protected:
	virtual void BeginPlay() override;

	/** Spawns the stylized mesh terrain for the overworld (uses blockout heightmap) */
	void SpawnOverworldTerrain();
};
