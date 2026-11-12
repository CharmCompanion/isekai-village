// Copyright Epic Games, Inc. All Rights Reserved.
// CampSystemActor.cpp — Interactive Campfire for Resting, Cooking, and Party Strategy

#include "CampSystemActor.h"
#include "BattleCharacter.h"
#include "AdventurerManagerComponent.h"
#include "AdventurerGuildBoardActor.h"
#include "EngineUtils.h"
#include "Components/SphereComponent.h"
#include "Components/PointLightComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "GameFramework/GameModeBase.h"

ACampSystemActor::ACampSystemActor()
{
	PrimaryActorTick.bCanEverTick = false;

	CampFireMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("CampFireMesh"));
	RootComponent = CampFireMesh;
	CampFireMesh->SetCollisionProfileName(TEXT("BlockAll"));

	InteractionSphere = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionSphere"));
	InteractionSphere->SetupAttachment(RootComponent);
	InteractionSphere->InitSphereRadius(250.0f);
	InteractionSphere->SetCollisionProfileName(TEXT("OverlapAllDynamic"));

	CampFireLight = CreateDefaultSubobject<UPointLightComponent>(TEXT("CampFireLight"));
	CampFireLight->SetupAttachment(RootComponent);
	CampFireLight->SetRelativeLocation(FVector(0.0f, 0.0f, 40.0f));
	CampFireLight->SetLightColor(FLinearColor(1.0f, 0.55f, 0.15f));
	CampFireLight->SetIntensity(5000.0f);
	CampFireLight->SetAttenuationRadius(650.0f);
}

void ACampSystemActor::RestParty()
{
	TArray<AActor*> FoundHeroes;
	UGameplayStatics::GetAllActorsOfClass(this, ABattleCharacter::StaticClass(), FoundHeroes);

	for (AActor* Act : FoundHeroes)
	{
		if (ABattleCharacter* Hero = Cast<ABattleCharacter>(Act))
		{
			Hero->CurrentHP = Hero->MaxHP;
			Hero->CurrentTP = Hero->MaxTP;
			Hero->CurrentAG = Hero->MaxAG;
		}
	}

	OnPartyRested.Broadcast();
}

bool ACampSystemActor::CookRecipe(UCookingRecipeDataAsset* Recipe, FName ChefName)
{
	if (!Recipe) return false;

	CurrentActiveBuff.DishName = Recipe->DishName;
	CurrentActiveBuff.BuffType = Recipe->BuffType;
	CurrentActiveBuff.BattlesRemaining = Recipe->BuffDurationBattles;

	// Favorite Chef Bonus: +15% increased potency!
	float Mag = Recipe->BuffMagnitude;
	if (!Recipe->FavoriteChefHeroID.IsNone() && Recipe->FavoriteChefHeroID == ChefName)
	{
		Mag *= 1.15f;
	}
	CurrentActiveBuff.BuffMagnitude = Mag;

	// Apply immediate partial recovery from the meal
	TArray<AActor*> FoundHeroes;
	UGameplayStatics::GetAllActorsOfClass(this, ABattleCharacter::StaticClass(), FoundHeroes);
	for (AActor* Act : FoundHeroes)
	{
		if (ABattleCharacter* Hero = Cast<ABattleCharacter>(Act))
		{
			Hero->CurrentHP = FMath::Min(Hero->MaxHP, Hero->CurrentHP + (Hero->MaxHP * (Recipe->HP_RecoveryPercent / 100.0f)));
			Hero->CurrentTP = FMath::Min(Hero->MaxTP, Hero->CurrentTP + (Hero->MaxTP * (Recipe->TP_RecoveryPercent / 100.0f)));
		}
	}

	// Apply permanent dietary nutrition to active party adventurers (ToS2 style)
	FAdventurerNutrition NutritionDelta;
	NutritionDelta.Protein = Recipe->NutritionProtein;
	NutritionDelta.Vitality = Recipe->NutritionVitality;
	NutritionDelta.ManaInfusion = Recipe->NutritionMana;
	NutritionDelta.Agility = Recipe->NutritionAgility;
	NutritionDelta.HolyEssence = Recipe->NutritionHoly;
	NutritionDelta.DarkEssence = Recipe->NutritionDark;
	NutritionDelta.FireEssence = Recipe->NutritionFire;
	NutritionDelta.WaterEssence = Recipe->NutritionWater;
	NutritionDelta.WindEssence = Recipe->NutritionWind;
	NutritionDelta.EarthEssence = Recipe->NutritionEarth;

	UAdventurerManagerComponent* AdvMgr = nullptr;
	if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		AdvMgr = PlayerPawn->FindComponentByClass<UAdventurerManagerComponent>();
	}
	if (!AdvMgr)
	{
		if (AGameModeBase* GM = UGameplayStatics::GetGameMode(this))
		{
			AdvMgr = GM->FindComponentByClass<UAdventurerManagerComponent>();
		}
	}
	if (!AdvMgr)
	{
		for (TActorIterator<AAdventurerGuildBoardActor> It(GetWorld()); It; ++It)
		{
			if (AAdventurerGuildBoardActor* Board = *It)
			{
				AdvMgr = Board->AdventurerManager;
				break;
			}
		}
	}

	if (AdvMgr)
	{
		for (const FName& Ing : Recipe->RequiredIngredients)
		{
			AdvMgr->TownStockpile.ConsumeStock(EStockpileCategory::Food, Ing, 1);
		}
		AdvMgr->ApplyCampMealToParty(NutritionDelta);
	}

	OnDishCooked.Broadcast(CurrentActiveBuff);
	return true;
}

void ACampSystemActor::DecrementFoodBuff()
{
	if (CurrentActiveBuff.BattlesRemaining > 0)
	{
		CurrentActiveBuff.BattlesRemaining--;
		if (CurrentActiveBuff.BattlesRemaining <= 0)
		{
			CurrentActiveBuff.BuffType = EFoodBuffType::None;
		}
	}
}
