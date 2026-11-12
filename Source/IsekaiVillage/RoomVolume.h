// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BuildTypes.h"
#include "RoomVolume.generated.h"

class UBoxComponent;
class ULinchpinRecipe;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ARoomVolume : public AActor
{
	GENERATED_BODY()

public:
	ARoomVolume();

	virtual void BeginPlay() override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	TObjectPtr<UBoxComponent> Bounds;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Room")
	TArray<TObjectPtr<ULinchpinRecipe>> Recipes;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	ERoomFunction CurrentFunction = ERoomFunction::EmptyHall;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Room")
	FText CurrentLabel;

	UFUNCTION(BlueprintCallable, Category = "Room")
	void RefreshFunction();

private:
	float ScanTimer = 0.0f;
};
