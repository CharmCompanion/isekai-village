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

/** One modular piece stored relative to a template's anchor. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FBuildTemplatePiece
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildPieceType PieceType = EBuildPieceType::Wall;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildOccupancy Occupancy = EBuildOccupancy::Full;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildWallStyle WallStyle = EBuildWallStyle::Straight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FBuildMaterialAssignment Materials;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FVector RelativeLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float RelativeYaw = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FVector ScaleMultiplier = FVector(1.0f, 1.0f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	uint8 SectionMask = 0x0F;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	TArray<FBuildCorner> Corners;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float CellSize = 200.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float WallHeight = 280.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float Thickness = 18.0f;
};

/** One furniture prop stored relative to a template's anchor. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FBuildTemplateProp
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FName PropTag = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FVector RelativeLocation = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float RelativeYaw = 0.0f;
};

/** A saved building: modular pieces and linchpin props, shareable as JSON. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FBuildTemplate
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FString Name;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	TArray<FBuildTemplatePiece> Pieces;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	TArray<FBuildTemplateProp> Props;
};
