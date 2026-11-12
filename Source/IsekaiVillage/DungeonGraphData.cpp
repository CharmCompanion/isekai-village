// Copyright Epic Games, Inc. All Rights Reserved.
#include "DungeonGraphData.h"

static FDungeonRoom MakeRoom(const TCHAR* Id, const FVector& Center, const FVector2D& Size, ERoomFunction Function)
{
	FDungeonRoom Room;
	Room.RoomId = Id;
	Room.Center = Center;
	Room.Size = Size;
	Room.Function = Function;
	return Room;
}

static FDungeonHall MakeHall(const TCHAR* From, const TCHAR* To)
{
	FDungeonHall Hall;
	Hall.FromRoom = From;
	Hall.ToRoom = To;
	Hall.Width = 280.0f;
	return Hall;
}

static FDungeonMarker MakeMarker(EDungeonMarkerType Type, const TCHAR* Room, const FVector& Offset)
{
	FDungeonMarker Marker;
	Marker.Type = Type;
	Marker.RoomId = Room;
	Marker.LocalOffset = Offset;
	return Marker;
}

UDungeonGraphData* UDungeonGraphData::CreateElRuhnStarter()
{
	UDungeonGraphData* Graph = NewObject<UDungeonGraphData>(GetTransientPackage(), TEXT("ElRuhnSealedCave"));
	Graph->GraphId = TEXT("ElRuhnSealedCave");
	Graph->DisplayName = FText::FromString(TEXT("El Ruhn Sealed Cave"));
	Graph->Rooms = {
		MakeRoom(TEXT("Entrance"), FVector(0, 0, 0), FVector2D(900, 900), ERoomFunction::EmptyHall),
		MakeRoom(TEXT("Fork"), FVector(0, 1600, 0), FVector2D(700, 700), ERoomFunction::EmptyHall),
		MakeRoom(TEXT("Cache"), FVector(-1100, 2400, 0), FVector2D(800, 800), ERoomFunction::Treasure),
		MakeRoom(TEXT("Den"), FVector(1100, 2400, 0), FVector2D(800, 800), ERoomFunction::MonsterDen),
		MakeRoom(TEXT("Boss"), FVector(0, 3600, 0), FVector2D(1200, 1200), ERoomFunction::BossLair)
	};
	Graph->Halls = {
		MakeHall(TEXT("Entrance"), TEXT("Fork")),
		MakeHall(TEXT("Fork"), TEXT("Cache")),
		MakeHall(TEXT("Fork"), TEXT("Den")),
		MakeHall(TEXT("Cache"), TEXT("Boss")),
		MakeHall(TEXT("Den"), TEXT("Boss"))
	};
	Graph->Markers = {
		MakeMarker(EDungeonMarkerType::Entrance, TEXT("Entrance"), FVector(0, -300, 40)),
		MakeMarker(EDungeonMarkerType::Exit, TEXT("Entrance"), FVector(0, -360, 40)),
		MakeMarker(EDungeonMarkerType::Trap, TEXT("Fork"), FVector(0, 0, 20)),
		MakeMarker(EDungeonMarkerType::Treasure, TEXT("Cache"), FVector(0, 0, 20)),
		MakeMarker(EDungeonMarkerType::MonsterSpawn, TEXT("Den"), FVector(-120, 80, 20)),
		MakeMarker(EDungeonMarkerType::MonsterSpawn, TEXT("Den"), FVector(140, -60, 20)),
		MakeMarker(EDungeonMarkerType::Boss, TEXT("Boss"), FVector(0, 80, 20)),
		MakeMarker(EDungeonMarkerType::Vault, TEXT("Boss"), FVector(0, 320, 20))
	};
	return Graph;
}
