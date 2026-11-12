// Copyright Epic Games, Inc. All Rights Reserved.
// LordsManorActor.cpp — Implementation of Lord's Manor / Town Hall for Village Tier, Style Upgrades & Estate Management

#include "LordsManorActor.h"
#include "Components/SceneComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "AdventurerGuildBoardActor.h"
#include "AdventurerManagerComponent.h"
#include "IsekaiMenuWidgets.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"

ALordsManorActor::ALordsManorActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	ManorMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ManorMesh"));
	ManorMesh->SetupAttachment(SceneRoot);
	ManorMesh->SetCollisionProfileName(TEXT("BlockAll"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> VillageManorMesh(TEXT("/Game/Fantastic_Village_Pack/meshes/buildings/SM_BLD_body_v01_01.SM_BLD_body_v01_01"));
	if (VillageManorMesh.Succeeded())
	{
		ManorMesh->SetStaticMesh(VillageManorMesh.Object);
		ManorMesh->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
		if (CubeMesh.Succeeded())
		{
			ManorMesh->SetStaticMesh(CubeMesh.Object);
			ManorMesh->SetRelativeScale3D(FVector(2.0f, 2.0f, 2.5f));
			ManorMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 125.0f));
		}
	}

	InteractionTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionTrigger"));
	InteractionTrigger->SetupAttachment(SceneRoot);
	InteractionTrigger->SetSphereRadius(350.0f);
	InteractionTrigger->SetCollisionProfileName(TEXT("Trigger"));
	InteractionTrigger->SetGenerateOverlapEvents(true);

	InteractionTrigger->OnComponentBeginOverlap.AddDynamic(this, &ALordsManorActor::OnOverlapBegin);
}

void ALordsManorActor::BeginPlay()
{
	Super::BeginPlay();

	// Initialize default building tiers if not pre-configured
	if (BuildingTiers.Num() == 0)
	{
		BuildingTiers.Add(ETownBuildingType::LordsManor, ManorTier);
		BuildingTiers.Add(ETownBuildingType::AdventurersGuild, EBuildingTier::Tier_1_Rustic);
		BuildingTiers.Add(ETownBuildingType::FarmPlot, EBuildingTier::Tier_1_Rustic);
		BuildingTiers.Add(ETownBuildingType::TownShop, EBuildingTier::Tier_1_Rustic);
		BuildingTiers.Add(ETownBuildingType::InnAndTavern, EBuildingTier::Tier_1_Rustic);
		BuildingTiers.Add(ETownBuildingType::BlacksmithForge, EBuildingTier::Tier_1_Rustic);
		BuildingTiers.Add(ETownBuildingType::AlchemyWorkshop, EBuildingTier::Tier_1_Rustic);
		BuildingTiers.Add(ETownBuildingType::ResidentialEstate, EBuildingTier::Tier_1_Rustic);
	}
}

void ALordsManorActor::OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (APawn* Pawn = Cast<APawn>(OtherActor))
	{
		if (APlayerController* PC = Cast<APlayerController>(Pawn->GetController()))
		{
			OpenManorUI(PC);
		}
	}
}

bool ALordsManorActor::OpenManorUI(APlayerController* PlayerController)
{
	if (!PlayerController) return false;

	if (ActiveManorWidget)
	{
		CloseManorUI();
	}

	UClass* ClassToSpawn = LordsManorWidgetClass ? LordsManorWidgetClass.Get() : UIsekaiLordsManorWidget::StaticClass();
	ActiveManorWidget = CreateWidget<UIsekaiLordsManorWidget>(PlayerController, ClassToSpawn);
	if (ActiveManorWidget)
	{
		ActiveManorWidget->InitializeManor(this);
		ActiveManorWidget->AddToViewport(10);

		PlayerController->SetShowMouseCursor(true);
		FInputModeGameAndUI InputMode;
		InputMode.SetWidgetToFocus(ActiveManorWidget->TakeWidget());
		InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		PlayerController->SetInputMode(InputMode);
		return true;
	}

	return false;
}

void ALordsManorActor::CloseManorUI()
{
	if (ActiveManorWidget)
	{
		ActiveManorWidget->RemoveFromParent();
		ActiveManorWidget = nullptr;

		if (UWorld* World = GetWorld())
		{
			if (APlayerController* PC = World->GetFirstPlayerController())
			{
				PC->SetShowMouseCursor(false);
				PC->SetInputMode(FInputModeGameOnly());
			}
		}
	}
}

EBuildingTier ALordsManorActor::GetBuildingTier(ETownBuildingType BuildingType) const
{
	if (const EBuildingTier* FoundTier = BuildingTiers.Find(BuildingType))
	{
		return *FoundTier;
	}
	return EBuildingTier::Tier_1_Rustic;
}

bool ALordsManorActor::CanUpgradeBuilding(ETownBuildingType BuildingType, FText& OutReason) const
{
	const EBuildingTier Current = GetBuildingTier(BuildingType);
	const int32 CurrentVal = FTownBuildingRecord::GetTierValue(Current);

	if (CurrentVal >= 5)
	{
		OutReason = FText::FromString(TEXT("Building is already at maximum Tier 5 (Paragon / Grand Estate)."));
		return false;
	}

	const int32 TargetVal = CurrentVal + 1;
	const EBuildingTier TargetTier = FTownBuildingRecord::GetTierFromValue(TargetVal);

	// Buildings cannot exceed the Lord's Manor tier!
	if (BuildingType != ETownBuildingType::LordsManor)
	{
		const int32 ManorVal = FTownBuildingRecord::GetTierValue(ManorTier);
		if (TargetVal > ManorVal)
		{
			OutReason = FText::FromString(FString::Printf(TEXT("Requires Lord's Manor to be upgraded to Tier %d before town buildings can reach this level."), TargetVal));
			return false;
		}
	}

	OutReason = FText::FromString(TEXT("Eligible for upgrade."));
	return true;
}

bool ALordsManorActor::UpgradeBuilding(ETownBuildingType BuildingType, int32& PlayerGold, FTownStockpile& Stockpile, FText& OutReason)
{
	if (!CanUpgradeBuilding(BuildingType, OutReason))
	{
		return false;
	}

	const EBuildingTier Current = GetBuildingTier(BuildingType);
	const int32 TargetVal = FTownBuildingRecord::GetTierValue(Current) + 1;
	const EBuildingTier TargetTier = FTownBuildingRecord::GetTierFromValue(TargetVal);

	const FTownBuildingRecord Req = FTownBuildingRecord::CreateDefaultRecord(BuildingType, TargetTier);

	// Check Gold
	if (PlayerGold < Req.UpgradeGoldCost)
	{
		OutReason = FText::FromString(FString::Printf(TEXT("Insufficient Gold. Required: %d, Available: %d."), Req.UpgradeGoldCost, PlayerGold));
		return false;
	}

	// Check Timber & Stone in Crafting Stockpile
	const int32 AvailableTimber = Stockpile.GetStock(EStockpileCategory::Crafting, TEXT("Mat_Timber"));
	const int32 AvailableStone = Stockpile.GetStock(EStockpileCategory::Crafting, TEXT("Mat_Stone"));
	const int32 AvailableCores = Stockpile.GetStock(EStockpileCategory::Crafting, TEXT("Mat_DemonCore"));

	if (AvailableTimber < Req.UpgradeTimberCost)
	{
		OutReason = FText::FromString(FString::Printf(TEXT("Insufficient Timber in Stockpile. Required: %d, Available: %d."), Req.UpgradeTimberCost, AvailableTimber));
		return false;
	}

	if (AvailableStone < Req.UpgradeStoneCost)
	{
		OutReason = FText::FromString(FString::Printf(TEXT("Insufficient Stone in Stockpile. Required: %d, Available: %d."), Req.UpgradeStoneCost, AvailableStone));
		return false;
	}

	if (Req.UpgradeDemonCoreCost > 0 && AvailableCores < Req.UpgradeDemonCoreCost)
	{
		OutReason = FText::FromString(FString::Printf(TEXT("Insufficient Demon Cores in Stockpile. Required: %d, Available: %d."), Req.UpgradeDemonCoreCost, AvailableCores));
		return false;
	}

	// Deduct resources
	PlayerGold -= Req.UpgradeGoldCost;
	Stockpile.ConsumeStock(EStockpileCategory::Crafting, TEXT("Mat_Timber"), Req.UpgradeTimberCost);
	Stockpile.ConsumeStock(EStockpileCategory::Crafting, TEXT("Mat_Stone"), Req.UpgradeStoneCost);
	if (Req.UpgradeDemonCoreCost > 0)
	{
		Stockpile.ConsumeStock(EStockpileCategory::Crafting, TEXT("Mat_DemonCore"), Req.UpgradeDemonCoreCost);
	}

	// Apply upgrade
	BuildingTiers.Add(BuildingType, TargetTier);

	if (BuildingType == ETownBuildingType::LordsManor)
	{
		ManorTier = TargetTier;

		// Advance Housing Tiers and town prosperity
		switch (ManorTier)
		{
		case EBuildingTier::Tier_2_Timber:
			HousingTier = EResidentialHousingTier::ArtisanTownhouse;
			VillageStyle = ETownArchitecturalStyle::MedievalHalfTimbered;
			DailyTaxRevenue = 350;
			NoblePatronCount = 3;
			break;
		case EBuildingTier::Tier_3_StoneMasonry:
			HousingTier = EResidentialHousingTier::MerchantManor;
			VillageStyle = ETownArchitecturalStyle::StoneMasonry;
			DailyTaxRevenue = 750;
			NoblePatronCount = 7;
			break;
		case EBuildingTier::Tier_4_Fortified:
			HousingTier = EResidentialHousingTier::NobleEstate;
			VillageStyle = ETownArchitecturalStyle::GothicFortress;
			DailyTaxRevenue = 1500;
			NoblePatronCount = 14;
			break;
		case EBuildingTier::Tier_5_GrandEstate:
			HousingTier = EResidentialHousingTier::RoyalPalace;
			VillageStyle = ETownArchitecturalStyle::RoyalPalatial;
			DailyTaxRevenue = 3000;
			NoblePatronCount = 25;
			break;
		default:
			break;
		}

		OnVillageTierUpgraded.Broadcast(ManorTier, VillageStyle);
	}

	OnBuildingTierUpgraded.Broadcast(BuildingType, TargetTier);
	OutReason = FText::FromString(FString::Printf(TEXT("Successfully upgraded %s to Tier %d!"), *Req.BuildingName.ToString(), TargetVal));
	return true;
}

bool ALordsManorActor::UpgradeManor(int32& PlayerGold, FTownStockpile& Stockpile, FText& OutReason)
{
	return UpgradeBuilding(ETownBuildingType::LordsManor, PlayerGold, Stockpile, OutReason);
}

void ALordsManorActor::SetVillageArchitecturalStyle(ETownArchitecturalStyle NewStyle)
{
	VillageStyle = NewStyle;
	OnArchitecturalStyleChanged.Broadcast(VillageStyle);
}

int32 ALordsManorActor::CollectDailyTaxes()
{
	int32 TotalTax = DailyTaxRevenue;
	UWorld* World = GetWorld();
	if (World)
	{
		for (TActorIterator<AAdventurerGuildBoardActor> It(World); It; ++It)
		{
			if (AAdventurerGuildBoardActor* Board = *It)
			{
				if (Board->AdventurerManager)
				{
					TotalTax += Board->AdventurerManager->CollectAdventurerNobleTaxes();
					NoblePatronCount = Board->AdventurerManager->GetTotalLandedNoblesCount();
				}
				break;
			}
		}
	}
	return TotalTax;
}
