// Copyright Epic Games, Inc. All Rights Reserved.

#include "TownServiceWidget.h"
#include "VillageRuntime.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"
#include "Styling/CoreStyle.h"
#include "InputCoreTypes.h"

namespace
{
UTextBlock* SvcText(UWidgetTree* Tree, const FString& Value, int32 Size = 15, FLinearColor Color = FLinearColor(0.95f, 0.96f, 0.98f))
{
	UTextBlock* T = Tree->ConstructWidget<UTextBlock>();
	T->SetText(FText::FromString(Value));
	T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), Size));
	T->SetColorAndOpacity(FSlateColor(Color));
	T->SetAutoWrapText(true);
	return T;
}

UButton* SvcButton(UWidgetTree* Tree, const FString& Caption)
{
	UButton* B = Tree->ConstructWidget<UButton>();
	UTextBlock* T = SvcText(Tree, Caption, 15, FLinearColor(0.05f, 0.07f, 0.10f));
	B->AddChild(T);
	return B;
}
}

void UTownServiceActionButton::Init(UTownServiceWidget* InParent, FName InAction)
{
	Parent = InParent;
	ActionId = InAction;
}

void UTownServiceActionButton::OnClicked()
{
	if (Parent) Parent->TriggerAction(ActionId);
}

void UTownServiceWidget::InitializeService(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer, ETownBuilding InBuildingKind)
{
	Village = InVillage;
	Player = InPlayer;
	BuildingKind = InBuildingKind;
	SetIsFocusable(true);
	if (APlayerController* PC = GetOwningPlayer()) bOldCursor = PC->bShowMouseCursor;
}

TSharedRef<SWidget> UTownServiceWidget::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("ServiceTree"));
	UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Canvas;

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(680.0f);
	Size->SetHeightOverride(580.0f);
	if (UCanvasPanelSlot* CS = Canvas->AddChildToCanvas(Size))
	{
		CS->SetAnchors(FAnchors(0.5f, 0.5f));
		CS->SetAlignment(FVector2D(0.5f, 0.5f));
		CS->SetAutoSize(true);
	}

	UBorder* BG = WidgetTree->ConstructWidget<UBorder>();
	BG->SetBrushColor(FLinearColor(0.03f, 0.045f, 0.075f, 0.97f));
	BG->SetPadding(FMargin(18.0f));
	Size->AddChild(BG);

	UVerticalBox* Main = WidgetTree->ConstructWidget<UVerticalBox>();
	BG->AddChild(Main);

	TitleText = SvcText(WidgetTree, TEXT("TOWN SERVICE"), 24, FLinearColor(0.97f, 0.87f, 0.45f));
	Main->AddChildToVerticalBox(TitleText)->SetPadding(FMargin(0, 0, 0, 6));

	StandingSummary = SvcText(WidgetTree, TEXT(""), 14, FLinearColor(0.84f, 0.92f, 1.0f));
	Main->AddChildToVerticalBox(StandingSummary)->SetPadding(FMargin(0, 0, 0, 10));

	ActionsBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Main->AddChildToVerticalBox(ActionsBox)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	MessageText = SvcText(WidgetTree, TEXT(""), 15, FLinearColor(1.0f, 0.84f, 0.42f));
	Main->AddChildToVerticalBox(MessageText)->SetPadding(FMargin(0, 8, 0, 8));

	UButton* CloseBtn = SvcButton(WidgetTree, TEXT("Close (Esc / U)"));
	CloseBtn->OnClicked.AddDynamic(this, &UTownServiceWidget::OnCloseClicked);
	Main->AddChildToVerticalBox(CloseBtn);

	RefreshService();
	return Super::RebuildWidget();
}

void UTownServiceWidget::RefreshNumbers()
{
	if (!Village || !Player || !Player->Gather) return;
	FTownPlot Dummy;
	Dummy.Kind = BuildingKind;
	if (TitleText) TitleText->SetText(FText::FromString(FString::Printf(TEXT("EL RUHN — %s"), *Dummy.Title().ToString().ToUpper())));

	if (StandingSummary)
	{
		StandingSummary->SetText(FText::FromString(FString::Printf(
			TEXT("Guild Rank %s (Score %d, Trips %d)  |  Day %d  |  Trust %d  |  Floor %d/100\nCoin: %d  |  Vault: %d  |  Academy: T%d/3  |  Blessing: %s  |  Edict: %s"),
			*Village->GetGuildRankName(),
			Village->GetGuildStandingScore(),
			FMath::Clamp(Village->TownGuildRank + 1, 1, 5),
			Village->DayIndex,
			Village->Trust,
			Village->TowerFloor.HighestFloor,
			Player->Gather->GetCount(TEXT("Coin")),
			Village->BankVaultCoins,
			Village->AcademyResearchLevel,
			Village->ActiveChapelBlessing.IsNone() ? TEXT("None") : *Village->ActiveChapelBlessing.ToString(),
			Village->ActiveRoyalEdict.IsNone() ? TEXT("None") : *Village->ActiveRoyalEdict.ToString())));
	}
	if (MessageText)
	{
		MessageText->SetText(FText::FromString(Village->LastServiceMessage.IsEmpty()
			? TEXT("Select a town service below.")
			: Village->LastServiceMessage));
	}
}

void UTownServiceWidget::RefreshService()
{
	if (!ActionsBox) return;
	ActionsBox->ClearChildren();
	Handlers.Reset();

	auto AddBtn = [&](const FString& Label, FName ActionId)
	{
		UButton* B = SvcButton(WidgetTree, Label);
		UTownServiceActionButton* H = NewObject<UTownServiceActionButton>(this);
		H->Init(this, ActionId);
		B->OnClicked.AddDynamic(H, &UTownServiceActionButton::OnClicked);
		ActionsBox->AddChildToVerticalBox(B)->SetPadding(FMargin(0, 0, 0, 8));
		Handlers.Add(H);
	};

	switch (BuildingKind)
	{
	case ETownBuilding::Inn:
		AddBtn(TEXT("Rest Until Morning (New Day, Full HP/TP & 0 Fatigue; 1 Bread/+2 Trust)"), TEXT("Rest"));
		AddBtn(TEXT("Host Town Feast (2 Bread -> +4 Trust & Full Resident Morale)"), TEXT("Feast"));
		break;
	case ETownBuilding::Chapel:
		AddBtn(TEXT("Blessing of Valor (+15% Attack, Cleanse & Full HP)"), TEXT("BlessValor"));
		AddBtn(TEXT("Blessing of Bulwark (+15% Defense, Cleanse & Full HP)"), TEXT("BlessBulwark"));
		AddBtn(TEXT("Blessing of Grace (+20 Max HP & +15 TP, Cleanse & Full HP)"), TEXT("BlessGrace"));
		break;
	case ETownBuilding::Training:
		AddBtn(TEXT("Run Group Practice Drill (5 Coin or 1 Bread -> +25 XP All Adventurers)"), TEXT("GroupDrill"));
		AddBtn(TEXT("Begin Party Sparring Session"), TEXT("StartSparring"));
		break;
	case ETownBuilding::Bank:
		AddBtn(TEXT("Deposit 10 Coin into Vault (+10% daily interest + daily civic tax)"), TEXT("Deposit10"));
		AddBtn(TEXT("Withdraw 10 Coin from Vault"), TEXT("Withdraw10"));
		AddBtn(TEXT("Withdraw All Vault Coin"), TEXT("WithdrawAll"));
		break;
	case ETownBuilding::Bath:
		AddBtn(TEXT("Hot Spring Soak (Once/day: Full HP/TP, -50 Fatigue, +15 Max HP today)"), TEXT("Soak"));
		break;
	case ETownBuilding::Bell:
		AddBtn(TEXT("Ring Civic Bell (Once/day: +Trust, Rally Workers, Promote Guild Rank)"), TEXT("Ring"));
		break;
	case ETownBuilding::Academy:
		AddBtn(TEXT("Advance Arcane Research Tier (T1:10c+2I | T2:20c+3C | T3:35c+6C Wizardbane)"), TEXT("ResearchNext"));
		break;
	case ETownBuilding::Manor:
		AddBtn(TEXT("Enact Trade Charter Edict (+25% Bank Interest & Civic Tax)"), TEXT("EdictTrade"));
		AddBtn(TEXT("Enact Build Drive Edict (-15% Construction Wood Cost)"), TEXT("EdictBuild"));
		AddBtn(TEXT("Enact Guild Campaign Edict (+50% Practice & Daily Training XP)"), TEXT("EdictGuild"));
		AddBtn(TEXT("Collect Daily Manor Guild Stipend"), TEXT("CollectStipend"));
		break;
	case ETownBuilding::Castle:
		AddBtn(TEXT("Hold Royal Audience (Promote Guild Rank & Collect Daily Royal Grant)"), TEXT("RoyalAudience"));
		break;
	default:
		break;
	}
	RefreshNumbers();
}

bool UTownServiceWidget::TriggerAction(FName ActionId)
{
	const bool bOk = Village && Village->ExecuteServiceAction(BuildingKind, ActionId, Player);
	RefreshNumbers();
	return bOk;
}

void UTownServiceWidget::NativeTick(const FGeometry& Geometry, float DeltaSeconds)
{
	Super::NativeTick(Geometry, DeltaSeconds);
	RefreshIn -= DeltaSeconds;
	if (RefreshIn <= 0.0f)
	{
		RefreshIn = 0.4f;
		RefreshNumbers();
	}
}

void UTownServiceWidget::CloseService()
{
	if (!bRestoredInput)
	{
		bRestoredInput = true;
		if (APlayerController* PC = GetOwningPlayer())
		{
			PC->bShowMouseCursor = bOldCursor;
			PC->SetInputMode(FInputModeGameOnly());
		}
	}
	RemoveFromParent();
}

void UTownServiceWidget::NativeDestruct()
{
	if (!bRestoredInput)
	{
		bRestoredInput = true;
		if (APlayerController* PC = GetOwningPlayer())
		{
			PC->bShowMouseCursor = bOldCursor;
			PC->SetInputMode(FInputModeGameOnly());
		}
	}
	Super::NativeDestruct();
}

FReply UTownServiceWidget::NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::U)
	{
		CloseService();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(Geometry, Event);
}
