// Copyright Epic Games, Inc. All Rights Reserved.
#include "MineRuntime.h"
#include "BuildPiece.h"
#include "MineOreVein.h"
#include "MineShaft.h"
#include "IslandWarpPortal.h"
#include "Components/SceneComponent.h"
#include "Engine/Engine.h"

AMineRuntime::AMineRuntime()
{
	PrimaryActorTick.bCanEverTick = false;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	RootComponent = Root;
}

void AMineRuntime::BeginPlay()
{
	Super::BeginPlay();
	BuildMine();
}

void AMineRuntime::BuildFloor(int32 FloorIndex, float Z, FName Ore, int32 RequiredLevel, int32 VeinCount)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	const FVector Origin = GetActorLocation() + FVector(0, FloorIndex * 200.0f, Z);
	FActorSpawnParameters P;
	P.Owner = this;

	for (int32 x = -6; x <= 6; ++x)
	{
		for (int32 y = -5; y <= 5; ++y)
		{
			ABuildPiece* Floor = World->SpawnActor<ABuildPiece>(Origin + FVector(x * 200.0f, y * 200.0f, 0), FRotator::ZeroRotator, P);
			if (Floor)
			{
				Floor->PieceType = EBuildPieceType::Floor;
				Floor->RebuildMesh();
			}
		}
	}
	for (int32 i = 0; i < VeinCount; ++i)
	{
		const float Ang = i * 2.4f;
		const FVector Loc = Origin + FVector(FMath::Cos(Ang) * 700.0f, FMath::Sin(Ang) * 520.0f, 40.0f);
		AMineOreVein* Vein = World->SpawnActor<AMineOreVein>(Loc, FRotator::ZeroRotator, P);
		if (Vein)
		{
			Vein->OreId = Ore;
			Vein->RequiredLevel = RequiredLevel;
			Vein->HitsLeft = 3;
		}
	}
}

void AMineRuntime::BuildMine()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}
	BuildFloor(0, 0.0f, TEXT("Copper"), 1, 8);
	BuildFloor(1, -900.0f, TEXT("Iron"), 3, 8);
	BuildFloor(2, -1800.0f, TEXT("Crystal"), 6, 6);

	FActorSpawnParameters P;
	P.Owner = this;
	const FVector Base = GetActorLocation();

	if (AMineShaft* Down = World->SpawnActor<AMineShaft>(Base + FVector(0, 700, 40), FRotator::ZeroRotator, P))
	{
		Down->Destination = Base + FVector(0, 900, -860);
		Down->RequiredLevel = 3;
		Down->Label = TEXT("Iron shaft");
	}
	if (AMineShaft* Up1 = World->SpawnActor<AMineShaft>(Base + FVector(0, 1100, -860), FRotator::ZeroRotator, P))
	{
		Up1->Destination = Base + FVector(0, 500, 80);
		Up1->RequiredLevel = 1;
		Up1->Label = TEXT("Back to copper");
	}
	if (AMineShaft* Deep = World->SpawnActor<AMineShaft>(Base + FVector(0, 700, -860), FRotator::ZeroRotator, P))
	{
		Deep->Destination = Base + FVector(0, 900, -1760);
		Deep->RequiredLevel = 6;
		Deep->Label = TEXT("Crystal shaft");
	}
	if (AMineShaft* Up2 = World->SpawnActor<AMineShaft>(Base + FVector(0, 1100, -1760), FRotator::ZeroRotator, P))
	{
		Up2->Destination = Base + FVector(0, 500, -820);
		Up2->RequiredLevel = 3;
		Up2->Label = TEXT("Back to iron");
	}

	if (AIslandWarpPortal* Exit = World->SpawnActor<AIslandWarpPortal>(Base + FVector(0, -700, 40), FRotator::ZeroRotator, P))
	{
		Exit->DestinationLevel = ReturnLevel;
		Exit->ArrivalPlayerStartTag = ReturnStartTag;
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 4.0f, FColor::Silver, TEXT("El Ruhn Mine — copper, iron, crystal floors"));
	}
}
