// Copyright Epic Games, Inc. All Rights Reserved.
// TitleSystemTypes.h — Tales of Title progression, stat growth modifiers, and passives

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "TitleSystemTypes.generated.h"

class UTexture2D;

UENUM(BlueprintType)
enum class ETitleStatType : uint8
{
	MaxHP        UMETA(DisplayName = "Max HP"),
	MaxTP        UMETA(DisplayName = "Max TP"),
	PhysicalAtk  UMETA(DisplayName = "Physical Attack"),
	PhysicalDef  UMETA(DisplayName = "Physical Defense"),
	ArteAtk      UMETA(DisplayName = "Arte / Magic Attack"),
	ArteDef      UMETA(DisplayName = "Arte / Magic Defense"),
	CritRate     UMETA(DisplayName = "Critical Strike Rate"),
	SpeedBoost   UMETA(DisplayName = "Movement Speed")
};

USTRUCT(BlueprintType)
struct FTitleStatBonus
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Stats")
	ETitleStatType StatType = ETitleStatType::PhysicalAtk;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Stats")
	float BonusValue = 10.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Stats")
	bool bIsPercentage = false;
};

/**
 * Tales Title Data Asset (e.g. "Combo Master", "Demon Slayer", "Novice Cook", "Berserker")
 */
UCLASS(BlueprintType, ClassGroup = (TalesProgression))
class ISEKAIVILLAGE_API UTitleDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Info")
	FName TitleID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Info")
	FText TitleName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Info")
	FText Description = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Info")
	FText UnlockCondition = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title Info")
	TObjectPtr<UTexture2D> TitleIcon = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonuses")
	TArray<FTitleStatBonus> StatBonuses;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Passives")
	FName PassivePerkID = NAME_None; // e.g. "DemonBane", "FastCast", "TPConserve"

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Passives")
	FText PassivePerkDescription = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mastery")
	int32 RequiredMasteryExp = 500;
};

USTRUCT(BlueprintType)
struct FTitleProgressState
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title")
	TObjectPtr<UTitleDataAsset> TitleAsset = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title")
	int32 CurrentMasteryExp = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Title")
	bool bIsMastered = false;
};
