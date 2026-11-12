// Copyright Epic Games, Inc. All Rights Reserved.

#include "PartyReserveComponent.h"
#include "IsekaiVillageCharacter.h"
#include "VillageRuntime.h"
#include "EngineUtils.h"

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
	Hired.GolemId=FGuid::NewGuid();UGolemNeedsLibrary::Initialize(Hired.Drives,Hired.GolemId);
	Hired.bInActiveParty = GetActiveCompanionCount() < GetMaxCompanions();
	Hired.bAssignedToRampage = false;
	Reserve.Add(Hired);
	return true;
}

bool UPartyReserveComponent::RecordAdventurerPractice(FName Id,FName Domain,float Effort,bool Success)
{
 FHiredAdventurer* A=Reserve.FindByPredicate([&](const FHiredAdventurer& R){return R.AdventurerID==Id;});
 if(!A || A->bAssignedToRampage)return false;
 const AIsekaiVillageCharacter* OwnerChar=Cast<AIsekaiVillageCharacter>(GetOwner());
 const float ScaledEffort=(OwnerChar && OwnerChar->HasSphereSkill(TEXT("SoulImprint")))?Effort*1.5f:Effort;
 const bool Learned=UGolemNeedsLibrary::RecordPractice(A->Drives,Domain,ScaledEffort,Success);RefreshLearnedArtes();
 if(GetWorld())for(TActorIterator<AVillageRuntime> It(GetWorld());It;++It)
  for(FVillageGolemRecord& R:It->GolemResidents)if(R.AdventurerId==Id)R.Drives=A->Drives;
 return Learned;
}
void UPartyReserveComponent::RefreshLearnedArtes()
{
 for(FHiredAdventurer& A:Reserve)for(FName Skill:A.Drives.Skills)
  if(const TObjectPtr<UArteDataAsset>* Definition=LearnedArteDefinitions.Find(Skill);Definition && *Definition)A.KnownArtes.AddUnique(*Definition);
}
