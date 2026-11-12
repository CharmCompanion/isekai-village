// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "BuildTypes.h"
#include "DungeonGraphData.generated.h"

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FDungeonRoom
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName RoomId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FVector Center = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FVector2D Size = FVector2D(800.0f, 800.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	ERoomFunction Function = ERoomFunction::EmptyHall;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FDungeonHall
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName FromRoom;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName ToRoom;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	float Width = 280.0f;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FDungeonMarker
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	EDungeonMarkerType Type = EDungeonMarkerType::Treasure;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName RoomId;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FVector LocalOffset = FVector::ZeroVector;
};

UCLASS(BlueprintType)
class ISEKAIVILLAGE_API UDungeonGraphData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName GraphId = TEXT("ElRuhnSealedCave");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FText DisplayName = FText::FromString(TEXT("El Ruhn Sealed Cave"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	TArray<FDungeonRoom> Rooms;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	TArray<FDungeonHall> Halls;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	TArray<FDungeonMarker> Markers;

	virtual FPrimaryAssetId GetPrimaryAssetId() const override
	{
		return FPrimaryAssetId(TEXT("DungeonGraph"), GraphId);
	}

	static UDungeonGraphData* CreateElRuhnStarter();
};
