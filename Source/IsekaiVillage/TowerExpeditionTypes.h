#pragma once
#include "CoreMinimal.h"
#include "TowerAdaptation.h"
#include "TowerExpeditionTypes.generated.h"

UENUM(BlueprintType)
enum class ETowerRelic : uint8
{
 None,
 RunicSurge,     /** +20 starting TP and 15% faster combat readiness for the current run. */
 QuarryBlessing, /** +1 extra item yield on every resource deposit gathered this run. */
 AegisOath,      /** +15% passive guard mitigation and +25 Max HP per ally this run. */
 BerserkerBrand  /** Risk/Reward: +35% attack damage and +15% incoming damage this run. */
};

/** One reusable region definition; all dimensions are centimetres. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerRegionModule
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName Id;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FText Label;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector Center=FVector::ZeroVector;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FVector2D Size=FVector2D(2400,2400);
};
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerDeposit
{
 GENERATED_BODY()
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FName Id;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FName Item;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FVector Offset=FVector::ZeroVector;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 Yield=1;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bGuarded=false;
};
/** Durable floor state, saved atomically with village inventory and roster. No transient combat actors. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerFloorProgress
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 Version=2;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 Seed=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 Visit=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TMap<FName,int32> HarvestDays;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bCampBuilt=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 RestedVisit=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 GuardianClearedVisit=0;

 /** Current floor. Negative floors are New Game Plus. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 Floor=1;
 /** Deepest main-tower floor cleared. The gate can start at any floor up to one past it. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 HighestFloor=0;
 /** Deepest New Game Plus floor cleared, as a positive depth. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 HighestEcho=0;
 /** Floor the next run starts on. 0 means the next floor not yet cleared. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 StartFloor=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bNewGamePlus=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FTowerMemory Memory;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FTowerFloorPlan CurrentPlan;

 /** A run lasts from the gate until the Village portal, the entry gate or a failure. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bRunActive=false;
 /** Floor whose guardian was beaten this visit; portals open while it equals Floor. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 ClearedFloor=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 LastGrade=0;
 /** Floors the Leap portal moves; 0 when not offered. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 LeapOffer=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TArray<int32> BossesDefeated;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 TripsHomeUsed=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 CampRests=0;
 /** Items gathered this run; a failed run loses part of them. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TMap<FName,int32> RunLoot;
 /** Relic boons active for the current run. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TArray<ETowerRelic> RunRelics;
 /** Floors whose chamber Relic Altar was already claimed during this run. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TArray<int32> RelicClaimedFloors;
};
