#pragma once
#include "CoreMinimal.h"
#include "GolemNeeds.h"
#include "VillageGolemTypes.generated.h"

UENUM(BlueprintType)
enum class EGolemWorkRoutine : uint8
{
	None,
	Blacksmith_Hammering,
	Innkeeper_Hosting,
	Shopkeeper_Trading,
	Baker_Baking,
	Craftsman_Working,
	Sleeping_In_Bed,
	Alchemist_Brewing,
	Enchanter_Inscribing
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FVillageGolemRecord
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FGuid Id;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName AdventurerId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName ClassId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FGolemDriveState Drives;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FString Name;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName HomePlot;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName WorkPlot;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) bool bFemale = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) bool bHasPosition = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FVector Position = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName Cargo;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 CargoCount = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 SupplyIndex = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) bool bHasSupplyGoal=false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) float GatherSeconds = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) bool bHasWorkInputs = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) EGolemWorkRoutine Routine = EGolemWorkRoutine::None;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName StationPropTag = NAME_None;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FVillageSupplySite
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName Item;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FVector Location = FVector::ZeroVector;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 Stock = 20;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 DailyRestock = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 RestockDay = 1;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName SiteTag = NAME_None;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FVillageShopOffer
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FName ItemId = NAME_None;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString DisplayName;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) FString Category;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 BuyPrice = 2;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 SellPrice = 2;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 DefaultStock = 2;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 DailyTargetStock = 4;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) int32 MinDay = 1;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bRequireSmith = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite) bool bRequireMidTrustOrBank = false;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FVillageShopState
{
	GENERATED_BODY()
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) FName Plot;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 Wood = 4;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 Coins = 40;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) TMap<FName, int32> Stock;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame) int32 RestockDay = 1;
};
