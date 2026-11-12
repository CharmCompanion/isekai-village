// Copyright Epic Games, Inc. All Rights Reserved.
// TreasureChestActor.h — Dungeon treasure chests with lock mechanics and Demon Mimic surprise traps

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IsekaiVillageTypes.h"
#include "TreasureChestActor.generated.h"

class UBoxComponent;
class UStaticMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnChestOpenedSignature, int32, GoldAmount, FName, ItemID, int32, Quantity);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnMimicTriggeredSignature, class ATreasureChestActor*, MimicChest);

/**
 * Interactive treasure chest found in dungeons, fields, and ruins.
 * Can be normal, locked, or a camouflaged Demon Mimic trap.
 */
UCLASS(Blueprintable, BlueprintType, ClassGroup = (Dungeon))
class ISEKAIVILLAGE_API ATreasureChestActor : public AActor
{
	GENERATED_BODY()

public:
	ATreasureChestActor();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// ── Components ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> InteractionBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> ChestBaseMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> ChestLidMesh;

	// ── Chest State & Traps ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chest")
	bool bIsDemonMimic = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chest")
	bool bIsLocked = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Chest")
	FName RequiredKeyID = NAME_None;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Chest")
	bool bIsOpened = false;

	// ── Rewards (for Non-Mimics) ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	int32 GoldReward = 150;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	FName ItemRewardID = "AppleGel";

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	int32 ItemQuantity = 2;

	// ── Interaction ──
	UFUNCTION(BlueprintCallable, Category = "Chest")
	bool OpenChest(AActor* Interactor);

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Chest Events")
	FOnChestOpenedSignature OnChestOpened;

	UPROPERTY(BlueprintAssignable, Category = "Chest Events")
	FOnMimicTriggeredSignature OnMimicTriggered;

private:
	bool bIsAnimatingLid = false;
	FRotator TargetLidRotation;
};
