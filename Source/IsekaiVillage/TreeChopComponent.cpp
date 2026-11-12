// Copyright Epic Games, Inc. All Rights Reserved.
#include "TreeChopComponent.h"
#include "GatherInventoryComponent.h"
#include "FallingTree.h"
#include "IsekaiVillageCharacter.h"
#include "VillageRuntime.h"
#include "InstancedFoliageActor.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "GameFramework/PlayerController.h"

UTreeChopComponent::UTreeChopComponent()
{
	PrimaryComponentTick.bCanEverTick = false;
}

bool UTreeChopComponent::IsTreeMesh(const FString& Name) const
{
	const FString N = Name.ToLower();
	return N.Contains(TEXT("tree")) || N.Contains(TEXT("oak")) || N.Contains(TEXT("pine"))
		|| N.Contains(TEXT("palm")) || N.Contains(TEXT("fir")) || N.Contains(TEXT("birch"))
		|| N.Contains(TEXT("cypress")) || N.Contains(TEXT("spruce"));
}

FString UTreeChopComponent::MakeHitKey(const FString& OwnerPath, const FVector& Loc) const
{
	return FString::Printf(TEXT("%s_%.0f_%.0f_%.0f"), *OwnerPath, Loc.X, Loc.Y, Loc.Z);
}

bool UTreeChopComponent::RegisterHit(AIsekaiVillageCharacter* Character, const FString& HitKey)
{
	const int32 Need = Character->Gather->HitsToChop();
	int32& Left = HitsLeft.FindOrAdd(HitKey, Need);
	--Left;
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 0.8f, FColor::Yellow, FString::Printf(TEXT("Chop  %d"), FMath::Max(0, Left)));
	}
	if (Left > 0)
	{
		return false;
	}
	HitsLeft.Remove(HitKey);
	return true;
}

void UTreeChopComponent::SpawnFall(UWorld* World, UStaticMesh* SourceMesh, const FTransform& Xform, int32 WoodAmount)
{
	AFallingTree* Fall = World->SpawnActor<AFallingTree>(Xform.GetLocation(), Xform.GetRotation().Rotator());
	if (Fall)
	{
		Fall->StartFall(SourceMesh, Xform, WoodAmount);
	}
}

bool UTreeChopComponent::TryChopNearestFoliage(AIsekaiVillageCharacter* Character)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return false;
	}

	const FVector Origin = Character->GetActorLocation();
	const float Radius = Character->bSphereSkillHunt ? 480.0f : 320.0f;
	float BestDistSq = Radius * Radius;
	UInstancedStaticMeshComponent* BestISM = nullptr;
	int32 BestIndex = INDEX_NONE;
	FTransform BestXform;
	UStaticMesh* BestMesh = nullptr;

	for (TActorIterator<AInstancedFoliageActor> It(World); It; ++It)
	{
		TArray<UInstancedStaticMeshComponent*> Comps;
		It->GetComponents<UInstancedStaticMeshComponent>(Comps);
		for (UInstancedStaticMeshComponent* ISM : Comps)
		{
			UStaticMesh* SM = ISM->GetStaticMesh();
			if (!SM || !IsTreeMesh(SM->GetName()))
			{
				continue;
			}
			const TArray<int32> Ids = ISM->GetInstancesOverlappingSphere(Origin, Radius, true);
			for (const int32 Index : Ids)
			{
				FTransform Xform;
				if (!ISM->GetInstanceTransform(Index, Xform, true))
				{
					continue;
				}
				const float DistSq = FVector::DistSquared(Origin, Xform.GetLocation());
				if (DistSq < BestDistSq)
				{
					BestDistSq = DistSq;
					BestISM = ISM;
					BestIndex = Index;
					BestXform = Xform;
					BestMesh = SM;
				}
			}
		}
	}

	if (!BestISM || BestIndex == INDEX_NONE)
	{
		return false;
	}

	const FString HitKey = MakeHitKey(BestISM->GetPathName(), BestXform.GetLocation());
	if (!RegisterHit(Character, HitKey))
	{
		return true;
	}
	BestISM->RemoveInstance(BestIndex);
	SpawnFall(World, BestMesh, BestXform, AVillageRuntime::RollPlayerDrop(Character, TEXT("Wood"), Character->Gather->WoodYield()));
	return true;
}

bool UTreeChopComponent::TryChop()
{
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner());
	UWorld* World = GetWorld();
	if (!Character || !Character->Gather || !World)
	{
		return false;
	}

	FVector Start = Character->GetActorLocation() + FVector(0, 0, 40.0f);
	FVector End = Start + Character->GetActorForwardVector() * (Character->bSphereSkillHunt ? 420.0f : 280.0f);
	if (APlayerController* PC = Cast<APlayerController>(Character->GetController()))
	{
		FVector ViewLoc;
		FRotator ViewRot;
		PC->GetPlayerViewPoint(ViewLoc, ViewRot);
		Start = ViewLoc;
		End = ViewLoc + ViewRot.Vector() * 900.0f;
	}

	FHitResult Hit;
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(Character);
	if (World->LineTraceSingleByChannel(Hit, Start, End, ECC_Visibility, Params))
	{
		if (UInstancedStaticMeshComponent* ISM = Cast<UInstancedStaticMeshComponent>(Hit.GetComponent()))
		{
			UStaticMesh* SourceMesh = ISM->GetStaticMesh();
			if (SourceMesh && IsTreeMesh(SourceMesh->GetName()))
			{
				FTransform Xform = FTransform(Hit.ImpactPoint);
				const int32 Index = Hit.Item;
				if (Index >= 0)
				{
					ISM->GetInstanceTransform(Index, Xform, true);
				}
				const FString HitKey = MakeHitKey(ISM->GetPathName(), Xform.GetLocation());
				if (!RegisterHit(Character, HitKey))
				{
					return true;
				}
				if (Index >= 0)
				{
					ISM->RemoveInstance(Index);
				}
				SpawnFall(World, SourceMesh, Xform, AVillageRuntime::RollPlayerDrop(Character, TEXT("Wood"), Character->Gather->WoodYield()));
				return true;
			}
		}
		else if (AStaticMeshActor* SMA = Cast<AStaticMeshActor>(Hit.GetActor()))
		{
			UStaticMesh* SourceMesh = nullptr;
			if (UStaticMeshComponent* SMC = SMA->GetStaticMeshComponent())
			{
				SourceMesh = SMC->GetStaticMesh();
			}
			if (SourceMesh && IsTreeMesh(SourceMesh->GetName()))
			{
				const FTransform Xform = SMA->GetActorTransform();
				const FString HitKey = MakeHitKey(SMA->GetPathName(), Xform.GetLocation());
				if (!RegisterHit(Character, HitKey))
				{
					return true;
				}
				SMA->Destroy();
				SpawnFall(World, SourceMesh, Xform, AVillageRuntime::RollPlayerDrop(Character, TEXT("Wood"), Character->Gather->WoodYield()));
				return true;
			}
		}
	}

	return TryChopNearestFoliage(Character);
}
