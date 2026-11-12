// Copyright Epic Games, Inc. All Rights Reserved.
// BattleCharacter.cpp — LMBS Real-Time Player Combatant with Side-to-Side Orbit, Free Camera, and Elemental Artes

#include "BattleCharacter.h"
#include "BattleEnemy.h"
#include "BattleGameMode.h"
#include "BattleHUD.h"
#include "SpellProjectile.h"
#include "EarthWallConstruct.h"
#include "IsekaiGameplayAnimInstance.h"
#include "TitleManagerComponent.h"
#include "SkillGridComponent.h"
#include "AdventurersGuildComponent.h"
#include "PartyCombatManager.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSingleNodeInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimMontage.h"
#include "Camera/CameraComponent.h"
#include "GameFramework/SpringArmComponent.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"
#include "InputAction.h"
#include "InputModifiers.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "EngineUtils.h"

ABattleCharacter::ABattleCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(50.0f, 96.0f);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 1080.0f, 0.0f);
	GetCharacterMovement()->MaxWalkSpeed = 420.0f;
	GetCharacterMovement()->MaxAcceleration = 2048.0f;
	GetCharacterMovement()->BrakingDecelerationWalking = 2048.0f;
	GetCharacterMovement()->GroundFriction = 8.0f;
	GetCharacterMovement()->bUseSeparateBrakingFriction = true;
	GetCharacterMovement()->BrakingFriction = 8.0f;

	// Combat Camera
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 580.0f;
	CameraBoom->SetRelativeRotation(FRotator(-18.0f, 0.0f, 0.0f));
	CameraBoom->SocketOffset = FVector(0.0f, 0.0f, 75.0f);
	CameraBoom->ProbeSize = 12.0f;
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bInheritPitch = true;
	CameraBoom->bInheritYaw = true;
	CameraBoom->bInheritRoll = false;
	CameraBoom->bDoCollisionTest = true;
	CameraBoom->bEnableCameraLag = false; // Disabled to eliminate camera rubberbanding / elastic lag

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;
	FollowCamera->FieldOfView = 85.0f;

	// Progression & Guild Components
	TitleManager = CreateDefaultSubobject<UTitleManagerComponent>(TEXT("TitleManager"));
	SkillGrid = CreateDefaultSubobject<USkillGridComponent>(TEXT("SkillGrid"));
	GuildComponent = CreateDefaultSubobject<UAdventurersGuildComponent>(TEXT("GuildComponent"));

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

	// Locomotion Animations (Mixamo X_Bot)
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

	LoadWeaponStyleAnimations();

	CurrentHP = MaxHP;
	CurrentTP = MaxTP;
}

void ABattleCharacter::LoadWeaponStyleAnimations()
{
	MontageAttack1 = nullptr;
	MontageAttack2 = nullptr;
	MontageAttack3 = nullptr;
	MontageAttack4 = nullptr;
	MontageAttackMedium = nullptr;
	MontageHeavySlam = nullptr;
	MontageHeavyLunge = nullptr;
	MontageSprintLunge = nullptr;
	MontageCast1H = nullptr;
	MontageCast2H = nullptr;
	MontageBlock = nullptr;

	switch (CurrentWeaponStyle)
	{
	case EWeaponStyle::Greatsword:
		if (UAnimSequence* A1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_attack.great_sword_attack")))) AnimAttack1 = A1;
		if (UAnimSequence* A2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_slash.great_sword_slash")))) AnimAttack2 = A2;
		if (UAnimSequence* Med = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_high_spin_attack.great_sword_high_spin_attack")))) AnimAttackMedium = Med;
		if (UAnimSequence* Slam = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_jump_attack.great_sword_jump_attack")))) AnimHeavySlam = Slam;
		if (UAnimSequence* Lunge = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_slide_attack.great_sword_slide_attack")))) AnimHeavyLunge = Lunge;
		AnimSprintLunge = AnimHeavyLunge ? AnimHeavyLunge : AnimAttack1;
		AnimAttack3 = AnimAttackMedium ? AnimAttackMedium : AnimAttack1;
		AnimAttack4 = AnimHeavySlam ? AnimHeavySlam : AnimAttack1;
		if (UAnimSequence* Blk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/GreatSword/great_sword_blocking.great_sword_blocking")))) AnimBlock = Blk;

		MontageAttack1 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/GreatSword/AM_great_sword_attack.AM_great_sword_attack")));
		MontageAttack2 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/GreatSword/AM_great_sword_slash.AM_great_sword_slash")));
		MontageAttack3 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/GreatSword/AM_great_sword_high_spin_attack.AM_great_sword_high_spin_attack")));
		MontageAttackMedium = MontageAttack3;
		MontageHeavySlam = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/GreatSword/AM_great_sword_jump_attack.AM_great_sword_jump_attack")));
		MontageHeavyLunge = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/GreatSword/AM_great_sword_slide_attack.AM_great_sword_slide_attack")));
		MontageSprintLunge = MontageHeavyLunge ? MontageHeavyLunge : MontageAttack1;
		MontageAttack4 = MontageHeavySlam ? MontageHeavySlam : MontageAttack1;
		MontageBlock = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/GreatSword/AM_great_sword_blocking.AM_great_sword_blocking")));
		break;

	case EWeaponStyle::MagicStaff:
		if (UAnimSequence* M1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_1H_Magic_Attack_01.Standing_1H_Magic_Attack_01")))) AnimAttack1 = M1;
		if (UAnimSequence* M2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_1H_Magic_Attack_02.Standing_1H_Magic_Attack_02")))) AnimAttack2 = M2;
		if (UAnimSequence* M3 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_2H_Magic_Attack_01.Standing_2H_Magic_Attack_01")))) AnimAttackMedium = M3;
		if (UAnimSequence* MArea = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_2H_Magic_Area_Attack_01.Standing_2H_Magic_Area_Attack_01")))) AnimHeavySlam = MArea;
		AnimHeavyLunge = AnimAttackMedium ? AnimAttackMedium : AnimAttack1;
		AnimSprintLunge = AnimAttack1;
		AnimAttack3 = AnimAttackMedium ? AnimAttackMedium : AnimAttack1;
		AnimAttack4 = AnimHeavySlam ? AnimHeavySlam : AnimAttack1;
		if (UAnimSequence* Blk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_Block_Idle.Standing_Block_Idle")))) AnimBlock = Blk;

		MontageAttack1 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_Standing_1H_Magic_Attack_01.AM_Standing_1H_Magic_Attack_01")));
		MontageAttack2 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_Standing_1H_Magic_Attack_02.AM_Standing_1H_Magic_Attack_02")));
		MontageAttack3 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_Standing_2H_Magic_Attack_01.AM_Standing_2H_Magic_Attack_01")));
		MontageAttackMedium = MontageAttack3;
		MontageHeavySlam = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_Standing_2H_Magic_Area_Attack_01.AM_Standing_2H_Magic_Area_Attack_01")));
		MontageHeavyLunge = MontageAttackMedium ? MontageAttackMedium : MontageAttack1;
		MontageSprintLunge = MontageAttack1;
		MontageAttack4 = MontageHeavySlam ? MontageHeavySlam : MontageAttack1;
		MontageBlock = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_Standing_Block_Idle.AM_Standing_Block_Idle")));
		break;

	case EWeaponStyle::Unarmed:
		if (UAnimSequence* Axe1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_combo_attack_ver_1.standing_melee_combo_attack_ver_1")))) AnimAttack1 = Axe1;
		if (UAnimSequence* Axe2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_combo_attack_ver_2.standing_melee_combo_attack_ver_2")))) AnimAttack2 = Axe2;
		if (UAnimSequence* Axe3 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_attack_horizontal.standing_melee_attack_horizontal")))) AnimAttackMedium = Axe3;
		if (UAnimSequence* Slam = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_attack_downward.standing_melee_attack_downward")))) AnimHeavySlam = Slam;
		if (UAnimSequence* Lunge = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_run_jump_attack.standing_melee_run_jump_attack")))) AnimHeavyLunge = Lunge;
		AnimSprintLunge = AnimHeavyLunge ? AnimHeavyLunge : AnimAttack1;
		AnimAttack3 = AnimAttackMedium ? AnimAttackMedium : AnimAttack1;
		AnimAttack4 = AnimHeavySlam ? AnimHeavySlam : AnimAttack1;
		if (UAnimSequence* Blk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_block_idle.standing_block_idle")))) AnimBlock = Blk;

		MontageAttack1 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_melee_combo_attack_ver_1.AM_standing_melee_combo_attack_ver_1")));
		MontageAttack2 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_melee_combo_attack_ver_2.AM_standing_melee_combo_attack_ver_2")));
		MontageAttack3 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_melee_attack_horizontal.AM_standing_melee_attack_horizontal")));
		MontageAttackMedium = MontageAttack3;
		MontageHeavySlam = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_melee_attack_downward.AM_standing_melee_attack_downward")));
		MontageHeavyLunge = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_melee_run_jump_attack.AM_standing_melee_run_jump_attack")));
		MontageSprintLunge = MontageHeavyLunge ? MontageHeavyLunge : MontageAttack1;
		MontageAttack4 = MontageHeavySlam ? MontageHeavySlam : MontageAttack1;
		MontageBlock = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_block_idle.AM_standing_block_idle")));
		break;

	case EWeaponStyle::SwordAndShield:
	default:
		// In-place light attacks (zero root displacement, crisp Tales combo feel)
		if (UAnimSequence* A1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_attack_4.sword_and_shield_attack_4")))) AnimAttack1 = A1;
		if (UAnimSequence* A2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_slash_5.sword_and_shield_slash_5")))) AnimAttack2 = A2;
		if (UAnimSequence* Med = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_slash.sword_and_shield_slash")))) AnimAttackMedium = Med;
		if (!AnimAttackMedium) AnimAttackMedium = AnimAttack1;
		if (UAnimSequence* Slam = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/MeleeAxe/standing_melee_attack_downward.standing_melee_attack_downward")))) AnimHeavySlam = Slam;
		if (!AnimHeavySlam) AnimHeavySlam = AnimAttackMedium;
		if (UAnimSequence* Lunge = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_attack_3.sword_and_shield_attack_3")))) AnimHeavyLunge = Lunge;
		if (UAnimSequence* SpLunge = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_attack.sword_and_shield_attack")))) AnimSprintLunge = SpLunge;
		if (!AnimSprintLunge) AnimSprintLunge = AnimHeavyLunge ? AnimHeavyLunge : AnimAttack1;
		AnimAttack3 = AnimAttackMedium;
		AnimAttack4 = AnimHeavySlam;
		if (UAnimSequence* Blk = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_block.sword_and_shield_block")))) AnimBlock = Blk;

		MontageAttack1 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/SwordAndShield/AM_sword_and_shield_attack_4.AM_sword_and_shield_attack_4")));
		MontageAttack2 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/SwordAndShield/AM_sword_and_shield_slash_5.AM_sword_and_shield_slash_5")));
		MontageAttack3 = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/SwordAndShield/AM_sword_and_shield_slash.AM_sword_and_shield_slash")));
		MontageAttackMedium = MontageAttack3;
		MontageHeavySlam = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/MeleeAxe/AM_standing_melee_attack_downward.AM_standing_melee_attack_downward")));
		MontageHeavyLunge = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/SwordAndShield/AM_sword_and_shield_attack_3.AM_sword_and_shield_attack_3")));
		MontageSprintLunge = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/SwordAndShield/AM_sword_and_shield_attack.AM_sword_and_shield_attack")));
		MontageAttack4 = MontageHeavySlam ? MontageHeavySlam : MontageAttack1;
		MontageBlock = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/SwordAndShield/AM_sword_and_shield_block.AM_sword_and_shield_block")));
		break;
	}

	// Magic cast animations and montages (always loaded for elemental artes)
	if (UAnimSequence* C1 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/standing_1H_cast_spell_01.standing_1H_cast_spell_01")))) AnimCast1H = C1;
	if (UAnimSequence* C2 = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/Magic/Standing_2H_Magic_Area_Attack_02.Standing_2H_Magic_Area_Attack_02")))) AnimCast2H = C2;
	MontageCast1H = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_standing_1H_cast_spell_01.AM_standing_1H_cast_spell_01")));
	MontageCast2H = Cast<UAnimMontage>(StaticLoadObject(UAnimMontage::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Montages/Combat/Magic/AM_Standing_2H_Magic_Area_Attack_02.AM_Standing_2H_Magic_Area_Attack_02")));

	// Cache in StyleMontageMap
	FWeaponMontageConfig& Config = StyleMontageMap.FindOrAdd(CurrentWeaponStyle);
	Config.Attack1 = MontageAttack1;
	Config.Attack2 = MontageAttack2;
	Config.Attack3 = MontageAttack3;
	Config.HeavySlam = MontageHeavySlam;
	Config.HeavyLunge = MontageHeavyLunge;
	Config.SprintLunge = MontageSprintLunge;
	Config.Block = MontageBlock;
	Config.Cast1H = MontageCast1H;
	Config.Cast2H = MontageCast2H;

	// Fallback guarantees: no animation should ever be null
	if (!AnimAttack1) AnimAttack1 = AnimLocoIdle;
	if (!AnimAttack2) AnimAttack2 = AnimAttack1;
	if (!AnimAttack3) AnimAttack3 = AnimAttack2;
	if (!AnimAttack4) AnimAttack4 = AnimAttack3;
	if (!AnimAttackMedium) AnimAttackMedium = AnimAttack2;
	if (!AnimHeavySlam) AnimHeavySlam = AnimAttack4;
	if (!AnimHeavyLunge) AnimHeavyLunge = AnimAttack3;
	if (!AnimSprintLunge) AnimSprintLunge = AnimAttack1;
	if (!AnimBlock) AnimBlock = AnimLocoIdle;
	if (!AnimCast1H) AnimCast1H = AnimAttack1;
	if (!AnimCast2H) AnimCast2H = AnimAttack4;
}

void ABattleCharacter::SwitchWeaponStyle(EWeaponStyle NewStyle)
{
	CurrentWeaponStyle = NewStyle;
	LoadWeaponStyleAnimations();
}

void ABattleCharacter::PawnClientRestart()
{
	Super::PawnClientRestart();

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		PC->SetControlRotation(FRotator(-18.0f, GetActorRotation().Yaw, 0.0f));
		PC->SetInputMode(FInputModeGameOnly());
		PC->SetShowMouseCursor(false);
		if (PC->PlayerCameraManager)
		{
			PC->PlayerCameraManager->ViewPitchMin = -65.0f;
			PC->PlayerCameraManager->ViewPitchMax = 45.0f;
		}

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

void ABattleCharacter::BeginPlay()
{
	Super::BeginPlay();

	if (HeadMesh && GetMesh())
	{
		HeadMesh->SetLeaderPoseComponent(GetMesh());
	}
	CurrentHP = MaxHP;
	CurrentTP = MaxTP;

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

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
			FVector(0.0f, 0.0f, -96.0f),
			FRotator(0.0f, -90.0f, 0.0f)
		);
		MeshComp->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
		MeshComp->SetAnimationMode(EAnimationMode::AnimationBlueprint);
		MeshComp->SetAnimInstanceClass(UIsekaiGameplayAnimInstance::StaticClass());
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

	LoadWeaponStyleAnimations();

	CurrentLocoState = ELocomotionAnimState::Idle;

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->bOrientRotationToMovement = true;
		GetCharacterMovement()->bUseControllerDesiredRotation = false;
		GetCharacterMovement()->RotationRate = FRotator(0.0f, 1080.0f, 0.0f);
		GetCharacterMovement()->BrakingDecelerationWalking = 2048.0f;
		GetCharacterMovement()->MaxAcceleration = 2048.0f;
		GetCharacterMovement()->GroundFriction = 8.0f;
		GetCharacterMovement()->bUseSeparateBrakingFriction = true;
		GetCharacterMovement()->BrakingFriction = 8.0f;
		GetCharacterMovement()->MaxWalkSpeed = 420.0f;
		GetCharacterMovement()->GetNavAgentPropertiesRef().bCanCrouch = true;
		GetCharacterMovement()->bRunPhysicsWithNoController = false;
	}

	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		PC->SetControlRotation(FRotator(-18.0f, GetActorRotation().Yaw, 0.0f));
		PC->SetInputMode(FInputModeGameOnly());
		PC->SetShowMouseCursor(false);
		if (PC->PlayerCameraManager)
		{
			PC->PlayerCameraManager->ViewPitchMin = -65.0f;
			PC->PlayerCameraManager->ViewPitchMax = 45.0f;
		}

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

	// Auto-lock onto closest enemy at start of battle
	ToggleTargetLock();
}

void ABattleCharacter::ResetLocomotionToInput()
{
	if (bIsDodging || !GetMesh()) return;

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->bOrientRotationToMovement = true;
	}
}

void ABattleCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	UpdateCombatCamera(DeltaTime);

	// Hit-Stop Micro-Freeze (Anime Impact Pause)
	if (HitStopTimer > 0.0f)
	{
		HitStopTimer -= DeltaTime;
		if (HitStopTimer <= 0.0f)
		{
			CustomTimeDilation = 1.0f;
		}
	}

	// Counter Edge Window Decay
	if (bCanCounterEdge)
	{
		CounterEdgeWindowTimer -= DeltaTime;
		if (CounterEdgeWindowTimer <= 0.0f)
		{
			bCanCounterEdge = false;
			CounterEdgeWindowTimer = 0.0f;
		}
	}

	// AG (Arte Gauge / CC) Regeneration
	if (!bIsAttacking && !bIsDodging)
	{
		CurrentAG = FMath::Min(MaxAG, CurrentAG + AGRegenRate * DeltaTime);
	}

	// Overlimit State Decay
	if (OverlimitState.bIsActive)
	{
		OverlimitState.ActiveTimer -= DeltaTime;
		if (OverlimitState.ActiveTimer <= 0.0f)
		{
			OverlimitState.bIsActive = false;
			OverlimitState.OverlimitLevel = 0;
			OverlimitState.CurrentGauge = 0.0f;
		}
	}

	// Tales Escape System (Boundary Wall or Holding Escape)
	const float DistFromCenter = GetActorLocation().Size2D();
	const bool bNearBoundary = (DistFromCenter >= 1600.0f);
	const bool bMovingOutward = (FVector::DotProduct(GetVelocity().GetSafeNormal2D(), GetActorLocation().GetSafeNormal2D()) > 0.15f);

	if ((bNearBoundary && bMovingOutward) || bIsHoldingEscapeKey)
	{
		bIsEscaping = true;
		EscapeTimer += DeltaTime;
		if (EscapeTimer >= EscapeDuration)
		{
			EscapeTimer = EscapeDuration;
			if (ABattleGameMode* GM = Cast<ABattleGameMode>(UGameplayStatics::GetGameMode(this)))
			{
				GM->EscapeBattle();
			}
		}
	}
	else
	{
		bIsEscaping = false;
		EscapeTimer = FMath::Max(0.0f, EscapeTimer - DeltaTime * 2.0f);
	}

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

		if (Alpha >= 1.0f)
		{
			bIsDodging = false;
			if (GetCharacterMovement())
			{
				GetCharacterMovement()->bOrientRotationToMovement = true;
			}
			ResetLocomotionToInput();
		}
	}

	// 2. Attack / Cast Action State with Tales-Style Cancel Windows & Input Buffering
	if (bIsAttacking)
	{
		AttackTimer += DeltaTime;

		// Once the cancel window opens, check if the player buffered an attack strike!
		if (AttackTimer >= AttackCancelWindow)
		{
			if (bBufferedNormalAttack)
			{
				bBufferedNormalAttack = false;
				bBufferedHeavyAttack = false;
				bIsAttacking = false;
				PerformNormalAttack();
				return;
			}
			if (bBufferedHeavyAttack)
			{
				bBufferedHeavyAttack = false;
				bBufferedNormalAttack = false;
				bIsAttacking = false;
				PerformHeavyAttack();
				return;
			}
		}

		// Movement cancel during recovery follow-through as soon as active swing window finishes
		const bool bHasMoveInput = GetLastMovementInputVector().SizeSquared2D() > 0.01f;
		if ((AttackTimer >= AttackCancelWindow && bHasMoveInput) || (AttackTimer >= AttackDuration))
		{
			bIsAttacking = false;
			bBufferedNormalAttack = false;
			bBufferedHeavyAttack = false;
			ResetLocomotionToInput();
		}
	}

	// Safety check only if fallen far below the arena floor (floor is at Z=-5)
	const FVector Loc = GetActorLocation();
	if (Loc.Z < -600.0f)
	{
		TeleportTo(FVector(0.0f, -400.0f, 60.0f), GetActorRotation(), false, true);
	}
}

void ABattleCharacter::UpdateCombatCamera(float DeltaTime)
{
	// Only orient rotation to movement when not actively locked into an attack or evasive roll
	if (GetCharacterMovement() && !bIsAttacking && !bIsDodging)
	{
		GetCharacterMovement()->bOrientRotationToMovement = true;
	}

	if (!LockedTarget || !LockedTarget->IsAlive())
	{
		LockedTarget = nullptr;
		return;
	}

	// In modern battle mode, the player has full 360 camera control and free movement orientation.
	// Only attacks and artes will orient the character towards the target.
}

void ABattleCharacter::ToggleTargetLock()
{
	const FVector PlayerLoc = GetActorLocation();
	ABattleEnemy* BestTarget = nullptr;
	float ClosestDist = 3000.0f;

	for (TActorIterator<ABattleEnemy> It(GetWorld()); It; ++It)
	{
		ABattleEnemy* Enemy = *It;
		if (!Enemy || !Enemy->IsAlive()) continue;

		float Dist = FVector::Dist(PlayerLoc, Enemy->GetActorLocation());
		if (Dist < ClosestDist && Enemy != LockedTarget)
		{
			ClosestDist = Dist;
			BestTarget = Enemy;
		}
	}

	if (BestTarget)
	{
		LockedTarget = BestTarget;
	}
	else
	{
		// If no other target, try the closest living one
		for (TActorIterator<ABattleEnemy> It(GetWorld()); It; ++It)
		{
			ABattleEnemy* Enemy = *It;
			if (!Enemy || !Enemy->IsAlive()) continue;
			LockedTarget = Enemy;
			break;
		}
	}
}

// ── Combat Actions & Visual Artes ─────────────────────────────

void ABattleCharacter::PlayCombatMontageOrSequence(UAnimMontage* Montage, UAnimSequence* FallbackSeq, float PlayRate)
{
	if (Montage)
	{
		const float Duration = PlayAnimMontage(Montage, PlayRate);
		if (Duration > 0.0f)
		{
			return;
		}
	}
	PlayAnimMontageSafe(FallbackSeq, PlayRate);
}

void ABattleCharacter::PlayAnimMontageSafe(UAnimSequence* AnimSeq, float PlayRate)
{
	if (!AnimSeq)
	{
		AnimSeq = AnimAttack1 ? AnimAttack1 : AnimLocoIdle;
	}
	if (!AnimSeq || !GetMesh()) return;

	if (UAnimInstance* AnimInst = GetMesh()->GetAnimInstance())
	{
		AnimInst->PlaySlotAnimationAsDynamicMontage(AnimSeq, FName("DefaultSlot"), 0.12f, 0.18f, PlayRate);
	}
}

void ABattleCharacter::OnSprintStarted()
{
	bIsSprinting = true;
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = 680.0f;
	}
}

void ABattleCharacter::OnSprintEnded()
{
	bIsSprinting = false;
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = 420.0f;
	}
}

void ABattleCharacter::PerformSprintLungeAttack()
{
	const float CurrentTime = GetWorld()->GetTimeSeconds();
	if (bIsAttacking && AttackTimer < AttackCancelWindow) return;
	if (!bIsAttacking && (CurrentTime - LastAttackTime < AttackCooldown)) return;

	LastAttackTime = CurrentTime;
	ComboStep = 1;

	// Orient to movement direction or locked target
	FVector LungeDir = GetLastMovementInputVector().GetSafeNormal2D();
	if (LungeDir.IsNearlyZero() && GetCharacterMovement())
	{
		LungeDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
	}
	if (LungeDir.IsNearlyZero())
	{
		LungeDir = GetActorForwardVector();
	}

	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		LungeDir = FRotationMatrix(FRotator(0.0f, LookRot.Yaw, 0.0f)).GetUnitAxis(EAxis::X);
	}

	SetActorRotation(FRotator(0.0f, LungeDir.ToOrientationRotator().Yaw, 0.0f));

	bBufferedNormalAttack = false;
	bBufferedHeavyAttack = false;

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->StopMovementImmediately();
		GetCharacterMovement()->bOrientRotationToMovement = false;
	}

	UAnimSequence* AnimToPlay = AnimSprintLunge ? AnimSprintLunge : (AnimHeavyLunge ? AnimHeavyLunge : AnimAttack1);
	const float PlayRate = 1.65f;
	PlayCombatMontageOrSequence(MontageSprintLunge, AnimToPlay, PlayRate);

	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = 0.55f;
	AttackCancelWindow = 0.28f;
	CurrentLocoState = ELocomotionAnimState::Action;
	GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));

	// Controlled step forward
	LaunchCharacter(LungeDir * 120.0f, true, false);

	// Piercing hit detection with extended range
	const float Damage = BaseAttackPower * 2.2f;
	const FVector Start = GetActorLocation();
	const FVector End = Start + LungeDir * 340.0f;

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(95.0f);
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
			{
				if (Enemy->IsAlive())
				{
					Enemy->ReceiveArteDamage(Damage, EElement::Fire, LungeDir, false);
					TriggerHitStop(0.045f, 0.05f);
					if (SoundHitImpact)
					{
						UGameplayStatics::PlaySoundAtLocation(this, SoundHitImpact, Hit.ImpactPoint, 1.15f, 1.05f);
					}
					break;
				}
			}
		}
	}

	if (SoundSwing)
	{
		UGameplayStatics::PlaySoundAtLocation(this, SoundSwing, GetActorLocation(), 1.0f, 1.1f);
	}
}

void ABattleCharacter::PerformCounterEdge()
{
	bCanCounterEdge = false;
	CounterEdgeWindowTimer = 0.0f;
	CustomTimeDilation = 1.0f;

	const float CurrentTime = GetWorld()->GetTimeSeconds();
	LastAttackTime = CurrentTime;
	ComboStep = 1;

	// Instant flash warp towards locked target or forward
	FVector StrikeDir = GetActorForwardVector();
	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
		StrikeDir = FRotationMatrix(FRotator(0.0f, LookRot.Yaw, 0.0f)).GetUnitAxis(EAxis::X);

		// Flash thrust forward towards enemy
		const FVector TargetPos = LockedTarget->GetActorLocation() - StrikeDir * 120.0f;
		TeleportTo(FVector(TargetPos.X, TargetPos.Y, GetActorLocation().Z), GetActorRotation(), false, true);
	}

	UAnimSequence* CounterAnim = AnimHeavyLunge ? AnimHeavyLunge : (AnimAttack2 ? AnimAttack2 : AnimAttack1);
	PlayCombatMontageOrSequence(MontageHeavyLunge ? MontageHeavyLunge : MontageAttack2, CounterAnim, 1.85f);

	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = 0.52f;
	AttackCancelWindow = 0.25f;
	CurrentLocoState = ELocomotionAnimState::Action;

	// Counter Edge high-impact critical damage
	const float Damage = GetEffectiveAttackPower() * 3.2f;
	TriggerHitStop(0.08f, 0.02f); // Cinematic Counter Edge freeze

	if (SoundSwing)
	{
		UGameplayStatics::PlaySoundAtLocation(this, SoundSwing, GetActorLocation(), 1.2f, 1.3f);
	}

	if (LockedTarget && LockedTarget->IsAlive())
	{
		float Dealt = LockedTarget->ReceiveArteDamage(Damage, EElement::Holy, StrikeDir, true);
		CurrentTP = FMath::Min(GetEffectiveMaxTP(), CurrentTP + 15.0f);
		OverlimitState.CurrentGauge = FMath::Min(OverlimitState.MaxGauge, OverlimitState.CurrentGauge + 6.0f);

		if (SoundHitImpact)
		{
			UGameplayStatics::PlaySoundAtLocation(this, SoundHitImpact, LockedTarget->GetActorLocation(), 1.4f, 1.2f);
		}

		if (APlayerController* PC = Cast<APlayerController>(GetController()))
		{
			if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
			{
				HUD->RegisterComboHit(Dealt);
			}
		}
	}
}

void ABattleCharacter::PerformAerialAttack()
{
	const float CurrentTime = GetWorld()->GetTimeSeconds();
	LastAttackTime = CurrentTime;

	// Orient to locked enemy
	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
	}

	// Halt downward falling velocity briefly for crisp air juggles
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->Velocity.Z = FMath::Max(120.0f, GetCharacterMovement()->Velocity.Z * 0.2f);
	}

	UAnimSequence* AnimToPlay = AnimAttack1;
	PlayCombatMontageOrSequence(MontageAttack1, AnimToPlay, 1.75f);

	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = 0.40f;
	AttackCancelWindow = 0.18f;
	CurrentLocoState = ELocomotionAnimState::Action;

	const FVector Forward = GetActorForwardVector();
	const float BaseDamage = GetEffectiveAttackPower() * 1.25f;
	const FVector Start = GetActorLocation();
	const FVector End = Start + Forward * 240.0f;

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(100.0f);
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
			{
				if (Enemy->IsAlive())
				{
					float Dealt = Enemy->ReceiveArteDamage(BaseDamage, EElement::Wind, Forward, false);
					CurrentTP = FMath::Min(GetEffectiveMaxTP(), CurrentTP + 8.0f);
					TriggerHitStop(0.04f, 0.05f);

					if (SoundHitImpact)
					{
						UGameplayStatics::PlaySoundAtLocation(this, SoundHitImpact, Enemy->GetActorLocation());
					}

					if (APlayerController* PC = Cast<APlayerController>(GetController()))
					{
						if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
						{
							HUD->RegisterComboHit(Dealt);
						}
					}
					break;
				}
			}
		}
	}

	if (SoundSwing)
	{
		UGameplayStatics::PlaySoundAtLocation(this, SoundSwing, GetActorLocation(), 1.0f, 1.2f);
	}
}

void ABattleCharacter::PerformAerialDive()
{
	const float CurrentTime = GetWorld()->GetTimeSeconds();
	LastAttackTime = CurrentTime;

	// Orient to locked enemy
	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
	}

	// Air-to-Ground dive slam downward impulse
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->Velocity = GetActorForwardVector() * 250.0f + FVector(0.0f, 0.0f, -1400.0f);
	}

	UAnimSequence* AnimToPlay = AnimHeavySlam ? AnimHeavySlam : (AnimAttack4 ? AnimAttack4 : AnimAttack1);
	PlayCombatMontageOrSequence(MontageHeavySlam ? MontageHeavySlam : MontageAttack4, AnimToPlay, 1.80f);

	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = 0.65f;
	AttackCancelWindow = 0.35f;
	CurrentLocoState = ELocomotionAnimState::Action;

	const FVector Forward = GetActorForwardVector();
	const float BaseDamage = GetEffectiveAttackPower() * 2.6f;
	const FVector Start = GetActorLocation();
	const FVector End = Start + Forward * 260.0f + FVector(0.0f, 0.0f, -150.0f);

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(140.0f);
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
			{
				if (Enemy->IsAlive())
				{
					float Dealt = Enemy->ReceiveArteDamage(BaseDamage, EElement::Earth, Forward, true);
					CurrentTP = FMath::Min(GetEffectiveMaxTP(), CurrentTP + 14.0f);
					TriggerHitStop(0.07f, 0.03f); // Powerful dive slam impact freeze

					if (SoundHitImpact)
					{
						UGameplayStatics::PlaySoundAtLocation(this, SoundHitImpact, Enemy->GetActorLocation(), 1.25f, 0.95f);
					}

					if (APlayerController* PC = Cast<APlayerController>(GetController()))
					{
						if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
						{
							HUD->RegisterComboHit(Dealt);
						}
					}
					break;
				}
			}
		}
	}

	if (SoundSwing)
	{
		UGameplayStatics::PlaySoundAtLocation(this, SoundSwing, GetActorLocation(), 1.1f, 0.95f);
	}
}

void ABattleCharacter::PerformHeavyAttack()
{
	const float CurrentTime = GetWorld()->GetTimeSeconds();

	if (bIsAttacking)
	{
		if (AttackTimer < AttackCancelWindow)
		{
			bBufferedHeavyAttack = true;
			bBufferedNormalAttack = false;
			return;
		}
	}
	else if (CurrentTime - LastAttackTime < AttackCooldown)
	{
		bBufferedHeavyAttack = true;
		return;
	}

	bBufferedHeavyAttack = false;
	bBufferedNormalAttack = false;

	// Tales of Arise Aerial Dive Finisher:
	// If heavy attack is pressed while falling, execute Air-to-Ground Helm Splitter dive!
	if (GetCharacterMovement() && GetCharacterMovement()->IsFalling())
	{
		PerformAerialDive();
		return;
	}

	LastAttackTime = CurrentTime;
	ComboStep = 4;

	const bool bHasMoveInput = GetLastMovementInputVector().SizeSquared2D() > 0.01f ||
		(GetCharacterMovement() && GetCharacterMovement()->Velocity.SizeSquared2D() > 4000.0f);

	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
	}

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->StopMovementImmediately();
		GetCharacterMovement()->bOrientRotationToMovement = false;
	}

	const FVector Forward = GetActorForwardVector();
	UAnimSequence* AnimToPlay = nullptr;
	const float Damage = BaseAttackPower * 2.4f;

	if (bHasMoveInput && AnimHeavyLunge)
	{
		// Forward Heavy Lunge Finisher
		AnimToPlay = AnimHeavyLunge;
		PlayCombatMontageOrSequence(MontageHeavyLunge, AnimToPlay, 1.50f);
		LaunchCharacter(Forward * 80.0f, true, false);
		AttackDuration = 0.60f;
		AttackCancelWindow = 0.32f;
	}
	else
	{
		// Downward Heavy Leap Slam Finisher
		AnimToPlay = AnimHeavySlam ? AnimHeavySlam : (AnimAttack4 ? AnimAttack4 : AnimAttack1);
		PlayCombatMontageOrSequence(MontageHeavySlam ? MontageHeavySlam : MontageAttack4, AnimToPlay, 1.65f);
		LaunchCharacter(Forward * 40.0f + FVector(0.0f, 0.0f, 80.0f), true, false);
		AttackDuration = 0.68f;
		AttackCancelWindow = 0.35f;
	}

	bIsAttacking = true;
	AttackTimer = 0.0f;
	CurrentLocoState = ELocomotionAnimState::Action;
	GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));

	// Heavy trace detection
	const FVector Start = GetActorLocation();
	const FVector End = Start + Forward * 290.0f;

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(110.0f);
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
			{
				if (Enemy->IsAlive())
				{
					float Dealt = Enemy->ReceiveArteDamage(Damage, EElement::Earth, Forward, true);
					CurrentTP = FMath::Min(MaxTP, CurrentTP + 12.0f);
					TriggerHitStop(0.055f, 0.04f);
					OverlimitState.CurrentGauge = FMath::Min(OverlimitState.MaxGauge, OverlimitState.CurrentGauge + 3.0f);

					if (APlayerController* PC = Cast<APlayerController>(GetController()))
					{
						if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
						{
							HUD->RegisterComboHit(Dealt);
						}
					}
					break;
				}
			}
		}
	}

	// Radial ground shockwave impact on slam
	if (!bHasMoveInput || !AnimHeavyLunge)
	{
		const FVector ImpactPoint = Start + Forward * 180.0f;
		TArray<FHitResult> AoEHits;
		FCollisionShape AoESphere = FCollisionShape::MakeSphere(160.0f);
		if (GetWorld()->SweepMultiByChannel(AoEHits, ImpactPoint, ImpactPoint + FVector(0.0f, 0.0f, 1.0f), FQuat::Identity, ECC_Pawn, AoESphere, Params))
		{
			for (const FHitResult& AoEHit : AoEHits)
			{
				if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(AoEHit.GetActor()))
				{
					if (Enemy->IsAlive())
					{
						FVector KnockbackDir = (Enemy->GetActorLocation() - ImpactPoint).GetSafeNormal2D();
						if (KnockbackDir.IsNearlyZero()) KnockbackDir = Forward;
						Enemy->ReceiveArteDamage(Damage * 0.75f, EElement::Earth, KnockbackDir);
					}
				}
			}
		}
	}
}

void ABattleCharacter::PerformNormalAttack()
{
	const float CurrentTime = GetWorld()->GetTimeSeconds();

	// Tales of Arise Action Chaining with Input Buffering:
	if (bIsAttacking)
	{
		if (AttackTimer < AttackCancelWindow)
		{
			// Buffer the attack so rapid clicks during active frames are NEVER dropped!
			bBufferedNormalAttack = true;
			bBufferedHeavyAttack = false;
			return;
		}
	}
	else if (CurrentTime - LastAttackTime < AttackCooldown)
	{
		bBufferedNormalAttack = true;
		return;
	}

	bBufferedNormalAttack = false;
	bBufferedHeavyAttack = false;

	// Check if Sprint is active (either via Shift key or bIsSprinting)
	bool bSprintActive = bIsSprinting;
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (PC->IsInputKeyDown(EKeys::LeftShift) || PC->IsInputKeyDown(EKeys::RightShift))
		{
			bSprintActive = true;
		}
	}

	const bool bHasMoveInput = GetLastMovementInputVector().SizeSquared2D() > 0.01f ||
		(GetCharacterMovement() && GetCharacterMovement()->Velocity.SizeSquared2D() > 4000.0f);

	// Tales of Arise Counter Edge Trigger:
	// If the player presses Attack within the Perfect Dodge slow-mo window, unleash an instant Counter Edge thrust!
	if (bCanCounterEdge)
	{
		PerformCounterEdge();
		return;
	}

	// Tales of Arise Aerial Attack Branch:
	// If the player presses Attack while airborne, execute aerial slash!
	if (GetCharacterMovement() && GetCharacterMovement()->IsFalling())
	{
		PerformAerialAttack();
		return;
	}

	// ONLY lunge if Shift AND a movement key is pressed!
	if (bSprintActive && bHasMoveInput)
	{
		PerformSprintLungeAttack();
		return;
	}

	// Combo progression: 1 (Light 1) -> 2 (Light 2) -> 3 (Medium) -> 4 (Heavy Finisher)
	if (CurrentTime - LastAttackTime > 1.85f)
	{
		ComboStep = 1;
	}
	else
	{
		ComboStep = (ComboStep % 4) + 1;
	}

	LastAttackTime = CurrentTime;

	// Orient to locked enemy upon initiating an attack strike
	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
	}

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->StopMovementImmediately();
		GetCharacterMovement()->bOrientRotationToMovement = false;
	}

	UAnimSequence* AnimToPlay = AnimAttack1;
	float PlayRate = 1.60f;
	float Duration = 0.55f;
	float CancelWin = 0.48f;
	float DamageMultiplier = 1.0f;
	float ForwardLaunchForce = 0.0f; // STRICTLY ZERO LUNGE FOR LIGHT ATTACKS
	float TraceRange = 220.0f;
	float TraceRadius = 85.0f;
	bool bIsHeavyFinisher = false;

	switch (ComboStep)
	{
	case 1: // Light 1: Quick crisp slash in-place
		AnimToPlay = AnimAttack1;
		PlayRate = 1.60f;
		Duration = 0.42f;
		CancelWin = 0.20f;
		DamageMultiplier = 1.0f;
		ForwardLaunchForce = 0.0f;
		TraceRange = 220.0f;
		break;

	case 2: // Light 2: Follow-up cross-slash in-place
		AnimToPlay = AnimAttack2 ? AnimAttack2 : AnimAttack1;
		PlayRate = 1.65f;
		Duration = 0.45f;
		CancelWin = 0.22f;
		DamageMultiplier = 1.15f;
		ForwardLaunchForce = 0.0f;
		TraceRange = 220.0f;
		break;

	case 3: // Medium: Wider cleave in-place
		AnimToPlay = AnimAttackMedium ? AnimAttackMedium : AnimAttack1;
		PlayRate = 1.60f;
		Duration = 0.48f;
		CancelWin = 0.24f;
		DamageMultiplier = 1.5f;
		ForwardLaunchForce = 0.0f; // In-place, zero ice-skating
		TraceRange = 250.0f;
		TraceRadius = 100.0f;
		break;

	case 4: // Heavy Finisher: Downward Slam or Heavy Lunge
	default:
		bIsHeavyFinisher = true;
		if (bHasMoveInput && AnimHeavyLunge)
		{
			AnimToPlay = AnimHeavyLunge;
			PlayRate = 1.50f;
			Duration = 0.60f;
			CancelWin = 0.32f;
			DamageMultiplier = 2.2f;
			ForwardLaunchForce = 60.0f;
			TraceRange = 300.0f;
		}
		else
		{
			AnimToPlay = AnimHeavySlam ? AnimHeavySlam : (AnimAttack4 ? AnimAttack4 : AnimAttack1);
			PlayRate = 1.65f;
			Duration = 0.68f;
			CancelWin = 0.35f;
			DamageMultiplier = 2.4f;
			ForwardLaunchForce = 40.0f;
			TraceRange = 280.0f;
			TraceRadius = 120.0f;
		}
		break;
	}

	if (AnimToPlay && AnimToPlay->GetPlayLength() > 0.05f)
	{
		const float RealDuration = AnimToPlay->GetPlayLength() / PlayRate;
		Duration = FMath::Clamp(RealDuration, 0.38f, 0.68f);
		CancelWin = FMath::Clamp(Duration * 0.50f, 0.18f, 0.35f);
	}

	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = Duration;
	AttackCancelWindow = CancelWin;
	CurrentLocoState = ELocomotionAnimState::Action;
	GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));

	UAnimMontage* MontageToPlay = MontageAttack1;
	switch (ComboStep)
	{
	case 1:
		MontageToPlay = MontageAttack1;
		break;
	case 2:
		MontageToPlay = MontageAttack2 ? MontageAttack2 : MontageAttack1;
		break;
	case 3:
		MontageToPlay = MontageAttackMedium ? MontageAttackMedium : MontageAttack1;
		break;
	case 4:
	default:
		MontageToPlay = (bHasMoveInput && MontageHeavyLunge) ? MontageHeavyLunge : (MontageHeavySlam ? MontageHeavySlam : MontageAttack4);
		break;
	}
	PlayCombatMontageOrSequence(MontageToPlay, AnimToPlay, PlayRate);

	const FVector Forward = GetActorForwardVector();

	// Apply movement impulse ONLY when specifically designed for this tier
	if (ForwardLaunchForce > 0.0f)
	{
		if (bIsHeavyFinisher && !bHasMoveInput)
		{
			// Downward slam leap
			LaunchCharacter(Forward * ForwardLaunchForce + FVector(0.0f, 0.0f, 100.0f), true, false);
		}
		else
		{
			LaunchCharacter(Forward * ForwardLaunchForce, true, false);
		}
	}

	// Forward trace for hit detection
	const float BaseDamage = GetEffectiveAttackPower() * DamageMultiplier;
	const FVector Start = GetActorLocation();
	const FVector End = Start + Forward * TraceRange;

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(TraceRadius);
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
			{
				if (Enemy->IsAlive())
				{
					float Damage = BaseDamage;
					if (Enemy->IsDemon() && TitleManager && TitleManager->HasPassivePerk(FName("DemonBane")))
					{
						Damage *= 1.30f; // +30% damage against demonkind from mastered Demon Slayer title
					}

					float Dealt = Enemy->ReceiveArteDamage(Damage, EElement::Fire, Forward, bIsHeavyFinisher);
					CurrentTP = FMath::Min(GetEffectiveMaxTP(), CurrentTP + (bIsHeavyFinisher ? 12.0f : 6.0f));
					TriggerHitStop(bIsHeavyFinisher ? 0.055f : 0.038f, 0.05f);
					OverlimitState.CurrentGauge = FMath::Min(OverlimitState.MaxGauge, OverlimitState.CurrentGauge + (bIsHeavyFinisher ? 3.0f : 1.5f));

					// Tales of Arise Boost Strike Auto-Finisher Trigger on Broken Boss/Foe
					if (bIsHeavyFinisher && Enemy->CanBoostStrike())
					{
						TriggerHitStop(0.15f, 0.02f); // Cinematic Boost Strike dual freeze!
						Enemy->ReceiveArteDamage(Damage * 2.5f, EElement::Holy, Forward, true);
						if (SoundOverlimitBurst)
						{
							UGameplayStatics::PlaySoundAtLocation(this, SoundOverlimitBurst, Enemy->GetActorLocation(), 1.4f, 1.2f);
						}
					}

					if (SoundHitImpact)
					{
						const float PitchVariance = FMath::RandRange(0.95f, 1.15f);
						UGameplayStatics::PlaySoundAtLocation(this, SoundHitImpact, Enemy->GetActorLocation(), 1.0f, PitchVariance);
					}

					if (APlayerController* PC = Cast<APlayerController>(GetController()))
					{
						if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
						{
							HUD->RegisterComboHit(Dealt);
						}
					}
					break;
				}
			}
		}
	}

	// Shockwave ground effect on Heavy Slam
	if (bIsHeavyFinisher && (!bHasMoveInput || !AnimHeavyLunge))
	{
		const FVector ImpactPoint = Start + Forward * 180.0f;
		TArray<FHitResult> AoEHits;
		FCollisionShape AoESphere = FCollisionShape::MakeSphere(160.0f);
		if (GetWorld()->SweepMultiByChannel(AoEHits, ImpactPoint, ImpactPoint + FVector(0.0f, 0.0f, 1.0f), FQuat::Identity, ECC_Pawn, AoESphere, Params))
		{
			for (const FHitResult& AoEHit : AoEHits)
			{
				if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(AoEHit.GetActor()))
				{
					if (Enemy->IsAlive())
					{
						FVector KnockbackDir = (Enemy->GetActorLocation() - ImpactPoint).GetSafeNormal2D();
						if (KnockbackDir.IsNearlyZero()) KnockbackDir = Forward;
						Enemy->ReceiveArteDamage(BaseDamage * 0.75f, EElement::Earth, KnockbackDir);
					}
				}
			}
		}
	}
}

void ABattleCharacter::CastArte(int32 SlotIndex)
{
	float TPCost = 0.0f;
	float Damage = 0.0f;
	EElement Element = EElement::Fire;
	FName ProjectileShape = "spear";

	const float EffectiveAtk = GetEffectiveAttackPower();

	switch (SlotIndex)
	{
	case 1: // Ignis Spear (Fire Projectile)
		TPCost = 12.0f;
		Damage = EffectiveAtk * 2.2f;
		Element = EElement::Fire;
		ProjectileShape = "spear";
		break;
	case 2: // Aqua Surge (Water Wave + Heal)
		TPCost = 15.0f;
		Damage = EffectiveAtk * 1.8f;
		Element = EElement::Water;
		ProjectileShape = "wave";
		CurrentHP = FMath::Min(GetEffectiveMaxHP(), CurrentHP + 35.0f); // Heal player!
		break;
	case 3: // Terra Wall (Earth Construct)
		TPCost = 18.0f;
		Damage = EffectiveAtk * 2.8f;
		Element = EElement::Earth;
		ProjectileShape = "mine";
		break;
	case 4: // Ventus Blade (Wind Slices)
		TPCost = 14.0f;
		Damage = EffectiveAtk * 2.0f;
		Element = EElement::Wind;
		ProjectileShape = "spear";
		break;
	default:
		return;
	}

	if (CurrentTP < TPCost)
	{
		return; // Insufficient TP
	}

	CurrentTP -= TPCost;

	if (GetCharacterMovement())
	{
		GetCharacterMovement()->StopMovementImmediately();
		GetCharacterMovement()->bOrientRotationToMovement = false;
	}

	// Play Magic Casting Animation
	UAnimSequence* CastAnimToPlay = (SlotIndex == 3 || SlotIndex == 2) ? AnimCast2H : AnimCast1H;
	if (!CastAnimToPlay) CastAnimToPlay = AnimAttack1;

	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = 0.50f;
	AttackCancelWindow = 0.25f;
	CurrentLocoState = ELocomotionAnimState::Action;
	UAnimMontage* CastMontage = (SlotIndex == 3 || SlotIndex == 2) ? MontageCast2H : MontageCast1H;
	PlayCombatMontageOrSequence(CastMontage, CastAnimToPlay, 1.25f);

	UWorld* World = GetWorld();
	if (!World) return;


	const FVector SpawnLoc = GetActorLocation() + GetActorForwardVector() * 100.0f + FVector(0.0f, 0.0f, 30.0f);
	FRotator AimRot = GetActorRotation();

	if (LockedTarget && LockedTarget->IsAlive())
	{
		FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
		SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
		AimRot = (LockedTarget->GetActorLocation() - SpawnLoc).ToOrientationRotator();
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.Owner = this;
	SpawnParams.Instigator = this;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	if (SlotIndex == 3)
	{
		// Spawn rising Earth Wall Construct
		const FVector WallLoc = GetActorLocation() + GetActorForwardVector() * 260.0f;
		if (AEarthWallConstruct* Wall = World->SpawnActor<AEarthWallConstruct>(AEarthWallConstruct::StaticClass(), WallLoc, AimRot, SpawnParams))
		{
			Wall->InitWall(EElement::Earth, 1.0f);
		}
	}
	else
	{
		// Spawn Visible Elemental Spell Projectile (Ignis Spear, Aqua Surge, Ventus Blade)
		if (ASpellProjectile* Proj = World->SpawnActor<ASpellProjectile>(ASpellProjectile::StaticClass(), SpawnLoc, AimRot, SpawnParams))
		{
			Proj->BaseDamage = Damage;
			Proj->InitProjectile(Element, ProjectileShape, 1.0f);
		}
	}

	// AoE check in front to register immediate close-range hits
	const FVector Forward = GetActorForwardVector();
	const FVector End = SpawnLoc + Forward * 350.0f;

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(130.0f);
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);

	if (World->SweepMultiByChannel(Hits, SpawnLoc, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
			{
				if (Enemy->IsAlive())
				{
					float Dealt = Enemy->ReceiveArteDamage(Damage, Element, Forward);
					if (APlayerController* PC = Cast<APlayerController>(GetController()))
					{
						if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
						{
							HUD->RegisterComboHit(Dealt);
						}
					}
				}
			}
		}
	}

	// Keep feet firmly planted when casting magic - no artificial sliding
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->StopMovementImmediately();
	}
}

float ABattleCharacter::GetEffectiveAttackPower() const
{
	float Total = BaseAttackPower;
	if (TitleManager)
	{
		Total += TitleManager->GetTotalStatBonus(ETitleStatType::PhysicalAtk);
	}
	if (SkillGrid)
	{
		Total += SkillGrid->GetTotalSkillStatBonus(ETitleStatType::PhysicalAtk);
	}
	if (bIsGrudgingStrike)
	{
		Total *= 0.75f;
	}
	return Total;
}


float ABattleCharacter::GetEffectiveMaxHP() const
{
	float Total = MaxHP;
	if (TitleManager)
	{
		Total += TitleManager->GetTotalStatBonus(ETitleStatType::MaxHP);
	}
	if (SkillGrid)
	{
		Total += SkillGrid->GetTotalSkillStatBonus(ETitleStatType::MaxHP);
	}
	return Total;
}

float ABattleCharacter::GetEffectiveMaxTP() const
{
	float Total = MaxTP;
	if (TitleManager)
	{
		Total += TitleManager->GetTotalStatBonus(ETitleStatType::MaxTP);
	}
	if (SkillGrid)
	{
		Total += SkillGrid->GetTotalSkillStatBonus(ETitleStatType::MaxTP);
	}
	return Total;
}

void ABattleCharacter::SetFreeRun(bool bEnable)
{
	bIsFreeRunning = bEnable;
	if (GetCharacterMovement())
	{
		GetCharacterMovement()->MaxWalkSpeed = bEnable ? 540.0f : 420.0f;
	}
}

void ABattleCharacter::SetPaletteModifier(bool bActive)
{
	bPaletteModifierActive = bActive;
}

void ABattleCharacter::TriggerHitStop(float Duration, float Dilation)
{
	CustomTimeDilation = Dilation;
	HitStopTimer = Duration;
}

void ABattleCharacter::TriggerOverlimit()
{
	if (bIsGrudgingStrike) return; // Striking heroes refuse to enter Overlimit
	if (OverlimitState.bIsActive) return;
	if (OverlimitState.CurrentGauge < 40.0f) return;


	OverlimitState.bIsActive = true;
	OverlimitState.OverlimitLevel = 1;
	OverlimitState.ActiveTimer = OverlimitState.MaxDuration;
	OverlimitState.CurrentGauge = 0.0f;

	if (SoundOverlimitBurst)
	{
		UGameplayStatics::PlaySoundAtLocation(this, SoundOverlimitBurst, GetActorLocation());
	}

	// Overlimit burst wave knocking back nearby foes
	if (UWorld* World = GetWorld())
	{
		const FVector Loc = GetActorLocation();
		TArray<FHitResult> Hits;
		FCollisionShape Sphere = FCollisionShape::MakeSphere(380.0f);
		FCollisionQueryParams Params;
		Params.AddIgnoredActor(this);
		if (World->SweepMultiByChannel(Hits, Loc, Loc + FVector(0, 0, 1), FQuat::Identity, ECC_Pawn, Sphere, Params))
		{
			for (const FHitResult& Hit : Hits)
			{
				if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
				{
					if (Enemy->IsAlive())
					{
						FVector Push = (Enemy->GetActorLocation() - Loc).GetSafeNormal2D();
						Enemy->ReceiveArteDamage(BaseAttackPower * 1.5f, EElement::Fire, Push * 320.0f);
					}
				}
			}
		}
	}
}

void ABattleCharacter::TriggerMysticArte()
{
	if (!OverlimitState.bIsActive) return;
	if (bIsAttacking) return;

	OverlimitState.bIsActive = false;
	OverlimitState.OverlimitLevel = 0;

	// Cinematic freeze and multi-hit flurry
	TriggerHitStop(0.12f, 0.01f);
	bIsAttacking = true;
	AttackTimer = 0.0f;
	AttackDuration = 1.6f;
	AttackCancelWindow = 1.2f;

	UAnimSequence* HiOugiAnim = AnimCast2H ? AnimCast2H : (AnimAttack4 ? AnimAttack4 : AnimAttack1);
	PlayAnimMontageSafe(HiOugiAnim, 1.25f);

	// Massive Hi-Ougi blast in front
	if (UWorld* World = GetWorld())
	{
		const FVector Forward = GetActorForwardVector();
		const FVector Center = GetActorLocation() + Forward * 300.0f;

		TArray<FHitResult> Hits;
		FCollisionShape Sphere = FCollisionShape::MakeSphere(420.0f);
		FCollisionQueryParams Params;
		Params.AddIgnoredActor(this);

		if (World->SweepMultiByChannel(Hits, Center, Center + FVector(0, 0, 1), FQuat::Identity, ECC_Pawn, Sphere, Params))
		{
			for (const FHitResult& Hit : Hits)
			{
				if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
				{
					if (Enemy->IsAlive())
					{
						float Dealt = Enemy->ReceiveArteDamage(BaseAttackPower * 6.5f, EElement::Fire, Forward, true);
						if (APlayerController* PC = Cast<APlayerController>(GetController()))
						{
							if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
							{
								HUD->RegisterComboHit(Dealt);
							}
						}
					}
				}
			}
		}
	}
}

void ABattleCharacter::ExecuteDirectionalArte(EArteDirection Direction)
{
	const bool bInAir = GetCharacterMovement() && GetCharacterMovement()->IsFalling();
	UArteDataAsset* SelectedArte = nullptr;

	if (bInAir)
	{
		if (bPaletteModifierActive)
		{
			switch (Direction)
			{
			case EArteDirection::Neutral: SelectedArte = ArtePalette.ModAerialNeutral; break;
			case EArteDirection::Up:      SelectedArte = ArtePalette.ModAerialUp; break;
			case EArteDirection::Down:    SelectedArte = ArtePalette.ModAerialDown; break;
			case EArteDirection::Side:    SelectedArte = ArtePalette.ModAerialSide; break;
			}
		}
		else
		{
			switch (Direction)
			{
			case EArteDirection::Neutral: SelectedArte = ArtePalette.AerialNeutral; break;
			case EArteDirection::Up:      SelectedArte = ArtePalette.AerialUp; break;
			case EArteDirection::Down:    SelectedArte = ArtePalette.AerialDown; break;
			case EArteDirection::Side:    SelectedArte = ArtePalette.AerialSide; break;
			}
		}
	}
	else
	{
		if (bPaletteModifierActive)
		{
			switch (Direction)
			{
			case EArteDirection::Neutral: SelectedArte = ArtePalette.ModGroundNeutral; break;
			case EArteDirection::Up:      SelectedArte = ArtePalette.ModGroundUp; break;
			case EArteDirection::Down:    SelectedArte = ArtePalette.ModGroundDown; break;
			case EArteDirection::Side:    SelectedArte = ArtePalette.ModGroundSide; break;
			}
		}
		else
		{
			switch (Direction)
			{
			case EArteDirection::Neutral: SelectedArte = ArtePalette.GroundNeutral; break;
			case EArteDirection::Up:      SelectedArte = ArtePalette.GroundUp; break;
			case EArteDirection::Down:    SelectedArte = ArtePalette.GroundDown; break;
			case EArteDirection::Side:    SelectedArte = ArtePalette.GroundSide; break;
			}
		}
	}

	if (SelectedArte)
	{
		const float AGCost = OverlimitState.bIsActive ? 0.0f : SelectedArte->AG_Cost;
		float TPCost = OverlimitState.bIsActive ? 0.0f : SelectedArte->TP_Cost;
		if (TitleManager && TitleManager->HasPassivePerk(FName("TPConserve")))
		{
			TPCost *= 0.85f; // 15% TP conservation perk from mastered Title
		}

		if (CurrentAG < AGCost || CurrentTP < TPCost)
		{
			return; // Insufficient resources
		}

		CurrentAG = FMath::Max(0.0f, CurrentAG - AGCost);
		CurrentTP = FMath::Max(0.0f, CurrentTP - TPCost);

		bIsAttacking = true;
		AttackTimer = 0.0f;
		AttackDuration = 0.48f;
		AttackCancelWindow = 0.24f;
		CurrentLocoState = ELocomotionAnimState::Action;

		UAnimSequence* AnimToPlay = SelectedArte->AnimationToPlay;
		if (!AnimToPlay)
		{
			AnimToPlay = (SelectedArte->Shape == FName("spear")) ? AnimCast1H : AnimAttack2;
		}
		const bool bIsMagicArte = (SelectedArte->Shape == FName("spear") || SelectedArte->Shape == FName("wave") || SelectedArte->Shape == FName("mine") || SelectedArte->Shape == FName("wall"));
		UAnimMontage* ArteMontage = bIsMagicArte ? MontageCast1H : MontageAttack3;
		PlayCombatMontageOrSequence(ArteMontage, AnimToPlay, SelectedArte->AnimationPlayRate);

		if (LockedTarget && LockedTarget->IsAlive())
		{
			FRotator LookRot = (LockedTarget->GetActorLocation() - GetActorLocation()).ToOrientationRotator();
			SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
		}

		const FVector Forward = GetActorForwardVector();
		const FVector Start = GetActorLocation();
		const FVector End = Start + Forward * 260.0f;

		TArray<FHitResult> Hits;
		FCollisionShape Sphere = FCollisionShape::MakeSphere(110.0f);
		FCollisionQueryParams Params;
		Params.AddIgnoredActor(this);

		if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, Params))
		{
			for (const FHitResult& Hit : Hits)
			{
				if (ABattleEnemy* Enemy = Cast<ABattleEnemy>(Hit.GetActor()))
				{
					if (Enemy->IsAlive())
					{
						float Damage = GetEffectiveAttackPower() * SelectedArte->DamageMultiplier;
						if (Enemy->IsDemon() && TitleManager && TitleManager->HasPassivePerk(FName("DemonBane")))
						{
							Damage *= 1.30f; // +30% holy bane bonus against demons
						}

						float Dealt = Enemy->ReceiveArteDamage(Damage, SelectedArte->Element, Forward, SelectedArte->bLaunchesEnemy);
						TriggerHitStop(0.045f, 0.05f);
						OverlimitState.CurrentGauge = FMath::Min(OverlimitState.MaxGauge, OverlimitState.CurrentGauge + 3.5f);

						if (SoundHitImpact)
						{
							UGameplayStatics::PlaySoundAtLocation(this, SoundHitImpact, Enemy->GetActorLocation());
						}

						if (APlayerController* PC = Cast<APlayerController>(GetController()))
						{
							if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
							{
								HUD->RegisterComboHit(Dealt);
							}
						}
						break;
					}
				}
			}
		}

		if (SelectedArte->bDivesDown && bInAir)
		{
			LaunchCharacter(FVector(0.0f, 0.0f, -600.0f) + Forward * 120.0f, true, true);
		}
	}
	else
	{
		// Graceful fallback to existing CastArte slot if palette data asset is empty
		CastArte(static_cast<int32>(Direction) + 1);
	}
}

void ABattleCharacter::TriggerDodge()
{
	if (!GetCharacterMovement() || !GetCharacterMovement()->IsMovingOnGround()) return;
	if (bIsDodging) return;

	const float CurrentTime = GetWorld()->GetTimeSeconds();
	if (CurrentTime - LastDodgeTime < 0.40f) return;

	// Tales of Arise Dodge-Cancel: immediately interrupt any attack into an evasive roll!
	if (bIsAttacking)
	{
		bIsAttacking = false;
		AttackTimer = 0.0f;
	}
	bBufferedNormalAttack = false;
	bBufferedHeavyAttack = false;
	if (GetMesh())
	{
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
	}

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

	// Tales of Arise Perfect Dodge detection:
	// If dodging when an active enemy is within close striking proximity (350cm), trigger slow-mo & Counter Edge!
	bool bPerfectDodge = false;
	for (TActorIterator<ABattleEnemy> It(GetWorld()); It; ++It)
	{
		ABattleEnemy* Enemy = *It;
		if (Enemy && Enemy->IsAlive())
		{
			const float Dist = FVector::Dist(GetActorLocation(), Enemy->GetActorLocation());
			if (Dist <= 380.0f)
			{
				bPerfectDodge = true;
				break;
			}
		}
	}

	if (bPerfectDodge)
	{
		bCanCounterEdge = true;
		CounterEdgeWindowTimer = 0.95f; // Generous window to execute Counter Edge flash attack!
		TriggerHitStop(0.18f, 0.15f);    // Slow-motion cinematic Dodge freeze
		if (SoundOverlimitBurst)
		{
			UGameplayStatics::PlaySoundAtLocation(this, SoundOverlimitBurst, GetActorLocation(), 0.6f, 1.4f);
		}
	}
}


void ABattleCharacter::PerformJump()
{
	// Strict ground check: strictly prevents infinite jumps in mid-air
	if (!GetCharacterMovement() || !GetCharacterMovement()->IsMovingOnGround())
	{
		return;
	}

	FVector MoveDir = GetLastMovementInputVector().GetSafeNormal2D();
	if (MoveDir.IsNearlyZero())
	{
		MoveDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
	}

	if (!MoveDir.IsNearlyZero())
	{
		// Directional Jump (forward/diagonal leap with controlled vertical height)
		LaunchCharacter(MoveDir * 280.0f + FVector(0.0f, 0.0f, 520.0f), true, true);
	}
	else
	{
		// Standard vertical jump handled cleanly by AnimBP
		Jump();
	}
}

void ABattleCharacter::TakeCombatDamage(float DamageAmount, const FVector& HitDirection)
{
	if (CurrentHP <= 0.0f || bIsIncapacitated) return;

	// Invulnerability frames during active dodge (0.35s)
	const float CurrentTime = GetWorld()->GetTimeSeconds();
	if (CurrentTime - LastDodgeTime < 0.35f)
	{
		return;
	}

	float FinalDamage = DamageAmount;
	if (bIsGrudgingStrike)
	{
		FinalDamage *= 1.25f; // -25% defense debuff when forced into battle while on strike
	}

	CurrentHP = FMath::Max(0.0f, CurrentHP - FinalDamage);
	LaunchCharacter(HitDirection * 350.0f + FVector(0.0f, 0.0f, 100.0f), true, true);

	// Taking enemy damage interrupts escape attempt!
	EscapeTimer = 0.0f;
	bIsEscaping = false;

	if (CurrentHP <= 0.0f)
	{
		bIsIncapacitated = true;
		if (ABattleGameMode* GM = Cast<ABattleGameMode>(UGameplayStatics::GetGameMode(this)))
		{
			const FName ReportedID = (AdventurerProfileID != NAME_None) ? AdventurerProfileID : FName(TEXT("Hero_Player"));
			GM->RecordHeroIncapacitated(ReportedID);
			GM->OnPlayerDefeated();
		}
	}
}


float ABattleCharacter::TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser)
{
	float ActualDamage = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
	FVector HitDir = DamageCauser ? (GetActorLocation() - DamageCauser->GetActorLocation()).GetSafeNormal() : -GetActorForwardVector();
	TakeCombatDamage(DamageAmount, HitDir);
	return ActualDamage;
}

// ── Enhanced Input Handling (LMBS Side-to-Side Orbit & Free Cam) ──

void ABattleCharacter::EnhancedMove(const FInputActionValue& Value)
{
	const FVector2D Input = Value.Get<FVector2D>();
	if (Input.IsNearlyZero()) return;

	if (bIsDodging) return;

	// If attacking: allow movement input to seamlessly resume locomotion once the active swing window finishes!
	if (bIsAttacking)
	{
		if (AttackTimer < AttackCancelWindow)
		{
			return; // Active swing frames: feet stay planted
		}

		// Active swing finished: transition directly out of attack into movement!
		bIsAttacking = false;
		bBufferedNormalAttack = false;
		bBufferedHeavyAttack = false;
		ResetLocomotionToInput();
	}

	if (Controller)
	{
		if (LockedTarget && LockedTarget->IsAlive() && !bIsFreeRunning)
		{
			// Tales LMBS Plane: Input.Y moves forward/backward to target; Input.X circles/orbits around target!
			const FVector ToTarget = (LockedTarget->GetActorLocation() - GetActorLocation()).GetSafeNormal2D();
			const FVector Tangent = FVector(-ToTarget.Y, ToTarget.X, 0.0f);

			AddMovementInput(ToTarget, Input.Y);
			AddMovementInput(Tangent, Input.X);
		}
		else
		{
			// Free Run (Alt / L2 hold) or unlocked: 360 degree arena free motion!
			const FRotator Rotation = Controller->GetControlRotation();
			const FRotator YawRotation(0.0f, Rotation.Yaw, 0.0f);

			const FVector ForwardDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X);
			const FVector RightDir = FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y);

			AddMovementInput(ForwardDir, Input.Y);
			AddMovementInput(RightDir, Input.X);
		}
	}
}

void ABattleCharacter::EnhancedLook(const FInputActionValue& Value)
{
	const FVector2D LookValue = Value.Get<FVector2D>();
	if (!LookValue.IsNearlyZero())
	{
		AddControllerYawInput(LookValue.X);
		AddControllerPitchInput(LookValue.Y);
	}
}

void ABattleCharacter::CreateRuntimeInputMappings()
{
	if (RuntimeMappingContext && MoveAction && LookAction && AttackAction) return;

	// Movement Action
	MoveAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleMove"));
	MoveAction->ValueType = EInputActionValueType::Axis2D;
	MoveAction->AccumulationBehavior = EInputActionAccumulationBehavior::Cumulative;

	// Look Action (Modern Free Camera)
	LookAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleLook"));
	LookAction->ValueType = EInputActionValueType::Axis2D;
	LookAction->AccumulationBehavior = EInputActionAccumulationBehavior::Cumulative;

	JumpAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleJump"));
	JumpAction->ValueType = EInputActionValueType::Boolean;

	AttackAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleAttack"));
	HeavyAttackAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleHeavyAttack"));
	SprintAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleSprint"));
	TargetLockAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleTargetLock"));
	DodgeAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleDodge"));
	FreeRunAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleFreeRun"));
	PaletteModifierAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattlePaletteMod"));
	OverlimitAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleOverlimit"));
	Arte1Action = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleArte1"));
	Arte2Action = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleArte2"));
	Arte3Action = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleArte3"));
	Arte4Action = NewObject<UInputAction>(this, TEXT("RuntimeIA_BattleArte4"));

	RuntimeMappingContext = NewObject<UInputMappingContext>(this, TEXT("RuntimeIMC_Battle"));

	// ── W key -> (+1 Forward) ──
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(MoveAction, EKeys::W);
		UInputModifierSwizzleAxis* S = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		S->Order = EInputAxisSwizzle::YXZ;
		M.Modifiers.Add(S);
	}

	// ── S key -> (-1 Backward) ──
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(MoveAction, EKeys::S);
		UInputModifierSwizzleAxis* S = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		S->Order = EInputAxisSwizzle::YXZ;
		M.Modifiers.Add(S);
		UInputModifierNegate* N = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		N->bX = true; N->bY = true; N->bZ = true;
		M.Modifiers.Add(N);
	}

	// ── D key -> (+1 Strafe Right) ──
	RuntimeMappingContext->MapKey(MoveAction, EKeys::D);

	// ── A key -> (-1 Strafe Left) ──
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(MoveAction, EKeys::A);
		UInputModifierNegate* N = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		N->bX = true; N->bY = true; N->bZ = true;
		M.Modifiers.Add(N);
	}

	// ── Arrow Keys Fallback Movement ──
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(MoveAction, EKeys::Up);
		UInputModifierSwizzleAxis* S = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		S->Order = EInputAxisSwizzle::YXZ;
		M.Modifiers.Add(S);
	}
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(MoveAction, EKeys::Down);
		UInputModifierSwizzleAxis* S = NewObject<UInputModifierSwizzleAxis>(RuntimeMappingContext);
		S->Order = EInputAxisSwizzle::YXZ;
		M.Modifiers.Add(S);
		UInputModifierNegate* N = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		N->bX = true; N->bY = true; N->bZ = true;
		M.Modifiers.Add(N);
	}
	RuntimeMappingContext->MapKey(MoveAction, EKeys::Right);
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(MoveAction, EKeys::Left);
		UInputModifierNegate* N = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		N->bX = true; N->bY = true; N->bZ = true;
		M.Modifiers.Add(N);
	}

	// Gamepad Movement Stick
	RuntimeMappingContext->MapKey(MoveAction, EKeys::Gamepad_Left2D);

	// ── Sprint (Shift / Gamepad L3) ──
	RuntimeMappingContext->MapKey(SprintAction, EKeys::LeftShift);
	RuntimeMappingContext->MapKey(SprintAction, EKeys::RightShift);
	RuntimeMappingContext->MapKey(SprintAction, EKeys::Gamepad_LeftThumbstick);

	// ── Mouse Look & Gamepad Look (Modern Camera Rotation) ──
	{
		FEnhancedActionKeyMapping& M = RuntimeMappingContext->MapKey(LookAction, EKeys::Mouse2D);
		UInputModifierNegate* N = NewObject<UInputModifierNegate>(RuntimeMappingContext);
		N->bX = false; N->bY = true; N->bZ = false;
		M.Modifiers.Add(N);
	}
	RuntimeMappingContext->MapKey(LookAction, EKeys::Gamepad_Right2D);

	// Jump / Directional Jump (Space / Gamepad Bottom)
	RuntimeMappingContext->MapKey(JumpAction, EKeys::SpaceBar);
	RuntimeMappingContext->MapKey(JumpAction, EKeys::Gamepad_FaceButton_Bottom);

	// Normal Attack Combo (Left Click / Face Button Left)
	RuntimeMappingContext->MapKey(AttackAction, EKeys::LeftMouseButton);
	RuntimeMappingContext->MapKey(AttackAction, EKeys::Gamepad_FaceButton_Left);

	// Direct Heavy Attack / Finisher / Slam (Right Mouse Button / Face Button Top)
	RuntimeMappingContext->MapKey(HeavyAttackAction, EKeys::RightMouseButton);
	RuntimeMappingContext->MapKey(HeavyAttackAction, EKeys::Gamepad_FaceButton_Top);

	// Target Lock (Tab / Gamepad R3)
	RuntimeMappingContext->MapKey(TargetLockAction, EKeys::Tab);
	RuntimeMappingContext->MapKey(TargetLockAction, EKeys::Gamepad_RightThumbstick);

	// Dodge / Roll (Left Ctrl / Right Ctrl / Gamepad Face Button Right)
	RuntimeMappingContext->MapKey(DodgeAction, EKeys::LeftControl);
	RuntimeMappingContext->MapKey(DodgeAction, EKeys::RightControl);
	RuntimeMappingContext->MapKey(DodgeAction, EKeys::Gamepad_FaceButton_Right);

	// Free Run (Left Alt / Right Alt / Gamepad Left Trigger)
	RuntimeMappingContext->MapKey(FreeRunAction, EKeys::LeftAlt);
	RuntimeMappingContext->MapKey(FreeRunAction, EKeys::RightAlt);
	RuntimeMappingContext->MapKey(FreeRunAction, EKeys::Gamepad_LeftTrigger);

	// Palette Modifier (Q / Gamepad Left Shoulder)
	RuntimeMappingContext->MapKey(PaletteModifierAction, EKeys::Q);
	RuntimeMappingContext->MapKey(PaletteModifierAction, EKeys::Gamepad_LeftShoulder);

	// Overlimit (R / Gamepad Special Right)
	RuntimeMappingContext->MapKey(OverlimitAction, EKeys::R);
	RuntimeMappingContext->MapKey(OverlimitAction, EKeys::Gamepad_Special_Right);

	// 4 Elemental Artes / Directional Palette (1, 2, 3, 4)
	RuntimeMappingContext->MapKey(Arte1Action, EKeys::One);
	RuntimeMappingContext->MapKey(Arte2Action, EKeys::Two);
	RuntimeMappingContext->MapKey(Arte3Action, EKeys::Three);
	RuntimeMappingContext->MapKey(Arte4Action, EKeys::Four);

	// Switch Party Leader Action (Tab / Z / Gamepad D-Pad Up)
	SwitchLeaderAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_SwitchLeader"));
	SwitchLeaderAction->ValueType = EInputActionValueType::Boolean;
	RuntimeMappingContext->MapKey(SwitchLeaderAction, EKeys::Z);
	RuntimeMappingContext->MapKey(SwitchLeaderAction, EKeys::Gamepad_DPad_Up);

	// Escape Action (Escape / Gamepad Special Left)
	EscapeAction = NewObject<UInputAction>(this, TEXT("RuntimeIA_Escape"));
	EscapeAction->ValueType = EInputActionValueType::Boolean;
	RuntimeMappingContext->MapKey(EscapeAction, EKeys::Escape);
	RuntimeMappingContext->MapKey(EscapeAction, EKeys::Gamepad_Special_Left);
}

void ABattleCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
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
			EnhancedInput->BindAction(MoveAction, ETriggerEvent::Triggered, this, &ABattleCharacter::EnhancedMove);
		}
		if (LookAction)
		{
			EnhancedInput->BindAction(LookAction, ETriggerEvent::Triggered, this, &ABattleCharacter::EnhancedLook);
		}
		if (JumpAction)
		{
			EnhancedInput->BindAction(JumpAction, ETriggerEvent::Started, this, &ABattleCharacter::PerformJump);
		}
		if (AttackAction)
		{
			EnhancedInput->BindAction(AttackAction, ETriggerEvent::Started, this, &ABattleCharacter::PerformNormalAttack);
		}
		if (HeavyAttackAction)
		{
			EnhancedInput->BindAction(HeavyAttackAction, ETriggerEvent::Started, this, &ABattleCharacter::PerformHeavyAttack);
		}
		if (SprintAction)
		{
			EnhancedInput->BindAction(SprintAction, ETriggerEvent::Started, this, &ABattleCharacter::OnSprintStarted);
			EnhancedInput->BindAction(SprintAction, ETriggerEvent::Completed, this, &ABattleCharacter::OnSprintEnded);
		}
		if (FreeRunAction)
		{
			EnhancedInput->BindAction(FreeRunAction, ETriggerEvent::Started, this, &ABattleCharacter::SetFreeRun, true);
			EnhancedInput->BindAction(FreeRunAction, ETriggerEvent::Completed, this, &ABattleCharacter::SetFreeRun, false);
		}
		if (PaletteModifierAction)
		{
			EnhancedInput->BindAction(PaletteModifierAction, ETriggerEvent::Started, this, &ABattleCharacter::SetPaletteModifier, true);
			EnhancedInput->BindAction(PaletteModifierAction, ETriggerEvent::Completed, this, &ABattleCharacter::SetPaletteModifier, false);
		}
		if (OverlimitAction)
		{
			EnhancedInput->BindAction(OverlimitAction, ETriggerEvent::Started, this, &ABattleCharacter::TriggerOverlimit);
		}
		if (TargetLockAction)
		{
			EnhancedInput->BindAction(TargetLockAction, ETriggerEvent::Started, this, &ABattleCharacter::ToggleTargetLock);
		}
		if (DodgeAction)
		{
			EnhancedInput->BindAction(DodgeAction, ETriggerEvent::Started, this, &ABattleCharacter::TriggerDodge);
		}
		if (Arte1Action)
		{
			EnhancedInput->BindAction(Arte1Action, ETriggerEvent::Started, this, &ABattleCharacter::ExecuteDirectionalArte, EArteDirection::Neutral);
		}
		if (Arte2Action)
		{
			EnhancedInput->BindAction(Arte2Action, ETriggerEvent::Started, this, &ABattleCharacter::ExecuteDirectionalArte, EArteDirection::Up);
		}
		if (Arte3Action)
		{
			EnhancedInput->BindAction(Arte3Action, ETriggerEvent::Started, this, &ABattleCharacter::ExecuteDirectionalArte, EArteDirection::Down);
		}
		if (Arte4Action)
		{
			EnhancedInput->BindAction(Arte4Action, ETriggerEvent::Started, this, &ABattleCharacter::ExecuteDirectionalArte, EArteDirection::Side);
		}
		if (SwitchLeaderAction)
		{
			EnhancedInput->BindAction(SwitchLeaderAction, ETriggerEvent::Started, this, &ABattleCharacter::SwitchNextPartyLeader);
		}
		if (EscapeAction)
		{
			EnhancedInput->BindAction(EscapeAction, ETriggerEvent::Started, this, &ABattleCharacter::StartHoldingEscape);
			EnhancedInput->BindAction(EscapeAction, ETriggerEvent::Completed, this, &ABattleCharacter::StopHoldingEscape);
		}
	}
}

void ABattleCharacter::SwitchNextPartyLeader()
{
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<ABattleCharacter> It(World); It; ++It)
		{
			if (UPartyCombatManager* PartyMgr = It->FindComponentByClass<UPartyCombatManager>())
			{
				PartyMgr->NextLeader();
				return;
			}
		}
	}
}

void ABattleCharacter::StartHoldingEscape()
{
	bIsHoldingEscapeKey = true;
}

void ABattleCharacter::StopHoldingEscape()
{
	bIsHoldingEscapeKey = false;
}
