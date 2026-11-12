#pragma once
#include "CoreMinimal.h"
#include "VillageCitizen.h"
#include "VillageGolemTypes.h"
#include "VillageGolemCitizen.generated.h"

class AVillageRuntime;
class UCapsuleComponent;
class USkeletalMeshComponent;
class UAnimSequence;
class ALinchpinProp;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AVillageGolemCitizen : public AVillageCitizen
{
	GENERATED_BODY()
public:
	AVillageGolemCitizen();
	virtual void BeginPlay() override;
	virtual void Tick(float DeltaSeconds) override;
	virtual float TakeDamage(float Amount,const FDamageEvent& Event,AController* InstigatorController,AActor* Causer) override;
	virtual bool TryPlayerOffer(AIsekaiVillageCharacter* Player) override;
		virtual FText OfferLine() const override;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<UCapsuleComponent> MovementCapsule;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<USkeletalMeshComponent> GolemMesh;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) FGuid GolemId;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) FName WorkPlot;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) FName AppearanceClass;
	UPROPERTY(VisibleAnywhere,BlueprintReadOnly) bool bFemaleAppearance=false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) bool bRouteBlocked = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) int32 RouteIndex = 0;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TArray<FVector> Route;
	void Configure(AVillageRuntime* Village, const FVillageGolemRecord& Record);
	void SetExpeditionWalking(bool bMoving) { SetWalking(bMoving); }
	void SetHarvesting(bool bInHarvesting, EVillagePlace InPlace);
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) bool bHarvesting = false;
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly) EVillagePlace HarvestPlace = EVillagePlace::Forest;

	// Resident Linchpin Prop Work Routines
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Golem|Routine")
	EGolemWorkRoutine CurrentRoutine = EGolemWorkRoutine::None;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Golem|Routine")
	TWeakObjectPtr<ALinchpinProp> CurrentStationProp;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Golem|Routine")
	float RoutineTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Golem|Routine")
	float GreetCooldown = 0.0f;

	UFUNCTION(BlueprintCallable, Category = "Golem|Routine")
	void SetWorkRoutine(EGolemWorkRoutine InRoutine, ALinchpinProp* InStation = nullptr);

	UFUNCTION(BlueprintPure, Category = "Golem|Routine")
	EGolemWorkRoutine GetWorkRoutine() const { return CurrentRoutine; }

	UFUNCTION(BlueprintPure, Category = "Golem|Routine")
	ALinchpinProp* GetStationProp() const { return CurrentStationProp.Get(); }

private:
	UPROPERTY(Transient) TObjectPtr<AVillageRuntime> Village;
	UPROPERTY(Transient) TObjectPtr<UAnimSequence> IdleAnimation;
	UPROPERTY(Transient) TObjectPtr<UAnimSequence> WalkAnimation;
	bool bWalking = false;
	FVector RoutedGoal = FVector(UE_BIG_NUMBER);
	float RetryIn = 0;
	float HarvestAnimTime = 0.0f;
	void SetWalking(bool bMoving);
	void TickRoutineBehaviors(float DeltaSeconds);
};
