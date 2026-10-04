#pragma once
#include "CoreMinimal.h"
#include "Kismet/BlueprintFunctionLibrary.h"
#include "IslandLandscapeAuthoring.generated.h"
class ALandscape;

/** Editor authoring helpers; the saved map requires no runtime generator. */
UCLASS()
class ISEKAIVILLAGE_API UIslandLandscapeAuthoring : public UBlueprintFunctionLibrary
{
    GENERATED_BODY()
public:
    /** Apply one byte per vertex: zero retains ground, 255 removes it. */
    UFUNCTION(BlueprintCallable, Category="Isekai|Landscape Authoring")
    static bool ApplyIslandVisibility(ALandscape* Landscape, const FString& RawMaskPath);
};
