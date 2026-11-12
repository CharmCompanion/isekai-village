// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageHUD.cpp — Village Hub HUD (Dialogue Window, Location Banner, Interaction Prompts)

#include "IsekaiVillageHUD.h"
#include "IsekaiVillageCharacter.h"
#include "VillageNPC.h"
#include "TownZone.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

AIsekaiVillageHUD::AIsekaiVillageHUD()
{
}

void AIsekaiVillageHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas) return;

	float DeltaTime = GetWorld() ? GetWorld()->GetDeltaSeconds() : 0.016f;

	APawn* Pawn = GetOwningPawn();
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(Pawn);
	if (!Character) return;

	// Check nearby interactions if dialogue is not open
	if (!bDialogueOpen)
	{
		RefreshCachedActors();
		bool bFoundInteraction = false;
		const FVector PlayerLoc = Character->GetActorLocation();

		// 1. Check nearby NPCs first (highest priority)
		for (const TWeakObjectPtr<AVillageNPC>& NPCPtr : CachedNPCs)
		{
			if (AVillageNPC* NPC = NPCPtr.Get())
			{
				if (NPC->IsPlayerInRange(PlayerLoc))
				{
					CurrentPrompt = FText::Format(NSLOCTEXT("HUD", "TalkPrompt", "Press [E] to Talk to {0}"), NPC->NPCName);
					bShowPrompt = true;
					bFoundInteraction = true;
					break;
				}
			}
		}

		// 2. Check nearby Town Zones
		if (!bFoundInteraction)
		{
			for (const TWeakObjectPtr<ATownZone>& ZonePtr : CachedTownZones)
			{
				if (ATownZone* Zone = ZonePtr.Get())
				{
					float Dist = FVector::Dist2D(PlayerLoc, Zone->GetActorLocation());
					if (Dist <= 800.0f)
					{
						FText LocName = Zone->LocationName.IsEmpty() ? FText::FromString(TEXT("Destination")) : Zone->LocationName;
						CurrentPrompt = FText::Format(NSLOCTEXT("HUD", "EnterPrompt", "Press [E] to Enter {0}"), LocName);
						bShowPrompt = true;
						bFoundInteraction = true;
						break;
					}
				}
			}
		}

		if (!bFoundInteraction && bShowPrompt)
		{
			bShowPrompt = false;
		}
	}
	else
	{
		bShowPrompt = false;
		DialogueAnimTime += DeltaTime;
	}

	// Render layers
	DrawLocationBanner();
	DrawInteractionPrompt();

	if (bDialogueOpen)
	{
		DrawDialogueBox();
	}
}

void AIsekaiVillageHUD::RefreshCachedActors()
{
	float CurrentTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
	if (CurrentTime - LastCacheSearchTime > 2.5f || (CachedTownZones.Num() == 0 && CachedNPCs.Num() == 0))
	{
		LastCacheSearchTime = CurrentTime;
		CachedTownZones.Empty();
		CachedNPCs.Empty();

		for (TActorIterator<ATownZone> It(GetWorld()); It; ++It)
		{
			CachedTownZones.Add(*It);
		}
		for (TActorIterator<AVillageNPC> It(GetWorld()); It; ++It)
		{
			CachedNPCs.Add(*It);
		}
	}
}

void AIsekaiVillageHUD::ShowLocationBanner(const FText& Title, const FText& Subtitle, float Duration)
{
	BannerTitle = Title;
	BannerSubtitle = Subtitle;
	BannerTotalDuration = Duration > 0.0f ? Duration : 4.0f;
	BannerTimer = BannerTotalDuration;
	bBannerActive = true;
}

void AIsekaiVillageHUD::SetInteractionPrompt(const FText& PromptText, bool bShow)
{
	CurrentPrompt = PromptText;
	bShowPrompt = bShow;
}

void AIsekaiVillageHUD::StartDialogue(const FText& SpeakerName, const TArray<FText>& Lines, const FText& SpeakerRole)
{
	CurrentSpeaker = SpeakerName;
	CurrentSpeakerRole = SpeakerRole;
	ActiveDialogueLines = Lines;
	CurrentLineIndex = 0;
	DialogueAnimTime = 0.0f;
	bDialogueOpen = (ActiveDialogueLines.Num() > 0);
}

void AIsekaiVillageHUD::AdvanceDialogue()
{
	if (!bDialogueOpen) return;

	CurrentLineIndex++;
	DialogueAnimTime = 0.0f;

	if (CurrentLineIndex >= ActiveDialogueLines.Num())
	{
		CloseDialogue();
	}
}

void AIsekaiVillageHUD::CloseDialogue()
{
	bDialogueOpen = false;
	CurrentLineIndex = 0;
	ActiveDialogueLines.Empty();
}

// ── 1. Dialogue Window (JRPG Tales Style) ─────────────────────

void AIsekaiVillageHUD::DrawDialogueBox()
{
	if (!bDialogueOpen || !ActiveDialogueLines.IsValidIndex(CurrentLineIndex)) return;

	const float BoxW = FMath::Clamp(Canvas->SizeX * 0.76f, 680.0f, 960.0f);
	const float BoxH = 150.0f;
	const float BaseX = (Canvas->SizeX - BoxW) * 0.5f;
	const float BaseY = Canvas->SizeY - BoxH - 45.0f;

	// Dark royal blue backdrop
	DrawRect(FLinearColor(0.02f, 0.04f, 0.12f, 0.94f), BaseX, BaseY, BoxW, BoxH);

	// Gold ornate border
	const FLinearColor GoldBorder(1.0f, 0.82f, 0.28f, 1.0f);
	DrawRect(GoldBorder, BaseX, BaseY, BoxW, 3.0f);
	DrawRect(GoldBorder, BaseX, BaseY + BoxH - 3.0f, BoxW, 3.0f);
	DrawRect(GoldBorder, BaseX, BaseY, 3.0f, BoxH);
	DrawRect(GoldBorder, BaseX + BoxW - 3.0f, BaseY, 3.0f, BoxH);

	// Speaker Nameplate Box
	const float NameW = 260.0f;
	const float NameH = 34.0f;
	const float NameX = BaseX + 16.0f;
	const float NameY = BaseY - NameH + 4.0f;

	DrawRect(FLinearColor(0.06f, 0.09f, 0.22f, 0.96f), NameX, NameY, NameW, NameH);
	DrawRect(GoldBorder, NameX, NameY, NameW, 2.0f);
	DrawRect(GoldBorder, NameX, NameY, 2.0f, NameH);
	DrawRect(GoldBorder, NameX + NameW - 2.0f, NameY, 2.0f, NameH);

	FString SpeakerText = CurrentSpeaker.ToString();
	if (!CurrentSpeakerRole.IsEmpty())
	{
		SpeakerText += FString::Printf(TEXT("  [%s]"), *CurrentSpeakerRole.ToString());
	}
	DrawText(SpeakerText, FLinearColor(1.0f, 0.92f, 0.4f, 1.0f), NameX + 12.0f, NameY + 7.0f, nullptr, 1.05f);

	// Dialogue Line Text
	FString CurrentLine = ActiveDialogueLines[CurrentLineIndex].ToString();
	DrawText(CurrentLine, FLinearColor::White, BaseX + 28.0f, BaseY + 24.0f, nullptr, 1.15f);

	// Next indicator / Prompt
	const bool bIsLastLine = (CurrentLineIndex >= ActiveDialogueLines.Num() - 1);
	FString NextPromptStr = bIsLastLine ? TEXT("▼ [E] Close") : TEXT("▼ [E] Continue");

	// Gentle blink
	float Pulse = 0.5f + 0.5f * FMath::Sin(DialogueAnimTime * 5.0f);
	FLinearColor PromptColor(1.0f, 0.85f, 0.3f, 0.4f + 0.6f * Pulse);
	DrawText(NextPromptStr, PromptColor, BaseX + BoxW - 140.0f, BaseY + BoxH - 28.0f, nullptr, 0.95f);
}

// ── 2. Location Banner ────────────────────────────────────────

void AIsekaiVillageHUD::DrawLocationBanner()
{
	if (!bBannerActive || BannerTimer <= 0.0f) return;

	float DeltaTime = GetWorld() ? GetWorld()->GetDeltaSeconds() : 0.016f;
	BannerTimer -= DeltaTime;
	if (BannerTimer <= 0.0f)
	{
		bBannerActive = false;
		return;
	}

	const float Elapsed = BannerTotalDuration - BannerTimer;
	float Alpha = 1.0f;
	if (Elapsed < 0.6f) Alpha = Elapsed / 0.6f;
	else if (BannerTimer < 0.8f) Alpha = BannerTimer / 0.8f;

	const float BannerW = 600.0f;
	const float BannerH = 75.0f;
	const float BaseX = (Canvas->SizeX - BannerW) * 0.5f;
	const float BaseY = Canvas->SizeY * 0.16f;

	DrawRect(FLinearColor(0.02f, 0.04f, 0.08f, 0.82f * Alpha), BaseX, BaseY, BannerW, BannerH);
	DrawRect(FLinearColor(1.0f, 0.85f, 0.3f, 0.9f * Alpha), BaseX, BaseY, BannerW, 2.0f);
	DrawRect(FLinearColor(1.0f, 0.85f, 0.3f, 0.9f * Alpha), BaseX, BaseY + BannerH - 2.0f, BannerW, 2.0f);

	FString TitleStr = BannerTitle.ToString();
	FString SubStr = BannerSubtitle.ToString();

	DrawText(TitleStr, FLinearColor(1.0f, 0.92f, 0.4f, Alpha), BaseX + 40.0f, BaseY + 12.0f, nullptr, 1.4f);
	DrawText(SubStr, FLinearColor(0.85f, 0.85f, 0.85f, Alpha * 0.9f), BaseX + 40.0f, BaseY + 44.0f, nullptr, 0.95f);
}

// ── 3. Interaction Prompt ─────────────────────────────────────

void AIsekaiVillageHUD::DrawInteractionPrompt()
{
	if (!bShowPrompt || CurrentPrompt.IsEmpty()) return;

	const float PromptW = 380.0f;
	const float PromptH = 40.0f;
	const float PromptX = (Canvas->SizeX - PromptW) * 0.5f;
	const float PromptY = Canvas->SizeY * 0.72f;

	DrawRect(FLinearColor(0.04f, 0.06f, 0.12f, 0.85f), PromptX, PromptY, PromptW, PromptH);
	DrawRect(FLinearColor(0.3f, 0.8f, 1.0f, 0.9f), PromptX, PromptY, PromptW, 2.0f);
	DrawRect(FLinearColor(0.3f, 0.8f, 1.0f, 0.9f), PromptX, PromptY + PromptH - 2.0f, PromptW, 2.0f);

	DrawText(CurrentPrompt.ToString(), FLinearColor::White, PromptX + 18.0f, PromptY + 10.0f, nullptr, 1.05f);
}
