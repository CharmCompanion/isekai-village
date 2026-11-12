// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/Texture2D.h"
#include "IsekaiVillageTypes.h"
#include "ProceduralMeshComponent.h"
#include "NiagaraComponent.h"
#include "ProceduralMagicCircle.generated.h"

UENUM(BlueprintType)
enum class ECircleVisualState : uint8
{
	Stowed      UMETA(DisplayName = "Stowed (Hidden)"),
	Casting     UMETA(DisplayName = "Casting (Active)"),
	Sustained   UMETA(DisplayName = "Sustained (Placed World Construct)")
};

/**
 * Magic Circle — visual only (color + rotation, no tiers/compile).
 * Swap texture + tint by ActiveElement.
 */
UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AProceduralMagicCircle : public AActor
{
	GENERATED_BODY()

public:
	AProceduralMagicCircle();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UProceduralMeshComponent* GeneratedCircleMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* CircleMeshComp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UNiagaraComponent* CircleVFX;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle")
	UMaterialInterface* MasterCircleMaterial;

	UPROPERTY(Transient)
	UMaterialInstanceDynamic* DynamicCircleMaterial;

	// Element Textures
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle|Textures")
	UTexture2D* MasterCircleTexture;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle|Textures")
	UTexture2D* FireCircleTexture;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle|Textures")
	UTexture2D* EarthCircleTexture;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle|Textures")
	UTexture2D* WindCircleTexture;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle|Textures")
	UTexture2D* WaterCircleTexture;

	// Active element drives visual
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MagicCircle")
	EElement ActiveElement = EElement::Fire;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle")
	class USpellVisualDataAsset* SpellVisuals;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "MagicCircle")
	float EmissivePower = 14.0f;

	// Visual State Management
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MagicCircle")
	ECircleVisualState VisualState = ECircleVisualState::Stowed;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MagicCircle")
	float VisualScale = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MagicCircle")
	float TargetVisualScale = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MagicCircle")
	float FadeTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "MagicCircle")
	bool bIsFadingOut = false;

	UFUNCTION(BlueprintPure, Category = "MagicCircle")
	FLinearColor GetElementColor(EElement InElement) const;

	UFUNCTION(BlueprintPure, Category = "MagicCircle")
	UTexture2D* GetTextureForElement(EElement InElement) const;

	UFUNCTION(BlueprintCallable, Category = "MagicCircle")
	void SetActiveElement(EElement NewElement);

	UFUNCTION(BlueprintCallable, Category = "MagicCircle")
	void RebuildCircle();

	UFUNCTION(BlueprintCallable, Category = "MagicCircle")
	void SetVisualState(ECircleVisualState NewState);

	UFUNCTION(BlueprintCallable, Category = "MagicCircle")
	void SetChargeProgress(float ChargeRatio);

	UFUNCTION(BlueprintCallable, Category = "MagicCircle")
	void ActivateSpellBurst(bool bStayActive = false);

	UFUNCTION(BlueprintCallable, Category = "MagicCircle")
	void DeactivateCircle();

private:
	float CurrentRotation = 0.0f;
	float ActiveChargeRatio = 0.0f;

	void LoadDefaultAssets();
	void RebuildGeneratedGeometry();
	void AppendRibbon(TArray<FVector>& Verts, TArray<int32>& Tris, TArray<FVector>& Normals, TArray<FVector2D>& UVs, TArray<FColor>& Colors, const TArray<FVector2D>& Poly, float HalfWidth, float DrawAlpha, const FColor& Color);
};
