// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VillageTypes.h"
#include "VillageCitizen.generated.h"

class AIsekaiVillageCharacter;
class USphereComponent;
class UStaticMeshComponent;

UCLASS()
class ISEKAIVILLAGE_API AVillageCitizen : public AActor
{
	GENERATED_BODY()

public:
	AVillageCitizen();

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TObjectPtr<UStaticMeshComponent> Body;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TObjectPtr<USphereComponent> Reach;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	FCitizenMind Mind;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	FVector Goal = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	EVillagePlace GoalPlace = EVillagePlace::Inn;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float WalkSpeed = 280.0f;
	// Derived golem citizens supply swept, street-routed movement.
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	bool bUseStreetMovement = false;

	void SetGoal(EVillagePlace Place, const FVector& World);
	void Restyle();
	FText BarkLine() const;
	UFUNCTION(BlueprintPure, Category = "Village")
	virtual FText OfferLine() const;
	virtual bool TryPlayerOffer(AIsekaiVillageCharacter* Player);
	bool AtGoal(float Dist = 180.0f) const;

	UFUNCTION()
	void OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
