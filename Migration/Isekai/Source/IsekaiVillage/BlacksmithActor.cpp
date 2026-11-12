// Copyright Epic Games, Inc. All Rights Reserved.
// BlacksmithActor.cpp — Interactive Forge for Weapon Upgrading (+1 to +10), Elemental Infusion & Salvage

#include "BlacksmithActor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"

ABlacksmithActor::ABlacksmithActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	AnvilMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AnvilMesh"));
	AnvilMesh->SetupAttachment(SceneRoot);
	AnvilMesh->SetCollisionProfileName(TEXT("BlockAll"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> ForgeTableMesh(TEXT("/Game/Fantastic_Village_Pack/meshes/props/furniture/SM_PROP_table_01.SM_PROP_table_01"));
	if (ForgeTableMesh.Succeeded())
	{
		AnvilMesh->SetStaticMesh(ForgeTableMesh.Object);
		AnvilMesh->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
		AnvilMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
		if (CubeMesh.Succeeded())
		{
			AnvilMesh->SetStaticMesh(CubeMesh.Object);
			AnvilMesh->SetRelativeScale3D(FVector(0.6f, 0.9f, 0.8f));
			AnvilMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 40.0f));
		}
	}

	InteractionTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionTrigger"));
	InteractionTrigger->SetupAttachment(SceneRoot);
	InteractionTrigger->SetSphereRadius(240.0f);
	InteractionTrigger->SetCollisionProfileName(TEXT("Trigger"));
	InteractionTrigger->SetGenerateOverlapEvents(true);

	InteractionTrigger->OnComponentBeginOverlap.AddDynamic(this, &ABlacksmithActor::OnOverlapBegin);
}

void ABlacksmithActor::BeginPlay()
{
	Super::BeginPlay();

	if (ForgeRecipes.Num() == 0)
	{
		PopulateDefaultForgeRecipes();
	}
}

void ABlacksmithActor::PopulateDefaultForgeRecipes()
{
	// Recipe 1: Iron Longsword Refinement +1
	{
		FBlacksmithRecipe R;
		R.RecipeID = TEXT("Forge_IronSword_01");
		R.OutputName = FText::FromString(TEXT("Iron Longsword +1"));
		R.BaseEquipmentID = TEXT("Weapon_IronSword");
		R.RequiredOres = 2;
		R.RequiredDemonCores = 1;
		R.UpgradeLevel = 1;
		R.AddedAttackPower = 12.0f;
		R.GoldCost = 150;
		ForgeRecipes.Add(R);
	}

	// Recipe 2: Silver Broadsword Refinement +2
	{
		FBlacksmithRecipe R;
		R.RecipeID = TEXT("Forge_SilverSword_02");
		R.OutputName = FText::FromString(TEXT("Silver Broadsword +2"));
		R.BaseEquipmentID = TEXT("Weapon_SilverSword");
		R.RequiredOres = 4;
		R.RequiredDemonCores = 2;
		R.UpgradeLevel = 2;
		R.AddedAttackPower = 28.0f;
		R.GoldCost = 350;
		ForgeRecipes.Add(R);
	}

	// Recipe 3: Flame Infusion
	{
		FBlacksmithRecipe R;
		R.RecipeID = TEXT("Forge_Imbue_Fire");
		R.OutputName = FText::FromString(TEXT("Flametongue Edge"));
		R.BaseEquipmentID = TEXT("Weapon_IronSword");
		R.RequiredOres = 3;
		R.RequiredDemonCores = 3;
		R.ImbuedElement = EElement::Fire;
		R.AddedAttackPower = 20.0f;
		R.GoldCost = 400;
		ForgeRecipes.Add(R);
	}
}

void ABlacksmithActor::InteractWithPlayer(APawn* PlayerPawn)
{
	if (!PlayerPawn) return;
	OnBlacksmithInteracted.Broadcast(PlayerPawn);
}

void ABlacksmithActor::SetForgeTier(EBuildingTier NewTier)
{
	ForgeTier = NewTier;
}

int32 ABlacksmithActor::GetMaxRefinementLevel() const
{
	const int32 TVal = FTownBuildingRecord::GetTierValue(ForgeTier);
	return FMath::Clamp(TVal * 2, 2, 10); // Tier 1: +2, Tier 2: +4, Tier 3: +6, Tier 4: +8, Tier 5: +10
}

bool ABlacksmithActor::UpgradeWeapon(FName WeaponID, int32 TargetLevel, int32& PlayerGold,
	int32& PlayerOres, int32& PlayerDemonCores, float& OutNewAtk)
{
	if (TargetLevel < 1 || TargetLevel > GetMaxRefinementLevel()) return false;

	const int32 RequiredOre = TargetLevel * 2;
	const int32 RequiredCore = FMath::Max(1, TargetLevel / 2);
	const int32 CostGold = TargetLevel * 150;

	if (PlayerGold < CostGold || PlayerOres < RequiredOre || PlayerDemonCores < RequiredCore)
	{
		return false;
	}

	PlayerGold -= CostGold;
	PlayerOres -= RequiredOre;
	PlayerDemonCores -= RequiredCore;

	// Calculate new attack value: Base 30 + (Level * 14)
	OutNewAtk = 30.0f + (TargetLevel * 14.0f);

	OnWeaponUpgraded.Broadcast(WeaponID, TargetLevel, OutNewAtk);
	return true;
}

bool ABlacksmithActor::ImbueElement(FName WeaponID, EElement NewElement, int32& PlayerGold, int32& PlayerDemonCores)
{
	const int32 CostGold = 350;
	const int32 CostCores = 2;

	if (PlayerGold < CostGold || PlayerDemonCores < CostCores)
	{
		return false;
	}

	PlayerGold -= CostGold;
	PlayerDemonCores -= CostCores;
	return true;
}

bool ABlacksmithActor::DisassembleEquipment(FName WeaponID, int32& OutOresReturned, int32& OutDemonDustReturned)
{
	OutOresReturned = FMath::RandRange(2, 5);
	OutDemonDustReturned = FMath::RandRange(1, 3);
	return true;
}

void ABlacksmithActor::OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (APawn* Pawn = Cast<APawn>(OtherActor))
	{
		InteractWithPlayer(Pawn);
	}
}
