// Copyright Epic Games, Inc. All Rights Reserved.

#include "GuildMasterDesk.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
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

	const bool bHired = Character->PartyReserve->HireAdventurer(FText::FromString(TEXT("Guild Recruit")));
	if (GEngine)
	{
		if (bHired)
		{
			GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Cyan,
				FString::Printf(TEXT("Hired %s  (%d/%d reserve, %d active)"),
					TEXT("Guild Recruit"),
					Character->PartyReserve->Reserve.Num(),
					Character->PartyReserve->MaxReserve,
					Character->PartyReserve->GetActiveCompanionCount()));
		}
		else
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Red, TEXT("Guild roster is full."));
		}
	}
	return bHired;
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
