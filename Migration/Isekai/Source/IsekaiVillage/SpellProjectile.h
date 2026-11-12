// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/SphereComponent.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "NiagaraComponent.h"
#include "IsekaiVillageTypes.h"
#include "SpellProjectile.generated.h"

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ASpellProjectile : public AActor
{
	GENERATED_BODY()

public:
	ASpellProjectile();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* CollisionComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UProjectileMovementComponent* MovementComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNiagaraComponent* ProjectileVFX;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNiagaraComponent* AuraVFX;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* CoreMeshComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UPointLightComponent* AuraLight;

	UPROPERTY(Transient)
	UMaterialInstanceDynamic* DynamicProjectileMaterial;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	EElement ProjectileElement = EElement::Fire;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	FName ProjectileShape = "spear";

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	float BaseSpeed = 1800.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	float BaseDamage = 30.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	float ChargeRatio = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	int32 BouncesLeft = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	int32 PierceCount = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Projectile")
	bool bHasImpacted = false;

	UFUNCTION(BlueprintCallable, Category = "Projectile")
	void InitProjectile(EElement InElement, FName InShape, float InChargeRatio);

	UFUNCTION(BlueprintCallable, Category = "Projectile")
	void BindSpellVFX(class UNiagaraSystem* System);

	UFUNCTION()
	void OnProjectileHit(UPrimitiveComponent* HitComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit);

	UFUNCTION(BlueprintCallable, Category = "Projectile")
	void HandleImpact(const FHitResult& Hit);

	UFUNCTION(BlueprintImplementableEvent, Category = "Projectile")
	void SpawnImpactFX(FVector Location, FVector Normal);

	UFUNCTION(BlueprintImplementableEvent, Category = "Projectile")
	void SpawnLavaDecal(FVector Location);

private:
	float Lifetime = 8.0f;
	float Age = 0.0f;
	float EmberTimer = 0.0f;
	FLinearColor CachedElementColor = FLinearColor::White;

	void ApplyElementalPhysics();
	void ApplyElementalPresentation();
	void ForceProjectileSilhouette(UStaticMesh* ConeMesh, UStaticMesh* CylMesh, UStaticMesh* SphereMesh, float Scale);
	void UpdateElementalLight(float DeltaTime);
	void SpawnElementEmberTrail(float DeltaTime);
	void TrackHomingTarget(float DeltaTime);
	void PullNearbyTargets(float DeltaTime);

	static FLinearColor GetElementColor(EElement Element);
	static UNiagaraSystem* LoadElementTrailFX(EElement Element);
	static UNiagaraSystem* LoadElementAuraFX(EElement Element);
	static UNiagaraSystem* LoadElementImpactFX(EElement Element);
};
