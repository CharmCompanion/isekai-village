// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "IslandTerrainActor.generated.h"

/**
 * Organic Ocean Island Sanctum Landmass.
 * Features:
 * - South Beach starting cove at sea level
 * - Winding natural ascending trail up through grassy ridges
 * - Elevated northern tower plateau overlooking the ocean for the player's tower
 * - Sheer ocean sea cliffs on the north/east
 * - Surrounding turquoise ocean water plane
 */
UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AIslandTerrainActor : public AActor
{
	GENERATED_BODY()

public:
	AIslandTerrainActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* IslandLandmassMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* OceanWaterPlane;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* BeachCoveMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* TowerPlateauMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Island")
	FVector TowerPlateauLocation = FVector(2000.0f, 0.0f, 450.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Island")
	FVector BeachSpawnLocation = FVector(-2500.0f, -600.0f, 30.0f);

	UFUNCTION(BlueprintCallable, Category = "Island")
	void SetupIslandMaterials();

private:
	void ConstructOrganicIslandGeometry();
};

