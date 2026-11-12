// Copyright Epic Games, Inc. All Rights Reserved.

#include "WorldMapTransition.h"
#include "IsekaiVillageTypes.h"
#include "Kismet/GameplayStatics.h"

AWorldMapTransition::AWorldMapTransition()
{
	PrimaryActorTick.bCanEverTick = false;
}

void AWorldMapTransition::TransitionToZone(UObject* WorldContextObject, UWorldZoneData* Zone,
	FName EntryPointOverride, FVector SpawnOffset, FRotator SpawnRotation)
{
	if (!Zone || !WorldContextObject)
	{
		UE_LOG(LogTemp, Error, TEXT("AWorldMapTransition::TransitionToZone — Null Zone or WorldContextObject"));
		return;
	}

	UWorld* World = GEngine->GetWorldFromContextObject(WorldContextObject, EGetWorldErrorMode::LogAndReturnNull);
	if (!World) return;

	// Store transition data in GameInstance
	UGameInstance* GI = UGameplayStatics::GetGameInstance(WorldContextObject);
	UOverworldGameInstance* OGI = Cast<UOverworldGameInstance>(GI);
	if (OGI)
	{
		OGI->PendingEntryPoint = EntryPointOverride != NAME_None ? EntryPointOverride : Zone->EntryPointName;
		OGI->PendingZoneName = Zone->ZoneName;
		OGI->PendingSpawnPosition = SpawnOffset;
		OGI->PendingSpawnRotation = SpawnRotation;
	}

	// Load the destination map
	FString LevelName = Zone->MapToLoad.ToSoftObjectPath().GetAssetName();
	if (LevelName.IsEmpty())
	{
		LevelName = FPackageName::GetShortName(Zone->MapToLoad.GetLongPackageName());
	}

	if (!LevelName.IsEmpty())
	{
		UGameplayStatics::OpenLevel(WorldContextObject, FName(*LevelName));
	}
	else if (!Zone->MapToLoad.IsNull())
	{
		UGameplayStatics::OpenLevelBySoftObjectPtr(WorldContextObject, Zone->MapToLoad);
	}
	else
	{
		UE_LOG(LogTemp, Error, TEXT("AWorldMapTransition::TransitionToZone — Zone has no map set!"));
	}
}

