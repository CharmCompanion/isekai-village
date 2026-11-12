// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BlacksmithForge.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class AIsekaiVillageCharacter;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ABlacksmithForge : public AActor
{
	GENERATED_BODY()

public:
	ABlacksmithForge();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blacksmith")
	TObjectPtr<UBoxComponent> InteractBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blacksmith")
	TObjectPtr<UStaticMeshComponent> AnvilMesh;

	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	bool TryForge(AIsekaiVillageCharacter* Character);
	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	bool TryForgeAdventurerGear(AIsekaiVillageCharacter* Character);
	UFUNCTION(BlueprintCallable, Category = "Blacksmith")
	bool TemperWithToolParts(AIsekaiVillageCharacter* Character, FName AdventurerId = NAME_None);
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Blacksmith")
	FString LastForgeMessage;
	UFUNCTION(BlueprintPure, Category = "Blacksmith")
	FString ForgeStatusLine(AIsekaiVillageCharacter* Character) const;

	UFUNCTION()
	void OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
