// Copyright IsekaiVillage. Ground mine / glyph trap.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "IsekaiVillageTypes.h"
#include "SpellMine.generated.h"

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ASpellMine : public AActor
{
	GENERATED_BODY()

public:
	ASpellMine();
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	USphereComponent* TriggerSphere;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly)
	UStaticMeshComponent* MineMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float ArmDelay = 0.45f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float Lifetime = 20.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float BlastRadius = 420.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	float BlastDamage = 55.0f;

	UFUNCTION(BlueprintCallable)
	void InitMine(EElement InElement, float InChargeRatio, APawn* InInstigator);

	UFUNCTION(BlueprintCallable)
	void Detonate();

	UFUNCTION()
	void OnTriggerBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	EElement MineElement = EElement::Fire;
	float ChargeRatio = 0.0f;
	float Age = 0.0f;
	bool bArmed = false;
	bool bDetonated = false;
};
