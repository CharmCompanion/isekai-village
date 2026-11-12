// Copyright Epic Games, Inc. All Rights Reserved.
// BattleEnemy.h — LMBS Combat Enemy with Multiple Archetypes (Beasts, Mages, Zombies, Knights, Berserkers)

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "IsekaiVillageTypes.h"
#include "BattleEnemy.generated.h"

UENUM(BlueprintType)
enum class EBattleEnemyRole : uint8
{
	Melee              UMETA(DisplayName = "Melee Beast / Brawler"),
	Mage               UMETA(DisplayName = "Ranged Spellcaster / Mage"),
	Zombie             UMETA(DisplayName = "Undead / Zombie"),
	Knight             UMETA(DisplayName = "Sword & Shield Knight"),
	Berserker          UMETA(DisplayName = "Axe Berserker")
};

UENUM(BlueprintType)
enum class EBattleEnemyState : uint8
{
	Approaching,
	Strafing,
	Casting,
	Attacking,
	Blocking,
	Dodging,
	Staggered,
	Broken,
	AirJuggle,
	Defeated
};

class UAnimSequence;
class USkeletalMeshComponent;

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ABattleEnemy : public ACharacter
{
	GENERATED_BODY()

public:
	ABattleEnemy();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;
	virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser) override;

	// ── Role & Identity ──
	/** Modular BodyA head (the body mesh is headless). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	USkeletalMeshComponent* HeadMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Role")
	EBattleEnemyRole EnemyRole = EBattleEnemyRole::Melee;

	UFUNCTION(BlueprintCallable, Category = "Role")
	void SetEnemyRole(EBattleEnemyRole InRole);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	FText EnemyName = FText::FromString(TEXT("Dire Wolf"));

	// ── Stats ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float MaxHP = 260.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Stats")
	float CurrentHP = 260.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float AttackPower = 18.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	int32 ExpReward = 50;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	int32 GaldReward = 35;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	EElement WeaknessElement = EElement::Fire;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demon")
	EDemonCategory DemonCategory = EDemonCategory::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demon")
	FName BountyID = NAME_None;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Demon")
	bool bIsEnraged = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Demon")
	float EnrageThresholdPercent = 0.35f; // Enrage at 35% HP

	UFUNCTION(BlueprintPure, Category = "Demon")
	bool IsDemon() const { return DemonCategory != EDemonCategory::None; }

	// ── Combat Behavior ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float AttackRange = 170.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float AttackCooldown = 2.4f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	EBattleEnemyState CombatState = EBattleEnemyState::Approaching;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|IronStance")
	FIronStanceConfig IronStance;

	// ── Damage Receiving ──
	UFUNCTION(BlueprintCallable, Category = "Combat")
	float ReceiveArteDamage(float DamageAmount, EElement Element, const FVector& HitDirection, bool bLaunchesAirborne = false);

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsAlive() const { return CurrentHP > 0.0f && CombatState != EBattleEnemyState::Defeated; }

	UFUNCTION(BlueprintPure, Category = "Combat")
	bool IsBroken() const { return IronStance.bIsBroken; }

	// ── Tales Attack Telegraph & Boost Strike Vulnerability ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Telegraph")
	bool bIsTelegraphing = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Telegraph")
	float TelegraphTimer = 0.0f;

	UFUNCTION(BlueprintPure, Category = "Combat|BoostStrike")
	bool CanBoostStrike() const
	{
		return IsAlive() && (IronStance.bIsBroken || (CurrentHP / FMath::Max(1.0f, MaxHP) <= 0.40f));
	}

	// ── Animations ──
	UPROPERTY(Transient)
	UAnimSequence* AnimAttack = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttack2 = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttack3 = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimSpecialAttack = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimBlock = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimDash = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimHitReact = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoIdle = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoWalk = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoRun = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimDeath = nullptr;

	// ── Audio Cues ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundHitReact = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundIronStanceBreak = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundEnrage = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundDeath = nullptr;

	ELocomotionAnimState CurrentLocoState = ELocomotionAnimState::Idle;

private:

	void PlayAnimMontageSafe(UAnimSequence* Seq, float PlayRate = 1.0f);
	void LoadArchetypeAnimations();
	void ExecuteMeleeAttack(class ABattleCharacter* TargetPlayer);
	void TriggerDodge(const FVector& DodgeDir);
	void ExecuteMageCast(class ABattleCharacter* TargetPlayer);
	void ExecuteShieldBlock();
	void OnDefeated();

	float LastAttackTime = 0.0f;
	float LastDodgeTime = -10.0f;
	float StaggerTimer = 0.0f;
	float CastTimer = 0.0f;
	float BlockTimer = 0.0f;
	float AttackAnimTimer = 0.0f;
	float DodgeAnimTimer = 0.0f;
	float StrafeTimer = 0.0f;
	float StrafeDirection = 1.0f;
	int32 ComboIndex = 0;
	float DeadFloorZ = -100.0f;
};
