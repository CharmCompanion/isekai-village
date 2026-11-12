// Copyright Epic Games, Inc. All Rights Reserved.
// SkillGridComponent.cpp — Implementation of character Skill Grid and Arte unlocking

#include "SkillGridComponent.h"

USkillGridComponent::USkillGridComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void USkillGridComponent::BeginPlay()
{
	Super::BeginPlay();
}

void USkillGridComponent::AddSP(int32 Amount)
{
	if (Amount <= 0) return;

	AvailableSP += Amount;
	OnSPChanged.Broadcast(AvailableSP);
}

bool USkillGridComponent::CanUnlockNode(FName NodeID) const
{
	if (!ActiveGrid || UnlockedNodeIDs.Contains(NodeID))
	{
		return false;
	}

	const FSkillGridNode* TargetNode = nullptr;
	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (Node.NodeID == NodeID)
		{
			TargetNode = &Node;
			break;
		}
	}

	if (!TargetNode)
	{
		return false;
	}

	if (AvailableSP < TargetNode->SPCost)
	{
		return false;
	}

	// If no prerequisites, this is a starter/root node
	if (TargetNode->RequiredPrerequisites.Num() == 0)
	{
		return true;
	}

	// At least one prerequisite must be unlocked
	for (const FName& PrereqID : TargetNode->RequiredPrerequisites)
	{
		if (UnlockedNodeIDs.Contains(PrereqID))
		{
			return true;
		}
	}

	return false;
}

bool USkillGridComponent::UnlockNode(FName NodeID)
{
	if (!CanUnlockNode(NodeID))
	{
		return false;
	}

	const FSkillGridNode* TargetNode = nullptr;
	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (Node.NodeID == NodeID)
		{
			TargetNode = &Node;
			break;
		}
	}

	if (!TargetNode) return false;

	AvailableSP -= TargetNode->SPCost;
	UnlockedNodeIDs.Add(NodeID);

	OnSPChanged.Broadcast(AvailableSP);
	OnSkillNodeUnlocked.Broadcast(*TargetNode);

	if (IsGridCompleted())
	{
		OnSkillGridCompleted.Broadcast(ActiveGrid);
	}

	return true;
}

bool USkillGridComponent::IsNodeUnlocked(FName NodeID) const
{
	return UnlockedNodeIDs.Contains(NodeID);
}

bool USkillGridComponent::IsGridCompleted() const
{
	if (!ActiveGrid || ActiveGrid->Nodes.Num() == 0)
	{
		return false;
	}

	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (!UnlockedNodeIDs.Contains(Node.NodeID))
		{
			return false;
		}
	}

	return true;
}

bool USkillGridComponent::UnlockDisc(FName DiscID)
{
	if (DiscID == NAME_None || UnlockedDiscIDs.Contains(DiscID))
	{
		return false;
	}

	UnlockedDiscIDs.Add(DiscID);
	OnDiscUnlocked.Broadcast(DiscID);
	return true;
}

bool USkillGridComponent::IsDiscUnlocked(FName DiscID) const
{
	return UnlockedDiscIDs.Contains(DiscID);
}

bool USkillGridComponent::IsDiscCompleted(FName DiscID) const
{
	if (!ActiveGrid) return false;

	const FSphereDiscData* Disc = ActiveGrid->FindDisc(DiscID);
	if (!Disc || Disc->Nodes.Num() == 0) return false;

	for (const FSkillGridNode& Node : Disc->Nodes)
	{
		if (!UnlockedNodeIDs.Contains(Node.NodeID))
		{
			return false;
		}
	}
	return true;
}

bool USkillGridComponent::FlipCoinDisc(FName FrontDiscID, FName& OutBackDiscID)
{
	OutBackDiscID = NAME_None;
	if (!ActiveGrid) return false;

	const FSphereDiscData* FrontDisc = ActiveGrid->FindDisc(FrontDiscID);
	if (!FrontDisc || !FrontDisc->bIsCoinFlipDisc || FrontDisc->FlipSideDiscID == NAME_None)
	{
		return false;
	}

	// Must complete all front disc nodes before flipping
	if (!IsDiscCompleted(FrontDiscID))
	{
		return false;
	}

	OutBackDiscID = FrontDisc->FlipSideDiscID;
	FlippedCoinDiscs.Add(FrontDiscID);
	UnlockedDiscIDs.Add(OutBackDiscID);

	OnCoinDiscFlip.Broadcast(FrontDiscID, OutBackDiscID);
	return true;
}

bool USkillGridComponent::CanUnlockNodeOnDisc(FName DiscID, FName NodeID) const
{
	if (!ActiveGrid || UnlockedNodeIDs.Contains(NodeID)) return false;

	const FSphereDiscData* Disc = ActiveGrid->FindDisc(DiscID);
	if (!Disc) return false;

	// Disc itself must be unlocked
	if (!UnlockedDiscIDs.Contains(DiscID)) return false;

	const FSkillGridNode* TargetNode = nullptr;
	for (const FSkillGridNode& Node : Disc->Nodes)
	{
		if (Node.NodeID == NodeID)
		{
			TargetNode = &Node;
			break;
		}
	}

	if (!TargetNode || AvailableSP < TargetNode->SPCost) return false;

	if (TargetNode->RequiredPrerequisites.Num() == 0) return true;

	for (const FName& PrereqID : TargetNode->RequiredPrerequisites)
	{
		if (UnlockedNodeIDs.Contains(PrereqID)) return true;
	}

	return false;
}

bool USkillGridComponent::UnlockNodeOnDisc(FName DiscID, FName NodeID)
{
	if (!CanUnlockNodeOnDisc(DiscID, NodeID)) return false;

	const FSphereDiscData* Disc = ActiveGrid->FindDisc(DiscID);
	if (!Disc) return false;

	const FSkillGridNode* TargetNode = nullptr;
	for (const FSkillGridNode& Node : Disc->Nodes)
	{
		if (Node.NodeID == NodeID)
		{
			TargetNode = &Node;
			break;
		}
	}

	if (!TargetNode) return false;

	AvailableSP -= TargetNode->SPCost;
	UnlockedNodeIDs.Add(NodeID);

	OnSPChanged.Broadcast(AvailableSP);
	OnSkillNodeUnlocked.Broadcast(*TargetNode);

	if (IsDiscCompleted(DiscID))
	{
		// Check if coin flip disc is now ready
		if (Disc->bIsCoinFlipDisc)
		{
			FName BackDisc;
			FlipCoinDisc(DiscID, BackDisc);
		}
	}

	return true;
}

float USkillGridComponent::GetTotalSkillStatBonus(ETitleStatType StatType) const
{
	if (!ActiveGrid) return 0.0f;

	float Total = 0.0f;
	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (UnlockedNodeIDs.Contains(Node.NodeID) && Node.NodeType == ESkillNodeType::StatBoost && Node.StatType == StatType)
		{
			Total += Node.StatBonusValue;
		}
	}

	for (const FSphereDiscData& Disc : ActiveGrid->Discs)
	{
		for (const FSkillGridNode& Node : Disc.Nodes)
		{
			if (UnlockedNodeIDs.Contains(Node.NodeID) && Node.NodeType == ESkillNodeType::StatBoost && Node.StatType == StatType)
			{
				Total += Node.StatBonusValue;
			}
		}
	}

	return Total;
}

int32 USkillGridComponent::GetTotalBonusHP() const
{
	if (!ActiveGrid) return 0;
	int32 Bonus = 0;

	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.HP_Bonus;
	}
	for (const FSphereDiscData& Disc : ActiveGrid->Discs)
	{
		for (const FSkillGridNode& Node : Disc.Nodes)
		{
			if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.HP_Bonus;
		}
	}
	return Bonus;
}

int32 USkillGridComponent::GetTotalBonusTP() const
{
	if (!ActiveGrid) return 0;
	int32 Bonus = 0;

	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.TP_Bonus;
	}
	for (const FSphereDiscData& Disc : ActiveGrid->Discs)
	{
		for (const FSkillGridNode& Node : Disc.Nodes)
		{
			if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.TP_Bonus;
		}
	}
	return Bonus;
}

int32 USkillGridComponent::GetTotalBonusInventory() const
{
	if (!ActiveGrid) return 0;
	int32 Bonus = 0;

	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.Inventory_Bonus;
	}
	for (const FSphereDiscData& Disc : ActiveGrid->Discs)
	{
		for (const FSkillGridNode& Node : Disc.Nodes)
		{
			if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.Inventory_Bonus;
		}
	}
	return Bonus;
}

int32 USkillGridComponent::GetTotalBonusCarryWeight() const
{
	if (!ActiveGrid) return 0;
	int32 Bonus = 0;

	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.CarryWeight_Bonus;
	}
	for (const FSphereDiscData& Disc : ActiveGrid->Discs)
	{
		for (const FSkillGridNode& Node : Disc.Nodes)
		{
			if (UnlockedNodeIDs.Contains(Node.NodeID)) Bonus += Node.CarryWeight_Bonus;
		}
	}
	return Bonus;
}

bool USkillGridComponent::HasUnlockedPerkOrArte(FName Identifier) const
{
	if (Identifier == NAME_None || !ActiveGrid) return false;

	for (const FSkillGridNode& Node : ActiveGrid->Nodes)
	{
		if (UnlockedNodeIDs.Contains(Node.NodeID) && (Node.UnlockedArteOrPerkID == Identifier || Node.UnlockAction == Identifier))
		{
			return true;
		}
	}

	for (const FSphereDiscData& Disc : ActiveGrid->Discs)
	{
		for (const FSkillGridNode& Node : Disc.Nodes)
		{
			if (UnlockedNodeIDs.Contains(Node.NodeID) && (Node.UnlockedArteOrPerkID == Identifier || Node.UnlockAction == Identifier))
			{
				return true;
			}
		}
	}

	// Also check completion bonus
	if (IsGridCompleted() && ActiveGrid->CompletionBonusPerkID == Identifier)
	{
		return true;
	}

	return false;
}

void USkillGridComponent::SetActiveGrid(USkillGridDataAsset* NewGrid)
{
	ActiveGrid = NewGrid;
}
