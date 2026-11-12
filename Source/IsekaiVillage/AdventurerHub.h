// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AdventurerHub.generated.h"

class USceneComponent;
class AIslandWarpPortal;
class AGuildMasterDesk;
class ARoomVolume;
class ALinchpinProp;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AAdventurerHub : public AActor
{
	GENERATED_BODY()

public:
	AAdventurerHub();

	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Hub")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hub")
	FName DungeonLevel = TEXT("/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnDungeon");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hub")
	FName DungeonStartTag = TEXT("DungeonStart");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Hub")
	bool bPlayableInteriors = true;

	UFUNCTION(BlueprintCallable, Category = "Hub")
	void BuildHub();

private:
	AActor* SpawnBox(const FVector& Local, const FRotator& Rot, const FVector& Scale, const FLinearColor& Color);
	ALinchpinProp* SpawnProp(const FVector& Local, FName Tag);
	ARoomVolume* SpawnRoom(const FVector& Local, const FVector& Extent);
};
