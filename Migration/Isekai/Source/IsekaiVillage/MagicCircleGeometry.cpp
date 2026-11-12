#include "MagicCircleGeometry.h"

void FMagicCircleGeometry::GetShapeForElement(EElement Element, int32& OutCount, int32& OutSkip)
{
	OutSkip = 1;
	switch (Element)
	{
	case EElement::Fire:  OutCount = 3; break;
	case EElement::Earth: OutCount = 4; break;
	case EElement::Wind:  OutCount = 5; break;
	case EElement::Water: OutCount = 6; break;
	default:              OutCount = 6; break;
	}
}

TArray<FVector2D> FMagicCircleGeometry::BuildPointList(float Radius, int32 Count, float RotationRadians)
{
	TArray<FVector2D> Points;
	if (Count < 2 || Radius <= 0.0f) return Points;

	const float TwoPi = 2.0f * PI;
	for (int32 Index = 0; Index < Count; ++Index)
	{
		const float Angle = (static_cast<float>(Index) / static_cast<float>(Count)) * TwoPi - (PI * 0.5f);
		const float X = FMath::Cos(Angle) * Radius;
		const float Y = FMath::Sin(Angle) * Radius;
		const float CosR = FMath::Cos(RotationRadians);
		const float SinR = FMath::Sin(RotationRadians);
		Points.Add(FVector2D(X * CosR + Y * SinR, X * -SinR + Y * CosR));
	}
	return Points;
}

TArray<TArray<FVector2D>> FMagicCircleGeometry::ConnectPointLoops(const TArray<FVector2D>& Points, int32 Skip)
{
	TArray<TArray<FVector2D>> Loops;
	const int32 N = Points.Num();
	if (N < 2) return Loops;

	int32 Delta = Skip;
	if (Delta <= 0) Delta = 1;
	Delta = Delta % N;
	if (Delta == 0) Delta = 1;

	TArray<bool> Visited;
	Visited.Init(false, N);

	for (int32 Start = 0; Start < N; ++Start)
	{
		if (Visited[Start]) continue;

		TArray<FVector2D> Loop;
		int32 Index = Start;
		int32 Guard = 0;
		do
		{
			Loop.Add(Points[Index]);
			Visited[Index] = true;
			Index = (Index + Delta) % N;
			++Guard;
		} while (Index != Start && Guard <= N);

		if (Loop.Num() >= 2)
		{
			const FVector2D First = Loop[0];
			Loop.Add(First);
			Loops.Add(MoveTemp(Loop));
		}
	}
	return Loops;
}

TArray<FVector2D> FMagicCircleGeometry::BuildRing(float Radius, int32 Segments, float RotationRadians)
{
	TArray<FVector2D> Ring = BuildPointList(Radius, FMath::Max(64, Segments), RotationRadians);
	if (Ring.Num() > 0)
	{
		const FVector2D First = Ring[0];
		Ring.Add(First);
	}
	return Ring;
}

static FMagicCirclePoly MakePoly(TArray<FVector2D> Pts, float HalfWidth, float DrawStart, float DrawEnd, bool bClosed)
{
	FMagicCirclePoly Poly;
	Poly.Points = MoveTemp(Pts);
	Poly.HalfWidth = HalfWidth;
	Poly.DrawStart = DrawStart;
	Poly.DrawEnd = DrawEnd;
	Poly.bClosed = bClosed;
	return Poly;
}

static void AddLoops(TArray<FMagicCirclePoly>& Layers, const TArray<TArray<FVector2D>>& Loops, float HalfWidth, float DrawStart, float DrawEnd)
{
	for (const TArray<FVector2D>& Loop : Loops)
	{
		Layers.Add(MakePoly(Loop, HalfWidth, DrawStart, DrawEnd, true));
	}
}

static void AddLine(TArray<FMagicCirclePoly>& Layers, FVector2D A, FVector2D B, float HalfWidth, float DrawStart, float DrawEnd)
{
	TArray<FVector2D> Pts;
	Pts.Add(A);
	Pts.Add(B);
	Layers.Add(MakePoly(MoveTemp(Pts), HalfWidth, DrawStart, DrawEnd, false));
}

TArray<FMagicCirclePoly> FMagicCircleGeometry::BuildElementCircle(EElement Element, float ChargeRatio)
{
	TArray<FMagicCirclePoly> Layers;
	const float Charge = FMath::Clamp(ChargeRatio, 0.0f, 1.0f);
	if (Charge < 0.02f) return Layers;

	const float OuterR = 50.0f;
	const float Stroke = 1.8f;
	const float CoreStroke = 2.0f;

	int32 Count = 6;
	int32 Skip = 1;
	GetShapeForElement(Element, Count, Skip);

	// Outer ring
	Layers.Add(MakePoly(BuildRing(OuterR, 96, 0.0f), Stroke, 0.00f, 0.30f, true));
	Layers.Add(MakePoly(BuildRing(OuterR * 0.90f, 96, 0.0f), Stroke * 0.75f, 0.08f, 0.40f, true));

	// Element polygon
	const float CoreR = OuterR * 0.62f;
	const TArray<FVector2D> CorePts = BuildPointList(CoreR, Count, 0.0f);
	AddLoops(Layers, ConnectPointLoops(CorePts, 1), CoreStroke, 0.25f, 0.85f);
	if (Skip > 1)
	{
		AddLoops(Layers, ConnectPointLoops(CorePts, Skip), CoreStroke * 0.9f, 0.35f, 0.95f);
	}

	// Center cross
	const float CR = OuterR * 0.12f;
	AddLine(Layers, FVector2D(-CR, -CR), FVector2D(CR, CR), Stroke, 0.55f, 1.00f);
	AddLine(Layers, FVector2D(-CR, CR), FVector2D(CR, -CR), Stroke, 0.55f, 1.00f);

	TArray<FMagicCirclePoly> Visible;
	for (FMagicCirclePoly& Layer : Layers)
	{
		if (Charge >= Layer.DrawStart)
		{
			Visible.Add(MoveTemp(Layer));
		}
	}
	return Visible;
}
