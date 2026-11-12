// Copyright Epic Games, Inc. All Rights Reserved.
// SorcerersRingProjectile.h — Tales of-style Sorcerer's Ring energy beam for field stun & puzzle interaction

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "SorcerersRingProjectile.generated.h"

class USphereComponent;
class UProjectileMovementComponent;
class UPointLightComponent;
class UStaticMeshComponent;

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ASorcerersRingProjectile : public AActor
{
	GENERATED_BODY()

public:
	ASorcerersRingProjectile();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* CollisionComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UProjectileMovementComponent* MovementComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* OrbMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UPointLightComponent* RingLight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ring")
	float StunDuration = 5.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Ring")
	float ProjectileSpeed = 2200.0f;

	UFUNCTION()
	void OnOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);
};
