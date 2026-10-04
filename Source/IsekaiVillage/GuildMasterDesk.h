// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "GuildMasterDesk.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class AIsekaiVillageCharacter;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API AGuildMasterDesk : public AActor
{
	GENERATED_BODY()

public:
	AGuildMasterDesk();

protected:
	virtual void BeginPlay() override;

public:

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guild")
	TObjectPtr<UBoxComponent> InteractBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Guild")
	TObjectPtr<UStaticMeshComponent> DeskMesh;

	UFUNCTION(BlueprintCallable, Category = "Guild")
	bool TryHire(AIsekaiVillageCharacter* Character);

	UFUNCTION()
	void OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

	UFUNCTION()
	void OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex);
};
