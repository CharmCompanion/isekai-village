// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DayBoard.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class AIsekaiVillageCharacter;

UCLASS()
class ISEKAIVILLAGE_API ADayBoard : public AActor
{
	GENERATED_BODY()

public:
	ADayBoard();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TObjectPtr<UBoxComponent> InteractBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Village")
	TObjectPtr<UStaticMeshComponent> PostMesh;

	UFUNCTION(BlueprintCallable, Category = "Village")
	bool TryUse(AIsekaiVillageCharacter* Character);

	UFUNCTION()
	void OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
