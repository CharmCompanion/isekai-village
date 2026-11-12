// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "GatherTypes.h"
#include "GatherInventoryComponent.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UGatherInventoryComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UGatherInventoryComponent();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gather")
	EAxeTier AxeTier = EAxeTier::Stone;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gather")
	EAxeTier PickaxeTier = EAxeTier::Stone;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Gather")
	TArray<FGatherStack> Stacks;

	UFUNCTION(BlueprintCallable, Category = "Gather")
	void AddItem(FName ItemId, int32 Count);

	UFUNCTION(BlueprintPure, Category = "Gather")
	int32 GetCount(FName ItemId) const;

	UFUNCTION(BlueprintCallable, Category = "Gather")
	bool Consume(FName ItemId, int32 Count);

	UFUNCTION(BlueprintCallable, Category = "Gather")
	bool TryUpgradeAxe();

	UFUNCTION(BlueprintCallable, Category = "Gather")
	bool TryUpgradePickaxe();

	UFUNCTION(BlueprintCallable, Category = "Gather")
	bool TryForgeUpgrades();

	UFUNCTION(BlueprintPure, Category = "Gather")
	int32 HitsToChop() const;

	UFUNCTION(BlueprintPure, Category = "Gather")
	int32 HitsToMine() const;

	UFUNCTION(BlueprintPure, Category = "Gather")
	int32 WoodYield() const;

	UFUNCTION(BlueprintPure, Category = "Gather")
	int32 OreYield() const;

	UFUNCTION(BlueprintPure, Category = "Gather")
	FString AxeLabel() const;

	UFUNCTION(BlueprintPure, Category = "Gather")
	FString PickaxeLabel() const;

	UFUNCTION(BlueprintPure, Category = "Gather")
	FString InventoryLine() const;

	static int32 ForgeCost(const class AIsekaiVillageCharacter* Character, int32 Base, bool bCrystal = false);
};
