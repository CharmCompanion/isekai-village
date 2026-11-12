// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "VillageTypes.h"
#include "TownPlot.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class AIsekaiVillageCharacter;

UCLASS()
class ISEKAIVILLAGE_API AArchitectStake : public AActor
{
	GENERATED_BODY()

public:
	AArchitectStake();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Town")
	TObjectPtr<UBoxComponent> InteractBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Town")
	TObjectPtr<UStaticMeshComponent> MarkerMesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FName PlotId = NAME_None;

	UPROPERTY(Transient, VisibleAnywhere, BlueprintReadOnly, Category = "Town")
	TObjectPtr<AActor> BuiltVisual;
	UPROPERTY(VisibleAnywhere, Category = "Town")
	TObjectPtr<class UChildActorComponent> ServiceEntrance;

	void Restyle(const FTownPlot& Plot);
	bool TryUse(AIsekaiVillageCharacter* Character);
	FText PromptLine() const;

	UFUNCTION()
	void OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
