// Copyright Epic Games, Inc. All Rights Reserved.
// TitleManagerComponent.h — Component managing character Tales titles, equipping, stat bonuses, and masteries

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "TitleSystemTypes.h"
#include "TitleManagerComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTitleEquippedSignature, UTitleDataAsset*, NewTitle);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnTitleMasteredSignature, UTitleDataAsset*, MasteredTitle);

UCLASS(ClassGroup = (TalesProgression), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UTitleManagerComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UTitleManagerComponent();

protected:
	virtual void BeginPlay() override;

public:
	// ------------------------------------------------------------------
	// State
	// ------------------------------------------------------------------
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Titles")
	TArray<FTitleProgressState> UnlockedTitles;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Titles")
	TObjectPtr<UTitleDataAsset> EquippedTitle = nullptr;

	// ------------------------------------------------------------------
	// Operations
	// ------------------------------------------------------------------
	UFUNCTION(BlueprintCallable, Category = "Titles")
	bool UnlockTitle(UTitleDataAsset* NewTitle);

	UFUNCTION(BlueprintCallable, Category = "Titles")
	bool EquipTitle(FName TitleID);

	UFUNCTION(BlueprintCallable, Category = "Titles")
	void AddMasteryExp(int32 ExpAmount);

	UFUNCTION(BlueprintPure, Category = "Titles")
	float GetTotalStatBonus(ETitleStatType StatType) const;

	UFUNCTION(BlueprintPure, Category = "Titles")
	bool HasPassivePerk(FName PerkID) const;

	// ------------------------------------------------------------------
	// Delegates
	// ------------------------------------------------------------------
	UPROPERTY(BlueprintAssignable, Category = "Title Events")
	FOnTitleEquippedSignature OnTitleEquipped;

	UPROPERTY(BlueprintAssignable, Category = "Title Events")
	FOnTitleMasteredSignature OnTitleMastered;
};
