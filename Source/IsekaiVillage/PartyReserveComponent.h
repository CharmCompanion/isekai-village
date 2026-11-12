// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IsekaiVillageTypes.h"
#include "PartyReserveComponent.generated.h"

UCLASS(ClassGroup = "IsekaiVillage", meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UPartyReserveComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UPartyReserveComponent();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	int32 MaxReserve = 6;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Party") bool bUseGolemRoster=false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	int32 ActivePartyCap = 2;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Party")
	TArray<FHiredAdventurer> Reserve;

	UFUNCTION(BlueprintCallable, Category = "Party")
	bool HireAdventurer(FText Name);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Party|Learning") TMap<FName,TObjectPtr<UArteDataAsset>> LearnedArteDefinitions;
 UFUNCTION(BlueprintCallable,Category="Party|Learning") bool RecordAdventurerPractice(FName AdventurerId,FName Domain,float Effort,bool bSucceeded);
 UFUNCTION(BlueprintCallable,Category="Party|Learning") void RefreshLearnedArtes();

	UFUNCTION(BlueprintPure, Category = "Party")
	int32 GetActiveCompanionCount() const;

	UFUNCTION(BlueprintPure, Category = "Party")
	int32 GetMaxCompanions() const { return FMath::Max(0, ActivePartyCap - 1); }
};
