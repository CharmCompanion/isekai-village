// Copyright Epic Games, Inc. All Rights Reserved.
// TownShopActor.cpp — Interactive General Store, Apothecary, and Inn/Tavern Rest Stop

#include "TownShopActor.h"
#include "BattleCharacter.h"
#include "AdventurerManagerComponent.h"
#include "EngineUtils.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"

#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"

ATownShopActor::ATownShopActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	ShopCounterMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ShopCounterMesh"));
	ShopCounterMesh->SetupAttachment(SceneRoot);
	ShopCounterMesh->SetCollisionProfileName(TEXT("BlockAll"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> MarketStallMesh(TEXT("/Game/Fantastic_Village_Pack/meshes/props/construction/SM_PROP_market_v01_01.SM_PROP_market_v01_01"));
	if (MarketStallMesh.Succeeded())
	{
		ShopCounterMesh->SetStaticMesh(MarketStallMesh.Object);
		ShopCounterMesh->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
		ShopCounterMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
		if (CubeMesh.Succeeded())
		{
			ShopCounterMesh->SetStaticMesh(CubeMesh.Object);
			ShopCounterMesh->SetRelativeScale3D(FVector(0.8f, 2.0f, 0.9f));
			ShopCounterMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 45.0f));
		}
	}

	InteractionTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionTrigger"));
	InteractionTrigger->SetupAttachment(SceneRoot);
	InteractionTrigger->SetSphereRadius(240.0f);
	InteractionTrigger->SetCollisionProfileName(TEXT("Trigger"));
	InteractionTrigger->SetGenerateOverlapEvents(true);

	InteractionTrigger->OnComponentBeginOverlap.AddDynamic(this, &ATownShopActor::OnOverlapBegin);
}

void ATownShopActor::BeginPlay()
{
	Super::BeginPlay();

	if (Catalog.Num() == 0)
	{
		PopulateDefaultCatalog();
	}
}

void ATownShopActor::PopulateDefaultCatalog()
{
	if (ShopType == ETownShopType::GeneralStore)
	{
		ShopName = FText::FromString(TEXT("Galdor's General Provisions"));

		FShopItem Item1;
		Item1.ItemID = TEXT("Item_AppleGel");
		Item1.DisplayName = FText::FromString(TEXT("Apple Gel"));
		Item1.Description = FText::FromString(TEXT("Sweet apple gelatin. Restores 30% of maximum HP."));
		Item1.ItemType = EItemType::Consumable;
		Item1.BuyPrice = 100;
		Item1.SellPrice = 50;
		Catalog.Add(Item1);

		FShopItem Item2;
		Item2.ItemID = TEXT("Item_OrangeGel");
		Item2.DisplayName = FText::FromString(TEXT("Orange Gel"));
		Item2.Description = FText::FromString(TEXT("Tangy citrus gelatin. Restores 30% of maximum TP."));
		Item2.ItemType = EItemType::Consumable;
		Item2.BuyPrice = 180;
		Item2.SellPrice = 90;
		Catalog.Add(Item2);

		FShopItem Item3;
		Item3.ItemID = TEXT("Item_LifeBottle");
		Item3.DisplayName = FText::FromString(TEXT("Life Bottle"));
		Item3.Description = FText::FromString(TEXT("Miraculous flask that revives a fallen ally with 30% HP."));
		Item3.ItemType = EItemType::Consumable;
		Item3.BuyPrice = 300;
		Item3.SellPrice = 150;
		Catalog.Add(Item3);

		FShopItem Item4;
		Item4.ItemID = TEXT("Item_PanaceaBottle");
		Item4.DisplayName = FText::FromString(TEXT("Panacea Bottle"));
		Item4.Description = FText::FromString(TEXT("Cures all status ailments (Poison, Paralysis, Curse, Burn)."));
		Item4.ItemType = EItemType::Consumable;
		Item4.BuyPrice = 120;
		Item4.SellPrice = 60;
		Catalog.Add(Item4);

		FShopItem Tool1;
		Tool1.ItemID = TEXT("Tool_FarmingHoe");
		Tool1.DisplayName = FText::FromString(TEXT("Standard Farmer's Hoe"));
		Tool1.Description = FText::FromString(TEXT("Sturdy iron hoe for tilling farm soil plots."));
		Tool1.ItemType = EItemType::Equipment;
		Tool1.BuyPrice = 200;
		Tool1.SellPrice = 100;
		Catalog.Add(Tool1);
	}
	else if (ShopType == ETownShopType::Apothecary)
	{
		ShopName = FText::FromString(TEXT("Althea's Herbology & Seeds"));

		FShopItem Item1;
		Item1.ItemID = TEXT("Item_LemonGel");
		Item1.DisplayName = FText::FromString(TEXT("Lemon Gel"));
		Item1.Description = FText::FromString(TEXT("Potent lemon gelatin. Restores 60% of maximum HP."));
		Item1.ItemType = EItemType::Consumable;
		Item1.BuyPrice = 250;
		Item1.SellPrice = 125;
		Catalog.Add(Item1);

		FShopItem Item2;
		Item2.ItemID = TEXT("Item_MelangeGel");
		Item2.DisplayName = FText::FromString(TEXT("Melange Gel"));
		Item2.Description = FText::FromString(TEXT("Rare blend. Restores 30% HP and 30% TP simultaneously."));
		Item2.ItemType = EItemType::Consumable;
		Item2.BuyPrice = 380;
		Item2.SellPrice = 190;
		Catalog.Add(Item2);

		FShopItem Seed1;
		Seed1.ItemID = TEXT("Seed_Wheat");
		Seed1.DisplayName = FText::FromString(TEXT("Golden Wheat Seeds"));
		Seed1.Description = FText::FromString(TEXT("Seeds for baking flour and campfire bread recipes."));
		Seed1.ItemType = EItemType::Seed;
		Seed1.BuyPrice = 35;
		Seed1.SellPrice = 15;
		Catalog.Add(Seed1);

		FShopItem Seed2;
		Seed2.ItemID = TEXT("Seed_MoonTomato");
		Seed2.DisplayName = FText::FromString(TEXT("Moonlit Tomato Seeds"));
		Seed2.Description = FText::FromString(TEXT("Juicy crimson tomatoes essential for pasta and stews."));
		Seed2.ItemType = EItemType::Seed;
		Seed2.BuyPrice = 50;
		Seed2.SellPrice = 25;
		Catalog.Add(Seed2);

		// Tier 3+ Rare Seeds
		if (ShopTier >= EBuildingTier::Tier_3_StoneMasonry)
		{
			FShopItem Seed3;
			Seed3.ItemID = TEXT("Seed_DemonBerry");
			Seed3.DisplayName = FText::FromString(TEXT("Demon Berry Seeds"));
			Seed3.Description = FText::FromString(TEXT("Mystical berries that absorb chaotic mana from dungeon soil."));
			Seed3.ItemType = EItemType::Seed;
			Seed3.BuyPrice = 120;
			Seed3.SellPrice = 60;
			Catalog.Add(Seed3);
		}
	}
	else
	{
		ShopName = FText::FromString(TEXT("The Hearth & Barrel Inn"));
		const int32 TVal = FTownBuildingRecord::GetTierValue(ShopTier);
		InnRestCost = 40 + (TVal * 20); // 60, 80, 100, 120, 140
	}

	// High-tier consumables for General Store & Apothecary
	if (ShopType != ETownShopType::InnTavern)
	{
		if (ShopTier >= EBuildingTier::Tier_2_Timber)
		{
			FShopItem Lemon;
			Lemon.ItemID = TEXT("Item_LemonGel");
			Lemon.DisplayName = FText::FromString(TEXT("Lemon Gel"));
			Lemon.Description = FText::FromString(TEXT("Restores 60% of maximum HP."));
			Lemon.ItemType = EItemType::Consumable;
			Lemon.BuyPrice = 240;
			Lemon.SellPrice = 120;
			Catalog.Add(Lemon);

			FShopItem Pine;
			Pine.ItemID = TEXT("Item_PineappleGel");
			Pine.DisplayName = FText::FromString(TEXT("Pineapple Gel"));
			Pine.Description = FText::FromString(TEXT("Restores 60% of maximum TP."));
			Pine.ItemType = EItemType::Consumable;
			Pine.BuyPrice = 360;
			Pine.SellPrice = 180;
			Catalog.Add(Pine);
		}

		if (ShopTier >= EBuildingTier::Tier_3_StoneMasonry)
		{
			FShopItem Miracle;
			Miracle.ItemID = TEXT("Item_MiracleGel");
			Miracle.DisplayName = FText::FromString(TEXT("Miracle Gel"));
			Miracle.Description = FText::FromString(TEXT("Restores 60% HP and 60% TP simultaneously."));
			Miracle.ItemType = EItemType::Consumable;
			Miracle.BuyPrice = 600;
			Miracle.SellPrice = 300;
			Catalog.Add(Miracle);

			FShopItem Elixir;
			Elixir.ItemID = TEXT("Item_Elixir");
			Elixir.DisplayName = FText::FromString(TEXT("Elixir"));
			Elixir.Description = FText::FromString(TEXT("Miraculous draught. Restores 100% HP and TP."));
			Elixir.ItemType = EItemType::Consumable;
			Elixir.BuyPrice = 1200;
			Elixir.SellPrice = 600;
			Catalog.Add(Elixir);
		}

		if (ShopTier >= EBuildingTier::Tier_4_Fortified)
		{
			FShopItem AllDivide;
			AllDivide.ItemID = TEXT("Item_AllDivide");
			AllDivide.DisplayName = FText::FromString(TEXT("All-Divide"));
			AllDivide.Description = FText::FromString(TEXT("Legendary hourglass that halves all damage dealt and taken by both allies and enemies."));
			AllDivide.ItemType = EItemType::Consumable;
			AllDivide.BuyPrice = 2500;
			AllDivide.SellPrice = 1250;
			Catalog.Add(AllDivide);
		}
	}
}

void ATownShopActor::SetShopTier(EBuildingTier NewTier)
{
	ShopTier = NewTier;
	Catalog.Empty();
	PopulateDefaultCatalog();
}

void ATownShopActor::InteractWithPlayer(APawn* PlayerPawn)
{
	if (!PlayerPawn) return;
	OnShopInteracted.Broadcast(PlayerPawn, ShopType);
}

bool ATownShopActor::BuyItem(FName ItemID, int32 Quantity, int32& PlayerGold, float DiscountMultiplier)
{
	if (Quantity <= 0) return false;

	for (FShopItem& Item : Catalog)
	{
		if (Item.ItemID == ItemID)
		{
			if (Item.Stock < Quantity) return false;

			int32 TotalPrice = FMath::RoundToInt(Item.BuyPrice * Quantity * FMath::Clamp(DiscountMultiplier, 0.5f, 1.0f));
			if (PlayerGold < TotalPrice) return false;

			PlayerGold -= TotalPrice;
			Item.Stock -= Quantity;
			return true;
		}
	}

	return false;
}

bool ATownShopActor::SellItem(FName ItemID, int32 Quantity, int32& PlayerGold)
{
	if (Quantity <= 0) return false;

	for (FShopItem& Item : Catalog)
	{
		if (Item.ItemID == ItemID)
		{
			int32 TotalPayout = Item.SellPrice * Quantity;
			PlayerGold += TotalPayout;
			Item.Stock += Quantity;
			return true;
		}
	}

	// Unlisted items sold at flat 50 Gald
	PlayerGold += 50 * Quantity;
	return true;
}

bool ATownShopActor::RestAtInn(APawn* PlayerPawn, int32& PlayerGold)
{
	if (!PlayerPawn || PlayerGold < InnRestCost) return false;

	PlayerGold -= InnRestCost;

	// Heal player character to full
	if (ABattleCharacter* BattleChar = Cast<ABattleCharacter>(PlayerPawn))
	{
		BattleChar->CurrentHP = BattleChar->MaxHP;
		BattleChar->CurrentTP = BattleChar->MaxTP;
		BattleChar->CurrentAG = BattleChar->MaxAG;
		BattleChar->bIsIncapacitated = false;
	}

	// Restore entire active adventurer party from incapacitation and fatigue
	const bool bIsLuxurySuite = (ShopTier >= EBuildingTier::Tier_5_GrandEstate);
	if (UAdventurerManagerComponent* AdvMgr = PlayerPawn->FindComponentByClass<UAdventurerManagerComponent>())
	{
		AdvMgr->RestEntireActivePartyAtInn(bIsLuxurySuite);
	}
	else if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AActor> It(World); It; ++It)
		{
			if (UAdventurerManagerComponent* FoundMgr = It->FindComponentByClass<UAdventurerManagerComponent>())
			{
				FoundMgr->RestEntireActivePartyAtInn(bIsLuxurySuite);
				break;
			}
		}
	}

	OnPartyRestedAtInn.Broadcast(PlayerPawn);
	return true;
}


void ATownShopActor::OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (APawn* Pawn = Cast<APawn>(OtherActor))
	{
		InteractWithPlayer(Pawn);
	}
}
