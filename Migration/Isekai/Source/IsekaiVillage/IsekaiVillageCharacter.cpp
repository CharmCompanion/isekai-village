// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageCharacter.cpp — Modern JRPG Tales-style character movement & camera

#include "IsekaiVillageCharacter.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimInstance.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputModifiers.h"
#include "TownZone.h"
#include "VillageNPC.h"
#include "IsekaiVillageHUD.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "EngineUtils.h"

AIsekaiVillageCharacter::AIsekaiVillageCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(42.0f, NormalCapsuleHalfHeight);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 720.0f, 0.0f);
	GetCharacterMovement()->JumpZVelocity = 700.0f;
	GetCharacterMovement()->AirControl = 0.35f;
	GetCharacterMovement()->MaxWalkSpeed = NormalWalkSpeed;
	GetCharacterMovement()->MinAnalogWalkSpeed = 20.0f;
	GetCharacterMovement()->BrakingDecelerationWalking = 2000.0f;
	GetCharacterMovement()->GroundFriction = 8.0f;

	// Camera — Modern JRPG Tales framing (elevated, comfortable distance, wide FOV)
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 750.0f;
	CameraBoom->SetRelativeRotation(FRotator(-28.0f, 0.0f, 0.0f));
	CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 70.0f);
	CameraBoom->TargetOffset = FVector(0.0f, 0.0f, 50.0f);
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bInheritPitch = true;
	CameraBoom->bInheritYaw = true;
	CameraBoom->bInheritRoll = false;
	CameraBoom->bDoCollisionTest = false;
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 8.0f;
	CameraBoom->bEnableCameraRotationLag = true;
	CameraBoom->CameraRotationLagSpeed = 10.0f;
	CameraBoom->CameraLagMaxDistance = 100.0f;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;
	FollowCamera->FieldOfView = 90.0f;

	// Default Skeletal Mesh: X_Bot (Mixamo) with Manny fallback
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> XBotMesh(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
	if (XBotMesh.Succeeded())
	{
		GetMesh()->SetSkeletalMesh(XBotMesh.Object);
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -NormalCapsuleHalfHeight));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
		GetMesh()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<USkeletalMesh> MannyMesh(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
		if (MannyMesh.Succeeded())
		{
			GetMesh()->SetSkeletalMesh(MannyMesh.Object);
			GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -NormalCapsuleHalfHeight));
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

	// Default Locomotion Animations (Mixamo X_Bot)
	static ConstructorHelpers::FObjectFinder<UAnimSequence> IdleSeq(TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle"));
	if (IdleSeq.Succeeded()) AnimLocoIdle = IdleSeq.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> WalkSeq(TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/walking_inplace.walking_inplace"));
	if (WalkSeq.Succeeded()) AnimLocoWalk = WalkSeq.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> RunSeq(TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/running_inplace.running_inplace"));
	if (RunSeq.Succeeded()) AnimLocoRun = RunSeq.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> JumpSeq(TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/jumping_up.jumping_up"));
	if (JumpSeq.Succeeded()) AnimLocoJump = JumpSeq.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> RollSeq(TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/Sprinting_Forward_Roll.Sprinting_Forward_Roll"));
	if (RollSeq.Succeeded()) AnimRoll = RollSeq.Object;
	else
	{
		static ConstructorHelpers::FObjectFinder<UAnimSequence> FallRollSeq(TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/falling_to_roll.falling_to_roll"));
		if (FallRollSeq.Succeeded()) AnimRoll = FallRollSeq.Object;
	}

	// Farming Animation Finders
	static ConstructorHelpers::FObjectFinder<UAnimSequence> TillFinder(TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/dig_and_plant_seeds.dig_and_plant_seeds"));
	if (TillFinder.Succeeded()) AnimFarmingTill = TillFinder.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> WaterFinder(TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/watering.watering"));
	if (WaterFinder.Succeeded()) AnimFarmingWater = WaterFinder.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> HarvestFinder(TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/pull_plant.pull_plant"));
	if (HarvestFinder.Succeeded()) AnimFarmingHarvest = HarvestFinder.Object;

	static ConstructorHelpers::FObjectFinder<UAnimSequence> BoxFinder(TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/box_idle.box_idle"));
	if (BoxFinder.Succeeded()) AnimBoxHoldIdle = BoxFinder.Object;

	CurrentTP = MaxTP;
}

void AIsekaiVillageCharacter::PlayAnimMontageSafe(UAnimSequence* AnimSeq, float PlayRate)
{
	if (!AnimSeq || !GetMesh()) return;
	GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	GetMesh()->PlayAnimation(AnimSeq, false);
	GetMesh()->SetPlayRate(PlayRate);
}


void AIsekaiVillageCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		PC->SetControlRotation(FRotator(-28.0f, GetActorRotation().Yaw, 0.0f));
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

void AIsekaiVillageCharacter::BeginPlay()
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
		// Always force BodyA — BP overrides may have old mesh causing skeleton mismatch
		if (USkeletalMesh* LoadedMesh = Cast<USkeletalMesh>(StaticLoadObject(USkeletalMesh::StaticClass(), nullptr, TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"))))
		{
			MeshComp->SetSkeletalMesh(LoadedMesh);
		}

		MeshComp->SetRelativeLocationAndRotation(
			FVector(0.0f, 0.0f, -NormalCapsuleHalfHeight),
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

	// Runtime fallback loading for farming animations
	if (!AnimFarmingTill)
	{
		AnimFarmingTill = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/dig_and_plant_seeds.dig_and_plant_seeds")));
	}
	if (!AnimFarmingWater)
	{
		AnimFarmingWater = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/watering.watering")));
	}
	if (!AnimFarmingHarvest)
	{
		AnimFarmingHarvest = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/pull_plant.pull_plant")));
	}
	if (!AnimBoxHoldIdle)
	{
		AnimBoxHoldIdle = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/box_idle.box_idle")));
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

	if (UCharacterMovementComponent* CMC = GetCharacterMovement())
	{
		CMC->bOrientRotationToMovement = true;
		CMC->bUseControllerDesiredRotation = false;
		CMC->RotationRate = FRotator(0.0f, 1080.0f, 0.0f);
		CMC->GetNavAgentPropertiesRef().bCanCrouch = true;
		CMC->bCanWalkOffLedgesWhenCrouching = true;
	}

	if (CameraBoom)
	{
		CameraBoom->TargetArmLength = 750.0f;
		CameraBoom->bUsePawnControlRotation = true;
		CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 70.0f);
		CameraBoom->TargetOffset = FVector(0.0f, 0.0f, 50.0f);
		CameraBoom->bDoCollisionTest = false;
	}

	if (FollowCamera)
	{
		FollowCamera->FieldOfView = 90.0f;
	}

	// Check transition data from GameInstance
	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		if (GI->PendingZoneName != NAME_None || GI->PendingEntryPoint != NAME_None || GI->PendingSpawnPosition != FVector::ZeroVector)
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
				const float CapsuleHalfH = GetCapsuleComponent() ? GetCapsuleComponent()->GetScaledCapsuleHalfHeight() : NormalCapsuleHalfHeight;
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

	// Add Enhanced Input Context and reset Game Input Mode
	if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
	{
		PlayerController->SetControlRotation(FRotator(-28.0f, GetActorRotation().Yaw, 0.0f));
		PlayerController->SetInputMode(FInputModeGameOnly());
		PlayerController->SetShowMouseCursor(false);

		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
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


void AIsekaiVillageCharacter::Tick(float DeltaTime)
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
			GetMesh()->SetRelativeLocation(FVector(-HipsOffset, 0.0f, -NormalCapsuleHalfHeight));
		}

		if (Alpha >= 1.0f)
		{
			bIsDodging = false;
			if (GetMesh())
			{
				GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -NormalCapsuleHalfHeight));
			}
			if (GetCharacterMovement())
			{
				GetCharacterMovement()->bOrientRotationToMovement = true;
			}
			CurrentLocoState = ELocomotionAnimState::Action;
		}
	}

	// 2. Farming Action State
	if (bIsPerformingFarmingAction)
	{
		FarmingActionTimer += DeltaTime;
		if (FarmingActionTimer >= FarmingActionDuration)
		{
			bIsPerformingFarmingAction = false;
			CurrentLocoState = ELocomotionAnimState::Action;
		}
	}

	// 3. Dynamic Locomotion State Machine
	if (!bIsDodging && !bIsPerformingFarmingAction && GetMesh())
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
				if (AnimLocoJump)
				{
					GetMesh()->PlayAnimation(AnimLocoJump, true);
					GetMesh()->SetPlayRate(1.0f);
				}
				break;

			case ELocomotionAnimState::Run:
				if (AnimLocoRun)
				{
					GetMesh()->PlayAnimation(AnimLocoRun, true);
					GetMesh()->SetPlayRate(1.2f);
				}
				break;

			case ELocomotionAnimState::Walk:
				if (AnimLocoWalk)
				{
					GetMesh()->PlayAnimation(AnimLocoWalk, true);
					GetMesh()->SetPlayRate(1.0f);
				}
				break;

			case ELocomotionAnimState::Idle:
			default:
				if (AnimLocoIdle)
				{
					GetMesh()->PlayAnimation(AnimLocoIdle, true);
					GetMesh()->SetPlayRate(1.0f);
				}
				break;
			}
		}
	}


	// Modern Tales soft camera auto-realign when running
	if (bEnableAutoRealign && Controller)
	{
		const float CurrentTime = GetWorld()->GetTimeSeconds();
		const FVector Velocity = GetVelocity();
		const float Speed2D = Velocity.Size2D();

		// If moving faster than walking threshold AND player hasn't touched the camera recently
		if (Speed2D > 120.0f && (CurrentTime - LastLookInputTime) > AutoRealignDelay)
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
}


void AIsekaiVillageCharacter::CreateRuntimeInputMappings()
{
	if (RuntimeMappingContext && MoveAction && LookAction) return;

	// Create runtime InputActions
	UInputAction* RuntimeMoveAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Move_Village"));
	RuntimeMoveAction->ValueType = EInputActionValueType::Axis2D;
	RuntimeMoveAction->AccumulationBehavior = EInputActionAccumulationBehavior::Cumulative;
	RuntimeMoveAction->bConsumeInput = false;

	UInputAction* RuntimeLookAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Look_Village"));
	RuntimeLookAction->ValueType = EInputActionValueType::Axis2D;
	RuntimeLookAction->bConsumeInput = false;

	UInputAction* RuntimeJumpAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Jump_Village"));
	RuntimeJumpAction->ValueType = EInputActionValueType::Boolean;
	RuntimeJumpAction->bConsumeInput = false;

	UInputAction* RuntimeCrouchAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Crouch_Village"));
	RuntimeCrouchAction->ValueType = EInputActionValueType::Boolean;
	RuntimeCrouchAction->bConsumeInput = false;

	UInputAction* RuntimeSprintAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Sprint_Village"));
	RuntimeSprintAction->ValueType = EInputActionValueType::Boolean;
	RuntimeSprintAction->bConsumeInput = false;

	UInputAction* RuntimeDodgeAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Dodge_Village"));
	RuntimeDodgeAction->ValueType = EInputActionValueType::Boolean;
	RuntimeDodgeAction->bConsumeInput = false;

	UInputAction* RuntimeInteractAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Interact_Village"));
	RuntimeInteractAction->ValueType = EInputActionValueType::Boolean;
	RuntimeInteractAction->bConsumeInput = false;

	UInputAction* RuntimeCycleToolAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_CycleTool_Village"));
	RuntimeCycleToolAction->ValueType = EInputActionValueType::Boolean;
	RuntimeCycleToolAction->bConsumeInput = false;

	UInputAction* RuntimeUseToolAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_UseTool_Village"));
	RuntimeUseToolAction->ValueType = EInputActionValueType::Boolean;
	RuntimeUseToolAction->bConsumeInput = false;

	MoveAction = RuntimeMoveAction;
	LookAction = RuntimeLookAction;
	JumpAction = RuntimeJumpAction;
	CrouchAction = RuntimeCrouchAction;
	SprintAction = RuntimeSprintAction;
	DodgeAction = RuntimeDodgeAction;
	InteractAction = RuntimeInteractAction;
	CycleToolAction = RuntimeCycleToolAction;
	UseToolAction = RuntimeUseToolAction;

	// Create runtime mapping context
	RuntimeMappingContext = NewObject<UInputMappingContext>(this, TEXT("RuntimeIMC_Village"));

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
		Negate->bX = true;
		Negate->bY = true;
		Negate->bZ = true;
		Mapping.Modifiers.Add(Negate);
	}

	// ── D key → (+1, 0) ──
	RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::D);

	// ── A key → (-1, 0) ──
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::A);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = true;
		Negate->bY = true;
		Negate->bZ = true;
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
		Negate->bX = true;
		Negate->bY = true;
		Negate->bZ = true;
		Mapping.Modifiers.Add(Negate);
	}
	RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Right);
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Left);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = true;
		Negate->bY = true;
		Negate->bZ = true;
		Mapping.Modifiers.Add(Negate);
	}

	// Gamepad Stick
	RuntimeMappingContext->MapKey(RuntimeMoveAction, EKeys::Gamepad_Left2D);

	// Mouse Look (Mouse2D: X -> Yaw, Y -> Pitch inverted)
	{
		FEnhancedActionKeyMapping& Mapping = RuntimeMappingContext->MapKey(RuntimeLookAction, EKeys::Mouse2D);
		UInputModifierNegate* Negate = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		Negate->bX = false;
		Negate->bY = true;
		Negate->bZ = false;
		Mapping.Modifiers.Add(Negate);
	}
	RuntimeMappingContext->MapKey(RuntimeLookAction, EKeys::Gamepad_Right2D);

	// Jump / Directional Jump (Space / Gamepad Bottom)
	RuntimeMappingContext->MapKey(RuntimeJumpAction, EKeys::SpaceBar);
	RuntimeMappingContext->MapKey(RuntimeJumpAction, EKeys::Gamepad_FaceButton_Bottom);

	// Crouch (C / Gamepad Left Thumbstick)
	RuntimeMappingContext->MapKey(RuntimeCrouchAction, EKeys::C);
	RuntimeMappingContext->MapKey(RuntimeCrouchAction, EKeys::Gamepad_LeftThumbstick);

	// Sprint
	RuntimeMappingContext->MapKey(RuntimeSprintAction, EKeys::LeftShift);

	// Dodge / Roll (Left Ctrl / Right Ctrl / Gamepad Right)
	RuntimeMappingContext->MapKey(RuntimeDodgeAction, EKeys::LeftControl);
	RuntimeMappingContext->MapKey(RuntimeDodgeAction, EKeys::RightControl);
	RuntimeMappingContext->MapKey(RuntimeDodgeAction, EKeys::Gamepad_FaceButton_Right);

	// Interact (E / Gamepad Top)
	RuntimeMappingContext->MapKey(RuntimeInteractAction, EKeys::E);
	RuntimeMappingContext->MapKey(RuntimeInteractAction, EKeys::Gamepad_FaceButton_Top);

	// Farming Cycle Tool (Tab / Gamepad D-Pad Up / Gamepad Special Right)
	RuntimeMappingContext->MapKey(RuntimeCycleToolAction, EKeys::Tab);
	RuntimeMappingContext->MapKey(RuntimeCycleToolAction, EKeys::Gamepad_DPad_Up);
	RuntimeMappingContext->MapKey(RuntimeCycleToolAction, EKeys::Gamepad_Special_Right);

	// Farming Use Tool (F / Left Mouse Button / Gamepad Left)
	RuntimeMappingContext->MapKey(RuntimeUseToolAction, EKeys::F);
	RuntimeMappingContext->MapKey(RuntimeUseToolAction, EKeys::LeftMouseButton);
	RuntimeMappingContext->MapKey(RuntimeUseToolAction, EKeys::Gamepad_FaceButton_Left);
}

void AIsekaiVillageCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (!PlayerInputComponent) return;

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
			EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AIsekaiVillageCharacter::EnhancedMove);
		}
		if (LookAction)
		{
			EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &AIsekaiVillageCharacter::EnhancedLook);
		}
		if (JumpAction)
		{
			EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::PerformJump);
			EnhancedInput->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
		}
		if (CrouchAction)
		{
			EnhancedInput->BindAction(CrouchAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::ToggleCrouch);
		}
		if (SprintAction)
		{
			EnhancedInput->BindAction(SprintAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::StartSprint);
			EnhancedInput->BindAction(SprintAction, ETriggerEvent::Completed, this, &AIsekaiVillageCharacter::StopSprint);
		}
		if (DodgeAction)
		{
			EnhancedInput->BindAction(DodgeAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::TriggerDodge);
		}
		if (InteractAction)
		{
			EnhancedInput->BindAction(InteractAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::HandleInteractPressed);
		}
		if (CycleToolAction)
		{
			EnhancedInput->BindAction(CycleToolAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::CycleFarmingTool);
		}
		if (UseToolAction)
		{
			EnhancedInput->BindAction(UseToolAction, ETriggerEvent::Started, this, &AIsekaiVillageCharacter::UseFarmingTool);
		}
	}
}

void AIsekaiVillageCharacter::CycleFarmingTool()
{
	uint8 NextToolInt = (static_cast<uint8>(EquippedTool) + 1) % 5;
	EquippedTool = static_cast<EFarmingTool>(NextToolInt);

	FString ToolName;
	switch (EquippedTool)
	{
	case EFarmingTool::Hoe: ToolName = TEXT("Hoe (Soil Tilling)"); break;
	case EFarmingTool::Seeds: ToolName = TEXT("Seeds (Crop Planting)"); break;
	case EFarmingTool::WateringCan: ToolName = TEXT("Watering Can"); break;
	case EFarmingTool::Basket: ToolName = TEXT("Harvest Basket / Box"); break;
	default: ToolName = TEXT("Hands (Unarmed)"); break;
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(88, 2.5f, FColor::Emerald, FString::Printf(TEXT("[Farming] Equipped: %s"), *ToolName));
	}
}

void AIsekaiVillageCharacter::UseFarmingTool()
{
	if (bIsDodging) return;

	UAnimSequence* SelectedAnim = nullptr;
	switch (EquippedTool)
	{
	case EFarmingTool::Hoe:
	case EFarmingTool::Seeds:
		SelectedAnim = AnimFarmingTill;
		break;
	case EFarmingTool::WateringCan:
		SelectedAnim = AnimFarmingWater;
		break;
	case EFarmingTool::Basket:
		SelectedAnim = AnimFarmingHarvest;
		break;
	default:
		SelectedAnim = AnimBoxHoldIdle;
		break;
	}

	if (SelectedAnim)
	{
		bIsPerformingFarmingAction = true;
		FarmingActionTimer = 0.0f;
		FarmingActionDuration = 1.35f;
		CurrentLocoState = ELocomotionAnimState::Action;
		PlayAnimMontageSafe(SelectedAnim, 1.0f);
	}
}


// ───────── ENHANCED INPUT ─────────

void AIsekaiVillageCharacter::EnhancedMove(const FInputActionValue& Value)
{
	const FVector2D MovementVector = Value.Get<FVector2D>();
	if (Controller != nullptr && !MovementVector.IsNearlyZero())
	{
		const FRotator Rotation = Controller->GetControlRotation();
		const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);

		const FVector ForwardDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
		const FVector RightDirection = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

		AddMovementInput(ForwardDirection, MovementVector.Y);
		AddMovementInput(RightDirection, MovementVector.X);
	}
}

void AIsekaiVillageCharacter::EnhancedLook(const FInputActionValue& Value)
{
	const FVector2D LookAxisVector = Value.Get<FVector2D>();
	if (Controller != nullptr)
	{
		AddControllerYawInput(LookAxisVector.X);
		AddControllerPitchInput(LookAxisVector.Y);
		LastLookInputTime = GetWorld()->GetTimeSeconds();
	}
}

// ───────── ACTIONS ─────────

void AIsekaiVillageCharacter::PerformJump()
{
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

void AIsekaiVillageCharacter::ToggleCrouch()
{
	if (bIsCrouched)
	{
		UnCrouch();
	}
	else
	{
		Crouch();
	}
}

void AIsekaiVillageCharacter::StartSprint()
{
	bIsSprinting = true;
	GetCharacterMovement()->MaxWalkSpeed = SprintWalkSpeed;
}

void AIsekaiVillageCharacter::StopSprint()
{
	bIsSprinting = false;
	GetCharacterMovement()->MaxWalkSpeed = NormalWalkSpeed;
}

void AIsekaiVillageCharacter::TriggerDodge()
{
	if (!GetCharacterMovement() || !GetCharacterMovement()->IsMovingOnGround()) return;
	if (bIsDodging) return;

	const float CurrentTime = GetWorld()->GetTimeSeconds();
	if ((CurrentTime - LastDodgeTime) < 0.45f) return;

	LastDodgeTime = CurrentTime;

	FVector DashDir = GetLastMovementInputVector().GetSafeNormal2D();
	if (DashDir.IsNearlyZero())
	{
		DashDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
	}
	if (DashDir.IsNearlyZero())
	{
		if (Controller)
		{
			const FRotator CamRot = Controller->GetControlRotation();
			DashDir = FRotationMatrix(FRotator(0.0f, CamRot.Yaw, 0.0f)).GetUnitAxis(EAxis::X);
		}
		else
		{
			DashDir = GetActorForwardVector();
		}
	}

	DodgeDirection = DashDir;
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

	SetActorRotation(FRotator(0.0f, DashDir.ToOrientationRotator().Yaw, 0.0f));

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->bOrientRotationToMovement = false;
		GetCharacterMovement()->Velocity = DodgeDirection * 1050.0f;
	}
}


void AIsekaiVillageCharacter::HandleInteractPressed()
{
	// 1. Advance or close open dialogue if HUD dialogue is active
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AIsekaiVillageHUD* HUD = Cast<AIsekaiVillageHUD>(PC->GetHUD()))
		{
			if (HUD->IsDialogueOpen())
			{
				HUD->AdvanceDialogue();
				return;
			}
		}
	}

	const FVector PlayerLoc = GetActorLocation();

	// 2. Check nearby Village NPCs (highest priority)
	TArray<AActor*> AllNPCs;
	UGameplayStatics::GetAllActorsOfClass(GetWorld(), AVillageNPC::StaticClass(), AllNPCs);
	for (AActor* Actor : AllNPCs)
	{
		if (AVillageNPC* NPC = Cast<AVillageNPC>(Actor))
		{
			if (NPC->IsPlayerInRange(PlayerLoc))
			{
				NPC->InteractWithPlayer(this);
				return;
			}
		}
	}

	// 3. Check overlapping TownZones
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

	// 4. Check nearby TownZones within interaction range (800 units)
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
