// Copyright Epic Games, Inc. All Rights Reserved.
// AdventurersGuildActor.cpp — Interactive Guild Hall Desk & Bounty Board

#include "AdventurersGuildActor.h"
#include "AdventurersGuildComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "UObject/ConstructorHelpers.h"
#include "Engine/StaticMesh.h"

AAdventurersGuildActor::AAdventurersGuildActor()
{
	PrimaryActorTick.bCanEverTick = false;

	SceneRoot = CreateDefaultSubobject<USceneComponent>(TEXT("SceneRoot"));
	RootComponent = SceneRoot;

	BoardMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("BoardMesh"));
	BoardMesh->SetupAttachment(SceneRoot);
	BoardMesh->SetCollisionProfileName(TEXT("BlockAll"));

	static ConstructorHelpers::FObjectFinder<UStaticMesh> CubeMesh(TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (CubeMesh.Succeeded())
	{
		BoardMesh->SetStaticMesh(CubeMesh.Object);
		BoardMesh->SetRelativeScale3D(FVector(0.2f, 1.8f, 1.4f));
		BoardMesh->SetRelativeLocation(FVector(0.0f, 0.0f, 70.0f));
	}

	InteractionTrigger = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionTrigger"));
	InteractionTrigger->SetupAttachment(SceneRoot);
	InteractionTrigger->SetSphereRadius(250.0f);
	InteractionTrigger->SetCollisionProfileName(TEXT("Trigger"));
	InteractionTrigger->SetGenerateOverlapEvents(true);

	InteractionTrigger->OnComponentBeginOverlap.AddDynamic(this, &AAdventurersGuildActor::OnOverlapBegin);
}

void AAdventurersGuildActor::BeginPlay()
{
	Super::BeginPlay();

	if (BoardQuests.Num() == 0)
	{
		PopulateDefaultBounties();
	}
}

void AAdventurersGuildActor::PopulateDefaultBounties()
{
	// Bounty 1: Lesser Imps
	{
		FAdventurerQuest Q;
		Q.QuestID = TEXT("Bounty_Imp_01");
		Q.Title = FText::FromString(TEXT("Lesser Imp Extermination"));
		Q.Description = FText::FromString(TEXT("Rogue Lesser Imps have emerged near the outskirts. Cull 3 of them."));
		Q.Category = EQuestCategory::DemonSubjugation;
		Q.RequiredRank = EGuildRank::Copper;
		Q.TargetID = TEXT("LesserImp");
		Q.RequiredCount = 3;
		Q.RewardGald = 300;
		Q.RewardExp = 180;
		Q.RewardSP = 30;
		Q.RewardReputation = 75;
		BoardQuests.Add(Q);
	}

	// Bounty 2: Demon Brute
	{
		FAdventurerQuest Q;
		Q.QuestID = TEXT("Bounty_Brute_01");
		Q.Title = FText::FromString(TEXT("Demon Brute Suppression"));
		Q.Description = FText::FromString(TEXT("An armored Demon Brute was sighted near the valley pass. Eliminate it."));
		Q.Category = EQuestCategory::DemonSubjugation;
		Q.RequiredRank = EGuildRank::Iron;
		Q.TargetID = TEXT("DemonBrute");
		Q.RequiredCount = 1;
		Q.RewardGald = 750;
		Q.RewardExp = 450;
		Q.RewardSP = 60;
		Q.RewardReputation = 150;
		BoardQuests.Add(Q);
	}

	// Bounty 3: Gathering
	{
		FAdventurerQuest Q;
		Q.QuestID = TEXT("Gather_Herb_01");
		Q.Title = FText::FromString(TEXT("Apothecary Supply Run"));
		Q.Description = FText::FromString(TEXT("Collect 5 Moonlit Herbs for potion compounding at the guild hospital."));
		Q.Category = EQuestCategory::ResourceGathering;
		Q.RequiredRank = EGuildRank::Copper;
		Q.TargetID = TEXT("MoonlitHerb");
		Q.RequiredCount = 5;
		Q.RewardGald = 250;
		Q.RewardExp = 120;
		Q.RewardSP = 20;
		Q.RewardReputation = 50;
		BoardQuests.Add(Q);
	}

	// Bounty 4: Hellhounds
	{
		FAdventurerQuest Q;
		Q.QuestID = TEXT("Bounty_Hound_01");
		Q.Title = FText::FromString(TEXT("Fiery Hellhound Pack"));
		Q.Description = FText::FromString(TEXT("Subdue 2 Hellhounds terrorizing merchant caravans in the wasteland."));
		Q.Category = EQuestCategory::DemonSubjugation;
		Q.RequiredRank = EGuildRank::Bronze;
		Q.TargetID = TEXT("Hellhound");
		Q.RequiredCount = 2;
		Q.RewardGald = 900;
		Q.RewardExp = 550;
		Q.RewardSP = 75;
		Q.RewardReputation = 200;
		BoardQuests.Add(Q);
	}
}

void AAdventurersGuildActor::SetGuildTier(EBuildingTier NewTier)
{
	GuildTier = NewTier;
	BoardQuests.Empty();
	PopulateDefaultBounties();
}

void AAdventurersGuildActor::InteractWithPlayer(APawn* PlayerPawn)
{
	if (!PlayerPawn) return;

	UAdventurersGuildComponent* GuildComp = PlayerPawn->FindComponentByClass<UAdventurersGuildComponent>();
	OnGuildBoardInteracted.Broadcast(PlayerPawn, GuildComp);
}

void AAdventurersGuildActor::OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
	UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (APawn* Pawn = Cast<APawn>(OtherActor))
	{
		InteractWithPlayer(Pawn);
	}
}
