// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurerGuildBoardActor.h — Interactive guild board for hiring, raising, equipping, and dispatching adventurers

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "AdventurerSystemTypes.h"
#include "AdventurerGuildBoardActor.generated.h"

class UBoxComponent;
class UStaticMeshComponent;
class UAdventurerManagerComponent;
class UIsekaiGuildBoardWidget;

DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnAdventurerBoardInteractedSignature, AActor*, InteractingPlayer);

UCLASS(Blueprintable, BlueprintType, ClassGroup = (AdventurerSystem))
class ISEKAIVILLAGE_API AAdventurerGuildBoardActor : public AActor
{
	GENERATED_BODY()

public:
	AAdventurerGuildBoardActor();

protected:
	virtual void BeginPlay() override;

public:
	// ── Components ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<USceneComponent> SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UBoxComponent> InteractionBox;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UStaticMeshComponent> BoardMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	TObjectPtr<UAdventurerManagerComponent> AdventurerManager;

	// ── UI Integration ──
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Guild Board|UI")
	TSubclassOf<UIsekaiGuildBoardWidget> GuildBoardWidgetClass;

	UPROPERTY(Transient, BlueprintReadOnly, Category = "Guild Board|UI")
	TObjectPtr<UIsekaiGuildBoardWidget> ActiveGuildBoardWidget;

	UFUNCTION(BlueprintCallable, Category = "Guild Board|UI")
	bool OpenGuildBoardUI(APlayerController* PlayerController);

	UFUNCTION(BlueprintCallable, Category = "Guild Board|UI")
	void CloseGuildBoardUI();

	// ── Interaction ──
	UFUNCTION(BlueprintCallable, Category = "Guild Board")
	bool Interact(AActor* Interactor);

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Guild Board")
	FOnAdventurerBoardInteractedSignature OnBoardInteracted;
};
