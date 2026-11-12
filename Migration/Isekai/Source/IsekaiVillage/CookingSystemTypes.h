// Copyright Epic Games, Inc. All Rights Reserved.
// CookingSystemTypes.h — Tales of Recipe, Cooking Affinities, and Timed Food Buffs

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "CookingSystemTypes.generated.h"

class UTexture2D;

UENUM(BlueprintType)
enum class EFoodBuffType : uint8
{
	None           UMETA(DisplayName = "None"),
	AttackUp       UMETA(DisplayName = "Physical ATK Boost"),
	MagicUp        UMETA(DisplayName = "Elemental Arte Boost"),
	DefenseUp      UMETA(DisplayName = "Physical Defense Boost"),
	ExpBoost       UMETA(DisplayName = "EXP Gain +20%"),
	GaldBoost      UMETA(DisplayName = "Gald Gain +30%"),
	HpRegen        UMETA(DisplayName = "HP Regeneration in Combat"),
	AutoRevive     UMETA(DisplayName = "Auto-Revive Once")
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FActiveFoodBuff
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooking")
	FText DishName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooking")
	EFoodBuffType BuffType = EFoodBuffType::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooking")
	float BuffMagnitude = 0.20f; // +20%

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Cooking")
	int32 BattlesRemaining = 3;
};

/**
 * Data Asset representing a Tales Recipe (Mapo Tofu, Beef Stew, Sandwich, etc.)
 */
UCLASS(BlueprintType, ClassGroup = (TalesTemplate))
class ISEKAIVILLAGE_API UCookingRecipeDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	FName RecipeID;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	FText DishName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	FText Description;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	TObjectPtr<UTexture2D> DishIcon = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	float HP_RecoveryPercent = 30.0f; // Restores 30% HP

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	float TP_RecoveryPercent = 20.0f; // Restores 20% TP

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	EFoodBuffType BuffType = EFoodBuffType::AttackUp;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	float BuffMagnitude = 0.20f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	int32 BuffDurationBattles = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	FName FavoriteChefHeroID; // Hero who receives extra mastery bonus

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe")
	TArray<FName> RequiredIngredients;

	// Permanent Dietary Nutrition (ToS2 Monster raising style, for human adventurers)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionProtein = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionVitality = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionMana = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionAgility = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionHoly = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionDark = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionFire = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionWater = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionWind = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recipe|Nutrition")
	float NutritionEarth = 0.0f;
};
