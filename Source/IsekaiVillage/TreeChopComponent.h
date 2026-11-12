// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TreeChopComponent.generated.h"

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UTreeChopComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UTreeChopComponent();

	UFUNCTION(BlueprintCallable, Category = "Gather")
	bool TryChop();

private:
	bool IsTreeMesh(const FString& Name) const;
	FString MakeHitKey(const FString& OwnerPath, const FVector& Loc) const;
	bool RegisterHit(class AIsekaiVillageCharacter* Character, const FString& HitKey);
	void SpawnFall(UWorld* World, class UStaticMesh* SourceMesh, const FTransform& Xform, int32 WoodAmount);
	bool TryChopNearestFoliage(class AIsekaiVillageCharacter* Character);
	TMap<FString, int32> HitsLeft;
};
