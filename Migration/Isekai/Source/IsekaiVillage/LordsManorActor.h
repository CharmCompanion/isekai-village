// Copyright Epic Games, Inc. All Rights Reserved.
// LordsManorActor.h — Interactive Lord's Manor / Town Hall for Village Tier, Style Upgrades & Estate Management

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TownEconomyTypes.h"
#include "LordsManorActor.generated.h"

class USceneComponent;
class UStaticMeshComponent;
class USphereComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnVillageTierUpgradedSignature, EBuildingTier, NewTier, ETownArchitecturalStyle, NewStyle);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnBuildingTierUpgradedSignature, ETownBuildingType, BuildingType, EBuildingTier, NewTier);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnArchitecturalStyleChangedSignature, ETownArchitecturalStyle, NewStyle);

UCLASS(BlueprintType, ClassGroup = (TownSystems))
class ISEKAIVILLAGE_API ALordsManorActor : public AActor
{
	GENERATED_BODY()

public:
	ALordsManorActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> ManorMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USphereComponent> InteractionTrigger;

	// ── Village & Administration State ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Manor|Village")
	EBuildingTier ManorTier = EBuildingTier::Tier_1_Rustic;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Manor|Village")
	ETownArchitecturalStyle VillageStyle = ETownArchitecturalStyle::RusticTimber;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Manor|Village")
	EResidentialHousingTier HousingTier = EResidentialHousingTier::CommonerCottage;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Manor|Buildings")
	TMap<ETownBuildingType, EBuildingTier> BuildingTiers;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Manor|Economy")
	int32 DailyTaxRevenue = 150;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Manor|Economy")
	int32 NoblePatronCount = 0;

	// ── Building Upgrades ──
	UFUNCTION(BlueprintPure, Category = "Manor|Buildings")
	bool CanUpgradeBuilding(ETownBuildingType BuildingType, FText& OutReason) const;

	UFUNCTION(BlueprintCallable, Category = "Manor|Buildings")
	bool UpgradeBuilding(ETownBuildingType BuildingType, UPARAM(ref) int32& PlayerGold, UPARAM(ref) FTownStockpile& Stockpile, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "Manor|Village")
	bool UpgradeManor(UPARAM(ref) int32& PlayerGold, UPARAM(ref) FTownStockpile& Stockpile, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "Manor|Village")
	void SetVillageArchitecturalStyle(ETownArchitecturalStyle NewStyle);

	UFUNCTION(BlueprintCallable, Category = "Manor|Economy")
	int32 CollectDailyTaxes();

	UFUNCTION(BlueprintPure, Category = "Manor|Buildings")
	EBuildingTier GetBuildingTier(ETownBuildingType BuildingType) const;

	// ── Events ──
	UPROPERTY(BlueprintAssignable, Category = "Manor|Events")
	FOnVillageTierUpgradedSignature OnVillageTierUpgraded;

	UPROPERTY(BlueprintAssignable, Category = "Manor|Events")
	FOnBuildingTierUpgradedSignature OnBuildingTierUpgraded;

	UPROPERTY(BlueprintAssignable, Category = "Manor|Events")
	FOnArchitecturalStyleChangedSignature OnArchitecturalStyleChanged;

	// ── UI Integration ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Manor|UI")
	TSubclassOf<class UIsekaiLordsManorWidget> LordsManorWidgetClass;

	UPROPERTY(Transient, BlueprintReadOnly, Category = "Manor|UI")
	TObjectPtr<class UIsekaiLordsManorWidget> ActiveManorWidget;

	UFUNCTION(BlueprintCallable, Category = "Manor|UI")
	bool OpenManorUI(APlayerController* PlayerController);

	UFUNCTION(BlueprintCallable, Category = "Manor|UI")
	void CloseManorUI();

private:
	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);
};
