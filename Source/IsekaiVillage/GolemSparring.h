#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TowerExpeditionTypes.h"
#include "GolemSparring.generated.h"

class AVillageRuntime;
class AVillageGolemCitizen;
class AIsekaiVillageCharacter;
class ASlimeRunicMage;
class AProceduralMagicCircle;

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FGolemSparringMember
{
	GENERATED_BODY()
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FName AdventurerId;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<AVillageGolemCitizen> Actor;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float Health=100;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float TP=40;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float ReadyAt=0;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float GuardReduction=0;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bEvading=false;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bHealer=false;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FVector Formation=FVector::ZeroVector;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 WeaponTier=0;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 ArmorTier=0;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 TemperLevel=0;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float MaxHealth=100;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bVesselAnchorUsed=false;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FGolemSparringEnemy
{
	GENERATED_BODY()
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<ASlimeRunicMage> Actor;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<AProceduralMagicCircle> Circle;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FString Label;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) EElement Element=EElement::Fire;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float Health=50.f;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float MaxHealth=50.f;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float Damage=6.f;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) float ReadyAt=30.f;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 Turns=0;
};

/** Command-based, nonlethal integration slice. No tower rewards or permanent death. */
UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AGolemSparring : public AActor
{
	GENERATED_BODY()
public:
	AGolemSparring();
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<AVillageRuntime> Village;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<AIsekaiVillageCharacter> Commander;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<ASlimeRunicMage> Enemy;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TObjectPtr<AProceduralMagicCircle> GuardianCircle;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TArray<FGolemSparringEnemy> Minions;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 SelectedEnemyIndex=0;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TArray<FGolemSparringMember> Members;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FName Phase=TEXT("Idle");
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) int32 CurrentMember=INDEX_NONE;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TArray<FString> BattleLog;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FString LastError;
	UFUNCTION(BlueprintCallable) bool BeginSparring(AVillageRuntime* InVillage,AIsekaiVillageCharacter* Player);
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bFieldEncounter=false;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bVictory=false;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bPartyDefeated=false;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bHasFloorPlan=false;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FTowerFloorPlan FloorPlan;
	/** What the party did in this fight. The tower reads it on victory. */
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FTowerFloorLog EncounterLog;
	/** Call before BeginFieldEncounter. Without a plan the fight uses the original sparring rules. */
	UFUNCTION(BlueprintCallable) void ApplyFloorPlan(const FTowerFloorPlan& Plan,int32 Seed);
	UFUNCTION(BlueprintCallable) bool BeginFieldEncounter(AVillageRuntime* InVillage,AIsekaiVillageCharacter* Player,const TArray<AVillageGolemCitizen*>& Allies,FVector EnemyGround,int32 Variant);
	UFUNCTION(BlueprintPure) static float ElementMultiplier(EElement Attack,EElement Defender);
	UFUNCTION(BlueprintCallable) bool SelectEnemyTarget(int32 Index);
	UFUNCTION(BlueprintCallable) bool CycleEnemyTarget();
	UFUNCTION(BlueprintPure) int32 LivingMinionCount() const;
	UFUNCTION(BlueprintPure) float BossWardReduction() const;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) TArray<ETowerRelic> ActiveRelics;
	UFUNCTION(BlueprintPure) bool HasRelic(ETowerRelic Relic) const { return ActiveRelics.Contains(Relic); }
	UFUNCTION(BlueprintCallable) bool ExecuteAction(FName Action,int32 FriendlyTarget=-1);
	UFUNCTION(BlueprintCallable) void CancelSparring();
	UFUNCTION(BlueprintPure) FText BattleLine() const;
	float ReceiveDamage(AVillageGolemCitizen* Target,float Amount,AActor* Source);
	static AGolemSparring* FindFor(const AActor* Context);
	virtual void Tick(float DeltaSeconds) override;
	virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
	float EnemyReadyAt=20,EnemyDelay=0,AssemblyTime=0;
	bool bReleased=false;
	FVector EnemyPosition=FVector::ZeroVector;
	float EncounterHealth=90,EncounterDamage=12;
	int32 ShieldLeft=0,EnemyTurns=0,ActingEnemyIndex=0;
	float EnemyGuard=0;
	bool bEnemyEvading=false;
	FRandomStream TargetRandom;
	int32 PickEnemyTarget();
	void EnemyTurn();
	void MinionTurn(int32 MinionIdx);
	void SelectTurn();
	void Finish(const FString& Result);
	void ReleaseMembers();
	void Award(FName Id,FName Domain,float Effort);
	void Log(const FString& Message);
	void ApplyMemberStartingBonuses(FGolemSparringMember& M) const;
	bool HasSkill(int32 Member,FName Skill) const;
	bool HasPassive(int32 Member,FName Passive) const;
	bool SightToEnemy(int32 Member,const ASlimeRunicMage* TargetEnemy=nullptr) const;
	ASlimeRunicMage* GetTargetEnemy(int32 Index) const;
	bool AllEnemiesDefeated() const;
	bool IsCombatEnemy(const AActor* Actor) const;
	void EnsureValidTarget();
	void SpawnBossMinions();
	static UClass* SlimeClassForElement(EElement Elem);
	static const TCHAR* RuneTextureForElement(EElement Elem);
	static FLinearColor ColorForElement(EElement Elem);
	AProceduralMagicCircle* SpawnElementCircle(FVector Location,EElement Elem,float Scale);
};
