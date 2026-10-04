// Copyright Epic Games, Inc. All Rights Reserved.

#include "IsekaiVillageGameMode.h"
#include "IsekaiVillageCharacter.h"
#include "IsekaiVillageHUD.h"
#include "GameFramework/PlayerStart.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

AIsekaiVillageGameMode::AIsekaiVillageGameMode()
{
	DefaultPawnClass = AIsekaiVillageCharacter::StaticClass();
	HUDClass = AIsekaiVillageHUD::StaticClass();
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


