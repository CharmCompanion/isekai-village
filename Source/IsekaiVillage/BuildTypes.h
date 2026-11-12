// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "BuildTypes.generated.h"

UENUM(BlueprintType)
enum class EBuildPieceType : uint8
{
	Foundation,
	Floor,
	Wall,
	Doorway,
	Stair,
	Roof,
	Pillar
};

UENUM(BlueprintType)
enum class EBuildOccupancy : uint8
{
	Full,
	Half,
	Quarter,
	LShape
};

UENUM(BlueprintType)
enum class EBuildCornerStyle : uint8
{
	Sharp,
	Diagonal,
	Curved
};

UENUM(BlueprintType)
enum class EBuildWallStyle : uint8
{
	Straight,
	Diagonal45,
	CurvedArc
};

UENUM(BlueprintType)
enum class EBuildMaterialStyle : uint8
{
	WoodPlank,
	FieldStone,
	CutStone,
	Brick,
	MetalSheet,
	WhitePlaster,
	WallpaperStripes,
	WallpaperFloral,
	WoodWainscot
};

UENUM(BlueprintType)
enum class EDebrisType : uint8
{
	CharredTimber,
	StoneRubble,
	ScrapMetal,
	RuinedStructure
};

UENUM(BlueprintType)
enum class ERoomFunction : uint8
{
	EmptyHall,
	Blacksmith,
	Inn,
	Shop,
	AdventurersGuild,
	Bakery,
	Farmhouse,
	Treasure,
	MonsterDen,
	BossLair,
	Vault,
	AlchemistLab,
	Enchanter,
	ArcaneForge
};

UENUM(BlueprintType)
enum class EDungeonMarkerType : uint8
{
	Entrance,
	Exit,
	Trap,
	MonsterSpawn,
	Treasure,
	Boss,
	Vault
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FBuildCorner
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildCornerStyle Style = EBuildCornerStyle::Sharp;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FVector2D Offset = FVector2D::ZeroVector;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FBuildMaterialAssignment
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildMaterialStyle ExteriorMaterial = EBuildMaterialStyle::FieldStone;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildMaterialStyle InteriorMaterial = EBuildMaterialStyle::WhitePlaster;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildMaterialStyle TrimMaterial = EBuildMaterialStyle::WoodPlank;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FLinearColor ExteriorTint = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FLinearColor InteriorTint = FLinearColor::White;
};
