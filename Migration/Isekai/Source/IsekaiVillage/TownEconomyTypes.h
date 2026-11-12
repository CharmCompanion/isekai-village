// Copyright Epic Games, Inc. All Rights Reserved.
// TownEconomyTypes.h — Item Economy, Shop Items, Blacksmith Forging, and Alchemy Compounding

#pragma once

#include "CoreMinimal.h"
#include "IsekaiVillageTypes.h"
#include "TownEconomyTypes.generated.h"

/**
 * High-level category of inventory & shop items.
 */
UENUM(BlueprintType)
enum class EItemType : uint8
{
	Consumable UMETA(DisplayName = "Consumable (Gels, Bottles)"),
	Material   UMETA(DisplayName = "Crafting Material (Ores, Herbs, Demon Drops)"),
	Equipment  UMETA(DisplayName = "Equipment (Weapons, Armor, Rings)"),
	Seed       UMETA(DisplayName = "Farming Seed")
};

/**
 * Shop item definition for merchant inventories.
 */
USTRUCT(BlueprintType)
struct FShopItem
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Item")
	FName ItemID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Item")
	FText DisplayName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Item")
	FText Description = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Item")
	EItemType ItemType = EItemType::Consumable;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
	int32 BuyPrice = 100;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
	int32 SellPrice = 50;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Economy")
	int32 Stock = 99;
};

/**
 * Blacksmith forging and upgrade recipe.
 */
USTRUCT(BlueprintType)
struct FBlacksmithRecipe
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	FName RecipeID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	FText OutputName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	FName BaseEquipmentID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	int32 RequiredOres = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	int32 RequiredDemonCores = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	int32 UpgradeLevel = 1; // +1 to +10

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	float AddedAttackPower = 15.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	float AddedDefense = 8.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	EElement ImbuedElement = EElement::Fire;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Blacksmith")
	int32 GoldCost = 250;
};

/**
 * Alchemy compounding & potion synthesis recipe.
 */
USTRUCT(BlueprintType)
struct FAlchemyRecipe
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	FName RecipeID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	FText OutputPotionName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	FText EffectDescription = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	int32 RequiredHerbs = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	int32 RequiredCrops = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	int32 RequiredDemonEssence = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Alchemy")
	int32 GoldCost = 150;
};

/**
 * Stockpile category for town supply management.
 */
UENUM(BlueprintType)
enum class EStockpileCategory : uint8
{
	Food         UMETA(DisplayName = "Food & Ingredients (Crops, Meat, Herbs)"),
	Crafting     UMETA(DisplayName = "Crafting Supplies (Ores, Timber, Demon Cores)"),
	ShopSupply   UMETA(DisplayName = "Shop Supplies (Gels, Bottles, Seeds, Tools)")
};

/**
 * Unified town stockpile management for Food, Crafting, and Shop Supplies.
 */
USTRUCT(BlueprintType)
struct FTownStockpile
{
	GENERATED_BODY()

	// Food & Cooking Ingredients (Crops, Meats, Foraged Goods)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stockpile|Food")
	TMap<FName, int32> FoodItems;

	// Blacksmith & Crafting Supplies (Ores, Timber, Monster Cores)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stockpile|Crafting")
	TMap<FName, int32> CraftingMaterials;

	// General Merchant Shop Supplies (Gels, Bottles, Seeds, Tools)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stockpile|Shop")
	TMap<FName, int32> ShopSupplies;

	void AddStock(EStockpileCategory Category, FName ItemID, int32 Amount)
	{
		if (ItemID == NAME_None || Amount <= 0) return;

		TMap<FName, int32>* TargetMap = GetMapForCategory(Category);
		if (TargetMap)
		{
			int32 Current = TargetMap->FindRef(ItemID);
			TargetMap->Add(ItemID, Current + Amount);
		}
	}

	bool ConsumeStock(EStockpileCategory Category, FName ItemID, int32 Amount)
	{
		if (ItemID == NAME_None || Amount <= 0) return false;

		TMap<FName, int32>* TargetMap = GetMapForCategory(Category);
		if (TargetMap)
		{
			int32 Current = TargetMap->FindRef(ItemID);
			if (Current >= Amount)
			{
				TargetMap->Add(ItemID, Current - Amount);
				return true;
			}
		}
		return false;
	}

	int32 GetStock(EStockpileCategory Category, FName ItemID) const
	{
		const TMap<FName, int32>* TargetMap = GetConstMapForCategory(Category);
		if (TargetMap)
		{
			return TargetMap->FindRef(ItemID);
		}
		return 0;
	}

	int32 GetTotalFoodCount() const
	{
		int32 Sum = 0;
		for (const auto& Pair : FoodItems) Sum += Pair.Value;
		return Sum;
	}

	int32 GetFoodVarietyCount() const
	{
		int32 Count = 0;
		for (const auto& Pair : FoodItems)
		{
			if (Pair.Value > 0) Count++;
		}
		return Count;
	}

private:
	TMap<FName, int32>* GetMapForCategory(EStockpileCategory Category)
	{
		switch (Category)
		{
		case EStockpileCategory::Food: return &FoodItems;
		case EStockpileCategory::Crafting: return &CraftingMaterials;
		case EStockpileCategory::ShopSupply: return &ShopSupplies;
		default: return nullptr;
		}
	}

	const TMap<FName, int32>* GetConstMapForCategory(EStockpileCategory Category) const
	{
		switch (Category)
		{
		case EStockpileCategory::Food: return &FoodItems;
		case EStockpileCategory::Crafting: return &CraftingMaterials;
		case EStockpileCategory::ShopSupply: return &ShopSupplies;
		default: return nullptr;
		}
	}
};

/**
 * All town buildings and "mini-game" mechanic structures.
 */
UENUM(BlueprintType)
enum class ETownBuildingType : uint8
{
	LordsManor        UMETA(DisplayName = "Lord's Manor / Town Hall"),
	AdventurersGuild  UMETA(DisplayName = "Adventurers Guild Hall"),
	FarmPlot          UMETA(DisplayName = "Agricultural Farm Plot"),
	TownShop          UMETA(DisplayName = "General Store & Apothecary"),
	InnAndTavern      UMETA(DisplayName = "Inn & Tavern"),
	BlacksmithForge   UMETA(DisplayName = "Blacksmith Forge"),
	AlchemyWorkshop   UMETA(DisplayName = "Alchemy Laboratory"),
	ResidentialEstate UMETA(DisplayName = "Residential & Noble Estates")
};

/**
 * Standardized 5-tier upgrade level across all town buildings.
 */
UENUM(BlueprintType)
enum class EBuildingTier : uint8
{
	Tier_1_Rustic        UMETA(DisplayName = "Tier 1: Rustic Wood / Basic"),
	Tier_2_Timber        UMETA(DisplayName = "Tier 2: Sturdy Timber / Reinforced"),
	Tier_3_StoneMasonry  UMETA(DisplayName = "Tier 3: Masonry Stone / Established"),
	Tier_4_Fortified     UMETA(DisplayName = "Tier 4: Ironclad Fortress / Grand"),
	Tier_5_GrandEstate   UMETA(DisplayName = "Tier 5: Mythic / Royal Estate / Paragon")
};

/**
 * Village-wide visual architectural styles unlocked by the Lord's Manor.
 */
UENUM(BlueprintType)
enum class ETownArchitecturalStyle : uint8
{
	RusticTimber         UMETA(DisplayName = "Rustic Timber (Pioneer Hamlet)"),
	MedievalHalfTimbered UMETA(DisplayName = "Medieval Half-Timbered (Timber Village)"),
	StoneMasonry         UMETA(DisplayName = "Stone Masonry (Prosperous Town)"),
	GothicFortress       UMETA(DisplayName = "Gothic Slate & Iron (Fortified City)"),
	RoyalPalatial        UMETA(DisplayName = "Royal Palatial (Grand Noble Domain)")
};

/**
 * Residential housing tiers enabling Lords, Nobles, and Estate houses.
 */
UENUM(BlueprintType)
enum class EResidentialHousingTier : uint8
{
	CommonerCottage   UMETA(DisplayName = "Commoner Cottage & Bunkhouse"),
	ArtisanTownhouse  UMETA(DisplayName = "Artisan Townhouse"),
	MerchantManor     UMETA(DisplayName = "Merchant Manor"),
	NobleEstate       UMETA(DisplayName = "Noble Estate (High Aristocracy)"),
	RoyalPalace       UMETA(DisplayName = "Lordly Chateau / Royal Palace")
};

/**
 * Unified building record containing upgrade requirements and tier perks.
 */
USTRUCT(BlueprintType)
struct FTownBuildingRecord
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building")
	ETownBuildingType BuildingType = ETownBuildingType::LordsManor;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building")
	EBuildingTier CurrentTier = EBuildingTier::Tier_1_Rustic;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building")
	FText BuildingName = FText::GetEmpty();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building|Cost")
	int32 UpgradeGoldCost = 500;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building|Cost")
	int32 UpgradeTimberCost = 10;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building|Cost")
	int32 UpgradeStoneCost = 5;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building|Cost")
	int32 UpgradeDemonCoreCost = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building")
	EBuildingTier RequiredManorTier = EBuildingTier::Tier_1_Rustic;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Building")
	FText TierPerkDescription = FText::GetEmpty();

	static int32 GetTierValue(EBuildingTier Tier)
	{
		return static_cast<int32>(Tier) + 1;
	}

	static EBuildingTier GetTierFromValue(int32 Value)
	{
		return static_cast<EBuildingTier>(FMath::Clamp(Value - 1, 0, 4));
	}

	static FTownBuildingRecord CreateDefaultRecord(ETownBuildingType Type, EBuildingTier Tier)
	{
		FTownBuildingRecord Rec;
		Rec.BuildingType = Type;
		Rec.CurrentTier = Tier;
		const int32 TVal = GetTierValue(Tier);

		Rec.UpgradeGoldCost = 300 * TVal * TVal;
		Rec.UpgradeTimberCost = 10 * TVal;
		Rec.UpgradeStoneCost = 8 * TVal;
		Rec.UpgradeDemonCoreCost = (TVal >= 3) ? (TVal - 2) : 0;
		Rec.RequiredManorTier = Tier;

		switch (Type)
		{
		case ETownBuildingType::LordsManor:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Lord's Manor (Tier %d)"), TVal));
			Rec.RequiredManorTier = EBuildingTier::Tier_1_Rustic; // Manor gates itself
			Rec.TierPerkDescription = FText::FromString(TEXT("Increases village administrative tier, tax revenue, and max upgrade ceiling for all buildings."));
			break;
		case ETownBuildingType::AdventurersGuild:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Adventurers Guild Hall (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Unlocks higher bounty ranks, extra concurrent expedition slots, and expanded recruitment pool."));
			break;
		case ETownBuildingType::FarmPlot:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Agricultural Farm (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Expands soil grid dimensions, boosts crop growth speed, pristine quality chance, and arcane soil yields."));
			break;
		case ETownBuildingType::TownShop:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("General Store & Apothecary (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Expands consumable inventory with Miracle Gels, Elixirs, All-Divides, and rare seeds."));
			break;
		case ETownBuildingType::InnAndTavern:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Inn & Tavern (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Adds dining buffs, private luxury suites with full TP recovery, onsen bathhouse, and grand banquet hall."));
			break;
		case ETownBuildingType::BlacksmithForge:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Blacksmith Forge (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Raises maximum refinement ceiling (+1 to +10), unlocks elemental infusion, and divine masterwork traits."));
			break;
		case ETownBuildingType::AlchemyWorkshop:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Alchemy Workshop (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Unlocks high-tier transmutation, philosopher catalysts, and deep demon core purification."));
			break;
		case ETownBuildingType::ResidentialEstate:
			Rec.BuildingName = FText::FromString(FString::Printf(TEXT("Noble & Estate Housing (Tier %d)"), TVal));
			Rec.TierPerkDescription = FText::FromString(TEXT("Upgrades housing from commoner cottages to artisan townhouses, merchant manors, and noble estates."));
			break;
		}

		return Rec;
	}
};

