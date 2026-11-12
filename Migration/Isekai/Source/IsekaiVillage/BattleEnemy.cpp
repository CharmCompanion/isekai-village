// Copyright Epic Games, Inc. All Rights Reserved.
// BattleEnemy.cpp — LMBS Combat Enemy with Multiple Archetypes (Beasts, Mages, Zombies, Knights, Berserkers)

#include "BattleEnemy.h"
#include "BattleCharacter.h"
#include "BattleGameMode.h"
#include "SpellProjectile.h"
#include "IsekaiGameplayAnimInstance.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Engine/World.h"

ABattleEnemy::ABattleEnemy()
{
	PrimaryActorTick.bCanEverTick = true;
	AutoPossessAI = EAutoPossessAI::PlacedInWorldOrSpawned;

	GetCapsuleComponent()->InitCapsuleSize(45.0f, 96.0f);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);

	GetCharacterMovement()->bOrientRotationToMovement = false;
	GetCharacterMovement()->bUseControllerDesiredRotation = false;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 650.0f, 0.0f);
	GetCharacterMovement()->MaxWalkSpeed = 460.0f;
	GetCharacterMovement()->BrakingDecelerationWalking = 2500.0f;
	GetCharacterMovement()->GroundFriction = 8.0f;

	// Mesh Asset — default X_Bot (Mixamo) mesh with Manny fallback
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> XBotAsset(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
	if (XBotAsset.Succeeded())
	{
		GetMesh()->SetSkeletalMesh(XBotAsset.Object);
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
		GetMesh()->SetWorldScale3D(FVector(0.95f, 0.95f, 0.95f));
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
			GetMesh()->SetWorldScale3D(FVector(0.95f, 0.95f, 0.95f));
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

	CurrentHP = MaxHP;
}

void ABattleEnemy::BeginPlay()
{
	Super::BeginPlay();

	if (HeadMesh && GetMesh())
	{
		HeadMesh->SetLeaderPoseComponent(GetMesh());
	}
	CurrentHP = MaxHP;
	StrafeDirection = FMath::RandBool() ? 1.0f : -1.0f;

	if (GetCapsuleComponent())
	{
		GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	}

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->bOrientRotationToMovement = false;
		GetCharacterMovement()->bUseControllerDesiredRotation = false;
	}

	if (USkeletalMeshComponent* MeshComp = GetMesh())
	{
		// Always force BodyA — BP overrides may have old mesh causing skeleton mismatch
		if (USkeletalMesh* LoadedMesh = Cast<USkeletalMesh>(StaticLoadObject(USkeletalMesh::StaticClass(), nullptr, TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"))))
		{
			MeshComp->SetSkeletalMesh(LoadedMesh);
		}

		MeshComp->SetRelativeLocationAndRotation(
			FVector(0.0f, 0.0f, -96.0f),
			FRotator(0.0f, -90.0f, 0.0f)
		);
		MeshComp->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
		MeshComp->SetAnimationMode(EAnimationMode::AnimationBlueprint);
		MeshComp->SetAnimInstanceClass(UIsekaiGameplayAnimInstance::StaticClass());
	}

	SetEnemyRole(EnemyRole);
}

void ABattleEnemy::SetEnemyRole(EBattleEnemyRole InRole)
{
	EnemyRole = InRole;

	if (GetCharacterMovement())
	{
		switch (EnemyRole)
		{
		case EBattleEnemyRole::Mage:
			GetCharacterMovement()->MaxWalkSpeed = 380.0f;
			AttackRange = 850.0f;
			AttackCooldown = 3.2f;
			if (GetMesh()) GetMesh()->SetWorldScale3D(FVector(0.85f, 0.85f, 0.85f));
			break;

		case EBattleEnemyRole::Zombie:
			GetCharacterMovement()->MaxWalkSpeed = 320.0f;
			AttackRange = 150.0f;
			AttackCooldown = 1.9f;
			MaxHP = 340.0f;
			CurrentHP = MaxHP;
			if (GetMesh()) GetMesh()->SetWorldScale3D(FVector(1.0f, 1.0f, 1.0f));
			break;

		case EBattleEnemyRole::Knight:
			GetCharacterMovement()->MaxWalkSpeed = 440.0f;
			AttackRange = 180.0f;
			AttackCooldown = 2.4f;
			MaxHP = 380.0f;
			CurrentHP = MaxHP;
			if (GetMesh()) GetMesh()->SetWorldScale3D(FVector(1.05f, 1.05f, 1.05f));
			break;

		case EBattleEnemyRole::Berserker:
			GetCharacterMovement()->MaxWalkSpeed = 520.0f;
			AttackRange = 200.0f;
			AttackCooldown = 2.0f;
			MaxHP = 320.0f;
			CurrentHP = MaxHP;
			if (GetMesh()) GetMesh()->SetWorldScale3D(FVector(1.1f, 1.1f, 1.1f));
			break;

		case EBattleEnemyRole::Melee:
		default:
			GetCharacterMovement()->MaxWalkSpeed = 490.0f;
			AttackRange = 170.0f;
			AttackCooldown = 2.1f;
			if (GetMesh()) GetMesh()->SetWorldScale3D(FVector(0.96f, 0.96f, 0.96f));
			break;
		}
	}

	LoadArchetypeAnimations();

	CurrentLocoState = ELocomotionAnimState::Idle;
}

void ABattleEnemy::LoadArchetypeAnimations()
{
	AnimDeath = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Death/MM_Death_Front_01.MM_Death_Front_01")));

	switch (EnemyRole)
	{
	case EBattleEnemyRole::Zombie:
		if (UAnimSequence* A1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/zombie_attack.zombie_attack")))) AnimAttack = A1;
		if (UAnimSequence* A2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/zombie_headbutt.zombie_headbutt")))) AnimAttack2 = A2;
		if (UAnimSequence* A3 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/zombie_punching.zombie_punching")))) AnimAttack3 = A3;
		if (UAnimSequence* HR = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/zombie_reaction_hit.zombie_reaction_hit")))) AnimHitReact = HR;
		if (UAnimSequence* Idl = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/zombie_idle.zombie_idle")))) AnimLocoIdle = Idl;
		if (UAnimSequence* Wlk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/walking.walking")))) AnimLocoWalk = Wlk;
		if (UAnimSequence* Rn = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Enemies/zombie_running.zombie_running")))) AnimLocoRun = Rn;
		break;

	case EBattleEnemyRole::Knight:
		if (UAnimSequence* A1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_attack.sword_and_shield_attack")))) AnimAttack = A1;
		if (UAnimSequence* A2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_attack_2.sword_and_shield_attack_2")))) AnimAttack2 = A2;
		if (UAnimSequence* Blk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_block.sword_and_shield_block")))) AnimBlock = Blk;
		if (UAnimSequence* Idl = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_block_idle.sword_and_shield_block_idle")))) AnimLocoIdle = Idl;
		if (UAnimSequence* Wlk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Locomotion/walking.walking")))) AnimLocoWalk = Wlk;
		if (UAnimSequence* Rn = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Locomotion/running.running")))) AnimLocoRun = Rn;
		break;

	case EBattleEnemyRole::Mage:
		if (UAnimSequence* CastSeq = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/standing_1H_cast_spell_01.standing_1H_cast_spell_01")))) AnimSpecialAttack = CastSeq;
		if (UAnimSequence* AttSeq = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_1H_Magic_Attack_01.Standing_1H_Magic_Attack_01")))) AnimAttack = AttSeq;
		if (UAnimSequence* Idl = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")))) AnimLocoIdle = Idl;
		if (UAnimSequence* Wlk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/walking_inplace.walking_inplace")))) AnimLocoWalk = Wlk;
		if (UAnimSequence* Rn = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/running_inplace.running_inplace")))) AnimLocoRun = Rn;
		break;

	case EBattleEnemyRole::Berserker:
		if (UAnimSequence* A1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_attack.great_sword_attack")))) AnimAttack = A1;
		if (UAnimSequence* Idl = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")))) AnimLocoIdle = Idl;
		if (UAnimSequence* Wlk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/walking_inplace.walking_inplace")))) AnimLocoWalk = Wlk;
		if (UAnimSequence* Rn = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/running_inplace.running_inplace")))) AnimLocoRun = Rn;
		break;

	case EBattleEnemyRole::Melee:
	default:
		if (UAnimSequence* A1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_attack_downward.standing_melee_attack_downward")))) AnimAttack = A1;
		if (UAnimSequence* A2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_attack_horizontal.standing_melee_attack_horizontal")))) AnimAttack2 = A2;
		if (UAnimSequence* A3 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_attack_360_high.standing_melee_attack_360_high")))) AnimSpecialAttack = A3;
		if (UAnimSequence* Idl = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")))) AnimLocoIdle = Idl;
		if (UAnimSequence* Wlk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/walking_inplace.walking_inplace")))) AnimLocoWalk = Wlk;
		if (UAnimSequence* Rn = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/running_inplace.running_inplace")))) AnimLocoRun = Rn;
		break;
	}

	if (!AnimLocoIdle) AnimLocoIdle = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")));
	if (!AnimLocoWalk) AnimLocoWalk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/walking_inplace.walking_inplace")));
	if (!AnimLocoRun) AnimLocoRun = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/running_inplace.running_inplace")));

	if (!AnimHitReact)
	{
		AnimHitReact = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_react_large_gut.standing_react_large_gut")));
	}
	if (!AnimDash)
	{
		AnimDash = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/Sprinting_Forward_Roll.Sprinting_Forward_Roll")));
	}
}

void ABattleEnemy::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// Dead enemies still need to stay ON the floor: the single-node death clips
	// animate the root bone downward, and without capsule collision the corpse
	// would sink below the ground. Clamp the lowest mesh bound to the captured floor.
	if (!IsAlive())
	{
		if (GetMesh())
		{
			const FBoxSphereBounds MeshBounds = GetMesh()->Bounds;
			const float LowestZ = MeshBounds.Origin.Z - MeshBounds.BoxExtent.Z;
			if (LowestZ < DeadFloorZ)
			{
				SetActorLocation(GetActorLocation() + FVector(0.0f, 0.0f, DeadFloorZ - LowestZ));
			}
		}
		return;
	}

	const float CurrentTime = GetWorld()->GetTimeSeconds();

	// 1. Handle Active Attack Animation
	if (CombatState == EBattleEnemyState::Attacking)
	{
		AttackAnimTimer -= DeltaTime;
		if (AttackAnimTimer <= 0.0f)
		{
			CombatState = EBattleEnemyState::Approaching;
			CurrentLocoState = ELocomotionAnimState::Idle;
		}
		return;
	}

	// 2. Handle Active Dodge Animation
	if (CombatState == EBattleEnemyState::Dodging)
	{
		DodgeAnimTimer -= DeltaTime;
		if (DodgeAnimTimer <= 0.0f)
		{
			CombatState = EBattleEnemyState::Approaching;
			CurrentLocoState = ELocomotionAnimState::Idle;
		}
		return;
	}

	// 3. Handle Stagger Recovery
	if (CombatState == EBattleEnemyState::Staggered)
	{
		StaggerTimer -= DeltaTime;
		if (StaggerTimer <= 0.0f)
		{
			CombatState = EBattleEnemyState::Approaching;
			CurrentLocoState = ELocomotionAnimState::Idle;
		}
		return;
	}

	// 4. Handle Blocking State
	if (CombatState == EBattleEnemyState::Blocking)
	{
		BlockTimer -= DeltaTime;
		if (BlockTimer <= 0.0f)
		{
			CombatState = EBattleEnemyState::Approaching;
			CurrentLocoState = ELocomotionAnimState::Idle;
		}
		return;
	}

	// 5. Handle Broken State (Iron Stance Shattered)
	if (CombatState == EBattleEnemyState::Broken)
	{
		IronStance.BreakTimer -= DeltaTime;
		if (IronStance.BreakTimer <= 0.0f)
		{
			IronStance.bIsBroken = false;
			IronStance.CurrentArmorHits = IronStance.MaxArmorHits;
			CombatState = EBattleEnemyState::Approaching;
			CurrentLocoState = ELocomotionAnimState::Idle;
		}
	}

	// 6. Handle Air Juggle State (Enhanced Tales vertical float)
	if (CombatState == EBattleEnemyState::AirJuggle)
	{
		if (GetCharacterMovement())
		{
			// Dampen extreme fall acceleration so player aerial combos can link smoothly
			if (GetCharacterMovement()->Velocity.Z < -300.0f)
			{
				GetCharacterMovement()->Velocity.Z *= 0.85f;
			}
			if (GetCharacterMovement()->IsMovingOnGround())
			{
				CombatState = IronStance.bIsBroken ? EBattleEnemyState::Broken : EBattleEnemyState::Approaching;
				CurrentLocoState = ELocomotionAnimState::Idle;
			}
		}
		return;
	}

	// 7. Handle Pre-Attack Telegraph Window
	if (bIsTelegraphing)
	{
		TelegraphTimer -= DeltaTime;
		if (TelegraphTimer <= 0.0f)
		{
			bIsTelegraphing = false;
		}
	}

	// 5. Handle Mage Spell Cast Delay
	if (CombatState == EBattleEnemyState::Casting)
	{
		CastTimer -= DeltaTime;
		APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
		ABattleCharacter* BattleChar = Cast<ABattleCharacter>(PlayerPawn);
		if (BattleChar)
		{
			// Face player while casting
			FRotator LookRot = (BattleChar->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
			SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
		}

		if (CastTimer <= 0.0f)
		{
			ExecuteMageCast(BattleChar);
			CombatState = EBattleEnemyState::Strafing;
		}
		return;
	}

	APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
	ABattleCharacter* BattleChar = Cast<ABattleCharacter>(PlayerPawn);
	if (!BattleChar || BattleChar->CurrentHP <= 0.0f) return;

	const FVector PlayerLoc = BattleChar->GetActorLocation();
	const FVector MyLoc = GetActorLocation();
	const float Distance = FVector::Dist(MyLoc, PlayerLoc);
	const FVector ToPlayer = (PlayerLoc - MyLoc).GetSafeNormal2D();
	const FVector Tangent = FVector(-ToPlayer.Y, ToPlayer.X, 0.0f);

	// Update strafe flip timer
	StrafeTimer -= DeltaTime;
	if (StrafeTimer <= 0.0f)
	{
		StrafeTimer = FMath::FRandRange(1.8f, 3.5f);
		StrafeDirection = -StrafeDirection;
	}

	// ── AI Role Logic ──────────────────────────────────────────

	// Smoothly orient enemy towards player
	const FRotator TargetRot = FRotator(0.0f, ToPlayer.ToOrientationRotator().Yaw, 0.0f);
	SetActorRotation(FMath::RInterpConstantTo(GetActorRotation(), TargetRot, DeltaTime, 540.0f));

	if (EnemyRole == EBattleEnemyRole::Mage)
	{
		// Mage Spellcaster Behavior: keep range, strafe, cast spells
		const float PreferredMinDist = 500.0f;
		const float PreferredMaxDist = 850.0f;

		if (Distance < 350.0f)
		{
			if (CurrentTime - LastDodgeTime > 2.0f)
			{
				TriggerDodge(-ToPlayer + Tangent * StrafeDirection);
				LastDodgeTime = CurrentTime;
			}
			else
			{
				FVector BackDir = -ToPlayer + Tangent * (StrafeDirection * 0.4f);
				AddMovementInput(BackDir.GetSafeNormal(), 1.0f);
			}
		}
		else if (Distance > PreferredMaxDist)
		{
			FVector MoveDir = ToPlayer * 0.7f + Tangent * (StrafeDirection * 0.5f);
			AddMovementInput(MoveDir.GetSafeNormal(), 1.0f);
		}
		else
		{
			FVector StrafeDir = Tangent * StrafeDirection;
			AddMovementInput(StrafeDir.GetSafeNormal(), 0.9f);

			if (CurrentTime - LastAttackTime >= AttackCooldown)
			{
				CombatState = EBattleEnemyState::Casting;
				CastTimer = 0.55f;
				LastAttackTime = CurrentTime;
			}
		}
	}
	else if (EnemyRole == EBattleEnemyRole::Knight)
	{
		// Sword & Shield Knight: aggressive rush, shield blocks, combo slashes
		if (Distance <= AttackRange)
		{
			if (CurrentTime - LastAttackTime >= AttackCooldown)
			{
				if (FMath::FRand() < 0.25f && AnimBlock)
				{
					ExecuteShieldBlock();
				}
				else
				{
					ExecuteMeleeAttack(BattleChar);
				}
				LastAttackTime = CurrentTime;
			}
			else
			{
				// Circle and stalk player during attack cooldown
				AddMovementInput(Tangent * (StrafeDirection * 0.35f), 0.5f);
			}
		}
		else
		{
			FVector MoveDir = ToPlayer * 0.85f + Tangent * (StrafeDirection * 0.3f);
			AddMovementInput(MoveDir.GetSafeNormal(), 1.0f);
		}
	}
	else if (EnemyRole == EBattleEnemyRole::Zombie)
	{
		// Zombie: relentless pursuit and violent multi-swipes
		if (Distance <= AttackRange)
		{
			if (CurrentTime - LastAttackTime >= AttackCooldown)
			{
				ExecuteMeleeAttack(BattleChar);
				LastAttackTime = CurrentTime;
			}
			else
			{
				// Stalk and close in during cooldown
				AddMovementInput(ToPlayer * 0.4f + Tangent * (StrafeDirection * 0.25f), 0.4f);
			}
		}
		else
		{
			AddMovementInput(ToPlayer, 1.0f);
		}
	}
	else
	{
		// Melee Beast / Berserker: fast flanking rush & heavy jump strikes
		if (Distance <= AttackRange)
		{
			if (CurrentTime - LastAttackTime >= AttackCooldown)
			{
				ExecuteMeleeAttack(BattleChar);
				LastAttackTime = CurrentTime;
			}
			else
			{
				AddMovementInput(Tangent * (StrafeDirection * 0.4f), 0.6f);
			}
		}
		else
		{
			FVector MoveDir = ToPlayer * 0.9f + Tangent * (StrafeDirection * 0.25f);
			AddMovementInput(MoveDir.GetSafeNormal(), 1.0f);
		}
	}

}

void ABattleEnemy::PlayAnimMontageSafe(UAnimSequence* Seq, float PlayRate)
{
	if (!Seq || !GetMesh()) return;
	if (UAnimInstance* AnimInst = GetMesh()->GetAnimInstance())
	{
		AnimInst->PlaySlotAnimationAsDynamicMontage(Seq, FName("DefaultSlot"), 0.12f, 0.18f, PlayRate);
	}
}


void ABattleEnemy::ExecuteShieldBlock()
{
	CombatState = EBattleEnemyState::Blocking;
	BlockTimer = 1.0f;
	CurrentLocoState = ELocomotionAnimState::Action;
	PlayAnimMontageSafe(AnimBlock ? AnimBlock : AnimAttack, 1.0f);
}

void ABattleEnemy::ExecuteMeleeAttack(ABattleCharacter* TargetPlayer)
{
	if (!TargetPlayer) return;

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->StopMovementImmediately();
	}

	const FVector ToPlayer = (TargetPlayer->GetActorLocation() - GetActorLocation()).GetSafeNormal2D();
	SetActorRotation(FRotator(0.0f, ToPlayer.ToOrientationRotator().Yaw, 0.0f));

	ComboIndex = (ComboIndex + 1) % 3;
	UAnimSequence* AnimToPlay = AnimAttack;

	if (ComboIndex == 1 && AnimAttack2) AnimToPlay = AnimAttack2;
	else if (ComboIndex == 2 && AnimAttack3) AnimToPlay = AnimAttack3;
	else if (ComboIndex == 2 && AnimSpecialAttack) AnimToPlay = AnimSpecialAttack;

	const float PlayRate = 1.15f;
	const float SeqLen = AnimToPlay ? (AnimToPlay->GetPlayLength() / PlayRate) : 0.85f;
	AttackAnimTimer = FMath::Clamp(SeqLen, 0.50f, 0.85f);
	CombatState = EBattleEnemyState::Attacking;
	CurrentLocoState = ELocomotionAnimState::Action;

	// Activate attack telegraph glint (gives player distinct timing for Perfect Dodge!)
	bIsTelegraphing = true;
	TelegraphTimer = 0.35f;

	PlayAnimMontageSafe(AnimToPlay ? AnimToPlay : AnimAttack, PlayRate);

	// Deal damage without artificial sliding
	FVector HitDir = GetActorForwardVector();
	TargetPlayer->TakeCombatDamage(AttackPower, HitDir);
}

void ABattleEnemy::ExecuteMageCast(ABattleCharacter* TargetPlayer)
{
	UWorld* World = GetWorld();
	if (!World) return;

	CurrentLocoState = ELocomotionAnimState::Action;
	PlayAnimMontageSafe(AnimAttack ? AnimAttack : AnimSpecialAttack, 1.2f);

	const FVector SpawnLoc = GetActorLocation() + GetActorForwardVector() * 80.0f + FVector(0.0f, 0.0f, 40.0f);
	FRotator AimRot = GetActorRotation();

	if (TargetPlayer)
	{
		AimRot = (TargetPlayer->GetActorLocation() - SpawnLoc).ToOrientationRotator();
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = this;
	SpawnParams.Instigator = this;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	if (ASpellProjectile* Proj = World->SpawnActor<ASpellProjectile>(ASpellProjectile::StaticClass(), SpawnLoc, AimRot, SpawnParams))
	{
		Proj->BaseDamage = AttackPower;
		EElement CastElem = (WeaknessElement == EElement::Fire) ? EElement::Wind : EElement::Fire;
		Proj->InitProjectile(CastElem, FName("spear"), 1.0f);
	}
}

void ABattleEnemy::TriggerDodge(const FVector& DodgeDir)
{
	FVector Dir = DodgeDir.GetSafeNormal2D();
	if (Dir.IsNearlyZero())
	{
		Dir = -GetActorForwardVector();
	}

	CombatState = EBattleEnemyState::Dodging;
	const float PlayRate = 1.25f;
	const float SeqLen = AnimDash ? (AnimDash->GetPlayLength() / PlayRate) : 0.65f;
	DodgeAnimTimer = FMath::Clamp(SeqLen, 0.45f, 1.10f);
	CurrentLocoState = ELocomotionAnimState::Action;

	PlayAnimMontageSafe(AnimDash, PlayRate);
	LaunchCharacter(Dir * 950.0f, true, true);
}

float ABattleEnemy::ReceiveArteDamage(float DamageAmount, EElement Element, const FVector& HitDirection, bool bLaunchesAirborne)
{
	if (!IsAlive()) return 0.0f;

	// Check if Blocking with Shield
	if (CombatState == EBattleEnemyState::Blocking)
	{
		float BlockedDamage = DamageAmount * 0.2f; // 80% damage reduction
		CurrentHP = FMath::Max(0.0f, CurrentHP - BlockedDamage);
		if (AnimBlock) PlayAnimMontageSafe(AnimBlock, 1.2f);
		if (CurrentHP <= 0.0f) OnDefeated();
		return BlockedDamage;
	}

	// Elemental Weakness Multiplier (1.5x if matching weakness)
	float Multiplier = (Element == WeaknessElement) ? 1.5f : 1.0f;

	// Demon-specific elemental affinities
	if (IsDemon())
	{
		if (Element == EElement::Holy)
		{
			Multiplier *= 1.6f; // Holy light purges demon corruption (+160% total)
		}
		else if (Element == EElement::Dark)
		{
			Multiplier *= 0.5f; // Demons naturally resist chaotic dark energy
		}
	}

	float FinalDamage = DamageAmount * Multiplier;

	CurrentHP = FMath::Max(0.0f, CurrentHP - FinalDamage);

	// Enrage Trigger: When wounded below threshold, enter ferocious berserk state
	if (IsDemon() && !bIsEnraged && CurrentHP > 0.0f && (CurrentHP / MaxHP) <= EnrageThresholdPercent)
	{
		bIsEnraged = true;
		AttackPower *= 1.35f;
		AttackCooldown = FMath::Max(0.8f, AttackCooldown * 0.7f);
		if (GetCharacterMovement())
		{
			GetCharacterMovement()->MaxWalkSpeed *= 1.25f;
		}
		if (SoundEnrage)
		{
			UGameplayStatics::PlaySoundAtLocation(this, SoundEnrage, GetActorLocation());
		}
	}

	if (CurrentHP <= 0.0f)
	{
		OnDefeated();
		return FinalDamage;
	}

	// ── Iron Stance (Super Armor) Logic ──
	if (!IronStance.bIsBroken)
	{
		IronStance.CurrentArmorHits--;
		if (IronStance.CurrentArmorHits <= 0)
		{
			// Shatter Iron Stance! Enter Broken state!
			IronStance.bIsBroken = true;
			IronStance.BreakTimer = IronStance.BreakDuration;
			CombatState = EBattleEnemyState::Broken;
			StaggerTimer = 1.0f;
			CurrentLocoState = ELocomotionAnimState::Action;
			PlayAnimMontageSafe(AnimHitReact, 1.1f);
			if (SoundIronStanceBreak)
			{
				UGameplayStatics::PlaySoundAtLocation(this, SoundIronStanceBreak, GetActorLocation());
			}
			LaunchCharacter(HitDirection * 220.0f + FVector(0.0f, 0.0f, 100.0f), true, true);
		}
		else
		{
			// Super Armor absorbs the impact: minimal flinch, does not interrupt attacking or casting!
			if (CombatState != EBattleEnemyState::Attacking && CombatState != EBattleEnemyState::Casting)
			{
				PlayAnimMontageSafe(AnimHitReact, 1.5f);
			}
		}
		return FinalDamage;
	}

	// ── Broken State: Free Juggle & Stagger ──
	PlayAnimMontageSafe(AnimHitReact, 1.0f);

	if (bLaunchesAirborne || HitDirection.Z > 150.0f)
	{
		// Launch skyward for aerial juggle combo!
		CombatState = EBattleEnemyState::AirJuggle;
		CurrentLocoState = ELocomotionAnimState::Action;
		LaunchCharacter(FVector(0.0f, 0.0f, 520.0f) + HitDirection.GetSafeNormal2D() * 120.0f, true, true);
	}
	else if (CombatState == EBattleEnemyState::AirJuggle)
	{
		// Maintain juggle in mid-air
		LaunchCharacter(FVector(0.0f, 0.0f, 200.0f) + HitDirection.GetSafeNormal2D() * 80.0f, true, true);
	}
	else
	{
		// Ground stagger
		CombatState = EBattleEnemyState::Broken;
		const float SeqLen = AnimHitReact ? (AnimHitReact->GetPlayLength() / 1.0f) : 0.45f;
		StaggerTimer = FMath::Clamp(SeqLen, 0.35f, 0.85f);
		CurrentLocoState = ELocomotionAnimState::Action;
		LaunchCharacter(HitDirection * 180.0f + FVector(0.0f, 0.0f, 60.0f), true, false);
	}

	return FinalDamage;
}


float ABattleEnemy::TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser)
{
	float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
	FVector HitDir = DamageCauser ? (GetActorLocation() - DamageCauser->GetActorLocation()).GetSafeNormal() : -GetActorForwardVector();
	ReceiveArteDamage(DamageAmount, WeaknessElement, HitDir);
	return ActualDamage;
}

void ABattleEnemy::OnDefeated()
{
	CombatState = EBattleEnemyState::Defeated;

	// The death-launch (hit knockback) could still be carrying the enemy upward;
	// snap the corpse down onto the real floor so it doesn't hover mid-air.
	if (GetWorld() && GetCapsuleComponent())
	{
		const float HalfHeight = GetCapsuleComponent()->GetScaledCapsuleHalfHeight();
		FVector SnapLoc = GetActorLocation();
		FVector TraceStart = SnapLoc + FVector(0.0f, 0.0f, 60.0f);
		FVector TraceEnd = SnapLoc - FVector(0.0f, 0.0f, 1000.0f);

		FCollisionQueryParams Params;
		Params.AddIgnoredActor(this);

		FHitResult FloorHit;
		if (GetWorld()->LineTraceSingleByChannel(FloorHit, TraceStart, TraceEnd, ECC_WorldStatic, Params))
		{
			SnapLoc.Z = FloorHit.ImpactPoint.Z + HalfHeight;
		}
		DeadFloorZ = SnapLoc.Z - HalfHeight;
		SetActorLocation(SnapLoc);
	}

	GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GetCharacterMovement()->DisableMovement();

	if (AnimDeath)
	{
		PlayAnimMontageSafe(AnimDeath, 1.0f);
	}

	if (SoundDeath)
	{
		UGameplayStatics::PlaySoundAtLocation(this, SoundDeath, GetActorLocation());
	}

	if (ABattleGameMode* GM = Cast<ABattleGameMode>(UGameplayStatics::GetGameMode(this)))
	{
		GM->OnEnemyDefeated(this);
	}

	SetLifeSpan(3.5f);
}
