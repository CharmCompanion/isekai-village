// Copyright Epic Games, Inc. All Rights Reserved.
// SorcerersRingProjectile.cpp — Tales of-style Sorcerer's Ring energy beam for field stun & puzzle interaction

#include "SorcerersRingProjectile.h"
#include "OverworldMonsterAvatar.h"
#include "DungeonPuzzleGateActor.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/PointLightComponent.h"
#include "GameFramework/ProjectileMovementComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"

ASorcerersRingProjectile::ASorcerersRingProjectile()
{
	PrimaryActorTick.bCanEverTick = false;
	InitialLifeSpan = 3.5f;

	CollisionComp = CreateDefaultSubobject<USphereComponent>(TEXT("CollisionComp"));
	CollisionComp->InitSphereRadius(24.0f);
	CollisionComp->SetCollisionProfileName(TEXT("BlockAllDynamic"));
	CollisionComp->SetGenerateOverlapEvents(true);
	RootComponent = CollisionComp;

	CollisionComp->OnComponentBeginOverlap.AddDynamic(this, &ASorcerersRingProjectile::OnOverlap);
	CollisionComp->OnComponentHit.AddDynamic(this, &ASorcerersRingProjectile::OnHit);

	OrbMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("OrbMesh"));
	OrbMesh->SetupAttachment(CollisionComp);
	OrbMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	OrbMesh->SetRelativeScale3D(FVector(0.35f, 0.35f, 0.35f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> SphereMeshAsset(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (SphereMeshAsset.Succeeded())
	{
		OrbMesh->SetStaticMesh(SphereMeshAsset.Object);
	}

	RingLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("RingLight"));
	RingLight->SetupAttachment(CollisionComp);
	RingLight->SetLightColor(FLinearColor(1.0f, 0.6f, 0.1f)); // Warm amber/orange Sorcerer's Ring glow
	RingLight->Intensity = 4500.0f;
	RingLight->AttenuationRadius = 400.0f;

	MovementComp = CreateDefaultSubobject<UProjectileMovementComponent>(TEXT("MovementComp"));
	MovementComp->UpdatedComponent = CollisionComp;
	MovementComp->InitialSpeed = ProjectileSpeed;
	MovementComp->MaxSpeed = ProjectileSpeed;
	MovementComp->bRotationFollowsVelocity = true;
	MovementComp->bShouldBounce = false;
	MovementComp->ProjectileGravityScale = 0.0f; // Travels laser-straight in field
}

void ASorcerersRingProjectile::BeginPlay()
{
	Super::BeginPlay();

	// Dynamic emissive glow material for the projectile sphere
	if (OrbMesh)
	{
		if (UMaterialInterface* BaseMat = OrbMesh->GetMaterial(0))
		{
			UMaterialInstanceDynamic* DynMat = UMaterialInstanceDynamic::Create(BaseMat, this);
			if (DynMat)
			{
				DynMat->SetVectorParameterValue(TEXT("Color"), FLinearColor(2.5f, 1.2f, 0.2f, 1.0f));
				DynMat->SetScalarParameterValue(TEXT("Emissive"), 8.0f);
				OrbMesh->SetMaterial(0, DynMat);
			}
		}
	}
}

void ASorcerersRingProjectile::OnOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (!OtherActor || OtherActor == this || OtherActor == GetInstigator()) return;

	if (AOverworldMonsterAvatar* Monster = Cast<AOverworldMonsterAvatar>(OtherActor))
	{
		Monster->StunMonster(StunDuration);
		Destroy();
		return;
	}

	if (ADungeonPuzzleGateActor* Gate = Cast<ADungeonPuzzleGateActor>(OtherActor))
	{
		Gate->TryUnlockWithElement(Gate->RequiredElement);
		Destroy();
		return;
	}
}

void ASorcerersRingProjectile::OnHit(UPrimitiveComponent* HitComponent, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, FVector NormalImpulse, const FHitResult& Hit)
{
	if (!OtherActor || OtherActor == this || OtherActor == GetInstigator()) return;

	if (AOverworldMonsterAvatar* Monster = Cast<AOverworldMonsterAvatar>(OtherActor))
	{
		Monster->StunMonster(StunDuration);
	}
	else if (ADungeonPuzzleGateActor* Gate = Cast<ADungeonPuzzleGateActor>(OtherActor))
	{
		Gate->TryUnlockWithElement(Gate->RequiredElement);
	}

	Destroy();
}
