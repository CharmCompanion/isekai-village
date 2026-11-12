// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "BuildTypes.h"
#include "LinchpinRecipe.generated.h"

UCLASS(BlueprintType)
class ISEKAIVILLAGE_API ULinchpinRecipe : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	FName RecipeId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	TArray<FName> RequiredTags;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	ERoomFunction ResultFunction = ERoomFunction::EmptyHall;

	virtual FPrimaryAssetId GetPrimaryAssetId() const override
	{
		return FPrimaryAssetId(TEXT("LinchpinRecipe"), RecipeId.IsNone() ? GetFName() : RecipeId);
	}

	static void GetDefaultRecipes(TArray<TObjectPtr<ULinchpinRecipe>>& OutRecipes);

	UFUNCTION(BlueprintPure, Category = "Linchpin")
	static TArray<ULinchpinRecipe*> GetDefaultRecipesList();
};
