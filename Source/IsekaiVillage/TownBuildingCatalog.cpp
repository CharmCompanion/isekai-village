#include "VillageRuntime.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "TownPlot.h"
#include "GameFramework/PlayerController.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Kismet/GameplayStatics.h"

const FTownPlot* AVillageRuntime::SelectedBuilding() const
{
	return BuildingCatalog.IsValidIndex(SelectedBuildingIndex) ? &BuildingCatalog[SelectedBuildingIndex] : nullptr;
}

bool AVillageRuntime::SelectBuilding(FName CatalogId)
{
	for (int32 I=0; I<BuildingCatalog.Num(); ++I)
		if (BuildingCatalog[I].Id == CatalogId)
		{ SelectedBuildingIndex=I; bBuildingCatalogOpen=true; PlacementTurns=0; return true; }
	return false;
}

void AVillageRuntime::ToggleBuildingCatalog()
{
	if (bBuildingCatalogOpen) CancelBuildingPlacement();
	else if (bUseAuthoredPlots && !BuildingCatalog.IsEmpty()) bBuildingCatalogOpen=true;
}

void AVillageRuntime::CycleBuilding(int32 Direction)
{
	if (!bBuildingCatalogOpen || BuildingCatalog.IsEmpty()) return;
	SelectedBuildingIndex=(SelectedBuildingIndex+Direction+BuildingCatalog.Num())%BuildingCatalog.Num();
	PlacementTurns=0;
}

void AVillageRuntime::RotateBuilding() { if (bBuildingCatalogOpen) PlacementTurns=(PlacementTurns+1)%4; }

void AVillageRuntime::CancelBuildingPlacement()
{
	bBuildingCatalogOpen=false;
	if (IsValid(PlacementPreview)) PlacementPreview->Destroy();
	PlacementPreview=nullptr; PlacementPreviewTint=nullptr; PreviewPlotId=NAME_None; PreviewCatalogId=NAME_None;
}

bool AVillageRuntime::ApplyCatalog(FTownPlot& Plot, FName CatalogId, int32 Turns) const
{
	const FTownPlot* Choice=BuildingCatalog.FindByPredicate([CatalogId](const FTownPlot& P){return P.Id==CatalogId;});
	if (!Choice || !Choice->BuildingClass || Choice->WoodCost<0 || Choice->IronCost<0 || Choice->CrystalCost<0 || Choice->BuildableSize>Plot.BuildableSize) return false;
	Plot.CatalogId=CatalogId; Plot.Kind=Choice->Kind; Plot.Era=Choice->Era;
	Plot.DisplayName=Choice->DisplayName; Plot.WoodCost=Choice->WoodCost; Plot.IronCost=Choice->IronCost; Plot.CrystalCost=Choice->CrystalCost; Plot.BedBonus=Choice->BedBonus;
	Plot.BuildingClass=Choice->BuildingClass; Plot.BuildingScale=Choice->BuildingScale;
	Plot.PlacementTurns=((Turns%4)+4)%4;
	Plot.BuildingRotation.Yaw+=Choice->BuildingRotation.Yaw+90.0f*Plot.PlacementTurns;
	Plot.BuildingOffset=Plot.BuildingRotation.RotateVector(Choice->BuildingOffset);
	return true;
}

bool AVillageRuntime::CanAffordBuilding(const FTownPlot& Building, const AIsekaiVillageCharacter* Player) const
{
	if (!Player || !Player->Gather || !EraOpen(Building.Era,Player) || IsUniqueBuildingStanding(Building)) return false;
	const int32 Wood=Building.WoodPrice(EffectiveBuildDiscount(Player));
	return Player->Gather->GetCount(TEXT("Wood"))>=Wood && Player->Gather->GetCount(TEXT("Iron"))>=Building.IronCost && Player->Gather->GetCount(TEXT("Crystal"))>=Building.CrystalCost;
}

bool AVillageRuntime::IsUniqueBuildingStanding(const FTownPlot& Building) const
{
	const FName Id=Building.CatalogId.IsNone()?Building.Id:Building.CatalogId;
	const FTownPlot* Definition=BuildingCatalog.FindByPredicate([Id](const FTownPlot& Option){ return Option.Id==Id; });
	return Definition && Definition->bUniqueBuilding && Plots.ContainsByPredicate([Id](const FTownPlot& Plot){ return Plot.bBuilt && Plot.CatalogId==Id; });
}

FName AVillageRuntime::TargetPlot(const AIsekaiVillageCharacter* Player) const
{
	if (!Player || !GetWorld()) return NAME_None;
	if (const APlayerController* PC=Cast<APlayerController>(Player->GetController()))
	{
		FVector Eye; FRotator Direction; PC->GetPlayerViewPoint(Eye,Direction);
		FCollisionQueryParams Params; Params.AddIgnoredActor(Player);
		if (IsValid(PlacementPreview)) Params.AddIgnoredActor(PlacementPreview);
		FHitResult Hit;
		if (GetWorld()->LineTraceSingleByChannel(Hit,Eye,Eye+Direction.Vector()*15000.0f,ECC_Visibility,Params))
		{
			for (const FTownPlot& Plot:Plots)
			{
				if (!Plot.bFlexibleUse || Plot.bScenery) continue;
				const FVector Local=Plot.BuildingRotation.UnrotateVector(Hit.ImpactPoint-Plot.Location);
				if (FMath::Abs(Local.X)<Plot.BuildableSize*.5f && FMath::Abs(Local.Y)<Plot.BuildableSize*.5f && FMath::Abs(Local.Z)<3000.0f) return Plot.Id;
			}
		}
	}
	if (IsValid(Player->NearbyPlot) && Player->NearbyPlot->GetOwner()==this) return Player->NearbyPlot->PlotId;
	return NAME_None;
}

void AVillageRuntime::UpdatePlacementPreview()
{
	if (!bBuildingCatalogOpen) return;
	const AIsekaiVillageCharacter* Player=Cast<AIsekaiVillageCharacter>(UGameplayStatics::GetPlayerCharacter(this,0));
	const FTownPlot* Plot=FindPlot(TargetPlot(Player)); const FTownPlot* Choice=SelectedBuilding();
	if (!Plot || Plot->bBuilt || !Plot->bFlexibleUse || !Choice)
	{
		if (IsValid(PlacementPreview)) PlacementPreview->Destroy();
		PlacementPreview=nullptr; return;
	}
	FTownPlot Proposal=*Plot;
	if (!ApplyCatalog(Proposal,Choice->Id,PlacementTurns)) return;
	if (!IsValid(PlacementPreview) || PreviewPlotId!=Plot->Id || PreviewCatalogId!=Choice->Id || PreviewTurns!=PlacementTurns)
	{
		if (IsValid(PlacementPreview)) PlacementPreview->Destroy();
		FActorSpawnParameters Params; Params.Owner=this; Params.ObjectFlags|=RF_Transient;
		Params.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		const FTransform Transform(Proposal.BuildingRotation, Proposal.Location+Proposal.BuildingOffset, Proposal.BuildingScale);
		PlacementPreview=GetWorld()->SpawnActor<AActor>(Proposal.BuildingClass,Transform,Params);
		if (!PlacementPreview) return;
		PlacementPreview->SetActorEnableCollision(false); PlacementPreview->SetActorTickEnabled(false);
		PlacementPreviewTint=PlacementPreviewMaterial?UMaterialInstanceDynamic::Create(PlacementPreviewMaterial,this):nullptr;
		TArray<UStaticMeshComponent*> Components; PlacementPreview->GetComponents(Components);
		for (UStaticMeshComponent* Component:Components)
		{
			Component->SetCollisionEnabled(ECollisionEnabled::NoCollision); Component->SetCastShadow(false);
			if (PlacementPreviewTint)
				for (int32 I=0; I<Component->GetNumMaterials(); ++I) Component->SetMaterial(I,PlacementPreviewTint);
		}
		PreviewPlotId=Plot->Id; PreviewCatalogId=Choice->Id; PreviewTurns=PlacementTurns;
	}
	const FLinearColor Tint=CanAffordBuilding(Proposal,Player)?FLinearColor(.08f,.8f,.55f):FLinearColor(.95f,.18f,.08f);
	if (PlacementPreviewTint) PlacementPreviewTint->SetVectorParameterValue(TEXT("PreviewColor"),Tint);
}
