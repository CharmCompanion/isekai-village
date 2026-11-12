// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurerSystemTypes.h — Adventurer recruitment, raising, progression, and equipment types

#pragma once

#include "CoreMinimal.h"
#include "IsekaiVillageTypes.h"
#include "TownEconomyTypes.h"
#include "AdventurerSystemTypes.generated.h"


UENUM(BlueprintType)
enum class EAdventurerRank : uint8
{
	Rank_E   UMETA(DisplayName = "Rank E (Novice)"),
	Rank_D   UMETA(DisplayName = "Rank D (Apprentice)"),
	Rank_C   UMETA(DisplayName = "Rank C (Journeyman)"),
	Rank_B   UMETA(DisplayName = "Rank B (Veteran)"),
	Rank_A   UMETA(DisplayName = "Rank A (Master)"),
	Rank_S   UMETA(DisplayName = "Rank S (Champion / Hero)"),
	Rank_SS  UMETA(DisplayName = "Rank SS (Legend)"),
	Rank_SSS UMETA(DisplayName = "Rank SSS (Mythic / Demigod)")
};

/**
 * Dynamic party synergy when mentors and mentees are within 1-3 ranks of each other.
 */
USTRUCT(BlueprintType)
struct FPartyMentorshipSynergy
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mentorship")
	int32 MentorCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mentorship")
	int32 MenteeCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mentorship")
	float MenteeExpBonusMultiplier = 1.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mentorship")
	float MenteeStatBonusMultiplier = 1.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mentorship")
	float MenteeDamageReductionPercent = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mentorship")
	float MentorOverlimitBonusMultiplier = 1.0f;
};

UENUM(BlueprintType)
enum class EAdventurerClass : uint8
{
	// Tier 1: Novices / Base Classes
	Swordsman        UMETA(DisplayName = "Swordsman (Balanced Melee)"),
	Berserker        UMETA(DisplayName = "Berserker (Heavy Greatsword & High ATK)"),
	Mage             UMETA(DisplayName = "Mage / Sorcerer (Elemental Artes)"),
	Healer           UMETA(DisplayName = "Healer / Cleric (Support & Holy Artes)"),
	Rogue            UMETA(DisplayName = "Rogue (Dual Daggers & High Speed)"),
	Paladin          UMETA(DisplayName = "Paladin (Shield Tank & Holy Defense)"),

	// Tier 2: Specialists (Promoted at Lv 15+ with Diet Requirements)
	Warrior          UMETA(DisplayName = "Warrior (Swordsman Tier 2)"),
	Gladiator        UMETA(DisplayName = "Gladiator (Berserker Tier 2)"),
	Sorcerer         UMETA(DisplayName = "Sorcerer (Mage Tier 2)"),
	Cleric           UMETA(DisplayName = "Cleric (Healer Tier 2)"),
	Scout            UMETA(DisplayName = "Scout (Rogue Tier 2)"),
	Knight           UMETA(DisplayName = "Knight (Paladin Tier 2)"),

	// Tier 3: Paragons & Masters (Ascended at Lv 35+ with Master Feast & Sphere Grid)
	Swordmaster      UMETA(DisplayName = "Swordmaster (Combo & Aerial Juggle Master)"),
	RuneKnight       UMETA(DisplayName = "Rune Knight (Spellblade & Elemental Infusion)"),
	Warmaster        UMETA(DisplayName = "Warmaster (Iron Stance Shatterer)"),
	BloodReaver      UMETA(DisplayName = "Blood Reaver (Low-HP Frenzy Scaling)"),
	Archmage         UMETA(DisplayName = "Archmage (FastCast Elemental Cataclysm)"),
	Arcanist         UMETA(DisplayName = "Arcanist (Spell Mines & Gravity Wells)"),
	HighPriest       UMETA(DisplayName = "High Priest (Miracles & Full Revives)"),
	HolyInquisitor   UMETA(DisplayName = "Holy Inquisitor (Anti-Demon Exorcist)"),
	ShadowAssassin   UMETA(DisplayName = "Shadow Assassin (FlashStep & AG Loops)"),
	BountyHunter     UMETA(DisplayName = "Bounty Hunter (Traps, Bow Spread & Spoils)"),
	GuardianTemplar  UMETA(DisplayName = "Guardian Templar (Impenetrable Fortress & Cover)"),
	Crusader         UMETA(DisplayName = "Crusader (Radiant Retaliation & Team Aura)")
};

UENUM(BlueprintType)
enum class EAdventurerPersonality : uint8
{
	Brave        UMETA(DisplayName = "Brave (+15% Physical ATK)"),
	Stoic        UMETA(DisplayName = "Stoic (+20% Physical DEF)"),
	Arcane       UMETA(DisplayName = "Arcane Genius (+25% Arte Power)"),
	Greedy       UMETA(DisplayName = "Greedy (+25% Gald on Bounties & Expeditions)"),
	DemonHunter  UMETA(DisplayName = "Demon Hunter (+35% Damage vs Demonkind)"),
	Diligent     UMETA(DisplayName = "Diligent (+30% EXP Gain from Training)"),
	Foodie       UMETA(DisplayName = "Foodie (2x Cooking Buff Potency & Duration)"),
	Virtuoso     UMETA(DisplayName = "Virtuoso (+50% Overlimit Gauge Acceleration)"),
	Skittish     UMETA(DisplayName = "Skittish (+30% Movement & Evasion Speed)"),
	Zealous      UMETA(DisplayName = "Zealous (+40% Holy Light Damage vs Fiends)"),
	Bloodthirsty UMETA(DisplayName = "Bloodthirsty (Low HP Scaling up to +50% ATK)"),
	Technician   UMETA(DisplayName = "Technician (Critical Hits Refund 1 AG Pip)"),
	Protector    UMETA(DisplayName = "Protector (+25% Guard Efficiency & Shield Defense)"),
	Scholar      UMETA(DisplayName = "Scholar (+40% Rare Demon Material & Core Drop Rate)"),
	HotHeaded    UMETA(DisplayName = "Hot-Headed (+25% Fire Arte Power & Counter Stance)"),
	LoneWolf     UMETA(DisplayName = "Lone Wolf (+30% All Stats when Solo or Last Standing)"),
	Chivalrous   UMETA(DisplayName = "Chivalrous (+10% Stats Aura to Nearby Party)"),
	Carefree     UMETA(DisplayName = "Carefree (+20% Lucky Critical Strike Chance)")
};

UENUM(BlueprintType)
enum class EAdventurerAssignment : uint8
{
	RestingInTown    UMETA(DisplayName = "Resting in Town"),
	ActiveParty      UMETA(DisplayName = "Active Battle Party"),
	GuildExpedition  UMETA(DisplayName = "On Guild Expedition"),
	Training         UMETA(DisplayName = "Training Grounds"),
	RetiredInstructor UMETA(DisplayName = "Retired Town Instructor")
};

/**
 * Permanent dietary nutrition meters granted by Wonder Chef camp meals (ToS2 monster raising style).
 */
USTRUCT(BlueprintType)
struct FAdventurerNutrition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition")
	float Protein = 0.0f;       // Physical ATK, STR, Iron Stance break bonus

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition")
	float Vitality = 0.0f;      // Max HP, Physical DEF, Guard stability

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition")
	float ManaInfusion = 0.0f;  // Max TP, Arte Power, Cast speed

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition")
	float Agility = 0.0f;       // Movement speed, Dodge recovery, Crit rate

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition|Elements")
	float HolyEssence = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition|Elements")
	float DarkEssence = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition|Elements")
	float FireEssence = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition|Elements")
	float WaterEssence = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition|Elements")
	float WindEssence = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition|Elements")
	float EarthEssence = 0.0f;

	void AddNutrition(const FAdventurerNutrition& Other)
	{
		Protein += Other.Protein;
		Vitality += Other.Vitality;
		ManaInfusion += Other.ManaInfusion;
		Agility += Other.Agility;
		HolyEssence += Other.HolyEssence;
		DarkEssence += Other.DarkEssence;
		FireEssence += Other.FireEssence;
		WaterEssence += Other.WaterEssence;
		WindEssence += Other.WindEssence;
		EarthEssence += Other.EarthEssence;
	}
};

/**
 * Legacy Crest generated when a veteran retires, passed down to new recruits (Human breeding equivalent).
 */
USTRUCT(BlueprintType)
struct FLegacyCrest
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	FName CrestID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	FText OriginVeteranName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	EAdventurerClass OriginClass = EAdventurerClass::Swordsman;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	float StatGrowthMultiplier = 1.20f; // +20% per-level growth bonus

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	FName InheritedMasterPerk = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	int32 BonusStartingSP = 250;
};

/**
 * Senior-Junior Mentorship binding (Senior transfers passives, artes, and EXP bonus).
 */
USTRUCT(BlueprintType)
struct FAdventurerMentorship
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	FName MentorAdventurerID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	FName DiscipleAdventurerID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	float BonusExpRate = 1.25f; // +25% training EXP

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	FName InheritedPerkID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	FName InheritedArteID = NAME_None;
};

/**
 * 2-Phase grievance states for dissatisfied adventurers.
 */
UENUM(BlueprintType)
enum class EAdventurerGrievanceState : uint8
{
	Content         UMETA(DisplayName = "Content (Satisfaction >= 30%)"),
	Warning         UMETA(DisplayName = "Phase 1: Warning Notice (Days 1 to 7)"),
	OnStrike        UMETA(DisplayName = "Phase 2: On Strike / Unusable (Days 8 to 14)"),
	BurnoutLockout  UMETA(DisplayName = "Burnout Lockout (Mandatory R&R)"),
	Departed        UMETA(DisplayName = "Departed (Legacy)")
};

/**
 * Adventurer physical condition (Healthy, Fatigued, BurnoutLockout, Incapacitated, or On Strike).
 */
UENUM(BlueprintType)
enum class EAdventurerCondition : uint8
{
	Healthy         UMETA(DisplayName = "Healthy & Ready"),
	Fatigued        UMETA(DisplayName = "Fatigued (Heavy Use)"),
	BurnoutLockout  UMETA(DisplayName = "Burnout Lockout (Mandatory R&R)"),
	Incapacitated   UMETA(DisplayName = "Incapacitated / Injured (Needs Rest)"),
	OnStrike        UMETA(DisplayName = "On Strike (Protesting)")
};

/**
 * Private housing record for an adventurer (Rank C+ required for private ownership).
 */
USTRUCT(BlueprintType)
struct FAdventurerHouseData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Housing")
	bool bHasPrivateHouse = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Housing")
	EBuildingTier HouseTier = EBuildingTier::Tier_1_Rustic;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Housing")
	int32 LotIndex = -1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Housing")
	FText HouseCustomName = FText::GetEmpty();
};



/**
 * Detailed grievance record tracking personality issue, compounding severity, and resolution demands.
 */
USTRUCT(BlueprintType)
struct FAdventurerGrievance
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grievance")
	FText CauseTitle = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grievance")
	FText CauseDescription = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grievance")
	FText DailyNoticeText = FText::GetEmpty();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Grievance")
	int32 DaysDissatisfied = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Grievance")
	int32 CompoundingSeverity = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grievance")
	FName DemandedItemID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Grievance")
	int32 DemandedGaldCost = 300;
};

/**
 * Equipment loadout for an adventurer.
 */
USTRUCT(BlueprintType)
struct FAdventurerEquipment
{
	GENERATED_BODY()

	// Weapon Slot
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	FName WeaponID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	float AddedAttack = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	EElement WeaponElement = EElement::Fire;

	// Armor Slot
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	FName ArmorID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	float AddedDefense = 0.0f;

	// Accessory Slot
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	FName AccessoryID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	float AddedMaxHP = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	float AddedMaxTP = 0.0f;
};

/**
 * Complete profile of an adventurer (recruitable, trainable, equipable).
 */
USTRUCT(BlueprintType)
struct FAdventurerProfile
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Identity")
	FName AdventurerID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Identity")
	FText Name = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Identity")
	EAdventurerClass ClassType = EAdventurerClass::Swordsman;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Identity")
	EAdventurerPersonality Personality = EAdventurerPersonality::Brave;

	// Adventurer Guild Rank (Rank E through Rank SSS)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Identity")
	EAdventurerRank AdventurerRank = EAdventurerRank::Rank_E;

	// Job Progression Tier (1 = Novice, 2 = Specialist, 3 = Paragon/Master)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Identity")
	int32 JobTier = 1;

	// The nodes this adventurer has unlocked on their current sphere grid
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Progression")
	TArray<FName> UnlockedSphereNodes;

	// Satisfaction & Loyalty (0.0 to 100.0)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loyalty")
	float Satisfaction = 75.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Loyalty")
	EAdventurerGrievanceState GrievanceState = EAdventurerGrievanceState::Content;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	EAdventurerCondition Condition = EAdventurerCondition::Healthy;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	bool bIsIncapacitated = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	int32 IncapacitationCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	int32 ConsecutiveKOs = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	int32 FatigueLevel = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	int32 ConsecutiveBattlesWithoutRest = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	int32 RestDaysRemaining = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	bool bEmergencyHazardDeployed = false;

	// ── Private Housing & Vigor Engine (Rank C+) ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Housing")
	FAdventurerHouseData HouseData;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	float Vigor = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Condition")
	int32 BurnoutDaysRemaining = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Loyalty")
	bool bWantsToLeave = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Loyalty")
	bool bIsOnStrike = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Loyalty")
	bool bIsUsable = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Loyalty")
	int32 DaysDissatisfied = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Loyalty")
	float DaysUntilDeparture = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loyalty")
	FText DepartureReason = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loyalty")
	FName FavoriteDishID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loyalty")
	FAdventurerGrievance CurrentGrievance;

	bool CanOwnPrivateHouse() const
	{
		return AdventurerRank >= EAdventurerRank::Rank_C;
	}

	bool IsLandedNoble() const
	{
		return HouseData.bHasPrivateHouse && HouseData.HouseTier >= EBuildingTier::Tier_4_Fortified;
	}

	int32 GetHouseTierValue() const
	{
		if (!HouseData.bHasPrivateHouse) return 0;
		return FTownBuildingRecord::GetTierValue(HouseData.HouseTier);
	}

	float GetHousingVigorRecoveryRate() const
	{
		if (!HouseData.bHasPrivateHouse)
		{
			return 15.0f;
		}

		float Rate = 15.0f;
		switch (HouseData.HouseTier)
		{
		case EBuildingTier::Tier_1_Rustic:       Rate = 25.0f; break;
		case EBuildingTier::Tier_2_Timber:       Rate = 40.0f; break;
		case EBuildingTier::Tier_3_StoneMasonry: Rate = 60.0f; break;
		case EBuildingTier::Tier_4_Fortified:    Rate = 85.0f; break;
		case EBuildingTier::Tier_5_GrandEstate:  Rate = 100.0f; break;
		}

		if (Personality == EAdventurerPersonality::LoneWolf)
		{
			Rate *= 1.5f;
		}
		return Rate;
	}

	int32 GetBurnoutDurationDays() const
	{
		if (!HouseData.bHasPrivateHouse) return 5;
		switch (HouseData.HouseTier)
		{
		case EBuildingTier::Tier_1_Rustic:       return 4;
		case EBuildingTier::Tier_2_Timber:       return 3;
		case EBuildingTier::Tier_3_StoneMasonry: return 2;
		case EBuildingTier::Tier_4_Fortified:    return 1;
		case EBuildingTier::Tier_5_GrandEstate:  return 0;
		default:                                 return 4;
		}
	}

	void DrainVigor(float Amount)
	{
		Vigor = FMath::Clamp(Vigor - Amount, 0.0f, 100.0f);
		if (Vigor <= 0.0f)
		{
			Condition = EAdventurerCondition::BurnoutLockout;
			BurnoutDaysRemaining = GetBurnoutDurationDays();
			bIsUsable = false;
		}
		else if (Vigor < 30.0f && Condition == EAdventurerCondition::Healthy)
		{
			Condition = EAdventurerCondition::Fatigued;
		}
	}

	void RestoreVigor(float Amount)
	{
		Vigor = FMath::Clamp(Vigor + Amount, 0.0f, 100.0f);
		if (Vigor >= 100.0f && BurnoutDaysRemaining <= 0 && !bIsIncapacitated)
		{
			Condition = (GrievanceState == EAdventurerGrievanceState::OnStrike) ? EAdventurerCondition::OnStrike : EAdventurerCondition::Healthy;
			bIsUsable = !bIsOnStrike;
		}
	}

	// ── 18 Personality Housing Scaling Multipliers ──
	float GetHousingAttackMultiplier() const
	{
		float Mult = 1.0f;
		const int32 TierVal = GetHouseTierValue();
		if (Personality == EAdventurerPersonality::Brave)
		{
			Mult += (TierVal * 0.03f); // +3% ATK per tier
		}
		if (Personality == EAdventurerPersonality::LoneWolf && TierVal >= 3)
		{
			Mult += 0.25f; // +25% solo/residence boost
		}
		return Mult;
	}

	float GetHousingDefenseMultiplier() const
	{
		float Mult = 1.0f;
		const int32 TierVal = GetHouseTierValue();
		if (Personality == EAdventurerPersonality::Stoic)
		{
			Mult += (TierVal * 0.04f); // +4% DEF per tier
		}
		if (Personality == EAdventurerPersonality::Protector)
		{
			Mult += (TierVal * 0.03f);
		}
		return Mult;
	}

	float GetHousingArtePowerMultiplier() const
	{
		float Mult = 1.0f;
		const int32 TierVal = GetHouseTierValue();
		if (Personality == EAdventurerPersonality::Arcane)
		{
			Mult += (TierVal * 0.04f); // +4% Arte power per tier
		}
		if (Personality == EAdventurerPersonality::HotHeaded)
		{
			Mult += (TierVal * 0.04f);
		}
		if (Personality == EAdventurerPersonality::Zealous)
		{
			Mult += (TierVal * 0.05f);
		}
		return Mult;
	}

	float GetHousingGaldBonusMultiplier() const
	{
		float Mult = 1.0f;
		const int32 TierVal = GetHouseTierValue();
		if (Personality == EAdventurerPersonality::Greedy)
		{
			Mult += (TierVal * 0.05f); // +5% Gald per tier
		}
		return Mult;
	}

	float GetHousingExpBonusMultiplier() const
	{
		float Mult = 1.0f;
		const int32 TierVal = GetHouseTierValue();
		if (Personality == EAdventurerPersonality::Diligent)
		{
			Mult += (TierVal * 0.06f); // +6% EXP per tier
		}
		return Mult;
	}

	float GetHousingOverlimitRateMultiplier() const
	{
		float Mult = 1.0f;
		const int32 TierVal = GetHouseTierValue();
		if (Personality == EAdventurerPersonality::Virtuoso)
		{
			Mult += (TierVal * 0.08f); // +8% Overlimit rate per tier
		}
		return Mult;
	}

	float GetHousingCritBonus() const
	{
		if (Personality == EAdventurerPersonality::Carefree)
		{
			return GetHouseTierValue() * 0.03f; // +3% Crit per tier
		}
		return 0.0f;
	}

	float GetHousingSpeedMultiplier() const
	{
		if (Personality == EAdventurerPersonality::Skittish)
		{
			return 1.0f + (GetHouseTierValue() * 0.04f); // +4% speed per tier
		}
		return 1.0f;
	}

	float GetHousingRareDropMultiplier() const
	{
		if (Personality == EAdventurerPersonality::Scholar)
		{
			return 1.0f + (GetHouseTierValue() * 0.08f); // +8% rare drop per tier
		}
		return 1.0f;
	}

	float GetHousingDemonDamageMultiplier() const
	{
		if (Personality == EAdventurerPersonality::DemonHunter)
		{
			return 1.0f + (GetHouseTierValue() * 0.05f); // +5% demon damage per tier
		}
		return 1.0f;
	}

	float GetHousingNobleTaxDailyIncome() const
	{
		if (!IsLandedNoble()) return 0.0f;
		float Tax = 150.0f;
		if (Personality == EAdventurerPersonality::Greedy) Tax = 250.0f;
		else if (Personality == EAdventurerPersonality::Chivalrous) Tax = 200.0f;
		return Tax;
	}

	bool HasBossHunterAura() const
	{
		return Personality == EAdventurerPersonality::Brave && IsLandedNoble();
	}

	bool HasVirtuosoOverlimitStartAura() const
	{
		return Personality == EAdventurerPersonality::Virtuoso && IsLandedNoble();
	}

	bool HasSkittishAmbushImmunity() const
	{
		return Personality == EAdventurerPersonality::Skittish && GetHouseTierValue() >= 2;
	}

	void RecordIncapacitation(float BaseSatisfactionPenalty = -25.0f)
	{
		bIsIncapacitated = true;
		Condition = EAdventurerCondition::Incapacitated;
		IncapacitationCount++;
		ConsecutiveKOs++;
		RestDaysRemaining = FMath::Clamp(ConsecutiveKOs, 1, 3);
		DrainVigor(35.0f);

		float Penalty = BaseSatisfactionPenalty;
		if (Personality == EAdventurerPersonality::Skittish) Penalty *= 1.6f;
		else if (Personality == EAdventurerPersonality::Brave) Penalty *= 0.6f;
		else if (Personality == EAdventurerPersonality::Protector) Penalty *= 1.3f;
		else if (Personality == EAdventurerPersonality::Carefree) Penalty *= 1.5f;

		ModifySatisfaction(Penalty);
	}

	void RecordBattleParticipation()
	{
		ConsecutiveBattlesWithoutRest++;
		FatigueLevel = FMath::Clamp(FatigueLevel + 15, 0, 100);
		DrainVigor(15.0f);

		if (FatigueLevel >= 70)
		{
			if (Condition == EAdventurerCondition::Healthy)
			{
				Condition = EAdventurerCondition::Fatigued;
			}
			float HeavyUsePenalty = -8.0f;
			if (Personality == EAdventurerPersonality::Carefree) HeavyUsePenalty = -16.0f;
			ModifySatisfaction(HeavyUsePenalty);
		}
	}

	void RecoverFromRest(bool bLuxuryRest = false)
	{
		bIsIncapacitated = false;
		ConsecutiveKOs = 0;
		FatigueLevel = 0;
		ConsecutiveBattlesWithoutRest = 0;
		RestDaysRemaining = 0;
		BurnoutDaysRemaining = 0;
		Vigor = 100.0f;
		bEmergencyHazardDeployed = false;

		if (GrievanceState == EAdventurerGrievanceState::OnStrike)
		{
			Condition = EAdventurerCondition::OnStrike;
		}
		else
		{
			Condition = EAdventurerCondition::Healthy;
		}

		if (bLuxuryRest)
		{
			ModifySatisfaction(15.0f);
		}
	}

	void ModifySatisfaction(float Delta)
	{
		Satisfaction = FMath::Clamp(Satisfaction + Delta, 0.0f, 100.0f);
		if (Satisfaction >= 50.0f)
		{
			GrievanceState = EAdventurerGrievanceState::Content;
			bWantsToLeave = false;
			bIsOnStrike = false;
			bIsUsable = true;
			DaysDissatisfied = 0;
			DaysUntilDeparture = 0.0f;
			DepartureReason = FText::GetEmpty();
			CurrentGrievance = FAdventurerGrievance();

			if (!bIsIncapacitated && BurnoutDaysRemaining <= 0)
			{
				Condition = (FatigueLevel >= 70 || Vigor < 30.0f) ? EAdventurerCondition::Fatigued : EAdventurerCondition::Healthy;
			}
		}
		else if (Satisfaction < 30.0f)
		{
			if (bIsOnStrike || GrievanceState == EAdventurerGrievanceState::OnStrike)
			{
				Condition = EAdventurerCondition::OnStrike;
			}
		}
	}

	bool IsDissatisfied() const
	{
		return Satisfaction < 30.0f || GrievanceState != EAdventurerGrievanceState::Content;
	}

	bool CanDeployToBattle() const
	{
		if (bIsIncapacitated || Condition == EAdventurerCondition::Incapacitated)
		{
			return false;
		}

		if (Condition == EAdventurerCondition::BurnoutLockout || BurnoutDaysRemaining > 0)
		{
			return false;
		}

		if (bEmergencyHazardDeployed)
		{
			return true;
		}

		return bIsUsable && !bIsOnStrike && GrievanceState != EAdventurerGrievanceState::OnStrike;
	}



	static FAdventurerGrievance GeneratePersonalityGrievance(EAdventurerPersonality InPersonality, int32 DayCount, FName InFavoriteDish, int32 InConsecutiveKOs = 0, int32 InFatigueLevel = 0)
	{
		FAdventurerGrievance G;
		G.DaysDissatisfied = DayCount;
		if (DayCount <= 3) G.CompoundingSeverity = 1;
		else if (DayCount <= 7) G.CompoundingSeverity = 2;
		else G.CompoundingSeverity = 3;

		const int32 Sev = G.CompoundingSeverity;
		const int32 BaseGald = 300;

		// Terrible Use trigger: Combat Trauma from repeated knockouts
		if (InConsecutiveKOs >= 2)
		{
			G.CauseTitle = FText::FromString(TEXT("Combat Trauma & Near-Death Neglect"));
			G.CauseDescription = FText::FromString(TEXT("Repeatedly knocked out and left to bleed against demons! Demands immediate medical rest, Life Bottles, and upgraded armor."));
			G.DemandedItemID = TEXT("Consumable_LifeBottle");
			G.DemandedGaldCost = 450 * Sev;
			if (DayCount == 1) G.DailyNoticeText = FText::FromString(TEXT("I nearly died out there twice! I can't keep risking my life without better medical support!"));
			else if (DayCount <= 3) G.DailyNoticeText = FText::FromString(TEXT("My battle wounds are throbbing. I demand medicine and adequate downtime!"));
			else if (DayCount <= 7) G.DailyNoticeText = FText::FromString(TEXT("You are treating me like disposable fodder! Pay me hazard compensation or I strike!"));
			else G.DailyNoticeText = FText::FromString(TEXT("I am ON STRIKE. I refuse to lift a weapon until my trauma and hazard pay are paid in full!"));
			return G;
		}

		// Heavy Use trigger: Combat Burnout from continuous fighting without rest
		if (InFatigueLevel >= 80)
		{
			G.CauseTitle = FText::FromString(TEXT("Exhaustion & Combat Burnout"));
			G.CauseDescription = FText::FromString(TEXT("Forced to fight consecutive missions without rest. Demands mandatory Inn stay and hot meals."));
			G.DemandedItemID = InFavoriteDish != NAME_None ? InFavoriteDish : TEXT("Dish_Steak");
			G.DemandedGaldCost = 350 * Sev;
			if (DayCount == 1) G.DailyNoticeText = FText::FromString(TEXT("I haven't slept in days. I need rest before my body collapses in combat."));
			else if (DayCount <= 3) G.DailyNoticeText = FText::FromString(TEXT("Exhaustion is affecting my combat reflexes. We need a paid day off at the Inn!"));
			else if (DayCount <= 7) G.DailyNoticeText = FText::FromString(TEXT("I cannot stand anymore. If you send me out again without rest, I will strike!"));
			else G.DailyNoticeText = FText::FromString(TEXT("I am ON STRIKE from exhaustion. My weapon stays down until I receive full Inn rest and wages!"));
			return G;
		}

		switch (InPersonality)
		{
		case EAdventurerPersonality::Brave:
			G.CauseTitle = FText::FromString(TEXT("Lack of Worthy Foes"));
			G.CauseDescription = FText::FromString(TEXT("Bored by minor pests. Demands a high-tier demon subjugation bounty or boss hunt."));
			G.DemandedItemID = TEXT("Bounty_Hound_01");
			G.DemandedGaldCost = BaseGald * Sev;
			break;

		case EAdventurerPersonality::Stoic:
			G.CauseTitle = FText::FromString(TEXT("Dilapidated Defenses & Fragile Armor"));
			G.CauseDescription = FText::FromString(TEXT("Disturbed by weak village barricades and unrefined armor. Demands blacksmith forge upgrades."));
			G.DemandedItemID = TEXT("Mat_IronOre");
			G.DemandedGaldCost = 350 * Sev;
			break;
		case EAdventurerPersonality::Arcane:
			G.CauseTitle = FText::FromString(TEXT("Mana Reagent Starvation"));
			G.CauseDescription = FText::FromString(TEXT("Alchemy reagents and mana catalyst crystals are depleted. Demands purified demon cores."));
			G.DemandedItemID = TEXT("Mat_DemonCore");
			G.DemandedGaldCost = 400 * Sev;
			break;
		case EAdventurerPersonality::Greedy:
			G.CauseTitle = FText::FromString(TEXT("Unfair Contract & Low Wages"));
			G.CauseDescription = FText::FromString(TEXT("Complains quest cuts and wages are insultingly low. Demands an immediate retention bonus."));
			G.DemandedItemID = NAME_None;
			G.DemandedGaldCost = 500 * (Sev * Sev);
			break;
		case EAdventurerPersonality::DemonHunter:
			G.CauseTitle = FText::FromString(TEXT("Lax Demonic Vigilance"));
			G.CauseDescription = FText::FromString(TEXT("Furious that nearby demon nests remain unpurged while the guild wastes time."));
			G.DemandedItemID = TEXT("Mat_DemonCore");
			G.DemandedGaldCost = 300 * Sev;
			break;
		case EAdventurerPersonality::Diligent:
			G.CauseTitle = FText::FromString(TEXT("Stagnant Training Grounds"));
			G.CauseDescription = FText::FromString(TEXT("Feels skills dulling from lack of structured drills. Demands guild hall training facilities."));
			G.DemandedItemID = TEXT("Item_AppleGel");
			G.DemandedGaldCost = 350 * Sev;
			break;
		case EAdventurerPersonality::Foodie:
			G.CauseTitle = FText::FromString(TEXT("Culinary Despair"));
			G.CauseDescription = FText::FromString(TEXT("Refuses to eat bland travel rations. Demands a gourmet cooked dish from the Wonder Chef."));
			G.DemandedItemID = (InFavoriteDish != NAME_None) ? InFavoriteDish : TEXT("Dish_MaboCurry");
			G.DemandedGaldCost = 250 * Sev;
			break;
		case EAdventurerPersonality::Virtuoso:
			G.CauseTitle = FText::FromString(TEXT("Unappreciated Artistry"));
			G.CauseDescription = FText::FromString(TEXT("Feels combat elegance is taken for granted. Demands public guild praise and a Commendation Medal."));
			G.DemandedItemID = TEXT("Item_GuildMedal");
			G.DemandedGaldCost = 450 * Sev;
			break;
		case EAdventurerPersonality::Skittish:
			G.CauseTitle = FText::FromString(TEXT("Critical Medical Supply Shortage"));
			G.CauseDescription = FText::FromString(TEXT("Terrified of fatal wounds. Demands shop shelves be stocked with Life Bottles and Panaceas."));
			G.DemandedItemID = TEXT("Item_LifeBottle");
			G.DemandedGaldCost = 300 * Sev;
			break;
		case EAdventurerPersonality::Zealous:
			G.CauseTitle = FText::FromString(TEXT("Demonic Corruption Unpurified"));
			G.CauseDescription = FText::FromString(TEXT("Refuses to stand near foul demon miasma. Demands core purification at the Alchemy Lab."));
			G.DemandedItemID = TEXT("Item_PanaceaBottle");
			G.DemandedGaldCost = 350 * Sev;
			break;
		case EAdventurerPersonality::Bloodthirsty:
			G.CauseTitle = FText::FromString(TEXT("Combat Deprivation"));
			G.CauseDescription = FText::FromString(TEXT("Blood boils from too many peaceful days. Demands immediate deployment or weapon honing at the forge."));
			G.DemandedItemID = TEXT("Weapon_IronSword");
			G.DemandedGaldCost = 350 * Sev;
			break;
		case EAdventurerPersonality::Technician:
			G.CauseTitle = FText::FromString(TEXT("Subpar & Dull Equipment"));
			G.CauseDescription = FText::FromString(TEXT("Cannot perform AG combo loops with blunt blades. Demands weapon enhancement +1 or better."));
			G.DemandedItemID = TEXT("Tool_FarmingHoe");
			G.DemandedGaldCost = 400 * Sev;
			break;
		case EAdventurerPersonality::Protector:
			G.CauseTitle = FText::FromString(TEXT("Party Vulnerability & Neglected Rest"));
			G.CauseDescription = FText::FromString(TEXT("Distressed by injured teammates. Demands upgraded Inn suites or sturdy shields."));
			G.DemandedItemID = TEXT("Item_AppleGel");
			G.DemandedGaldCost = 300 * Sev;
			break;
		case EAdventurerPersonality::Scholar:
			G.CauseTitle = FText::FromString(TEXT("Intellectual Stagnation"));
			G.CauseDescription = FText::FromString(TEXT("Town lacks archives and rare monster specimens. Demands demon cores and alchemical manuscripts."));
			G.DemandedItemID = TEXT("Mat_DemonCore");
			G.DemandedGaldCost = 400 * Sev;
			break;
		case EAdventurerPersonality::HotHeaded:
			G.CauseTitle = FText::FromString(TEXT("Simmering Impatience"));
			G.CauseDescription = FText::FromString(TEXT("Furious at being kept waiting. Demands a blazing hot spicy meal or immediate arena duel."));
			G.DemandedItemID = TEXT("Dish_MaboCurry");
			G.DemandedGaldCost = 300 * Sev;
			break;
		case EAdventurerPersonality::LoneWolf:
			G.CauseTitle = FText::FromString(TEXT("Suffocating Crowds & Commoner Bunkhouse"));
			G.CauseDescription = FText::FromString(TEXT("Hates crowded barracks. Demands private estate housing or solitary scouting dispatch."));
			G.DemandedItemID = TEXT("Mat_Timber");
			G.DemandedGaldCost = 500 * Sev;
			break;
		case EAdventurerPersonality::Chivalrous:
			G.CauseTitle = FText::FromString(TEXT("Civic Neglect & Tarnished Honor"));
			G.CauseDescription = FText::FromString(TEXT("Disappointed by dilapidated village buildings. Demands civic building tier upgrades or guild rank rise."));
			G.DemandedItemID = TEXT("Item_GuildMedal");
			G.DemandedGaldCost = 450 * Sev;
			break;
		case EAdventurerPersonality::Carefree:
			G.CauseTitle = FText::FromString(TEXT("Lack of Festive Merriment"));
			G.CauseDescription = FText::FromString(TEXT("Town is too gloomy. Demands tavern merriment, fruit parfaits, and leisure time."));
			G.DemandedItemID = TEXT("Dish_FruitParfait");
			G.DemandedGaldCost = 250 * Sev;
			break;
		}

		if (DayCount <= 3)
		{
			G.DailyNoticeText = FText::FromString(FString::Printf(TEXT("Day %d Notice: %s — %s (Early resolution recommended)."),
				DayCount, *G.CauseTitle.ToString(), *G.CauseDescription.ToString()));
		}
		else if (DayCount <= 7)
		{
			G.DailyNoticeText = FText::FromString(FString::Printf(TEXT("URGENT (Day %d/7): %s! Demands compounded to %d Gald or %s. Strike begins on Day 8!"),
				DayCount, *G.CauseTitle.ToString(), G.DemandedGaldCost, *G.DemandedItemID.ToString()));
		}
		else if (DayCount <= 14)
		{
			G.DailyNoticeText = FText::FromString(FString::Printf(TEXT("ON STRIKE (Day %d/14): Adventurer is UNUSABLE! Demands %d Gald and %s. Permanent departure in %d days!"),
				DayCount, G.DemandedGaldCost, *G.DemandedItemID.ToString(), 15 - DayCount));
		}
		else
		{
			G.DailyNoticeText = FText::FromString(TEXT("FINAL DEPARTURE: Grievance ignored for 14 full days. Adventurer has left the guild."));
		}

		return G;
	}

	static int32 GetRankValue(EAdventurerRank Rank)
	{
		return static_cast<int32>(Rank);
	}

	static EAdventurerRank GetRankFromValue(int32 Value)
	{
		return static_cast<EAdventurerRank>(FMath::Clamp(Value, 0, 7));
	}

	// Progression
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	int32 Level = 1;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Stats")
	int32 CurrentExp = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	int32 ExpToNextLevel = 100;

	// Base Attributes
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float BaseHP = 450.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float BaseTP = 80.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float BaseAttack = 25.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float BaseDefense = 15.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float BaseArtePower = 20.0f;

	// Equipment Loadout
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Equipment")
	FAdventurerEquipment Equipment;

	// Permanent Dietary Nutrition (Wonder Chef Camp Cooking)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Nutrition")
	FAdventurerNutrition Nutrition;

	// Inherited Legacy Crest (from retired veteran)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Legacy")
	FLegacyCrest AssignedLegacyCrest;

	// Mentorship Linkage
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	FName MentorID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Mentorship")
	FName DiscipleID = NAME_None;

	// Recruitment & Roster Status
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recruitment")
	int32 HiringCost = 250;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Recruitment")
	EAdventurerAssignment Assignment = EAdventurerAssignment::RestingInTown;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Artes")
	TArray<FName> LearnedArtes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Artes")
	TArray<FName> CrossClassArtes;

	// Partner Social Bonds (Rank 1-5 with party members)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Bonds")
	TMap<FName, int32> PartnerBonds;

	// Calculated Attributes (Base + Equipment + Personality + Nutrition + Legacy + Housing)
	float GetTotalAttack() const
	{
		float Atk = (BaseAttack + Equipment.AddedAttack) * (1.0f + (Nutrition.Protein * 0.005f));
		if (AssignedLegacyCrest.CrestID != NAME_None) Atk *= AssignedLegacyCrest.StatGrowthMultiplier;
		if (Personality == EAdventurerPersonality::Brave) Atk *= 1.15f;
		Atk *= GetHousingAttackMultiplier();
		return Atk;
	}

	float GetTotalDefense() const
	{
		float Def = (BaseDefense + Equipment.AddedDefense) * (1.0f + (Nutrition.Vitality * 0.005f));
		if (AssignedLegacyCrest.CrestID != NAME_None) Def *= AssignedLegacyCrest.StatGrowthMultiplier;
		if (Personality == EAdventurerPersonality::Stoic) Def *= 1.20f;
		Def *= GetHousingDefenseMultiplier();
		return Def;
	}

	float GetTotalMaxHP() const
	{
		float HP = (BaseHP + Equipment.AddedMaxHP) * (1.0f + (Nutrition.Vitality * 0.005f));
		if (AssignedLegacyCrest.CrestID != NAME_None) HP *= AssignedLegacyCrest.StatGrowthMultiplier;
		if (Personality == EAdventurerPersonality::Protector) HP *= (1.0f + (GetHouseTierValue() * 0.03f));
		return HP;
	}

	float GetTotalMaxTP() const
	{
		float TP = (BaseTP + Equipment.AddedMaxTP) * (1.0f + (Nutrition.ManaInfusion * 0.005f));
		if (AssignedLegacyCrest.CrestID != NAME_None) TP *= AssignedLegacyCrest.StatGrowthMultiplier;
		return TP;
	}

	float GetTotalArtePower() const
	{
		float Pwr = BaseArtePower * (1.0f + (Nutrition.ManaInfusion * 0.005f));
		if (AssignedLegacyCrest.CrestID != NAME_None) Pwr *= AssignedLegacyCrest.StatGrowthMultiplier;
		if (Personality == EAdventurerPersonality::Arcane) Pwr *= 1.25f;
		Pwr *= GetHousingArtePowerMultiplier();
		return Pwr;
	}

	static int32 GetClassTier(EAdventurerClass InClass)
	{
		uint8 Val = static_cast<uint8>(InClass);
		if (Val <= 5) return 1;       // Swordsman .. Paladin
		if (Val <= 11) return 2;      // Warrior .. Knight
		return 3;                     // Swordmaster .. Crusader
	}

	static bool CanBranchToClass(EAdventurerClass CurrentClass, EAdventurerClass TargetClass)
	{
		switch (CurrentClass)
		{
		case EAdventurerClass::Swordsman:
			return TargetClass == EAdventurerClass::Warrior;
		case EAdventurerClass::Warrior:
			return TargetClass == EAdventurerClass::Swordmaster || TargetClass == EAdventurerClass::RuneKnight;
		case EAdventurerClass::Berserker:
			return TargetClass == EAdventurerClass::Gladiator;
		case EAdventurerClass::Gladiator:
			return TargetClass == EAdventurerClass::Warmaster || TargetClass == EAdventurerClass::BloodReaver;
		case EAdventurerClass::Mage:
			return TargetClass == EAdventurerClass::Sorcerer;
		case EAdventurerClass::Sorcerer:
			return TargetClass == EAdventurerClass::Archmage || TargetClass == EAdventurerClass::Arcanist;
		case EAdventurerClass::Healer:
			return TargetClass == EAdventurerClass::Cleric;
		case EAdventurerClass::Cleric:
			return TargetClass == EAdventurerClass::HighPriest || TargetClass == EAdventurerClass::HolyInquisitor;
		case EAdventurerClass::Rogue:
			return TargetClass == EAdventurerClass::Scout;
		case EAdventurerClass::Scout:
			return TargetClass == EAdventurerClass::ShadowAssassin || TargetClass == EAdventurerClass::BountyHunter;
		case EAdventurerClass::Paladin:
			return TargetClass == EAdventurerClass::Knight;
		case EAdventurerClass::Knight:
			return TargetClass == EAdventurerClass::GuardianTemplar || TargetClass == EAdventurerClass::Crusader;
		default:
			return false;
		}
	}

	float GetCriticalChanceBonus() const
	{
		float Bonus = (Personality == EAdventurerPersonality::Carefree) ? 0.20f : 0.0f;
		Bonus += GetHousingCritBonus();
		return Bonus;
	}

	float GetDemonDamageMultiplier() const
	{
		float Mult = (Personality == EAdventurerPersonality::DemonHunter) ? 1.35f : 1.0f;
		Mult *= GetHousingDemonDamageMultiplier();
		return Mult;
	}

	float GetHolyDamageMultiplier() const
	{
		return (Personality == EAdventurerPersonality::Zealous) ? 1.40f : 1.0f;
	}

	float GetFireDamageMultiplier() const
	{
		return (Personality == EAdventurerPersonality::HotHeaded) ? 1.25f : 1.0f;
	}

	float GetGaldBonusMultiplier() const
	{
		float Mult = (Personality == EAdventurerPersonality::Greedy) ? 1.25f : 1.0f;
		Mult *= GetHousingGaldBonusMultiplier();
		return Mult;
	}

	float GetExpBonusMultiplier() const
	{
		float Mult = (Personality == EAdventurerPersonality::Diligent) ? 1.30f : 1.0f;
		Mult *= GetHousingExpBonusMultiplier();
		return Mult;
	}

	float GetOverlimitAccelerationMultiplier() const
	{
		float Mult = (Personality == EAdventurerPersonality::Virtuoso) ? 1.50f : 1.0f;
		Mult *= GetHousingOverlimitRateMultiplier();
		return Mult;
	}

	float GetMovementSpeedMultiplier() const
	{
		float Mult = (Personality == EAdventurerPersonality::Skittish) ? 1.30f : 1.0f;
		Mult *= GetHousingSpeedMultiplier();
		return Mult;
	}

	float GetCookingEffectMultiplier() const
	{
		return (Personality == EAdventurerPersonality::Foodie) ? 2.0f : 1.0f;
	}

	float GetRareDropMultiplier() const
	{
		float Mult = (Personality == EAdventurerPersonality::Scholar) ? 1.40f : 1.0f;
		Mult *= GetHousingRareDropMultiplier();
		return Mult;
	}


	float GetGuardEfficiencyMultiplier() const
	{
		return (Personality == EAdventurerPersonality::Protector) ? 1.25f : 1.0f;
	}

	float GetPartyAuraBonusMultiplier() const
	{
		return (Personality == EAdventurerPersonality::Chivalrous) ? 1.10f : 1.0f;
	}

	float GetBloodthirstyAttackMultiplier(float CurrentHPRatio) const
	{
		if (Personality == EAdventurerPersonality::Bloodthirsty && CurrentHPRatio < 0.35f)
		{
			return 1.50f;
		}
		return 1.0f;
	}

	bool HasTechnicianAGRefund() const
	{
		return Personality == EAdventurerPersonality::Technician;
	}

	bool IsLoneWolf() const
	{
		return Personality == EAdventurerPersonality::LoneWolf;
	}
};

/**
 * Guild Expedition / Dispatch Mission for hired adventurers.
 */
USTRUCT(BlueprintType)
struct FAdventurerExpedition
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	FName ExpeditionID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	FText ExpeditionName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	TArray<FName> AssignedAdventurerIDs;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	float DurationSeconds = 60.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Expedition")
	float TimeElapsed = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	FName TargetBountyID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	int32 GoldReward = 300;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Expedition")
	int32 ExpReward = 200;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Expedition")
	bool bIsCompleted = false;
};
