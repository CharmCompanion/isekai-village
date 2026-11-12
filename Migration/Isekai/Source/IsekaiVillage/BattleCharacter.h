// Copyright Epic Games, Inc. All Rights Reserved.
// BattleCharacter.h — LMBS Real-Time Player Combatant with Side-to-Side Orbit, Free Camera, and Elemental Artes

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "IsekaiVillageTypes.h"
#include "InputActionValue.h"
#include "BattleCharacter.generated.h"

class USpringArmComponent;
class UCameraComponent;
class ABattleEnemy;
class UInputMappingContext;
class UInputAction;
class UAnimSequence;
class UAnimMontage;
class USkeletalMeshComponent;

USTRUCT(BlueprintType)
struct FWeaponMontageConfig
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> Attack1 = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> Attack2 = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> Attack3 = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> HeavySlam = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> HeavyLunge = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> SprintLunge = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> Block = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> Cast1H = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Animation")
	TObjectPtr<UAnimMontage> Cast2H = nullptr;
};

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ABattleCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	ABattleCharacter();

protected:
	virtual void BeginPlay() override;

public:
	virtual void PawnClientRestart() override;
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;
	virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser) override;

	// ── Components ──
	/** Modular BodyA head (the body mesh is headless). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	USkeletalMeshComponent* HeadMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	USpringArmComponent* CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	UCameraComponent* FollowCamera;

	// ── Stats ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float MaxHP = 500.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Stats")
	float CurrentHP = 500.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float MaxTP = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Stats")
	float CurrentTP = 100.0f;

	// ── AG (Arte Gauge / Chain Capacity) ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float MaxAG = 4.0f; // 4 Arte pips

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Stats")
	float CurrentAG = 4.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float AGRegenRate = 1.25f; // Pips per second when idle/guarding

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	float BaseAttackPower = 28.0f;

	// ── Progression Components ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Progression")
	TObjectPtr<class UTitleManagerComponent> TitleManager;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Progression")
	TObjectPtr<class USkillGridComponent> SkillGrid;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Progression")
	TObjectPtr<class UAdventurersGuildComponent> GuildComponent;

	// ── Adventurer Identity & Condition ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Adventurer")
	FName AdventurerProfileID = NAME_None;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	bool bIsIncapacitated = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	bool bIsGrudgingStrike = false;

	UFUNCTION(BlueprintPure, Category = "Combat|Stats")
	float GetEffectiveAttackPower() const;


	UFUNCTION(BlueprintPure, Category = "Combat|Stats")
	float GetEffectiveMaxHP() const;

	UFUNCTION(BlueprintPure, Category = "Combat|Stats")
	float GetEffectiveMaxTP() const;

	// ── Free Run & Target Locking ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|FreeRun")
	bool bIsFreeRunning = false;

	UFUNCTION(BlueprintCallable, Category = "Combat|FreeRun")
	void SetFreeRun(bool bEnable);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	ABattleEnemy* LockedTarget = nullptr;

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ToggleTargetLock();

	// ── Overlimit & Mystic Artes (Hi-Ougi) ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Overlimit")
	FOverlimitState OverlimitState;

	UFUNCTION(BlueprintCallable, Category = "Combat|Overlimit")
	void TriggerOverlimit();

	UFUNCTION(BlueprintCallable, Category = "Combat|Overlimit")
	void TriggerMysticArte();

	// ── 16-Slot Arte Palette ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Palette")
	FArteSlotMapping ArtePalette;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Palette")
	bool bPaletteModifierActive = false;

	UFUNCTION(BlueprintCallable, Category = "Combat|Palette")
	void SetPaletteModifier(bool bActive);

	UFUNCTION(BlueprintCallable, Category = "Combat|Palette")
	void ExecuteDirectionalArte(EArteDirection Direction);

	// ── Audio Cues ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundHitImpact = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundSwing = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	TObjectPtr<class USoundBase> SoundOverlimitBurst = nullptr;

	// ── Hit-Stop Impact Freeze ──
	UFUNCTION(BlueprintCallable, Category = "Combat|HitStop")
	void TriggerHitStop(float Duration = 0.045f, float Dilation = 0.05f);

	// ── Combat Actions ──
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformNormalAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformHeavyAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformSprintLungeAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformCounterEdge();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformAerialAttack();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformAerialDive();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void CastArte(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void TriggerDodge();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void PerformJump();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void TakeCombatDamage(float DamageAmount, const FVector& HitDirection);

	// ── Counter Edge State ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	bool bCanCounterEdge = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	float CounterEdgeWindowTimer = 0.0f;

	// ── Tales Escape System ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Escape")
	float EscapeTimer = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Escape")
	float EscapeDuration = 3.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Escape")
	bool bIsEscaping = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Escape")
	bool bIsHoldingEscapeKey = false;

	UFUNCTION(BlueprintCallable, Category = "Combat|Escape")
	void StartHoldingEscape();

	UFUNCTION(BlueprintCallable, Category = "Combat|Escape")
	void StopHoldingEscape();

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* EscapeAction;

	UFUNCTION(BlueprintCallable, Category = "Party")
	void SwitchNextPartyLeader();

	// ── Input Actions ──
	UPROPERTY(Transient)
	UInputMappingContext* RuntimeMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* SwitchLeaderAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* MoveAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* LookAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* JumpAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* AttackAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* HeavyAttackAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* SprintAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* FreeRunAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* PaletteModifierAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* OverlimitAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* TargetLockAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte1Action;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte2Action;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte3Action;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte4Action;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* DodgeAction;

	// ── Attack Animations & Styles ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	EWeaponStyle CurrentWeaponStyle = EWeaponStyle::SwordAndShield;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|Montages")
	TMap<EWeaponStyle, FWeaponMontageConfig> StyleMontageMap;

	UPROPERTY(Transient)
	UAnimMontage* MontageAttack1 = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageAttack2 = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageAttack3 = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageAttack4 = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageAttackMedium = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageHeavySlam = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageHeavyLunge = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageSprintLunge = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageCast1H = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageCast2H = nullptr;

	UPROPERTY(Transient)
	UAnimMontage* MontageBlock = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttack1 = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttack2 = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttack3 = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttack4 = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimAttackMedium = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimHeavySlam = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimHeavyLunge = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimSprintLunge = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimCast1H = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimCast2H = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimBlock = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimDash = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimRoll = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoIdle = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoWalk = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoRun = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoJump = nullptr;

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void SwitchWeaponStyle(EWeaponStyle NewStyle);

private:
	void PlayCombatMontageOrSequence(UAnimMontage* Montage, UAnimSequence* FallbackSeq, float PlayRate = 1.0f);
	void PlayAnimMontageSafe(UAnimSequence* AnimSeq, float PlayRate = 1.0f);
	void LoadWeaponStyleAnimations();
	void EnhancedMove(const FInputActionValue& Value);
	void EnhancedLook(const FInputActionValue& Value);
	void CreateRuntimeInputMappings();
	void UpdateCombatCamera(float DeltaTime);
	void OnSprintStarted();
	void OnSprintEnded();
	void ResetLocomotionToInput();

	ELocomotionAnimState CurrentLocoState = ELocomotionAnimState::Idle;

	// Sprint tracking
	bool bIsSprinting = false;

	// Combo tracking & fluid cancel windows (Tales of Arise style)
	int32 ComboStep = 0;
	float LastAttackTime = -10.0f;
	float AttackCooldown = 0.05f;
	bool bIsAttacking = false;
	float AttackTimer = 0.0f;
	float AttackDuration = 0.45f;
	float AttackCancelWindow = 0.22f;
	bool bCanCancelAttack = false;
	bool bBufferedNormalAttack = false;
	bool bBufferedHeavyAttack = false;

	// Hit-Stop impact freeze
	float HitStopTimer = 0.0f;

	// Dodge & Roll
	float LastDodgeTime = -10.0f;
	bool bIsInvulnerable = false;
	bool bIsDodging = false;
	float DodgeTimer = 0.0f;
	float DodgeDuration = 0.55f;
	FVector DodgeDirection = FVector::ZeroVector;
};

