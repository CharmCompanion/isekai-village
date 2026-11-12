// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GatherPickup.generated.h"

class USphereComponent;
class UStaticMeshComponent;

UCLASS()
class ISEKAIVILLAGE_API AGatherPickup : public AActor
{
	GENERATED_BODY()

public:
	AGatherPickup();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Gather")
	TObjectPtr<USphereComponent> Grab;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Gather")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gather")
	FName ItemId = TEXT("Wood");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gather")
	int32 Amount = 1;

	void SetupAsLog(int32 InAmount);
	void SetupAsOre(FName InItem, int32 InAmount);

	UFUNCTION()
	void OnGrab(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	float Age = 0.0f;
	bool bCollected = false;
};
