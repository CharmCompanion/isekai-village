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

	auto AddWorkYield = [this](FName ID, const TCHAR* Label)
	{
		WorkFaceNodes.Add(ID, MakeSkillNode(ID, FText::FromString(Label), TEXT("Yield+1")));
	};
	auto AddWorkCarry = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Carry8", "+8 kg Carry"));
		Node.CarryWeight_Bonus = 8;
		WorkFaceNodes.Add(ID, Node);
	};
	auto AddWorkInv = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Inv5", "+5 Inventory"));
		Node.Inventory_Bonus = 5;
		WorkFaceNodes.Add(ID, Node);
	};
	auto AddWorkBuild = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Build10", "+10% Build"));
		Node.BuildSpeed_Percent = 10.0f;
		WorkFaceNodes.Add(ID, Node);
	};
	auto AddWorkHP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "HP10", "+10 HP"));
		Node.HP_Bonus = 10;
		WorkFaceNodes.Add(ID, Node);
	};
	AddWorkYield(TEXT("CB_Work_Yield1"), TEXT("Yield I"));
	AddWorkYield(TEXT("CB_Work_Yield2"), TEXT("Yield II"));
	AddWorkYield(TEXT("CB_Work_Yield3"), TEXT("Yield III"));
	AddWorkCarry(TEXT("CB_Work_Carry1"), TEXT("Work Carry I"));
	AddWorkCarry(TEXT("CB_Work_Carry2"), TEXT("Work Carry II"));
	AddWorkCarry(TEXT("CB_Work_Carry3"), TEXT("Work Carry III"));
	AddWorkInv(TEXT("CB_Work_Inv1"), TEXT("Work Pack I"));
	AddWorkInv(TEXT("CB_Work_Inv2"), TEXT("Work Pack II"));
	AddWorkInv(TEXT("CB_Work_Inv3"), TEXT("Work Pack III"));
	AddWorkBuild(TEXT("CB_Work_Build1"), TEXT("Build I"));
	AddWorkBuild(TEXT("CB_Work_Build2"), TEXT("Build II"));
	AddWorkBuild(TEXT("CB_Work_Build3"), TEXT("Build III"));
	AddWorkHP(TEXT("CB_Work_HP1"), TEXT("Work HP I"));
	AddWorkHP(TEXT("CB_Work_HP2"), TEXT("Work HP II"));
	if (FSphereNode* WorkStart = WorkFaceNodes.Find(WorkStartNodeID))
	{
		WorkStart->bIsCenterNode = true;
	}
	WorkNodeOrder = {
		TEXT("CB_Work_Yield1"), TEXT("CB_Work_Yield2"), TEXT("CB_Work_Yield3"),
		TEXT("CB_Work_Carry1"), TEXT("CB_Work_Carry2"), TEXT("CB_Work_Carry3"),
		TEXT("CB_Work_Inv1"), TEXT("CB_Work_Inv2"), TEXT("CB_Work_Inv3"),
		TEXT("CB_Work_Build1"), TEXT("CB_Work_Build2"), TEXT("CB_Work_Build3"),
		TEXT("CB_Work_HP1"), TEXT("CB_Work_HP2")
	};
	LinkRing(WorkFaceNodes, WorkNodeOrder);

	auto AddVilSkill = [this](FName ID, const TCHAR* Label, FName Action)
	{
		VillagerFaceNodes.Add(ID, MakeSkillNode(ID, FText::FromString(Label), Action));
	};
	auto AddVilHP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "HP10", "+10 HP"));
		Node.HP_Bonus = 10;
		VillagerFaceNodes.Add(ID, Node);
	};
	auto AddVilTP = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "TP10", "+10 TP"));
		Node.TP_Bonus = 10;
		VillagerFaceNodes.Add(ID, Node);
	};
	auto AddVilCarry = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Carry8", "+8 kg Carry"));
		Node.CarryWeight_Bonus = 8;
		VillagerFaceNodes.Add(ID, Node);
	};
	auto AddVilMove = [this](FName ID, const TCHAR* Label)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), NSLOCTEXT("IsekaiVillage", "Move3", "+3% Move Speed"));
		Node.MoveSpeed_Percent = 3.0f;
		VillagerFaceNodes.Add(ID, Node);
	};
	AddVilSkill(TEXT("CB_Vil_Jab"), TEXT("Jab"), TEXT("Jab"));
	AddVilSkill(TEXT("CB_Vil_DoubleKick"), TEXT("Double Kick"), TEXT("DoubleKick"));
	AddVilSkill(TEXT("CB_Vil_HawkSmash"), TEXT("Hawk Smash"), TEXT("HawkSmash"));
	AddVilHP(TEXT("CB_Vil_HP1"), TEXT("Regal HP I"));
	AddVilHP(TEXT("CB_Vil_HP2"), TEXT("Regal HP II"));
	AddVilHP(TEXT("CB_Vil_HP3"), TEXT("Regal HP III"));
	AddVilHP(TEXT("CB_Vil_HP4"), TEXT("Regal HP IV"));
	AddVilTP(TEXT("CB_Vil_TP1"), TEXT("Regal TP I"));
	AddVilTP(TEXT("CB_Vil_TP2"), TEXT("Regal TP II"));
	AddVilTP(TEXT("CB_Vil_TP3"), TEXT("Regal TP III"));
	AddVilCarry(TEXT("CB_Vil_Carry1"), TEXT("Regal Carry I"));
	AddVilCarry(TEXT("CB_Vil_Carry2"), TEXT("Regal Carry II"));
	AddVilMove(TEXT("CB_Vil_Move1"), TEXT("Regal Stride I"));
	AddVilMove(TEXT("CB_Vil_Move2"), TEXT("Regal Stride II"));
	if (FSphereNode* VilStart = VillagerFaceNodes.Find(VillagerStartNodeID))
	{
		VilStart->bIsCenterNode = true;
	}
	VillagerNodeOrder = {
		TEXT("CB_Vil_Jab"), TEXT("CB_Vil_DoubleKick"), TEXT("CB_Vil_HawkSmash"),
		TEXT("CB_Vil_HP1"), TEXT("CB_Vil_HP2"), TEXT("CB_Vil_HP3"), TEXT("CB_Vil_HP4"),
		TEXT("CB_Vil_TP1"), TEXT("CB_Vil_TP2"), TEXT("CB_Vil_TP3"),
		TEXT("CB_Vil_Carry1"), TEXT("CB_Vil_Carry2"),
		TEXT("CB_Vil_Move1"), TEXT("CB_Vil_Move2")
	};
	LinkRing(VillagerFaceNodes, VillagerNodeOrder);

	auto AddDisc = [this](FName DiscID, const TCHAR* Title, const TCHAR* Category, const TCHAR* UnlockHint) -> FSphereDiscDefinition&
	{
		FSphereDiscDefinition& D = ExtraDiscs.AddDefaulted_GetRef();
		D.DiscID = DiscID;
		D.Title = FText::FromString(Title);
		D.Category = FText::FromString(Category);
		D.UnlockHint = FText::FromString(UnlockHint);
		return D;
	};
	auto PushSkill = [](FSphereDiscDefinition& D, FName ID, const TCHAR* Label, FName Action, const TCHAR* Desc)
	{
		FSphereNode Node = MakeSkillNode(ID, FText::FromString(Label), Action);
		Node.Description = FText::FromString(Desc);
		if (D.StartNodeID.IsNone())
		{
			D.StartNodeID = ID;
			Node.bIsCenterNode = true;
		}
		D.Nodes.Add(ID, Node);
		D.NodeOrder.Add(ID);
	};
	auto PushStat = [](FSphereDiscDefinition& D, FName ID, const TCHAR* Label, const TCHAR* Desc, auto&& Configure)
	{
		FSphereNode Node = MakeStatNode(ID, FText::FromString(Label), FText::FromString(Desc));
		Configure(Node);
		D.Nodes.Add(ID, Node);
		D.NodeOrder.Add(ID);
	};

	// Disc 2: Crafting (10 nodes: 3 skill / 7 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Crafting"), TEXT("CRAFTING"), TEXT("Town Main"), TEXT("Complete CENTER B — Work to unlock"));
		PushSkill(D, TEXT("Crf_Salvage"), TEXT("Forge Salvage"), TEXT("ForgeDiscount"), TEXT("Forge costs -1 material (when >= 4)"));
		PushSkill(D, TEXT("Crf_Masterwork"), TEXT("Masterwork"), TEXT("FieldRepair"), TEXT("Forged gear +4 party ATK & +10 HP; Repair +15 Wall"));
		PushSkill(D, TEXT("Crf_Stockpile"), TEXT("Yield IV"), TEXT("Yield+1"), TEXT("+1 Wood/Ore gather yield"));
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Crf_Inv%d"), i), *FString::Printf(TEXT("Craft Pack %d"), i), TEXT("+5 Inventory"), [](FSphereNode& N) { N.Inventory_Bonus = 5; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Crf_Carry%d"), i), *FString::Printf(TEXT("Craft Carry %d"), i), TEXT("+8 kg Carry"), [](FSphereNode& N) { N.CarryWeight_Bonus = 8; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Crf_Build%d"), i), *FString::Printf(TEXT("Timberwright %d"), i), TEXT("+5% Build Wood Discount"), [](FSphereNode& N) { N.BuildSpeed_Percent = 5.0f; });
		PushStat(D, TEXT("Crf_HP1"), TEXT("Smith Vigor"), TEXT("+10 HP"), [](FSphereNode& N) { N.HP_Bonus = 10; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 3: Domain+Architect (14 nodes: 4 town perks / 10 town stat boosts)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("DomainArchitect"), TEXT("DOMAIN + ARCHITECT"), TEXT("Town Main"), TEXT("Complete CENTER B — Work to unlock"));
		PushSkill(D, TEXT("Dom_ExpandedLofts"), TEXT("Expanded Lofts"), TEXT("LoftBeds+2"), TEXT("House loft upgrades grant +2 beds instead of +1"));
		PushSkill(D, TEXT("Dom_CivicWatch"), TEXT("Civic Watch"), TEXT("CivicWatch"), TEXT("+3 Wall/day, extra -1 CrimeHeat/day, +10% Safety"));
		PushSkill(D, TEXT("Dom_HallCharter"), TEXT("Hall Charter"), TEXT("HallCharter"), TEXT("+1 courier cargo & +1 Farm/Bakery/Smith batch output"));
		PushSkill(D, TEXT("Dom_KingdomCharter"), TEXT("Kingdom Charter"), TEXT("HireCap+1"), TEXT("+1 Active Party Cap & Kingdom stewardship"));
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Dom_Build%d"), i), *FString::Printf(TEXT("Build Discount %d"), i), TEXT("+10% Build Wood Discount"), [](FSphereNode& N) { N.BuildSpeed_Percent = 10.0f; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Dom_Trust%d"), i), *FString::Printf(TEXT("Civic Trust %d"), i), TEXT("+5 Town Trust"), [](FSphereNode& N) { N.Trust_Bonus = 5; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Dom_Attract%d"), i), *FString::Printf(TEXT("Prosperity %d"), i), TEXT("+10% Town Attraction"), [](FSphereNode& N) { N.Attraction_Percent = 10.0f; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Dom_Worker%d"), i), *FString::Printf(TEXT("Worker Pace %d"), i), TEXT("+12% Golem Worker Speed & Rest"), [](FSphereNode& N) { N.WorkerPace_Percent = 12.0f; });
		PushStat(D, TEXT("Dom_Haul1"), TEXT("Supply Depot"), TEXT("+10 Inventory"), [](FSphereNode& N) { N.Inventory_Bonus = 10; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 4: Economy+Hospitality (14 nodes: 6 skill / 8 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("EconomyHospitality"), TEXT("ECONOMY + HOSP"), TEXT("Town Main"), TEXT("Complete CENTER B — Work to unlock"));
		PushSkill(D, TEXT("Eco_Haggle"), TEXT("Shop Haggle"), TEXT("ShopHaggle"), TEXT("Sell wood +1 Coin; buy wood 1 Coin"));
		PushSkill(D, TEXT("Eco_FestivalBoost"), TEXT("Festival Boost"), TEXT("FestivalProlong"), TEXT("Festivals trigger at Trust 15+ & give +1 Trust/day"));
		PushSkill(D, TEXT("Eco_BathhouseHeal"), TEXT("Bathhouse Tonic"), TEXT("BathhouseRegen"), TEXT("+2 HP/s in town w/ Bath; +50% golem rest rate"));
		PushSkill(D, TEXT("Eco_InnCare"), TEXT("Inn Hospitality"), TEXT("InnHospitality"), TEXT("+1 daily FoodStock w/ Inn & faster leisure recovery"));
		PushSkill(D, TEXT("Eco_BulkVault"), TEXT("Trade Vault"), TEXT("VaultStock"), TEXT("+2 daily hall supply site restock capacity"));
		PushSkill(D, TEXT("Eco_CivicMissions"), TEXT("Guild Bounty"), TEXT("MissionReward+1"), TEXT("+2 bonus Trust & +5 Coin per day slip"));
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Eco_Gald%d"), i), *FString::Printf(TEXT("Trade Margin %d"), i), TEXT("+10% Gald/Coin Trade"), [](FSphereNode& N) { N.Gald_Percent = 10; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Eco_Carry%d"), i), *FString::Printf(TEXT("Bulk Carry %d"), i), TEXT("+10 kg Carry"), [](FSphereNode& N) { N.CarryWeight_Bonus = 10; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Eco_Inv%d"), i), *FString::Printf(TEXT("Merchant Pack %d"), i), TEXT("+5 Inventory"), [](FSphereNode& N) { N.Inventory_Bonus = 5; });
		PushStat(D, TEXT("Eco_Trust1"), TEXT("Merchant Trust"), TEXT("+5 Town Trust"), [](FSphereNode& N) { N.Trust_Bonus = 5; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 5: Melee (12 nodes: 4 skill / 8 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Melee"), TEXT("MELEE"), TEXT("Combat Main"), TEXT("Complete CENTER B — Villager to unlock"));
		PushSkill(D, TEXT("Mel_SwordRain"), TEXT("Sword Rain"), TEXT("SwordRain"), TEXT("Melee (F) adds +2 rapid strikes & wider arc"));
		PushSkill(D, TEXT("Mel_SonicThrust"), TEXT("Sonic Thrust"), TEXT("SonicThrust"), TEXT("Melee (F) lunges forward (+12 dmg)"));
		PushSkill(D, TEXT("Mel_Beast"), TEXT("Beast Roar"), TEXT("BeastRoar"), TEXT("+20 melee dmg, heavy knockback, +6 party ATK"));
		PushSkill(D, TEXT("Mel_EnchantBlade"), TEXT("Elemental Blade"), TEXT("ElementalBlade"), TEXT("Infuses melee (F) with Active Element (+10 dmg)"));
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Mel_Atk%d"), i), *FString::Printf(TEXT("Vanguard Atk %d"), i), TEXT("+3 Attack"), [](FSphereNode& N) { N.Attack_Bonus = 3; });
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Mel_HP%d"), i), *FString::Printf(TEXT("Vanguard HP %d"), i), TEXT("+15 HP"), [](FSphereNode& N) { N.HP_Bonus = 15; });
		PushStat(D, TEXT("Mel_TP1"), TEXT("Vanguard TP"), TEXT("+10 TP"), [](FSphereNode& N) { N.TP_Bonus = 10; });
		PushStat(D, TEXT("Mel_Move1"), TEXT("Footwork"), TEXT("+4% Move Speed"), [](FSphereNode& N) { N.MoveSpeed_Percent = 4.0f; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 6: Magic (12 nodes: 4 skill / 8 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Magic"), TEXT("MAGIC"), TEXT("Combat Main"), TEXT("Complete CENTER B — Villager to unlock"));
		PushSkill(D, TEXT("Mag_CostCut"), TEXT("TP Conserve"), TEXT("TPConserve"), TEXT("-20% Arte TP cost, +2 TP/s regen, -15% party Bolt TP"));
		PushSkill(D, TEXT("Mag_SpreadFan"), TEXT("Spread Fan"), TEXT("SpreadFan"), TEXT("Artes fire a 3-way 14-deg projectile fan"));
		PushSkill(D, TEXT("Mag_DualFocus"), TEXT("Quick Cast"), TEXT("QuickCast"), TEXT("Focus Mode casts cost 0 TP & deal +35% dmg"));
		PushSkill(D, TEXT("Mag_ArcaneSurge"), TEXT("Arcane Surge"), TEXT("ArcaneSurge"), TEXT("+20% party Arcane Bolt damage"));
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Mag_Mag%d"), i), *FString::Printf(TEXT("Arcane Power %d"), i), TEXT("+4 Magic"), [](FSphereNode& N) { N.Magic_Bonus = 4; });
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Mag_TP%d"), i), *FString::Printf(TEXT("Mana Pool %d"), i), TEXT("+15 TP"), [](FSphereNode& N) { N.TP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Mag_HP%d"), i), *FString::Printf(TEXT("Mage Vigor %d"), i), TEXT("+10 HP"), [](FSphereNode& N) { N.HP_Bonus = 10; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 7: Cleric (10 nodes: 3 skill / 7 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Cleric"), TEXT("CLERIC"), TEXT("Combat Main"), TEXT("Complete CENTER B — Villager to unlock"));
		PushSkill(D, TEXT("Clr_SacredHeal"), TEXT("Sacred Heal"), TEXT("SacredHeal"), TEXT("Party First Aid heals +35% more HP"));
		PushSkill(D, TEXT("Clr_AegisBarrier"), TEXT("Aegis Barrier"), TEXT("AegisBarrier"), TEXT("+10% party & MC damage reduction"));
		PushSkill(D, TEXT("Clr_ReviveGrace"), TEXT("Revive Grace"), TEXT("ReviveGrace"), TEXT("First Aid revives knocked-out allies at 35% HP"));
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Clr_HP%d"), i), *FString::Printf(TEXT("Sanctuary HP %d"), i), TEXT("+15 HP"), [](FSphereNode& N) { N.HP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Clr_TP%d"), i), *FString::Printf(TEXT("Prayer TP %d"), i), TEXT("+15 TP"), [](FSphereNode& N) { N.TP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Clr_Res%d"), i), *FString::Printf(TEXT("Ward Res %d"), i), TEXT("+4% Damage Reduction"), [](FSphereNode& N) { N.Res_Percent = 4.0f; });
		PushStat(D, TEXT("Clr_Trust1"), TEXT("Chapel Grace"), TEXT("+5 Town Trust"), [](FSphereNode& N) { N.Trust_Bonus = 5; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 8: Ranger (10 nodes: 3 skill / 7 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Ranger"), TEXT("RANGER"), TEXT("Endgame"), TEXT("Complete MELEE disc to unlock"));
		PushSkill(D, TEXT("Rng_BowSpread"), TEXT("Bow Spread"), TEXT("BowSpread"), TEXT("+1 projectile pierce & Ranger crit 25%->45%"));
		PushSkill(D, TEXT("Rng_AmbushStrike"), TEXT("Ambush Strike"), TEXT("AmbushStrike"), TEXT("Slide/Focus attacks deal x1.5 damage"));
		PushSkill(D, TEXT("Rng_MasterHunter"), TEXT("Master Hunter"), TEXT("MasterHunter"), TEXT("+15% crit/weakness dmg & +1 guarded deposit yield"));
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Rng_Move%d"), i), *FString::Printf(TEXT("Wind Step %d"), i), TEXT("+4% Move Speed"), [](FSphereNode& N) { N.MoveSpeed_Percent = 4.0f; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Rng_Atk%d"), i), *FString::Printf(TEXT("Precision %d"), i), TEXT("+3 Attack"), [](FSphereNode& N) { N.Attack_Bonus = 3; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Rng_TP%d"), i), *FString::Printf(TEXT("Hunter TP %d"), i), TEXT("+10 TP"), [](FSphereNode& N) { N.TP_Bonus = 10; });
		PushStat(D, TEXT("Rng_Carry1"), TEXT("Quiver Pack"), TEXT("+8 kg Carry"), [](FSphereNode& N) { N.CarryWeight_Bonus = 8; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 9: Summons (14 nodes: 4 skill / 10 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Summons"), TEXT("SUMMONS"), TEXT("Endgame"), TEXT("Complete CLERIC disc to unlock"));
		PushSkill(D, TEXT("Sum_BondCap"), TEXT("Pact Charter"), TEXT("HireCap+1"), TEXT("+1 Active Party Cap"));
		PushSkill(D, TEXT("Sum_TamerTempo"), TEXT("Tamer Tempo"), TEXT("SummonHaste"), TEXT("Companions recover turns 15% faster"));
		PushSkill(D, TEXT("Sum_ElementLink"), TEXT("Element Link"), TEXT("ElementLink"), TEXT("Companion Bolts sync to MC Element (+20% dmg)"));
		PushSkill(D, TEXT("Sum_GuardPact"), TEXT("Spirit Pact"), TEXT("SpiritGuard"), TEXT("Companions start battle +15 Max HP & +10 TP"));
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Sum_HP%d"), i), *FString::Printf(TEXT("Bond HP %d"), i), TEXT("+15 HP"), [](FSphereNode& N) { N.HP_Bonus = 15; });
		for (int32 i = 1; i <= 3; ++i)
			PushStat(D, *FString::Printf(TEXT("Sum_TP%d"), i), *FString::Printf(TEXT("Bond TP %d"), i), TEXT("+15 TP"), [](FSphereNode& N) { N.TP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Sum_Trust%d"), i), *FString::Printf(TEXT("Familiar Bond %d"), i), TEXT("+5 Town Trust"), [](FSphereNode& N) { N.Trust_Bonus = 5; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Sum_Mag%d"), i), *FString::Printf(TEXT("Spirit Magic %d"), i), TEXT("+4 Magic"), [](FSphereNode& N) { N.Magic_Bonus = 4; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 10: Soulsmith (12 nodes: 4 skill / 8 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Soulsmith"), TEXT("SOULSMITH"), TEXT("Endgame"), TEXT("Complete DOMAIN+ARCHITECT or MAGIC to unlock"));
		PushSkill(D, TEXT("Sol_SoulImprint"), TEXT("Soul Imprint"), TEXT("SoulImprint"), TEXT("+50% golem skill/passive practice speed"));
		PushSkill(D, TEXT("Sol_VesselAnchor"), TEXT("Vessel Anchor"), TEXT("VesselAnchor"), TEXT("Survive first fatal blow at 1 HP once per fight"));
		PushSkill(D, TEXT("Sol_SoulResonance"), TEXT("Soul Resonance"), TEXT("SoulResonance"), TEXT("Party gains +8 ATK & +15% heal potency"));
		PushSkill(D, TEXT("Sol_EchoBreaker"), TEXT("Echo Breaker"), TEXT("EchoBreaker"), TEXT("+25% damage vs Tower Bosses & Guarded foes"));
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Sol_HP%d"), i), *FString::Printf(TEXT("Vessel HP %d"), i), TEXT("+15 HP"), [](FSphereNode& N) { N.HP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Sol_TP%d"), i), *FString::Printf(TEXT("Soul Core TP %d"), i), TEXT("+15 TP"), [](FSphereNode& N) { N.TP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Sol_Trust%d"), i), *FString::Printf(TEXT("Core Harmony %d"), i), TEXT("+5 Town Trust"), [](FSphereNode& N) { N.Trust_Bonus = 5; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Sol_Carry%d"), i), *FString::Printf(TEXT("Vessel Carry %d"), i), TEXT("+10 kg Carry"), [](FSphereNode& N) { N.CarryWeight_Bonus = 10; });
		LinkRing(D.Nodes, D.NodeOrder);
	}

	// Disc 11: Artificer (12 nodes: 4 skill / 8 stat)
	{
		FSphereDiscDefinition& D = AddDisc(TEXT("Artificer"), TEXT("ARTIFICER"), TEXT("Endgame"), TEXT("Complete CRAFTING or MAGIC to unlock"));
		PushSkill(D, TEXT("Art_RelicMastery"), TEXT("Relic Mastery"), TEXT("RelicEmpowered"), TEXT("+25% Relic Altar boon strength (+2 Crystals fallback)"));
		PushSkill(D, TEXT("Art_RunicTonic"), TEXT("Runic Tonic"), TEXT("RunicTonic"), TEXT("Rations (P) cure +50% fatigue & restore +25 HP / +15 TP"));
		PushSkill(D, TEXT("Art_SanctuaryCamp"), TEXT("Sanctuary Camp"), TEXT("SanctuaryCamp"), TEXT("-1 Camp build cost, +1 Trip Home & full rest restore"));
		PushSkill(D, TEXT("Art_CatalystExtract"), TEXT("Catalyst Extract"), TEXT("CatalystExtract"), TEXT("+1 Tower deposit yield & -1 Runic Forge Crystal"));
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Art_Inv%d"), i), *FString::Printf(TEXT("Artificer Satchel %d"), i), TEXT("+8 Inventory"), [](FSphereNode& N) { N.Inventory_Bonus = 8; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Art_TP%d"), i), *FString::Printf(TEXT("Alembic TP %d"), i), TEXT("+15 TP"), [](FSphereNode& N) { N.TP_Bonus = 15; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Art_Res%d"), i), *FString::Printf(TEXT("Runic Ward %d"), i), TEXT("+5% Damage Reduction"), [](FSphereNode& N) { N.Res_Percent = 5.0f; });
		for (int32 i = 1; i <= 2; ++i)
			PushStat(D, *FString::Printf(TEXT("Art_Build%d"), i), *FString::Printf(TEXT("Artifice Discount %d"), i), TEXT("+5% Build Wood Discount"), [](FSphereNode& N) { N.BuildSpeed_Percent = 5.0f; });
		LinkRing(D.Nodes, D.NodeOrder);
	}
}

bool USphereGridDataAsset::GetNode(FName NodeID, FSphereNode& OutNode) const
{
	for (const TMap<FName, FSphereNode>* Face : { &Nodes, &FlipFaceNodes, &WorkFaceNodes, &VillagerFaceNodes })
	{
		if (const FSphereNode* Found = Face->Find(NodeID))
		{
			OutNode = *Found;
			return true;
		}
	}
	for (const FSphereDiscDefinition& Extra : ExtraDiscs)
	{
		if (const FSphereNode* Found = Extra.Nodes.Find(NodeID))
		{
			OutNode = *Found;
			return true;
		}
	}
	return false;
}

FSphereGridStatTotals USphereGridDataAsset::SumBonuses(const TArray<FName>& UnlockedNodeIDs) const
{
	FSphereGridStatTotals Totals;
	FSphereNode Node;
	for (const FName& NodeID : UnlockedNodeIDs)
	{
		if (!GetNode(NodeID, Node))
		{
			continue;
		}
		Totals.HP += Node.HP_Bonus;
		Totals.TP += Node.TP_Bonus;
		Totals.Inventory += Node.Inventory_Bonus;
		Totals.CarryWeight += Node.CarryWeight_Bonus;
		Totals.MoveSpeedPercent += Node.MoveSpeed_Percent;
		Totals.BuildSpeedPercent += Node.BuildSpeed_Percent;
		Totals.Trust += Node.Trust_Bonus;
		Totals.GaldPercent += Node.Gald_Percent;
		Totals.Attack += Node.Attack_Bonus;
		Totals.Magic += Node.Magic_Bonus;
		Totals.ResPercent += Node.Res_Percent;
		Totals.AttractionPercent += Node.Attraction_Percent;
		Totals.WorkerPacePercent += Node.WorkerPace_Percent;
	}
	return Totals;
}

FText USphereGridDataAsset::DiscDisplayTitle(int32 Disc, bool bFlipped) const
{
	if (Disc == 0)
	{
		return bFlipped
			? NSLOCTEXT("IsekaiVillage", "AdvFace", "CENTER A — Adventurer")
			: NSLOCTEXT("IsekaiVillage", "LifeFace", "CENTER A — Life");
	}
	if (Disc == 1)
	{
		return bFlipped
			? NSLOCTEXT("IsekaiVillage", "VilFace", "CENTER B — Villager")
			: NSLOCTEXT("IsekaiVillage", "WorkFace", "CENTER B — Work");
	}
	const int32 ExtraIndex = Disc - 2;
	return ExtraDiscs.IsValidIndex(ExtraIndex) ? ExtraDiscs[ExtraIndex].Title : FText::GetEmpty();
}

FText USphereGridDataAsset::DiscCategoryLabel(int32 Disc) const
{
	if (Disc <= 1)
	{
		return NSLOCTEXT("IsekaiVillage", "StarterDisc", "Starter");
	}
	const int32 ExtraIndex = Disc - 2;
	return ExtraDiscs.IsValidIndex(ExtraIndex) ? ExtraDiscs[ExtraIndex].Category : FText::GetEmpty();
}

FText USphereGridDataAsset::DiscUnlockHint(int32 Disc) const
{
	if (Disc == 0)
	{
		return NSLOCTEXT("IsekaiVillage", "StartUnlocked", "Unlocked at start");
	}
	if (Disc == 1)
	{
		return NSLOCTEXT("IsekaiVillage", "CenterBHint", "Complete CENTER A — Adventurer to unlock");
	}
	const int32 ExtraIndex = Disc - 2;
	return ExtraDiscs.IsValidIndex(ExtraIndex) ? ExtraDiscs[ExtraIndex].UnlockHint : FText::GetEmpty();
}

bool USphereGridDataAsset::IsDiscUnlocked(int32 Disc, const TArray<FName>& UnlockedNodeIDs) const
{
	if (Disc == 0)
	{
		return true;
	}
	if (Disc == 1)
	{
		return IsFaceComplete(0, true, UnlockedNodeIDs);
	}
	if (Disc >= 2 && Disc <= 4) // Town Main 3
	{
		return IsFaceComplete(1, false, UnlockedNodeIDs);
	}
	if (Disc >= 5 && Disc <= 7) // Combat Main 3
	{
		return IsFaceComplete(1, true, UnlockedNodeIDs);
	}
	if (Disc == 8) // Ranger <- Melee
	{
		return IsFaceComplete(5, false, UnlockedNodeIDs);
	}
	if (Disc == 9) // Summons <- Cleric
	{
		return IsFaceComplete(7, false, UnlockedNodeIDs);
	}
	if (Disc == 10) // Soulsmith <- Domain+Architect OR Magic
	{
		return IsFaceComplete(3, false, UnlockedNodeIDs) || IsFaceComplete(6, false, UnlockedNodeIDs);
	}
	if (Disc == 11) // Artificer <- Crafting OR Magic
	{
		return IsFaceComplete(2, false, UnlockedNodeIDs) || IsFaceComplete(6, false, UnlockedNodeIDs);
	}
	return false;
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

const TMap<FName, FSphereNode>& USphereGridDataAsset::FaceMap(int32 Disc, bool bFlipped) const
{
	if (Disc >= 2)
	{
		const int32 ExtraIndex = Disc - 2;
		static const TMap<FName, FSphereNode> EmptyMap;
		return ExtraDiscs.IsValidIndex(ExtraIndex) ? ExtraDiscs[ExtraIndex].Nodes : EmptyMap;
	}
	if (Disc == 1)
	{
		return bFlipped ? VillagerFaceNodes : WorkFaceNodes;
	}
	return bFlipped ? FlipFaceNodes : Nodes;
}

const TArray<FName>& USphereGridDataAsset::FaceOrder(int32 Disc, bool bFlipped) const
{
	if (Disc >= 2)
	{
		const int32 ExtraIndex = Disc - 2;
		static const TArray<FName> EmptyOrder;
		return ExtraDiscs.IsValidIndex(ExtraIndex) ? ExtraDiscs[ExtraIndex].NodeOrder : EmptyOrder;
	}
	if (Disc == 1)
	{
		return bFlipped ? VillagerNodeOrder : WorkNodeOrder;
	}
	return bFlipped ? FlipNodeOrder : LifeNodeOrder;
}

FName USphereGridDataAsset::FaceStart(int32 Disc, bool bFlipped) const
{
	if (Disc >= 2)
	{
		const int32 ExtraIndex = Disc - 2;
		return ExtraDiscs.IsValidIndex(ExtraIndex) ? ExtraDiscs[ExtraIndex].StartNodeID : NAME_None;
	}
	if (Disc == 1)
	{
		return bFlipped ? VillagerStartNodeID : WorkStartNodeID;
	}
	return bFlipped ? FlipStartNodeID : StartNodeID;
}

bool USphereGridDataAsset::IsFaceComplete(int32 Disc, bool bFlipped, const TArray<FName>& UnlockedNodeIDs) const
{
	const TMap<FName, FSphereNode>& Face = FaceMap(Disc, bFlipped);
	if (Face.Num() == 0)
	{
		return false;
	}
	for (const TPair<FName, FSphereNode>& Pair : Face)
	{
		if (!UnlockedNodeIDs.Contains(Pair.Key))
		{
			return false;
		}
	}
	return true;
}

bool USphereGridDataAsset::HasUnlockedOnDisc(int32 Disc, bool bFlipped, const TArray<FName>& UnlockedNodeIDs) const
{
	const TMap<FName, FSphereNode>& Face = FaceMap(Disc, bFlipped);
	for (const FName& NodeID : UnlockedNodeIDs)
	{
		if (Face.Contains(NodeID))
		{
			return true;
		}
	}
	return false;
}

bool USphereGridDataAsset::IsNodeAdjacentOnDisc(FName NodeID, const TArray<FName>& UnlockedNodeIDs, int32 Disc, bool bFlipped) const
{
	if (!IsDiscUnlocked(Disc, UnlockedNodeIDs))
	{
		return false;
	}
	const TMap<FName, FSphereNode>& Face = FaceMap(Disc, bFlipped);
	const FName Start = FaceStart(Disc, bFlipped);
	if (!Face.Contains(NodeID) || UnlockedNodeIDs.Contains(NodeID))
	{
		return false;
	}
	if (!HasUnlockedOnDisc(Disc, bFlipped, UnlockedNodeIDs))
	{
		return NodeID == Start;
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
