// Copyright Epic Games, Inc. All Rights Reserved.
#include "MineShaft.h"
#include "IsekaiVillageCharacter.h"
#include "Components/SphereComponent.h"
#include "Engine/Engine.h"

AMineShaft::AMineShaft()
{
	PrimaryActorTick.bCanEverTick = true;
	Trigger = CreateDefaultSubobject<USphereComponent>(TEXT("Trigger"));
	Trigger->InitSphereRadius(160.0f);
	Trigger->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Trigger->SetCollisionResponseToAllChannels(ECR_Ignore);
	Trigger->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	RootComponent = Trigger;
}

void AMineShaft::BeginPlay()
{
	Super::BeginPlay();
	Trigger->OnComponentBeginOverlap.AddDynamic(this, &AMineShaft::OnBegin);
	Trigger->OnComponentEndOverlap.AddDynamic(this, &AMineShaft::OnEnd);
}

void AMineShaft::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	if (!bInside)
	{
		Charge = FMath::Max(0.0f, Charge - DeltaTime);
		return;
	}
	Charge += DeltaTime;
	if (Charge >= 1.4f)
	{
		Charge = 0.0f;
		if (APawn* Pawn = GetWorld() ? GetWorld()->GetFirstPlayerController()->GetPawn() : nullptr)
		{
			if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(Pawn))
			{
				if (Character->GetGatherLevel() < RequiredLevel)
				{
					if (GEngine)
					{
						GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange,
							FString::Printf(TEXT("%s is sealed until gather level %d"), *Label.ToString(), RequiredLevel));
					}
					return;
				}
				Character->SetActorLocation(Destination);
			}
		}
	}
}

void AMineShaft::OnBegin(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		bInside = true;
	}
}

void AMineShaft::OnEnd(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		bInside = false;
	}
}
