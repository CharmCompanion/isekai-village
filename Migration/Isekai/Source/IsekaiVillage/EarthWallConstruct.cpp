// Copyright Epic Games, Inc. All Rights Reserved.

#include "EarthWallConstruct.h"
#include "SpellElementVFX.h"
#include "NiagaraComponent.h"
#include "NiagaraSystem.h"

AEarthWallConstruct::AEarthWallConstruct()
{
	PrimaryActorTick.bCanEverTick = true;

	CollisionBox = CreateDefaultSubobject<UBoxComponent>(TEXT("CollisionBox"));
	CollisionBox->SetBoxExtent(FVector(WallThickness * 0.5f, WallWidth * 0.5f, MaxHeight * 0.5f));
	CollisionBox->SetCollisionProfileName(TEXT("BlockAll"));
	RootComponent = CollisionBox;

	WallMeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("WallMeshComp"));
	WallMeshComp->SetupAttachment(RootComponent);
	WallMeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	WallMeshComp->SetRelativeScale3D(FVector(WallThickness / 100.0f, WallWidth / 100.0f, MaxHeight / 100.0f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMeshAss(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeMeshAss.Succeeded())
	{
		WallMeshComp->SetStaticMesh(CubeMeshAss.Object);
	}

	WallVFX = CreateDefaultSubobject<UNiagaraComponent>(TEXT("WallVFX"));
	WallVFX->SetupAttachment(RootComponent);
	WallVFX->SetAutoActivate(false);
}

void AEarthWallConstruct::BeginPlay()
{
	Super::BeginPlay();

	GroundLocation = GetActorLocation();
	TargetLocation = GroundLocation + FVector(0.0f, 0.0f, MaxHeight * 0.5f);
	StartLocation = TargetLocation - FVector(0.0f, 0.0f, MaxHeight);
	SetActorLocation(StartLocation);
	bIsErupting = true;
	EruptAlpha = 0.0f;
}

void AEarthWallConstruct::InitWall(EElement InElement, float ChargeRatio)
{
	WallElement = InElement;
	bSolidWall = FSpellElementVFX::WallUsesSolidMesh(WallElement);

	const float ScaleMult = 1.0f + (ChargeRatio * 0.6f);
	MaxHeight *= ScaleMult;
	WallWidth *= ScaleMult;
	Health *= (1.0f + ChargeRatio * 1.0f);

	if (CollisionBox)
	{
		CollisionBox->SetBoxExtent(FVector(WallThickness * 0.5f, WallWidth * 0.5f, MaxHeight * 0.5f));
	}

	TargetLocation = GroundLocation + FVector(0.0f, 0.0f, MaxHeight * 0.5f);
	StartLocation = TargetLocation - FVector(0.0f, 0.0f, MaxHeight);

	if (WallMeshComp)
	{
		WallMeshComp->SetVisibility(bSolidWall);
		WallMeshComp->SetHiddenInGame(!bSolidWall);
	}

	if (bSolidWall)
	{
		SetActorLocation(StartLocation);
		bIsErupting = true;
		EruptAlpha = 0.0f;

		if (WallMeshComp)
		{
			WallMeshComp->SetRelativeScale3D(FVector(WallThickness / 100.0f, WallWidth / 100.0f, MaxHeight / 100.0f));

			UMaterialInterface* BaseMat = Cast<UMaterialInterface>(StaticLoadObject(UMaterialInterface::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/BasicShapeMaterial.BasicShapeMaterial")));
			if (BaseMat)
			{
				if (UMaterialInstanceDynamic* DynMat = WallMeshComp->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat))
				{
					DynMat->SetVectorParameterValue(FName("Color"), FLinearColor(0.45f, 0.35f, 0.22f, 1.0f));
				}
			}
		}
	}
	else
	{
		SetActorLocation(TargetLocation);
		bIsErupting = false;
		EruptAlpha = 1.0f;

		if (WallVFX)
		{
			if (UNiagaraSystem* Curtain = FSpellElementVFX::LoadWallFX(WallElement))
			{
				WallVFX->SetAsset(Curtain);
				WallVFX->ResetSystem();
				WallVFX->Activate(true);
			}
		}
		RefreshWallVFX(0.0f);
	}
}

void AEarthWallConstruct::RefreshWallVFX(float Progress)
{
	if (!WallVFX || bSolidWall) return;
	FSpellElementVFX::ApplyWallParams(WallVFX, WallElement, WallWidth, MaxHeight, Progress);
}

void AEarthWallConstruct::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	Age += DeltaTime;

	if (bIsErupting)
	{
		EruptAlpha += DeltaTime * 4.5f;
		if (EruptAlpha >= 1.0f)
		{
			EruptAlpha = 1.0f;
			bIsErupting = false;
			SetActorLocation(TargetLocation);
		}
		else
		{
			float EasedAlpha = FMath::InterpEaseOut(0.0f, 1.0f, EruptAlpha, 3.0f);
			SetActorLocation(FMath::Lerp(StartLocation, TargetLocation, EasedAlpha));
		}
	}

	if (Age >= Lifetime)
	{
		const float SinkAlpha = (Age - Lifetime) / 0.8f;
		if (SinkAlpha >= 1.0f)
		{
			Destroy();
			return;
		}

		if (bSolidWall)
		{
			SetActorLocation(FMath::Lerp(TargetLocation, StartLocation, SinkAlpha));
		}
		else
		{
			RefreshWallVFX(1.0f - SinkAlpha);
		}
		return;
	}

	if (!bSolidWall)
	{
		RefreshWallVFX(FMath::Clamp(Age / 0.35f, 0.0f, 1.0f));
	}
}

float AEarthWallConstruct::TakeDamage(float DamageAmount, struct FDamageEvent const& DamageEvent, class AController* EventInstigator, AActor* DamageCauser)
{
	Health -= DamageAmount;
	if (Health <= 0.0f)
	{
		Destroy();
	}
	return DamageAmount;
}
