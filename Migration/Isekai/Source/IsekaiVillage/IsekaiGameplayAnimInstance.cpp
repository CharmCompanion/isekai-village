// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiGameplayAnimInstance.cpp — Universal C++ AnimInstance with smooth BlendSpace locomotion & montage slots

#include "IsekaiGameplayAnimInstance.h"
#include "GameFramework/Pawn.h"
#include "Animation/BlendSpace.h"

void FIsekaiGameplayAnimInstanceProxy::Initialize(UAnimInstance* InAnimInstance)
{
	InitNodes();

	if (UIsekaiGameplayAnimInstance* GameplayAnimInst = Cast<UIsekaiGameplayAnimInstance>(InAnimInstance))
	{
		if (UBlendSpace* BS = GameplayAnimInst->GetLocoBlendSpace())
		{
			Loco.SetBlendSpace(BS);
		}
	}

	FAnimInstanceProxy::Initialize(InAnimInstance);
}

void FIsekaiGameplayAnimInstanceProxy::InitializeObjects(UAnimInstance* InAnimInstance)
{
	FAnimInstanceProxy::InitializeObjects(InAnimInstance);
	InitNodes();
}

UIsekaiGameplayAnimInstance::UIsekaiGameplayAnimInstance()
{
	LocoBlendSpace = Cast<UBlendSpace>(StaticLoadObject(UBlendSpace::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Blendspaces/BS_IdleRun.BS_IdleRun")));
}

void UIsekaiGameplayAnimInstance::NativeInitializeAnimation()
{
	Super::NativeInitializeAnimation();

	if (!LocoBlendSpace)
	{
		LocoBlendSpace = Cast<UBlendSpace>(StaticLoadObject(UBlendSpace::StaticClass(), nullptr, TEXT("/Game/IsekaiVillage/Animations/Blendspaces/BS_IdleRun.BS_IdleRun")));
	}

	FIsekaiGameplayAnimInstanceProxy& LocalProxy = GetProxyOnGameThread<FIsekaiGameplayAnimInstanceProxy>();
	if (LocoBlendSpace)
	{
		LocalProxy.SetBlendSpace(LocoBlendSpace);
	}
}

void UIsekaiGameplayAnimInstance::SetCustomLocoBlendSpace(UBlendSpace* NewBS)
{
	if (NewBS)
	{
		LocoBlendSpace = NewBS;
		FIsekaiGameplayAnimInstanceProxy& LocalProxy = GetProxyOnGameThread<FIsekaiGameplayAnimInstanceProxy>();
		LocalProxy.SetBlendSpace(NewBS);
	}
}

void UIsekaiGameplayAnimInstance::NativeUpdateAnimation(float DeltaTimeX)
{
	Super::NativeUpdateAnimation(DeltaTimeX);

	APawn* OwningPawn = TryGetPawnOwner();
	if (OwningPawn)
	{
		const FVector Velocity = OwningPawn->GetVelocity();
		Speed = FVector2D(Velocity.X, Velocity.Y).Size();

		FIsekaiGameplayAnimInstanceProxy& LocalProxy = GetProxyOnGameThread<FIsekaiGameplayAnimInstanceProxy>();
		LocalProxy.SetSpeed(Speed);
	}
}
