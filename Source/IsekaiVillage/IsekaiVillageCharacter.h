// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageCharacter.h — Tales of Symphonia artes + Adventure Quest 64 stats + Nier movement

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "NiagaraComponent.h"
#include "InputActionValue.h"
#include "IsekaiVillageTypes.h"
#include "ProceduralMagicCircle.h"
#include "SpellProjectile.h"
#include "IsekaiVillageCharacter.generated.h"

class UInputMappingContext;
class UInputAction;
class UAnimSequence;
class UAnimInstance;
class USphereGridDataAsset;
class UPartyReserveComponent;

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AIsekaiVillageCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AIsekaiVillageCharacter();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	// Enhanced Input
	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputMappingContext* DefaultMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* MoveAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* LookAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* JumpAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte1Action; // LMB

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte2Action; // RMB

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte3Action; // Q

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* Arte4Action; // E

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* DodgeAction; // C

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* SprintAction; // Shift

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* CancelAction; // Tab

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* MeleeAction; // F

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* ScrollUpAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* ScrollDownAction;

	// Camera
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	USpringArmComponent* CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	UCameraComponent* FollowCamera;

	// Magic Circle Visual (element color + rotation only, no tiers)
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Magic")
	AProceduralMagicCircle* LeftHandCircleActor;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Magic")
	AProceduralMagicCircle* RightHandCircleActor;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Magic")
	AProceduralMagicCircle* GroundTargetCircleActor;

	// Orbs
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Magic|InHand")
	UNiagaraComponent* LeftHandOrbVFX;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Magic|InHand")
	UNiagaraComponent* RightHandOrbVFX;

	// Projectile / VFX
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Magic")
	TSubclassOf<ASpellProjectile> ProjectileClass;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Magic")
	class USpellVisualDataAsset* SpellVisuals;

	// TP Pool (Tales style)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Magic|TP")
	float MaxTP = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Magic|TP")
	float CurrentTP = 100.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Magic|TP")
	float TPRegenRate = 8.0f; // Per second

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat|HP")
	float MaxHP = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|HP")
	float CurrentHP = 100.0f;

	// Active Element (4 elements: Fire/Water/Earth/Wind)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Magic|Element")
	EElement ActiveElement = EElement::Fire;

	// 4 Arte Slots (LMB/RMB/Q/E)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Magic|Artes")
	TArray<class UArteDataAsset*> EquippedArtes; // Size 4

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TObjectPtr<USphereGridDataAsset> SphereGrid;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	int32 SpherePoints = 13;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	TArray<FName> UnlockedSphereNodes;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	int32 SphereHPBonus = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	int32 SphereInventoryBonus = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	int32 SphereCarryWeightBonus = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	int32 SphereTrustBonus = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereGridFlipped = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereGridOpen = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereSkillDash = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereSkillHunt = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereSkillDangerSense = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereSkillTrailblaze = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Party")
	TObjectPtr<UPartyReserveComponent> PartyReserve;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Party")
	bool bNearGuildMaster = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Zone")
	bool bNearTownZone = false;

	// NIER: AUTOMATA MOVEMENT SYSTEM
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement|Dodge")
	bool bIsDodging = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement|Dodge")
	float DodgeWindowTimer = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement|Dodge")
	float PerfectDodgeWindowDuration = 0.18f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement|Dodge")
	float DashCooldown = 0.55f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement|Dodge")
	float DashCooldownRemaining = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement|Dodge")
	bool bIsFocusMode = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement|Dodge")
	float FocusModeDuration = 0.45f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement|Dodge")
	float FocusModeTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement|Dodge")
	bool bSilentCastReady = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	bool bHasAerialDash = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float AerialDashStrength = 1400.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	bool bIsBulletTime = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	bool bIsSprinting = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	bool bIsSliding = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	float SlideTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	FVector SlideDirection;

	// ARTES
	UFUNCTION(BlueprintCallable, Category = "Magic|Artes")
	void TriggerArte(int32 SlotIndex);

	UFUNCTION(BlueprintCallable, Category = "Magic|Artes")
	void CancelArte();

	UFUNCTION(BlueprintCallable, Category = "Magic|TP")
	bool SpendTP(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Magic|TP")
	void RestoreTP(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Combat|HP")
	void RestoreHP(float Amount);

	virtual float TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser) override;

	UFUNCTION(BlueprintCallable, Category = "Magic|Element")
	void CycleActiveElement(int32 Direction);

	// NIER MOVEMENT
	UFUNCTION(BlueprintCallable, Category = "Movement")
	void TriggerDodge();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void ActivateFocusMode();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StartSprint();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StopSprint();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StartSlide();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StopSlide();

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void PerformMeleeStrike();

	UFUNCTION(BlueprintCallable, Category = "Magic")
	void UpdateMagicCircles();

	UFUNCTION(BlueprintCallable, Category = "SphereGrid")
	bool UnlockSphereNode(FName NodeID);

	UFUNCTION(BlueprintCallable, Category = "SphereGrid")
	void RefreshSphereGridBonuses();

	UFUNCTION(BlueprintCallable, Category = "SphereGrid")
	bool FlipSphereGrid();

	UFUNCTION(BlueprintCallable, Category = "SphereGrid")
	void ToggleSphereGrid();

	UFUNCTION(BlueprintCallable, Category = "Party")
	void TryTalkToGuild();

	UFUNCTION(BlueprintPure, Category = "Magic")
	FVector GetGroundAimLocation() const;

	UFUNCTION(BlueprintPure, Category = "Magic")
	FVector GetAimDirectionFromMouse() const;

	// INPUT HANDLERS
	void EnhancedMove(const FInputActionValue& Value);
	void EnhancedLook(const FInputActionValue& Value);

	// Arte slot wrappers for BindKey (no lambda support)
	void OnArte1Pressed();
	void OnArte1Released();
	void OnArte2Pressed();
	void OnArte2Released();
	void OnArte3Pressed();
	void OnArte3Released();
	void OnArte4Pressed();
	void OnArte4Released();
	void OnScrollUp();
	void OnScrollDown();

	// NIER
	void SetBulletTime(bool bActive, float Dilation = 0.25f);

	void MoveForwardAxis(float Value);
	void MoveRightAxis(float Value);
	void MoveForwardDirect(float Value);
	void MoveBackwardDirect(float Value);
	void MoveRightDirect(float Value);
	void MoveLeftDirect(float Value);
	void LookPitchDirect(float Value);

	void OnMouseScrollUp();
	void OnMouseScrollDown();

private:
	AProceduralMagicCircle* GetLeftCircleActor() const;
	AProceduralMagicCircle* GetRightCircleActor() const;
	AProceduralMagicCircle* GetGroundTargetCircleActor() const;

	float NormalCapsuleHalfHeight = 88.0f;
	float SlideCapsuleHalfHeight  = 44.0f;
	float BaseMaxTP = 100.0f;
	float BaseWalkSpeed = 600.0f;
	float BaseMaxHP = 100.0f;

	// Cosmetic mage appearance (BodyA/Head/Hair/Beard/Eyebrows/Hat/Cape)
	UPROPERTY(Transient)
	TArray<TObjectPtr<USkeletalMeshComponent>> AppearanceMeshes;

	/** Hidden cast pose driver for UltimateSpellSystem anims. */
	UPROPERTY(Transient)
	TObjectPtr<USkeletalMeshComponent> CastPoseDriver = nullptr;
};