// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IsekaiVillageTypes.h"
#include "IslandWarpPortal.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class UMaterialInstanceDynamic;

/**
 * A portal/magic circle that spins up and gets brighter when the player stands on it,
 * eventually warping them to the destination zone.
 */
UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AIslandWarpPortal : public AActor
{
	GENERATED_BODY()

public:
	AIslandWarpPortal();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Portal")
	USceneComponent* RootScene;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Portal")
	UBoxComponent* TriggerVolume;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Portal")
	UStaticMeshComponent* PortalMesh;

	/** The zone to transition to when the portal is fully charged */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	UWorldZoneData* DestinationZone;

	/** How long the player must stand on the portal to warp (in seconds) */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	float MaxChargeTime = 2.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Portal")
	float CurrentCharge = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Portal")
	bool bIsCharging = false;

	/** Idle rotation speed of the portal mesh */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	float BaseRotationSpeed = 30.0f;

	/** Fast rotation speed of the portal mesh when fully charged */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	float MaxRotationSpeed = 400.0f;

	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnOverlapEnd(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

private:
	UPROPERTY()
	UMaterialInstanceDynamic* PortalMaterial;
};
