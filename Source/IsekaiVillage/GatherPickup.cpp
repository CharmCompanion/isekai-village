// Copyright Epic Games, Inc. All Rights Reserved.
#include "GatherPickup.h"
#include "GatherInventoryComponent.h"
#include "IsekaiVillageCharacter.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"

AGatherPickup::AGatherPickup()
{
	PrimaryActorTick.bCanEverTick = true;
	Grab = CreateDefaultSubobject<USphereComponent>(TEXT("Grab"));
	Grab->InitSphereRadius(90.0f);
	Grab->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Grab->SetCollisionResponseToAllChannels(ECR_Ignore);
	Grab->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	Grab->SetGenerateOverlapEvents(true);
	RootComponent = Grab;

	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetupAttachment(RootComponent);
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void AGatherPickup::BeginPlay()
{
	Super::BeginPlay();
	Grab->OnComponentBeginOverlap.AddDynamic(this, &AGatherPickup::OnGrab);
}

void AGatherPickup::SetupAsLog(int32 InAmount)
{
	ItemId = TEXT("Wood");
	Amount = FMath::Max(1, InAmount);
	if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
	{
		Mesh->SetStaticMesh(Cube);
	}
	Mesh->SetRelativeScale3D(FVector(0.35f, 0.35f, 1.1f));
	Mesh->SetRelativeRotation(FRotator(0.0f, 0.0f, 90.0f));
}

void AGatherPickup::SetupAsOre(FName InItem, int32 InAmount)
{
	ItemId = InItem;
	Amount = FMath::Max(1, InAmount);
	if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
	{
		Mesh->SetStaticMesh(Cube);
	}
	Mesh->SetRelativeScale3D(FVector(0.28f, 0.28f, 0.22f));
}

void AGatherPickup::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	Age += DeltaTime;
	AddActorWorldOffset(FVector(0, 0, FMath::Sin(Age * 4.0f) * 8.0f * DeltaTime));
	AddActorWorldRotation(FRotator(0, 80.0f * DeltaTime, 0));
	if (Age > 0.35f && !bCollected)
	{
		if (APawn* Pawn = GetWorld() ? GetWorld()->GetFirstPlayerController() ? GetWorld()->GetFirstPlayerController()->GetPawn() : nullptr : nullptr)
		{
			if (FVector::Dist(Pawn->GetActorLocation(), GetActorLocation()) < 160.0f)
			{
				OnGrab(nullptr, Pawn, nullptr, 0, false, FHitResult());
			}
		}
	}
}

void AGatherPickup::OnGrab(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (bCollected)
	{
		return;
	}
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor);
	if (!Character || !Character->Gather)
	{
		return;
	}
	bCollected = true;
	Character->Gather->AddItem(ItemId, Amount);
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 1.6f, FColor::Green, FString::Printf(TEXT("+%d %s"), Amount, *ItemId.ToString()));
	}
	Destroy();
}
