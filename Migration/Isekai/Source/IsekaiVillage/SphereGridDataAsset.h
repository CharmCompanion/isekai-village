// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "IsekaiVillageTypes.h"
#include "SphereGridDataAsset.generated.h"

/**
 * Data asset defining a Sphere Grid for adventurer progression.
 * Follows FFX Expert grid style: stat nodes and skill/arte nodes.
 */
UCLASS(BlueprintType, ClassGroup = "IsekaiVillage")
class ISEKAIVILLAGE_API USphereGridDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	/** Map of NodeID to Sphere Node definition */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TMap<FName, FSphereNode> GridNodes;

	/** The starting node ID for this grid */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName StartingNodeID;

	/** Grid class category (e.g. "Swordsman", "CENTER_A_Life") */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName GridCategory;
};
