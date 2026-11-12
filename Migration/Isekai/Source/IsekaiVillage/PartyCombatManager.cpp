// Copyright Epic Games, Inc. All Rights Reserved.
// PartyCombatManager.cpp — 4-Member Active Party, Seamless Leader Switching, and Tactical Gambits

#include "PartyCombatManager.h"
#include "BattleCharacter.h"
#include "BattleEnemy.h"
#include "GameFramework/PlayerController.h"
#include "Kismet/GameplayStatics.h"

UPartyCombatManager::UPartyCombatManager()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void UPartyCombatManager::BeginPlay()
{
	Super::BeginPlay();

	// Auto-register owner if it is a BattleCharacter
	if (ABattleCharacter* Char = Cast<ABattleCharacter>(GetOwner()))
	{
		RegisterPartyMember(Char);
	}
}

void UPartyCombatManager::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	AITickTimer += DeltaTime;
	if (AITickTimer >= 0.25f) // Evaluate companion tactical decisions 4 times per second
	{
		ExecuteCompanionAI(AITickTimer);
		AITickTimer = 0.0f;
	}
}

void UPartyCombatManager::RegisterPartyMember(ABattleCharacter* Character)
{
	if (!Character) return;
	if (!ActivePartyMembers.Contains(Character))
	{
		ActivePartyMembers.Add(Character);
	}
}

ABattleCharacter* UPartyCombatManager::GetLeader() const
{
	if (ActivePartyMembers.IsValidIndex(CurrentLeaderIndex))
	{
		return ActivePartyMembers[CurrentLeaderIndex];
	}
	return nullptr;
}

bool UPartyCombatManager::SwitchLeader(int32 NewLeaderIndex)
{
	if (!ActivePartyMembers.IsValidIndex(NewLeaderIndex)) return false;
	if (NewLeaderIndex == CurrentLeaderIndex) return false;

	ABattleCharacter* OldLeader = GetLeader();
	ABattleCharacter* NewLeader = ActivePartyMembers[NewLeaderIndex];

	if (!NewLeader || NewLeader->CurrentHP <= 0.0f) return false;

	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (!PC) return false;

	// Seamless transfer of player possession
	PC->UnPossess();
	PC->Possess(NewLeader);

	CurrentLeaderIndex = NewLeaderIndex;
	OnPartyLeaderSwitched.Broadcast(NewLeader, CurrentLeaderIndex);

	return true;
}

void UPartyCombatManager::NextLeader()
{
	if (ActivePartyMembers.Num() <= 1) return;

	for (int32 i = 1; i <= ActivePartyMembers.Num(); ++i)
	{
		int32 CandidateIndex = (CurrentLeaderIndex + i) % ActivePartyMembers.Num();
		if (ActivePartyMembers[CandidateIndex] && ActivePartyMembers[CandidateIndex]->CurrentHP > 0.0f)
		{
			SwitchLeader(CandidateIndex);
			break;
		}
	}
}

void UPartyCombatManager::SetTacticsStrategy(ETalesTacticsStrategy NewStrategy)
{
	CurrentStrategy = NewStrategy;
	OnPartyStrategyChanged.Broadcast(CurrentStrategy);
}

void UPartyCombatManager::BroadcastVoiceBark(const FText& Line, ABattleCharacter* Speaker)
{
	OnCombatVoiceBark.Broadcast(Line, Speaker);
}

void UPartyCombatManager::ExecuteCompanionAI(float DeltaTime)
{
	ABattleCharacter* Leader = GetLeader();

	for (int32 i = 0; i < ActivePartyMembers.Num(); ++i)
	{
		if (i == CurrentLeaderIndex) continue; // Skip human-controlled party leader

		ABattleCharacter* Companion = ActivePartyMembers[i];
		if (!Companion || Companion->CurrentHP <= 0.0f) continue;

		// Tactical Gambit 1: Healing Check
		if (CurrentStrategy == ETalesTacticsStrategy::HealPriority || CurrentStrategy == ETalesTacticsStrategy::Balanced)
		{
			for (ABattleCharacter* Ally : ActivePartyMembers)
			{
				if (Ally && Ally->CurrentHP > 0.0f && (Ally->CurrentHP / Ally->MaxHP) < 0.45f)
				{
					if (Companion->CurrentTP >= 15.0f)
					{
						Companion->CastArte(2); // Aqua Surge / Healing Wave
						BroadcastVoiceBark(FText::FromString(TEXT("Hold on, I've got you healed!")), Companion);
						return;
					}
				}
			}
		}

		// Tactical Gambit 2: Assist Leader's Locked Target
		ABattleEnemy* TargetEnemy = Leader ? Leader->LockedTarget : nullptr;
		if (!TargetEnemy || !TargetEnemy->IsAlive())
		{
			// Find nearest living enemy in the arena
			TArray<AActor*> FoundEnemies;
			UGameplayStatics::GetAllActorsOfClass(this, ABattleEnemy::StaticClass(), FoundEnemies);
			float ClosestDist = 99999.0f;
			for (AActor* Act : FoundEnemies)
			{
				if (ABattleEnemy* E = Cast<ABattleEnemy>(Act))
				{
					if (E->IsAlive())
					{
						float Dist = FVector::Dist(Companion->GetActorLocation(), E->GetActorLocation());
						if (Dist < ClosestDist)
						{
							ClosestDist = Dist;
							TargetEnemy = E;
						}
					}
				}
			}
		}

		if (TargetEnemy && TargetEnemy->IsAlive())
		{
			Companion->LockedTarget = TargetEnemy;
			const float Distance = FVector::Dist(Companion->GetActorLocation(), TargetEnemy->GetActorLocation());

			if (CurrentStrategy == ETalesTacticsStrategy::KeepDistance)
			{
				// Caster AI: keep distance and cast ranged elemental spells
				if (Distance < 400.0f)
				{
					Companion->TriggerDodge();
				}
				else if (Distance > 800.0f)
				{
					FVector Dir = (TargetEnemy->GetActorLocation() - Companion->GetActorLocation()).GetSafeNormal();
					Companion->AddMovementInput(Dir, 1.0f);
				}
				else
				{
					if (Companion->CurrentTP >= 12.0f)
					{
						Companion->CastArte(1); // Ignis Spear
					}
				}
			}
			else
			{
				// Melee / Balanced AI: close in and execute combos
				if (Distance > 180.0f)
				{
					FVector Dir = (TargetEnemy->GetActorLocation() - Companion->GetActorLocation()).GetSafeNormal();
					Companion->AddMovementInput(Dir, 1.0f);
				}
				else
				{
					// Close combat range: execute attack chains
					if (TargetEnemy->IsBroken())
					{
						Companion->PerformHeavyAttack(); // Heavy juggle launch on broken enemy
					}
					else
					{
						Companion->PerformNormalAttack();
					}
				}
			}
		}
	}
}
