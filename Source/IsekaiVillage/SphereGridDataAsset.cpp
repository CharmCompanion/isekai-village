// Copyright Epic Games, Inc. All Rights Reserved.

#include "SphereGridDataAsset.h"

namespace
{
	FSphereNode MakeStatNode(FName NodeID, const FText& DisplayName, const FText& Description)
	{
		FSphereNode Node;
		Node.NodeID = NodeID;
		Node.DisplayName = DisplayName;
		Node.Description = Description;
		Node.NodeType = ESphereNodeType::Stat;
		return Node;
	}

	FSphereNode MakeSkillNode(FName NodeID, const FText& DisplayName, FName UnlockAction)
	{
		FSphereNode Node;
		Node.NodeID = NodeID;
		Node.DisplayName = DisplayName;
		Node.Description = FText::FromName(UnlockAction);
		Node.NodeType = ESphereNodeType::Skill;
		Node.UnlockAction = UnlockAction;
		return Node;
	}

	void LinkRing(TMap<FName, FSphereNode>& InNodes, const TArray<FName>& Order)
	{
		const int32 Count = Order.Num();
		for (int32 Index = 0; Index < Count; ++Index)
		{
			FSphereNode* Node = InNodes.Find(Order[Index]);
			if (!Node)
			{
				continue;
			}
			Node->ConnectedNodes.Reset();
			Node->ConnectedNodes.Add(Order[(Index + Count - 1) % Count]);
			Node->ConnectedNodes.Add(Order[(Index + 1) % Count]);
		}
	}
}

USphereGridDataAsset::USphereGridDataAsset()
{
	DiscName = NSLOCTEXT("IsekaiVillage", "CenterALife", "CENTER A — Life");

	auto AddHP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "HP10", "+10 HP"));
		Node.HP_Bonus = 10;
		Nodes.Add(ID, Node);
	};
	auto AddTP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "TP10", "+10 TP"));
		Node.TP_Bonus = 10;
		Nodes.Add(ID, Node);
	};
	auto AddInv = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Inv5", "+5 Inventory"));
		Node.Inventory_Bonus = 5;
		Nodes.Add(ID, Node);
	};
	auto AddCarry = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Carry8", "+8 kg Carry"));
		Node.CarryWeight_Bonus = 8;
		Nodes.Add(ID, Node);
	};
	auto AddMove = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Move3", "+3% Move Speed"));
		Node.MoveSpeed_Percent = 3.0f;
		Nodes.Add(ID, Node);
	};

	AddHP(TEXT("CA_Life_HP1"), TEXT("Life HP I"));
	AddHP(TEXT("CA_Life_HP2"), TEXT("Life HP II"));
	AddHP(TEXT("CA_Life_HP3"), TEXT("Life HP III"));
	AddHP(TEXT("CA_Life_HP4"), TEXT("Life HP IV"));
	AddTP(TEXT("CA_Life_TP1"), TEXT("Life TP I"));
	AddTP(TEXT("CA_Life_TP2"), TEXT("Life TP II"));
	AddTP(TEXT("CA_Life_TP3"), TEXT("Life TP III"));
	AddInv(TEXT("CA_Life_Inv1"), TEXT("Life Pack I"));
	AddInv(TEXT("CA_Life_Inv2"), TEXT("Life Pack II"));
	AddInv(TEXT("CA_Life_Inv3"), TEXT("Life Pack III"));
	AddCarry(TEXT("CA_Life_Carry1"), TEXT("Life Carry I"));
	AddCarry(TEXT("CA_Life_Carry2"), TEXT("Life Carry II"));
	AddMove(TEXT("CA_Life_Move1"), TEXT("Life Stride I"));
	AddMove(TEXT("CA_Life_Move2"), TEXT("Life Stride II"));

	if (FSphereNode* Start = Nodes.Find(StartNodeID))
	{
		Start->bIsCenterNode = true;
	}

	LifeNodeOrder = {
		TEXT("CA_Life_HP1"), TEXT("CA_Life_HP2"), TEXT("CA_Life_HP3"), TEXT("CA_Life_HP4"),
		TEXT("CA_Life_TP1"), TEXT("CA_Life_TP2"), TEXT("CA_Life_TP3"),
		TEXT("CA_Life_Inv1"), TEXT("CA_Life_Inv2"), TEXT("CA_Life_Inv3"),
		TEXT("CA_Life_Carry1"), TEXT("CA_Life_Carry2"),
		TEXT("CA_Life_Move1"), TEXT("CA_Life_Move2")
	};
	LinkRing(Nodes, LifeNodeOrder);

	auto AddFlipSkill = [this](FName ID, const FText& Label, FName Action)
	{
		FlipFaceNodes.Add(ID, MakeSkillNode(ID, Label, Action));
	};
	auto AddFlipHP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "HP10", "+10 HP"));
		Node.HP_Bonus = 10;
		FlipFaceNodes.Add(ID, Node);
	};
	auto AddFlipTP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "TP10", "+10 TP"));
		Node.TP_Bonus = 10;
		FlipFaceNodes.Add(ID, Node);
	};
	auto AddFlipCarry = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Carry8", "+8 kg Carry"));
		Node.CarryWeight_Bonus = 8;
		FlipFaceNodes.Add(ID, Node);
	};
	auto AddFlipMove = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Move3", "+3% Move Speed"));
		Node.MoveSpeed_Percent = 3.0f;
		FlipFaceNodes.Add(ID, Node);
	};

	AddFlipSkill(TEXT("CA_Adv_Dash"), NSLOCTEXT("IsekaiVillage", "Dash", "Dash"), TEXT("Dash"));
	AddFlipSkill(TEXT("CA_Adv_Hunt"), NSLOCTEXT("IsekaiVillage", "Hunt", "Hunt"), TEXT("Hunt"));
	AddFlipSkill(TEXT("CA_Adv_DangerSense"), NSLOCTEXT("IsekaiVillage", "DangerSense", "Danger Sense"), TEXT("DangerSense"));
	AddFlipSkill(TEXT("CA_Adv_Trailblaze"), NSLOCTEXT("IsekaiVillage", "Trailblaze", "Trailblaze"), TEXT("Trailblaze"));
	AddFlipHP(TEXT("CA_Adv_HP1"), TEXT("Field HP I"));
	AddFlipHP(TEXT("CA_Adv_HP2"), TEXT("Field HP II"));
	AddFlipHP(TEXT("CA_Adv_HP3"), TEXT("Field HP III"));
	AddFlipTP(TEXT("CA_Adv_TP1"), TEXT("Field TP I"));
	AddFlipTP(TEXT("CA_Adv_TP2"), TEXT("Field TP II"));
	AddFlipCarry(TEXT("CA_Adv_Carry1"), TEXT("Field Pack I"));
	AddFlipCarry(TEXT("CA_Adv_Carry2"), TEXT("Field Pack II"));
	AddFlipMove(TEXT("CA_Adv_Move1"), TEXT("Field Stride I"));
	AddFlipMove(TEXT("CA_Adv_Move2"), TEXT("Field Stride II"));

	FSphereNode Trust = MakeStatNode(TEXT("CA_Adv_Trust1"), FText::FromString(TEXT("Town Trust")), NSLOCTEXT("IsekaiVillage", "Trust5", "+5 Trust"));
	Trust.Trust_Bonus = 5;
	FlipFaceNodes.Add(TEXT("CA_Adv_Trust1"), Trust);

	if (FSphereNode* FlipStart = FlipFaceNodes.Find(FlipStartNodeID))
	{
		FlipStart->bIsCenterNode = true;
	}

	FlipNodeOrder = {
		TEXT("CA_Adv_Dash"), TEXT("CA_Adv_Hunt"), TEXT("CA_Adv_DangerSense"), TEXT("CA_Adv_Trailblaze"),
		TEXT("CA_Adv_HP1"), TEXT("CA_Adv_HP2"), TEXT("CA_Adv_HP3"),
		TEXT("CA_Adv_TP1"), TEXT("CA_Adv_TP2"),
		TEXT("CA_Adv_Carry1"), TEXT("CA_Adv_Carry2"),
		TEXT("CA_Adv_Move1"), TEXT("CA_Adv_Move2"),
		TEXT("CA_Adv_Trust1")
	};
	LinkRing(FlipFaceNodes, FlipNodeOrder);
}

bool USphereGridDataAsset::GetNode(FName NodeID, FSphereNode& OutNode) const
{
	if (const FSphereNode* Found = Nodes.Find(NodeID))
	{
		OutNode = *Found;
		return true;
	}
	if (const FSphereNode* Found = FlipFaceNodes.Find(NodeID))
	{
		OutNode = *Found;
		return true;
	}
	return false;
}

FSphereGridStatTotals USphereGridDataAsset::SumBonuses(const TArray<FName>& UnlockedNodeIDs) const
{
	FSphereGridStatTotals Totals;
	for (const FName& NodeID : UnlockedNodeIDs)
	{
		const FSphereNode* Node = Nodes.Find(NodeID);
		if (!Node)
		{
			Node = FlipFaceNodes.Find(NodeID);
		}
		if (!Node)
		{
			continue;
		}
		Totals.HP += Node->HP_Bonus;
		Totals.TP += Node->TP_Bonus;
		Totals.Inventory += Node->Inventory_Bonus;
		Totals.CarryWeight += Node->CarryWeight_Bonus;
		Totals.MoveSpeedPercent += Node->MoveSpeed_Percent;
		Totals.BuildSpeedPercent += Node->BuildSpeed_Percent;
		Totals.Trust += Node->Trust_Bonus;
		Totals.GaldPercent += Node->Gald_Percent;
	}
	return Totals;
}

bool USphereGridDataAsset::IsLifeFaceComplete(const TArray<FName>& UnlockedNodeIDs) const
{
	if (Nodes.Num() == 0)
	{
		return false;
	}
	for (const TPair<FName, FSphereNode>& Pair : Nodes)
	{
		if (!UnlockedNodeIDs.Contains(Pair.Key))
		{
			return false;
		}
	}
	return true;
}

bool USphereGridDataAsset::IsFlipFaceComplete(const TArray<FName>& UnlockedNodeIDs) const
{
	if (FlipFaceNodes.Num() == 0)
	{
		return false;
	}
	for (const TPair<FName, FSphereNode>& Pair : FlipFaceNodes)
	{
		if (!UnlockedNodeIDs.Contains(Pair.Key))
		{
			return false;
		}
	}
	return true;
}

bool USphereGridDataAsset::HasUnlockedNodeOnFace(const TArray<FName>& UnlockedNodeIDs, bool bFlipped) const
{
	const TMap<FName, FSphereNode>& Face = bFlipped ? FlipFaceNodes : Nodes;
	for (const FName& NodeID : UnlockedNodeIDs)
	{
		if (Face.Contains(NodeID))
		{
			return true;
		}
	}
	return false;
}

bool USphereGridDataAsset::IsNodeAdjacentToUnlocked(FName NodeID, const TArray<FName>& UnlockedNodeIDs, bool bFlipped) const
{
	const TMap<FName, FSphereNode>& Face = bFlipped ? FlipFaceNodes : Nodes;
	const FName FaceStart = bFlipped ? FlipStartNodeID : StartNodeID;

	if (!Face.Contains(NodeID) || UnlockedNodeIDs.Contains(NodeID))
	{
		return false;
	}

	if (!HasUnlockedNodeOnFace(UnlockedNodeIDs, bFlipped))
	{
		return NodeID == FaceStart;
	}

	const FSphereNode* Candidate = Face.Find(NodeID);
	if (!Candidate)
	{
		return false;
	}

	for (const FName& UnlockedID : UnlockedNodeIDs)
	{
		const FSphereNode* Unlocked = Face.Find(UnlockedID);
		if (!Unlocked)
		{
			continue;
		}
		if (Unlocked->ConnectedNodes.Contains(NodeID) || Candidate->ConnectedNodes.Contains(UnlockedID))
		{
			return true;
		}
	}
	return false;
}
