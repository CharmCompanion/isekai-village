// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "DungeonGraphData.h"
#include "DungeonRuntime.generated.h"

class UDungeonGraphData;
class USceneComponent;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ADungeonRuntime : public AActor
{
	GENERATED_BODY()

public:
	ADungeonRuntime();

	virtual void BeginPlay() override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Dungeon")
	TObjectPtr<USceneComponent> Root;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	TObjectPtr<UDungeonGraphData> Graph;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName ReturnLevel = TEXT("/Game/IsekaiVillage/AdventureWorld/Maps/Map_ElRuhnSky");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Dungeon")
	FName ReturnStartTag = TEXT("DungeonReturn");

	UFUNCTION(BlueprintCallable, Category = "Dungeon")
	void BuildFromGraph();

private:
	const FDungeonRoom* FindRoom(FName Id) const;
	void SpawnRoomShell(const FDungeonRoom& Room);
	void SpawnHall(const FDungeonHall& Hall);
	void SpawnMarker(const FDungeonMarker& Marker);
};
