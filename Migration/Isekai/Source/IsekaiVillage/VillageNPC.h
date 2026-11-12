// Copyright Epic Games, Inc. All Rights Reserved.
// VillageNPC.h — Interactive Village NPC with JRPG Dialogue, Farming Routines & Archetypes

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "IsekaiVillageTypes.h"
#include "VillageNPC.generated.h"

class USphereComponent;
class UAnimSequence;
class USkeletalMeshComponent;

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AVillageNPC : public ACharacter
{
	GENERATED_BODY()

public:
	AVillageNPC();

protected:
	virtual void BeginPlay() override;

public:
	virtual void Tick(float DeltaTime) override;

	/** Modular BodyA head (the body mesh is headless). */
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Mesh")
	USkeletalMeshComponent* HeadMesh;

	// ── NPC Identity ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NPC")
	ENPCArchetype Archetype = ENPCArchetype::Villager;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NPC")
	FText NPCName = FText::FromString(TEXT("Elder Corrine"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NPC")
	FText RoleTitle = FText::FromString(TEXT("Village Elder"));

	// ── Dialogue Script ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NPC")
	TArray<FText> DialogueLines;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "NPC")
	float InteractionRadius = 250.0f;

	/** Trigger dialogue interaction with the player */
	UFUNCTION(BlueprintCallable, Category = "NPC")
	void InteractWithPlayer(APawn* Interactor);

	/** Check if player is within range */
	UFUNCTION(BlueprintPure, Category = "NPC")
	bool IsPlayerInRange(const FVector& PlayerLocation) const;

	// ── Dynamic NPC Animations ──
	UPROPERTY(Transient)
	UAnimSequence* AnimFarmingTill = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimFarmingWater = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimFarmingHarvest = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimGuardStance = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimBoxIdle = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoIdle = nullptr;

	UPROPERTY(Transient)
	UAnimSequence* AnimLocoWalk = nullptr;

	ELocomotionAnimState CurrentLocoState = ELocomotionAnimState::Idle;

	UFUNCTION(BlueprintCallable, Category = "NPC")

	void SetNPCArchetype(ENPCArchetype NewArchetype);

private:
	void FacePlayer(const FVector& PlayerLocation);
	void PlayAnimMontageSafe(UAnimSequence* Seq, float PlayRate = 1.0f);
	void UpdateRoutine(float DeltaTime);
	void InitializeArchetypeDefaults();

	float RoutineTimer = 0.0f;
	float RoutineInterval = 7.0f;
	int32 RoutineStep = 0;
	bool bIsInteracting = false;
	float InteractingTimer = 0.0f;
};

