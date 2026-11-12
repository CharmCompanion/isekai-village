// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurersGuildComponent.cpp — Manages Guild Rank, Quest Tracking, Bounties, and Promotion Trials

#include "AdventurersGuildComponent.h"
#include "Kismet/GameplayStatics.h"

UAdventurersGuildComponent::UAdventurersGuildComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
	CurrentRank = EGuildRank::Copper;
	GuildReputation = 0;
	ReputationPerRank = 500;
}

void UAdventurersGuildComponent::BeginPlay()
{
	Super::BeginPlay();
}

bool UAdventurersGuildComponent::AcceptQuest(const FAdventurerQuest& NewQuest)
{
	if (NewQuest.QuestID == NAME_None) return false;

	// Check if already active or completed
	if (CompletedQuestIDs.Contains(NewQuest.QuestID)) return false;
	for (const FAdventurerQuest& Q : ActiveQuests)
	{
		if (Q.QuestID == NewQuest.QuestID) return false;
	}

	// Check rank requirement
	if (static_cast<uint8>(CurrentRank) < static_cast<uint8>(NewQuest.RequiredRank))
	{
		return false;
	}

	FAdventurerQuest Accepted = NewQuest;
	Accepted.State = EQuestState::Active;
	Accepted.CurrentCount = 0;

	ActiveQuests.Add(Accepted);
	OnQuestAccepted.Broadcast(Accepted);
	return true;
}

void UAdventurersGuildComponent::AbandonQuest(FName QuestID)
{
	for (int32 i = ActiveQuests.Num() - 1; i >= 0; --i)
	{
		if (ActiveQuests[i].QuestID == QuestID)
		{
			ActiveQuests.RemoveAt(i);
			break;
		}
	}
}

void UAdventurersGuildComponent::ReportProgress(FName TargetID, int32 Amount)
{
	if (TargetID == NAME_None || Amount <= 0) return;

	for (FAdventurerQuest& Quest : ActiveQuests)
	{
		if (Quest.State == EQuestState::Active && Quest.TargetID == TargetID)
		{
			Quest.CurrentCount = FMath::Min(Quest.RequiredCount, Quest.CurrentCount + Amount);
			if (Quest.CurrentCount >= Quest.RequiredCount)
			{
				Quest.State = EQuestState::ReadyToTurnIn;
			}
			OnQuestProgressUpdated.Broadcast(Quest);
		}
	}
}

bool UAdventurersGuildComponent::TurnInQuest(FName QuestID)
{
	for (int32 i = 0; i < ActiveQuests.Num(); ++i)
	{
		if (ActiveQuests[i].QuestID == QuestID && ActiveQuests[i].State == EQuestState::ReadyToTurnIn)
		{
			FAdventurerQuest Finished = ActiveQuests[i];
			Finished.State = EQuestState::Completed;

			// Add Reputation
			GuildReputation += Finished.RewardReputation;
			OnReputationUpdated.Broadcast(Finished.RewardReputation, GuildReputation);

			// Track stats
			TotalBountiesClaimed++;
			CompletedQuestIDs.Add(QuestID);
			ActiveQuests.RemoveAt(i);

			OnQuestCompleted.Broadcast(Finished);

			// Check auto-promotion opportunity
			if (CanRankUp())
			{
				PromoteRank();
			}

			return true;
		}
	}

	return false;
}

bool UAdventurersGuildComponent::CanRankUp() const
{
	if (CurrentRank >= EGuildRank::Diamond) return false;

	const int32 RequiredRep = ReputationPerRank * (static_cast<int32>(CurrentRank) + 1);
	return GuildReputation >= RequiredRep;
}

bool UAdventurersGuildComponent::PromoteRank()
{
	if (!CanRankUp()) return false;

	uint8 NextRankInt = static_cast<uint8>(CurrentRank) + 1;
	CurrentRank = static_cast<EGuildRank>(NextRankInt);

	OnGuildRankPromoted.Broadcast(CurrentRank, GuildReputation);
	return true;
}

float UAdventurersGuildComponent::GetGuildShopDiscount() const
{
	switch (CurrentRank)
	{
	case EGuildRank::Iron:     return 0.05f; // 5% off
	case EGuildRank::Bronze:   return 0.08f; // 8% off
	case EGuildRank::Silver:   return 0.12f; // 12% off
	case EGuildRank::Gold:     return 0.16f; // 16% off
	case EGuildRank::Platinum: return 0.20f; // 20% off
	case EGuildRank::Diamond:  return 0.25f; // 25% off
	case EGuildRank::Copper:
	default:                   return 0.0f;
	}
}

FText UAdventurersGuildComponent::GetRankDisplayName() const
{
	switch (CurrentRank)
	{
	case EGuildRank::Iron:     return FText::FromString(TEXT("Iron Rank"));
	case EGuildRank::Bronze:   return FText::FromString(TEXT("Bronze Rank"));
	case EGuildRank::Silver:   return FText::FromString(TEXT("Silver Rank"));
	case EGuildRank::Gold:     return FText::FromString(TEXT("Gold Rank"));
	case EGuildRank::Platinum: return FText::FromString(TEXT("Platinum Rank"));
	case EGuildRank::Diamond:  return FText::FromString(TEXT("Diamond Rank"));
	case EGuildRank::Copper:
	default:                   return FText::FromString(TEXT("Copper Rank"));
	}
}
