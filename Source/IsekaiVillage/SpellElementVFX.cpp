// Copyright IsekaiVillage.
#include "SpellElementVFX.h"
#include "NiagaraSystem.h"
#include "NiagaraComponent.h"

UNiagaraSystem* FSpellElementVFX::LoadFirst(const TCHAR* const* Paths, int32 Count)
{
	for (int32 i = 0; i < Count; ++i)
	{
		if (UNiagaraSystem* Sys = Cast<UNiagaraSystem>(StaticLoadObject(UNiagaraSystem::StaticClass(), nullptr, Paths[i])))
		{
			return Sys;
		}
	}
	return nullptr;
}

FLinearColor FSpellElementVFX::GetElementColor(EElement Element)
{
	switch (Element)
	{
	case EElement::Fire:       return FLinearColor(1.0f, 0.28f, 0.04f, 1.0f);
	case EElement::Earth:      return FLinearColor(0.72f, 0.45f, 0.12f, 1.0f);
	case EElement::Wind:       return FLinearColor(0.45f, 1.0f, 0.70f, 1.0f);
	case EElement::Water:      return FLinearColor(0.10f, 0.55f, 1.0f, 1.0f);
	default:                   return FLinearColor::White;
	}
}

static bool IsSpearForm(FName Shape)
{
	return Shape == FName("spear") || Shape == FName("drill") || Shape == FName("pierce") || Shape.IsNone();
}

static bool IsHomingForm(FName Shape)
{
	return Shape == FName("homing") || Shape == FName("ball");
}

static bool IsWaveForm(FName Shape)
{
	return Shape == FName("wave") || Shape == FName("aoe") || Shape == FName("nova");
}

UNiagaraSystem* FSpellElementVFX::LoadBodyFX(EElement Element, FName Shape)
{
	const bool bSpear = IsSpearForm(Shape);
	const bool bHoming = IsHomingForm(Shape);
	const bool bWave = IsWaveForm(Shape);

	switch (Element)
	{
	case EElement::Fire:
		if (bWave)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/MixedVFX/Particles/Fires/NS_FlameTornado.NS_FlameTornado"),
				TEXT("/Game/MixedVFX/Particles/Fires/NS_FlameThrower.NS_FlameThrower"),
				TEXT("/Game/MixedVFX/Particles/Fires/NS_BigFire.NS_BigFire"),
				TEXT("/Game/MixedVFX/Particles/Fires/NS_FireBarrier.NS_FireBarrier"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		if (bHoming)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/Sperate_VFX/NS_Magma_Shot_Projectile.NS_Magma_Shot_Projectile"),
				TEXT("/Game/MixedVFX/Particles/Fires/NS_BigFire.NS_BigFire"),
				TEXT("/Game/MixedVFX/Particles/Projectiles/NS_FireArrow.NS_FireArrow"),
				TEXT("/Game/MixedVFX/Particles/Fires/NS_TorchFire.NS_TorchFire"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		// spear = flame lance / hose from hand.
		// NS_Sword_Fire leads because it exposes SwordLength/Color, so it can be shaped and tinted;
		// NS_FlameThrower has no user params and always renders its own baked cone.
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Fire/NS_Sword_Fire.NS_Sword_Fire"),
				TEXT("/Game/MixedVFX/Particles/Fires/NS_FlameThrower.NS_FlameThrower"),
				TEXT("/Game/MixedVFX/Particles/Slashes/SeparateParts/Slashes/NS_FireSlash_OnlySlash.NS_FireSlash_OnlySlash"),
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/Sperate_VFX/NS_Magma_Shot_Projectile.NS_Magma_Shot_Projectile"),
				TEXT("/Game/_SplineVFX/NS/NS_Spline_Fire.NS_Spline_Fire"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}

	case EElement::Water:
		if (bWave)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/_SplineVFX/NS/NS_Spline_WaterSplash.NS_Spline_WaterSplash"),
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Magic_Big_Bubbles_Explosion.NS_Magic_Big_Bubbles_Explosion"),
				TEXT("/Game/SoStylized/Environment/Water/NS_WaterfallSplash.NS_WaterfallSplash"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_SlashTrail_Water_Loop.NS_SlashTrail_Water_Loop"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		if (bHoming)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Magic_Bubbles.NS_Magic_Bubbles"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_AuraFX_Water.NS_AuraFX_Water"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Ice/NS_AuraFX_Ice.NS_AuraFX_Ice"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_Sword_Water.NS_Sword_Water"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_SlashTrail_Water_Loop.NS_SlashTrail_Water_Loop"),
				TEXT("/Game/_SplineVFX/NS/NS_Spline_WaterSplash.NS_Spline_WaterSplash"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Ice/NS_Sword_Ice.NS_Sword_Ice"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}

	case EElement::Earth:
		if (bWave)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Crystal_Torrent.NS_Crystal_Torrent"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_SlashTrail_Sand_Loop.NS_SlashTrail_Sand_Loop"),
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Shattering_Crystal.NS_Shattering_Crystal"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		if (bHoming)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Shattering_Crystal.NS_Shattering_Crystal"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_AuraFX_Sand.NS_AuraFX_Sand"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Nature/NS_AuraFX_Nature.NS_AuraFX_Nature"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_Sword_Sand.NS_Sword_Sand"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Nature/NS_Sword_Nature.NS_Sword_Nature"),
				TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Crystal_Torrent.NS_Crystal_Torrent"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_SlashTrail_Sand_Loop.NS_SlashTrail_Sand_Loop"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}

	case EElement::Wind:
		if (bWave)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/MixedVFX/Particles/Mix/NS_Wind.NS_Wind"),
				TEXT("/Game/_SplineVFX/NS/NS_Spline_Wind.NS_Spline_Wind"),
				TEXT("/Game/SoStylized/Effects/NS_WindLines.NS_WindLines"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		if (bHoming)
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_AuraFX_Wind.NS_AuraFX_Wind"),
				TEXT("/Game/MixedVFX/Particles/Mix/NS_Wind.NS_Wind"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}
		{
			static const TCHAR* Paths[] = {
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_Sword_Wind.NS_Sword_Wind"),
				TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_SlashTrail_Wind.NS_SlashTrail_Wind"),
				TEXT("/Game/_SplineVFX/NS/NS_Spline_Wind.NS_Spline_Wind"),
			};
			return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
		}

	default:
		return nullptr;
	}
}

UNiagaraSystem* FSpellElementVFX::LoadChargeFX(EElement Element, FName Shape)
{
	// Prefer continuous hand forms (flamethrower / hose / rock aura) over one-shot owner casts
	if (UNiagaraSystem* Body = LoadBodyFX(Element, Shape))
	{
		return Body;
	}

	switch (Element)
	{
	case EElement::Fire:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Magma_Shot_Owner_Cast_Spell.NS_Magma_Shot_Owner_Cast_Spell"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Fire/NS_AuraFX_Fire.NS_AuraFX_Fire"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Water:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Magic_Bubbles_Owner_Cast_Spell.NS_Magic_Bubbles_Owner_Cast_Spell"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_AuraFX_Water.NS_AuraFX_Water"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Earth:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Crystal_Torrent_Owner_Cast.NS_Crystal_Torrent_Owner_Cast"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_AuraFX_Sand.NS_AuraFX_Sand"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Wind:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_AuraFX_Wind.NS_AuraFX_Wind"),
			TEXT("/Game/MixedVFX/Particles/Mix/NS_Wind.NS_Wind"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	default:
		return nullptr;
	}
}

UNiagaraSystem* FSpellElementVFX::LoadAuraFX(EElement Element)
{
	switch (Element)
	{
	case EElement::Fire:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Fire/NS_AuraFX_Fire.NS_AuraFX_Fire"),
			TEXT("/Game/MixedVFX/Particles/Fires/NS_TorchFire.NS_TorchFire"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Water:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_AuraFX_Water.NS_AuraFX_Water"),
			TEXT("/Game/_SplineVFX/NS/NS_Spline_Frost.NS_Spline_Frost"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Earth:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_AuraFX_Sand.NS_AuraFX_Sand"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Nature/NS_AuraFX_Nature.NS_AuraFX_Nature"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Wind:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_AuraFX_Wind.NS_AuraFX_Wind"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	default:
		return nullptr;
	}
}

UNiagaraSystem* FSpellElementVFX::LoadImpactFX(EElement Element)
{
	switch (Element)
	{
	case EElement::Fire:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/MixedVFX/Particles/Projectiles/Hits/NS_FireArrow_Hit.NS_FireArrow_Hit"),
			TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/Sperate_VFX/NS_Magma_Shot_Impact.NS_Magma_Shot_Impact"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Fire/NS_Hit_Fire_Once.NS_Hit_Fire_Once"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Water:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_Hit_water_Once.NS_Hit_water_Once"),
			TEXT("/Game/_SplineVFX/NS/NS_Spline_WaterSplash.NS_Spline_WaterSplash"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Earth:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_Hit_Sand_Once.NS_Hit_Sand_Once"),
			TEXT("/Game/Mixed_Magic_VFX_Pack/VFX/NS_Shattering_Crystal.NS_Shattering_Crystal"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Wind:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_Hit_Wind_Once.NS_Hit_Wind_Once"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	default:
		return nullptr;
	}
}

FVector FSpellElementVFX::GetBodyScale(EElement Element, FName Shape, float ChargeRatio)
{
	const float Grow = 1.0f + ChargeRatio * 0.55f;
	if (IsWaveForm(Shape))
	{
		return FVector(2.8f, 2.8f, 2.2f) * Grow;
	}
	if (IsHomingForm(Shape))
	{
		return FVector(1.8f) * Grow;
	}

	// Spear thickness only. Length is driven by GetBodyLength through User.SwordLength /
	// User.EndParticle_Position; stretching the component instead elongated local Z, which is the
	// projectile's *up*, so lances rendered as vertical smears rather than pointing along travel.
	float Rad = 1.4f;
	if (Element == EElement::Fire || Element == EElement::Water) { Rad = 1.5f; }
	if (Element == EElement::Earth) { Rad = 1.8f; }
	return FVector(Rad) * Grow;
}

float FSpellElementVFX::GetBodyLength(EElement Element, FName Shape, float ChargeRatio)
{
	const float Grow = 1.0f + ChargeRatio * 0.55f;
	if (IsWaveForm(Shape))
	{
		return 90.0f * Grow;
	}
	if (IsHomingForm(Shape))
	{
		return 60.0f * Grow;
	}

	// Lance length along forward, per element read: bolts long and thin, rock short and chunky.
	float Len = 200.0f;
	switch (Element)
	{
	case EElement::Water:     Len = 240.0f; break;
	case EElement::Fire:      Len = 220.0f; break;
	case EElement::Wind:      Len = 210.0f; break;
	case EElement::Earth:     Len = 150.0f; break;
	default: break;
	}
	return Len * Grow;
}

void FSpellElementVFX::ApplyBodyParams(UNiagaraComponent* Comp, EElement Element, FName Shape, float ChargeRatio)
{
	if (!Comp)
	{
		return;
	}

	const FLinearColor Color = GetElementColor(Element);
	const float Length = GetBodyLength(Element, Shape, ChargeRatio);

	// SlashTrail systems build their trail from the origin to EndParticle_Position, so putting that
	// on +X aims the lance down the projectile's travel direction.
	Comp->SetVariableLinearColor(FName("User.Color"), Color);
	Comp->SetVariableLinearColor(FName("User.Color002"), Color);
	Comp->SetVariableFloat(FName("User.SwordLength"), Length);
	Comp->SetVariableVec3(FName("User.EndParticle_Position"), FVector(Length, 0.0f, 0.0f));
	Comp->SetVariableFloat(FName("User.Brightness"), 1.5f + ChargeRatio);
	Comp->SetVariableFloat(FName("User.TrailWidth"), 6.0f + ChargeRatio * 6.0f);

	// Kept for the handful of packs that read these instead.
	Comp->SetVariableFloat(FName("User.Scale"), 1.0f + ChargeRatio * 0.5f);
	Comp->SetVariableFloat(FName("User.Charge"), ChargeRatio);
	Comp->SetVariableInt(FName("User.ElementType"), static_cast<int32>(Element));
}

UNiagaraSystem* FSpellElementVFX::LoadOrbFX(EElement Element)
{
	// The AuraFX family swirls around a point, which is what a held bending orb needs.
	// The sword/spline families are directional and read as a lance instead of a ball.
	switch (Element)
	{
	case EElement::Fire:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Fire/NS_AuraFX_Fire.NS_AuraFX_Fire"),
			TEXT("/Game/MixedVFX/Particles/Fires/NS_BigFire.NS_BigFire"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Water:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Water/NS_AuraFX_Water.NS_AuraFX_Water"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Ice/NS_AuraFX_Ice.NS_AuraFX_Ice"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Earth:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Sand/NS_AuraFX_Sand.NS_AuraFX_Sand"),
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Nature/NS_AuraFX_Nature.NS_AuraFX_Nature"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Wind:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/SlashTrail_SoftTofu/Niagara/Wind/NS_AuraFX_Wind.NS_AuraFX_Wind"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	default:
		return nullptr;
	}
}

void FSpellElementVFX::ApplyOrbParams(UNiagaraComponent* Comp, EElement Element, float ChargeRatio)
{
	if (!Comp)
	{
		return;
	}

	// Ball swells from a spark to a held mass as the cast charges.
	const float Radius = FMath::Lerp(8.0f, 34.0f, FMath::Clamp(ChargeRatio, 0.0f, 1.0f));
	const float Size = FMath::Lerp(0.6f, 2.4f, FMath::Clamp(ChargeRatio, 0.0f, 1.0f));

	Comp->SetVariableLinearColor(FName("User.Color"), GetElementColor(Element));
	Comp->SetVariableFloat(FName("User.Radius"), Radius);
	Comp->SetVariableFloat(FName("User.Size"), Size);
	Comp->SetVariableFloat(FName("User.Brightness"), 1.0f + ChargeRatio * 1.8f);
	Comp->SetVariableFloat(FName("User.MeshScale"), Size);
	Comp->SetVariableFloat(FName("User.Spark_Radius"), Radius);

	// Aura systems that still expect a blade extent get a short one so they curl into a ball.
	Comp->SetVariableFloat(FName("User.SwordLength"), Radius);
	Comp->SetVariableVec3(FName("User.EndParticle_Position"), FVector(Radius, 0.0f, 0.0f));
}

bool FSpellElementVFX::WallUsesSolidMesh(EElement Element)
{
	return Element == EElement::Earth;
}

UNiagaraSystem* FSpellElementVFX::LoadWallFX(EElement Element)
{
	// Spline systems run along a line and expose Extent/Progress, so they read as a curtain.
	switch (Element)
	{
	case EElement::Fire:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/_SplineVFX/NS/NS_Spline_Fire.NS_Spline_Fire"),
			TEXT("/Game/MixedVFX/Particles/Fires/NS_FireBarrier.NS_FireBarrier"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Water:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/_SplineVFX/NS/NS_Spline_WaterSplash.NS_Spline_WaterSplash"),
			TEXT("/Game/_SplineVFX/NS/NS_Spline_Frost.NS_Spline_Frost"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	case EElement::Wind:
	{
		static const TCHAR* Paths[] = {
			TEXT("/Game/_SplineVFX/NS/NS_Spline_Wind.NS_Spline_Wind"),
		};
		return LoadFirst(Paths, UE_ARRAY_COUNT(Paths));
	}
	default:
		return nullptr; // Earth erupts as solid geometry instead.
	}
}

void FSpellElementVFX::ApplyWallParams(UNiagaraComponent* Comp, EElement Element, float Width, float Height, float Progress)
{
	if (!Comp)
	{
		return;
	}

	const FLinearColor Color = GetElementColor(Element);

	// Extent spans the wall face; the spline pack reads it as the emitter volume.
	Comp->SetVariableVec3(FName("User.Extent"), FVector(20.0f, Width, Height));
	Comp->SetVariableFloat(FName("User.Progress"), FMath::Clamp(Progress, 0.0f, 1.0f));
	Comp->SetVariableFloat(FName("User._Size"), FMath::Max(1.0f, Height / 120.0f));
	Comp->SetVariableFloat(FName("User._Width"), FMath::Max(1.0f, Width / 160.0f));
	Comp->SetVariableFloat(FName("User._Brightness"), 1.6f);
	Comp->SetVariableFloat(FName("User.Count"), FMath::Clamp(Width / 8.0f, 12.0f, 90.0f));
	Comp->SetVariableBool(FName("User._AdaptTerrain"), true);

	// The pack names this "_ColorHue"; set both forms since only the matching type binds.
	Comp->SetVariableLinearColor(FName("User._ColorHue"), Color);
	Comp->SetVariableLinearColor(FName("User.Tint"), Color);
	Comp->SetVariableLinearColor(FName("User.Color"), Color);
}

