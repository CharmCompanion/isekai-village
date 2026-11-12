// Copyright Epic Games, Inc. All Rights Reserved.
#include "FallingTree.h"
#include "GatherPickup.h"
#include "Components/StaticMeshComponent.h"

AFallingTree::AFallingTree()
{
	PrimaryActorTick.bCanEverTick = true;
	Mesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Mesh"));
	Mesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	RootComponent = Mesh;
}

void AFallingTree::StartFall(UStaticMesh* InMesh, const FTransform& WorldXform, int32 InWoodAmount)
{
	SetActorTransform(WorldXform);
	if (InMesh)
	{
		Mesh->SetStaticMesh(InMesh);
	}
	WoodAmount = FMath::Max(1, InWoodAmount);
	StartRot = GetActorRotation();
	FallAxis = FVector::CrossProduct(GetActorUpVector(), FVector::ForwardVector);
	if (FallAxis.IsNearlyZero())
	{
		FallAxis = FVector::RightVector;
	}
	FallAxis.Normalize();
}

void AFallingTree::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	FallTime += DeltaTime;
	const float T = FMath::Clamp(FallTime / 1.15f, 0.0f, 1.0f);
	const float Ease = T * T;
	const FQuat Tip(FallAxis, FMath::DegreesToRadians(88.0f * Ease));
	SetActorRotation(Tip * StartRot.Quaternion());
	if (!bDropped && FallTime >= 1.15f)
	{
		bDropped = true;
		if (UWorld* World = GetWorld())
		{
			const int32 Logs = FMath::Clamp(WoodAmount, 1, 5);
			for (int32 i = 0; i < Logs; ++i)
			{
				const FVector Offset = GetActorRightVector() * (i * 40.0f - 40.0f) + FVector(0, 0, 30.0f);
				AGatherPickup* Log = World->SpawnActor<AGatherPickup>(GetActorLocation() + Offset, FRotator::ZeroRotator);
				if (Log)
				{
					Log->SetupAsLog(1);
				}
			}
		}
		Destroy();
	}
}
