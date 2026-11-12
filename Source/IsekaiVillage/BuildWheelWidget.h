// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "BuildTypes.h"
#include "BuildWheelWidget.generated.h"

class UBuildEditComponent;
class AIsekaiVillageCharacter;
class UVerticalBox;
class UHorizontalBox;
class UTextBlock;
class UButton;
class UBorder;
class UScrollBox;

UENUM(BlueprintType)
enum class EBuildWheelCategory : uint8
{
	Structures,
	Furniture,
	Materials
};

USTRUCT(BlueprintType)
struct FBuildWheelItem
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName Identifier;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName CostRes1 = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 CostAmount1 = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	FName CostRes2 = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 CostAmount2 = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	int32 MinTier = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bUnlocked = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite)
	bool bCanAfford = true;
};

UCLASS()
class ISEKAIVILLAGE_API UBuildWheelItemRow : public UUserWidget
{
	GENERATED_BODY()

public:
	void InitializeRow(class UBuildWheelWidget* InWheel, int32 InIndex);
	void RefreshRow();

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	UFUNCTION() void HandleSelectClicked();

private:
	UPROPERTY() TObjectPtr<class UBuildWheelWidget> Wheel;
	int32 ItemIndex = INDEX_NONE;

	UPROPERTY() TObjectPtr<UTextBlock> TitleText;
	UPROPERTY() TObjectPtr<UTextBlock> CostText;
	UPROPERTY() TObjectPtr<UButton> SelectButton;
	UPROPERTY() TObjectPtr<UTextBlock> SelectLabel;
};

UCLASS()
class ISEKAIVILLAGE_API UBuildWheelWidget : public UUserWidget
{
	GENERATED_BODY()

public:
	UFUNCTION(BlueprintCallable, Category = "BuildWheel")
	void InitializeWheel(UBuildEditComponent* InBuildComp, AIsekaiVillageCharacter* InCharacter);

	UFUNCTION(BlueprintCallable, Category = "BuildWheel")
	void SetCategory(EBuildWheelCategory NewCategory);

	UFUNCTION(BlueprintCallable, Category = "BuildWheel")
	void SelectItemIndex(int32 Index);

	UFUNCTION(BlueprintCallable, Category = "BuildWheel")
	void CloseWheel();

	UFUNCTION(BlueprintCallable, Category = "BuildWheel")
	void RefreshItems();

	UFUNCTION(BlueprintPure, Category = "BuildWheel")
	UBuildEditComponent* GetBuildComp() const { return BuildComp; }

	UFUNCTION(BlueprintPure, Category = "BuildWheel")
	AIsekaiVillageCharacter* GetCharacter() const { return Character; }

	UFUNCTION(BlueprintPure, Category = "BuildWheel")
	TArray<FBuildWheelItem> GetCurrentItems() const { return CurrentItems; }

protected:
	virtual TSharedRef<SWidget> RebuildWidget() override;
	virtual void NativeTick(const FGeometry& Geometry, float DeltaSeconds) override;
	virtual void NativeDestruct() override;
	virtual FReply NativeOnKeyDown(const FGeometry& Geometry, const FKeyEvent& Event) override;

	UFUNCTION() void HandleCategoryStructures();
	UFUNCTION() void HandleCategoryFurniture();
	UFUNCTION() void HandleCategoryMaterials();
	UFUNCTION() void HandleCloseClicked();

private:
	UPROPERTY() TObjectPtr<UBuildEditComponent> BuildComp;
	UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Character;

	EBuildWheelCategory CurrentCategory = EBuildWheelCategory::Structures;
	UPROPERTY() TArray<FBuildWheelItem> CurrentItems;

	UPROPERTY() TObjectPtr<UTextBlock> HeaderTitleText;
	UPROPERTY() TObjectPtr<UTextBlock> TierInfoText;
	UPROPERTY() TObjectPtr<UTextBlock> HelpHintText;
	UPROPERTY() TObjectPtr<UVerticalBox> ItemsListVerticalBox;

	UPROPERTY() TObjectPtr<UButton> TabStructuresBtn;
	UPROPERTY() TObjectPtr<UButton> TabFurnitureBtn;
	UPROPERTY() TObjectPtr<UButton> TabMaterialsBtn;

	UPROPERTY() TArray<TObjectPtr<UBuildWheelItemRow>> ItemRows;

	bool bOldCursor = false;
	bool bRestoredInput = false;

	void PopulateCategoryItems();
};
