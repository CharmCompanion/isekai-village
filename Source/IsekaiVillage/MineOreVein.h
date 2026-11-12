// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MineOreVein.generated.h"

class UStaticMeshComponent;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AMineOreVein : public AActor
{
	GENERATED_BODY()

public:
	AMineOreVein();
	virtual void OnConstruction(const FTransform& Transform) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mine")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mine")
	FName OreId = TEXT("Copper");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mine")
	int32 HitsLeft = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mine")
	int32 RequiredLevel = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mine")
	float RespawnSeconds = 0.0f;

	UFUNCTION(BlueprintCallable, Category = "Mine")
	bool TryMine(class AIsekaiVillageCharacter* Character);

private:
	bool bHitsInitialized = false;
	bool bDepleted = false;
	int32 InitialHits = 3;
	FTimerHandle RespawnTimerHandle;
	void RespawnVein();
};
