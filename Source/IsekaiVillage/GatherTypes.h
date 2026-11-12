// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GatherTypes.generated.h"

UENUM(BlueprintType)
enum class EAxeTier : uint8
{
	Fists,
	Stone,
	Iron,
	Steel
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FGatherStack
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gather")
	FName ItemId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Gather")
	int32 Count = 0;
};
