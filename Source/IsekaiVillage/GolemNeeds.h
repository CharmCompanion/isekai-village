#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GolemNeeds.generated.h"

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FGolemDriveState
{
 GENERATED_BODY()
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) bool bInitialized=false;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Fatigue=15;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Curiosity=20;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Loneliness=15;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Diligence=.6f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float StudyAffinity=.5f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Sociability=.5f;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName Interest=TEXT("Guard");
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FName Activity=TEXT("Work");
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) FString Reason=TEXT("My workplace needs me.");
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float Commitment=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float ThinkIn=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float ActivitySeconds=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) float LeisureCooldown=0;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TMap<FName,float> Practice;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TArray<FName> Skills;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TArray<FName> Passives;
 UPROPERTY(EditAnywhere,BlueprintReadWrite,SaveGame) TArray<FString> LearningLog;
};

UCLASS()
class ISEKAIVILLAGE_API UGolemNeedsLibrary : public UBlueprintFunctionLibrary
{
 GENERATED_BODY()
public:
 static void Initialize(FGolemDriveState& State,const FGuid& Id);
 static void Elapse(FGolemDriveState& State,float Seconds);
 UFUNCTION(BlueprintCallable,Category="Golems|Needs")
 static FName ChooseActivity(UPARAM(ref) FGolemDriveState& State,bool bCanWork,bool bCanStudy,bool bCanSocialize,bool bCarrying,float WorkUrgency,bool bNight);
 // Call only after a successful, meaningful action. Never award for selecting a command.
 UFUNCTION(BlueprintCallable,Category="Golems|Learning")
 static bool RecordPractice(UPARAM(ref) FGolemDriveState& State,FName Domain,float Effort,bool bSucceeded=true);
 UFUNCTION(BlueprintPure,Category="Golems|Learning") static float WalkingMultiplier(const FGolemDriveState& State);
 UFUNCTION(BlueprintPure,Category="Golems|Learning") static float WorkMultiplier(const FGolemDriveState& State);
 UFUNCTION(BlueprintPure,Category="Golems|Learning") static float FatigueMultiplier(const FGolemDriveState& State);
};
