// Copyright Epic Games, Inc. All Rights Reserved.
// SkillGridTypes.h — Tales of Arise / Xillia style Skill Sphere & Arte Grid types

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "TitleSystemTypes.h"
#include "SkillGridTypes.generated.h"

class UTexture2D;

UENUM(BlueprintType)
enum class ESkillNodeType : uint8
{
	StatBoost      UMETA(DisplayName = "Permanent Stat Boost"),
	ArteUnlock     UMETA(DisplayName = "Arte / Spell Unlock"),
	CombatPassive  UMETA(DisplayName = "Combat Passive Perk"),
	OverlimitPerk  UMETA(DisplayName = "Overlimit Enhancement"),
	TownAction     UMETA(DisplayName = "Town Action Unlock")
};

UENUM(BlueprintType)
enum class EDiscCategory : uint8
{
	CenterA_Life          UMETA(DisplayName = "Center A (Life)"),
	CenterA_Adventurer    UMETA(DisplayName = "Center A (Adventurer - Coin Flip)"),
	CenterB_Work          UMETA(DisplayName = "Center B (Work)"),
	CenterB_Villager      UMETA(DisplayName = "Center B (Villager - Coin Flip)"),
	CombatMelee           UMETA(DisplayName = "Combat Melee (Lloyd Style)"),
	CombatMagic           UMETA(DisplayName = "Combat Magic (Genis Style)"),
	CombatCleric          UMETA(DisplayName = "Combat Cleric (Raine Style)"),
	CombatRanger          UMETA(DisplayName = "Combat Ranger"),
	TownCrafting          UMETA(DisplayName = "Town Crafting"),
	TownDomain            UMETA(DisplayName = "Town Domain"),
	TownEconomy           UMETA(DisplayName = "Town Economy & Hospitality"),
	AdvancedArchitect     UMETA(DisplayName = "Advanced Architect"),
	AdvancedDungeonMaster UMETA(DisplayName = "Advanced Dungeon Master")
};

USTRUCT(BlueprintType)
struct FSkillGridNode
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Node")
	FName NodeID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Node")
	FText NodeTitle = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Node")
	FText Description = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Node")
	ESkillNodeType NodeType = ESkillNodeType::StatBoost;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Node")
	int32 SPCost = 100;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Node")
	TArray<FName> RequiredPrerequisites;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stat Boost")
	ETitleStatType StatType = ETitleStatType::PhysicalAtk;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stat Boost")
	float StatBonusValue = 15.0f;

	// FFX Expert / Isekai Village specific node stats (~70% stat distribution)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 HP_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 TP_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Inventory_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 CarryWeight_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float MoveSpeed_Percent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float BuildSpeed_Percent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Trust_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Gald_Percent = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte or Perk")
	FName UnlockedArteOrPerkID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte or Perk")
	FName UnlockAction = NAME_None; // e.g. "HireCap+1", "RoomCap+2"

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UI Layout")
	FVector2D GridPosition = FVector2D::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "UI Layout")
	TObjectPtr<UTexture2D> NodeIcon = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connections")
	TArray<FName> ConnectedNodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Connections")
	bool bIsCenterNode = false;
};

/**
 * Single Disc / Sphere wheel definition in the 11-disc constellation.
 */
USTRUCT(BlueprintType)
struct FSphereDiscData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	FName DiscID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	FText DiscTitle = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	FText Description = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	EDiscCategory Category = EDiscCategory::CenterA_Life;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	TArray<FSkillGridNode> Nodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	FName CompletionBonusPerkID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	FText CompletionBonusDescription = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coin Flip")
	bool bIsCoinFlipDisc = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Coin Flip")
	FName FlipSideDiscID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Disc")
	TArray<FName> RequiredDiscPrerequisites;
};

/**
 * Data asset defining a complete character skill sphere or 11-disc constellation.
 */
UCLASS(BlueprintType, ClassGroup = (TalesProgression))
class ISEKAIVILLAGE_API USkillGridDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid Info")
	FName GridID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid Info")
	FText GridTitle = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grid Info")
	FText Description = FText::GetEmpty();

	// Primary single-disc nodes (backwards-compatible)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nodes")
	TArray<FSkillGridNode> Nodes;

	// Full 11-disc constellation (from Isekai Village GDD)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Sphere Constellation")
	TArray<FSphereDiscData> Discs;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Completion Bonus")
	FName CompletionBonusPerkID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Completion Bonus")
	FText CompletionBonusDescription = FText::GetEmpty();

	const FSphereDiscData* FindDisc(FName DiscID) const
	{
		for (const FSphereDiscData& Disc : Discs)
		{
			if (Disc.DiscID == DiscID) return &Disc;
		}
		return nullptr;
	}
};
