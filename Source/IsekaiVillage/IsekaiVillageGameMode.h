// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IsekaiVillageGameMode.generated.h"

UCLASS(minimalapi)
class AIsekaiVillageGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	AIsekaiVillageGameMode();
	virtual void BeginPlay() override;
	virtual AActor* ChoosePlayerStart_Implementation(AController* Player) override;
};


