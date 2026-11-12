// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "IsekaiVillageTypes.h"
#include "EarthWallConstruct.generated.h"

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AEarthWallConstruct : public AActor
{
	GENERATED_BODY()

public:
	AEarthWallConstruct();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UBoxComponent* CollisionBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* WallMeshComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	class UNiagaraComponent* WallVFX;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "EarthWall")
	float MaxHeight = 240.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "EarthWall")
	float WallWidth = 320.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "EarthWall")
	float WallThickness = 60.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "EarthWall")
	float Lifetime = 12.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "EarthWall")
	float Health = 400.0f;

	UFUNCTION(BlueprintCallable, Category = "EarthWall")
	void InitWall(EElement InElement, float InChargeRatio);

	virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser) override;

private:
	void RefreshWallVFX(float Progress);

	FVector GroundLocation;
	FVector TargetLocation;
	FVector StartLocation;
	float EruptAlpha = 0.0f;
	bool bIsErupting = true;
	float Age = 0.0f;
	EElement WallElement = EElement::Earth;
	bool bSolidWall = true;
};
