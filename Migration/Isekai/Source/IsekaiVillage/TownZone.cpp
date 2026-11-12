// Copyright Epic Games, Inc. All Rights Reserved.

#include "TownZone.h"
#include "Components/BoxComponent.h"
#include "IsekaiVillageTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/Engine.h"

ATownZone::ATownZone()
{
	PrimaryActorTick.bCanEverTick = false;

	// Root is the trigger volume
	TriggerVolume = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerVolume"));
	RootComponent = TriggerVolume;
	TriggerVolume->SetBoxExtent(FVector(400.0f, 400.0f, 300.0f));
	TriggerVolume->SetCollisionProfileName(TEXT("Trigger"));
	TriggerVolume->SetGenerateOverlapEvents(true);

	// Bind overlap events
	TriggerVolume->OnComponentBeginOverlap.AddDynamic(this, &ATownZone::OnOverlapBegin);
	TriggerVolume->OnComponentEndOverlap.AddDynamic(this, &ATownZone::OnOverlapEnd);
}

void ATownZone::BeginPlay()
{
	Super::BeginPlay();
}

// ── Overlap Handling ───────────────────────────────────────

void ATownZone::OnOverlapBegin(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex, bool bFromSweep,
	const FHitResult& SweepResult)
{
	if (!OtherActor || !OtherActor->IsA<APawn>()) return;

	// Only react to the player pawn
	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (!PC || OtherActor != PC->GetPawn()) return;

	bPlayerInside = true;

	if (bAutoTransition)
	{
		TriggerTransition();
	}
	else
	{
		// Notify HUD / interaction prompt system
		// The player needs to press Interact to enter
		OnTransitionTriggered.Broadcast(LocationName);
	}
}

void ATownZone::OnOverlapEnd(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex)
{
	if (!OtherActor || !OtherActor->IsA<APawn>()) return;

	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (!PC || OtherActor != PC->GetPawn()) return;

	bPlayerInside = false;
}

// ── Transition ─────────────────────────────────────────────

void ATownZone::TriggerTransition()
{
	if (bTransitionPending) return;
	if (!DestinationZone)
	{
		UE_LOG(LogTemp, Warning, TEXT("ATownZone::TriggerTransition — DestinationZone is NULL on %s!"), *GetName());
		return;
	}

	bTransitionPending = true;

	// Store transition data in GameInstance
	UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance());
	if (GI)
	{
		GI->PendingEntryPoint = EntryPointOverride != NAME_None ? EntryPointOverride : DestinationZone->EntryPointName;
		GI->PendingZoneName = DestinationZone->ZoneName;
		GI->PendingSpawnPosition = SpawnOffset;
		GI->PendingSpawnRotation = SpawnRotation;
	}

	// Broadcast event (for UI fade-out, etc.)
	OnTransitionTriggered.Broadcast(LocationName);

	// Load the destination map using clean level name
	FString LevelName = DestinationZone->MapToLoad.ToSoftObjectPath().GetAssetName();
	if (LevelName.IsEmpty())
	{
		LevelName = FPackageName::GetShortName(DestinationZone->MapToLoad.GetLongPackageName());
	}

	if (!LevelName.IsEmpty())
	{
		UGameplayStatics::OpenLevel(this, FName(*LevelName));
	}
	else if (!DestinationZone->MapToLoad.IsNull())
	{
		UGameplayStatics::OpenLevelBySoftObjectPtr(this, DestinationZone->MapToLoad);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("ATownZone::TriggerTransition — DestinationZone has no map set!"));
		bTransitionPending = false;
	}
}

