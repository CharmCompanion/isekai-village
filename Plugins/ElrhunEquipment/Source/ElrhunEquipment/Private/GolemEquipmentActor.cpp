#include "GolemEquipmentActor.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimInstance.h"
#include "Modules/ModuleManager.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ElrhunEquipment)

AGolemEquipmentActor::AGolemEquipmentActor() {
 PrimaryActorTick.bCanEverTick = true;
 PrimaryActorTick.bStartWithTickEnabled = false;
 PrimaryActorTick.TickGroup = TG_PostUpdateWork;
}

void AGolemEquipmentActor::RebuildEquipment() {
 if (HasAnyFlags(RF_ClassDefaultObject | RF_ArchetypeObject)) return;
 if (bRebuildingEquipment) return;
 TGuardValue<bool> RebuildGuard(bRebuildingEquipment, true);
 for (UStaticMeshComponent* Component : SpawnedEquipment) if (IsValid(Component)) Component->DestroyComponent();
 SpawnedEquipment.Reset();
 for (UStaticMeshComponent* Component : BowStringComponents) if (IsValid(Component)) Component->DestroyComponent();
 BowStringComponents.Reset();
 if (IsValid(NockedArrowComponent)) NockedArrowComponent->DestroyComponent();
 NockedArrowComponent = nullptr;
 SetActorTickEnabled(bAnimateBowString);
 USkeletalMeshComponent* Body = GetSkeletalMeshComponent();
 if (!Body || !Body->GetSkeletalMeshAsset()) return;
 const FReferenceSkeleton& Skeleton = Body->GetSkeletalMeshAsset()->GetRefSkeleton();
 const TArray<FTransform>& Pose = Skeleton.GetRefBonePose();
 for (const FGolemEquipmentItem& Item : EquippedItems) {
  int32 Index = Skeleton.FindBoneIndex(Item.Bone);
  if (!Item.Mesh || Index == INDEX_NONE) continue;
  FTransform BoneToMesh = Pose[Index];
  for (int32 Parent = Skeleton.GetParentIndex(Index); Parent != INDEX_NONE; Parent = Skeleton.GetParentIndex(Parent))
   BoneToMesh *= Pose[Parent];
  UStaticMeshComponent* Part = NewObject<UStaticMeshComponent>(this, NAME_None, RF_Transient);
  Part->CreationMethod = EComponentCreationMethod::Instance;
  Part->SetStaticMesh(Item.Mesh);
  Part->SetupAttachment(Body, Item.Bone);
  Part->SetRelativeTransform(Item.Adjustment * BoneToMesh.Inverse());
  Part->SetMobility(EComponentMobility::Movable);
  Part->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
  Part->SetCollisionObjectType(ECC_WorldDynamic);
  Part->SetCollisionResponseToAllChannels(ECR_Ignore);
  Part->SetCollisionResponseToChannel(ECC_Visibility, ECR_Block);
  Part->SetGenerateOverlapEvents(false);
  Part->CanCharacterStepUpOn = ECB_No;
  Part->IgnoreActorWhenMoving(this, true);
  Part->RegisterComponent();
  SpawnedEquipment.Add(Part);
 }
 if (bAnimateBowString && BowStringSegmentMesh && SpawnedEquipment.IsValidIndex(BowEquipmentIndex)) {
  auto AddBowPart = [&](UStaticMesh* Mesh) {
   UStaticMeshComponent* Part = NewObject<UStaticMeshComponent>(this, NAME_None, RF_Transient);
   Part->CreationMethod = EComponentCreationMethod::Instance;
   Part->SetupAttachment(Body); Part->SetStaticMesh(Mesh);
   Part->SetMobility(EComponentMobility::Movable);
   Part->SetCollisionEnabled(ECollisionEnabled::NoCollision);
   Part->SetGenerateOverlapEvents(false); Part->RegisterComponent();
   return Part;
  };
  for (int32 I=0; I<2; ++I) {
   UStaticMeshComponent* Part = AddBowPart(BowStringSegmentMesh);
   if (BowStringMaterial) Part->SetMaterial(0, BowStringMaterial);
   BowStringComponents.Add(Part);
  }
  if (NockedArrowMesh) NockedArrowComponent = AddBowPart(NockedArrowMesh);
  UpdateBowString();
 }
}

void AGolemEquipmentActor::Tick(float DeltaSeconds) {
 Super::Tick(DeltaSeconds); UpdateBowString();
}

void AGolemEquipmentActor::UpdateBowString() {
 USkeletalMeshComponent* Body = GetSkeletalMeshComponent();
 if (!bAnimateBowString || !Body || BowStringComponents.Num()!=2 || !SpawnedEquipment.IsValidIndex(BowEquipmentIndex)) return;
 UStaticMeshComponent* Bow = SpawnedEquipment[BowEquipmentIndex];
 if (!IsValid(Bow)) return;
 const FVector Upper = Bow->GetComponentTransform().TransformPosition(BowUpperTip);
 const FVector Lower = Bow->GetComponentTransform().TransformPosition(BowLowerTip);
 const FVector Rest = (Upper+Lower)*.5f;
 float Draw = BowDrawOverride;
 if (Draw<0) Draw = Body->GetAnimInstance() ? Body->GetAnimInstance()->GetCurveValue(BowDrawCurve) : 0.f;
 Draw = FMath::Clamp(Draw,0.f,1.f);
 if (bUseDiscreteBowRelease) Draw=Draw>=.5f ? 1.f : 0.f;
 FVector Hand = Body->GetSocketTransform(BowDrawHand).TransformPosition(BowDrawHandOffset);
 Hand = Rest + (Hand-Rest).GetClampedToMaxSize(120.f);
 const FVector Middle = FMath::Lerp(Rest,Hand,Draw);
 auto SetSegment = [](UStaticMeshComponent* Part,const FVector& A,const FVector& B) {
  const FVector Delta=B-A;
  Part->SetWorldLocationAndRotation((A+B)*.5f,FRotationMatrix::MakeFromZ(Delta).ToQuat());
  // Engine cylinder: 100 cm long, 50 cm radius. String radius is 0.075 cm.
  Part->SetWorldScale3D(FVector(.0015f,.0015f,Delta.Size()/100.f));
 };
 SetSegment(BowStringComponents[0],Upper,Middle); SetSegment(BowStringComponents[1],Middle,Lower);
 if (NockedArrowComponent) {
  const FVector ArrowRest=bUseBowArrowRest ? Bow->GetComponentTransform().TransformPosition(BowArrowRest) : Rest;
  FVector Aim=(ArrowRest-Middle).GetSafeNormal();
  if (Aim.IsNearlyZero()) Aim=Bow->GetForwardVector();
  bool Visible=Draw>.1f;
  if (Visible && bHideBlockedPreviewArrow) {
   // Keep the nock's intended finger contact out of the owner clearance trace.
   FHitResult Hit;FCollisionQueryParams Params(SCENE_QUERY_STAT(ElrhunNockedArrowClearance),false);
   Visible=!Body->LineTraceComponent(Hit,Middle+Aim*8.f,Middle+Aim*75.f,Params);
  }
  NockedArrowComponent->SetVisibility(Visible);
  NockedArrowComponent->SetWorldLocationAndRotation(Middle,Aim.Rotation());
  NockedArrowComponent->SetWorldScale3D(FVector::OneVector);
 }
}
void AGolemEquipmentActor::OnConstruction(const FTransform& Transform) {
 Super::OnConstruction(Transform); RebuildEquipment();
}
void AGolemEquipmentActor::BeginPlay() {
 Super::BeginPlay(); RebuildEquipment();
}
void AGolemEquipmentActor::PostRegisterAllComponents() {
 Super::PostRegisterAllComponents(); RebuildEquipment();
}
#if WITH_EDITOR
void AGolemEquipmentActor::PostEditChangeProperty(FPropertyChangedEvent& Event) {
 Super::PostEditChangeProperty(Event);
 if (!HasAnyFlags(RF_ClassDefaultObject | RF_ArchetypeObject)) RebuildEquipment();
}
#endif
