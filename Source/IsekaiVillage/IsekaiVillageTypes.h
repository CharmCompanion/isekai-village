// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "GolemNeeds.h"
#include "Engine/DataAsset.h"
#include "Engine/Texture2D.h"
#include "Engine/GameInstance.h"
#include "IsekaiVillageTypes.generated.h"

/**
 * 4 Core Elements for Isekai Village (Fire/Water/Earth/Wind only).
 * Light/Dark/Lightning reserved for DLC (Ranger/Summons).
 */
UENUM(BlueprintType)
enum class EElement : uint8
{
	Fire    UMETA(DisplayName = "Fire (Ignis)"),
	Water   UMETA(DisplayName = "Water (Aqua)"),
	Earth   UMETA(DisplayName = "Earth (Terra)"),
	Wind    UMETA(DisplayName = "Wind (Ventus)")
};

/**
 * Targeting Mode for artes.
 */
UENUM(BlueprintType)
enum class ETargetingMode : uint8
{
	ForwardDirectional UMETA(DisplayName = "Forward Directional"),
	GroundPlacement    UMETA(DisplayName = "Ground Placement"),
	SelfTarget         UMETA(DisplayName = "Self Target")
};

/**
 * Arte Data Asset - replaces old GrimoirePage/FSpellCircleConfig.
 * Each arte is a DataAsset with TP cost, element, shape, targeting.
 */
UCLASS(BlueprintType, ClassGroup = "IsekaiVillage")
class ISEKAIVILLAGE_API UArteDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	FText ArteName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	FText Description;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	UTexture2D* Icon;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	EElement Element = EElement::Fire;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	FName Shape = "spear"; // spear, wave, homing, orbit_shield, mine, wall

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	ETargetingMode Targeting = ETargetingMode::ForwardDirectional;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float TP_Cost = 12.0f; // Tap cost

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float TP_HoldCost = 25.0f; // Hold 0.3s cost (spread/fan)

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float Cooldown = 0.0f; // 0 = no CD, shared GCD handled elsewhere

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	int32 MulticastCount = 1; // 1, 2, 3, 5 per FFX tier idea

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	bool bIsHoldArte = false; // true = hold 0.3s for TP_HoldCost version
};

/**
 * Sphere Grid Node - replaces GrimoirePage/GrimoireSlotState.
 * FFX Expert ratio: ~70% stat nodes, ~30% skill nodes.
 */
UENUM(BlueprintType)
enum class ESphereNodeType : uint8
{
	Stat,
	Skill
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FSphereNode
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FName NodeID;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	FText Description;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	ESphereNodeType NodeType = ESphereNodeType::Stat;

	// Stat node values
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 HP_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 TP_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Inventory_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 CarryWeight_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float MoveSpeed_Percent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float BuildSpeed_Percent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Trust_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Gald_Percent = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Attack_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	int32 Magic_Bonus = 0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float Res_Percent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float Attraction_Percent = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Stat")
	float WorkerPace_Percent = 0.0f;

	// Skill node
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Skill")
	TObjectPtr<UArteDataAsset> UnlockArte = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid|Skill")
	FName UnlockAction; // "HireCap+1", "RoomCap+2", etc.

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	TArray<FName> ConnectedNodes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "SphereGrid")
	bool bIsCenterNode = false; // CENTER A/B flip nodes
};

/**
 * Party Reserve - hired adventurers.
 */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FHiredAdventurer
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	FName AdventurerID;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") FGuid GolemId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") FGolemDriveState Drives;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") FName ClassId;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") bool bHasChosenBody=false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") bool bFemaleBody=false;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") int32 WeaponTier=0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") int32 ArmorTier=0;
	UPROPERTY(EditAnywhere, BlueprintReadWrite, SaveGame, Category="Party") int32 TemperLevel=0;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	FText Name;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	int32 Rank = 0; // D=0, C=1, B=2, A=3

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	TArray<TObjectPtr<UArteDataAsset>> KnownArtes;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	bool bInActiveParty = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Party")
	bool bAssignedToRampage = false;
};

UENUM(BlueprintType)
enum class ELocomotionAnimState : uint8
{
	Idle       UMETA(DisplayName = "Idle"),
	Walk       UMETA(DisplayName = "Walk"),
	Run        UMETA(DisplayName = "Run"),
	Jump       UMETA(DisplayName = "Jump"),
	DodgeRoll  UMETA(DisplayName = "Dodge Roll"),
	Action     UMETA(DisplayName = "Action")
};

UENUM(BlueprintType)
enum class EBattleArenaBiome : uint8
{
	Plains    UMETA(DisplayName = "Grasslands / Plains"),
	Forest    UMETA(DisplayName = "Forest / Woods"),
	Desert    UMETA(DisplayName = "Desert / Wasteland"),
	Arena     UMETA(DisplayName = "Standard Arena")
};

UENUM(BlueprintType)
enum class EEncounterAdvantage : uint8
{
	Normal          UMETA(DisplayName = "Normal Encounter"),
	PlayerAdvantage UMETA(DisplayName = "Player Advantage"),
	SurpriseAttack  UMETA(DisplayName = "Surprise Attack / Ambush")
};

class UWorld;

UCLASS(BlueprintType)
class ISEKAIVILLAGE_API UWorldZoneData : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FName ZoneName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FText DisplayName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	TSoftObjectPtr<UWorld> MapToLoad;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FName EntryPointName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FVector EntryOffset = FVector::ZeroVector;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FRotator EntryRotation = FRotator::ZeroRotator;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	bool bIsOverworld = false;

	virtual FPrimaryAssetId GetPrimaryAssetId() const override
	{
		return FPrimaryAssetId("WorldZone", ZoneName);
	}
};

UCLASS()
class ISEKAIVILLAGE_API UOverworldGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FName PendingEntryPoint;

	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FName PendingZoneName;

	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FVector PendingSpawnPosition = FVector::ZeroVector;

	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FRotator PendingSpawnRotation = FRotator::ZeroRotator;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	FVector ReturnOverworldPosition = FVector::ZeroVector;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	FRotator ReturnOverworldRotation = FRotator::ZeroRotator;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	FName EncounteredEnemyParty = NAME_None;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	bool bReturningFromBattle = false;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	bool bLastBattleVictory = false;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	bool bPartyWasWipedOut = false;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	EEncounterAdvantage CurrentEncounterAdvantage = EEncounterAdvantage::Normal;

	UFUNCTION(BlueprintCallable, Category = "Transition")
	void ClearPendingTransition()
	{
		PendingEntryPoint = NAME_None;
		PendingZoneName = NAME_None;
		PendingSpawnPosition = FVector::ZeroVector;
		PendingSpawnRotation = FRotator::ZeroRotator;
	}
};
