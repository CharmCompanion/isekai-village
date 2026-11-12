// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageCharacter.h — Modern JRPG Tales-style character movement & camera

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "InputActionValue.h"
#include "IsekaiVillageTypes.h"
#include "IsekaiVillageCharacter.generated.h"

class UInputMappingContext;
class UInputAction;
class USkeletalMeshComponent;

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AIsekaiVillageCharacter : public ACharacter
{
	GENERATED_BODY()

public:
	AIsekaiVillageCharacter();

protected:
	virtual void BeginPlay() override;

public:
	virtual void PawnClientRestart() override;
	virtual void Tick(float DeltaTime) override;
	virtual void SetupPlayerInputComponent(class UInputComponent* PlayerInputComponent) override;

	void CreateRuntimeInputMappings();

	// Modular BodyA parts (the BodyA body mesh is headless; the head is a separate mesh on the same skeleton)
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	USkeletalMeshComponent* HeadMesh;

	// Enhanced Input
	UPROPERTY(Transient)
	UInputMappingContext* RuntimeMappingContext;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* MoveAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* LookAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* JumpAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* CrouchAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* SprintAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* DodgeAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* InteractAction;

	// Camera
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	USpringArmComponent* CameraBoom;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Camera")
	UCameraComponent* FollowCamera;

	/** Enable Tales-style soft auto-realign behind player movement */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	bool bEnableAutoRealign = false;

	/** Delay in seconds after manual camera input before auto-realign kicks in */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float AutoRealignDelay = 1.0f;

	/** Speed of smooth camera auto-centering */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Camera")
	float AutoRealignSpeed = 2.5f;

	float LastLookInputTime = 0.0f;

	// Movement Properties
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float NormalWalkSpeed = 600.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float SprintWalkSpeed = 950.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float DodgeImpulse = 1600.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Movement")
	float DodgeCooldown = 0.4f;

	float LastDodgeTime = -10.0f;
	bool bIsDodging = false;
	float DodgeTimer = 0.0f;
	float DodgeDuration = 0.55f;
	FVector DodgeDirection = FVector::ZeroVector;

	UPROPERTY(Transient)
	UAnimSequence* AnimRoll;

	void PlayAnimMontageSafe(UAnimSequence* AnimSeq, float PlayRate = 1.0f);

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	bool bIsSprinting = false;

	// Minimal JRPG TP / Element support for HUD compatibility
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	float MaxTP = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Stats")
	float CurrentTP = 100.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Stats")
	EElement ActiveElement = EElement::Fire;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	bool bIsFocusMode = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	float FocusModeTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Movement")
	float FocusModeDuration = 0.45f;

	// ── Locomotion Animations ──
	UPROPERTY(Transient)
	UAnimSequence* AnimLocoIdle = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoWalk = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoRun = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoJump = nullptr;

	// ── Farming System ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Farming")
	EFarmingTool EquippedTool = EFarmingTool::None;


	UPROPERTY(Transient)
	UAnimSequence* AnimFarmingTill = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimFarmingWater = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimFarmingHarvest = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimBoxHoldIdle = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* CycleToolAction;

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Input")
	UInputAction* UseToolAction;

	UFUNCTION(BlueprintCallable, Category = "Farming")
	void CycleFarmingTool();

	UFUNCTION(BlueprintCallable, Category = "Farming")
	void UseFarmingTool();

	// Actions
	UFUNCTION(BlueprintCallable, Category = "Movement")
	void PerformJump();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void ToggleCrouch();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StartSprint();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void StopSprint();

	UFUNCTION(BlueprintCallable, Category = "Movement")
	void TriggerDodge();

	UFUNCTION(BlueprintCallable, Category = "Interaction")
	void HandleInteractPressed();


	// Input Handlers
	void EnhancedMove(const FInputActionValue& Value);
	void EnhancedLook(const FInputActionValue& Value);

private:
	float NormalCapsuleHalfHeight = 88.0f;

	ELocomotionAnimState CurrentLocoState = ELocomotionAnimState::Idle;
	bool bIsPerformingFarmingAction = false;
	float FarmingActionTimer = 0.0f;
	float FarmingActionDuration = 1.0f;
};