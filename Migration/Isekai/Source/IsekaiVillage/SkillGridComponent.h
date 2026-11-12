// Copyright Epic Games, Inc. All Rights Reserved.
// SkillGridComponent.h — Component managing character Skill Points (SP) and Arte/Perk node unlocking

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkillGridTypes.h"
#include "SkillGridComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSPChangedSignature, int32, NewSP);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSkillNodeUnlockedSignature, const FSkillGridNode&, UnlockedNode);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSkillGridCompletedSignature, USkillGridDataAsset*, CompletedGrid);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCoinDiscFlipSignature, FName, FrontDiscID, FName, BackDiscID);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnDiscUnlockedSignature, FName, DiscID);

UCLASS(ClassGroup = (TalesProgression), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API USkillGridComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkillGridComponent();

protected:
	virtual void BeginPlay() override;

public:
	// ------------------------------------------------------------------
	// State
	// ------------------------------------------------------------------
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skill Points")
	int32 AvailableSP = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skill Grid")
	TObjectPtr<USkillGridDataAsset> ActiveGrid = nullptr;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skill Grid")
	TSet<FName> UnlockedNodeIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skill Grid")
	TSet<FName> UnlockedDiscIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skill Grid")
	TSet<FName> FlippedCoinDiscs;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skill Grid")
	FName ActiveDiscID = NAME_None;

	// ------------------------------------------------------------------
	// Operations
	// ------------------------------------------------------------------
	UFUNCTION(BlueprintCallable, Category = "Skill Operations")
	void AddSP(int32 Amount);

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool CanUnlockNode(FName NodeID) const;

	UFUNCTION(BlueprintCallable, Category = "Skill Operations")
	bool UnlockNode(FName NodeID);

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool IsNodeUnlocked(FName NodeID) const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool IsGridCompleted() const;

	UFUNCTION(BlueprintCallable, Category = "Skill Operations")
	bool UnlockDisc(FName DiscID);

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool IsDiscUnlocked(FName DiscID) const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool IsDiscCompleted(FName DiscID) const;

	UFUNCTION(BlueprintCallable, Category = "Skill Operations")
	bool FlipCoinDisc(FName FrontDiscID, FName& OutBackDiscID);

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool CanUnlockNodeOnDisc(FName DiscID, FName NodeID) const;

	UFUNCTION(BlueprintCallable, Category = "Skill Operations")
	bool UnlockNodeOnDisc(FName DiscID, FName NodeID);

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	float GetTotalSkillStatBonus(ETitleStatType StatType) const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	int32 GetTotalBonusHP() const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	int32 GetTotalBonusTP() const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	int32 GetTotalBonusInventory() const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	int32 GetTotalBonusCarryWeight() const;

	UFUNCTION(BlueprintPure, Category = "Skill Operations")
	bool HasUnlockedPerkOrArte(FName Identifier) const;

	UFUNCTION(BlueprintCallable, Category = "Skill Operations")
	void SetActiveGrid(USkillGridDataAsset* NewGrid);

	// ------------------------------------------------------------------
	// Delegates
	// ------------------------------------------------------------------
	UPROPERTY(BlueprintAssignable, Category = "Skill Events")
	FOnSPChangedSignature OnSPChanged;

	UPROPERTY(BlueprintAssignable, Category = "Skill Events")
	FOnSkillNodeUnlockedSignature OnSkillNodeUnlocked;

	UPROPERTY(BlueprintAssignable, Category = "Skill Events")
	FOnSkillGridCompletedSignature OnSkillGridCompleted;

	UPROPERTY(BlueprintAssignable, Category = "Skill Events")
	FOnCoinDiscFlipSignature OnCoinDiscFlip;

	UPROPERTY(BlueprintAssignable, Category = "Skill Events")
	FOnDiscUnlockedSignature OnDiscUnlocked;
};
