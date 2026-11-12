#pragma once
#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TowerExpeditionTypes.h"
#include "TowerExpedition.generated.h"
class AVillageRuntime;
class AIsekaiVillageCharacter;
class AVillageGolemCitizen;
class UInstancedStaticMeshComponent;
class UTextRenderComponent;
class UMaterialInterface;
class AGolemSparring;
class UTownConstructionSave;

USTRUCT(BlueprintType)
struct FTowerTravellingCompanion
{
 GENERATED_BODY()
 UPROPERTY() TObjectPtr<AVillageGolemCitizen> Actor;
 UPROPERTY() FName Id;
 UPROPERTY() FVector Home=FVector::ZeroVector;
 int32 TrailIndex=0;
 bool bTickWasEnabled=true;
};
/** First exploration slice. Remains in the village world, with a separate modular floor. */
UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ATowerExpedition : public AActor
{
 GENERATED_BODY()
public:
 ATowerExpedition();
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") FVector FloorOrigin=FVector(400000,0,50000);
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") TArray<FTowerRegionModule> Regions;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") TArray<FIntPoint> Connections;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") TObjectPtr<UMaterialInterface> StoneMaterial;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") TObjectPtr<UMaterialInterface> MossMaterial;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") TObjectPtr<UMaterialInterface> CrystalMaterial;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") int32 BreadCost=2;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") int32 CampWoodCost=4;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower") int32 CampStoneCost=2;
 /** Counter rules the tower can spend its budget on. Edit rows here; no code needed. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower|Adaptation") TArray<FTowerCounterRule> CounterRules;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower|Adaptation") int32 BossInterval=5;
 /** Share of skipped floors' budgets added to a Leap landing floor. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower|Adaptation") float LeapBudgetShare=1;
 /** Extra budget per camp rest when regular enemies respawn. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower|Adaptation") float RespawnBudgetPerRest=3;
 /** Share of this run's gathered items lost when the run fails. */
 UPROPERTY(EditAnywhere,BlueprintReadWrite,Category="Tower|Adaptation") float FailureLootLoss=.5f;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") bool bInside=false;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") TObjectPtr<AVillageRuntime> Village;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") TObjectPtr<AIsekaiVillageCharacter> Commander;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") TArray<FTowerDeposit> Deposits;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") FString LastMessage;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") TArray<FTowerTravellingCompanion> Companions;
 UPROPERTY(VisibleAnywhere,BlueprintReadOnly,Category="Tower") TObjectPtr<AGolemSparring> GuardianBattle;
 UFUNCTION(BlueprintCallable,Category="Tower") bool BuildFloor();
 UFUNCTION(BlueprintCallable,Category="Tower") bool Depart(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool Interact(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool ReturnToVillage(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool GatherDeposit(AIsekaiVillageCharacter* Player,FName Id);
 UFUNCTION(BlueprintCallable,Category="Tower") bool UseCamp(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool ShareRations(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool ActivateAltar(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool ChallengeGuardian(AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable,Category="Tower") bool ChoosePortal(AIsekaiVillageCharacter* Player,ETowerPortal Portal);
 /** Ends the run and sends the party home. A failed run loses part of this run's gathered items. */
 UFUNCTION(BlueprintCallable,Category="Tower") bool EndRun(AIsekaiVillageCharacter* Player,bool bFailed);
 /** At the gate, before a run: steps through the floors the gate can start from. */
 UFUNCTION(BlueprintCallable,Category="Tower") bool CycleStartFloor(AIsekaiVillageCharacter* Player);
 /** Saves a guardian victory and opens the portals. Safe to call again while saving retries. */
 bool CommitGuardianClear(const FTowerFloorLog& Log);
 UFUNCTION(BlueprintPure,Category="Tower") bool FloorCleared() const;
 UFUNCTION(BlueprintPure,Category="Tower") TArray<ETowerPortal> AvailablePortals() const;
 UFUNCTION(BlueprintPure,Category="Tower") FString PortalPreview(ETowerPortal Portal) const;
 UFUNCTION(BlueprintPure,Category="Tower") FVector PortalPoint(ETowerPortal Portal) const;
 /** Guild rank is the highest rank among hired adventurers. D=0, C=1, B=2, A=3. */
 UFUNCTION(BlueprintPure,Category="Tower") int32 GuildRank() const;
 UFUNCTION(BlueprintPure,Category="Tower") int32 TripsHomeAllowed() const;
 UFUNCTION(BlueprintPure,Category="Tower") TArray<int32> StartableFloors() const;
 UFUNCTION(BlueprintPure,Category="Tower") FText StatusLine(AIsekaiVillageCharacter* Player) const;
 UFUNCTION(BlueprintPure,Category="Tower") bool DepositAvailable(FName Id) const;
 UFUNCTION(BlueprintPure,Category="Tower") FVector EntryPoint() const;
 UFUNCTION(BlueprintPure,Category="Tower") FVector CampPoint() const;
 UFUNCTION(BlueprintPure,Category="Tower") FVector GuardianPoint() const;
 UFUNCTION(BlueprintPure,Category="Tower") FVector AltarPoint() const;
 UFUNCTION(BlueprintPure,Category="Tower") bool FloorAltarAvailable() const;
 UFUNCTION(BlueprintPure,Category="Tower") ETowerRelic CurrentFloorAltarRelic() const;
 UFUNCTION(BlueprintPure,Category="Tower") static FString RelicName(ETowerRelic Relic);
 UFUNCTION(BlueprintPure,Category="Tower") static FString RelicDescription(ETowerRelic Relic);
 static ATowerExpedition* Find(const AActor* Context);
 void PreserveVillagePositions(UTownConstructionSave* Saved) const;
 virtual void Tick(float DeltaSeconds) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Stone;
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Moss;
 UPROPERTY() TObjectPtr<UInstancedStaticMeshComponent> Gems;
 UPROPERTY() TArray<TObjectPtr<UTextRenderComponent>> Labels;
 UPROPERTY() TArray<FVector> Trail;
 FVector ReturnPoint=FVector::ZeroVector;
 float NeedsIn=0,RetrySaveIn=0;
 bool bBuilt=false,bFailurePending=false;
 void PlanCurrentFloor(float ExtraBudget,bool bRespawn);
 bool MoveToFloor(AIsekaiVillageCharacter* Player,int32 Steps,bool bLeap);
 bool PartyCanStand(const FVector& Spawn) const;
 void PlaceParty(const FVector& Spawn);
 /** Saves the already-changed floor state and sends the party home. Restores Before if anything fails. */
 bool GoHome(AIsekaiVillageCharacter* Player,const FTowerFloorProgress& Before,const FString& Message);
 int32 RenderDay=-1;
 bool LinkVillage();
 FVector RegionCenter(FName Id) const;
 bool Busy() const;
 bool At(AIsekaiVillageCharacter* Player,const FVector& Point,float Radius=300) const;
 bool CheckStanding(const FVector& Point,AActor* Ignore) const;
 void RestoreParty();
 void FollowParty(float DeltaSeconds);
 void AddBox(UInstancedStaticMeshComponent* Mesh,const FVector& Center,const FVector& Size,float Yaw=0);
 void AddLabel(const FString& Text,const FVector& Position);
 void SyncDrives();
 bool Fail(const FString& Message);
};
