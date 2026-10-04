// Copyright Epic Games, Inc. All Rights Reserved.

#include "SphereGridWidget.h"
#include "SphereGridDataAsset.h"
#include "IsekaiVillageCharacter.h"
#include "Blueprint/WidgetTree.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/Button.h"
#include "Components/TextBlock.h"
#include "Kismet/GameplayStatics.h"

void USphereNodeClickTarget::HandleClicked()
{
	if (USphereGridWidget* Widget = Owner.Get())
	{
		Widget->HandleNodeClicked(NodeID);
	}
}

void USphereGridWidget::NativeOnInitialized()
{
	Super::NativeOnInitialized();
	EnsureLayout();
}

void USphereGridWidget::NativeConstruct()
{
	Super::NativeConstruct();
	EnsureLayout();
	RebuildGrid();
}

void USphereGridWidget::NativeTick(const FGeometry& MyGeometry, float InDeltaTime)
{
	Super::NativeTick(MyGeometry, InDeltaTime);
	RefreshVisuals();
}

void USphereGridWidget::EnsureLayout()
{
	if (!WidgetTree)
	{
		return;
	}

	if (!WidgetTree->RootWidget)
	{
		RootCanvas = WidgetTree->ConstructWidget<UCanvasPanel>(UCanvasPanel::StaticClass(), TEXT("RootCanvas"));
		WidgetTree->RootWidget = RootCanvas;
	}
	else
	{
		RootCanvas = Cast<UCanvasPanel>(WidgetTree->RootWidget);
	}

	if (!RootCanvas || HeaderText)
	{
		return;
	}

	auto AddText = [this](const FName Name, const FVector2D Position, int32 FontSize) -> UTextBlock*
	{
		UTextBlock* Text = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), Name);
		FSlateFontInfo Font = Text->GetFont();
		Font.Size = FontSize;
		Text->SetFont(Font);
		Text->SetColorAndOpacity(FSlateColor(FLinearColor(0.75f, 0.9f, 1.0f)));
		UCanvasPanelSlot* CanvasSlot = RootCanvas->AddChildToCanvas(Text);
		CanvasSlot->SetPosition(Position);
		CanvasSlot->SetAutoSize(true);
		return Text;
	};

	HeaderText = AddText(TEXT("HeaderText"), FVector2D(40.0f, 24.0f), 28);
	StatusText = AddText(TEXT("StatusText"), FVector2D(40.0f, 64.0f), 18);

	FlipButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("FlipButton"));
	UCanvasPanelSlot* FlipSlot = RootCanvas->AddChildToCanvas(FlipButton);
	FlipSlot->SetPosition(FVector2D(40.0f, 100.0f));
	FlipSlot->SetSize(FVector2D(220.0f, 40.0f));
	UTextBlock* FlipLabel = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("FlipLabel"));
	FlipLabel->SetText(NSLOCTEXT("IsekaiVillage", "FlipCoin", "Flip Coin (Adventurer)"));
	FlipButton->AddChild(FlipLabel);
	FlipButton->OnClicked.AddDynamic(this, &USphereGridWidget::HandleFlipClicked);
}

void USphereGridWidget::RebuildGrid()
{
	EnsureLayout();
	if (!RootCanvas)
	{
		return;
	}

	for (UButton* Button : NodeButtons)
	{
		if (Button)
		{
			Button->RemoveFromParent();
		}
	}
	NodeButtons.Reset();
	NodeLabels.Reset();
	ClickTargets.Reset();

	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPlayerPawn());
	if (!Character)
	{
		Character = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
	}
	if (!Character || !Character->SphereGrid)
	{
		return;
	}

	const TArray<FName>& Order = Character->bSphereGridFlipped
		? Character->SphereGrid->FlipNodeOrder
		: Character->SphereGrid->LifeNodeOrder;

	const FVector2D Center(640.0f, 400.0f);
	const float Radius = 240.0f;
	const int32 Count = Order.Num();
	for (int32 Index = 0; Index < Count; ++Index)
	{
		const float Angle = (2.0f * PI * Index) / FMath::Max(Count, 1) - PI * 0.5f;
		const FVector2D Position = Center + FVector2D(FMath::Cos(Angle), FMath::Sin(Angle)) * Radius;

		UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), *FString::Printf(TEXT("NodeBtn_%d"), Index));
		UCanvasPanelSlot* CanvasSlot = RootCanvas->AddChildToCanvas(Button);
		CanvasSlot->SetPosition(Position - FVector2D(54.0f, 28.0f));
		CanvasSlot->SetSize(FVector2D(108.0f, 56.0f));

		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), *FString::Printf(TEXT("NodeLbl_%d"), Index));
		Label->SetAutoWrapText(true);
		Button->AddChild(Label);

		USphereNodeClickTarget* Target = NewObject<USphereNodeClickTarget>(this);
		Target->NodeID = Order[Index];
		Target->Owner = this;
		Button->OnClicked.AddDynamic(Target, &USphereNodeClickTarget::HandleClicked);

		NodeButtons.Add(Button);
		NodeLabels.Add(Label);
		ClickTargets.Add(Target);
	}

	RefreshVisuals();
}

void USphereGridWidget::RefreshVisuals()
{
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPlayerPawn());
	if (!Character)
	{
		Character = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
	}
	if (!Character || !Character->SphereGrid || !HeaderText || !StatusText)
	{
		return;
	}

	USphereGridDataAsset* Grid = Character->SphereGrid;
	const bool bFlipped = Character->bSphereGridFlipped;
	HeaderText->SetText(bFlipped
		? NSLOCTEXT("IsekaiVillage", "AdvFace", "CENTER A — Adventurer")
		: NSLOCTEXT("IsekaiVillage", "LifeFace", "CENTER A — Life"));

	StatusText->SetText(FText::FromString(FString::Printf(
		TEXT("SP %d   HP +%d  TP +%d  Inv +%d  Carry +%d  Move +%.0f%%  Trust +%d"),
		Character->SpherePoints,
		Character->SphereHPBonus,
		Grid->SumBonuses(Character->UnlockedSphereNodes).TP,
		Character->SphereInventoryBonus,
		Character->SphereCarryWeightBonus,
		Grid->SumBonuses(Character->UnlockedSphereNodes).MoveSpeedPercent,
		Character->SphereTrustBonus)));

	if (FlipButton)
	{
		const bool bCanFlip = !bFlipped && Grid->IsLifeFaceComplete(Character->UnlockedSphereNodes);
		FlipButton->SetIsEnabled(bCanFlip);
		FlipButton->SetVisibility(bCanFlip ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	}

	const TArray<FName>& Order = bFlipped ? Grid->FlipNodeOrder : Grid->LifeNodeOrder;
	for (int32 Index = 0; Index < NodeButtons.Num() && Index < Order.Num(); ++Index)
	{
		const FName NodeID = Order[Index];
		FSphereNode Node;
		Grid->GetNode(NodeID, Node);

		const bool bUnlocked = Character->UnlockedSphereNodes.Contains(NodeID);
		const bool bAdjacent = Grid->IsNodeAdjacentToUnlocked(NodeID, Character->UnlockedSphereNodes, bFlipped);
		if (NodeLabels.IsValidIndex(Index) && NodeLabels[Index])
		{
			NodeLabels[Index]->SetText(Node.DisplayName);
		}
		if (NodeButtons[Index])
		{
			const bool bStartFree = bAdjacent && !Grid->HasUnlockedNodeOnFace(Character->UnlockedSphereNodes, bFlipped);
			NodeButtons[Index]->SetIsEnabled(!bUnlocked && bAdjacent && (bStartFree || Character->SpherePoints > 0));
			FLinearColor Tint = bUnlocked
				? FLinearColor(0.15f, 0.55f, 0.95f)
				: (bAdjacent ? FLinearColor(0.95f, 0.75f, 0.2f) : FLinearColor(0.2f, 0.22f, 0.28f));
			NodeButtons[Index]->SetBackgroundColor(Tint);
		}
	}
}

void USphereGridWidget::HandleNodeClicked(FName NodeID)
{
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPlayerPawn());
	if (!Character)
	{
		Character = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
	}
	if (Character)
	{
		Character->UnlockSphereNode(NodeID);
		RefreshVisuals();
	}
}

void USphereGridWidget::HandleFlipClicked()
{
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPlayerPawn());
	if (!Character)
	{
		Character = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
	}
	if (Character && Character->FlipSphereGrid())
	{
		RebuildGrid();
	}
}
