// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiBuilderAnimInstance.cpp — C++ AnimInstance proxy for Village Builder

#include "IsekaiBuilderAnimInstance.h"
#include "GameFramework/Pawn.h"
#include "Animation/BlendSpace.h"

void FIsekaiBuilderAnimInstanceProxy::InitializeObjects(UAnimInstance* InAnimInstance)
{
	FAnimInstanceProxy::InitializeObjects(InAnimInstance);

	// Wire: Slot sources from Loco (base locomotion blendspace)
	Slot.Source.SetLinkNode(&Loco);
	Slot.SlotName = FName("DefaultSlot");
	Slot.bAlwaysUpdateSourcePose = true;

	// Wire: Tools base pose = Loco (full-body locomotion)
	Tools.BasePose.SetLinkNode(&Loco);

	// Configure blend mode BEFORE AddPose so SyncBlendMasksAndLayers creates the LayerSetup entry
	Tools.BlendMode = ELayeredBoneBlendMode::BranchFilter;
	Tools.bMeshSpaceRotationBlend = true;

	// AddPose() properly handles BlendPoses + BlendWeights(1.0) + SyncBlendMasksAndLayers
	Tools.AddPose();
	Tools.BlendPoses[0].SetLinkNode(&Slot);

	// Configure branch filter: spine_01 depth 0 = entire upper body (arms, head, spine chain)
	FBranchFilter Filter;
	Filter.BoneName = FName("spine_01");
	Filter.BlendDepth = 0;
	Tools.LayerSetup[0].BranchFilters.Add(Filter);
}

UIsekaiBuilderAnimInstance::UIsekaiBuilderAnimInstance()
{
}

void UIsekaiBuilderAnimInstance::NativeInitializeAnimation()
{
	Super::NativeInitializeAnimation();

	if (!LocoBlendSpace)
	{
		LocoBlendSpace = LoadObject<UBlendSpace>(nullptr, TEXT("/Game/IsekaiVillage/Animations/Blendspaces/BS_IdleRun"));
	}

	FIsekaiBuilderAnimInstanceProxy& LocalProxy = GetProxyOnGameThread<FIsekaiBuilderAnimInstanceProxy>();
	if (LocoBlendSpace)
	{
		LocalProxy.SetBlendSpace(LocoBlendSpace);
	}
}

void UIsekaiBuilderAnimInstance::NativeUpdateAnimation(float DeltaTimeX)
{
	Super::NativeUpdateAnimation(DeltaTimeX);

	APawn* OwningPawn = TryGetPawnOwner();
	if (OwningPawn)
	{
		FVector Velocity = OwningPawn->GetVelocity();
		Speed = FVector(Velocity.X, Velocity.Y, 0.0f).Size();

		FIsekaiBuilderAnimInstanceProxy& LocalProxy = GetProxyOnGameThread<FIsekaiBuilderAnimInstanceProxy>();
		LocalProxy.SetSpeed(Speed);
	}
}
