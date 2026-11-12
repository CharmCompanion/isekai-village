// Copyright Epic Games, Inc. All Rights Reserved.
#include "DebrisActor.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "UObject/ConstructorHelpers.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "GatherPickup.h"
#include "Engine/Engine.h"

ADebrisActor::ADebrisActor()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	Mesh->SetCollisionResponseToAllChannels(ECR_Block);
	RootComponent = Mesh;

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeFinder(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeFinder.Succeeded())
	{
		Mesh->SetStaticMesh(CubeFinder.Object);
	}
}

void ADebrisActor::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	SetupDebris(DebrisType);
}

void ADebrisActor::SetupDebris(EDebrisType InType)
{
	DebrisType = InType;
	switch (DebrisType)
	{
	case EDebrisType::CharredTimber:
		YieldAmount = 5;
		SetActorScale3D(FVector(1.4f, 0.45f, 0.35f));
		break;
	case EDebrisType::StoneRubble:
		YieldAmount = 6;
		SetActorScale3D(FVector(0.9f, 0.9f, 0.5f));
		break;
	case EDebrisType::ScrapMetal:
		YieldAmount = 3;
		SetActorScale3D(FVector(0.7f, 0.6f, 0.4f));
		break;
	case EDebrisType::RuinedStructure:
		YieldAmount = 10;
		HitsRemaining = 5;
		SetActorScale3D(FVector(1.8f, 1.8f, 1.2f));
		break;
	}
}

FName ADebrisActor::GetPrimaryLootId() const
{
	if (!CustomDropId.IsNone())
	{
		return CustomDropId;
	}
	switch (DebrisType)
	{
	case EDebrisType::CharredTimber:
		return TEXT("Wood");
	case EDebrisType::StoneRubble:
		return TEXT("Stone");
	case EDebrisType::ScrapMetal:
		return TEXT("Iron");
	case EDebrisType::RuinedStructure:
		return TEXT("Stone");
	}
	return TEXT("Stone");
}

FText ADebrisActor::GetDebrisDisplayName() const
{
	switch (DebrisType)
	{
	case EDebrisType::CharredTimber:
		return FText::FromString(TEXT("Charred Timber"));
	case EDebrisType::StoneRubble:
		return FText::FromString(TEXT("Stone Rubble"));
	case EDebrisType::ScrapMetal:
		return FText::FromString(TEXT("Scrap Metal"));
	case EDebrisType::RuinedStructure:
		return FText::FromString(TEXT("Ruined Structure"));
	}
	return FText::FromString(TEXT("Debris"));
}

bool ADebrisActor::TrySalvage(AIsekaiVillageCharacter* Character)
{
	if (!Character)
	{
		return false;
	}

	--HitsRemaining;

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 0.8f, FColor::Yellow,
			FString::Printf(TEXT("Salvaging %s [%d hits left]"), *GetDebrisDisplayName().ToString(), HitsRemaining));
	}

	if (HitsRemaining > 0)
	{
		return true;
	}

	UWorld* World = GetWorld();
	const FVector SpawnLoc = GetActorLocation() + FVector(0.0f, 0.0f, 40.0f);

	if (DebrisType == EDebrisType::RuinedStructure)
	{
		// Drops a multi-resource bundle
		if (World)
		{
			if (AGatherPickup* WoodDrop = World->SpawnActor<AGatherPickup>(SpawnLoc + FVector(20.0f, 0.0f, 0.0f), FRotator::ZeroRotator))
			{
				WoodDrop->SetupAsLog(6);
			}
			if (AGatherPickup* StoneDrop = World->SpawnActor<AGatherPickup>(SpawnLoc + FVector(-20.0f, 20.0f, 0.0f), FRotator::ZeroRotator))
			{
				StoneDrop->SetupAsOre(TEXT("Stone"), 8);
			}
			if (AGatherPickup* IronDrop = World->SpawnActor<AGatherPickup>(SpawnLoc + FVector(0.0f, -20.0f, 0.0f), FRotator::ZeroRotator))
			{
				IronDrop->SetupAsOre(TEXT("Iron"), 3);
			}
		}
		else if (Character->Gather)
		{
			Character->Gather->AddItem(TEXT("Wood"), 6);
			Character->Gather->AddItem(TEXT("Stone"), 8);
			Character->Gather->AddItem(TEXT("Iron"), 3);
		}
	}
	else
	{
		const FName Loot = GetPrimaryLootId();
		if (World)
		{
			if (AGatherPickup* Drop = World->SpawnActor<AGatherPickup>(SpawnLoc, FRotator::ZeroRotator))
			{
				if (Loot == TEXT("Wood"))
				{
					Drop->SetupAsLog(YieldAmount);
				}
				else
				{
					Drop->SetupAsOre(Loot, YieldAmount);
				}
			}
		}
		else if (Character->Gather)
		{
			Character->Gather->AddItem(Loot, YieldAmount);
		}
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Green,
			FString::Printf(TEXT("Cleared %s! Acquired salvaged building supplies."), *GetDebrisDisplayName().ToString()));
	}

	Destroy();
	return true;
}
