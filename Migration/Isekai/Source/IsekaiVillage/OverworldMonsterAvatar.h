// Copyright Epic Games, Inc. All Rights Reserved.
// OverworldMonsterAvatar.h — Tales of-style roaming monster avatar on overworld

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "IsekaiVillageTypes.h"
#include "OverworldMonsterAvatar.generated.h"

class USphereComponent;
class USkeletalMeshComponent;

UENUM(BlueprintType)
enum class EMonsterAIState : uint8
{
	Idle,
	Patrolling,
	Chasing,
	Fleeing
};

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AOverworldMonsterAvatar : public ACharacter
{
	GENERATED_BODY()

public:
	AOverworldMonsterAvatar();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	// ── Components ──
	/** Modular BodyA head (the body mesh is headless). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	USkeletalMeshComponent* HeadMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	USphereComponent* EncounterTrigger;

	// ── AI & Movement Settings ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float PatrolSpeed = 250.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float ChaseSpeed = 550.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float AggroRadius = 800.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "AI")
	float PatrolRadius = 1200.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	FName EnemyPartyID = TEXT("Party_WolfPack_01");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	FText MonsterName = FText::FromString(TEXT("Dire Wolf"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	EBattleArenaBiome ArenaBiome = EBattleArenaBiome::Plains;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Combat")
	TSoftObjectPtr<UWorld> CustomBattleMap;


	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI")
	EMonsterAIState CurrentState = EMonsterAIState::Idle;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI")
	bool bIsStunned = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "AI")
	float StunTimer = 0.0f;

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void StunMonster(float Duration = 5.0f);

	UFUNCTION(BlueprintCallable, Category = "Combat")
	void TriggerBattleEncounter(APawn* PlayerPawn);

private:
	UFUNCTION()
	void OnEncounterOverlap(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	void UpdatePatrol(float DeltaTime);
	void UpdateChase(float DeltaTime, class AOverworldCharacter* PlayerChar);
	void PickNewPatrolPoint();

	FVector HomeLocation;
	FVector CurrentTargetLocation;
	float StateTimer = 0.0f;
	float StateDuration = 3.0f;
	bool bEncounterTriggered = false;
};
