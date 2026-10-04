// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IslandWarpPortal.generated.h"

class USphereComponent;
class UStaticMeshComponent;
class AProceduralMagicCircle;

UCLASS(Blueprintable)
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
	TObjectPtr<USphereComponent> TriggerSphere;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Portal")
	TObjectPtr<UStaticMeshComponent> PortalMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	FName DestinationLevel = TEXT("/Game/IsekaiVillage/Maps/Map_Overworld");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	FName ArrivalPlayerStartTag;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	float MaxChargeTime = 2.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	float IdleRotationSpeed = 40.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Portal")
	float MaxRotationSpeed = 280.0f;

	UFUNCTION()
	void OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnTriggerEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);

private:
	UPROPERTY()
	TObjectPtr<AProceduralMagicCircle> CircleVisual;

	float ChargeTime = 0.0f;
	bool bPlayerInside = false;
	bool bHasWarped = false;
};
