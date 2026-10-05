// Copyright Epic Games, Inc. All Rights Reserved.

#include "OverworldCharacter.h"
#include "TownZone.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimInstance.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputActionValue.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputModifiers.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/TargetPoint.h"
#include "EngineUtils.h"
#include "IsekaiVillageTypes.h"


AOverworldCharacter::AOverworldCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	// Capsule — slightly larger for overworld feel
	GetCapsuleComponent()->InitCapsuleSize(50.0f, 96.0f);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);

	// Mesh — default X_Bot (Mixamo) mesh with Manny fallback
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> XBotAsset(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
	if (XBotAsset.Succeeded())
	{
		GetMesh()->SetSkeletalMesh(XBotAsset.Object);
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
		GetMesh()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<USkeletalMesh> MannyMesh(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
		if (MannyMesh.Succeeded())
		{
			GetMesh()->SetSkeletalMesh(MannyMesh.Object);
			GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
			GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
			GetMesh()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
		}
	}

	// Modular head — the BodyA body mesh is headless; the head is a separate mesh on the same skeleton
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> HeadAsset(TEXT("/Game/StylizedCharacters/BodyA/Heads/Head_01/SKM_HeadA_01.SKM_HeadA_01"));
	HeadMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("HeadMesh"));
	HeadMesh->SetupAttachment(GetMesh());
	HeadMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	HeadMesh->SetGenerateOverlapEvents(false);
	if (HeadAsset.Succeeded())
	{
		HeadMesh->SetSkeletalMesh(HeadAsset.Object);
	}

	// Movement defaults — 8-directional, character faces movement direction
	GetCharacterMovement()->MaxWalkSpeed = WalkSpeed;
	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 1080.0f, 0.0f);
	GetCharacterMovement()->BrakingDecelerationWalking = 4000.0f;
	GetCharacterMovement()->BrakingDecelerationFlying = 5000.0f;
	GetCharacterMovement()->MaxAcceleration = 4000.0f;
	GetCharacterMovement()->GroundFriction = 10.0f;
	GetCharacterMovement()->bUseSeparateBrakingFriction = true;
	GetCharacterMovement()->BrakingFriction = 10.0f;
	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;


	// Camera boom — Modern Tales overworld: elevated framing, smooth lag, smart auto-follow
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 700.0f;
	CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 80.0f);
	CameraBoom->TargetOffset = FVector(0.0f, 0.0f, 60.0f);
	CameraBoom->SetRelativeRotation(FRotator(-35.0f, 0.0f, 0.0f));
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bInheritPitch = true;
	CameraBoom->bInheritYaw = true;
	CameraBoom->bInheritRoll = false;
	CameraBoom->bDoCollisionTest = false;
	CameraBoom->ProbeSize = 12.0f;
	CameraBoom->ProbeChannel = ECC_Camera;
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 8.0f;
	CameraBoom->bEnableCameraRotationLag = true;
	CameraBoom->CameraRotationLagSpeed = 8.0f;
	CameraBoom->CameraLagMaxDistance = 100.0f;

	DefaultArmLength = 700.0f;
	FlightArmLength = 1500.0f;

	// Overhead camera
	OverheadCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("OverheadCamera"));
	OverheadCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	OverheadCamera->bUsePawnControlRotation = false;

	// Rheaird mesh — invisible by default
	RheairdMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("RheairdMesh"));
	RheairdMesh->SetupAttachment(RootComponent);
	RheairdMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -60.0f));
	RheairdMesh->SetVisibility(false);
	RheairdMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);

	// Auto-possess handled by GameMode's DefaultPawnClass
}

void AOverworldCharacter::PlayAnimMontageSafe(UAnimSequence* AnimSeq, float PlayRate)
{
	if (!AnimSeq || !GetMesh()) return;
	GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	GetMesh()->PlayAnimation(AnimSeq, false);
	GetMesh()->SetPlayRate(PlayRate);
}

void AOverworldCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		PC->SetControlRotation(FRotator(-30.0f, GetActorRotation().Yaw, 0.0f));
		PC->SetInputMode(FInputModeGameOnly());
		PC->SetShowMouseCursor(false);

		if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
			ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			CreateRuntimeInputMappings();
			Subsystem->ClearAllMappings();
			if (RuntimeMappingContext)
			{
				Subsystem->AddMappingContext(RuntimeMappingContext, 0);
			}
		}
	}
}

void AOverworldCharacter::BeginPlay()
{
	Super::BeginPlay();

	if (HeadMesh && GetMesh())
	{
		HeadMesh->SetLeaderPoseComponent(GetMesh());
	}

	if (GetCapsuleComponent())
	{
		GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	}

	if (USkeletalMeshComponent* MeshComp = GetMesh())
	{
		// Always force BodyA — BP_OverworldCharacter may override the C++ constructor with an old mesh
		if (USkeletalMesh* LoadedMesh = Cast<USkeletalMesh>(StaticLoadObject(USkeletalMesh::StaticClass(), nullptr, TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"))))
		{
			MeshComp->SetSkeletalMesh(LoadedMesh);
		}

		MeshComp->SetRelativeLocationAndRotation(
			FVector(0.0f, 0.0f, -96.0f),
			FRotator(0.0f, -90.0f, 0.0f)
		);
		MeshComp->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
		MeshComp->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	}

	AnimLocoIdle = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")));
	AnimLocoWalk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/walking_inplace.walking_inplace")));
	AnimLocoRun = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/running_inplace.running_inplace")));
	AnimLocoJump = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/jumping_up.jumping_up")));
	AnimRoll = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/Sprinting_Forward_Roll.Sprinting_Forward_Roll")));
	if (!AnimRoll)
	{
		AnimRoll = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/falling_to_roll.falling_to_roll")));
	}

	CurrentLocoState = ELocomotionAnimState::Idle;
	if (GetMesh() && AnimLocoIdle)
	{
		GetMesh()->PlayAnimation(AnimLocoIdle, true);
		GetMesh()->SetPlayRate(1.0f);
	}


	if (GetCapsuleComponent())
	{
		GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	}

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	// Apply movement speed and enable crouching
	if (UCharacterMovementComponent* CMC = GetCharacterMovement())
	{
		CMC->bOrientRotationToMovement = true;
		CMC->bUseControllerDesiredRotation = false;
		CMC->RotationRate = FRotator(0.0f, 1080.0f, 0.0f);
		CMC->MaxWalkSpeed = WalkSpeed;
		CMC->GetNavAgentPropertiesRef().bCanCrouch = true;
		CMC->bCanWalkOffLedgesWhenCrouching = true;
	}

	// Check transition data from GameInstance
	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		if (GI->bReturningFromBattle && GI->ReturnOverworldPosition != FVector::ZeroVector)
		{
			FVector FinalLoc = GI->ReturnOverworldPosition;
			FRotator FinalRot = GI->ReturnOverworldRotation;

			FHitResult GroundHit;
			FVector TraceStart = FinalLoc + FVector(0.0f, 0.0f, 400.0f);
			FVector TraceEnd = FinalLoc - FVector(0.0f, 0.0f, 600.0f);
			FCollisionQueryParams QueryParams;
			QueryParams.AddIgnoredActor(this);

			if (GetWorld()->LineTraceSingleByChannel(GroundHit, TraceStart, TraceEnd, ECC_WorldStatic, QueryParams))
			{
				const float CapsuleHalfH = GetCapsuleComponent() ? GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 96.0f;
				FinalLoc.Z = GroundHit.ImpactPoint.Z + CapsuleHalfH + 5.0f;
			}
			else
			{
				FinalLoc.Z += 30.0f;
			}

			TeleportTo(FinalLoc, FinalRot, false, true);

			GI->bReturningFromBattle = false;
			GI->ReturnOverworldPosition = FVector::ZeroVector;

		}
		else if (GI->PendingZoneName != NAME_None || GI->PendingEntryPoint != NAME_None || GI->PendingSpawnPosition != FVector::ZeroVector)
		{
			AActor* EntryActor = nullptr;
			if (GI->PendingEntryPoint != NAME_None)
			{
				const FString TargetNameStr = GI->PendingEntryPoint.ToString();
				for (TActorIterator<AActor> It(GetWorld()); It; ++It)
				{
					AActor* Candidate = *It;
					if (!Candidate || Candidate == this) continue;

					if (Candidate->GetFName() == GI->PendingEntryPoint ||
						Candidate->ActorHasTag(GI->PendingEntryPoint) ||
						Candidate->GetName().Equals(TargetNameStr, ESearchCase::IgnoreCase) ||
						Candidate->GetName().StartsWith(TargetNameStr, ESearchCase::IgnoreCase))
					{
						EntryActor = Candidate;
						break;
					}
#if WITH_EDITOR
					if (Candidate->GetActorLabel().Equals(TargetNameStr, ESearchCase::IgnoreCase))
					{
						EntryActor = Candidate;
						break;
					}
#endif
				}
			}

			FVector FinalLoc = GetActorLocation();
			FRotator FinalRot = GetActorRotation();

			if (EntryActor)
			{
				FinalLoc = EntryActor->GetActorLocation() + GI->PendingSpawnPosition;
				FinalRot = (GI->PendingSpawnRotation != FRotator::ZeroRotator) ? GI->PendingSpawnRotation : EntryActor->GetActorRotation();
			}
			else if (GI->PendingSpawnPosition != FVector::ZeroVector)
			{
				FinalLoc = GI->PendingSpawnPosition;
				FinalRot = GI->PendingSpawnRotation;
			}

			// Ground trace to prevent capsule embedding in landscape or objects
			FHitResult GroundHit;
			FVector TraceStart = FinalLoc + FVector(0.0f, 0.0f, 400.0f);
			FVector TraceEnd = FinalLoc - FVector(0.0f, 0.0f, 600.0f);
			FCollisionQueryParams QueryParams;
			QueryParams.AddIgnoredActor(this);
			if (EntryActor) QueryParams.AddIgnoredActor(EntryActor);

			if (GetWorld()->LineTraceSingleByChannel(GroundHit, TraceStart, TraceEnd, ECC_WorldStatic, QueryParams))
			{
				const float CapsuleHalfH = GetCapsuleComponent() ? GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : 96.0f;
				FinalLoc.Z = GroundHit.ImpactPoint.Z + CapsuleHalfH + 5.0f;
			}
			else
			{
				FinalLoc.Z += 30.0f;
			}

			TeleportTo(FinalLoc, FinalRot, false, true);
			GI->ClearPendingTransition();
		}
	}


	// Initialize camera view, input mode, and Enhanced Input mappings
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		PC->SetControlRotation(FRotator(-30.0f, GetActorRotation().Yaw, 0.0f));
		PC->SetInputMode(FInputModeGameOnly());
		PC->SetShowMouseCursor(false);

		if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
			ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			CreateRuntimeInputMappings();
			Subsystem->ClearAllMappings();
			if (RuntimeMappingContext)
			{
				Subsystem->AddMappingContext(RuntimeMappingContext, 0);
			}
		}
	}
}


void AOverworldCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// 1. Evasive Roll Movement
	if (bIsDodging)
	{
		DodgeTimer += DeltaTime;
		const float Alpha = FMath::Clamp(DodgeTimer / DodgeDuration, 0.0f, 1.0f);

		if (GetCharacterMovement())
		{
			const float Speed = FMath::Lerp(1050.0f, 350.0f, Alpha);
			GetCharacterMovement()->Velocity = DodgeDirection * Speed;
		}

		// Counteract forward translation in Sprinting_Forward_Roll so mesh stays centered in capsule
		if (GetMesh())
		{
			const float HipsOffset = FMath::Lerp(0.0f, 567.4f, Alpha);
			GetMesh()->SetRelativeLocation(FVector(-HipsOffset, 0.0f, -96.0f));
		}

		if (Alpha >= 1.0f)
		{
			bIsDodging = false;
			if (GetMesh())
			{
				GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
			}
			if (GetCharacterMovement())
			{
				GetCharacterMovement()->bOrientRotationToMovement = true;
			}
			CurrentLocoState = ELocomotionAnimState::Action;
		}
	}

	// 2. Locomotion State Machine when on foot and not dodging
	if (!bIsFlying && !bIsDodging && GetMesh())
	{
		const float Speed2D = GetVelocity().Size2D();
		const bool bInAir = GetCharacterMovement() && GetCharacterMovement()->IsFalling();

		ELocomotionAnimState TargetState = ELocomotionAnimState::Idle;
		if (bInAir)
		{
			TargetState = ELocomotionAnimState::Jump;
		}
		else if (Speed2D > 620.0f)
		{
			TargetState = ELocomotionAnimState::Run;
		}
		else if (Speed2D > 30.0f)
		{
			TargetState = ELocomotionAnimState::Walk;
		}
		else
		{
			TargetState = ELocomotionAnimState::Idle;
		}

		if (CurrentLocoState != TargetState)
		{
			CurrentLocoState = TargetState;
			GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);
			switch (TargetState)
			{
			case ELocomotionAnimState::Jump:
				if (AnimLocoJump) { GetMesh()->PlayAnimation(AnimLocoJump, true); GetMesh()->SetPlayRate(1.0f); }
				break;
			case ELocomotionAnimState::Run:
				if (AnimLocoRun) { GetMesh()->PlayAnimation(AnimLocoRun, true); GetMesh()->SetPlayRate(1.2f); }
				break;
			case ELocomotionAnimState::Walk:
				if (AnimLocoWalk) { GetMesh()->PlayAnimation(AnimLocoWalk, true); GetMesh()->SetPlayRate(1.0f); }
				break;
			case ELocomotionAnimState::Idle:
			default:
				if (AnimLocoIdle) { GetMesh()->PlayAnimation(AnimLocoIdle, true); GetMesh()->SetPlayRate(1.0f); }
				break;
			}
		}
	}


	// Modern Tales soft camera auto-realign when exploring overworld
	if (bEnableAutoRealign && Controller)
	{
		const float CurrentTime = GetWorld()->GetTimeSeconds();
		const FVector Velocity = GetVelocity();
		const float Speed2D = Velocity.Size2D();

		// If running and player hasn't touched the camera recently
		if (Speed2D > 100.0f && (CurrentTime - LastLookInputTime) > AutoRealignDelay)
		{
			const FRotator TargetRot = Velocity.ToOrientationRotator();
			const FRotator CurrentControlRot = Controller->GetControlRotation();

			// Smoothly interpolate only the Yaw towards movement direction
			const FRotator NewControlRot = FMath::RInterpTo(
				CurrentControlRot,
				FRotator(CurrentControlRot.Pitch, TargetRot.Yaw, 0.0f),
				DeltaTime,
				AutoRealignSpeed
			);

			Controller->SetControlRotation(NewControlRot);
		}
	}

	if (bIsFlying)
	{
		// Maintain flight altitude above terrain
		FVector Start = GetActorLocation();
		FVector TraceEnd = Start - FVector(0.0f, 0.0f, 10000.0f);

		FHitResult Hit;
		FCollisionQueryParams Params;
		Params.AddIgnoredActor(this);

		float DesiredHeight = FlightAltitude;
		float CurrentHeight = 0.0f;

		if (GetWorld()->LineTraceSingleByChannel(Hit, Start, TraceEnd, ECC_Visibility, Params))
		{
			CurrentHeight = Start.Z - Hit.ImpactPoint.Z;
		}

		// Smoothly adjust to desired altitude without sliding lag
		if (FMath::Abs(CurrentHeight - DesiredHeight) > 30.0f)
		{
			float TargetZ = Start.Z + (DesiredHeight - CurrentHeight);
			FVector TargetLoc = FVector(Start.X, Start.Y, FMath::FInterpTo(Start.Z, TargetZ, DeltaTime, 8.0f));
			SetActorLocation(TargetLoc);
		}


		// Check if we can land
		FVector DummyLanding;
		bCanLand = FindValidLandingSpot(DummyLanding);
	}
}

void AOverworldCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (!PlayerInputComponent) return;

	// Ensure runtime mapping context and actions are created before binding!
	CreateRuntimeInputMappings();

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem =
			ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PC->GetLocalPlayer()))
		{
			if (RuntimeMappingContext)
			{
				Subsystem->AddMappingContext(RuntimeMappingContext, 0);
			}
		}
	}

	if (UEnhancedInputComponent* EnhancedInput = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		if (MoveAction)
		{
			EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AOverworldCharacter::EnhancedMove);
		}
		if (LookAction)
		{
			EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &AOverworldCharacter::EnhancedLook);
		}
		if (JumpAction)
		{
			EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started, this, &AOverworldCharacter::PerformJump);
		}
		if (CrouchAction)
		{
			EnhancedInput->BindAction(CrouchAction, ETriggerEvent::Started, this, &AOverworldCharacter::ToggleCrouch);
		}
		if (DodgeAction)
		{
			EnhancedInput->BindAction(DodgeAction, ETriggerEvent::Started, this, &AOverworldCharacter::TriggerDodge);
		}
		if (FlightToggleAction)
		{
			EnhancedInput->BindAction(FlightToggleAction, ETriggerEvent::Started, this, &AOverworldCharacter::OnFlightTogglePressed);
		}
		if (InteractAction)
		{
			EnhancedInput->BindAction(InteractAction, ETriggerEvent::Started, this, &AOverworldCharacter::HandleInteractPressed);
		}
		if (SorcerersRingAction)
		{
			EnhancedInput->BindAction(SorcerersRingAction, ETriggerEvent::Started, this, &AOverworldCharacter::FireSorcerersRing);
		}
	}
}

// ── Input Handlers ─────────────────────────────────────────

void AOverworldCharacter::EnhancedMove(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();

	// Use controller yaw for movement direction
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC) return;

	FRotator ControlRotation = PC->GetControlRotation();
	FRotator YawRotation(0.0f, ControlRotation.Yaw, 0.0f);

	const FVector ForwardDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
	const FVector RightDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

	AddMovementInput(ForwardDir, Input.Y);
	AddMovementInput(RightDir, Input.X);
}

void AOverworldCharacter::EnhancedLook(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		PC->AddYawInput(Input.X);
		PC->AddPitchInput(-Input.Y);
		LastLookInputTime = GetWorld()->GetTimeSeconds();
	}
}

void AOverworldCharacter::MoveForwardDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), 1.0f);
	}
}

void AOverworldCharacter::MoveBackwardDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), -1.0f);
	}
}

void AOverworldCharacter::MoveRightDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), 1.0f);
	}
}

void AOverworldCharacter::MoveLeftDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), -1.0f);
	}
}

void AOverworldCharacter::LookYawDirect(float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		AddControllerYawInput(Value);
		LastLookInputTime = GetWorld()->GetTimeSeconds();
	}
}

void AOverworldCharacter::LookPitchDirect(float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		AddControllerPitchInput(-Value);
		LastLookInputTime = GetWorld()->GetTimeSeconds();
	}
}

void AOverworldCharacter::OnFlightTogglePressed()
{
	ToggleFlight();
}

void AOverworldCharacter::HandleInteractPressed()
{
	OnInteractActivated.Broadcast();

	// 1. Check overlapping TownZones
	TArray<AActor*> OverlappingActors;
	GetOverlappingActors(OverlappingActors, ATownZone::StaticClass());
	for (AActor* Actor : OverlappingActors)
	{
		if (ATownZone* Zone = Cast<ATownZone>(Actor))
		{
			Zone->TriggerTransition();
			return;
		}
	}

	// 2. Check nearby TownZones within interaction range (800 units)
	const FVector PlayerLoc = GetActorLocation();
	TArray<AActor*> AllTownZones;
	UGameplayStatics::GetAllActorsOfClass(GetWorld(), ATownZone::StaticClass(), AllTownZones);
	for (AActor* Actor : AllTownZones)
	{
		if (ATownZone* Zone = Cast<ATownZone>(Actor))
		{
			if (FVector::Dist(PlayerLoc, Zone->GetActorLocation()) <= 800.0f)
			{
				Zone->TriggerTransition();
				return;
			}
		}
	}
}

// ── Flight System ──────────────────────────────────────────

void AOverworldCharacter::ToggleFlight()
{
	if (bIsFlying)
	{
		// Try to land
		TryLand();
	}
	else
	{
		// Take off
		bIsFlying = true;

		if (UCharacterMovementComponent* CMC = GetCharacterMovement())
		{
			CMC->SetMovementMode(MOVE_Flying);
			CMC->MaxFlySpeed = FlightSpeed;
			CMC->BrakingDecelerationFlying = 5000.0f;
			CMC->MaxAcceleration = 4000.0f;
		}

		CameraBoom->TargetArmLength = FlightArmLength;
		UpdateFlightVisuals();
	}
}

bool AOverworldCharacter::TryLand()
{
	if (!bIsFlying) return false;

	FVector LandingSpot;
	if (!FindValidLandingSpot(LandingSpot)) return false;

	// Land at the valid spot
	SetActorLocation(LandingSpot);

	if (UCharacterMovementComponent* CMC = GetCharacterMovement())
	{
		CMC->SetMovementMode(MOVE_Walking);
		CMC->MaxWalkSpeed = WalkSpeed;
		CMC->BrakingDecelerationWalking = 4000.0f;
		CMC->MaxAcceleration = 4000.0f;
	}

	bIsFlying = false;
	CameraBoom->TargetArmLength = DefaultArmLength;
	UpdateFlightVisuals();
	return true;
}

void AOverworldCharacter::ForceTakeoff()
{
	if (bIsFlying) return;

	bIsFlying = true;
	if (UCharacterMovementComponent* CMC = GetCharacterMovement())
	{
		CMC->SetMovementMode(MOVE_Flying);
		CMC->MaxFlySpeed = FlightSpeed;
		CMC->BrakingDecelerationFlying = 5000.0f;
		CMC->MaxAcceleration = 4000.0f;
	}

	CameraBoom->TargetArmLength = FlightArmLength;
	UpdateFlightVisuals();
}


void AOverworldCharacter::UpdateFlightVisuals()
{
	RheairdMesh->SetVisibility(bIsFlying);
}

bool AOverworldCharacter::FindValidLandingSpot(FVector& OutLocation) const
{
	FVector Start = GetActorLocation();
	FVector TraceEnd = Start - FVector(0.0f, 0.0f, 10000.0f);

	FHitResult Hit;
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (!GetWorld()->LineTraceSingleByChannel(Hit, Start, TraceEnd, ECC_Visibility, Params))
		return false;

	// Check surface type — only allow landing on terrain (not water, not buildings)
	// For now, accept any landscape/static mesh hit
	OutLocation = FVector(Hit.ImpactPoint.X, Hit.ImpactPoint.Y, Hit.ImpactPoint.Z + 100.0f);
	return true;
}

void AOverworldCharacter::PerformJump()
{
	if (bIsFlying)
	{
		// Altitude boost while in flight
		AddMovementInput(FVector::UpVector, 1.0f);
		return;
	}

	if (!GetCharacterMovement() || !GetCharacterMovement()->IsMovingOnGround())
	{
		return; // Prevent infinite jumps in mid-air
	}

	FVector MoveDir = GetLastMovementInputVector().GetSafeNormal2D();
	if (MoveDir.IsNearlyZero())
	{
		MoveDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
	}

	if (!MoveDir.IsNearlyZero())
	{
		// Directional Jump (Space + Movement Direction)
		LaunchCharacter(MoveDir * 280.0f + FVector(0.0f, 0.0f, 520.0f), true, true);
	}
	else
	{
		Jump();
	}
}

void AOverworldCharacter::ToggleCrouch()
{
	if (bIsFlying) return;

	if (bIsCrouched)
	{
		UnCrouch();
	}
	else
	{
		Crouch();
	}
}

void AOverworldCharacter::TriggerDodge()
{
	if (bIsFlying) return;
	if (!GetCharacterMovement() || !GetCharacterMovement()->IsMovingOnGround()) return;
	if (bIsDodging) return;

	const float CurrentTime = GetWorld()->GetTimeSeconds();
	if (CurrentTime - LastDodgeTime < 0.45f) return;

	LastDodgeTime = CurrentTime;

	FVector DodgeDir = GetLastMovementInputVector().GetSafeNormal2D();
	if (DodgeDir.IsNearlyZero())
	{
		DodgeDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
	}
	if (DodgeDir.IsNearlyZero())
	{
		DodgeDir = GetActorForwardVector();
	}

	DodgeDirection = DodgeDir;
	bIsDodging = true;
	DodgeTimer = 0.0f;

	const float RollPlayRate = 1.35f;
	if (AnimRoll)
	{
		DodgeDuration = AnimRoll->GetPlayLength() / RollPlayRate;
		PlayAnimMontageSafe(AnimRoll, RollPlayRate);
	}
	else
	{
		DodgeDuration = 0.85f;
	}
	CurrentLocoState = ELocomotionAnimState::DodgeRoll;

	SetActorRotation(FRotator(0.0f, DodgeDir.ToOrientationRotator().Yaw, 0.0f));

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->bOrientRotationToMovement = false;
		GetCharacterMovement()->Velocity = DodgeDirection * 1050.0f;
	}
}

// ── Runtime Input Setup ──────────────────────────────────────

void AOverworldCharacter::CreateRuntimeInputMappings()
{
	if (RuntimeMappingContext && MoveAction && LookAction) return;

	// Create a runtime InputAction for movement (Axis2D, Cumulative for diagonal WASD)
	UInputAction* RuntimeMoveAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Move"));
	RuntimeMoveAction->ValueType = EInputActionValueType::Axis2D;
	RuntimeMoveAction->AccumulationBehavior = EInputActionAccumulationBehavior::Cumulative;
	RuntimeMoveAction->bConsumeInput = false;
	RuntimeMoveAction->bConsumesActionAndAxisMappings = false;

	// Create a runtime InputAction for camera look (Axis2D)
	UInputAction* RuntimeLookAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Look"));
	RuntimeLookAction->ValueType = EInputActionValueType::Axis2D;
	RuntimeLookAction->bConsumeInput = false;
	RuntimeLookAction->bConsumesActionAndAxisMappings = false;

	// Jump (Space / Gamepad Bottom)
	UInputAction* RuntimeJumpAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Jump"));
	RuntimeJumpAction->ValueType = EInputActionValueType::Boolean;

	// Crouch (C / Gamepad Left Thumbstick)
	UInputAction* RuntimeCrouchAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Crouch"));
	RuntimeCrouchAction->ValueType = EInputActionValueType::Boolean;

	// Dodge / Roll (Left Ctrl / Right Ctrl / Gamepad Right)
	UInputAction* RuntimeDodgeAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Dodge"));
	RuntimeDodgeAction->ValueType = EInputActionValueType::Boolean;

	// Sorcerer's Ring (R / Gamepad Left Shoulder)
	UInputAction* RuntimeSorcerersRingAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_SorcerersRing"));
	RuntimeSorcerersRingAction->ValueType = EInputActionValueType::Boolean;

	// Store in UPROPERTY slots so SetupPlayerInputComponent can bind them
	MoveAction = RuntimeMoveAction;
	LookAction = RuntimeLookAction;
	JumpAction = RuntimeJumpAction;
	CrouchAction = RuntimeCrouchAction;
	DodgeAction = RuntimeDodgeAction;
	SorcerersRingAction = RuntimeSorcerersRingAction;

	// Create the runtime mapping context
	RuntimeMappingContext = NewObject<UInputMappingContext>(this, TEXT("RuntimeIMC_Overworld"));

	// ── W key → (0, +1) ──
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::W);
		UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		Swizzle->Order = EInputAxisSwizzle::YXZ;
		Mapping.Modifiers.Add(Swizzle);
	}

	// ── S key → (0, -1) ──
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::S);
		UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		Swizzle->Order = EInputAxisSwizzle::YXZ;
		Mapping.Modifiers.Add(Swizzle);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = false;
		Negate->bY = true;
		Negate->bZ = false;
		Mapping.Modifiers.Add(Negate);
	}

	// ── D key → (+1, 0) ──
	RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::D);

	// ── A key → (-1, 0) ──
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::A);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = true;
		Negate->bY = false;
		Negate->bZ = false;
		Mapping.Modifiers.Add(Negate);
	}

	// ── Arrow Keys Fallback ──
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Up);
		UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		Swizzle->Order = EInputAxisSwizzle::YXZ;
		Mapping.Modifiers.Add(Swizzle);
	}
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Down);
		UInputModifierSwizzleAxis* Swizzle = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		Swizzle->Order = EInputAxisSwizzle::YXZ;
		Mapping.Modifiers.Add(Swizzle);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = false;
		Negate->bY = true;
		Negate->bZ = false;
		Mapping.Modifiers.Add(Negate);
	}
	RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Right);
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Left);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = true;
		Negate->bY = false;
		Negate->bZ = false;
		Mapping.Modifiers.Add(Negate);
	}

	// Gamepad Stick
	RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Gamepad_Left2D);

	// Mouse Look
	RuntimeMappingContext->MapKey(RuntimeLookAction, EKeys::Mouse2D);
	RuntimeMappingContext->MapKey(RuntimeLookAction, EKeys::Gamepad_Right2D);

	// Jump / Directional Jump (Space / Gamepad Bottom)
	RuntimeMappingContext->MapKey(RuntimeJumpAction, EKeys::SpaceBar);
	RuntimeMappingContext->MapKey(RuntimeJumpAction, EKeys::Gamepad_FaceButton_Bottom);

	// Crouch (C / Gamepad Stick Click)
	RuntimeMappingContext->MapKey(RuntimeCrouchAction, EKeys::C);
	RuntimeMappingContext->MapKey(RuntimeCrouchAction, EKeys::Gamepad_LeftThumbstick);

	// Dodge / Roll (Left Ctrl / Right Ctrl / Gamepad Right)
	RuntimeMappingContext->MapKey(RuntimeDodgeAction, EKeys::LeftControl);
	RuntimeMappingContext->MapKey(RuntimeDodgeAction, EKeys::RightControl);
	RuntimeMappingContext->MapKey(RuntimeDodgeAction, EKeys::Gamepad_FaceButton_Right);

	// ── F key → Flight toggle ──
	if (FlightToggleAction)
	{
		RuntimeMappingContext->MapKey(FlightToggleAction, EKeys::F);
		RuntimeMappingContext->MapKey(FlightToggleAction, EKeys::Gamepad_FaceButton_Top);
	}

	// ── E key → Interact ──
	if (InteractAction)
	{
		RuntimeMappingContext->MapKey(InteractAction, EKeys::E);
		RuntimeMappingContext->MapKey(InteractAction, EKeys::Gamepad_FaceButton_Bottom);
	}

	// ── R key / Left Shoulder → Sorcerer's Ring ──
	if (SorcerersRingAction)
	{
		RuntimeMappingContext->MapKey(SorcerersRingAction, EKeys::R);
		RuntimeMappingContext->MapKey(SorcerersRingAction, EKeys::Gamepad_LeftShoulder);
	}
}

void AOverworldCharacter::FireSorcerersRing()
{
}
