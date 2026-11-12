// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiBuilderAnimInstance.h — C++ AnimInstance proxy for Village Builder

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimInstanceProxy.h"
#include "AnimNodes/AnimNode_BlendSpacePlayer.h"
#include "AnimNodes/AnimNode_Slot.h"
#include "AnimNodes/AnimNode_LayeredBoneBlend.h"
#include "IsekaiBuilderAnimInstance.generated.h"

USTRUCT()
struct FIsekaiBuilderAnimInstanceProxy : public FAnimInstanceProxy
{
	GENERATED_BODY()

	FIsekaiBuilderAnimInstanceProxy() = default;
	FIsekaiBuilderAnimInstanceProxy(UAnimInstance* InAnimInstance)
		: FAnimInstanceProxy(InAnimInstance)
	{
	}

	// Root node tells the proxy system to drive Initialize/CacheBones/Update/Evaluate
	// through the linked node graph automatically (Tools -> Slot -> Loco, Tools -> Loco)
	virtual FAnimNode_Base* GetCustomRootNode() override { return &Tools; }

	virtual void InitializeObjects(UAnimInstance* InAnimInstance) override;

	void SetBlendSpace(UBlendSpace* InBlendSpace)
	{
		Loco.SetBlendSpace(InBlendSpace);
	}

	void SetSpeed(float InSpeed)
	{
		Speed = InSpeed;
		// Set blendspace position so Loco samples correctly on next graph update
		Loco.SetPosition(FVector(InSpeed, 0.0f, 0.0f));
	}

	UPROPERTY(Transient)
	FAnimNode_BlendSpacePlayer_Standalone Loco;

	UPROPERTY(Transient)
	FAnimNode_Slot Slot;

	UPROPERTY(Transient)
	FAnimNode_LayeredBoneBlend Tools;

	float Speed = 0.0f;
};

UCLASS(Transient, Blueprintable)
class ISEKAIVILLAGE_API UIsekaiBuilderAnimInstance : public UAnimInstance
{
	GENERATED_BODY()

public:
	UIsekaiBuilderAnimInstance();

	virtual void NativeInitializeAnimation() override;
	virtual void NativeUpdateAnimation(float DeltaTimeX) override;

protected:
	virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override
	{
		return new FIsekaiBuilderAnimInstanceProxy(this);
	}

	virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy) override
	{
		delete InProxy;
	}

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation")
	UBlendSpace* LocoBlendSpace = nullptr;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
	float Speed = 0.0f;
};
