// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "FallingTree.generated.h"

class UStaticMeshComponent;
class UStaticMesh;

UCLASS()
class ISEKAIVILLAGE_API AFallingTree : public AActor
{
	GENERATED_BODY()

public:
	AFallingTree();
	virtual void Tick(float DeltaTime) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Gather")
	TObjectPtr<UStaticMeshComponent> Mesh;

	void StartFall(UStaticMesh* InMesh, const FTransform& WorldXform, int32 InWoodAmount);

private:
	float FallTime = 0.0f;
	int32 WoodAmount = 2;
	bool bDropped = false;
	FRotator StartRot;
	FVector FallAxis = FVector::RightVector;
};
