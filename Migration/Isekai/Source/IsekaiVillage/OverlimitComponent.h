// Copyright Epic Games, Inc. All Rights Reserved.
// OverlimitComponent.h — Tales of Overlimit (OVL 1-4), Mystic Artes (Hi-Ougi), and Boost Attacks

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IsekaiVillageTypes.h"
#include "OverlimitComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnOverlimitStateChanged, bool, bIsActive);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnOverlimitGaugeUpdated, float, CurrentGauge, float, MaxGauge);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnMysticArteExecuted, FText, ArteName, AActor*, InstigatorActor, AActor*, TargetActor);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnBoostStrikeTriggered, AActor*, FirstHero, AActor*, SecondHero);

UCLASS(ClassGroup = (TalesTemplate), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UOverlimitComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UOverlimitComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ── Gauge & State ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Overlimit")
	float MaxGauge = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	float CurrentGauge = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	int32 OverlimitLevel = 0; // 0 = off, 1-4

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	bool bIsOverlimitActive = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Overlimit")
	float Duration = 12.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	float TimeRemaining = 0.0f;

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Overlimit|Events")
	FOnOverlimitStateChanged OnOverlimitStateChanged;

	UPROPERTY(BlueprintAssignable, Category = "Overlimit|Events")
	FOnOverlimitGaugeUpdated OnOverlimitGaugeUpdated;

	UPROPERTY(BlueprintAssignable, Category = "Overlimit|Events")
	FOnMysticArteExecuted OnMysticArteExecuted;

	UPROPERTY(BlueprintAssignable, Category = "Overlimit|Events")
	FOnBoostStrikeTriggered OnBoostStrikeTriggered;

	// ── Core Operations ──
	UFUNCTION(BlueprintCallable, Category = "Overlimit")
	void AddGauge(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Overlimit")
	bool ActivateOverlimit(int32 RequestedLevel = 1);

	UFUNCTION(BlueprintCallable, Category = "Overlimit")
	void DeactivateOverlimit();

	UFUNCTION(BlueprintPure, Category = "Overlimit")
	bool CanExecuteMysticArte() const { return bIsOverlimitActive && OverlimitLevel >= 1; }

	/** Executes signature Mystic Arte (Hi-Ougi) with camera lock, time freeze, and damage */
	UFUNCTION(BlueprintCallable, Category = "Overlimit")
	bool ExecuteMysticArte(FText ArteName, float DamageMultiplier, AActor* TargetActor);

	/** Executes a Tales of Arise style companion Boost Attack */
	UFUNCTION(BlueprintCallable, Category = "Overlimit|BoostAttack")
	bool CallBoostAttack(int32 PartyMemberIndex, AActor* TargetActor);

	/** Executes a 2-hero cinematic Boost Strike instant kill / massive finisher */
	UFUNCTION(BlueprintCallable, Category = "Overlimit|BoostStrike")
	bool TriggerBoostStrike(AActor* TargetActor);

	// ── Boost Attack Gauges (One per party slot 1-4) ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit|BoostAttack")
	TArray<float> BoostGauges;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Overlimit|BoostAttack")
	float BoostChargeRate = 0.08f; // Fills over ~12s

protected:
	virtual void BeginPlay() override;
};
