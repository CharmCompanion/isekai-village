// Copyright Epic Games, Inc. All Rights Reserved.
#include "LinchpinProp.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "Engine/Engine.h"

ALinchpinProp::ALinchpinProp()
{
	PrimaryActorTick.bCanEverTick = false;

	Bounds = CreateDefaultSubobject<UBoxComponent>(TEXT("Bounds"));
	Bounds->InitBoxExtent(FVector(50.0f, 50.0f, 50.0f));
	Bounds->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Bounds->SetCollisionResponseToAllChannels(ECR_Overlap);
	Bounds->SetGenerateOverlapEvents(true);
	RootComponent = Bounds;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(RootComponent);
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Mesh->SetCollisionResponseToAllChannels(ECR_Block);

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeFinder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeFinder.Succeeded())
	{
		Mesh->SetStaticMesh(CubeFinder.Object);
	}
}

void ALinchpinProp::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	SetupProp(LinchpinTag);
}

void ALinchpinProp::SetupProp(FName InTag)
{
	LinchpinTag = InTag;
	if (LinchpinTag == TEXT("Anvil"))
	{
		DisplayName = FText::FromString(TEXT("Smith's Anvil"));
		AssociatedFunction = ERoomFunction::Blacksmith;
	}
	else if (LinchpinTag == TEXT("Forge"))
	{
		DisplayName = FText::FromString(TEXT("Blast Furnace"));
		AssociatedFunction = ERoomFunction::Blacksmith;
	}
	else if (LinchpinTag == TEXT("Bed"))
	{
		DisplayName = FText::FromString(TEXT("Comfortable Bed"));
		AssociatedFunction = ERoomFunction::Inn;
	}
	else if (LinchpinTag == TEXT("Counter"))
	{
		DisplayName = FText::FromString(TEXT("Merchant Counter"));
		AssociatedFunction = ERoomFunction::Shop;
	}
	else if (LinchpinTag == TEXT("Crate"))
	{
		DisplayName = FText::FromString(TEXT("Supply Crate"));
		AssociatedFunction = ERoomFunction::Shop;
	}
	else if (LinchpinTag == TEXT("Desk"))
	{
		DisplayName = FText::FromString(TEXT("Guildmaster Desk"));
		AssociatedFunction = ERoomFunction::AdventurersGuild;
	}
	else if (LinchpinTag == TEXT("Board"))
	{
		DisplayName = FText::FromString(TEXT("Expedition Board"));
		AssociatedFunction = ERoomFunction::AdventurersGuild;
	}
	else if (LinchpinTag == TEXT("Oven"))
	{
		DisplayName = FText::FromString(TEXT("Stone Hearth Oven"));
		AssociatedFunction = ERoomFunction::Bakery;
	}
	else if (LinchpinTag == TEXT("Workbench"))
	{
		DisplayName = FText::FromString(TEXT("Craftsman Workbench"));
		AssociatedFunction = ERoomFunction::Farmhouse;
	}
	else if (LinchpinTag == TEXT("Chest"))
	{
		DisplayName = FText::FromString(TEXT("Reinforced Chest"));
		AssociatedFunction = ERoomFunction::Treasure;
	}
	else if (LinchpinTag == TEXT("Cauldron"))
	{
		DisplayName = FText::FromString(TEXT("Alchemist Cauldron"));
		AssociatedFunction = ERoomFunction::AlchemistLab;
	}
	else if (LinchpinTag == TEXT("HerbRack"))
	{
		DisplayName = FText::FromString(TEXT("Drying Herb Rack"));
		AssociatedFunction = ERoomFunction::AlchemistLab;
	}
	else if (LinchpinTag == TEXT("ArcaneTable"))
	{
		DisplayName = FText::FromString(TEXT("Enchanter's Arcane Table"));
		AssociatedFunction = ERoomFunction::Enchanter;
	}
	else if (LinchpinTag == TEXT("CrystalFocus"))
	{
		DisplayName = FText::FromString(TEXT("Resonant Crystal Focus"));
		AssociatedFunction = ERoomFunction::Enchanter;
	}
	else if (LinchpinTag == TEXT("CelestialAnvil"))
	{
		DisplayName = FText::FromString(TEXT("Celestial Core Anvil"));
		AssociatedFunction = ERoomFunction::ArcaneForge;
	}
	else if (LinchpinTag == TEXT("RunicCrucible"))
	{
		DisplayName = FText::FromString(TEXT("Runic Star Crucible"));
		AssociatedFunction = ERoomFunction::ArcaneForge;
	}
	else
	{
		DisplayName = FText::FromString(InTag.ToString());
		AssociatedFunction = ERoomFunction::EmptyHall;
	}

	ApplyTagVisual();
}

void ALinchpinProp::ApplyTagVisual()
{
	FVector Scale(0.7f, 0.7f, 0.7f);
	FLinearColor Tint = FLinearColor::White;

	if (LinchpinTag == TEXT("Anvil"))
	{
		Scale = FVector(0.9f, 0.55f, 0.45f);
		Tint = FLinearColor(0.25f, 0.26f, 0.30f);
	}
	else if (LinchpinTag == TEXT("Forge"))
	{
		Scale = FVector(1.1f, 0.85f, 0.95f);
		Tint = FLinearColor(0.35f, 0.22f, 0.18f);
	}
	else if (LinchpinTag == TEXT("Bed"))
	{
		Scale = FVector(1.6f, 0.85f, 0.38f);
		Tint = FLinearColor(0.75f, 0.35f, 0.35f);
	}
	else if (LinchpinTag == TEXT("Counter"))
	{
		Scale = FVector(1.4f, 0.45f, 0.75f);
		Tint = FLinearColor(0.50f, 0.32f, 0.18f);
	}
	else if (LinchpinTag == TEXT("Crate"))
	{
		Scale = FVector(0.55f, 0.55f, 0.55f);
		Tint = FLinearColor(0.45f, 0.30f, 0.15f);
	}
	else if (LinchpinTag == TEXT("Desk"))
	{
		Scale = FVector(1.5f, 0.7f, 0.65f);
		Tint = FLinearColor(0.38f, 0.22f, 0.12f);
	}
	else if (LinchpinTag == TEXT("Board"))
	{
		Scale = FVector(0.15f, 1.4f, 1.1f);
		Tint = FLinearColor(0.55f, 0.42f, 0.28f);
	}
	else if (LinchpinTag == TEXT("Oven"))
	{
		Scale = FVector(1.1f, 1.0f, 0.9f);
		Tint = FLinearColor(0.65f, 0.35f, 0.25f);
	}
	else if (LinchpinTag == TEXT("Workbench"))
	{
		Scale = FVector(1.3f, 0.7f, 0.6f);
		Tint = FLinearColor(0.52f, 0.38f, 0.20f);
	}
	else if (LinchpinTag == TEXT("Chest"))
	{
		Scale = FVector(0.9f, 0.6f, 0.5f);
		Tint = FLinearColor(0.40f, 0.28f, 0.15f);
	}
	else if (LinchpinTag == TEXT("Cauldron"))
	{
		Scale = FVector(0.85f, 0.85f, 0.75f);
		Tint = FLinearColor(0.18f, 0.45f, 0.25f);
	}
	else if (LinchpinTag == TEXT("HerbRack"))
	{
		Scale = FVector(0.35f, 1.2f, 1.1f);
		Tint = FLinearColor(0.35f, 0.55f, 0.25f);
	}
	else if (LinchpinTag == TEXT("ArcaneTable"))
	{
		Scale = FVector(1.4f, 0.8f, 0.75f);
		Tint = FLinearColor(0.25f, 0.20f, 0.65f);
	}
	else if (LinchpinTag == TEXT("CrystalFocus"))
	{
		Scale = FVector(0.45f, 0.45f, 1.25f);
		Tint = FLinearColor(0.45f, 0.75f, 1.0f);
	}
	else if (LinchpinTag == TEXT("CelestialAnvil"))
	{
		Scale = FVector(1.1f, 0.75f, 0.65f);
		Tint = FLinearColor(1.0f, 0.85f, 0.35f);
	}
	else if (LinchpinTag == TEXT("RunicCrucible"))
	{
		Scale = FVector(1.2f, 1.2f, 1.0f);
		Tint = FLinearColor(0.85f, 0.30f, 0.85f);
	}

	Mesh->SetRelativeScale3D(Scale);
	Bounds->SetBoxExtent(Scale * 50.0f + FVector(15.0f, 15.0f, 15.0f));

	if (UMaterialInterface* BaseMat = Mesh->GetMaterial(0))
	{
		UMaterialInstanceDynamic* DynMat = Mesh->CreateAndSetMaterialInstanceDynamic(0);
		if (DynMat)
		{
			DynMat->SetVectorParameterValue(TEXT("Color"), Tint);
			DynMat->SetVectorParameterValue(TEXT("BaseColor"), Tint);
		}
	}
}

FText ALinchpinProp::GetStationHint() const
{
	if (LinchpinTag == TEXT("Anvil") || LinchpinTag == TEXT("Forge"))
	{
		return FText::FromString(TEXT("Press [F] to Forge Upgrades"));
	}
	if (LinchpinTag == TEXT("Bed"))
	{
		return FText::FromString(TEXT("Press [F] to Rest & Replenish"));
	}
	if (LinchpinTag == TEXT("Counter"))
	{
		return FText::FromString(TEXT("Press [F] to Trade"));
	}
	if (LinchpinTag == TEXT("Oven") || LinchpinTag == TEXT("Workbench"))
	{
		return FText::FromString(TEXT("Press [F] to Craft Supplies"));
	}
	if (LinchpinTag == TEXT("Chest"))
	{
		return FText::FromString(TEXT("Press [F] to Open Storage"));
	}
	return FText::FromString(TEXT("Press [F] to Inspect"));
}

bool ALinchpinProp::TryInteract(AIsekaiVillageCharacter* Character)
{
	if (!Character)
	{
		return false;
	}

	if (LinchpinTag == TEXT("Anvil") || LinchpinTag == TEXT("Forge"))
	{
		if (Character->Gather && Character->Gather->TryForgeUpgrades())
		{
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Orange, TEXT("Blacksmithing: Tool forged to next tier!"));
			}
			return true;
		}
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow, TEXT("Blacksmithing: Need more Ore/Wood to upgrade tools."));
		}
		return true;
	}

	if (LinchpinTag == TEXT("Bed"))
	{
		Character->CurrentHP = Character->MaxHP;
		Character->CurrentTP = Character->MaxTP;
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Emerald, TEXT("Rested in bed! HP & Arte TP completely restored."));
		}
		return true;
	}

	if (LinchpinTag == TEXT("Counter"))
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan, TEXT("Trading post active: Golem merchant standing by."));
		}
		return true;
	}

	if (LinchpinTag == TEXT("Oven"))
	{
		if (Character->Gather)
		{
			Character->Gather->AddItem(TEXT("Bread"), 1);
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("Baked 1 fresh travel bread from the hearth oven!"));
			}
			return true;
		}
	}

	if (LinchpinTag == TEXT("Workbench"))
	{
		if (Character->Gather && Character->Gather->GetCount(TEXT("Wood")) >= 2)
		{
			Character->Gather->Consume(TEXT("Wood"), 2);
			Character->Gather->AddItem(TEXT("ToolParts"), 1);
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Green, TEXT("Crafted 1 ToolParts at the carpenter workbench!"));
			}
			return true;
		}
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow, TEXT("Workbench: Need 2 Wood to craft ToolParts."));
		}
		return true;
	}

	if (LinchpinTag == TEXT("Cauldron") || LinchpinTag == TEXT("HerbRack"))
	{
		Character->RestoreHP(35.0f);
		Character->RestoreTP(20.0f);
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Green, TEXT("Alchemist Lab: Drank soothing botanical tonic (+35 HP, +20 TP)!"));
		}
		return true;
	}

	if (LinchpinTag == TEXT("ArcaneTable") || LinchpinTag == TEXT("CrystalFocus"))
	{
		Character->RestoreTP(Character->MaxTP);
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Magenta, TEXT("Enchanter Spire: Runic resonance fully recharged Arte TP!"));
		}
		return true;
	}

	if (LinchpinTag == TEXT("CelestialAnvil") || LinchpinTag == TEXT("RunicCrucible"))
	{
		if (Character->Gather && Character->Gather->TryForgeUpgrades())
		{
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Yellow, TEXT("Celestial Forge: Legendary weapon harmonic infusion forged!"));
			}
			return true;
		}
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Yellow, TEXT("Celestial Forge: Stand ready to forge endgame weapons with Crystals & Ore."));
		}
		return true;
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::White, FString::Printf(TEXT("Inspected %s."), *DisplayName.ToString()));
	}
	return true;
}
