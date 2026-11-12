// Copyright Epic Games, Inc. All Rights Reserved.
// CampSystemActor.h — Interactive Campfire for Resting, Cooking, and Party Strategy

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "CookingSystemTypes.h"
#include "CampSystemActor.generated.h"

class USphereComponent;
class UPointLightComponent;
class UNiagaraComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDishCooked, const FActiveFoodBuff&, ActiveBuff);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnPartyRested);

UCLASS(ClassGroup = (TalesTemplate))
class ISEKAIVILLAGE_API ACampSystemActor : public AActor
{
	GENERATED_BODY()

public:
	ACampSystemActor();

	// ── Components ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* InteractionSphere;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UPointLightComponent* CampFireLight;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* CampFireMesh;

	// ── Cooking State ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Cooking")
	FActiveFoodBuff CurrentActiveBuff;

	UPROPERTY(BlueprintAssignable, Category = "Cooking|Events")
	FOnDishCooked OnDishCooked;

	UPROPERTY(BlueprintAssignable, Category = "Cooking|Events")
	FOnPartyRested OnPartyRested;

	// ── Core Operations ──
	/** Fully restores HP and TP for player and party members */
	UFUNCTION(BlueprintCallable, Category = "Camp")
	void RestParty();

	/** Prepares a recipe, granting party-wide buffs for upcoming battles */
	UFUNCTION(BlueprintCallable, Category = "Camp|Cooking")
	bool CookRecipe(UCookingRecipeDataAsset* Recipe, FName ChefName);

	/** Consumes one battle from active food buff duration */
	UFUNCTION(BlueprintCallable, Category = "Camp|Cooking")
	void DecrementFoodBuff();

	UFUNCTION(BlueprintPure, Category = "Camp|Cooking")
	bool HasActiveFoodBuff() const { return CurrentActiveBuff.BattlesRemaining > 0 && CurrentActiveBuff.BuffType != EFoodBuffType::None; }
};
