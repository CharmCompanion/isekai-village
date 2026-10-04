// Copyright Epic Games, Inc. All Rights Reserved.

#include "IslandWarpPortal.h"
#include "IsekaiVillageCharacter.h"
#include "ProceduralMagicCircle.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"
#include "Kismet/GameplayStatics.h"

AIslandWarpPortal::AIslandWarpPortal()
{
	PrimaryActorTick.bCanEverTick = true;

	TriggerSphere = CreateDefaultSubobject<USphereComponent>(TEXT("TriggerSphere"));
	TriggerSphere->InitSphereRadius(180.0f);
	TriggerSphere->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	TriggerSphere->SetCollisionResponseToAllChannels(ECR_Ignore);
	TriggerSphere->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	RootComponent = TriggerSphere;

	PortalMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("PortalMesh"));
	PortalMesh->SetupAttachment(RootComponent);
	PortalMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	PortalMesh->SetRelativeScale3D(FVector(3.2f, 3.2f, 0.12f));
}

void AIslandWarpPortal::BeginPlay()
{
	Super::BeginPlay();

	if (!PortalMesh->GetStaticMesh())
	{
		if (UStaticMesh* Cylinder = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
		{
			PortalMesh->SetStaticMesh(Cylinder);
		}
	}

	TriggerSphere->OnComponentBeginOverlap.AddDynamic(this, &AIslandWarpPortal::OnTriggerBeginOverlap);
	TriggerSphere->OnComponentEndOverlap.AddDynamic(this, &AIslandWarpPortal::OnTriggerEndOverlap);

	if (UWorld* World = GetWorld())
	{
		FActorSpawnParameters SpawnParams;
		SpawnParams.Owner = this;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		CircleVisual = World->SpawnActor<AProceduralMagicCircle>(AProceduralMagicCircle::StaticClass(), GetActorTransform(), SpawnParams);
		if (CircleVisual)
		{
			CircleVisual->AttachToActor(this, FAttachmentTransformRules::SnapToTargetNotIncludingScale);
			CircleVisual->SetActorScale3D(FVector(2.4f));
			CircleVisual->SetVisualState(ECircleVisualState::Casting);
		}
	}
}

void AIslandWarpPortal::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bPlayerInside && !bHasWarped)
	{
		ChargeTime = FMath::Min(MaxChargeTime, ChargeTime + DeltaTime);
	}
	else
	{
		ChargeTime = FMath::Max(0.0f, ChargeTime - DeltaTime * 1.5f);
	}

	const float ChargeRatio = (MaxChargeTime > 0.0f) ? (ChargeTime / MaxChargeTime) : 0.0f;
	const float SpinSpeed = FMath::Lerp(IdleRotationSpeed, MaxRotationSpeed, ChargeRatio);
	AddActorWorldRotation(FRotator(0.0f, SpinSpeed * DeltaTime, 0.0f));

	if (CircleVisual)
	{
		CircleVisual->SetChargeProgress(ChargeRatio);
		CircleVisual->EmissivePower = 4.5f + ChargeRatio * 18.0f;
	}

	if (!bHasWarped && bPlayerInside && ChargeTime >= MaxChargeTime && !DestinationLevel.IsNone())
	{
		bHasWarped = true;
		FString Options;
		if (!ArrivalPlayerStartTag.IsNone())
		{
			Options = FString::Printf(TEXT("Warp=%s"), *ArrivalPlayerStartTag.ToString());
		}
		UGameplayStatics::OpenLevel(this, DestinationLevel, true, Options);
	}
}

void AIslandWarpPortal::OnTriggerBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		bPlayerInside = true;
	}
}

void AIslandWarpPortal::OnTriggerEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		bPlayerInside = false;
	}
}
