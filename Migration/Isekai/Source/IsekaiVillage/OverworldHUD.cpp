// Copyright Epic Games, Inc. All Rights Reserved.
// OverworldHUD.cpp — JRPG Exploration HUD (Mini-map, Compass, Location Banner, Flight Telemetry)

#include "OverworldHUD.h"
#include "OverworldCharacter.h"
#include "TownZone.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

AOverworldHUD::AOverworldHUD()
{
}

void AOverworldHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas) return;

	APawn* Pawn = GetOwningPawn();
	AOverworldCharacter* Character = Cast<AOverworldCharacter>(Pawn);
	if (!Character) return;

	// Check if near any town zone to update interaction prompt
	RefreshCachedTownZones();
	bool bFoundNearbyZone = false;
	const FVector PlayerLoc = Character->GetActorLocation();

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
				bFoundNearbyZone = true;
				break;
			}
		}
	}

	if (!bFoundNearbyZone && bShowPrompt)
	{
		bShowPrompt = false;
	}

	// Render HUD components
	DrawMiniMapAndCompass(Character);
	DrawFlightTelemetry(Character);
	DrawLocationBanner();
	DrawInteractionPrompt();
}

void AOverworldHUD::RefreshCachedTownZones()
{
	float CurrentTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;
	if (CurrentTime - LastZoneSearchTime > 3.0f || CachedTownZones.Num() == 0)
	{
		LastZoneSearchTime = CurrentTime;
		CachedTownZones.Empty();
		for (TActorIterator<ATownZone> It(GetWorld()); It; ++It)
		{
			CachedTownZones.Add(*It);
		}
	}
}

void AOverworldHUD::ShowLocationBanner(const FText& Title, const FText& Subtitle, float Duration)
{
	BannerTitle = Title;
	BannerSubtitle = Subtitle;
	BannerTotalDuration = Duration > 0.0f ? Duration : 4.0f;
	BannerTimer = BannerTotalDuration;
	bBannerActive = true;
}

void AOverworldHUD::SetInteractionPrompt(const FText& PromptText, bool bShow)
{
	CurrentPrompt = PromptText;
	bShowPrompt = bShow;
}

// ── 1. Mini-map & Compass (Top-Right) ─────────────────────────

void AOverworldHUD::DrawMiniMapAndCompass(AOverworldCharacter* Character)
{
	const float RadarRadius = 85.0f;
	const float CenterX = Canvas->SizeX - RadarRadius - 35.0f;
	const float CenterY = RadarRadius + 35.0f;
	const float WorldToRadarScale = 0.008f; // 1 meter = 0.8 radar pixels

	// Dark semi-transparent radar background
	DrawRect(FLinearColor(0.02f, 0.04f, 0.08f, 0.75f),
		CenterX - RadarRadius, CenterY - RadarRadius,
		RadarRadius * 2.0f, RadarRadius * 2.0f);

	// Elegant golden outer border
	const FLinearColor GoldBorder(0.95f, 0.75f, 0.25f, 0.85f);
	DrawRect(GoldBorder, CenterX - RadarRadius - 2.0f, CenterY - RadarRadius - 2.0f, RadarRadius * 2.0f + 4.0f, 2.0f);
	DrawRect(GoldBorder, CenterX - RadarRadius - 2.0f, CenterY + RadarRadius, RadarRadius * 2.0f + 4.0f, 2.0f);
	DrawRect(GoldBorder, CenterX - RadarRadius - 2.0f, CenterY - RadarRadius - 2.0f, 2.0f, RadarRadius * 2.0f + 4.0f);
	DrawRect(GoldBorder, CenterX + RadarRadius, CenterY - RadarRadius - 2.0f, 2.0f, RadarRadius * 2.0f + 4.0f);

	// Cardinal Points (N, S, E, W) relative to player camera / world orientation
	APlayerController* PC = Cast<APlayerController>(Character->GetController());
	const float CamYaw = PC ? PC->GetControlRotation().Yaw : Character->GetActorRotation().Yaw;
	const float CamRad = FMath::DegreesToRadians(CamYaw);

	auto DrawCardinal = [&](const FString& Label, float AngleDeg, const FLinearColor& Color)
	{
		float Rad = FMath::DegreesToRadians(AngleDeg - CamYaw);
		float OffsetX = FMath::Sin(Rad) * (RadarRadius - 14.0f);
		float OffsetY = -FMath::Cos(Rad) * (RadarRadius - 14.0f);
		DrawText(Label, Color, CenterX + OffsetX - 4.0f, CenterY + OffsetY - 6.0f, nullptr, 0.9f);
	};

	DrawCardinal(TEXT("N"), 0.0f, FLinearColor(1.0f, 0.35f, 0.35f, 1.0f));
	DrawCardinal(TEXT("E"), 90.0f, FLinearColor(0.8f, 0.85f, 0.95f, 0.8f));
	DrawCardinal(TEXT("S"), 180.0f, FLinearColor(0.8f, 0.85f, 0.95f, 0.8f));
	DrawCardinal(TEXT("W"), 270.0f, FLinearColor(0.8f, 0.85f, 0.95f, 0.8f));

	// Draw POIs (Towns & Dungeons) on the radar
	const FVector PlayerLoc = Character->GetActorLocation();
	for (const TWeakObjectPtr<ATownZone>& ZonePtr : CachedTownZones)
	{
		if (ATownZone* Zone = ZonePtr.Get())
		{
			FVector Delta = Zone->GetActorLocation() - PlayerLoc;
			// Rotate by camera yaw so radar is forward-oriented
			FVector RotatedDelta = FRotator(0.0f, -CamYaw, 0.0f).RotateVector(Delta);

			float IconX = CenterX + (RotatedDelta.Y * WorldToRadarScale);
			float IconY = CenterY - (RotatedDelta.X * WorldToRadarScale);

			// Clamp inside radar boundary
			float DistFromCenter = FVector2D(IconX - CenterX, IconY - CenterY).Size();
			if (DistFromCenter > RadarRadius - 10.0f)
			{
				float Angle = FMath::Atan2(IconY - CenterY, IconX - CenterX);
				IconX = CenterX + FMath::Cos(Angle) * (RadarRadius - 10.0f);
				IconY = CenterY + FMath::Sin(Angle) * (RadarRadius - 10.0f);
			}

			// Town POI Icon (Cyan diamond marker)
			DrawRect(FLinearColor(0.0f, 0.9f, 1.0f, 0.9f), IconX - 3.0f, IconY - 3.0f, 6.0f, 6.0f);
		}
	}

	// Player Arrow (center of radar pointing forward)
	const FLinearColor PlayerColor(1.0f, 0.9f, 0.2f, 1.0f);
	DrawRect(PlayerColor, CenterX - 3.0f, CenterY - 3.0f, 6.0f, 6.0f);
	DrawRect(FLinearColor(1.0f, 1.0f, 1.0f, 0.9f), CenterX - 1.0f, CenterY - 7.0f, 2.0f, 4.0f);
}

// ── 2. Flight & Travel Telemetry ──────────────────────────────

void AOverworldHUD::DrawFlightTelemetry(AOverworldCharacter* Character)
{
	const float PosX = Canvas->SizeX - 230.0f;
	const float PosY = 220.0f;

	// Mode Banner
	if (Character->bIsFlying)
	{
		DrawRect(FLinearColor(0.02f, 0.05f, 0.12f, 0.80f), PosX, PosY, 195.0f, 45.0f);
		DrawRect(FLinearColor(0.2f, 0.7f, 1.0f, 0.8f), PosX, PosY, 195.0f, 2.0f);

		DrawText(TEXT("RHEAIRD FLIGHT [F]"), FLinearColor(0.3f, 0.85f, 1.0f), PosX + 10.0f, PosY + 6.0f, nullptr, 0.9f);

		FString LandStr = Character->bCanLand ? TEXT("LANDING: SAFE") : TEXT("LANDING: BLOCKED");
		FLinearColor LandColor = Character->bCanLand ? FLinearColor(0.3f, 1.0f, 0.4f) : FLinearColor(1.0f, 0.35f, 0.35f);
		DrawText(LandStr, LandColor, PosX + 10.0f, PosY + 24.0f, nullptr, 0.8f);
	}
	else
	{
		DrawRect(FLinearColor(0.02f, 0.03f, 0.06f, 0.65f), PosX, PosY, 195.0f, 30.0f);
		DrawText(TEXT("[F] CALL RHEAIRD"), FLinearColor(0.7f, 0.75f, 0.85f, 0.8f), PosX + 10.0f, PosY + 8.0f, nullptr, 0.85f);
	}
}

// ── 3. Animated Location Banner (Top Center) ──────────────────

void AOverworldHUD::DrawLocationBanner()
{
	if (!bBannerActive) return;

	float DeltaTime = GetWorld() ? GetWorld()->GetDeltaSeconds() : 0.016f;
	BannerTimer -= DeltaTime;

	if (BannerTimer <= 0.0f)
	{
		bBannerActive = false;
		return;
	}

	// Calculate smooth fade-in (first 0.6s) and fade-out (last 0.8s)
	float Alpha = 1.0f;
	float Elapsed = BannerTotalDuration - BannerTimer;
	if (Elapsed < 0.6f)
	{
		Alpha = FMath::Clamp(Elapsed / 0.6f, 0.0f, 1.0f);
	}
	else if (BannerTimer < 0.8f)
	{
		Alpha = FMath::Clamp(BannerTimer / 0.8f, 0.0f, 1.0f);
	}

	const float BannerW = 460.0f;
	const float BannerH = 65.0f;
	const float PosX = (Canvas->SizeX - BannerW) * 0.5f;
	const float PosY = 70.0f;

	// Dark gradient backdrop
	DrawRect(FLinearColor(0.01f, 0.02f, 0.05f, 0.85f * Alpha), PosX, PosY, BannerW, BannerH);

	// Gold header and footer lines
	const FLinearColor GoldLine(0.95f, 0.78f, 0.30f, 0.9f * Alpha);
	DrawRect(GoldLine, PosX, PosY, BannerW, 2.0f);
	DrawRect(GoldLine, PosX, PosY + BannerH, BannerW, 2.0f);

	// Diamond center emblem accent
	DrawRect(GoldLine, PosX + BannerW * 0.5f - 4.0f, PosY - 4.0f, 8.0f, 8.0f);

	// Location Title
	FString TitleStr = BannerTitle.ToString().ToUpper();
	DrawText(TitleStr, FLinearColor(1.0f, 0.95f, 0.8f, Alpha),
		PosX + 25.0f, PosY + 12.0f, nullptr, 1.35f);

	// Subtitle
	if (!BannerSubtitle.IsEmpty())
	{
		FString SubStr = BannerSubtitle.ToString();
		DrawText(SubStr, FLinearColor(0.65f, 0.75f, 0.9f, 0.9f * Alpha),
			PosX + 28.0f, PosY + 40.0f, nullptr, 0.95f);
	}
}

// ── 4. Interaction Prompt (Bottom Center) ─────────────────────

void AOverworldHUD::DrawInteractionPrompt()
{
	if (!bShowPrompt || CurrentPrompt.IsEmpty()) return;

	const float PromptW = 340.0f;
	const float PromptH = 36.0f;
	const float PosX = (Canvas->SizeX - PromptW) * 0.5f;
	const float PosY = Canvas->SizeY - 140.0f;

	// Backdrop
	DrawRect(FLinearColor(0.02f, 0.03f, 0.07f, 0.88f), PosX, PosY, PromptW, PromptH);

	// Accent border
	const FLinearColor CyanAccent(0.1f, 0.8f, 1.0f, 0.85f);
	DrawRect(CyanAccent, PosX, PosY, PromptW, 2.0f);
	DrawRect(CyanAccent, PosX, PosY + PromptH - 2.0f, PromptW, 2.0f);

	// Prompt Text
	DrawText(CurrentPrompt.ToString(), FLinearColor(1.0f, 1.0f, 1.0f, 1.0f),
		PosX + 20.0f, PosY + 9.0f, nullptr, 1.05f);
}
