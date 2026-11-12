// Copyright Epic Games, Inc. All Rights Reserved.
#include "GatherInventoryComponent.h"
#include "IsekaiVillageCharacter.h"
#include "Engine/Engine.h"

UGatherInventoryComponent::UGatherInventoryComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

void UGatherInventoryComponent::AddItem(FName ItemId, int32 Count)
{
	if (ItemId.IsNone() || Count <= 0)
	{
		return;
	}
	for (FGatherStack& Stack : Stacks)
	{
		if (Stack.ItemId == ItemId)
		{
			Stack.Count += Count;
			return;
		}
	}
	FGatherStack Stack;
	Stack.ItemId = ItemId;
	Stack.Count = Count;
	Stacks.Add(Stack);
}

int32 UGatherInventoryComponent::GetCount(FName ItemId) const
{
	for (const FGatherStack& Stack : Stacks)
	{
		if (Stack.ItemId == ItemId)
		{
			return Stack.Count;
		}
	}
	return 0;
}

bool UGatherInventoryComponent::Consume(FName ItemId, int32 Count)
{
	if (Count <= 0) return false;
	if (GetCount(ItemId) < Count)
	{
		return false;
	}
	for (FGatherStack& Stack : Stacks)
	{
		if (Stack.ItemId == ItemId)
		{
			Stack.Count -= Count;
			return true;
		}
	}
	return false;
}

static int32 HitsForTier(EAxeTier Tier)
{
	switch (Tier)
	{
	case EAxeTier::Fists: return 8;
	case EAxeTier::Stone: return 4;
	case EAxeTier::Iron: return 2;
	case EAxeTier::Steel: return 1;
	default: return 4;
	}
}

static int32 YieldForTier(EAxeTier Tier)
{
	switch (Tier)
	{
	case EAxeTier::Fists: return 1;
	case EAxeTier::Stone: return 2;
	case EAxeTier::Iron: return 3;
	case EAxeTier::Steel: return 5;
	default: return 2;
	}
}

static FString ToolLabel(EAxeTier Tier, const TCHAR* Kind)
{
	switch (Tier)
	{
	case EAxeTier::Fists: return FString::Printf(TEXT("Fists"));
	case EAxeTier::Stone: return FString::Printf(TEXT("Stone %s"), Kind);
	case EAxeTier::Iron: return FString::Printf(TEXT("Iron %s"), Kind);
	case EAxeTier::Steel: return FString::Printf(TEXT("Steel %s"), Kind);
	default: return Kind;
	}
}

int32 UGatherInventoryComponent::ForgeCost(const AIsekaiVillageCharacter* Character, int32 Base, bool bCrystal)
{
	if (bCrystal)
	{
		return (Character && Character->HasSphereSkill(TEXT("CatalystExtract"))) ? FMath::Max(1, Base - 1) : Base;
	}
	return (Character && Character->HasSphereSkill(TEXT("ForgeDiscount")) && Base >= 4) ? Base - 1 : Base;
}

bool UGatherInventoryComponent::TryUpgradeAxe()
{
	const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner());
	auto Cost = [Character](int32 Base, bool bCrystal = false) { return ForgeCost(Character, Base, bCrystal); };
	if (AxeTier == EAxeTier::Stone && GetCount(TEXT("Iron")) >= Cost(6) && GetCount(TEXT("Wood")) >= Cost(4))
	{
		Consume(TEXT("Iron"), Cost(6));
		Consume(TEXT("Wood"), Cost(4));
		AxeTier = EAxeTier::Iron;
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Silver, TEXT("Blacksmith forged an Iron Axe"));
		return true;
	}
	if (AxeTier == EAxeTier::Iron && GetCount(TEXT("Crystal")) >= Cost(4, true) && GetCount(TEXT("Iron")) >= Cost(8))
	{
		Consume(TEXT("Crystal"), Cost(4, true));
		Consume(TEXT("Iron"), Cost(8));
		AxeTier = EAxeTier::Steel;
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Cyan, TEXT("Blacksmith forged a Steel Axe"));
		return true;
	}
	return false;
}

bool UGatherInventoryComponent::TryUpgradePickaxe()
{
	const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner());
	auto Cost = [Character](int32 Base, bool bCrystal = false) { return ForgeCost(Character, Base, bCrystal); };
	if (PickaxeTier == EAxeTier::Stone && GetCount(TEXT("Iron")) >= Cost(8) && GetCount(TEXT("Wood")) >= Cost(2))
	{
		Consume(TEXT("Iron"), Cost(8));
		Consume(TEXT("Wood"), Cost(2));
		PickaxeTier = EAxeTier::Iron;
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Silver, TEXT("Blacksmith forged an Iron Pickaxe"));
		return true;
	}
	if (PickaxeTier == EAxeTier::Iron && GetCount(TEXT("Crystal")) >= Cost(6, true) && GetCount(TEXT("Iron")) >= Cost(6))
	{
		Consume(TEXT("Crystal"), Cost(6, true));
		Consume(TEXT("Iron"), Cost(6));
		PickaxeTier = EAxeTier::Steel;
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Cyan, TEXT("Blacksmith forged a Steel Pickaxe"));
		return true;
	}
	return false;
}

bool UGatherInventoryComponent::TryForgeUpgrades()
{
	const bool bAxe = TryUpgradeAxe();
	const bool bPick = TryUpgradePickaxe();
	if (bAxe || bPick)
	{
		return true;
	}
	if (!GEngine)
	{
		return false;
	}
	if (AxeTier == EAxeTier::Steel && PickaxeTier == EAxeTier::Steel)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Silver, TEXT("Both tools are fully forged."));
	}
	else
	{
		FString Hint = TEXT("Bring mats to the blacksmith: ");
		if (AxeTier == EAxeTier::Stone)
		{
			Hint += TEXT("Axe 6 Iron + 4 Wood. ");
		}
		else if (AxeTier == EAxeTier::Iron)
		{
			Hint += TEXT("Axe 4 Crystal + 8 Iron. ");
		}
		if (PickaxeTier == EAxeTier::Stone)
		{
			Hint += TEXT("Pickaxe 8 Iron + 2 Wood.");
		}
		else if (PickaxeTier == EAxeTier::Iron)
		{
			Hint += TEXT("Pickaxe 6 Crystal + 6 Iron.");
		}
		GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Orange, Hint);
	}
	return false;
}

int32 UGatherInventoryComponent::HitsToChop() const
{
	int32 Hits = HitsForTier(AxeTier);
	if (const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner()))
	{
		if (Character->bSphereSkillHunt)
		{
			Hits = FMath::Max(1, Hits - 1);
		}
	}
	return Hits;
}

int32 UGatherInventoryComponent::HitsToMine() const
{
	int32 Hits = HitsForTier(PickaxeTier);
	if (const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner()))
	{
		if (Character->bSphereSkillHunt)
		{
			Hits = FMath::Max(1, Hits - 1);
		}
	}
	return Hits;
}

int32 UGatherInventoryComponent::WoodYield() const
{
	int32 Qty = YieldForTier(AxeTier);
	if (const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner()))
	{
		if (Character->bSphereSkillHunt)
		{
			++Qty;
		}
		Qty += Character->SphereYieldBonus;
	}
	return Qty;
}

int32 UGatherInventoryComponent::OreYield() const
{
	int32 Qty = YieldForTier(PickaxeTier);
	if (const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner()))
	{
		if (Character->bSphereSkillHunt)
		{
			++Qty;
		}
		Qty += Character->SphereYieldBonus;
	}
	return Qty;
}

FString UGatherInventoryComponent::AxeLabel() const
{
	return ToolLabel(AxeTier, TEXT("Axe"));
}

FString UGatherInventoryComponent::PickaxeLabel() const
{
	return ToolLabel(PickaxeTier, TEXT("Pick"));
}

FString UGatherInventoryComponent::InventoryLine() const
{
	return FString::Printf(TEXT("%s / %s   Wood %d  Stone %d  Fish %d  Wheat %d  Bread %d  Parts %d  Copper %d  Iron %d  Crystal %d  Coins %d"),
		*AxeLabel(), *PickaxeLabel(), GetCount(TEXT("Wood")), GetCount(TEXT("Stone")), GetCount(TEXT("Fish")), GetCount(TEXT("Wheat")), GetCount(TEXT("Bread")), GetCount(TEXT("ToolParts")), GetCount(TEXT("Copper")), GetCount(TEXT("Iron")), GetCount(TEXT("Crystal")), GetCount(TEXT("Coin")));
}
