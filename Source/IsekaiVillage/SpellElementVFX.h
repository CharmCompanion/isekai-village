// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "IsekaiVillageTypes.h"

class UNiagaraSystem;
class UNiagaraComponent;

/**
 * Maps (Element, Shape) → real Fab Niagara.
 * Shapes: spear, homing, wave, wall, mine, orbit_shield.
 */
struct FSpellElementVFX
{
	static UNiagaraSystem* LoadFirst(const TCHAR* const* Paths, int32 Count);
	static FLinearColor GetElementColor(EElement Element);

	static UNiagaraSystem* LoadBodyFX(EElement Element, FName Shape);
	static UNiagaraSystem* LoadChargeFX(EElement Element, FName Shape);
	static UNiagaraSystem* LoadAuraFX(EElement Element);
	static UNiagaraSystem* LoadImpactFX(EElement Element);

	static FVector GetBodyScale(EElement Element, FName Shape, float ChargeRatio);
	static float GetBodyLength(EElement Element, FName Shape, float ChargeRatio);
	static void ApplyBodyParams(UNiagaraComponent* Comp, EElement Element, FName Shape, float ChargeRatio);

	static UNiagaraSystem* LoadOrbFX(EElement Element);
	static void ApplyOrbParams(UNiagaraComponent* Comp, EElement Element, float ChargeRatio);

	static UNiagaraSystem* LoadWallFX(EElement Element);
	static void ApplyWallParams(UNiagaraComponent* Comp, EElement Element, float Width, float Height, float Progress);
	static bool WallUsesSolidMesh(EElement Element);
};
