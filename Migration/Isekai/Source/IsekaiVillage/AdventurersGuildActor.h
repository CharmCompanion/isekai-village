// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurersGuildActor.h — Interactive Guild Hall Desk & Bounty Board

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AdventurersGuildTypes.h"
#include "TownEconomyTypes.h"
#include "AdventurersGuildActor.generated.h"

class USphereComponent;
class UStaticMeshComponent;
class UAdventurersGuildComponent;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnGuildBoardInteracted, APawn*, Interactor, UAdventurersGuildComponent*, GuildComp);

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API AAdventurersGuildActor : public AActor
{
	GENERATED_BODY()

public:
	AAdventurersGuildActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* BoardMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* InteractionTrigger;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild")
	FText GuildBranchName = FText::FromString(TEXT("Eldoria Adventurers Guild"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild")
	EBuildingTier GuildTier = EBuildingTier::Tier_1_Rustic;

	UFUNCTION(BlueprintCallable, Category = "Guild")
	void SetGuildTier(EBuildingTier NewTier);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild")
	TArray<FAdventurerQuest> BoardQuests;

	UPROPERTY(BlueprintAssignable, Category = "Guild|Events")
	FOnGuildBoardInteracted OnGuildBoardInteracted;

	UFUNCTION(BlueprintCallable, Category = "Guild")
	void InteractWithPlayer(APawn* PlayerPawn);

	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	void PopulateDefaultBounties();
};
