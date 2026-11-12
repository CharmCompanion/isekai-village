// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiSaveGame.h — Unified Save/Load system for Adventurers vs Demons JRPG progression

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "AdventurersGuildTypes.h"
#include "TitleSystemTypes.h"
#include "AdventurerSystemTypes.h"
#include "TownEconomyTypes.h"
#include "IsekaiSaveGame.generated.h"

USTRUCT(BlueprintType)
struct FSaveFarmTileRecord
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SaveData")
	int32 GridX = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SaveData")
	int32 GridY = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SaveData")
	uint8 TileState = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SaveData")
	FName CropID = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SaveData")
	int32 GrowthStage = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SaveData")
	bool bIsWatered = false;
};

/**
 * SaveGame object persisting all player state across sessions and map transitions.
 */
UCLASS(BlueprintType)
class ISEKAIVILLAGE_API UIsekaiSaveGame : public USaveGame
{
	GENERATED_BODY()

public:
	UIsekaiSaveGame();

	// ── Player Base Stats ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Player")
	int32 PlayerLevel = 1;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Player")
	int32 CurrentExp = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Player")
	int32 Gald = 500;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Player")
	float SavedHP = 500.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Player")
	float SavedTP = 100.0f;

	// ── Progression (Titles & Skill Grid) ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Progression")
	FName EquippedTitleID = NAME_None;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Progression")
	TArray<FName> UnlockedTitleIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Progression")
	int32 AvailableSP = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Progression")
	TArray<FName> UnlockedSkillNodeIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Progression")
	TArray<FName> UnlockedDiscIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Progression")
	TArray<FName> FlippedCoinDiscs;

	// ── Adventurers Guild ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Guild")
	EGuildRank GuildRank = EGuildRank::Copper;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Guild")
	int32 GuildReputation = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Guild")
	TArray<FName> CompletedQuestIDs;

	// ── Adventurers Roster & Lineage ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Adventurers")
	TArray<FAdventurerProfile> SavedAdventurers;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Adventurers")
	TArray<FName> SavedActivePartyIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Adventurers")
	TArray<FName> SavedAuxiliaryPartyBetaIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Adventurers")
	TArray<FName> SavedAuxiliaryPartyGammaIDs;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Adventurers")
	TArray<FLegacyCrest> SavedLegacyCrests;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Adventurers")
	TArray<FAdventurerMentorship> SavedMentorships;

	// ── Inventory & Stockpile ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Inventory")
	TMap<FName, int32> ItemInventory;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Stockpile")
	FTownStockpile SavedTownStockpile;

	// ── Lord's Manor & Town Buildings ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Town")
	EBuildingTier SavedManorTier = EBuildingTier::Tier_1_Rustic;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Town")
	ETownArchitecturalStyle SavedVillageStyle = ETownArchitecturalStyle::RusticTimber;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Town")
	EResidentialHousingTier SavedHousingTier = EResidentialHousingTier::CommonerCottage;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Town")
	TMap<ETownBuildingType, EBuildingTier> SavedBuildingTiers;

	// ── World & Location ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|World")
	FName SavedMapName = FName("Map_Village");

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|World")
	FVector SavedLocation = FVector::ZeroVector;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|World")
	FRotator SavedRotation = FRotator::ZeroRotator;

	// ── Farming State ──
	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "SaveData|Farming")
	TArray<FSaveFarmTileRecord> SavedFarmPlots;

	// ── Static Save/Load Operations ──
	UFUNCTION(BlueprintCallable, Category = "SaveGame")
	static bool SaveProgress(UObject* WorldContextObject, const FString& SlotName = TEXT("SaveSlot_01"));

	UFUNCTION(BlueprintCallable, Category = "SaveGame")
	static bool LoadProgress(UObject* WorldContextObject, const FString& SlotName = TEXT("SaveSlot_01"));

	UFUNCTION(BlueprintPure, Category = "SaveGame")
	static bool DoesSaveExist(const FString& SlotName = TEXT("SaveSlot_01"));
};
