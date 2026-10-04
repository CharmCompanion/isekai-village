// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageCharacter.cpp — Tales TP artes + Nier movement (clean rewrite, no old magic)

#include "IsekaiVillageCharacter.h"
#include "IsekaiVillageHUD.h"
#include "SphereGridDataAsset.h"
#include "PartyReserveComponent.h"
#include "GuildMasterDesk.h"
#include "TownZone.h"
#include "EngineUtils.h"
#include "Engine/TargetPoint.h"
#include "SpellVisualDataAsset.h"
#include "SpellProjectile.h"
#include "SpellElementVFX.h"
#include "NiagaraSystem.h"
#include "NiagaraComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Components/CapsuleComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimInstance.h"
#include "Kismet/GameplayStatics.h"
#include "LandscapeProxy.h"
#include "Engine/DamageEvents.h"
#include "UObject/ConstructorHelpers.h"
#include "EnhancedInputComponent.h"
#include "EnhancedInputSubsystems.h"
#include "InputMappingContext.h"

AIsekaiVillageCharacter::AIsekaiVillageCharacter()
{
	PrimaryActorTick.bCanEverTick = true;

	GetCapsuleComponent()->InitCapsuleSize(42.0f, NormalCapsuleHalfHeight);

	bUseControllerRotationPitch = false;
	bUseControllerRotationYaw = false;
	bUseControllerRotationRoll = false;

	GetCharacterMovement()->bOrientRotationToMovement = true;
	GetCharacterMovement()->RotationRate = FRotator(0.0f, 720.0f, 0.0f);
	GetCharacterMovement()->JumpZVelocity = 700.0f;
	GetCharacterMovement()->AirControl = 0.35f;
	GetCharacterMovement()->MaxWalkSpeed = 600.0f;
	GetCharacterMovement()->MinAnalogWalkSpeed = 20.0f;
	GetCharacterMovement()->BrakingDecelerationWalking = 2000.0f;

	// Camera
	CameraBoom = CreateDefaultSubobject<USpringArmComponent>(TEXT("CameraBoom"));
	CameraBoom->SetupAttachment(RootComponent);
	CameraBoom->TargetArmLength = 400.0f;
	CameraBoom->bUsePawnControlRotation = true;
	CameraBoom->bInheritPitch = true;
	CameraBoom->bInheritYaw = true;
	CameraBoom->bInheritRoll = false;
	CameraBoom->bDoCollisionTest = true;
	CameraBoom->SocketOffset = FVector(0.0f, 40.0f, 50.0f);
	CameraBoom->bEnableCameraLag = true;
	CameraBoom->CameraLagSpeed = 12.0f;

	FollowCamera = CreateDefaultSubobject<UCameraComponent>(TEXT("FollowCamera"));
	FollowCamera->SetupAttachment(CameraBoom, USpringArmComponent::SocketName);
	FollowCamera->bUsePawnControlRotation = false;

	// Orbs (palm-attached during arte charge)
	LeftHandOrbVFX = CreateDefaultSubobject<UNiagaraComponent>(TEXT("LeftHandOrbVFX"));
	LeftHandOrbVFX->SetupAttachment(GetMesh());
	LeftHandOrbVFX->SetAutoActivate(false);

	RightHandOrbVFX = CreateDefaultSubobject<UNiagaraComponent>(TEXT("RightHandOrbVFX"));
	RightHandOrbVFX->SetupAttachment(GetMesh());
	RightHandOrbVFX->SetAutoActivate(false);

	PartyReserve = CreateDefaultSubobject<UPartyReserveComponent>(TEXT("PartyReserve"));

	// Default Mannequin + Anim
	static ConstructorHelpers::FObjectFinder<USkeletalMesh> MeshAsset(TEXT("/Game/Characters/Mannequins/Meshes/SKM_Manny_Simple.SKM_Manny_Simple"));
	if (MeshAsset.Succeeded())
	{
		GetMesh()->SetSkeletalMesh(MeshAsset.Object);
		GetMesh()->SetRelativeLocation(FVector(0.0f, 0.0f, -NormalCapsuleHalfHeight));
		GetMesh()->SetRelativeRotation(FRotator(0.0f, -90.0f, 0.0f));
	}

	static ConstructorHelpers::FClassFinder<UAnimInstance> AnimBP(TEXT("/Game/Characters/Mannequins/Anims/Unarmed/ABP_Unarmed.ABP_Unarmed_C"));
	if (AnimBP.Succeeded())
	{
		GetMesh()->SetAnimInstanceClass(AnimBP.Class);
	}

	// Enhanced Input
	static ConstructorHelpers::FObjectFinder<UInputMappingContext> IMCAss(TEXT("/Game/Input/IMC_Default.IMC_Default"));
	if (IMCAss.Succeeded()) DefaultMappingContext = IMCAss.Object;

	static ConstructorHelpers::FObjectFinder<UInputAction> IAMoveAss(TEXT("/Game/Input/Actions/IA_Move.IA_Move"));
	if (IAMoveAss.Succeeded()) MoveAction = IAMoveAss.Object;

	static ConstructorHelpers::FObjectFinder<UInputAction> IALookAss(TEXT("/Game/Input/Actions/IA_Look.IA_Look"));
	if (IALookAss.Succeeded()) LookAction = IALookAss.Object;

	static ConstructorHelpers::FObjectFinder<UInputAction> IAJumpAss(TEXT("/Game/Input/Actions/IA_Jump.IA_Jump"));
	if (IAJumpAss.Succeeded()) JumpAction = IAJumpAss.Object;

	// Arte slots — 4 starter artes (overridden by BP at runtime)
	EquippedArtes.SetNum(4);

	CurrentTP = MaxTP;
	BaseMaxTP = MaxTP;
	CurrentHP = MaxHP;
	BaseMaxHP = MaxHP;
	if (UCharacterMovementComponent* MoveComp = GetCharacterMovement())
	{
		BaseWalkSpeed = MoveComp->MaxWalkSpeed;
	}
}

void AIsekaiVillageCharacter::BeginPlay()
{
	Super::BeginPlay();

	if (USkeletalMeshComponent* MeshComp = GetMesh())
	{
		MeshComp->SetRelativeLocationAndRotation(
			FVector(0.0f, 0.0f, -NormalCapsuleHalfHeight),
			FRotator(0.0f, -90.0f, 0.0f)
		);
	}

	if (CameraBoom)
	{
		CameraBoom->TargetArmLength = 400.0f;
		CameraBoom->bUsePawnControlRotation = true;
		CameraBoom->SocketOffset = FVector(0.0f, 40.0f, 50.0f);
	}

	// Spawn magic circle actors (visual only)
	UWorld* World = GetWorld();
	if (World)
	{
		FActorSpawnParameters SpawnParams;
		SpawnParams.Owner = this;
		SpawnParams.Instigator = this;

		LeftHandCircleActor = World->SpawnActor<AProceduralMagicCircle>(AProceduralMagicCircle::StaticClass(), SpawnParams);
		RightHandCircleActor = World->SpawnActor<AProceduralMagicCircle>(AProceduralMagicCircle::StaticClass(), SpawnParams);
		GroundTargetCircleActor = World->SpawnActor<AProceduralMagicCircle>(AProceduralMagicCircle::StaticClass(), SpawnParams);
		if (GroundTargetCircleActor)
		{
			GroundTargetCircleActor->SetActorScale3D(FVector(1.8f));
			GroundTargetCircleActor->SetActorHiddenInGame(true);
		}
	}

	if (!SphereGrid)
	{
		SphereGrid = NewObject<USphereGridDataAsset>(this, TEXT("RuntimeCenterA"));
	}

	if (SphereGrid && UnlockedSphereNodes.Num() == 0)
	{
		UnlockSphereNode(SphereGrid->StartNodeID);
	}
	else
	{
		RefreshSphereGridBonuses();
	}

	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		if (GI->bReturningFromBattle)
		{
			SetActorLocationAndRotation(GI->ReturnOverworldPosition, GI->ReturnOverworldRotation);
			GI->bReturningFromBattle = false;
		}
		else if (GI->PendingEntryPoint != NAME_None)
		{
			bool bFound = false;
			for (TActorIterator<ATargetPoint> It(GetWorld()); It; ++It)
			{
				if (It->ActorHasTag(GI->PendingEntryPoint) || It->GetName().Contains(GI->PendingEntryPoint.ToString()))
				{
					SetActorLocationAndRotation(It->GetActorLocation() + GI->PendingSpawnPosition, GI->PendingSpawnRotation);
					bFound = true;
					break;
				}
			}
			if (!bFound && !GI->PendingSpawnPosition.IsNearlyZero())
			{
				SetActorLocationAndRotation(GI->PendingSpawnPosition, GI->PendingSpawnRotation);
			}
			GI->ClearPendingTransition();
		}
	}

	// Add Enhanced Input Context
	if (APlayerController* PlayerController = Cast<APlayerController>(Controller))
	{
		if (UEnhancedInputLocalPlayerSubsystem* Subsystem = ULocalPlayer::GetSubsystem<UEnhancedInputLocalPlayerSubsystem>(PlayerController->GetLocalPlayer()))
		{
			if (DefaultMappingContext)
			{
				Subsystem->AddMappingContext(DefaultMappingContext, 0);
			}
		}
	}
}

void AIsekaiVillageCharacter::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	// TP Regen (Tales style — 8/s out of combat)
	if (CurrentTP < MaxTP)
	{
		CurrentTP = FMath::Min(MaxTP, CurrentTP + TPRegenRate * DeltaTime);
	}

	// Dash cooldown
	if (DashCooldownRemaining > 0.0f)
	{
		DashCooldownRemaining = FMath::Max(0.0f, DashCooldownRemaining - DeltaTime);
	}

	// Focus Mode timer
	if (bIsFocusMode)
	{
		FocusModeTimer -= DeltaTime;
		if (FocusModeTimer <= 0.0f)
		{
			bIsFocusMode = false;
			bSilentCastReady = false;
			SetBulletTime(false);
		}
	}

	// Aerial dash reset on landing
	if (GetCharacterMovement()->IsMovingOnGround())
	{
		bHasAerialDash = true;
	}

	// Keep air control snappy
	GetCharacterMovement()->AirControl = bIsFocusMode ? 0.55f : 0.35f;
}

void AIsekaiVillageCharacter::SetupPlayerInputComponent(UInputComponent* PlayerInputComponent)
{
	Super::SetupPlayerInputComponent(PlayerInputComponent);

	if (!PlayerInputComponent) return;

	if (UEnhancedInputComponent* EnhancedInputComponent = Cast<UEnhancedInputComponent>(PlayerInputComponent))
	{
		if (MoveAction)
		{
			EnhancedInputComponent->BindAction(MoveAction, ETriggerEvent::Triggered, this, &AIsekaiVillageCharacter::EnhancedMove);
		}
		if (LookAction)
		{
			EnhancedInputComponent->BindAction(LookAction, ETriggerEvent::Triggered, this, &AIsekaiVillageCharacter::EnhancedLook);
		}
		if (JumpAction)
		{
			EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Started, this, &ACharacter::Jump);
			EnhancedInputComponent->BindAction(JumpAction, ETriggerEvent::Completed, this, &ACharacter::StopJumping);
		}
	}

	PlayerInputComponent->BindKey(EKeys::K, IE_Pressed, this, &AIsekaiVillageCharacter::ToggleSphereGrid);
	PlayerInputComponent->BindKey(EKeys::T, IE_Pressed, this, &AIsekaiVillageCharacter::TryTalkToGuild);

	// Mouse look fallbacks
	PlayerInputComponent->BindAxisKey(EKeys::MouseX, this, &APawn::AddControllerYawInput);
	PlayerInputComponent->BindAxisKey(EKeys::MouseY, this, &AIsekaiVillageCharacter::LookPitchDirect);

	// Arte bindings — LMB/RMB/Q/E → Arte1-4
	PlayerInputComponent->BindKey(EKeys::LeftMouseButton, IE_Pressed, this, &AIsekaiVillageCharacter::OnArte1Pressed);
	PlayerInputComponent->BindKey(EKeys::LeftMouseButton, IE_Released, this, &AIsekaiVillageCharacter::OnArte1Released);
	PlayerInputComponent->BindKey(EKeys::RightMouseButton, IE_Pressed, this, &AIsekaiVillageCharacter::OnArte2Pressed);
	PlayerInputComponent->BindKey(EKeys::RightMouseButton, IE_Released, this, &AIsekaiVillageCharacter::OnArte2Released);
	PlayerInputComponent->BindKey(EKeys::Q, IE_Pressed, this, &AIsekaiVillageCharacter::OnArte3Pressed);
	PlayerInputComponent->BindKey(EKeys::Q, IE_Released, this, &AIsekaiVillageCharacter::OnArte3Released);
	PlayerInputComponent->BindKey(EKeys::E, IE_Pressed, this, &AIsekaiVillageCharacter::OnArte4Pressed);
	PlayerInputComponent->BindKey(EKeys::E, IE_Released, this, &AIsekaiVillageCharacter::OnArte4Released);

	// Tab = Cancel arte
	PlayerInputComponent->BindKey(EKeys::Tab, IE_Pressed, this, &AIsekaiVillageCharacter::CancelArte);

	// F = Melee strike
	PlayerInputComponent->BindKey(EKeys::F, IE_Pressed, this, &AIsekaiVillageCharacter::PerformMeleeStrike);

	// Mouse Scroll = Cycle element
	PlayerInputComponent->BindKey(EKeys::MouseScrollUp, IE_Pressed, this, &AIsekaiVillageCharacter::OnScrollUp);
	PlayerInputComponent->BindKey(EKeys::MouseScrollDown, IE_Pressed, this, &AIsekaiVillageCharacter::OnScrollDown);

	// Movement: C = dodge, Shift = sprint, Ctrl = slide
	PlayerInputComponent->BindKey(EKeys::C, IE_Pressed, this, &AIsekaiVillageCharacter::TriggerDodge);
	PlayerInputComponent->BindKey(EKeys::LeftShift, IE_Pressed, this, &AIsekaiVillageCharacter::StartSprint);
	PlayerInputComponent->BindKey(EKeys::LeftShift, IE_Released, this, &AIsekaiVillageCharacter::StopSprint);
	PlayerInputComponent->BindKey(EKeys::LeftControl, IE_Pressed, this, &AIsekaiVillageCharacter::StartSlide);
	PlayerInputComponent->BindKey(EKeys::SpaceBar, IE_Pressed, this, &ACharacter::Jump);
	PlayerInputComponent->BindKey(EKeys::SpaceBar, IE_Released, this, &ACharacter::StopJumping);
}

// ───────── ENHANCED INPUT ─────────

void AIsekaiVillageCharacter::EnhancedMove(const FInputActionValue& Value)
{
	FVector2D MovementVector = Value.Get<FVector2D>();
	if (Controller != nullptr)
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
	FVector2D LookAxisVector = Value.Get<FVector2D>();
	if (Controller != nullptr)
	{
		AddControllerYawInput(LookAxisVector.X);
		AddControllerPitchInput(-LookAxisVector.Y);
	}
}

void AIsekaiVillageCharacter::OnArte1Pressed()  { TriggerArte(0); }
void AIsekaiVillageCharacter::OnArte1Released() { CancelArte(); }
void AIsekaiVillageCharacter::OnArte2Pressed()  { TriggerArte(1); }
void AIsekaiVillageCharacter::OnArte2Released() { CancelArte(); }
void AIsekaiVillageCharacter::OnArte3Pressed()  { TriggerArte(2); }
void AIsekaiVillageCharacter::OnArte3Released() { CancelArte(); }
void AIsekaiVillageCharacter::OnArte4Pressed()  { TriggerArte(3); }
void AIsekaiVillageCharacter::OnArte4Released() { CancelArte(); }
void AIsekaiVillageCharacter::OnScrollUp()   { CycleActiveElement(1); }
void AIsekaiVillageCharacter::OnScrollDown() { CycleActiveElement(-1); }

void AIsekaiVillageCharacter::MoveForwardAxis(float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), Value);
	}
}

void AIsekaiVillageCharacter::MoveRightAxis(float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), Value);
	}
}

void AIsekaiVillageCharacter::MoveForwardDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), 1.0f);
	}
}

void AIsekaiVillageCharacter::MoveBackwardDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::X), -1.0f);
	}
}

void AIsekaiVillageCharacter::MoveRightDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), 1.0f);
	}
}

void AIsekaiVillageCharacter::MoveLeftDirect(float Value)
{
	if (Controller && Value > 0.1f)
	{
		const FRotator YawRotation(0.0f, Controller->GetControlRotation().Yaw, 0.0f);
		AddMovementInput(FRotationMatrix(YawRotation).GetUnitAxis(EAxis::Y), -1.0f);
	}
}

void AIsekaiVillageCharacter::LookPitchDirect(float Value)
{
	if (Controller && !FMath::IsNearlyZero(Value))
	{
		AddControllerPitchInput(-Value);
	}
}

// ───────── ARTE SYSTEM (Tales TP) ─────────

void AIsekaiVillageCharacter::TriggerArte(int32 SlotIndex)
{
	if (bSphereGridOpen)
	{
		return;
	}
	if (!EquippedArtes.IsValidIndex(SlotIndex) || !EquippedArtes[SlotIndex]) return;

	UArteDataAsset* Arte = EquippedArtes[SlotIndex];
	if (CurrentTP < Arte->TP_Cost) return;

	SpendTP(Arte->TP_Cost);

	UWorld* World = GetWorld();
	if (!World) return;

	FActorSpawnParameters SpawnParams;
	SpawnParams.Instigator = this;
	SpawnParams.Owner = this;

	FVector AimDir = GetAimDirectionFromMouse();
	if (AimDir.IsNearlyZero()) AimDir = GetActorForwardVector();
	AimDir = AimDir.GetSafeNormal();

	FVector SpawnOrigin = GetActorLocation() + AimDir * 60.0f;

	ASpellProjectile* Proj = World->SpawnActor<ASpellProjectile>(ASpellProjectile::StaticClass(), SpawnOrigin, AimDir.Rotation(), SpawnParams);
	if (Proj)
	{
		Proj->InitProjectile(Arte->Element, Arte->Shape, 1.0f);
		UNiagaraSystem* FX = SpellVisuals ? SpellVisuals->GetProjectileFXForElement(Arte->Element) : nullptr;
		Proj->BindSpellVFX(FX);
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 1.5f, FColor::Cyan,
			FString::Printf(TEXT("Arte: %s (TP -%.0f)"), *Arte->ArteName.ToString(), Arte->TP_Cost));
	}
}

void AIsekaiVillageCharacter::CancelArte()
{
	// Nothing to cancel currently — arte is instant on press
}

bool AIsekaiVillageCharacter::SpendTP(float Amount)
{
	if (CurrentTP < Amount)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Red, TEXT("Not enough TP!"));
		}
		return false;
	}
	CurrentTP -= Amount;
	return true;
}

void AIsekaiVillageCharacter::RestoreTP(float Amount)
{
	CurrentTP = FMath::Min(MaxTP, CurrentTP + Amount);
}

void AIsekaiVillageCharacter::RestoreHP(float Amount)
{
	CurrentHP = FMath::Min(MaxHP, CurrentHP + Amount);
}

float AIsekaiVillageCharacter::TakeDamage(float DamageAmount, FDamageEvent const& DamageEvent, AController* EventInstigator, AActor* DamageCauser)
{
	const float Applied = Super::TakeDamage(DamageAmount, DamageEvent, EventInstigator, DamageCauser);
	CurrentHP = FMath::Max(0.0f, CurrentHP - Applied);
	return Applied;
}

bool AIsekaiVillageCharacter::UnlockSphereNode(FName NodeID)
{
	if (!SphereGrid || NodeID.IsNone())
	{
		return false;
	}
	if (UnlockedSphereNodes.Contains(NodeID))
	{
		return false;
	}
	if (!SphereGrid->IsNodeAdjacentToUnlocked(NodeID, UnlockedSphereNodes, bSphereGridFlipped))
	{
		return false;
	}

	const bool bStartingTile = !SphereGrid->HasUnlockedNodeOnFace(UnlockedSphereNodes, bSphereGridFlipped)
		&& NodeID == (bSphereGridFlipped ? SphereGrid->FlipStartNodeID : SphereGrid->StartNodeID);
	if (!bStartingTile)
	{
		if (SpherePoints < 1)
		{
			return false;
		}
		--SpherePoints;
	}

	UnlockedSphereNodes.Add(NodeID);
	RefreshSphereGridBonuses();
	return true;
}

void AIsekaiVillageCharacter::RefreshSphereGridBonuses()
{
	FSphereGridStatTotals Totals;
	if (SphereGrid)
	{
		Totals = SphereGrid->SumBonuses(UnlockedSphereNodes);
	}

	SphereHPBonus = Totals.HP;
	SphereInventoryBonus = Totals.Inventory;
	SphereCarryWeightBonus = Totals.CarryWeight;
	SphereTrustBonus = Totals.Trust;

	bSphereSkillDash = UnlockedSphereNodes.Contains(TEXT("CA_Adv_Dash"));
	bSphereSkillHunt = UnlockedSphereNodes.Contains(TEXT("CA_Adv_Hunt"));
	bSphereSkillDangerSense = UnlockedSphereNodes.Contains(TEXT("CA_Adv_DangerSense"));
	bSphereSkillTrailblaze = UnlockedSphereNodes.Contains(TEXT("CA_Adv_Trailblaze"));

	if (PartyReserve && SphereGrid)
	{
		int32 HireBonus = 0;
		for (const FName& NodeID : UnlockedSphereNodes)
		{
			FSphereNode Node;
			if (SphereGrid->GetNode(NodeID, Node) && Node.UnlockAction == TEXT("HireCap+1"))
			{
				++HireBonus;
			}
		}
		PartyReserve->ActivePartyCap = 2 + HireBonus;
	}

	const float PreviousMaxHP = MaxHP;
	MaxHP = BaseMaxHP + static_cast<float>(Totals.HP);
	if (MaxHP > PreviousMaxHP)
	{
		CurrentHP += (MaxHP - PreviousMaxHP);
	}
	CurrentHP = FMath::Min(CurrentHP, MaxHP);

	const float PreviousMaxTP = MaxTP;
	MaxTP = BaseMaxTP + static_cast<float>(Totals.TP);
	if (MaxTP > PreviousMaxTP)
	{
		CurrentTP += (MaxTP - PreviousMaxTP);
	}
	CurrentTP = FMath::Min(CurrentTP, MaxTP);

	if (UCharacterMovementComponent* MoveComp = GetCharacterMovement())
	{
		MoveComp->MaxWalkSpeed = BaseWalkSpeed * (1.0f + Totals.MoveSpeedPercent / 100.0f);
	}
}

bool AIsekaiVillageCharacter::FlipSphereGrid()
{
	if (bSphereGridFlipped || !SphereGrid || !SphereGrid->IsLifeFaceComplete(UnlockedSphereNodes))
	{
		return false;
	}

	bSphereGridFlipped = true;
	UnlockSphereNode(SphereGrid->FlipStartNodeID);
	return true;
}

void AIsekaiVillageCharacter::ToggleSphereGrid()
{
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AIsekaiVillageHUD* HUD = PC->GetHUD<AIsekaiVillageHUD>())
		{
			HUD->ToggleSphereGrid();
		}
	}
}

void AIsekaiVillageCharacter::TryTalkToGuild()
{
	if (bSphereGridOpen)
	{
		return;
	}

	TArray<AActor*> Overlaps;
	GetOverlappingActors(Overlaps, ATownZone::StaticClass());
	for (AActor* Actor : Overlaps)
	{
		if (ATownZone* Zone = Cast<ATownZone>(Actor))
		{
			Zone->TriggerTransition();
			return;
		}
	}

	GetOverlappingActors(Overlaps, AGuildMasterDesk::StaticClass());
	for (AActor* Actor : Overlaps)
	{
		if (AGuildMasterDesk* Desk = Cast<AGuildMasterDesk>(Actor))
		{
			Desk->TryHire(this);
			return;
		}
	}
}

void AIsekaiVillageCharacter::CycleActiveElement(int32 Direction)
{
	const TArray<EElement> Cycle = { EElement::Fire, EElement::Water, EElement::Earth, EElement::Wind };
	int32 Idx = Cycle.IndexOfByKey(ActiveElement);
	if (Idx == INDEX_NONE) Idx = 0;

	Idx = (Idx + Direction + Cycle.Num()) % Cycle.Num();
	ActiveElement = Cycle[Idx];

	if (GEngine)
	{
		FString ElementName = UEnum::GetValueAsString(ActiveElement);
		ElementName.Split(TEXT("::"), nullptr, &ElementName);
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan, FString::Printf(TEXT("Element: %s"), *ElementName));
	}
}

// ───────── MELEE (F key) ─────────

void AIsekaiVillageCharacter::PerformMeleeStrike()
{
	if (bSphereGridOpen)
	{
		return;
	}
	FVector Start = GetActorLocation();
	FVector End = Start + (GetActorForwardVector() * 220.0f);

	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(70.0f);
	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);

	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, QueryParams))
	{
		for (const FHitResult& Hit : Hits)
		{
			AActor* Target = Hit.GetActor();
			if (Target && Target != this)
			{
				FPointDamageEvent DmgEvent(40.0f, Hit, GetActorForwardVector(), nullptr);
				Target->TakeDamage(40.0f, DmgEvent, GetController(), this);

				ACharacter* TargetChar = Cast<ACharacter>(Target);
				if (TargetChar)
				{
					FVector KnockbackDir = (Target->GetActorLocation() - GetActorLocation()).GetSafeNormal();
					KnockbackDir.Z = 0.35f;
					TargetChar->LaunchCharacter(KnockbackDir * 1200.0f, true, true);
				}
			}
		}
	}
}

// ───────── MAGIC CIRCLES (visual only) ─────────

void AIsekaiVillageCharacter::UpdateMagicCircles()
{
	AProceduralMagicCircle* LeftCircle = GetLeftCircleActor();
	if (LeftCircle)
	{
		LeftCircle->SetActiveElement(ActiveElement);
		LeftCircle->SetVisualState(ECircleVisualState::Casting);
		LeftCircle->RebuildCircle();
	}

	AProceduralMagicCircle* RightCircle = GetRightCircleActor();
	if (RightCircle)
	{
		RightCircle->SetActiveElement(ActiveElement);
		RightCircle->SetVisualState(ECircleVisualState::Casting);
		RightCircle->RebuildCircle();
	}
}

// ───────── MOVEMENT (Nier) ─────────

void AIsekaiVillageCharacter::TriggerDodge()
{
	if (DashCooldownRemaining > 0.0f) return;

	bool bIsAirborne = !GetCharacterMovement()->IsMovingOnGround();

	if (bIsAirborne && bHasAerialDash)
	{
		FVector DashDir = GetCharacterMovement()->Velocity.GetSafeNormal();
		if (DashDir.IsNearlyZero())
		{
			if (Controller)
			{
				FRotator CamRot = Controller->GetControlRotation();
				DashDir = FRotationMatrix(FRotator(0.0f, CamRot.Yaw, 0.0f)).GetUnitAxis(EAxis::X);
			}
			else
			{
				DashDir = GetActorForwardVector();
			}
		}
		FVector AerialForce = DashDir * AerialDashStrength;
		AerialForce.Z = 300.0f;
		LaunchCharacter(AerialForce, true, true);
		bHasAerialDash = false;
	}
	else if (!bIsAirborne)
	{
		FVector DashDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
		if (DashDir.IsNearlyZero()) DashDir = GetActorForwardVector();

		LaunchCharacter(DashDir * 1700.0f, true, true);
		ActivateFocusMode();
	}

	DashCooldownRemaining = DashCooldown;
}

void AIsekaiVillageCharacter::ActivateFocusMode()
{
	if (bIsFocusMode) return;

	bIsFocusMode = true;
	bSilentCastReady = true;
	FocusModeTimer = FocusModeDuration;
	SetBulletTime(true, 0.25f);

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, FocusModeDuration, FColor::Cyan,
			TEXT("FOCUS MODE — Silent Cast Ready"), true, FVector2D(1.8f, 1.8f));
	}
}

void AIsekaiVillageCharacter::StartSprint()
{
	bIsSprinting = true;
	GetCharacterMovement()->MaxWalkSpeed = 900.0f;
}

void AIsekaiVillageCharacter::StopSprint()
{
	bIsSprinting = false;
	GetCharacterMovement()->MaxWalkSpeed = 600.0f;
}

void AIsekaiVillageCharacter::StartSlide()
{
	if (GetCharacterMovement()->IsMovingOnGround() && !bIsSliding)
	{
		bIsSliding = true;
		SlideTimer = 0.5f;
		SlideDirection = GetCharacterMovement()->Velocity.GetSafeNormal2D();
		if (SlideDirection.IsNearlyZero()) SlideDirection = GetActorForwardVector();
		GetCapsuleComponent()->SetCapsuleHalfHeight(SlideCapsuleHalfHeight);
	}
}

void AIsekaiVillageCharacter::StopSlide()
{
	bIsSliding = false;
	SlideTimer = 0.0f;
	GetCapsuleComponent()->SetCapsuleHalfHeight(NormalCapsuleHalfHeight);
	GetCharacterMovement()->MaxWalkSpeed = 600.0f;
}

// ───────── HELPERS ─────────

void AIsekaiVillageCharacter::SetBulletTime(bool bActive, float Dilation)
{
	bIsBulletTime = bActive;
	UWorld* World = GetWorld();
	if (!World) return;

	float TargetDilation = bActive ? Dilation : 1.0f;
	UGameplayStatics::SetGlobalTimeDilation(World, TargetDilation);
	CustomTimeDilation = bActive ? (1.0f / Dilation) : 1.0f;
}

FVector AIsekaiVillageCharacter::GetGroundAimLocation() const
{
	FVector AimDir = GetAimDirectionFromMouse();
	AimDir.Z = FMath::Clamp(AimDir.Z, -0.85f, 0.85f);
	AimDir = AimDir.GetSafeNormal();
	if (AimDir.IsNearlyZero())
	{
		AimDir = GetActorForwardVector();
	}

	FVector TargetPos = GetActorLocation() + (AimDir * 1200.0f);

	FHitResult Hit;
	FCollisionQueryParams Params;
	Params.AddIgnoredActor(this);
	const FVector TraceStart = TargetPos + FVector(0, 0, 800.0f);
	const FVector TraceEnd = TargetPos - FVector(0, 0, 4000.0f);
	if (GetWorld() && GetWorld()->LineTraceSingleByChannel(Hit, TraceStart, TraceEnd, ECC_Visibility, Params))
	{
		TargetPos = Hit.ImpactPoint;
	}
	else
	{
		TargetPos.Z = GetActorLocation().Z - NormalCapsuleHalfHeight;
	}

	return TargetPos;
}

FVector AIsekaiVillageCharacter::GetAimDirectionFromMouse() const
{
	if (Controller)
	{
		const FRotator CamRot = Controller->GetControlRotation();
		FVector Dir = CamRot.Vector();
		if (Dir.IsNearlyZero())
		{
			return GetActorForwardVector();
		}
		return Dir.GetSafeNormal();
	}
	return GetActorForwardVector();
}

AProceduralMagicCircle* AIsekaiVillageCharacter::GetLeftCircleActor() const
{
	return LeftHandCircleActor;
}

AProceduralMagicCircle* AIsekaiVillageCharacter::GetRightCircleActor() const
{
	return RightHandCircleActor;
}

AProceduralMagicCircle* AIsekaiVillageCharacter::GetGroundTargetCircleActor() const
{
	return GroundTargetCircleActor;
}
