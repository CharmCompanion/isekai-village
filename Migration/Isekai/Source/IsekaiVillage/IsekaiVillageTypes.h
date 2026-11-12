// Copyright Epic Games, Inc. All Rights Reserved.

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataTable.h"
#include "Engine/LevelStreaming.h"
#include "Engine/DataAsset.h"
#include "Engine/GameInstance.h"
#include "IsekaiVillageTypes.generated.h"

class UWorld;

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
	Wind    UMETA(DisplayName = "Wind (Ventus)"),
	Holy    UMETA(DisplayName = "Holy / Light (Lux)"),
	Dark    UMETA(DisplayName = "Dark / Chaos (Tenebrae)")
};

/**
 * Demon taxonomy for the "Adventurers vs Demons" game theme.
 */
UENUM(BlueprintType)
enum class EDemonCategory : uint8
{
	None       UMETA(DisplayName = "Non-Demon / Beast"),
	LesserImp  UMETA(DisplayName = "Lesser Winged Imp"),
	Brute      UMETA(DisplayName = "Hell Brute / Fiend"),
	Hellhound  UMETA(DisplayName = "Demon Hellhound"),
	Wraith     UMETA(DisplayName = "Dark Wraith / Sorcerer"),
	ArchDemon  UMETA(DisplayName = "Arch-Demon / Demon Lord"),
	Mimic      UMETA(DisplayName = "Demon Mimic Trap")
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
 * Biome types for location-specific battle arena maps.
 */
UENUM(BlueprintType)
enum class EBattleArenaBiome : uint8
{
	Plains    UMETA(DisplayName = "Grasslands / Plains"),
	Forest    UMETA(DisplayName = "Forest / Woods"),
	Desert    UMETA(DisplayName = "Desert / Wasteland"),
	Arena     UMETA(DisplayName = "Standard Arena")
};

/**
 * Encounter Advantage states for symbol encounters.
 */
UENUM(BlueprintType)
enum class EEncounterAdvantage : uint8
{
	Normal          UMETA(DisplayName = "Normal Encounter"),
	PlayerAdvantage UMETA(DisplayName = "Player Advantage"),
	SurpriseAttack  UMETA(DisplayName = "Surprise Attack / Ambush")
};

/**
 * Farming tools for village life sim.
 */
UENUM(BlueprintType)
enum class EFarmingTool : uint8
{
	None         UMETA(DisplayName = "None / Hands"),
	Hoe          UMETA(DisplayName = "Hoe (Tilling)"),
	Seeds        UMETA(DisplayName = "Seeds (Planting)"),
	WateringCan  UMETA(DisplayName = "Watering Can"),
	Basket       UMETA(DisplayName = "Basket / Box (Harvesting & Carrying)")
};

/**
 * NPC Archetypes & Routine activities in the village.
 */
UENUM(BlueprintType)
enum class ENPCArchetype : uint8
{
	Villager    UMETA(DisplayName = "Villager / Townsfolk"),
	Farmer      UMETA(DisplayName = "Farmer"),
	Guard       UMETA(DisplayName = "Village Guard"),
	Elder       UMETA(DisplayName = "Village Elder"),
	Shopkeeper  UMETA(DisplayName = "Merchant / Shopkeeper")
};

/**
 * Player combat weapon styles.
 */
UENUM(BlueprintType)
enum class EWeaponStyle : uint8
{
	SwordAndShield UMETA(DisplayName = "Sword & Shield"),
	Greatsword     UMETA(DisplayName = "Greatsword"),
	DualWield      UMETA(DisplayName = "Dual Wield"),
	MagicStaff     UMETA(DisplayName = "Magic Staff / Spells"),
	Unarmed        UMETA(DisplayName = "Brawler / Unarmed")
};

/**
 * Enemy archetypes with specialized combat AI & animation sets.
 */
UENUM(BlueprintType)
enum class EEnemyArchetype : uint8
{
	MeleeBeast        UMETA(DisplayName = "Wild Beast / Mutant"),
	ZombieUndead      UMETA(DisplayName = "Undead / Zombie"),
	SwordShieldKnight UMETA(DisplayName = "Armored Knight / Guard"),
	MageCultist       UMETA(DisplayName = "Cultist Spellcaster"),
	AxeBerserker      UMETA(DisplayName = "Axe Berserker")
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

/**
 * Tales of Arte Tiers (Base -> Arcane -> Altered -> Mystic Hi-Ougi).
 */
UENUM(BlueprintType)
enum class EArteTier : uint8
{
	Base     UMETA(DisplayName = "Base Arte"),
	Arcane   UMETA(DisplayName = "Arcane Arte"),
	Altered  UMETA(DisplayName = "Altered Arte"),
	Mystic   UMETA(DisplayName = "Mystic Arte (Hi-Ougi)")
};

/**
 * Execution zone for the arte (Ground, Air, or Both).
 */
UENUM(BlueprintType)
enum class EArteTargetZone : uint8
{
	GroundOnly  UMETA(DisplayName = "Ground Only"),
	AerialOnly  UMETA(DisplayName = "Aerial Only"),
	Any         UMETA(DisplayName = "Ground & Aerial")
};

/**
 * Directional input modifier for arte palette mapping.
 */
UENUM(BlueprintType)
enum class EArteDirection : uint8
{
	Neutral UMETA(DisplayName = "Neutral"),
	Up      UMETA(DisplayName = "Up / Forward"),
	Down    UMETA(DisplayName = "Down / Backward"),
	Side    UMETA(DisplayName = "Side / Left-Right")
};

class UAnimSequence;

/**
 * Arte Data Asset - Definitive Tales of Arte specification.
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
	EArteTier ArteTier = EArteTier::Base;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	EArteTargetZone TargetZone = EArteTargetZone::Any;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	EElement Element = EElement::Fire;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	FName Shape = "spear"; // spear, wave, homing, orbit_shield, mine, wall

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	ETargetingMode Targeting = ETargetingMode::ForwardDirectional;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float TP_Cost = 12.0f; // Technical Point cost

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float AG_Cost = 1.0f; // Arte Gauge / Chain Capacity cost (1-3 pips)

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float TP_HoldCost = 25.0f; // Hold 0.3s cost (spread/fan)

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float Cooldown = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float DamageMultiplier = 1.6f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	bool bLaunchesEnemy = false; // Knocks enemy airborne for aerial juggles

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	bool bDivesDown = false; // Air-to-ground dive slam finisher

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	bool bKnocksDown = false; // Sweeps enemy to ground

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	TObjectPtr<UAnimSequence> AnimationToPlay = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	float AnimationPlayRate = 1.4f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	int32 MulticastCount = 1;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	bool bIsHoldArte = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Arte")
	bool bIsMagicCast = false;
};

/**
 * 16-Slot Arte Palette Mapping (Ground + Aerial + Shoulder Modifier).
 */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FArteSlotMapping
{
	GENERATED_BODY()

	// Primary Ground Palette
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundPrimary")
	TObjectPtr<UArteDataAsset> GroundNeutral = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundPrimary")
	TObjectPtr<UArteDataAsset> GroundUp = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundPrimary")
	TObjectPtr<UArteDataAsset> GroundDown = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundPrimary")
	TObjectPtr<UArteDataAsset> GroundSide = nullptr;

	// Secondary Ground Palette (with Modifier Key held, e.g. L1/LB)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundSecondary")
	TObjectPtr<UArteDataAsset> ModGroundNeutral = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundSecondary")
	TObjectPtr<UArteDataAsset> ModGroundUp = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundSecondary")
	TObjectPtr<UArteDataAsset> ModGroundDown = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|GroundSecondary")
	TObjectPtr<UArteDataAsset> ModGroundSide = nullptr;

	// Primary Aerial Palette
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialPrimary")
	TObjectPtr<UArteDataAsset> AerialNeutral = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialPrimary")
	TObjectPtr<UArteDataAsset> AerialUp = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialPrimary")
	TObjectPtr<UArteDataAsset> AerialDown = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialPrimary")
	TObjectPtr<UArteDataAsset> AerialSide = nullptr;

	// Secondary Aerial Palette (with Modifier Key held)
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialSecondary")
	TObjectPtr<UArteDataAsset> ModAerialNeutral = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialSecondary")
	TObjectPtr<UArteDataAsset> ModAerialUp = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialSecondary")
	TObjectPtr<UArteDataAsset> ModAerialDown = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "ArtePalette|AerialSecondary")
	TObjectPtr<UArteDataAsset> ModAerialSide = nullptr;
};

/**
 * Iron Stance (Super Armor) & Break System for Enemies.
 */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FIronStanceConfig
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IronStance")
	int32 MaxArmorHits = 4;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "IronStance")
	int32 CurrentArmorHits = 4;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "IronStance")
	bool bIsBroken = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "IronStance")
	float BreakDuration = 3.5f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "IronStance")
	float BreakTimer = 0.0f;
};

/**
 * Hit-Stop Impact Freeze Configuration.
 */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FHitStopConfig
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "HitStop")
	float HitStopDuration = 0.045f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "HitStop")
	float HitStopTimeDilation = 0.05f;
};

/**
 * Overlimit State for Tales Characters.
 */
USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FOverlimitState
{
	GENERATED_BODY()

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	float CurrentGauge = 0.0f; // 0.0 to 100.0

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Overlimit")
	float MaxGauge = 100.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	int32 OverlimitLevel = 0; // 0 = off, 1-4 = active

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	float ActiveTimer = 0.0f;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Overlimit")
	float MaxDuration = 12.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Overlimit")
	bool bIsActive = false;
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

// ─────────────────────────────────────────────────────────────
// Overworld / World Zone System (Tales of Symphonia style)
// ─────────────────────────────────────────────────────────────

/**
 * Defines a world zone — a map that can be loaded via transition.
 * Create these as DataAssets in Content/IsekaiVillage/Zones/.
 */
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

	/** TargetPoint name to spawn at when entering this zone. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FName EntryPointName;

	/** Positional offset from the entry point. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FVector EntryOffset = FVector::ZeroVector;

	/** Facing direction on entry. */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	FRotator EntryRotation = FRotator::ZeroRotator;

	/** Is this zone an overworld (scaled-down world map)? */
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Zone")
	bool bIsOverworld = false;

	virtual FPrimaryAssetId GetPrimaryAssetId() const override
	{
		return FPrimaryAssetId("WorldZone", ZoneName);
	}
};

/**
 * Lightweight GameInstance that persists data across map transitions.
 * Stores the last entry point so the new map can position the player.
 */
UCLASS()
class ISEKAIVILLAGE_API UOverworldGameInstance : public UGameInstance
{
	GENERATED_BODY()

public:
	/** TargetPoint name to spawn at in the destination map. */
	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FName PendingEntryPoint;

	/** Zone we are transitioning into. */
	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FName PendingZoneName;

	/** World position to spawn at (used when no TargetPoint found). */
	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FVector PendingSpawnPosition = FVector::ZeroVector;

	/** Facing direction on spawn. */
	UPROPERTY(BlueprintReadWrite, Category = "Transition")
	FRotator PendingSpawnRotation = FRotator::ZeroRotator;

	// ── Battle Encounter State ──
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
	TArray<FName> PendingIncapacitatedHeroIDs;

	UPROPERTY(BlueprintReadWrite, Category = "Battle")
	EEncounterAdvantage CurrentEncounterAdvantage = EEncounterAdvantage::Normal;


	/** Clear pending data after spawn. */
	UFUNCTION(BlueprintCallable, Category = "Transition")
	void ClearPendingTransition()
	{
		PendingEntryPoint = NAME_None;
		PendingZoneName = NAME_None;
		PendingSpawnPosition = FVector::ZeroVector;
		PendingSpawnRotation = FRotator::ZeroRotator;
	}
};