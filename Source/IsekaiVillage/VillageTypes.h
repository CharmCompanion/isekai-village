// Copyright Epic Games, Inc. All Rights Reserved.
#pragma once

#include "CoreMinimal.h"
#include "VillageTypes.generated.h"

class AActor;

UENUM(BlueprintType)
enum class ECitizenTrait : uint8
{
	Brave,
	Cautious,
	Greedy,
	Lazy,
	Earnest,
	Stoic,
	Cheerful
};

UENUM(BlueprintType)
enum class ECitizenStatus : uint8
{
	Visitor,
	Resident,
	Leaving
};

UENUM(BlueprintType)
enum class ECitizenJob : uint8
{
	None,
	Hauler,
	Guard,
	Adventurer,
	Clerk
};

UENUM(BlueprintType)
enum class ECitizenMutex : uint8
{
	Idle,
	Food,
	Gather,
	Train,
	Guard,
	Shop,
	Chapel,
	Sleep,
	Tower,
	Party
};

UENUM(BlueprintType)
enum class ECitizenOrigin : uint8
{
	ElRuhn,
	Yozuan,
	Kelsin,
	Rabaric,
	Vylfod,
	Gosain
};

UENUM(BlueprintType)
enum class EVillageWeather : uint8
{
	Clear,
	Rain,
	Heat,
	Cold,
	Fog,
	Drought
};

UENUM(BlueprintType)
enum class ELootPresence : uint8
{
	PlayerSolo,
	PlayerParty,
	AdventurerRun
};

UENUM(BlueprintType)
enum class EVillagePlace : uint8
{
	House,
	Inn,
	Bakery,
	Farm,
	Guild,
	Training,
	Smith,
	Shop,
	Chapel,
	Warehouse,
	Forest,
	Gate,
	Academy,
	Bank,
	Bath,
	Bell,
	Castle,
	Lake,
	Mine
};

UENUM(BlueprintType)
enum class ESettlementEra : uint8
{
	Homestead,
	Village,
	Town,
	Barony,
	Kingdom
};

UENUM(BlueprintType)
enum class ETownEra : uint8
{
	Village,
	LargeTown,
	Kingdom
};

UENUM(BlueprintType)
enum class ETownBuilding : uint8
{
	House,
	Inn,
	Shop,
	Smith,
	Guild,
	Chapel,
	Training,
	Warehouse,
	Bakery,
	Farm,
	Bank,
	Bath,
	Bell,
	Academy,
	Manor,
	Castle,
	Unassigned
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FTownPlot
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FName Id = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	ETownBuilding Kind = ETownBuilding::House;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	ETownEra Era = ETownEra::Village;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FVector Location = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	bool bBuilt = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	bool bScenery = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	bool bUpgraded = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	int32 WoodCost = 8;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	int32 IronCost = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	int32 CrystalCost = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	int32 BedBonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	TSubclassOf<AActor> BuildingClass;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FRotator BuildingRotation = FRotator::ZeroRotator;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FVector BuildingScale = FVector::OneVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FVector BuildingOffset = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FVector StakeOffset = FVector::ZeroVector;

	// Flexible land has no assigned use until the player places a catalogue building.
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	bool bFlexibleUse = false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	FName CatalogId = NAME_None;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	int32 PlacementTurns = 0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	float BuildableSize = 2400.0f;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Town")
	bool bUniqueBuilding = false;

	int32 WoodPrice(float ConstructionDiscount) const
	{
		if (WoodCost == 0) return 0;
		const float Multiplier = 1.0f - FMath::Clamp(ConstructionDiscount, 0.0f, 50.0f) / 100.0f;
		return FMath::Max(1, FMath::RoundToInt(WoodCost * Multiplier));
	}

	FText Title() const
	{
		if (!DisplayName.IsEmpty()) return DisplayName;
		switch (Kind)
		{
		case ETownBuilding::Unassigned: return FText::FromString(TEXT("Unassigned land"));
		case ETownBuilding::Inn: return FText::FromString(TEXT("Inn"));
		case ETownBuilding::Shop: return FText::FromString(TEXT("Shop"));
		case ETownBuilding::Smith: return FText::FromString(TEXT("Blacksmith"));
		case ETownBuilding::Guild: return FText::FromString(TEXT("Guild"));
		case ETownBuilding::Chapel: return FText::FromString(TEXT("Chapel"));
		case ETownBuilding::Training: return FText::FromString(TEXT("Training yard"));
		case ETownBuilding::Warehouse: return FText::FromString(TEXT("Warehouse"));
		case ETownBuilding::Bakery: return FText::FromString(TEXT("Bakery"));
		case ETownBuilding::Farm: return FText::FromString(TEXT("Farm"));
		case ETownBuilding::Bank: return FText::FromString(TEXT("Bank"));
		case ETownBuilding::Bath: return FText::FromString(TEXT("Bathhouse"));
		case ETownBuilding::Bell: return FText::FromString(TEXT("Bell tower"));
		case ETownBuilding::Academy: return FText::FromString(TEXT("Academy"));
		case ETownBuilding::Manor: return FText::FromString(TEXT("Manor"));
		case ETownBuilding::Castle: return FText::FromString(TEXT("Castle"));
		default: return FText::FromString(TEXT("House"));
		}
	}
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FLootDrop
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	FName ItemId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	int32 BaseQty = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	bool bPlayerSolo = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	bool bPlayerParty = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	bool bAdventurerRun = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Loot")
	bool bBoundUnique = false;

	bool Allows(ELootPresence P) const
	{
		switch (P)
		{
		case ELootPresence::PlayerSolo: return bPlayerSolo;
		case ELootPresence::PlayerParty: return bPlayerParty;
		case ELootPresence::AdventurerRun: return bAdventurerRun;
		default: return false;
		}
	}
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FVillageOffer
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float Food = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float Beds = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float Safety = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float Coin = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float Purpose = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	float Faith = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	int32 FreeBeds = 0;
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FCitizenMind
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	ECitizenTrait Trait = ECitizenTrait::Earnest;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	ECitizenStatus Status = ECitizenStatus::Visitor;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	ECitizenJob Job = ECitizenJob::None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	ECitizenMutex Mutex = ECitizenMutex::Idle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	ECitizenOrigin Origin = ECitizenOrigin::ElRuhn;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Hunger = 40;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Rest = 60;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Safety = 55;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Coin = 30;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Purpose = 40;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Morale = 55;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Rank = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 CombatXP = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 GatherXP = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 TrainHours = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 BondPlayer = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 BondTown = 10;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Debt = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 Wound = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 AgeDays = 20;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 LeaveStreak = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	int32 VisitNightsLeft = 2;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bHasChop = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bHasMine = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bHasAttack = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bHasGuard = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bLastSaleFair = true;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bUnpaid = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	bool bSick = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	FName HomeId = NAME_None;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	TArray<FName> BagIds;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Citizen")
	TArray<int32> BagCounts;

	int32 BagCount(FName Id) const
	{
		for (int32 i = 0; i < BagIds.Num(); ++i)
		{
			if (BagIds[i] == Id) return BagCounts[i];
		}
		return 0;
	}

	void AddBag(FName Id, int32 N)
	{
		if (Id.IsNone() || N <= 0) return;
		for (int32 i = 0; i < BagIds.Num(); ++i)
		{
			if (BagIds[i] == Id) { BagCounts[i] += N; return; }
		}
		BagIds.Add(Id);
		BagCounts.Add(N);
	}

	int32 TakeAll(FName Id)
	{
		for (int32 i = 0; i < BagIds.Num(); ++i)
		{
			if (BagIds[i] == Id)
			{
				const int32 N = BagCounts[i];
				BagIds.RemoveAt(i);
				BagCounts.RemoveAt(i);
				return N;
			}
		}
		return 0;
	}

	int32 TotalBag() const
	{
		int32 S = 0;
		for (int32 C : BagCounts) S += C;
		return S;
	}
};

UENUM(BlueprintType)
enum class EDayMissionKind : uint8
{
	FetchWood,
	RepairWall,
	CookMeals,
	StockStall
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FDayMission
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	EDayMissionKind Kind = EDayMissionKind::FetchWood;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	int32 Need = 5;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	int32 Have = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Village")
	bool bClaimed = false;

	FText Title() const
	{
		switch (Kind)
		{
		case EDayMissionKind::RepairWall: return FText::FromString(TEXT("Repair wall 30%"));
		case EDayMissionKind::CookMeals: return FText::FromString(TEXT("Cook 3"));
		case EDayMissionKind::StockStall: return FText::FromString(TEXT("Stock stall 3"));
		default: return FText::FromString(TEXT("Fetch 5 logs"));
		}
	}

	bool IsReady() const { return !bClaimed && Have >= Need; }
};
