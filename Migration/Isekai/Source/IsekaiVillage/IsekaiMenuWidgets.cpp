// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiMenuWidgets.cpp — Implementation of UMG menu widgets for Guild Board, Manor, Skill Grid, Titles & Cooking

#include "IsekaiMenuWidgets.h"
#include "AdventurerManagerComponent.h"
#include "LordsManorActor.h"
#include "SkillGridComponent.h"
#include "TitleManagerComponent.h"

// ═══════════════════════════════════════════════════════════════════════
// UIsekaiGuildBoardWidget
// ═══════════════════════════════════════════════════════════════════════

void UIsekaiGuildBoardWidget::InitializeGuildBoard(UAdventurerManagerComponent* InManager)
{
	AdventurerManager = InManager;
}

TArray<FAdventurerProfile> UIsekaiGuildBoardWidget::GetVisitingCandidates() const
{
	if (!AdventurerManager) return {};
	return AdventurerManager->VisitingAdventurers;
}

bool UIsekaiGuildBoardWidget::HireCandidate(FName AdventurerID, int32& PlayerGold)
{
	if (!AdventurerManager) return false;

	const bool bSuccess = AdventurerManager->HireAdventurer(AdventurerID, PlayerGold);
	if (bSuccess)
	{
		OnCandidateHired(AdventurerID);
	}
	return bSuccess;
}

TArray<FName> UIsekaiGuildBoardWidget::GetSquadMembers(uint8 SquadIndex) const
{
	if (!AdventurerManager) return {};

	switch (SquadIndex)
	{
	case 0:
		return AdventurerManager->ActivePartyAdventurerIDs;
	case 1:
		return AdventurerManager->AuxiliaryPartyBetaIDs;
	case 2:
		return AdventurerManager->AuxiliaryPartyGammaIDs;
	default:
		return {};
	}
}

bool UIsekaiGuildBoardWidget::GetHeroProfile(FName AdventurerID, FAdventurerProfile& OutProfile) const
{
	if (!AdventurerManager) return false;
	return AdventurerManager->GetAdventurerProfile(AdventurerID, OutProfile);
}

bool UIsekaiGuildBoardWidget::SwapSquadToActive(uint8 TargetAuxIndex)
{
	if (!AdventurerManager) return false;

	const bool bSuccess = AdventurerManager->SwapActiveWithAuxiliaryParty(TargetAuxIndex);
	if (bSuccess)
	{
		OnSquadRotated(TargetAuxIndex);
	}
	return bSuccess;
}

bool UIsekaiGuildBoardWidget::AssignHeroToSquad(FName AdventurerID, uint8 SquadIndex, int32 SlotIndex)
{
	if (!AdventurerManager) return false;

	if (SquadIndex == 0)
	{
		return AdventurerManager->AssignToActiveParty(AdventurerID, SlotIndex);
	}
	return AdventurerManager->AssignToAuxiliaryParty(AdventurerID, SquadIndex, SlotIndex);
}

bool UIsekaiGuildBoardWidget::RemoveHeroFromSquad(FName AdventurerID, uint8 SquadIndex)
{
	if (!AdventurerManager) return false;

	if (SquadIndex == 0)
	{
		return AdventurerManager->RemoveFromActiveParty(AdventurerID);
	}
	return AdventurerManager->RemoveFromAuxiliaryParty(AdventurerID, SquadIndex);
}

bool UIsekaiGuildBoardWidget::CanHeroOwnHouse(FName AdventurerID) const
{
	if (!AdventurerManager) return false;

	FAdventurerProfile Profile;
	if (AdventurerManager->GetAdventurerProfile(AdventurerID, Profile))
	{
		return Profile.CanOwnPrivateHouse();
	}
	return false;
}

bool UIsekaiGuildBoardWidget::AssignLotDeed(FName AdventurerID, int32 LotIndex, FText& OutReason)
{
	if (!AdventurerManager)
	{
		OutReason = FText::FromString(TEXT("Adventurer Manager not assigned to widget."));
		return false;
	}
	return AdventurerManager->AssignAdventurerToHouse(AdventurerID, LotIndex, OutReason);
}

bool UIsekaiGuildBoardWidget::UpgradeResidence(FName AdventurerID, int32& PlayerGold, FText& OutReason)
{
	if (!AdventurerManager)
	{
		OutReason = FText::FromString(TEXT("Adventurer Manager not assigned to widget."));
		return false;
	}

	const bool bSuccess = AdventurerManager->UpgradeAdventurerHouse(AdventurerID, PlayerGold, OutReason);
	if (bSuccess)
	{
		FAdventurerProfile Profile;
		if (AdventurerManager->GetAdventurerProfile(AdventurerID, Profile))
		{
			OnHouseUpgraded(AdventurerID, Profile.HouseData.HouseTier);
		}
	}
	return bSuccess;
}

// ═══════════════════════════════════════════════════════════════════════
// UIsekaiLordsManorWidget
// ═══════════════════════════════════════════════════════════════════════

void UIsekaiLordsManorWidget::InitializeManor(ALordsManorActor* InManor)
{
	LordsManor = InManor;
}

EBuildingTier UIsekaiLordsManorWidget::GetCurrentVillageTier() const
{
	return LordsManor ? LordsManor->ManorTier : EBuildingTier::Tier_1_Rustic;
}

ETownArchitecturalStyle UIsekaiLordsManorWidget::GetCurrentVillageStyle() const
{
	return LordsManor ? LordsManor->VillageStyle : ETownArchitecturalStyle::RusticTimber;
}

bool UIsekaiLordsManorWidget::UpgradeVillageManor(int32& PlayerGold, FTownStockpile& Stockpile, FText& OutReason)
{
	if (!LordsManor)
	{
		OutReason = FText::FromString(TEXT("Lord's Manor not assigned to widget."));
		return false;
	}

	const bool bSuccess = LordsManor->UpgradeManor(PlayerGold, Stockpile, OutReason);
	if (bSuccess)
	{
		OnVillageTierUpgraded(LordsManor->ManorTier, LordsManor->VillageStyle);
	}
	return bSuccess;
}

bool UIsekaiLordsManorWidget::UpgradeTownBuilding(ETownBuildingType BuildingType, int32& PlayerGold, FTownStockpile& Stockpile, FText& OutReason)
{
	if (!LordsManor)
	{
		OutReason = FText::FromString(TEXT("Lord's Manor not assigned to widget."));
		return false;
	}
	return LordsManor->UpgradeBuilding(BuildingType, PlayerGold, Stockpile, OutReason);
}

void UIsekaiLordsManorWidget::ChangeVillageStyle(ETownArchitecturalStyle NewStyle)
{
	if (LordsManor)
	{
		LordsManor->SetVillageArchitecturalStyle(NewStyle);
	}
}

int32 UIsekaiLordsManorWidget::GetProjectedDailyTaxRevenue() const
{
	return LordsManor ? LordsManor->CollectDailyTaxes() : 0;
}

int32 UIsekaiLordsManorWidget::GetLandedNobleCount() const
{
	return LordsManor ? LordsManor->NoblePatronCount : 0;
}

// ═══════════════════════════════════════════════════════════════════════
// UIsekaiSkillGridWidget
// ═══════════════════════════════════════════════════════════════════════

void UIsekaiSkillGridWidget::InitializeSkillGrid(USkillGridComponent* InGrid)
{
	SkillGrid = InGrid;
}

int32 UIsekaiSkillGridWidget::GetAvailableSP() const
{
	return SkillGrid ? SkillGrid->AvailableSP : 0;
}

TArray<FSphereDiscData> UIsekaiSkillGridWidget::GetAllDiscs() const
{
	return (SkillGrid && SkillGrid->ActiveGrid) ? SkillGrid->ActiveGrid->Discs : TArray<FSphereDiscData>();
}

bool UIsekaiSkillGridWidget::IsDiscUnlocked(FName DiscID) const
{
	return SkillGrid ? SkillGrid->IsDiscUnlocked(DiscID) : false;
}

bool UIsekaiSkillGridWidget::UnlockNode(FName NodeID, FText& OutReason)
{
	if (!SkillGrid)
	{
		OutReason = FText::FromString(TEXT("Skill Grid not assigned to widget."));
		return false;
	}

	if (!SkillGrid->CanUnlockNode(NodeID))
	{
		OutReason = FText::FromString(TEXT("Cannot unlock node: prerequisites not met or insufficient SP."));
		return false;
	}

	const bool bSuccess = SkillGrid->UnlockNode(NodeID);
	if (bSuccess)
	{
		OnNodeUnlocked(NodeID);
	}
	else
	{
		OutReason = FText::FromString(TEXT("Failed to unlock skill node."));
	}
	return bSuccess;
}

bool UIsekaiSkillGridWidget::ToggleCenterCoinFlip(bool bSelectB, FText& OutReason)
{
	if (!SkillGrid)
	{
		OutReason = FText::FromString(TEXT("Skill Grid not assigned to widget."));
		return false;
	}

	FName FrontDiscID = bSelectB ? FName("Disc_CenterA") : FName("Disc_CenterB");
	FName OutBackDiscID = NAME_None;
	const bool bSuccess = SkillGrid->FlipCoinDisc(FrontDiscID, OutBackDiscID);
	if (!bSuccess)
	{
		OutReason = FText::FromString(TEXT("Complete all nodes on current disc to flip coin."));
	}
	return bSuccess;
}

// ═══════════════════════════════════════════════════════════════════════
// UIsekaiTitleMenuWidget
// ═══════════════════════════════════════════════════════════════════════

void UIsekaiTitleMenuWidget::InitializeTitleMenu(UTitleManagerComponent* InManager)
{
	TitleManager = InManager;
}

bool UIsekaiTitleMenuWidget::EquipTitle(FName TitleID)
{
	if (!TitleManager) return false;

	const bool bSuccess = TitleManager->EquipTitle(TitleID);
	if (bSuccess)
	{
		OnTitleEquipped(TitleID);
	}
	return bSuccess;
}

FName UIsekaiTitleMenuWidget::GetEquippedTitleID() const
{
	return (TitleManager && TitleManager->EquippedTitle) ? TitleManager->EquippedTitle->TitleID : NAME_None;
}

TArray<FName> UIsekaiTitleMenuWidget::GetUnlockedTitles() const
{
	TArray<FName> Result;
	if (TitleManager)
	{
		for (const FTitleProgressState& State : TitleManager->UnlockedTitles)
		{
			if (State.TitleAsset)
			{
				Result.Add(State.TitleAsset->TitleID);
			}
		}
	}
	return Result;
}

// ═══════════════════════════════════════════════════════════════════════
// UIsekaiCampCookingWidget
// ═══════════════════════════════════════════════════════════════════════

void UIsekaiCampCookingWidget::InitializeCampCooking(UAdventurerManagerComponent* InManager)
{
	AdventurerManager = InManager;
}

bool UIsekaiCampCookingWidget::CookCampMeal(const FAdventurerNutrition& MealNutrition)
{
	if (!AdventurerManager) return false;

	AdventurerManager->ApplyCampMealToParty(MealNutrition);
	OnMealPrepared();
	return true;
}

int32 UIsekaiCampCookingWidget::GetPartnerBondLevel(FName AdvA, FName AdvB) const
{
	return AdventurerManager ? AdventurerManager->GetAdventurerBondLevel(AdvA, AdvB) : 1;
}
