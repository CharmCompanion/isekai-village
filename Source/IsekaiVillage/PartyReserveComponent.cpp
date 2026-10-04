// Copyright Epic Games, Inc. All Rights Reserved.

#include "PartyReserveComponent.h"

UPartyReserveComponent::UPartyReserveComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

int32 UPartyReserveComponent::GetActiveCompanionCount() const
{
	int32 Count = 0;
	for (const FHiredAdventurer& Adventurer : Reserve)
	{
		if (Adventurer.bInActiveParty)
		{
			++Count;
		}
	}
	return Count;
}

bool UPartyReserveComponent::HireAdventurer(FText Name)
{
	if (Reserve.Num() >= MaxReserve)
	{
		return false;
	}

	FHiredAdventurer Hired;
	Hired.AdventurerID = FName(*FString::Printf(TEXT("Adv_%d"), Reserve.Num() + 1));
	Hired.Name = Name.IsEmpty() ? FText::FromString(TEXT("Guild Recruit")) : Name;
	Hired.Rank = 0;
	Hired.bInActiveParty = GetActiveCompanionCount() < GetMaxCompanions();
	Hired.bAssignedToRampage = false;
	Reserve.Add(Hired);
	return true;
}
