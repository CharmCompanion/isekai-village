#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "GolemClothTools.generated.h"
class USkeletalMesh;
class UPhysicsAsset;
class UStaticMesh;
class UAnimSequence;
UCLASS()
class ELRHUNEQUIPMENTEDITOR_API UGolemClothTools : public UBlueprintFunctionLibrary {
 GENERATED_BODY()
public:
 UFUNCTION(BlueprintCallable, Category="Elrhun|Clothing")
 static bool CreateCapeCloth(USkeletalMesh* Mesh, int32 SectionIndex, UPhysicsAsset* PhysicsAsset, float PinHeight, float MaximumMovement);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Clothing")
 static FString InspectClothing(USkeletalMesh* Mesh);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Clothing")
 static bool FitBodyCollision(USkeletalMesh* Mesh, UPhysicsAsset* PhysicsAsset);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Clothing")
 static int32 EnsureWeaponCollision(UStaticMesh* Mesh);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Clothing")
 static bool FinalizeCapeAnchors(USkeletalMesh* Mesh, float CollisionClearance, float MaximumMovement);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Clothing")
 static void ResetCapeCloth(USkeletalMesh* Mesh);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Equipment")
 static bool ApplyHeldBonePose(UAnimSequence* Animation, const TMap<FName,FTransform>& LocalBonePose);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Equipment")
 static bool SetEquipmentCurve(UAnimSequence* Animation, FName CurveName, const TArray<float>& Times, const TArray<float>& Values);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Equipment")
 static bool NormalizeEquipmentRoot(UAnimSequence* Animation, bool PreserveChildPose = true, bool GroundFeet = false);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Equipment")
 static bool FitNativeHeadCollision(USkeletalMesh* Mesh, UPhysicsAsset* PhysicsAsset, FVector HeadCenter, float Radius);
 UFUNCTION(BlueprintCallable, Category="Elrhun|Equipment")
 static bool SetEquipmentBoneTrack(UAnimSequence* Animation, FName Bone, const TArray<FTransform>& LocalKeys);
};
