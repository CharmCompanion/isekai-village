// Copyright Epic Games, Inc. All Rights Reserved.
// DungeonPuzzleGateActor.h — Elemental puzzle barrier gate reacting to Sorcerer's Ring and artes

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IsekaiVillageTypes.h"
#include "DungeonPuzzleGateActor.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class ASorcerersRingProjectile;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnGateUnlockedSignature, ADungeonPuzzleGateActor*, GateActor);

/**
 * Elemental barrier or sealed gate inside demon dungeons and ruins.
 * Requires striking with a matching or neutralizing element from Sorcerer's Ring.
 */
UCLASS(Blueprintable, BlueprintType, ClassGroup = (Dungeon))
class ISEKAIVILLAGE_API ADungeonPuzzleGateActor : public AActor
{
	GENERATED_BODY()

public:
	ADungeonPuzzleGateActor();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// ── Components ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> GateCollision;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> GateMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> ElementalRuneMesh;

	// ── Puzzle Configuration ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Puzzle")
	EElement RequiredElement = EElement::Fire;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Puzzle")
	bool bIsUnlocked = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Puzzle")
	FVector OpenedDisplacement = FVector(0.0f, 0.0f, -320.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Puzzle")
	float OpenSpeed = 1.8f;

	// ── Interaction ──
	UFUNCTION(BlueprintCallable, Category = "Puzzle")
	bool TryUnlockWithElement(EElement InElement);

	UFUNCTION()
	void OnGateOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Puzzle Events")
	FOnGateUnlockedSignature OnGateUnlocked;

private:
	FVector ClosedLocation;
	FVector TargetLocation;
	bool bIsAnimatingOpen = false;
};
