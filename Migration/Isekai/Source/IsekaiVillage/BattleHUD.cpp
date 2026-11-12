// Copyright Epic Games, Inc. All Rights Reserved.
// BattleHUD.cpp — LMBS Real-Time Combat HUD (HP/TP, Combo Ticker, Artes Bar, Target Reticle, Victory Banner)

#include "BattleHUD.h"
#include "BattleCharacter.h"
#include "BattleEnemy.h"
#include "PartyCombatManager.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

ABattleHUD::ABattleHUD()
{
	RecentMinorElements.Add(EElement::Water);
	RecentMinorElements.Add(EElement::Wind);
	RecentMinorElements.Add(EElement::Earth);
}

void ABattleHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas) return;

	float DeltaTime = GetWorld() ? GetWorld()->GetDeltaSeconds() : 0.016f;

	// Tick combo decay
	if (ComboTimer > 0.0f)
	{
		ComboTimer -= DeltaTime;
		if (ComboTimer <= 0.0f)
		{
			ComboHitCount = 0;
			ComboTotalDamage = 0.0f;
		}
	}

	APawn* Pawn = GetOwningPawn();
	ABattleCharacter* Character = Cast<ABattleCharacter>(Pawn);

	if (Character)
	{
		DrawPartyRoster(Character);
		DrawArtesBar(Character);
		DrawTargetLock(Character);
		DrawEscapeMeter(Character);
	}

	DrawComboCounter();
	DrawStartBanner();

	if (bVictoryActive)
	{
		VictoryTimer += DeltaTime;
		DrawVictoryBanner();
	}
	else if (bDefeatActive)
	{
		DefeatTimer += DeltaTime;
		DrawDefeatBanner();
	}
}

void ABattleHUD::RegisterComboHit(float Damage)
{
	ComboHitCount++;
	ComboTotalDamage += Damage;
	ComboTimer = MaxComboDuration;
}

void ABattleHUD::RegisterElementCast(EElement Element)
{
	DominantElement = Element;
	RecentMinorElements.Insert(Element, 0);
	if (RecentMinorElements.Num() > 4)
	{
		RecentMinorElements.SetNum(4);
	}
}

void ABattleHUD::ShowBattleStartBanner(const FText& Title, const FText& Subtitle, float Duration)
{
	StartBannerTitle = Title;
	StartBannerSubtitle = Subtitle;
	StartBannerDuration = Duration > 0.0f ? Duration : 3.5f;
	StartBannerTimer = StartBannerDuration;
	bStartBannerActive = true;
}

void ABattleHUD::ShowVictoryBanner(int32 ExpEarned, int32 GaldEarned, float GradeEarned, const FText& BanterText)
{
	bVictoryActive = true;
	bDefeatActive = false;
	VictoryExp = ExpEarned;
	VictoryGald = GaldEarned;
	VictoryGrade = GradeEarned;
	VictoryBanter = BanterText;
	VictoryTimer = 0.0f;
}

void ABattleHUD::ShowDefeatBanner()
{
	bDefeatActive = true;
	bVictoryActive = false;
	DefeatTimer = 0.0f;
}

// ══════════════════════════════════════════════════════════════════
// ── ToS2 x Arise Procedural Styling Helpers ──────────────────────
// ══════════════════════════════════════════════════════════════════

void ABattleHUD::DrawOrnateBeveledCard(const FVector2D& Pos, const FVector2D& Size, const FLinearColor& BgColor, const FLinearColor& RimColor, float CornerCut)
{
	// Main body rectangle with cut corners
	DrawRect(BgColor, Pos.X + CornerCut, Pos.Y, Size.X - 2.0f * CornerCut, Size.Y);
	DrawRect(BgColor, Pos.X, Pos.Y + CornerCut, CornerCut, Size.Y - 2.0f * CornerCut);
	DrawRect(BgColor, Pos.X + Size.X - CornerCut, Pos.Y + CornerCut, CornerCut, Size.Y - 2.0f * CornerCut);

	// Inner royal glass glow (subtle top highlight gradient)
	DrawRect(FLinearColor(1.0f, 1.0f, 1.0f, 0.04f), Pos.X + CornerCut, Pos.Y + 2.0f, Size.X - 2.0f * CornerCut, Size.Y * 0.4f);

	// Gold filigree beveled outer edge lines
	const float Thickness = 1.8f;
	// Top and bottom edges
	DrawRect(RimColor, Pos.X + CornerCut, Pos.Y, Size.X - 2.0f * CornerCut, Thickness);
	DrawRect(RimColor, Pos.X + CornerCut, Pos.Y + Size.Y - Thickness, Size.X - 2.0f * CornerCut, Thickness);
	// Left and right edges
	DrawRect(RimColor, Pos.X, Pos.Y + CornerCut, Thickness, Size.Y - 2.0f * CornerCut);
	DrawRect(RimColor, Pos.X + Size.X - Thickness, Pos.Y + CornerCut, Thickness, Size.Y - 2.0f * CornerCut);

	// Diagonal corner steps (45-degree bevel bevel emulation)
	for (float step = 0; step < CornerCut; step += 1.5f)
	{
		DrawRect(RimColor, Pos.X + CornerCut - step, Pos.Y + step, 1.5f, 1.5f);
		DrawRect(RimColor, Pos.X + Size.X - CornerCut + step, Pos.Y + step, 1.5f, 1.5f);
		DrawRect(RimColor, Pos.X + CornerCut - step, Pos.Y + Size.Y - step, 1.5f, 1.5f);
		DrawRect(RimColor, Pos.X + Size.X - CornerCut + step, Pos.Y + Size.Y - step, 1.5f, 1.5f);
	}
}

void ABattleHUD::DrawFiligreeBorder(const FVector2D& Pos, const FVector2D& Size, const FLinearColor& GoldColor)
{
	// Ornate corner gem brackets
	const float CornerLen = 14.0f;
	const float Thick = 2.0f;

	// Top-Left
	DrawRect(GoldColor, Pos.X - 2.0f, Pos.Y - 2.0f, CornerLen, Thick);
	DrawRect(GoldColor, Pos.X - 2.0f, Pos.Y - 2.0f, Thick, CornerLen);
	// Top-Right
	DrawRect(GoldColor, Pos.X + Size.X - CornerLen + 2.0f, Pos.Y - 2.0f, CornerLen, Thick);
	DrawRect(GoldColor, Pos.X + Size.X - Thick + 2.0f, Pos.Y - 2.0f, Thick, CornerLen);
	// Bottom-Left
	DrawRect(GoldColor, Pos.X - 2.0f, Pos.Y + Size.Y - Thick + 2.0f, CornerLen, Thick);
	DrawRect(GoldColor, Pos.X - 2.0f, Pos.Y + Size.Y - CornerLen + 2.0f, Thick, CornerLen);
	// Bottom-Right
	DrawRect(GoldColor, Pos.X + Size.X - CornerLen + 2.0f, Pos.Y + Size.Y - Thick + 2.0f, CornerLen, Thick);
	DrawRect(GoldColor, Pos.X + Size.X - Thick + 2.0f, Pos.Y + Size.Y - CornerLen + 2.0f, Thick, CornerLen);
}

void ABattleHUD::DrawDiamondPip(const FVector2D& CenterPos, float Radius, const FLinearColor& FillColor, const FLinearColor& BorderColor)
{
	// Diamond rasterization
	const int32 Steps = FMath::RoundToInt(Radius);
	for (int32 i = 0; i <= Steps; ++i)
	{
		const float Span = (1.0f - (float)i / Steps) * Radius;
		DrawRect(FillColor, CenterPos.X - Span, CenterPos.Y - Radius + i, Span * 2.0f, 1.0f);
		DrawRect(FillColor, CenterPos.X - Span, CenterPos.Y + Radius - i, Span * 2.0f, 1.0f);
	}

	// Diamond metallic border
	for (int32 i = 0; i <= Steps; ++i)
	{
		const float Span = (1.0f - (float)i / Steps) * Radius;
		DrawRect(BorderColor, CenterPos.X - Span, CenterPos.Y - Radius + i, 1.5f, 1.0f);
		DrawRect(BorderColor, CenterPos.X + Span - 1.5f, CenterPos.Y - Radius + i, 1.5f, 1.0f);
		DrawRect(BorderColor, CenterPos.X - Span, CenterPos.Y + Radius - i, 1.5f, 1.0f);
		DrawRect(BorderColor, CenterPos.X + Span - 1.5f, CenterPos.Y + Radius - i, 1.5f, 1.0f);
	}
}

void ABattleHUD::DrawElementalGrid(const FVector2D& CenterPos, float Radius)
{
	// Symphonia 2 Elemental Grid Wheel
	// Dominant Element gets the large central orb, minor elements orbit
	auto GetElementColor = [](EElement E) -> FLinearColor
	{
		switch (E)
		{
		case EElement::Fire:  return FLinearColor(1.0f, 0.35f, 0.1f, 1.0f);
		case EElement::Water: return FLinearColor(0.15f, 0.65f, 1.0f, 1.0f);
		case EElement::Earth: return FLinearColor(0.85f, 0.58f, 0.2f, 1.0f);
		case EElement::Wind:  return FLinearColor(0.2f, 0.95f, 0.45f, 1.0f);
		default:              return FLinearColor(0.9f, 0.85f, 0.3f, 1.0f);
		}
	};

	auto GetElementGlyph = [](EElement E) -> const TCHAR*
	{
		switch (E)
		{
		case EElement::Fire:  return TEXT("🔥");
		case EElement::Water: return TEXT("💧");
		case EElement::Earth: return TEXT("⛰");
		case EElement::Wind:  return TEXT("🌪");
		default:              return TEXT("✦");
		}
	};

	// Outer runic ring
	DrawDiamondPip(CenterPos, Radius, FLinearColor(0.02f, 0.04f, 0.08f, 0.88f), FLinearColor(0.85f, 0.70f, 0.22f, 0.95f));

	// Central Dominant Orb
	const FLinearColor DomColor = GetElementColor(DominantElement);
	DrawDiamondPip(CenterPos, Radius * 0.55f, DomColor, FLinearColor(1.0f, 0.92f, 0.55f, 1.0f));

	// 4 Orbital Satellite Element Pips
	const float OrbitR = Radius * 0.72f;
	const FVector2D Offsets[4] = {
		FVector2D(0.0f, -OrbitR),
		FVector2D(OrbitR, 0.0f),
		FVector2D(0.0f, OrbitR),
		FVector2D(-OrbitR, 0.0f)
	};

	for (int32 i = 0; i < 4; ++i)
	{
		EElement MinorElem = (RecentMinorElements.IsValidIndex(i)) ? RecentMinorElements[i] : (EElement)i;
		FLinearColor MinorCol = GetElementColor(MinorElem);
		DrawDiamondPip(CenterPos + Offsets[i], 4.5f, MinorCol, FLinearColor(0.9f, 0.8f, 0.4f, 0.9f));
	}

	// Element label
	DrawText(GetElementGlyph(DominantElement), FLinearColor::White, CenterPos.X - 5.0f, CenterPos.Y - 7.0f, nullptr, 0.75f);
}

// ══════════════════════════════════════════════════════════════════
// ── 1. ToS2 Party Roster Status Plates (Bottom-Left) ─────────────
// ══════════════════════════════════════════════════════════════════

void ABattleHUD::DrawPartyRoster(ABattleCharacter* Leader)
{
	if (!Leader) return;

	// Metallic Gold & Midnight Navy Palette
	const FLinearColor NavyGlass(0.02f, 0.04f, 0.10f, 0.88f);
	const FLinearColor GoldBorder(0.85f, 0.70f, 0.22f, 0.95f);
	const FLinearColor GoldHighlight(1.0f, 0.92f, 0.55f, 1.0f);
	const FLinearColor SilverBorder(0.55f, 0.60f, 0.72f, 0.80f);

	// Retrieve Active Party Members from PartyCombatManager
	TArray<ABattleCharacter*> Party;
	UPartyCombatManager* PartyMgr = nullptr;
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<ABattleCharacter> It(World); It; ++It)
		{
			if (UPartyCombatManager* Found = It->FindComponentByClass<UPartyCombatManager>())
			{
				PartyMgr = Found;
				break;
			}
		}
	}

	if (PartyMgr && PartyMgr->ActivePartyMembers.Num() > 0)
	{
		Party = PartyMgr->ActivePartyMembers;
	}
	else
	{
		Party.Add(Leader);
	}

	// ── Primary 1P Active Leader Card (Angled & Prominent) ──
	const float LeaderX = 35.0f;
	const float LeaderY = Canvas->SizeY - 165.0f;
	const float LeaderW = 310.0f;
	const float LeaderH = 125.0f;

	// Overlimit Golden Blaze or Standard Filigree Rim
	FLinearColor RimCol = Leader->OverlimitState.bIsActive ? GoldHighlight : GoldBorder;
	DrawOrnateBeveledCard(FVector2D(LeaderX, LeaderY), FVector2D(LeaderW, LeaderH), NavyGlass, RimCol, 8.0f);
	DrawFiligreeBorder(FVector2D(LeaderX, LeaderY), FVector2D(LeaderW, LeaderH), RimCol);

	// ToS2 "1P" Emblem Badge (Red/Gold polygon)
	DrawOrnateBeveledCard(FVector2D(LeaderX + 8.0f, LeaderY + 6.0f), FVector2D(34.0f, 20.0f), FLinearColor(0.75f, 0.1f, 0.1f, 0.95f), GoldHighlight, 3.0f);
	DrawText(TEXT("1P"), FLinearColor::White, LeaderX + 16.0f, LeaderY + 9.0f, nullptr, 0.85f);

	// Character Title / Profile
	FString NameStr = Leader->AdventurerProfileID.IsNone() ? TEXT("EMIL CASTAGNIER") : Leader->AdventurerProfileID.ToString().ToUpper();
	if (Leader->OverlimitState.bIsActive)
	{
		NameStr = FString::Printf(TEXT("★ %s [OVERLIMIT LV%d] ★"), *NameStr, Leader->OverlimitState.OverlimitLevel);
		DrawText(NameStr, GoldHighlight, LeaderX + 48.0f, LeaderY + 8.0f, nullptr, 1.0f);
	}
	else if (Leader->bCanCounterEdge)
	{
		DrawText(TEXT("⚡ COUNTER EDGE READY! ⚡"), FLinearColor(0.2f, 1.0f, 1.0f, 1.0f), LeaderX + 48.0f, LeaderY + 8.0f, nullptr, 0.95f);
	}
	else
	{
		DrawText(NameStr, GoldHighlight, LeaderX + 48.0f, LeaderY + 8.0f, nullptr, 0.95f);
	}

	// ── Segmented HP Bar (ToS2 Emerald -> Crimson) ──
	const float BarX = LeaderX + 16.0f;
	const float BarW = LeaderW - 68.0f; // Leave space for Elemental Grid wheel
	const float HPPercent = FMath::Clamp(Leader->CurrentHP / FMath::Max(1.0f, Leader->GetEffectiveMaxHP()), 0.0f, 1.0f);
	const float HPY = LeaderY + 32.0f;
	const float BarH = 14.0f;

	// HP Track & Bevel Frame
	DrawRect(FLinearColor(0.18f, 0.04f, 0.04f, 0.9f), BarX, HPY, BarW, BarH);
	FLinearColor HPFillCol = (HPPercent > 0.35f) ? FLinearColor(0.12f, 0.85f, 0.35f, 1.0f) : FLinearColor(0.95f, 0.2f, 0.15f, 1.0f);
	DrawRect(HPFillCol, BarX, HPY, BarW * HPPercent, BarH);
	DrawRect(GoldBorder, BarX, HPY, BarW, 1.2f);
	DrawRect(GoldBorder, BarX, HPY + BarH - 1.2f, BarW, 1.2f);

	FString HPStr = FString::Printf(TEXT("HP  %d / %d"), FMath::RoundToInt(Leader->CurrentHP), FMath::RoundToInt(Leader->GetEffectiveMaxHP()));
	DrawText(HPStr, FLinearColor::White, BarX + 6.0f, HPY + 1.0f, nullptr, 0.80f);

	// ── Segmented TP Bar (ToS2 Sapphire / Cyan) ──
	const float TPPercent = FMath::Clamp(Leader->CurrentTP / FMath::Max(1.0f, Leader->GetEffectiveMaxTP()), 0.0f, 1.0f);
	const float TPY = LeaderY + 52.0f;
	DrawRect(FLinearColor(0.04f, 0.12f, 0.25f, 0.9f), BarX, TPY, BarW, BarH);
	DrawRect(FLinearColor(0.0f, 0.65f, 1.0f, 1.0f), BarX, TPY, BarW * TPPercent, BarH);
	DrawRect(GoldBorder, BarX, TPY, BarW, 1.2f);
	DrawRect(GoldBorder, BarX, TPY + BarH - 1.2f, BarW, 1.2f);

	FString TPStr = FString::Printf(TEXT("TP  %d / %d"), FMath::RoundToInt(Leader->CurrentTP), FMath::RoundToInt(Leader->GetEffectiveMaxTP()));
	DrawText(TPStr, FLinearColor::White, BarX + 6.0f, TPY + 1.0f, nullptr, 0.80f);

	// ── Tales of Arise Diamond AG Pips ──
	const float AGY = LeaderY + 77.0f;
	const int32 MaxPips = FMath::Clamp(FMath::RoundToInt(Leader->MaxAG), 1, 6);
	const float PipSpacing = 22.0f;
	for (int32 i = 0; i < MaxPips; ++i)
	{
		const float PipFill = FMath::Clamp(Leader->CurrentAG - i, 0.0f, 1.0f);
		FVector2D PipPos(BarX + 12.0f + i * PipSpacing, AGY + 8.0f);
		FLinearColor PipCol = (PipFill >= 1.0f) ?
			(Leader->OverlimitState.bIsActive ? GoldHighlight : FLinearColor(0.15f, 0.95f, 0.75f, 1.0f)) :
			FLinearColor(0.12f, 0.15f, 0.22f, 0.75f);
		DrawDiamondPip(PipPos, 7.5f, PipCol, GoldBorder);
	}
	DrawText(TEXT("AG"), FLinearColor(0.85f, 0.95f, 0.9f, 0.95f), BarX + MaxPips * PipSpacing + 16.0f, AGY + 2.0f, nullptr, 0.78f);

	// ── Overlimit Burst Gauge (ToS2 / Arise Bottom Gold Track) ──
	const float OLPercent = FMath::Clamp(Leader->OverlimitState.CurrentGauge / FMath::Max(1.0f, Leader->OverlimitState.MaxGauge), 0.0f, 1.0f);
	DrawRect(FLinearColor(0.12f, 0.08f, 0.02f, 0.8f), LeaderX + 8.0f, LeaderY + LeaderH - 12.0f, LeaderW - 16.0f, 5.0f);
	if (OLPercent > 0.0f)
	{
		DrawRect(FLinearColor(1.0f, 0.85f, 0.15f, 0.95f), LeaderX + 8.0f, LeaderY + LeaderH - 12.0f, (LeaderW - 16.0f) * OLPercent, 5.0f);
	}

	// ── Tales of Symphonia 2 Elemental Grid Wheel (Right of Leader Card) ──
	DrawElementalGrid(FVector2D(LeaderX + LeaderW - 28.0f, LeaderY + 52.0f), 22.0f);

	// ── Companion Mini Status Plates (2P, 3P, etc. to the right of Leader) ──
	float CompanionX = LeaderX + LeaderW + 16.0f;
	const float CompW = 165.0f;
	const float CompH = 100.0f;
	const float CompY = Canvas->SizeY - 140.0f;

	int32 PlayerSlotIndex = 2;
	for (ABattleCharacter* Companion : Party)
	{
		if (Companion == Leader || !Companion) continue;

		// Companion Card
		DrawOrnateBeveledCard(FVector2D(CompanionX, CompY), FVector2D(CompW, CompH), NavyGlass, SilverBorder, 6.0f);

		// 2P / 3P Slot Badge
		FString SlotTag = FString::Printf(TEXT("%dP"), PlayerSlotIndex);
		DrawOrnateBeveledCard(FVector2D(CompanionX + 6.0f, CompY + 5.0f), FVector2D(24.0f, 16.0f), FLinearColor(0.2f, 0.35f, 0.75f, 0.95f), SilverBorder, 2.0f);
		DrawText(SlotTag, FLinearColor::White, CompanionX + 10.0f, CompY + 6.0f, nullptr, 0.72f);

		// Name / Class Role
		FString CompName = TEXT("MARTA LUALDI");
		if (Companion->AdventurerProfileID == FName(TEXT("Companion_Vanguard"))) CompName = TEXT("RICHTER (SWORD)");
		else if (Companion->AdventurerProfileID == FName(TEXT("Companion_Mage"))) CompName = TEXT("MARTA (HEALER)");
		else if (!Companion->AdventurerProfileID.IsNone()) CompName = Companion->AdventurerProfileID.ToString().ToUpper();
		DrawText(CompName, FLinearColor(0.9f, 0.9f, 0.95f, 1.0f), CompanionX + 34.0f, CompY + 6.0f, nullptr, 0.75f);

		// Companion HP
		const float CompHPPercent = FMath::Clamp(Companion->CurrentHP / FMath::Max(1.0f, Companion->GetEffectiveMaxHP()), 0.0f, 1.0f);
		const float MiniBarW = CompW - 16.0f;
		const float MiniBarH = 10.0f;
		const float CompHPY = CompY + 28.0f;

		DrawRect(FLinearColor(0.18f, 0.04f, 0.04f, 0.9f), CompanionX + 8.0f, CompHPY, MiniBarW, MiniBarH);
		FLinearColor CompHPCol = (CompHPPercent > 0.35f) ? FLinearColor(0.12f, 0.85f, 0.35f, 1.0f) : FLinearColor(0.95f, 0.2f, 0.15f, 1.0f);
		DrawRect(CompHPCol, CompanionX + 8.0f, CompHPY, MiniBarW * CompHPPercent, MiniBarH);
		FString CompHPStr = FString::Printf(TEXT("HP %d"), FMath::RoundToInt(Companion->CurrentHP));
		DrawText(CompHPStr, FLinearColor::White, CompanionX + 12.0f, CompHPY - 1.0f, nullptr, 0.70f);

		// Companion TP
		const float CompTPPercent = FMath::Clamp(Companion->CurrentTP / FMath::Max(1.0f, Companion->GetEffectiveMaxTP()), 0.0f, 1.0f);
		const float CompTPY = CompY + 44.0f;
		DrawRect(FLinearColor(0.04f, 0.12f, 0.25f, 0.9f), CompanionX + 8.0f, CompTPY, MiniBarW, MiniBarH);
		DrawRect(FLinearColor(0.0f, 0.65f, 1.0f, 1.0f), CompanionX + 8.0f, CompTPY, MiniBarW * CompTPPercent, MiniBarH);
		FString CompTPStr = FString::Printf(TEXT("TP %d"), FMath::RoundToInt(Companion->CurrentTP));
		DrawText(CompTPStr, FLinearColor::White, CompanionX + 12.0f, CompTPY - 1.0f, nullptr, 0.70f);

		// Tactic Gambit Indicator
		DrawText(TEXT("AUTO • BALANCED"), FLinearColor(0.7f, 0.85f, 0.8f, 0.85f), CompanionX + 10.0f, CompY + 68.0f, nullptr, 0.70f);

		CompanionX += CompW + 10.0f;
		PlayerSlotIndex++;
	}

	// Leader Switch Hint
	DrawText(TEXT("[Z / D-PAD UP] SWITCH LEADER"), FLinearColor(0.75f, 0.85f, 0.95f, 0.85f), LeaderX + 8.0f, LeaderY - 18.0f, nullptr, 0.80f);
}

// ══════════════════════════════════════════════════════════════════
// ── 2. Artes Shortcut Bar (Bottom-Center - ToS2 Winged Filigree) ─
// ══════════════════════════════════════════════════════════════════

void ABattleHUD::DrawArtesBar(ABattleCharacter* Character)
{
	const float SlotW = 148.0f;
	const float SlotH = 54.0f;
	const float Spacing = 12.0f;
	const float TotalW = 4 * SlotW + 3 * Spacing;
	const float StartX = (Canvas->SizeX - TotalW) * 0.5f;
	const float StartY = Canvas->SizeY - 74.0f;

	const FLinearColor NavyGlass(0.02f, 0.04f, 0.10f, 0.90f);
	const FLinearColor GoldBorder(0.85f, 0.70f, 0.22f, 0.95f);
	const FLinearColor GoldHighlight(1.0f, 0.92f, 0.55f, 1.0f);

	struct FArteSlotInfo
	{
		FString Key;
		FString Name;
		FString ElementStr;
		float TPCost;
		FLinearColor ElementColor;
	};

	const FArteSlotInfo Slots[4] = {
		{ TEXT("[1]"), TEXT("Ignis Spear"), TEXT("Fire"), 12.0f, FLinearColor(1.0f, 0.35f, 0.1f, 1.0f) },
		{ TEXT("[2]"), TEXT("Aqua Surge"), TEXT("Water+Heal"), 15.0f, FLinearColor(0.15f, 0.65f, 1.0f, 1.0f) },
		{ TEXT("[3]"), TEXT("Terra Wall"), TEXT("Earth"), 18.0f, FLinearColor(0.9f, 0.6f, 0.15f, 1.0f) },
		{ TEXT("[4]"), TEXT("Ventus Blade"), TEXT("Wind"), 14.0f, FLinearColor(0.2f, 0.95f, 0.45f, 1.0f) }
	};

	// Center Arte Bar Ornate Wing Header
	DrawOrnateBeveledCard(FVector2D(StartX - 10.0f, StartY - 22.0f), FVector2D(TotalW + 20.0f, 20.0f), FLinearColor(0.04f, 0.06f, 0.14f, 0.88f), GoldBorder, 4.0f);
	DrawText(TEXT("⚔ ARTES & SPIRIT SKILLS ⚔"), GoldHighlight, StartX + TotalW * 0.5f - 95.0f, StartY - 19.0f, nullptr, 0.82f);

	for (int32 i = 0; i < 4; ++i)
	{
		const float X = StartX + i * (SlotW + Spacing);
		const bool bCanAfford = (Character->CurrentTP >= Slots[i].TPCost);

		// ToS2 Winged Beveled Slot
		FLinearColor RimCol = bCanAfford ? GoldBorder : FLinearColor(0.4f, 0.4f, 0.4f, 0.6f);
		DrawOrnateBeveledCard(FVector2D(X, StartY), FVector2D(SlotW, SlotH), NavyGlass, RimCol, 6.0f);

		// Top Element Color Bar & Filigree mount
		FLinearColor ElementCol = bCanAfford ? Slots[i].ElementColor : FLinearColor(0.3f, 0.3f, 0.3f, 0.5f);
		DrawRect(ElementCol, X + 6.0f, StartY + 2.0f, SlotW - 12.0f, 2.5f);

		// Element Gem Diamond Pip
		DrawDiamondPip(FVector2D(X + 14.0f, StartY + 18.0f), 5.5f, ElementCol, GoldHighlight);

		// Key Shortcut & Arte Name
		FLinearColor TextColor = bCanAfford ? FLinearColor::White : FLinearColor(0.55f, 0.55f, 0.55f, 0.7f);
		FString KeyAndName = FString::Printf(TEXT("%s %s"), *Slots[i].Key, *Slots[i].Name);
		DrawText(KeyAndName, TextColor, X + 26.0f, StartY + 10.0f, nullptr, 0.85f);

		// TP Cost & Element Subtext
		FString SubText = FString::Printf(TEXT("%s | %d TP"), *Slots[i].ElementStr, FMath::RoundToInt(Slots[i].TPCost));
		DrawText(SubText, ElementCol, X + 26.0f, StartY + 30.0f, nullptr, 0.75f);
	}
}

// ══════════════════════════════════════════════════════════════════
// ── 3. Target Lock & Enemy Health (ToS2 Runic Reticle) ───────────
// ══════════════════════════════════════════════════════════════════

void ABattleHUD::DrawTargetLock(ABattleCharacter* Character)
{
	if (!Character || !Character->LockedTarget || !Character->LockedTarget->IsAlive())
	{
		return;
	}

	ABattleEnemy* Enemy = Character->LockedTarget;
	const FLinearColor NavyGlass(0.02f, 0.04f, 0.10f, 0.90f);
	const FLinearColor GoldBorder(0.85f, 0.70f, 0.22f, 0.95f);
	const FLinearColor GoldHighlight(1.0f, 0.92f, 0.55f, 1.0f);
	const FLinearColor CrimsonGlow(0.95f, 0.2f, 0.2f, 0.95f);

	// 1. Top-Center Boss/Enemy Header Bar (ToS2 Beveled Plate)
	const float BoxW = 460.0f;
	const float BoxH = 50.0f;
	const float BaseX = (Canvas->SizeX - BoxW) * 0.5f;
	const float BaseY = 28.0f;

	DrawOrnateBeveledCard(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), NavyGlass, CrimsonGlow, 8.0f);
	DrawFiligreeBorder(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), GoldBorder);

	// Enemy Name & Weakness
	FString WeakStr;
	switch (Enemy->WeaknessElement)
	{
	case EElement::Fire:  WeakStr = TEXT("WEAK: FIRE [🔥]"); break;
	case EElement::Water: WeakStr = TEXT("WEAK: WATER [💧]"); break;
	case EElement::Earth: WeakStr = TEXT("WEAK: EARTH [⛰]"); break;
	case EElement::Wind:  WeakStr = TEXT("WEAK: WIND [🌪]"); break;
	}

	FString TitleStr = FString::Printf(TEXT("⚔ %s    %s"), *Enemy->EnemyName.ToString().ToUpper(), *WeakStr);
	DrawText(TitleStr, GoldHighlight, BaseX + 16.0f, BaseY + 6.0f, nullptr, 0.92f);

	// HP Bar
	const float EnemyHPPercent = FMath::Clamp(Enemy->CurrentHP / FMath::Max(1.0f, Enemy->MaxHP), 0.0f, 1.0f);
	const float BarW = BoxW - 32.0f;
	const float BarH = 13.0f;
	DrawRect(FLinearColor(0.25f, 0.04f, 0.04f, 0.9f), BaseX + 16.0f, BaseY + 28.0f, BarW, BarH);
	DrawRect(FLinearColor(0.95f, 0.25f, 0.15f, 1.0f), BaseX + 16.0f, BaseY + 28.0f, BarW * EnemyHPPercent, BarH);
	DrawRect(GoldBorder, BaseX + 16.0f, BaseY + 28.0f, BarW, 1.2f);
	DrawRect(GoldBorder, BaseX + 16.0f, BaseY + 28.0f + BarH - 1.2f, BarW, 1.2f);

	// 2. ToS2 Circular Runic Dial & Range Reticle in World Space
	APlayerController* PC = GetOwningPlayerController();
	if (PC)
	{
		const FVector EnemyLoc = Enemy->GetActorLocation();
		const float Dist = FVector::Dist(Character->GetActorLocation(), EnemyLoc);

		FVector EnemyHeadLoc = EnemyLoc + FVector(0.0f, 0.0f, 65.0f);
		FVector2D ScreenPos;
		if (PC->ProjectWorldLocationToScreen(EnemyHeadLoc, ScreenPos))
		{
			const float ReticleRadius = 32.0f;
			FLinearColor ReticleCol = Enemy->bIsTelegraphing ? CrimsonGlow : GoldBorder;

			// Circular Runic Ring with 4 Cardinal Glyph Diamonds (ToS2 Style)
			DrawDiamondPip(ScreenPos + FVector2D(0.0f, -ReticleRadius), 6.0f, ReticleCol, GoldHighlight); // North
			DrawDiamondPip(ScreenPos + FVector2D(ReticleRadius, 0.0f), 6.0f, ReticleCol, GoldHighlight);  // East
			DrawDiamondPip(ScreenPos + FVector2D(0.0f, ReticleRadius), 6.0f, ReticleCol, GoldHighlight);  // South
			DrawDiamondPip(ScreenPos + FVector2D(-ReticleRadius, 0.0f), 6.0f, ReticleCol, GoldHighlight); // West

			// Corner bracket accents
			DrawRect(ReticleCol, ScreenPos.X - ReticleRadius * 0.7f, ScreenPos.Y - ReticleRadius * 0.7f, 8.0f, 2.0f);
			DrawRect(ReticleCol, ScreenPos.X - ReticleRadius * 0.7f, ScreenPos.Y - ReticleRadius * 0.7f, 2.0f, 8.0f);
			DrawRect(ReticleCol, ScreenPos.X + ReticleRadius * 0.7f - 8.0f, ScreenPos.Y - ReticleRadius * 0.7f, 8.0f, 2.0f);
			DrawRect(ReticleCol, ScreenPos.X + ReticleRadius * 0.7f - 2.0f, ScreenPos.Y - ReticleRadius * 0.7f, 2.0f, 8.0f);
			DrawRect(ReticleCol, ScreenPos.X - ReticleRadius * 0.7f, ScreenPos.Y + ReticleRadius * 0.7f - 2.0f, 8.0f, 2.0f);
			DrawRect(ReticleCol, ScreenPos.X - ReticleRadius * 0.7f, ScreenPos.Y + ReticleRadius * 0.7f - 8.0f, 2.0f, 8.0f);
			DrawRect(ReticleCol, ScreenPos.X + ReticleRadius * 0.7f - 8.0f, ScreenPos.Y + ReticleRadius * 0.7f - 2.0f, 8.0f, 2.0f);
			DrawRect(ReticleCol, ScreenPos.X + ReticleRadius * 0.7f - 2.0f, ScreenPos.Y + ReticleRadius * 0.7f - 8.0f, 2.0f, 8.0f);

			// Range readout
			FString RangeStr = (Dist <= 280.0f) ? TEXT("⚔ [MELEE]") : FString::Printf(TEXT("✦ %d u"), FMath::RoundToInt(Dist));
			FLinearColor RangeColor = (Dist <= 280.0f) ? FLinearColor(0.2f, 1.0f, 0.4f, 1.0f) : GoldHighlight;
			DrawText(RangeStr, RangeColor, ScreenPos.X - 25.0f, ScreenPos.Y + ReticleRadius + 10.0f, nullptr, 0.82f);

			// Telegraph Flash (Alert player to incoming enemy strike)
			if (Enemy->bIsTelegraphing)
			{
				DrawOrnateBeveledCard(FVector2D(ScreenPos.X - 52.0f, ScreenPos.Y - ReticleRadius - 28.0f), FVector2D(104.0f, 20.0f), FLinearColor(0.85f, 0.1f, 0.1f, 0.95f), GoldHighlight, 4.0f);
				DrawText(TEXT("⚠ TELEGRAPH ⚠"), FLinearColor::White, ScreenPos.X - 44.0f, ScreenPos.Y - ReticleRadius - 26.0f, nullptr, 0.78f);
			}

			// Tales of Arise Boost Strike Co-op Finisher Prompt
			if (Enemy->CanBoostStrike())
			{
				DrawOrnateBeveledCard(FVector2D(ScreenPos.X - 70.0f, ScreenPos.Y + ReticleRadius + 30.0f), FVector2D(140.0f, 24.0f), FLinearColor(0.08f, 0.75f, 0.95f, 0.95f), GoldHighlight, 5.0f);
				DrawText(TEXT("★ BOOST STRIKE [SPACE] ★"), FLinearColor::Black, ScreenPos.X - 64.0f, ScreenPos.Y + ReticleRadius + 34.0f, nullptr, 0.82f);
			}
		}
	}
}

// ══════════════════════════════════════════════════════════════════
// ── 4. Combo Counter (ToS2 Bold Beveled Hits Banner) ─────────────
// ══════════════════════════════════════════════════════════════════

void ABattleHUD::DrawComboCounter()
{
	if (ComboHitCount <= 0 || ComboTimer <= 0.0f) return;

	const float Alpha = FMath::Clamp(ComboTimer / 0.5f, 0.0f, 1.0f);
	const float BoxW = 240.0f;
	const float BoxH = 95.0f;
	const float BaseX = Canvas->SizeX - BoxW - 40.0f;
	const float BaseY = Canvas->SizeY * 0.36f;

	const FLinearColor NavyGlass(0.02f, 0.04f, 0.10f, 0.88f * Alpha);
	const FLinearColor GoldBorder(0.85f, 0.70f, 0.22f, 0.95f * Alpha);
	const FLinearColor GoldHighlight(1.0f, 0.92f, 0.55f, 1.0f * Alpha);

	DrawOrnateBeveledCard(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), NavyGlass, GoldBorder, 8.0f);
	DrawFiligreeBorder(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), GoldHighlight);

	// Combo Title Rank
	FString RankTitle = TEXT("");
	FLinearColor TitleColor = FLinearColor::White;
	if (ComboHitCount >= 100) { RankTitle = TEXT("★ LEGENDARY! ★"); TitleColor = FLinearColor(1.0f, 0.2f, 0.85f, Alpha); }
	else if (ComboHitCount >= 75) { RankTitle = TEXT("UNBELIEVABLE!"); TitleColor = FLinearColor(1.0f, 0.35f, 0.2f, Alpha); }
	else if (ComboHitCount >= 50) { RankTitle = TEXT("FANTASTIC!"); TitleColor = GoldHighlight; }
	else if (ComboHitCount >= 25) { RankTitle = TEXT("GREAT!"); TitleColor = FLinearColor(0.2f, 0.85f, 1.0f, Alpha); }
	else if (ComboHitCount >= 10) { RankTitle = TEXT("COOL!"); TitleColor = FLinearColor(0.35f, 1.0f, 0.45f, Alpha); }

	if (!RankTitle.IsEmpty())
	{
		DrawText(RankTitle, TitleColor, BaseX + 20.0f, BaseY - 22.0f, nullptr, 1.15f);
	}

	// Bold Hit Count
	FString HitStr = FString::Printf(TEXT("%d HITS!"), ComboHitCount);
	DrawText(HitStr, GoldHighlight, BaseX + 18.0f, BaseY + 12.0f, nullptr, 1.65f);

	// Total Damage Ticker
	FString DmgStr = FString::Printf(TEXT("+%d DAMAGE"), FMath::RoundToInt(ComboTotalDamage));
	DrawText(DmgStr, FLinearColor(1.0f, 0.45f, 0.2f, Alpha), BaseX + 18.0f, BaseY + 56.0f, nullptr, 1.05f);
}

// ── 5. Victory Banner (Center Screen) ─────────────────────────

void ABattleHUD::DrawVictoryBanner()
{
	const float BoxW = 560.0f;
	const float BoxH = 230.0f;
	const float BaseX = (Canvas->SizeX - BoxW) * 0.5f;
	const float BaseY = (Canvas->SizeY - BoxH) * 0.30f;

	const FLinearColor DarkParchment(0.04f, 0.03f, 0.02f, 0.95f);
	const FLinearColor GoldBorder(0.85f, 0.70f, 0.22f, 1.0f);
	const FLinearColor GoldHighlight(1.0f, 0.92f, 0.55f, 1.0f);

	DrawOrnateBeveledCard(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), DarkParchment, GoldBorder, 10.0f);
	DrawFiligreeBorder(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), GoldHighlight);

	// Header
	DrawText(TEXT("★ VICTORY ★"), GoldHighlight, BaseX + 180.0f, BaseY + 18.0f, nullptr, 1.9f);

	// Rewards
	FString ExpStr = FString::Printf(TEXT("EXPERIENCE ACQUIRED:  +%d EXP"), VictoryExp);
	DrawText(ExpStr, FLinearColor(0.3f, 0.9f, 1.0f, 1.0f), BaseX + 50.0f, BaseY + 70.0f, nullptr, 1.15f);

	FString GaldStr = FString::Printf(TEXT("GALD OBTAINED:        +%d G"), VictoryGald);
	DrawText(GaldStr, FLinearColor(1.0f, 0.8f, 0.3f, 1.0f), BaseX + 50.0f, BaseY + 102.0f, nullptr, 1.15f);

	// Grade Tally
	FString GradeStr = FString::Printf(TEXT("GRADE EARNED:         +%0.2f Pt"), VictoryGrade);
	DrawText(GradeStr, GoldHighlight, BaseX + 50.0f, BaseY + 134.0f, nullptr, 1.15f);

	// Status note
	DrawText(TEXT("Returning to Overworld..."), FLinearColor(0.85f, 0.85f, 0.85f, 0.9f), BaseX + 175.0f, BaseY + 185.0f, nullptr, 0.95f);

	// Party Victory Banter Box
	if (!VictoryBanter.IsEmpty())
	{
		const float BanterW = 640.0f;
		const float BanterH = 68.0f;
		const float BanterX = (Canvas->SizeX - BanterW) * 0.5f;
		const float BanterY = BaseY + BoxH + 20.0f;

		DrawOrnateBeveledCard(FVector2D(BanterX, BanterY), FVector2D(BanterW, BanterH), FLinearColor(0.03f, 0.05f, 0.12f, 0.94f), GoldBorder, 6.0f);
		DrawText(VictoryBanter.ToString(), FLinearColor(1.0f, 0.95f, 0.85f, 1.0f), BanterX + 24.0f, BanterY + 24.0f, nullptr, 1.05f);
	}
}

// ── 6. Defeat Banner ──────────────────────────────────────────

void ABattleHUD::DrawDefeatBanner()
{
	const float BoxW = 440.0f;
	const float BoxH = 130.0f;
	const float BaseX = (Canvas->SizeX - BoxW) * 0.5f;
	const float BaseY = (Canvas->SizeY - BoxH) * 0.38f;

	DrawOrnateBeveledCard(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), FLinearColor(0.12f, 0.02f, 0.02f, 0.94f), FLinearColor(0.9f, 0.15f, 0.15f, 1.0f), 8.0f);
	DrawFiligreeBorder(FVector2D(BaseX, BaseY), FVector2D(BoxW, BoxH), FLinearColor(1.0f, 0.3f, 0.3f, 1.0f));

	DrawText(TEXT("BATTLE DEFEATED..."), FLinearColor(0.95f, 0.2f, 0.2f, 1.0f), BaseX + 95.0f, BaseY + 28.0f, nullptr, 1.6f);
	DrawText(TEXT("Retreating to safety..."), FLinearColor(0.85f, 0.85f, 0.85f, 0.9f), BaseX + 130.0f, BaseY + 80.0f, nullptr, 1.0f);
}

// ── 7. Start Banner ───────────────────────────────────────────

void ABattleHUD::DrawStartBanner()
{
	if (!bStartBannerActive || StartBannerTimer <= 0.0f) return;

	float DeltaTime = GetWorld() ? GetWorld()->GetDeltaSeconds() : 0.016f;
	StartBannerTimer -= DeltaTime;
	if (StartBannerTimer <= 0.0f)
	{
		bStartBannerActive = false;
		return;
	}

	const float Elapsed = StartBannerDuration - StartBannerTimer;
	float Alpha = 1.0f;
	if (Elapsed < 0.5f) Alpha = Elapsed / 0.5f;
	else if (StartBannerTimer < 0.6f) Alpha = StartBannerTimer / 0.6f;

	const float BannerW = 620.0f;
	const float BannerH = 80.0f;
	const float BaseX = (Canvas->SizeX - BannerW) * 0.5f;
	const float BaseY = Canvas->SizeY * 0.18f;

	DrawRect(FLinearColor(0.02f, 0.04f, 0.1f, 0.88f * Alpha), BaseX, BaseY, BannerW, BannerH);
	DrawRect(FLinearColor(1.0f, 0.35f, 0.15f, 0.95f * Alpha), BaseX, BaseY, BannerW, 3.0f);
	DrawRect(FLinearColor(1.0f, 0.35f, 0.15f, 0.95f * Alpha), BaseX, BaseY + BannerH - 3.0f, BannerW, 3.0f);

	FString TitleStr = StartBannerTitle.ToString();
	FString SubStr = StartBannerSubtitle.ToString();

	DrawText(TitleStr, FLinearColor(1.0f, 0.9f, 0.2f, Alpha), BaseX + 35.0f, BaseY + 14.0f, nullptr, 1.45f);
	DrawText(SubStr, FLinearColor(0.85f, 0.85f, 0.85f, Alpha * 0.9f), BaseX + 35.0f, BaseY + 46.0f, nullptr, 0.95f);
}

void ABattleHUD::DrawEscapeMeter(ABattleCharacter* Character)
{
	if (!Character || Character->EscapeTimer <= 0.0f) return;

	const float EscapePct = FMath::Clamp(Character->EscapeTimer / Character->EscapeDuration, 0.0f, 1.0f);
	const float MeterW = 340.0f;
	const float MeterH = 22.0f;
	const float BaseX = (Canvas->SizeX - MeterW) * 0.5f;
	const float BaseY = Canvas->SizeY * 0.82f;

	// Background card
	DrawRect(FLinearColor(0.05f, 0.05f, 0.08f, 0.85f), BaseX - 10.0f, BaseY - 24.0f, MeterW + 20.0f, MeterH + 34.0f);

	// Border
	DrawRect(FLinearColor(0.9f, 0.8f, 0.2f, 0.9f), BaseX - 2.0f, BaseY - 2.0f, MeterW + 4.0f, MeterH + 4.0f);
	DrawRect(FLinearColor(0.08f, 0.08f, 0.1f, 1.0f), BaseX, BaseY, MeterW, MeterH);

	// Fill bar (Glowing Emerald -> Gold when ready)
	FLinearColor FillCol = (EscapePct >= 1.0f) ? FLinearColor(0.2f, 1.0f, 0.3f, 1.0f) : FLinearColor(0.95f, 0.75f, 0.15f, 1.0f);
	DrawRect(FillCol, BaseX, BaseY, MeterW * EscapePct, MeterH);

	// Label
	DrawText(TEXT("ESCAPING... (HOLD TO FLEE)"), FLinearColor(1.0f, 0.95f, 0.7f, 1.0f), BaseX + 25.0f, BaseY - 20.0f, nullptr, 0.95f);
}
