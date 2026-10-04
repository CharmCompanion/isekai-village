// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IsekaiVillageTypes.h"
#include "TownZone.generated.h"

class UBoxComponent;

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ATownZone : public AActor
{
	GENERATED_BODY()

public:
	ATownZone();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Zone")
	UBoxComponent* TriggerVolume;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	UWorldZoneData* DestinationZone;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FText LocationName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FName EntryPointOverride;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FVector SpawnOffset = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FRotator SpawnRotation = FRotator::ZeroRotator;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	bool bAutoTransition = false;

	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTransitionTriggered, const FText&, LocName);
	UPROPERTY(BlueprintAssignable, Category = "Zone")
	FOnTransitionTriggered OnTransitionTriggered;

	UFUNCTION(BlueprintCallable, Category = "Zone")
	void TriggerTransition();

	UFUNCTION(BlueprintPure, Category = "Zone")
	bool IsPlayerInside() const { return bPlayerInside; }

private:
	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex, bool bFromSweep,
		const FHitResult& SweepResult);

	UFUNCTION()
	void OnOverlapEnd(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComponent, int32 OtherBodyIndex);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Zone", meta = (AllowPrivateAccess = "true"))
	bool bPlayerInside = false;

	bool bTransitionPending = false;
};
