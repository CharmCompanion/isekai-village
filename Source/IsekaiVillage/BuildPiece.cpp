// Copyright Epic Games, Inc. All Rights Reserved.
#include "BuildPiece.h"
#include "ProceduralMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/Engine.h"

ABuildPiece::ABuildPiece()
{
	PrimaryActorTick.bCanEverTick = false;
	Mesh = CreateDefaultSubobject<UProceduralMeshComponent>(TEXT("Mesh"));
	Mesh->bUseAsyncCooking = true;
	RootComponent = Mesh;
	EnsureCorners();
}

void ABuildPiece::OnConstruction(const FTransform& Transform)
{
	Super::OnConstruction(Transform);
	RebuildMesh();
}

void ABuildPiece::EnsureCorners()
{
	if (Corners.Num() != 4)
	{
		Corners.SetNum(4);
	}
}

FVector ABuildPiece::SnapWorld(const FVector& World, float InCellSize)
{
	const float S = FMath::Max(1.0f, InCellSize);
	return FVector(
		FMath::RoundToFloat(World.X / S) * S,
		FMath::RoundToFloat(World.Y / S) * S,
		FMath::RoundToFloat(World.Z / S) * S);
}

float ABuildPiece::SnapYaw(float YawDegrees)
{
	return FMath::RoundToFloat(YawDegrees / 90.0f) * 90.0f;
}

void ABuildPiece::SetOccupancy(EBuildOccupancy InOccupancy)
{
	Occupancy = InOccupancy;
	RebuildMesh();
}

void ABuildPiece::CycleOccupancy()
{
	const uint8 Next = (static_cast<uint8>(Occupancy) + 1) % 4;
	SetOccupancy(static_cast<EBuildOccupancy>(Next));
}

void ABuildPiece::SetWallStyle(EBuildWallStyle InStyle)
{
	WallStyle = InStyle;
	RebuildMesh();
}

void ABuildPiece::CycleWallStyle()
{
	const uint8 Next = (static_cast<uint8>(WallStyle) + 1) % 3;
	SetWallStyle(static_cast<EBuildWallStyle>(Next));
}

void ABuildPiece::SetSectionMask(uint8 NewMask)
{
	SectionMask = NewMask & 0x0F;
	RebuildMesh();
}

void ABuildPiece::ToggleQuadrant(int32 QuadrantIndex)
{
	if (QuadrantIndex >= 0 && QuadrantIndex < 4)
	{
		SectionMask ^= (1 << QuadrantIndex);
		RebuildMesh();
	}
}

bool ABuildPiece::IsQuadrantActive(int32 QuadrantIndex) const
{
	if (QuadrantIndex >= 0 && QuadrantIndex < 4)
	{
		return (SectionMask & (1 << QuadrantIndex)) != 0;
	}
	return false;
}

void ABuildPiece::SetScaleMultiplier(FVector InScale)
{
	ScaleMultiplier = FVector(
		FMath::Clamp(InScale.X, 0.25f, 4.0f),
		FMath::Clamp(InScale.Y, 0.25f, 4.0f),
		FMath::Clamp(InScale.Z, 0.25f, 4.0f));
	RebuildMesh();
}

void ABuildPiece::AdjustScale(float Factor)
{
	SetScaleMultiplier(ScaleMultiplier * Factor);
}

void ABuildPiece::CycleCornerStyle(int32 CornerIndex)
{
	EnsureCorners();
	if (!Corners.IsValidIndex(CornerIndex))
	{
		return;
	}
	const uint8 Next = (static_cast<uint8>(Corners[CornerIndex].Style) + 1) % 3;
	Corners[CornerIndex].Style = static_cast<EBuildCornerStyle>(Next);
	RebuildMesh();
}

void ABuildPiece::SetCornerOffset(int32 CornerIndex, FVector2D Offset)
{
	EnsureCorners();
	if (!Corners.IsValidIndex(CornerIndex))
	{
		return;
	}
	Corners[CornerIndex].Offset = Offset.GetClampedToSize(0.0f, CellSize * 0.45f);
	RebuildMesh();
}

void ABuildPiece::CycleExteriorMaterial()
{
	const uint8 Next = (static_cast<uint8>(MaterialConfig.ExteriorMaterial) + 1) % 9;
	MaterialConfig.ExteriorMaterial = static_cast<EBuildMaterialStyle>(Next);
	RebuildMesh();
}

void ABuildPiece::CycleInteriorMaterial()
{
	const uint8 Next = (static_cast<uint8>(MaterialConfig.InteriorMaterial) + 1) % 9;
	MaterialConfig.InteriorMaterial = static_cast<EBuildMaterialStyle>(Next);
	RebuildMesh();
}

void ABuildPiece::CycleTrimMaterial()
{
	const uint8 Next = (static_cast<uint8>(MaterialConfig.TrimMaterial) + 1) % 9;
	MaterialConfig.TrimMaterial = static_cast<EBuildMaterialStyle>(Next);
	RebuildMesh();
}

void ABuildPiece::SetExteriorTint(FLinearColor InTint)
{
	MaterialConfig.ExteriorTint = InTint;
	RebuildMesh();
}

void ABuildPiece::SetInteriorTint(FLinearColor InTint)
{
	MaterialConfig.InteriorTint = InTint;
	RebuildMesh();
}

int32 ABuildPiece::NearestCorner(const FVector& WorldLocation) const
{
	const FVector Local = GetActorTransform().InverseTransformPosition(WorldLocation);
	const float H = CellSize * ScaleMultiplier.X * 0.5f;
	const FVector2D Pts[4] = {
		FVector2D(-H, -H), FVector2D(H, -H), FVector2D(H, H), FVector2D(-H, H)
	};
	int32 Best = 0;
	float BestDist = MAX_FLT;
	for (int32 i = 0; i < 4; ++i)
	{
		const float D = FVector2D::DistSquared(FVector2D(Local.X, Local.Y), Pts[i]);
		if (D < BestDist)
		{
			BestDist = D;
			Best = i;
		}
	}
	return Best;
}

TArray<FVector> ABuildPiece::GetSnapPoints() const
{
	TArray<FVector> Points;
	const FTransform Xform = GetActorTransform();
	const float HX = CellSize * ScaleMultiplier.X * 0.5f;
	const float HY = CellSize * ScaleMultiplier.Y * 0.5f;
	const float HZ = (PieceType == EBuildPieceType::Wall || PieceType == EBuildPieceType::Doorway || PieceType == EBuildPieceType::Pillar) 
		? (WallHeight * ScaleMultiplier.Z) 
		: (Thickness * ScaleMultiplier.Z);

	// 4 base corners
	Points.Add(Xform.TransformPosition(FVector(-HX, -HY, 0.0f)));
	Points.Add(Xform.TransformPosition(FVector( HX, -HY, 0.0f)));
	Points.Add(Xform.TransformPosition(FVector( HX,  HY, 0.0f)));
	Points.Add(Xform.TransformPosition(FVector(-HX,  HY, 0.0f)));

	// 4 edge midpoints
	Points.Add(Xform.TransformPosition(FVector(0.0f, -HY, 0.0f)));
	Points.Add(Xform.TransformPosition(FVector( HX, 0.0f, 0.0f)));
	Points.Add(Xform.TransformPosition(FVector(0.0f,  HY, 0.0f)));
	Points.Add(Xform.TransformPosition(FVector(-HX, 0.0f, 0.0f)));

	// Top center & top corners for vertical stacking
	Points.Add(Xform.TransformPosition(FVector(0.0f, 0.0f, HZ)));
	Points.Add(Xform.TransformPosition(FVector(-HX, -HY, HZ)));
	Points.Add(Xform.TransformPosition(FVector( HX, -HY, HZ)));
	Points.Add(Xform.TransformPosition(FVector( HX,  HY, HZ)));
	Points.Add(Xform.TransformPosition(FVector(-HX,  HY, HZ)));

	return Points;
}

bool ABuildPiece::FindBestSnap(const ABuildPiece* PlacingPiece, const TArray<ABuildPiece*>& NearbyPieces, float SnapRadius, FVector& OutSnappedLocation, FRotator& OutSnappedRotation)
{
	if (!PlacingPiece)
	{
		return false;
	}

	const TArray<FVector> MySnaps = PlacingPiece->GetSnapPoints();
	float BestDistSq = FMath::Square(SnapRadius);
	bool bFound = false;
	FVector BestDelta = FVector::ZeroVector;

	for (const ABuildPiece* Other : NearbyPieces)
	{
		if (!Other || Other == PlacingPiece)
		{
			continue;
		}
		const TArray<FVector> OtherSnaps = Other->GetSnapPoints();
		for (const FVector& PtMine : MySnaps)
		{
			for (const FVector& PtOther : OtherSnaps)
			{
				const float DSq = FVector::DistSquared(PtMine, PtOther);
				if (DSq < BestDistSq)
				{
					BestDistSq = DSq;
					BestDelta = PtOther - PtMine;
					bFound = true;
				}
			}
		}
	}

	if (bFound)
	{
		OutSnappedLocation = PlacingPiece->GetActorLocation() + BestDelta;
		OutSnappedRotation = PlacingPiece->GetActorRotation();
		return true;
	}
	return false;
}

FLinearColor ABuildPiece::GetColorForMaterialStyle(EBuildMaterialStyle Style, const FLinearColor& CustomTint)
{
	FLinearColor Base;
	switch (Style)
	{
	case EBuildMaterialStyle::WoodPlank:
		Base = FLinearColor(0.55f, 0.38f, 0.22f);
		break;
	case EBuildMaterialStyle::FieldStone:
		Base = FLinearColor(0.48f, 0.48f, 0.46f);
		break;
	case EBuildMaterialStyle::CutStone:
		Base = FLinearColor(0.68f, 0.68f, 0.70f);
		break;
	case EBuildMaterialStyle::Brick:
		Base = FLinearColor(0.62f, 0.28f, 0.20f);
		break;
	case EBuildMaterialStyle::MetalSheet:
		Base = FLinearColor(0.35f, 0.38f, 0.42f);
		break;
	case EBuildMaterialStyle::WhitePlaster:
		Base = FLinearColor(0.92f, 0.90f, 0.85f);
		break;
	case EBuildMaterialStyle::WallpaperStripes:
		Base = FLinearColor(0.85f, 0.82f, 0.72f);
		break;
	case EBuildMaterialStyle::WallpaperFloral:
		Base = FLinearColor(0.78f, 0.85f, 0.75f);
		break;
	case EBuildMaterialStyle::WoodWainscot:
		Base = FLinearColor(0.40f, 0.26f, 0.16f);
		break;
	default:
		Base = FLinearColor::White;
		break;
	}
	return Base * CustomTint;
}

void ABuildPiece::OccupiedCells(bool OutCells[2][2]) const
{
	OutCells[0][0] = OutCells[1][0] = OutCells[0][1] = OutCells[1][1] = false;
	switch (Occupancy)
	{
	case EBuildOccupancy::Full:
		OutCells[0][0] = OutCells[1][0] = OutCells[0][1] = OutCells[1][1] = true;
		break;
	case EBuildOccupancy::Half:
		OutCells[0][0] = OutCells[1][0] = true;
		break;
	case EBuildOccupancy::Quarter:
		OutCells[0][0] = true;
		break;
	case EBuildOccupancy::LShape:
		OutCells[0][0] = OutCells[1][0] = OutCells[0][1] = true;
		break;
	}

	// Apply SectionMask sub-grid quadrant filtering
	if ((SectionMask & (1 << 0)) == 0) OutCells[0][0] = false;
	if ((SectionMask & (1 << 1)) == 0) OutCells[1][0] = false;
	if ((SectionMask & (1 << 2)) == 0) OutCells[1][1] = false;
	if ((SectionMask & (1 << 3)) == 0) OutCells[0][1] = false;
}

void ABuildPiece::BuildMultiSectionFootprint(float Z0, float Z1)
{
	EnsureCorners();
	bool Cells[2][2];
	OccupiedCells(Cells);

	const float ActualCellX = CellSize * ScaleMultiplier.X;
	const float ActualCellY = CellSize * ScaleMultiplier.Y;
	const float HX = ActualCellX * 0.5f;
	const float HY = ActualCellY * 0.5f;
	const float QX = ActualCellX * 0.5f;
	const float QY = ActualCellY * 0.5f;

	// Section 0: Bottom (Exterior underside)
	// Section 1: Top (Interior floor / ceiling)
	// Section 2: Sides (Fascia / trim)
	TArray<FVector> SecV[3];
	TArray<int32> SecT[3];
	TArray<FVector> SecN[3];
	TArray<FVector2D> SecUV[3];
	TArray<FLinearColor> SecCol[3];

	const FLinearColor ExtColor = GetColorForMaterialStyle(MaterialConfig.ExteriorMaterial, MaterialConfig.ExteriorTint);
	const FLinearColor IntColor = GetColorForMaterialStyle(MaterialConfig.InteriorMaterial, MaterialConfig.InteriorTint);
	const FLinearColor TrimColor = GetColorForMaterialStyle(MaterialConfig.TrimMaterial, FLinearColor::White);

	auto CornerOfCell = [&](int32 ix, int32 iy, int32 cx, int32 cy) -> int32
	{
		const float X = (ix == 0 ? -HX : 0.0f) + (cx ? QX : 0.0f);
		const float Y = (iy == 0 ? -HY : 0.0f) + (cy ? QY : 0.0f);
		if (FMath::IsNearlyEqual(X, -HX, 1.0f) && FMath::IsNearlyEqual(Y, -HY, 1.0f)) return 0;
		if (FMath::IsNearlyEqual(X, HX, 1.0f) && FMath::IsNearlyEqual(Y, -HY, 1.0f)) return 1;
		if (FMath::IsNearlyEqual(X, HX, 1.0f) && FMath::IsNearlyEqual(Y, HY, 1.0f)) return 2;
		if (FMath::IsNearlyEqual(X, -HX, 1.0f) && FMath::IsNearlyEqual(Y, HY, 1.0f)) return 3;
		return INDEX_NONE;
	};

	for (int32 ix = 0; ix < 2; ++ix)
	{
		for (int32 iy = 0; iy < 2; ++iy)
		{
			if (!Cells[ix][iy])
			{
				continue;
			}

			FVector2D P[4] = {
				FVector2D(-HX + ix * QX, -HY + iy * QY),
				FVector2D(-HX + (ix + 1) * QX, -HY + iy * QY),
				FVector2D(-HX + (ix + 1) * QX, -HY + (iy + 1) * QY),
				FVector2D(-HX + ix * QX, -HY + (iy + 1) * QY)
			};

			const int32 LocalToTile[4] = {
				CornerOfCell(ix, iy, 0, 0), CornerOfCell(ix, iy, 1, 0),
				CornerOfCell(ix, iy, 1, 1), CornerOfCell(ix, iy, 0, 1)
			};

			for (int32 c = 0; c < 4; ++c)
			{
				if (LocalToTile[c] != INDEX_NONE)
				{
					P[c] += Corners[LocalToTile[c]].Offset * FVector2D(ScaleMultiplier.X, ScaleMultiplier.Y);
				}
			}

			TArray<FVector2D> Poly;
			for (int32 c = 0; c < 4; ++c)
			{
				const int32 TileC = LocalToTile[c];
				const bool bOuter = TileC != INDEX_NONE;
				if (bOuter && Corners[TileC].Style == EBuildCornerStyle::Diagonal)
				{
					const FVector2D Prev = P[(c + 3) % 4];
					const FVector2D Next = P[(c + 1) % 4];
					const float Cut = QX * 0.45f;
					Poly.Add(FMath::Lerp(P[c], Prev, Cut / FMath::Max(1.0f, FVector2D::Distance(P[c], Prev))));
					Poly.Add(FMath::Lerp(P[c], Next, Cut / FMath::Max(1.0f, FVector2D::Distance(P[c], Next))));
				}
				else if (bOuter && Corners[TileC].Style == EBuildCornerStyle::Curved)
				{
					const FVector2D Prev = P[(c + 3) % 4];
					const FVector2D Next = P[(c + 1) % 4];
					const FVector2D A = FMath::Lerp(P[c], Prev, 0.4f);
					const FVector2D B = FMath::Lerp(P[c], Next, 0.4f);
					for (int32 s = 0; s <= 4; ++s)
					{
						const float T = s / 4.0f;
						Poly.Add(FMath::Lerp(A, B, T) + (P[c] - FMath::Lerp(A, B, 0.5f)) * (1.0f - T) * T * 2.0f);
					}
				}
				else
				{
					Poly.Add(P[c]);
				}
			}

			const FVector2D Centroid = [&]()
			{
				FVector2D Sum = FVector2D::ZeroVector;
				for (const FVector2D& Pt : Poly) Sum += Pt;
				return Sum / FMath::Max(1, Poly.Num());
			}();

			// Section 1: Top face (Interior finish)
			const int32 TopBase = SecV[1].Num();
			SecV[1].Add(FVector(Centroid.X, Centroid.Y, Z1));
			SecN[1].Add(FVector::UpVector);
			SecUV[1].Add(FVector2D(Centroid.X, Centroid.Y) / 200.0f);
			SecCol[1].Add(IntColor);
			for (const FVector2D& Pt : Poly)
			{
				SecV[1].Add(FVector(Pt.X, Pt.Y, Z1));
				SecN[1].Add(FVector::UpVector);
				SecUV[1].Add(FVector2D(Pt.X, Pt.Y) / 200.0f);
				SecCol[1].Add(IntColor);
			}
			const int32 N = Poly.Num();
			for (int32 i = 0; i < N; ++i)
			{
				const int32 I0 = TopBase + 1 + i;
				const int32 I1 = TopBase + 1 + ((i + 1) % N);
				SecT[1].Add(TopBase);
				SecT[1].Add(I0);
				SecT[1].Add(I1);
			}

			// Section 0: Bottom face (Exterior finish)
			const int32 BotBase = SecV[0].Num();
			SecV[0].Add(FVector(Centroid.X, Centroid.Y, Z0));
			SecN[0].Add(FVector::DownVector);
			SecUV[0].Add(FVector2D(Centroid.X, Centroid.Y) / 200.0f);
			SecCol[0].Add(ExtColor);
			for (const FVector2D& Pt : Poly)
			{
				SecV[0].Add(FVector(Pt.X, Pt.Y, Z0));
				SecN[0].Add(FVector::DownVector);
				SecUV[0].Add(FVector2D(Pt.X, Pt.Y) / 200.0f);
				SecCol[0].Add(ExtColor);
			}
			for (int32 i = 0; i < N; ++i)
			{
				const int32 I0 = BotBase + 1 + i;
				const int32 I1 = BotBase + 1 + ((i + 1) % N);
				SecT[0].Add(BotBase);
				SecT[0].Add(I1);
				SecT[0].Add(I0);
			}

			// Section 2: Perimeter side walls (Trim)
			for (int32 i = 0; i < N; ++i)
			{
				const int32 J = (i + 1) % N;
				const FVector A0(Poly[i].X, Poly[i].Y, Z0);
				const FVector A1(Poly[J].X, Poly[J].Y, Z0);
				const FVector B1(Poly[J].X, Poly[J].Y, Z1);
				const FVector B0(Poly[i].X, Poly[i].Y, Z1);
				const FVector SideN = FVector::CrossProduct(A1 - A0, B0 - A0).GetSafeNormal();

				const int32 BaseSide = SecV[2].Num();
				SecV[2].Add(A0); SecV[2].Add(A1); SecV[2].Add(B1); SecV[2].Add(B0);
				SecN[2].Add(SideN); SecN[2].Add(SideN); SecN[2].Add(SideN); SecN[2].Add(SideN);
				const float Len = FVector::Distance(A0, A1) / 200.0f;
				SecUV[2].Add(FVector2D(0.0f, Z0 / 200.0f));
				SecUV[2].Add(FVector2D(Len,  Z0 / 200.0f));
				SecUV[2].Add(FVector2D(Len,  Z1 / 200.0f));
				SecUV[2].Add(FVector2D(0.0f, Z1 / 200.0f));
				SecCol[2].Add(TrimColor); SecCol[2].Add(TrimColor); SecCol[2].Add(TrimColor); SecCol[2].Add(TrimColor);

				SecT[2].Add(BaseSide); SecT[2].Add(BaseSide + 1); SecT[2].Add(BaseSide + 2);
				SecT[2].Add(BaseSide); SecT[2].Add(BaseSide + 2); SecT[2].Add(BaseSide + 3);
			}
		}
	}

	for (int32 s = 0; s < 3; ++s)
	{
		if (SecV[s].Num() > 0)
		{
			Mesh->CreateMeshSection_LinearColor(s, SecV[s], SecT[s], SecN[s], SecUV[s], SecCol[s], TArray<FProcMeshTangent>(), true);
		}
	}
}

void ABuildPiece::BuildMultiSectionWall()
{
	const float HX = CellSize * ScaleMultiplier.X * 0.5f;
	const float HZ = WallHeight * ScaleMultiplier.Z;
	const float T = Thickness * 0.5f;

	TArray<FVector> SecV[3];
	TArray<int32> SecT[3];
	TArray<FVector> SecN[3];
	TArray<FVector2D> SecUV[3];
	TArray<FLinearColor> SecCol[3];

	const FLinearColor ExtColor = GetColorForMaterialStyle(MaterialConfig.ExteriorMaterial, MaterialConfig.ExteriorTint);
	const FLinearColor IntColor = GetColorForMaterialStyle(MaterialConfig.InteriorMaterial, MaterialConfig.InteriorTint);
	const FLinearColor TrimColor = GetColorForMaterialStyle(MaterialConfig.TrimMaterial, FLinearColor::White);

	auto AddQuad = [&](int32 SecIdx, const FVector& P0, const FVector& P1, const FVector& P2, const FVector& P3, const FVector& Normal, const FLinearColor& Color)
	{
		const int32 Base = SecV[SecIdx].Num();
		SecV[SecIdx].Add(P0); SecV[SecIdx].Add(P1); SecV[SecIdx].Add(P2); SecV[SecIdx].Add(P3);
		SecN[SecIdx].Add(Normal); SecN[SecIdx].Add(Normal); SecN[SecIdx].Add(Normal); SecN[SecIdx].Add(Normal);
		SecUV[SecIdx].Add(FVector2D(P0.X, P0.Z) / 200.0f);
		SecUV[SecIdx].Add(FVector2D(P1.X, P1.Z) / 200.0f);
		SecUV[SecIdx].Add(FVector2D(P2.X, P2.Z) / 200.0f);
		SecUV[SecIdx].Add(FVector2D(P3.X, P3.Z) / 200.0f);
		SecCol[SecIdx].Add(Color); SecCol[SecIdx].Add(Color); SecCol[SecIdx].Add(Color); SecCol[SecIdx].Add(Color);

		SecT[SecIdx].Add(Base); SecT[SecIdx].Add(Base + 1); SecT[SecIdx].Add(Base + 2);
		SecT[SecIdx].Add(Base); SecT[SecIdx].Add(Base + 2); SecT[SecIdx].Add(Base + 3);
	};

	if (WallStyle == EBuildWallStyle::Diagonal45)
	{
		// Diagonal 45-degree wall spanning (-HX, -HX) to (HX, HX)
		const FVector Dir = FVector(HX * 2.0f, HX * 2.0f, 0.0f).GetSafeNormal();
		const FVector Perpendicular = FVector(-Dir.Y, Dir.X, 0.0f) * T;

		const FVector S0 = FVector(-HX, -HX, 0.0f);
		const FVector S1 = FVector( HX,  HX, 0.0f);

		// Exterior Face (Sec 0)
		AddQuad(0, S0 + Perpendicular, S1 + Perpendicular, S1 + Perpendicular + FVector(0,0,HZ), S0 + Perpendicular + FVector(0,0,HZ), Perpendicular.GetSafeNormal(), ExtColor);
		// Interior Face (Sec 1)
		AddQuad(1, S1 - Perpendicular, S0 - Perpendicular, S0 - Perpendicular + FVector(0,0,HZ), S1 - Perpendicular + FVector(0,0,HZ), -Perpendicular.GetSafeNormal(), IntColor);
		// Trim (Sec 2): Top, Bottom, Ends
		AddQuad(2, S0 + Perpendicular + FVector(0,0,HZ), S1 + Perpendicular + FVector(0,0,HZ), S1 - Perpendicular + FVector(0,0,HZ), S0 - Perpendicular + FVector(0,0,HZ), FVector::UpVector, TrimColor);
		AddQuad(2, S0 - Perpendicular, S1 - Perpendicular, S1 + Perpendicular, S0 + Perpendicular, FVector::DownVector, TrimColor);
		AddQuad(2, S0 - Perpendicular, S0 + Perpendicular, S0 + Perpendicular + FVector(0,0,HZ), S0 - Perpendicular + FVector(0,0,HZ), -Dir, TrimColor);
		AddQuad(2, S1 + Perpendicular, S1 - Perpendicular, S1 - Perpendicular + FVector(0,0,HZ), S1 + Perpendicular + FVector(0,0,HZ),  Dir, TrimColor);
	}
	else if (WallStyle == EBuildWallStyle::CurvedArc)
	{
		// Curved arc wall: 8 segments sweeping a smooth circular arc
		const int32 NumSteps = 8;
		const float Radius = HX * 1.414f;
		const float StartAngle = 0.0f;
		const float EndAngle = PI * 0.5f;

		for (int32 i = 0; i < NumSteps; ++i)
		{
			const float A0 = StartAngle + (EndAngle - StartAngle) * (float(i) / NumSteps);
			const float A1 = StartAngle + (EndAngle - StartAngle) * (float(i + 1) / NumSteps);

			const FVector2D RadDir0(FMath::Cos(A0), FMath::Sin(A0));
			const FVector2D RadDir1(FMath::Cos(A1), FMath::Sin(A1));

			const FVector2D Center(-HX, -HX);
			const FVector2D Outer0 = Center + RadDir0 * (Radius + T);
			const FVector2D Outer1 = Center + RadDir1 * (Radius + T);
			const FVector2D Inner0 = Center + RadDir0 * (Radius - T);
			const FVector2D Inner1 = Center + RadDir1 * (Radius - T);

			// Exterior Face (Sec 0)
			AddQuad(0, FVector(Outer0.X, Outer0.Y, 0.0f), FVector(Outer1.X, Outer1.Y, 0.0f), FVector(Outer1.X, Outer1.Y, HZ), FVector(Outer0.X, Outer0.Y, HZ), FVector(RadDir0.X, RadDir0.Y, 0.0f), ExtColor);
			// Interior Face (Sec 1)
			AddQuad(1, FVector(Inner1.X, Inner1.Y, 0.0f), FVector(Inner0.X, Inner0.Y, 0.0f), FVector(Inner0.X, Inner0.Y, HZ), FVector(Inner1.X, Inner1.Y, HZ), -FVector(RadDir0.X, RadDir0.Y, 0.0f), IntColor);
			// Trim: Top & Bottom
			AddQuad(2, FVector(Outer0.X, Outer0.Y, HZ), FVector(Outer1.X, Outer1.Y, HZ), FVector(Inner1.X, Inner1.Y, HZ), FVector(Inner0.X, Inner0.Y, HZ), FVector::UpVector, TrimColor);
			AddQuad(2, FVector(Outer1.X, Outer1.Y, 0.0f), FVector(Outer0.X, Outer0.Y, 0.0f), FVector(Inner0.X, Inner0.Y, 0.0f), FVector(Inner1.X, Inner1.Y, 0.0f), FVector::DownVector, TrimColor);
		}
	}
	else
	{
		// Straight wall
		const bool bIsDoor = (PieceType == EBuildPieceType::Doorway);
		const float DoorHalfWidth = 45.0f;
		const float DoorHeight = HZ * 0.75f;

		if (bIsDoor)
		{
			// Left wall column
			AddQuad(0, FVector(-HX, -T, 0.0f), FVector(-DoorHalfWidth, -T, 0.0f), FVector(-DoorHalfWidth, -T, HZ), FVector(-HX, -T, HZ), FVector(0, -1, 0), ExtColor);
			AddQuad(1, FVector(-DoorHalfWidth, T, 0.0f), FVector(-HX, T, 0.0f), FVector(-HX, T, HZ), FVector(-DoorHalfWidth, T, HZ), FVector(0, 1, 0), IntColor);

			// Right wall column
			AddQuad(0, FVector(DoorHalfWidth, -T, 0.0f), FVector(HX, -T, 0.0f), FVector(HX, -T, HZ), FVector(DoorHalfWidth, -T, HZ), FVector(0, -1, 0), ExtColor);
			AddQuad(1, FVector(HX, T, 0.0f), FVector(DoorHalfWidth, T, 0.0f), FVector(DoorHalfWidth, T, HZ), FVector(HX, T, HZ), FVector(0, 1, 0), IntColor);

			// Lintel (above doorway)
			AddQuad(0, FVector(-DoorHalfWidth, -T, DoorHeight), FVector(DoorHalfWidth, -T, DoorHeight), FVector(DoorHalfWidth, -T, HZ), FVector(-DoorHalfWidth, -T, HZ), FVector(0, -1, 0), ExtColor);
			AddQuad(1, FVector(DoorHalfWidth, T, DoorHeight), FVector(-DoorHalfWidth, T, DoorHeight), FVector(-DoorHalfWidth, T, HZ), FVector(DoorHalfWidth, T, HZ), FVector(0, 1, 0), IntColor);

			// Doorway frame trim (Sec 2)
			AddQuad(2, FVector(-DoorHalfWidth, -T, 0.0f), FVector(-DoorHalfWidth, T, 0.0f), FVector(-DoorHalfWidth, T, DoorHeight), FVector(-DoorHalfWidth, -T, DoorHeight), FVector(1, 0, 0), TrimColor);
			AddQuad(2, FVector(DoorHalfWidth, T, 0.0f), FVector(DoorHalfWidth, -T, 0.0f), FVector(DoorHalfWidth, -T, DoorHeight), FVector(DoorHalfWidth, T, DoorHeight), FVector(-1, 0, 0), TrimColor);
			AddQuad(2, FVector(-DoorHalfWidth, T, DoorHeight), FVector(DoorHalfWidth, T, DoorHeight), FVector(DoorHalfWidth, -T, DoorHeight), FVector(-DoorHalfWidth, -T, DoorHeight), FVector(0, 0, -1), TrimColor);
		}
		else
		{
			// Full Exterior Face (Sec 0, facing -Y)
			AddQuad(0, FVector(-HX, -T, 0.0f), FVector(HX, -T, 0.0f), FVector(HX, -T, HZ), FVector(-HX, -T, HZ), FVector(0, -1, 0), ExtColor);
			// Full Interior Face (Sec 1, facing +Y)
			AddQuad(1, FVector(HX, T, 0.0f), FVector(-HX, T, 0.0f), FVector(-HX, T, HZ), FVector(HX, T, HZ), FVector(0, 1, 0), IntColor);
		}

		// Top, bottom, left, right edge trim (Sec 2)
		AddQuad(2, FVector(-HX, -T, HZ), FVector(HX, -T, HZ), FVector(HX, T, HZ), FVector(-HX, T, HZ), FVector::UpVector, TrimColor);
		AddQuad(2, FVector(-HX, T, 0.0f), FVector(HX, T, 0.0f), FVector(HX, -T, 0.0f), FVector(-HX, -T, 0.0f), FVector::DownVector, TrimColor);
		AddQuad(2, FVector(-HX, T, 0.0f), FVector(-HX, -T, 0.0f), FVector(-HX, -T, HZ), FVector(-HX, T, HZ), FVector(-1, 0, 0), TrimColor);
		AddQuad(2, FVector(HX, -T, 0.0f), FVector(HX, T, 0.0f), FVector(HX, T, HZ), FVector(HX, -T, HZ), FVector(1, 0, 0), TrimColor);
	}

	for (int32 s = 0; s < 3; ++s)
	{
		if (SecV[s].Num() > 0)
		{
			Mesh->CreateMeshSection_LinearColor(s, SecV[s], SecT[s], SecN[s], SecUV[s], SecCol[s], TArray<FProcMeshTangent>(), true);
		}
	}
}

void ABuildPiece::BuildMultiSectionStair()
{
	const float HX = CellSize * ScaleMultiplier.X * 0.5f;
	const float HY = CellSize * ScaleMultiplier.Y * 0.5f;
	const float HZ = WallHeight * ScaleMultiplier.Z;
	const int32 Steps = 8;
	const float StepDepth = (HY * 2.0f) / Steps;
	const float StepHeight = HZ / Steps;

	TArray<FVector> SecV;
	TArray<int32> SecT;
	TArray<FVector> SecN;
	TArray<FVector2D> SecUV;
	TArray<FLinearColor> SecCol;
	const FLinearColor WoodColor = GetColorForMaterialStyle(MaterialConfig.InteriorMaterial, MaterialConfig.InteriorTint);

	for (int32 s = 0; s < Steps; ++s)
	{
		const float Y0 = -HY + s * StepDepth;
		const float Y1 = Y0 + StepDepth;
		const float Z = (s + 1) * StepHeight;

		// Tread (top of step)
		const int32 Base = SecV.Num();
		SecV.Add(FVector(-HX, Y0, Z)); SecV.Add(FVector(HX, Y0, Z));
		SecV.Add(FVector(HX, Y1, Z));  SecV.Add(FVector(-HX, Y1, Z));
		for (int32 i = 0; i < 4; ++i)
		{
			SecN.Add(FVector::UpVector);
			SecCol.Add(WoodColor);
		}
		SecUV.Add(FVector2D(0, 0)); SecUV.Add(FVector2D(1, 0));
		SecUV.Add(FVector2D(1, 1)); SecUV.Add(FVector2D(0, 1));
		SecT.Add(Base); SecT.Add(Base + 1); SecT.Add(Base + 2);
		SecT.Add(Base); SecT.Add(Base + 2); SecT.Add(Base + 3);

		// Riser (front of step)
		const int32 RiserBase = SecV.Num();
		const float PrevZ = s * StepHeight;
		SecV.Add(FVector(-HX, Y0, PrevZ)); SecV.Add(FVector(HX, Y0, PrevZ));
		SecV.Add(FVector(HX, Y0, Z));     SecV.Add(FVector(-HX, Y0, Z));
		for (int32 i = 0; i < 4; ++i)
		{
			SecN.Add(FVector(0, -1, 0));
			SecCol.Add(WoodColor);
		}
		SecUV.Add(FVector2D(0, 0)); SecUV.Add(FVector2D(1, 0));
		SecUV.Add(FVector2D(1, 1)); SecUV.Add(FVector2D(0, 1));
		SecT.Add(RiserBase); SecT.Add(RiserBase + 1); SecT.Add(RiserBase + 2);
		SecT.Add(RiserBase); SecT.Add(RiserBase + 2); SecT.Add(RiserBase + 3);
	}

	Mesh->CreateMeshSection_LinearColor(0, SecV, SecT, SecN, SecUV, SecCol, TArray<FProcMeshTangent>(), true);
}

void ABuildPiece::BuildMultiSectionPillar()
{
	const float T = Thickness * 1.5f * ScaleMultiplier.X;
	const float HZ = WallHeight * ScaleMultiplier.Z;

	TArray<FVector> SecV;
	TArray<int32> SecT;
	TArray<FVector> SecN;
	TArray<FVector2D> SecUV;
	TArray<FLinearColor> SecCol;
	const FLinearColor PillarColor = GetColorForMaterialStyle(MaterialConfig.TrimMaterial, FLinearColor::White);

	const FVector C[8] = {
		FVector(-T, -T, 0.0f), FVector( T, -T, 0.0f), FVector( T,  T, 0.0f), FVector(-T,  T, 0.0f),
		FVector(-T, -T,  HZ ), FVector( T, -T,  HZ ), FVector( T,  T,  HZ ), FVector(-T,  T,  HZ )
	};
	const int32 Faces[6][4] = {{0,1,2,3},{4,7,6,5},{0,4,5,1},{1,5,6,2},{2,6,7,3},{3,7,4,0}};
	const FVector FaceN[6] = {
		FVector(0,0,-1), FVector(0,0,1), FVector(0,-1,0), FVector(1,0,0), FVector(0,1,0), FVector(-1,0,0)
	};

	for (int32 f = 0; f < 6; ++f)
	{
		const int32 Base = SecV.Num();
		for (int32 i = 0; i < 4; ++i)
		{
			SecV.Add(C[Faces[f][i]]);
			SecN.Add(FaceN[f]);
			SecUV.Add(FVector2D(i == 1 || i == 2, i >= 2));
			SecCol.Add(PillarColor);
		}
		SecT.Add(Base); SecT.Add(Base + 1); SecT.Add(Base + 2);
		SecT.Add(Base); SecT.Add(Base + 2); SecT.Add(Base + 3);
	}

	Mesh->CreateMeshSection_LinearColor(2, SecV, SecT, SecN, SecUV, SecCol, TArray<FProcMeshTangent>(), true);
}

void ABuildPiece::RebuildMesh()
{
	Mesh->ClearAllMeshSections();

	switch (PieceType)
	{
	case EBuildPieceType::Foundation:
		BuildMultiSectionFootprint(-40.0f * ScaleMultiplier.Z, 8.0f * ScaleMultiplier.Z);
		break;
	case EBuildPieceType::Floor:
		BuildMultiSectionFootprint(0.0f, Thickness * ScaleMultiplier.Z);
		break;
	case EBuildPieceType::Roof:
		BuildMultiSectionFootprint((WallHeight - 12.0f) * ScaleMultiplier.Z, (WallHeight + 20.0f) * ScaleMultiplier.Z);
		break;
	case EBuildPieceType::Wall:
	case EBuildPieceType::Doorway:
		BuildMultiSectionWall();
		break;
	case EBuildPieceType::Stair:
		BuildMultiSectionStair();
		break;
	case EBuildPieceType::Pillar:
		BuildMultiSectionPillar();
		break;
	}

	Mesh->SetCollisionEnabled(bPreview ? ECollisionEnabled::NoCollision : ECollisionEnabled::QueryAndPhysics);
}
