// Copyright Epic Games, Inc. All Rights Reserved.
// OverworldCharacter.h — Tales of Symphonia-style overworld traversal + Rheaird flight

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputActionValue.h"
#include "IsekaiVillageTypes.h"
#include "OverworldCharacter.generated.h"


class UInputMappingContext;
class UInputAction;
class UStaticMeshComponent;
class USkeletalMeshComponent;

/**
 * Overworld character — used on the scaled-down world map.
 * Simpler than the village character: no combat, no artes.
 * Camera is overhead, movement is face-camera-direction.
 * Flight (Rheaird) is toggled with a single button.
 */
UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AOverworldCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AOverworldCharacter();

protected:
	virtual void BeginPlay() override;

public:
	virtual void PawnClientRestart() override;
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	// ── Components ──────────────────────────────────────────

	/** Modular BodyA head (the body mesh is headless; the head is a separate mesh on the same skeleton). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	USkeletalMeshComponent* HeadMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	USpringArmComponent* CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	UCameraComponent* OverheadCamera;

	/** The Rheaird (flying mount) visual. Hidden when on foot. */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Flight")
	UStaticMeshComponent* RheairdMesh;

	// ── Input ───────────────────────────────────────────────

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputMappingContext* OverworldMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* MoveAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* LookAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* JumpAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* CrouchAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* DodgeAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* FlightToggleAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* InteractAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* SorcerersRingAction;

	// ── Movement Config ─────────────────────────────────────

	/** Walk speed on foot. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float WalkSpeed = 800.0f;

	/** Flight speed when Rheaird is active. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float FlightSpeed = 2400.0f;

	/** Height above terrain when flying. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float FlightAltitude = 1200.0f;

	/** How far ahead to trace for landing validation. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float LandingTraceDistance = 2000.0f;

	// ── Flight State ────────────────────────────────────────

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Flight")
	bool bIsFlying = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Flight")
	bool bCanLand = false;

	// ── Blueprint Events ────────────────────────────────────

	/** Fired when the player presses Interact near a town zone. */
	DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnInteractActivated);
	UPROPERTY(BlueprintAssignable, Category = "Events")
	FOnInteractActivated OnInteractActivated;

	// ── Modern Tales Camera Config ──────────────────────────
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	bool bEnableAutoRealign = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float AutoRealignDelay = 1.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float AutoRealignSpeed = 3.0f;

	float LastLookInputTime = 0.0f;

	// ── Public API ──────────────────────────────────────────

	/** Toggle Rheaird flight on/off. */
	UFUNCTION(BlueprintCallable, Category = "Flight")
	void ToggleFlight();

	/** Attempt to land the Rheaird. Returns true if landing succeeded. */
	UFUNCTION(BlueprintCallable, Category = "Flight")
	bool TryLand();

	/** Force-takeoff (used by GameMode on spawn if stored state says flying). */
	UFUNCTION(BlueprintCallable, Category = "Flight")
	void ForceTakeoff();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void PerformJump();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void ToggleCrouch();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void TriggerDodge();

	/** Fires Sorcerer's Ring energy beam forward to stun monsters and trigger field devices */
	UFUNCTION(BlueprintCallable, Category = "Field")
	void FireSorcerersRing();

	// Direct input handlers (fallbacks for 100% responsiveness)
	void MoveForwardDirect(float Value);
	void MoveBackwardDirect(float Value);
	void MoveRightDirect(float Value);
	void MoveLeftDirect(float Value);
	void LookYawDirect(float Value);
	void LookPitchDirect(float Value);

private:
	// Input handlers
	void EnhancedMove(const FInputActionValue& Value);
	void EnhancedLook(const FInputActionValue& Value);
	void OnFlightTogglePressed();
	void HandleInteractPressed();

	// Internal
	void UpdateFlightVisuals();
	bool FindValidLandingSpot(FVector& OutLocation) const;
	void CreateRuntimeInputMappings();

	float DefaultArmLength;
	float FlightArmLength;

	// Dodge & Roll
	float LastDodgeTime = -10.0f;
	bool bIsDodging = false;
	float DodgeTimer = 0.0f;
	float DodgeDuration = 0.55f;
	FVector DodgeDirection = FVector::ZeroVector;

	UPROPERTY(Transient)
	UAnimSequence* AnimRoll;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoIdle = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoWalk = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoRun = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoJump = nullptr;

	ELocomotionAnimState CurrentLocoState = ELocomotionAnimState::Idle;

	void PlayAnimMontageSafe(UAnimSequence* AnimSeq, float PlayRate = 1.0f);

	UPROPERTY()
	TObjectPtr<class UInputMappingContext> RuntimeMappingContext;
};

