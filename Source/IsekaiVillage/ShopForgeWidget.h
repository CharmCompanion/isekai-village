// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "ShopForgeWidget.generated.h"

class AVillageRuntime;
class AIsekaiVillageCharacter;
class ABlacksmithForge;
class UVerticalBox;
class UTextBlock;
class UButton;
class UShopWidget;
class UForgeWidget;

UCLASS()
class ISEKAIVILLAGE_API UShopRow : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeRow(UShopWidget* InShop, FName InItemId);
	void RefreshRow();
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	UFUNCTION() void HandleBuy();
	UFUNCTION() void HandleSell();
private:
	UPROPERTY() TObjectPtr<UShopWidget> Shop;
	FName ItemId = NAME_None;
	UPROPERTY() TObjectPtr<UTextBlock> Details;
	UPROPERTY() TObjectPtr<UTextBlock> BuyLabel;
	UPROPERTY() TObjectPtr<UTextBlock> SellLabel;
	UPROPERTY() TObjectPtr<UButton> BuyButton;
	UPROPERTY() TObjectPtr<UButton> SellButton;
};

UCLASS()
class ISEKAIVILLAGE_API UShopWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeShop(AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer, FName InShopPlot);
	UFUNCTION(BlueprintCallable) bool ExecuteTrade(FName ItemId, bool bBuy);
	UFUNCTION(BlueprintCallable) void RefreshShop();
	UFUNCTION(BlueprintCallable) void CloseShop();
	AVillageRuntime* GetVillage() const { return Village; }
	AIsekaiVillageCharacter* GetPlayer() const { return Player; }
	FName GetShopPlot() const { return ShopPlot; }
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
private:
	UPROPERTY() TObjectPtr<AVillageRuntime> Village;
	UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Player;
	FName ShopPlot = NAME_None;
	UPROPERTY() TObjectPtr<UTextBlock> HeaderStatus;
	UPROPERTY() TObjectPtr<UTextBlock> MessageText;
	UPROPERTY() TObjectPtr<UVerticalBox> CatalogBox;
	UPROPERTY() TArray<TObjectPtr<UShopRow>> Rows;
	float RefreshIn = 0.0f;
	bool bOldCursor = false;
	bool bRestoredInput = false;
	void RefreshNumbers();
};

UCLASS()
class ISEKAIVILLAGE_API UForgeMemberRow : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeRow(UForgeWidget* InForge, FName InAdventurerId);
	void RefreshRow();
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	UFUNCTION() void HandleTemper();
private:
	UPROPERTY() TObjectPtr<UForgeWidget> ForgeWidget;
	FName AdventurerId = NAME_None;
	UPROPERTY() TObjectPtr<UTextBlock> Details;
	UPROPERTY() TObjectPtr<UTextBlock> TemperLabel;
	UPROPERTY() TObjectPtr<UButton> TemperButton;
};

UCLASS()
class ISEKAIVILLAGE_API UForgeWidget : public UUserWidget
{
	GENERATED_BODY()
public:
	void InitializeForge(ABlacksmithForge* InForge, AVillageRuntime* InVillage, AIsekaiVillageCharacter* InPlayer);
	UFUNCTION(BlueprintCallable) bool UpgradeAxe();
	UFUNCTION(BlueprintCallable) bool UpgradePickaxe();
	UFUNCTION(BlueprintCallable) bool ForgeNextGear();
	UFUNCTION(BlueprintCallable) bool TemperAdventurer(FName AdventurerId);
	UFUNCTION(BlueprintCallable) bool ReinforceWalls();
	UFUNCTION(BlueprintCallable) void RefreshForge();
	UFUNCTION(BlueprintCallable) void CloseForge();
	ABlacksmithForge* GetForge() const { return Forge; }
	AVillageRuntime* GetVillage() const { return Village; }
	AIsekaiVillageCharacter* GetPlayer() const { return Player; }
protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;
private:
	UFUNCTION() void OnUpgradeAxe() { UpgradeAxe(); }
	UFUNCTION() void OnUpgradePickaxe() { UpgradePickaxe(); }
	UFUNCTION() void OnForgeGear() { ForgeNextGear(); }
	UFUNCTION() void OnReinforceWall() { ReinforceWalls(); }
	UFUNCTION() void OnCloseClicked() { CloseForge(); }
	UPROPERTY() TObjectPtr<ABlacksmithForge> Forge;
	UPROPERTY() TObjectPtr<AVillageRuntime> Village;
	UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Player;
	UPROPERTY() TObjectPtr<UTextBlock> StockSummary;
	UPROPERTY() TObjectPtr<UTextBlock> ToolsStatus;
	UPROPERTY() TObjectPtr<UTextBlock> MessageText;
	UPROPERTY() TObjectPtr<UButton> AxeButton;
	UPROPERTY() TObjectPtr<UButton> PickButton;
	UPROPERTY() TObjectPtr<UButton> GearButton;
	UPROPERTY() TObjectPtr<UButton> WallButton;
	UPROPERTY() TObjectPtr<UVerticalBox> RosterBox;
	UPROPERTY() TArray<TObjectPtr<UForgeMemberRow>> MemberRows;
	FString ActionFeedback;
	float RefreshIn = 0.0f;
	bool bOldCursor = false;
	bool bRestoredInput = false;
	void RefreshNumbers();
};
