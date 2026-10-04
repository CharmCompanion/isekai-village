#pragma once

#include "CoreMinimal.h"
#include "IsekaiVillageTypes.h"

struct FMagicCirclePoly
{
	TArray<FVector2D> Points;
	bool bClosed = true;
	float HalfWidth = 0.8f;
	float DrawStart = 0.0f;
	float DrawEnd = 1.0f;
};

struct ISEKAIVILLAGE_API FMagicCircleGeometry
{
	static void GetShapeForElement(EElement Element, int32& OutCount, int32& OutSkip);
	static TArray<FVector2D> BuildPointList(float Radius, int32 Count, float RotationRadians);
	static TArray<TArray<FVector2D>> ConnectPointLoops(const TArray<FVector2D>& Points, int32 Skip);
	static TArray<FVector2D> BuildRing(float Radius, int32 Segments, float RotationRadians);

	// Visual circle only — no spell compile, no fusions, no symbols
	static TArray<FMagicCirclePoly> BuildElementCircle(EElement Element, float ChargeRatio);
};
