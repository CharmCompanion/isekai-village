// Copyright Epic Games, Inc. All Rights Reserved.
// WonderChefActor.cpp — Quirky Disguised Prop that Reveals Recipes (Tales Signature Hallmark)

#include "WonderChefActor.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SphereComponent.h"

AWonderChefActor::AWonderChefActor()
{
	PrimaryActorTick.bCanEverTick = false;

	DisguiseMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("DisguiseMesh"));
	RootComponent = DisguiseMesh;
	DisguiseMesh->SetCollisionProfileName(TEXT("BlockAll"));

	InteractionSphere = CreateDefaultSubobject<USphereComponent>(TEXT("InteractionSphere"));
	InteractionSphere->SetupAttachment(RootComponent);
	InteractionSphere->InitSphereRadius(160.0f);
	InteractionSphere->SetCollisionProfileName(TEXT("OverlapAllDynamic"));
}

bool AWonderChefActor::DiscoverChef()
{
	if (bHasBeenDiscovered) return false;

	bHasBeenDiscovered = true;

	OnWonderChefDiscovered.Broadcast(RewardRecipe, DiscoveryDialogue);

	// Disappear after rewarding the recipe in classic Wonder Chef fashion
	SetLifeSpan(3.5f);

	return true;
}
