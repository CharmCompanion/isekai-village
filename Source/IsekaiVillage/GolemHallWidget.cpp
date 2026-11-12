#include "GolemHallWidget.h"
#include "VillageRuntime.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "GatherInventoryComponent.h"
#include "GolemSparring.h"
#include "Blueprint/WidgetTree.h"
#include "Components/Border.h"
#include "Components/Button.h"
#include "Components/CanvasPanel.h"
#include "Components/CanvasPanelSlot.h"
#include "Components/ComboBoxString.h"
#include "Components/EditableTextBox.h"
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

static UTextBlock* HallText(UWidgetTree* Tree,const FString& Value,int32 Size=16)
{auto* T=Tree->ConstructWidget<UTextBlock>();T->SetText(FText::FromString(Value));T->SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),Size));T->SetAutoWrapText(true);return T;}
static UButton* HallButton(UWidgetTree* Tree,const FString& Caption,UTextBlock** Label=nullptr,FName WidgetName=NAME_None)
{auto* B=Tree->ConstructWidget<UButton>(UButton::StaticClass(),WidgetName);auto* T=HallText(Tree,Caption);T->SetColorAndOpacity(FSlateColor(FLinearColor(.04f,.06f,.09f)));B->AddChild(T);if(Label)*Label=T;return B;}

void UGolemHallWidget::InitializeHall(AVillageRuntime* V,AIsekaiVillageCharacter* P)
{Village=V;Commander=P;SetIsFocusable(true);if(auto* PC=GetOwningPlayer())bOldCursor=PC->bShowMouseCursor;}
TSharedRef<SWidget> UGolemHallWidget::RebuildWidget()
{
 WidgetTree=NewObject<UWidgetTree>(this,TEXT("HallTree"));auto* Canvas=WidgetTree->ConstructWidget<UCanvasPanel>();WidgetTree->RootWidget=Canvas;
 auto* Size=WidgetTree->ConstructWidget<USizeBox>();Size->SetWidthOverride(720);Size->SetHeightOverride(780);auto* CS=Canvas->AddChildToCanvas(Size);CS->SetAnchors(FAnchors(.5f,.5f));CS->SetAlignment(FVector2D(.5f,.5f));CS->SetAutoSize(true);
 auto* Background=WidgetTree->ConstructWidget<UBorder>();Background->SetBrushColor(FLinearColor(.025f,.04f,.065f,.98f));Background->SetPadding(FMargin(18));Size->AddChild(Background);
 auto* Main=WidgetTree->ConstructWidget<UVerticalBox>();Background->AddChild(Main);
 Main->AddChildToVerticalBox(HallText(WidgetTree,TEXT("ADVENTURE HALL"),25));
 Main->AddChildToVerticalBox(HallText(WidgetTree,TEXT("Create a golem, then choose who to bring. Classes set the outfit and practice focus; skills are learned through activity."),15));
 Main->AddChildToVerticalBox(HallText(WidgetTree,TEXT("Tank: guard | Mage: magic | Ranger: scouting | Healer: aid"),14));
 Resources=HallText(WidgetTree,TEXT(""));Main->AddChildToVerticalBox(Resources);
 auto* Collect=HallButton(WidgetTree,TEXT("Collect delivered supplies"),nullptr,TEXT("CollectButton"));Collect->OnClicked.AddDynamic(this,&UGolemHallWidget::CollectSupplies);Main->AddChildToVerticalBox(Collect)->SetPadding(FMargin(0,4,0,8));
 auto* Choices=WidgetTree->ConstructWidget<UHorizontalBox>();Main->AddChildToVerticalBox(Choices);
 ClassChoice=WidgetTree->ConstructWidget<UComboBoxString>(UComboBoxString::StaticClass(),TEXT("ClassChoice"));for(const TCHAR* C:{TEXT("Tank"),TEXT("Mage"),TEXT("Ranger"),TEXT("Healer")})ClassChoice->AddOption(C);ClassChoice->SetSelectedOption(TEXT("Tank"));Choices->AddChildToHorizontalBox(ClassChoice)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
 BodyChoice=WidgetTree->ConstructWidget<UComboBoxString>(UComboBoxString::StaticClass(),TEXT("BodyChoice"));BodyChoice->AddOption(TEXT("Male body"));BodyChoice->AddOption(TEXT("Female body"));BodyChoice->SetSelectedOption(TEXT("Male body"));Choices->AddChildToHorizontalBox(BodyChoice)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
 NameEntry=WidgetTree->ConstructWidget<UEditableTextBox>(UEditableTextBox::StaticClass(),TEXT("NameEntry"));auto NameStyle=NameEntry->GetWidgetStyle();NameStyle.TextStyle.SetFont(FCoreStyle::GetDefaultFontStyle(TEXT("Regular"),16));NameEntry->SetWidgetStyle(NameStyle);NameEntry->SetForegroundColor(FLinearColor(.05f,.07f,.1f));NameEntry->SetHintText(FText::FromString(TEXT("Optional name (up to 40 characters)")));Main->AddChildToVerticalBox(NameEntry)->SetPadding(FMargin(0,6));
 CreateButton=HallButton(WidgetTree,TEXT("Create golem"),nullptr,TEXT("CreateButton"));CreateButton->OnClicked.AddDynamic(this,&UGolemHallWidget::CreateSelected);Main->AddChildToVerticalBox(CreateButton)->SetPadding(FMargin(0,0,0,6));
 Message=HallText(WidgetTree,TEXT(""),15);Message->SetColorAndOpacity(FSlateColor(FLinearColor(1,.82f,.4f)));Main->AddChildToVerticalBox(Message);
 PartySummary=HallText(WidgetTree,TEXT(""),18);Main->AddChildToVerticalBox(PartySummary)->SetPadding(FMargin(0,8,0,4));
 Main->AddChildToVerticalBox(HallText(WidgetTree,TEXT("Housing supports your reserve. More active slots unlock through the Sphere Grid and town upgrades."),14));
 auto* Scroll=WidgetTree->ConstructWidget<UScrollBox>();Main->AddChildToVerticalBox(Scroll)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));RosterBox=WidgetTree->ConstructWidget<UVerticalBox>(UVerticalBox::StaticClass(),TEXT("RosterBox"));Scroll->AddChild(RosterBox);
 auto* Close=HallButton(WidgetTree,TEXT("Close (Esc)"),nullptr,TEXT("CloseButton"));Close->OnClicked.AddDynamic(this,&UGolemHallWidget::CloseHall);Main->AddChildToVerticalBox(Close)->SetPadding(FMargin(0,8,0,0));
 RefreshHall();return Super::RebuildWidget();
}
void UGolemHallWidget::RefreshNumbers()
{
 if(!Village || !Commander || !Commander->Gather || !Commander->PartyReserve)return;
 Resources->SetText(FText::FromString(FString::Printf(TEXT("Recipe: %d stone + %d wood | You have: %d stone, %d wood | Free beds: %d"),Village->GolemStoneCost,Village->GolemWoodCost,Commander->Gather->GetCount(TEXT("Stone")),Commander->Gather->GetCount(TEXT("Wood")),Village->FreeAdventurerBeds(Commander))));
 PartySummary->SetText(FText::FromString(FString::Printf(TEXT("Roster %d | Active adventurers %d/%d"),Commander->PartyReserve->Reserve.Num(),Commander->PartyReserve->GetActiveCompanionCount(),Commander->PartyReserve->GetMaxCompanions())));
 Message->SetText(FText::FromString(Village->LastHallMessage));
 CreateButton->SetIsEnabled(Village->CanUseAdventureHall(Commander) && Village->FreeAdventurerBeds(Commander)>0 && Commander->Gather->GetCount(TEXT("Stone"))>=Village->GolemStoneCost && Commander->Gather->GetCount(TEXT("Wood"))>=Village->GolemWoodCost);
}
void UGolemHallWidget::RefreshHall()
{
 if(!RosterBox || !Commander || !Commander->PartyReserve)return;
 RosterBox->ClearChildren();Rows.Reset();
 for(const auto& A:Commander->PartyReserve->Reserve)
 {auto* Row=CreateWidget<UGolemHallRow>(GetOwningPlayer());Row->InitializeRow(this,A.AdventurerID);RosterBox->AddChildToVerticalBox(Row)->SetPadding(FMargin(0,0,0,8));Rows.Add(Row);}
 if(Rows.IsEmpty())RosterBox->AddChildToVerticalBox(HallText(WidgetTree,TEXT("No adventurers yet. Create one with village resources and a free bed.")));
 RefreshNumbers();
}
bool UGolemHallWidget::SubmitCreation(FName ClassId,bool Female,FText Name)
{const bool Ok=Village && Village->CreateGolemAdventurer(Commander,ClassId,Female,Name);RefreshHall();return Ok;}
bool UGolemHallWidget::ChooseActive(FName Id,bool Active)
{const bool Ok=Village && Village->SetAdventurerActive(Commander,Id,Active);RefreshHall();return Ok;}
void UGolemHallWidget::CreateSelected(){if(SubmitCreation(FName(*ClassChoice->GetSelectedOption()),BodyChoice->GetSelectedOption()==TEXT("Female body"),NameEntry->GetText()))NameEntry->SetText(FText::GetEmpty());}
void UGolemHallWidget::CollectSupplies(){if(Village){int32 Total=0;for(const auto& Pair:Village->HallSupplies)Total+=FMath::Max(0,Pair.Value);const bool Ok=Village->WithdrawHallSupplies(Commander);Village->LastHallMessage=!Ok?TEXT("Return to the adventure hall to collect supplies."):Total>0?TEXT("Delivered supplies collected."):TEXT("The hall store is empty. Workers will bring more.");}RefreshHall();}
void UGolemHallWidget::NativeTick(const FGeometry& G,float D){Super::NativeTick(G,D);RefreshIn-=D;if(RefreshIn<=0){RefreshIn=.5f;RefreshNumbers();for(const auto& Row:Rows)if(Row)Row->RefreshRow();}}
void UGolemHallWidget::RestoreInput(){if(bRestoredInput)return;bRestoredInput=true;if(auto* PC=GetOwningPlayer()){PC->bShowMouseCursor=bOldCursor;PC->SetInputMode(FInputModeGameOnly());}}
void UGolemHallWidget::CloseHall(){RestoreInput();RemoveFromParent();}
void UGolemHallWidget::NativeDestruct(){RestoreInput();Super::NativeDestruct();}
FReply UGolemHallWidget::NativeOnKeyDown(const FGeometry& G,const FKeyEvent& E){if(E.GetKey()==EKeys::Escape){CloseHall();return FReply::Handled();}return Super::NativeOnKeyDown(G,E);}

void UGolemHallRow::InitializeRow(UGolemHallWidget* H,FName InId){Hall=H;Id=InId;}
TSharedRef<SWidget> UGolemHallRow::RebuildWidget()
{
 WidgetTree=NewObject<UWidgetTree>(this,TEXT("RosterRowTree"));auto* Border=WidgetTree->ConstructWidget<UBorder>();Border->SetBrushColor(FLinearColor(.07f,.10f,.15f,.95f));Border->SetPadding(FMargin(10));WidgetTree->RootWidget=Border;
 auto* Box=WidgetTree->ConstructWidget<UHorizontalBox>();Border->AddChild(Box);Details=HallText(WidgetTree,TEXT(""),15);Box->AddChildToHorizontalBox(Details)->SetSize(FSlateChildSize(ESlateSizeRule::Fill));
 UTextBlock* Label=nullptr;ActiveButton=HallButton(WidgetTree,TEXT(""),&Label,TEXT("ActiveButton"));ButtonText=Label;ActiveButton->OnClicked.AddDynamic(this,&UGolemHallRow::ToggleActive);Box->AddChildToHorizontalBox(ActiveButton)->SetPadding(FMargin(8,0,0,0));RefreshRow();return Super::RebuildWidget();
}
void UGolemHallRow::RefreshRow()
{
 if(!Details || !Hall || !Hall->GetCommander() || !Hall->GetCommander()->PartyReserve)return;auto* P=Hall->GetCommander();auto* V=Hall->GetVillage();
 const auto* A=P->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==Id;});if(!A)return;
 auto Names=[](const TArray<FName>& Values){FString R;for(FName X:Values){if(!R.IsEmpty())R+=TEXT(", ");R+=FName::NameToDisplayString(X.ToString(),false);}return R.IsEmpty()?FString(TEXT("None yet")):R;};
 const bool Housed=V && V->GolemResidents.ContainsByPredicate([&](const auto& R){return R.AdventurerId==Id && !R.HomePlot.IsNone();});
 const FString Role=A->ClassId.IsNone()?TEXT("Adventurer"):A->ClassId.ToString();const FString Body=A->bHasChosenBody?(A->bFemaleBody?TEXT("Female body"):TEXT("Male body")):TEXT("Existing body");
 Details->SetText(FText::FromString(FString::Printf(TEXT("%s | %s | %s | %s\n%s | %s practice %.0f\nSkills: %s\nPassives: %s"),*A->Name.ToString(),*Role,*Body,A->bInActiveParty?TEXT("Active"):TEXT("Reserve"),Housed?TEXT("Housed"):TEXT("Needs housing"),*A->Drives.Interest.ToString(),A->Drives.Practice.FindRef(A->Drives.Interest),*Names(A->Drives.Skills),*Names(A->Drives.Passives))));
 ButtonText->SetText(FText::FromString(A->bAssignedToRampage?TEXT("On expedition"):A->bInActiveParty?TEXT("Bench"):TEXT("Make active")));
 ActiveButton->SetIsEnabled(!A->bAssignedToRampage && (A->bInActiveParty || (Housed && P->PartyReserve->GetActiveCompanionCount()<P->PartyReserve->GetMaxCompanions())));
}
void UGolemHallRow::ToggleActive(){if(Hall && Hall->GetCommander() && Hall->GetCommander()->PartyReserve)if(const auto* A=Hall->GetCommander()->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==Id;}))Hall->ChooseActive(Id,!A->bInActiveParty);}
