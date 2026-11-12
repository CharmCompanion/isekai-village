// Copyright Epic Games, Inc. All Rights Reserved.

#include "VillageRuntime.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "VillageCitizen.h"
#include "Engine/Engine.h"

namespace
{
void ToastService(const FString& Msg, FColor Color = FColor::Cyan)
{
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 3.0f, Color, Msg);
	}
}
}

bool AVillageRuntime::IsServiceBuilding(ETownBuilding Kind)
{
	switch (Kind)
	{
	case ETownBuilding::Inn:
	case ETownBuilding::Chapel:
	case ETownBuilding::Training:
	case ETownBuilding::Bank:
	case ETownBuilding::Bath:
	case ETownBuilding::Bell:
	case ETownBuilding::Academy:
	case ETownBuilding::Manor:
	case ETownBuilding::Castle:
		return true;
	default:
		return false;
	}
}

float AVillageRuntime::EffectiveBuildDiscount(const AIsekaiVillageCharacter* Player) const
{
	const float Base = Player ? Player->SphereBuildSpeed : 0.0f;
	const float EdictBonus = (ActiveRoyalEdict == TEXT("BuildDrive")) ? 15.0f : 0.0f;
	return FMath::Clamp(Base + EdictBonus, 0.0f, 50.0f);
}

int32 AVillageRuntime::GetGuildStandingScore() const
{
	int32 Score = FMath::Min(24, Trust / 4);
	Score += FMath::Clamp(AcademyResearchLevel, 0, 3) * 8;
	Score += FMath::Clamp(TowerFloor.HighestFloor, 0, 100);

	TSet<ETownBuilding> DistinctKinds;
	for (const FTownPlot& Plot : Plots)
	{
		if (!Plot.bBuilt) continue;
		if (Plot.Kind == ETownBuilding::House)
		{
			Score += Plot.bUpgraded ? 6 : 4;
		}
		else if (!DistinctKinds.Contains(Plot.Kind))
		{
			DistinctKinds.Add(Plot.Kind);
			Score += Plot.bScenery ? 4 : 9;
		}
		else
		{
			Score += Plot.bScenery ? 2 : 4;
		}
	}
	return Score;
}

int32 AVillageRuntime::ComputeGuildRank() const
{
	const int32 Score = GetGuildStandingScore();
	if (Score >= 120 && HasBuilding(ETownBuilding::Castle)) return 4; // S
	if (Score >= 85) return 3;  // A
	if (Score >= 55) return 2;  // B
	if (Score >= 30) return 1;  // C
	return 0;                   // D
}

FString AVillageRuntime::GetGuildRankName() const
{
	static const TCHAR* Names[] = { TEXT("D"), TEXT("C"), TEXT("B"), TEXT("A"), TEXT("S") };
	return Names[FMath::Clamp(TownGuildRank, 0, 4)];
}

int32 AVillageRuntime::EvaluateGuildRank(AIsekaiVillageCharacter* Player)
{
	const int32 Target = ComputeGuildRank();
	if (Target > TownGuildRank)
	{
		const int32 Gain = Target - TownGuildRank;
		TownGuildRank = Target;
		Trust = FMath::Min(99, Trust + Gain * 4);
		if (Player)
		{
			Player->SpherePoints += Gain;
		}
		LastServiceMessage = FString::Printf(
			TEXT("Guild Rank Promoted to Rank %s! (+%d SP, Trips Home: %d)"),
			*GetGuildRankName(), Gain, UTowerAdaptationLibrary::TripsHomeForRank(TownGuildRank));
		ToastService(LastServiceMessage, FColor::Yellow);
	}
	return TownGuildRank;
}

FName AVillageRuntime::NearestServicePlot(const FVector& Position) const
{
	FName Best = NAME_None;
	double BestDist = FMath::Square(450.0);
	for (const FTownPlot& Plot : Plots)
	{
		if (!Plot.bBuilt || !IsServiceBuilding(Plot.Kind)) continue;
		const double D = FVector::DistSquared2D(Position, Plot.Location + Plot.StakeOffset);
		if (D <= BestDist)
		{
			Best = Plot.Id;
			BestDist = D;
		}
	}
	return Best;
}

FString AVillageRuntime::BuildingQuickHint(ETownBuilding Kind) const
{
	switch (Kind)
	{
	case ETownBuilding::Inn: return TEXT("T Rest & Advance Day  |  U Open Inn Services");
	case ETownBuilding::Chapel: return TEXT("T Daily Blessing & Cleanse  |  U Open Chapel Services");
	case ETownBuilding::Training: return TEXT("T Group Drill (+25 Practice)  |  U Open Knight School");
	case ETownBuilding::Bank: return TEXT("T Deposit/Withdraw Coin  |  U Open Royal Bank");
	case ETownBuilding::Bath: return TEXT("T Hot Spring Soak  |  U Open Bathhouse");
	case ETownBuilding::Bell: return TEXT("T Ring Civic Bell (Guild Inspect)  |  U Town Ledger");
	case ETownBuilding::Academy: return TEXT("T Advance Arcane Research  |  U Open Magic Academy");
	case ETownBuilding::Manor: return TEXT("T Switch Royal Edict  |  U Open Noble Manor");
	case ETownBuilding::Castle: return TEXT("T Royal Audience & Grant  |  U Open Castle Keep");
	default: return FString();
	}
}

void AVillageRuntime::RollOverNewDay(AIsekaiVillageCharacter* Player)
{
	bBathhouseSoakedToday = false;

	if (HasBuilding(ETownBuilding::Bank))
	{
		const bool bCharter = (ActiveRoyalEdict == TEXT("TradeCharter"));
		const int32 MaxInterest = bCharter ? 50 : 40;
		const int32 Interest = FMath::Min(MaxInterest, FMath::RoundToInt(BankVaultCoins * (bCharter ? 0.125f : 0.10f)));
		const int32 BaseTax = bKingdom ? 20 : (bLargeTown ? 12 : 8);
		const int32 Tax = bCharter ? FMath::RoundToInt(BaseTax * 1.25f) : BaseTax;
		BankVaultCoins += Interest + Tax;
	}

	if (HasBuilding(ETownBuilding::Chapel))
	{
		for (AVillageCitizen* C : Living())
		{
			if (C)
			{
				C->Mind.bSick = false;
				C->Mind.Wound = 0;
			}
		}
	}

	if (HasBuilding(ETownBuilding::Inn))
	{
		for (FVillageGolemRecord& R : GolemResidents)
		{
			R.Drives.Fatigue = FMath::Max(0.0f, R.Drives.Fatigue - 20.0f);
			R.Drives.Loneliness = FMath::Max(0.0f, R.Drives.Loneliness - 10.0f);
		}
	}

	const bool bHasTrain = HasBuilding(ETownBuilding::Training);
	const bool bHasAcademy = HasBuilding(ETownBuilding::Academy);
	if ((bHasTrain || bHasAcademy) && Player && Player->PartyReserve)
	{
		const int32 BaseReps = (bHasTrain ? 1 : 0) + (bHasAcademy ? 2 : 0);
		const int32 Reps = (ActiveRoyalEdict == TEXT("GuildCampaign")) ? FMath::CeilToInt(BaseReps * 1.5f) : BaseReps;
		TSet<FName> HousedAdv;
		for (const FVillageGolemRecord& R : GolemResidents)
		{
			if (!R.AdventurerId.IsNone() && !R.HomePlot.IsNone()) HousedAdv.Add(R.AdventurerId);
		}
		for (const FHiredAdventurer& A : Player->PartyReserve->Reserve)
		{
			if (!HousedAdv.Contains(A.AdventurerID)) continue;
			const FName Domain = A.Drives.Interest.IsNone() ? FName(TEXT("Guard")) : A.Drives.Interest;
			for (int32 R = 0; R < Reps; ++R)
			{
				Player->PartyReserve->RecordAdventurerPractice(A.AdventurerID, Domain, 5.0f, true);
			}
		}
	}

	EvaluateGuildRank(Player);
}

bool AVillageRuntime::UseBuildingService(FName PlotId, AIsekaiVillageCharacter* Player)
{
	const FTownPlot* Plot = FindPlot(PlotId);
	if (!Plot || !Plot->bBuilt || !IsServiceBuilding(Plot->Kind)) return false;

	FName PrimaryAction = NAME_None;
	switch (Plot->Kind)
	{
	case ETownBuilding::Inn: PrimaryAction = TEXT("Rest"); break;
	case ETownBuilding::Chapel: PrimaryAction = TEXT("Pray"); break;
	case ETownBuilding::Training: PrimaryAction = TEXT("GroupDrill"); break;
	case ETownBuilding::Bank: PrimaryAction = (Player && Player->Gather && Player->Gather->GetCount(TEXT("Coin")) >= 10) ? FName(TEXT("Deposit10")) : FName(TEXT("Withdraw10")); break;
	case ETownBuilding::Bath: PrimaryAction = TEXT("Soak"); break;
	case ETownBuilding::Bell: PrimaryAction = TEXT("Ring"); break;
	case ETownBuilding::Academy: PrimaryAction = TEXT("ResearchNext"); break;
	case ETownBuilding::Manor: PrimaryAction = TEXT("CycleEdict"); break;
	case ETownBuilding::Castle: PrimaryAction = TEXT("RoyalAudience"); break;
	default: break;
	}
	return ExecuteServiceAction(Plot->Kind, PrimaryAction, Player);
}

bool AVillageRuntime::ExecuteServiceAction(ETownBuilding Kind, FName ActionId, AIsekaiVillageCharacter* Player)
{
	if (!Player || !HasBuilding(Kind))
	{
		LastServiceMessage = TEXT("Stand near a built service building to use this facility.");
		return false;
	}
	UGatherInventoryComponent* Gather = Player->Gather;
	auto Fail = [&](const FString& Why)
	{
		LastServiceMessage = Why;
		ToastService(Why, FColor::Orange);
		return false;
	};
	auto Succeed = [&](const FString& What)
	{
		LastServiceMessage = What;
		ToastService(What, FColor::Cyan);
		if (bUseGolemVillage && !ConstructionSaveSlot.IsEmpty()) SaveVillageState(Player);
		return true;
	};

	switch (Kind)
	{
	case ETownBuilding::Inn:
	{
		if (ActionId == TEXT("Rest"))
		{
			Player->RestoreHP(Player->MaxHP);
			Player->RestoreTP(Player->MaxTP);
			for (FVillageGolemRecord& R : GolemResidents) R.Drives.Fatigue = 0.0f;
			if (Player->PartyReserve)
			{
				for (FHiredAdventurer& A : Player->PartyReserve->Reserve) A.Drives.Fatigue = 0.0f;
			}
			const bool bInnPerk = Player->HasSphereSkill(TEXT("InnHospitality"));
			if (bInnPerk || (Gather && Gather->Consume(TEXT("Bread"), 1)))
			{
				Trust = FMath::Min(99, Trust + 2);
			}
			WindowIndex = 7;
			TickWindow(); // Advances DayIndex, weather, shop restock, bank interest & RollOverNewDay
			return Succeed(FString::Printf(TEXT("Rested at the Inn. Welcome to Day %d! HP/TP & fatigue restored."), DayIndex));
		}
		if (ActionId == TEXT("Feast"))
		{
			if (!Gather || Gather->GetCount(TEXT("Bread")) < 2) return Fail(TEXT("Hosting an Inn feast requires 2 Bread."));
			Gather->Consume(TEXT("Bread"), 2);
			Trust = FMath::Min(99, Trust + 4);
			Player->RestoreHP(Player->MaxHP);
			Player->RestoreTP(Player->MaxTP);
			for (FVillageGolemRecord& R : GolemResidents)
			{
				R.Drives.Fatigue = 0.0f;
				R.Drives.Loneliness = 0.0f;
			}
			EvaluateGuildRank(Player);
			return Succeed(FString::Printf(TEXT("Hosted an Inn feast! +4 Trust (Trust %d) and boosted village morale."), Trust));
		}
		break;
	}
	case ETownBuilding::Chapel:
	{
		FName Chosen = ActionId;
		if (ActionId == TEXT("Pray"))
		{
			Chosen = (ActiveChapelBlessing == TEXT("Valor")) ? FName(TEXT("Bulwark"))
				: (ActiveChapelBlessing == TEXT("Bulwark")) ? FName(TEXT("Grace")) : FName(TEXT("Valor"));
		}
		else if (ActionId == TEXT("BlessValor")) Chosen = TEXT("Valor");
		else if (ActionId == TEXT("BlessBulwark")) Chosen = TEXT("Bulwark");
		else if (ActionId == TEXT("BlessGrace")) Chosen = TEXT("Grace");

		const int32 Cost = Player->HasSphereSkill(TEXT("SpiritGrace")) ? 4 : 8;
		if (!Gather || Gather->GetCount(TEXT("Coin")) < Cost) return Fail(FString::Printf(TEXT("Chapel blessing requires %d Coin."), Cost));
		Gather->Consume(TEXT("Coin"), Cost);
		ActiveChapelBlessing = Chosen;
		Player->RestoreHP(Player->MaxHP);
		for (AVillageCitizen* C : Living())
		{
			if (C) { C->Mind.bSick = false; C->Mind.Wound = 0; }
		}
		return Succeed(FString::Printf(TEXT("Chapel Blessing [%s] bestowed (-%d Coin). Sickness cleansed & HP restored."), *Chosen.ToString(), Cost));
	}
	case ETownBuilding::Training:
	{
		if (ActionId == TEXT("StartSparring"))
		{
			Player->ToggleSparring();
			LastServiceMessage = TEXT("Toggled party training sparring.");
			return true;
		}
		if (ActionId == TEXT("GroupDrill"))
		{
			if (!Player->PartyReserve) return Fail(TEXT("Build the Adventure Hall and recruit golems first."));
			const bool bPaidCoin = Gather && Gather->Consume(TEXT("Coin"), 5);
			const bool bPaidBread = !bPaidCoin && Gather && Gather->Consume(TEXT("Bread"), 1);
			if (!bPaidCoin && !bPaidBread) return Fail(TEXT("Group Drill needs 5 Coin or 1 Bread."));
			int32 Trained = 0;
			const int32 Drills = (ActiveRoyalEdict == TEXT("GuildCampaign")) ? 6 : 4;
			for (const FHiredAdventurer& A : Player->PartyReserve->Reserve)
			{
				const FName Domain = A.Drives.Interest.IsNone() ? FName(TEXT("Guard")) : A.Drives.Interest;
				bool bAny = false;
				for (int32 R = 0; R < Drills; ++R)
				{
					bAny |= Player->PartyReserve->RecordAdventurerPractice(A.AdventurerID, Domain, 5.0f, true);
				}
				if (bAny) ++Trained;
			}
			Trust = FMath::Min(99, Trust + 1);
			EvaluateGuildRank(Player);
			return Succeed(FString::Printf(TEXT("Knight School drill complete! Trained %d adventurer(s) (+%d Practice XP)."), Trained, Drills * 5));
		}
		break;
	}
	case ETownBuilding::Bank:
	{
		if (!Gather) return false;
		if (ActionId == TEXT("Deposit10"))
		{
			const int32 Amt = FMath::Min(10, Gather->GetCount(TEXT("Coin")));
			if (Amt <= 0) return Fail(TEXT("You have no Coin to deposit."));
			Gather->Consume(TEXT("Coin"), Amt);
			BankVaultCoins += Amt;
			return Succeed(FString::Printf(TEXT("Deposited %d Coin. Bank Vault: %d Coin."), Amt, BankVaultCoins));
		}
		if (ActionId == TEXT("Withdraw10"))
		{
			const int32 Amt = FMath::Min(10, BankVaultCoins);
			if (Amt <= 0) return Fail(TEXT("The Bank Vault is empty."));
			BankVaultCoins -= Amt;
			Gather->AddItem(TEXT("Coin"), Amt);
			return Succeed(FString::Printf(TEXT("Withdrew %d Coin. Bank Vault: %d Coin."), Amt, BankVaultCoins));
		}
		if (ActionId == TEXT("WithdrawAll"))
		{
			if (BankVaultCoins <= 0) return Fail(TEXT("The Bank Vault is empty."));
			const int32 Amt = BankVaultCoins;
			BankVaultCoins = 0;
			Gather->AddItem(TEXT("Coin"), Amt);
			return Succeed(FString::Printf(TEXT("Withdrew all %d Coin from Bank Vault."), Amt));
		}
		break;
	}
	case ETownBuilding::Bath:
	{
		if (bBathhouseSoakedToday) return Fail(TEXT("Already soaked in the Bathhouse today."));
		bBathhouseSoakedToday = true;
		Player->RestoreHP(Player->MaxHP);
		Player->RestoreTP(Player->MaxTP);
		if (Player->PartyReserve)
		{
			for (FHiredAdventurer& A : Player->PartyReserve->Reserve)
			{
				A.Drives.Fatigue = FMath::Max(0.0f, A.Drives.Fatigue - 50.0f);
			}
		}
		return Succeed(TEXT("Bathhouse soak refreshed the party! Fatigue reduced & +15 Max HP buffer granted today."));
	}
	case ETownBuilding::Bell:
	{
		if (BellRungDay == DayIndex) return Fail(TEXT("Town Bell was already rung today."));
		BellRungDay = DayIndex;
		const int32 TrustBoost = Player->HasSphereSkill(TEXT("FestivalProlong")) ? 2 : 1;
		Trust = FMath::Min(99, Trust + TrustBoost);
		for (FVillageGolemRecord& R : GolemResidents)
		{
			if (R.Drives.Fatigue < 70.0f) R.Drives.Activity = TEXT("Work");
		}
		EvaluateGuildRank(Player);
		return Succeed(FString::Printf(TEXT("Town Bell rung! Guild Rank %s (Score %d) | Floor %d/100 | +%d Trust."),
			*GetGuildRankName(), GetGuildStandingScore(), TowerFloor.HighestFloor, TrustBoost));
	}
	case ETownBuilding::Academy:
	{
		if (AcademyResearchLevel >= 3) return Fail(TEXT("All 3 Academy Arcane Research tiers are complete (Wizardbane Seal active!)."));
		const int32 Next = AcademyResearchLevel + 1;
		const int32 CoinCost = Next == 1 ? 10 : Next == 2 ? 20 : 35;
		const FName Mat = (Next == 1) ? FName(TEXT("Iron")) : FName(TEXT("Crystal"));
		const int32 MatCost = Next == 1 ? 2 : Next == 2 ? 3 : 6;
		if (!Gather || Gather->GetCount(TEXT("Coin")) < CoinCost || Gather->GetCount(Mat) < MatCost)
		{
			return Fail(FString::Printf(TEXT("Research Tier %d needs %d Coin and %d %s."), Next, CoinCost, MatCost, *Mat.ToString()));
		}
		Gather->Consume(TEXT("Coin"), CoinCost);
		Gather->Consume(Mat, MatCost);
		AcademyResearchLevel = Next;
		Trust = FMath::Min(99, Trust + 3);
		EvaluateGuildRank(Player);
		const TCHAR* TierTitle = (Next == 1) ? TEXT("Arcane Treatise (-15% TP cost & +15 MaxTP)")
			: (Next == 2) ? TEXT("Elemental Matrix (+15% Spell & Magic Damage)")
			: TEXT("Wizardbane Seal (+20 HP, +12% DR, +10% ATK for Floor 100)");
		return Succeed(FString::Printf(TEXT("Academy Research Tier %d complete: %s!"), Next, TierTitle));
	}
	case ETownBuilding::Manor:
	{
		if (ActionId == TEXT("CollectStipend"))
		{
			if (StipendCollectedDay == DayIndex) return Fail(TEXT("Today's Guild stipend was already collected."));
			if (!Gather) return false;
			StipendCollectedDay = DayIndex;
			const int32 Stipend = (TownGuildRank + 1) * 6;
			Gather->AddItem(TEXT("Coin"), Stipend);
			return Succeed(FString::Printf(TEXT("Collected Rank %s Manor stipend: +%d Coin."), *GetGuildRankName(), Stipend));
		}
		if (ActionId == TEXT("CycleEdict"))
		{
			ActiveRoyalEdict = (ActiveRoyalEdict == TEXT("TradeCharter")) ? FName(TEXT("BuildDrive"))
				: (ActiveRoyalEdict == TEXT("BuildDrive")) ? FName(TEXT("GuildCampaign")) : FName(TEXT("TradeCharter"));
		}
		else if (ActionId == TEXT("EdictTrade") || ActionId == TEXT("EdictBuild") || ActionId == TEXT("EdictGuild"))
		{
			ActiveRoyalEdict = (ActionId == TEXT("EdictTrade")) ? FName(TEXT("TradeCharter"))
				: (ActionId == TEXT("EdictBuild")) ? FName(TEXT("BuildDrive")) : FName(TEXT("GuildCampaign"));
		}
		else return false;
		return Succeed(FString::Printf(TEXT("Enacted Manor Edict: [%s]."), *ActiveRoyalEdict.ToString()));
	}
	case ETownBuilding::Castle:
	{
		EvaluateGuildRank(Player);
		if (RoyalGrantDay != DayIndex && Gather)
		{
			RoyalGrantDay = DayIndex;
			const int32 Grant = (TownGuildRank + 2) * 8;
			Gather->AddItem(TEXT("Coin"), Grant);
			return Succeed(FString::Printf(TEXT("Royal Audience! Guild Rank %s | Collected %d Coin Royal Grant | Banner +10%% ATK/DEF!"),
				*GetGuildRankName(), Grant));
		}
		return Succeed(FString::Printf(TEXT("Castle Keep Report: Guild Rank %s (%d pts) | Deepest Floor %d/100 | Academy Tier %d/3."),
			*GetGuildRankName(), GetGuildStandingScore(), TowerFloor.HighestFloor, AcademyResearchLevel));
	}
	default:
		break;
	}
	return false;
}

int32 AVillageRuntime::DevelopedPlotCount() const
{
	int32 Count = 0;
	for (const FTownPlot& Plot : Plots)
	{
		if (Plot.bBuilt && !Plot.bScenery)
		{
			++Count;
		}
	}
	return Count;
}

ESettlementEra AVillageRuntime::GetSettlementEra(const AIsekaiVillageCharacter* Player) const
{
	const AIsekaiVillageCharacter* P = Player ? Player : ActiveTownPlayer();
	const int32 Nodes = P ? P->UnlockedSphereNodes.Num() : 0;
	const int32 EffTrust = Trust + (P ? P->SphereTrustBonus : 0);
	const int32 Dev = DevelopedPlotCount();
	const int32 Beds = BedCapacity();

	if (EffTrust >= 80 && Nodes >= 8 && (HasBuilding(ETownBuilding::Castle) || Dev >= 6 || bKingdom))
	{
		return ESettlementEra::Kingdom;
	}
	if (EffTrust >= 50 && Nodes >= 4 && (HasBuilding(ETownBuilding::Manor) || HasBuilding(ETownBuilding::Academy) || Dev >= 4 || bLargeTown))
	{
		return ESettlementEra::Barony;
	}
	if (EffTrust >= 30 && Nodes >= 2 && (Dev >= 3 || Beds >= 6))
	{
		return ESettlementEra::Town;
	}
	if (EffTrust >= 12 && (Dev >= 1 || Beds >= 2))
	{
		return ESettlementEra::Village;
	}
	return ESettlementEra::Homestead;
}

FString AVillageRuntime::GetSettlementEraName(const AIsekaiVillageCharacter* Player) const
{
	switch (GetSettlementEra(Player))
	{
	case ESettlementEra::Homestead: return TEXT("Homestead");
	case ESettlementEra::Village: return TEXT("Village");
	case ESettlementEra::Town: return TEXT("Town");
	case ESettlementEra::Barony: return TEXT("Barony");
	case ESettlementEra::Kingdom: return TEXT("Kingdom");
	default: return TEXT("Homestead");
	}
}

FString AVillageRuntime::GetNextEraRequirementText(const AIsekaiVillageCharacter* Player) const
{
	const AIsekaiVillageCharacter* P = Player ? Player : ActiveTownPlayer();
	const int32 Nodes = P ? P->UnlockedSphereNodes.Num() : 0;
	const int32 EffTrust = Trust + (P ? P->SphereTrustBonus : 0);
	const int32 Dev = DevelopedPlotCount();
	const int32 Beds = BedCapacity();

	switch (GetSettlementEra(P))
	{
	case ESettlementEra::Homestead:
		return FString::Printf(TEXT("Next [Village]: Trust %d/12 | Built %d/1 | Beds %d/2"), EffTrust, Dev, Beds);
	case ESettlementEra::Village:
		return FString::Printf(TEXT("Next [Town]: Trust %d/30 | Nodes %d/2 | Built %d/3"), EffTrust, Nodes, Dev);
	case ESettlementEra::Town:
		return FString::Printf(TEXT("Next [Barony]: Trust %d/50 | Nodes %d/4 | Built %d/4"), EffTrust, Nodes, Dev);
	case ESettlementEra::Barony:
		return FString::Printf(TEXT("Next [Kingdom]: Trust %d/80 | Nodes %d/8 | Castle/Built %d/6"), EffTrust, Nodes, Dev);
	case ESettlementEra::Kingdom:
		return TEXT("Kingdom Era Reached — Max Settlement Tier!");
	default:
		return FString();
	}
}

bool AVillageRuntime::TryCompleteMissionAtIndex(int32 MissionIndex, AIsekaiVillageCharacter* Player)
{
	if (!Player || !Player->Gather || !TodayMissions.IsValidIndex(MissionIndex))
	{
		return false;
	}
	FDayMission& Mission = TodayMissions[MissionIndex];
	if (Mission.bClaimed)
	{
		LastServiceMessage = TEXT("Commission already completed today.");
		return false;
	}
	if (Mission.Kind == EDayMissionKind::CookMeals && Mission.Have < Mission.Need)
	{
		if (FoodStock <= 0)
		{
			LastServiceMessage = TEXT("No town food stock available to cook meals.");
			return false;
		}
		--FoodStock;
		++Mission.Have;
		if (Mission.IsReady())
		{
			RewardMission(Player, Mission);
			EvaluateGuildRank(Player);
			SaveVillageState(Player);
			LastServiceMessage = FString::Printf(TEXT("Completed %s (+1 SP, Trust %d)!"), *Mission.Title().ToString(), Trust);
		}
		else
		{
			LastServiceMessage = FString::Printf(TEXT("Cooked meal (%d/%d)."), Mission.Have, Mission.Need);
		}
		return true;
	}
	if (Mission.Kind == EDayMissionKind::FetchWood)
	{
		if (Player->Gather->GetCount(TEXT("Wood")) < Mission.Need)
		{
			LastServiceMessage = FString::Printf(TEXT("Need %d Wood to deliver."), Mission.Need);
			return false;
		}
		Player->Gather->Consume(TEXT("Wood"), Mission.Need);
		Mission.Have = Mission.Need;
		RewardMission(Player, Mission);
		EvaluateGuildRank(Player);
		SaveVillageState(Player);
		LastServiceMessage = FString::Printf(TEXT("Delivered Wood commission (+1 SP, Trust %d)!"), Trust);
		return true;
	}
	if (Mission.Kind == EDayMissionKind::RepairWall)
	{
		if (Player->Gather->GetCount(TEXT("Wood")) < 3)
		{
			LastServiceMessage = TEXT("Need 3 Wood to repair the town wall.");
			return false;
		}
		Player->Gather->Consume(TEXT("Wood"), 3);
		WallIntegrity = FMath::Min(100, WallIntegrity + 30);
		Mission.Have = Mission.Need;
		RewardMission(Player, Mission);
		EvaluateGuildRank(Player);
		SaveVillageState(Player);
		LastServiceMessage = FString::Printf(TEXT("Wall repaired to %d/100 (+1 SP, Trust %d)!"), WallIntegrity, Trust);
		return true;
	}
	if (Mission.Kind == EDayMissionKind::StockStall)
	{
		Mission.Have = FMath::Min(Mission.Need, WoodSoldToday);
		if (!Mission.IsReady())
		{
			LastServiceMessage = FString::Printf(TEXT("Sell %d more Wood at a Shop (%d/%d)."), Mission.Need - Mission.Have, Mission.Have, Mission.Need);
			return false;
		}
		RewardMission(Player, Mission);
		EvaluateGuildRank(Player);
		SaveVillageState(Player);
		LastServiceMessage = FString::Printf(TEXT("Claimed Stock Stall commission (+1 SP, Trust %d)!"), Trust);
		return true;
	}
	return false;
}
