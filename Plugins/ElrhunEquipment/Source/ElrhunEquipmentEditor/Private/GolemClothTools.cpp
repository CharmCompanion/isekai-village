#include "GolemClothTools.h"
#include "Engine/SkeletalMesh.h"
#include "ClothingAsset.h"
#include "ClothingAssetFactoryInterface.h"
#include "ClothingSystemEditorInterfaceModule.h"
#include "ChaosCloth/ChaosClothConfig.h"
#include "Modules/ModuleManager.h"
#include "Rendering/SkeletalMeshModel.h"
#include "Rendering/SkeletalMeshLODModel.h"
#include "PhysicsEngine/PhysicsAsset.h"
#include "PhysicsEngine/SkeletalBodySetup.h"
#include "Engine/StaticMesh.h"
#include "StaticMeshResources.h"
#include "Animation/AnimSequence.h"
#include "Animation/Skeleton.h"
#include "Animation/AnimData/IAnimationDataController.h"
#include "Animation/AnimData/IAnimationDataModel.h"

IMPLEMENT_MODULE(FDefaultModuleImpl, ElrhunEquipmentEditor)

bool UGolemClothTools::FitNativeHeadCollision(USkeletalMesh* Mesh,UPhysicsAsset* Physics,FVector Center,float Radius) {
 if (!Mesh || !Physics || Radius<=0) return false;
 const FReferenceSkeleton& Ref=Mesh->GetRefSkeleton(); const int32 Index=Ref.FindBoneIndex(TEXT("head")); if (Index==INDEX_NONE) return false;
 FTransform Bone=Ref.GetRefBonePose()[Index];
 for (int32 Parent=Ref.GetParentIndex(Index);Parent!=INDEX_NONE;Parent=Ref.GetParentIndex(Parent)) Bone*=Ref.GetRefBonePose()[Parent];
 Physics->Modify();USkeletalBodySetup* Head=nullptr;
 for (USkeletalBodySetup* Body:Physics->SkeletalBodySetups) if (Body && Body->BoneName==TEXT("head")) { Head=Body;break; }
 if (!Head) { Head=NewObject<USkeletalBodySetup>(Physics,NAME_None,RF_Transactional);Head->BoneName=TEXT("head");Physics->SkeletalBodySetups.Add(Head); }
 Head->Modify();Head->AggGeom.EmptyElements();Head->PhysicsType=PhysType_Kinematic;
 FKSphereElem Shape;Shape.Center=Bone.InverseTransformPosition(Center);Shape.Radius=Radius/FMath::Max(.0001f,static_cast<float>(Bone.GetScale3D().GetAbsMax()));Head->AggGeom.SphereElems.Add(Shape);
 Head->InvalidatePhysicsData();Head->CreatePhysicsMeshes();Physics->UpdateBodySetupIndexMap();Physics->UpdateBoundsBodiesArray();Physics->MarkPackageDirty();return true;
}

bool UGolemClothTools::SetEquipmentBoneTrack(UAnimSequence* Animation,FName Bone,const TArray<FTransform>& Keys) {
 if (!Animation || !Animation->GetSkeleton() || !Animation->GetDataModel() || Keys.Num()!=Animation->GetDataModel()->GetNumberOfKeys() || Animation->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Bone)==INDEX_NONE) return false;
 IAnimationDataController& Controller=Animation->GetController();Controller.OpenBracket(NSLOCTEXT("Elrhun","SafeEquipmentTrack","Correct equipment arm clearance"),false);Controller.AddBoneCurve(Bone,false);
 TArray<FVector> Positions,Scales;TArray<FQuat> Rotations;
 for (const FTransform& Value:Keys) { Positions.Add(Value.GetTranslation());Scales.Add(Value.GetScale3D());Rotations.Add(Value.GetRotation().GetNormalized()); }
 const bool Result=Controller.SetBoneTrackKeys(Bone,Positions,Rotations,Scales,false);Controller.CloseBracket(false);Animation->MarkPackageDirty();return Result;
}

bool UGolemClothTools::NormalizeEquipmentRoot(UAnimSequence* Animation, bool PreserveChildPose, bool GroundFeet) {
 if (!Animation || !Animation->GetSkeleton() || !Animation->GetDataModel()) return false;
 const IAnimationDataModel* Model=Animation->GetDataModel();
 const FReferenceSkeleton& Ref=Animation->GetSkeleton()->GetReferenceSkeleton();
 const int32 Count=Model->GetNumberOfKeys();
 if (Count<1 || Ref.GetNum()<2) return false;
 TArray<FName> Names; Model->GetBoneTrackNames(Names); TSet<FName> Tracks(Names);
 TArray<int32> Children;
 for (int32 Bone=1;Bone<Ref.GetNum();++Bone) if (Ref.GetParentIndex(Bone)==0) Children.Add(Bone);
 if (Children.IsEmpty()) return false;
 const TArray<FTransform>& Bind=Ref.GetRefBonePose();
 auto LocalAt=[&](int32 Bone,int32 Frame) { return Tracks.Contains(Ref.GetBoneName(Bone)) ? Model->GetBoneTrackTransform(Ref.GetBoneName(Bone),FFrameNumber(Frame)) : Bind[Bone]; };
 const FVector FirstRoot=LocalAt(0,0).GetTranslation();
 TArray<FTransform> RefWorld; RefWorld.SetNum(Ref.GetNum());
 for (int32 Bone=0;Bone<Ref.GetNum();++Bone) RefWorld[Bone]=Ref.GetParentIndex(Bone)==INDEX_NONE ? Bind[Bone] : Bind[Bone]*RefWorld[Ref.GetParentIndex(Bone)];
 const int32 Left=Ref.FindBoneIndex(TEXT("foot_l")),Right=Ref.FindBoneIndex(TEXT("foot_r"));
 if (GroundFeet && (Left==INDEX_NONE || Right==INDEX_NONE)) return false;
 const double RefFloor=GroundFeet ? FMath::Min(RefWorld[Left].GetTranslation().Z,RefWorld[Right].GetTranslation().Z) : 0.;
 TMap<int32,TArray<FTransform>> Baked;
 Baked.Add(0); for (int32 Child:Children) Baked.Add(Child);
 for (int32 Frame=0;Frame<Count;++Frame) {
  TArray<FTransform> Local; Local.SetNum(Ref.GetNum());
  for (int32 Bone=0;Bone<Ref.GetNum();++Bone) Local[Bone]=LocalAt(Bone,Frame);
  if (PreserveChildPose) for (int32 Child:Children) {
   FTransform World=Local[Child]*Local[0];
   World.AddToTranslation(FVector(-FirstRoot.X,-FirstRoot.Y,0.));
   Local[Child]=World.GetRelativeTransform(Bind[0]);
  }
  Local[0]=Bind[0];
  if (GroundFeet) {
   TArray<FTransform> World; World.SetNum(Ref.GetNum());
   for (int32 Bone=0;Bone<Ref.GetNum();++Bone) World[Bone]=Ref.GetParentIndex(Bone)==INDEX_NONE ? Local[Bone] : Local[Bone]*World[Ref.GetParentIndex(Bone)];
   const double Height=FMath::Min(World[Left].GetTranslation().Z,World[Right].GetTranslation().Z)-RefFloor;
   const FVector Offset=Bind[0].InverseTransformVector(FVector(0.,0.,Height));
   for (int32 Child:Children) Local[Child].AddToTranslation(-Offset);
  }
  for (auto& Pair:Baked) Pair.Value.Add(Local[Pair.Key]);
 }
 IAnimationDataController& Controller=Animation->GetController();
 Controller.OpenBracket(NSLOCTEXT("Elrhun","GroundEquipment","Preserve body height with a neutral equipment root"),false);
 bool Success=true;
 for (const auto& Pair:Baked) {
  const FName Name=Ref.GetBoneName(Pair.Key); Controller.AddBoneCurve(Name,false);
  TArray<FVector> Positions,Scales; TArray<FQuat> Rotations;
  for (const FTransform& Value:Pair.Value) { Positions.Add(Value.GetTranslation()); Rotations.Add(Value.GetRotation().GetNormalized()); Scales.Add(Value.GetScale3D()); }
  Success=Controller.SetBoneTrackKeys(Name,Positions,Rotations,Scales,false) && Success;
 }
 Controller.CloseBracket(false); Animation->bForceRootLock=true; Animation->MarkPackageDirty(); return Success;
}

bool UGolemClothTools::ApplyHeldBonePose(UAnimSequence* Animation, const TMap<FName,FTransform>& LocalBonePose) {
 if (!Animation || LocalBonePose.IsEmpty() || !Animation->GetDataModel()) return false;
 IAnimationDataController& Controller=Animation->GetController();
 const int32 Count=Animation->GetDataModel()->GetNumberOfKeys();
 if (Count<1) return false;
 Controller.OpenBracket(NSLOCTEXT("Elrhun","HeldBonePose","Fit native hand pose"),false);
 bool Success=true;
 for (const auto& Pair:LocalBonePose) {
  if (!Animation->GetSkeleton() || Animation->GetSkeleton()->GetReferenceSkeleton().FindBoneIndex(Pair.Key)==INDEX_NONE) { Success=false; continue; }
  Controller.AddBoneCurve(Pair.Key,false);
  TArray<FVector> Positions; Positions.Init(Pair.Value.GetTranslation(),Count);
  TArray<FQuat> Rotations; Rotations.Init(Pair.Value.GetRotation().GetNormalized(),Count);
  TArray<FVector> Scales; Scales.Init(Pair.Value.GetScale3D(),Count);
  Success=Controller.SetBoneTrackKeys(Pair.Key,Positions,Rotations,Scales,false) && Success;
 }
 Controller.CloseBracket(false); Animation->MarkPackageDirty(); return Success;
}

bool UGolemClothTools::SetEquipmentCurve(UAnimSequence* Animation,FName CurveName,const TArray<float>& Times,const TArray<float>& Values) {
 if (!Animation || Times.Num()!=Values.Num() || Times.IsEmpty()) return false;
 IAnimationDataController& Controller=Animation->GetController();
 const FAnimationCurveIdentifier Curve(CurveName,ERawCurveTrackTypes::RCT_Float);
 Controller.OpenBracket(NSLOCTEXT("Elrhun","EquipmentCurve","Animate bow draw"),false);
 Controller.AddCurve(Curve,4,false); TArray<FRichCurveKey> Keys;
 for (int32 I=0;I<Times.Num();++I) { FRichCurveKey Key(Times[I],Values[I]);Key.InterpMode=RCIM_Linear;Keys.Add(Key); }
 const bool Success=Controller.SetCurveKeys(Curve,Keys,false);
 Controller.CloseBracket(false); Animation->MarkPackageDirty();return Success;
}

bool UGolemClothTools::CreateCapeCloth(USkeletalMesh* Mesh, int32 SectionIndex, UPhysicsAsset* PhysicsAsset, float PinHeight, float MaximumMovement) {
 if (!Mesh || !PhysicsAsset || MaximumMovement <= 0) return false;
 auto& Module = FModuleManager::LoadModuleChecked<FClothingSystemEditorInterfaceModule>("ClothingSystemEditorInterface");
 UClothingAssetFactoryBase* Factory = Module.GetClothingAssetFactory();
 if (!Factory) return false;
 FSkeletalMeshClothBuildParams Params;
 Params.AssetName = FString::Printf(TEXT("ElrhunCape_%d"), SectionIndex);
 Params.LodIndex = 0;
 Params.SourceSection = SectionIndex;
 Params.bRemoveFromMesh = false;
 Params.PhysicsAsset = PhysicsAsset;
 UClothingAssetCommon* Asset = Cast<UClothingAssetCommon>(Factory->CreateFromSkeletalMesh(Mesh, Params));
 if (!Asset || Asset->LodData.IsEmpty()) return false;
 Asset->PhysicsAsset = PhysicsAsset;
 FClothLODDataCommon& Lod = Asset->LodData[0];
 FPointWeightMap Mask(Lod.PhysicalMeshData.Vertices.Num());
 Mask.Name = TEXT("Pinned neckline and collision clearance");
 Mask.CurrentTarget = static_cast<uint8>(EWeightMapTargetCommon::MaxDistance);
 Mask.bEnabled = true;
 for (int32 Index = 0; Index < Mask.Values.Num(); ++Index) {
  const float Height = Lod.PhysicalMeshData.Vertices[Index].Z;
  Mask.Values[Index] = FMath::Clamp((PinHeight - Height) / 30.f, 0.f, 1.f) * MaximumMovement;
 }
 Lod.PointWeightMaps.Add(Mask);
 Lod.PushWeightsToMesh();
 UChaosClothConfig* Config = NewObject<UChaosClothConfig>(Asset);
 Config->CollisionThickness = .35f;
 Config->bUseCCD = true;
 Config->bUseSelfCollisions = true;
 Config->SelfCollisionThickness = .25f;
 Config->GravityScale = .4f;
 Asset->ClothConfigs.Add(UChaosClothConfig::StaticClass()->GetFName(), Config);
 UChaosClothSharedSimConfig* Shared = NewObject<UChaosClothSharedSimConfig>(Asset);
 Shared->IterationCount = 5;
 Shared->SubdivisionCount = 2;
 Asset->ClothConfigs.Add(UChaosClothSharedSimConfig::StaticClass()->GetFName(), Shared);
 Mesh->Modify();
 Mesh->AddClothingAsset(Asset);
 Asset->ApplyParameterMasks();
 Asset->InvalidateAllCachedData();
 bool Bound=false;
 {
  FScopedSkeletalMeshPostEditChange Change(Mesh);
  auto& LodModel=Mesh->GetImportedModel()->LODModels[0];
  const int32 OriginalIndex=LodModel.Sections[SectionIndex].OriginalDataSectionIndex;
  Bound=Asset->BindToSkeletalMesh(Mesh, 0, SectionIndex, 0);
  if (Bound) {
   auto& Data=LodModel.UserSectionsData.FindOrAdd(OriginalIndex);
   Data.CorrespondClothAssetIndex=Mesh->GetMeshClothingAssets().IndexOfByKey(Asset);
   Data.ClothingData.AssetGuid=Asset->GetAssetGuid();Data.ClothingData.AssetLodIndex=0;
  }
 }
 Mesh->MarkPackageDirty();
 return Bound;
}

FString UGolemClothTools::InspectClothing(USkeletalMesh* Mesh) {
 if (!Mesh) return TEXT("null");
 FString Result = TEXT("{\"sections\":[");
 if (const FSkeletalMeshModel* Model = Mesh->GetImportedModel(); Model && !Model->LODModels.IsEmpty()) {
  const auto& Sections = Model->LODModels[0].Sections;
  for (int32 I = 0; I < Sections.Num(); ++I) {
   const auto& Section = Sections[I];
   if (I) Result += TEXT(",");
   Result += FString::Printf(TEXT("{\"section\":%d,\"material\":%d,\"vertices\":%d,\"cloth\":%s}"),I,Section.MaterialIndex,Section.NumVertices,Section.HasClothingData()?TEXT("true"):TEXT("false"));
  }
 }
 Result += TEXT("],\"cloth_assets\":[");
 bool First = true;
 for (UClothingAssetBase* Base : Mesh->GetMeshClothingAssets()) {
  const UClothingAssetCommon* Asset = Cast<UClothingAssetCommon>(Base);
  if (!Asset || Asset->LodData.IsEmpty()) continue;
  if (!First) Result += TEXT(","); First = false;
  int32 Pinned=0, Moving=0;
  for (const FPointWeightMap& Mask : Asset->LodData[0].PointWeightMaps)
   if (Mask.bEnabled && Mask.CurrentTarget == static_cast<uint8>(EWeightMapTargetCommon::MaxDistance))
    for (float Value : Mask.Values) {if (Value <= 0) ++Pinned; else ++Moving;}
  Result += FString::Printf(TEXT("{\"name\":\"%s\",\"pinned\":%d,\"moving\":%d,\"physics\":\"%s\"}"),*Asset->GetName(),Pinned,Moving,*GetPathNameSafe(Asset->PhysicsAsset));
 }
 Result += TEXT("],\"collision_bodies\":[");
 if (const UPhysicsAsset* Physics = Mesh->GetPhysicsAsset()) {
  for (int32 I=0; I<Physics->SkeletalBodySetups.Num(); ++I) {
   const USkeletalBodySetup* Body=Physics->SkeletalBodySetups[I];
   if (I) Result+=TEXT(",");
   Result+=FString::Printf(TEXT("{\"bone\":\"%s\",\"spheres\":%d,\"capsules\":%d,\"tapered_capsules\":%d,\"convex\":%d}"),*Body->BoneName.ToString(),Body->AggGeom.SphereElems.Num(),Body->AggGeom.SphylElems.Num(),Body->AggGeom.TaperedCapsuleElems.Num(),Body->AggGeom.ConvexElems.Num());
  }
 }
 return Result+TEXT("]}");
}

bool UGolemClothTools::FitBodyCollision(USkeletalMesh* Mesh, UPhysicsAsset* Physics) {
 if (!Mesh || !Physics) return false;
 Physics->Modify(); Physics->SkeletalBodySetups.Reset(); Physics->ConstraintSetup.Reset(); Physics->CollisionDisableTable.Reset();
 const FReferenceSkeleton& Ref=Mesh->GetRefSkeleton();
 auto BoneTransform=[&](FName Name) {
  const int32 Index=Ref.FindBoneIndex(Name); if (Index==INDEX_NONE) return FTransform::Identity;
  FTransform T=Ref.GetRefBonePose()[Index];
  for (int32 P=Ref.GetParentIndex(Index);P!=INDEX_NONE;P=Ref.GetParentIndex(P)) T*=Ref.GetRefBonePose()[P];
  return T;
 };
 auto NewBody=[&](FName Name) {
  USkeletalBodySetup* Body=NewObject<USkeletalBodySetup>(Physics,NAME_None,RF_Transactional);
  Body->BoneName=Name; Body->PhysicsType=PhysType_Kinematic; Body->DefaultInstance.SetCollisionProfileName(TEXT("Pawn"));
  Physics->SkeletalBodySetups.Add(Body); return Body;
 };
 auto Sphere=[&](USkeletalBodySetup* Body,FVector Center,float Radius) {
  const FTransform Bone=BoneTransform(Body->BoneName);
  FKSphereElem Shape;Shape.Center=Bone.InverseTransformPosition(Center);Shape.Radius=Radius/FMath::Max(.0001f,static_cast<float>(Bone.GetScale3D().GetAbsMax()));Body->AggGeom.SphereElems.Add(Shape);
 };
 auto Capsule=[&](USkeletalBodySetup* Body,FVector A,FVector B,float Radius) {
  const FTransform Inverse=BoneTransform(Body->BoneName).Inverse(); A=Inverse.TransformPosition(A);B=Inverse.TransformPosition(B);
  const float LocalRadius=Radius/FMath::Max(.0001f,static_cast<float>(BoneTransform(Body->BoneName).GetScale3D().GetAbsMax()));
  FKSphylElem Shape;Shape.Center=(A+B)*.5;Shape.Radius=LocalRadius;Shape.Length=FMath::Max(0.f,static_cast<float>((B-A).Length())-2*LocalRadius);
  Shape.Rotation=FQuat::FindBetweenNormals(FVector::UpVector,(B-A).GetSafeNormal()).Rotator();Body->AggGeom.SphylElems.Add(Shape);
 };
 const FVector Up=FVector::UpVector;
 const FVector Right=(BoneTransform(TEXT("LeftArm")).GetLocation()-BoneTransform(TEXT("RightArm")).GetLocation()).GetSafeNormal();
 Sphere(NewBody(TEXT("Head")),BoneTransform(TEXT("Head")).GetLocation()+Up*17,18.1f);
 Sphere(NewBody(TEXT("Neck")),BoneTransform(TEXT("Neck")).GetLocation(),4.4f);
 USkeletalBodySetup* Chest=NewBody(TEXT("Spine1"));
 for (float Sign:{-1.f,1.f}) Capsule(Chest,Right*4*Sign+Up*106.5f,Right*4*Sign+Up*134.2f,10.4f);
 USkeletalBodySetup* Waist=NewBody(TEXT("Spine"));
 for (float Sign:{-1.f,1.f}) Sphere(Waist,Right*2*Sign+Up*105.25f,8.2f);
 USkeletalBodySetup* Pelvis=NewBody(TEXT("Hips"));
 for (float Sign:{-1.f,1.f}) Sphere(Pelvis,Right*4*Sign+Up*95,8.2f);
 for (const TCHAR* Side:{TEXT("Left"),TEXT("Right")}) {
  const FString S(Side);
  auto Link=[&](const TCHAR* Start,const TCHAR* End,float Radius) {
   FName Bone(*(S+Start));USkeletalBodySetup* Body=NewBody(Bone);
   const FTransform Inverse=BoneTransform(Bone).Inverse();
   FVector A=Inverse.TransformPosition(BoneTransform(Bone).GetLocation());
   FVector B=Inverse.TransformPosition(BoneTransform(FName(*(S+End))).GetLocation());
   FVector Middle=(A+B)*.5;
   for (int32 I=0;I<2;++I) {
    const FVector P=I?Middle:A,Q=I?B:Middle;
    FKTaperedCapsuleElem Shape;Shape.Center=(P+Q)*.5;Shape.Length=(Q-P).Length();
    const float Scale=FMath::Max(.0001f,static_cast<float>(BoneTransform(Bone).GetScale3D().GetAbsMax()));
    Shape.Radius0=(I?Radius:4.4f)/Scale;Shape.Radius1=(I?4.4f:Radius)/Scale;
    Shape.Rotation=FQuat::FindBetweenNormals(FVector::UpVector,(P-Q).GetSafeNormal()).Rotator();
    Body->AggGeom.TaperedCapsuleElems.Add(Shape);
   }
  };
  Link(TEXT("Arm"),TEXT("ForeArm"),5.1f);Link(TEXT("ForeArm"),TEXT("Hand"),5.3f);
  Link(TEXT("Hand"),TEXT("HandMiddle1"),4.4f);
  Link(TEXT("UpLeg"),TEXT("Leg"),7.5f);Link(TEXT("Leg"),TEXT("Foot"),6.5f);
  Link(TEXT("Foot"),TEXT("ToeBase"),4.f);
 }
 for (USkeletalBodySetup* Body:Physics->SkeletalBodySetups) {Body->InvalidatePhysicsData();Body->CreatePhysicsMeshes();}
 Physics->UpdateBodySetupIndexMap();Physics->UpdateBoundsBodiesArray();Physics->MarkPackageDirty();return true;
}

int32 UGolemClothTools::EnsureWeaponCollision(UStaticMesh* Mesh) {
 if (!Mesh) return -1;
 Mesh->Modify();Mesh->CreateBodySetup();UBodySetup* Body=Mesh->GetBodySetup();if (!Body) return -1;
 if (!Body->AggGeom.GetElementCount()) {
  const FStaticMeshRenderData* Data=Mesh->GetRenderData();if (!Data || Data->LODResources.IsEmpty()) return -1;
  FKConvexElem Convex;const auto& Positions=Data->LODResources[0].VertexBuffers.PositionVertexBuffer;
  for (uint32 I=0;I<Positions.GetNumVertices();++I) Convex.VertexData.Add(FVector(Positions.VertexPosition(I)));
  Convex.UpdateElemBox();Body->AggGeom.ConvexElems.Add(MoveTemp(Convex));
 }
 Body->CollisionTraceFlag=CTF_UseSimpleAndComplex;Body->InvalidatePhysicsData();Body->CreatePhysicsMeshes();Mesh->MarkPackageDirty();return Body->AggGeom.GetElementCount();
}

bool UGolemClothTools::FinalizeCapeAnchors(USkeletalMesh* Mesh,float CollisionClearance,float MaximumMovement) {
 if (!Mesh) return false;
 for (UClothingAssetBase* Base:Mesh->GetMeshClothingAssets()) {
  UClothingAssetCommon* Asset=Cast<UClothingAssetCommon>(Base);if (!Asset) continue;
  for (FClothLODDataCommon& Lod:Asset->LodData) {
   const auto& Vertices=Lod.PhysicalMeshData.Vertices;const auto& Indices=Lod.PhysicalMeshData.Indices;
   TArray<int32> Parent;Parent.SetNum(Vertices.Num());for (int32 I=0;I<Parent.Num();++I) Parent[I]=I;
   auto Find=[&](int32 Index) {while (Parent[Index]!=Index) {Parent[Index]=Parent[Parent[Index]];Index=Parent[Index];}return Index;};
   for (int32 I=0;I+2<Indices.Num();I+=3) {Parent[Find(Indices[I])]=Find(Indices[I+1]);Parent[Find(Indices[I+1])]=Find(Indices[I+2]);}
   TMap<int32,FVector2f> Heights;
   for (int32 I=0;I<Vertices.Num();++I) {
    const int32 Root=Find(I);const float Z=Vertices[I].Z;
    if (FVector2f* Span=Heights.Find(Root)) {Span->X=FMath::Min(Span->X,Z);Span->Y=FMath::Max(Span->Y,Z);} else Heights.Add(Root,FVector2f(Z,Z));
   }
   for (FPointWeightMap& Old:Lod.PointWeightMaps) if (Old.CurrentTarget==static_cast<uint8>(EWeightMapTargetCommon::MaxDistance)) Old.bEnabled=false;
   FPointWeightMap Mask(Vertices.Num());Mask.Name=TEXT("Pinned upper edge of every connected garment panel");Mask.CurrentTarget=static_cast<uint8>(EWeightMapTargetCommon::MaxDistance);Mask.bEnabled=true;
   for (int32 I=0;I<Vertices.Num();++I) {
    const FVector2f Span=Heights[Find(I)];const float Height=Span.Y-Span.X;
    const float Pin=Span.Y-Height*.1f;
    Mask.Values[I]=Height<.1f?0.f:FMath::Clamp((Pin-Vertices[I].Z)/FMath::Max(1.f,Height*.25f),0.f,1.f)*FMath::Min(MaximumMovement,Height*.45f);
   }
   Lod.PointWeightMaps.Add(Mask);
  }
  if (UChaosClothConfig* Config=Asset->GetClothConfig<UChaosClothConfig>()) {Config->CollisionThickness=CollisionClearance;Config->SelfCollisionThickness=.5f;Config->bUseCCD=true;Config->bUseSelfCollisions=true;}
  Asset->ApplyParameterMasks(true);Asset->InvalidateAllCachedData();Asset->MarkPackageDirty();
 }
 Mesh->MarkPackageDirty();return true;
}

void UGolemClothTools::ResetCapeCloth(USkeletalMesh* Mesh) {
 if (!Mesh) return;
 FScopedSkeletalMeshPostEditChange Change(Mesh);Mesh->Modify();
 const auto Assets=Mesh->GetMeshClothingAssets();
 for (UClothingAssetBase* Asset:Assets) if (Asset) Asset->UnbindFromSkeletalMesh(Mesh,INDEX_NONE,INDEX_NONE);
 Mesh->SetMeshClothingAssets(TArray<UClothingAssetBase*>());Mesh->MarkPackageDirty();
}
