#pragma once
#include "CoreMinimal.h"
#include "GameFramework/SaveGame.h"
#include "VillageGolemTypes.h"
#include "GatherTypes.h"
#include "VillageTypes.h"
#include "IsekaiVillageTypes.h"
#include "TowerExpeditionTypes.h"
#include "TownConstructionSave.generated.h"

UCLASS()
class ISEKAIVILLAGE_API UTownConstructionSave : public USaveGame
{
	GENERATED_BODY()
public:
 UPROPERTY(SaveGame) FTowerFloorProgress TowerFloor;
	UPROPERTY(SaveGame) TArray<FName> BuiltPlots;
	UPROPERTY(SaveGame) TArray<FName> UpgradedPlots;
	UPROPERTY(SaveGame) TMap<FName,int32> LoftBedBonuses;
	UPROPERTY(SaveGame) TMap<FName, FName> PlotBuildingIds;
	UPROPERTY(SaveGame) TMap<FName, int32> PlotRotations;
	// Missing in older construction-only saves; those keep their normal defaults.
	UPROPERTY(SaveGame) bool bHasVillageState = false;
	UPROPERTY(SaveGame) int32 VillageStateVersion = 1;
	UPROPERTY(SaveGame) TArray<FVillageGolemRecord> Golems;
	UPROPERTY(SaveGame) TArray<FVillageShopState> Shops;
	UPROPERTY(SaveGame) bool bHasSupplies = false;
	UPROPERTY(SaveGame) TArray<FVillageSupplySite> SupplySites;
	UPROPERTY(SaveGame) TMap<FName,int32> HallSupplies;
	UPROPERTY(SaveGame) bool bHasPlayerInventory = false;
	UPROPERTY(SaveGame) TArray<FGatherStack> PlayerInventory;
	UPROPERTY(SaveGame) EAxeTier AxeTier = EAxeTier::Stone;
	UPROPERTY(SaveGame) EAxeTier PickaxeTier = EAxeTier::Stone;
	UPROPERTY(SaveGame) int32 VillageDay = 1;
	UPROPERTY(SaveGame) int32 VillageWindow = 0;
	UPROPERTY(SaveGame) EVillageWeather VillageWeather = EVillageWeather::Clear;
	UPROPERTY(SaveGame) int32 VillageTrust = 12;
	UPROPERTY(SaveGame) int32 VillageFood = 18;
	UPROPERTY(SaveGame) int32 VillageWoodSold = 0;
	UPROPERTY(SaveGame) TArray<FDayMission> VillageMissions;
	UPROPERTY(SaveGame) bool bHasPlayerProgress = false;
	UPROPERTY(SaveGame) TArray<FName> PlayerSphereNodes;
	UPROPERTY(SaveGame) int32 PlayerSpherePoints = 13;
	UPROPERTY(SaveGame) int32 PlayerSphereDisc = 0;
	UPROPERTY(SaveGame) bool bPlayerGridFlipped = false;
	UPROPERTY(SaveGame) bool bPlayerWorkFlipped = false;
	UPROPERTY(SaveGame) bool bPlayerCenterBUnlocked = false;
	UPROPERTY(SaveGame) TArray<FHiredAdventurer> PlayerReserve;
	UPROPERTY(SaveGame) bool bHasTownServices = false;
	UPROPERTY(SaveGame) int32 BankVaultCoins = 0;
	UPROPERTY(SaveGame) int32 TownGuildRank = 0;
	UPROPERTY(SaveGame) int32 AcademyResearchLevel = 0;
	UPROPERTY(SaveGame) FName ActiveChapelBlessing = NAME_None;
	UPROPERTY(SaveGame) FName ActiveRoyalEdict = NAME_None;
	UPROPERTY(SaveGame) bool bBathhouseSoakedToday = false;
	UPROPERTY(SaveGame) int32 BellRungDay = 0;
	UPROPERTY(SaveGame) int32 StipendCollectedDay = 0;
	UPROPERTY(SaveGame) int32 RoyalGrantDay = 0;
	UPROPERTY(SaveGame) bool bHasWallIntegrity = false;
	UPROPERTY(SaveGame) int32 VillageWallIntegrity = 40;
};
