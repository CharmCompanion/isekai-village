// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurerManagerComponent.cpp — Implementation of adventurer recruitment, training, equipment, and guild dispatch

#include "AdventurerManagerComponent.h"
#include "SphereGridDataAsset.h"
#include "Engine/World.h"
#include "EngineUtils.h"
#include "LordsManorActor.h"

UAdventurerManagerComponent::UAdventurerManagerComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UAdventurerManagerComponent::BeginPlay()
{
	Super::BeginPlay();

	if (ActivePartyAdventurerIDs.Num() == 0)
	{
		ActivePartyAdventurerIDs.Init(NAME_None, 4);
	}
	if (AuxiliaryPartyBetaIDs.Num() == 0)
	{
		AuxiliaryPartyBetaIDs.Init(NAME_None, 4);
	}
	if (AuxiliaryPartyGammaIDs.Num() == 0)
	{
		AuxiliaryPartyGammaIDs.Init(NAME_None, 4);
	}

	if (VisitingAdventurers.Num() == 0)
	{
		RefreshVisitingAdventurers(4);
	}
}

void UAdventurerManagerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	for (FAdventurerExpedition& Expedition : ActiveExpeditions)
	{
		if (!Expedition.bIsCompleted)
		{
			Expedition.TimeElapsed += DeltaTime;
			if (Expedition.TimeElapsed >= Expedition.DurationSeconds)
			{
				Expedition.bIsCompleted = true;
				OnExpeditionCompleted.Broadcast(Expedition);
			}
		}
	}
}

void UAdventurerManagerComponent::RefreshVisitingAdventurers(int32 Count)
{
	VisitingAdventurers.Empty();
	VisitingAdventurers.Reserve(Count);

	static const TCHAR* NamePool[] = {
		TEXT("Kaelen"), TEXT("Lyra"), TEXT("Rowan"), TEXT("Seraphina"),
		TEXT("Darius"), TEXT("Vesper"), TEXT("Eldrin"), TEXT("Sylvia"),
		TEXT("Garrick"), TEXT("Talia"), TEXT("Fenris"), TEXT("Aurelia")
	};

	const int32 PoolSize = UE_ARRAY_COUNT(NamePool);

	for (int32 i = 0; i < Count; ++i)
	{
		FAdventurerProfile NewAdv;
		const int32 NameIdx = (i + FMath::RandRange(0, PoolSize - 1)) % PoolSize;
		NewAdv.Name = FText::FromString(NamePool[NameIdx]);
		NewAdv.AdventurerID = FName(*FString::Printf(TEXT("Adv_%s_%d"), NamePool[NameIdx], FMath::RandRange(100, 999)));

		// Random Class & Personality
		NewAdv.ClassType = static_cast<EAdventurerClass>(FMath::RandRange(0, 5));
		NewAdv.Personality = static_cast<EAdventurerPersonality>(FMath::RandRange(0, 17));

		NewAdv.Level = FMath::RandRange(1, 3);
		NewAdv.CurrentExp = 0;
		NewAdv.ExpToNextLevel = 100 * NewAdv.Level;

		// Attribute profiles by class
		switch (NewAdv.ClassType)
		{
		case EAdventurerClass::Swordsman:
			NewAdv.BaseHP = 480.0f; NewAdv.BaseTP = 80.0f; NewAdv.BaseAttack = 26.0f; NewAdv.BaseDefense = 18.0f; NewAdv.BaseArtePower = 18.0f;
			break;
		case EAdventurerClass::Berserker:
			NewAdv.BaseHP = 580.0f; NewAdv.BaseTP = 60.0f; NewAdv.BaseAttack = 34.0f; NewAdv.BaseDefense = 12.0f; NewAdv.BaseArtePower = 12.0f;
			break;
		case EAdventurerClass::Mage:
			NewAdv.BaseHP = 360.0f; NewAdv.BaseTP = 140.0f; NewAdv.BaseAttack = 16.0f; NewAdv.BaseDefense = 10.0f; NewAdv.BaseArtePower = 32.0f;
			break;
		case EAdventurerClass::Healer:
			NewAdv.BaseHP = 400.0f; NewAdv.BaseTP = 130.0f; NewAdv.BaseAttack = 18.0f; NewAdv.BaseDefense = 14.0f; NewAdv.BaseArtePower = 28.0f;
			break;
		case EAdventurerClass::Rogue:
			NewAdv.BaseHP = 420.0f; NewAdv.BaseTP = 90.0f; NewAdv.BaseAttack = 28.0f; NewAdv.BaseDefense = 14.0f; NewAdv.BaseArtePower = 20.0f;
			break;
		case EAdventurerClass::Paladin:
			NewAdv.BaseHP = 540.0f; NewAdv.BaseTP = 90.0f; NewAdv.BaseAttack = 22.0f; NewAdv.BaseDefense = 26.0f; NewAdv.BaseArtePower = 20.0f;
			break;
		}

		NewAdv.HiringCost = 150 + (NewAdv.Level * 75);
		NewAdv.Assignment = EAdventurerAssignment::RestingInTown;

		static const FName DishPool[] = {
			TEXT("Dish_Sandwich"), TEXT("Dish_Omelette"), TEXT("Dish_BeefStew"),
			TEXT("Dish_MaboCurry"), TEXT("Dish_FruitParfait"), TEXT("Dish_RoastDemonBoar")
		};
		NewAdv.FavoriteDishID = DishPool[FMath::RandRange(0, UE_ARRAY_COUNT(DishPool) - 1)];
		NewAdv.AdventurerRank = EAdventurerRank::Rank_E;
		NewAdv.Satisfaction = 75.0f;
		NewAdv.bWantsToLeave = false;
		NewAdv.DaysUntilDeparture = 0.0f;

		VisitingAdventurers.Add(NewAdv);
	}

	OnVisitingPoolRefreshed.Broadcast();
}

bool UAdventurerManagerComponent::HireAdventurer(FName AdventurerID, int32& PlayerGold)
{
	for (int32 i = 0; i < VisitingAdventurers.Num(); ++i)
	{
		if (VisitingAdventurers[i].AdventurerID == AdventurerID)
		{
			FAdventurerProfile Adv = VisitingAdventurers[i];
			if (PlayerGold < Adv.HiringCost)
			{
				return false; // Insufficient funds
			}

			PlayerGold -= Adv.HiringCost;
			Adv.Assignment = EAdventurerAssignment::RestingInTown;
			HiredAdventurers.Add(Adv);
			VisitingAdventurers.RemoveAt(i);

			// If active party has fewer than 4 members, auto-assign
			if (ActivePartyAdventurerIDs.Num() < 4)
			{
				AssignToActiveParty(Adv.AdventurerID, ActivePartyAdventurerIDs.Num());
			}

			OnAdventurerHired.Broadcast(Adv);
			return true;
		}
	}
	return false;
}

bool UAdventurerManagerComponent::DismissAdventurer(FName AdventurerID)
{
	RemoveFromActiveParty(AdventurerID);

	for (int32 i = 0; i < HiredAdventurers.Num(); ++i)
	{
		if (HiredAdventurers[i].AdventurerID == AdventurerID)
		{
			HiredAdventurers.RemoveAt(i);
			return true;
		}
	}
	return false;
}

FAdventurerProfile* UAdventurerManagerComponent::FindHiredAdventurer(FName AdventurerID)
{
	for (FAdventurerProfile& Adv : HiredAdventurers)
	{
		if (Adv.AdventurerID == AdventurerID)
		{
			return &Adv;
		}
	}
	return nullptr;
}

bool UAdventurerManagerComponent::TrainAdventurer(FName AdventurerID, int32 ExpAmount)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv || ExpAmount <= 0) return false;

	// Diligent personality gains bonus training EXP
	int32 FinalExp = ExpAmount;
	if (Adv->Personality == EAdventurerPersonality::Diligent)
	{
		FinalExp = FMath::RoundToInt(FinalExp * 1.30f);
	}

	// Mentorship bonus (+25% training EXP)
	if (Adv->MentorID != NAME_None)
	{
		FinalExp = FMath::RoundToInt(FinalExp * 1.25f);
	}

	Adv->CurrentExp += FinalExp;
	while (Adv->CurrentExp >= Adv->ExpToNextLevel)
	{
		LevelUpAdventurer(*Adv);
	}

	return true;
}

void UAdventurerManagerComponent::LevelUpAdventurer(FAdventurerProfile& Profile)
{
	Profile.Level++;
	Profile.CurrentExp -= Profile.ExpToNextLevel;
	Profile.ExpToNextLevel = FMath::RoundToInt(Profile.ExpToNextLevel * 1.35f);

	float GrowthMult = (Profile.AssignedLegacyCrest.CrestID != NAME_None) ? Profile.AssignedLegacyCrest.StatGrowthMultiplier : 1.0f;

	// Stat growth based on class and tier
	switch (Profile.ClassType)
	{
	case EAdventurerClass::Berserker:
	case EAdventurerClass::Gladiator:
	case EAdventurerClass::Warmaster:
	case EAdventurerClass::BloodReaver:
		Profile.BaseHP += 45.0f * GrowthMult;
		Profile.BaseTP += 8.0f * GrowthMult;
		Profile.BaseAttack += 5.5f * GrowthMult;
		Profile.BaseDefense += 2.5f * GrowthMult;
		Profile.BaseArtePower += 1.5f * GrowthMult;
		break;
	case EAdventurerClass::Mage:
	case EAdventurerClass::Sorcerer:
	case EAdventurerClass::Archmage:
	case EAdventurerClass::Arcanist:
		Profile.BaseHP += 25.0f * GrowthMult;
		Profile.BaseTP += 16.0f * GrowthMult;
		Profile.BaseAttack += 2.0f * GrowthMult;
		Profile.BaseDefense += 2.0f * GrowthMult;
		Profile.BaseArtePower += 5.5f * GrowthMult;
		break;
	case EAdventurerClass::Paladin:
	case EAdventurerClass::Knight:
	case EAdventurerClass::GuardianTemplar:
	case EAdventurerClass::Crusader:
		Profile.BaseHP += 40.0f * GrowthMult;
		Profile.BaseTP += 10.0f * GrowthMult;
		Profile.BaseAttack += 3.0f * GrowthMult;
		Profile.BaseDefense += 5.0f * GrowthMult;
		Profile.BaseArtePower += 2.5f * GrowthMult;
		break;
	default: // Swordsman, Warrior, Swordmaster, Rogue, Scout, Healer, Cleric, etc.
		Profile.BaseHP += 35.0f * GrowthMult;
		Profile.BaseTP += 12.0f * GrowthMult;
		Profile.BaseAttack += 4.0f * GrowthMult;
		Profile.BaseDefense += 3.5f * GrowthMult;
		Profile.BaseArtePower += 3.5f * GrowthMult;
		break;
	}

	// Update Adventurer Rank dynamically as they reach level milestones
	if (Profile.Level >= 90) Profile.AdventurerRank = EAdventurerRank::Rank_SSS;
	else if (Profile.Level >= 70) Profile.AdventurerRank = EAdventurerRank::Rank_SS;
	else if (Profile.Level >= 50) Profile.AdventurerRank = EAdventurerRank::Rank_S;
	else if (Profile.Level >= 40) Profile.AdventurerRank = EAdventurerRank::Rank_A;
	else if (Profile.Level >= 30) Profile.AdventurerRank = EAdventurerRank::Rank_B;
	else if (Profile.Level >= 20) Profile.AdventurerRank = EAdventurerRank::Rank_C;
	else if (Profile.Level >= 10) Profile.AdventurerRank = EAdventurerRank::Rank_D;
	else Profile.AdventurerRank = EAdventurerRank::Rank_E;

	Profile.ModifySatisfaction(10.0f);

	OnAdventurerLeveledUp.Broadcast(Profile, Profile.Level);
}

bool UAdventurerManagerComponent::EquipWeapon(FName AdventurerID, FName WeaponID, float AtkBonus, EElement WeaponElement)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	Adv->Equipment.WeaponID = WeaponID;
	Adv->Equipment.AddedAttack = AtkBonus;
	Adv->Equipment.WeaponElement = WeaponElement;

	OnAdventurerEquipmentChanged.Broadcast(AdventurerID, Adv->Equipment);
	return true;
}

bool UAdventurerManagerComponent::EquipArmor(FName AdventurerID, FName ArmorID, float DefBonus)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	Adv->Equipment.ArmorID = ArmorID;
	Adv->Equipment.AddedDefense = DefBonus;

	OnAdventurerEquipmentChanged.Broadcast(AdventurerID, Adv->Equipment);
	return true;
}

bool UAdventurerManagerComponent::EquipAccessory(FName AdventurerID, FName AccessoryID, float HPBonus, float TPBonus)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	Adv->Equipment.AccessoryID = AccessoryID;
	Adv->Equipment.AddedMaxHP = HPBonus;
	Adv->Equipment.AddedMaxTP = TPBonus;

	OnAdventurerEquipmentChanged.Broadcast(AdventurerID, Adv->Equipment);
	return true;
}

bool UAdventurerManagerComponent::UnequipSlot(FName AdventurerID, uint8 SlotIndex)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	switch (SlotIndex)
	{
	case 0: // Weapon
		Adv->Equipment.WeaponID = NAME_None;
		Adv->Equipment.AddedAttack = 0.0f;
		break;
	case 1: // Armor
		Adv->Equipment.ArmorID = NAME_None;
		Adv->Equipment.AddedDefense = 0.0f;
		break;
	case 2: // Accessory
		Adv->Equipment.AccessoryID = NAME_None;
		Adv->Equipment.AddedMaxHP = 0.0f;
		Adv->Equipment.AddedMaxTP = 0.0f;
		break;
	default:
		return false;
	}

	OnAdventurerEquipmentChanged.Broadcast(AdventurerID, Adv->Equipment);
	return true;
}

bool UAdventurerManagerComponent::AssignToActiveParty(FName AdventurerID, int32 PartySlotIndex)
{
	if (PartySlotIndex < 0 || PartySlotIndex >= 4) return false;

	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv || !Adv->CanDeployToBattle() || Adv->Assignment == EAdventurerAssignment::GuildExpedition)
	{
		return false; // Cannot assign if out on an expedition or on strike / unusable!
	}

	// Remove from auxiliary squads if previously assigned there
	RemoveFromAuxiliaryParty(AdventurerID, 0);

	// Remove from prior slot if present
	ActivePartyAdventurerIDs.Remove(AdventurerID);

	if (ActivePartyAdventurerIDs.Num() <= PartySlotIndex)
	{
		ActivePartyAdventurerIDs.SetNum(PartySlotIndex + 1);
	}

	// Release previous occupant of this slot
	FName PreviousOccupant = ActivePartyAdventurerIDs[PartySlotIndex];
	if (PreviousOccupant != NAME_None)
	{
		if (FAdventurerProfile* OldAdv = FindHiredAdventurer(PreviousOccupant))
		{
			OldAdv->Assignment = EAdventurerAssignment::RestingInTown;
		}
	}

	ActivePartyAdventurerIDs[PartySlotIndex] = AdventurerID;
	Adv->Assignment = EAdventurerAssignment::ActiveParty;
	OnPartyMentorshipCalculated.Broadcast(CalculateActivePartyMentorshipSynergy());
	return true;
}

bool UAdventurerManagerComponent::RemoveFromActiveParty(FName AdventurerID)
{
	for (int32 i = 0; i < ActivePartyAdventurerIDs.Num(); ++i)
	{
		if (ActivePartyAdventurerIDs[i] == AdventurerID)
		{
			ActivePartyAdventurerIDs[i] = NAME_None;
			if (FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID))
			{
				Adv->Assignment = EAdventurerAssignment::RestingInTown;
			}
			OnPartyMentorshipCalculated.Broadcast(CalculateActivePartyMentorshipSynergy());
			return true;
		}
	}
	return false;
}

bool UAdventurerManagerComponent::StartExpedition(const TArray<FName>& AdventurerIDs, FName ExpeditionID, const FText& ExpeditionName, float DurationSeconds, int32 GoldReward, int32 ExpReward, FName TargetBountyID)
{
	if (AdventurerIDs.Num() == 0) return false;

	// Verify adventurers are idle in town and not on strike
	for (const FName& AdvID : AdventurerIDs)
	{
		FAdventurerProfile* Adv = FindHiredAdventurer(AdvID);
		if (!Adv || !Adv->CanDeployToBattle() || Adv->Assignment != EAdventurerAssignment::RestingInTown)
		{
			return false;
		}
	}

	// Set status to expedition
	for (const FName& AdvID : AdventurerIDs)
	{
		if (FAdventurerProfile* Adv = FindHiredAdventurer(AdvID))
		{
			Adv->Assignment = EAdventurerAssignment::GuildExpedition;
		}
	}

	FAdventurerExpedition NewExp;
	NewExp.ExpeditionID = ExpeditionID;
	NewExp.ExpeditionName = ExpeditionName;
	NewExp.AssignedAdventurerIDs = AdventurerIDs;
	NewExp.DurationSeconds = FMath::Max(10.0f, DurationSeconds);
	NewExp.TimeElapsed = 0.0f;
	NewExp.TargetBountyID = TargetBountyID;
	NewExp.GoldReward = GoldReward;
	NewExp.ExpReward = ExpReward;
	NewExp.bIsCompleted = false;

	ActiveExpeditions.Add(NewExp);
	return true;
}

bool UAdventurerManagerComponent::ClaimExpeditionReward(FName ExpeditionID, int32& OutGoldReward, int32& OutExpReward)
{
	for (int32 i = 0; i < ActiveExpeditions.Num(); ++i)
	{
		if (ActiveExpeditions[i].ExpeditionID == ExpeditionID && ActiveExpeditions[i].bIsCompleted)
		{
			FAdventurerExpedition Exp = ActiveExpeditions[i];
			OutGoldReward = Exp.GoldReward;
			OutExpReward = Exp.ExpReward;

			// Reward each dispatched adventurer with training EXP and return them to town
			for (const FName& AdvID : Exp.AssignedAdventurerIDs)
			{
				if (FAdventurerProfile* Adv = FindHiredAdventurer(AdvID))
				{
					// Greedy personality earns extra gold!
					if (Adv->Personality == EAdventurerPersonality::Greedy)
					{
						OutGoldReward += FMath::RoundToInt(Exp.GoldReward * 0.25f);
					}

					Adv->Assignment = EAdventurerAssignment::RestingInTown;
					TrainAdventurer(AdvID, Exp.ExpReward);
				}
			}

			ActiveExpeditions.RemoveAt(i);
			return true;
		}
	}
	return false;
}

bool UAdventurerManagerComponent::GetAdventurerProfile(FName AdventurerID, FAdventurerProfile& OutProfile) const
{
	for (const FAdventurerProfile& Adv : HiredAdventurers)
	{
		if (Adv.AdventurerID == AdventurerID)
		{
			OutProfile = Adv;
			return true;
		}
	}
	for (const FAdventurerProfile& Adv : VisitingAdventurers)
	{
		if (Adv.AdventurerID == AdventurerID)
		{
			OutProfile = Adv;
			return true;
		}
	}
	return false;
}

bool UAdventurerManagerComponent::AssignMentor(FName MentorID, FName DiscipleID)
{
	if (MentorID == NAME_None || DiscipleID == NAME_None || MentorID == DiscipleID)
	{
		return false;
	}

	FAdventurerProfile* Mentor = FindHiredAdventurer(MentorID);
	FAdventurerProfile* Disciple = FindHiredAdventurer(DiscipleID);
	if (!Mentor || !Disciple) return false;

	// Mentor must be Level >= 15, Disciple must be Tier 1 (JobTier <= 1)
	if (Mentor->Level < 15 || Disciple->JobTier > 1)
	{
		return false;
	}

	// Remove previous mentorship if exists
	RemoveMentor(DiscipleID);

	FAdventurerMentorship Mentorship;
	Mentorship.MentorAdventurerID = MentorID;
	Mentorship.DiscipleAdventurerID = DiscipleID;
	Mentorship.BonusExpRate = 1.25f;
	Mentorship.InheritedPerkID = FName(*UEnum::GetValueAsString(Mentor->Personality));

	if (Mentor->LearnedArtes.Num() > 0)
	{
		Mentorship.InheritedArteID = Mentor->LearnedArtes[0];
		Disciple->CrossClassArtes.AddUnique(Mentorship.InheritedArteID);
	}

	Mentor->DiscipleID = DiscipleID;
	Disciple->MentorID = MentorID;

	ActiveMentorships.Add(Mentorship);
	return true;
}

bool UAdventurerManagerComponent::RemoveMentor(FName DiscipleID)
{
	for (int32 i = 0; i < ActiveMentorships.Num(); ++i)
	{
		if (ActiveMentorships[i].DiscipleAdventurerID == DiscipleID)
		{
			FName MentorID = ActiveMentorships[i].MentorAdventurerID;
			if (FAdventurerProfile* Mentor = FindHiredAdventurer(MentorID))
			{
				Mentor->DiscipleID = NAME_None;
			}
			if (FAdventurerProfile* Disciple = FindHiredAdventurer(DiscipleID))
			{
				Disciple->MentorID = NAME_None;
			}

			ActiveMentorships.RemoveAt(i);
			return true;
		}
	}
	return false;
}

bool UAdventurerManagerComponent::RetireVeteranToTown(FName VeteranID, FLegacyCrest& OutCrest)
{
	FAdventurerProfile* Veteran = FindHiredAdventurer(VeteranID);
	if (!Veteran || Veteran->Level < 35)
	{
		return false;
	}

	// Unslot from active party if present
	RemoveFromActiveParty(VeteranID);

	// Remove any mentorship linkage
	if (Veteran->DiscipleID != NAME_None)
	{
		RemoveMentor(Veteran->DiscipleID);
	}
	if (Veteran->MentorID != NAME_None)
	{
		RemoveMentor(VeteranID);
	}

	Veteran->Assignment = EAdventurerAssignment::RetiredInstructor;

	FLegacyCrest NewCrest;
	NewCrest.CrestID = FName(*FString::Printf(TEXT("Crest_%s"), *VeteranID.ToString()));
	NewCrest.OriginVeteranName = Veteran->Name;
	NewCrest.OriginClass = Veteran->ClassType;
	NewCrest.StatGrowthMultiplier = 1.20f;
	NewCrest.InheritedMasterPerk = FName(*FString::Printf(TEXT("Legacy_%s"), *UEnum::GetValueAsString(Veteran->ClassType)));
	NewCrest.BonusStartingSP = 250;

	AvailableLegacyCrests.Add(NewCrest);
	OutCrest = NewCrest;
	return true;
}

bool UAdventurerManagerComponent::ApplyLegacyCrest(FName AdventurerID, FName CrestID)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv || Adv->Level > 5) return false;

	for (int32 i = 0; i < AvailableLegacyCrests.Num(); ++i)
	{
		if (AvailableLegacyCrests[i].CrestID == CrestID)
		{
			Adv->AssignedLegacyCrest = AvailableLegacyCrests[i];
			Adv->CurrentExp += AvailableLegacyCrests[i].BonusStartingSP;
			AvailableLegacyCrests.RemoveAt(i);
			return true;
		}
	}
	return false;
}

bool UAdventurerManagerComponent::CanPromoteAdventurer(FName AdventurerID, EAdventurerClass TargetClass, FText& OutReason) const
{
	const FAdventurerProfile* TargetAdv = nullptr;
	for (const FAdventurerProfile& Adv : HiredAdventurers)
	{
		if (Adv.AdventurerID == AdventurerID)
		{
			TargetAdv = &Adv;
			break;
		}
	}

	if (!TargetAdv)
	{
		OutReason = FText::FromString(TEXT("Adventurer not found."));
		return false;
	}

	if (!FAdventurerProfile::CanBranchToClass(TargetAdv->ClassType, TargetClass))
	{
		OutReason = FText::FromString(TEXT("Invalid class promotion branch for this adventurer."));
		return false;
	}

	int32 TargetTier = FAdventurerProfile::GetClassTier(TargetClass);
	if (TargetTier == 2)
	{
		if (TargetAdv->Level < 15)
		{
			OutReason = FText::FromString(TEXT("Requires Level 15 to promote to Tier 2 Specialist."));
			return false;
		}

		float RelevantNutrient = TargetAdv->Nutrition.Protein + TargetAdv->Nutrition.Vitality + TargetAdv->Nutrition.ManaInfusion + TargetAdv->Nutrition.Agility;
		if (RelevantNutrient < 20.0f)
		{
			OutReason = FText::FromString(TEXT("Requires at least 20 total dietary nutrition points from Wonder Chef meals."));
			return false;
		}
	}
	else if (TargetTier == 3)
	{
		if (TargetAdv->Level < 35)
		{
			OutReason = FText::FromString(TEXT("Requires Level 35 to ascend to Tier 3 Paragon/Master."));
			return false;
		}

		float RelevantNutrient = TargetAdv->Nutrition.Protein + TargetAdv->Nutrition.Vitality + TargetAdv->Nutrition.ManaInfusion + TargetAdv->Nutrition.Agility;
		if (RelevantNutrient < 60.0f)
		{
			OutReason = FText::FromString(TEXT("Requires at least 60 total dietary nutrition points from Wonder Chef meals."));
			return false;
		}
	}

	OutReason = FText::FromString(TEXT("Eligible for class promotion!"));
	return true;
}

bool UAdventurerManagerComponent::PromoteAdventurer(FName AdventurerID, EAdventurerClass TargetClass)
{
	FText Reason;
	if (!CanPromoteAdventurer(AdventurerID, TargetClass, Reason))
	{
		return false;
	}

	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	Adv->ClassType = TargetClass;
	Adv->JobTier = FAdventurerProfile::GetClassTier(TargetClass);

	// Significant stat jump upon promotion (+25% base stats)
	Adv->BaseHP *= 1.25f;
	Adv->BaseTP *= 1.20f;
	Adv->BaseAttack *= 1.25f;
	Adv->BaseDefense *= 1.20f;
	Adv->BaseArtePower *= 1.25f;

	return true;
}

void UAdventurerManagerComponent::ApplyCampMealToParty(const FAdventurerNutrition& MealNutrition)
{
	for (const FName& AdvID : ActivePartyAdventurerIDs)
	{
		if (AdvID == NAME_None) continue;
		if (FAdventurerProfile* Adv = FindHiredAdventurer(AdvID))
		{
			Adv->Nutrition.AddNutrition(MealNutrition);
		}
	}

	// Strengthen partner bonds among all active party members
	for (int32 i = 0; i < ActivePartyAdventurerIDs.Num(); ++i)
	{
		for (int32 j = i + 1; j < ActivePartyAdventurerIDs.Num(); ++j)
		{
			if (ActivePartyAdventurerIDs[i] != NAME_None && ActivePartyAdventurerIDs[j] != NAME_None)
			{
				IncreaseAdventurerBond(ActivePartyAdventurerIDs[i], ActivePartyAdventurerIDs[j], 15);
			}
		}
	}
}

void UAdventurerManagerComponent::IncreaseAdventurerBond(FName AdvA, FName AdvB, int32 BondPoints)
{
	if (AdvA == NAME_None || AdvB == NAME_None || AdvA == AdvB) return;

	if (FAdventurerProfile* ProfileA = FindHiredAdventurer(AdvA))
	{
		int32 Current = ProfileA->PartnerBonds.FindRef(AdvB);
		ProfileA->PartnerBonds.Add(AdvB, FMath::Min(500, Current + BondPoints));
	}
	if (FAdventurerProfile* ProfileB = FindHiredAdventurer(AdvB))
	{
		int32 Current = ProfileB->PartnerBonds.FindRef(AdvA);
		ProfileB->PartnerBonds.Add(AdvA, FMath::Min(500, Current + BondPoints));
	}
}

int32 UAdventurerManagerComponent::GetAdventurerBondLevel(FName AdvA, FName AdvB) const
{
	for (const FAdventurerProfile& Adv : HiredAdventurers)
	{
		if (Adv.AdventurerID == AdvA)
		{
			int32 Points = Adv.PartnerBonds.FindRef(AdvB);
			return FMath::Clamp(1 + (Points / 100), 1, 5);
		}
	}
	return 1;
}

void UAdventurerManagerComponent::AdvanceDayCycle()
{
	const bool bHasFoodInStock = TownStockpile.GetTotalFoodCount() > 0;
	const bool bHighVariety = TownStockpile.GetFoodVarietyCount() >= 3;

	for (int32 i = HiredAdventurers.Num() - 1; i >= 0; --i)
	{
		FAdventurerProfile& Adv = HiredAdventurers[i];

		// Check food consumption from Town Stockpile
		if (bHasFoodInStock)
		{
			FName ConsumedFoodKey = NAME_None;
			for (auto& Pair : TownStockpile.FoodItems)
			{
				if (Pair.Value > 0)
				{
					ConsumedFoodKey = Pair.Key;
					Pair.Value--;
					break;
				}
			}

			// Favorite meal discovery or high variety nutrition
			if (ConsumedFoodKey != NAME_None && ConsumedFoodKey == Adv.FavoriteDishID)
			{
				Adv.ModifySatisfaction(15.0f);
			}
			else if (bHighVariety)
			{
				Adv.ModifySatisfaction(5.0f);
			}
		}
		else
		{
			// Starvation / food shortage in town
			Adv.ModifySatisfaction(-8.0f);
		}

		// Reset emergency hazard pay 1-battle pass
		Adv.bEmergencyHazardDeployed = false;

		// Convalescence for incapacitated heroes resting in town
		if (Adv.bIsIncapacitated)
		{
			Adv.RestDaysRemaining = FMath::Max(0, Adv.RestDaysRemaining - 1);
			if (Adv.RestDaysRemaining <= 0)
			{
				Adv.bIsIncapacitated = false;
				Adv.Condition = (Adv.FatigueLevel >= 70) ? EAdventurerCondition::Fatigued : EAdventurerCondition::Healthy;
				Adv.bIsUsable = !Adv.bIsOnStrike && (Adv.Condition != EAdventurerCondition::BurnoutLockout);
			}
		}

		// Passive fatigue & Vigor recovery when resting in town (scaled by Private Housing tier)
		if (Adv.Assignment != EAdventurerAssignment::ActiveParty)
		{
			Adv.FatigueLevel = FMath::Max(0, Adv.FatigueLevel - 25);
			Adv.ConsecutiveBattlesWithoutRest = 0;
			Adv.RestoreVigor(Adv.GetHousingVigorRecoveryRate());

			if (!Adv.bIsIncapacitated && Adv.FatigueLevel < 70 && Adv.Condition == EAdventurerCondition::Fatigued)
			{
				Adv.Condition = EAdventurerCondition::Healthy;
			}
		}

		// Burnout Lockout (Mandatory Vacation) recovery countdown
		if (Adv.BurnoutDaysRemaining > 0)
		{
			Adv.BurnoutDaysRemaining--;
			if (Adv.BurnoutDaysRemaining <= 0)
			{
				Adv.Condition = EAdventurerCondition::Healthy;
				if (Adv.GrievanceState == EAdventurerGrievanceState::BurnoutLockout)
				{
					Adv.GrievanceState = EAdventurerGrievanceState::Content;
					Adv.DaysDissatisfied = 0;
				}
				Adv.bIsUsable = !Adv.bIsOnStrike;
				Adv.RestoreVigor(100.0f); // Fully refreshed after mandatory R&R
				OnAdventurerBurnoutRecovered.Broadcast(Adv.AdventurerID);
			}
		}

		// Active party heroes gain extra satisfaction from adventuring
		if (Adv.Assignment == EAdventurerAssignment::ActiveParty)
		{
			Adv.ModifySatisfaction(3.0f);
		}

		// Grievance progression when dissatisfied (Satisfaction < 30.0f)
		if (Adv.Satisfaction < 30.0f)
		{
			Adv.DaysDissatisfied++;
			Adv.CurrentGrievance = FAdventurerProfile::GeneratePersonalityGrievance(Adv.Personality, Adv.DaysDissatisfied, Adv.FavoriteDishID, Adv.ConsecutiveKOs, Adv.FatigueLevel);


			if (Adv.DaysDissatisfied <= 7)
			{
				// Phase 1: Warning Notice (Days 1 to 7) — Adventurer remains usable, warnings escalate
				Adv.GrievanceState = EAdventurerGrievanceState::Warning;
				Adv.bIsUsable = true;
				Adv.bIsOnStrike = false;
				Adv.bWantsToLeave = false;
				Adv.DaysUntilDeparture = 15.0f - Adv.DaysDissatisfied;
				Adv.DepartureReason = Adv.CurrentGrievance.DailyNoticeText;

				OnAdventurerDepartureWarning.Broadcast(Adv.AdventurerID, Adv.CurrentGrievance.DailyNoticeText);
			}
			else if (Adv.DaysDissatisfied <= 14)
			{
				// Phase 2: On Strike / Unusable (Days 8 to 14) — Removed from party, demands compound
				Adv.GrievanceState = EAdventurerGrievanceState::OnStrike;
				Adv.bIsOnStrike = true;
				Adv.bIsUsable = false;
				Adv.bWantsToLeave = true;
				Adv.DaysUntilDeparture = 15.0f - Adv.DaysDissatisfied;
				Adv.DepartureReason = Adv.CurrentGrievance.DailyNoticeText;

				// Forcefully unslot from active battle party if present
				RemoveFromActiveParty(Adv.AdventurerID);

				OnAdventurerStrikeStarted.Broadcast(Adv.AdventurerID, Adv.CurrentGrievance);
				OnAdventurerDepartureWarning.Broadcast(Adv.AdventurerID, Adv.CurrentGrievance.DailyNoticeText);
			}
			else
			{
				// Mandatory Vacation / Burnout Lockout (Day 15+)
				// Adventurers NEVER permanently delete themselves from the roster!
				Adv.GrievanceState = EAdventurerGrievanceState::BurnoutLockout;
				Adv.Condition = EAdventurerCondition::BurnoutLockout;
				Adv.bIsUsable = false;
				Adv.bIsOnStrike = false;
				Adv.bWantsToLeave = false;
				Adv.BurnoutDaysRemaining = Adv.GetBurnoutDurationDays();
				Adv.DepartureReason = FText::FromString(FString::Printf(TEXT("%s has entered Mandatory Vacation / Burnout Lockout for %d days due to prolonged grievances!"), *Adv.Name.ToString(), Adv.BurnoutDaysRemaining));

				// Forcefully unslot from active battle party and auxiliary squads
				RemoveFromActiveParty(Adv.AdventurerID);
				RemoveFromAuxiliaryParty(Adv.AdventurerID, 0);

				OnAdventurerBurnoutStarted.Broadcast(Adv.AdventurerID, Adv.BurnoutDaysRemaining);
			}
		}
	}

	// Collect daily noble taxes from Landed Nobles (Tier 4+ Residences)
	const int32 DailyNobleTaxes = CollectAdventurerNobleTaxes();
	if (DailyNobleTaxes > 0)
	{
		TownStockpile.AddStock(EStockpileCategory::ShopSupply, TEXT("Item_Gald"), DailyNobleTaxes);
	}

	// Refresh visiting pool daily
	RefreshVisitingAdventurers(4);
}

bool UAdventurerManagerComponent::AppeaseWithGald(FName AdventurerID, int32& PlayerGold, int32 BonusAmount)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	const bool bWasDissatisfied = Adv->IsDissatisfied();
	const int32 RequiredGald = (Adv->CurrentGrievance.DemandedGaldCost > 0) ? Adv->CurrentGrievance.DemandedGaldCost : BonusAmount;

	if (PlayerGold < RequiredGald) return false;

	PlayerGold -= RequiredGald;

	const float Gain = (Adv->Personality == EAdventurerPersonality::Greedy) ? 60.0f : 45.0f;
	Adv->ModifySatisfaction(Gain);

	if (bWasDissatisfied && !Adv->IsDissatisfied())
	{
		OnAdventurerStrikeResolved.Broadcast(Adv->AdventurerID);
	}
	return true;
}

bool UAdventurerManagerComponent::AppeaseWithMeal(FName AdventurerID, FName DishItemID)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	if (!TownStockpile.ConsumeStock(EStockpileCategory::Food, DishItemID, 1))
	{
		return false;
	}

	const bool bWasDissatisfied = Adv->IsDissatisfied();

	float Gain = 40.0f;
	if (Adv->FavoriteDishID == DishItemID)
	{
		Gain = 65.0f;
	}
	if (Adv->Personality == EAdventurerPersonality::Foodie)
	{
		Gain *= 1.5f;
	}

	Adv->ModifySatisfaction(Gain);

	if (bWasDissatisfied && !Adv->IsDissatisfied())
	{
		OnAdventurerStrikeResolved.Broadcast(Adv->AdventurerID);
	}
	return true;
}

bool UAdventurerManagerComponent::AppeaseWithEquipment(FName AdventurerID, FName EquipmentID)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	const bool bWasDissatisfied = Adv->IsDissatisfied();

	Adv->Equipment.AddedAttack += 10.0f;
	Adv->Equipment.AddedDefense += 5.0f;
	Adv->ModifySatisfaction(55.0f);

	if (bWasDissatisfied && !Adv->IsDissatisfied())
	{
		OnAdventurerStrikeResolved.Broadcast(Adv->AdventurerID);
	}
	return true;
}

bool UAdventurerManagerComponent::AppeaseWithGuildMedal(FName AdventurerID)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	const bool bWasDissatisfied = Adv->IsDissatisfied();

	float Gain = 35.0f;
	if (Adv->Personality == EAdventurerPersonality::Virtuoso || Adv->Personality == EAdventurerPersonality::Chivalrous)
	{
		Gain = 55.0f;
	}

	Adv->ModifySatisfaction(Gain);

	if (bWasDissatisfied && !Adv->IsDissatisfied())
	{
		OnAdventurerStrikeResolved.Broadcast(Adv->AdventurerID);
	}
	return true;
}

FPartyMentorshipSynergy UAdventurerManagerComponent::CalculateActivePartyMentorshipSynergy() const
{
	FPartyMentorshipSynergy Synergy;

	TArray<FAdventurerProfile> PartyProfiles;
	for (const FName& AdvID : ActivePartyAdventurerIDs)
	{
		if (AdvID == NAME_None) continue;
		FAdventurerProfile Profile;
		if (GetAdventurerProfile(AdvID, Profile))
		{
			PartyProfiles.Add(Profile);
		}
	}

	if (PartyProfiles.Num() < 2)
	{
		return Synergy;
	}

	TSet<FName> Mentors;
	TSet<FName> Mentees;

	for (int32 i = 0; i < PartyProfiles.Num(); ++i)
	{
		const int32 RankA = FAdventurerProfile::GetRankValue(PartyProfiles[i].AdventurerRank);
		for (int32 j = 0; j < PartyProfiles.Num(); ++j)
		{
			if (i == j) continue;
			const int32 RankB = FAdventurerProfile::GetRankValue(PartyProfiles[j].AdventurerRank);
			const int32 Delta = RankA - RankB;

			if (Delta >= 1 && Delta <= 3)
			{
				Mentors.Add(PartyProfiles[i].AdventurerID);
				Mentees.Add(PartyProfiles[j].AdventurerID);
			}
		}
	}

	Synergy.MentorCount = Mentors.Num();
	Synergy.MenteeCount = Mentees.Num();

	if (Synergy.MentorCount == 1 && Synergy.MenteeCount == 3)
	{
		Synergy.MenteeExpBonusMultiplier = 1.35f;
		Synergy.MenteeStatBonusMultiplier = 1.10f;
		Synergy.MenteeDamageReductionPercent = 10.0f;
		Synergy.MentorOverlimitBonusMultiplier = 1.25f;
	}
	else if (Synergy.MentorCount == 2 && Synergy.MenteeCount == 2)
	{
		Synergy.MenteeExpBonusMultiplier = 1.20f;
		Synergy.MenteeStatBonusMultiplier = 1.20f;
		Synergy.MenteeDamageReductionPercent = 20.0f;
		Synergy.MentorOverlimitBonusMultiplier = 1.20f;
	}
	else if (Synergy.MentorCount == 3 && Synergy.MenteeCount == 1)
	{
		Synergy.MenteeExpBonusMultiplier = 1.20f;
		Synergy.MenteeStatBonusMultiplier = 1.30f;
		Synergy.MenteeDamageReductionPercent = 40.0f;
		Synergy.MentorOverlimitBonusMultiplier = 1.15f;
	}
	else if (Synergy.MentorCount >= 1 && Synergy.MenteeCount >= 1)
	{
		const float Total = static_cast<float>(Synergy.MentorCount + Synergy.MenteeCount);
		const float MenteeRatio = static_cast<float>(Synergy.MenteeCount) / Total;
		const float MentorRatio = static_cast<float>(Synergy.MentorCount) / Total;

		Synergy.MenteeExpBonusMultiplier = 1.0f + (0.35f * MenteeRatio);
		Synergy.MenteeStatBonusMultiplier = 1.0f + (0.25f * MentorRatio);
		Synergy.MenteeDamageReductionPercent = 35.0f * MentorRatio;
		Synergy.MentorOverlimitBonusMultiplier = 1.0f + (0.20f * MenteeRatio);
	}

	return Synergy;
}

void UAdventurerManagerComponent::RecordBattleEnd(bool bVictory, const TArray<FName>& IncapacitatedIDs)
{
	for (const FName& AdvID : ActivePartyAdventurerIDs)
	{
		if (AdvID == NAME_None) continue;
		FAdventurerProfile* Adv = FindHiredAdventurer(AdvID);
		if (!Adv) continue;

		if (IncapacitatedIDs.Contains(AdvID))
		{
			// Terrible Use: Incapacitated in combat
			Adv->RecordIncapacitation();
			OnAdventurerIncapacitated.Broadcast(Adv->AdventurerID, Adv->IncapacitationCount);

			if (Adv->Condition == EAdventurerCondition::BurnoutLockout)
			{
				RemoveFromActiveParty(Adv->AdventurerID);
				OnAdventurerBurnoutStarted.Broadcast(Adv->AdventurerID, Adv->BurnoutDaysRemaining);
			}
			// Check for repeated knockouts / trauma triggering grievances
			else if (Adv->ConsecutiveKOs >= 2 || Adv->Satisfaction < 30.0f)
			{
				Adv->DaysDissatisfied = FMath::Max(1, Adv->DaysDissatisfied);
				Adv->CurrentGrievance = FAdventurerProfile::GeneratePersonalityGrievance(Adv->Personality, Adv->DaysDissatisfied, Adv->FavoriteDishID, Adv->ConsecutiveKOs, Adv->FatigueLevel);
				if (Adv->GrievanceState == EAdventurerGrievanceState::Content)
				{
					Adv->GrievanceState = EAdventurerGrievanceState::Warning;
					Adv->DaysUntilDeparture = 14.0f;
				}
				Adv->DepartureReason = Adv->CurrentGrievance.DailyNoticeText;
				OnAdventurerDepartureWarning.Broadcast(Adv->AdventurerID, Adv->DepartureReason);
			}
		}
		else
		{
			// Heavy Use: Battle participation & fatigue accumulation
			Adv->RecordBattleParticipation();
			if (Adv->Condition == EAdventurerCondition::BurnoutLockout)
			{
				RemoveFromActiveParty(Adv->AdventurerID);
				OnAdventurerBurnoutStarted.Broadcast(Adv->AdventurerID, Adv->BurnoutDaysRemaining);
			}
			else if (Adv->FatigueLevel >= 70)
			{
				OnAdventurerFatigued.Broadcast(Adv->AdventurerID, Adv->FatigueLevel);
			}
			if (!bVictory)
			{
				Adv->ModifySatisfaction(-5.0f);
			}
		}
	}

	CalculateActivePartyMentorshipSynergy();
}

bool UAdventurerManagerComponent::RestAdventurerAtInn(FName AdventurerID, bool bLuxuryBathhouse)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	const bool bWasDissatisfied = Adv->IsDissatisfied();
	Adv->RecoverFromRest(bLuxuryBathhouse);

	// If resting resolves their fatigue/trauma grievance
	if (bWasDissatisfied && !Adv->IsDissatisfied())
	{
		OnAdventurerStrikeResolved.Broadcast(Adv->AdventurerID);
	}
	return true;
}

void UAdventurerManagerComponent::RestEntireActivePartyAtInn(bool bLuxuryBathhouse)
{
	for (const FName& AdvID : ActivePartyAdventurerIDs)
	{
		if (AdvID != NAME_None)
		{
			RestAdventurerAtInn(AdvID, bLuxuryBathhouse);
		}
	}
}

bool UAdventurerManagerComponent::DeployStrikingHeroWithHazardPay(FName AdventurerID, int32& PlayerGold, FText& OutReason)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv)
	{
		OutReason = FText::FromString(TEXT("Adventurer not found in hired roster."));
		return false;
	}

	if (!Adv->bIsOnStrike && Adv->GrievanceState != EAdventurerGrievanceState::OnStrike)
	{
		OutReason = FText::FromString(TEXT("Adventurer is not on strike. Standard deployment applies."));
		return false;
	}

	if (Adv->bIsIncapacitated || Adv->Condition == EAdventurerCondition::Incapacitated)
	{
		OutReason = FText::FromString(TEXT("Adventurer is incapacitated with severe combat trauma! They must rest at the Inn before fighting."));
		return false;
	}

	const int32 HazardFee = FMath::RoundToInt(Adv->HiringCost * 2.5f);
	if (PlayerGold < HazardFee)
	{
		OutReason = FText::Format(FText::FromString(TEXT("Insufficient Gald! Emergency hazard pay requires {0} Gald.")), FText::AsNumber(HazardFee));
		return false;
	}

	PlayerGold -= HazardFee;
	Adv->bEmergencyHazardDeployed = true;
	OutReason = FText::Format(FText::FromString(TEXT("Paid {0} Gald emergency hazard contract! {1} will fight for ONE battle with Grudging Strike debuffs (-25% ATK/DEF, no Overlimit).")), FText::AsNumber(HazardFee), Adv->Name);
	return true;
}

bool UAdventurerManagerComponent::SwapActiveWithAuxiliaryParty(uint8 TargetAuxIndex)
{
	if (TargetAuxIndex != 1 && TargetAuxIndex != 2)
	{
		return false;
	}

	TArray<FName>& TargetAux = (TargetAuxIndex == 1) ? AuxiliaryPartyBetaIDs : AuxiliaryPartyGammaIDs;

	// Ensure arrays are padded to 4
	while (ActivePartyAdventurerIDs.Num() < 4) ActivePartyAdventurerIDs.Add(NAME_None);
	while (TargetAux.Num() < 4) TargetAux.Add(NAME_None);

	// Swap squad assignments
	TArray<FName> Temp = ActivePartyAdventurerIDs;
	ActivePartyAdventurerIDs = TargetAux;
	TargetAux = Temp;

	// Update assignments for heroes in the newly active party
	for (const FName& AdvID : ActivePartyAdventurerIDs)
	{
		if (AdvID != NAME_None)
		{
			if (FAdventurerProfile* Adv = FindHiredAdventurer(AdvID))
			{
				Adv->Assignment = EAdventurerAssignment::ActiveParty;
			}
		}
	}

	// Update assignments for heroes rotated out to the auxiliary squad
	for (const FName& AdvID : TargetAux)
	{
		if (AdvID != NAME_None)
		{
			if (FAdventurerProfile* Adv = FindHiredAdventurer(AdvID))
			{
				Adv->Assignment = EAdventurerAssignment::RestingInTown;
			}
		}
	}

	OnPartyMentorshipCalculated.Broadcast(CalculateActivePartyMentorshipSynergy());
	return true;
}

bool UAdventurerManagerComponent::AssignToAuxiliaryParty(FName AdventurerID, uint8 AuxIndex, int32 SlotIndex)
{
	if (AdventurerID == NAME_None || (AuxIndex != 1 && AuxIndex != 2) || SlotIndex < 0 || SlotIndex >= 4)
	{
		return false;
	}

	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv || !Adv->CanDeployToBattle())
	{
		return false;
	}

	TArray<FName>& TargetAux = (AuxIndex == 1) ? AuxiliaryPartyBetaIDs : AuxiliaryPartyGammaIDs;
	TArray<FName>& OtherAux = (AuxIndex == 1) ? AuxiliaryPartyGammaIDs : AuxiliaryPartyBetaIDs;

	while (TargetAux.Num() < 4) TargetAux.Add(NAME_None);
	while (OtherAux.Num() < 4) OtherAux.Add(NAME_None);

	// Remove from ActiveParty if present
	RemoveFromActiveParty(AdventurerID);

	// Remove from other auxiliary squad if present
	for (int32 i = 0; i < OtherAux.Num(); ++i)
	{
		if (OtherAux[i] == AdventurerID)
		{
			OtherAux[i] = NAME_None;
		}
	}

	// Remove from current target squad if already placed elsewhere
	for (int32 i = 0; i < TargetAux.Num(); ++i)
	{
		if (TargetAux[i] == AdventurerID)
		{
			TargetAux[i] = NAME_None;
		}
	}

	// Release previous occupant of this slot
	FName PreviousOccupant = TargetAux[SlotIndex];
	if (PreviousOccupant != NAME_None)
	{
		if (FAdventurerProfile* OldAdv = FindHiredAdventurer(PreviousOccupant))
		{
			OldAdv->Assignment = EAdventurerAssignment::RestingInTown;
		}
	}

	TargetAux[SlotIndex] = AdventurerID;
	Adv->Assignment = EAdventurerAssignment::RestingInTown;
	return true;
}

bool UAdventurerManagerComponent::RemoveFromAuxiliaryParty(FName AdventurerID, uint8 AuxIndex)
{
	if (AdventurerID == NAME_None) return false;

	bool bFound = false;
	if (AuxIndex == 1 || AuxIndex == 0)
	{
		for (int32 i = 0; i < AuxiliaryPartyBetaIDs.Num(); ++i)
		{
			if (AuxiliaryPartyBetaIDs[i] == AdventurerID)
			{
				AuxiliaryPartyBetaIDs[i] = NAME_None;
				bFound = true;
			}
		}
	}

	if (AuxIndex == 2 || AuxIndex == 0)
	{
		for (int32 i = 0; i < AuxiliaryPartyGammaIDs.Num(); ++i)
		{
			if (AuxiliaryPartyGammaIDs[i] == AdventurerID)
			{
				AuxiliaryPartyGammaIDs[i] = NAME_None;
				bFound = true;
			}
		}
	}

	if (bFound)
	{
		if (FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID))
		{
			if (Adv->Assignment != EAdventurerAssignment::ActiveParty)
			{
				Adv->Assignment = EAdventurerAssignment::RestingInTown;
			}
		}
	}

	return bFound;
}

bool UAdventurerManagerComponent::AssignAdventurerToHouse(FName AdventurerID, int32 LotIndex, FText& OutReason)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv)
	{
		OutReason = FText::FromString(TEXT("Adventurer not found in hired roster."));
		return false;
	}

	if (!Adv->CanOwnPrivateHouse())
	{
		OutReason = FText::Format(FText::FromString(TEXT("{0} is currently {1}. Private housing is strictly gated to Rank C or higher! Rank E and D recruits reside in communal Guild Barracks (+15 Vigor/day).")),
			Adv->Name,
			FText::FromString(UEnum::GetValueAsString(Adv->AdventurerRank)));
		return false;
	}

	if (LotIndex < 0)
	{
		OutReason = FText::FromString(TEXT("Invalid residential lot index specified."));
		return false;
	}

	// Check if this lot is already occupied by another adventurer
	for (const FAdventurerProfile& Other : HiredAdventurers)
	{
		if (Other.AdventurerID != AdventurerID && Other.HouseData.bHasPrivateHouse && Other.HouseData.LotIndex == LotIndex)
		{
			OutReason = FText::Format(FText::FromString(TEXT("Residential Lot {0} is already deeded to {1}!")),
				FText::AsNumber(LotIndex),
				Other.Name);
			return false;
		}
	}

	Adv->HouseData.bHasPrivateHouse = true;
	Adv->HouseData.LotIndex = LotIndex;
	Adv->HouseData.HouseTier = EBuildingTier::Tier_1_Rustic;
	Adv->ModifySatisfaction(25.0f);

	OutReason = FText::Format(FText::FromString(TEXT("Deeded Residential Lot {0} to {1}! Base Tier 1 Cottage provides +25 Vigor/day and personality scaling bonuses.")),
		FText::AsNumber(LotIndex),
		Adv->Name);

	OnAdventurerHouseUpgraded.Broadcast(Adv->AdventurerID, Adv->HouseData.HouseTier, Adv->IsLandedNoble());
	return true;
}

bool UAdventurerManagerComponent::UpgradeAdventurerHouse(FName AdventurerID, int32& PlayerGold, FText& OutReason)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv)
	{
		OutReason = FText::FromString(TEXT("Adventurer not found in hired roster."));
		return false;
	}

	if (!Adv->HouseData.bHasPrivateHouse)
	{
		OutReason = FText::Format(FText::FromString(TEXT("{0} does not own a residential lot yet. Assign to a private lot before upgrading.")), Adv->Name);
		return false;
	}

	const int32 CurrentTierVal = Adv->GetHouseTierValue();
	if (CurrentTierVal >= 5)
	{
		OutReason = FText::FromString(TEXT("House is already at maximum Tier 5 (Royal Palace / Grand Estate)."));
		return false;
	}

	const int32 TargetTierVal = CurrentTierVal + 1;

	// Lord's Manor Gating: Residences cannot exceed the Lord's Manor municipal tier!
	int32 ManorMaxTier = 1;
	UWorld* World = GetWorld();
	if (World)
	{
		for (TActorIterator<ALordsManorActor> It(World); It; ++It)
		{
			if (ALordsManorActor* Manor = *It)
			{
				ManorMaxTier = FTownBuildingRecord::GetTierValue(Manor->ManorTier);
				break;
			}
		}
	}

	if (TargetTierVal > ManorMaxTier)
	{
		OutReason = FText::Format(FText::FromString(TEXT("Lord's Manor must be upgraded to Tier {0} before adventurer residences can reach Tier {0}! (Current Manor Tier: {1})")),
			FText::AsNumber(TargetTierVal),
			FText::AsNumber(ManorMaxTier));
		return false;
	}

	// Calculate upgrade costs by target tier
	int32 ReqGold = 0;
	int32 ReqTimber = 0;
	int32 ReqStone = 0;
	int32 ReqDemonCore = 0;
	const EBuildingTier TargetTier = FTownBuildingRecord::GetTierFromValue(TargetTierVal);

	switch (TargetTierVal)
	{
	case 2:
		ReqGold = 500;
		ReqTimber = 30;
		ReqStone = 20;
		ReqDemonCore = 0;
		break;
	case 3:
		ReqGold = 1500;
		ReqTimber = 80;
		ReqStone = 60;
		ReqDemonCore = 0;
		break;
	case 4:
		ReqGold = 4000;
		ReqTimber = 180;
		ReqStone = 150;
		ReqDemonCore = 5;
		break;
	case 5:
		ReqGold = 10000;
		ReqTimber = 400;
		ReqStone = 350;
		ReqDemonCore = 20;
		break;
	default:
		break;
	}

	if (PlayerGold < ReqGold)
	{
		OutReason = FText::Format(FText::FromString(TEXT("Insufficient Gold. Required: {0}, Available: {1}.")),
			FText::AsNumber(ReqGold),
			FText::AsNumber(PlayerGold));
		return false;
	}

	const int32 StockTimber = TownStockpile.GetStock(EStockpileCategory::Crafting, TEXT("Mat_Timber"));
	const int32 StockStone = TownStockpile.GetStock(EStockpileCategory::Crafting, TEXT("Mat_Stone"));
	const int32 StockCores = TownStockpile.GetStock(EStockpileCategory::Crafting, TEXT("Mat_DemonCore"));

	if (StockTimber < ReqTimber)
	{
		OutReason = FText::Format(FText::FromString(TEXT("Insufficient Timber in Stockpile. Required: {0}, Available: {1}.")),
			FText::AsNumber(ReqTimber),
			FText::AsNumber(StockTimber));
		return false;
	}

	if (StockStone < ReqStone)
	{
		OutReason = FText::Format(FText::FromString(TEXT("Insufficient Stone in Stockpile. Required: {0}, Available: {1}.")),
			FText::AsNumber(ReqStone),
			FText::AsNumber(StockStone));
		return false;
	}

	if (ReqDemonCore > 0 && StockCores < ReqDemonCore)
	{
		OutReason = FText::Format(FText::FromString(TEXT("Insufficient Demon Cores in Stockpile. Required: {0}, Available: {1}.")),
			FText::AsNumber(ReqDemonCore),
			FText::AsNumber(StockCores));
		return false;
	}

	// Deduct resources
	PlayerGold -= ReqGold;
	TownStockpile.ConsumeStock(EStockpileCategory::Crafting, TEXT("Mat_Timber"), ReqTimber);
	TownStockpile.ConsumeStock(EStockpileCategory::Crafting, TEXT("Mat_Stone"), ReqStone);
	if (ReqDemonCore > 0)
	{
		TownStockpile.ConsumeStock(EStockpileCategory::Crafting, TEXT("Mat_DemonCore"), ReqDemonCore);
	}

	Adv->HouseData.HouseTier = TargetTier;
	Adv->ModifySatisfaction(35.0f);

	FString NobleNotice = TEXT("");
	if (TargetTierVal >= 4)
	{
		NobleNotice = TEXT(" [LANDED NOBLE UNLOCKED! Pays daily municipal noble taxes & activates Signature Aura Perk]");
	}

	OutReason = FText::Format(FText::FromString(TEXT("Successfully upgraded {0}'s residence to Tier {1} ({2})!{3}")),
		Adv->Name,
		FText::AsNumber(TargetTierVal),
		FText::FromString(UEnum::GetValueAsString(TargetTier)),
		FText::FromString(NobleNotice));

	OnAdventurerHouseUpgraded.Broadcast(Adv->AdventurerID, TargetTier, Adv->IsLandedNoble());
	return true;
}

int32 UAdventurerManagerComponent::GetTotalLandedNoblesCount() const
{
	int32 Count = 0;
	for (const FAdventurerProfile& Adv : HiredAdventurers)
	{
		if (Adv.IsLandedNoble())
		{
			Count++;
		}
	}
	return Count;
}

int32 UAdventurerManagerComponent::CollectAdventurerNobleTaxes()
{
	int32 TotalNobleTax = 0;
	for (const FAdventurerProfile& Adv : HiredAdventurers)
	{
		TotalNobleTax += Adv.GetHousingNobleTaxDailyIncome();
	}
	return TotalNobleTax;
}



bool UAdventurerManagerComponent::FeedAdventurer(FName AdventurerID, FName FoodItemID, int32 ExpYield, float StatMultiplier)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	// Feeding gives EXP and also permanently increases base stats by a tiny amount based on multiplier
	Adv->BaseHP += 10.0f * StatMultiplier;
	Adv->BaseTP += 2.0f * StatMultiplier;
	Adv->BaseAttack += 1.0f * StatMultiplier;
	Adv->BaseDefense += 1.0f * StatMultiplier;
	Adv->BaseArtePower += 1.0f * StatMultiplier;
	
	// Favorite dish gives double!
	if (Adv->FavoriteDishID == FoodItemID)
	{
		ExpYield *= 2;
	}

	TrainAdventurer(AdventurerID, ExpYield);
	return true;
}

bool UAdventurerManagerComponent::EvolveAdventurerClass(FName AdventurerID, EAdventurerClass NewClass)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv) return false;

	// ToS2 Breeding Mechanic: Reset Level to 1, but keep 20% of current stats added to base stats!
	// This makes reincarnation infinitely scale them over time.
	
	Adv->BaseHP += (Adv->Level * 10.0f) * 0.2f;
	Adv->BaseTP += (Adv->Level * 2.0f) * 0.2f;
	Adv->BaseAttack += (Adv->Level * 1.5f) * 0.2f;
	Adv->BaseDefense += (Adv->Level * 1.0f) * 0.2f;
	Adv->BaseArtePower += (Adv->Level * 1.5f) * 0.2f;
	
	Adv->Level = 1;
	Adv->CurrentExp = 0;
	Adv->ExpToNextLevel = 100;
	
	Adv->ClassType = NewClass;
	Adv->JobTier = (int32)NewClass >= 12 ? 3 : ((int32)NewClass >= 6 ? 2 : 1);
	
	return true;
}

bool UAdventurerManagerComponent::UnlockSphereNode(FName AdventurerID, USphereGridDataAsset* GridAsset, FName NodeID)
{
	FAdventurerProfile* Adv = FindHiredAdventurer(AdventurerID);
	if (!Adv || !GridAsset) return false;

	if (Adv->UnlockedSphereNodes.Contains(NodeID)) return false; // Already unlocked

	const FSphereNode* NodePtr = GridAsset->GridNodes.Find(NodeID);
	if (!NodePtr) return false;

	// Apply stats
	if (NodePtr->NodeType == ESphereNodeType::Stat)
	{
		Adv->BaseHP += NodePtr->HP_Bonus;
		Adv->BaseTP += NodePtr->TP_Bonus;
		// Trust and Inventory are town-level stats, but we can store them here or apply to town
	}
	else if (NodePtr->NodeType == ESphereNodeType::Skill)
	{
		if (NodePtr->UnlockArte)
		{
			// Give them the arte (assuming there's an artes array, but for now we just record the unlock)
		}
	}

	Adv->UnlockedSphereNodes.Add(NodeID);
	return true;
}


