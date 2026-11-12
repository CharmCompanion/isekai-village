// Copyright Epic Games, Inc. All Rights Reserved.
#include "DayBoardCatalogWidgets.h"
#include "VillageRuntime.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/HorizontalBox.h"
#include "Components/HorizontalBoxSlot.h"
#include "Components/ScrollBox.h"
#include "Components/SizeBox.h"
#include "Components/TextBlock.h"
#include "Components/VerticalBox.h"
#include "Components/VerticalBoxSlot.h"
#include "GameFramework/PlayerController.h"
#include "InputCoreTypes.h"
#include "Styling/CoreStyle.h"

namespace
{
UTextBlock* BoardMakeText(UWidgetTree* Tree, const FString& Text, int32 Size = 15, FLinearColor Color = FLinearColor::White)
{
	UTextBlock* T = Tree->ConstructWidget<UTextBlock>();
	T->SetText(FText::FromString(Text));
	T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), Size));
	T->SetColorAndOpacity(FSlateColor(Color));
	T->SetAutoWrapText(true);
	return T;
}

UButton* BoardMakeButton(UWidgetTree* Tree, const FString& Caption, UTextBlock** OutLabel = nullptr)
{
	UButton* B = Tree->ConstructWidget<UButton>();
	UTextBlock* T = BoardMakeText(Tree, Caption, 14, FLinearColor(0.05f, 0.08f, 0.12f));
	B->AddChild(T);
	if (OutLabel) *OutLabel = T;
	return B;
}

void BoardRestoreGameInput(const UUserWidget* Widget, bool bOldCursor, bool& bRestored)
{
	if (bRestored) return;
	bRestored = true;
	if (APlayerController* PC = Widget->GetOwningPlayer())
	{
		PC->bShowMouseCursor = bOldCursor;
		PC->SetInputMode(FInputModeGameOnly());
	}
}

FString EraBadge(ETownEra Era)
{
	switch (Era)
	{
	case ETownEra::Kingdom: return TEXT("[Kingdom]");
	case ETownEra::LargeTown: return TEXT("[Barony/Town]");
	default: return TEXT("[Village]");
	}
}
}

void UDayBoardMissionRow::InitializeRow(UDayBoardWidget* InBoard, int32 InIndex)
{
	Board = InBoard;
	MissionIndex = InIndex;
}

TSharedRef<SWidget> UDayBoardMissionRow::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("DayBoardRowTree"));
	UBorder* Border = WidgetTree->ConstructWidget<UBorder>();
	Border->SetBrushColor(FLinearColor(0.07f, 0.10f, 0.16f, 0.95f));
	Border->SetPadding(FMargin(10.0f));
	WidgetTree->RootWidget = Border;

	UHorizontalBox* Box = WidgetTree->ConstructWidget<UHorizontalBox>();
	Border->AddChild(Box);

	Details = BoardMakeText(WidgetTree, TEXT(""), 14);
	Box->AddChildToHorizontalBox(Details)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UTextBlock* Label = nullptr;
	ActionButton = BoardMakeButton(WidgetTree, TEXT("Complete"), &Label);
	ActionLabel = Label;
	ActionButton->OnClicked.AddDynamic(this, &UDayBoardMissionRow::HandleComplete);
	Box->AddChildToHorizontalBox(ActionButton)->SetPadding(FMargin(8.0f, 0.0f, 0.0f, 0.0f));

	RefreshRow();
	return Super::RebuildWidget();
}

void UDayBoardMissionRow::RefreshRow()
{
	if (!Details || !ActionButton || !Board || !Board->GetVillage() || !Board->GetPlayer()) return;
	AVillageRuntime* V = Board->GetVillage();
	AIsekaiVillageCharacter* P = Board->GetPlayer();
	if (!V->TodayMissions.IsValidIndex(MissionIndex) || !P->Gather) return;

	const FDayMission& M = V->TodayMissions[MissionIndex];
	FString ActionName = TEXT("Turn In");
	bool bCanAct = !M.bClaimed;
	if (M.bClaimed)
	{
		ActionName = TEXT("Done");
	}
	else if (M.Kind == EDayMissionKind::CookMeals)
	{
		ActionName = FString::Printf(TEXT("Cook (%d Food)"), V->FoodStock);
		bCanAct = V->FoodStock > 0 && M.Have < M.Need;
	}
	else if (M.Kind == EDayMissionKind::FetchWood)
	{
		ActionName = FString::Printf(TEXT("Deliver %d Wood"), M.Need);
		bCanAct = P->Gather->GetCount(TEXT("Wood")) >= M.Need;
	}
	else if (M.Kind == EDayMissionKind::RepairWall)
	{
		ActionName = TEXT("Repair (3 Wood)");
		bCanAct = P->Gather->GetCount(TEXT("Wood")) >= 3;
	}
	else if (M.Kind == EDayMissionKind::StockStall)
	{
		ActionName = M.IsReady() ? TEXT("Claim") : TEXT("Sell at Shop");
		bCanAct = M.Have >= M.Need || V->WoodSoldToday >= M.Need;
	}

	Details->SetText(FText::FromString(FString::Printf(TEXT("%s  [%d / %d]  |  Reward: +1 SP, +5 Trust%s"),
		*M.Title().ToString(), M.Have, M.Need, M.bClaimed ? TEXT("  [CLAIMED]") : TEXT(""))));
	if (ActionLabel) ActionLabel->SetText(FText::FromString(ActionName));
	ActionButton->SetIsEnabled(bCanAct);
}

void UDayBoardMissionRow::HandleComplete()
{
	if (Board) Board->SubmitMission(MissionIndex);
}

void UDayBoardWidget::InitializeBoard(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer)
{
	Village = InVillage;
	Player = InPlayer;
	SetIsFocusable(true);
	if (APlayerController* PC = GetOwningPlayer()) bOldCursor = PC->bShowMouseCursor;
}

TSharedRef<SWidget> UDayBoardWidget::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("DayBoardTree"));
	UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Canvas;

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(760.0f);
	Size->SetHeightOverride(560.0f);
	UCanvasPanelSlot* CS = Canvas->AddChildToCanvas(Size);
	CS->SetAnchors(FAnchors(0.5f, 0.5f));
	CS->SetAlignment(FVector2D(0.5f, 0.5f));
	CS->SetAutoSize(true);

	UBorder* Bg = WidgetTree->ConstructWidget<UBorder>();
	Bg->SetBrushColor(FLinearColor(0.025f, 0.04f, 0.065f, 0.97f));
	Bg->SetPadding(FMargin(18.0f));
	Size->AddChild(Bg);

	UVerticalBox* Main = WidgetTree->ConstructWidget<UVerticalBox>();
	Bg->AddChild(Main);

	Main->AddChildToVerticalBox(BoardMakeText(WidgetTree, TEXT("VILLAGE COMMISSION & ERA BOARD"), 24, FLinearColor(0.95f, 0.85f, 0.52f)));
	HeaderStatus = BoardMakeText(WidgetTree, TEXT(""), 15, FLinearColor(0.75f, 0.90f, 1.0f));
	Main->AddChildToVerticalBox(HeaderStatus)->SetPadding(FMargin(0.0f, 4.0f, 0.0f, 4.0f));

	EraProgressText = BoardMakeText(WidgetTree, TEXT(""), 14, FLinearColor(0.72f, 0.95f, 0.78f));
	Main->AddChildToVerticalBox(EraProgressText)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 8.0f));

	MessageText = BoardMakeText(WidgetTree, TEXT("Complete daily slips to build Trust & earn Sphere Points (+1 SP)."), 14, FLinearColor(1.0f, 0.82f, 0.42f));
	Main->AddChildToVerticalBox(MessageText)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 8.0f));

	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Main->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	MissionsBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(MissionsBox);

	UHorizontalBox* Footer = WidgetTree->ConstructWidget<UHorizontalBox>();
	Main->AddChildToVerticalBox(Footer)->SetPadding(FMargin(0.0f, 10.0f, 0.0f, 0.0f));

	UTextBlock* FL = nullptr;
	FortifyButton = BoardMakeButton(WidgetTree, TEXT("Fortify Wall (1 ToolParts + 2 Wood -> +15)"), &FL);
	FortifyLabel = FL;
	FortifyButton->OnClicked.AddDynamic(this, &UDayBoardWidget::HandleFortifyWall);
	Footer->AddChildToHorizontalBox(FortifyButton)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UButton* CloseBtn = BoardMakeButton(WidgetTree, TEXT("Close (Esc / U)"));
	CloseBtn->OnClicked.AddDynamic(this, &UDayBoardWidget::CloseBoard);
	Footer->AddChildToHorizontalBox(CloseBtn)->SetPadding(FMargin(10.0f, 0.0f, 0.0f, 0.0f));

	RefreshBoard();
	return Super::RebuildWidget();
}

void UDayBoardWidget::RefreshNumbers()
{
	if (!Village || !Player || !Player->Gather) return;
	if (HeaderStatus)
	{
		HeaderStatus->SetText(FText::FromString(FString::Printf(
			TEXT("Day %d  |  Era: %s  |  Guild Rank %s  |  Trust %d  |  Wall %d/100  |  FoodStock %d  |  Wood %d  ToolParts %d"),
			Village->DayIndex, *Village->GetSettlementEraName(Player), *Village->GetGuildRankName(),
			Village->Trust + Player->SphereTrustBonus, Village->WallIntegrity, Village->FoodStock,
			Player->Gather->GetCount(TEXT("Wood")), Player->Gather->GetCount(TEXT("ToolParts")))));
	}
	if (EraProgressText)
	{
		EraProgressText->SetText(FText::FromString(Village->GetNextEraRequirementText(Player)));
	}
	if (FortifyButton)
	{
		FortifyButton->SetIsEnabled(Player->Gather->GetCount(TEXT("ToolParts")) >= 1 && Player->Gather->GetCount(TEXT("Wood")) >= 2 && Village->WallIntegrity < 100);
	}
}

void UDayBoardWidget::RefreshBoard()
{
	if (!MissionsBox || !Village) return;
	MissionsBox->ClearChildren();
	Rows.Reset();
	for (int32 i = 0; i < Village->TodayMissions.Num(); ++i)
	{
		UDayBoardMissionRow* Row = CreateWidget<UDayBoardMissionRow>(GetOwningPlayer());
		if (Row)
		{
			Row->InitializeRow(this, i);
			MissionsBox->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 8.0f));
			Rows.Add(Row);
		}
	}
	RefreshNumbers();
}

bool UDayBoardWidget::SubmitMission(int32 Index)
{
	const bool Ok = Village && Village->TryCompleteMissionAtIndex(Index, Player);
	if (MessageText && Village && !Village->LastServiceMessage.IsEmpty())
	{
		MessageText->SetText(FText::FromString(Village->LastServiceMessage));
	}
	RefreshBoard();
	return Ok;
}

void UDayBoardWidget::HandleFortifyWall()
{
	FortifyWall();
}

bool UDayBoardWidget::FortifyWall()
{
	const bool Ok = Village && Village->ReinforceWallWithToolParts(Player);
	if (MessageText && Village)
	{
		MessageText->SetText(FText::FromString(Ok
			? FString::Printf(TEXT("Town wall fortified to %d/100!"), Village->WallIntegrity)
			: TEXT("Need 1 ToolParts and 2 Wood (and wall below 100).")));
	}
	RefreshNumbers();
	return Ok;
}

void UDayBoardWidget::NativeTick(const FGeometry& Geometry, float DeltaSeconds)
{
	Super::NativeTick(Geometry, DeltaSeconds);
	RefreshIn -= DeltaSeconds;
	if (RefreshIn <= 0.0f)
	{
		RefreshIn = 0.5f;
		RefreshNumbers();
		for (UDayBoardMissionRow* Row : Rows) if (Row) Row->RefreshRow();
	}
}

void UDayBoardWidget::CloseBoard()
{
	BoardRestoreGameInput(this, bOldCursor, bRestoredInput);
	RemoveFromParent();
}

void UDayBoardWidget::NativeDestruct()
{
	BoardRestoreGameInput(this, bOldCursor, bRestoredInput);
	Super::NativeDestruct();
}

FReply UDayBoardWidget::NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::U)
	{
		CloseBoard();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(Geometry, Event);
}

// ───────── UBuildingCatalogWidget (Non-blocking HUD dock) ─────────

void UBuildingCatalogWidget::InitializeCatalog(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer)
{
	Village = InVillage;
	Player = InPlayer;
}

TSharedRef<SWidget> UBuildingCatalogWidget::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("BuildingCatalogTree"));
	UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Canvas;

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(430.0f);
	Size->SetHeightOverride(560.0f);
	UCanvasPanelSlot* CS = Canvas->AddChildToCanvas(Size);
	CS->SetAnchors(FAnchors(1.0f, 0.5f));
	CS->SetAlignment(FVector2D(1.0f, 0.5f));
	CS->SetOffsets(FMargin(-24.0f, 0.0f, 430.0f, 560.0f));
	CS->SetAutoSize(true);

	UBorder* Bg = WidgetTree->ConstructWidget<UBorder>();
	Bg->SetBrushColor(FLinearColor(0.015f, 0.025f, 0.045f, 0.94f));
	Bg->SetPadding(FMargin(14.0f));
	Size->AddChild(Bg);

	UVerticalBox* Main = WidgetTree->ConstructWidget<UVerticalBox>();
	Bg->AddChild(Main);

	HeaderText = BoardMakeText(WidgetTree, TEXT("BUILDING CATALOGUE"), 20, FLinearColor(0.94f, 0.84f, 0.57f));
	Main->AddChildToVerticalBox(HeaderText);

	EraText = BoardMakeText(WidgetTree, TEXT(""), 12, FLinearColor(0.72f, 0.93f, 0.79f));
	Main->AddChildToVerticalBox(EraText)->SetPadding(FMargin(0.0f, 2.0f, 0.0f, 2.0f));

	ResourcesText = BoardMakeText(WidgetTree, TEXT(""), 12, FLinearColor(0.85f, 0.85f, 0.72f));
	Main->AddChildToVerticalBox(ResourcesText)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 6.0f));

	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Main->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	EntriesBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(EntriesBox);

	SelectedDetailText = BoardMakeText(WidgetTree, TEXT(""), 12, FLinearColor(1.0f, 0.68f, 0.35f));
	Main->AddChildToVerticalBox(SelectedDetailText)->SetPadding(FMargin(0.0f, 6.0f, 0.0f, 2.0f));
	Main->AddChildToVerticalBox(BoardMakeText(WidgetTree, TEXT("Scroll/PgUp/PgDn: Choose  |  R: Rotate 90  |  LMB/T: Build  |  B/RMB: Close"), 11, FLinearColor(0.72f, 0.82f, 0.92f)));

	BuildEntryList();
	UpdateEntryHighlights();
	return Super::RebuildWidget();
}

void UBuildingCatalogWidget::BuildEntryList()
{
	if (!EntriesBox || !Village) return;
	EntriesBox->ClearChildren();
	EntryBorders.Reset();
	EntryLabels.Reset();
	EntryCosts.Reset();

	for (int32 i = 0; i < Village->BuildingCatalog.Num(); ++i)
	{
		const FTownPlot& Choice = Village->BuildingCatalog[i];
		UBorder* RowBorder = WidgetTree->ConstructWidget<UBorder>();
		RowBorder->SetPadding(FMargin(6.0f, 3.0f));

		UHorizontalBox* HB = WidgetTree->ConstructWidget<UHorizontalBox>();
		RowBorder->AddChild(HB);

		UTextBlock* TitleText = BoardMakeText(WidgetTree, Choice.Title().ToString(), 13);
		UTextBlock* CostText = BoardMakeText(WidgetTree, TEXT(""), 12, FLinearColor(0.85f, 0.76f, 0.54f));
		HB->AddChildToHorizontalBox(TitleText)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		HB->AddChildToHorizontalBox(CostText)->SetPadding(FMargin(8.0f, 0.0f, 0.0f, 0.0f));

		EntriesBox->AddChildToVerticalBox(RowBorder)->SetPadding(FMargin(0.0f, 1.0f));
		EntryBorders.Add(RowBorder);
		EntryLabels.Add(TitleText);
		EntryCosts.Add(CostText);
	}
}

void UBuildingCatalogWidget::UpdateEntryHighlights()
{
	if (!Village) return;
	const float Discount = Village->EffectiveBuildDiscount(Player);
	const int32 Dev = Village->DevelopedPlotCount();
	CachedSelection = Village->SelectedBuildingIndex;
	CachedTrust = Village->Trust;
	CachedBuiltCount = Dev;
	CachedDiscount = Discount;

	if (HeaderText)
	{
		HeaderText->SetText(FText::FromString(FString::Printf(TEXT("BUILDING CATALOGUE  [%s]"), *Village->GetSettlementEraName(Player))));
	}
	if (EraText)
	{
		EraText->SetText(FText::FromString(Village->GetNextEraRequirementText(Player)));
	}
	if (ResourcesText && Player && Player->Gather)
	{
		ResourcesText->SetText(FText::FromString(FString::Printf(TEXT("Stock: %dW  %dI  %dC   |   Wood Discount: -%.0f%%"),
			Player->Gather->GetCount(TEXT("Wood")), Player->Gather->GetCount(TEXT("Iron")),
			Player->Gather->GetCount(TEXT("Crystal")), Discount)));
	}

	if (EntryBorders.Num() != Village->BuildingCatalog.Num())
	{
		BuildEntryList();
	}

	for (int32 i = 0; i < Village->BuildingCatalog.Num(); ++i)
	{
		const FTownPlot& Choice = Village->BuildingCatalog[i];
		const bool bOpen = Village->EraOpen(Choice.Era, Player);
		const bool bBuiltUnique = Village->IsUniqueBuildingStanding(Choice);
		const bool bSelected = (i == Village->SelectedBuildingIndex);
		const int32 Wood = Choice.WoodPrice(Discount);

		if (EntryBorders.IsValidIndex(i) && EntryBorders[i])
		{
			EntryBorders[i]->SetBrushColor(bSelected
				? FLinearColor(0.08f, 0.28f, 0.36f, 0.96f)
				: FLinearColor(0.03f, 0.05f, 0.09f, 0.65f));
		}
		if (EntryLabels.IsValidIndex(i) && EntryLabels[i])
		{
			const TCHAR* Tag = bBuiltUnique ? TEXT(" [built]") : (bOpen ? TEXT("") : TEXT(" [locked]"));
			EntryLabels[i]->SetText(FText::FromString(FString::Printf(TEXT("%s%s %s%s"),
				bSelected ? TEXT("> ") : TEXT("  "),
				*EraBadge(Choice.Era), *Choice.Title().ToString(), Tag)));
			EntryLabels[i]->SetColorAndOpacity(FSlateColor(bOpen ? FLinearColor(0.92f, 0.95f, 0.94f) : FLinearColor(0.55f, 0.58f, 0.65f)));
		}
		if (EntryCosts.IsValidIndex(i) && EntryCosts[i])
		{
			EntryCosts[i]->SetText(FText::FromString(FString::Printf(TEXT("%dW %dI %dC"), Wood, Choice.IronCost, Choice.CrystalCost)));
		}
	}

	if (SelectedDetailText)
	{
		if (const FTownPlot* Sel = Village->SelectedBuilding())
		{
			if (!Village->EraOpen(Sel->Era, Player))
			{
				SelectedDetailText->SetText(FText::FromString(Sel->Era == ETownEra::Kingdom
					? TEXT("Unlock Kingdom buildings: Effective Trust 80 + 8 Sphere nodes")
					: TEXT("Unlock Town/Barony buildings: Effective Trust 50 + 4 Sphere nodes")));
				SelectedDetailText->SetColorAndOpacity(FSlateColor(FLinearColor(1.0f, 0.55f, 0.30f)));
			}
			else if (Village->CanAffordBuilding(*Sel, Player))
			{
				SelectedDetailText->SetText(FText::FromString(TEXT("Ready to place — aim at empty land (green tint) and Left Click or press T.")));
				SelectedDetailText->SetColorAndOpacity(FSlateColor(FLinearColor(0.45f, 0.95f, 0.68f)));
			}
			else
			{
				SelectedDetailText->SetText(FText::FromString(TEXT("Need more resources (or unique building already standing).")));
				SelectedDetailText->SetColorAndOpacity(FSlateColor(FLinearColor(1.0f, 0.72f, 0.38f)));
			}
		}
	}
}

void UBuildingCatalogWidget::RefreshCatalog()
{
	UpdateEntryHighlights();
}

bool UBuildingCatalogWidget::SelectCatalogIndex(int32 Index)
{
	if (!Village || !Village->BuildingCatalog.IsValidIndex(Index)) return false;
	Village->SelectedBuildingIndex = Index;
	Village->PlacementTurns = 0;
	UpdateEntryHighlights();
	return true;
}

void UBuildingCatalogWidget::CloseCatalog()
{
	RemoveFromParent();
}

void UBuildingCatalogWidget::NativeTick(const FGeometry& Geometry, float DeltaSeconds)
{
	Super::NativeTick(Geometry, DeltaSeconds);
	if (!Village || !Village->bBuildingCatalogOpen)
	{
		RemoveFromParent();
		return;
	}
	if (CachedSelection != Village->SelectedBuildingIndex
		|| CachedTrust != Village->Trust
		|| CachedBuiltCount != Village->DevelopedPlotCount()
		|| !FMath::IsNearlyEqual(CachedDiscount, Village->EffectiveBuildDiscount(Player)))
	{
		UpdateEntryHighlights();
	}
}
