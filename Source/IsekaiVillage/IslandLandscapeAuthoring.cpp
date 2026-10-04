#include "IslandLandscapeAuthoring.h"
#include "Landscape.h"
#if WITH_EDITOR
#include "LandscapeEdit.h"
#include "LandscapeEditLayer.h"
#include "LandscapeInfo.h"
#include "LandscapeLayerInfoObject.h"
#include "Misc/FileHelper.h"
#endif

bool UIslandLandscapeAuthoring::ApplyIslandVisibility(ALandscape* Landscape, const FString& RawMaskPath)
{
#if WITH_EDITOR
    if (!Landscape || !Landscape->GetLandscapeInfo() || !Landscape->GetEditLayer(0)) return false;
    ULandscapeInfo* Info = Landscape->GetLandscapeInfo();
    int32 X1, Y1, X2, Y2;
    TArray<uint8> Bytes;
    if (!Info->GetLandscapeExtent(X1,Y1,X2,Y2) || !FFileHelper::LoadFileToArray(Bytes,*RawMaskPath)
        || Bytes.Num() != (X2-X1+1)*(Y2-Y1+1)) return false;
    auto* Visibility = ALandscapeProxy::VisibilityLayer;
    Landscape->Modify();
    Landscape->UpdateTargetLayer(Visibility->GetLayerName(), FLandscapeTargetLayerSettings(Visibility));
    Info->UpdateLayerInfoMap(Landscape, true);
    {
        FLandscapeEditDataInterface Edit(Info);
        Edit.SetEditLayer(Landscape->GetEditLayer(0)->GetGuid());
        // Use the engine's visibility layer identity, not an ordinary paint layer.
        Edit.SetAlphaData(Visibility,X1,Y1,X2,Y2,Bytes.GetData(),0,ELandscapeLayerPaintingRestriction::None);
        Edit.Flush();
    }
    Landscape->ForceLayersFullUpdate();
    Landscape->RecreateCollisionComponents();
    Landscape->MarkPackageDirty();
    return true;
#else
    return false;
#endif
}
