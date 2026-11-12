// Copyright Epic Games, Inc. All Rights Reserved.
// AlchemyWorkshopActor.cpp — Interactive Alchemy Laboratory for Demon Core Refining & Potion Compounding

#include "AlchemyWorkshopActor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"

AAlchemyWorkshopActor::AAlchemyWorkshopActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	CauldronMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CauldronMesh"));
	CauldronMesh->SetupAttachment(SceneRoot);
	CauldronMesh->SetCollisionProfileName(TEXT("BlockAll"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> PotMesh(TEXT("/Game/Fantastic_Village_Pack/meshes/props/food/SM_PROP_cookingpot_big.SM_PROP_cookingpot_big"));
	if (PotMesh.Succeeded())
	{
		CauldronMesh->SetStaticMesh(PotMesh.Object);
		CauldronMesh->SetRelativeScale3D(FVector(1.2f, 1.2f, 1.2f));
		CauldronMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 0.0f));
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<UStaticMesh> CylinderMesh(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
		if (CylinderMesh.Succeeded())
		{
			CauldronMesh->SetStaticMesh(CylinderMesh.Object);
			CauldronMesh->SetRelativeScale3D(FVector(0.9f, 0.9f, 0.7f));
			CauldronMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 35.0f));
		}
	}

	CauldronGlow = CreateDefaultSubobject<UPointLightComponent>(TEXT("CauldronGlow"));
	CauldronGlow->SetupAttachment(CauldronMesh);
	CauldronGlow->SetRelativeLocation(FVector(0.0f, 0.0f, 40.0f));
	CauldronGlow->SetLightColor(FLinearColor(0.2f, 1.0f, 0.6f)); // Mystical cyan-emerald glow
	CauldronGlow->Intensity = 3000.0f;
	CauldronGlow->AttenuationRadius = 350.0f;

	InteractionTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionTrigger"));
	InteractionTrigger->SetupAttachment(SceneRoot);
	InteractionTrigger->SetSphereRadius(240.0f);
	InteractionTrigger->SetCollisionProfileName(TEXT("Trigger"));
	InteractionTrigger->SetGenerateOverlapEvents(true);

	InteractionTrigger->OnComponentBeginOverlap.AddDynamic(this, &AAlchemyWorkshopActor::OnOverlapBegin);
}

void AAlchemyWorkshopActor::BeginPlay()
{
	Super::BeginPlay();

	if (AlchemyRecipes.Num() == 0)
	{
		PopulateDefaultAlchemyRecipes();
	}
}

void AAlchemyWorkshopActor::PopulateDefaultAlchemyRecipes()
{
	// Recipe 1: Miracle Elixir
	{
		FAlchemyRecipe R;
		R.RecipeID = TEXT("Alchemy_MiracleElixir");
		R.OutputPotionName = FText::FromString(TEXT("Miracle Elixir"));
		R.EffectDescription = FText::FromString(TEXT("Fully restores HP & TP to all allies and cures ailments."));
		R.RequiredHerbs = 3;
		R.RequiredCrops = 2;
		R.RequiredDemonEssence = 1;
		R.GoldCost = 250;
		AlchemyRecipes.Add(R);
	}

	// Recipe 2: Overlimit Tonic
	{
		FAlchemyRecipe R;
		R.RecipeID = TEXT("Alchemy_OverlimitTonic");
		R.OutputPotionName = FText::FromString(TEXT("Overlimit Burst Draught"));
		R.EffectDescription = FText::FromString(TEXT("Instantly fills 50% of the active hero's Overlimit gauge."));
		R.RequiredHerbs = 2;
		R.RequiredCrops = 4;
		R.RequiredDemonEssence = 2;
		R.GoldCost = 350;
		AlchemyRecipes.Add(R);
	}

	// Recipe 3: Aegis Ward Talisman
	{
		FAlchemyRecipe R;
		R.RecipeID = TEXT("Alchemy_AegisWard");
		R.OutputPotionName = FText::FromString(TEXT("Aegis Protection Talisman"));
		R.EffectDescription = FText::FromString(TEXT("Grants +35% elemental defense against demon black magic."));
		R.RequiredHerbs = 4;
		R.RequiredCrops = 1;
		R.RequiredDemonEssence = 3;
		R.GoldCost = 500;
		AlchemyRecipes.Add(R);
	}

	// Tier 3+ Philosopher's Elixir
	if (WorkshopTier >= EBuildingTier::Tier_3_StoneMasonry)
	{
		FAlchemyRecipe R;
		R.RecipeID = TEXT("Alchemy_PhilosopherElixir");
		R.OutputPotionName = FText::FromString(TEXT("Philosopher's Miracle Elixir"));
		R.EffectDescription = FText::FromString(TEXT("Full HP and TP recovery plus Overlimit surge."));
		R.RequiredHerbs = 5;
		R.RequiredCrops = 3;
		R.RequiredDemonEssence = 4;
		R.GoldCost = 900;
		AlchemyRecipes.Add(R);
	}
}

void AAlchemyWorkshopActor::SetWorkshopTier(EBuildingTier NewTier)
{
	WorkshopTier = NewTier;
	AlchemyRecipes.Empty();
	PopulateDefaultAlchemyRecipes();
}

void AAlchemyWorkshopActor::InteractWithPlayer(APawn* PlayerPawn)
{
	if (!PlayerPawn) return;
	OnAlchemyInteracted.Broadcast(PlayerPawn);
}

bool AAlchemyWorkshopActor::CompoundPotion(FName RecipeID, int32& PlayerGold, int32& PlayerHerbs,
	int32& PlayerCrops, int32& PlayerDemonEssence, FText& OutPotionName)
{
	for (const FAlchemyRecipe& R : AlchemyRecipes)
	{
		if (R.RecipeID == RecipeID)
		{
			if (PlayerGold < R.GoldCost || PlayerHerbs < R.RequiredHerbs ||
				PlayerCrops < R.RequiredCrops || PlayerDemonEssence < R.RequiredDemonEssence)
			{
				return false;
			}

			PlayerGold -= R.GoldCost;
			PlayerHerbs -= R.RequiredHerbs;
			PlayerCrops -= R.RequiredCrops;
			PlayerDemonEssence -= R.RequiredDemonEssence;
			OutPotionName = R.OutputPotionName;

			OnPotionCompounded.Broadcast(RecipeID, OutPotionName);
			return true;
		}
	}

	return false;
}

bool AAlchemyWorkshopActor::PurifyDemonCores(int32 CorruptedCoresIn, int32& OutPurifiedCrystals)
{
	if (CorruptedCoresIn <= 0) return false;

	// 2 corrupted cores yield 1 pure alchemical crystal
	OutPurifiedCrystals = CorruptedCoresIn / 2;
	return OutPurifiedCrystals > 0;
}

void AAlchemyWorkshopActor::OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (APawn* Pawn = Cast<APawn>(OtherActor))
	{
		InteractWithPlayer(Pawn);
	}
}
