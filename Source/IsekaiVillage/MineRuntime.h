// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "MineRuntime.generated.h"

class USceneComponent;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AMineRuntime : public AActor
{
	GENERATED_BODY()

public:
	AMineRuntime();
	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mine")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mine")
	FName ReturnLevel = TEXT("/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mine")
	FName ReturnStartTag = TEXT("MineReturn");

	void BuildMine();

private:
	void BuildFloor(int32 FloorIndex, float Z, FName Ore, int32 RequiredLevel, int32 VeinCount);
};
