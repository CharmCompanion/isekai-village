// Copyright Epic Games, Inc. All Rights Reserved.

#include "ShopForgeWidget.h"
#include "VillageRuntime.h"
#include "BlacksmithForge.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
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
#include "Styling/CoreStyle.h"
#include "InputCoreTypes.h"

namespace
{
UTextBlock* MakePanelText(UWidgetTree* Tree, const FString& Value, int32 Size = 15, FLinearColor Color = FLinearColor(0.95f, 0.96f, 0.98f))
{
	UTextBlock* T = Tree->ConstructWidget<UTextBlock>();
	T->SetText(FText::FromString(Value));
	T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"), Size));
	T->SetColorAndOpacity(FSlateColor(Color));
	T->SetAutoWrapText(true);
	return T;
}

UButton* MakePanelButton(UWidgetTree* Tree, const FString& Caption, UTextBlock** OutLabel = nullptr, FName Name = NAME_None)
{
	UButton* B = Tree->ConstructWidget<UButton>(UButton::StaticClass(), Name);
	UTextBlock* T = MakePanelText(Tree, Caption, 14, FLinearColor(0.05f, 0.07f, 0.1f));
	B->AddChild(T);
	if (OutLabel) *OutLabel = T;
	return B;
}

UVerticalBox* BuildModalFrame(UWidgetTree* Tree, int32 Width, int32 Height, const FString& Title, const FString& Subtitle)
{
	UCanvasPanel* Canvas = Tree->ConstructWidget<UCanvasPanel>();
	Tree->RootWidget = Canvas;
	USizeBox* Size = Tree->ConstructWidget<USizeBox>();
	Size->SetWidthOverride(static_cast<float>(Width));
	Size->SetHeightOverride(static_cast<float>(Height));
	if (UCanvasPanelSlot* CS = Canvas->AddChildToCanvas(Size))
	{
		CS->SetAnchors(FAnchors(0.5f, 0.5f));
		CS->SetAlignment(FVector2D(0.5f, 0.5f));
		CS->SetAutoSize(true);
	}
	UBorder* BG = Tree->ConstructWidget<UBorder>();
	BG->SetBrushColor(FLinearColor(0.03f, 0.045f, 0.07f, 0.97f));
	BG->SetPadding(FMargin(18.0f));
	Size->AddChild(BG);
	UVerticalBox* Main = Tree->ConstructWidget<UVerticalBox>();
	BG->AddChild(Main);
	Main->AddChildToVerticalBox(MakePanelText(Tree, Title, 24, FLinearColor(0.97f, 0.87f, 0.45f)));
	Main->AddChildToVerticalBox(MakePanelText(Tree, Subtitle, 14, FLinearColor(0.80f, 0.85f, 0.92f)))->SetPadding(FMargin(0, 2, 0, 8));
	return Main;
}

void RestoreModalInput(UUserWidget* Widget, bool bOldCursor, bool& bRestored)
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

void UShopRow::InitializeRow(UShopWidget* InShop, FName InItemId)
{
	Shop = InShop;
	ItemId = InItemId;
}

TSharedRef<SWidget> UShopRow::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("ShopRowTree"));
	UBorder* Border = WidgetTree->ConstructWidget<UBorder>();
	Border->SetBrushColor(FLinearColor(0.075f, 0.105f, 0.16f, 0.95f));
	Border->SetPadding(FMargin(10.0f, 8.0f));
	WidgetTree->RootWidget = Border;

	UHorizontalBox* Row = WidgetTree->ConstructWidget<UHorizontalBox>();
	Border->AddChild(Row);
	Details = MakePanelText(WidgetTree, TEXT(""), 15);
	Row->AddChildToHorizontalBox(Details)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UTextBlock* BuyLbl = nullptr;
	BuyButton = MakePanelButton(WidgetTree, TEXT("Buy"), &BuyLbl);
	BuyLabel = BuyLbl;
	BuyButton->OnClicked.AddDynamic(this, &UShopRow::HandleBuy);
	Row->AddChildToHorizontalBox(BuyButton)->SetPadding(FMargin(8, 0, 4, 0));

	UTextBlock* SellLbl = nullptr;
	SellButton = MakePanelButton(WidgetTree, TEXT("Sell"), &SellLbl);
	SellLabel = SellLbl;
	SellButton->OnClicked.AddDynamic(this, &UShopRow::HandleSell);
	Row->AddChildToHorizontalBox(SellButton);

	RefreshRow();
	return Super::RebuildWidget();
}

void UShopRow::RefreshRow()
{
	if (!Shop || !Details || !BuyButton || !SellButton) return;
	AVillageRuntime* V = Shop->GetVillage();
	AIsekaiVillageCharacter* P = Shop->GetPlayer();
	const FVillageShopOffer* O = AVillageRuntime::FindShopOffer(ItemId);
	if (!V || !P || !P->Gather || !O) return;

	const FName Plot = Shop->GetShopPlot();
	const int32 ShopStock = V->GetShopItemStock(Plot, ItemId);
	const int32 BagCount = P->Gather->GetCount(ItemId);
	const int32 BuyCost = V->GetShopBuyPrice(ItemId, P);
	const int32 SellPay = V->GetShopSellPrice(ItemId, P);
	const bool bStaffed = V->IsShopStaffed(Plot);
	const bool bUnlocked = V->IsShopOfferUnlocked(ItemId);

	int32 TillCoins = 0;
	if (const FVillageShopState* State = V->GolemShops.FindByPredicate([&](const FVillageShopState& S) { return S.Plot == Plot; }))
	{
		TillCoins = State->Coins;
	}

	const FString LockNote = bUnlocked ? FString() : TEXT(" [Locked]");
	Details->SetText(FText::FromString(FString::Printf(TEXT("%s (%s)%s\nShop stock: %d   |   In pack: %d"),
		*O->DisplayName, *O->Category, *LockNote, ShopStock, BagCount)));

	BuyLabel->SetText(FText::FromString(FString::Printf(TEXT("Buy (-%dc)"), BuyCost)));
	SellLabel->SetText(FText::FromString(FString::Printf(TEXT("Sell (+%dc)"), SellPay)));
	BuyButton->SetIsEnabled(bStaffed && bUnlocked && ShopStock > 0 && P->Gather->GetCount(TEXT("Coin")) >= BuyCost);
	SellButton->SetIsEnabled(bStaffed && BagCount > 0 && TillCoins >= SellPay);
}

void UShopRow::HandleBuy()
{
	if (Shop) Shop->ExecuteTrade(ItemId, true);
}

void UShopRow::HandleSell()
{
	if (Shop) Shop->ExecuteTrade(ItemId, false);
}

void UShopWidget::InitializeShop(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer, FName InShopPlot)
{
	Village = InVillage;
	Player = InPlayer;
	ShopPlot = InShopPlot;
	SetIsFocusable(true);
	if (APlayerController* PC = GetOwningPlayer()) bOldCursor = PC->bShowMouseCursor;
}

TSharedRef<SWidget> UShopWidget::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("ShopTree"));
	UVerticalBox* Main = BuildModalFrame(WidgetTree, 760, 740,
		TEXT("EL RUHN GENERAL STORE"),
		TEXT("Buy provisions for the Tower or sell extra timber, ore, crystals, and smith-crafted Tool Parts. (T/Y still quick-trade Wood.)"));

	HeaderStatus = MakePanelText(WidgetTree, TEXT(""), 15, FLinearColor(0.85f, 0.94f, 1.0f));
	Main->AddChildToVerticalBox(HeaderStatus)->SetPadding(FMargin(0, 0, 0, 6));

	MessageText = MakePanelText(WidgetTree, TEXT(""), 15, FLinearColor(1.0f, 0.84f, 0.42f));
	Main->AddChildToVerticalBox(MessageText)->SetPadding(FMargin(0, 0, 0, 8));

	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Main->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	CatalogBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(CatalogBox);

	UButton* CloseBtn = MakePanelButton(WidgetTree, TEXT("Close (Esc / U)"), nullptr, TEXT("CloseShopButton"));
	CloseBtn->OnClicked.AddDynamic(this, &UShopWidget::CloseShop);
	Main->AddChildToVerticalBox(CloseBtn)->SetPadding(FMargin(0, 10, 0, 0));

	RefreshShop();
	return Super::RebuildWidget();
}

void UShopWidget::RefreshNumbers()
{
	if (!Village || !Player || !Player->Gather || !HeaderStatus) return;
	const FVillageShopState* Shop = Village->GolemShops.FindByPredicate([&](const FVillageShopState& S) { return S.Plot == ShopPlot; });
	const bool bStaffed = Village->IsShopStaffed(ShopPlot);
	const FString Keeper = Village->ShopKeeperName(ShopPlot);
	const int32 Till = Shop ? Shop->Coins : 0;
	const bool bHaggle = Player->HasSphereSkill(TEXT("ShopHaggle"));
	const int32 Gald = Player->SphereTotals.GaldPercent;

	HeaderStatus->SetText(FText::FromString(FString::Printf(
		TEXT("Keeper: %s (%s)  |  Till: %d Coin  |  Your Coin: %d%s%s"),
		*Keeper,
		bStaffed ? TEXT("OPEN") : TEXT("CLOSED / AWAY"),
		Till,
		Player->Gather->GetCount(TEXT("Coin")),
		bHaggle ? TEXT("  |  ShopHaggle") : TEXT(""),
		Gald > 0 ? *FString::Printf(TEXT(" (+%d%% Gald)"), Gald) : TEXT(""))));

	if (MessageText)
	{
		MessageText->SetText(FText::FromString(Village->LastShopMessage.IsEmpty()
			? (bStaffed ? TEXT("Select an item below to buy or sell.") : TEXT("Counter closed while the keeper is resting or commuting."))
			: Village->LastShopMessage));
	}
}

void UShopWidget::RefreshShop()
{
	if (!CatalogBox) return;
	CatalogBox->ClearChildren();
	Rows.Reset();
	for (const FVillageShopOffer& O : AVillageRuntime::ShopCatalog())
	{
		UShopRow* Row = CreateWidget<UShopRow>(GetOwningPlayer());
		Row->InitializeRow(this, O.ItemId);
		CatalogBox->AddChildToVerticalBox(Row)->SetPadding(FMargin(0, 0, 0, 6));
		Rows.Add(Row);
	}
	RefreshNumbers();
}

bool UShopWidget::ExecuteTrade(FName ItemId, bool bBuy)
{
	const bool bOk = Village && Village->TradeShopItem(ShopPlot, ItemId, bBuy, Player);
	RefreshNumbers();
	for (UShopRow* Row : Rows) if (Row) Row->RefreshRow();
	return bOk;
}

void UShopWidget::NativeTick(const FGeometry& Geometry, float DeltaSeconds)
{
	Super::NativeTick(Geometry, DeltaSeconds);
	RefreshIn -= DeltaSeconds;
	if (RefreshIn <= 0.0f)
	{
		RefreshIn = 0.4f;
		RefreshNumbers();
		for (UShopRow* Row : Rows) if (Row) Row->RefreshRow();
	}
}

void UShopWidget::CloseShop()
{
	RestoreModalInput(this, bOldCursor, bRestoredInput);
	RemoveFromParent();
}

void UShopWidget::NativeDestruct()
{
	RestoreModalInput(this, bOldCursor, bRestoredInput);
	Super::NativeDestruct();
}

FReply UShopWidget::NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::U)
	{
		CloseShop();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(Geometry, Event);
}

void UForgeMemberRow::InitializeRow(UForgeWidget* InForge, FName InAdventurerId)
{
	ForgeWidget = InForge;
	AdventurerId = InAdventurerId;
}

TSharedRef<SWidget> UForgeMemberRow::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("ForgeMemberRowTree"));
	UBorder* Border = WidgetTree->ConstructWidget<UBorder>();
	Border->SetBrushColor(FLinearColor(0.08f, 0.10f, 0.15f, 0.95f));
	Border->SetPadding(FMargin(10.0f, 8.0f));
	WidgetTree->RootWidget = Border;

	UHorizontalBox* Box = WidgetTree->ConstructWidget<UHorizontalBox>();
	Border->AddChild(Box);
	Details = MakePanelText(WidgetTree, TEXT(""), 15);
	Box->AddChildToHorizontalBox(Details)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));

	UTextBlock* Label = nullptr;
	TemperButton = MakePanelButton(WidgetTree, TEXT("Temper"), &Label);
	TemperLabel = Label;
	TemperButton->OnClicked.AddDynamic(this, &UForgeMemberRow::HandleTemper);
	Box->AddChildToHorizontalBox(TemperButton)->SetPadding(FMargin(8, 0, 0, 0));

	RefreshRow();
	return Super::RebuildWidget();
}

void UForgeMemberRow::RefreshRow()
{
	if (!ForgeWidget || !Details || !TemperButton) return;
	AIsekaiVillageCharacter* P = ForgeWidget->GetPlayer();
	if (!P || !P->Gather || !P->PartyReserve) return;
	const FHiredAdventurer* A = P->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X) { return X.AdventurerID == AdventurerId; });
	if (!A) return;

	const int32 PartsCost = UGatherInventoryComponent::ForgeCost(P, 2);
	Details->SetText(FText::FromString(FString::Printf(
		TEXT("%s (%s | %s)   Wpn T%d | Arm T%d | Temper +%d"),
		*A->Name.ToString(),
		A->ClassId.IsNone() ? TEXT("Adventurer") : *A->ClassId.ToString(),
		A->bInActiveParty ? TEXT("Active") : TEXT("Reserve"),
		A->WeaponTier, A->ArmorTier, A->TemperLevel)));

	if (A->TemperLevel >= 2)
	{
		TemperLabel->SetText(FText::FromString(TEXT("Max +2")));
		TemperButton->SetIsEnabled(false);
	}
	else
	{
		TemperLabel->SetText(FText::FromString(FString::Printf(TEXT("Temper +%d (%d Parts)"), A->TemperLevel + 1, PartsCost)));
		TemperButton->SetIsEnabled(P->Gather->GetCount(TEXT("ToolParts")) >= PartsCost);
	}
}

void UForgeMemberRow::HandleTemper()
{
	if (ForgeWidget) ForgeWidget->TemperAdventurer(AdventurerId);
}

void UForgeWidget::InitializeForge(ABlacksmithForge* InForge, AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer)
{
	Forge = InForge;
	Village = InVillage;
	Player = InPlayer;
	SetIsFocusable(true);
	if (APlayerController* PC = GetOwningPlayer()) bOldCursor = PC->bShowMouseCursor;
}

TSharedRef<SWidget> UForgeWidget::RebuildWidget()
{
	WidgetTree = NewObject<UWidgetTree>(this, TEXT("ForgeTree"));
	UVerticalBox* Main = BuildModalFrame(WidgetTree, 760, 760,
		TEXT("VILLAGE BLACKSMITH & TOOLBENCH"),
		TEXT("Upgrade tools, forge Iron/Runic battle gear, or spend Tool Parts to temper adventurer gear (+5% DEF & +4 ATK per rank) or fortify town walls."));

	StockSummary = MakePanelText(WidgetTree, TEXT(""), 15, FLinearColor(0.86f, 0.94f, 1.0f));
	Main->AddChildToVerticalBox(StockSummary);
	ToolsStatus = MakePanelText(WidgetTree, TEXT(""), 14, FLinearColor(0.78f, 0.88f, 0.94f));
	Main->AddChildToVerticalBox(ToolsStatus)->SetPadding(FMargin(0, 2, 0, 8));

	UHorizontalBox* Actions = WidgetTree->ConstructWidget<UHorizontalBox>();
	Main->AddChildToVerticalBox(Actions)->SetPadding(FMargin(0, 0, 0, 8));

	AxeButton = MakePanelButton(WidgetTree, TEXT("Upgrade Axe"));
	AxeButton->OnClicked.AddDynamic(this, &UForgeWidget::OnUpgradeAxe);
	Actions->AddChildToHorizontalBox(AxeButton)->SetPadding(FMargin(0, 0, 6, 0));

	PickButton = MakePanelButton(WidgetTree, TEXT("Upgrade Pickaxe"));
	PickButton->OnClicked.AddDynamic(this, &UForgeWidget::OnUpgradePickaxe);
	Actions->AddChildToHorizontalBox(PickButton)->SetPadding(FMargin(0, 0, 6, 0));

	GearButton = MakePanelButton(WidgetTree, TEXT("Forge Party Gear"));
	GearButton->OnClicked.AddDynamic(this, &UForgeWidget::OnForgeGear);
	Actions->AddChildToHorizontalBox(GearButton)->SetPadding(FMargin(0, 0, 6, 0));

	WallButton = MakePanelButton(WidgetTree, TEXT("Fortify Wall (1 Parts + 2W)"));
	WallButton->OnClicked.AddDynamic(this, &UForgeWidget::OnReinforceWall);
	Actions->AddChildToHorizontalBox(WallButton);

	MessageText = MakePanelText(WidgetTree, TEXT(""), 15, FLinearColor(1.0f, 0.84f, 0.42f));
	Main->AddChildToVerticalBox(MessageText)->SetPadding(FMargin(0, 0, 0, 8));

	Main->AddChildToVerticalBox(MakePanelText(WidgetTree, TEXT("Adventurer Gear & Tool Parts Tempering (+10 HP, +4 ATK, +5% Guard per rank):"), 15));
	UScrollBox* Scroll = WidgetTree->ConstructWidget<UScrollBox>();
	Main->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
	RosterBox = WidgetTree->ConstructWidget<UVerticalBox>();
	Scroll->AddChild(RosterBox);

	UButton* CloseBtn = MakePanelButton(WidgetTree, TEXT("Close (Esc / U)"), nullptr, TEXT("CloseForgeButton"));
	CloseBtn->OnClicked.AddDynamic(this, &UForgeWidget::OnCloseClicked);
	Main->AddChildToVerticalBox(CloseBtn)->SetPadding(FMargin(0, 10, 0, 0));

	RefreshForge();
	return Super::RebuildWidget();
}

void UForgeWidget::RefreshNumbers()
{
	if (!Player || !Player->Gather || !StockSummary) return;
	UGatherInventoryComponent* G = Player->Gather;
	const int32 Wall = Village ? Village->WallIntegrity : 100;
	StockSummary->SetText(FText::FromString(FString::Printf(
		TEXT("Wood %d | Stone %d | Iron %d | Crystal %d | ToolParts %d | Coin %d | Wall %d%%"),
		G->GetCount(TEXT("Wood")), G->GetCount(TEXT("Stone")), G->GetCount(TEXT("Iron")),
		G->GetCount(TEXT("Crystal")), G->GetCount(TEXT("ToolParts")), G->GetCount(TEXT("Coin")), Wall)));

	if (ToolsStatus)
	{
		ToolsStatus->SetText(FText::FromString(Forge ? Forge->ForgeStatusLine(Player) : G->InventoryLine()));
	}
	if (MessageText)
	{
		FString Msg = !ActionFeedback.IsEmpty() ? ActionFeedback : (Forge ? Forge->LastForgeMessage : FString());
		if (Msg.IsEmpty()) Msg = TEXT("Press any action above or temper an adventurer with Tool Parts.");
		MessageText->SetText(FText::FromString(Msg));
	}
	if (WallButton)
	{
		WallButton->SetIsEnabled(Village && Village->WallIntegrity < 100 && G->GetCount(TEXT("ToolParts")) >= 1 && G->GetCount(TEXT("Wood")) >= 2);
	}
}

void UForgeWidget::RefreshForge()
{
	if (!RosterBox || !Player || !Player->PartyReserve) return;
	RosterBox->ClearChildren();
	MemberRows.Reset();
	for (const FHiredAdventurer& A : Player->PartyReserve->Reserve)
	{
		UForgeMemberRow* Row = CreateWidget<UForgeMemberRow>(GetOwningPlayer());
		Row->InitializeRow(this, A.AdventurerID);
		RosterBox->AddChildToVerticalBox(Row)->SetPadding(FMargin(0, 0, 0, 6));
		MemberRows.Add(Row);
	}
	if (MemberRows.IsEmpty())
	{
		RosterBox->AddChildToVerticalBox(MakePanelText(WidgetTree, TEXT("Create golems at the Adventure Hall to forge weapons, armor, and temper enhancements."), 14));
	}
	RefreshNumbers();
}

bool UForgeWidget::UpgradeAxe()
{
	const bool bOk = Player && Player->Gather && Player->Gather->TryUpgradeAxe();
	if (bOk && Village) Village->SaveVillageState(Player);
	ActionFeedback = bOk ? TEXT("Upgraded axe!") : (Player && Player->Gather ? Player->Gather->InventoryLine() : TEXT("Need Iron/Crystal/Wood."));
	RefreshForge();
	return bOk;
}

bool UForgeWidget::UpgradePickaxe()
{
	const bool bOk = Player && Player->Gather && Player->Gather->TryUpgradePickaxe();
	if (bOk && Village) Village->SaveVillageState(Player);
	ActionFeedback = bOk ? TEXT("Upgraded pickaxe!") : (Player && Player->Gather ? Player->Gather->InventoryLine() : TEXT("Need Iron/Crystal/Wood."));
	RefreshForge();
	return bOk;
}

bool UForgeWidget::ForgeNextGear()
{
	const bool bOk = Forge && Forge->TryForgeAdventurerGear(Player);
	ActionFeedback = bOk ? TEXT("Forged adventurer equipment!") : (Forge ? Forge->ForgeStatusLine(Player) : TEXT("Need materials or adventurer."));
	RefreshForge();
	return bOk;
}

bool UForgeWidget::TemperAdventurer(FName AdventurerId)
{
	const bool bOk = Forge && Forge->TemperWithToolParts(Player, AdventurerId);
	if (Forge && !Forge->LastForgeMessage.IsEmpty()) ActionFeedback = Forge->LastForgeMessage;
	RefreshForge();
	return bOk;
}

bool UForgeWidget::ReinforceWalls()
{
	const bool bOk = Village && Village->ReinforceWallWithToolParts(Player);
	ActionFeedback = bOk
		? FString::Printf(TEXT("Reinforced village walls to %d%%!"), Village->WallIntegrity)
		: TEXT("Needs 1 Tool Parts, 2 Wood, and wall integrity below 100%.");
	RefreshForge();
	return bOk;
}

void UForgeWidget::NativeTick(const FGeometry& Geometry, float DeltaSeconds)
{
	Super::NativeTick(Geometry, DeltaSeconds);
	RefreshIn -= DeltaSeconds;
	if (RefreshIn <= 0.0f)
	{
		RefreshIn = 0.4f;
		RefreshNumbers();
		for (UForgeMemberRow* Row : MemberRows) if (Row) Row->RefreshRow();
	}
}

void UForgeWidget::CloseForge()
{
	RestoreModalInput(this, bOldCursor, bRestoredInput);
	RemoveFromParent();
}

void UForgeWidget::NativeDestruct()
{
	RestoreModalInput(this, bOldCursor, bRestoredInput);
	Super::NativeDestruct();
}

FReply UForgeWidget::NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event)
{
	if (Event.GetKey() == EKeys::Escape || Event.GetKey() == EKeys::U)
	{
		CloseForge();
		return FReply::Handled();
	}
	return Super::NativeOnKeyDown(Geometry, Event);
}
