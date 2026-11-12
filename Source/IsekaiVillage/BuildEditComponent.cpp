// Copyright Epic Games, Inc. All Rights Reserved.
#include "BuildEditComponent.h"
#include "BuildPiece.h"
#include "LinchpinProp.h"
#include "RoomVolume.h"
#include "BuildWheelWidget.h"
#include "VillageRuntime.h"
#include "Components/BoxComponent.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "GameFramework/PlayerController.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "EngineUtils.h"
#include "DrawDebugHelpers.h"
#include "Dom/JsonObject.h"
#include "Serialization/JsonSerializer.h"
#include "Serialization/JsonReader.h"
#include "Serialization/JsonWriter.h"
#include "Misc/FileHelper.h"
#include "Misc/Paths.h"
#include "HAL/FileManager.h"
#include "InputCoreTypes.h"

UBuildEditComponent::UBuildEditComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
	AvailablePropTags = {
		TEXT("Anvil"), TEXT("Forge"), TEXT("Bed"), TEXT("Counter"),
		TEXT("Oven"), TEXT("Workbench"), TEXT("Chest"), TEXT("Crate"), TEXT("Board")
	};
	CurrentPropTag = TEXT("Anvil");
}

namespace
{
	FString BuildTemplateDirectory()
	{
		return FPaths::Combine(FPaths::ProjectSavedDir(), TEXT("BuildTemplates"));
	}

	TSharedRef<FJsonObject> VectorToJson(const FVector& Value)
	{
		TSharedRef<FJsonObject> Object = MakeShared<FJsonObject>();
		Object->SetNumberField(TEXT("x"), Value.X);
		Object->SetNumberField(TEXT("y"), Value.Y);
		Object->SetNumberField(TEXT("z"), Value.Z);
		return Object;
	}

	FVector JsonToVector(const TSharedPtr<FJsonObject>& Object, const FVector& Fallback)
	{
		if (!Object.IsValid())
		{
			return Fallback;
		}
		return FVector(Object->GetNumberField(TEXT("x")), Object->GetNumberField(TEXT("y")), Object->GetNumberField(TEXT("z")));
	}

	void RefreshRoomsAt(UWorld* World, const FVector& Location)
	{
		if (!World)
		{
			return;
		}
		for (TActorIterator<ARoomVolume> It(World); It; ++It)
		{
			if (!It->Bounds)
			{
				continue;
			}
			const FBox Box(
				It->GetActorLocation() - It->Bounds->GetScaledBoxExtent(),
				It->GetActorLocation() + It->Bounds->GetScaledBoxExtent());
			if (Box.IsInside(Location))
			{
				It->RefreshFunction();
			}
		}
	}
}

void UBuildEditComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);
	if (!bBuildMode || !GEngine)
	{
		return;
	}
	DrawTemplateSelection();

	if (bPlacingProps)
	{
		FName R1, R2;
		int32 C1 = 0, C2 = 0;
		GetPropCraftCost(CurrentPropTag, R1, C1, R2, C2);
		FString CostStr = FString::Printf(TEXT("Cost: %d %s"), C1, *R1.ToString());
		if (C2 > 0)
		{
			CostStr += FString::Printf(TEXT(", %d %s"), C2, *R2.ToString());
		}

		GEngine->AddOnScreenDebugMessage(74201, 0.0f, FColor::Cyan,
			FString::Printf(TEXT("FURNITURE CRAFT: [%s] | %s | Snap: %s | Yaw: %.0f [LMB place/craft, RMB del, Scroll cycle, P mode, R rotate]"),
				*CurrentPropTag.ToString(), *CostStr, bFreeformPlacement ? TEXT("Free") : TEXT("Room Grid 50cm"), PlacementYaw));
	}
	else
	{
		const TCHAR* StyleName = TEXT("Straight");
		if (CurrentWallStyle == EBuildWallStyle::Diagonal45) StyleName = TEXT("Diagonal 45");
		else if (CurrentWallStyle == EBuildWallStyle::CurvedArc) StyleName = TEXT("Curved Arc");

		const TCHAR* PieceNames[] = { TEXT("Foundation"), TEXT("Floor"), TEXT("Wall"), TEXT("Doorway"), TEXT("Stair"), TEXT("Roof"), TEXT("Pillar") };
		const int32 PieceIdx = FMath::Clamp(static_cast<int32>(CurrentType), 0, 6);

		GEngine->AddOnScreenDebugMessage(74201, 0.0f, FColor::Yellow,
			FString::Printf(TEXT("BUILD: %s [%s] | Scale: %.2fx | Snap: %s | Yaw: %.0f [LMB place, RMB del, Q occ, E corner, M wall, X/C mat, P furniture, R rotate]"),
				PieceNames[PieceIdx], StyleName, CurrentScale.X, bFreeformPlacement ? TEXT("Free") : TEXT("Magnetic Snap"), PlacementYaw));
	}
}

APlayerController* UBuildEditComponent::GetPC() const
{
	if (const APawn* Pawn = Cast<APawn>(GetOwner()))
	{
		return Cast<APlayerController>(Pawn->GetController());
	}
	return nullptr;
}

bool UBuildEditComponent::TraceCursor(FHitResult& OutHit) const
{
	APlayerController* PC = GetPC();
	UWorld* World = GetWorld();
	if (!PC || !World)
	{
		return false;
	}
	FVector Start, Dir;
	if (!PC->DeprojectMousePositionToWorld(Start, Dir))
	{
		FRotator ViewRot;
		PC->GetPlayerViewPoint(Start, ViewRot);
		Dir = ViewRot.Vector();
	}
	const AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner());
	const float Reach = (Character && Character->bFreeBuildCam) ? 120000.0f : 8000.0f;
	FCollisionQueryParams Params(SCENE_QUERY_STAT(BuildTrace), true);
	Params.AddIgnoredActor(GetOwner());
	return World->LineTraceSingleByChannel(OutHit, Start + Dir * 40.0f, Start + Dir * Reach, ECC_Visibility, Params);
}

FVector UBuildEditComponent::SnapLocation(const FVector& World) const
{
	return ABuildPiece::SnapWorld(World, 200.0f);
}

FVector UBuildEditComponent::SnapFurnitureLocation(const FVector& WorldLoc, FRotator& InOutRotation) const
{
	if (bFreeformPlacement)
	{
		return WorldLoc;
	}

	// Snap to 50cm internal room sub-grid
	const float GridSize = 50.0f;
	FVector Snapped(
		FMath::RoundToFloat(WorldLoc.X / GridSize) * GridSize,
		FMath::RoundToFloat(WorldLoc.Y / GridSize) * GridSize,
		WorldLoc.Z
	);

	// Check if near an interior ABuildPiece wall within 120cm for wall flush alignment
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<ABuildPiece> It(World); It; ++It)
		{
			if (It->PieceType == EBuildPieceType::Wall || It->PieceType == EBuildPieceType::Doorway)
			{
				const float DistSq = FVector::DistSquared2D(It->GetActorLocation(), WorldLoc);
				if (DistSq < FMath::Square(120.0f))
				{
					// Snap flush with wall back
					const FVector WallFwd = It->GetActorForwardVector();
					const FVector WallRight = It->GetActorRightVector();
					InOutRotation.Yaw = It->GetActorRotation().Yaw;
					Snapped.X = It->GetActorLocation().X + WallFwd.X * 35.0f;
					Snapped.Y = It->GetActorLocation().Y + WallFwd.Y * 35.0f;
					break;
				}
			}
		}
	}

	return Snapped;
}

bool UBuildEditComponent::GetPropCraftCost(FName PropTag, FName& OutRes1, int32& OutCost1, FName& OutRes2, int32& OutCost2)
{
	OutRes1 = TEXT("Wood");
	OutCost1 = 2;
	OutRes2 = NAME_None;
	OutCost2 = 0;

	if (PropTag == TEXT("Anvil"))
	{
		OutRes1 = TEXT("Iron");
		OutCost1 = 4;
		OutRes2 = TEXT("Stone");
		OutCost2 = 2;
		return true;
	}
	if (PropTag == TEXT("Forge"))
	{
		OutRes1 = TEXT("Stone");
		OutCost1 = 6;
		OutRes2 = TEXT("Iron");
		OutCost2 = 2;
		return true;
	}
	if (PropTag == TEXT("Bed"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 6;
		OutRes2 = TEXT("ToolParts");
		OutCost2 = 1;
		return true;
	}
	if (PropTag == TEXT("Counter"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 4;
		OutRes2 = TEXT("Stone");
		OutCost2 = 1;
		return true;
	}
	if (PropTag == TEXT("Oven"))
	{
		OutRes1 = TEXT("Stone");
		OutCost1 = 6;
		OutRes2 = TEXT("Iron");
		OutCost2 = 2;
		return true;
	}
	if (PropTag == TEXT("Workbench"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 4;
		OutRes2 = TEXT("Iron");
		OutCost2 = 1;
		return true;
	}
	if (PropTag == TEXT("Chest"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 4;
		OutRes2 = TEXT("Iron");
		OutCost2 = 1;
		return true;
	}
	if (PropTag == TEXT("Crate"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 2;
		return true;
	}
	if (PropTag == TEXT("Cauldron"))
	{
		OutRes1 = TEXT("Stone");
		OutCost1 = 4;
		OutRes2 = TEXT("Iron");
		OutCost2 = 2;
		return true;
	}
	if (PropTag == TEXT("HerbRack"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 4;
		OutRes2 = TEXT("Stone");
		OutCost2 = 1;
		return true;
	}
	if (PropTag == TEXT("ArcaneTable"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 6;
		OutRes2 = TEXT("Crystal");
		OutCost2 = 2;
		return true;
	}
	if (PropTag == TEXT("CrystalFocus"))
	{
		OutRes1 = TEXT("Stone");
		OutCost1 = 2;
		OutRes2 = TEXT("Crystal");
		OutCost2 = 3;
		return true;
	}
	if (PropTag == TEXT("CelestialAnvil"))
	{
		OutRes1 = TEXT("Iron");
		OutCost1 = 10;
		OutRes2 = TEXT("Crystal");
		OutCost2 = 5;
		return true;
	}
	if (PropTag == TEXT("RunicCrucible"))
	{
		OutRes1 = TEXT("Stone");
		OutCost1 = 12;
		OutRes2 = TEXT("Crystal");
		OutCost2 = 6;
		return true;
	}
	if (PropTag == TEXT("Board"))
	{
		OutRes1 = TEXT("Wood");
		OutCost1 = 3;
		return true;
	}
	return false;
}

void UBuildEditComponent::ToggleBuildMode()
{
	bBuildMode = !bBuildMode;
	if (!bBuildMode)
	{
		SelectedPiece = nullptr;
		SelectedProp = nullptr;
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Yellow, bBuildMode ? TEXT("Build mode ON (Palworld/Fallout modular)") : TEXT("Build mode OFF"));
	}
}

void UBuildEditComponent::TogglePropPlacementMode()
{
	bPlacingProps = !bPlacingProps;
	SelectedPiece = nullptr;
	SelectedProp = nullptr;
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan, bPlacingProps ? TEXT("Placement Mode: FURNITURE & LINCHPIN WORKSTATIONS") : TEXT("Placement Mode: MODULAR WALLS & FLOORS"));
	}
}

void UBuildEditComponent::CyclePropType(int32 Direction)
{
	if (AvailablePropTags.Num() == 0)
	{
		return;
	}
	int32 CurrentIdx = AvailablePropTags.IndexOfByKey(CurrentPropTag);
	if (CurrentIdx == INDEX_NONE)
	{
		CurrentIdx = 0;
	}
	int32 NextIdx = CurrentIdx + (Direction >= 0 ? 1 : -1);
	if (NextIdx < 0) NextIdx = AvailablePropTags.Num() - 1;
	if (NextIdx >= AvailablePropTags.Num()) NextIdx = 0;
	CurrentPropTag = AvailablePropTags[NextIdx];

	if (SelectedProp)
	{
		SelectedProp->SetupProp(CurrentPropTag);
	}
}

void UBuildEditComponent::ToggleFreeform()
{
	bFreeformPlacement = !bFreeformPlacement;
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan, bFreeformPlacement ? TEXT("Freeform Placement: ON") : TEXT("Socket/Grid Snapping: ON"));
	}
}

void UBuildEditComponent::RotatePlacement(float DeltaDegrees)
{
	PlacementYaw = FRotator::NormalizeAxis(PlacementYaw + DeltaDegrees);
	if (SelectedPiece)
	{
		FRotator NewRot = SelectedPiece->GetActorRotation();
		NewRot.Yaw = FRotator::NormalizeAxis(NewRot.Yaw + DeltaDegrees);
		SelectedPiece->SetActorRotation(NewRot);
	}
	if (SelectedProp)
	{
		FRotator NewRot = SelectedProp->GetActorRotation();
		NewRot.Yaw = FRotator::NormalizeAxis(NewRot.Yaw + DeltaDegrees);
		SelectedProp->SetActorRotation(NewRot);
	}
}

void UBuildEditComponent::AdjustScale(float Factor)
{
	CurrentScale = (CurrentScale * Factor).GetClampedToSize(0.25f, 4.0f);
	if (SelectedPiece)
	{
		SelectedPiece->AdjustScale(Factor);
	}
}

void UBuildEditComponent::CycleWallStyle()
{
	const uint8 Next = (static_cast<uint8>(CurrentWallStyle) + 1) % 3;
	CurrentWallStyle = static_cast<EBuildWallStyle>(Next);
	if (SelectedPiece)
	{
		SelectedPiece->SetWallStyle(CurrentWallStyle);
	}
}

void UBuildEditComponent::CycleExteriorMaterial()
{
	const uint8 Next = (static_cast<uint8>(CurrentMaterials.ExteriorMaterial) + 1) % 9;
	CurrentMaterials.ExteriorMaterial = static_cast<EBuildMaterialStyle>(Next);
	if (SelectedPiece)
	{
		SelectedPiece->CycleExteriorMaterial();
	}
}

void UBuildEditComponent::CycleInteriorMaterial()
{
	const uint8 Next = (static_cast<uint8>(CurrentMaterials.InteriorMaterial) + 1) % 9;
	CurrentMaterials.InteriorMaterial = static_cast<EBuildMaterialStyle>(Next);
	if (SelectedPiece)
	{
		SelectedPiece->CycleInteriorMaterial();
	}
}

void UBuildEditComponent::CycleTrimMaterial()
{
	const uint8 Next = (static_cast<uint8>(CurrentMaterials.TrimMaterial) + 1) % 9;
	CurrentMaterials.TrimMaterial = static_cast<EBuildMaterialStyle>(Next);
	if (SelectedPiece)
	{
		SelectedPiece->CycleTrimMaterial();
	}
}

void UBuildEditComponent::ToggleQuadrant(int32 QuadrantIndex)
{
	if (SelectedPiece)
	{
		SelectedPiece->ToggleQuadrant(QuadrantIndex);
	}
}

bool UBuildEditComponent::TryCraftAndPlaceProp(AIsekaiVillageCharacter* Character, const FVector& Location, const FRotator& Rotation)
{
	if (!Character)
	{
		return false;
	}

	FName R1, R2;
	int32 C1 = 0, C2 = 0;
	GetPropCraftCost(CurrentPropTag, R1, C1, R2, C2);

	if (Character->Gather)
	{
		if (Character->Gather->GetCount(R1) < C1 || (C2 > 0 && Character->Gather->GetCount(R2) < C2))
		{
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Red,
					FString::Printf(TEXT("Cannot craft %s: Need %d %s!"), *CurrentPropTag.ToString(), C1, *R1.ToString()));
			}
			return false;
		}

		Character->Gather->Consume(R1, C1);
		if (C2 > 0)
		{
			Character->Gather->Consume(R2, C2);
		}
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return false;
	}

	ALinchpinProp* Prop = World->SpawnActor<ALinchpinProp>(Location, Rotation);
	if (Prop)
	{
		Prop->SetupProp(CurrentPropTag);
		SelectedProp = Prop;

		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Green,
				FString::Printf(TEXT("Crafted & Placed %s!"), *Prop->DisplayName.ToString()));
		}

		// Trigger immediate scan on any enclosing ARoomVolume
		for (TActorIterator<ARoomVolume> It(World); It; ++It)
		{
			if (It->Bounds)
			{
				const FBox Box(It->GetActorLocation() - It->Bounds->GetScaledBoxExtent(), It->GetActorLocation() + It->Bounds->GetScaledBoxExtent());
				if (Box.IsInside(Location))
				{
					It->RefreshFunction();
				}
			}
		}
		return true;
	}
	return false;
}

void UBuildEditComponent::PlaceOrSelect()
{
	if (!bBuildMode)
	{
		return;
	}
	FHitResult Hit;
	if (!TraceCursor(Hit))
	{
		return;
	}

	AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(GetOwner());
	if (APlayerController* PC = GetPC(); PC && PC->IsInputKeyDown(EKeys::LeftShift))
	{
		ToggleSelectionActor(Hit.GetActor());
		return;
	}
	if (IsTemplateArmed())
	{
		const FVector Origin = bFreeformPlacement ? Hit.Location : SnapLocation(Hit.Location);
		StampTemplateNamed(LoadedTemplates[ArmedTemplateIndex].Name, Origin, PlacementYaw);
		return;
	}

	if (bPlacingProps)
	{
		if (ALinchpinProp* Prop = Cast<ALinchpinProp>(Hit.GetActor()))
		{
			SelectedProp = Prop;
			CurrentPropTag = Prop->LinchpinTag;
			PlacementYaw = Prop->GetActorRotation().Yaw;
			return;
		}

		FRotator SnappedRot(0.0f, PlacementYaw, 0.0f);
		FVector SnappedLoc = SnapFurnitureLocation(Hit.Location, SnappedRot);
		TryCraftAndPlaceProp(Character, SnappedLoc, SnappedRot);
		return;
	}

	// Modular Building Piece Placement
	if (ABuildPiece* Piece = Cast<ABuildPiece>(Hit.GetActor()))
	{
		SelectedPiece = Piece;
		CurrentType = Piece->PieceType;
		CurrentOccupancy = Piece->Occupancy;
		CurrentWallStyle = Piece->WallStyle;
		CurrentMaterials = Piece->MaterialConfig;
		CurrentScale = Piece->ScaleMultiplier;
		PlacementYaw = Piece->GetActorRotation().Yaw;
		return;
	}

	UWorld* World = GetWorld();
	if (!World)
	{
		return;
	}

	FVector SpawnLoc = bFreeformPlacement ? Hit.Location : SnapLocation(Hit.Location);
	FRotator SpawnRot = FRotator(0.0f, PlacementYaw, 0.0f);

	if (!bFreeformPlacement)
	{
		TArray<ABuildPiece*> NearbyPieces;
		for (TActorIterator<ABuildPiece> It(World); It; ++It)
		{
			if (FVector::DistSquared(It->GetActorLocation(), Hit.Location) < FMath::Square(600.0f))
			{
				NearbyPieces.Add(*It);
			}
		}

		if (NearbyPieces.Num() > 0)
		{
			FVector SnappedLoc = FVector::ZeroVector;
			FRotator SnappedRot = FRotator::ZeroRotator;
			float BestDistSq = FMath::Square(140.0f);
			bool bSnapped = false;
			for (const ABuildPiece* Other : NearbyPieces)
			{
				for (const FVector& Pt : Other->GetSnapPoints())
				{
					const float DSq = FVector::DistSquared(Pt, Hit.Location);
					if (DSq < BestDistSq)
					{
						BestDistSq = DSq;
						SnappedLoc = Pt;
						SnappedRot = Other->GetActorRotation();
						bSnapped = true;
					}
				}
			}
			if (bSnapped)
			{
				SpawnLoc = SnappedLoc;
				SpawnRot = SnappedRot;
			}
		}
	}

	ABuildPiece* Piece = World->SpawnActor<ABuildPiece>(SpawnLoc, SpawnRot);
	if (Piece)
	{
		Piece->PieceType = CurrentType;
		Piece->Occupancy = CurrentOccupancy;
		Piece->WallStyle = CurrentWallStyle;
		Piece->MaterialConfig = CurrentMaterials;
		Piece->ScaleMultiplier = CurrentScale;
		Piece->RebuildMesh();
		SelectedPiece = Piece;
	}
}

void UBuildEditComponent::CycleOccupancy()
{
	if (!bBuildMode)
	{
		return;
	}
	const int32 Next = (static_cast<int32>(CurrentOccupancy) + 1) % 4;
	CurrentOccupancy = static_cast<EBuildOccupancy>(Next);
	if (SelectedPiece)
	{
		SelectedPiece->SetOccupancy(CurrentOccupancy);
	}
}

void UBuildEditComponent::CyclePieceType(int32 Direction)
{
	if (!bBuildMode)
	{
		return;
	}
	if (bPlacingProps)
	{
		CyclePropType(Direction);
		return;
	}

	const int32 Count = static_cast<int32>(EBuildPieceType::Pillar) + 1;
	int32 Next = static_cast<int32>(CurrentType) + (Direction >= 0 ? 1 : -1);
	if (Next < 0) Next = Count - 1;
	if (Next >= Count) Next = 0;
	CurrentType = static_cast<EBuildPieceType>(Next);
	if (SelectedPiece)
	{
		SelectedPiece->PieceType = CurrentType;
		SelectedPiece->RebuildMesh();
	}
}

void UBuildEditComponent::CycleCornerStyle()
{
	if (!bBuildMode || !SelectedPiece)
	{
		ActiveCorner = (ActiveCorner + 1) % 4;
		return;
	}
	SelectedPiece->CycleCornerStyle(ActiveCorner);
	ActiveCorner = (ActiveCorner + 1) % 4;
}

void UBuildEditComponent::NudgeActiveCorner(float Amount)
{
	if (!bBuildMode || !SelectedPiece)
	{
		return;
	}
	SelectedPiece->EnsureCorners();
	if (!SelectedPiece->Corners.IsValidIndex(ActiveCorner))
	{
		return;
	}
	const FVector2D Dirs[4] = { FVector2D(-1, -1), FVector2D(1, -1), FVector2D(1, 1), FVector2D(-1, 1) };
	SelectedPiece->SetCornerOffset(ActiveCorner, SelectedPiece->Corners[ActiveCorner].Offset + Dirs[ActiveCorner].GetSafeNormal() * Amount);
}

void UBuildEditComponent::RemoveSelected()
{
	if (!bBuildMode)
	{
		return;
	}
	if (SelectedProp)
	{
		SelectedProp->Destroy();
		SelectedProp = nullptr;
		return;
	}
	if (SelectedPiece)
	{
		SelectedPiece->Destroy();
		SelectedPiece = nullptr;
		return;
	}
	FHitResult Hit;
	if (TraceCursor(Hit))
	{
		if (ALinchpinProp* Prop = Cast<ALinchpinProp>(Hit.GetActor()))
		{
			Prop->Destroy();
			return;
		}
		if (ABuildPiece* Piece = Cast<ABuildPiece>(Hit.GetActor()))
		{
			Piece->Destroy();
		}
	}
}

void UBuildEditComponent::ToggleSelectionActor(AActor* Actor)
{
	if (ABuildPiece* Piece = Cast<ABuildPiece>(Actor))
	{
		if (Piece->bPreview)
		{
			return;
		}
		const int32 Index = TemplateSelectionPieces.IndexOfByKey(Piece);
		if (Index != INDEX_NONE)
		{
			TemplateSelectionPieces.RemoveAt(Index);
		}
		else
		{
			TemplateSelectionPieces.Add(Piece);
		}
		SelectedPiece = Piece;
		return;
	}
	if (ALinchpinProp* Prop = Cast<ALinchpinProp>(Actor))
	{
		const int32 Index = TemplateSelectionProps.IndexOfByKey(Prop);
		if (Index != INDEX_NONE)
		{
			TemplateSelectionProps.RemoveAt(Index);
		}
		else
		{
			TemplateSelectionProps.Add(Prop);
		}
		SelectedProp = Prop;
	}
}

int32 UBuildEditComponent::GrabUnderCursor(float Radius)
{
	FHitResult Hit;
	FVector Origin = FVector::ZeroVector;
	if (TraceCursor(Hit))
	{
		Origin = Hit.Location;
	}
	else if (const AActor* Owner = GetOwner())
	{
		Origin = Owner->GetActorLocation() + Owner->GetActorForwardVector() * 1500.0f;
	}
	else
	{
		return 0;
	}

	TemplateSelectionPieces.Reset();
	TemplateSelectionProps.Reset();
	UWorld* World = GetWorld();
	if (!World)
	{
		return 0;
	}
	const float RadiusSq = FMath::Square(Radius);
	for (TActorIterator<ABuildPiece> It(World); It; ++It)
	{
		if (!It->bPreview && FVector::DistSquared(It->GetActorLocation(), Origin) <= RadiusSq)
		{
			TemplateSelectionPieces.Add(*It);
		}
	}
	for (TActorIterator<ALinchpinProp> It(World); It; ++It)
	{
		if (FVector::DistSquared(It->GetActorLocation(), Origin) <= RadiusSq)
		{
			TemplateSelectionProps.Add(*It);
		}
	}
	const int32 Count = GetTemplateSelectionCount();
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Green, FString::Printf(TEXT("Grabbed %d pieces for a template."), Count));
	}
	return Count;
}

FBuildTemplate UBuildEditComponent::CaptureSelection(const FString& Name) const
{
	FBuildTemplate Template;
	Template.Name = Name;
	FVector Sum = FVector::ZeroVector;
	int32 Count = 0;
	for (const ABuildPiece* Piece : TemplateSelectionPieces)
	{
		if (IsValid(Piece))
		{
			Sum += Piece->GetActorLocation();
			++Count;
		}
	}
	for (const ALinchpinProp* Prop : TemplateSelectionProps)
	{
		if (IsValid(Prop))
		{
			Sum += Prop->GetActorLocation();
			++Count;
		}
	}
	if (Count == 0)
	{
		return Template;
	}
	const FVector Anchor = Sum / static_cast<float>(Count);
	for (const ABuildPiece* Piece : TemplateSelectionPieces)
	{
		if (!IsValid(Piece))
		{
			continue;
		}
		FBuildTemplatePiece Record;
		Record.PieceType = Piece->PieceType;
		Record.Occupancy = Piece->Occupancy;
		Record.WallStyle = Piece->WallStyle;
		Record.Materials = Piece->MaterialConfig;
		Record.RelativeLocation = Piece->GetActorLocation() - Anchor;
		Record.RelativeYaw = Piece->GetActorRotation().Yaw;
		Record.ScaleMultiplier = Piece->ScaleMultiplier;
		Record.SectionMask = Piece->SectionMask;
		Record.Corners = Piece->Corners;
		Record.CellSize = Piece->CellSize;
		Record.WallHeight = Piece->WallHeight;
		Record.Thickness = Piece->Thickness;
		Template.Pieces.Add(Record);
	}
	for (const ALinchpinProp* Prop : TemplateSelectionProps)
	{
		if (!IsValid(Prop))
		{
			continue;
		}
		FBuildTemplateProp Record;
		Record.PropTag = Prop->LinchpinTag;
		Record.RelativeLocation = Prop->GetActorLocation() - Anchor;
		Record.RelativeYaw = Prop->GetActorRotation().Yaw;
		Template.Props.Add(Record);
	}
	return Template;
}

FString UBuildEditComponent::SaveTemplateNamed(const FString& Name)
{
	if (Name.IsEmpty() || Name.Contains(TEXT("/")) || Name.Contains(TEXT("\\")) || Name.Contains(TEXT("..")))
	{
		return FString();
	}
	const FBuildTemplate Template = CaptureSelection(Name);
	if (Template.Pieces.Num() == 0 && Template.Props.Num() == 0)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("Select pieces with Shift+Click or F3 before saving a template."));
		}
		return FString();
	}

	TSharedRef<FJsonObject> Root = MakeShared<FJsonObject>();
	Root->SetStringField(TEXT("name"), Template.Name);
	TArray<TSharedPtr<FJsonValue>> PieceValues;
	for (const FBuildTemplatePiece& Piece : Template.Pieces)
	{
		TSharedRef<FJsonObject> Object = MakeShared<FJsonObject>();
		Object->SetNumberField(TEXT("type"), static_cast<int32>(Piece.PieceType));
		Object->SetNumberField(TEXT("occupancy"), static_cast<int32>(Piece.Occupancy));
		Object->SetNumberField(TEXT("wallStyle"), static_cast<int32>(Piece.WallStyle));
		Object->SetNumberField(TEXT("exterior"), static_cast<int32>(Piece.Materials.ExteriorMaterial));
		Object->SetNumberField(TEXT("interior"), static_cast<int32>(Piece.Materials.InteriorMaterial));
		Object->SetNumberField(TEXT("trim"), static_cast<int32>(Piece.Materials.TrimMaterial));
		Object->SetObjectField(TEXT("location"), VectorToJson(Piece.RelativeLocation));
		Object->SetNumberField(TEXT("yaw"), Piece.RelativeYaw);
		Object->SetObjectField(TEXT("scale"), VectorToJson(Piece.ScaleMultiplier));
		Object->SetNumberField(TEXT("sectionMask"), Piece.SectionMask);
		Object->SetNumberField(TEXT("cell"), Piece.CellSize);
		Object->SetNumberField(TEXT("height"), Piece.WallHeight);
		Object->SetNumberField(TEXT("thickness"), Piece.Thickness);
		TArray<TSharedPtr<FJsonValue>> CornerValues;
		for (const FBuildCorner& Corner : Piece.Corners)
		{
			TSharedRef<FJsonObject> CornerObject = MakeShared<FJsonObject>();
			CornerObject->SetNumberField(TEXT("style"), static_cast<int32>(Corner.Style));
			CornerObject->SetNumberField(TEXT("x"), Corner.Offset.X);
			CornerObject->SetNumberField(TEXT("y"), Corner.Offset.Y);
			CornerValues.Add(MakeShared<FJsonValueObject>(CornerObject));
		}
		Object->SetArrayField(TEXT("corners"), CornerValues);
		PieceValues.Add(MakeShared<FJsonValueObject>(Object));
	}
	Root->SetArrayField(TEXT("pieces"), PieceValues);
	TArray<TSharedPtr<FJsonValue>> PropValues;
	for (const FBuildTemplateProp& Prop : Template.Props)
	{
		TSharedRef<FJsonObject> Object = MakeShared<FJsonObject>();
		Object->SetStringField(TEXT("tag"), Prop.PropTag.ToString());
		Object->SetObjectField(TEXT("location"), VectorToJson(Prop.RelativeLocation));
		Object->SetNumberField(TEXT("yaw"), Prop.RelativeYaw);
		PropValues.Add(MakeShared<FJsonValueObject>(Object));
	}
	Root->SetArrayField(TEXT("props"), PropValues);

	FString Json;
	const TSharedRef<TJsonWriter<>> Writer = TJsonWriterFactory<>::Create(&Json);
	if (!FJsonSerializer::Serialize(Root, Writer))
	{
		return FString();
	}
	const FString Directory = BuildTemplateDirectory();
	IFileManager::Get().MakeDirectory(*Directory, true);
	const FString Path = FPaths::Combine(Directory, Name + TEXT(".json"));
	if (!FFileHelper::SaveStringToFile(Json, *Path))
	{
		return FString();
	}

	ReloadBuildTemplates();
	ArmedTemplateIndex = LoadedTemplates.IndexOfByPredicate([&Name](const FBuildTemplate& Item) { return Item.Name == Name; });
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 4.0f, FColor::Green, FString::Printf(TEXT("Saved template %s  (%d parts)  Saved/BuildTemplates/%s.json"), *Name, Template.Pieces.Num() + Template.Props.Num(), *Name));
	}
	return Name;
}

FString UBuildEditComponent::SaveSelectionAsTemplate()
{
	const FString Directory = BuildTemplateDirectory();
	int32 Index = 1;
	FString Name;
	do
	{
		Name = FString::Printf(TEXT("Template_%02d"), Index);
		++Index;
	}
	while (FPaths::FileExists(FPaths::Combine(Directory, Name + TEXT(".json"))));
	return SaveTemplateNamed(Name);
}

void UBuildEditComponent::ClearTemplateSelection()
{
	TemplateSelectionPieces.Reset();
	TemplateSelectionProps.Reset();
	ArmedTemplateIndex = -1;
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Silver, TEXT("Template selection cleared."));
	}
}

void UBuildEditComponent::ReloadBuildTemplates()
{
	const FString ArmedName = GetArmedTemplateName();
	LoadedTemplates.Reset();
	TArray<FString> Files;
	IFileManager::Get().FindFiles(Files, *FPaths::Combine(BuildTemplateDirectory(), TEXT("*.json")), true, false);
	Files.Sort();
	for (const FString& File : Files)
	{
		FString Json;
		if (!FFileHelper::LoadFileToString(Json, *FPaths::Combine(BuildTemplateDirectory(), File)))
		{
			continue;
		}
		TSharedPtr<FJsonObject> Root;
		const TSharedRef<TJsonReader<>> Reader = TJsonReaderFactory<>::Create(Json);
		if (!FJsonSerializer::Deserialize(Reader, Root) || !Root.IsValid())
		{
			continue;
		}
		FBuildTemplate Template;
		Template.Name = Root->GetStringField(TEXT("name"));
		if (Template.Name.IsEmpty())
		{
			Template.Name = FPaths::GetBaseFilename(File);
		}
		const TArray<TSharedPtr<FJsonValue>>* PieceValues = nullptr;
		if (Root->TryGetArrayField(TEXT("pieces"), PieceValues))
		{
			for (const TSharedPtr<FJsonValue>& Value : *PieceValues)
			{
				const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
				if (!Object.IsValid())
				{
					continue;
				}
				FBuildTemplatePiece Piece;
				Piece.PieceType = static_cast<EBuildPieceType>(static_cast<uint8>(Object->GetIntegerField(TEXT("type"))));
				Piece.Occupancy = static_cast<EBuildOccupancy>(static_cast<uint8>(Object->GetIntegerField(TEXT("occupancy"))));
				Piece.WallStyle = static_cast<EBuildWallStyle>(static_cast<uint8>(Object->GetIntegerField(TEXT("wallStyle"))));
				Piece.Materials.ExteriorMaterial = static_cast<EBuildMaterialStyle>(static_cast<uint8>(Object->GetIntegerField(TEXT("exterior"))));
				Piece.Materials.InteriorMaterial = static_cast<EBuildMaterialStyle>(static_cast<uint8>(Object->GetIntegerField(TEXT("interior"))));
				Piece.Materials.TrimMaterial = static_cast<EBuildMaterialStyle>(static_cast<uint8>(Object->GetIntegerField(TEXT("trim"))));
				const TSharedPtr<FJsonObject>* Location = nullptr;
				if (Object->TryGetObjectField(TEXT("location"), Location))
				{
					Piece.RelativeLocation = JsonToVector(*Location, FVector::ZeroVector);
				}
				Piece.RelativeYaw = Object->GetNumberField(TEXT("yaw"));
				const TSharedPtr<FJsonObject>* Scale = nullptr;
				if (Object->TryGetObjectField(TEXT("scale"), Scale))
				{
					Piece.ScaleMultiplier = JsonToVector(*Scale, FVector::OneVector);
				}
				Piece.SectionMask = static_cast<uint8>(Object->GetIntegerField(TEXT("sectionMask")));
				double Cell = 200.0;
				double Height = 280.0;
				double Thickness = 18.0;
				Object->TryGetNumberField(TEXT("cell"), Cell);
				Object->TryGetNumberField(TEXT("height"), Height);
				Object->TryGetNumberField(TEXT("thickness"), Thickness);
				Piece.CellSize = static_cast<float>(Cell);
				Piece.WallHeight = static_cast<float>(Height);
				Piece.Thickness = static_cast<float>(Thickness);
				const TArray<TSharedPtr<FJsonValue>>* CornerValues = nullptr;
				if (Object->TryGetArrayField(TEXT("corners"), CornerValues))
				{
					for (const TSharedPtr<FJsonValue>& CornerValue : *CornerValues)
					{
						const TSharedPtr<FJsonObject> CornerObject = CornerValue.IsValid() ? CornerValue->AsObject() : nullptr;
						if (!CornerObject.IsValid())
						{
							continue;
						}
						FBuildCorner Corner;
						Corner.Style = static_cast<EBuildCornerStyle>(static_cast<uint8>(CornerObject->GetIntegerField(TEXT("style"))));
						Corner.Offset = FVector2D(CornerObject->GetNumberField(TEXT("x")), CornerObject->GetNumberField(TEXT("y")));
						Piece.Corners.Add(Corner);
					}
				}
				Template.Pieces.Add(Piece);
			}
		}
		const TArray<TSharedPtr<FJsonValue>>* PropValues = nullptr;
		if (Root->TryGetArrayField(TEXT("props"), PropValues))
		{
			for (const TSharedPtr<FJsonValue>& Value : *PropValues)
			{
				const TSharedPtr<FJsonObject> Object = Value.IsValid() ? Value->AsObject() : nullptr;
				if (!Object.IsValid())
				{
					continue;
				}
				FBuildTemplateProp Prop;
				Prop.PropTag = FName(*Object->GetStringField(TEXT("tag")));
				const TSharedPtr<FJsonObject>* Location = nullptr;
				if (Object->TryGetObjectField(TEXT("location"), Location))
				{
					Prop.RelativeLocation = JsonToVector(*Location, FVector::ZeroVector);
				}
				Prop.RelativeYaw = Object->GetNumberField(TEXT("yaw"));
				Template.Props.Add(Prop);
			}
		}
		if (Template.Pieces.Num() > 0 || Template.Props.Num() > 0)
		{
			LoadedTemplates.Add(Template);
		}
	}
	ArmedTemplateIndex = LoadedTemplates.IndexOfByPredicate([&ArmedName](const FBuildTemplate& Item) { return Item.Name == ArmedName; });
}

void UBuildEditComponent::CycleArmedTemplate(int32 Direction)
{
	const FString Current = GetArmedTemplateName();
	ReloadBuildTemplates();
	if (LoadedTemplates.Num() == 0)
	{
		ArmedTemplateIndex = -1;
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Orange, TEXT("No saved templates in Saved/BuildTemplates."));
		}
		return;
	}
	int32 Slot = LoadedTemplates.IndexOfByPredicate([&Current](const FBuildTemplate& Item) { return Item.Name == Current; });
	const int32 Span = LoadedTemplates.Num() + 1;
	int32 Cursor = Slot + 1;
	Cursor = (Cursor + (Direction >= 0 ? 1 : -1) + Span * 2) % Span;
	ArmedTemplateIndex = Cursor - 1;
	if (GEngine)
	{
		const FString Label = IsTemplateArmed() ? GetArmedTemplateName() : FString(TEXT("none"));
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Cyan, FString::Printf(TEXT("Stamp template: %s"), *Label));
	}
}

FString UBuildEditComponent::GetArmedTemplateName() const
{
	return IsTemplateArmed() ? LoadedTemplates[ArmedTemplateIndex].Name : FString();
}

int32 UBuildEditComponent::GetTemplateSelectionCount() const
{
	int32 Count = 0;
	for (const ABuildPiece* Piece : TemplateSelectionPieces)
	{
		if (IsValid(Piece))
		{
			++Count;
		}
	}
	for (const ALinchpinProp* Prop : TemplateSelectionProps)
	{
		if (IsValid(Prop))
		{
			++Count;
		}
	}
	return Count;
}

int32 UBuildEditComponent::StampTemplateNamed(const FString& Name, const FVector& Origin, float Yaw)
{
	if (!LoadedTemplates.ContainsByPredicate([&Name](const FBuildTemplate& Item) { return Item.Name == Name; }))
	{
		ReloadBuildTemplates();
	}
	const FBuildTemplate* Template = LoadedTemplates.FindByPredicate([&Name](const FBuildTemplate& Item) { return Item.Name == Name; });
	UWorld* World = GetWorld();
	if (!Template || !World)
	{
		return 0;
	}
	int32 Spawned = 0;
	for (const FBuildTemplatePiece& Record : Template->Pieces)
	{
		const FVector Location = Origin + Record.RelativeLocation.RotateAngleAxis(Yaw, FVector::UpVector);
		const FRotator Rotation(0.0f, Record.RelativeYaw + Yaw, 0.0f);
		ABuildPiece* Piece = World->SpawnActor<ABuildPiece>(Location, Rotation);
		if (!Piece)
		{
			continue;
		}
		Piece->PieceType = Record.PieceType;
		Piece->Occupancy = Record.Occupancy;
		Piece->WallStyle = Record.WallStyle;
		Piece->MaterialConfig = Record.Materials;
		Piece->ScaleMultiplier = Record.ScaleMultiplier;
		Piece->SectionMask = Record.SectionMask;
		Piece->CellSize = Record.CellSize;
		Piece->WallHeight = Record.WallHeight;
		Piece->Thickness = Record.Thickness;
		if (Record.Corners.Num() == 4)
		{
			Piece->Corners = Record.Corners;
		}
		Piece->RebuildMesh();
		++Spawned;
	}
	for (const FBuildTemplateProp& Record : Template->Props)
	{
		const FVector Location = Origin + Record.RelativeLocation.RotateAngleAxis(Yaw, FVector::UpVector);
		const FRotator Rotation(0.0f, Record.RelativeYaw + Yaw, 0.0f);
		ALinchpinProp* Prop = World->SpawnActor<ALinchpinProp>(Location, Rotation);
		if (!Prop)
		{
			continue;
		}
		Prop->SetupProp(Record.PropTag);
		RefreshRoomsAt(World, Location);
		++Spawned;
	}
	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 2.0f, FColor::Green, FString::Printf(TEXT("Stamped %s (%d parts)."), *Name, Spawned));
	}
	return Spawned;
}

void UBuildEditComponent::DrawTemplateSelection() const
{
	UWorld* World = GetWorld();
	if (!World || !World->IsGameWorld())
	{
		return;
	}
	for (const ABuildPiece* Piece : TemplateSelectionPieces)
	{
		if (IsValid(Piece))
		{
			DrawDebugBox(World, Piece->GetActorLocation(), FVector(90.0f, 90.0f, 150.0f), FColor::Green, false, 0.0f, 0, 2.0f);
		}
	}
	for (const ALinchpinProp* Prop : TemplateSelectionProps)
	{
		if (IsValid(Prop))
		{
			DrawDebugBox(World, Prop->GetActorLocation(), FVector(55.0f, 55.0f, 55.0f), FColor::Cyan, false, 0.0f, 0, 2.0f);
		}
	}
}

int32 UBuildEditComponent::GetUnlockedTier() const
{
	int32 Cleared = 0;
	if (const AVillageRuntime* Village = AVillageRuntime::Get(this))
	{
		Cleared = Village->TowerFloor.HighestFloor;
	}
	if (Cleared >= 10) return 4;
	if (Cleared >= 5) return 3;
	if (Cleared >= 1) return 2;
	return 1;
}

bool UBuildEditComponent::IsPropUnlocked(FName PropTag) const
{
	const int32 Tier = GetUnlockedTier();
	if (PropTag == TEXT("Cauldron") || PropTag == TEXT("HerbRack") || PropTag == TEXT("ArcaneTable") || PropTag == TEXT("CrystalFocus"))
	{
		return Tier >= 2;
	}
	if (PropTag == TEXT("Desk") || PropTag == TEXT("Vault"))
	{
		return Tier >= 3;
	}
	if (PropTag == TEXT("CelestialAnvil") || PropTag == TEXT("RunicCrucible"))
	{
		return Tier >= 4;
	}
	return true;
}

void UBuildEditComponent::RefreshUnlockedProps()
{
	const TArray<FName> FullList = {
		TEXT("Anvil"), TEXT("Forge"), TEXT("Bed"), TEXT("Counter"),
		TEXT("Oven"), TEXT("Workbench"), TEXT("Chest"), TEXT("Crate"), TEXT("Board"),
		TEXT("Cauldron"), TEXT("HerbRack"), TEXT("ArcaneTable"), TEXT("CrystalFocus"),
		TEXT("CelestialAnvil"), TEXT("RunicCrucible")
	};
	AvailablePropTags.Reset();
	for (const FName& Tag : FullList)
	{
		if (IsPropUnlocked(Tag))
		{
			AvailablePropTags.Add(Tag);
		}
	}
	if (!AvailablePropTags.Contains(CurrentPropTag) && AvailablePropTags.Num() > 0)
	{
		CurrentPropTag = AvailablePropTags[0];
	}
}

void UBuildEditComponent::ToggleBuildWheel()
{
	if (IsBuildWheelOpen())
	{
		CloseBuildWheel();
	}
	else
	{
		OpenBuildWheel();
	}
}

void UBuildEditComponent::OpenBuildWheel()
{
	if (IsBuildWheelOpen())
	{
		return;
	}

	APlayerController* PC = GetPC();
	if (!PC)
	{
		return;
	}

	AIsekaiVillageCharacter* Char = Cast<AIsekaiVillageCharacter>(GetOwner());
	BuildWheelWidget = CreateWidget<UBuildWheelWidget>(PC);
	if (BuildWheelWidget)
	{
		BuildWheelWidget->InitializeWheel(this, Char);
		BuildWheelWidget->AddToViewport(500);
	}
}

void UBuildEditComponent::CloseBuildWheel()
{
	if (BuildWheelWidget)
	{
		BuildWheelWidget->CloseWheel();
		BuildWheelWidget = nullptr;
	}
}

void UBuildEditComponent::SelectWheelItem(int32 CategoryIndex, int32 ItemIndex)
{
	if (BuildWheelWidget)
	{
		BuildWheelWidget->SetCategory(static_cast<EBuildWheelCategory>(CategoryIndex));
		BuildWheelWidget->SelectItemIndex(ItemIndex);
	}
}
