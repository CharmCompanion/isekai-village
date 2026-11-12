// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VillageTypes.h"
#include "VillageGolemTypes.h"
#include "TowerExpeditionTypes.h"
#include "VillageRuntime.generated.h"

class AVillageCitizen;
class AIsekaiVillageCharacter;

UCLASS()
class ISEKAIVILLAGE_API AVillageRuntime : public AActor
{
	GENERATED_BODY()

public:
	AVillageRuntime();
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") FTowerFloorProgress TowerFloor;

	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type EndPlayReason) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") bool bUseGolemVillage = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Village|Golems") bool bUseOrganicGolemNeeds=false;
	UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Village|Golems") TSubclassOf<class ASlimeRunicMage> SparringSlimeClass;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Village|Golems") TMap<FName,TObjectPtr<class USkeletalMesh>> AdventurerMeshes;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Village|Golems") int32 GolemStoneCost=6;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Village|Golems") int32 GolemWoodCost=4;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Village|Golems") FString LastHallMessage;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Village|Golems") FString LastShopMessage;
 void EnsureShopStock(FVillageShopState& Shop, bool bDailyRollover = true) const;
 UFUNCTION(BlueprintPure,Category="Village|Golems") bool CanUseAdventureHall(AIsekaiVillageCharacter* Player) const;
 UFUNCTION(BlueprintPure,Category="Village|Golems") int32 FreeAdventurerBeds(AIsekaiVillageCharacter* Player) const;
 UFUNCTION(BlueprintPure,Category="Village|Golems") USkeletalMesh* FindAdventurerMesh(FName ClassId,bool bFemale) const;
 UFUNCTION(BlueprintCallable,Category="Village|Golems") bool CreateGolemAdventurer(AIsekaiVillageCharacter* Player,FName ClassId,bool bFemale,FText Name);
 UFUNCTION(BlueprintCallable,Category="Village|Golems") bool SetAdventurerActive(AIsekaiVillageCharacter* Player,FName Id,bool bActive);
	UFUNCTION(BlueprintCallable, Category="Village|Golems") bool AdvanceGolemNeeds(class AVillageGolemCitizen* Worker,float DeltaSeconds);
	UFUNCTION(BlueprintPure, Category="Village|Golems") FText GolemWantLine(FGuid Id) const;
	UFUNCTION(BlueprintCallable, Category="Village|Golems") bool SetGolemNeeds(FGuid Id,float Fatigue,float Curiosity,float Loneliness,FName Interest);
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TArray<FVector> StreetNodes;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TArray<FIntPoint> StreetEdges;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TObjectPtr<class USkeletalMesh> MaleWorkerMesh;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TObjectPtr<class USkeletalMesh> FemaleWorkerMesh;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TObjectPtr<class UAnimSequence> MaleWorkerIdle;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TObjectPtr<class UAnimSequence> FemaleWorkerIdle;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TObjectPtr<class UAnimSequence> MaleWorkerWalk;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TObjectPtr<class UAnimSequence> FemaleWorkerWalk;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Golems") TArray<FVillageGolemRecord> GolemResidents;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Golems") TArray<FVillageShopState> GolemShops;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Golems") TArray<FVillageSupplySite> SupplySites;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Golems") TMap<FName,int32> HallSupplies;
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") bool WithdrawHallSupplies(AIsekaiVillageCharacter* Player);
	bool AdvanceHallCourier(class AVillageGolemCitizen* Worker, float DeltaSeconds);
	bool AdvanceProductionWorker(class AVillageGolemCitizen* Worker, float DeltaSeconds);
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Golems") bool bLastVillageSaveSucceeded = false;
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") void ReconcileGolemPopulation();
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") bool SaveVillageState(AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") void ReloadVillageState(AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") bool TradeWood(FName ShopPlot, bool bBuy, AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") bool TradeShopItem(FName ShopPlot, FName ItemId, bool bBuy, AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintPure, Category = "Village") static AVillageRuntime* Get(const UObject* WorldContextObject);
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Rooms") TArray<TObjectPtr<class ARoomVolume>> DynamicRooms;
	UFUNCTION(BlueprintCallable, Category = "Village|Rooms") void RegisterDynamicRoom(class ARoomVolume* Room);
	UFUNCTION(BlueprintCallable, Category = "Village|Rooms") void UnregisterDynamicRoom(class ARoomVolume* Room);
	UFUNCTION(BlueprintPure, Category = "Village|Rooms") class ARoomVolume* FindDynamicRoom(FName RoomId) const;
	UFUNCTION(BlueprintPure, Category = "Village|Rooms") class ALinchpinProp* FindLinchpinPropInRoom(FName RoomId, FName PreferredTag = NAME_None) const;
	UFUNCTION(BlueprintPure, Category = "Village|Rooms") class ALinchpinProp* FindBedForGolem(const FVillageGolemRecord& Record) const;
	UFUNCTION(BlueprintCallable, Category = "Village|Golems") bool ReinforceWallWithToolParts(AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintPure, Category = "Village|Services") static bool IsServiceBuilding(ETownBuilding Kind);
	UFUNCTION(BlueprintPure, Category = "Village|Services") int32 GetGuildStandingScore() const;
	UFUNCTION(BlueprintPure, Category = "Village|Services") int32 ComputeGuildRank() const;
	UFUNCTION(BlueprintPure, Category = "Village|Services") FString GetGuildRankName() const;
	UFUNCTION(BlueprintCallable, Category = "Village|Services") int32 EvaluateGuildRank(AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintCallable, Category = "Village|Services") bool UseBuildingService(FName PlotId, AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintCallable, Category = "Village|Services") bool ExecuteServiceAction(ETownBuilding Kind, FName ActionId, AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintPure, Category = "Village|Services") FName NearestServicePlot(const FVector& Position) const;
	UFUNCTION(BlueprintPure, Category = "Village|Services") FString BuildingQuickHint(ETownBuilding Kind) const;
	UFUNCTION(BlueprintPure, Category = "Village|Services") ESettlementEra GetSettlementEra(const AIsekaiVillageCharacter* Player = nullptr) const;
	UFUNCTION(BlueprintPure, Category = "Village|Services") FString GetSettlementEraName(const AIsekaiVillageCharacter* Player = nullptr) const;
	UFUNCTION(BlueprintPure, Category = "Village|Services") FString GetNextEraRequirementText(const AIsekaiVillageCharacter* Player = nullptr) const;
	UFUNCTION(BlueprintPure, Category = "Village|Construction") int32 DevelopedPlotCount() const;
	UFUNCTION(BlueprintCallable, Category = "Village|Services") bool TryCompleteMissionAtIndex(int32 MissionIndex, AIsekaiVillageCharacter* Player);
	float EffectiveBuildDiscount(const AIsekaiVillageCharacter* Player) const;
	void RollOverNewDay(AIsekaiVillageCharacter* Player);
	static const TArray<FVillageShopOffer>& ShopCatalog();
	static const FVillageShopOffer* FindShopOffer(FName ItemId);
	UFUNCTION(BlueprintPure, Category = "Village|Golems") bool IsShopOfferUnlocked(FName ItemId) const;
	UFUNCTION(BlueprintPure, Category = "Village|Golems") int32 GetShopBuyPrice(FName ItemId, const AIsekaiVillageCharacter* Player) const;
	UFUNCTION(BlueprintPure, Category = "Village|Golems") int32 GetShopSellPrice(FName ItemId, const AIsekaiVillageCharacter* Player) const;
	UFUNCTION(BlueprintPure, Category = "Village|Golems") int32 GetShopItemStock(FName ShopPlot, FName ItemId) const;
	UFUNCTION(BlueprintPure, Category = "Village|Golems") FString ShopKeeperName(FName ShopPlot) const;
	UFUNCTION(BlueprintPure, Category = "Village|Golems") bool IsShopStaffed(FName ShopPlot) const;
	UFUNCTION(BlueprintPure, Category = "Village|Golems") FText GolemVillageLine() const;
	bool BuildStreetRoute(const FVector& From, const FVector& To, TArray<FVector>& Out) const;
	FVector WorkerEntrance(const FTownPlot& Plot) const;
	FName NearestGolemShop(const FVector& Position) const;
	FName NearestBuiltShop(const FVector& Position) const;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float WindowSeconds = 10.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 WindowIndex = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 DayIndex = 1;

	UPROPERTY(VisibleAnywhere, BlueprintReadWrite, Category = "Village")
	EVillageWeather Weather = EVillageWeather::Clear;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 Trust = 12;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 FoodStock = 18;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 ShopWood = 4;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 ShopOre = 2;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 ShopCoin = 40;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 CrimeHeat = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 FestivalDays = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 StrikeHours = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	bool bLargeTown = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	bool bKingdom = false;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TArray<FTownPlot> Plots;

	// Opt-in per-map layout. Existing maps retain their original seeded plots.
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Construction")
	bool bUseAuthoredPlots = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Construction", meta = (EditCondition = "bUseAuthoredPlots"))
	TArray<FTownPlot> AuthoredPlots;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Construction")
	FString ConstructionSaveSlot;

	// FTownPlot entries here are building definitions; their position is ignored.
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Construction")
	TArray<FTownPlot> BuildingCatalog;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village|Construction")
	TObjectPtr<class UMaterialInterface> PlacementPreviewMaterial;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Construction")
	bool bBuildingCatalogOpen = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Construction")
	int32 SelectedBuildingIndex = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Construction")
	int32 PlacementTurns = 0;
	UFUNCTION(BlueprintCallable, Category = "Village|Construction")
	bool SelectBuilding(FName CatalogId);
	UFUNCTION(BlueprintCallable, Category = "Village|Construction")
	void ToggleBuildingCatalog();
	void CycleBuilding(int32 Direction);
	void RotateBuilding();
	void CancelBuildingPlacement();
	const FTownPlot* SelectedBuilding() const;
	FName TargetPlot(const AIsekaiVillageCharacter* Player) const;
	bool CanAffordBuilding(const FTownPlot& Building, const AIsekaiVillageCharacter* Player) const;
	bool IsUniqueBuildingStanding(const FTownPlot& Building) const;
	bool EraOpen(ETownEra Era, const AIsekaiVillageCharacter* Player) const;

	UFUNCTION(BlueprintCallable, Category = "Village|Construction")
	void InitializeConstruction();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 WallIntegrity = 40;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	int32 BankVaultCoins = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	int32 TownGuildRank = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	int32 AcademyResearchLevel = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	FName ActiveChapelBlessing = NAME_None;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	FName ActiveRoyalEdict = NAME_None;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	bool bBathhouseSoakedToday = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	int32 BellRungDay = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	int32 StipendCollectedDay = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	int32 RoyalGrantDay = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village|Services")
	FString LastServiceMessage;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	int32 WoodSoldToday = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TArray<FDayMission> TodayMissions;

	FVillageOffer BuildOffer() const;
	FVector PlaceLoc(EVillagePlace Place) const;
	int32 ResidentCount() const;
	int32 VisitorCount() const;
	int32 FreeBeds() const;
	float AverageFit() const;
	FText CensusLine() const;
	FText WindowName() const;

	AVillageCitizen* SpawnPerson(ECitizenStatus Status, ECitizenOrigin Origin, ECitizenTrait Trait);
	AVillageCitizen* NearestCitizen(const FVector& World, float RadiusCm) const;
	AVillageCitizen* NearestAt(EVillagePlace Place, float RadiusCm) const;
	bool TryShopOffer(AIsekaiVillageCharacter* Player);
	bool IsNearShop(const FVector& Location) const;
	bool TryBoard(AIsekaiVillageCharacter* Player);
	UFUNCTION(BlueprintCallable, Category = "Village|Construction")
	bool TryBuildPlot(FName PlotId, AIsekaiVillageCharacter* Player);
	bool HasBuilding(ETownBuilding Kind) const;
	const FTownPlot* FindPlot(FName PlotId) const;
	FTownPlot* FindPlot(FName PlotId);
	int32 BedCapacity() const;
	FText BoardLine() const;
	FText ArchitectLine() const;
	const AIsekaiVillageCharacter* ActiveTownPlayer() const;
	void RefreshMissions();
	void RefreshPlotStakes();

	static int32 ResolveLootQty(const FLootDrop& Drop, ELootPresence Presence, float Luck, int32 Rank);
	static ELootPresence PresenceFor(const AIsekaiVillageCharacter* Character);
	static FLootDrop MakeDrop(FName ItemId, int32 BaseQty);
	static int32 RollPlayerDrop(AIsekaiVillageCharacter* Character, FName ItemId, int32 BaseQty);

protected:
	UPROPERTY(Transient) TObjectPtr<AActor> PlacementPreview;
	UPROPERTY(Transient) TObjectPtr<class UMaterialInstanceDynamic> PlacementPreviewTint;
	FName PreviewPlotId;
	FName PreviewCatalogId;
	int32 PreviewTurns = -1;
	bool ApplyCatalog(FTownPlot& Plot, FName CatalogId, int32 Turns) const;
	void UpdatePlacementPreview();
	float Accrued = 0.0f;
	float VisitAccrued = 0.0f;
	float VillageSaveAccrued = 0.0f;
	UPROPERTY(Transient) TObjectPtr<class UTownConstructionSave> PendingVillageSave;
	TMap<FName, int32> LoftBedBonuses;
	TWeakObjectPtr<AIsekaiVillageCharacter> VillagePlayer;
	bool bVillagePlayerRestored = false;
	void RestoreVillagePlayer();
	void ReadVillageState(class UTownConstructionSave* Saved);
	void WriteVillageState(class UTownConstructionSave* Saved);
	void TickGolemVillage(float DeltaSeconds);
	int32 VisitSeed = 1;

	void TickWindow();
	void TickCitizen(AVillageCitizen* C);
	void TickNeeds(FCitizenMind& M);
	void TickWork(AVillageCitizen* C);
	void TickAmbush(AVillageCitizen* C);
	void TickStay(AVillageCitizen* C);
	void ApplyWeatherNeeds(FCitizenMind& M) const;
	void PayRent(FCitizenMind& M);
	void RollCrime(AVillageCitizen* C);
	void RollIllness(FCitizenMind& M);
	void AgeAndGossip(FCitizenMind& M);
	int32 FitOf(const FCitizenMind& M) const;
	void SeedStarter();
	void SeedPlots();
	void SpawnPlotStakes();
	bool SaveConstruction();
	void RewardMission(AIsekaiVillageCharacter* Player, FDayMission& Mission);
	TArray<AVillageCitizen*> Living() const;
};
