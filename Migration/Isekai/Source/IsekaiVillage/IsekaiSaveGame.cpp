// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiSaveGame.cpp — Unified Save/Load system implementation

#include "IsekaiSaveGame.h"
#include "BattleCharacter.h"
#include "TitleManagerComponent.h"
#include "SkillGridComponent.h"
#include "AdventurersGuildComponent.h"
#include "AdventurerGuildBoardActor.h"
#include "AdventurerManagerComponent.h"
#include "FarmPlotActor.h"
#include "LordsManorActor.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Engine/World.h"

UIsekaiSaveGame::UIsekaiSaveGame()
{
}

bool UIsekaiSaveGame::DoesSaveExist(const FString& SlotName)
{
	return UGameplayStatics::DoesSaveGameExist(SlotName, 0);
}

bool UIsekaiSaveGame::SaveProgress(UObject* WorldContextObject, const FString& SlotName)
{
	if (!WorldContextObject) return false;

	UWorld* World = WorldContextObject->GetWorld();
	if (!World) return false;

	UIsekaiSaveGame* SaveObj = Cast<UIsekaiSaveGame>(UGameplayStatics::CreateSaveGameObject(UIsekaiSaveGame::StaticClass()));
	if (!SaveObj) return false;

	// Record current Map Name
	SaveObj->SavedMapName = FName(*World->GetMapName());

	// Gather player state
	if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(WorldContextObject, 0))
	{
		SaveObj->SavedLocation = PlayerPawn->GetActorLocation();
		SaveObj->SavedRotation = PlayerPawn->GetActorRotation();

		if (ABattleCharacter* Hero = Cast<ABattleCharacter>(PlayerPawn))
		{
			SaveObj->SavedHP = Hero->CurrentHP;
			SaveObj->SavedTP = Hero->CurrentTP;

			// Titles
			if (Hero->TitleManager)
			{
				if (Hero->TitleManager->EquippedTitle)
				{
					SaveObj->EquippedTitleID = Hero->TitleManager->EquippedTitle->TitleID;
				}
				SaveObj->UnlockedTitleIDs.Empty();
				for (const FTitleProgressState& State : Hero->TitleManager->UnlockedTitles)
				{
					if (State.TitleAsset)
					{
						SaveObj->UnlockedTitleIDs.Add(State.TitleAsset->TitleID);
					}
				}
			}

			// Skill Grid
			if (Hero->SkillGrid)
			{
				SaveObj->AvailableSP = Hero->SkillGrid->AvailableSP;
				SaveObj->UnlockedSkillNodeIDs = Hero->SkillGrid->UnlockedNodeIDs.Array();
				SaveObj->UnlockedDiscIDs = Hero->SkillGrid->UnlockedDiscIDs.Array();
				SaveObj->FlippedCoinDiscs = Hero->SkillGrid->FlippedCoinDiscs.Array();
			}

			// Adventurers Guild
			if (Hero->GuildComponent)
			{
				SaveObj->GuildRank = Hero->GuildComponent->CurrentRank;
				SaveObj->GuildReputation = Hero->GuildComponent->GuildReputation;
				SaveObj->CompletedQuestIDs = Hero->GuildComponent->CompletedQuestIDs;
			}
		}
	}

	// Gather Farming plot states
	SaveObj->SavedFarmPlots.Empty();
	for (TActorIterator<AFarmPlotActor> It(World); It; ++It)
	{
		if (AFarmPlotActor* Plot = *It)
		{
			for (const FFarmTile& Tile : Plot->Tiles)
			{
				FSaveFarmTileRecord Record;
				Record.GridX = Tile.GridX;
				Record.GridY = Tile.GridY;
				Record.TileState = (uint8)Tile.State;
				Record.CropID = Tile.PlantedCrop ? Tile.PlantedCrop->CropID : NAME_None;
				Record.GrowthStage = Tile.CurrentGrowthStage;
				Record.bIsWatered = Tile.bIsWatered;
				SaveObj->SavedFarmPlots.Add(Record);
			}
		}
	}

	// Gather Adventurers roster & active party & lineage
	for (TActorIterator<AAdventurerGuildBoardActor> It(World); It; ++It)
	{
		if (AAdventurerGuildBoardActor* Board = *It)
		{
			if (Board->AdventurerManager)
			{
				SaveObj->SavedAdventurers = Board->AdventurerManager->HiredAdventurers;
				SaveObj->SavedActivePartyIDs = Board->AdventurerManager->ActivePartyAdventurerIDs;
				SaveObj->SavedAuxiliaryPartyBetaIDs = Board->AdventurerManager->AuxiliaryPartyBetaIDs;
				SaveObj->SavedAuxiliaryPartyGammaIDs = Board->AdventurerManager->AuxiliaryPartyGammaIDs;
				SaveObj->SavedLegacyCrests = Board->AdventurerManager->AvailableLegacyCrests;
				SaveObj->SavedMentorships = Board->AdventurerManager->ActiveMentorships;
				SaveObj->SavedTownStockpile = Board->AdventurerManager->TownStockpile;
				break;
			}
		}
	}

	// Gather Lord's Manor & Town Building tiers
	for (TActorIterator<ALordsManorActor> It(World); It; ++It)
	{
		if (ALordsManorActor* Manor = *It)
		{
			SaveObj->SavedManorTier = Manor->ManorTier;
			SaveObj->SavedVillageStyle = Manor->VillageStyle;
			SaveObj->SavedHousingTier = Manor->HousingTier;
			SaveObj->SavedBuildingTiers = Manor->BuildingTiers;
			break;
		}
	}

	return UGameplayStatics::SaveGameToSlot(SaveObj, SlotName, 0);
}

bool UIsekaiSaveGame::LoadProgress(UObject* WorldContextObject, const FString& SlotName)
{
	if (!WorldContextObject || !DoesSaveExist(SlotName)) return false;

	UWorld* World = WorldContextObject->GetWorld();
	if (!World) return false;

	UIsekaiSaveGame* SaveObj = Cast<UIsekaiSaveGame>(UGameplayStatics::LoadGameFromSlot(SlotName, 0));
	if (!SaveObj) return false;

	// Restore player state
	if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(WorldContextObject, 0))
	{
		if (SaveObj->SavedLocation != FVector::ZeroVector)
		{
			PlayerPawn->SetActorLocation(SaveObj->SavedLocation);
			PlayerPawn->SetActorRotation(SaveObj->SavedRotation);
		}

		if (ABattleCharacter* Hero = Cast<ABattleCharacter>(PlayerPawn))
		{
			Hero->CurrentHP = SaveObj->SavedHP;
			Hero->CurrentTP = SaveObj->SavedTP;

			if (Hero->TitleManager)
			{
				if (SaveObj->EquippedTitleID != NAME_None)
				{
					Hero->TitleManager->EquipTitle(SaveObj->EquippedTitleID);
				}
			}

			if (Hero->SkillGrid)
			{
				Hero->SkillGrid->AvailableSP = SaveObj->AvailableSP;
				Hero->SkillGrid->UnlockedNodeIDs.Empty();
				for (const FName& NodeID : SaveObj->UnlockedSkillNodeIDs)
				{
					Hero->SkillGrid->UnlockedNodeIDs.Add(NodeID);
				}
				Hero->SkillGrid->UnlockedDiscIDs.Empty();
				for (const FName& DiscID : SaveObj->UnlockedDiscIDs)
				{
					Hero->SkillGrid->UnlockedDiscIDs.Add(DiscID);
				}
				Hero->SkillGrid->FlippedCoinDiscs.Empty();
				for (const FName& DiscID : SaveObj->FlippedCoinDiscs)
				{
					Hero->SkillGrid->FlippedCoinDiscs.Add(DiscID);
				}
			}

			if (Hero->GuildComponent)
			{
				Hero->GuildComponent->CurrentRank = SaveObj->GuildRank;
				Hero->GuildComponent->GuildReputation = SaveObj->GuildReputation;
				Hero->GuildComponent->CompletedQuestIDs = SaveObj->CompletedQuestIDs;
			}
		}
	}

	// Restore Adventurers roster & active party & lineage
	for (TActorIterator<AAdventurerGuildBoardActor> It(World); It; ++It)
	{
		if (AAdventurerGuildBoardActor* Board = *It)
		{
			if (Board->AdventurerManager)
			{
				Board->AdventurerManager->HiredAdventurers = SaveObj->SavedAdventurers;
				Board->AdventurerManager->ActivePartyAdventurerIDs = SaveObj->SavedActivePartyIDs;
				Board->AdventurerManager->AuxiliaryPartyBetaIDs = SaveObj->SavedAuxiliaryPartyBetaIDs;
				Board->AdventurerManager->AuxiliaryPartyGammaIDs = SaveObj->SavedAuxiliaryPartyGammaIDs;
				Board->AdventurerManager->AvailableLegacyCrests = SaveObj->SavedLegacyCrests;
				Board->AdventurerManager->ActiveMentorships = SaveObj->SavedMentorships;
				Board->AdventurerManager->TownStockpile = SaveObj->SavedTownStockpile;
				break;
			}
		}
	}

	// Restore Lord's Manor & Town Building tiers
	for (TActorIterator<ALordsManorActor> It(World); It; ++It)
	{
		if (ALordsManorActor* Manor = *It)
		{
			Manor->ManorTier = SaveObj->SavedManorTier;
			Manor->VillageStyle = SaveObj->SavedVillageStyle;
			Manor->HousingTier = SaveObj->SavedHousingTier;
			Manor->BuildingTiers = SaveObj->SavedBuildingTiers;
			break;
		}
	}

	return true;
}
