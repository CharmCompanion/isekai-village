// Copyright Epic Games, Inc. All Rights Reserved.
#include "BuildWheelWidget.h"
#include "BuildEditComponent.h"
#include "BuildPiece.h"
#include "LinchpinProp.h"
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
UTextBlock* WheelMakeText(UWidgetTree* Tree, const FString& Text, int32 Size = 15, FLinearColor Color = FLinearColor::White)
{
	UTextBlock* T = Tree->ConstructWidget<UTextBlock>();
	T->SetText(FText::FromString(Text));
	T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), Size));
	T->SetColorAndOpacity(FSlateColor(Color));
	T->SetAutoWrapText(true);
	return T;
}

UButton* WheelMakeButton(UWidgetTree* Tree, const FString& Caption, UTextBlock** OutLabel = nullptr)
{
	UButton* B = Tree->ConstructWidget<UButton>();
	UTextBlock* T = WheelMakeText(Tree, Caption, 14, FLinearColor(0.05f, 0.08f, 0.12f));
	B->AddChild(T);
	if (OutLabel) *OutLabel = T;
	return B;
}

void WheelRestoreInput(const UUserWidget* Widget, bool bOldCursor, bool& bRestored)
{
	if (bRestored) return;
	bRestored = true;
	if (APlayerController* PC = Widget->GetOwningPlayer())
	{
		PC->bShowMouseCursor = bOldCursor;
		PC->SetInputMode(FInputModeGameOnly());
	}
}
}

void UBuildWheelItemRow::InitializeRow(UBuildWheelWidget* InWheel, int32 InIndex)
{
	Wheel = InWheel;
	ItemIndex = InIndex;
}

TSharedRef<SWidget> UBuildWheelItemRow::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("WheelRowTree"));
	UBorder* RowBorder = WidgetTree->ConstructWidget<UBorder>();
	RowBorder->SetBrushColor(FLinearColor(0.04f, 0.07f, 0.11f, 0.85f));
	RowBorder->SetPadding(FMargin(10.0f, 6.0f));
	WidgetTree->RootWidget = RowBorder;

	UHorizontalBox* HBox = WidgetTree->ConstructWidget<UHorizontalBox>();
	RowBorder->AddChild(HBox);

	UVerticalBox* InfoVBox = WidgetTree->ConstructWidget<UVerticalBox>();
	HBox->AddChildToHorizontalBox(InfoVBox)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	TitleText = WheelMakeText(WidgetTree, TEXT("Item"), 15, FLinearColor(0.95f, 0.90f, 0.65f));
	InfoVBox->AddChildToVerticalBox(TitleText);

	CostText = WheelMakeText(WidgetTree, TEXT("Cost"), 13, FLinearColor(0.75f, 0.85f, 0.95f));
	InfoVBox->AddChildToVerticalBox(CostText);

	UTextBlock* LB = nullptr;
	SelectButton = WheelMakeButton(WidgetTree, TEXT("Equip"), &LB);
	SelectLabel = LB;
	SelectButton->OnClicked.AddDynamic(this, &UBuildWheelItemRow::HandleSelectClicked);
	HBox->AddChildToHorizontalBox(SelectButton)->SetPadding(FMargin(12.0f, 0.0f, 0.0f, 0.0f));

	RefreshRow();
	return Super::RebuildWidget();
}

void UBuildWheelItemRow::RefreshRow()
{
	if (!Wheel || !TitleText || !CostText || !SelectButton || !Wheel->GetCharacter())
	{
		return;
	}

	const TArray<FBuildWheelItem>& Items = Wheel->GetCurrentItems();
	if (!Items.IsValidIndex(ItemIndex))
	{
		return;
	}

	const FBuildWheelItem& Item = Items[ItemIndex];
	TitleText->SetText(Item.DisplayName);

	if (!Item.bUnlocked)
	{
		CostText->SetText(FText::FromString(FString::Printf(TEXT("Requires Tower Floor Tier %d (Locked)"), Item.MinTier)));
		CostText->SetColorAndOpacity(FSlateColor(FLinearColor(0.85f, 0.35f, 0.35f)));
		if (SelectLabel) SelectLabel->SetText(FText::FromString(TEXT("Locked")));
		SelectButton->SetIsEnabled(false);
		return;
	}

	FString CostStr;
	if (Item.CostAmount1 > 0)
	{
		const int32 Have1 = Wheel->GetCharacter()->Gather ? Wheel->GetCharacter()->Gather->GetCount(Item.CostRes1) : 0;
		CostStr += FString::Printf(TEXT("%s: %d/%d"), *Item.CostRes1.ToString(), Have1, Item.CostAmount1);
	}
	if (Item.CostAmount2 > 0)
	{
		const int32 Have2 = Wheel->GetCharacter()->Gather ? Wheel->GetCharacter()->Gather->GetCount(Item.CostRes2) : 0;
		CostStr += FString::Printf(TEXT(" | %s: %d/%d"), *Item.CostRes2.ToString(), Have2, Item.CostAmount2);
	}
	if (CostStr.IsEmpty())
	{
		CostStr = TEXT("Free Construction / Finish");
	}

	CostText->SetText(FText::FromString(CostStr));
	CostText->SetColorAndOpacity(FSlateColor(Item.bCanAfford ? FLinearColor(0.45f, 0.95f, 0.55f) : FLinearColor(0.95f, 0.45f, 0.45f)));

	if (SelectLabel)
	{
		SelectLabel->SetText(FText::FromString(FString::Printf(TEXT("[%d] Select"), ItemIndex + 1)));
	}
	SelectButton->SetIsEnabled(Item.bUnlocked);
}

void UBuildWheelItemRow::HandleSelectClicked()
{
	if (Wheel)
	{
		Wheel->SelectItemIndex(ItemIndex);
	}
}

void UBuildWheelWidget::InitializeWheel(UBuildEditComponent* InBuildComp, AIsekaiVillageCharacter* InCharacter)
{
	BuildComp = InBuildComp;
	Character = InCharacter;
	SetIsFocusable(true);

	if (APlayerController* PC = GetOwningPlayer())
	{
		bOldCursor = PC->bShowMouseCursor;
		PC->bShowMouseCursor = true;
		FInputModeGameAndUI Mode;
		Mode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		PC->SetInputMode(Mode);
	}

	PopulateCategoryItems();
}

TSharedRef<SWidget> UBuildWheelWidget::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("BuildWheelTree"));
	UCanvasPanel* Canvas = WidgetTree->ConstructWidget<UCanvasPanel>();
	WidgetTree->RootWidget = Canvas;

	USizeBox* Size = WidgetTree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(780.0f);
	Size->SetHeightOverride(580.0f);
	UCanvasPanelSlot* CS = Canvas->AddChildToCanvas(Size);
	CS->SetAnchors(FAnchors(0.5f, 0.5f));
	CS->SetAlignment(FVector2D(0.5f, 0.5f));
	CS->SetAutoSize(true);

	UBorder* Bg = WidgetTree->ConstructWidget<UBorder>();
	Bg->SetBrushColor(FLinearColor(0.02f, 0.035f, 0.055f, 0.96f));
	Bg->SetPadding(FMargin(18.0f));
	Size->AddChild(Bg);

	UVerticalBox* Main = WidgetTree->ConstructWidget<UVerticalBox>();
	Bg->AddChild(Main);

	HeaderTitleText = WheelMakeText(WidgetTree, TEXT("BUILD HUD & RADIAL CATALOG"), 22, FLinearColor(0.95f, 0.85f, 0.45f));
	Main->AddChildToVerticalBox(HeaderTitleText);

	TierInfoText = WheelMakeText(WidgetTree, TEXT("Tower Blueprints: Tier 1 Unlocked"), 14, FLinearColor(0.65f, 0.85f, 1.0f));
	Main->AddChildToVerticalBox(TierInfoText)->SetPadding(FMargin(0.0f, 3.0f, 0.0f, 6.0f));

	// Tab Buttons
	UHorizontalBox* Tabs = WidgetTree->ConstructWidget<UHorizontalBox>();
	Main->AddChildToVerticalBox(Tabs)->SetPadding(FMargin(0.0f, 0.0f, 0.0f, 10.0f));

	UTextBlock* T1 = nullptr;
	TabStructuresBtn = WheelMakeButton(WidgetTree, TEXT("[1] Structures & Walls"), &T1);
	TabStructuresBtn->OnClicked.AddDynamic(this, &UBuildWheelWidget::HandleCategoryStructures);
	if (UHorizontalBoxSlot* S1 = Tabs->AddChildToHorizontalBox(TabStructuresBtn))
	{
		S1->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	}

	UTextBlock* T2 = nullptr;
	TabFurnitureBtn = WheelMakeButton(WidgetTree, TEXT("[2] Linchpin Workstations"), &T2);
	TabFurnitureBtn->OnClicked.AddDynamic(this, &UBuildWheelWidget::HandleCategoryFurniture);
	if (UHorizontalBoxSlot* S2 = Tabs->AddChildToHorizontalBox(TabFurnitureBtn))
	{
		S2->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
		S2->SetPadding(FMargin(6.0f, 0.0f, 6.0f, 0.0f));
	}

	UTextBlock* T3 = nullptr;
	TabMaterialsBtn = WheelMakeButton(WidgetTree, TEXT("[3] Materials & Wallpapers"), &T3);
	TabMaterialsBtn->OnClicked.AddDynamic(this, &UBuildWheelWidget::HandleCategoryMaterials);
	if (UHorizontalBoxSlot* S3 = Tabs->AddChildToHorizontalBox(TabMaterialsBtn))
	{
		S3->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	}

	// Items List Scroll
	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Main->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	ItemsListVerticalBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(ItemsListVerticalBox);

	// Footer / Hints
	UHorizontalBox* Footer = WidgetTree->ConstructWidget<UHorizontalBox>();
	Main->AddChildToVerticalBox(Footer)->SetPadding(FMargin(0.0f, 8.0f, 0.0f, 0.0f));

	HelpHintText = WheelMakeText(WidgetTree, TEXT("Press 1-9 to quick-equip | Tab to cycle tabs | Esc / B to close wheel"), 13, FLinearColor(0.85f, 0.80f, 0.65f));
	Footer->AddChildToHorizontalBox(HelpHintText)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UButton* CloseBtn = WheelMakeButton(WidgetTree, TEXT("Close (Esc)"));
	CloseBtn->OnClicked.AddDynamic(this, &UBuildWheelWidget::HandleCloseClicked);
	Footer->AddChildToHorizontalBox(CloseBtn)->SetPadding(FMargin(10.0f, 0.0f, 0.0f, 0.0f));

	RefreshItems();
	return Super::RebuildWidget();
}

void UBuildWheelWidget::PopulateCategoryItems()
{
	CurrentItems.Reset();
	const int32 Tier = BuildComp ? BuildComp->GetUnlockedTier() : 1;

	if (CurrentCategory == EBuildWheelCategory::Structures)
	{
		auto AddStruct = [&](const TCHAR* Name, FName Id, EBuildPieceType Type, EBuildWallStyle Style)
		{
			FBuildWheelItem Item;
			Item.DisplayName = FText::FromString(Name);
			Item.Identifier = Id;
			Item.CostRes1 = TEXT("Wood");
			Item.CostAmount1 = 2;
			Item.CostRes2 = TEXT("Stone");
			Item.CostAmount2 = 1;
			Item.bUnlocked = true;
			const int32 HaveW = Character && Character->Gather ? Character->Gather->GetCount(TEXT("Wood")) : 0;
			const int32 HaveS = Character && Character->Gather ? Character->Gather->GetCount(TEXT("Stone")) : 0;
			Item.bCanAfford = (HaveW >= 2 && HaveS >= 1);
			CurrentItems.Add(Item);
		};

		AddStruct(TEXT("Wall (Straight 200cm)"), TEXT("Wall_Straight"), EBuildPieceType::Wall, EBuildWallStyle::Straight);
		AddStruct(TEXT("Wall (Curved Arc 90deg)"), TEXT("Wall_Curved"), EBuildPieceType::Wall, EBuildWallStyle::CurvedArc);
		AddStruct(TEXT("Wall (45 Diagonal)"), TEXT("Wall_Diagonal"), EBuildPieceType::Wall, EBuildWallStyle::Diagonal45);
		AddStruct(TEXT("Doorway Opening"), TEXT("Doorway"), EBuildPieceType::Doorway, EBuildWallStyle::Straight);
		AddStruct(TEXT("Foundation Block"), TEXT("Foundation"), EBuildPieceType::Foundation, EBuildWallStyle::Straight);
		AddStruct(TEXT("Floor / Ceiling Slab"), TEXT("Floor"), EBuildPieceType::Floor, EBuildWallStyle::Straight);
		AddStruct(TEXT("Staircase"), TEXT("Stair"), EBuildPieceType::Stair, EBuildWallStyle::Straight);
		AddStruct(TEXT("Gabled Roof"), TEXT("Roof"), EBuildPieceType::Roof, EBuildWallStyle::Straight);
		AddStruct(TEXT("Support Pillar"), TEXT("Pillar"), EBuildPieceType::Pillar, EBuildWallStyle::Straight);
	}
	else if (CurrentCategory == EBuildWheelCategory::Furniture)
	{
		const TArray<FName> AllProps = {
			TEXT("Anvil"), TEXT("Forge"), TEXT("Bed"), TEXT("Counter"),
			TEXT("Oven"), TEXT("Workbench"), TEXT("Chest"), TEXT("Crate"),
			TEXT("Cauldron"), TEXT("HerbRack"), TEXT("ArcaneTable"), TEXT("CrystalFocus"),
			TEXT("CelestialAnvil"), TEXT("RunicCrucible")
		};

		for (const FName& PropTag : AllProps)
		{
			FBuildWheelItem Item;
			Item.Identifier = PropTag;
			Item.DisplayName = FText::FromString(PropTag.ToString());
			UBuildEditComponent::GetPropCraftCost(PropTag, Item.CostRes1, Item.CostAmount1, Item.CostRes2, Item.CostAmount2);

			if (PropTag == TEXT("Cauldron") || PropTag == TEXT("HerbRack") || PropTag == TEXT("ArcaneTable") || PropTag == TEXT("CrystalFocus"))
			{
				Item.MinTier = 2;
			}
			else if (PropTag == TEXT("CelestialAnvil") || PropTag == TEXT("RunicCrucible"))
			{
				Item.MinTier = 4;
			}
			else
			{
				Item.MinTier = 1;
			}

			Item.bUnlocked = (Tier >= Item.MinTier);
			const int32 H1 = Character && Character->Gather ? Character->Gather->GetCount(Item.CostRes1) : 0;
			const int32 H2 = Character && Character->Gather ? Character->Gather->GetCount(Item.CostRes2) : 0;
			Item.bCanAfford = (H1 >= Item.CostAmount1 && H2 >= Item.CostAmount2);
			CurrentItems.Add(Item);
		}
	}
	else if (CurrentCategory == EBuildWheelCategory::Materials)
	{
		const TCHAR* Mats[] = {
			TEXT("Wood Plank"), TEXT("Field Stone"), TEXT("Cut Stone"), TEXT("Brick"),
			TEXT("Metal Sheet"), TEXT("White Plaster"), TEXT("Wallpaper Stripes"), TEXT("Wallpaper Floral"), TEXT("Wood Wainscot")
		};

		for (int32 I = 0; I < 9; ++I)
		{
			FBuildWheelItem Item;
			Item.DisplayName = FText::FromString(Mats[I]);
			Item.Identifier = FName(*FString::Printf(TEXT("Mat_%d"), I));
			Item.bUnlocked = true;
			Item.bCanAfford = true;
			CurrentItems.Add(Item);
		}
	}
}

void UBuildWheelWidget::RefreshItems()
{
	PopulateCategoryItems();
	if (!ItemsListVerticalBox)
	{
		return;
	}

	ItemsListVerticalBox->ClearChildren();
	ItemRows.Reset();

	if (TierInfoText && BuildComp)
	{
		const int32 Tier = BuildComp->GetUnlockedTier();
		TierInfoText->SetText(FText::FromString(FString::Printf(TEXT("Tower Progress: Tier %d Blueprints Active | %s Mode"),
			Tier, CurrentCategory == EBuildWheelCategory::Structures ? TEXT("Structural Pieces") :
			CurrentCategory == EBuildWheelCategory::Furniture ? TEXT("Linchpin Workstations") : TEXT("Wall Finishes & Mats"))));
	}

	for (int32 I = 0; I < CurrentItems.Num(); ++I)
	{
		UBuildWheelItemRow* Row = CreateWidget<UBuildWheelItemRow>(this);
		if (Row)
		{
			Row->InitializeRow(this, I);
			ItemsListVerticalBox->AddChildToVerticalBox(Row)->SetPadding(FMargin(0.0f, 2.0f, 0.0f, 2.0f));
			ItemRows.Add(Row);
		}
	}
}

void UBuildWheelWidget::SetCategory(EBuildWheelCategory NewCategory)
{
	CurrentCategory = NewCategory;
	RefreshItems();
}

void UBuildWheelWidget::SelectItemIndex(int32 Index)
{
	if (!CurrentItems.IsValidIndex(Index) || !BuildComp)
	{
		return;
	}

	const FBuildWheelItem& Item = CurrentItems[Index];
	if (!Item.bUnlocked)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Red, FString::Printf(TEXT("Item locked! Clear Floor Tier %d to unlock."), Item.MinTier));
		}
		return;
	}

	if (CurrentCategory == EBuildWheelCategory::Structures)
	{
		BuildComp->bPlacingProps = false;
		if (Item.Identifier == TEXT("Wall_Straight"))
		{
			BuildComp->CurrentType = EBuildPieceType::Wall;
			BuildComp->CurrentWallStyle = EBuildWallStyle::Straight;
		}
		else if (Item.Identifier == TEXT("Wall_Curved"))
		{
			BuildComp->CurrentType = EBuildPieceType::Wall;
			BuildComp->CurrentWallStyle = EBuildWallStyle::CurvedArc;
		}
		else if (Item.Identifier == TEXT("Wall_Diagonal"))
		{
			BuildComp->CurrentType = EBuildPieceType::Wall;
			BuildComp->CurrentWallStyle = EBuildWallStyle::Diagonal45;
		}
		else if (Item.Identifier == TEXT("Doorway"))
		{
			BuildComp->CurrentType = EBuildPieceType::Doorway;
		}
		else if (Item.Identifier == TEXT("Foundation"))
		{
			BuildComp->CurrentType = EBuildPieceType::Foundation;
		}
		else if (Item.Identifier == TEXT("Floor"))
		{
			BuildComp->CurrentType = EBuildPieceType::Floor;
		}
		else if (Item.Identifier == TEXT("Stair"))
		{
			BuildComp->CurrentType = EBuildPieceType::Stair;
		}
		else if (Item.Identifier == TEXT("Roof"))
		{
			BuildComp->CurrentType = EBuildPieceType::Roof;
		}
		else if (Item.Identifier == TEXT("Pillar"))
		{
			BuildComp->CurrentType = EBuildPieceType::Pillar;
		}
		if (BuildComp->SelectedPiece)
		{
			BuildComp->SelectedPiece->PieceType = BuildComp->CurrentType;
			BuildComp->SelectedPiece->WallStyle = BuildComp->CurrentWallStyle;
			BuildComp->SelectedPiece->RebuildMesh();
		}
	}
	else if (CurrentCategory == EBuildWheelCategory::Furniture)
	{
		BuildComp->bPlacingProps = true;
		BuildComp->CurrentPropTag = Item.Identifier;
		if (BuildComp->SelectedProp)
		{
			BuildComp->SelectedProp->SetupProp(BuildComp->CurrentPropTag);
		}
	}
	else if (CurrentCategory == EBuildWheelCategory::Materials)
	{
		const int32 MatIdx = FMath::Clamp(Index, 0, 8);
		BuildComp->CurrentMaterials.ExteriorMaterial = static_cast<EBuildMaterialStyle>(MatIdx);
		BuildComp->CurrentMaterials.InteriorMaterial = static_cast<EBuildMaterialStyle>(MatIdx);
		if (BuildComp->SelectedPiece)
		{
			BuildComp->SelectedPiece->MaterialConfig = BuildComp->CurrentMaterials;
			BuildComp->SelectedPiece->RebuildMesh();
		}
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Emerald, FString::Printf(TEXT("Equipped: %s"), *Item.DisplayName.ToString()));
	}

	CloseWheel();
}

void UBuildWheelWidget::CloseWheel()
{
	WheelRestoreInput(this, bOldCursor, bRestoredInput);
	RemoveFromParent();
	if (BuildComp)
	{
		BuildComp->BuildWheelWidget = nullptr;
	}
}

void UBuildWheelWidget::NativeTick(const FGeometry& Geometry, float DeltaSeconds)
{
	Super::NativeTick(Geometry, DeltaSeconds);
}

void UBuildWheelWidget::NativeDestruct()
{
	WheelRestoreInput(this, bOldCursor, bRestoredInput);
	Super::NativeDestruct();
}

FReply UBuildWheelWidget::NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	const FKey Key = Event.GetKey();
	if (Key == EKeys::Escape || Key == EKeys::B)
	{
		CloseWheel();
		return FReply::Handled();
	}
	if (Key == EKeys::Tab)
	{
		const int32 Next = (static_cast<int32>(CurrentCategory) + 1) % 3;
		SetCategory(static_cast<EBuildWheelCategory>(Next));
		return FReply::Handled();
	}
	if (Key == EKeys::One) { SelectItemIndex(0); return FReply::Handled(); }
	if (Key == EKeys::Two) { SelectItemIndex(1); return FReply::Handled(); }
	if (Key == EKeys::Three) { SelectItemIndex(2); return FReply::Handled(); }
	if (Key == EKeys::Four) { SelectItemIndex(3); return FReply::Handled(); }
	if (Key == EKeys::Five) { SelectItemIndex(4); return FReply::Handled(); }
	if (Key == EKeys::Six) { SelectItemIndex(5); return FReply::Handled(); }
	if (Key == EKeys::Seven) { SelectItemIndex(6); return FReply::Handled(); }
	if (Key == EKeys::Eight) { SelectItemIndex(7); return FReply::Handled(); }
	if (Key == EKeys::Nine) { SelectItemIndex(8); return FReply::Handled(); }

	return Super::NativeOnKeyDown(Geometry, Event);
}

void UBuildWheelWidget::HandleCategoryStructures()
{
	SetCategory(EBuildWheelCategory::Structures);
}

void UBuildWheelWidget::HandleCategoryFurniture()
{
	SetCategory(EBuildWheelCategory::Furniture);
}

void UBuildWheelWidget::HandleCategoryMaterials()
{
	SetCategory(EBuildWheelCategory::Materials);
}

void UBuildWheelWidget::HandleCloseClicked()
{
	CloseWheel();
}
