// Copyright Epic Games, Inc. All Rights Reserved.
// MeshTerrainBuilder.cpp — Generates a walkable mesh terrain from an R16 heightmap

#include "MeshTerrainBuilder.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "UObject/UObjectGlobals.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Materials/Material.h"

AMeshTerrainBuilder::AMeshTerrainBuilder()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	TerrainMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("TerrainMesh"));
	TerrainMesh->SetupAttachment(RootComponent);
	TerrainMesh->SetCollisionProfileName(TEXT("BlockAll"));
	TerrainMesh->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	TerrainMesh->bUseAsyncCooking = true;

	// Water plane (stylized world water, sits above the generated heightfield)
	WaterPlane = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WaterPlane"));
	WaterPlane->SetupAttachment(RootComponent);
	WaterPlane->SetCollisionProfileName(TEXT("OverlapAll"));
	static ConstructorHelpers::FObjectFinder<UStaticMesh> PlaneMesh(TEXT("/Engine/BasicShapes/Plane.Plane"));
	if (PlaneMesh.Succeeded())
	{
		WaterPlane->SetStaticMesh(PlaneMesh.Object);
	}
}

void AMeshTerrainBuilder::BeginPlay()
{
	Super::BeginPlay();

	GenerateFromFileOrDefault();
}

void AMeshTerrainBuilder::GenerateFromFileOrDefault()
{
	if (bLoadFromR16File && !HeightmapPath.IsEmpty())
	{
		int32 W = 0, H = 0;
		TArray<uint16> Data = LoadR16Heightmap(HeightmapPath, W, H);
		if (Data.Num() > 0)
		{
			GenerateFromHeightmapData(Data, W, H);
			return;
		}
	}

	GenerateTerrain();
}

void AMeshTerrainBuilder::GenerateTerrain()
{
	// Flat / gently-rolling stylized terrain plane (procedural fallback if no heightmap)
	const int32 Res = FMath::Clamp(TerrainResolution, 32, 512);
	const float Step = TerrainSize / (float)Res;

	TArray<FVector> Vertices;
	TArray<int32> Triangles;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FLinearColor> VertexColors;
	TArray<FProcMeshTangent> Tangents;

	Vertices.Reserve((Res + 1) * (Res + 1));
	UVs.Reserve((Res + 1) * (Res + 1));
	VertexColors.Reserve((Res + 1) * (Res + 1));
	Tangents.Reserve((Res + 1) * (Res + 1));

	const float HalfExtent = TerrainSize * 0.5f;

	for (int32 Y = 0; Y <= Res; ++Y)
	{
		for (int32 X = 0; X <= Res; ++X)
		{
			float WorldX = -HalfExtent + X * Step;
			float WorldY = -HalfExtent + Y * Step;

			// Gentle organic roll: layered sine waves (stylized rolling plains)
			float Z = HeightOffset;
			if (!bFlatArena)
			{
				Z += FMath::Sin(WorldX * 0.0016f + 1.7f) * 90.0f;
				Z += FMath::Sin(WorldY * 0.0012f) * 70.0f;
				Z += FMath::Sin((WorldX + WorldY) * 0.0009f) * 45.0f;
			}

			Vertices.Add(FVector(WorldX, WorldY, Z));
			UVs.Add(FVector2D((float)X / (float)Res, (float)Y / (float)Res));
			VertexColors.Add(FLinearColor(1.0f, 1.0f, 1.0f, 1.0f));
		}
	}

	for (int32 Y = 0; Y < Res; ++Y)
	{
		for (int32 X = 0; X < Res; ++X)
		{
			int32 TL = Y * (Res + 1) + X;
			int32 TR = TL + 1;
			int32 BL = (Y + 1) * (Res + 1) + X;
			int32 BR = BL + 1;

			Triangles.Add(TL);
			Triangles.Add(BL);
			Triangles.Add(TR);

			Triangles.Add(TR);
			Triangles.Add(BL);
			Triangles.Add(BR);
		}
	}

	TerrainMesh->CreateMeshSection_LinearColor(0, Vertices, Triangles, Normals, UVs, VertexColors, Tangents, true);
	TerrainMesh->SetRelativeLocation(FVector::ZeroVector);

	ApplyBiomeMaterial();
	ApplyWaterMaterial();
}

void AMeshTerrainBuilder::GenerateFromHeightmapData(const TArray<uint16>& HeightData, int32 Width, int32 Height)
{
	if (HeightData.Num() == 0 || Width <= 0 || Height <= 0)
	{
		GenerateTerrain();
		return;
	}

	const int32 Res = FMath::Clamp(TerrainResolution, 32, 512);
	const float Step = TerrainSize / (float)Res;

	TArray<FVector> Vertices;
	TArray<int32> Triangles;
	TArray<FVector2D> UVs;
	TArray<FLinearColor> VertexColors;

	Vertices.Reserve((Res + 1) * (Res + 1));
	UVs.Reserve((Res + 1) * (Res + 1));
	VertexColors.Reserve((Res + 1) * (Res + 1));

	const float HalfExtent = TerrainSize * 0.5f;

	// Normalize against the heightmap's own min/max so the lowest ground = HeightOffset
	float DataMin = 65535.0f;
	float DataMax = 0.0f;
	for (const uint16& Raw : HeightData)
	{
		DataMin = FMath::Min(DataMin, (float)Raw);
		DataMax = FMath::Max(DataMax, (float)Raw);
	}
	const float DataRange = FMath::Max(DataMax - DataMin, 1.0f);

	// Sampling region into the source heightmap (center-crop if resolutions differ)
	const int32 SrcW = Width;
	const int32 SrcH = Height;

	for (int32 Y = 0; Y <= Res; ++Y)
	{
		for (int32 X = 0; X <= Res; ++X)
		{
			float WorldX = -HalfExtent + X * Step;
			float WorldY = -HalfExtent + Y * Step;

			// Bilinear-ish sample from the source (nearest for now, cheap and stable)
			int32 SrcX = FMath::Clamp((int32)((float)X / (float)Res * (float)(SrcW - 1)), 0, SrcW - 1);
			int32 SrcY = FMath::Clamp((int32)((float)Y / (float)Res * (float)(SrcH - 1)), 0, SrcH - 1);

			uint16 RawHeight = HeightData[SrcY * SrcW + SrcX];
			float Normalized = ((float)RawHeight - DataMin) / DataRange;
			float Z = HeightOffset + Normalized * HeightScale;

			Vertices.Add(FVector(WorldX, WorldY, Z));
			UVs.Add(FVector2D((float)X / (float)Res, (float)Y / (float)Res));
			VertexColors.Add(FLinearColor(1.0f, 1.0f, 1.0f, 1.0f));
		}
	}

	for (int32 Y = 0; Y < Res; ++Y)
	{
		for (int32 X = 0; X < Res; ++X)
		{
			int32 TL = Y * (Res + 1) + X;
			int32 TR = TL + 1;
			int32 BL = (Y + 1) * (Res + 1) + X;
			int32 BR = BL + 1;

			Triangles.Add(TL);
			Triangles.Add(BL);
			Triangles.Add(TR);

			Triangles.Add(TR);
			Triangles.Add(BL);
			Triangles.Add(BR);
		}
	}

	TerrainMesh->CreateMeshSection_LinearColor(0, Vertices, Triangles, TArray<FVector>(), UVs, VertexColors, TArray<FProcMeshTangent>(), true);

	ApplyBiomeMaterial();
	ApplyWaterMaterial();
}

float AMeshTerrainBuilder::GetHeightAt(int32 X, int32 Y, const TArray<uint16>& HeightData, int32 DataWidth, int32 DataHeight)
{
	if (HeightData.Num() == 0)
	{
		return HeightOffset;
	}
	int32 SrcX = FMath::Clamp(X, 0, DataWidth - 1);
	int32 SrcY = FMath::Clamp(Y, 0, DataHeight - 1);
	uint16 RawHeight = HeightData[SrcY * DataWidth + SrcX];

	float DataMin = 65535.0f;
	float DataMax = 0.0f;
	for (const uint16& Raw : HeightData)
	{
		DataMin = FMath::Min(DataMin, (float)Raw);
		DataMax = FMath::Max(DataMax, (float)Raw);
	}
	const float DataRange = FMath::Max(DataMax - DataMin, 1.0f);

	return HeightOffset + (((float)RawHeight - DataMin) / DataRange) * HeightScale;
}

TArray<uint16> AMeshTerrainBuilder::LoadR16Heightmap(const FString& FilePath, int32& OutWidth, int32& OutHeight)
{
	TArray<uint16> Empty;

	// Resolve relative paths against the project content root
	FString ResolvedPath = FilePath;
	if (FPaths::IsRelative(FilePath))
	{
		ResolvedPath = FPaths::Combine(FPaths::ProjectContentDir(), FilePath);
	}

	TArray<uint8> RawBytes;
	if (!FFileHelper::LoadFileToArray(RawBytes, *ResolvedPath))
	{
		UE_LOG(LogTemp, Warning, TEXT("MeshTerrainBuilder: failed to load heightmap %s"), *ResolvedPath);
		return Empty;
	}

	// R16 raw = 2 bytes per sample. Guess square size.
	const int32 SampleCount = RawBytes.Num() / 2;
	if (SampleCount <= 0)
	{
		return Empty;
	}

	const int32 Side = (int32)FMath::Sqrt((float)SampleCount);
	OutWidth = Side;
	OutHeight = Side;

	if (Side * Side != SampleCount)
	{
		UE_LOG(LogTemp, Warning, TEXT("MeshTerrainBuilder: R16 not square (%d samples), clamping..."), SampleCount);
	}

	TArray<uint16> HeightData;
	HeightData.SetNum(SampleCount);

	for (int32 i = 0; i < SampleCount; ++i)
	{
		// Little-endian uint16
		HeightData[i] = (uint16)(RawBytes[i * 2]) | ((uint16)RawBytes[i * 2 + 1] << 8);
	}

	return HeightData;
}

void AMeshTerrainBuilder::ApplyBiomeMaterial()
{
	UMaterialInterface* TerrainMat = Cast<UMaterialInterface>(StaticLoadObject(UMaterialInterface::StaticClass(), nullptr, *TerrainMaterialPath));
	if (!TerrainMat)
	{
		// Fallback per-biome palette so the world is readable even without the pack
		TerrainMat = LoadObject<UMaterial>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	}

	if (!TerrainMat)
	{
		return;
	}

	UMaterialInstanceDynamic* DynMat = UMaterialInstanceDynamic::Create(TerrainMat, this);
	if (!DynMat)
	{
		return;
	}

	// Painterly stylized color palettes per biome
	switch (Biome)
	{
	case ETerrainBiome::Plains:
		DynMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.35f, 0.65f, 0.24f, 1.0f));
		break;
	case ETerrainBiome::Forest:
		DynMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.22f, 0.48f, 0.17f, 1.0f));
		break;
	case ETerrainBiome::Desert:
		DynMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.86f, 0.73f, 0.45f, 1.0f));
		break;
	case ETerrainBiome::Snow:
		DynMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.88f, 0.92f, 0.94f, 1.0f));
		break;
	case ETerrainBiome::Cave:
		DynMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.18f, 0.16f, 0.16f, 1.0f));
		break;
	}

	if (TerrainMesh)
	{
		TerrainMesh->SetMaterial(0, DynMat);
	}
}

void AMeshTerrainBuilder::ApplyWaterMaterial()
{
	if (!bGenerateWater || !WaterPlane)
	{
		WaterPlane->SetVisibility(false);
		return;
	}

	UMaterialInterface* WaterMat = Cast<UMaterialInterface>(StaticLoadObject(UMaterialInterface::StaticClass(), nullptr, *WaterMaterialPath));
	if (!WaterMat)
	{
		WaterMat = LoadObject<UMaterial>(nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial"));
	}

	if (WaterMat)
	{
		UMaterialInstanceDynamic* DynWater = UMaterialInstanceDynamic::Create(WaterMat, this);
		if (DynWater)
		{
			DynWater->SetVectorParameterValue(FName("Color"), FLinearColor(0.05f, 0.45f, 0.62f, 0.75f));
			WaterPlane->SetMaterial(0, DynWater);
		}
	}

	// Water plane floats just above the terrain's water level, sized to match terrain
	WaterPlane->SetRelativeLocation(FVector(0.0f, 0.0f, WaterLevel));
	WaterPlane->SetRelativeScale3D(FVector(TerrainSize * 0.01f, TerrainSize * 0.01f, 1.0f));
}

AMeshTerrainBuilder* AMeshTerrainBuilder::SpawnTerrainForBiome(UObject* WorldContextObject, ETerrainBiome InBiome, FVector Location)
{
	if (!WorldContextObject)
	{
		return nullptr;
	}

	UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::ReturnNull);
	if (!World)
	{
		return nullptr;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	AMeshTerrainBuilder* Terrain = World->SpawnActor<AMeshTerrainBuilder>(AMeshTerrainBuilder::StaticClass(), Location, FRotator::ZeroRotator, SpawnParams);
	if (Terrain)
	{
		Terrain->Biome = InBiome;
		Terrain->GenerateTerrain();
	}

	return Terrain;
}