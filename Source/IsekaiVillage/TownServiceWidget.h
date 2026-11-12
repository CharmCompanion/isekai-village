// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "VillageTypes.h"
#include "TownServiceWidget.generated.h"

class AVillageRuntime;
class AIsekaiVillageCharacter;
class UVerticalBox;
class UTextBlock;
class UButton;

UCLASS()
class ISEKAIVILLAGE_API UTownServiceActionButton : public UObject
{
	GENERATED_BODY()
public:
	void Init(class UTownServiceWidget* InParent, FName InAction);
	UFUNCTION() void OnClicked();
private:
	UPROPERTY() TObjectPtr<UTownServiceWidget> Parent;
	FName ActionId = NAME_None;
};

UCLASS()
class ISEKAIVILLAGE_API UTownServiceWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeService(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer, ETownBuilding InBuildingKind);
	UFUNCTION(BlueprintCallable) bool TriggerAction(FName ActionId);
	UFUNCTION(BlueprintCallable) void RefreshService();
	UFUNCTION(BlueprintCallable) void CloseService();
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
private:
	UFUNCTION() void OnCloseClicked() { CloseService(); }
	UPROPERTY() TObjectPtr<AVillageRuntime> Village;
	UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Player;
	ETownBuilding BuildingKind = ETownBuilding::Inn;
	UPROPERTY() TObjectPtr<UTextBlock> TitleText;
	UPROPERTY() TObjectPtr<UTextBlock> StandingSummary;
	UPROPERTY() TObjectPtr<UTextBlock> MessageText;
	UPROPERTY() TObjectPtr<UVerticalBox> ActionsBox;
	UPROPERTY() TArray<TObjectPtr<UTownServiceActionButton>> Handlers;
	float RefreshIn = 0.0f;
	bool bOldCursor = false;
	bool bRestoredInput = false;
	void RefreshNumbers();
};
