// Copyright Epic Games, Inc. All Rights Reserved.
// DungeonPuzzleGateActor.cpp — Implementation of elemental puzzle barrier gate

#include "DungeonPuzzleGateActor.h"
#include "SorcerersRingProjectile.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"

ADungeonPuzzleGateActor::ADungeonPuzzleGateActor()
{
	PrimaryActorTick.bCanEverTick = true;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	GateCollision = CreateDefaultSubobject<UBoxComponent>(TEXT("GateCollision"));
	GateCollision->SetupAttachment(SceneRoot);
	GateCollision->SetBoxExtent(FVector(60.0f, 250.0f, 250.0f));
	GateCollision->SetCollisionProfileName(TEXT("BlockAll"));
	GateCollision->SetGenerateOverlapEvents(true);

	GateMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("GateMesh"));
	GateMesh->SetupAttachment(GateCollision);

	ElementalRuneMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ElementalRuneMesh"));
	ElementalRuneMesh->SetupAttachment(GateMesh);
	ElementalRuneMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void ADungeonPuzzleGateActor::BeginPlay()
{
	Super::BeginPlay();

	ClosedLocation = GetActorLocation();
	TargetLocation = ClosedLocation + OpenedDisplacement;

	if (GateCollision)
	{
		GateCollision->OnComponentBeginOverlap.AddDynamic(this, &ADungeonPuzzleGateActor::OnGateOverlap);
	}
}

void ADungeonPuzzleGateActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsAnimatingOpen)
	{
		const FVector CurrentLoc = GetActorLocation();
		const FVector NewLoc = FMath::VInterpTo(CurrentLoc, TargetLocation, DeltaTime, OpenSpeed);
		SetActorLocation(NewLoc);

		if (FVector::DistSquared(NewLoc, TargetLocation) < 4.0f)
		{
			SetActorLocation(TargetLocation);
			bIsAnimatingOpen = false;
			if (GateCollision)
			{
				GateCollision->SetCollisionEnabled(ECollisionEnabled::NoCollision);
			}
		}
	}
}

bool ADungeonPuzzleGateActor::TryUnlockWithElement(EElement InElement)
{
	if (bIsUnlocked) return false;

	if (InElement == RequiredElement || InElement == EElement::Holy)
	{
		bIsUnlocked = true;
		bIsAnimatingOpen = true;

		if (ElementalRuneMesh)
		{
			ElementalRuneMesh->SetVisibility(false);
		}

		OnGateUnlocked.Broadcast(this);
		return true;
	}

	return false;
}

void ADungeonPuzzleGateActor::OnGateOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (!OtherActor || bIsUnlocked) return;

	if (OtherActor->IsA(ASorcerersRingProjectile::StaticClass()))
	{
		// Sorcerer's Ring energy beam triggers the elemental reaction
		TryUnlockWithElement(RequiredElement);
	}
}
