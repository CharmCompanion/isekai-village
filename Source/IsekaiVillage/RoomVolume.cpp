// Copyright Epic Games, Inc. All Rights Reserved.
#include "RoomVolume.h"
#include "LinchpinRecipe.h"
#include "LinchpinProp.h"
#include "GuildMasterDesk.h"
#include "VillageRuntime.h"
#include "Components/BoxComponent.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"

ARoomVolume::ARoomVolume()
{
	PrimaryActorTick.bCanEverTick = true;
	Bounds = CreateDefaultSubobject<UBoxComponent>(TEXT("Bounds"));
	Bounds->InitBoxExtent(FVector(400.0f, 400.0f, 200.0f));
	Bounds->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Bounds->SetCollisionResponseToAllChannels(ECR_Overlap);
	Bounds->SetGenerateOverlapEvents(true);
	RootComponent = Bounds;
}

void ARoomVolume::BeginPlay()
{
	Super::BeginPlay();
	if (Recipes.Num() == 0)
	{
		ULinchpinRecipe::GetDefaultRecipes(Recipes);
	}
	RefreshFunction();
}

void ARoomVolume::EndPlay(const EEndPlayReason::Type EndPlayReason)
{
	if (AVillageRuntime* Runtime = AVillageRuntime::Get(this))
	{
		Runtime->UnregisterDynamicRoom(this);
	}
	Super::EndPlay(EndPlayReason);
}

void ARoomVolume::Tick(float DeltaTime)
{
	Super::Tick(DeltaTime);
	ScanTimer += DeltaTime;
	if (ScanTimer >= 0.75f)
	{
		ScanTimer = 0.0f;
		RefreshFunction();
	}
}

void ARoomVolume::RefreshFunction()
{
	if (Recipes.Num() == 0)
	{
		ULinchpinRecipe::GetDefaultRecipes(Recipes);
	}

	TSet<FName> FoundTags;
	TArray<AActor*> Overlaps;
	Bounds->GetOverlappingActors(Overlaps);

	// Fallback spatial box check for editor / un-simulated test execution
	if (Overlaps.IsEmpty() && GetWorld())
	{
		const FBox Box(GetActorLocation() - Bounds->GetScaledBoxExtent(), GetActorLocation() + Bounds->GetScaledBoxExtent());
		for (TActorIterator<ALinchpinProp> It(GetWorld()); It; ++It)
		{
			if (Box.IsInside(It->GetActorLocation()))
			{
				Overlaps.Add(*It);
			}
		}
		for (TActorIterator<AGuildMasterDesk> It(GetWorld()); It; ++It)
		{
			if (Box.IsInside(It->GetActorLocation()))
			{
				Overlaps.Add(*It);
			}
		}
	}

	for (AActor* Actor : Overlaps)
	{
		if (const ALinchpinProp* Prop = Cast<ALinchpinProp>(Actor))
		{
			FoundTags.Add(Prop->LinchpinTag);
		}
		if (Cast<AGuildMasterDesk>(Actor))
		{
			FoundTags.Add(TEXT("Desk"));
		}
	}

	ERoomFunction Best = ERoomFunction::EmptyHall;
	FText Label = FText::FromString(TEXT("Empty hall"));
	int32 BestCount = 0;
	for (ULinchpinRecipe* Recipe : Recipes)
	{
		if (!Recipe)
		{
			continue;
		}
		bool bAll = Recipe->RequiredTags.Num() > 0;
		for (const FName& Need : Recipe->RequiredTags)
		{
			if (!FoundTags.Contains(Need))
			{
				bAll = false;
				break;
			}
		}
		if (bAll && Recipe->RequiredTags.Num() > BestCount)
		{
			BestCount = Recipe->RequiredTags.Num();
			Best = Recipe->ResultFunction;
			Label = Recipe->DisplayName;
		}
	}

	if (Best != CurrentFunction)
	{
		CurrentFunction = Best;
		CurrentLabel = Label;
		if (AVillageRuntime* Runtime = AVillageRuntime::Get(this))
		{
			if (CurrentFunction != ERoomFunction::EmptyHall)
			{
				Runtime->RegisterDynamicRoom(this);
			}
			else
			{
				Runtime->UnregisterDynamicRoom(this);
			}
		}
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Emerald, FString::Printf(TEXT("Room is now: %s! Golems notified."), *Label.ToString()));
		}
	}
	else
	{
		CurrentLabel = Label;
		if (AVillageRuntime* Runtime = AVillageRuntime::Get(this))
		{
			if (CurrentFunction != ERoomFunction::EmptyHall && !Runtime->DynamicRooms.Contains(this))
			{
				Runtime->RegisterDynamicRoom(this);
			}
		}
	}
}
