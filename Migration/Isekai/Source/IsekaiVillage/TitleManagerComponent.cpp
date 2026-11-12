// Copyright Epic Games, Inc. All Rights Reserved.
// TitleManagerComponent.cpp — Implementation of Title manager component

#include "TitleManagerComponent.h"

UTitleManagerComponent::UTitleManagerComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UTitleManagerComponent::BeginPlay()
{
	Super::BeginPlay();
}

bool UTitleManagerComponent::UnlockTitle(UTitleDataAsset* NewTitle)
{
	if (!NewTitle) return false;

	for (const FTitleProgressState& State : UnlockedTitles)
	{
		if (State.TitleAsset && State.TitleAsset->TitleID == NewTitle->TitleID)
		{
			return false; // Already unlocked
		}
	}

	FTitleProgressState NewState;
	NewState.TitleAsset = NewTitle;
	NewState.CurrentMasteryExp = 0;
	NewState.bIsMastered = false;
	UnlockedTitles.Add(NewState);

	// If no title equipped, auto-equip the first unlocked title
	if (!EquippedTitle)
	{
		EquippedTitle = NewTitle;
		OnTitleEquipped.Broadcast(EquippedTitle);
	}

	return true;
}

bool UTitleManagerComponent::EquipTitle(FName TitleID)
{
	for (const FTitleProgressState& State : UnlockedTitles)
	{
		if (State.TitleAsset && State.TitleAsset->TitleID == TitleID)
		{
			EquippedTitle = State.TitleAsset;
			OnTitleEquipped.Broadcast(EquippedTitle);
			return true;
		}
	}
	return false;
}

void UTitleManagerComponent::AddMasteryExp(int32 ExpAmount)
{
	if (!EquippedTitle || ExpAmount <= 0) return;

	for (FTitleProgressState& State : UnlockedTitles)
	{
		if (State.TitleAsset == EquippedTitle)
		{
			if (State.bIsMastered) return;

			State.CurrentMasteryExp += ExpAmount;
			if (State.CurrentMasteryExp >= State.TitleAsset->RequiredMasteryExp)
			{
				State.bIsMastered = true;
				OnTitleMastered.Broadcast(State.TitleAsset);
			}
			break;
		}
	}
}

float UTitleManagerComponent::GetTotalStatBonus(ETitleStatType StatType) const
{
	if (!EquippedTitle) return 0.0f;

	float Total = 0.0f;
	for (const FTitleStatBonus& Bonus : EquippedTitle->StatBonuses)
	{
		if (Bonus.StatType == StatType)
		{
			Total += Bonus.BonusValue;
		}
	}
	return Total;
}

bool UTitleManagerComponent::HasPassivePerk(FName PerkID) const
{
	if (PerkID == NAME_None) return false;

	// Check currently equipped title
	if (EquippedTitle && EquippedTitle->PassivePerkID == PerkID)
	{
		return true;
	}

	// Also check mastered titles (mastered title passives stay with the hero!)
	for (const FTitleProgressState& State : UnlockedTitles)
	{
		if (State.bIsMastered && State.TitleAsset && State.TitleAsset->PassivePerkID == PerkID)
		{
			return true;
		}
	}

	return false;
}
