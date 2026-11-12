// Copyright Epic Games, Inc. All Rights Reserved.
// VillageNPC.cpp — Interactive Village NPC with JRPG Dialogue, Farming Routines & Archetypes

#include "VillageNPC.h"
#include "IsekaiVillageHUD.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimSequence.h"
#include "Animation/AnimMontage.h"
#include "Kismet/GameplayStatics.h"

AVillageNPC::AVillageNPC()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(42.0f, 90.0f);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);

	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->MaxWalkSpeed = 180.0f;

	// Mesh — default X_Bot (Mixamo) mesh with Manny fallback
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> XBotAsset(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
	if (XBotAsset.Succeeded())
	{
		GetMesh()->SetSkeletalMesh(XBotAsset.Object);
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -90.0f));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
		GetMesh()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	}
	else
	{
		static ConstructorHelpers::FObjectFinder<USkeletalMesh> MannyMesh(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
		if (MannyMesh.Succeeded())
		{
			GetMesh()->SetSkeletalMesh(MannyMesh.Object);
			GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -90.0f));
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

	InitializeArchetypeDefaults();
}

void AVillageNPC::BeginPlay()
{
	Super::BeginPlay();

	if (HeadMesh && GetMesh())
	{
		HeadMesh->SetLeaderPoseComponent(GetMesh());
	}

	if (USkeletalMeshComponent* MeshComp = GetMesh())
	{
		// Always force BodyA — BP overrides may have old mesh causing skeleton mismatch
		if (USkeletalMesh* LoadedMesh = Cast<USkeletalMesh>(StaticLoadObject(USkeletalMesh::StaticClass(), nullptr, TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"))))
		{
			MeshComp->SetSkeletalMesh(LoadedMesh);
		}

		MeshComp->SetRelativeLocationAndRotation(
			FVector(0.0f, 0.0f, -90.0f),
			FRotator(0.0f, -90.0f, 0.0f)
		);
		MeshComp->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
		MeshComp->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	}

	AnimLocoIdle = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")));
	AnimFarmingTill = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/dig_and_plant_seeds.dig_and_plant_seeds")));
	AnimFarmingWater = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/watering.watering")));
	AnimFarmingHarvest = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/Farming/pull_plant.pull_plant")));
	AnimGuardStance = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Combat/SwordAndShield/sword_and_shield_block_idle.sword_and_shield_block_idle")));
	if (!AnimGuardStance)
	{
		AnimGuardStance = Cast<UAnimSequence>(StaticLoadObject(UAnimSequence::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Shared/ActionAdventure/idle.idle")));
	}

	// Play initial archetype animation
	if (GetMesh())
	{
		if (Archetype == ENPCArchetype::Farmer && AnimFarmingTill)
		{
			GetMesh()->PlayAnimation(AnimFarmingTill, true);
		}
		else if (Archetype == ENPCArchetype::Guard && AnimGuardStance)
		{
			GetMesh()->PlayAnimation(AnimGuardStance, true);
		}
		else if (AnimLocoIdle)
		{
			GetMesh()->PlayAnimation(AnimLocoIdle, true);
		}
	}
}


void AVillageNPC::InitializeArchetypeDefaults()
{
	DialogueLines.Empty();

	switch (Archetype)
	{
	case ENPCArchetype::Farmer:
		NPCName = FText::FromString(TEXT("Farmer Barnaby"));
		RoleTitle = FText::FromString(TEXT("Village Agriculturalist"));
		DialogueLines.Add(FText::FromString(TEXT("Fine morning for the fields! Our Mana soil is rich and fertile.")));
		DialogueLines.Add(FText::FromString(TEXT("Equip your Hoe to till soil, scatter seeds, and keep crops watered regularly!")));
		DialogueLines.Add(FText::FromString(TEXT("Harvested produce can be sold in town or cooked into stat-boosting meals.")));
		break;

	case ENPCArchetype::Guard:
		NPCName = FText::FromString(TEXT("Captain Vane"));
		RoleTitle = FText::FromString(TEXT("Gate Guardian"));
		DialogueLines.Add(FText::FromString(TEXT("Halt! Beyond these gates roam fierce monsters and wild mutants.")));
		DialogueLines.Add(FText::FromString(TEXT("Ensure your blade is sharpened and your TP gauge is full before setting foot on the overworld.")));
		DialogueLines.Add(FText::FromString(TEXT("Use your combat roll (Ctrl) to dodge deadly strikes and counter during enemy openings!")));
		break;

	case ENPCArchetype::Shopkeeper:
		NPCName = FText::FromString(TEXT("Merchant Lyra"));
		RoleTitle = FText::FromString(TEXT("Traveling Merchant"));
		DialogueLines.Add(FText::FromString(TEXT("Welcome, adventurer! Looking for restorative Apple Gels, Seeds, or new gear?")));
		DialogueLines.Add(FText::FromString(TEXT("Defeat beasts in the outer biomes to earn Gald and trade for rare materials!")));
		break;

	case ENPCArchetype::Elder:
	case ENPCArchetype::Villager:
	default:
		NPCName = FText::FromString(TEXT("Elder Corrine"));
		RoleTitle = FText::FromString(TEXT("Village Elder"));
		DialogueLines.Add(FText::FromString(TEXT("Welcome to Iselia Village, brave adventurer!")));
		DialogueLines.Add(FText::FromString(TEXT("The overworld beyond our gates is vast. Roaming beasts guard the outer biomes.")));
		DialogueLines.Add(FText::FromString(TEXT("Remember: in combat, exploit elemental weaknesses with Ignis, Aqua, Terra, and Ventus!")));
		DialogueLines.Add(FText::FromString(TEXT("May the Mana Goddess watch over your journey!")));
		break;
	}
}

void AVillageNPC::SetNPCArchetype(ENPCArchetype NewArchetype)
{
	Archetype = NewArchetype;
	InitializeArchetypeDefaults();
}

void AVillageNPC::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsInteracting)
	{
		InteractingTimer -= DeltaTime;
		if (InteractingTimer <= 0.0f)
		{
			bIsInteracting = false;
		}
		return;
	}

	UpdateRoutine(DeltaTime);
}

void AVillageNPC::UpdateRoutine(float DeltaTime)
{
	RoutineTimer += DeltaTime;
	if (RoutineTimer < RoutineInterval) return;

	RoutineTimer = 0.0f;
	RoutineStep = (RoutineStep + 1) % 4;

	if (Archetype == ENPCArchetype::Farmer)
	{
		switch (RoutineStep)
		{
		case 0:
			if (AnimFarmingTill) PlayAnimMontageSafe(AnimFarmingTill, 1.0f);
			break;
		case 1:
			if (AnimFarmingWater) PlayAnimMontageSafe(AnimFarmingWater, 1.0f);
			break;
		case 2:
			if (AnimFarmingHarvest) PlayAnimMontageSafe(AnimFarmingHarvest, 1.0f);
			break;
		case 3:
			if (AnimBoxIdle) PlayAnimMontageSafe(AnimBoxIdle, 1.0f);
			break;
		}
	}
	else if (Archetype == ENPCArchetype::Guard)
	{
		if (AnimGuardStance && RoutineStep % 2 == 0)
		{
			PlayAnimMontageSafe(AnimGuardStance, 1.0f);
		}
	}
}

void AVillageNPC::PlayAnimMontageSafe(UAnimSequence* Seq, float PlayRate)
{
	if (!Seq || !GetMesh()) return;
	GetMesh()->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	GetMesh()->PlayAnimation(Seq, false);
	GetMesh()->SetPlayRate(PlayRate);
}


bool AVillageNPC::IsPlayerInRange(const FVector& PlayerLocation) const
{
	return FVector::Dist2D(GetActorLocation(), PlayerLocation) <= InteractionRadius;
}

void AVillageNPC::FacePlayer(const FVector& PlayerLocation)
{
	FRotator LookRot = (PlayerLocation - GetActorLocation()).ToOrientationRotator();
	SetActorRotation(FRotator(0.0f, LookRot.Yaw, 0.0f));
}

void AVillageNPC::InteractWithPlayer(APawn* Interactor)
{
	if (!Interactor) return;

	bIsInteracting = true;
	InteractingTimer = 10.0f;

	FacePlayer(Interactor->GetActorLocation());

	if (APlayerController* PC = Cast<APlayerController>(Interactor->GetController()))
	{
		if (AIsekaiVillageHUD* HUD = Cast<AIsekaiVillageHUD>(PC->GetHUD()))
		{
			HUD->StartDialogue(NPCName, DialogueLines, RoleTitle);
		}
	}
}

