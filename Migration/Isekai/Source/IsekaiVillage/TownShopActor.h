// Copyright Epic Games, Inc. All Rights Reserved.
// TownShopActor.h — Interactive General Store, Apothecary, and Inn/Tavern Rest Stop

#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Actor.h"
#include "TownEconomyTypes.h"
#include "TownShopActor.generated.h"

class USphereComponent;
class UStaticMeshComponent;

UENUM(BlueprintType)
enum class ETownShopType : uint8
{
	GeneralStore UMETA(DisplayName = "General Store (Gels, Bottles, Tools)"),
	InnTavern    UMETA(DisplayName = "Inn & Tavern (Rest, Food, Banter)"),
	Apothecary   UMETA(DisplayName = "Apothecary (Potions, Seeds, Remedies)")
};

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnShopInteracted, APawn*, Interactor, ETownShopType, ShopType);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnPartyRestedAtInn, APawn*, Interactor);

UCLASS(Blueprintable, BlueprintType)
class ISEKAIVILLAGE_API ATownShopActor : public AActor
{
	GENERATED_BODY()

public:
	ATownShopActor();

protected:
	virtual void BeginPlay() override;

public:
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USceneComponent* SceneRoot;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	UStaticMeshComponent* ShopCounterMesh;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Components")
	USphereComponent* InteractionTrigger;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shop")
	ETownShopType ShopType = ETownShopType::GeneralStore;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shop")
	FText ShopName = FText::FromString(TEXT("Galdor's Provisions"));

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shop")
	TArray<FShopItem> Catalog;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Shop")
	EBuildingTier ShopTier = EBuildingTier::Tier_1_Rustic;

	UFUNCTION(BlueprintCallable, Category = "Shop")
	void SetShopTier(EBuildingTier NewTier);

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Inn")
	int32 InnRestCost = 60;

	UPROPERTY(BlueprintAssignable, Category = "Shop|Events")
	FOnShopInteracted OnShopInteracted;

	UPROPERTY(BlueprintAssignable, Category = "Shop|Events")
	FOnPartyRestedAtInn OnPartyRestedAtInn;

	UFUNCTION(BlueprintCallable, Category = "Shop")
	void InteractWithPlayer(APawn* PlayerPawn);

	UFUNCTION(BlueprintCallable, Category = "Shop")
	bool BuyItem(FName ItemID, int32 Quantity, UPARAM(ref) int32& PlayerGold, float DiscountMultiplier = 1.0f);

	UFUNCTION(BlueprintCallable, Category = "Shop")
	bool SellItem(FName ItemID, int32 Quantity, UPARAM(ref) int32& PlayerGold);

	/** Rest at Inn: Restores HP/TP and clears negative status */
	UFUNCTION(BlueprintCallable, Category = "Inn")
	bool RestAtInn(APawn* PlayerPawn, UPARAM(ref) int32& PlayerGold);

	UFUNCTION()
	void OnOverlapBegin(UPrimitiveComponent* OverlappedComp, AActor* OtherActor,
		UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult);

private:
	void PopulateDefaultCatalog();
};
