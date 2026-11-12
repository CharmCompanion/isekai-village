// Copyright Epic Games, Inc. All Rights Reserved.
// IsekaiGameplayAnimInstance.h — Universal C++ AnimInstance with smooth BlendSpace locomotion & montage slots

#pragma once

#include "CoreMinimal.h"
#include "Animation/AnimInstance.h"
#include "Animation/AnimInstanceProxy.h"
#include "AnimNodes/AnimNode_BlendSpacePlayer.h"
#include "AnimNodes/AnimNode_Slot.h"
#include "IsekaiGameplayAnimInstance.generated.h"

class UBlendSpace;

USTRUCT()
struct FIsekaiGameplayAnimInstanceProxy : public FAnimInstanceProxy
{
	GENERATED_BODY()

	FIsekaiGameplayAnimInstanceProxy()
	{
		InitNodes();
	}

	FIsekaiGameplayAnimInstanceProxy(UAnimInstance* InAnimInstance)
		: FAnimInstanceProxy(InAnimInstance)
	{
		InitNodes();
	}

	void InitNodes()
	{
		Slot.Source.SetLinkNode(&Loco);
		Slot.SlotName = FName("DefaultSlot");
		Slot.bAlwaysUpdateSourcePose = true;
		Loco.SetLoop(true);
		Loco.SetPlayRate(1.0f);
	}

	virtual FAnimNode_Base* GetCustomRootNode() override { return &Slot; }

	virtual void GetCustomNodes(TArray<FAnimNode_Base*>& OutNodes) override
	{
		OutNodes.Add(&Loco);
		OutNodes.Add(&Slot);
	}

	virtual void Initialize(UAnimInstance* InAnimInstance) override;
	virtual void InitializeObjects(UAnimInstance* InAnimInstance) override;

	void SetBlendSpace(UBlendSpace* InBlendSpace)
	{
		Loco.SetBlendSpace(InBlendSpace);
	}

	void SetSpeed(float InSpeed)
	{
		Speed = InSpeed;
		Loco.SetPosition(FVector(InSpeed, 0.0f, 0.0f));
	}

	UPROPERTY(Transient)
	FAnimNode_BlendSpacePlayer_Standalone Loco;

	UPROPERTY(Transient)
	FAnimNode_Slot Slot;

	float Speed = 0.0f;
};

UCLASS(Transient, Blueprintable)
class ISEKAIVILLAGE_API UIsekaiGameplayAnimInstance : public UAnimInstance
{
	GENERATED_BODY()

public:
	UIsekaiGameplayAnimInstance();

	virtual void NativeInitializeAnimation() override;
	virtual void NativeUpdateAnimation(float DeltaTimeX) override;

	void SetCustomLocoBlendSpace(UBlendSpace* NewBS);
	UBlendSpace* GetLocoBlendSpace() const { return LocoBlendSpace; }

protected:
	virtual FAnimInstanceProxy* CreateAnimInstanceProxy() override
	{
		return new FIsekaiGameplayAnimInstanceProxy(this);
	}

	virtual void DestroyAnimInstanceProxy(FAnimInstanceProxy* InProxy) override
	{
		delete InProxy;
	}

	UPROPERTY(EditAnywhere, BlueprintReadOnly, Category = "Animation")
	TObjectPtr<UBlendSpace> LocoBlendSpace = nullptr;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Animation")
	float Speed = 0.0f;
};
