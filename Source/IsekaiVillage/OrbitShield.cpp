// Copyright IsekaiVillage. Orbiting defensive shield.
#include "OrbitShield.h"
#include "SpellProjectile.h"

AOrbitShield::AOrbitShield()
{
	PrimaryActorTick.bCanEverTick = true;

	ShieldSphere = CreateDefaultSubobject<USphereComponent>(TEXT("ShieldSphere"));
	ShieldSphere->InitSphereRadius(BlockRadius);
	ShieldSphere->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	RootComponent = ShieldSphere;
	ShieldSphere->OnComponentBeginOverlap.AddDynamic(this, &AOrbitShield::OnShieldOverlap);

	ShieldMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("ShieldMesh"));
	ShieldMesh->SetupAttachment(RootComponent);
	ShieldMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	ShieldMesh->SetRelativeScale3D(FVector(0.55f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Sphere.Sphere"));
	if (Sphere.Succeeded())
	{
		ShieldMesh->SetStaticMesh(Sphere.Object);
	}
}

void AOrbitShield::InitShield(EElement InElement, float InChargeRatio, AActor* InOwner)
{
	ShieldElement = InElement;
	ChargeRatio = FMath::Clamp(InChargeRatio, 0.0f, 1.0f);
	OwnerActor = InOwner;
	Lifetime = 5.0f + ChargeRatio * 5.0f;
	OrbitRadius = 100.0f + ChargeRatio * 60.0f;
	BlockRadius = 55.0f + ChargeRatio * 40.0f;
	ShieldSphere->SetSphereRadius(BlockRadius);

	if (UMaterialInterface* BaseMat = Cast<UMaterialInterface>(StaticLoadObject(
		UMaterialInterface::StaticClass(), nullptr,
		TEXT("/Game/IsekaiVillage/Materials/M_SpellEmissive_Master.M_SpellEmissive_Master"))))
	{
		if (UMaterialInstanceDynamic* Dyn = ShieldMesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat))
		{
			FLinearColor C(0.3f, 0.8f, 1.0f);
			switch (ShieldElement)
			{
			case EElement::Fire:  C = FLinearColor(1.0f, 0.35f, 0.1f); break;
			case EElement::Earth: C = FLinearColor(0.75f, 0.55f, 0.2f); break;
			case EElement::Water: C = FLinearColor(0.15f, 0.7f, 1.0f); break;
			case EElement::Wind:  C = FLinearColor(0.5f, 1.0f, 0.7f); break;
			}
			Dyn->SetVectorParameterValue(FName("Color"), C * 12.0f);
		}
	}
}

void AOrbitShield::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	Age += DeltaTime;
	if (Age >= Lifetime)
	{
		Destroy();
		return;
	}

	AActor* Own = OwnerActor.Get();
	if (!Own)
	{
		Destroy();
		return;
	}

	AngleDeg += OrbitSpeedDeg * DeltaTime;
	const float Rad = FMath::DegreesToRadians(AngleDeg);
	const FVector Center = Own->GetActorLocation() + FVector(0, 0, 40.0f);
	const FVector Pos = Center + FVector(FMath::Cos(Rad) * OrbitRadius, FMath::Sin(Rad) * OrbitRadius, 20.0f * FMath::Sin(Rad * 2.0f));
	SetActorLocation(Pos);
}

void AOrbitShield::OnShieldOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (!OtherActor || OtherActor == OwnerActor.Get()) return;

	if (ASpellProjectile* Proj = Cast<ASpellProjectile>(OtherActor))
	{
		if (Proj->GetInstigator() == OwnerActor.Get()) return;
		FHitResult Hit;
		Hit.ImpactPoint = Proj->GetActorLocation();
		Hit.ImpactNormal = FVector::UpVector;
		Proj->HandleImpact(Hit);
	}
}
