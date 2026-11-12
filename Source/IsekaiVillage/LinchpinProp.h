// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BuildTypes.h"
#include "LinchpinProp.generated.h"

class UStaticMeshComponent;
class UBoxComponent;
class AIsekaiVillageCharacter;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ALinchpinProp : public AActor
{
	GENERATED_BODY()

public:
	ALinchpinProp();

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Linchpin")
	TObjectPtr<UBoxComponent> Bounds;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Linchpin")
	TObjectPtr<UStaticMeshComponent> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	FName LinchpinTag = TEXT("Anvil");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Linchpin")
	ERoomFunction AssociatedFunction = ERoomFunction::Blacksmith;

	UFUNCTION(BlueprintCallable, Category = "Linchpin")
	void SetupProp(FName InTag);

	UFUNCTION(BlueprintCallable, Category = "Linchpin")
	bool TryInteract(AIsekaiVillageCharacter* Character);

	UFUNCTION(BlueprintPure, Category = "Linchpin")
	FText GetStationHint() const;

	void ApplyTagVisual();

protected:
	virtual void OnConstruction(const FTransform& Transform) override;
};
