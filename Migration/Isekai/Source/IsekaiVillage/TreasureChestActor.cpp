// Copyright Epic Games, Inc. All Rights Reserved.
// TreasureChestActor.cpp — Implementation of interactive treasure chest and Demon Mimic trap

#include "TreasureChestActor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"

ATreasureChestActor::ATreasureChestActor()
{
	PrimaryActorTick.bCanEverTick = true;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	InteractionBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractionBox"));
	InteractionBox->SetupAttachment(SceneRoot);
	InteractionBox->SetBoxExtent(FVector(100.0f, 100.0f, 75.0f));
	InteractionBox->SetCollisionProfileName(TEXT("Trigger"));

	ChestBaseMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ChestBaseMesh"));
	ChestBaseMesh->SetupAttachment(SceneRoot);

	ChestLidMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ChestLidMesh"));
	ChestLidMesh->SetupAttachment(ChestBaseMesh);
	ChestLidMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 40.0f));
}

void ATreasureChestActor::BeginPlay()
{
	Super::BeginPlay();
}

void ATreasureChestActor::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsAnimatingLid && ChestLidMesh)
	{
		const FRotator CurrentRot = ChestLidMesh->GetRelativeRotation();
		const FRotator NewRot = FMath::RInterpTo(CurrentRot, TargetLidRotation, DeltaTime, 6.0f);
		ChestLidMesh->SetRelativeRotation(NewRot);

		if (FMath::Abs(NewRot.Pitch - TargetLidRotation.Pitch) < 1.0f)
		{
			ChestLidMesh->SetRelativeRotation(TargetLidRotation);
			bIsAnimatingLid = false;
		}
	}
}

bool ATreasureChestActor::OpenChest(AActor* Interactor)
{
	if (bIsOpened) return false;

	if (bIsDemonMimic)
	{
		bIsOpened = true;
		TargetLidRotation = FRotator(-115.0f, 0.0f, 0.0f);
		bIsAnimatingLid = true;

		// Set up Tales Surprise Attack encounter on GameInstance
		if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(UGameplayStatics::GetGameInstance(this)))
		{
			GI->EncounteredEnemyParty = FName("DemonMimic");
			GI->CurrentEncounterAdvantage = EEncounterAdvantage::SurpriseAttack;
			GI->ReturnOverworldPosition = Interactor ? Interactor->GetActorLocation() : GetActorLocation();
			GI->ReturnOverworldRotation = Interactor ? Interactor->GetActorRotation() : GetActorRotation();
		}

		// Ambush! Awakens the demon mimic!
		OnMimicTriggered.Broadcast(this);
		return true;
	}

	if (bIsLocked)
	{
		// Chest is locked with a key mechanism
		return false;
	}

	bIsOpened = true;
	TargetLidRotation = FRotator(-105.0f, 0.0f, 0.0f);
	bIsAnimatingLid = true;

	OnChestOpened.Broadcast(GoldReward, ItemRewardID, ItemQuantity);
	return true;
}
