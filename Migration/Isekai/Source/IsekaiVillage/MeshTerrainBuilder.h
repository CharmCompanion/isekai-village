// Copyright Epic Games, Inc. All Rights Reserved.
// MeshTerrainBuilder.h — Generates a walkable mesh terrain from an R16 heightmap

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "ProceduralMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "MeshTerrainBuilder.generated.h"

UENUM(BlueprintType)
enum class ETerrainBiome : uint8
{
	Plains   UMETA(DisplayName = "Plains"),
	Forest   UMETA(DisplayName = "Forest"),
	Desert   UMETA(DisplayName = "Desert"),
	Snow     UMETA(DisplayName = "Snow"),
	Cave     UMETA(DisplayName = "Cave")
};

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AMeshTerrainBuilder : public AActor
{
	GENERATED_BODY()

public:
	AMeshTerrainBuilder();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Terrain")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Terrain")
	UProceduralMeshComponent* TerrainMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Terrain")
	UStaticMeshComponent* WaterPlane;

	// ── Terrain Settings ──

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Size")
	float TerrainSize = 8000.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Size")
	int32 TerrainResolution = 256;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Height")
	float HeightScale = 600.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Height")
	float HeightOffset = -50.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Biome")
	ETerrainBiome Biome = ETerrainBiome::Plains;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Biome")
	bool bGenerateWater = true;

	// When true, output is a perfectly flat pad at HeightOffset (used for battle arenas)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Biome")
	bool bFlatArena = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Biome")
	float WaterLevel = 10.0f;

	// ── Heightmap Source ──

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Heightmap")
	FString HeightmapPath;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Heightmap")
	bool bLoadFromR16File = false;

	// ── Material Paths (SoStylized) ──

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Material")
	FString TerrainMaterialPath = TEXT("/Game/SoStylized/Materials/M_StylizedBasic.M_StylizedBasic");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Terrain|Material")
	FString WaterMaterialPath = TEXT("/Game/SoStylized/Environment/Water/Materials/MI_Water.MI_Water");

	// ── Functions ──

	UFUNCTION(BlueprintCallable, Category = "Terrain")
	void GenerateTerrain();

	/** Generate from the configured R16 heightmap file (if bLoadFromR16File) or gas procedural terrain */
	UFUNCTION(BlueprintCallable, Category = "Terrain")
	void GenerateFromFileOrDefault();

	void GenerateFromHeightmapData(const TArray<uint16>& HeightData, int32 Width, int32 Height);

	UFUNCTION(BlueprintCallable, Category = "Terrain")
	static AMeshTerrainBuilder* SpawnTerrainForBiome(UObject* WorldContextObject, ETerrainBiome InBiome, FVector Location);

protected:
	void ApplyBiomeMaterial();
	void ApplyWaterMaterial();
	TArray<uint16> LoadR16Heightmap(const FString& FilePath, int32& OutWidth, int32& OutHeight);
	float GetHeightAt(int32 X, int32 Y, const TArray<uint16>& HeightData, int32 DataWidth, int32 DataHeight);
};
