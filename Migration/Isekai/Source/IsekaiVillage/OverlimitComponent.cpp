// Copyright Epic Games, Inc. All Rights Reserved.
// OverlimitComponent.cpp — Tales of Overlimit (OVL 1-4), Mystic Artes (Hi-Ougi), and Boost Attacks

#include "OverlimitComponent.h"
#include "BattleEnemy.h"
#include "BattleCharacter.h"
#include "GameFramework/Character.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

UOverlimitComponent::UOverlimitComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	BoostGauges.Init(1.0f, 4);
}

void UOverlimitComponent::BeginPlay()
{
	Super::BeginPlay();

	BoostGauges.Empty();
	BoostGauges.Init(1.0f, 4);
	CurrentGauge = 0.0f;
	bIsOverlimitActive = false;
	OverlimitLevel = 0;
}

void UOverlimitComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// Overlimit Timer Decay
	if (bIsOverlimitActive)
	{
		TimeRemaining -= DeltaTime;
		if (TimeRemaining <= 0.0f)
		{
			DeactivateOverlimit();
		}
	}

	// Boost Attack Gauges Regeneration (for all 4 party assist slots)
	for (int32 i = 0; i < BoostGauges.Num(); ++i)
	{
		if (BoostGauges[i] < 1.0f)
		{
			BoostGauges[i] = FMath::Min(1.0f, BoostGauges[i] + BoostChargeRate * DeltaTime);
		}
	}
}

void UOverlimitComponent::AddGauge(float Amount)
{
	if (bIsOverlimitActive) return;

	CurrentGauge = FMath::Clamp(CurrentGauge + Amount, 0.0f, MaxGauge);
	OnOverlimitGaugeUpdated.Broadcast(CurrentGauge, MaxGauge);

	// Auto-ready level tier thresholds: 25% = L1, 50% = L2, 75% = L3, 100% = L4
	if (CurrentGauge >= MaxGauge)
	{
		OverlimitLevel = 4;
	}
	else if (CurrentGauge >= 75.0f)
	{
		OverlimitLevel = 3;
	}
	else if (CurrentGauge >= 50.0f)
	{
		OverlimitLevel = 2;
	}
	else if (CurrentGauge >= 25.0f)
	{
		OverlimitLevel = 1;
	}
	else
	{
		OverlimitLevel = 0;
	}
}

bool UOverlimitComponent::ActivateOverlimit(int32 RequestedLevel)
{
	if (bIsOverlimitActive) return false;
	if (CurrentGauge < 25.0f && RequestedLevel <= 1)
	{
		// Allow test trigger if requested
		if (CurrentGauge <= 0.0f) CurrentGauge = 50.0f;
	}

	bIsOverlimitActive = true;
	OverlimitLevel = FMath::Clamp(RequestedLevel, 1, 4);
	TimeRemaining = Duration + (OverlimitLevel * 2.0f); // Higher level gives longer OVL!
	CurrentGauge = 0.0f;

	OnOverlimitStateChanged.Broadcast(true);

	// Radial burst shockwave knocking back nearby foes
	AActor* OwnerActor = GetOwner();
	if (OwnerActor && OwnerActor->GetWorld())
	{
		const FVector Loc = OwnerActor->GetActorLocation();
		TArray<FHitResult> Hits;
		FCollisionShape Sphere = FCollisionShape::MakeSphere(450.0f);
		FCollisionQueryParams Params;
		Params.AddIgnoredActor(OwnerActor);

		if (OwnerActor->GetWorld()->SweepMultiByChannel(Hits, Loc, Loc + FVector(0, 0, 1), FQuat::Identity, ECC_Pawn, Sphere, Params))
		{
			for (const FHitResult& Hit : Hits)
			{
				if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
				{
					if (Enemy->IsAlive())
					{
						FVector Push = (Enemy->GetActorLocation() - Loc).GetSafeNormal2D();
						Enemy->ReceiveArteDamage(35.0f, EElement::Fire, Push * 380.0f);
					}
				}
			}
		}
	}

	return true;
}

void UOverlimitComponent::DeactivateOverlimit()
{
	if (!bIsOverlimitActive) return;

	bIsOverlimitActive = false;
	OverlimitLevel = 0;
	TimeRemaining = 0.0f;
	CurrentGauge = 0.0f;

	OnOverlimitStateChanged.Broadcast(false);
	OnOverlimitGaugeUpdated.Broadcast(0.0f, MaxGauge);
}

bool UOverlimitComponent::ExecuteMysticArte(FText ArteName, float DamageMultiplier, AActor* TargetActor)
{
	if (!CanExecuteMysticArte()) return false;

	AActor* OwnerActor = GetOwner();
	if (!OwnerActor) return false;

	// Broadcast Hi-Ougi event for UI cut-in and cinematic camera
	OnMysticArteExecuted.Broadcast(ArteName, OwnerActor, TargetActor);

	// Apply massive burst damage
	if (TargetActor)
	{
		if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(TargetActor))
		{
			if (Enemy->IsAlive())
			{
				FVector Dir = (TargetActor->GetActorLocation() - OwnerActor->GetActorLocation()).GetSafeNormal();
				Enemy->ReceiveArteDamage(200.0f * DamageMultiplier, EElement::Fire, Dir, true);
			}
		}
		else
		{
			UGameplayStatics::ApplyDamage(TargetActor, 200.0f * DamageMultiplier, nullptr, OwnerActor, nullptr);
		}
	}

	DeactivateOverlimit();
	return true;
}

bool UOverlimitComponent::CallBoostAttack(int32 PartyMemberIndex, AActor* TargetActor)
{
	if (!BoostGauges.IsValidIndex(PartyMemberIndex)) return false;
	if (BoostGauges[PartyMemberIndex] < 1.0f) return false;

	BoostGauges[PartyMemberIndex] = 0.0f; // Consume assist gauge

	// Tales of Arise Boost Attack effect: shatter Iron Stance and knock down!
	if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(TargetActor))
	{
		if (Enemy->IsAlive())
		{
			Enemy->IronStance.CurrentArmorHits = 0;
			Enemy->IronStance.bIsBroken = true;
			Enemy->IronStance.BreakTimer = Enemy->IronStance.BreakDuration + 2.0f;
			Enemy->CombatState = EBattleEnemyState::Broken;

			FVector KnockDir = GetOwner() ? GetOwner()->GetActorForwardVector() : FVector::ForwardVector;
			Enemy->ReceiveArteDamage(75.0f, EElement::Wind, KnockDir, true);
		}
	}

	return true;
}

bool UOverlimitComponent::TriggerBoostStrike(AActor* TargetActor)
{
	AActor* OwnerActor = GetOwner();
	if (!OwnerActor || !TargetActor) return false;

	OnBoostStrikeTriggered.Broadcast(OwnerActor, nullptr);

	if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(TargetActor))
	{
		if (Enemy->IsAlive())
		{
			FVector StrikeDir = (TargetActor->GetActorLocation() - OwnerActor->GetActorLocation()).GetSafeNormal();
			Enemy->ReceiveArteDamage(500.0f, EElement::Fire, StrikeDir, true);
		}
	}

	return true;
}
