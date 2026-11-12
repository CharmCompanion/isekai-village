// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiVillageHUD — TP bar + arte slots + element indicator + Focus Mode flash

#include "IsekaiVillageHUD.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "SphereGridWidget.h"
#include "PartyReserveComponent.h"
#include "GolemSparring.h"
#include "GolemHallWidget.h"
#include "DayBoardCatalogWidgets.h"
#include "LakeFishingSpot.h"
#include "MineOreVein.h"
#include "TowerExpedition.h"
#include "VillageRuntime.h"
#include "VillageCitizen.h"
#include "TownPlot.h"
#include "BuildEditComponent.h"
#include "BuildTypes.h"
#include "EngineUtils.h"
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

void AIsekaiVillageHUD::RefreshSphereGrid()
{
	if (SphereGridWidget)
	{
		SphereGridWidget->RebuildGrid();
	}
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
	if (Character->HasBlockingModalUI()) return;

	if (bSphereGridVisible)
	{
		if (!(SphereGridWidget && SphereGridWidget->GetClass() != USphereGridWidget::StaticClass()))
		{
			DrawSphereGrid(Character);
		}
		return;
	}


 if(auto* Battle=AGolemSparring::FindFor(Character))
 {
  TArray<FString> Lines;Battle->BattleLine().ToString().ParseIntoArrayLines(Lines);
  const float X=FMath::Max(30.f,Canvas->SizeX-640.f);
  const float Height=Lines.Num()*18.f+24.f;const float Y=FMath::Max(170.f,Canvas->SizeY-Height-24.f);
  DrawRect(FLinearColor(.025f,.04f,.07f,.93f),X-12,Y-10,630,Height);
  for(int32 I=0;I<Lines.Num();++I)DrawText(Lines[I],I==0?FLinearColor(.55f,.85f,1.f):FLinearColor(.88f,.95f,1.f),X,Y+I*18.f,nullptr,1.f);
 }
 if(auto* Tower=ATowerExpedition::Find(Character))
 {
  const FString Text=Tower->StatusLine(Character).ToString();
  if(!Text.IsEmpty())
  {
   TArray<FString> Raw,Lines;Text.ParseIntoArrayLines(Raw);
   for(const FString& Line:Raw){TArray<FString> Words;Line.ParseIntoArrayWS(Words);FString Wrapped;for(const FString& Word:Words){if(Wrapped.Len()+Word.Len()>78){Lines.Add(Wrapped);Wrapped.Empty();}if(!Wrapped.IsEmpty())Wrapped+=TEXT(" ");Wrapped+=Word;}if(!Wrapped.IsEmpty())Lines.Add(Wrapped);}
   const float X=Tower->bInside?30.f:FMath::Max(30.f,Canvas->SizeX-600.f),Y=Tower->bInside?65.f:145.f;
   DrawRect(FLinearColor(.025f,.04f,.07f,.92f),X-10,Y-8,580,Lines.Num()*19.f+20);
   for(int32 I=0;I<Lines.Num();++I)DrawText(Lines[I],I==0?FLinearColor(.55f,.95f,.8f):FLinearColor(.9f,.95f,1),X,Y+19.f*I,nullptr,.9f);
  }
  if(Tower->bInside){if(Character->Gather)DrawText(Character->Gather->InventoryLine(),FLinearColor(.85f,.85f,.65f),30,28,nullptr,.8f);return;}
 }
	DrawTPBar(Character);
	DrawElementIndicator(Character);
	DrawFocusModeFlash(Character);
	if (Character->IsBuildMode())
	{
		DrawBuildModeOverlay(Character);
	}
	if (Character->Gather)
	{
		DrawText(FString::Printf(TEXT("Lv %d  %s"), Character->GetGatherLevel(), *Character->Gather->InventoryLine()),
			FLinearColor(0.85f, 0.82f, 0.62f), 30.0f, 28.0f, nullptr, 0.95f);
	}
	{
		FString Skills;
		for (const FName& Action : Character->UnlockedSphereActions)
		{
			if (Action == TEXT("Yield+1") || Action == TEXT("HireCap+1")) continue;
			Skills += Action.ToString() + TEXT(" ");
		}
		if (Character->SphereYieldBonus > 0) Skills += FString::Printf(TEXT("Yield+%d "), Character->SphereYieldBonus);
		if (Character->PartyReserve && Character->PartyReserve->ActivePartyCap > 2) Skills += FString::Printf(TEXT("PartyCap:%d "), Character->PartyReserve->ActivePartyCap);
		if (!Skills.IsEmpty())
		{
			DrawText(Skills, FLinearColor(0.65f, 0.85f, 0.95f), 30.0f, 12.0f, nullptr, 0.72f);
		}
	}
	if (UWorld* World = Character->GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			if (!It->BuildingCatalog.IsEmpty())
			{
				DrawText(TEXT("B  Building catalogue"),FLinearColor(.75f,.88f,1.f),30.f,112.f,nullptr,.85f);
				const bool bHasUMGCatalog = Character->CatalogWidget && Character->CatalogWidget->IsInViewport();
				if (It->bBuildingCatalogOpen && !bHasUMGCatalog)
				{
					const float X=FMath::Max(20.f,Canvas->SizeX-390.f), Y=145.f;
					DrawRect(FLinearColor(.015f,.025f,.045f,.94f),X-14,Y-14,382,It->BuildingCatalog.Num()*24.f+142.f);
					DrawText(TEXT("CHOOSE A BUILDING"),FLinearColor(.94f,.84f,.57f),X,Y,nullptr,1.1f);
					DrawText(TEXT("Scroll / PgUp / PgDn: choose   R: rotate   B: cancel"),FLinearColor(.75f,.82f,.9f),X,Y+30,nullptr,.68f);
					for (int32 I=0;I<It->BuildingCatalog.Num();++I)
					{
						const FTownPlot& Choice=It->BuildingCatalog[I];
						const bool Open=It->EraOpen(Choice.Era,Character), Selected=I==It->SelectedBuildingIndex;
						const int32 Wood=Choice.WoodPrice(Character->SphereBuildSpeed);
						const float RowY=Y+57+I*24;
						if (Selected) DrawRect(FLinearColor(.07f,.22f,.28f,.95f),X-6,RowY-2,366,23);
						const TCHAR* Status=It->IsUniqueBuildingStanding(Choice)?TEXT(" [built]"):(Open?TEXT(""):TEXT(" [locked]"));
						DrawText(FString::Printf(TEXT("%s%s%s"),Selected?TEXT("> "):TEXT("  "),*Choice.Title().ToString(),Status),Open?FLinearColor(.9f,.92f,.9f):FLinearColor(.5f,.54f,.6f),X,RowY,nullptr,.78f);
						DrawText(FString::Printf(TEXT("%dW %dI %dC"),Wood,Choice.IronCost,Choice.CrystalCost),FLinearColor(.82f,.73f,.51f),X+255,RowY,nullptr,.7f);
					}
					const float Bottom=Y+64+It->BuildingCatalog.Num()*24;
					DrawText(TEXT("Aim at empty land; Left click or T to purchase."),FLinearColor(.68f,.93f,.79f),X,Bottom,nullptr,.72f);
					DrawText(TEXT("Green: ready   Red: resources / era locked"),FLinearColor(.8f,.82f,.85f),X,Bottom+23,nullptr,.72f);
					if (const FTownPlot* Choice=It->SelectedBuilding(); Choice && !It->EraOpen(Choice->Era,Character))
						DrawText(Choice->Era==ETownEra::Kingdom?TEXT("Unlock: Trust 80 + 8 sphere nodes"):TEXT("Unlock: Trust 50 + 4 sphere nodes"),FLinearColor(1.f,.62f,.35f),X,Bottom+46,nullptr,.72f);
				}
			}
			DrawText(It->CensusLine().ToString(), FLinearColor(0.72f, 0.78f, 0.62f), 30.0f, 50.0f, nullptr, 0.82f);
			DrawText(It->ArchitectLine().ToString(), FLinearColor(0.78f, 0.72f, 0.58f), 30.0f, 68.0f, nullptr, 0.76f);
			DrawText(It->BoardLine().ToString(), FLinearColor(0.88f, 0.8f, 0.55f), 30.0f, 86.0f, nullptr, 0.78f);
			if (It->bUseGolemVillage) DrawText(It->GolemVillageLine().ToString(), FLinearColor(.68f,.93f,.79f), 30.f, 132.f, nullptr, .78f);
   if(It->bUseGolemVillage)DrawText(TEXT("H at adventure hall: create / choose party | J at Knight school: sparring"),FLinearColor(.72f,.86f,1.f),30.f,150.f,nullptr,.78f);
			if (Character->bSphereSkillDangerSense)
			{
				FString Warn;
				if (It->WindowIndex == 4)
				{
					Warn = TEXT("Danger Sense: ambush hour on the road");
				}
				else if (It->CrimeHeat >= 3)
				{
					Warn = TEXT("Danger Sense: crime is rising");
				}
				for (TActorIterator<AVillageCitizen> Cit(World); Cit; ++Cit)
				{
					if (IsValid(*Cit) && Cit->Mind.Wound > 10
						&& FVector::DistSquared(Cit->GetActorLocation(), Character->GetActorLocation()) < 2800.0f * 2800.0f)
					{
						Warn = FString::Printf(TEXT("Danger Sense: %s is hurt nearby"), *Cit->Mind.DisplayName.ToString());
						break;
					}
				}
				if (!Warn.IsEmpty())
				{
					DrawText(Warn, FLinearColor(1.0f, 0.45f, 0.35f), 30.0f, 104.0f, nullptr, 0.8f);
				}
			}
			if (It->IsNearShop(Character->GetActorLocation()))
			{
				DrawText(It->bUseGolemVillage ? TEXT("T sell 1 wood (+2c)   Y buy 1 wood (2c)   U Open Shop") : TEXT("T  Trade at the stall"), FLinearColor(0.95f, 0.88f, 0.45f),
					Canvas->SizeX * 0.5f - 110.0f, Canvas->SizeY * 0.70f, nullptr, 1.1f);
			}
			else if (const FTownPlot* SvcPlot = It->FindPlot(It->NearestServicePlot(Character->GetActorLocation())))
			{
				const FString Hint = It->BuildingQuickHint(SvcPlot->Kind);
				if (!Hint.IsEmpty())
				{
					DrawText(Hint, FLinearColor(0.75f, 0.92f, 1.0f), Canvas->SizeX * 0.5f - 150.0f, Canvas->SizeY * 0.70f, nullptr, 1.1f);
				}
			}
			break;
		}
	}
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
		DrawText(Character->PartyReserve->bUseGolemRoster ? FString::Printf(TEXT("Adventurers %d  Active %d/%d"),Character->PartyReserve->Reserve.Num(),Character->PartyReserve->GetActiveCompanionCount(),Character->PartyReserve->GetMaxCompanions()) : FString::Printf(TEXT("Reserve %d/%d  Active %d"),
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
		bool bHallStore=false;
		for (TActorIterator<AVillageRuntime> It(GetWorld()); It; ++It) { bHallStore=It->bUseGolemVillage; break; }
		DrawText(bHallStore ? TEXT("T  Collect adventure hall supplies") : TEXT("T  Ask who will walk with you"), FLinearColor(1.0f, 0.92f, 0.45f),
			Canvas->SizeX * 0.5f - 150.0f, Canvas->SizeY * 0.62f, nullptr, 1.15f);
	}
	if (Character->bNearBlacksmith)
	{
		DrawText(TEXT("T  Quick-forge tools / gear   |   U  Open Blacksmith & Temper"), FLinearColor(0.95f, 0.72f, 0.35f),
			Canvas->SizeX * 0.5f - 160.0f, Canvas->SizeY * 0.66f, nullptr, 1.15f);
	}
	if (Character->bNearDayBoard)
	{
		DrawText(TEXT("T  Turn in day slip   |   U  Open Commission & Era Board"), FLinearColor(0.95f, 0.85f, 0.4f),
			Canvas->SizeX * 0.5f - 170.0f, Canvas->SizeY * 0.50f, nullptr, 1.15f);
	}
	else if (UWorld* ResourceWorld = Character->GetWorld())
	{
		TArray<AActor*> NearFish;
		Character->GetOverlappingActors(NearFish, ALakeFishingSpot::StaticClass());
		if (!NearFish.IsEmpty())
		{
			if (const ALakeFishingSpot* Spot = Cast<ALakeFishingSpot>(NearFish[0]))
			{
				DrawText(FString::Printf(TEXT("F / LMB / T  Fish at %s (%d left)"), *Spot->SpotTitle, Spot->CatchesRemaining),
					FLinearColor(0.45f, 0.90f, 1.0f), Canvas->SizeX * 0.5f - 170.0f, Canvas->SizeY * 0.50f, nullptr, 1.1f);
			}
		}
		else
		{
			for (TActorIterator<AMineOreVein> VeinIt(ResourceWorld); VeinIt; ++VeinIt)
			{
				if (FVector::DistSquared(Character->GetActorLocation(), VeinIt->GetActorLocation()) <= FMath::Square(320.0f))
				{
					DrawText(FString::Printf(TEXT("F / LMB / T  Mine %s Vein (Lv %d)"), *VeinIt->OreId.ToString(), VeinIt->RequiredLevel),
						FLinearColor(0.92f, 0.78f, 0.45f), Canvas->SizeX * 0.5f - 150.0f, Canvas->SizeY * 0.50f, nullptr, 1.1f);
					break;
				}
			}
		}
	}
	if (Character->bNearTownPlot && IsValid(Character->NearbyPlot))
	{
		DrawText(Character->NearbyPlot->PromptLine().ToString(), FLinearColor(0.9f, 0.82f, 0.55f),
			Canvas->SizeX * 0.5f - 180.0f, Canvas->SizeY * 0.46f, nullptr, 1.05f);
	}
	if (!AGolemSparring::FindFor(Character) && Character->bNearCitizen && IsValid(Character->NearbyCitizen))
	{
		DrawText(Character->NearbyCitizen->OfferLine().ToString(), FLinearColor(0.95f, 0.9f, 0.7f),
			Canvas->SizeX * 0.5f - 160.0f, Canvas->SizeY * 0.54f, nullptr, 1.1f);
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
	const int32 Disc = FMath::Clamp(Character->SphereDisc, 0, Grid->DiscCount() - 1);
	const bool bFlipped = Character->SphereFaceFlipped();
	const bool bDiscUnlocked = Grid->IsDiscUnlocked(Disc, Character->UnlockedSphereNodes);
	const TArray<FName>& Order = Grid->FaceOrder(Disc, bFlipped);

	DrawRect(FLinearColor(0.02f, 0.03f, 0.07f, 0.86f), 0, 0, Canvas->SizeX, Canvas->SizeY);

	const FString Header = FString::Printf(TEXT("[%s] %s%s  (K close  N next unlocked disc)"),
		*Grid->DiscCategoryLabel(Disc).ToString(),
		*Grid->DiscDisplayTitle(Disc, bFlipped).ToString(),
		bDiscUnlocked ? TEXT("") : TEXT(" [LOCKED]"));
	DrawText(Header, bDiscUnlocked ? FLinearColor(0.75f, 0.9f, 1.0f) : FLinearColor(1.0f, 0.65f, 0.35f), 260.0f, 24.0f, nullptr, 1.3f);

	const FSphereGridStatTotals& T = Character->SphereTotals;
	DrawText(FString::Printf(TEXT("SP %d  |  HP +%d  TP +%d  Atk +%d  Mag +%d  Res +%.0f%%  |  Inv +%d  Carry +%dkg  Build -%.0f%%  Attract +%.0f%%  Pace +%.0f%%  Trust +%d  Yield +%d"),
		Character->SpherePoints, T.HP, T.TP, T.Attack, T.Magic, T.ResPercent,
		T.Inventory, T.CarryWeight, T.BuildSpeedPercent, T.AttractionPercent, T.WorkerPacePercent, T.Trust, Character->SphereYieldBonus),
		FLinearColor(0.68f, 0.84f, 0.96f), 260.0f, 56.0f, nullptr, 0.9f);

	if (!bDiscUnlocked)
	{
		DrawText(FString::Printf(TEXT("Unlock requirement: %s"), *Grid->DiscUnlockHint(Disc).ToString()),
			FLinearColor(1.0f, 0.72f, 0.35f), 260.0f, 84.0f, nullptr, 1.0f);
	}
	else if (Grid->DiscHasFlip(Disc) && !bFlipped && Grid->IsFaceComplete(Disc, false, Character->UnlockedSphereNodes))
	{
		DrawRect(FLinearColor(0.85f, 0.65f, 0.1f, 0.95f), 260.0f, 84.0f, 220.0f, 34.0f);
		DrawText(TEXT("FLIP COIN"), FLinearColor(0.05f, 0.05f, 0.08f), 320.0f, 89.0f, nullptr, 1.05f);
		AddHitBox(FVector2D(260.0f, 84.0f), FVector2D(220.0f, 34.0f), FName(TEXT("SPHERE_FLIP")), true);
	}

	// Left rail: all 12 discs
	for (int32 D = 0; D < Grid->DiscCount(); ++D)
	{
		const bool bDUnlocked = Grid->IsDiscUnlocked(D, Character->UnlockedSphereNodes);
		const bool bDComplete = Grid->DiscHasFlip(D)
			? (Grid->IsFaceComplete(D, false, Character->UnlockedSphereNodes) && Grid->IsFaceComplete(D, true, Character->UnlockedSphereNodes))
			: Grid->IsFaceComplete(D, false, Character->UnlockedSphereNodes);
		const bool bSelected = (D == Disc);
		FLinearColor BtnColor = bSelected
			? FLinearColor(0.14f, 0.55f, 0.92f, 0.96f)
			: (bDComplete ? FLinearColor(0.12f, 0.52f, 0.36f, 0.92f)
				: (bDUnlocked ? FLinearColor(0.18f, 0.25f, 0.38f, 0.92f) : FLinearColor(0.12f, 0.12f, 0.16f, 0.85f)));
		const float BtnY = 24.0f + D * 42.0f;
		DrawRect(BtnColor, 24.0f, BtnY, 214.0f, 36.0f);
		const FString Label = Grid->DiscDisplayTitle(D, D == Disc ? bFlipped : false).ToString();
		DrawText(bDUnlocked ? Label : FString::Printf(TEXT("[Lock] %s"), *Label),
			bDUnlocked ? FLinearColor::White : FLinearColor(0.6f, 0.62f, 0.68f), 32.0f, BtnY + 9.0f, nullptr, 0.78f);
		AddHitBox(FVector2D(24.0f, BtnY), FVector2D(214.0f, 36.0f), FName(*FString::Printf(TEXT("SPHERE_DISC_%d"), D)), true);
	}

	const float CenterX = 250.0f + (Canvas->SizeX - 250.0f) * 0.5f;
	const float CenterY = Canvas->SizeY * 0.55f;
	const float Radius = FMath::Min(Canvas->SizeX - 300.0f, Canvas->SizeY - 140.0f) * 0.32f;
	const int32 Count = Order.Num();
	const float BoxW = 136.0f;
	const float BoxH = 44.0f;
	FString NextHint;

	for (int32 Index = 0; Index < Count; ++Index)
	{
		const FName NodeID = Order[Index];
		FSphereNode Node;
		Grid->GetNode(NodeID, Node);

		const float Angle = (2.0f * PI * Index) / FMath::Max(Count, 1) - PI * 0.5f;
		const float X = CenterX + FMath::Cos(Angle) * Radius - BoxW * 0.5f;
		const float Y = CenterY + FMath::Sin(Angle) * Radius - BoxH * 0.5f;

		const bool bUnlocked = Character->UnlockedSphereNodes.Contains(NodeID);
		const bool bAdjacent = Grid->IsNodeAdjacentOnDisc(NodeID, Character->UnlockedSphereNodes, Disc, bFlipped);
		FLinearColor Color = bUnlocked
			? FLinearColor(0.12f, 0.45f, 0.9f, 0.95f)
			: (bAdjacent ? FLinearColor(0.9f, 0.7f, 0.15f, 0.95f) : FLinearColor(0.18f, 0.2f, 0.26f, 0.9f));

		DrawRect(Color, X, Y, BoxW, BoxH);
		DrawText(Node.DisplayName.ToString(), FLinearColor::White, X + 6.0f, Y + 5.0f, nullptr, 0.8f);
		if (!Node.Description.IsEmpty())
		{
			DrawText(Node.Description.ToString().Left(24), FLinearColor(0.86f, 0.92f, 0.98f), X + 6.0f, Y + 22.0f, nullptr, 0.62f);
		}
		if (bAdjacent && NextHint.IsEmpty())
		{
			NextHint = FString::Printf(TEXT("Next: %s — %s"), *Node.DisplayName.ToString(), *Node.Description.ToString());
		}
		AddHitBox(FVector2D(X, Y), FVector2D(BoxW, BoxH), NodeID, true);
	}

	if (!NextHint.IsEmpty())
	{
		DrawText(NextHint, FLinearColor(0.98f, 0.85f, 0.45f), 260.0f, Canvas->SizeY - 38.0f, nullptr, 0.92f);
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

	const FString NameStr = BoxName.ToString();
	if (NameStr.StartsWith(TEXT("SPHERE_DISC_")))
	{
		const int32 DiscIdx = FCString::Atoi(*NameStr.Mid(12));
		if (Character->SelectSphereDisc(DiscIdx) && SphereGridWidget)
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

static FString GetHUDPieceTypeName(EBuildPieceType Type)
{
	switch (Type)
	{
	case EBuildPieceType::Foundation: return TEXT("Foundation");
	case EBuildPieceType::Floor: return TEXT("Floor");
	case EBuildPieceType::Wall: return TEXT("Wall");
	case EBuildPieceType::Doorway: return TEXT("Doorway");
	case EBuildPieceType::Stair: return TEXT("Stairs");
	case EBuildPieceType::Roof: return TEXT("Roof");
	case EBuildPieceType::Pillar: return TEXT("Pillar");
	default: return TEXT("Custom Piece");
	}
}

static FString GetHUDWallStyleName(EBuildWallStyle Style)
{
	switch (Style)
	{
	case EBuildWallStyle::Straight: return TEXT("Straight");
	case EBuildWallStyle::Diagonal45: return TEXT("45° Diagonal");
	case EBuildWallStyle::CurvedArc: return TEXT("Curved Arc");
	default: return TEXT("Straight");
	}
}

static FString GetHUDMaterialStyleName(EBuildMaterialStyle Style)
{
	switch (Style)
	{
	case EBuildMaterialStyle::WoodPlank: return TEXT("Wood Plank");
	case EBuildMaterialStyle::FieldStone: return TEXT("Field Stone");
	case EBuildMaterialStyle::CutStone: return TEXT("Cut Stone");
	case EBuildMaterialStyle::Brick: return TEXT("Brick");
	case EBuildMaterialStyle::MetalSheet: return TEXT("Metal Sheet");
	case EBuildMaterialStyle::WhitePlaster: return TEXT("White Plaster");
	case EBuildMaterialStyle::WallpaperStripes: return TEXT("Striped Wallpaper");
	case EBuildMaterialStyle::WallpaperFloral: return TEXT("Floral Wallpaper");
	case EBuildMaterialStyle::WoodWainscot: return TEXT("Wood Wainscot");
	default: return TEXT("Standard");
	}
}

void AIsekaiVillageHUD::DrawBuildModeOverlay(AIsekaiVillageCharacter* Character)
{
	if (!Character || !Character->BuildEdit || !Character->IsBuildMode() || !Canvas) return;

	UBuildEditComponent* BE = Character->BuildEdit;
	const float PanelW = 430.0f;
	const float PanelH = 330.0f;
	const float X = FMath::Max(20.0f, Canvas->SizeX - PanelW - 25.0f);
	const float Y = 30.0f;

	// Dark semi-transparent backdrop with golden/cyan border
	DrawRect(FLinearColor(0.015f, 0.03f, 0.05f, 0.92f), X, Y, PanelW, PanelH);
	DrawRect(FLinearColor(0.18f, 0.65f, 0.85f, 0.8f), X, Y, PanelW, 3.0f);

	// Header
	const int32 Tier = BE->GetUnlockedTier();
	const FString Header = FString::Printf(TEXT("BUILD MODE  •  TIER %d BLUEPRINTS"), Tier);
	DrawText(Header, FLinearColor(0.95f, 0.82f, 0.35f), X + 15.0f, Y + 12.0f, nullptr, 1.05f);

	float CurrentY = Y + 38.0f;

	if (BE->bPlacingProps)
	{
		DrawText(TEXT("Active Mode: LINCHPIN FURNITURE"), FLinearColor(0.35f, 0.95f, 0.75f), X + 15.0f, CurrentY, nullptr, 0.88f);
		CurrentY += 22.0f;

		FName Res1, Res2;
		int32 Cost1 = 0, Cost2 = 0;
		FString CostStr;
		if (UBuildEditComponent::GetPropCraftCost(BE->CurrentPropTag, Res1, Cost1, Res2, Cost2))
		{
			CostStr = FString::Printf(TEXT("(%d %s, %d %s)"), Cost1, *Res1.ToString(), Cost2, *Res2.ToString());
		}
		DrawText(FString::Printf(TEXT("Equipped: %s %s"), *BE->CurrentPropTag.ToString(), *CostStr), FLinearColor::White, X + 15.0f, CurrentY, nullptr, 0.92f);
		CurrentY += 22.0f;
	}
	else
	{
		DrawText(TEXT("Active Mode: MODULAR STRUCTURES"), FLinearColor(0.45f, 0.85f, 1.0f), X + 15.0f, CurrentY, nullptr, 0.88f);
		CurrentY += 22.0f;

		const FString PieceStr = FString::Printf(TEXT("Piece: %s  |  Style: %s"), *GetHUDPieceTypeName(BE->CurrentType), *GetHUDWallStyleName(BE->CurrentWallStyle));
		DrawText(PieceStr, FLinearColor::White, X + 15.0f, CurrentY, nullptr, 0.90f);
		CurrentY += 22.0f;

		const FString MatStr = FString::Printf(TEXT("Ext: %s  |  Int: %s"), *GetHUDMaterialStyleName(BE->CurrentMaterials.ExteriorMaterial), *GetHUDMaterialStyleName(BE->CurrentMaterials.InteriorMaterial));
		DrawText(MatStr, FLinearColor(0.85f, 0.85f, 0.70f), X + 15.0f, CurrentY, nullptr, 0.82f);
		CurrentY += 22.0f;
	}

	const FString SnapStr = BE->bFreeformPlacement ? TEXT("FREEFORM") : TEXT("MAGNETIC SNAP");
	const FString ScaleStr = FString::Printf(TEXT("Snap: %s  |  Scale: %.1fx  |  Rot: %.0f°"), *SnapStr, BE->CurrentScale.X, BE->PlacementYaw);
	DrawText(ScaleStr, FLinearColor(0.70f, 0.85f, 0.95f), X + 15.0f, CurrentY, nullptr, 0.80f);
	CurrentY += 26.0f;

	// Divider line
	DrawRect(FLinearColor(0.2f, 0.3f, 0.4f, 0.6f), X + 10.0f, CurrentY, PanelW - 20.0f, 1.0f);
	CurrentY += 8.0f;

	// Controls
	DrawText(TEXT("[Q] Radial Wheel   | [P] Switch Furniture / Structure"), FLinearColor(0.95f, 0.90f, 0.65f), X + 15.0f, CurrentY, nullptr, 0.75f);
	CurrentY += 18.0f;
	DrawText(TEXT("[M] Wall Style     | [O] Cutout Sub-quadrant"), FLinearColor(0.85f, 0.88f, 0.92f), X + 15.0f, CurrentY, nullptr, 0.75f);
	CurrentY += 18.0f;
	DrawText(TEXT("[C] Cycle Wallpaper| [R] Rotate 90° | [F] Freeform"), FLinearColor(0.85f, 0.88f, 0.92f), X + 15.0f, CurrentY, nullptr, 0.75f);
	CurrentY += 18.0f;
	DrawText(TEXT("[LMB] Place/Craft  | [RMB] Remove   | [B] Exit Build"), FLinearColor(0.45f, 0.95f, 0.65f), X + 15.0f, CurrentY, nullptr, 0.78f);
	CurrentY += 18.0f;
	const FString CamLine = Character->bFreeBuildCam
		? TEXT("[F2] Free Cam ON   | Space/Ctrl up-down | Shift fast")
		: TEXT("[F2] Free Cam      | fly past the island edge");
	DrawText(CamLine, FLinearColor(0.55f, 0.9f, 1.0f), X + 15.0f, CurrentY, nullptr, 0.75f);
	CurrentY += 18.0f;
	const FString TemplateName = BE->IsTemplateArmed() ? BE->GetArmedTemplateName() : FString(TEXT("none"));
	DrawText(FString::Printf(TEXT("[Shift+LMB] Select %d  [F3] Grab  [F4] Save"), BE->GetTemplateSelectionCount()), FLinearColor(0.75f, 0.95f, 0.7f), X + 15.0f, CurrentY, nullptr, 0.72f);
	CurrentY += 18.0f;
	DrawText(FString::Printf(TEXT("[F6] Stamp: %s   [F7] Clear selection"), *TemplateName), FLinearColor(0.75f, 0.95f, 0.7f), X + 15.0f, CurrentY, nullptr, 0.72f);
}
