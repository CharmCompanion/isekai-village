// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "DayBoardCatalogWidgets.generated.h"

class AVillageRuntime;
class AIsekaiVillageCharacter;
class UVerticalBox;
class UTextBlock;
class UButton;
class UBorder;
class UDayBoardWidget;

UCLASS()
class ISEKAIVILLAGE_API UDayBoardMissionRow : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeRow(UDayBoardWidget* InBoard, int32 InIndex);
	void RefreshRow();
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	UFUNCTION() void HandleComplete();
private:
	UPROPERTY() TObjectPtr<UDayBoardWidget> Board;
	int32 MissionIndex = INDEX_NONE;
	UPROPERTY() TObjectPtr<UTextBlock> Details;
	UPROPERTY() TObjectPtr<UTextBlock> ActionLabel;
	UPROPERTY() TObjectPtr<UButton> ActionButton;
};

UCLASS()
class ISEKAIVILLAGE_API UDayBoardWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeBoard(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer);
	UFUNCTION(BlueprintCallable) bool SubmitMission(int32 Index);
	UFUNCTION(BlueprintCallable) bool FortifyWall();
	UFUNCTION(BlueprintCallable) void RefreshBoard();
	UFUNCTION(BlueprintCallable) void CloseBoard();
	UFUNCTION() void HandleFortifyWall();
	AVillageRuntime* GetVillage() const { return Village; }
	AIsekaiVillageCharacter* GetPlayer() const { return Player; }
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
private:
	UPROPERTY() TObjectPtr<AVillageRuntime> Village;
	UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Player;
	UPROPERTY() TObjectPtr<UTextBlock> HeaderStatus;
	UPROPERTY() TObjectPtr<UTextBlock> EraProgressText;
	UPROPERTY() TObjectPtr<UTextBlock> MessageText;
	UPROPERTY() TObjectPtr<UTextBlock> FortifyLabel;
	UPROPERTY() TObjectPtr<UButton> FortifyButton;
	UPROPERTY() TObjectPtr<UVerticalBox> MissionsBox;
	UPROPERTY() TArray<TObjectPtr<UDayBoardMissionRow>> Rows;
	float RefreshIn = 0.0f;
	bool bOldCursor = false;
	bool bRestoredInput = false;
	void RefreshNumbers();
};

UCLASS()
class ISEKAIVILLAGE_API UBuildingCatalogWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeCatalog(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer);
	UFUNCTION(BlueprintCallable) void RefreshCatalog();
	UFUNCTION(BlueprintCallable) void CloseCatalog();
	UFUNCTION(BlueprintCallable) bool SelectCatalogIndex(int32 Index);
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
private:
	UPROPERTY() TObjectPtr<AVillageRuntime> Village;
	UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Player;
	UPROPERTY() TObjectPtr<UTextBlock> HeaderText;
	UPROPERTY() TObjectPtr<UTextBlock> EraText;
	UPROPERTY() TObjectPtr<UTextBlock> ResourcesText;
	UPROPERTY() TObjectPtr<UTextBlock> SelectedDetailText;
	UPROPERTY() TObjectPtr<UVerticalBox> EntriesBox;
	UPROPERTY() TArray<TObjectPtr<UBorder>> EntryBorders;
	UPROPERTY() TArray<TObjectPtr<UTextBlock>> EntryLabels;
	UPROPERTY() TArray<TObjectPtr<UTextBlock>> EntryCosts;
	int32 CachedSelection = INDEX_NONE;
	int32 CachedTrust = -1;
	int32 CachedBuiltCount = -1;
	float CachedDiscount = -1.0f;
	void BuildEntryList();
	void UpdateEntryHighlights();
};
