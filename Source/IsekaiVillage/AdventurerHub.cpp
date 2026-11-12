// Copyright Epic Games, Inc. All Rights Reserved.
#include "AdventurerHub.h"
#include "IslandWarpPortal.h"
#include "GuildMasterDesk.h"
#include "RoomVolume.h"
#include "LinchpinProp.h"
#include "BuildPiece.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Components/StaticMeshComponent.h"
#include "Components/SceneComponent.h"
#include "Components/BoxComponent.h"
AAdventurerHub::AAdventurerHub()
{
	PrimaryActorTick.bCanEverTick = false;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	RootComponent = Root;
}

void AAdventurerHub::BeginPlay()
{
	Super::BeginPlay();
	BuildHub();
}

AActor* AAdventurerHub::SpawnBox(const FVector& Local, const FRotator& Rot, const FVector& Scale, const FLinearColor& Color)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}
	FActorSpawnParameters P;
	P.Owner = this;
	AStaticMeshActor* Box = World->SpawnActor<AStaticMeshActor>(GetActorLocation() + Local, Rot, P);
	if (!Box)
	{
		return nullptr;
	}
	UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	if (UStaticMeshComponent* Mesh = Box->GetStaticMeshComponent())
	{
		Mesh->SetMobility(EComponentMobility::Movable);
		if (Cube)
		{
			Mesh->SetStaticMesh(Cube);
		}
		Mesh->SetWorldScale3D(Scale);
		if (UMaterialInterface* Base = Mesh->GetMaterial(0))
		{
			if (UMaterialInstanceDynamic* Dyn = UMaterialInstanceDynamic::Create(Base, Box))
			{
				Dyn->SetVectorParameterValue(TEXT("Color"), Color);
				Mesh->SetMaterial(0, Dyn);
			}
		}
	}
	Box->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
	return Box;
}

ALinchpinProp* AAdventurerHub::SpawnProp(const FVector& Local, FName Tag)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}
	FActorSpawnParameters P;
	P.Owner = this;
	ALinchpinProp* Prop = World->SpawnActor<ALinchpinProp>(GetActorLocation() + Local, FRotator::ZeroRotator, P);
	if (Prop)
	{
		Prop->LinchpinTag = Tag;
		Prop->ApplyTagVisual();
		Prop->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
	}
	return Prop;
}

ARoomVolume* AAdventurerHub::SpawnRoom(const FVector& Local, const FVector& Extent)
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return nullptr;
	}
	FActorSpawnParameters P;
	P.Owner = this;
	ARoomVolume* Room = World->SpawnActor<ARoomVolume>(GetActorLocation() + Local, FRotator::ZeroRotator, P);
	if (Room && Room->Bounds)
	{
		Room->Bounds->SetBoxExtent(Extent);
		Room->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
	}
	return Room;
}

void AAdventurerHub::BuildHub()
{
	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	const FLinearColor Stone(0.18f, 0.16f, 0.22f);
	const FLinearColor Gold(0.85f, 0.62f, 0.18f);
	const FLinearColor Teal(0.12f, 0.55f, 0.62f);
	const FLinearColor Banner(0.72f, 0.12f, 0.28f);
	const FLinearColor Wood(0.32f, 0.20f, 0.10f);
	const FLinearColor Roof(0.10f, 0.42f, 0.48f);

	// Plaza floor + magic ring
	SpawnBox(FVector(0, 0, -20), FRotator::ZeroRotator, FVector(28, 22, 0.4f), Stone);
	SpawnBox(FVector(0, 280, -8), FRotator::ZeroRotator, FVector(8, 8, 0.16f), Teal);
	SpawnBox(FVector(0, 280, -4), FRotator::ZeroRotator, FVector(5.2f, 5.2f, 0.08f), Gold);

	// Grand stair toward the mountain mouth (+Y)
	for (int32 i = 0; i < 8; ++i)
	{
		SpawnBox(FVector(0, 700.0f + i * 70.0f, i * 18.0f), FRotator::ZeroRotator, FVector(10.0f - i * 0.25f, 0.8f, 0.22f), Stone);
	}

	// Arch
	SpawnBox(FVector(-220, 1280, 280), FRotator::ZeroRotator, FVector(1.2f, 1.2f, 6.0f), Stone);
	SpawnBox(FVector(220, 1280, 280), FRotator::ZeroRotator, FVector(1.2f, 1.2f, 6.0f), Stone);
	SpawnBox(FVector(0, 1280, 560), FRotator::ZeroRotator, FVector(5.6f, 1.4f, 1.1f), Gold);

	// Lanterns + banners
	SpawnBox(FVector(-320, 180, 160), FRotator::ZeroRotator, FVector(0.3f, 0.3f, 3.4f), Stone);
	SpawnBox(FVector(320, 180, 160), FRotator::ZeroRotator, FVector(0.3f, 0.3f, 3.4f), Stone);
	SpawnBox(FVector(-320, 180, 340), FRotator::ZeroRotator, FVector(0.7f, 0.7f, 0.5f), Gold);
	SpawnBox(FVector(320, 180, 340), FRotator::ZeroRotator, FVector(0.7f, 0.7f, 0.5f), Gold);
	SpawnBox(FVector(-180, 1280, 420), FRotator::ZeroRotator, FVector(0.12f, 1.4f, 2.4f), Banner);
	SpawnBox(FVector(180, 1280, 420), FRotator::ZeroRotator, FVector(0.12f, 1.4f, 2.4f), Banner);

	FActorSpawnParameters P;
	P.Owner = this;
	AIslandWarpPortal* Portal = World->SpawnActor<AIslandWarpPortal>(GetActorLocation() + FVector(0, 1280, 40), FRotator::ZeroRotator, P);
	if (Portal)
	{
		Portal->DestinationLevel = DungeonLevel;
		Portal->ArrivalPlayerStartTag = DungeonStartTag;
		Portal->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
	}

	auto Building = [&](const FVector& Center, const FLinearColor& Accent)
	{
		SpawnBox(Center + FVector(0, 0, 160), FRotator::ZeroRotator, FVector(6.5f, 5.2f, 3.2f), Wood);
		SpawnBox(Center + FVector(0, 0, 340), FRotator::ZeroRotator, FVector(7.2f, 5.8f, 0.6f), Roof);
		SpawnBox(Center + FVector(0, -270, 140), FRotator::ZeroRotator, FVector(1.6f, 0.2f, 2.2f), Accent);
	};

	Building(FVector(-900, -120, 0), Gold);
	Building(FVector(900, -120, 0), Teal);
	Building(FVector(-900, -900, 0), Banner);
	Building(FVector(900, -900, 0), FLinearColor(0.55f, 0.22f, 0.08f));

	if (!bPlayableInteriors)
	{
		return;
	}

	if (AGuildMasterDesk* Desk = World->SpawnActor<AGuildMasterDesk>(GetActorLocation() + FVector(-900, -80, 40), FRotator::ZeroRotator, P))
	{
		Desk->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
	}
	SpawnProp(FVector(-900, -160, 40), TEXT("Board"));
	SpawnRoom(FVector(-900, -120, 160), FVector(340, 280, 180));

	SpawnProp(FVector(900, -80, 40), TEXT("Counter"));
	SpawnProp(FVector(980, -180, 40), TEXT("Crate"));
	SpawnRoom(FVector(900, -120, 160), FVector(340, 280, 180));

	SpawnProp(FVector(-900, -860, 40), TEXT("Bed"));
	SpawnProp(FVector(-820, -960, 40), TEXT("Counter"));
	SpawnRoom(FVector(-900, -900, 160), FVector(340, 280, 180));

	SpawnProp(FVector(860, -860, 40), TEXT("Forge"));
	SpawnProp(FVector(960, -940, 40), TEXT("Anvil"));
	SpawnRoom(FVector(900, -900, 160), FVector(340, 280, 180));

	for (int32 i = 0; i < 4; ++i)
	{
		ABuildPiece* Piece = World->SpawnActor<ABuildPiece>(GetActorLocation() + FVector(200.0f + i * 200.0f, -400.0f, 0.0f), FRotator::ZeroRotator, P);
		if (Piece)
		{
			Piece->PieceType = (i == 0) ? EBuildPieceType::Foundation : EBuildPieceType::Wall;
			Piece->Occupancy = EBuildOccupancy::Full;
			Piece->RebuildMesh();
			Piece->AttachToActor(this, FAttachmentTransformRules::KeepWorldTransform);
		}
	}
}
