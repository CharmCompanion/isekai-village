// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiMenuWidgets.h — Complete UMG Widget Base Classes for Town Hall, Guild Board, 11-Disc Skill Grid, Titles & Cooking

#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "AdventurerSystemTypes.h"
#include "TownEconomyTypes.h"
#include "TitleSystemTypes.h"
#include "SkillGridTypes.h"
#include "IsekaiMenuWidgets.generated.h"

class UAdventurerManagerComponent;
class ALordsManorActor;
class USkillGridComponent;
class UTitleManagerComponent;

/**
 * Interactive Guild Notice Board UMG Widget
 * Manages Recruitment candidates, Auxiliary Squad rotation (Alpha, Beta, Gamma), and Rank C+ Private Housing Deeds.
 */
UCLASS(Abstract, Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API UIsekaiGuildBoardWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "GuildBoard")
	void InitializeGuildBoard(UAdventurerManagerComponent* InManager);

	UPROPERTY(BlueprintReadOnly, Category = "GuildBoard")
	TObjectPtr<UAdventurerManagerComponent> AdventurerManager;

	// ── Recruitment View ──
	UFUNCTION(BlueprintPure, Category = "GuildBoard|Recruitment")
	TArray<FAdventurerProfile> GetVisitingCandidates() const;

	UFUNCTION(BlueprintCallable, Category = "GuildBoard|Recruitment")
	bool HireCandidate(FName AdventurerID, UPARAM(ref) int32& PlayerGold);

	// ── Auxiliary Squads View (Team Alpha, Team Beta, Team Gamma) ──
	UFUNCTION(BlueprintPure, Category = "GuildBoard|Squads")
	TArray<FName> GetSquadMembers(uint8 SquadIndex) const; // 0 = Alpha, 1 = Beta, 2 = Gamma

	UFUNCTION(BlueprintPure, Category = "GuildBoard|Squads")
	bool GetHeroProfile(FName AdventurerID, FAdventurerProfile& OutProfile) const;

	UFUNCTION(BlueprintCallable, Category = "GuildBoard|Squads")
	bool SwapSquadToActive(uint8 TargetAuxIndex); // 1 = Beta, 2 = Gamma

	UFUNCTION(BlueprintCallable, Category = "GuildBoard|Squads")
	bool AssignHeroToSquad(FName AdventurerID, uint8 SquadIndex, int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "GuildBoard|Squads")
	bool RemoveHeroFromSquad(FName AdventurerID, uint8 SquadIndex);

	// ── Private Housing Deeds View (Rank C+) ──
	UFUNCTION(BlueprintPure, Category = "GuildBoard|Housing")
	bool CanHeroOwnHouse(FName AdventurerID) const;

	UFUNCTION(BlueprintCallable, Category = "GuildBoard|Housing")
	bool AssignLotDeed(FName AdventurerID, int32 LotIndex, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "GuildBoard|Housing")
	bool UpgradeResidence(FName AdventurerID, UPARAM(ref) int32& PlayerGold, FText& OutReason);

	// ── Blueprint-Implementable Visual / Audio Events ──
	UFUNCTION(BlueprintImplementableEvent, Category = "GuildBoard|Events")
	void OnCandidateHired(FName AdventurerID);

	UFUNCTION(BlueprintImplementableEvent, Category = "GuildBoard|Events")
	void OnSquadRotated(uint8 ActiveAuxIndex);

	UFUNCTION(BlueprintImplementableEvent, Category = "GuildBoard|Events")
	void OnHouseUpgraded(FName AdventurerID, EBuildingTier NewTier);
};

/**
 * Interactive Lord's Manor / Town Hall Administration UMG Widget
 * Manages Village Municipal Tiers, Town-wide Architectural Styles, and Noble Patron Tax Ledger.
 */
UCLASS(Abstract, Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API UIsekaiLordsManorWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Manor")
	void InitializeManor(ALordsManorActor* InManor);

	UPROPERTY(BlueprintReadOnly, Category = "Manor")
	TObjectPtr<ALordsManorActor> LordsManor;

	UFUNCTION(BlueprintPure, Category = "Manor|Village")
	EBuildingTier GetCurrentVillageTier() const;

	UFUNCTION(BlueprintPure, Category = "Manor|Village")
	ETownArchitecturalStyle GetCurrentVillageStyle() const;

	UFUNCTION(BlueprintCallable, Category = "Manor|Village")
	bool UpgradeVillageManor(UPARAM(ref) int32& PlayerGold, UPARAM(ref) FTownStockpile& Stockpile, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "Manor|Buildings")
	bool UpgradeTownBuilding(ETownBuildingType BuildingType, UPARAM(ref) int32& PlayerGold, UPARAM(ref) FTownStockpile& Stockpile, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "Manor|Village")
	void ChangeVillageStyle(ETownArchitecturalStyle NewStyle);

	UFUNCTION(BlueprintPure, Category = "Manor|Economy")
	int32 GetProjectedDailyTaxRevenue() const;

	UFUNCTION(BlueprintPure, Category = "Manor|Economy")
	int32 GetLandedNobleCount() const;

	UFUNCTION(BlueprintImplementableEvent, Category = "Manor|Events")
	void OnVillageTierUpgraded(EBuildingTier NewTier, ETownArchitecturalStyle NewStyle);
};

/**
 * Interactive 11-Disc Multi-Wheel Sphere Grid UMG Widget
 * Manages Center A/B Coin Flip discs, Combat Discs, Town Mini-Game Discs, and SP Node Unlocking.
 */
UCLASS(Abstract, Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API UIsekaiSkillGridWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "SkillGrid")
	void InitializeSkillGrid(USkillGridComponent* InGrid);

	UPROPERTY(BlueprintReadOnly, Category = "SkillGrid")
	TObjectPtr<USkillGridComponent> SkillGrid;

	UFUNCTION(BlueprintPure, Category = "SkillGrid")
	int32 GetAvailableSP() const;

	UFUNCTION(BlueprintPure, Category = "SkillGrid")
	TArray<FSphereDiscData> GetAllDiscs() const;

	UFUNCTION(BlueprintPure, Category = "SkillGrid")
	bool IsDiscUnlocked(FName DiscID) const;

	UFUNCTION(BlueprintCallable, Category = "SkillGrid")
	bool UnlockNode(FName NodeID, FText& OutReason);

	UFUNCTION(BlueprintCallable, Category = "SkillGrid")
	bool ToggleCenterCoinFlip(bool bSelectB, FText& OutReason);

	UFUNCTION(BlueprintImplementableEvent, Category = "SkillGrid|Events")
	void OnNodeUnlocked(FName NodeID);
};

/**
 * Interactive Tales Titles & Passive Mastery Menu UMG Widget
 */
UCLASS(Abstract, Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API UIsekaiTitleMenuWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "Titles")
	void InitializeTitleMenu(UTitleManagerComponent* InManager);

	UPROPERTY(BlueprintReadOnly, Category = "Titles")
	TObjectPtr<UTitleManagerComponent> TitleManager;

	UFUNCTION(BlueprintCallable, Category = "Titles")
	bool EquipTitle(FName TitleID);

	UFUNCTION(BlueprintPure, Category = "Titles")
	FName GetEquippedTitleID() const;

	UFUNCTION(BlueprintPure, Category = "Titles")
	TArray<FName> GetUnlockedTitles() const;

	UFUNCTION(BlueprintImplementableEvent, Category = "Titles|Events")
	void OnTitleEquipped(FName TitleID);
};

/**
 * Interactive Campfire & Wonder Chef Dietary Nutrition Menu UMG Widget
 */
UCLASS(Abstract, Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API UIsekaiCampCookingWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "CampCooking")
	void InitializeCampCooking(UAdventurerManagerComponent* InManager);

	UPROPERTY(BlueprintReadOnly, Category = "CampCooking")
	TObjectPtr<UAdventurerManagerComponent> AdventurerManager;

	UFUNCTION(BlueprintCallable, Category = "CampCooking")
	bool CookCampMeal(const FAdventurerNutrition& MealNutrition);

	UFUNCTION(BlueprintPure, Category = "CampCooking")
	int32 GetPartnerBondLevel(FName AdvA, FName AdvB) const;

	UFUNCTION(BlueprintImplementableEvent, Category = "CampCooking|Events")
	void OnMealPrepared();
};
