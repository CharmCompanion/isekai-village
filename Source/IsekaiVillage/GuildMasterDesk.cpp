// Copyright Epic Games, Inc. All Rights Reserved.

#include "GuildMasterDesk.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "VillageRuntime.h"
#include "VillageCitizen.h"
#include "EngineUtils.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"

AGuildMasterDesk::AGuildMasterDesk()
{
	PrimaryActorTick.bCanEverTick = false;

	InteractBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractBox"));
	InteractBox->InitBoxExtent(FVector(120.0f, 120.0f, 90.0f));
	InteractBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	InteractBox->SetCollisionResponseToAllChannels(ECR_Ignore);
	InteractBox->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	RootComponent = InteractBox;

	DeskMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DeskMesh"));
	DeskMesh->SetupAttachment(RootComponent);
	DeskMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	DeskMesh->SetRelativeScale3D(FVector(1.6f, 0.8f, 0.7f));
}

void AGuildMasterDesk::BeginPlay()
{
	Super::BeginPlay();

	if (!DeskMesh->GetStaticMesh())
	{
		if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
		{
			DeskMesh->SetStaticMesh(Cube);
		}
	}

	InteractBox->OnComponentBeginOverlap.AddDynamic(this, &AGuildMasterDesk::OnBeginOverlap);
	InteractBox->OnComponentEndOverlap.AddDynamic(this, &AGuildMasterDesk::OnEndOverlap);
}

bool AGuildMasterDesk::TryHire(AIsekaiVillageCharacter* Character)
{
	if (!Character || !Character->PartyReserve)
	{
		return false;
	}

	AVillageRuntime* Village = nullptr;
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			Village = *It;
			break;
		}
	}
	AVillageCitizen* Candidate = Village ? Village->NearestAt(EVillagePlace::Guild, 900.0f) : nullptr;
	if (!Candidate)
	{
		Candidate = Village ? Village->NearestCitizen(GetActorLocation(), 1200.0f) : nullptr;
	}
	if (Candidate && (Candidate->Mind.Job == ECitizenJob::Adventurer || Candidate->Mind.bHasAttack))
	{
		return Candidate->TryPlayerOffer(Character);
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Orange, TEXT("No one at the hall will walk with you yet."));
	}
	return false;
}

void AGuildMasterDesk::OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearGuildMaster = true;
	}
}

void AGuildMasterDesk::OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearGuildMaster = false;
	}
}
