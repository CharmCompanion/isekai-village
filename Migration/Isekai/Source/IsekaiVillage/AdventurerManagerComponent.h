// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurerManagerComponent.h — Component managing visiting adventurers, hiring, training, equipment, and guild dispatch

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "AdventurerSystemTypes.h"
#include "TownEconomyTypes.h"
#include "AdventurerManagerComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAdventurerHiredSignature, const FAdventurerProfile&, Adventurer);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerLeveledUpSignature, const FAdventurerProfile&, Adventurer, int32, NewLevel);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerEquipmentChangedSignature, FName, AdventurerID, const FAdventurerEquipment&, NewEquipment);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnExpeditionCompletedSignature, const FAdventurerExpedition&, CompletedExpedition);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnVisitingPoolRefreshedSignature);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerDepartureWarningSignature, FName, AdventurerID, const FText&, Reason);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAdventurerDepartedSignature, FName, AdventurerID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerStrikeStartedSignature, FName, AdventurerID, const FAdventurerGrievance&, Grievance);

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAdventurerStrikeResolvedSignature, FName, AdventurerID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPartyMentorshipCalculatedSignature, const FPartyMentorshipSynergy&, Synergy);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerIncapacitatedSignature, FName, AdventurerID, int32, IncapacitationCount);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerFatiguedSignature, FName, AdventurerID, int32, FatigueLevel);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnAdventurerHouseUpgradedSignature, FName, AdventurerID, EBuildingTier, NewTier, bool, bIsLandedNoble);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnAdventurerBurnoutStartedSignature, FName, AdventurerID, int32, LockoutDays);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAdventurerBurnoutRecoveredSignature, FName, AdventurerID);


UCLASS(ClassGroup = (AdventurerSystem), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UAdventurerManagerComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UAdventurerManagerComponent();

protected:
	virtual void BeginPlay() override;

public:
	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ── Roster & Pools ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Recruitment")
	TArray<FAdventurerProfile> VisitingAdventurers;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Roster")
	TArray<FAdventurerProfile> HiredAdventurers;

	// ── Squad Arrays (Team Alpha, Team Beta, Team Gamma) ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Party")
	TArray<FName> ActivePartyAdventurerIDs; // Team Alpha (Active in battle)

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Party")
	TArray<FName> AuxiliaryPartyBetaIDs; // Team Beta (Auxiliary Squad 1)

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Party")
	TArray<FName> AuxiliaryPartyGammaIDs; // Team Gamma (Auxiliary Squad 2)

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Expeditions")
	TArray<FAdventurerExpedition> ActiveExpeditions;


	// ── Recruitment & Raising ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Recruitment")
	void RefreshVisitingAdventurers(int32 Count = 4);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Recruitment")
	bool HireAdventurer(FName AdventurerID, UPARAM(ref) int32& PlayerGold);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Recruitment")
	bool DismissAdventurer(FName AdventurerID);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Raising")
	bool TrainAdventurer(FName AdventurerID, int32 ExpAmount);

	// ToS2 Style Evolution & Sphere Grid
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Evolution")
	bool FeedAdventurer(FName AdventurerID, FName FoodItemID, int32 ExpYield, float StatMultiplier);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Evolution")
	bool EvolveAdventurerClass(FName AdventurerID, EAdventurerClass NewClass);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Evolution")
	bool UnlockSphereNode(FName AdventurerID, class USphereGridDataAsset* GridAsset, FName NodeID);

	// ── Equipment Management ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Equipment")
	bool EquipWeapon(FName AdventurerID, FName WeaponID, float AtkBonus, EElement WeaponElement = EElement::Fire);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Equipment")
	bool EquipArmor(FName AdventurerID, FName ArmorID, float DefBonus);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Equipment")
	bool EquipAccessory(FName AdventurerID, FName AccessoryID, float HPBonus, float TPBonus);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Equipment")
	bool UnequipSlot(FName AdventurerID, uint8 SlotIndex); // 0=Weapon, 1=Armor, 2=Accessory

	// ── Party & Expeditions ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Party")
	bool AssignToActiveParty(FName AdventurerID, int32 PartySlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Party")
	bool RemoveFromActiveParty(FName AdventurerID);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Expeditions")
	bool StartExpedition(const TArray<FName>& AdventurerIDs, FName ExpeditionID, const FText& ExpeditionName, float DurationSeconds, int32 GoldReward, int32 ExpReward, FName TargetBountyID = NAME_None);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Expeditions")
	bool ClaimExpeditionReward(FName ExpeditionID, int32& OutGoldReward, int32& OutExpReward);

	UFUNCTION(BlueprintPure, Category = "Adventurers|Query")
	bool GetAdventurerProfile(FName AdventurerID, FAdventurerProfile& OutProfile) const;

	// ── Mentorship & Legacy (Human Breeding Equivalent) ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Legacy")
	TArray<FLegacyCrest> AvailableLegacyCrests;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Adventurers|Mentorship")
	TArray<FAdventurerMentorship> ActiveMentorships;

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Mentorship")
	bool AssignMentor(FName MentorID, FName DiscipleID);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Mentorship")
	bool RemoveMentor(FName DiscipleID);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Legacy")
	bool RetireVeteranToTown(FName VeteranID, FLegacyCrest& OutCrest);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Legacy")
	bool ApplyLegacyCrest(FName AdventurerID, FName CrestID);

	// ── Job Promotions (Branching Evolution Trees) ──
	UFUNCTION(BlueprintPure, Category = "Adventurers|Promotion")
	bool CanPromoteAdventurer(FName AdventurerID, EAdventurerClass TargetClass, FText& OutReason) const;

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Promotion")
	bool PromoteAdventurer(FName AdventurerID, EAdventurerClass TargetClass);

	// ── Nutrition & Camp Diet ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Nutrition")
	void ApplyCampMealToParty(const FAdventurerNutrition& MealNutrition);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Bonds")
	void IncreaseAdventurerBond(FName AdvA, FName AdvB, int32 BondPoints);

	UFUNCTION(BlueprintPure, Category = "Adventurers|Bonds")
	int32 GetAdventurerBondLevel(FName AdvA, FName AdvB) const;

	// ── Town Stockpiles (Food, Crafting, Shop Supplies) ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Adventurers|Stockpile")
	FTownStockpile TownStockpile;

	// ── Daily Simulation & Retention / Departure ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Roster")
	void AdvanceDayCycle();

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Appeasement")
	bool AppeaseWithGald(FName AdventurerID, UPARAM(ref) int32& PlayerGold, int32 BonusAmount = 300);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Appeasement")
	bool AppeaseWithMeal(FName AdventurerID, FName DishItemID);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Appeasement")
	bool AppeaseWithEquipment(FName AdventurerID, FName EquipmentID);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Appeasement")
	bool AppeaseWithGuildMedal(FName AdventurerID);

	// ── Combat Incapacitation, Fatigue & Rest Recovery ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Combat")
	void RecordBattleEnd(bool bVictory, const TArray<FName>& IncapacitatedIDs);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Rest")
	bool RestAdventurerAtInn(FName AdventurerID, bool bLuxuryBathhouse = false);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Rest")
	void RestEntireActivePartyAtInn(bool bLuxuryBathhouse = false);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Appeasement")
	bool DeployStrikingHeroWithHazardPay(FName AdventurerID, UPARAM(ref) int32& PlayerGold, FText& OutReason);

	// ── Auxiliary Squad Management (Team Alpha, Team Beta, Team Gamma) ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Auxiliary")
	bool SwapActiveWithAuxiliaryParty(uint8 TargetAuxIndex);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Auxiliary")
	bool AssignToAuxiliaryParty(FName AdventurerID, uint8 AuxIndex, int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Auxiliary")
	bool RemoveFromAuxiliaryParty(FName AdventurerID, uint8 AuxIndex);

	// ── Private Housing & Noble Estates Management (Rank C+) ──
	UFUNCTION(BlueprintCallable, Category = "Adventurers|Housing")
	bool AssignAdventurerToHouse(FName AdventurerID, int32 LotIndex, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Housing")
	bool UpgradeAdventurerHouse(FName AdventurerID, UPARAM(ref) int32& PlayerGold, FText& OutReason);

	UFUNCTION(BlueprintPure, Category = "Adventurers|Housing")
	int32 GetTotalLandedNoblesCount() const;

	UFUNCTION(BlueprintCallable, Category = "Adventurers|Housing")
	int32 CollectAdventurerNobleTaxes();

	// ── Passive Party Mentorship Synergy (1-3 Rank Delta) ──
	UFUNCTION(BlueprintPure, Category = "Adventurers|Mentorship")
	FPartyMentorshipSynergy CalculateActivePartyMentorshipSynergy() const;

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerHiredSignature OnAdventurerHired;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerLeveledUpSignature OnAdventurerLeveledUp;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerEquipmentChangedSignature OnAdventurerEquipmentChanged;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnExpeditionCompletedSignature OnExpeditionCompleted;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnVisitingPoolRefreshedSignature OnVisitingPoolRefreshed;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerDepartureWarningSignature OnAdventurerDepartureWarning;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerDepartedSignature OnAdventurerDeparted;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerStrikeStartedSignature OnAdventurerStrikeStarted;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerStrikeResolvedSignature OnAdventurerStrikeResolved;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnPartyMentorshipCalculatedSignature OnPartyMentorshipCalculated;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerIncapacitatedSignature OnAdventurerIncapacitated;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerFatiguedSignature OnAdventurerFatigued;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerHouseUpgradedSignature OnAdventurerHouseUpgraded;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerBurnoutStartedSignature OnAdventurerBurnoutStarted;

	UPROPERTY(BlueprintAssignable, Category = "Adventurers|Events")
	FOnAdventurerBurnoutRecoveredSignature OnAdventurerBurnoutRecovered;



private:
	FAdventurerProfile* FindHiredAdventurer(FName AdventurerID);
	void LevelUpAdventurer(FAdventurerProfile& Profile);
};

