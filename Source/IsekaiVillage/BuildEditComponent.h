// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "BuildTypes.h"
#include "BuildEditComponent.generated.h"

class ABuildPiece;
class ALinchpinProp;
class APlayerController;
class AIsekaiVillageCharacter;

UCLASS(ClassGroup = (Custom), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API UBuildEditComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	UBuildEditComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	bool bBuildMode = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	bool bPlacingProps = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FName CurrentPropTag = TEXT("Anvil");

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	TArray<FName> AvailablePropTags;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildPieceType CurrentType = EBuildPieceType::Wall;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildOccupancy CurrentOccupancy = EBuildOccupancy::Full;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	EBuildWallStyle CurrentWallStyle = EBuildWallStyle::Straight;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FBuildMaterialAssignment CurrentMaterials;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	FVector CurrentScale = FVector(1.0f, 1.0f, 1.0f);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	bool bFreeformPlacement = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	float PlacementYaw = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Build")
	TObjectPtr<ABuildPiece> SelectedPiece;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Build")
	TObjectPtr<ALinchpinProp> SelectedProp;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Build")
	int32 ActiveCorner = 0;

	UFUNCTION(BlueprintCallable, Category = "Build")
	void ToggleBuildMode();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void TogglePropPlacementMode();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CyclePropType(int32 Direction);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void PlaceOrSelect();

	UFUNCTION(BlueprintCallable, Category = "Build")
	bool TryCraftAndPlaceProp(AIsekaiVillageCharacter* Character, const FVector& Location, const FRotator& Rotation);

	UFUNCTION(BlueprintPure, Category = "Build")
	static bool GetPropCraftCost(FName PropTag, FName& OutRes1, int32& OutCost1, FName& OutRes2, int32& OutCost2);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleOccupancy();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CyclePieceType(int32 Direction);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleWallStyle();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleExteriorMaterial();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleInteriorMaterial();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleTrimMaterial();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void RotatePlacement(float DeltaDegrees = 90.0f);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void AdjustScale(float Factor);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void ToggleQuadrant(int32 QuadrantIndex);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void ToggleFreeform();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void CycleCornerStyle();

	UFUNCTION(BlueprintCallable, Category = "Build")
	void NudgeActiveCorner(float Amount);

	UFUNCTION(BlueprintCallable, Category = "Build")
	void RemoveSelected();

	/** Shift-click toggles one piece or prop in the copy selection. */
	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	void ToggleSelectionActor(AActor* Actor);

	/** Replace the selection with every piece and prop near the cursor. */
	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	int32 GrabUnderCursor(float Radius = 1800.0f);

	/** Write the current selection to Saved/BuildTemplates and arm it for stamping. */
	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	FString SaveSelectionAsTemplate();

	/** Save under an explicit file name. Empty string on failure. */
	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	FString SaveTemplateNamed(const FString& Name);

	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	void ClearTemplateSelection();

	/** Step through saved templates. The slot before the first is "none". */
	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	void CycleArmedTemplate(int32 Direction);

	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	void ReloadBuildTemplates();

	UFUNCTION(BlueprintPure, Category = "Build|Template")
	bool IsTemplateArmed() const { return LoadedTemplates.IsValidIndex(ArmedTemplateIndex); }

	UFUNCTION(BlueprintPure, Category = "Build|Template")
	FString GetArmedTemplateName() const;

	UFUNCTION(BlueprintPure, Category = "Build|Template")
	int32 GetTemplateSelectionCount() const;

	/** Spawn the named template. Yaw rotates the whole building around Origin. */
	UFUNCTION(BlueprintCallable, Category = "Build|Template")
	int32 StampTemplateNamed(const FString& Name, const FVector& Origin, float Yaw);

	UPROPERTY(Transient)
	TObjectPtr<class UBuildWheelWidget> BuildWheelWidget;

	UFUNCTION(BlueprintPure, Category = "Build")
	int32 GetUnlockedTier() const;

	UFUNCTION(BlueprintPure, Category = "Build")
	bool IsPropUnlocked(FName PropTag) const;

	UFUNCTION(BlueprintCallable, Category = "Build")
	void RefreshUnlockedProps();

	UFUNCTION(BlueprintCallable, Category = "Build|UI")
	void ToggleBuildWheel();

	UFUNCTION(BlueprintCallable, Category = "Build|UI")
	void OpenBuildWheel();

	UFUNCTION(BlueprintCallable, Category = "Build|UI")
	void CloseBuildWheel();

	UFUNCTION(BlueprintPure, Category = "Build|UI")
	bool IsBuildWheelOpen() const { return BuildWheelWidget != nullptr; }

	UFUNCTION(BlueprintCallable, Category = "Build|UI")
	void SelectWheelItem(int32 CategoryIndex, int32 ItemIndex);

	FVector SnapFurnitureLocation(const FVector& WorldLoc, FRotator& InOutRotation) const;

	UPROPERTY()
	TArray<TObjectPtr<ABuildPiece>> TemplateSelectionPieces;

	UPROPERTY()
	TArray<TObjectPtr<ALinchpinProp>> TemplateSelectionProps;

	UPROPERTY()
	TArray<FBuildTemplate> LoadedTemplates;

	int32 ArmedTemplateIndex = -1;

private:
	bool TraceCursor(FHitResult& OutHit) const;
	FVector SnapLocation(const FVector& World) const;
	APlayerController* GetPC() const;
	FBuildTemplate CaptureSelection(const FString& Name) const;
	void DrawTemplateSelection() const;
};
