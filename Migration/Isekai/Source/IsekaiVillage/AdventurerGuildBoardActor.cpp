// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurerGuildBoardActor.cpp — Implementation of interactive guild board actor

#include "AdventurerGuildBoardActor.h"
#include "AdventurerManagerComponent.h"
#include "IsekaiMenuWidgets.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "GameFramework/PlayerController.h"
#include "GameFramework/Pawn.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"

AAdventurerGuildBoardActor::AAdventurerGuildBoardActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	SetRootComponent(SceneRoot);

	InteractionBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractionBox"));
	InteractionBox->SetupAttachment(SceneRoot);
	InteractionBox->SetBoxExtent(FVector(120.0f, 120.0f, 80.0f));
	InteractionBox->SetCollisionProfileName(TEXT("Trigger"));

	BoardMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BoardMesh"));
	BoardMesh->SetupAttachment(SceneRoot);
	BoardMesh->SetCollisionProfileName(TEXT("BlockAll"));

	// Try loading Fantastic Village Pack wooden notice board mesh
	static ConstructorHelpers::FObjectFinder<UStaticMesh> VillageBoardMesh(TEXT("/Game/Fantastic_Village_Pack/meshes/props/deco/SM_PROP_board_01.SM_PROP_board_01"));
	if (VillageBoardMesh.Succeeded())
	{
		BoardMesh->SetStaticMesh(VillageBoardMesh.Object);
		BoardMesh->SetRelativeScale3D(FVector(1.0f, 1.0f, 1.0f));
	}
	else
	{
		// Fallback placeholder shape
		static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
		if (CubeMesh.Succeeded())
		{
			BoardMesh->SetStaticMesh(CubeMesh.Object);
			BoardMesh->SetRelativeScale3D(FVector(0.4f, 1.6f, 1.2f));
			BoardMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 60.0f));
		}
	}

	AdventurerManager = CreateDefaultSubobject<UAdventurerManagerComponent>(TEXT("AdventurerManager"));
}

void AAdventurerGuildBoardActor::BeginPlay()
{
	Super::BeginPlay();
}

bool AAdventurerGuildBoardActor::Interact(AActor* Interactor)
{
	if (!Interactor) return false;

	OnBoardInteracted.Broadcast(Interactor);

	if (APawn* Pawn = Cast<APawn>(Interactor))
	{
		if (APlayerController* PC = Cast<APlayerController>(Pawn->GetController()))
		{
			OpenGuildBoardUI(PC);
		}
	}

	return true;
}

bool AAdventurerGuildBoardActor::OpenGuildBoardUI(APlayerController* PlayerController)
{
	if (!PlayerController) return false;

	if (ActiveGuildBoardWidget)
	{
		CloseGuildBoardUI();
	}

	UClass* ClassToSpawn = GuildBoardWidgetClass ? GuildBoardWidgetClass.Get() : UIsekaiGuildBoardWidget::StaticClass();
	ActiveGuildBoardWidget = CreateWidget<UIsekaiGuildBoardWidget>(PlayerController, ClassToSpawn);
	if (ActiveGuildBoardWidget)
	{
		ActiveGuildBoardWidget->InitializeGuildBoard(AdventurerManager);
		ActiveGuildBoardWidget->AddToViewport(10);

		PlayerController->SetShowMouseCursor(true);
		FInputModeGameAndUI InputMode;
		InputMode.SetWidgetToFocus(ActiveGuildBoardWidget->TakeWidget());
		InputMode.SetLockMouseToViewportBehavior(EMouseLockMode::DoNotLock);
		PlayerController->SetInputMode(InputMode);
		return true;
	}

	return false;
}

void AAdventurerGuildBoardActor::CloseGuildBoardUI()
{
	if (ActiveGuildBoardWidget)
	{
		ActiveGuildBoardWidget->RemoveFromParent();
		ActiveGuildBoardWidget = nullptr;

		if (UWorld* World = GetWorld())
		{
			if (APlayerController* PC = World->GetFirstPlayerController())
			{
				PC->SetShowMouseCursor(false);
				PC->SetInputMode(FInputModeGameOnly());
			}
		}
	}
}
