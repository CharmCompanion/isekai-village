// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "IsekaiVillageTypes.h"
#include "SphereGridDataAsset.generated.h"

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FSphereGridStatTotals
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 HP = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 TP = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 Inventory = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 CarryWeight = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	float MoveSpeedPercent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	float BuildSpeedPercent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 Trust = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 GaldPercent = 0;
};

/**
 * One Sphere Grid disc. CENTER A Life ships 14 default stat nodes (GDD §4).
 */
UCLASS(BlueprintType)
class ISEKAIVILLAGE_API USphereGridDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	USphereGridDataAsset();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName DiscID = TEXT("CenterA");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FText DiscName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName StartNodeID = TEXT("CA_Life_HP1");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName FlipStartNodeID = TEXT("CA_Adv_Dash");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TMap<FName, FSphereNode> Nodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FName> LifeNodeOrder;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TMap<FName, FSphereNode> FlipFaceNodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FName> FlipNodeOrder;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool GetNode(FName NodeID, FSphereNode& OutNode) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	FSphereGridStatTotals SumBonuses(const TArray<FName>& UnlockedNodeIDs) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool IsLifeFaceComplete(const TArray<FName>& UnlockedNodeIDs) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool IsFlipFaceComplete(const TArray<FName>& UnlockedNodeIDs) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool IsNodeAdjacentToUnlocked(FName NodeID, const TArray<FName>& UnlockedNodeIDs, bool bFlipped) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool HasUnlockedNodeOnFace(const TArray<FName>& UnlockedNodeIDs, bool bFlipped) const;
};
