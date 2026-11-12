// Copyright Epic Games, Inc. All Rights Reserved.

#include "SpellVisualDataAsset.h"

USpellVisualDataAsset::USpellVisualDataAsset()
{
	FElementalVisualData Fire;
	Fire.PrimaryColor = FLinearColor(1.0f, 0.28f, 0.06f, 1.0f);
	ElementVisuals.Add(EElement::Fire, Fire);

	FElementalVisualData Earth;
	Earth.PrimaryColor = FLinearColor(0.88f, 0.68f, 0.22f, 1.0f);
	ElementVisuals.Add(EElement::Earth, Earth);

	FElementalVisualData Wind;
	Wind.PrimaryColor = FLinearColor(0.20f, 0.98f, 0.68f, 1.0f);
	ElementVisuals.Add(EElement::Wind, Wind);

	FElementalVisualData Water;
	Water.PrimaryColor = FLinearColor(0.12f, 0.72f, 1.0f, 1.0f);
	ElementVisuals.Add(EElement::Water, Water);
}

FLinearColor USpellVisualDataAsset::GetColorForElement(EElement InElement) const
{
	if (ElementVisuals.Contains(InElement))
	{
		return ElementVisuals[InElement].PrimaryColor;
	}
	return FLinearColor::White;
}

UNiagaraSystem* USpellVisualDataAsset::GetProjectileFXForElement(EElement InElement) const
{
	if (ElementVisuals.Contains(InElement))
	{
		return ElementVisuals[InElement].ProjectileFX;
	}
	return nullptr;
}

UNiagaraSystem* USpellVisualDataAsset::GetCircleFXForElement(EElement InElement) const
{
	if (ElementVisuals.Contains(InElement))
	{
		return ElementVisuals[InElement].MagicCircleFX;
	}
	return nullptr;
}

UNiagaraSystem* USpellVisualDataAsset::GetImpactFXForElement(EElement InElement) const
{
	if (ElementVisuals.Contains(InElement))
	{
		return ElementVisuals[InElement].ImpactFX;
	}
	return nullptr;
}
