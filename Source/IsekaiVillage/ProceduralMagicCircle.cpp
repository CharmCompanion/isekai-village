// Copyright Epic Games, Inc. All Rights Reserved.

#include "ProceduralMagicCircle.h"
#include "SpellVisualDataAsset.h"
#include "MagicCircleGeometry.h"
#include "NiagaraSystem.h"
#include "ProceduralMeshComponent.h"

AProceduralMagicCircle::AProceduralMagicCircle()
{
	PrimaryActorTick.bCanEverTick = true;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	CircleMeshComp = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CircleMeshComp"));
	CircleMeshComp->SetupAttachment(RootComponent);
	CircleMeshComp->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	CircleMeshComp->SetCastShadow(false);
	CircleMeshComp->SetRelativeRotation(FRotator::ZeroRotator);
	CircleMeshComp->SetRelativeScale3D(FVector(2.0f, 2.0f, 1.0f));

	GeneratedCircleMesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("GeneratedCircleMesh"));
	GeneratedCircleMesh->SetupAttachment(RootComponent);
	GeneratedCircleMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	GeneratedCircleMesh->SetCastShadow(false);

	CircleVFX = CreateDefaultSubobject<UNiagaraComponent>(TEXT("CircleVFX"));
	CircleVFX->SetupAttachment(RootComponent);
	CircleVFX->SetAutoActivate(false);

	EmissivePower = 4.5f;
}

void AProceduralMagicCircle::LoadDefaultAssets()
{
	if (!CircleMeshComp->GetStaticMesh())
	{
		UStaticMesh* PlaneMesh = Cast<UStaticMesh>(StaticLoadObject(UStaticMesh::StaticClass(), nullptr, TEXT("/Engine/BasicShapes/Plane.Plane")));
		if (PlaneMesh) CircleMeshComp->SetStaticMesh(PlaneMesh);
	}

	if (!MasterCircleMaterial)
	{
		MasterCircleMaterial = Cast<UMaterialInterface>(StaticLoadObject(UMaterialInterface::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Materials/M_MagicCircle_Master.M_MagicCircle_Master")));
	}

	auto LoadTex = [](const TCHAR* Path) -> UTexture2D* {
		return Cast<UTexture2D>(StaticLoadObject(UTexture2D::StaticClass(), nullptr, Path));
	};

	if (!MasterCircleTexture) MasterCircleTexture = LoadTex(TEXT("/Game/IsekaiVillage/Textures/T_MagicCircle_Master.T_MagicCircle_Master"));
	if (!FireCircleTexture)   FireCircleTexture   = LoadTex(TEXT("/Game/IsekaiVillage/Textures/T_MagicCircle_Fire.T_MagicCircle_Fire"));
	if (!EarthCircleTexture)  EarthCircleTexture  = LoadTex(TEXT("/Game/IsekaiVillage/Textures/T_MagicCircle_Earth.T_MagicCircle_Earth"));
	if (!WindCircleTexture)   WindCircleTexture   = LoadTex(TEXT("/Game/IsekaiVillage/Textures/T_MagicCircle_Wind.T_MagicCircle_Wind"));
	if (!WaterCircleTexture)  WaterCircleTexture  = LoadTex(TEXT("/Game/IsekaiVillage/Textures/T_MagicCircle_Water.T_MagicCircle_Water"));
}

void AProceduralMagicCircle::BeginPlay()
{
	Super::BeginPlay();

	LoadDefaultAssets();

	VisualState = ECircleVisualState::Stowed;
	VisualScale = 0.0f;
	TargetVisualScale = 0.0f;

	if (CircleMeshComp)
	{
		if (MasterCircleMaterial)
		{
			DynamicCircleMaterial = CircleMeshComp->CreateAndSetMaterialInstanceDynamicFromMaterial(0, MasterCircleMaterial);
		}
		CircleMeshComp->SetVisibility(false);
	}

	if (GeneratedCircleMesh)
	{
		UMaterialInterface* LineMat = MasterCircleMaterial;
		if (!LineMat)
		{
			LineMat = Cast<UMaterialInterface>(StaticLoadObject(UMaterialInterface::StaticClass(), nullptr,
				TEXT("/Game/IsekaiVillage/Materials/M_SpellEmissive_Master.M_SpellEmissive_Master")));
		}
		if (LineMat)
		{
			UMaterialInstanceDynamic* LineMID = UMaterialInstanceDynamic::Create(LineMat, this);
			GeneratedCircleMesh->SetMaterial(0, LineMID);
		}
		GeneratedCircleMesh->SetVisibility(false);
	}

	RebuildCircle();
}

void AProceduralMagicCircle::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);

	if (bIsFadingOut)
	{
		FadeTimer -= DeltaTime;
		if (FadeTimer <= 0.0f)
		{
			bIsFadingOut = false;
			TargetVisualScale = 0.0f;
			VisualState = ECircleVisualState::Stowed;
		}
	}

	VisualScale = FMath::FInterpTo(VisualScale, TargetVisualScale, DeltaTime, 14.0f);

	if (VisualScale <= 0.02f)
	{
		if (CircleMeshComp) CircleMeshComp->SetVisibility(false);
		if (GeneratedCircleMesh) GeneratedCircleMesh->SetVisibility(false);
		return;
	}

	if (GeneratedCircleMesh)
	{
		GeneratedCircleMesh->SetVisibility(true);
		GeneratedCircleMesh->SetAbsolute(false, false, false);
		const float S = FMath::Max(0.01f, VisualScale);
		GeneratedCircleMesh->SetRelativeScale3D(FVector(S));
	}
	if (CircleMeshComp)
	{
		CircleMeshComp->SetVisibility(false);
	}

	if (VisualState == ECircleVisualState::Casting)
	{
		CurrentRotation += DeltaTime * (0.45f + ActiveChargeRatio * 0.75f);
	}
	else
	{
		CurrentRotation = 0.0f;
	}

	if (GeneratedCircleMesh)
	{
		GeneratedCircleMesh->SetRelativeRotation(FRotator(0.0f, FMath::RadiansToDegrees(CurrentRotation), 0.0f));
	}

	if (VisualState == ECircleVisualState::Casting)
	{
		RebuildGeneratedGeometry();
	}

	if (!DynamicCircleMaterial && CircleMeshComp && MasterCircleMaterial)
	{
		DynamicCircleMaterial = CircleMeshComp->CreateAndSetMaterialInstanceDynamicFromMaterial(0, MasterCircleMaterial);
		RebuildCircle();
	}

	if (DynamicCircleMaterial)
	{
		FLinearColor Color = GetElementColor(ActiveElement);
		float EffectiveGlow = EmissivePower * (1.0f + ActiveChargeRatio * 0.6f);

		DynamicCircleMaterial->SetVectorParameterValue(FName("EmissiveColor"), Color);
		DynamicCircleMaterial->SetScalarParameterValue(FName("GlowIntensity"), EffectiveGlow);

		UTexture2D* TargetTex = GetTextureForElement(ActiveElement);
		if (TargetTex)
		{
			DynamicCircleMaterial->SetTextureParameterValue(FName("CircleTexture"), TargetTex);
		}
	}
}

FLinearColor AProceduralMagicCircle::GetElementColor(EElement InElement) const
{
	if (SpellVisuals && SpellVisuals->ElementVisuals.Contains(InElement))
	{
		return SpellVisuals->ElementVisuals[InElement].PrimaryColor;
	}

	switch (InElement)
	{
	case EElement::Fire:  return FLinearColor(1.0f, 0.22f, 0.04f, 1.0f);
	case EElement::Earth: return FLinearColor(0.95f, 0.60f, 0.12f, 1.0f);
	case EElement::Wind:  return FLinearColor(0.12f, 0.95f, 0.55f, 1.0f);
	case EElement::Water: return FLinearColor(0.04f, 0.65f, 1.0f, 1.0f);
	default:              return FLinearColor(0.04f, 0.65f, 1.0f, 1.0f);
	}
}

UTexture2D* AProceduralMagicCircle::GetTextureForElement(EElement InElement) const
{
	switch (InElement)
	{
	case EElement::Fire:  return FireCircleTexture ? FireCircleTexture : MasterCircleTexture;
	case EElement::Earth: return EarthCircleTexture ? EarthCircleTexture : MasterCircleTexture;
	case EElement::Wind:  return WindCircleTexture ? WindCircleTexture : MasterCircleTexture;
	case EElement::Water: return WaterCircleTexture ? WaterCircleTexture : MasterCircleTexture;
	default:              return MasterCircleTexture;
	}
}

void AProceduralMagicCircle::SetActiveElement(EElement NewElement)
{
	ActiveElement = NewElement;
}

void AProceduralMagicCircle::RebuildCircle()
{
	if (DynamicCircleMaterial)
	{
		DynamicCircleMaterial->SetVectorParameterValue(FName("EmissiveColor"), GetElementColor(ActiveElement));

		UTexture2D* TargetTex = GetTextureForElement(ActiveElement);
		if (TargetTex)
		{
			DynamicCircleMaterial->SetTextureParameterValue(FName("CircleTexture"), TargetTex);
		}
	}

	RebuildGeneratedGeometry();

	if (CircleVFX)
	{
		if (SpellVisuals)
		{
			if (UNiagaraSystem* FX = SpellVisuals->GetCircleFXForElement(ActiveElement))
			{
				if (CircleVFX->GetAsset() != FX)
				{
					CircleVFX->SetAsset(FX);
				}
				CircleVFX->SetVariableLinearColor(FName("User.Color"), GetElementColor(ActiveElement));
				CircleVFX->SetVariableFloat(FName("User.EmissivePower"), EmissivePower);
				CircleVFX->Activate(true);
			}
		}
		int32 Count = 6;
		int32 Skip = 1;
		FMagicCircleGeometry::GetShapeForElement(ActiveElement, Count, Skip);
		CircleVFX->SetVariableInt(FName("User.Symmetry"), Count);
		CircleVFX->SetVariableInt(FName("User.Skip"), Skip);
		CircleVFX->SetVariableFloat(FName("User.Charge"), ActiveChargeRatio);
	}
}

void AProceduralMagicCircle::SetVisualState(ECircleVisualState NewState)
{
	VisualState = NewState;
	if (VisualState == ECircleVisualState::Casting)
	{
		TargetVisualScale = 0.55f + ActiveChargeRatio * 0.35f;
		if (GeneratedCircleMesh) GeneratedCircleMesh->SetVisibility(true);
		bIsFadingOut = false;
	}
	else if (VisualState == ECircleVisualState::Stowed)
	{
		TargetVisualScale = 0.0f;
	}
}

void AProceduralMagicCircle::SetChargeProgress(float ChargeRatio)
{
	ActiveChargeRatio = FMath::Clamp(ChargeRatio, 0.0f, 1.0f);
	VisualState = ECircleVisualState::Casting;
	TargetVisualScale = 0.55f + ActiveChargeRatio * 0.35f;
	if (GeneratedCircleMesh) GeneratedCircleMesh->SetVisibility(true);
	bIsFadingOut = false;
	RebuildGeneratedGeometry();
}

void AProceduralMagicCircle::ActivateSpellBurst(bool bStayActive)
{
	if (!bStayActive)
	{
		bIsFadingOut = true;
		FadeTimer = 0.35f;
	}
	else
	{
		VisualState = ECircleVisualState::Sustained;
		TargetVisualScale = 1.0f;
		VisualScale = 1.0f;
		if (GeneratedCircleMesh) GeneratedCircleMesh->SetVisibility(true);
	}
}

void AProceduralMagicCircle::DeactivateCircle()
{
	VisualState = ECircleVisualState::Stowed;
	bIsFadingOut = false;
	TargetVisualScale = 0.0f;
	VisualScale = 0.0f;
	if (GeneratedCircleMesh) GeneratedCircleMesh->SetVisibility(false);
	if (CircleVFX) CircleVFX->Deactivate();
}

void AProceduralMagicCircle::AppendRibbon(
	TArray<FVector>& Verts, TArray<int32>& Tris, TArray<FVector>& Normals, TArray<FVector2D>& UVs, TArray<FColor>& Colors,
	const TArray<FVector2D>& Poly, float HalfWidth, float DrawAlpha, const FColor& Color)
{
	if (Poly.Num() < 2 || DrawAlpha <= 0.01f) return;

	float TotalLen = 0.0f;
	for (int32 i = 1; i < Poly.Num(); ++i)
	{
		TotalLen += FVector2D::Distance(Poly[i - 1], Poly[i]);
	}
	if (TotalLen <= KINDA_SMALL_NUMBER) return;

	const float MaxLen = TotalLen * FMath::Clamp(DrawAlpha, 0.0f, 1.0f);
	float Acc = 0.0f;

	for (int32 i = 1; i < Poly.Num(); ++i)
	{
		const FVector2D A = Poly[i - 1];
		const FVector2D B = Poly[i];
		const float SegLen = FVector2D::Distance(A, B);
		if (SegLen <= KINDA_SMALL_NUMBER) continue;

		FVector2D End = B;
		float UseLen = SegLen;
		if (Acc + SegLen > MaxLen)
		{
			const float T = (MaxLen - Acc) / SegLen;
			End = FMath::Lerp(A, B, T);
			UseLen = MaxLen - Acc;
		}

		FVector2D Dir = End - A;
		Dir.Normalize();
		const FVector2D Right(-Dir.Y, Dir.X);

		const int32 Base = Verts.Num();
		const FVector P0(A.X - Right.X * HalfWidth, A.Y - Right.Y * HalfWidth, 1.2f);
		const FVector P1(A.X + Right.X * HalfWidth, A.Y + Right.Y * HalfWidth, 1.2f);
		const FVector P2(End.X + Right.X * HalfWidth, End.Y + Right.Y * HalfWidth, 1.2f);
		const FVector P3(End.X - Right.X * HalfWidth, End.Y - Right.Y * HalfWidth, 1.2f);

		Verts.Add(P0); Verts.Add(P1); Verts.Add(P2); Verts.Add(P3);
		Normals.Add(FVector::UpVector); Normals.Add(FVector::UpVector);
		Normals.Add(FVector::UpVector); Normals.Add(FVector::UpVector);
		UVs.Add(FVector2D(0, 0)); UVs.Add(FVector2D(1, 0));
		UVs.Add(FVector2D(1, 1)); UVs.Add(FVector2D(0, 1));
		Colors.Add(Color); Colors.Add(Color); Colors.Add(Color); Colors.Add(Color);
		Tris.Add(Base + 0); Tris.Add(Base + 1); Tris.Add(Base + 2);
		Tris.Add(Base + 0); Tris.Add(Base + 2); Tris.Add(Base + 3);

		Acc += UseLen;
		if (Acc >= MaxLen - KINDA_SMALL_NUMBER) break;
	}
}

void AProceduralMagicCircle::RebuildGeneratedGeometry()
{
	if (!GeneratedCircleMesh) return;

	const TArray<FMagicCirclePoly> CompiledLayers = FMagicCircleGeometry::BuildElementCircle(ActiveElement, ActiveChargeRatio);
	TArray<FVector> Verts;
	TArray<int32> Tris;
	TArray<FVector> Normals;
	TArray<FVector2D> UVs;
	TArray<FColor> Colors;
	const FColor Col = (GetElementColor(ActiveElement) * (EmissivePower * 0.35f)).ToFColor(true);

	for (const FMagicCirclePoly& Layer : CompiledLayers)
	{
		const float Span = FMath::Max(0.01f, Layer.DrawEnd - Layer.DrawStart);
		float Local = (ActiveChargeRatio - Layer.DrawStart) / Span;
		Local = FMath::Clamp(Local, 0.0f, 1.0f);
		AppendRibbon(Verts, Tris, Normals, UVs, Colors, Layer.Points, Layer.HalfWidth, Local, Col);
	}

	if (Verts.Num() == 0)
	{
		GeneratedCircleMesh->ClearAllMeshSections();
		return;
	}

	GeneratedCircleMesh->CreateMeshSection(0, Verts, Tris, Normals, UVs, Colors, TArray<FProcMeshTangent>(), false);
	if (UMaterialInterface* Mat = GeneratedCircleMesh->GetMaterial(0))
	{
		if (UMaterialInstanceDynamic* Dyn = Cast<UMaterialInstanceDynamic>(Mat))
		{
			Dyn->SetVectorParameterValue(FName("Color"), GetElementColor(ActiveElement));
			Dyn->SetVectorParameterValue(FName("EmissiveColor"), GetElementColor(ActiveElement));
			Dyn->SetScalarParameterValue(FName("GlowIntensity"), EmissivePower * (1.0f + ActiveChargeRatio * 0.6f));
		}
	}
}
