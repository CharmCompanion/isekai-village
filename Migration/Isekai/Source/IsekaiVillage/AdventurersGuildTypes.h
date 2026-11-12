// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurersGuildTypes.h — Guild Ranks, Quest Categories, Bounty Contracts, and Data Assets

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "AdventurersGuildTypes.generated.h"

/**
 * Guild Ranks representing adventurer prowess and clearance level.
 */
UENUM(BlueprintType)
enum class EGuildRank : uint8
{
	Copper   UMETA(DisplayName = "Copper (Novice)"),
	Iron     UMETA(DisplayName = "Iron (Apprentice)"),
	Bronze   UMETA(DisplayName = "Bronze (Journeyman)"),
	Silver   UMETA(DisplayName = "Silver (Veteran)"),
	Gold     UMETA(DisplayName = "Gold (Elite)"),
	Platinum UMETA(DisplayName = "Platinum (Master)"),
	Diamond  UMETA(DisplayName = "Diamond (Heroic / Grandmaster)")
};

/**
 * Categories of Adventurers Guild contracts.
 */
UENUM(BlueprintType)
enum class EQuestCategory : uint8
{
	DemonSubjugation    UMETA(DisplayName = "Demon Subjugation / Bounty"),
	ResourceGathering   UMETA(DisplayName = "Resource Gathering / Harvest"),
	DungeonInvestigation UMETA(DisplayName = "Dungeon Investigation"),
	RescueEscort        UMETA(DisplayName = "Rescue & Escort")
};

/**
 * Lifecycle state of an adventurer quest.
 */
UENUM(BlueprintType)
enum class EQuestState : uint8
{
	Available,
	Active,
	ReadyToTurnIn,
	Completed,
	Failed
};

/**
 * Individual quest contract structure.
 */
USTRUCT(BlueprintType)
struct FAdventurerQuest
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	FName QuestID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	FText Title = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	FText Description = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	EQuestCategory Category = EQuestCategory::DemonSubjugation;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	EGuildRank RequiredRank = EGuildRank::Copper;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	FName TargetID = TEXT("LesserImp");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Quest")
	int32 RequiredCount = 3;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Quest")
	int32 CurrentCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Quest")
	EQuestState State = EQuestState::Available;

	// ── Rewards ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
	int32 RewardGald = 250;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
	int32 RewardExp = 150;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
	int32 RewardSP = 25;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
	int32 RewardReputation = 50;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Rewards")
	FName RewardItemID = NAME_None;
};

/**
 * Data asset for hand-crafted quest blueprints & rank promotion trials.
 */
UCLASS(BlueprintType)
class ISEKAIVILLAGE_API UQuestDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Quest")
	FAdventurerQuest QuestData;
};
