// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageCharacter.cpp — Tales TP artes + Nier movement (clean rewrite, no old magic)

#include "IsekaiVillageCharacter.h"
#include "IsekaiVillageHUD.h"
#include "SphereGridDataAsset.h"
#include "PartyReserveComponent.h"
#include "GolemSparring.h"
#include "GolemHallWidget.h"
#include "ShopForgeWidget.h"
#include "TownServiceWidget.h"
#include "DayBoardCatalogWidgets.h"
#include "LakeFishingSpot.h"
#include "TowerExpedition.h"
#include "BuildEditComponent.h"
#include "GatherInventoryComponent.h"
#include "TreeChopComponent.h"
#include "MineOreVein.h"
#include "DebrisActor.h"
#include "LinchpinProp.h"
#include "GuildMasterDesk.h"
#include "BlacksmithForge.h"
#include "TownZone.h"
#include "VillageCitizen.h"
#include "VillageRuntime.h"
#include "DayBoard.h"
#include "TownPlot.h"
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

static AVillageRuntime* TownBuilder(const AIsekaiVillageCharacter* Player);

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
	BuildEdit = CreateDefaultSubobject<UBuildEditComponent>(TEXT("BuildEdit"));
	Gather = CreateDefaultSubobject<UGatherInventoryComponent>(TEXT("Gather"));
	TreeChop = CreateDefaultSubobject<UTreeChopComponent>(TEXT("TreeChop"));

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

	if (EquippedArtes.Num() < 4)
	{
		EquippedArtes.SetNum(4);
	}
	auto MakeStarterArte = [this](const TCHAR* Name, EElement Elem, FName Shape, float TPCost, int32 Multicast) -> UArteDataAsset*
	{
		UArteDataAsset* Arte = NewObject<UArteDataAsset>(this);
		Arte->ArteName = FText::FromString(Name);
		Arte->Element = Elem;
		Arte->Shape = Shape;
		Arte->TP_Cost = TPCost;
		Arte->TP_HoldCost = TPCost * 2.0f;
		Arte->MulticastCount = Multicast;
		return Arte;
	};
	if (!EquippedArtes[0]) EquippedArtes[0] = MakeStarterArte(TEXT("Elemental Lance"), ActiveElement, TEXT("spear"), 12.0f, 1);
	if (!EquippedArtes[1]) EquippedArtes[1] = MakeStarterArte(TEXT("Aqua Wave"), EElement::Water, TEXT("wave"), 14.0f, 1);
	if (!EquippedArtes[2]) EquippedArtes[2] = MakeStarterArte(TEXT("Terra Seeker"), EElement::Earth, TEXT("homing"), 18.0f, 1);
	if (!EquippedArtes[3]) EquippedArtes[3] = MakeStarterArte(TEXT("Gale Fan"), EElement::Wind, TEXT("spear"), 16.0f, 3);

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

	// TP Regen (Tales style — 8/s base + Magic/TPConserve scaling)
	if (CurrentTP < MaxTP)
	{
		CurrentTP = FMath::Min(MaxTP, CurrentTP + TPRegenRate * DeltaTime);
	}
	if (HasSphereSkill(TEXT("BathhouseRegen")) && CurrentHP < MaxHP)
	{
		ATowerExpedition* Tower = ATowerExpedition::Find(this);
		if (AVillageRuntime* Village = (!Tower || !Tower->bInside) ? TownBuilder(this) : nullptr; Village && Village->HasBuilding(ETownBuilding::Bath))
		{
			RestoreHP(2.0f * DeltaTime);
		}
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
	PlayerInputComponent->BindKey(EKeys::N, IE_Pressed, this, &AIsekaiVillageCharacter::CycleSphereDisc);
	PlayerInputComponent->BindKey(EKeys::T, IE_Pressed, this, &AIsekaiVillageCharacter::TryTalkToGuild);
	PlayerInputComponent->BindKey(EKeys::Y, IE_Pressed, this, &AIsekaiVillageCharacter::BuyShopWood);
	PlayerInputComponent->BindKey(EKeys::U, IE_Pressed, this, &AIsekaiVillageCharacter::ToggleStationMenu);
	PlayerInputComponent->BindKey(EKeys::F5, IE_Pressed, this, &AIsekaiVillageCharacter::SaveVillageProgress);
 PlayerInputComponent->BindKey(EKeys::J,IE_Pressed,this,&AIsekaiVillageCharacter::ToggleSparring);
 PlayerInputComponent->BindKey(EKeys::H,IE_Pressed,this,&AIsekaiVillageCharacter::ToggleAdventureHall);
 PlayerInputComponent->BindKey(EKeys::G,IE_Pressed,this,&AIsekaiVillageCharacter::TowerInteract);
 PlayerInputComponent->BindKey(EKeys::V,IE_Pressed,this,&AIsekaiVillageCharacter::TowerReturn);
 PlayerInputComponent->BindKey(EKeys::P,IE_Pressed,this,&AIsekaiVillageCharacter::OnBuildTogglePropMode);
 PlayerInputComponent->BindKey(EKeys::One,IE_Pressed,this,&AIsekaiVillageCharacter::SparStrike);
 PlayerInputComponent->BindKey(EKeys::Two,IE_Pressed,this,&AIsekaiVillageCharacter::SparDefend);
 PlayerInputComponent->BindKey(EKeys::Three,IE_Pressed,this,&AIsekaiVillageCharacter::SparGuard);
 PlayerInputComponent->BindKey(EKeys::Four,IE_Pressed,this,&AIsekaiVillageCharacter::SparBolt);
 PlayerInputComponent->BindKey(EKeys::Five,IE_Pressed,this,&AIsekaiVillageCharacter::SparHeal);
 PlayerInputComponent->BindKey(EKeys::Six,IE_Pressed,this,&AIsekaiVillageCharacter::SparEvade);
	PlayerInputComponent->BindKey(EKeys::B, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildToggle);
	PlayerInputComponent->BindKey(EKeys::R, IE_Pressed, this, &AIsekaiVillageCharacter::OnRotateTownBuilding);
	PlayerInputComponent->BindKey(EKeys::Z, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildCornerPullIn);
	PlayerInputComponent->BindKey(EKeys::C, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildCornerPullOut);
	PlayerInputComponent->BindKey(EKeys::M, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildCycleWallStyle);
	PlayerInputComponent->BindKey(EKeys::X, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildCycleMaterial);
	PlayerInputComponent->BindKey(EKeys::V, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildToggleFreeform);
	PlayerInputComponent->BindKey(EKeys::RightBracket, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildScaleUp);
	PlayerInputComponent->BindKey(EKeys::LeftBracket, IE_Pressed, this, &AIsekaiVillageCharacter::OnBuildScaleDown);

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
	PlayerInputComponent->BindKey(EKeys::Tab, IE_Pressed, this, &AIsekaiVillageCharacter::SparCycleTarget);

	// F = Melee strike
	PlayerInputComponent->BindKey(EKeys::F, IE_Pressed, this, &AIsekaiVillageCharacter::PerformMeleeStrike);

	// Mouse Scroll = Cycle element
	PlayerInputComponent->BindKey(EKeys::MouseScrollUp, IE_Pressed, this, &AIsekaiVillageCharacter::OnScrollUp);
	PlayerInputComponent->BindKey(EKeys::MouseScrollDown, IE_Pressed, this, &AIsekaiVillageCharacter::OnScrollDown);
	PlayerInputComponent->BindKey(EKeys::PageUp, IE_Pressed, this, &AIsekaiVillageCharacter::OnScrollUp);
	PlayerInputComponent->BindKey(EKeys::PageDown, IE_Pressed, this, &AIsekaiVillageCharacter::OnScrollDown);

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

bool AIsekaiVillageCharacter::IsBuildMode() const
{
	return BuildEdit && BuildEdit->bBuildMode;
}

static AVillageRuntime* TownBuilder(const AIsekaiVillageCharacter* Player)
{
	if (Player && Player->GetWorld())
		for (TActorIterator<AVillageRuntime> It(Player->GetWorld()); It; ++It)
			if (It->bUseAuthoredPlots && !It->BuildingCatalog.IsEmpty()) return *It;
	return nullptr;
}

void AIsekaiVillageCharacter::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
 CloseAllModals();
	if (AVillageRuntime* Village = TownBuilder(this); Village && Village->bUseGolemVillage) Village->SaveVillageState(this);
	Super::EndPlay(EndPlayReason);
}

void AIsekaiVillageCharacter::BuyShopWood()
{
	if (bSphereGridOpen) return;
	if (AVillageRuntime* Village = TownBuilder(this); Village && Village->bUseGolemVillage && !Village->bBuildingCatalogOpen)
		Village->TradeWood(Village->NearestGolemShop(GetActorLocation()), true, this);
}

void AIsekaiVillageCharacter::SaveVillageProgress()
{
	if (AVillageRuntime* Village = TownBuilder(this); Village && Village->bUseGolemVillage)
	{
		const bool Saved = Village->SaveVillageState(this);
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.f, Saved ? FColor::Green : FColor::Red, Saved ? TEXT("Village saved.") : TEXT("Village save failed."));
	}
}

void AIsekaiVillageCharacter::OnRotateTownBuilding()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->RotatePlacement(90.0f);
		return;
	}
	if (AVillageRuntime* Village=TownBuilder(this)) Village->RotateBuilding();
}

void AIsekaiVillageCharacter::OnBuildToggle()
{
	if (auto* T=ATowerExpedition::Find(this); T && T->bInside) return;
	if (HasBlockingModalUI()) return;
	if (!BuildEdit)
	{
		return;
	}
	if (!BuildEdit->bBuildMode && GetActorLocation().Z < -50000.0f)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("Piece edit is only unlocked on El Ruhn."));
		}
		return;
	}
	BuildEdit->ToggleBuildMode();
}

void AIsekaiVillageCharacter::OnBuildCornerPullIn()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->NudgeActiveCorner(-12.0f);
	}
}

void AIsekaiVillageCharacter::OnBuildCornerPullOut()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->NudgeActiveCorner(12.0f);
	}
}

void AIsekaiVillageCharacter::OnBuildToggleWheel()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->ToggleBuildWheel();
	}
}

void AIsekaiVillageCharacter::OnBuildTogglePropMode()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->TogglePropPlacementMode();
	}
	else
	{
		TowerRations();
	}
}

void AIsekaiVillageCharacter::OnBuildCycleWallStyle()
{
	if (IsBuildMode() && BuildEdit)
	{
		if (BuildEdit->bPlacingProps)
		{
			BuildEdit->CyclePropType(1);
		}
		else
		{
			BuildEdit->CycleWallStyle();
		}
	}
}

void AIsekaiVillageCharacter::OnBuildCycleMaterial()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->CycleExteriorMaterial();
		BuildEdit->CycleInteriorMaterial();
	}
}

void AIsekaiVillageCharacter::OnBuildToggleFreeform()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->ToggleFreeform();
	}
}

void AIsekaiVillageCharacter::OnBuildScaleUp()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->AdjustScale(1.25f);
	}
}

void AIsekaiVillageCharacter::OnBuildScaleDown()
{
	if (IsBuildMode() && BuildEdit)
	{
		BuildEdit->AdjustScale(0.8f);
	}
}

void AIsekaiVillageCharacter::OnArte1Pressed()
{
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen)
	{
		const FName Id=Village->TargetPlot(this);
		if (const FTownPlot* Plot=Village->FindPlot(Id); Plot && !Plot->bBuilt) Village->TryBuildPlot(Id,this);
		return;
	}
	if (IsBuildMode()) { BuildEdit->PlaceOrSelect(); return; }
	TriggerArte(0);
}
void AIsekaiVillageCharacter::OnArte1Released() { if (!IsBuildMode()) CancelArte(); }
void AIsekaiVillageCharacter::OnArte2Pressed()
{
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen) { Village->CancelBuildingPlacement(); return; }
	if (IsBuildMode()) { BuildEdit->RemoveSelected(); return; }
	TriggerArte(1);
}
void AIsekaiVillageCharacter::OnArte2Released() { if (!IsBuildMode()) CancelArte(); }
void AIsekaiVillageCharacter::OnArte3Pressed()
{
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen) return;
	if (IsBuildMode()) { BuildEdit->CycleOccupancy(); return; }
	TriggerArte(2);
}
void AIsekaiVillageCharacter::OnArte3Released() { if (!IsBuildMode()) CancelArte(); }
void AIsekaiVillageCharacter::OnArte4Pressed()
{
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen) return;
	if (IsBuildMode()) { BuildEdit->CycleCornerStyle(); return; }
	TriggerArte(3);
}
void AIsekaiVillageCharacter::OnArte4Released() { if (!IsBuildMode()) CancelArte(); }
void AIsekaiVillageCharacter::OnScrollUp()
{
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen) { Village->CycleBuilding(-1); return; }
	if (IsBuildMode()) { BuildEdit->CyclePieceType(1); return; }
	CycleActiveElement(1);
}
void AIsekaiVillageCharacter::OnScrollDown()
{
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen) { Village->CycleBuilding(1); return; }
	if (IsBuildMode()) { BuildEdit->CyclePieceType(-1); return; }
	CycleActiveElement(-1);
}

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
 if(HasBlockingModalUI())return;
 if(auto* B=AGolemSparring::FindFor(this);B && B->Phase!=TEXT("Result"))return;
	if (bSphereGridOpen)
	{
		return;
	}
	if (!EquippedArtes.IsValidIndex(SlotIndex) || !EquippedArtes[SlotIndex]) return;

	UArteDataAsset* Arte = EquippedArtes[SlotIndex];
	const bool bSilentCast = bIsFocusMode && bSilentCastReady;
	const float EffectiveCost = bSilentCast ? 0.0f : (Arte->TP_Cost * (HasSphereSkill(TEXT("TPConserve")) ? 0.80f : 1.0f));
	if (CurrentTP < EffectiveCost) return;

	if (bSilentCast)
	{
		bSilentCastReady = false;
	}
	else if (EffectiveCost > 0.0f)
	{
		SpendTP(EffectiveCost);
	}

	UWorld* World = GetWorld();
	if (!World) return;

	const EElement CastElem = (SlotIndex == 0) ? ActiveElement : Arte->Element;
	const int32 FanCount = HasSphereSkill(TEXT("SpreadFan")) ? FMath::Max(3, Arte->MulticastCount) : FMath::Max(1, Arte->MulticastCount);
	float SpellDamage = 30.0f + static_cast<float>(SphereTotals.Magic) * 2.5f;
	if (bSilentCast && HasSphereSkill(TEXT("QuickCast")))
	{
		SpellDamage *= 1.35f;
	}
	if ((bIsSliding || bIsFocusMode) && HasSphereSkill(TEXT("AmbushStrike")))
	{
		SpellDamage *= 1.5f;
	}

	FActorSpawnParameters SpawnParams;
	SpawnParams.Instigator = this;
	SpawnParams.Owner = this;

	FVector AimDir = GetAimDirectionFromMouse();
	if (AimDir.IsNearlyZero()) AimDir = GetActorForwardVector();
	AimDir = AimDir.GetSafeNormal();

	const float SpreadStep = (FanCount > 1) ? (14.0f / static_cast<float>(FanCount - 1)) : 0.0f;
	for (int32 Shot = 0; Shot < FanCount; ++Shot)
	{
		const float YawOffset = (FanCount > 1) ? ((static_cast<float>(Shot) - static_cast<float>(FanCount - 1) * 0.5f) * SpreadStep) : 0.0f;
		const FRotator ShotRot = AimDir.Rotation() + FRotator(0.0f, YawOffset, 0.0f);
		const FVector SpawnOrigin = GetActorLocation() + ShotRot.Vector() * 60.0f;
		ASpellProjectile* Proj = World->SpawnActor<ASpellProjectile>(ASpellProjectile::StaticClass(), SpawnOrigin, ShotRot, SpawnParams);
		if (Proj)
		{
			Proj->InitProjectile(CastElem, Arte->Shape, bSilentCast ? 1.0f : 0.0f);
			Proj->BaseDamage = SpellDamage;
			if (HasSphereSkill(TEXT("BowSpread")))
			{
				Proj->PierceCount += 1;
			}
			UNiagaraSystem* FX = SpellVisuals ? SpellVisuals->GetProjectileFXForElement(CastElem) : nullptr;
			Proj->BindSpellVFX(FX);
		}
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 1.5f, FColor::Cyan,
			FString::Printf(TEXT("Arte: %s (TP -%.0f%s)"), *Arte->ArteName.ToString(), EffectiveCost, bSilentCast ? TEXT(" SILENT") : TEXT("")));
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
	const float ResCut = FMath::Clamp(SphereTotals.ResPercent / 100.0f + (HasSphereSkill(TEXT("AegisBarrier")) ? 0.10f : 0.0f), 0.0f, 0.75f);
	const float Applied = Super::TakeDamage(DamageAmount * (1.0f - ResCut), DamageEvent, EventInstigator, DamageCauser);
	CurrentHP = FMath::Max(0.0f, CurrentHP - Applied);
	return Applied;
}

bool AIsekaiVillageCharacter::UnlockSphereNode(FName NodeID)
{
	if (!SphereGrid || NodeID.IsNone())
	{
		return false;
	}
	if (UnlockedSphereNodes.Contains(NodeID) || !SphereGrid->IsDiscUnlocked(SphereDisc, UnlockedSphereNodes))
	{
		return false;
	}
	if (!SphereGrid->IsNodeAdjacentOnDisc(NodeID, UnlockedSphereNodes, SphereDisc, SphereFaceFlipped()))
	{
		return false;
	}

	const bool bStartingTile = !SphereGrid->HasUnlockedOnDisc(SphereDisc, SphereFaceFlipped(), UnlockedSphereNodes)
		&& NodeID == SphereGrid->FaceStart(SphereDisc, SphereFaceFlipped());
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
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AIsekaiVillageHUD* HUD = PC->GetHUD<AIsekaiVillageHUD>())
		{
			if (bSphereGridOpen)
			{
				HUD->RefreshSphereGrid();
			}
		}
	}
	return true;
}

void AIsekaiVillageCharacter::RefreshSphereGridBonuses()
{
	FSphereGridStatTotals Totals;
	if (SphereGrid)
	{
		Totals = SphereGrid->SumBonuses(UnlockedSphereNodes);
	}
	SphereTotals = Totals;

	SphereHPBonus = Totals.HP;
	SphereInventoryBonus = Totals.Inventory;
	SphereCarryWeightBonus = Totals.CarryWeight;
	SphereTrustBonus = Totals.Trust;
	SphereBuildSpeed = Totals.BuildSpeedPercent;
	SphereYieldBonus = 0;

	UnlockedSphereActions.Reset();
	int32 HireBonus = 0;
	for (const FName& NodeID : UnlockedSphereNodes)
	{
		FSphereNode Node;
		if (!SphereGrid || !SphereGrid->GetNode(NodeID, Node) || Node.UnlockAction.IsNone())
		{
			continue;
		}
		UnlockedSphereActions.Add(Node.UnlockAction);
		if (Node.UnlockAction == TEXT("Yield+1"))
		{
			++SphereYieldBonus;
		}
		else if (Node.UnlockAction == TEXT("HireCap+1"))
		{
			++HireBonus;
		}
	}

	bSphereSkillDash = HasSphereSkill(TEXT("Dash"));
	bSphereSkillHunt = HasSphereSkill(TEXT("Hunt"));
	bSphereSkillDangerSense = HasSphereSkill(TEXT("DangerSense"));
	bSphereSkillTrailblaze = HasSphereSkill(TEXT("Trailblaze"));
	bSphereSkillJab = HasSphereSkill(TEXT("Jab"));
	bSphereSkillDoubleKick = HasSphereSkill(TEXT("DoubleKick"));
	bSphereSkillHawkSmash = HasSphereSkill(TEXT("HawkSmash"));

	if (!bCenterBUnlocked && SphereGrid && SphereGrid->IsDiscUnlocked(1, UnlockedSphereNodes))
	{
		bCenterBUnlocked = true;
	}

	if (PartyReserve)
	{
		int32 TownBonus = 0;
		if (UWorld* World = GetWorld())
		{
			for (TActorIterator<AVillageRuntime> It(World); It; ++It)
			{
				if (It->HasBuilding(ETownBuilding::Academy)) ++TownBonus;
				if (It->HasBuilding(ETownBuilding::Castle)) ++TownBonus;
				break;
			}
		}
		PartyReserve->ActivePartyCap = 2 + HireBonus + TownBonus;
	}

	TPRegenRate = 8.0f + (HasSphereSkill(TEXT("TPConserve")) ? 2.0f : 0.0f) + static_cast<float>(Totals.Magic) * 0.15f;

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

	UpdateMovementSpeed();
}

bool AIsekaiVillageCharacter::FlipSphereGrid()
{
	if (!SphereGrid || !SphereGrid->DiscHasFlip(SphereDisc))
	{
		return false;
	}
	if (SphereDisc == 1)
	{
		if (bWorkFlipped || !SphereGrid->IsFaceComplete(1, false, UnlockedSphereNodes))
		{
			return false;
		}
		bWorkFlipped = true;
		UnlockSphereNode(SphereGrid->VillagerStartNodeID);
		return true;
	}
	if (bSphereGridFlipped || !SphereGrid->IsLifeFaceComplete(UnlockedSphereNodes))
	{
		return false;
	}
	bSphereGridFlipped = true;
	UnlockSphereNode(SphereGrid->FlipStartNodeID);
	return true;
}

void AIsekaiVillageCharacter::CycleSphereDisc()
{
	if (!bSphereGridOpen || !SphereGrid)
	{
		return;
	}
	const int32 Count = SphereGrid->DiscCount();
	for (int32 Step = 1; Step < Count; ++Step)
	{
		const int32 Candidate = (SphereDisc + Step) % Count;
		if (SphereGrid->IsDiscUnlocked(Candidate, UnlockedSphereNodes))
		{
			SphereDisc = Candidate;
			break;
		}
	}
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AIsekaiVillageHUD* HUD = PC->GetHUD<AIsekaiVillageHUD>())
		{
			HUD->RefreshSphereGrid();
		}
	}
}

bool AIsekaiVillageCharacter::SelectSphereDisc(int32 DiscIndex)
{
	if (!SphereGrid || DiscIndex < 0 || DiscIndex >= SphereGrid->DiscCount())
	{
		return false;
	}
	SphereDisc = DiscIndex;
	if (APlayerController* PC = Cast<APlayerController>(GetController()))
	{
		if (AIsekaiVillageHUD* HUD = PC->GetHUD<AIsekaiVillageHUD>())
		{
			HUD->RefreshSphereGrid();
		}
	}
	return true;
}

void AIsekaiVillageCharacter::ToggleSphereGrid()
{
 CloseAllModals();
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
	if (AVillageRuntime* Village=TownBuilder(this); Village && Village->bBuildingCatalogOpen)
	{
		const FName Id=Village->TargetPlot(this);
		if (const FTownPlot* Plot=Village->FindPlot(Id); Plot && !Plot->bBuilt) Village->TryBuildPlot(Id,this);
		return;
	}
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

	if (AVillageRuntime* Village = TownBuilder(this); Village && Village->WithdrawHallSupplies(this)) return;

	if (IsValid(NearbyCitizen))
	{
		NearbyCitizen->TryPlayerOffer(this);
		return;
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

	GetOverlappingActors(Overlaps, ABlacksmithForge::StaticClass());
	for (AActor* Actor : Overlaps)
	{
		if (ABlacksmithForge* Forge = Cast<ABlacksmithForge>(Actor))
		{
			Forge->TryForge(this);
			return;
		}
	}

	GetOverlappingActors(Overlaps, ADayBoard::StaticClass());
	for (AActor* Actor : Overlaps)
	{
		if (ADayBoard* Board = Cast<ADayBoard>(Actor))
		{
			Board->TryUse(this);
			return;
		}
	}

	if (IsValid(NearbyPlot))
	{
		NearbyPlot->TryUse(this);
		return;
	}

	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			if (It->TryShopOffer(this))
			{
				return;
			}
		}
	}
	TArray<AActor*> DebrisOverlaps;
	GetOverlappingActors(DebrisOverlaps, ADebrisActor::StaticClass());
	for (AActor* Actor : DebrisOverlaps)
	{
		if (ADebrisActor* Debris = Cast<ADebrisActor>(Actor); Debris && Debris->TrySalvage(this))
		{
			return;
		}
	}
	TArray<AActor*> FishOverlaps;
	GetOverlappingActors(FishOverlaps, ALakeFishingSpot::StaticClass());
	for (AActor* Actor : FishOverlaps)
	{
		if (ALakeFishingSpot* Spot = Cast<ALakeFishingSpot>(Actor); Spot && Spot->TryFish(this))
		{
			return;
		}
	}
	if (UWorld* ResourceWorld = GetWorld())
	{
		for (TActorIterator<AMineOreVein> It(ResourceWorld); It; ++It)
		{
			if (FVector::DistSquared(GetActorLocation(), It->GetActorLocation()) <= FMath::Square(320.0f) && It->TryMine(this))
			{
				return;
			}
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

int32 AIsekaiVillageCharacter::GetGatherLevel() const
{
	int32 FromMine = 1;
	if (Gather)
	{
		const int32 Ore = Gather->GetCount(TEXT("Copper")) + Gather->GetCount(TEXT("Iron")) + Gather->GetCount(TEXT("Crystal"));
		FromMine = 1 + Ore / 6;
	}
	const int32 FromSphere = 1 + FMath::Max(0, UnlockedSphereNodes.Num() - 1);
	return FMath::Max(FromMine, FromSphere);
}

bool AIsekaiVillageCharacter::TryGather()
{
	if (bSphereGridOpen || IsBuildMode())
	{
		return false;
	}
	if (TreeChop && TreeChop->TryChop())
	{
		return true;
	}
	FVector Start = GetActorLocation();
	FVector End = Start + GetActorForwardVector() * 240.0f;
	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(80.0f);
	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);
	if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Visibility, Sphere, QueryParams))
	{
		for (const FHitResult& Hit : Hits)
		{
			if (AMineOreVein* Vein = Cast<AMineOreVein>(Hit.GetActor()))
			{
				return Vein->TryMine(this);
			}
			if (ADebrisActor* Debris = Cast<ADebrisActor>(Hit.GetActor()))
			{
				return Debris->TrySalvage(this);
			}
			if (ALakeFishingSpot* Spot = Cast<ALakeFishingSpot>(Hit.GetActor()))
			{
				return Spot->TryFish(this);
			}
			if (ALinchpinProp* Prop = Cast<ALinchpinProp>(Hit.GetActor()))
			{
				return Prop->TryInteract(this);
			}
		}
	}
	TArray<AActor*> DebrisOverlaps;
	GetOverlappingActors(DebrisOverlaps, ADebrisActor::StaticClass());
	for (AActor* Actor : DebrisOverlaps)
	{
		if (ADebrisActor* Debris = Cast<ADebrisActor>(Actor); Debris && Debris->TrySalvage(this))
		{
			return true;
		}
	}
	TArray<AActor*> FishOverlaps;
	GetOverlappingActors(FishOverlaps, ALakeFishingSpot::StaticClass());
	for (AActor* Actor : FishOverlaps)
	{
		if (ALakeFishingSpot* Spot = Cast<ALakeFishingSpot>(Actor); Spot && Spot->TryFish(this))
		{
			return true;
		}
	}
	TArray<AActor*> PropOverlaps;
	GetOverlappingActors(PropOverlaps, ALinchpinProp::StaticClass());
	for (AActor* Actor : PropOverlaps)
	{
		if (ALinchpinProp* Prop = Cast<ALinchpinProp>(Actor); Prop && Prop->TryInteract(this))
		{
			return true;
		}
	}
	return false;
}

void AIsekaiVillageCharacter::PerformMeleeStrike()
{
 if(HasBlockingModalUI())return;
 if(auto* B=AGolemSparring::FindFor(this);B && B->Phase!=TEXT("Result"))return;
	if (bSphereGridOpen)
	{
		return;
	}
	if (TryGather())
	{
		return;
	}
	FVector Start = GetActorLocation();
	FVector End = Start + (GetActorForwardVector() * 220.0f);

	const float Radius = HasSphereSkill(TEXT("SwordRain")) ? 95.0f : 70.0f;
	TArray<FHitResult> Hits;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(Radius);
	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);

	int32 Strikes = 1;
	float Damage = 40.0f + static_cast<float>(SphereTotals.Attack) * 2.5f;
	if (bSphereSkillJab)
	{
		Damage += 12.0f;
	}
	if (bSphereSkillDoubleKick)
	{
		++Strikes;
	}
	if (bSphereSkillHawkSmash)
	{
		Damage += 18.0f;
		++Strikes;
	}
	if (HasSphereSkill(TEXT("SwordRain")))
	{
		Strikes += 2;
	}
	if (HasSphereSkill(TEXT("SonicThrust")))
	{
		Damage += 12.0f;
		if (GetCharacterMovement() && GetCharacterMovement()->IsMovingOnGround())
		{
			LaunchCharacter(GetActorForwardVector() * 350.0f, true, false);
		}
	}
	float KnockbackForce = 1200.0f;
	if (HasSphereSkill(TEXT("BeastRoar")))
	{
		Damage += 20.0f;
		KnockbackForce = 1750.0f;
	}
	if (HasSphereSkill(TEXT("ElementalBlade")))
	{
		Damage += 10.0f;
		UpdateMagicCircles();
	}
	if ((bIsSliding || bIsFocusMode) && HasSphereSkill(TEXT("AmbushStrike")))
	{
		Damage *= 1.5f;
	}

	for (int32 Strike = 0; Strike < Strikes; ++Strike)
	{
		Hits.Reset();
		if (GetWorld()->SweepMultiByChannel(Hits, Start, End, FQuat::Identity, ECC_Pawn, Sphere, QueryParams))
		{
			for (const FHitResult& Hit : Hits)
			{
				AActor* Target = Hit.GetActor();
				if (Target && Target != this)
				{
					FPointDamageEvent DmgEvent(Damage, Hit, GetActorForwardVector(), nullptr);
					Target->TakeDamage(Damage, DmgEvent, GetController(), this);

					ACharacter* TargetChar = Cast<ACharacter>(Target);
					if (TargetChar)
					{
						FVector KnockbackDir = (Target->GetActorLocation() - GetActorLocation()).GetSafeNormal();
						KnockbackDir.Z = 0.35f;
						TargetChar->LaunchCharacter(KnockbackDir * KnockbackForce, true, true);
					}
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
	if (IsBuildMode())
	{
		OnBuildCornerPullOut();
		return;
	}
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
		FVector AerialForce = DashDir * AerialDashStrength * (bSphereSkillDash ? 1.2f : 1.0f);
		AerialForce.Z = 300.0f;
		LaunchCharacter(AerialForce, true, true);
		bHasAerialDash = false;
	}
	else if (!bIsAirborne)
	{
		FVector DashDir = GetCharacterMovement()->Velocity.GetSafeNormal2D();
		if (DashDir.IsNearlyZero()) DashDir = GetActorForwardVector();

		LaunchCharacter(DashDir * (bSphereSkillDash ? 2100.0f : 1700.0f), true, true);
		ActivateFocusMode();
	}

	DashCooldownRemaining = bSphereSkillDash ? 0.32f : DashCooldown;
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

void AIsekaiVillageCharacter::UpdateMovementSpeed()
{
	if (UCharacterMovementComponent* MoveComp = GetCharacterMovement())
	{
		const float SpeedMult = 1.0f + SphereTotals.MoveSpeedPercent / 100.0f;
		float Speed = (bIsSprinting ? 900.0f : BaseWalkSpeed) * SpeedMult;
		if (bSphereSkillTrailblaze)
		{
			Speed += 90.0f;
		}
		MoveComp->MaxWalkSpeed = Speed;
	}
}

void AIsekaiVillageCharacter::StartSprint()
{
	bIsSprinting = true;
	UpdateMovementSpeed();
}

void AIsekaiVillageCharacter::StopSprint()
{
	bIsSprinting = false;
	UpdateMovementSpeed();
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
	UpdateMovementSpeed();
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

void AIsekaiVillageCharacter::ToggleSparring()
{
 if(HasBlockingModalUI())return;
 if(auto* B=AGolemSparring::FindFor(this)){B->CancelSparring();return;}
 if(auto* T=ATowerExpedition::Find(this); T && T->bInside)return;
 auto* V=TownBuilder(this);
 if(!V || !V->bUseGolemVillage || bSphereGridOpen || V->bBuildingCatalogOpen)return;
 FActorSpawnParameters P;P.Owner=this;
 auto* B=GetWorld()->SpawnActor<AGolemSparring>(GetActorLocation(),FRotator::ZeroRotator,P);
 if(B && !B->BeginSparring(V,this))
 {if(GEngine)GEngine->AddOnScreenDebugMessage(-1,5.f,FColor::Yellow,B->LastError);B->Destroy();}
}
static void SendSparringAction(AIsekaiVillageCharacter* Player,FName Action)
{if(Player && !Player->bSphereGridOpen)if(auto* B=AGolemSparring::FindFor(Player))B->ExecuteAction(Action);}
void AIsekaiVillageCharacter::SparStrike(){SendSparringAction(this,TEXT("Strike"));}
void AIsekaiVillageCharacter::SparDefend(){SendSparringAction(this,TEXT("Defend"));}
void AIsekaiVillageCharacter::SparGuard(){SendSparringAction(this,TEXT("GuardStance"));}
void AIsekaiVillageCharacter::SparBolt(){SendSparringAction(this,TEXT("ArcaneBolt"));}
void AIsekaiVillageCharacter::SparHeal(){SendSparringAction(this,TEXT("FirstAid"));}
void AIsekaiVillageCharacter::SparEvade(){SendSparringAction(this,TEXT("EvasiveStep"));}
void AIsekaiVillageCharacter::SparCycleTarget()
{
	if(!bSphereGridOpen)
	{
		if(auto* B=AGolemSparring::FindFor(this); B && B->Phase!=TEXT("Result"))
		{
			B->CycleEnemyTarget();
			return;
		}
	}
	CancelArte();
}

void AIsekaiVillageCharacter::ToggleAdventureHall()
{
 if(HallWidget && HallWidget->IsInViewport()){HallWidget->CloseHall();return;}
 if(bSphereGridOpen || HasBlockingModalUI())return;
 auto* V=TownBuilder(this);
 if(!V || !V->CanUseAdventureHall(this)) { if(GEngine)GEngine->AddOnScreenDebugMessage(-1,4.f,FColor::Yellow,TEXT("Stand at your adventure hall, then press H."));return; }
 if(V->bBuildingCatalogOpen || AGolemSparring::FindFor(this))return;
 auto* PC=Cast<APlayerController>(GetController());if(!PC)return;
 HallWidget=CreateWidget<UGolemHallWidget>(PC);if(!HallWidget)return;HallWidget->InitializeHall(V,this);HallWidget->AddToViewport(30);
 PC->bShowMouseCursor=true;FInputModeGameAndUI Mode;Mode.SetWidgetToFocus(HallWidget->TakeWidget());Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);PC->SetInputMode(Mode);
}

bool AIsekaiVillageCharacter::HasBlockingModalUI() const
{
	return (HallWidget && HallWidget->IsInViewport())
		|| (ShopWidget && ShopWidget->IsInViewport())
		|| (ForgeWidget && ForgeWidget->IsInViewport())
		|| (ServiceWidget && ServiceWidget->IsInViewport())
		|| (BoardWidget && BoardWidget->IsInViewport());
}

void AIsekaiVillageCharacter::CloseAllModals()
{
	if (HallWidget && HallWidget->IsInViewport()) HallWidget->CloseHall();
	if (ShopWidget && ShopWidget->IsInViewport()) ShopWidget->CloseShop();
	if (ForgeWidget && ForgeWidget->IsInViewport()) ForgeWidget->CloseForge();
	if (ServiceWidget && ServiceWidget->IsInViewport()) ServiceWidget->CloseService();
	if (BoardWidget && BoardWidget->IsInViewport()) BoardWidget->CloseBoard();
}

bool AIsekaiVillageCharacter::OpenShopMenu(FName ShopPlot)
{
	if (ShopWidget && ShopWidget->IsInViewport())
	{
		ShopWidget->CloseShop();
		return true;
	}
	if (bSphereGridOpen || HasBlockingModalUI() || AGolemSparring::FindFor(this)) return false;
	AVillageRuntime* V = TownBuilder(this);
	if (!V || !V->bUseGolemVillage) return false;
	const FName TargetPlot = ShopPlot.IsNone() ? V->NearestBuiltShop(GetActorLocation()) : ShopPlot;
	if (TargetPlot.IsNone()) return false;
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC) return false;
	ShopWidget = CreateWidget<UShopWidget>(PC);
	if (!ShopWidget) return false;
	ShopWidget->InitializeShop(V, this, TargetPlot);
	ShopWidget->AddToViewport(30);
	PC->bShowMouseCursor = true;
	FInputModeGameAndUI Mode;
	Mode.SetWidgetToFocus(ShopWidget->TakeWidget());
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
	return true;
}

bool AIsekaiVillageCharacter::OpenForgeMenu()
{
	if (ForgeWidget && ForgeWidget->IsInViewport())
	{
		ForgeWidget->CloseForge();
		return true;
	}
	if (bSphereGridOpen || HasBlockingModalUI() || AGolemSparring::FindFor(this)) return false;
	ABlacksmithForge* NearestForge = nullptr;
	double BestDist = FMath::Square(600.0);
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<ABlacksmithForge> It(World); It; ++It)
		{
			const double D = FVector::DistSquared2D(GetActorLocation(), It->GetActorLocation());
			if (D <= BestDist)
			{
				BestDist = D;
				NearestForge = *It;
			}
		}
	}
	if (!NearestForge && !bNearBlacksmith) return false;
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC) return false;
	ForgeWidget = CreateWidget<UForgeWidget>(PC);
	if (!ForgeWidget) return false;
	ForgeWidget->InitializeForge(NearestForge, TownBuilder(this), this);
	ForgeWidget->AddToViewport(30);
	PC->bShowMouseCursor = true;
	FInputModeGameAndUI Mode;
	Mode.SetWidgetToFocus(ForgeWidget->TakeWidget());
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
	return true;
}

void AIsekaiVillageCharacter::ToggleStationMenu()
{
	if (ShopWidget && ShopWidget->IsInViewport()) { ShopWidget->CloseShop(); return; }
	if (ForgeWidget && ForgeWidget->IsInViewport()) { ForgeWidget->CloseForge(); return; }
	if (ServiceWidget && ServiceWidget->IsInViewport()) { ServiceWidget->CloseService(); return; }
	if (BoardWidget && BoardWidget->IsInViewport()) { BoardWidget->CloseBoard(); return; }
	if (HallWidget && HallWidget->IsInViewport()) { HallWidget->CloseHall(); return; }
	if (bSphereGridOpen || AGolemSparring::FindFor(this)) return;
	if (ATowerExpedition* Tower = ATowerExpedition::Find(this); Tower && Tower->bInside) return;
	AVillageRuntime* V = TownBuilder(this);
	if (V && V->bBuildingCatalogOpen) return;

	if (OpenForgeMenu()) return;
	if (OpenShopMenu()) return;
	if (OpenServiceMenu()) return;
	if (bNearDayBoard && OpenBoardMenu()) return;
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Yellow,
			TEXT("Stand near a Shop, Blacksmith Forge, service building, or Day Board, then press U."));
	}
}

bool AIsekaiVillageCharacter::OpenServiceMenu(FName PlotId)
{
	if (ServiceWidget && ServiceWidget->IsInViewport())
	{
		ServiceWidget->CloseService();
		return true;
	}
	if (bSphereGridOpen || HasBlockingModalUI() || AGolemSparring::FindFor(this)) return false;
	AVillageRuntime* V = TownBuilder(this);
	if (!V) return false;
	const FName TargetPlotId = PlotId.IsNone() ? V->NearestServicePlot(GetActorLocation()) : PlotId;
	const FTownPlot* Plot = V->FindPlot(TargetPlotId);
	if (!Plot || !Plot->bBuilt || !V->IsServiceBuilding(Plot->Kind)) return false;
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC) return false;
	ServiceWidget = CreateWidget<UTownServiceWidget>(PC);
	if (!ServiceWidget) return false;
	ServiceWidget->InitializeService(V, this, Plot->Kind);
	ServiceWidget->AddToViewport(30);
	PC->bShowMouseCursor = true;
	FInputModeGameAndUI Mode;
	Mode.SetWidgetToFocus(ServiceWidget->TakeWidget());
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
	return true;
}

bool AIsekaiVillageCharacter::OpenBoardMenu()
{
	if (BoardWidget && BoardWidget->IsInViewport())
	{
		BoardWidget->CloseBoard();
		return true;
	}
	if (bSphereGridOpen || HasBlockingModalUI() || AGolemSparring::FindFor(this)) return false;
	AVillageRuntime* V = TownBuilder(this);
	if (!V) return false;
	APlayerController* PC = Cast<APlayerController>(GetController());
	if (!PC) return false;
	BoardWidget = CreateWidget<UDayBoardWidget>(PC);
	if (!BoardWidget) return false;
	BoardWidget->InitializeBoard(V, this);
	BoardWidget->AddToViewport(30);
	PC->bShowMouseCursor = true;
	FInputModeGameAndUI Mode;
	Mode.SetWidgetToFocus(BoardWidget->TakeWidget());
	Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
	PC->SetInputMode(Mode);
	return true;
}

void AIsekaiVillageCharacter::SyncBuildingCatalogWidget(AVillageRuntime* Village)
{
	if (Village && Village->bBuildingCatalogOpen)
	{
		if (APlayerController* PC = Cast<APlayerController>(GetController()))
		{
			if (!CatalogWidget)
			{
				CatalogWidget = CreateWidget<UBuildingCatalogWidget>(PC);
			}
			if (CatalogWidget)
			{
				CatalogWidget->InitializeCatalog(Village, this);
				if (!CatalogWidget->IsInViewport())
				{
					CatalogWidget->AddToViewport(15);
				}
				CatalogWidget->RefreshCatalog();
			}
		}
	}
	else if (CatalogWidget && CatalogWidget->IsInViewport())
	{
		CatalogWidget->CloseCatalog();
	}
}

void AIsekaiVillageCharacter::TowerInteract()
{
 if(bSphereGridOpen || HasBlockingModalUI())return;
 if(auto* T=ATowerExpedition::Find(this))T->Interact(this);
}
void AIsekaiVillageCharacter::TowerReturn()
{
 if(bSphereGridOpen || HasBlockingModalUI())return;
 if(auto* T=ATowerExpedition::Find(this)){if(T->bInside)T->ReturnToVillage(this);else T->CycleStartFloor(this);}
}
void AIsekaiVillageCharacter::TowerRations()
{
 if(bSphereGridOpen || HasBlockingModalUI())return;
 if(auto* T=ATowerExpedition::Find(this))T->ShareRations(this);
}
