// Copyright Epic Games, Inc. All Rights Reserved.
// OverworldHUD.h — JRPG Exploration HUD (Mini-map, Compass, Location Banner, Flight Telemetry)

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "OverworldHUD.generated.h"

class AOverworldCharacter;
class ATownZone;

UCLASS()
class ISEKAIVILLAGE_API AOverworldHUD : public AHUD
{
	GENERATED_BODY()

public:
	AOverworldHUD();
	virtual void DrawHUD() override;

	/** Trigger a location banner popup on screen */
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowLocationBanner(const FText& Title, const FText& Subtitle, float Duration = 4.0f);

	/** Set active interaction prompt */
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void SetInteractionPrompt(const FText& PromptText, bool bShow);

private:
	void DrawLocationBanner();
	void DrawMiniMapAndCompass(AOverworldCharacter* Character);
	void DrawFlightTelemetry(AOverworldCharacter* Character);
	void DrawInteractionPrompt();

	// ── Location Banner Animation State ──
	FText BannerTitle;
	FText BannerSubtitle;
	float BannerTimer = 0.0f;
	float BannerTotalDuration = 4.0f;
	bool bBannerActive = false;

	// ── Interaction Prompt ──
	FText CurrentPrompt;
	bool bShowPrompt = false;

	// ── Discovered POIs Cache ──
	UPROPERTY(Transient)
	TArray<TWeakObjectPtr<ATownZone>> CachedTownZones;
	float LastZoneSearchTime = -10.0f;
	void RefreshCachedTownZones();
};
