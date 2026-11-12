// Copyright Epic Games, Inc. All Rights Reserved.

#include "IslandWarpPortal.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "WorldMapTransition.h"
#include "GameFramework/Character.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"

AIslandWarpPortal::AIslandWarpPortal()
{
	PrimaryActorTick.bCanEverTick = true;

	RootScene = CreateDefaultSubobject<USceneComponent>(TEXT("RootScene"));
	RootComponent = RootScene;

	PortalMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PortalMesh"));
	PortalMesh->SetupAttachment(RootScene);
	PortalMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	
	// Try to find a default plane/circle mesh so it works nicely in editor
	static ConstructorHelpers::FObjectFinder<UStaticMesh> DefaultMesh(TEXT("/Engine/BasicShapes/Cylinder"));
	if (DefaultMesh.Succeeded())
	{
		PortalMesh->SetStaticMesh(DefaultMesh.Object);
		PortalMesh->SetRelativeScale3D(FVector(2.0f, 2.0f, 0.05f));
	}

	TriggerVolume = CreateDefaultSubobject<UBoxComponent>(TEXT("TriggerVolume"));
	TriggerVolume->SetupAttachment(RootScene);
	TriggerVolume->SetBoxExtent(FVector(100.f, 100.f, 50.f));
	TriggerVolume->SetCollisionProfileName(TEXT("Trigger"));
}

void AIslandWarpPortal::BeginPlay()
{
	Super::BeginPlay();

	TriggerVolume->OnComponentBeginOverlap.AddDynamic(this, &AIslandWarpPortal::OnOverlapBegin);
	TriggerVolume->OnComponentEndOverlap.AddDynamic(this, &AIslandWarpPortal::OnOverlapEnd);

	if (PortalMesh->GetMaterial(0))
	{
		PortalMaterial = PortalMesh->CreateAndSetMaterialInstanceDynamic(0);
	}
}

void AIslandWarpPortal::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsCharging)
	{
		CurrentCharge += DeltaTime;
		
		// Have we charged enough to warp?
		if (CurrentCharge >= MaxChargeTime)
		{
			bIsCharging = false;
			CurrentCharge = 0.0f; // Reset just in case they return here

			if (DestinationZone)
			{
				AWorldMapTransition::TransitionToZone(this, DestinationZone);
			}
		}
	}
	else
	{
		// Cool down charge if the player stepped off early
		CurrentCharge = FMath::FInterpTo(CurrentCharge, 0.0f, DeltaTime, 3.0f);
	}

	// Calculate alpha (0.0 to 1.0) based on charge progress
	float ChargeAlpha = FMath::Clamp(CurrentCharge / MaxChargeTime, 0.0f, 1.0f);
	
	// Spin the portal. Speed interpolates as charge goes up.
	float CurrentRotSpeed = FMath::Lerp(BaseRotationSpeed, MaxRotationSpeed, ChargeAlpha);
	PortalMesh->AddLocalRotation(FRotator(0.f, CurrentRotSpeed * DeltaTime, 0.f));

	// Light up the portal material
	if (PortalMaterial)
	{
		// Assuming the material has a scalar parameter called EmissiveMultiplier
		PortalMaterial->SetScalarParameterValue(TEXT("EmissiveMultiplier"), FMath::Lerp(1.0f, 20.0f, ChargeAlpha));
		
		// Let's also set a Color tint parameter if it exists to make it glow brighter
		PortalMaterial->SetVectorParameterValue(TEXT("Color"), FLinearColor::White * FMath::Lerp(1.0f, 3.0f, ChargeAlpha));
	}
}

void AIslandWarpPortal::OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (OtherActor && OtherActor != this && OtherActor->IsA<ACharacter>())
	{
		// Only trigger for the locally controlled player
		if (OtherActor == UGameplayStatics::GetPlayerCharacter(this, 0))
		{
			bIsCharging = true;
		}
	}
}

void AIslandWarpPortal::OnOverlapEnd(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (OtherActor && OtherActor == UGameplayStatics::GetPlayerCharacter(this, 0))
	{
		bIsCharging = false;
	}
}
