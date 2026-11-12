// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "LakeFishingSpot.generated.h"

class USphereComponent;
class UStaticMeshComponent;
class AIsekaiVillageCharacter;

/**
 * Interactive shoreline / pier fishing spot for Map_ElRuhnSky Lake and Veil Falls.
 * Players cast/reel via melee-gather (F / LMB) or interact (T) to catch Fish.
 */
UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ALakeFishingSpot : public AActor
{
	GENERATED_BODY()

public:
	ALakeFishingSpot();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Lake")
	TObjectPtr<USphereComponent> InteractSphere;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Lake")
	TObjectPtr<UStaticMeshComponent> BuoyMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lake")
	FString SpotTitle = TEXT("SkyLake Fishing Pier");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lake")
	int32 CatchesRemaining = 12;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lake")
	int32 MaxCatchesPerRestock = 12;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Lake")
	float RestockSeconds = 45.0f;

	UFUNCTION(BlueprintCallable, Category = "Lake")
	bool TryFish(AIsekaiVillageCharacter* Character);

	UFUNCTION(BlueprintCallable, Category = "Lake")
	void ReplenishSpot();

private:
	int32 CastsOnCurrentFish = 0;
	FTimerHandle RestockTimer;
};
