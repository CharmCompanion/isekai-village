// Copyright Epic Games, Inc. All Rights Reserved.
// AlchemyWorkshopActor.h — Interactive Alchemy Laboratory for Demon Core Refining & Potion Compounding

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TownEconomyTypes.h"
#include "AlchemyWorkshopActor.generated.h"

class USphereComponent;
class UStaticMeshComponent;
class UPointLightComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAlchemyInteracted, APawn*, Interactor);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnPotionCompounded, FName, RecipeID, FText, PotionName);

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AAlchemyWorkshopActor : public AActor
{
	GENERATED_BODY()

public:
	AAlchemyWorkshopActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* CauldronMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UPointLightComponent* CauldronGlow;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* InteractionTrigger;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	FText LabName = FText::FromString(TEXT("Caelum's Arcane Apotheca"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	EBuildingTier WorkshopTier = EBuildingTier::Tier_1_Rustic;

	UFUNCTION(BlueprintCallable, Category = "Alchemy")
	void SetWorkshopTier(EBuildingTier NewTier);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	TArray<FAlchemyRecipe> AlchemyRecipes;

	UPROPERTY(BlueprintAssignable, Category = "Alchemy|Events")
	FOnAlchemyInteracted OnAlchemyInteracted;

	UPROPERTY(BlueprintAssignable, Category = "Alchemy|Events")
	FOnPotionCompounded OnPotionCompounded;

	UFUNCTION(BlueprintCallable, Category = "Alchemy")
	void InteractWithPlayer(APawn* PlayerPawn);

	/** Compound a potion or elixir from herbs, farm crops, and demon essences */
	UFUNCTION(BlueprintCallable, Category = "Alchemy")
	bool CompoundPotion(FName RecipeID, UPARAM(ref) int32& PlayerGold, UPARAM(ref) int32& PlayerHerbs,
		UPARAM(ref) int32& PlayerCrops, UPARAM(ref) int32& PlayerDemonEssence, FText& OutPotionName);

	/** Purify dark demon remnants into pure catalyst crystals */
	UFUNCTION(BlueprintCallable, Category = "Alchemy")
	bool PurifyDemonCores(int32 CorruptedCoresIn, int32& OutPurifiedCrystals);

	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	void PopulateDefaultAlchemyRecipes();
};
