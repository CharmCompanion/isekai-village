// Copyright Epic Games, Inc. All Rights Reserved.

#include "OverworldMonsterAvatar.h"
#include "IsekaiVillageCharacter.h"
#include "IsekaiVillageTypes.h"
#include "Components/SphereComponent.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "Animation/AnimInstance.h"

AOverworldMonsterAvatar::AOverworldMonsterAvatar()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(45.0f, 96.0f);
	GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);

	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 480.0f, 0.0f);
	GetCharacterMovement()->MaxWalkSpeed = PatrolSpeed;
	GetCharacterMovement()->BrakingDecelerationWalking = 2000.0f;
	GetCharacterMovement()->GroundFriction = 8.0f;

	EncounterTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("EncounterTrigger"));
	EncounterTrigger->SetupAttachment(RootComponent);
	EncounterTrigger->SetSphereRadius(75.0f);
	EncounterTrigger->SetCollisionProfileName(TEXT("Trigger"));
	EncounterTrigger->SetGenerateOverlapEvents(true);
	EncounterTrigger->OnComponentBeginOverlap.AddDynamic(this, &AOverworldMonsterAvatar::OnEncounterOverlap);

	static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(TEXT("/Game/StylizedCharacters/BodyA/Body/SKM_BodyA.SKM_BodyA"));
	if (MeshAsset.Succeeded())
	{
		GetMesh()->SetSkeletalMesh(MeshAsset.Object);
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -96.0f));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
		GetMesh()->SetWorldScale3D(FVector(0.85f, 0.85f, 0.85f));
	}

	static ConstructorHelpers::FObjectFinder<USkeletalMesh> HeadAsset(TEXT("/Game/StylizedCharacters/BodyA/Heads/Head_01/SKM_HeadA_01.SKM_HeadA_01"));
	HeadMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("HeadMesh"));
	HeadMesh->SetupAttachment(GetMesh());
	HeadMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	if (HeadAsset.Succeeded())
	{
		HeadMesh->SetSkeletalMesh(HeadAsset.Object);
	}

	static ConstructorHelpers::FClassFinder<UAnimInstance> AnimBP(TEXT("/Game/IsekaiVillage/ABP/ABP_IsekaiEnemy.ABP_IsekaiEnemy_C"));
	if (AnimBP.Succeeded())
	{
		GetMesh()->SetAnimInstanceClass(AnimBP.Class);
	}
}

void AOverworldMonsterAvatar::BeginPlay()
{
	Super::BeginPlay();
	if (HeadMesh && GetMesh())
	{
		HeadMesh->SetLeaderPoseComponent(GetMesh());
	}
	HomeLocation = GetActorLocation();
	PickNewPatrolPoint();
}

void AOverworldMonsterAvatar::StunMonster(float Duration)
{
	bIsStunned = true;
	StunTimer = FMath::Max(Duration, 1.0f);
	CurrentState = EMonsterAIState::Idle;
	GetCharacterMovement()->StopMovementImmediately();
}

void AOverworldMonsterAvatar::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	if (bEncounterTriggered) return;

	if (bIsStunned)
	{
		StunTimer -= DeltaTime;
		if (StunTimer <= 0.0f)
		{
			bIsStunned = false;
		}
		return;
	}

	APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
	if (PlayerPawn && PlayerPawn->IsA<AIsekaiVillageCharacter>())
	{
		const float Dist = FVector::Dist(GetActorLocation(), PlayerPawn->GetActorLocation());
		if (Dist <= AggroRadius)
		{
			CurrentState = EMonsterAIState::Chasing;
			GetCharacterMovement()->MaxWalkSpeed = ChaseSpeed;
			UpdateChase(DeltaTime, PlayerPawn);
			return;
		}
	}

	if (CurrentState == EMonsterAIState::Chasing)
	{
		CurrentState = EMonsterAIState::Patrolling;
		GetCharacterMovement()->MaxWalkSpeed = PatrolSpeed;
		PickNewPatrolPoint();
	}

	UpdatePatrol(DeltaTime);
}

void AOverworldMonsterAvatar::PickNewPatrolPoint()
{
	const float RandomAngle = FMath::RandRange(0.0f, 2.0f * PI);
	const float RandomDist = FMath::RandRange(200.0f, PatrolRadius);
	CurrentTargetLocation = HomeLocation + FVector(
		FMath::Cos(RandomAngle) * RandomDist,
		FMath::Sin(RandomAngle) * RandomDist,
		0.0f
	);
	StateDuration = FMath::RandRange(3.0f, 6.0f);
	StateTimer = 0.0f;
	CurrentState = FMath::RandBool() ? EMonsterAIState::Patrolling : EMonsterAIState::Idle;
}

void AOverworldMonsterAvatar::UpdatePatrol(float DeltaTime)
{
	StateTimer += DeltaTime;
	if (StateTimer >= StateDuration)
	{
		PickNewPatrolPoint();
		return;
	}

	if (CurrentState == EMonsterAIState::Patrolling)
	{
		FVector Direction = (CurrentTargetLocation - GetActorLocation()).GetSafeNormal2D();
		AddMovementInput(Direction, 1.0f);
		if (FVector::Dist2D(GetActorLocation(), CurrentTargetLocation) < 100.0f)
		{
			CurrentState = EMonsterAIState::Idle;
		}
	}
}

void AOverworldMonsterAvatar::UpdateChase(float DeltaTime, APawn* PlayerPawn)
{
	if (!PlayerPawn) return;
	FVector Direction = (PlayerPawn->GetActorLocation() - GetActorLocation()).GetSafeNormal2D();
	AddMovementInput(Direction, 1.0f);
}

void AOverworldMonsterAvatar::OnEncounterOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (bEncounterTriggered) return;
	if (!Cast<AIsekaiVillageCharacter>(OtherActor)) return;

	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (!PC || OtherActor != PC->GetPawn()) return;

	TriggerBattleEncounter(Cast<APawn>(OtherActor));
}

void AOverworldMonsterAvatar::TriggerBattleEncounter(APawn* PlayerPawn)
{
	if (bEncounterTriggered) return;
	bEncounterTriggered = true;

	EEncounterAdvantage Advantage = EEncounterAdvantage::Normal;
	if (bIsStunned)
	{
		Advantage = EEncounterAdvantage::PlayerAdvantage;
	}

	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		if (PlayerPawn)
		{
			GI->ReturnOverworldPosition = PlayerPawn->GetActorLocation();
			GI->ReturnOverworldRotation = PlayerPawn->GetActorRotation();
		}
		GI->EncounteredEnemyParty = EnemyPartyID;
		GI->bReturningFromBattle = false;
		GI->CurrentEncounterAdvantage = Advantage;
	}

	FString BattleMapName;
	if (!CustomBattleMap.IsNull())
	{
		BattleMapName = CustomBattleMap.ToSoftObjectPath().GetAssetName();
	}
	if (BattleMapName.IsEmpty())
	{
		switch (ArenaBiome)
		{
		case EBattleArenaBiome::Forest:
			BattleMapName = TEXT("/Game/IsekaiVillage/Maps/Map_Battle_Forest");
			break;
		case EBattleArenaBiome::Desert:
			BattleMapName = TEXT("/Game/IsekaiVillage/Maps/Map_Battle_Desert");
			break;
		case EBattleArenaBiome::Arena:
			BattleMapName = TEXT("/Game/IsekaiVillage/Maps/Map_BattleArena");
			break;
		case EBattleArenaBiome::Plains:
		default:
			BattleMapName = TEXT("/Game/IsekaiVillage/Maps/Map_Battle_Plains");
			break;
		}
	}

	GetCharacterMovement()->DisableMovement();
	UGameplayStatics::OpenLevel(this, FName(*BattleMapName));
}
