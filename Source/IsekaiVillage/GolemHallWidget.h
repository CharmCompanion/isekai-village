#pragma once
#include "CoreMinimal.h"
#include "Blueprint/UserWidget.h"
#include "GolemHallWidget.generated.h"
class AVillageRuntime;
class AIsekaiVillageCharacter;
class UVerticalBox;
class UTextBlock;
class UComboBoxString;
class UEditableTextBox;
class UButton;
class UGolemHallWidget;

UCLASS()
class ISEKAIVILLAGE_API UGolemHallRow : public UUserWidget
{
 GENERATED_BODY()
public:
 void InitializeRow(UGolemHallWidget* InHall,FName InId);
 void RefreshRow();
protected:
 virtual TSharedRef<SWidget> RebuildWidget() override;
 UFUNCTION() void ToggleActive();
private:
 UPROPERTY() TObjectPtr<UGolemHallWidget> Hall;
 FName Id;
 UPROPERTY() TObjectPtr<UTextBlock> Details;
 UPROPERTY() TObjectPtr<UTextBlock> ButtonText;
 UPROPERTY() TObjectPtr<UButton> ActiveButton;
};

UCLASS()
class ISEKAIVILLAGE_API UGolemHallWidget : public UUserWidget
{
 GENERATED_BODY()
public:
 void InitializeHall(AVillageRuntime* InVillage,AIsekaiVillageCharacter* Player);
 UFUNCTION(BlueprintCallable) void RefreshHall();
 UFUNCTION(BlueprintCallable) bool SubmitCreation(FName ClassId,bool bFemale,FText Name);
 UFUNCTION(BlueprintCallable) bool ChooseActive(FName Id,bool bActive);
 UFUNCTION(BlueprintCallable) void CloseHall();
 AVillageRuntime* GetVillage() const{return Village;}
 AIsekaiVillageCharacter* GetCommander() const{return Commander;}
protected:
 virtual TSharedRef<SWidget> RebuildWidget() override;
 virtual void NativeTick(const FGeometry& Geometry,float DeltaSeconds) override;
 virtual void NativeDestruct() override;
 virtual FReply NativeOnKeyDown(const FGeometry& Geometry,const FKeyEvent& Event) override;
 UFUNCTION() void CreateSelected();
 UFUNCTION() void CollectSupplies();
private:
 UPROPERTY() TObjectPtr<AVillageRuntime> Village;
 UPROPERTY() TObjectPtr<AIsekaiVillageCharacter> Commander;
 UPROPERTY() TObjectPtr<UTextBlock> Resources;
 UPROPERTY() TObjectPtr<UTextBlock> Message;
 UPROPERTY() TObjectPtr<UTextBlock> PartySummary;
 UPROPERTY() TObjectPtr<UVerticalBox> RosterBox;
 UPROPERTY() TObjectPtr<UComboBoxString> ClassChoice;
 UPROPERTY() TObjectPtr<UComboBoxString> BodyChoice;
 UPROPERTY() TObjectPtr<UEditableTextBox> NameEntry;
 UPROPERTY() TObjectPtr<UButton> CreateButton;
 UPROPERTY() TArray<TObjectPtr<UGolemHallRow>> Rows;
 float RefreshIn=0;
 bool bOldCursor=false,bRestoredInput=false;
 void RestoreInput();
 void RefreshNumbers();
};
