// Copyright Epic Games, Inc. All Rights Reserved.
// BattleGameMode.cpp — LMBS Arena Combat GameMode (Enemy Spawning, Victory & Defeat Flow, Overworld Return)

#include "BattleGameMode.h"
#include "BattleHUD.h"
#include "BattleCharacter.h"
#include "BattleEnemy.h"
#include "MeshTerrainBuilder.h"
#include "SkillGridComponent.h"
#include "TitleManagerComponent.h"
#include "AdventurersGuildComponent.h"
#include "PartyCombatManager.h"
#include "IsekaiVillageTypes.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"
#include "Engine/DirectionalLight.h"
#include "Engine/SkyLight.h"
#include "Components/SkyLightComponent.h"
#include "Components/DirectionalLightComponent.h"
#include "Components/SkyAtmosphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMeshActor.h"
#include "Engine/StaticMesh.h"
#include "Engine/PostProcessVolume.h"
#include "EngineUtils.h"
#include "TimerManager.h"

ABattleGameMode::ABattleGameMode()
{
	DefaultPawnClass = ABattleCharacter::StaticClass();
	HUDClass = ABattleHUD::StaticClass();
}

void ABattleGameMode::BeginPlay()
{
	Super::BeginPlay();

	EnsureArenaEnvironment();

	// Position player in arena facing forward
	if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		PlayerPawn->TeleportTo(FVector(0.0f, -600.0f, 110.0f), FRotator(0.0f, 90.0f, 0.0f), false, true);
	}

	BattleStartTime = GetWorld() ? GetWorld()->GetTimeSeconds() : 0.0f;

	SpawnEnemyParty();
	SpawnPartyCompanions();

	// Check Encounter Advantage from Overworld
	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		BattleEncounterAdvantage = GI->CurrentEncounterAdvantage;
	}

	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
		{
			if (BattleEncounterAdvantage == EEncounterAdvantage::PlayerAdvantage)
			{
				HUD->ShowBattleStartBanner(
					FText::FromString(TEXT("★ PLAYER ADVANTAGE! ★")),
					FText::FromString(TEXT("Enemies are dazed & broken! Immediate Arte offensive!")),
					3.5f
				);
			}
			else if (BattleEncounterAdvantage == EEncounterAdvantage::SurpriseAttack)
			{
				HUD->ShowBattleStartBanner(
					FText::FromString(TEXT("⚠️ SURPRISE ATTACK! ⚠️")),
					FText::FromString(TEXT("Ambushed from behind! Offense temporarily disrupted!")),
					3.5f
				);
			}
			else
			{
				HUD->ShowBattleStartBanner(
					FText::FromString(TEXT("LMBS Combat Arena")),
					FText::FromString(TEXT("Defeat all hostile targets to return to the Overworld!")),
					3.0f
				);
			}
		}
	}

	// Apply encounter advantage effects
	if (BattleEncounterAdvantage == EEncounterAdvantage::PlayerAdvantage)
	{
		// All enemies begin in Broken / Stagger state
		for (TActorIterator<ABattleEnemy> It(GetWorld()); It; ++It)
		{
			if (ABattleEnemy* Enemy = *It)
			{
				Enemy->IronStance.bIsBroken = true;
				Enemy->IronStance.CurrentArmorHits = 0;
				Enemy->IronStance.BreakTimer = 4.0f;
				Enemy->CombatState = EBattleEnemyState::Broken;
			}
		}

		// Player party starts with full AG and 50% Overlimit
		if (ABattleCharacter* BattleChar = Cast<ABattleCharacter>(UGameplayStatics::GetPlayerPawn(this, 0)))
		{
			BattleChar->CurrentAG = BattleChar->MaxAG;
			BattleChar->OverlimitState.CurrentGauge = 50.0f;
		}
	}
	else if (BattleEncounterAdvantage == EEncounterAdvantage::SurpriseAttack)
	{
		// Player starts empty AG
		if (ABattleCharacter* BattleChar = Cast<ABattleCharacter>(UGameplayStatics::GetPlayerPawn(this, 0)))
		{
			BattleChar->CurrentAG = 0.0f;
		}
	}
}

void ABattleGameMode::EnsureArenaEnvironment()
{
	UWorld* World = GetWorld();
	if (!World) return;

	// 1. Ensure Directional Sunlight
	bool bHasSun = false;
	for (TActorIterator<ADirectionalLight> It(World); It; ++It)
	{
		bHasSun = true;
		break;
	}
	if (!bHasSun)
	{
		ADirectionalLight* Sun = World->SpawnActor<ADirectionalLight>(ADirectionalLight::StaticClass(), FVector(0.0f, 0.0f, 1000.0f), FRotator(-40.0f, -45.0f, 0.0f));
		if (Sun && Sun->GetComponent())
		{
			Sun->GetComponent()->SetIntensity(3.5f);
			Sun->GetComponent()->SetLightColor(FLinearColor(1.0f, 0.95f, 0.85f));
			Sun->GetComponent()->SetAtmosphereSunLight(true);
		}
	}

	// 2. Ensure SkyLight
	bool bHasSkyLight = false;
	for (TActorIterator<ASkyLight> It(World); It; ++It)
	{
		bHasSkyLight = true;
		break;
	}
	if (!bHasSkyLight)
	{
		ASkyLight* SkyLight = World->SpawnActor<ASkyLight>(ASkyLight::StaticClass(), FVector(0.0f, 0.0f, 500.0f), FRotator::ZeroRotator);
		if (SkyLight && SkyLight->GetLightComponent())
		{
			SkyLight->GetLightComponent()->SetIntensity(1.5f);
			SkyLight->GetLightComponent()->bRealTimeCapture = true;
		}
	}

	// 3. Ensure Sky Atmosphere
	bool bHasAtmosphere = false;
	for (TActorIterator<ASkyAtmosphere> It(World); It; ++It)
	{
		bHasAtmosphere = true;
		break;
	}
	if (!bHasAtmosphere)
	{
		World->SpawnActor<ASkyAtmosphere>(ASkyAtmosphere::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator);
	}

	// 4. Ensure PostProcess Volume with Bounded Exposure (Prevents Lumen cached lighting clipping)
	bool bHasPostProcess = false;
	for (TActorIterator<APostProcessVolume> It(World); It; ++It)
	{
		APostProcessVolume* PP = *It;
		if (PP && PP->bUnbound)
		{
			bHasPostProcess = true;
			PP->Settings.bOverride_AutoExposureMethod = true;
			PP->Settings.AutoExposureMethod = EAutoExposureMethod::AEM_Histogram;
			PP->Settings.bOverride_AutoExposureMinBrightness = true;
			PP->Settings.AutoExposureMinBrightness = 0.5f;
			PP->Settings.bOverride_AutoExposureMaxBrightness = true;
			PP->Settings.AutoExposureMaxBrightness = 3.0f;
			break;
		}
	}
	if (!bHasPostProcess)
	{
		FActorSpawnParameters SpawnParams;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		if (APostProcessVolume* PP = World->SpawnActor<APostProcessVolume>(APostProcessVolume::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams))
		{
			PP->bUnbound = true;
			PP->Settings.bOverride_AutoExposureMethod = true;
			PP->Settings.AutoExposureMethod = EAutoExposureMethod::AEM_Histogram;
			PP->Settings.bOverride_AutoExposureMinBrightness = true;
			PP->Settings.AutoExposureMinBrightness = 0.5f;
			PP->Settings.bOverride_AutoExposureMaxBrightness = true;
			PP->Settings.AutoExposureMaxBrightness = 3.0f;
		}
	}

// 5. Ensure Arena Terrain (themed stylized mesh terrain per biome) & Boundary Ring
	UStaticMesh* CylinderMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (!CylinderMesh)
	{
		CylinderMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	}

	if (CylinderMesh)
	{
		SpawnArenaTerrain();
		SpawnBoundaryRing();
	}
}

ETerrainBiome ABattleGameMode::GetArenaBiomeFromMap()
{
	UWorld* World = GetWorld();
	FString MapName = World ? World->GetMapName() : FString();
	MapName.ToLowerInline();

	if (MapName.Contains(TEXT("plains")))
	{
		return ETerrainBiome::Plains;
	}
	if (MapName.Contains(TEXT("forest")))
	{
		return ETerrainBiome::Forest;
	}
	if (MapName.Contains(TEXT("desert")))
	{
		return ETerrainBiome::Desert;
	}
	if (MapName.Contains(TEXT("snow")))
	{
		return ETerrainBiome::Snow;
	}

	// Fall back on the encounter party ID (the area the enemy was encountered)
	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		FName PartyID = GI->EncounteredEnemyParty;
		if (PartyID == FName("Undead_Crypt") || PartyID == FName("Zombies") || PartyID == FName("Graveyard"))
		{
			return ETerrainBiome::Cave;
		}
		if (PartyID == FName("Forest_Pack") || PartyID == FName("Forest"))
		{
			return ETerrainBiome::Forest;
		}
		if (PartyID == FName("Desert_Band") || PartyID == FName("Desert"))
		{
			return ETerrainBiome::Desert;
		}
	}

	return ETerrainBiome::Plains;
}

void ABattleGameMode::SpawnArenaTerrain()
{
	UWorld* World = GetWorld();
	if (!World) return;

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	// Flat combat pad spanning the original 3600-unit-radius stage
	AMeshTerrainBuilder* Terrain = World->SpawnActor<AMeshTerrainBuilder>(AMeshTerrainBuilder::StaticClass(), FVector::ZeroVector, FRotator::ZeroRotator, SpawnParams);
	if (Terrain)
	{
		Terrain->Biome = GetArenaBiomeFromMap();
		Terrain->bFlatArena = true;
		Terrain->TerrainSize = 7600.0f;
		Terrain->TerrainResolution = 128;
		Terrain->HeightOffset = 0.0f;
		Terrain->HeightScale = 0.0f;
		Terrain->bGenerateWater = false;
		Terrain->bLoadFromR16File = false;
		Terrain->GenerateTerrain();
	}

	SpawnBiomeDecor(Terrain);
}

void ABattleGameMode::SpawnBoundaryRing()
{
	UWorld* World = GetWorld();
	if (!World) return;

	UStaticMesh* CylinderMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder"));
	if (!CylinderMesh)
	{
		CylinderMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	}
	if (!CylinderMesh) return;

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	// 24 themed boundary wall pillars around the perimeter forming a solid barrier
	const float ArenaRadius = 1750.0f;
	const int32 PillarCount = 24;
	for (int32 i = 0; i < PillarCount; ++i)
	{
		float Angle = (float)i * (2.0f * PI / (float)PillarCount);
		FVector PillarLoc = FVector(FMath::Cos(Angle) * ArenaRadius, FMath::Sin(Angle) * ArenaRadius, 180.0f);
		AStaticMeshActor* Pillar = World->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), PillarLoc, FRotator::ZeroRotator, SpawnParams);
		if (Pillar)
		{
			Pillar->GetStaticMeshComponent()->SetStaticMesh(CylinderMesh);
			Pillar->GetStaticMeshComponent()->SetWorldScale3D(FVector(2.4f, 2.4f, 4.5f));
			Pillar->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
			Pillar->GetStaticMeshComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
			Pillar->SetMobility(EComponentMobility::Static);
		}
	}
}

void ABattleGameMode::SpawnBiomeDecor(AMeshTerrainBuilder* Terrain)
{
	UWorld* World = GetWorld();
	if (!World) return;

	UStaticMesh* RockMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube"));
	UStaticMesh* DecorMesh = RockMesh;

	// Prefer SoStylized stylized rocks where available
	if (Terrain)
	{
		switch (Terrain->Biome)
		{
		case ETerrainBiome::Forest:
			DecorMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/SoStylized/Environment/Rocks/Classic/SM_BoulderClassic1.SM_BoulderClassic1"));
			break;
		case ETerrainBiome::Desert:
			DecorMesh = LoadObject<UStaticMesh>(nullptr, TEXT("/Game/SoStylized/Environment/Rocks/Desert/SM_RockDesert_CliffA01.SM_RockDesert_CliffA01"));
			break;
		default:
			break;
		}
		if (!DecorMesh)
		{
			DecorMesh = RockMesh;
		}
	}

	// Scatter rough stylized rock clusters around the arena rim (kept off the combat pad)
	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AlwaysSpawn;

	for (int32 i = 0; i < 14; ++i)
	{
		float Angle = (float)i * (2.0f * PI / 14.0f) + PI * 0.06f;
		float Radius = 2050.0f + (i % 3) * 90.0f;
		FVector Loc(FMath::Cos(Angle) * Radius, FMath::Sin(Angle) * Radius, 0.0f);

		AStaticMeshActor* Rock = World->SpawnActor<AStaticMeshActor>(AStaticMeshActor::StaticClass(), Loc, FRotator(0.0f, FMath::FRandRange(0.0f, 360.0f), 0.0f), SpawnParams);
		if (Rock)
		{
			Rock->GetStaticMeshComponent()->SetStaticMesh(DecorMesh);
			float S = FMath::FRandRange(0.8f, 1.9f);
			Rock->GetStaticMeshComponent()->SetWorldScale3D(FVector(S, S, S * FMath::FRandRange(0.6f, 1.1f)));
			Rock->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));
			Rock->GetStaticMeshComponent()->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
			Rock->SetMobility(EComponentMobility::Static);
		}
	}
}

void ABattleGameMode::SpawnEnemyParty()
{
	UWorld* World = GetWorld();
	if (!World) return;

	UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance());
	FName PartyID = GI ? GI->EncounteredEnemyParty : FName("DefaultEncounter");

	// Spawn facing south toward player
	struct FEnemySpawnConfig
	{
		FVector Position;
		FText Name;
		float MaxHP;
		float AttackPower;
		int32 Exp;
		int32 Gald;
		EElement Weakness;
		EBattleEnemyRole Role;
	};

	TArray<FEnemySpawnConfig> EnemiesToSpawn;

	if (PartyID == FName("Undead_Crypt") || PartyID == FName("Zombies") || PartyID == FName("Graveyard"))
	{
		EnemiesToSpawn.Add({ FVector(0.0f, 320.0f, 110.0f), FText::FromString(TEXT("Cursed Zombie")), 340.0f, 20.0f, 70, 50, EElement::Fire, EBattleEnemyRole::Zombie });
		EnemiesToSpawn.Add({ FVector(-320.0f, 520.0f, 110.0f), FText::FromString(TEXT("Ghoul Shambler")), 290.0f, 18.0f, 55, 35, EElement::Fire, EBattleEnemyRole::Zombie });
		EnemiesToSpawn.Add({ FVector(320.0f, 620.0f, 110.0f), FText::FromString(TEXT("Necromancer Acolyte")), 210.0f, 22.0f, 65, 45, EElement::Wind, EBattleEnemyRole::Mage });
	}
	else if (PartyID == FName("Bandit_Camp") || PartyID == FName("Castle") || PartyID == FName("Knights"))
	{
		EnemiesToSpawn.Add({ FVector(-200.0f, 360.0f, 110.0f), FText::FromString(TEXT("Rogue Knight")), 380.0f, 22.0f, 80, 60, EElement::Earth, EBattleEnemyRole::Knight });
		EnemiesToSpawn.Add({ FVector(200.0f, 360.0f, 110.0f), FText::FromString(TEXT("Axe Berserker")), 320.0f, 26.0f, 75, 55, EElement::Water, EBattleEnemyRole::Berserker });
	}
	else if (PartyID == FName("Forest_Pack") || PartyID == FName("Forest"))
	{
		EnemiesToSpawn.Add({ FVector(0.0f, 320.0f, 110.0f), FText::FromString(TEXT("Forest Treant")), 320.0f, 20.0f, 65, 45, EElement::Fire, EBattleEnemyRole::Melee });
		EnemiesToSpawn.Add({ FVector(320.0f, 620.0f, 110.0f), FText::FromString(TEXT("Forest Sorcerer")), 200.0f, 22.0f, 60, 40, EElement::Wind, EBattleEnemyRole::Mage });
	}
	else if (PartyID == FName("Desert_Band") || PartyID == FName("Desert"))
	{
		EnemiesToSpawn.Add({ FVector(0.0f, 320.0f, 110.0f), FText::FromString(TEXT("Dune Basilisk")), 350.0f, 22.0f, 75, 55, EElement::Water, EBattleEnemyRole::Melee });
		EnemiesToSpawn.Add({ FVector(-320.0f, 620.0f, 110.0f), FText::FromString(TEXT("Desert Mystic")), 210.0f, 24.0f, 70, 50, EElement::Water, EBattleEnemyRole::Mage });
	}
	else
	{
		// Default Plains Encounter: 1 Melee Beast + 1 Ranged Mage + 1 Knight / Undead
		EnemiesToSpawn.Add({ FVector(0.0f, 320.0f, 110.0f), FText::FromString(TEXT("Dire Wolf Alpha")), 280.0f, 20.0f, 55, 35, EElement::Fire, EBattleEnemyRole::Melee });
		EnemiesToSpawn.Add({ FVector(300.0f, 620.0f, 110.0f), FText::FromString(TEXT("Dire Shaman")), 190.0f, 22.0f, 50, 30, EElement::Wind, EBattleEnemyRole::Mage });
		EnemiesToSpawn.Add({ FVector(-280.0f, 500.0f, 110.0f), FText::FromString(TEXT("Rogue Guard")), 320.0f, 18.0f, 60, 40, EElement::Earth, EBattleEnemyRole::Knight });
	}


	LivingEnemiesCount = 0;
	TotalExpGained = 0;
	TotalGaldGained = 0;

	for (const FEnemySpawnConfig& Config : EnemiesToSpawn)
	{
		FRotator SpawnRot = FRotator(0.0f, -90.0f, 0.0f); // Face south toward player

		FActorSpawnParameters SpawnParams;
		SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

		if (ABattleEnemy* NewEnemy = World->SpawnActor<ABattleEnemy>(ABattleEnemy::StaticClass(), Config.Position, SpawnRot, SpawnParams))
		{
			NewEnemy->SetEnemyRole(Config.Role);
			NewEnemy->EnemyName = Config.Name;
			NewEnemy->MaxHP = Config.MaxHP;
			NewEnemy->CurrentHP = Config.MaxHP;
			NewEnemy->AttackPower = Config.AttackPower;
			NewEnemy->ExpReward = Config.Exp;
			NewEnemy->GaldReward = Config.Gald;
			NewEnemy->WeaknessElement = Config.Weakness;

			LivingEnemiesCount++;
		}
	}
}

void ABattleGameMode::SpawnPartyCompanions()
{
	UWorld* World = GetWorld();
	if (!World) return;

	APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0);
	ABattleCharacter* PlayerChar = Cast<ABattleCharacter>(PlayerPawn);
	if (!PlayerChar) return;

	// Ensure player character has a PartyCombatManager
	UPartyCombatManager* PartyMgr = PlayerChar->FindComponentByClass<UPartyCombatManager>();
	if (!PartyMgr)
	{
		PartyMgr = NewObject<UPartyCombatManager>(PlayerChar, TEXT("RuntimePartyManager"));
		PartyMgr->RegisterComponent();
	}

	PartyMgr->ActivePartyMembers.Empty();
	PartyMgr->RegisterPartyMember(PlayerChar);

	// Spawn Companion 1: Greatsword Berserker / Vanguard (Left Flank)
	const FVector Comp1Loc = FVector(-180.0f, -720.0f, 110.0f);
	const FRotator CompRot = FRotator(0.0f, 90.0f, 0.0f);

	FActorSpawnParameters SpawnParams;
	SpawnParams.SpawnCollisionHandlingOverride = ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButAlwaysSpawn;

	if (ABattleCharacter* Comp1 = World->SpawnActor<ABattleCharacter>(ABattleCharacter::StaticClass(), Comp1Loc, CompRot, SpawnParams))
	{
		Comp1->SwitchWeaponStyle(EWeaponStyle::Greatsword);
		Comp1->AdventurerProfileID = FName(TEXT("Companion_Vanguard"));
		PartyMgr->RegisterPartyMember(Comp1);
	}

	// Spawn Companion 2: Elemental Mage / Healer (Right Flank)
	const FVector Comp2Loc = FVector(180.0f, -720.0f, 110.0f);
	if (ABattleCharacter* Comp2 = World->SpawnActor<ABattleCharacter>(ABattleCharacter::StaticClass(), Comp2Loc, CompRot, SpawnParams))
	{
		Comp2->SwitchWeaponStyle(EWeaponStyle::SwordAndShield);
		Comp2->AdventurerProfileID = FName(TEXT("Companion_Mage"));
		PartyMgr->RegisterPartyMember(Comp2);
	}
}

void ABattleGameMode::OnEnemyDefeated(ABattleEnemy* Enemy)
{
	if (!Enemy || bBattleFinished) return;

	TotalExpGained += Enemy->ExpReward;
	TotalGaldGained += Enemy->GaldReward;
	LivingEnemiesCount--;

	// Award progression & guild bounty credit to active hero
	if (APawn* PlayerPawn = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		if (ABattleCharacter* Hero = Cast<ABattleCharacter>(PlayerPawn))
		{
			if (Hero->SkillGrid)
			{
				Hero->SkillGrid->AddSP(FMath::Max(15, Enemy->ExpReward / 2));
			}

			if (Hero->TitleManager)
			{
				Hero->TitleManager->AddMasteryExp(Enemy->ExpReward);
			}

			if (Hero->GuildComponent)
			{
				if (Enemy->BountyID != NAME_None)
				{
					Hero->GuildComponent->ReportProgress(Enemy->BountyID, 1);
				}
				if (Enemy->IsDemon())
				{
					Hero->GuildComponent->ReportProgress(FName("AnyDemon"), 1);
				}
			}
		}
	}

	if (LivingEnemiesCount <= 0)
	{
		bBattleFinished = true;
		VictorySequence();
	}
}

void ABattleGameMode::VictorySequence()
{
	CalculatedGrade = CalculateBattleGrade();
	FText Banter = GetRandomVictoryBanter();

	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (PC)
	{
		if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
		{
			HUD->ShowVictoryBanner(TotalExpGained, TotalGaldGained, CalculatedGrade, Banter);
		}
	}

	// Wait 4.5 seconds for player to enjoy the victory banner, grade tally, and banter, then return
	GetWorldTimerManager().SetTimer(
		TransitionTimerHandle,
		this,
		&ABattleGameMode::ReturnToOverworld,
		4.5f,
		false
	);
}

float ABattleGameMode::CalculateBattleGrade()
{
	float Grade = 2.0f; // Base victory grade

	const float ClearTime = GetWorld() ? (GetWorld()->GetTimeSeconds() - BattleStartTime) : 30.0f;
	if (ClearTime < 25.0f)
	{
		Grade += 1.5f; // Fast clear bonus!
	}
	else if (ClearTime < 45.0f)
	{
		Grade += 0.8f;
	}

	// Player health bonus
	if (APawn* Pawn = UGameplayStatics::GetPlayerPawn(this, 0))
	{
		if (ABattleCharacter* Hero = Cast<ABattleCharacter>(Pawn))
		{
			if (Hero->CurrentHP >= Hero->MaxHP * 0.9f)
			{
				Grade += 1.5f; // Flawless / near-flawless victory!
			}
		}
	}

	return FMath::Max(0.2f, Grade);
}

FText ABattleGameMode::GetRandomVictoryBanter()
{
	static const TCHAR* BanterPool[] = {
		TEXT("Hero: \"That was a clean strike!\"\nMage: \"Don't get cocky, there are more ahead!\""),
		TEXT("Knight: \"Our defense held firm. Well fought, everyone!\"\nHero: \"Couldn't have done it without you!\""),
		TEXT("Hero: \"Is that all they've got?\"\nBerserker: \"Hah! I was just getting warmed up!\""),
		TEXT("Mage: \"The elemental flow was harmonious in that battle.\"\nHero: \"Your spell timing was incredible!\""),
		TEXT("Hero: \"Victory is ours! Let's press onward to the next destination!\"")
	};

	const int32 Index = FMath::RandRange(0, UE_ARRAY_COUNT(BanterPool) - 1);
	return FText::FromString(BanterPool[Index]);
}

void ABattleGameMode::RecordHeroIncapacitated(FName HeroID)
{
	if (HeroID != NAME_None)
	{
		IncapacitatedHeroIDs.AddUnique(HeroID);
	}
}

void ABattleGameMode::ReturnToOverworld()
{
	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		GI->bReturningFromBattle = true;
		GI->bLastBattleVictory = true;
		GI->bPartyWasWipedOut = false;
		GI->PendingIncapacitatedHeroIDs = IncapacitatedHeroIDs;
	}

	UGameplayStatics::OpenLevel(this, FName("/Game/IsekaiVillage/Maps/Map_Overworld"));
}

void ABattleGameMode::OnPlayerDefeated()
{
	if (bBattleFinished) return;
	bBattleFinished = true;

	APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0);
	if (PC)
	{
		if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
		{
			HUD->ShowDefeatBanner();
		}
	}

	// Retreat after defeat
	GetWorldTimerManager().SetTimer(
		TransitionTimerHandle,
		this,
		&ABattleGameMode::DefeatSequence,
		3.0f,
		false
	);
}

void ABattleGameMode::DefeatSequence()
{
	if (UOverworldGameInstance* GI = Cast<UOverworldGameInstance>(GetGameInstance()))
	{
		GI->bReturningFromBattle = true;
		GI->bLastBattleVictory = false;
		GI->bPartyWasWipedOut = true;
		GI->PendingIncapacitatedHeroIDs = IncapacitatedHeroIDs;
	}

	UGameplayStatics::OpenLevel(this, FName("/Game/IsekaiVillage/Maps/Map_Overworld"));
}


void ABattleGameMode::EscapeBattle()
{
	if (bBattleFinished) return;
	bBattleFinished = true;

	if (APlayerController* PC = UGameplayStatics::GetPlayerController(this, 0))
	{
		if (ABattleHUD* HUD = Cast<ABattleHUD>(PC->GetHUD()))
		{
			HUD->ShowBattleStartBanner(
				FText::FromString(TEXT("ESCAPED!")),
				FText::FromString(TEXT("Successfully fled from combat!")),
				2.0f
			);
		}
	}

	GetWorldTimerManager().SetTimer(
		TransitionTimerHandle,
		this,
		&ABattleGameMode::DefeatSequence,
		1.5f,
		false
	);
}
