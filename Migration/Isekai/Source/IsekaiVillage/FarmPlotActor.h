// Copyright Epic Games, Inc. All Rights Reserved.
// FarmPlotActor.h — Modular interactive farming plot actor for crop cultivation

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FarmingSystemTypes.h"
#include "TownEconomyTypes.h"
#include "FarmPlotActor.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class UInstancedStaticMeshComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_FourParams(FOnCropHarvestedSignature, int32, GridX, int32, GridY, FName, ItemID, int32, YieldCount);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnTileStateChangedSignature, int32, GridX, int32, GridY, EFarmTileState, NewState);

/**
 * Interactive farm plot with customizable NxM soil grid.
 * Supports tilling, sowing, watering, and harvesting.
 */
UCLASS(BlueprintType, Blueprintable, ClassGroup = (Farming))
class ISEKAIVILLAGE_API AFarmPlotActor : public AActor
{
	GENERATED_BODY()

public:
	AFarmPlotActor();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// ------------------------------------------------------------------
	// Configuration
	// ------------------------------------------------------------------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Farm Setup")
	int32 GridWidth = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Farm Setup")
	int32 GridHeight = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Farm Setup")
	float TileSpacing = 120.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Farm Setup")
	EBuildingTier FarmTier = EBuildingTier::Tier_1_Rustic;

	UFUNCTION(BlueprintCallable, Category = "Farm Setup")
	void SetFarmTier(EBuildingTier NewTier);

	// ------------------------------------------------------------------
	// Components
	// ------------------------------------------------------------------
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> PlotMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> InteractionBox;

	// ------------------------------------------------------------------
	// Tile Data
	// ------------------------------------------------------------------
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Farm Data")
	TArray<FFarmTile> Tiles;

	// ------------------------------------------------------------------
	// Grid Operations
	// ------------------------------------------------------------------
	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	void InitializePlot();

	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	bool GetTileCoordinatesFromLocation(const FVector& WorldLocation, int32& OutX, int32& OutY) const;

	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	bool TillTile(int32 X, int32 Y);

	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	bool PlantCrop(int32 X, int32 Y, UCropDataAsset* InCrop);

	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	bool WaterTile(int32 X, int32 Y);

	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	bool HarvestTile(int32 X, int32 Y, FName& OutHarvestItemID, int32& OutYield, ECropQuality& OutQuality);

	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	bool ClearTile(int32 X, int32 Y);

	/** Fast-forward 1 full day of growth across all tiles */
	UFUNCTION(BlueprintCallable, Category = "Farm Operations")
	void AdvanceDay();

	UFUNCTION(BlueprintPure, Category = "Farm Operations")
	EFarmTileState GetTileState(int32 X, int32 Y) const;

	// ------------------------------------------------------------------
	// Delegates
	// ------------------------------------------------------------------
	UPROPERTY(BlueprintAssignable, Category = "Farm Events")
	FOnCropHarvestedSignature OnCropHarvested;

	UPROPERTY(BlueprintAssignable, Category = "Farm Events")
	FOnTileStateChangedSignature OnTileStateChanged;

private:
	int32 GetIndex(int32 X, int32 Y) const;
	bool IsValidCoord(int32 X, int32 Y) const;
};
