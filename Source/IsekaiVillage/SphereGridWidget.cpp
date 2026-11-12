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
		if (DiscIndex >= 0)
		{
			Widget->HandleDiscClicked(DiscIndex);
		}
		else
		{
			Widget->HandleNodeClicked(NodeID);
		}
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

	HeaderText = AddText(TEXT("HeaderText"), FVector2D(260.0f, 22.0f), 26);
	StatusText = AddText(TEXT("StatusText"), FVector2D(260.0f, 58.0f), 16);

	FlipButton = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), TEXT("FlipButton"));
	UCanvasPanelSlot* FlipSlot = RootCanvas->AddChildToCanvas(FlipButton);
	FlipSlot->SetPosition(FVector2D(260.0f, 88.0f));
	FlipSlot->SetSize(FVector2D(220.0f, 36.0f));
	UTextBlock* FlipLabel = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), TEXT("FlipLabel"));
	FlipLabel->SetText(NSLOCTEXT("IsekaiVillage", "FlipCoin", "Flip Coin"));
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
	for (UButton* Button : DiscButtons)
	{
		if (Button)
		{
			Button->RemoveFromParent();
		}
	}
	NodeButtons.Reset();
	NodeLabels.Reset();
	DiscButtons.Reset();
	DiscLabels.Reset();
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

	USphereGridDataAsset* Grid = Character->SphereGrid;
	for (int32 D = 0; D < Grid->DiscCount(); ++D)
	{
		UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), *FString::Printf(TEXT("DiscBtn_%d"), D));
		UCanvasPanelSlot* CanvasSlot = RootCanvas->AddChildToCanvas(Button);
		CanvasSlot->SetPosition(FVector2D(24.0f, 22.0f + D * 42.0f));
		CanvasSlot->SetSize(FVector2D(214.0f, 36.0f));

		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), *FString::Printf(TEXT("DiscLbl_%d"), D));
		FSlateFontInfo Font = Label->GetFont();
		Font.Size = 11;
		Label->SetFont(Font);
		Button->AddChild(Label);

		USphereNodeClickTarget* Target = NewObject<USphereNodeClickTarget>(this);
		Target->DiscIndex = D;
		Target->Owner = this;
		Button->OnClicked.AddDynamic(Target, &USphereNodeClickTarget::HandleClicked);

		DiscButtons.Add(Button);
		DiscLabels.Add(Label);
		ClickTargets.Add(Target);
	}

	const TArray<FName>& Order = Grid->FaceOrder(Character->SphereDisc, Character->SphereFaceFlipped());

	const FVector2D Center(760.0f, 415.0f);
	const float Radius = 235.0f;
	const int32 Count = Order.Num();
	for (int32 Index = 0; Index < Count; ++Index)
	{
		const float Angle = (2.0f * PI * Index) / FMath::Max(Count, 1) - PI * 0.5f;
		const FVector2D Position = Center + FVector2D(FMath::Cos(Angle), FMath::Sin(Angle)) * Radius;

		UButton* Button = WidgetTree->ConstructWidget<UButton>(UButton::StaticClass(), *FString::Printf(TEXT("NodeBtn_%d"), Index));
		UCanvasPanelSlot* CanvasSlot = RootCanvas->AddChildToCanvas(Button);
		CanvasSlot->SetPosition(Position - FVector2D(66.0f, 28.0f));
		CanvasSlot->SetSize(FVector2D(132.0f, 56.0f));

		UTextBlock* Label = WidgetTree->ConstructWidget<UTextBlock>(UTextBlock::StaticClass(), *FString::Printf(TEXT("NodeLbl_%d"), Index));
		FSlateFontInfo Font = Label->GetFont();
		Font.Size = 10;
		Label->SetFont(Font);
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
	const int32 Disc = FMath::Clamp(Character->SphereDisc, 0, Grid->DiscCount() - 1);
	const bool bFlipped = Character->SphereFaceFlipped();
	const bool bDiscUnlocked = Grid->IsDiscUnlocked(Disc, Character->UnlockedSphereNodes);
	HeaderText->SetText(FText::FromString(FString::Printf(TEXT("[%s] %s%s"),
		*Grid->DiscCategoryLabel(Disc).ToString(),
		*Grid->DiscDisplayTitle(Disc, bFlipped).ToString(),
		bDiscUnlocked ? TEXT("") : TEXT(" [LOCKED]"))));

	const FSphereGridStatTotals& T = Character->SphereTotals;
	StatusText->SetText(FText::FromString(FString::Printf(
		TEXT("SP %d | HP +%d TP +%d Atk +%d Mag +%d Res +%.0f%% | Inv +%d Carry +%dkg Build -%.0f%% Attract +%.0f%% Pace +%.0f%% Trust +%d%s"),
		Character->SpherePoints, T.HP, T.TP, T.Attack, T.Magic, T.ResPercent,
		T.Inventory, T.CarryWeight, T.BuildSpeedPercent, T.AttractionPercent, T.WorkerPacePercent, T.Trust,
		bDiscUnlocked ? TEXT("") : *FString::Printf(TEXT("\nUnlock: %s"), *Grid->DiscUnlockHint(Disc).ToString()))));

	for (int32 D = 0; D < DiscButtons.Num() && D < Grid->DiscCount(); ++D)
	{
		const bool bDUnlocked = Grid->IsDiscUnlocked(D, Character->UnlockedSphereNodes);
		const bool bDComplete = Grid->DiscHasFlip(D)
			? (Grid->IsFaceComplete(D, false, Character->UnlockedSphereNodes) && Grid->IsFaceComplete(D, true, Character->UnlockedSphereNodes))
			: Grid->IsFaceComplete(D, false, Character->UnlockedSphereNodes);
		const bool bSelected = (D == Disc);
		if (DiscLabels.IsValidIndex(D) && DiscLabels[D])
		{
			const FString Title = Grid->DiscDisplayTitle(D, bSelected ? bFlipped : false).ToString();
			DiscLabels[D]->SetText(FText::FromString(bDUnlocked ? Title : FString::Printf(TEXT("[Lock] %s"), *Title)));
		}
		if (DiscButtons[D])
		{
			FLinearColor Tint = bSelected
				? FLinearColor(0.14f, 0.55f, 0.92f)
				: (bDComplete ? FLinearColor(0.12f, 0.52f, 0.36f)
					: (bDUnlocked ? FLinearColor(0.18f, 0.25f, 0.38f) : FLinearColor(0.12f, 0.12f, 0.16f)));
			DiscButtons[D]->SetBackgroundColor(Tint);
		}
	}

	if (FlipButton)
	{
		const bool bCanFlip = bDiscUnlocked && Grid->DiscHasFlip(Disc) && !bFlipped && Grid->IsFaceComplete(Disc, false, Character->UnlockedSphereNodes);
		FlipButton->SetIsEnabled(bCanFlip);
		FlipButton->SetVisibility(bCanFlip ? ESlateVisibility::Visible : ESlateVisibility::Collapsed);
	}

	const TArray<FName>& Order = Grid->FaceOrder(Disc, bFlipped);
	for (int32 Index = 0; Index < NodeButtons.Num() && Index < Order.Num(); ++Index)
	{
		const FName NodeID = Order[Index];
		FSphereNode Node;
		Grid->GetNode(NodeID, Node);

		const bool bUnlocked = Character->UnlockedSphereNodes.Contains(NodeID);
		const bool bAdjacent = Grid->IsNodeAdjacentOnDisc(NodeID, Character->UnlockedSphereNodes, Disc, bFlipped);
		if (NodeLabels.IsValidIndex(Index) && NodeLabels[Index])
		{
			NodeLabels[Index]->SetText(Node.DisplayName);
		}
		if (NodeButtons[Index])
		{
			const bool bStartFree = bAdjacent && !Grid->HasUnlockedOnDisc(Disc, bFlipped, Character->UnlockedSphereNodes);
			NodeButtons[Index]->SetIsEnabled(!bUnlocked && bAdjacent && (bStartFree || Character->SpherePoints > 0));
			NodeButtons[Index]->SetToolTipText(Node.Description);
			FLinearColor Tint = bUnlocked
				? FLinearColor(0.15f, 0.55f, 0.95f)
				: (bAdjacent ? FLinearColor(0.95f, 0.75f, 0.2f) : FLinearColor(0.2f, 0.22f, 0.28f));
			NodeButtons[Index]->SetBackgroundColor(Tint);
		}
	}
}

void USphereGridWidget::HandleDiscClicked(int32 DiscIndex)
{
	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwningPlayerPawn());
	if (!Character)
	{
		Character = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this, 0));
	}
	if (Character && Character->SelectSphereDisc(DiscIndex))
	{
		RebuildGrid();
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
