// Copyright Epic Games, Inc. All Rights Reserved.
#include "LakeFishingSpot.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "VillageRuntime.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "TimerManager.h"

ALakeFishingSpot::ALakeFishingSpot()
{
	PrimaryActorTick.bCanEverTick = false;

	InteractSphere = CreateDefaultSubobject<USphereComponent>(TEXT("InteractSphere"));
	InteractSphere->InitSphereRadius(260.0f);
	InteractSphere->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	InteractSphere->SetCollisionResponseToAllChannels(ECR_Ignore);
	InteractSphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	InteractSphere->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
	RootComponent = InteractSphere;

	BuoyMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BuoyMesh"));
	BuoyMesh->SetupAttachment(RootComponent);
	BuoyMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	BuoyMesh->SetRelativeScale3D(FVector(0.65f, 0.65f, 0.9f));
	BuoyMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 35.0f));
	if (UStaticMesh* Cyl = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
	{
		BuoyMesh->SetStaticMesh(Cyl);
	}
}

bool ALakeFishingSpot::TryFish(AIsekaiVillageCharacter* Character)
{
	if (!Character || !Character->Gather)
	{
		return false;
	}
	if (CatchesRemaining <= 0)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan,
				FString::Printf(TEXT("%s is quiet right now — wait a moment for fish to return."), *SpotTitle));
		}
		if (UWorld* World = GetWorld(); World && RestockSeconds > 0.0f && !World->GetTimerManager().IsTimerActive(RestockTimer))
		{
			World->GetTimerManager().SetTimer(RestockTimer, this, &ALakeFishingSpot::ReplenishSpot, RestockSeconds, false);
		}
		return true;
	}

	const int32 NeedCasts = Character->GetGatherLevel() >= 3 ? 1 : 2;
	++CastsOnCurrentFish;
	if (CastsOnCurrentFish < NeedCasts)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 1.2f, FColor::Cyan,
				FString::Printf(TEXT("%s: float bobbed! Reel once more..."), *SpotTitle));
		}
		return true;
	}

	CastsOnCurrentFish = 0;
	--CatchesRemaining;
	const int32 BaseCatch = 1 + (Character->SphereYieldBonus > 0 ? 1 : 0);
	const int32 Yield = FMath::Max(1, AVillageRuntime::RollPlayerDrop(Character, TEXT("Fish"), BaseCatch));
	Character->Gather->AddItem(TEXT("Fish"), Yield);

	if (CatchesRemaining <= 0 && GetWorld() && RestockSeconds > 0.0f)
	{
		GetWorld()->GetTimerManager().SetTimer(RestockTimer, this, &ALakeFishingSpot::ReplenishSpot, RestockSeconds, false);
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.4f, FColor::Cyan,
			FString::Printf(TEXT("Caught %d Fish at %s! (%d left)"), Yield, *SpotTitle, CatchesRemaining));
	}
	return true;
}

void ALakeFishingSpot::ReplenishSpot()
{
	CatchesRemaining = FMath::Max(1, MaxCatchesPerRestock);
	CastsOnCurrentFish = 0;
}
