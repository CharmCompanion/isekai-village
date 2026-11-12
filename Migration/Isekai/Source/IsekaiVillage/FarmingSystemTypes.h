// Copyright Epic Games, Inc. All Rights Reserved.
// FarmingSystemTypes.h — Agricultural and crop management system

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "IsekaiVillageTypes.h"
#include "FarmingSystemTypes.generated.h"

class UStaticMesh;
class UTexture2D;

/**
 * State of a single farm soil tile.
 */
UENUM(BlueprintType)
enum class EFarmTileState : uint8
{
	Untilled  UMETA(DisplayName = "Untilled Soil"),
	Tilled    UMETA(DisplayName = "Tilled Soil (Ready for Seeds)"),
	Planted   UMETA(DisplayName = "Planted (Awaiting Water/Growth)"),
	Watered   UMETA(DisplayName = "Watered & Growing"),
	Mature    UMETA(DisplayName = "Mature (Ready to Harvest)"),
	Withered  UMETA(DisplayName = "Withered (Needs clearing)")
};

/**
 * Crop harvest quality grade affecting cooking/alchemy buff potency.
 */
UENUM(BlueprintType)
enum class ECropQuality : uint8
{
	Normal   UMETA(DisplayName = "Standard Quality"),
	High     UMETA(DisplayName = "High Quality (★)"),
	Pristine UMETA(DisplayName = "Pristine Quality (★★)")
};

/**
 * Data asset defining a cultivatable crop in the game.
 */
UCLASS(BlueprintType, ClassGroup = (Farming))
class ISEKAIVILLAGE_API UCropDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crop Info")
	FName CropID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crop Info")
	FText CropName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crop Info")
	FText Description = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crop Info")
	TObjectPtr<UTexture2D> CropIcon = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Growth")
	int32 TotalGrowthStages = 3; // e.g. 1: Seedling, 2: Sprout, 3: Mature

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Growth")
	float SecondsPerGrowthStage = 15.0f; // Configurable for fast testing or long day cycle

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Harvest")
	FName HarvestedItemID = NAME_None; // Feeds into Cooking / Alchemy

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Harvest")
	int32 MinHarvestYield = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Harvest")
	int32 MaxHarvestYield = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Harvest")
	float HighQualityChance = 0.25f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Harvest")
	float PristineQualityChance = 0.08f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	TObjectPtr<UStaticMesh> SeedlingMesh = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	TObjectPtr<UStaticMesh> GrowingMesh = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	TObjectPtr<UStaticMesh> MatureMesh = nullptr;
};

/**
 * Runtime state of an individual farm plot soil square.
 */
USTRUCT(BlueprintType)
struct FFarmTile
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Tile")
	int32 GridX = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Tile")
	int32 GridY = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Tile")
	EFarmTileState State = EFarmTileState::Untilled;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Crop")
	TObjectPtr<UCropDataAsset> PlantedCrop = nullptr;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Growth")
	int32 CurrentGrowthStage = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Growth")
	float GrowthTimer = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Growth")
	bool bIsWatered = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Harvest")
	ECropQuality CropQuality = ECropQuality::Normal;
};
