// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "GameFramework/HUD.h"
#include "IsekaiVillageHUD.generated.h"

class USphereGridWidget;

UCLASS()
class ISEKAIVILLAGE_API AIsekaiVillageHUD : public AHUD
{
	GENERATED_BODY()

public:
	AIsekaiVillageHUD();
	virtual void BeginPlay() override;
	virtual void DrawHUD() override;
	virtual void NotifyHitBoxClick(FName BoxName) override;

	UFUNCTION(BlueprintCallable, Category = "SphereGrid")
	void ToggleSphereGrid();

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TSubclassOf<USphereGridWidget> SphereGridWidgetClass;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "SphereGrid")
	bool bSphereGridVisible = false;

protected:
	UPROPERTY()
	TObjectPtr<USphereGridWidget> SphereGridWidget;

private:
	void DrawTPBar(class AIsekaiVillageCharacter* Character);
	void DrawArteSlots(class AIsekaiVillageCharacter* Character);
	void DrawElementIndicator(class AIsekaiVillageCharacter* Character);
	void DrawFocusModeFlash(class AIsekaiVillageCharacter* Character);
	void DrawSphereGrid(class AIsekaiVillageCharacter* Character);
	void SetSphereGridInput(bool bOpen);
};
