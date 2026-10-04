// Copyright Epic Games, Inc. All Rights Reserved.

#include "TownZone.h"
#include "IsekaiVillageCharacter.h"
#include "Components/BoxComponent.h"
#include "IsekaiVillageTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Misc/PackageName.h"

ATownZone::ATownZone()
{
	PrimaryActorTick.bCanEverTick = false;

	TriggerVolume = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerVolume"));
	RootComponent = TriggerVolume;
	TriggerVolume->SetBoxExtent(FVector(400.0f, 400.0f, 300.0f));
	TriggerVolume->SetCollisionProfileName(TEXT("Trigger"));
	TriggerVolume->SetGenerateOverlapEvents(true);

	TriggerVolume->OnComponentBeginOverlap.AddDynamic(this, &ATownZone::OnOverlapBegin);
	TriggerVolume->OnComponentEndOverlap.AddDynamic(this, &ATownZone::OnOverlapEnd);
}

void ATownZone::BeginPlay()
{
	Super::BeginPlay();
}

void ATownZone::OnOverlapBegin(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex, bool bFromSweep,
	const FHitResult& SweepResult)
{
	if (!OtherActor || !OtherActor->IsA<APawn>()) return;

	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (!PC || OtherActor != PC->GetPawn()) return;

	bPlayerInside = true;
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearTownZone = true;
	}

	if (bAutoTransition)
	{
		TriggerTransition();
	}
	else
	{
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
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearTownZone = false;
	}
}

void ATownZone::TriggerTransition()
{
	if (bTransitionPending) return;
	if (!DestinationZone)
	{
		UE_LOG(LogTemp, Warning, TEXT("ATownZone::TriggerTransition — DestinationZone is NULL on %s"), *GetName());
		return;
	}

	bTransitionPending = true;

	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		GI->PendingEntryPoint = EntryPointOverride != NAME_None ? EntryPointOverride : DestinationZone->EntryPointName;
		GI->PendingZoneName = DestinationZone->ZoneName;
		GI->PendingSpawnPosition = SpawnOffset;
		GI->PendingSpawnRotation = SpawnRotation;
	}

	OnTransitionTriggered.Broadcast(LocationName);

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
		bTransitionPending = false;
	}
}
