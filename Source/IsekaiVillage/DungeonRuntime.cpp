// Copyright Epic Games, Inc. All Rights Reserved.
#include "DungeonRuntime.h"
#include "DungeonGraphData.h"
#include "BuildPiece.h"
#include "LinchpinProp.h"
#include "IslandWarpPortal.h"
#include "Engine/Engine.h"

ADungeonRuntime::ADungeonRuntime()
{
	PrimaryActorTick.bCanEverTick = false;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	RootComponent = Root;
}

void ADungeonRuntime::BeginPlay()
{
	Super::BeginPlay();
	if (!Graph)
	{
		Graph = UDungeonGraphData::CreateElRuhnStarter();
	}
	BuildFromGraph();
}

const FDungeonRoom* ADungeonRuntime::FindRoom(FName Id) const
{
	if (!Graph)
	{
		return nullptr;
	}
	for (const FDungeonRoom& Room : Graph->Rooms)
	{
		if (Room.RoomId == Id)
		{
			return &Room;
		}
	}
	return nullptr;
}

void ADungeonRuntime::SpawnRoomShell(const FDungeonRoom& Room)
{
	const FVector Origin = GetActorLocation() + Room.Center;
	const int32 NX = FMath::Max(1, FMath::RoundToInt(Room.Size.X / 200.0f));
	const int32 NY = FMath::Max(1, FMath::RoundToInt(Room.Size.Y / 200.0f));
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	for (int32 x = 0; x < NX; ++x)
	{
		for (int32 y = 0; y < NY; ++y)
		{
			const FVector Loc = Origin + FVector((x - NX * 0.5f + 0.5f) * 200.0f, (y - NY * 0.5f + 0.5f) * 200.0f, 0.0f);
			FActorSpawnParameters P;
			P.Owner = this;
			ABuildPiece* Floor = World->SpawnActor<ABuildPiece>(Loc, FRotator::ZeroRotator, P);
			if (Floor)
			{
				Floor->PieceType = EBuildPieceType::Floor;
				Floor->Occupancy = EBuildOccupancy::Full;
				Floor->RebuildMesh();
			}
		}
	}

	auto WallAt = [&](const FVector& Loc, float Yaw)
	{
		FActorSpawnParameters P;
		P.Owner = this;
		ABuildPiece* Wall = World->SpawnActor<ABuildPiece>(Loc, FRotator(0, Yaw, 0), P);
		if (Wall)
		{
			Wall->PieceType = EBuildPieceType::Wall;
			Wall->Occupancy = EBuildOccupancy::Full;
			Wall->RebuildMesh();
		}
	};

	const float HalfX = Room.Size.X * 0.5f;
	const float HalfY = Room.Size.Y * 0.5f;
	for (int32 x = 0; x < NX; ++x)
	{
		const float X = (x - NX * 0.5f + 0.5f) * 200.0f;
		WallAt(Origin + FVector(X, -HalfY, 0), 0);
		WallAt(Origin + FVector(X, HalfY, 0), 180);
	}
	for (int32 y = 0; y < NY; ++y)
	{
		const float Y = (y - NY * 0.5f + 0.5f) * 200.0f;
		WallAt(Origin + FVector(-HalfX, Y, 0), 90);
		WallAt(Origin + FVector(HalfX, Y, 0), -90);
	}
}

void ADungeonRuntime::SpawnHall(const FDungeonHall& Hall)
{
	const FDungeonRoom* A = FindRoom(Hall.FromRoom);
	const FDungeonRoom* B = FindRoom(Hall.ToRoom);
	UWorld* World = GetWorld();
	if (!A || !B || !World)
	{
		return;
	}
	const FVector Start = GetActorLocation() + A->Center;
	const FVector End = GetActorLocation() + B->Center;
	const FVector Delta = End - Start;
	const float Len = Delta.Size2D();
	const int32 Steps = FMath::Max(1, FMath::RoundToInt(Len / 200.0f));
	const FRotator Yaw = Delta.Rotation();
	for (int32 i = 1; i < Steps; ++i)
	{
		const FVector Loc = FMath::Lerp(Start, End, i / static_cast<float>(Steps));
		FActorSpawnParameters P;
		P.Owner = this;
		ABuildPiece* Floor = World->SpawnActor<ABuildPiece>(Loc, Yaw, P);
		if (Floor)
		{
			Floor->PieceType = EBuildPieceType::Floor;
			Floor->Occupancy = EBuildOccupancy::Half;
			Floor->RebuildMesh();
		}
	}
}

void ADungeonRuntime::SpawnMarker(const FDungeonMarker& Marker)
{
	const FDungeonRoom* Room = FindRoom(Marker.RoomId);
	UWorld* World = GetWorld();
	if (!Room || !World)
	{
		return;
	}
	const FVector Loc = GetActorLocation() + Room->Center + Marker.LocalOffset;
	FActorSpawnParameters P;
	P.Owner = this;

	if (Marker.Type == EDungeonMarkerType::Exit || Marker.Type == EDungeonMarkerType::Entrance)
	{
		AIslandWarpPortal* Portal = World->SpawnActor<AIslandWarpPortal>(Loc, FRotator::ZeroRotator, P);
		if (Portal)
		{
			Portal->DestinationLevel = ReturnLevel;
			Portal->ArrivalPlayerStartTag = ReturnStartTag;
		}
		return;
	}

	ALinchpinProp* Prop = World->SpawnActor<ALinchpinProp>(Loc, FRotator::ZeroRotator, P);
	if (!Prop)
	{
		return;
	}
	switch (Marker.Type)
	{
	case EDungeonMarkerType::Trap: Prop->LinchpinTag = TEXT("Trap"); break;
	case EDungeonMarkerType::MonsterSpawn: Prop->LinchpinTag = TEXT("Spawner"); break;
	case EDungeonMarkerType::Treasure: Prop->LinchpinTag = TEXT("Chest"); break;
	case EDungeonMarkerType::Boss: Prop->LinchpinTag = TEXT("Boss"); break;
	case EDungeonMarkerType::Vault: Prop->LinchpinTag = TEXT("Vault"); break;
	default: Prop->LinchpinTag = TEXT("Crate"); break;
	}
	Prop->ApplyTagVisual();
}

void ADungeonRuntime::BuildFromGraph()
{
	if (!Graph)
	{
		return;
	}
	for (const FDungeonRoom& Room : Graph->Rooms)
	{
		SpawnRoomShell(Room);
	}
	for (const FDungeonHall& Hall : Graph->Halls)
	{
		SpawnHall(Hall);
	}
	for (const FDungeonMarker& Marker : Graph->Markers)
	{
		SpawnMarker(Marker);
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 4.0f, FColor::Cyan, FString::Printf(TEXT("Dungeon: %s"), *Graph->DisplayName.ToString()));
	}
}
