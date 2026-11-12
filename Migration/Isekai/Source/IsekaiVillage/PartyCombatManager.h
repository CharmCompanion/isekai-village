// Copyright Epic Games, Inc. All Rights Reserved.
// PartyCombatManager.h — 4-Member Active Party, Seamless Leader Switching, and Tactical Gambits

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "IsekaiVillageTypes.h"
#include "PartyCombatManager.generated.h"

class ABattleCharacter;
class ABattleEnemy;

UENUM(BlueprintType)
enum class ETalesTacticsStrategy : uint8
{
	Balanced          UMETA(DisplayName = "Balanced / Standard"),
	Aggressive        UMETA(DisplayName = "Fight All-Out / Full Offense"),
	KeepDistance      UMETA(DisplayName = "Keep Distance / Magic Caster"),
	ConserveResources UMETA(DisplayName = "Conserve TP and AG"),
	HealPriority      UMETA(DisplayName = "Prioritize Healing & Support")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnPartyLeaderSwitched, ABattleCharacter*, NewLeader, int32, LeaderIndex);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPartyStrategyChanged, ETalesTacticsStrategy, NewStrategy);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnCombatVoiceBark, FText, BarkDialogue, ABattleCharacter*, Speaker);

UCLASS(ClassGroup = (TalesTemplate), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UPartyCombatManager : public UActorComponent
{
	GENERATED_BODY()

public:
	UPartyCombatManager();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ── Active Party Roster ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Party")
	TArray<ABattleCharacter*> ActivePartyMembers;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Party")
	int32 CurrentLeaderIndex = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party|Tactics")
	ETalesTacticsStrategy CurrentStrategy = ETalesTacticsStrategy::Balanced;

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Party|Events")
	FOnPartyLeaderSwitched OnPartyLeaderSwitched;

	UPROPERTY(BlueprintAssignable, Category = "Party|Events")
	FOnPartyStrategyChanged OnPartyStrategyChanged;

	UPROPERTY(BlueprintAssignable, Category = "Party|Events")
	FOnCombatVoiceBark OnCombatVoiceBark;

	// ── Core Operations ──
	UFUNCTION(BlueprintCallable, Category = "Party")
	void RegisterPartyMember(ABattleCharacter* Character);

	UFUNCTION(BlueprintCallable, Category = "Party")
	bool SwitchLeader(int32 NewLeaderIndex);

	UFUNCTION(BlueprintCallable, Category = "Party")
	void NextLeader();

	UFUNCTION(BlueprintCallable, Category = "Party")
	void SetTacticsStrategy(ETalesTacticsStrategy NewStrategy);

	UFUNCTION(BlueprintCallable, Category = "Party")
	ABattleCharacter* GetLeader() const;

	UFUNCTION(BlueprintCallable, Category = "Party")
	void BroadcastVoiceBark(const FText& Line, ABattleCharacter* Speaker);

protected:
	virtual void BeginPlay() override;

private:
	void ExecuteCompanionAI(float DeltaTime);
	float AITickTimer = 0.0f;
};
