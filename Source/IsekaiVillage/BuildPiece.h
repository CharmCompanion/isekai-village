// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "BuildTypes.h"
#include "BuildPiece.generated.h"

class UProceduralMeshComponent;
class UMaterialInstanceDynamic;

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ABuildPiece : public AActor
{
	GENERATED_BODY()

public:
	ABuildPiece();

	virtual void OnConstruction(const FTransform& Transform) override;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Build")
	TObjectPtr<UProceduralMeshComponent> Mesh;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildPieceType PieceType = EBuildPieceType::Wall;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildOccupancy Occupancy = EBuildOccupancy::Full;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildWallStyle WallStyle = EBuildWallStyle::Straight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FBuildMaterialAssignment MaterialConfig;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	TArray<FBuildCorner> Corners;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float CellSize = 200.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float WallHeight = 280.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float Thickness = 18.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FVector ScaleMultiplier = FVector(1.0f, 1.0f, 1.0f);

	/** 4-bit mask for quadrants [0][0], [1][0], [1][1], [0][1]. Bit 0=1 means quadrant is present. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	uint8 SectionMask = 0x0F;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	bool bPreview = false;

	UFUNCTION(BlueprintCallable, Category = "Build")
	void RebuildMesh();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetOccupancy(EBuildOccupancy InOccupancy);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleOccupancy();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetWallStyle(EBuildWallStyle InStyle);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleWallStyle();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetSectionMask(uint8 NewMask);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void ToggleQuadrant(int32 QuadrantIndex);

	UFUNCTION(BlueprintCallable, Category = "Build")
	bool IsQuadrantActive(int32 QuadrantIndex) const;

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetScaleMultiplier(FVector InScale);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void AdjustScale(float Factor);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleCornerStyle(int32 CornerIndex);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetCornerOffset(int32 CornerIndex, FVector2D Offset);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleExteriorMaterial();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleInteriorMaterial();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleTrimMaterial();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetExteriorTint(FLinearColor InTint);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void SetInteriorTint(FLinearColor InTint);

	UFUNCTION(BlueprintPure, Category = "Build")
	int32 NearestCorner(const FVector& WorldLocation) const;

	UFUNCTION(BlueprintPure, Category = "Build")
	TArray<FVector> GetSnapPoints() const;

	UFUNCTION(BlueprintPure, Category = "Build")
	static FVector SnapWorld(const FVector& World, float InCellSize = 200.0f);

	UFUNCTION(BlueprintPure, Category = "Build")
	static float SnapYaw(float YawDegrees);

	UFUNCTION(BlueprintCallable, Category = "Build")
	static bool FindBestSnap(const ABuildPiece* PlacingPiece, const TArray<ABuildPiece*>& NearbyPieces, float SnapRadius, FVector& OutSnappedLocation, FRotator& OutSnappedRotation);

	void EnsureCorners();

private:
	void OccupiedCells(bool OutCells[2][2]) const;
	void BuildMultiSectionFootprint(float Z0, float Z1);
	void BuildMultiSectionWall();
	void BuildMultiSectionStair();
	void BuildMultiSectionPillar();

	void ApplyMaterialStyling();

	static FLinearColor GetColorForMaterialStyle(EBuildMaterialStyle Style, const FLinearColor& CustomTint);
};
