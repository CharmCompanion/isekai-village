// Copyright Epic Games, Inc. All Rights Reserved.
// FarmPlotActor.cpp — Modular interactive farming plot actor implementation

#include "FarmPlotActor.h"
#include "AdventurerManagerComponent.h"
#include "AdventurerGuildBoardActor.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "Engine/World.h"

AFarmPlotActor::AFarmPlotActor()
{
	PrimaryActorTick.bCanEverTick = true;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	PlotMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PlotMesh"));
	PlotMesh->SetupAttachment(SceneRoot);
	PlotMesh->SetCollisionProfileName(TEXT("BlockAll"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> WoodFoundationMesh(TEXT("/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_foundation_wood_01.SM_PROP_foundation_wood_01"));
	if (WoodFoundationMesh.Succeeded())
	{
		PlotMesh->SetStaticMesh(WoodFoundationMesh.Object);
		PlotMesh->SetRelativeScale3D(FVector(1.5f, 1.5f, 0.4f));
		PlotMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
	}

	InteractionBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractionBox"));
	InteractionBox->SetupAttachment(SceneRoot);
	InteractionBox->SetBoxExtent(FVector(200.0f, 200.0f, 50.0f));
	InteractionBox->SetCollisionProfileName(TEXT("Trigger"));
}

void AFarmPlotActor::BeginPlay()
{
	Super::BeginPlay();

	if (Tiles.Num() == 0)
	{
		InitializePlot();
	}
}

void AFarmPlotActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	for (FFarmTile& Tile : Tiles)
	{
		if (Tile.State == EFarmTileState::Watered && Tile.PlantedCrop)
		{
			Tile.GrowthTimer += DeltaTime;
			if (Tile.GrowthTimer >= Tile.PlantedCrop->SecondsPerGrowthStage)
			{
				Tile.GrowthTimer = 0.0f;
				Tile.CurrentGrowthStage++;
				Tile.bIsWatered = false;

				if (Tile.CurrentGrowthStage >= Tile.PlantedCrop->TotalGrowthStages)
				{
					Tile.State = EFarmTileState::Mature;

					// Determine harvest quality
					const float Roll = FMath::FRand();
					if (Roll <= Tile.PlantedCrop->PristineQualityChance)
					{
						Tile.CropQuality = ECropQuality::Pristine;
					}
					else if (Roll <= (Tile.PlantedCrop->PristineQualityChance + Tile.PlantedCrop->HighQualityChance))
					{
						Tile.CropQuality = ECropQuality::High;
					}
					else
					{
						Tile.CropQuality = ECropQuality::Normal;
					}
				}
				else
				{
					// Still growing, waiting for next watering
					Tile.State = EFarmTileState::Planted;
				}

				OnTileStateChanged.Broadcast(Tile.GridX, Tile.GridY, Tile.State);
			}
		}
	}
}

void AFarmPlotActor::SetFarmTier(EBuildingTier NewTier)
{
	FarmTier = NewTier;
	const int32 TVal = FTownBuildingRecord::GetTierValue(FarmTier);

	GridWidth = 2 + TVal;
	GridHeight = 2 + TVal;
	InitializePlot();
}

void AFarmPlotActor::InitializePlot()
{
	Tiles.Empty();
	Tiles.Reserve(GridWidth * GridHeight);

	for (int32 Y = 0; Y < GridHeight; ++Y)
	{
		for (int32 X = 0; X < GridWidth; ++X)
		{
			FFarmTile NewTile;
			NewTile.GridX = X;
			NewTile.GridY = Y;
			NewTile.State = EFarmTileState::Untilled;
			NewTile.PlantedCrop = nullptr;
			NewTile.CurrentGrowthStage = 0;
			NewTile.GrowthTimer = 0.0f;
			NewTile.bIsWatered = false;
			NewTile.CropQuality = ECropQuality::Normal;

			Tiles.Add(NewTile);
		}
	}

	// Adjust collision box to span the whole plot
	const float HalfW = (GridWidth * TileSpacing) * 0.5f;
	const float HalfH = (GridHeight * TileSpacing) * 0.5f;
	InteractionBox->SetBoxExtent(FVector(HalfW, HalfH, 60.0f));
	InteractionBox->SetRelativeLocation(FVector(HalfW - (TileSpacing * 0.5f), HalfH - (TileSpacing * 0.5f), 30.0f));
}

int32 AFarmPlotActor::GetIndex(int32 X, int32 Y) const
{
	return Y * GridWidth + X;
}

bool AFarmPlotActor::IsValidCoord(int32 X, int32 Y) const
{
	return X >= 0 && X < GridWidth && Y >= 0 && Y < GridHeight;
}

bool AFarmPlotActor::GetTileCoordinatesFromLocation(const FVector& WorldLocation, int32& OutX, int32& OutY) const
{
	const FVector LocalPos = GetActorTransform().InverseTransformPosition(WorldLocation);
	OutX = FMath::FloorToInt((LocalPos.X + (TileSpacing * 0.5f)) / TileSpacing);
	OutY = FMath::FloorToInt((LocalPos.Y + (TileSpacing * 0.5f)) / TileSpacing);

	return IsValidCoord(OutX, OutY);
}

bool AFarmPlotActor::TillTile(int32 X, int32 Y)
{
	if (!IsValidCoord(X, Y)) return false;

	const int32 Idx = GetIndex(X, Y);
	if (Tiles[Idx].State == EFarmTileState::Untilled)
	{
		Tiles[Idx].State = EFarmTileState::Tilled;
		OnTileStateChanged.Broadcast(X, Y, Tiles[Idx].State);
		return true;
	}
	return false;
}

bool AFarmPlotActor::PlantCrop(int32 X, int32 Y, UCropDataAsset* InCrop)
{
	if (!IsValidCoord(X, Y) || !InCrop) return false;

	const int32 Idx = GetIndex(X, Y);
	if (Tiles[Idx].State == EFarmTileState::Tilled)
	{
		Tiles[Idx].State = EFarmTileState::Planted;
		Tiles[Idx].PlantedCrop = InCrop;
		Tiles[Idx].CurrentGrowthStage = 0;
		Tiles[Idx].GrowthTimer = 0.0f;
		Tiles[Idx].bIsWatered = false;
		OnTileStateChanged.Broadcast(X, Y, Tiles[Idx].State);
		return true;
	}
	return false;
}

bool AFarmPlotActor::WaterTile(int32 X, int32 Y)
{
	if (!IsValidCoord(X, Y)) return false;

	const int32 Idx = GetIndex(X, Y);
	if (Tiles[Idx].State == EFarmTileState::Planted)
	{
		Tiles[Idx].bIsWatered = true;
		Tiles[Idx].State = EFarmTileState::Watered;
		OnTileStateChanged.Broadcast(X, Y, Tiles[Idx].State);
		return true;
	}
	else if (Tiles[Idx].State == EFarmTileState::Tilled)
	{
		Tiles[Idx].bIsWatered = true;
		return true;
	}
	return false;
}

bool AFarmPlotActor::HarvestTile(int32 X, int32 Y, FName& OutHarvestItemID, int32& OutYield, ECropQuality& OutQuality)
{
	if (!IsValidCoord(X, Y)) return false;

	const int32 Idx = GetIndex(X, Y);
	FFarmTile& Tile = Tiles[Idx];

	if (Tile.State == EFarmTileState::Mature && Tile.PlantedCrop)
	{
		OutHarvestItemID = Tile.PlantedCrop->HarvestedItemID;
		OutYield = FMath::RandRange(Tile.PlantedCrop->MinHarvestYield, Tile.PlantedCrop->MaxHarvestYield);
		const int32 TVal = FTownBuildingRecord::GetTierValue(FarmTier);
		if (Tile.CropQuality == ECropQuality::Pristine || TVal >= 3)
		{
			OutYield += 1;
		}
		if (TVal >= 5) // Arcane Soil yield surge
		{
			OutYield = FMath::RoundToInt(OutYield * 1.5f);
		}
		OutQuality = Tile.CropQuality;

		OnCropHarvested.Broadcast(X, Y, OutHarvestItemID, OutYield);

		// Deposit harvested crops into Town Stockpile (Food category)
		for (TActorIterator<AAdventurerGuildBoardActor> It(GetWorld()); It; ++It)
		{
			if (AAdventurerGuildBoardActor* Board = *It)
			{
				if (Board->AdventurerManager)
				{
					Board->AdventurerManager->TownStockpile.AddStock(EStockpileCategory::Food, OutHarvestItemID, OutYield);
					break;
				}
			}
		}

		// Reset tile to tilled
		Tile.State = EFarmTileState::Tilled;
		Tile.PlantedCrop = nullptr;
		Tile.CurrentGrowthStage = 0;
		Tile.GrowthTimer = 0.0f;
		Tile.bIsWatered = false;
		Tile.CropQuality = ECropQuality::Normal;

		OnTileStateChanged.Broadcast(X, Y, Tile.State);
		return true;
	}

	return false;
}

bool AFarmPlotActor::ClearTile(int32 X, int32 Y)
{
	if (!IsValidCoord(X, Y)) return false;

	const int32 Idx = GetIndex(X, Y);
	FFarmTile& Tile = Tiles[Idx];

	if (Tile.State == EFarmTileState::Withered)
	{
		Tile.State = EFarmTileState::Untilled;
		Tile.PlantedCrop = nullptr;
		Tile.CurrentGrowthStage = 0;
		Tile.GrowthTimer = 0.0f;
		Tile.bIsWatered = false;
		OnTileStateChanged.Broadcast(X, Y, Tile.State);
		return true;
	}
	return false;
}

void AFarmPlotActor::AdvanceDay()
{
	for (FFarmTile& Tile : Tiles)
	{
		if ((Tile.State == EFarmTileState::Watered || Tile.bIsWatered) && Tile.PlantedCrop)
		{
			Tile.CurrentGrowthStage++;
			Tile.bIsWatered = false;

			if (Tile.CurrentGrowthStage >= Tile.PlantedCrop->TotalGrowthStages)
			{
				Tile.State = EFarmTileState::Mature;
			}
			else
			{
				Tile.State = EFarmTileState::Planted;
			}
			OnTileStateChanged.Broadcast(Tile.GridX, Tile.GridY, Tile.State);
		}
		else if (Tile.State == EFarmTileState::Planted && !Tile.bIsWatered)
		{
			// Left unwatered for a whole day: risk of withering
			Tile.State = EFarmTileState::Withered;
			OnTileStateChanged.Broadcast(Tile.GridX, Tile.GridY, Tile.State);
		}
	}
}

EFarmTileState AFarmPlotActor::GetTileState(int32 X, int32 Y) const
{
	if (!IsValidCoord(X, Y)) return EFarmTileState::Untilled;
	return Tiles[GetIndex(X, Y)].State;
}
