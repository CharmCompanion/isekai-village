// Copyright Epic Games, Inc. All Rights Reserved.
#include "TownPlot.h"
#include "IsekaiVillageCharacter.h"
#include "VillageRuntime.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Components/ChildActorComponent.h"
#include "GuildMasterDesk.h"
#include "BlacksmithForge.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

AArchitectStake::AArchitectStake()
{
	PrimaryActorTick.bCanEverTick = false;

	InteractBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractBox"));
	InteractBox->InitBoxExtent(FVector(220.0f, 220.0f, 140.0f));
	InteractBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	InteractBox->SetCollisionResponseToAllChannels(ECR_Ignore);
	InteractBox->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	RootComponent = InteractBox;

	MarkerMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("MarkerMesh"));
	MarkerMesh->SetupAttachment(RootComponent);
	MarkerMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	ServiceEntrance = CreateDefaultSubobject<UChildActorComponent>(TEXT("ServiceEntrance"));
	ServiceEntrance->SetupAttachment(RootComponent);
}

void AArchitectStake::BeginPlay()
{
	Super::BeginPlay();
	if (!MarkerMesh->GetStaticMesh())
	{
		if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
		{
			MarkerMesh->SetStaticMesh(Cube);
		}
	}
	InteractBox->OnComponentBeginOverlap.AddDynamic(this, &AArchitectStake::OnBeginOverlap);
	InteractBox->OnComponentEndOverlap.AddDynamic(this, &AArchitectStake::OnEndOverlap);
}

void AArchitectStake::Restyle(const FTownPlot& Plot)
{
	if (Plot.bFlexibleUse && Plot.bBuilt && !ServiceEntrance->GetChildActor())
	{
		if (Plot.Kind == ETownBuilding::Guild) ServiceEntrance->SetChildActorClass(AGuildMasterDesk::StaticClass());
		if (Plot.Kind == ETownBuilding::Smith) ServiceEntrance->SetChildActorClass(ABlacksmithForge::StaticClass());
		// The selected building supplies the exterior. The child supplies its interaction.
		if (AActor* Service = ServiceEntrance->GetChildActor()) Service->SetActorHiddenInGame(true);
	}
	if (Plot.bBuilt && Plot.BuildingClass)
	{
		if (!IsValid(BuiltVisual) && GetWorld())
		{
			FActorSpawnParameters Params;
			Params.Owner = this;
			Params.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
			const FTransform Transform(Plot.BuildingRotation, Plot.Location + Plot.BuildingOffset, Plot.BuildingScale);
			BuiltVisual = GetWorld()->SpawnActor<AActor>(Plot.BuildingClass, Transform, Params);
		}
		MarkerMesh->SetVisibility(!IsValid(BuiltVisual));
		if (IsValid(BuiltVisual)) return;
	}
	MarkerMesh->SetVisibility(true);
	FLinearColor Color(0.45f, 0.42f, 0.36f);
	FVector Scale(0.45f, 0.45f, 1.2f);
	if (Plot.bBuilt)
	{
		Scale = (Plot.Kind == ETownBuilding::Castle) ? FVector(2.4f, 2.4f, 3.2f)
			: (Plot.Kind == ETownBuilding::House) ? FVector(1.2f, 1.0f, 1.4f)
			: FVector(1.6f, 1.4f, 1.8f);
		switch (Plot.Kind)
		{
		case ETownBuilding::House: Color = FLinearColor(0.55f, 0.4f, 0.28f); break;
		case ETownBuilding::Bank: Color = FLinearColor(0.62f, 0.55f, 0.22f); break;
		case ETownBuilding::Bath: Color = FLinearColor(0.35f, 0.55f, 0.62f); break;
		case ETownBuilding::Bell: Color = FLinearColor(0.5f, 0.48f, 0.42f); break;
		case ETownBuilding::Academy: Color = FLinearColor(0.42f, 0.32f, 0.58f); break;
		case ETownBuilding::Manor: Color = FLinearColor(0.48f, 0.28f, 0.28f); break;
		case ETownBuilding::Castle: Color = FLinearColor(0.38f, 0.38f, 0.42f); break;
		default: Color = FLinearColor(0.4f, 0.45f, 0.35f); break;
		}
	}
	MarkerMesh->SetRelativeScale3D(Scale);
	MarkerMesh->SetRelativeLocation(FVector(0.0f, 0.0f, Scale.Z * 50.0f));
	if (UMaterialInterface* Base = MarkerMesh->GetMaterial(0))
	{
		if (UMaterialInstanceDynamic* Dyn = UMaterialInstanceDynamic::Create(Base, this))
		{
			Dyn->SetVectorParameterValue(TEXT("Color"), Color);
			MarkerMesh->SetMaterial(0, Dyn);
		}
	}
}

bool AArchitectStake::TryUse(AIsekaiVillageCharacter* Character)
{
	if (AVillageRuntime* Village = Cast<AVillageRuntime>(GetOwner()))
	{
		const FTownPlot* Plot = Village->FindPlot(PlotId);
		if (Plot && Plot->bFlexibleUse && Plot->bBuilt && Plot->Kind == ETownBuilding::Shop) return Village->TryShopOffer(Character);
		if (Plot && Plot->bBuilt && !Village->bBuildingCatalogOpen && Village->IsServiceBuilding(Plot->Kind)) return Village->UseBuildingService(PlotId, Character);
		return Village->TryBuildPlot(PlotId, Character);
	}
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			return It->TryBuildPlot(PlotId, Character);
		}
	}
	return false;
}

FText AArchitectStake::PromptLine() const
{
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			if (const FTownPlot* Plot = It->FindPlot(PlotId))
			{
				if (Plot->bFlexibleUse && Plot->bBuilt && Plot->Kind == ETownBuilding::Shop) return FText::FromString(TEXT("T Sell Wood | Y Buy Wood | U General Store"));
				if (Plot->bFlexibleUse && Plot->bBuilt && Plot->Kind == ETownBuilding::Guild) return FText::FromString(TEXT("T  Visit the guild desk"));
				if (Plot->bFlexibleUse && Plot->bBuilt && Plot->Kind == ETownBuilding::Smith) return FText::FromString(TEXT("T  Use the forge"));
				if (Plot->bFlexibleUse && !Plot->bBuilt)
				{
					const FTownPlot* Choice=It->SelectedBuilding();
					return FText::FromString(It->bBuildingCatalogOpen && Choice
						? FString::Printf(TEXT("T / Left click  Purchase and place %s here   |   Scroll: building   R: rotate"),*Choice->Title().ToString())
						: TEXT("Unassigned land  |  B or T: choose a building"));
				}
				int32 Wood = Plot->WoodCost;
				int32 Loft = 6;
				if (AIsekaiVillageCharacter* Player = Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(World, 0)))
				{
					const float Cut = FMath::Clamp(Player->SphereBuildSpeed, 0.0f, 50.0f) / 100.0f;
					Wood = FMath::Max(1, FMath::RoundToInt(static_cast<float>(Wood) * (1.0f - Cut)));
					Loft = FMath::Max(1, FMath::RoundToInt(6.0f * (1.0f - Cut)));
				}
				if (Plot->bBuilt && Plot->Kind == ETownBuilding::House && !Plot->bUpgraded)
				{
					return FText::FromString(FString::Printf(TEXT("T  Upgrade %s  %d Wood"), *Plot->Title().ToString(), Loft));
				}
				const FString ServiceHint = It->BuildingQuickHint(Plot->Kind);
				if (Plot->bBuilt && !ServiceHint.IsEmpty())
				{
					return FText::FromString(ServiceHint);
				}
				if (Plot->bBuilt)
				{
					return FText::FromString(FString::Printf(TEXT("%s is standing"), *Plot->Title().ToString()));
				}
				return FText::FromString(FString::Printf(TEXT("T  Raise %s  %dW%s%s"),
					*Plot->Title().ToString(),
					Wood,
					Plot->IronCost > 0 ? *FString::Printf(TEXT(" %dI"), Plot->IronCost) : TEXT(""),
					Plot->CrystalCost > 0 ? *FString::Printf(TEXT(" %dC"), Plot->CrystalCost) : TEXT("")));
			}
		}
	}
	return FText::FromString(TEXT("T  Raise a building"));
}

void AArchitectStake::OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearTownPlot = true;
		Character->NearbyPlot = this;
	}
}

void AArchitectStake::OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		if (Character->NearbyPlot.Get() == this)
		{
			Character->NearbyPlot = nullptr;
			Character->bNearTownPlot = false;
		}
	}
}
