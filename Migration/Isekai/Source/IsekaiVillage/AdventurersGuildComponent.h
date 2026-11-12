// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurersGuildComponent.h — Manages Guild Rank, Quest Tracking, Bounties, and Promotion Trials

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "AdventurersGuildTypes.h"
#include "TownEconomyTypes.h"
#include "AdventurersGuildComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnQuestStateChanged, const FAdventurerQuest&, Quest);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnGuildRankChanged, EGuildRank, NewRank, int32, Reputation);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnReputationEarned, int32, AddedReputation, int32, TotalReputation);

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UAdventurersGuildComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UAdventurersGuildComponent();

	virtual void BeginPlay() override;

	// ── Tier & Rank ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild|Tier")
	EBuildingTier GuildTier = EBuildingTier::Tier_1_Rustic;

	UFUNCTION(BlueprintPure, Category = "Guild|Tier")
	int32 GetMaxConcurrentExpeditions() const { return 2 + static_cast<int32>(GuildTier); }

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild|Rank")
	EGuildRank CurrentRank = EGuildRank::Copper;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guild|Rank")
	int32 GuildReputation = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild|Rank")
	int32 ReputationPerRank = 500;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guild|Stats")
	int32 TotalBountiesClaimed = 0;

	// ── Quests ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guild|Quests")
	TArray<FAdventurerQuest> ActiveQuests;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guild|Quests")
	TArray<FName> CompletedQuestIDs;

	// ── Events ──
	UPROPERTY(BlueprintAssignable, Category = "Guild|Events")
	FOnQuestStateChanged OnQuestAccepted;

	UPROPERTY(BlueprintAssignable, Category = "Guild|Events")
	FOnQuestStateChanged OnQuestProgressUpdated;

	UPROPERTY(BlueprintAssignable, Category = "Guild|Events")
	FOnQuestStateChanged OnQuestCompleted;

	UPROPERTY(BlueprintAssignable, Category = "Guild|Events")
	FOnGuildRankChanged OnGuildRankPromoted;

	UPROPERTY(BlueprintAssignable, Category = "Guild|Events")
	FOnReputationEarned OnReputationUpdated;

	// ── Operations ──
	UFUNCTION(BlueprintCallable, Category = "Guild|Quests")
	bool AcceptQuest(const FAdventurerQuest& NewQuest);

	UFUNCTION(BlueprintCallable, Category = "Guild|Quests")
	void AbandonQuest(FName QuestID);

	/** Called when monsters are defeated or items collected */
	UFUNCTION(BlueprintCallable, Category = "Guild|Quests")
	void ReportProgress(FName TargetID, int32 Amount = 1);

	UFUNCTION(BlueprintCallable, Category = "Guild|Quests")
	bool TurnInQuest(FName QuestID);

	UFUNCTION(BlueprintPure, Category = "Guild|Rank")
	bool CanRankUp() const;

	UFUNCTION(BlueprintCallable, Category = "Guild|Rank")
	bool PromoteRank();

	/** Guild discount on town shop purchases (0% to 25%) */
	UFUNCTION(BlueprintPure, Category = "Guild|Perks")
	float GetGuildShopDiscount() const;

	/** Get human-readable title for current rank */
	UFUNCTION(BlueprintPure, Category = "Guild|Rank")
	FText GetRankDisplayName() const;
};
