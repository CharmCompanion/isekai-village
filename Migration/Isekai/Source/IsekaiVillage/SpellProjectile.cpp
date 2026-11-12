// Copyright Epic Games, Inc. All Rights Reserved.

#include "SpellProjectile.h"
#include "SpellElementVFX.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/DamageEvents.h"
#include "Engine/OverlapResult.h"
#include "NiagaraSystem.h"
#include "NiagaraFunctionLibrary.h"
#include "Components/PointLightComponent.h"

ASpellProjectile::ASpellProjectile()
{
	PrimaryActorTick.bCanEverTick = true;

	CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("SphereComp"));
	CollisionComp->InitSphereRadius(25.0f);
	CollisionComp->SetCollisionProfileName(TEXT("Projectile"));
	CollisionComp->OnComponentHit.AddDynamic(this, &ASpellProjectile::OnProjectileHit);
	RootComponent = CollisionComp;

	ProjectileVFX = CreateDefaultSubobject<UNiagaraComponent>(TEXT("ProjectileVFX"));
	ProjectileVFX->SetupAttachment(RootComponent);
	ProjectileVFX->SetAutoActivate(false);

	AuraVFX = CreateDefaultSubobject<UNiagaraComponent>(TEXT("AuraVFX"));
	AuraVFX->SetupAttachment(RootComponent);
	AuraVFX->SetAutoActivate(false);

	CoreMeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CoreMeshComp"));
	CoreMeshComp->SetupAttachment(RootComponent);
	CoreMeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	CoreMeshComp->SetCastShadow(false);
	CoreMeshComp->SetRelativeScale3D(FVector(0.35f));

	AuraLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("AuraLight"));
	AuraLight->SetupAttachment(RootComponent);
	AuraLight->SetIntensity(0.0f);
	AuraLight->SetAttenuationRadius(400.0f);
	AuraLight->SetCastShadows(false);
	AuraLight->bUseTemperature = false;

	MovementComp = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("ProjectileMovement"));
	MovementComp->UpdatedComponent = CollisionComp;
	MovementComp->InitialSpeed = BaseSpeed;
	MovementComp->MaxSpeed = BaseSpeed * 2.0f;
	MovementComp->bRotationFollowsVelocity = true;
	MovementComp->bShouldBounce = false;
	MovementComp->ProjectileGravityScale = 0.0f;

	InitialLifeSpan = Lifetime;
}

FLinearColor ASpellProjectile::GetElementColor(EElement Element)
{
	return FSpellElementVFX::GetElementColor(Element);
}

UNiagaraSystem* ASpellProjectile::LoadElementTrailFX(EElement Element)
{
	return FSpellElementVFX::LoadBodyFX(Element, FName("spear"));
}

UNiagaraSystem* ASpellProjectile::LoadElementAuraFX(EElement Element)
{
	return FSpellElementVFX::LoadAuraFX(Element);
}

UNiagaraSystem* ASpellProjectile::LoadElementImpactFX(EElement Element)
{
	if (UNiagaraSystem* FX = FSpellElementVFX::LoadImpactFX(Element))
	{
		return FX;
	}
	static UNiagaraSystem* FallbackImpact = Cast<UNiagaraSystem>(StaticLoadObject(UNiagaraSystem::StaticClass(), nullptr,
		TEXT("/Game/IsekaiVillage/Niagara/NS_SpellImpact_Burst.NS_SpellImpact_Burst")));
	return FallbackImpact;
}

void ASpellProjectile::BeginPlay()
{
	Super::BeginPlay();

	if (CoreMeshComp && !CoreMeshComp->GetStaticMesh())
	{
		static UStaticMesh* CachedSphereMesh = Cast<UStaticMesh>(StaticLoadObject(UStaticMesh::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")));
		if (CachedSphereMesh)
		{
			CoreMeshComp->SetStaticMesh(CachedSphereMesh);
		}
	}

	ApplyElementalPhysics();
	ApplyElementalPresentation();
}

void ASpellProjectile::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	Age += DeltaTime;
	UpdateElementalLight(DeltaTime);
	SpawnElementEmberTrail(DeltaTime);

	if (CoreMeshComp)
	{
		const EElement Elem = ProjectileElement;
		const FName Shape = ProjectileShape;

		if (Elem == EElement::Earth || (Shape == FName("spear") && Elem == EElement::Water))
		{
			CoreMeshComp->AddWorldRotation(FQuat(GetActorForwardVector(), FMath::DegreesToRadians(1800.0f * DeltaTime)).Rotator());
		}
		else if (Elem == EElement::Wind || Shape == FName("wave"))
		{
			CoreMeshComp->AddLocalRotation(FRotator(0.0f, 2400.0f * DeltaTime, 0.0f));
		}
		else if (Elem == EElement::Fire)
		{
			if (DynamicProjectileMaterial)
			{
				const float Pulse = 0.85f + 0.25f * FMath::Sin(Age * 18.0f);
				DynamicProjectileMaterial->SetVectorParameterValue(FName("Color"), CachedElementColor * (16.0f * Pulse));
			}
			CoreMeshComp->AddLocalRotation(FRotator(140.0f * DeltaTime, 200.0f * DeltaTime, 0.0f));
		}
		else
		{
			CoreMeshComp->AddLocalRotation(FRotator(60.0f * DeltaTime, 90.0f * DeltaTime, 0.0f));
		}
	}

	if (ProjectileShape == FName("homing"))
	{
		TrackHomingTarget(DeltaTime);
	}
}

void ASpellProjectile::UpdateElementalLight(float DeltaTime)
{
	if (!AuraLight) return;

	float BaseIntensity = 2500.0f;
	float Radius = 450.0f;
	float Flicker = 1.0f;

	switch (ProjectileElement)
	{
	case EElement::Fire:
		BaseIntensity = 6000.0f;
		Radius = 700.0f;
		Flicker = 0.75f + 0.45f * FMath::Abs(FMath::Sin(Age * 22.0f)) + 0.15f * FMath::FRand();
		break;
	case EElement::Water:
		BaseIntensity = 2800.0f;
		Radius = 500.0f;
		Flicker = 0.85f + 0.15f * FMath::Sin(Age * 8.0f);
		break;
	case EElement::Wind:
		BaseIntensity = 1800.0f;
		Radius = 400.0f;
		break;
	case EElement::Earth:
		BaseIntensity = 5500.0f;
		Radius = 650.0f;
		break;
	default:
		break;
	}

	AuraLight->SetIntensity(BaseIntensity * Flicker * (0.7f + ChargeRatio * 0.6f));
	AuraLight->SetAttenuationRadius(Radius * (0.8f + ChargeRatio * 0.4f));
	AuraLight->SetLightColor(CachedElementColor);
}

void ASpellProjectile::SpawnElementEmberTrail(float DeltaTime)
{
	return;
}

void ASpellProjectile::InitProjectile(EElement InElement, FName InShape, float InChargeRatio)
{
	ProjectileElement = InElement;
	ProjectileShape = InShape;
	ChargeRatio = FMath::Clamp(InChargeRatio, 0.0f, 1.0f);
	CachedElementColor = GetElementColor(ProjectileElement);

	if (ProjectileShape == FName("pierce"))
	{
		PierceCount += 2;
	}

	ApplyElementalPhysics();
	ApplyElementalPresentation();

	if (GetInstigator())
	{
		const FVector CasterVelocity = GetInstigator()->GetVelocity();
		MovementComp->Velocity = (GetActorForwardVector() * MovementComp->InitialSpeed) + (CasterVelocity * 0.5f);
	}
}

void ASpellProjectile::ForceProjectileSilhouette(UStaticMesh* ConeMesh, UStaticMesh* CylMesh, UStaticMesh* SphereMesh, float Scale)
{
	(void)ConeMesh;
	(void)CylMesh;
	(void)SphereMesh;
	(void)Scale;

	if (CoreMeshComp)
	{
		CoreMeshComp->SetVisibility(false);
		CoreMeshComp->SetHiddenInGame(true);
		CoreMeshComp->SetStaticMesh(nullptr);
	}
}

void ASpellProjectile::ApplyElementalPresentation()
{
	CachedElementColor = GetElementColor(ProjectileElement);

	const EElement Elem = ProjectileElement;
	const FName Shape = ProjectileShape;

	ForceProjectileSilhouette(nullptr, nullptr, nullptr, 1.0f);

	UNiagaraSystem* BodyFX = FSpellElementVFX::LoadBodyFX(Elem, Shape);
	const FVector BodyScale = FSpellElementVFX::GetBodyScale(Elem, Shape, ChargeRatio);

	if (ProjectileVFX && BodyFX)
	{
		ProjectileVFX->SetAsset(BodyFX);
		ProjectileVFX->SetRelativeScale3D(BodyScale);
		ProjectileVFX->SetRelativeRotation(FRotator::ZeroRotator);
		ProjectileVFX->ResetSystem();
		ProjectileVFX->Activate(true);

		FSpellElementVFX::ApplyBodyParams(ProjectileVFX, Elem, Shape, ChargeRatio);
		ProjectileVFX->SetVariableLinearColor(FName("User.Color"), CachedElementColor);
		ProjectileVFX->SetVariableInt(FName("User.Shape"),
			Shape == FName("homing") ? 0 : Shape == FName("spear") ? 1 : Shape == FName("wave") ? 2 : 0);
	}

	UNiagaraSystem* AuraFX = FSpellElementVFX::LoadAuraFX(Elem);
	if (AuraFX && AuraVFX)
	{
		AuraVFX->SetAsset(AuraFX);
		AuraVFX->SetRelativeScale3D(FVector(1.4f + ChargeRatio * 0.5f));
		AuraVFX->ResetSystem();
		AuraVFX->Activate(true);
		AuraVFX->SetVariableLinearColor(FName("User.Color"), CachedElementColor);
	}

	if (AuraLight)
	{
		AuraLight->SetVisibility(true);
		AuraLight->SetLightColor(CachedElementColor);
		float LightBoost = 12000.0f;
		if (Elem == EElement::Fire) LightBoost = 16000.0f;
		else if (Elem == EElement::Earth) LightBoost = 9000.0f;
		AuraLight->SetIntensity(LightBoost * (0.7f + ChargeRatio * 0.6f));
		AuraLight->SetAttenuationRadius((Elem == EElement::Earth) ? 700.0f : 1000.0f);
		UpdateElementalLight(0.0f);
	}
}

void ASpellProjectile::BindSpellVFX(UNiagaraSystem* System)
{
	UNiagaraSystem* Trail = FSpellElementVFX::LoadBodyFX(ProjectileElement, ProjectileShape);
	if (!Trail && System) Trail = System;
	if (!Trail)
	{
		static UNiagaraSystem* CachedFallbackTrail = Cast<UNiagaraSystem>(StaticLoadObject(UNiagaraSystem::StaticClass(), nullptr,
			TEXT("/Game/IsekaiVillage/Niagara/NS_SpellProjectile_Trail.NS_SpellProjectile_Trail")));
		Trail = CachedFallbackTrail;
	}

	if (ProjectileVFX && Trail)
	{
		ProjectileVFX->SetAsset(Trail);
		ProjectileVFX->Activate(true);
	}

	CachedElementColor = GetElementColor(ProjectileElement);
	if (ProjectileVFX)
	{
		ProjectileVFX->SetVariableLinearColor(FName("User.Color"), CachedElementColor);
		ProjectileVFX->SetVariableFloat(FName("User.Scale"), 1.0f + ChargeRatio * 0.5f);
		ProjectileVFX->SetVariableFloat(FName("User.Charge"), ChargeRatio);
		ProjectileVFX->SetVariableInt(FName("User.ElementType"), static_cast<int32>(ProjectileElement));
	}

	ApplyElementalPresentation();
}

void ASpellProjectile::ApplyElementalPhysics()
{
	FLinearColor Color = GetElementColor(ProjectileElement);
	CachedElementColor = Color;

	if (CoreMeshComp)
	{
		static UStaticMesh* SphereMesh = Cast<UStaticMesh>(StaticLoadObject(UStaticMesh::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/Sphere.Sphere")));
		static UStaticMesh* ConeMesh = Cast<UStaticMesh>(StaticLoadObject(UStaticMesh::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/Cone.Cone")));
		static UStaticMesh* CylMesh = Cast<UStaticMesh>(StaticLoadObject(UStaticMesh::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")));

		const float Scale = 1.0f + ChargeRatio * 0.6f;
		const FName Shape = ProjectileShape;

		MovementComp->ProjectileGravityScale = 0.0f;
		MovementComp->InitialSpeed = 2800.0f * Scale;
		MovementComp->MaxSpeed = 4200.0f;
		CollisionComp->SetSphereRadius(22.0f);

		if (Shape == FName("spear"))
		{
			if (ConeMesh) CoreMeshComp->SetStaticMesh(ConeMesh);
			CoreMeshComp->SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));
			CoreMeshComp->SetRelativeScale3D(FVector(0.28f, 0.28f, 3.60f) * Scale);
			CollisionComp->SetSphereRadius(18.0f);
			MovementComp->InitialSpeed = 3400.0f * Scale;
			MovementComp->MaxSpeed = 5200.0f;
		}
		else if (Shape == FName("wave"))
		{
			if (CylMesh) CoreMeshComp->SetStaticMesh(CylMesh);
			CoreMeshComp->SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));
			CoreMeshComp->SetRelativeScale3D(FVector(2.20f, 2.20f, 0.10f) * Scale);
			CollisionComp->SetSphereRadius(56.0f);
			MovementComp->InitialSpeed = 2400.0f * Scale;
			MovementComp->MaxSpeed = 3600.0f;
		}
		else
		{
			if (SphereMesh) CoreMeshComp->SetStaticMesh(SphereMesh);
			CoreMeshComp->SetRelativeRotation(FRotator::ZeroRotator);
			CoreMeshComp->SetRelativeScale3D(FVector(0.55f) * Scale);
			CollisionComp->SetSphereRadius(28.0f);
		}

		switch (ProjectileElement)
		{
		case EElement::Earth:
			MovementComp->ProjectileGravityScale = 2.0f;
			MovementComp->InitialSpeed = 2800.0f * Scale;
			MovementComp->MaxSpeed = 4200.0f;
			if (Shape == FName("spear") && ConeMesh)
			{
				CoreMeshComp->SetStaticMesh(ConeMesh);
				CoreMeshComp->SetRelativeScale3D(FVector(0.40f, 0.40f, 1.70f) * Scale);
			}
			break;

		case EElement::Fire:
			MovementComp->ProjectileGravityScale = 0.8f;
			MovementComp->InitialSpeed = 2200.0f * Scale;
			MovementComp->MaxSpeed = 3200.0f;
			if (Shape == FName("spear") && ConeMesh)
			{
				CoreMeshComp->SetStaticMesh(ConeMesh);
				CoreMeshComp->SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));
				CoreMeshComp->SetRelativeScale3D(FVector(0.32f, 0.32f, 3.40f) * Scale);
			}
			break;

		case EElement::Water:
			MovementComp->ProjectileGravityScale = 0.2f;
			MovementComp->InitialSpeed = 3600.0f * Scale;
			MovementComp->MaxSpeed = 5000.0f;
			if (Shape == FName("spear") && ConeMesh)
			{
				CoreMeshComp->SetStaticMesh(ConeMesh);
				CoreMeshComp->SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));
				CoreMeshComp->SetRelativeScale3D(FVector(0.20f, 0.20f, 4.20f) * Scale);
				CollisionComp->SetSphereRadius(14.0f);
			}
			break;

		case EElement::Wind:
			MovementComp->InitialSpeed = 2600.0f * Scale;
			MovementComp->MaxSpeed = 3800.0f;
			if (CylMesh)
			{
				CoreMeshComp->SetStaticMesh(CylMesh);
				CoreMeshComp->SetRelativeRotation(FRotator(90.0f, 0.0f, 0.0f));
				CoreMeshComp->SetRelativeScale3D(FVector(1.60f, 1.60f, 0.06f) * Scale);
			}
			break;

		default:
			break;
		}

		MovementComp->Velocity = GetActorForwardVector() * MovementComp->InitialSpeed;

		const float SpeedScale = 0.42f;
		MovementComp->InitialSpeed *= SpeedScale;
		MovementComp->MaxSpeed *= SpeedScale;
		MovementComp->Velocity = GetActorForwardVector() * MovementComp->InitialSpeed;

		ForceProjectileSilhouette(ConeMesh, CylMesh, SphereMesh, Scale);

		if (!DynamicProjectileMaterial)
		{
			static UMaterialInterface* BaseMat = Cast<UMaterialInterface>(StaticLoadObject(
				UMaterialInterface::StaticClass(), nullptr,
				TEXT("/Game/IsekaiVillage/Materials/M_SpellEmissive_Master.M_SpellEmissive_Master")));
			if (BaseMat)
			{
				DynamicProjectileMaterial = CoreMeshComp->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat);
			}
		}
		if (DynamicProjectileMaterial)
		{
			float EmissiveStrength = 10.0f;
			switch (ProjectileElement)
			{
			case EElement::Earth: EmissiveStrength = 2.0f; break;
			case EElement::Fire:  EmissiveStrength = 16.0f; break;
			case EElement::Water: EmissiveStrength = 11.0f; break;
			case EElement::Wind:  EmissiveStrength = 9.0f; break;
			default: break;
			}
			FLinearColor MatColor = (ProjectileElement == EElement::Earth)
				? FLinearColor(0.38f, 0.28f, 0.14f, 1.0f)
				: (Color * EmissiveStrength);
			DynamicProjectileMaterial->SetVectorParameterValue(FName("Color"), MatColor);
		}
	}

	if (ProjectileVFX)
	{
		ProjectileVFX->SetVariableLinearColor(FName("User.Color"), Color);
		ProjectileVFX->SetVariableFloat(FName("User.Scale"), 1.0f + ChargeRatio * 0.5f);
		ProjectileVFX->SetVariableInt(FName("User.ElementType"), static_cast<int32>(ProjectileElement));
	}
}

void ASpellProjectile::OnProjectileHit(UPrimitiveComponent* HitComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
	if (OtherActor && OtherActor != this && OtherActor != GetInstigator())
	{
		const float DamageToApply = BaseDamage * (1.0f + ChargeRatio * 0.8f);
		FPointDamageEvent DmgEvent(DamageToApply, Hit, GetActorForwardVector(), nullptr);
		OtherActor->TakeDamage(DamageToApply, DmgEvent, GetInstigatorController(), this);

		if (PierceCount > 0)
		{
			PierceCount--;
			return;
		}
	}

	if (BouncesLeft > 0)
	{
		BouncesLeft--;
		return;
	}

	HandleImpact(Hit);
}

void ASpellProjectile::HandleImpact(const FHitResult& Hit)
{
	if (bHasImpacted) return;
	bHasImpacted = true;

	SpawnImpactFX(Hit.ImpactPoint, Hit.ImpactNormal);

	if (UNiagaraSystem* ImpactSys = LoadElementImpactFX(ProjectileElement))
	{
		if (UNiagaraComponent* Burst = UNiagaraFunctionLibrary::SpawnSystemAtLocation(
			GetWorld(), ImpactSys, Hit.ImpactPoint, Hit.ImpactNormal.Rotation()))
		{
			Burst->SetVariableLinearColor(FName("User.Color"), CachedElementColor);
			Burst->SetVariableInt(FName("User.ElementType"), static_cast<int32>(ProjectileElement));
			Burst->SetWorldScale3D(FVector(0.8f + ChargeRatio * 0.6f));
		}
	}

	if (UWorld* World = GetWorld())
	{
		if (AActor* Flash = World->SpawnActor<AActor>(AActor::StaticClass(), Hit.ImpactPoint, FRotator::ZeroRotator))
		{
			UPointLightComponent* FlashLight = NewObject<UPointLightComponent>(Flash);
			FlashLight->RegisterComponent();
			Flash->SetRootComponent(FlashLight);
			FlashLight->SetWorldLocation(Hit.ImpactPoint);
			FlashLight->SetLightColor(CachedElementColor);
			FlashLight->SetIntensity(8000.0f);
			FlashLight->SetAttenuationRadius(900.0f);
			FlashLight->SetCastShadows(false);
			Flash->SetLifeSpan(0.18f);
		}
	}

	if (ProjectileElement == EElement::Fire || ProjectileShape == FName("wave"))
	{
		TArray<AActor*> IgnoredActors;
		IgnoredActors.Add(this);
		if (GetInstigator()) IgnoredActors.Add(GetInstigator());

		const float Radius = ProjectileShape == FName("wave") ? 420.0f : 280.0f;
		UGameplayStatics::ApplyRadialDamage(
			this,
			BaseDamage * (1.1f + ChargeRatio * 0.5f),
			Hit.ImpactPoint,
			Radius,
			nullptr,
			IgnoredActors,
			this,
			GetInstigatorController(),
			true
		);
	}

	Destroy();
}

void ASpellProjectile::TrackHomingTarget(float DeltaTime)
{
	FVector Forward = GetActorForwardVector();
	FVector CurrentLoc = GetActorLocation();

	TArray<FOverlapResult> Overlaps;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(1200.0f);
	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);
	if (GetInstigator()) QueryParams.AddIgnoredActor(GetInstigator());

	if (GetWorld()->OverlapMultiByChannel(Overlaps, CurrentLoc, FQuat::Identity, ECC_Pawn, Sphere, QueryParams))
	{
		AActor* BestTarget = nullptr;
		float BestDot = 0.3f;

		for (const FOverlapResult& Overlap : Overlaps)
		{
			AActor* Target = Overlap.GetActor();
			if (!Target) continue;

			FVector DirToTarget = (Target->GetActorLocation() - CurrentLoc).GetSafeNormal();
			float Dot = FVector::DotProduct(Forward, DirToTarget);
			if (Dot > BestDot)
			{
				BestDot = Dot;
				BestTarget = Target;
			}
		}

		if (BestTarget)
		{
			FVector TargetDir = (BestTarget->GetActorLocation() - CurrentLoc).GetSafeNormal();
			FVector NewDir = FMath::VInterpTo(Forward, TargetDir, DeltaTime, 5.0f).GetSafeNormal();
			MovementComp->Velocity = NewDir * MovementComp->Velocity.Size();
			SetActorRotation(NewDir.Rotation());
		}
	}
}

void ASpellProjectile::PullNearbyTargets(float DeltaTime)
{
	FVector CurrentLoc = GetActorLocation();
	TArray<FOverlapResult> Overlaps;
	FCollisionShape Sphere = FCollisionShape::MakeSphere(600.0f);
	FCollisionQueryParams QueryParams;
	QueryParams.AddIgnoredActor(this);

	if (GetWorld()->OverlapMultiByChannel(Overlaps, CurrentLoc, FQuat::Identity, ECC_Pawn, Sphere, QueryParams))
	{
		for (const FOverlapResult& Overlap : Overlaps)
		{
			AActor* Target = Overlap.GetActor();
			if (!Target || Target == GetInstigator()) continue;

			FVector PullDir = (CurrentLoc - Target->GetActorLocation()).GetSafeNormal();
			Target->AddActorWorldOffset(PullDir * (400.0f * DeltaTime), true);
		}
	}
}
