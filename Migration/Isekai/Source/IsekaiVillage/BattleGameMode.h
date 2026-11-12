// Copyright Epic Games, Inc. All Rights Reserved.
// BattleGameMode.h — LMBS Arena Combat GameMode (Enemy Spawning, Victory & Defeat Flow, Overworld Return)

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/GameModeBase.h"
#include "IsekaiVillageTypes.h"
#include "MeshTerrainBuilder.h"
#include "BattleGameMode.generated.h"

class ABattleEnemy;
class ABattleCharacter;

UCLASS()
class ISEKAIVILLAGE_API ABattleGameMode : public AGameModeBase
{
	GENERATED_BODY()

public:
	ABattleGameMode();

	virtual void BeginPlay() override;

	/** Called when an enemy is slain in combat */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void OnEnemyDefeated(ABattleEnemy* Enemy);

	/** Record an incapacitated party hero during battle */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void RecordHeroIncapacitated(FName HeroID);

	/** Called when the player's HP reaches 0 */
	UFUNCTION(BlueprintCallable, Category = "Combat")
	void OnPlayerDefeated();

	/** Called when the player flees/escapes from combat */
	UFUNCTION(BlueprintCallable, Category = "Combat|Escape")
	void EscapeBattle();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	TArray<FName> IncapacitatedHeroIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	EEncounterAdvantage BattleEncounterAdvantage = EEncounterAdvantage::Normal;


protected:
	void EnsureArenaEnvironment();
	void SpawnEnemyParty();
	void SpawnPartyCompanions();
	void VictorySequence();
	void ReturnToOverworld();
	void DefeatSequence();

	/** Determine the arena biome based on the loaded map name */
	ETerrainBiome GetArenaBiomeFromMap();

	/** Spawn themed arena decor (rocks, crystals, obstacles) for the biome */
	void SpawnBiomeDecor(AMeshTerrainBuilder* Terrain);

	void SpawnArenaTerrain();
	void SpawnBoundaryRing();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	int32 LivingEnemiesCount = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	int32 TotalExpGained = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	int32 TotalGaldGained = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat")
	bool bBattleFinished = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Grade")
	float BattleStartTime = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Combat|Grade")
	float CalculatedGrade = 2.5f;

	float CalculateBattleGrade();
	FText GetRandomVictoryBanter();

	FTimerHandle TransitionTimerHandle;
};
