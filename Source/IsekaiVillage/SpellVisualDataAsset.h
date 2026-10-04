// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "NiagaraSystem.h"
#include "Sound/SoundBase.h"
#include "IsekaiVillageTypes.h"
#include "SpellVisualDataAsset.generated.h"

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FElementalVisualData
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	FLinearColor PrimaryColor = FLinearColor::White;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	UNiagaraSystem* MagicCircleFX = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	UNiagaraSystem* ProjectileFX = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Visuals")
	UNiagaraSystem* ImpactFX = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	USoundBase* CastSound = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Audio")
	USoundBase* ImpactSound = nullptr;
};

/**
 * Master Visual Data Asset — 4 elements only (no fusions).
 * Edit colors, Niagara FX, sounds per element in ONE central asset.
 */
UCLASS(BlueprintType)
class ISEKAIVILLAGE_API USpellVisualDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	USpellVisualDataAsset();

	// 4 Core Elements
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Elemental Visuals")
	TMap<EElement, FElementalVisualData> ElementVisuals;

	UFUNCTION(BlueprintPure, Category = "Visuals")
	FLinearColor GetColorForElement(EElement InElement) const;

	UFUNCTION(BlueprintPure, Category = "Visuals")
	UNiagaraSystem* GetProjectileFXForElement(EElement InElement) const;

	UFUNCTION(BlueprintPure, Category = "Visuals")
	UNiagaraSystem* GetCircleFXForElement(EElement InElement) const;

	UFUNCTION(BlueprintPure, Category = "Visuals")
	UNiagaraSystem* GetImpactFXForElement(EElement InElement) const;
};
