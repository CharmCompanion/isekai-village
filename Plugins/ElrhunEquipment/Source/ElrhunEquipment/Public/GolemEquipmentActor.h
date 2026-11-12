#pragma once
#include "CoreMinimal.h"
#include "Animation/SkeletalMeshActor.h"
#include "GolemEquipmentActor.generated.h"
class UStaticMesh;
class UStaticMeshComponent;
class UMaterialInterface;

USTRUCT(BlueprintType)
struct ELRHUNEQUIPMENT_API FGolemEquipmentItem {
 GENERATED_BODY()
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment") TObjectPtr<UStaticMesh> Mesh;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment") FName Bone;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment") FTransform Adjustment = FTransform::Identity;
};

UCLASS(Blueprintable)
class ELRHUNEQUIPMENT_API AGolemEquipmentActor : public ASkeletalMeshActor {
 GENERATED_BODY()
public:
 AGolemEquipmentActor();
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment") TArray<FGolemEquipmentItem> EquippedItems;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") bool bAnimateBowString = false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") int32 BowEquipmentIndex = 0;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") FVector BowUpperTip = FVector::ZeroVector;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") FVector BowLowerTip = FVector::ZeroVector;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") FVector BowArrowRest = FVector::ZeroVector;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") bool bUseBowArrowRest = false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") bool bHideBlockedPreviewArrow = true;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") bool bUseDiscreteBowRelease = false;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") FName BowDrawHand = TEXT("hand_r");
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") FVector BowDrawHandOffset = FVector::ZeroVector;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") FName BowDrawCurve = TEXT("ElrhunBowDraw");
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow", meta=(ClampMin="-1",ClampMax="1")) float BowDrawOverride = -1.f;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") TObjectPtr<UStaticMesh> BowStringSegmentMesh;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") TObjectPtr<UMaterialInterface> BowStringMaterial;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Equipment|Bow") TObjectPtr<UStaticMesh> NockedArrowMesh;
 UFUNCTION(BlueprintCallable, Category="Equipment") void RebuildEquipment();
 virtual void OnConstruction(const FTransform& Transform) override;
 virtual void BeginPlay() override;
 virtual void PostRegisterAllComponents() override;
 virtual void Tick(float DeltaSeconds) override;
#if WITH_EDITOR
 virtual bool ShouldTickIfViewportsOnly() const override { return bAnimateBowString; }
 virtual void PostEditChangeProperty(FPropertyChangedEvent& Event) override;
#endif
private:
 bool bRebuildingEquipment = false;
 UPROPERTY(Transient) TArray<TObjectPtr<UStaticMeshComponent>> SpawnedEquipment;
 UPROPERTY(Transient) TArray<TObjectPtr<UStaticMeshComponent>> BowStringComponents;
 UPROPERTY(Transient) TObjectPtr<UStaticMeshComponent> NockedArrowComponent;
 void UpdateBowString();
};
