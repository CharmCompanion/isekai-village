// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BuildTypes.h"
#include "DebrisActor.generated.h"

class UStaticMeshComponent;
class AIsekaiVillageCharacter;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ADebrisActor : public AActor
{
	GENERATED_BODY()

public:
	ADebrisActor();

	virtual void OnConstruction(const FTransform& Transform) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Debris")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Debris")
	EDebrisType DebrisType = EDebrisType::StoneRubble;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Debris")
	int32 HitsRemaining = 3;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Debris")
	int32 YieldAmount = 4;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Debris")
	FName CustomDropId = NAME_None;

	UFUNCTION(BlueprintCallable, Category = "Debris")
	void SetupDebris(EDebrisType InType);

	UFUNCTION(BlueprintCallable, Category = "Debris")
	bool TrySalvage(AIsekaiVillageCharacter* Character);

	UFUNCTION(BlueprintPure, Category = "Debris")
	FName GetPrimaryLootId() const;

	UFUNCTION(BlueprintPure, Category = "Debris")
	FText GetDebrisDisplayName() const;
};
