// Copyright Epic Games, Inc. All Rights Reserved.
// WorldMapTransition.h — Static helper for map transitions from Blueprints

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IsekaiVillageTypes.h"
#include "WorldMapTransition.generated.h"

/**
 * Static helper actor — call TransitionToZone from Blueprints.
 * Place in any map, then call the static function from a BP event.
 * Or use ATownZone directly for volume-based transitions.
 */
UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AWorldMapTransition : public AActor
{
	GENERATED_BODY()

public:
	AWorldMapTransition();

	/**
	 * Transition to a different world zone.
	 * Stores entry data in GameInstance and loads the destination map.
	 */
	UFUNCTION(BlueprintCallable, Category = "WorldMap", meta = (WorldContext = "WorldContextObject"))
	static void TransitionToZone(UObject* WorldContextObject, UWorldZoneData* Zone,
		FName EntryPointOverride = NAME_None, FVector SpawnOffset = FVector::ZeroVector,
		FRotator SpawnRotation = FRotator::ZeroRotator);
};
