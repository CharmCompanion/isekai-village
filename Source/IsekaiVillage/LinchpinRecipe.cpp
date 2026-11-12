// Copyright Epic Games, Inc. All Rights Reserved.
#include "LinchpinRecipe.h"

static ULinchpinRecipe* MakeRecipe(const TCHAR* Id, const TCHAR* Name, ERoomFunction Function, const TArray<FName>& Tags)
{
	ULinchpinRecipe* Recipe = NewObject<ULinchpinRecipe>(GetTransientPackage(), FName(Id));
	Recipe->RecipeId = Id;
	Recipe->DisplayName = FText::FromString(Name);
	Recipe->ResultFunction = Function;
	Recipe->RequiredTags = Tags;
	return Recipe;
}

void ULinchpinRecipe::GetDefaultRecipes(TArray<TObjectPtr<ULinchpinRecipe>>& OutRecipes)
{
	OutRecipes.Reset();
	OutRecipes.Add(MakeRecipe(TEXT("Blacksmith"), TEXT("Blacksmith"), ERoomFunction::Blacksmith, {TEXT("Forge"), TEXT("Anvil")}));
	OutRecipes.Add(MakeRecipe(TEXT("Inn"), TEXT("Inn"), ERoomFunction::Inn, {TEXT("Bed"), TEXT("Counter")}));
	OutRecipes.Add(MakeRecipe(TEXT("Shop"), TEXT("Shop"), ERoomFunction::Shop, {TEXT("Counter"), TEXT("Crate")}));
	OutRecipes.Add(MakeRecipe(TEXT("Guild"), TEXT("Adventurers Guild"), ERoomFunction::AdventurersGuild, {TEXT("Desk"), TEXT("Board")}));
	OutRecipes.Add(MakeRecipe(TEXT("Bakery"), TEXT("Bakery"), ERoomFunction::Bakery, {TEXT("Oven"), TEXT("Counter")}));
	OutRecipes.Add(MakeRecipe(TEXT("Farmhouse"), TEXT("Farmhouse"), ERoomFunction::Farmhouse, {TEXT("Workbench"), TEXT("GrainSack")}));
	OutRecipes.Add(MakeRecipe(TEXT("Treasure"), TEXT("Treasure Room"), ERoomFunction::Treasure, {TEXT("Chest")}));
	OutRecipes.Add(MakeRecipe(TEXT("MonsterDen"), TEXT("Monster Den"), ERoomFunction::MonsterDen, {TEXT("Spawner")}));
	OutRecipes.Add(MakeRecipe(TEXT("BossLair"), TEXT("Boss Lair"), ERoomFunction::BossLair, {TEXT("Boss")}));
	OutRecipes.Add(MakeRecipe(TEXT("Vault"), TEXT("Vault"), ERoomFunction::Vault, {TEXT("Vault")}));
	OutRecipes.Add(MakeRecipe(TEXT("AlchemistLab"), TEXT("Alchemist Lab"), ERoomFunction::AlchemistLab, {TEXT("Cauldron"), TEXT("HerbRack")}));
	OutRecipes.Add(MakeRecipe(TEXT("Enchanter"), TEXT("Enchanter Spire"), ERoomFunction::Enchanter, {TEXT("ArcaneTable"), TEXT("CrystalFocus")}));
	OutRecipes.Add(MakeRecipe(TEXT("ArcaneForge"), TEXT("Arcane Celestial Forge"), ERoomFunction::ArcaneForge, {TEXT("CelestialAnvil"), TEXT("RunicCrucible")}));
}

TArray<ULinchpinRecipe*> ULinchpinRecipe::GetDefaultRecipesList()
{
	TArray<TObjectPtr<ULinchpinRecipe>> Ptrs;
	GetDefaultRecipes(Ptrs);
	TArray<ULinchpinRecipe*> Out;
	for (const auto& P : Ptrs)
	{
		if (P) Out.Add(P.Get());
	}
	return Out;
}
