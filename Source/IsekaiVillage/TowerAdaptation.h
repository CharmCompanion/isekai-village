#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "IsekaiVillageTypes.h"
#include "TowerAdaptation.generated.h"

/** What the tower watches. Element habits are only recorded by elemental skills. */
UENUM(BlueprintType)
enum class ETowerHabit : uint8
{
 Fire,Water,Earth,Wind,
 Physical,Magic,Guard,Evasion,Healing,
 Burst,Grind,Carry,LargeParty,
 Count UMETA(Hidden)
};

UENUM(BlueprintType)
enum class ETowerIntelligence : uint8
{
 Instinct,  /** Random target. */
 Hunter,    /** Lowest health. */
 Tactician, /** Healer first, avoids guarded targets. */
 Mimic      /** Tactician that also copies the party's favourite style. */
};

UENUM(BlueprintType)
enum class ETowerPortal : uint8
{
 Village, /** Ends the run safely. */
 Camp,    /** Pause; only once the run's camp is built. */
 Forward,
 Leap
};

/** One floor's record. Filled by combat, consumed when the floor is cleared. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerFloorLog
{
 GENERATED_BODY()
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TMap<ETowerHabit,float> Habits;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TMap<FName,float> MemberDamage;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 Actions=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 Fights=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 PartySize=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 Knockouts=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float DamageTaken=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float PartyMaxHealth=0;
 void Add(ETowerHabit Habit,float Amount=1){Habits.FindOrAdd(Habit)+=Amount;}
};

/** Long-lived habits. Kept when a run ends or fails. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerMemory
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TMap<ETowerHabit,float> Weights;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName CarryId;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float LastEase=.5f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 FloorsRecorded=0;
};

/** Combat changes a counter rule applies. Rules combine by multiplying and adding. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerEncounterModifiers
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float HealthMult=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float DamageMult=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float PhysicalTakenMult=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float MagicTakenMult=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float HealingMult=1;
 /** Scales the party's guard reduction. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float GuardMult=1;
 /** Scales the time between enemy turns. Above 1 is slower. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float EnemyRecoveryMult=1;
 /** Damage added per enemy turn, as a fraction of base damage. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float EnrageStep=0;
 /** Damage from members other than the marked carry. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float SupportDamageMult=1;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) int32 ShieldHits=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bSureHit=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bFocusCarry=false;
 void Combine(const FTowerEncounterModifiers& O);
};

/** Data row: one counter to one habit, with the opening it leaves. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerCounterRule
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FName Id;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) ETowerHabit Habit=ETowerHabit::Physical;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) float Cost=6;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FString Announcement;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FString Opening;
 /** Elemental counters change the enemy element; the opening is the element that beats it. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite) bool bSetsElement=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) EElement EnemyElement=EElement::Water;
 UPROPERTY(EditAnywhere,BlueprintReadWrite) FTowerEncounterModifiers Modifiers;
};

/** Everything the next floor needs. Saved so the announcement stays stable. */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTowerFloorPlan
{
 GENERATED_BODY()
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) int32 Floor=1;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) float Budget=0;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) bool bBoss=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) bool bTowerUnsure=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) bool bRespawn=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) ETowerIntelligence Intelligence=ETowerIntelligence::Instinct;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) bool bHasElement=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) EElement EnemyElement=EElement::Water;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) TArray<FName> Rules;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) FTowerEncounterModifiers Modifiers;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) FName CarryId;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) ETowerHabit MimicHabit=ETowerHabit::Physical;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) float RewardMult=1;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,SaveGame) FString Announcement;
};

/** Pure tower rules. No world access, so every rule is unit tested. */
UCLASS()
class ISEKAIVILLAGE_API UTowerAdaptationLibrary : public UBlueprintFunctionLibrary
{
 GENERATED_BODY()
public:
 static constexpr float NoticeThreshold=.35f;
 static constexpr float MemoryDecay=.6f;
 static constexpr int32 DefaultBossInterval=5;

 UFUNCTION(BlueprintPure,Category="Tower") static TArray<FTowerCounterRule> DefaultCounterRules();
 UFUNCTION(BlueprintPure,Category="Tower") static FString HabitName(ETowerHabit Habit);
 /** Water beats Fire, Fire beats Wind, Wind beats Earth, Earth beats Water. */
 UFUNCTION(BlueprintPure,Category="Tower") static EElement ElementThatBeats(EElement Element);
 /** 0 is a near-wipe, 1 is a flawless quick clear. */
 UFUNCTION(BlueprintPure,Category="Tower") static float EaseScore(const FTowerFloorLog& Log);
 /** 0 struggle, 1 clear, 2 strong, 3 perfect. */
 UFUNCTION(BlueprintPure,Category="Tower") static int32 ClearGrade(float Ease);
 UFUNCTION(BlueprintPure,Category="Tower") static bool IsBossFloor(int32 Floor,int32 BossInterval=5);
 UFUNCTION(BlueprintPure,Category="Tower") static float BaseBudget(int32 Floor);
 /** Floors Leap skips ahead: 0 when not offered, otherwise 2 or 3, never past the next boss floor. */
 UFUNCTION(BlueprintPure,Category="Tower") static int32 LeapDistance(int32 Floor,int32 Grade,int32 BossInterval=5);
 /** Guild rank D=0 gives 1 trip, C=1 gives 2, B and above gives 3. */
 UFUNCTION(BlueprintPure,Category="Tower") static int32 TripsHomeForRank(int32 GuildRank);
 /** Turns combat into habit shares. Memory decays unless bHoldMemory. */
 UFUNCTION(BlueprintCallable,Category="Tower") static void RecordFloor(UPARAM(ref) FTowerMemory& Memory,const FTowerFloorLog& Log,bool bHoldMemory);
 UFUNCTION(BlueprintPure,Category="Tower") static TArray<ETowerHabit> NoticedHabits(const FTowerMemory& Memory,int32 Max,bool bForce);
 UFUNCTION(BlueprintPure,Category="Tower") static FTowerFloorPlan PlanFloor(int32 Floor,const FTowerMemory& Memory,const TArray<FTowerCounterRule>& Rules,float ExtraBudget,int32 BossInterval=5);
};
