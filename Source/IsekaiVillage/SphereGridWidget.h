// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "SphereGridWidget.generated.h"

class UButton;
class UTextBlock;
class UCanvasPanel;
class USphereGridWidget;

UCLASS()
class ISEKAIVILLAGE_API USphereNodeClickTarget : public UObject
{
	GENERATED_BODY()

public:
	FName NodeID;
	TWeakObjectPtr<USphereGridWidget> Owner;

	UFUNCTION()
	void HandleClicked();
};

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API USphereGridWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	virtual void NativeOnInitialized() override;
	virtual void NativeConstruct() override;
	virtual void NativeTick(const FGeometry& MyGeometry, float InDeltaTime) override;

	UFUNCTION(BlueprintCallable, Category = "SphereGrid")
	void RebuildGrid();

	void HandleNodeClicked(FName NodeID);

protected:
	UPROPERTY()
	TObjectPtr<UCanvasPanel> RootCanvas;

	UPROPERTY()
	TObjectPtr<UTextBlock> HeaderText;

	UPROPERTY()
	TObjectPtr<UTextBlock> StatusText;

	UPROPERTY()
	TObjectPtr<UButton> FlipButton;

	UPROPERTY()
	TArray<TObjectPtr<UButton>> NodeButtons;

	UPROPERTY()
	TArray<TObjectPtr<UTextBlock>> NodeLabels;

	UPROPERTY()
	TArray<TObjectPtr<USphereNodeClickTarget>> ClickTargets;

	UFUNCTION()
	void HandleFlipClicked();

	void EnsureLayout();
	void RefreshVisuals();
};
