// Copyright Epic Games, Inc. All Rights Reserved.
// WonderChefActor.h — Quirky Disguised Prop that Reveals Recipes (Tales Signature Hallmark)

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CookingSystemTypes.h"
#include "WonderChefActor.generated.h"

class USphereComponent;
class UStaticMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnWonderChefDiscovered, UCookingRecipeDataAsset*, RecipeAwarded, const FText&, ChefDialogue);

UCLASS(ClassGroup = (TalesTemplate))
class ISEKAIVILLAGE_API AWonderChefActor : public AActor
{
	GENERATED_BODY()

public:
	AWonderChefActor();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* DisguiseMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* InteractionSphere;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WonderChef")
	TObjectPtr<UCookingRecipeDataAsset> RewardRecipe = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "WonderChef")
	FText DiscoveryDialogue = FText::FromString(TEXT("Aha! You found me! I am the Wonder Chef! Learn this magnificent recipe!"));

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "WonderChef")
	bool bHasBeenDiscovered = false;

	UPROPERTY(BlueprintAssignable, Category = "WonderChef|Events")
	FOnWonderChefDiscovered OnWonderChefDiscovered;

	UFUNCTION(BlueprintCallable, Category = "WonderChef")
	bool DiscoverChef();
};
