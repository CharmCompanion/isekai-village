// Copyright Epic Games, Inc. All Rights Reserved.
// TownZone.h — Trigger volume for entering/exiting towns on the overworld

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "IsekaiVillageTypes.h"
#include "TownZone.generated.h"

class UBoxComponent;

/**
 * Town Zone — placed around village/dungeon entrances on the overworld.
 * When the player overlaps the trigger and presses Interact, it loads the destination map.
 * Also used inside villages to transition back to the overworld.
 */
UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ATownZone : public AActor
{
	GENERATED_BODY()

public:
	ATownZone();

protected:
	virtual void BeginPlay() override;

public:
	// ── Components ──────────────────────────────────────────

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Zone")
	UBoxComponent* TriggerVolume;

	// ── Configuration ───────────────────────────────────────

	/** The zone to transition to when entering this trigger. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	UWorldZoneData* DestinationZone;

	/** Display name shown in UI when player is near (e.g., "Isekai Village"). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FText LocationName;

	/** Override the entry point name in the destination zone. If empty, use DestinationZone's default. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FName EntryPointOverride;

	/** Offset applied to the spawn position. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FVector SpawnOffset = FVector::ZeroVector;

	/** Rotation to set on the player when they spawn in the destination zone. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FRotator SpawnRotation = FRotator::ZeroRotator;

	/** If true, automatically transition on overlap (no button press needed). */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	bool bAutoTransition = false;

	// ── Events ──────────────────────────────────────────────

	/** Fired just before the transition starts. */
	DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTransitionTriggered, const FText&, LocName);
	UPROPERTY(BlueprintAssignable, Category = "Zone")
	FOnTransitionTriggered OnTransitionTriggered;

	// ── API ─────────────────────────────────────────────────

	/** Manually trigger the transition (e.g., from an interaction prompt). */
	UFUNCTION(BlueprintCallable, Category = "Zone")
	void TriggerTransition();

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

