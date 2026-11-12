// Copyright Epic Games, Inc. All Rights Reserved.
#include "DayBoard.h"
#include "IsekaiVillageCharacter.h"
#include "VillageRuntime.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"

ADayBoard::ADayBoard()
{
	PrimaryActorTick.bCanEverTick = false;

	InteractBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractBox"));
	InteractBox->InitBoxExtent(FVector(200.0f, 200.0f, 120.0f));
	InteractBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	InteractBox->SetCollisionResponseToAllChannels(ECR_Ignore);
	InteractBox->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	RootComponent = InteractBox;

	PostMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PostMesh"));
	PostMesh->SetupAttachment(RootComponent);
	PostMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	PostMesh->SetRelativeScale3D(FVector(0.35f, 1.1f, 1.8f));
	PostMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 80.0f));
}

void ADayBoard::BeginPlay()
{
	Super::BeginPlay();
	if (!PostMesh->GetStaticMesh())
	{
		if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
		{
			PostMesh->SetStaticMesh(Cube);
		}
	}
	InteractBox->OnComponentBeginOverlap.AddDynamic(this, &ADayBoard::OnBeginOverlap);
	InteractBox->OnComponentEndOverlap.AddDynamic(this, &ADayBoard::OnEndOverlap);
}

bool ADayBoard::TryUse(AIsekaiVillageCharacter* Character)
{
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			return It->TryBoard(Character);
		}
	}
	return false;
}

void ADayBoard::OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearDayBoard = true;
	}
}

void ADayBoard::OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearDayBoard = false;
	}
}
