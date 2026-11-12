// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageHUD.h — Village Hub HUD (Dialogue Window, Location Banner, Interaction Prompts)

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "IsekaiVillageHUD.generated.h"

class AVillageNPC;
class ATownZone;
class AIsekaiVillageCharacter;

UCLASS()
class ISEKAIVILLAGE_API AIsekaiVillageHUD : public AHUD
{
	GENERATED_BODY()

public:
	AIsekaiVillageHUD();
	virtual void DrawHUD() override;

	/** Trigger a location banner popup on screen */
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void ShowLocationBanner(const FText& Title, const FText& Subtitle, float Duration = 4.0f);

	/** Set active interaction prompt */
	UFUNCTION(BlueprintCallable, Category = "HUD")
	void SetInteractionPrompt(const FText& PromptText, bool bShow);

	// ── JRPG Dialogue System ──
	UFUNCTION(BlueprintCallable, Category = "Dialogue")
	void StartDialogue(const FText& SpeakerName, const TArray<FText>& Lines, const FText& SpeakerRole = FText::GetEmpty());

	UFUNCTION(BlueprintCallable, Category = "Dialogue")
	void AdvanceDialogue();

	UFUNCTION(BlueprintCallable, Category = "Dialogue")
	void CloseDialogue();

	UFUNCTION(BlueprintPure, Category = "Dialogue")
	bool IsDialogueOpen() const { return bDialogueOpen; }

private:
	void DrawLocationBanner();
	void DrawInteractionPrompt();
	void DrawDialogueBox();

	// ── Location Banner State ──
	FText BannerTitle;
	FText BannerSubtitle;
	float BannerTimer = 0.0f;
	float BannerTotalDuration = 4.0f;
	bool bBannerActive = false;

	// ── Interaction Prompt State ──
	FText CurrentPrompt;
	bool bShowPrompt = false;

	// ── Dialogue State ──
	bool bDialogueOpen = false;
	FText CurrentSpeaker;
	FText CurrentSpeakerRole;
	TArray<FText> ActiveDialogueLines;
	int32 CurrentLineIndex = 0;
	float DialogueAnimTime = 0.0f;

	// ── Cached Actors (Plain C++ Weak Pointers to prevent UHT reflection crashes) ──
	TArray<TWeakObjectPtr<ATownZone>> CachedTownZones;
	TArray<TWeakObjectPtr<AVillageNPC>> CachedNPCs;

	float LastCacheSearchTime = -10.0f;
	void RefreshCachedActors();
};
