// Copyright Epic Games, Inc. All Rights Reserved.
// BlacksmithActor.h — Interactive Forge for Weapon Upgrading (+1 to +10), Elemental Infusion & Salvage

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TownEconomyTypes.h"
#include "BlacksmithActor.generated.h"

class USphereComponent;
class UStaticMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnBlacksmithInteracted, APawn*, Interactor);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnWeaponUpgraded, FName, WeaponID, int32, NewLevel, float, NewAttackPower);

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ABlacksmithActor : public AActor
{
	GENERATED_BODY()

public:
	ABlacksmithActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* AnvilMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* InteractionTrigger;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	FText SmithyName = FText::FromString(TEXT("Brant's Heavy Ironworks"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	EBuildingTier ForgeTier = EBuildingTier::Tier_1_Rustic;

	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	void SetForgeTier(EBuildingTier NewTier);

	UFUNCTION(BlueprintPure, Category = "Blacksmith")
	int32 GetMaxRefinementLevel() const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	TArray<FBlacksmithRecipe> ForgeRecipes;

	UPROPERTY(BlueprintAssignable, Category = "Blacksmith|Events")
	FOnBlacksmithInteracted OnBlacksmithInteracted;

	UPROPERTY(BlueprintAssignable, Category = "Blacksmith|Events")
	FOnWeaponUpgraded OnWeaponUpgraded;

	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	void InteractWithPlayer(APawn* PlayerPawn);

	/** Upgrade weapon from current level to TargetLevel (+1 to +10) */
	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	bool UpgradeWeapon(FName WeaponID, int32 TargetLevel, UPARAM(ref) int32& PlayerGold,
		UPARAM(ref) int32& PlayerOres, UPARAM(ref) int32& PlayerDemonCores, float& OutNewAtk);

	/** Imbue weapon with elemental property (Fire, Water, Earth, Wind) */
	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	bool ImbueElement(FName WeaponID, EElement NewElement, UPARAM(ref) int32& PlayerGold,
		UPARAM(ref) int32& PlayerDemonCores);

	/** Disassemble equipment into raw ores and demon dust */
	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	bool DisassembleEquipment(FName WeaponID, int32& OutOresReturned, int32& OutDemonDustReturned);

	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	void PopulateDefaultForgeRecipes();
};
