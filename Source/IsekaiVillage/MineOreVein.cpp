// Copyright Epic Games, Inc. All Rights Reserved.
#include "MineOreVein.h"
#include "GatherPickup.h"
#include "GatherInventoryComponent.h"
#include "IsekaiVillageCharacter.h"
#include "VillageRuntime.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"
#include "TimerManager.h"

AMineOreVein::AMineOreVein()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	RootComponent = Mesh;
}

bool AMineOreVein::TryMine(AIsekaiVillageCharacter* Character)
{
	if (bDepleted || !Character || !Character->Gather)
	{
		return false;
	}
	if (Character->GetGatherLevel() < RequiredLevel)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange,
				FString::Printf(TEXT("This %s vein needs gather level %d"), *OreId.ToString(), RequiredLevel));
		}
		return true;
	}
	if (!bHitsInitialized)
	{
		InitialHits = HitsLeft > 0 ? HitsLeft : Character->Gather->HitsToMine();
		HitsLeft = Character->Gather->HitsToMine();
		bHitsInitialized = true;
	}
	--HitsLeft;
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 0.8f, FColor::Orange, FString::Printf(TEXT("Mine  %s  %d"), *OreId.ToString(), HitsLeft));
	}
	if (HitsLeft > 0)
	{
		return true;
	}
	const int32 Qty = AVillageRuntime::RollPlayerDrop(Character, OreId, Character->Gather->OreYield());
	if (Qty <= 0)
	{
		HitsLeft = Character->Gather->HitsToMine();
		return true;
	}
	if (UWorld* World = GetWorld())
	{
		AGatherPickup* Drop = World->SpawnActor<AGatherPickup>(GetActorLocation() + FVector(0, 0, 40.0f), FRotator::ZeroRotator);
		if (Drop)
		{
			Drop->SetupAsOre(OreId, Qty);
		}
	}
	if (RespawnSeconds > 0.0f && GetWorld())
	{
		bDepleted = true;
		Mesh->SetVisibility(false, true);
		Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
		GetWorld()->GetTimerManager().SetTimer(RespawnTimerHandle, this, &AMineOreVein::RespawnVein, RespawnSeconds, false);
		return true;
	}
	Destroy();
	return true;
}

void AMineOreVein::RespawnVein()
{
	bDepleted = false;
	bHitsInitialized = false;
	HitsLeft = InitialHits > 0 ? InitialHits : 3;
	if (Mesh)
	{
		Mesh->SetVisibility(true, true);
		Mesh->SetCollisionEnabled(ECollisionEnabled::QueryAndPhysics);
	}
}

void AMineOreVein::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	if (!Mesh->GetStaticMesh())
	{
		if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
		{
			Mesh->SetStaticMesh(Cube);
		}
	}
	if (OreId == TEXT("Iron"))
	{
		Mesh->SetRelativeScale3D(FVector(0.9f, 0.7f, 0.55f));
	}
	else if (OreId == TEXT("Crystal"))
	{
		Mesh->SetRelativeScale3D(FVector(0.55f, 0.55f, 1.1f));
	}
	else
	{
		Mesh->SetRelativeScale3D(FVector(0.7f, 0.7f, 0.45f));
	}
}
