// Copyright IsekaiVillage. Orbiting defensive shield.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "IsekaiVillageTypes.h"
#include "OrbitShield.generated.h"

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AOrbitShield : public AActor
{
	GENERATED_BODY()

public:
	AOrbitShield();
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	USphereComponent* ShieldSphere;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	UStaticMeshComponent* ShieldMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float OrbitRadius = 120.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float OrbitSpeedDeg = 220.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Lifetime = 6.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float BlockRadius = 70.0f;

	UFUNCTION(BlueprintCallable)
	void InitShield(EElement InElement, float InChargeRatio, AActor* InOwner);

	UFUNCTION()
	void OnShieldOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	EElement ShieldElement = EElement::Fire;
	float ChargeRatio = 0.0f;
	float Age = 0.0f;
	float AngleDeg = 0.0f;
	TWeakObjectPtr<AActor> OwnerActor;
};
