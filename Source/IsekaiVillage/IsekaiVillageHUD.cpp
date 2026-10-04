// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageHUD — TP bar + arte slots + element indicator + Focus Mode flash

#include "IsekaiVillageHUD.h"
#include "IsekaiVillageCharacter.h"
#include "SphereGridWidget.h"
#include "PartyReserveComponent.h"
#include "SphereGridDataAsset.h"
#include "Blueprint/UserWidget.h"
#include "Engine/Canvas.h"
#include "Engine/Font.h"
#include "GameFramework/PlayerController.h"
#include "UObject/ConstructorHelpers.h"

AIsekaiVillageHUD::AIsekaiVillageHUD()
{
	SphereGridWidgetClass = USphereGridWidget::StaticClass();
	static ConstructorHelpers::FClassFinder<USphereGridWidget> SphereGridWBP(TEXT("/Game/IsekaiVillage/UI/WBP_SphereGrid.WBP_SphereGrid_C"));
	if (SphereGridWBP.Succeeded())
	{
		SphereGridWidgetClass = SphereGridWBP.Class;
	}
}

void AIsekaiVillageHUD::BeginPlay()
{
	Super::BeginPlay();

	if (APlayerController* PC = GetOwningPlayerController())
	{
		TSubclassOf<USphereGridWidget> WidgetClass = SphereGridWidgetClass
			? SphereGridWidgetClass
			: TSubclassOf<USphereGridWidget>(USphereGridWidget::StaticClass());
		SphereGridWidget = CreateWidget<USphereGridWidget>(PC, WidgetClass);
	}
}

void AIsekaiVillageHUD::ToggleSphereGrid()
{
	bSphereGridVisible = !bSphereGridVisible;
	const bool bUseWBP = SphereGridWidget && SphereGridWidget->GetClass() != USphereGridWidget::StaticClass();
	if (bUseWBP)
	{
		if (bSphereGridVisible)
		{
			SphereGridWidget->AddToViewport(20);
			SphereGridWidget->RebuildGrid();
		}
		else
		{
			SphereGridWidget->RemoveFromParent();
		}
	}
	SetSphereGridInput(bSphereGridVisible);
}

void AIsekaiVillageHUD::SetSphereGridInput(bool bOpen)
{
	APlayerController* PC = GetOwningPlayerController();
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPawn());
	if (Character)
	{
		Character->bSphereGridOpen = bOpen;
	}
	if (!PC)
	{
		return;
	}

	PC->bEnableClickEvents = bOpen;
	PC->bEnableMouseOverEvents = bOpen;
	PC->SetShowMouseCursor(bOpen);
	if (bOpen)
	{
		FInputModeGameAndUI Mode;
		if (SphereGridWidget && SphereGridWidget->GetClass() != USphereGridWidget::StaticClass())
		{
			Mode.SetWidgetToFocus(SphereGridWidget->TakeWidget());
		}
		Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		PC->SetInputMode(Mode);
	}
	else
	{
		PC->SetInputMode(FInputModeGameOnly());
	}
}

void AIsekaiVillageHUD::DrawHUD()
{
	Super::DrawHUD();
	if (!Canvas) return;

	APawn* Pawn = GetOwningPawn();
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(Pawn);
	if (!Character) return;

	if (bSphereGridVisible)
	{
		if (!(SphereGridWidget && SphereGridWidget->GetClass() != USphereGridWidget::StaticClass()))
		{
			DrawSphereGrid(Character);
		}
		return;
	}

	DrawTPBar(Character);
	DrawElementIndicator(Character);
	DrawFocusModeFlash(Character);
}

static FLinearColor GetElementColor(EElement Elem)
{
	switch (Elem)
	{
	case EElement::Fire:  return FLinearColor(1.0f, 0.25f, 0.05f);
	case EElement::Earth: return FLinearColor(0.95f, 0.65f, 0.15f);
	case EElement::Wind:  return FLinearColor(0.15f, 0.95f, 0.55f);
	case EElement::Water: return FLinearColor(0.05f, 0.68f, 1.0f);
	default:              return FLinearColor::White;
	}
}

static FString GetElementShortName(EElement Elem)
{
	switch (Elem)
	{
	case EElement::Fire:  return TEXT("FIRE");
	case EElement::Earth: return TEXT("EARTH");
	case EElement::Wind:  return TEXT("WIND");
	case EElement::Water: return TEXT("WATER");
	default:              return TEXT("???");
	}
}

// TP Bar (bottom-left)
void AIsekaiVillageHUD::DrawTPBar(AIsekaiVillageCharacter* Character)
{
	const float BarW = 260.0f;
	const float BarH = 14.0f;
	const float PosX = 30.0f;
	const float PosY = Canvas->SizeY - 80.0f;

	float TPRatio = (Character->MaxTP > 0.0f)
		? FMath::Clamp(Character->CurrentTP / Character->MaxTP, 0.0f, 1.0f)
		: 0.0f;
	float HPRatio = (Character->MaxHP > 0.0f)
		? FMath::Clamp(Character->CurrentHP / Character->MaxHP, 0.0f, 1.0f)
		: 0.0f;

	const float HPBarY = PosY - 38.0f;
	DrawRect(FLinearColor(0.08f, 0.02f, 0.02f, 0.88f), PosX - 2, HPBarY - 2, BarW + 4, BarH + 4);
	DrawRect(FLinearColor(0.85f, 0.18f, 0.18f, 1.0f), PosX, HPBarY, BarW * HPRatio, BarH);
	DrawText(FString::Printf(TEXT("HP  %.0f / %.0f"), Character->CurrentHP, Character->MaxHP),
		FLinearColor(1.0f, 0.55f, 0.55f), PosX, HPBarY - 18.0f, nullptr, 0.9f);

	// Background
	DrawRect(FLinearColor(0.03f, 0.03f, 0.10f, 0.88f), PosX - 2, PosY - 2, BarW + 4, BarH + 4);

	// TP fill — cyan when high, orange when low
	FLinearColor FillColor = (TPRatio < 0.2f)
		? FLinearColor(0.9f, 0.35f, 0.05f, 1.0f)
		: FLinearColor(0.05f, 0.55f, 1.0f, 1.0f);
	DrawRect(FillColor, PosX, PosY, BarW * TPRatio, BarH);

	// Border
	DrawRect(FLinearColor(0.1f, 0.4f, 0.9f, 0.7f), PosX - 2, PosY - 2, BarW + 4, 2.0f);
	DrawRect(FLinearColor(0.1f, 0.4f, 0.9f, 0.7f), PosX - 2, PosY + BarH, BarW + 4, 2.0f);
	DrawRect(FLinearColor(0.1f, 0.4f, 0.9f, 0.7f), PosX - 2, PosY - 2, 2.0f, BarH + 4);
	DrawRect(FLinearColor(0.1f, 0.4f, 0.9f, 0.7f), PosX + BarW + 2, PosY - 2, 2.0f, BarH + 4);

	// Label
	FString TPStr = FString::Printf(TEXT("TP  %.0f / %.0f"), Character->CurrentTP, Character->MaxTP);
	FLinearColor LabelColor = (TPRatio < 0.2f) ? FLinearColor(1.0f, 0.3f, 0.3f) : FLinearColor(0.6f, 0.85f, 1.0f);
	DrawText(TPStr, LabelColor, PosX, PosY - 20.0f, nullptr, 0.9f);
	DrawText(FString::Printf(TEXT("K Sphere Grid   SP %d"), Character->SpherePoints),
		FLinearColor(0.7f, 0.8f, 0.95f), PosX, PosY + BarH + 6.0f, nullptr, 0.8f);
	if (Character->PartyReserve)
	{
		DrawText(FString::Printf(TEXT("Reserve %d/%d  Active %d"),
			Character->PartyReserve->Reserve.Num(),
			Character->PartyReserve->MaxReserve,
			Character->PartyReserve->GetActiveCompanionCount()),
			FLinearColor(0.85f, 0.8f, 0.55f), PosX + 270.0f, PosY - 20.0f, nullptr, 0.85f);
	}
	if (Character->bNearTownZone)
	{
		DrawText(TEXT("T  Enter town"), FLinearColor(0.85f, 1.0f, 0.55f),
			Canvas->SizeX * 0.5f - 90.0f, Canvas->SizeY * 0.58f, nullptr, 1.15f);
	}
	if (Character->bNearGuildMaster)
	{
		DrawText(TEXT("T  Hire at Guild Master"), FLinearColor(1.0f, 0.92f, 0.45f),
			Canvas->SizeX * 0.5f - 120.0f, Canvas->SizeY * 0.62f, nullptr, 1.15f);
	}

	// Arte slots (4 boxes next to TP bar)
	const float SlotSize = 40.0f;
	const float SlotPad = 6.0f;
	const float SlotY = PosY - 60.0f;
	for (int32 i = 0; i < 4; ++i)
	{
		float SlotX = PosX + i * (SlotSize + SlotPad);
		FLinearColor SlotBg = FLinearColor(0.02f, 0.03f, 0.06f, 0.80f);
		DrawRect(SlotBg, SlotX, SlotY, SlotSize, SlotSize);
		FString Label = FString::Printf(TEXT("%d"), i + 1);
		DrawText(Label, FLinearColor(0.5f, 0.6f, 0.8f), SlotX + 4.0f, SlotY + 4.0f, nullptr, 0.85f);
	}
}

// Active Element indicator (bottom-center)
void AIsekaiVillageHUD::DrawElementIndicator(AIsekaiVillageCharacter* Character)
{
	float CX = Canvas->SizeX * 0.5f;
	float CY = Canvas->SizeY - 60.0f;
	FLinearColor ElemColor = GetElementColor(Character->ActiveElement);
	FString ElemName = GetElementShortName(Character->ActiveElement);

	DrawRect(FLinearColor(0.02f, 0.03f, 0.06f, 0.85f), CX - 50.0f, CY - 12.0f, 100.0f, 28.0f);
	DrawRect(ElemColor, CX - 50.0f, CY - 12.0f, 100.0f, 2.0f);
	DrawRect(ElemColor, CX - 50.0f, CY + 14.0f, 100.0f, 2.0f);
	DrawText(ElemName, ElemColor, CX - 30.0f, CY - 5.0f, nullptr, 1.0f);
}

// Focus Mode flash
void AIsekaiVillageHUD::DrawFocusModeFlash(AIsekaiVillageCharacter* Character)
{
	if (!Character->bIsFocusMode) return;

	float Alpha = FMath::Clamp(Character->FocusModeTimer / Character->FocusModeDuration, 0.0f, 1.0f) * 0.18f;

	float EdgeW = Canvas->SizeX * 0.06f;
	DrawRect(FLinearColor(0.0f, 0.85f, 1.0f, Alpha), 0, 0, EdgeW, Canvas->SizeY);
	DrawRect(FLinearColor(0.0f, 0.85f, 1.0f, Alpha), Canvas->SizeX - EdgeW, 0, EdgeW, Canvas->SizeY);
	DrawRect(FLinearColor(0.0f, 0.85f, 1.0f, Alpha), 0, 0, Canvas->SizeX, EdgeW);
	DrawRect(FLinearColor(0.0f, 0.85f, 1.0f, Alpha), 0, Canvas->SizeY - EdgeW, Canvas->SizeX, EdgeW);

	DrawText(TEXT("FOCUS — SILENT CAST READY"),
		FLinearColor(0.0f, 0.92f, 1.0f, FMath::Clamp(Alpha * 5.0f, 0.0f, 1.0f)),
		Canvas->SizeX * 0.5f - 160.0f,
		Canvas->SizeY * 0.38f,
		nullptr, 1.3f);
}

void AIsekaiVillageHUD::DrawSphereGrid(AIsekaiVillageCharacter* Character)
{
	if (!Character->SphereGrid)
	{
		return;
	}

	USphereGridDataAsset* Grid = Character->SphereGrid;
	const bool bFlipped = Character->bSphereGridFlipped;
	const TArray<FName>& Order = bFlipped ? Grid->FlipNodeOrder : Grid->LifeNodeOrder;

	DrawRect(FLinearColor(0.02f, 0.03f, 0.07f, 0.78f), 0, 0, Canvas->SizeX, Canvas->SizeY);

	const FString Title = bFlipped ? TEXT("CENTER A — Adventurer  (K close)") : TEXT("CENTER A — Life  (K close)");
	DrawText(Title, FLinearColor(0.75f, 0.9f, 1.0f), 40.0f, 28.0f, nullptr, 1.4f);
	DrawText(FString::Printf(TEXT("SP %d   HP +%d  Inv +%d  Carry +%d kg  Trust +%d"),
		Character->SpherePoints, Character->SphereHPBonus, Character->SphereInventoryBonus,
		Character->SphereCarryWeightBonus, Character->SphereTrustBonus),
		FLinearColor(0.65f, 0.8f, 0.95f), 40.0f, 60.0f, nullptr, 1.0f);

	if (!bFlipped && Grid->IsLifeFaceComplete(Character->UnlockedSphereNodes))
	{
		DrawRect(FLinearColor(0.85f, 0.65f, 0.1f, 0.9f), 40.0f, 96.0f, 220.0f, 36.0f);
		DrawText(TEXT("FLIP COIN"), FLinearColor(0.05f, 0.05f, 0.08f), 70.0f, 102.0f, nullptr, 1.1f);
		AddHitBox(FVector2D(40.0f, 96.0f), FVector2D(220.0f, 36.0f), FName(TEXT("SPHERE_FLIP")), true);
	}

	const float CenterX = Canvas->SizeX * 0.5f;
	const float CenterY = Canvas->SizeY * 0.52f;
	const float Radius = FMath::Min(Canvas->SizeX, Canvas->SizeY) * 0.28f;
	const int32 Count = Order.Num();
	const float BoxW = 120.0f;
	const float BoxH = 42.0f;

	for (int32 Index = 0; Index < Count; ++Index)
	{
		const FName NodeID = Order[Index];
		FSphereNode Node;
		Grid->GetNode(NodeID, Node);

		const float Angle = (2.0f * PI * Index) / FMath::Max(Count, 1) - PI * 0.5f;
		const float X = CenterX + FMath::Cos(Angle) * Radius - BoxW * 0.5f;
		const float Y = CenterY + FMath::Sin(Angle) * Radius - BoxH * 0.5f;

		const bool bUnlocked = Character->UnlockedSphereNodes.Contains(NodeID);
		const bool bAdjacent = Grid->IsNodeAdjacentToUnlocked(NodeID, Character->UnlockedSphereNodes, bFlipped);
		FLinearColor Color = bUnlocked
			? FLinearColor(0.12f, 0.45f, 0.9f, 0.95f)
			: (bAdjacent ? FLinearColor(0.9f, 0.7f, 0.15f, 0.95f) : FLinearColor(0.18f, 0.2f, 0.26f, 0.9f));

		DrawRect(Color, X, Y, BoxW, BoxH);
		DrawText(Node.DisplayName.ToString(), FLinearColor::White, X + 6.0f, Y + 10.0f, nullptr, 0.85f);
		AddHitBox(FVector2D(X, Y), FVector2D(BoxW, BoxH), NodeID, true);
	}
}

void AIsekaiVillageHUD::NotifyHitBoxClick(FName BoxName)
{
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPawn());
	if (!Character || !bSphereGridVisible)
	{
		return;
	}

	if (BoxName == FName(TEXT("SPHERE_FLIP")))
	{
		if (Character->FlipSphereGrid() && SphereGridWidget)
		{
			SphereGridWidget->RebuildGrid();
		}
		return;
	}

	Character->UnlockSphereNode(BoxName);
	if (SphereGridWidget)
	{
		SphereGridWidget->RebuildGrid();
	}
}
