// Copyright Epic Games, Inc. All Rights Reserved.
// BattleHUD.h — LMBS Real-Time Combat HUD (HP/TP, Combo Ticker, Artes Bar, Target Reticle, Victory Banner)

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "IsekaiVillageTypes.h"
#include "BattleHUD.generated.h"

class ABattleCharacter;
class ABattleEnemy;

UCLASS()
class ISEKAIVILLAGE_API ABattleHUD : public AHUD
{
	GENERATED_BODY()

public:
	ABattleHUD();
	virtual void DrawHUD() override;

	/** Called by BattleCharacter when hitting an enemy */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void RegisterComboHit(float Damage);

	/** Called by BattleGameMode on victory */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ShowVictoryBanner(int32 ExpEarned, int32 GaldEarned, float GradeEarned = 2.5f, const FText& BanterText = FText::GetEmpty());

	/** Called by BattleGameMode on player defeat */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ShowDefeatBanner();

	/** Called at the start of battle */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void ShowBattleStartBanner(const FText& Title, const FText& Subtitle, float Duration = 3.5f);

	/** Update elemental field dominance (Tales of Symphonia 2 Elemental Grid) */
	UFUNCTION(BlueprintCallable, Category = "Combat|Element")
	void RegisterElementCast(EElement Element);

private:
	// ── ToS2 x Arise Procedural Styling Helpers ──
	void DrawOrnateBeveledCard(const FVector2D& Pos, const FVector2D& Size, const FLinearColor& BgColor, const FLinearColor& RimColor, float CornerCut = 8.0f);
	void DrawFiligreeBorder(const FVector2D& Pos, const FVector2D& Size, const FLinearColor& GoldColor);
	void DrawDiamondPip(const FVector2D& CenterPos, float Size, const FLinearColor& FillColor, const FLinearColor& BorderColor);
	void DrawElementalGrid(const FVector2D& CenterPos, float Radius);

	// ── HUD Subsystems ──
	void DrawStartBanner();
	void DrawPartyRoster(ABattleCharacter* Leader);
	void DrawArtesBar(ABattleCharacter* Character);
	void DrawTargetLock(ABattleCharacter* Character);
	void DrawComboCounter();
	void DrawVictoryBanner();
	void DrawDefeatBanner();
	void DrawEscapeMeter(ABattleCharacter* Character);

	// ── Combo Counter State ──
	int32 ComboHitCount = 0;
	float ComboTotalDamage = 0.0f;
	float ComboTimer = 0.0f;
	const float MaxComboDuration = 2.5f;

	// ── Tales of Symphonia 2 Elemental Grid State ──
	EElement DominantElement = EElement::Fire;
	TArray<EElement> RecentMinorElements;

	// ── Victory Sequence State ──
	bool bVictoryActive = false;
	int32 VictoryExp = 0;
	int32 VictoryGald = 0;
	float VictoryGrade = 2.5f;
	FText VictoryBanter;
	float VictoryTimer = 0.0f;

	// ── Defeat Sequence State ──
	bool bDefeatActive = false;
	float DefeatTimer = 0.0f;

	// ── Start Banner State ──
	bool bStartBannerActive = false;
	FText StartBannerTitle;
	FText StartBannerSubtitle;
	float StartBannerTimer = 0.0f;
	float StartBannerDuration = 3.5f;
};

