// Copyright Epic Games, Inc. All Rights Reserved.

#include "IsekaiVillageGameMode.h"
#include "IsekaiVillageCharacter.h"
#include "IsekaiVillageHUD.h"
#include "BlacksmithForge.h"
#include "VillageRuntime.h"
#include "DayBoard.h"
#include "GameFramework/PlayerStart.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

AIsekaiVillageGameMode::AIsekaiVillageGameMode()
{
	DefaultPawnClass = AIsekaiVillageCharacter::StaticClass();
	HUDClass = AIsekaiVillageHUD::StaticClass();
}

void AIsekaiVillageGameMode::BeginPlay()
{
	Super::BeginPlay();

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	bool bHasForge = false;
	for (TActorIterator<ABlacksmithForge> It(World); It; ++It)
	{
		bHasForge = true;
		break;
	}
	if (!bHasForge)
	{
		FVector ForgeLoc(-15500.0f, -9500.0f, 2850.0f);
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			ForgeLoc = It->GetActorLocation() + FVector(250.0f, -250.0f, 50.0f);
			break;
		}
		World->SpawnActor<ABlacksmithForge>(ForgeLoc, FRotator::ZeroRotator);
	}
	if (!World->GetMapName().Contains(TEXT("AnimeAdventure")))
	{
		return;
	}
	bool bHasVillage = false;
	for (TActorIterator<AVillageRuntime> It(World); It; ++It)
	{
		bHasVillage = true;
		break;
	}
	if (!bHasVillage)
	{
		World->SpawnActor<AVillageRuntime>(FVector(1000.0f, 10000.0f, 2650.0f), FRotator::ZeroRotator);
	}
	bool bHasBoard = false;
	for (TActorIterator<ADayBoard> It(World); It; ++It)
	{
		bHasBoard = true;
		break;
	}
	if (!bHasBoard)
	{
		World->SpawnActor<ADayBoard>(FVector(7000.0f, -7400.0f, 2500.0f), FRotator::ZeroRotator);
	}
}

AActor* AIsekaiVillageGameMode::ChoosePlayerStart_Implementation(AController* Player)
{
	const FString WarpTag = UGameplayStatics::ParseOption(OptionsString, TEXT("Warp"));
	if (!WarpTag.IsEmpty())
	{
		for (TActorIterator<APlayerStart> It(GetWorld()); It; ++It)
		{
			if (It->PlayerStartTag.ToString().Equals(WarpTag, ESearchCase::IgnoreCase))
			{
				return *It;
			}
		}
	}
	return Super::ChoosePlayerStart_Implementation(Player);
}


