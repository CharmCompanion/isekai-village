// Copyright IsekaiVillage. Ground mine / glyph trap.
#include "SpellMine.h"
#include "Kismet/GameplayStatics.h"
#include "NiagaraFunctionLibrary.h"
#include "NiagaraSystem.h"

ASpellMine::ASpellMine()
{
	PrimaryActorTick.bCanEverTick = true;

	TriggerSphere = CreateDefaultSubobject<USphereComponent>(TEXT("TriggerSphere"));
	TriggerSphere->InitSphereRadius(90.0f);
	TriggerSphere->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
	RootComponent = TriggerSphere;
	TriggerSphere->OnComponentBeginOverlap.AddDynamic(this, &ASpellMine::OnTriggerBegin);

	MineMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MineMesh"));
	MineMesh->SetupAttachment(RootComponent);
	MineMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	MineMesh->SetRelativeScale3D(FVector(0.45f, 0.45f, 0.12f));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> Sphere(TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (Sphere.Succeeded())
	{
		MineMesh->SetStaticMesh(Sphere.Object);
	}
}

void ASpellMine::InitMine(EElement InElement, float InChargeRatio, APawn* InInstigator)
{
	MineElement = InElement;
	ChargeRatio = FMath::Clamp(InChargeRatio, 0.0f, 1.0f);
	SetInstigator(InInstigator);
	BlastDamage *= (1.0f + ChargeRatio * 1.2f);
	BlastRadius *= (1.0f + ChargeRatio * 0.5f);
	TriggerSphere->SetSphereRadius(70.0f + ChargeRatio * 50.0f);

	if (UMaterialInterface* BaseMat = Cast<UMaterialInterface>(StaticLoadObject(
		UMaterialInterface::StaticClass(), nullptr,
		TEXT("/Game/IsekaiVillage/Materials/M_SpellEmissive_Master.M_SpellEmissive_Master"))))
	{
		if (UMaterialInstanceDynamic* Dyn = MineMesh->CreateAndSetMaterialInstanceDynamicFromMaterial(0, BaseMat))
		{
			FLinearColor C(1.0f, 0.3f, 0.05f);
			switch (MineElement)
			{
			case EElement::Fire:  C = FLinearColor(1.0f, 0.2f, 0.05f); break;
			case EElement::Earth: C = FLinearColor(0.7f, 0.45f, 0.1f); break;
			case EElement::Water: C = FLinearColor(0.1f, 0.6f, 1.0f); break;
			case EElement::Wind:  C = FLinearColor(0.4f, 1.0f, 0.6f); break;
			}
			Dyn->SetVectorParameterValue(FName("Color"), C * 8.0f);
		}
	}
}

void ASpellMine::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	Age += DeltaTime;
	if (!bArmed && Age >= ArmDelay)
	{
		bArmed = true;
	}
	if (Age >= Lifetime)
	{
		Detonate();
	}
	if (MineMesh)
	{
		MineMesh->AddLocalRotation(FRotator(0.0f, 120.0f * DeltaTime, 0.0f));
	}
}

void ASpellMine::OnTriggerBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (!bArmed || bDetonated || !OtherActor || OtherActor == GetInstigator()) return;
	if (OtherActor->IsA(APawn::StaticClass()) || OtherActor->ActorHasTag(FName("Enemy")))
	{
		Detonate();
	}
}

void ASpellMine::Detonate()
{
	if (bDetonated) return;
	bDetonated = true;

	TArray<AActor*> Ignore;
	Ignore.Add(this);
	if (GetInstigator()) Ignore.Add(GetInstigator());

	UGameplayStatics::ApplyRadialDamage(
		this, BlastDamage, GetActorLocation(), BlastRadius, nullptr,
		Ignore, this, GetInstigator() ? GetInstigator()->GetController() : nullptr, true);

	if (UNiagaraSystem* Burst = Cast<UNiagaraSystem>(StaticLoadObject(
		UNiagaraSystem::StaticClass(), nullptr,
		TEXT("/Game/IsekaiVillage/Niagara/NS_SpellImpact_Burst.NS_SpellImpact_Burst"))))
	{
		UNiagaraFunctionLibrary::SpawnSystemAtLocation(GetWorld(), Burst, GetActorLocation());
	}

	Destroy();
}
