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

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 Attack = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 Magic = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	float ResPercent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	float AttractionPercent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	float WorkerPacePercent = 0.0f;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FSphereDiscDefinition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName DiscID;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FText Title;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FText Category;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FText UnlockHint;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName StartNodeID;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TMap<FName, FSphereNode> Nodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FName> NodeOrder;
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

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName WorkStartNodeID = TEXT("CB_Work_Yield1");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName VillagerStartNodeID = TEXT("CB_Vil_Jab");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TMap<FName, FSphereNode> WorkFaceNodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FName> WorkNodeOrder;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TMap<FName, FSphereNode> VillagerFaceNodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FName> VillagerNodeOrder;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FSphereDiscDefinition> ExtraDiscs;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	int32 DiscCount() const { return 2 + ExtraDiscs.Num(); }

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool DiscHasFlip(int32 Disc) const { return Disc == 0 || Disc == 1; }

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	FText DiscDisplayTitle(int32 Disc, bool bFlipped) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	FText DiscCategoryLabel(int32 Disc) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	FText DiscUnlockHint(int32 Disc) const;

	UFUNCTION(BlueprintPure, Category = "SphereGrid")
	bool IsDiscUnlocked(int32 Disc, const TArray<FName>& UnlockedNodeIDs) const;

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

	const TMap<FName, FSphereNode>& FaceMap(int32 Disc, bool bFlipped) const;
	const TArray<FName>& FaceOrder(int32 Disc, bool bFlipped) const;
	FName FaceStart(int32 Disc, bool bFlipped) const;
	bool IsFaceComplete(int32 Disc, bool bFlipped, const TArray<FName>& UnlockedNodeIDs) const;
	bool HasUnlockedOnDisc(int32 Disc, bool bFlipped, const TArray<FName>& UnlockedNodeIDs) const;
	bool IsNodeAdjacentOnDisc(FName NodeID, const TArray<FName>& UnlockedNodeIDs, int32 Disc, bool bFlipped) const;
};
