// Copyright Epic Games, Inc. All Rights Reserved.

#include "BlacksmithForge.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "VillageRuntime.h"
#include "EngineUtils.h"
#include "Components/BoxComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Engine/StaticMesh.h"

ABlacksmithForge::ABlacksmithForge()
{
	PrimaryActorTick.bCanEverTick = false;

	InteractBox = CreateDefaultSubobject<UBoxComponent>(TEXT("InteractBox"));
	InteractBox->InitBoxExtent(FVector(220.0f, 220.0f, 120.0f));
	InteractBox->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	InteractBox->SetCollisionResponseToAllChannels(ECR_Ignore);
	InteractBox->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	RootComponent = InteractBox;

	AnvilMesh = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("AnvilMesh"));
	AnvilMesh->SetupAttachment(RootComponent);
	AnvilMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	AnvilMesh->SetRelativeScale3D(FVector(1.1f, 0.7f, 0.85f));
}

void ABlacksmithForge::BeginPlay()
{
	Super::BeginPlay();

	if (!AnvilMesh->GetStaticMesh())
	{
		if (UStaticMesh* Cube = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cube.Cube")))
		{
			AnvilMesh->SetStaticMesh(Cube);
		}
	}

	InteractBox->OnComponentBeginOverlap.AddDynamic(this, &ABlacksmithForge::OnBeginOverlap);
	InteractBox->OnComponentEndOverlap.AddDynamic(this, &ABlacksmithForge::OnEndOverlap);
}

bool ABlacksmithForge::TryForge(AIsekaiVillageCharacter* Character)
{
	if (!Character || !Character->Gather)
	{
		return false;
	}
	UGatherInventoryComponent* Gather = Character->Gather;
	auto Cost = [Character](int32 Base, bool bCrystal = false) { return UGatherInventoryComponent::ForgeCost(Character, Base, bCrystal); };
	const bool bCanAxe = (Gather->AxeTier == EAxeTier::Stone && Gather->GetCount(TEXT("Iron")) >= Cost(6) && Gather->GetCount(TEXT("Wood")) >= Cost(4))
		|| (Gather->AxeTier == EAxeTier::Iron && Gather->GetCount(TEXT("Crystal")) >= Cost(4, true) && Gather->GetCount(TEXT("Iron")) >= Cost(8));
	const bool bCanPick = (Gather->PickaxeTier == EAxeTier::Stone && Gather->GetCount(TEXT("Iron")) >= Cost(8) && Gather->GetCount(TEXT("Wood")) >= Cost(2))
		|| (Gather->PickaxeTier == EAxeTier::Iron && Gather->GetCount(TEXT("Crystal")) >= Cost(6, true) && Gather->GetCount(TEXT("Iron")) >= Cost(6));

	if (bCanAxe || bCanPick)
	{
		const bool bToolSuccess = Gather->TryForgeUpgrades();
		if (bToolSuccess)
		{
			if (UWorld* World = GetWorld())
			{
				for (TActorIterator<AVillageRuntime> It(World); It; ++It)
				{
					It->SaveVillageState(Character);
					break;
				}
			}
			return true;
		}
	}

	if (TryForgeAdventurerGear(Character))
	{
		return true;
	}

	if (GEngine)
	{
		GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Orange, ForgeStatusLine(Character));
	}
	return false;
}

bool ABlacksmithForge::TryForgeAdventurerGear(AIsekaiVillageCharacter* Character)
{
	if (!Character || !Character->Gather || !Character->PartyReserve)
	{
		return false;
	}

	UGatherInventoryComponent* Gather = Character->Gather;
	TArray<FHiredAdventurer>& Reserve = Character->PartyReserve->Reserve;
	if (Reserve.IsEmpty())
	{
		return false;
	}

	auto Cost = [Character](int32 Base, bool bCrystal = false) { return UGatherInventoryComponent::ForgeCost(Character, Base, bCrystal); };
	auto TryUpgradeMember = [&](FHiredAdventurer& A) -> bool
	{
		// 1. Iron Weapon (Tier 0 -> 1): 4 Iron + 2 Wood (+6 ATK)
		if (A.WeaponTier == 0 && Gather->GetCount(TEXT("Iron")) >= Cost(4) && Gather->GetCount(TEXT("Wood")) >= Cost(2))
		{
			Gather->Consume(TEXT("Iron"), Cost(4));
			Gather->Consume(TEXT("Wood"), Cost(2));
			A.WeaponTier = 1;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Silver,
					FString::Printf(TEXT("Forged Iron Weapon for %s (+6 ATK)"), *A.Name.ToString()));
			}
			return true;
		}

		// 2. Iron Armor (Tier 0 -> 1): 4 Iron + 2 Stone (+25 Max HP, 10% Guard)
		if (A.ArmorTier == 0 && Gather->GetCount(TEXT("Iron")) >= Cost(4) && Gather->GetCount(TEXT("Stone")) >= Cost(2))
		{
			Gather->Consume(TEXT("Iron"), Cost(4));
			Gather->Consume(TEXT("Stone"), Cost(2));
			A.ArmorTier = 1;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Silver,
					FString::Printf(TEXT("Forged Iron Armor for %s (+25 HP, +10%% Guard)"), *A.Name.ToString()));
			}
			return true;
		}

		// 3. Runic Weapon (Tier 1 -> 2): 4 Crystal + 6 Iron (+12 ATK, +10 starting TP)
		if (A.WeaponTier == 1 && Gather->GetCount(TEXT("Crystal")) >= Cost(4, true) && Gather->GetCount(TEXT("Iron")) >= Cost(6))
		{
			Gather->Consume(TEXT("Crystal"), Cost(4, true));
			Gather->Consume(TEXT("Iron"), Cost(6));
			A.WeaponTier = 2;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Cyan,
					FString::Printf(TEXT("Forged Runic Weapon for %s (+12 ATK, +10 Max TP)"), *A.Name.ToString()));
			}
			return true;
		}

		// 4. Runic Armor (Tier 1 -> 2): 4 Crystal + 6 Iron (+50 Max HP, 20% Guard)
		if (A.ArmorTier == 1 && Gather->GetCount(TEXT("Crystal")) >= Cost(4, true) && Gather->GetCount(TEXT("Iron")) >= Cost(6))
		{
			Gather->Consume(TEXT("Crystal"), Cost(4, true));
			Gather->Consume(TEXT("Iron"), Cost(6));
			A.ArmorTier = 2;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.0f, FColor::Cyan,
					FString::Printf(TEXT("Forged Runic Armor for %s (+50 HP, +20%% Guard)"), *A.Name.ToString()));
			}
			return true;
		}

		return false;
	};

	bool bForged = false;
	for (FHiredAdventurer& A : Reserve)
	{
		if (A.bInActiveParty)
		{
			if (TryUpgradeMember(A))
			{
				bForged = true;
				break;
			}
		}
	}

	if (!bForged)
	{
		for (FHiredAdventurer& A : Reserve)
		{
			if (!A.bInActiveParty)
			{
				if (TryUpgradeMember(A))
				{
					bForged = true;
					break;
				}
			}
		}
	}

	if (bForged)
	{
		if (UWorld* World = GetWorld())
		{
			for (TActorIterator<AVillageRuntime> It(World); It; ++It)
			{
				It->SaveVillageState(Character);
				break;
			}
		}
		return true;
	}

	return false;
}

bool ABlacksmithForge::TemperWithToolParts(AIsekaiVillageCharacter* Character, FName AdventurerId)
{
	if (!Character || !Character->Gather || !Character->PartyReserve)
	{
		return false;
	}
	UGatherInventoryComponent* Gather = Character->Gather;
	TArray<FHiredAdventurer>& Reserve = Character->PartyReserve->Reserve;
	const int32 CostParts = UGatherInventoryComponent::ForgeCost(Character, 2);
	auto CanTemper = [](const FHiredAdventurer& A) { return A.TemperLevel < 2; };

	FHiredAdventurer* Target = nullptr;
	if (!AdventurerId.IsNone())
	{
		Target = Reserve.FindByPredicate([AdventurerId](const FHiredAdventurer& A) { return A.AdventurerID == AdventurerId; });
		if (!Target || !CanTemper(*Target))
		{
			LastForgeMessage = Target ? TEXT("Chosen adventurer gear is already fully tempered (+2).") : TEXT("Adventurer not found.");
			return false;
		}
	}
	else
	{
		Target = Reserve.FindByPredicate([&](const FHiredAdventurer& A) { return A.bInActiveParty && CanTemper(A); });
		if (!Target) Target = Reserve.FindByPredicate([&](const FHiredAdventurer& A) { return CanTemper(A); });
	}
	if (!Target)
	{
		LastForgeMessage = TEXT("All adventurers already have +2 Masterwork Temper!");
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Cyan, LastForgeMessage);
		return false;
	}
	if (Gather->GetCount(TEXT("ToolParts")) < CostParts)
	{
		LastForgeMessage = FString::Printf(TEXT("Tempering %s needs %d Tool Parts (from Smith or Shop)."), *Target->Name.ToString(), CostParts);
		if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.5f, FColor::Orange, LastForgeMessage);
		return false;
	}
	Gather->Consume(TEXT("ToolParts"), CostParts);
	Target->TemperLevel = FMath::Min(2, Target->TemperLevel + 1);
	LastForgeMessage = FString::Printf(TEXT("Tempered %s's gear to +%d with %d Tool Parts (+%d%% ATK/DEF)!"),
		*Target->Name.ToString(), Target->TemperLevel, CostParts, Target->TemperLevel * 5);
	if (GEngine) GEngine->AddOnScreenDebugMessage(-1, 2.8f, FColor::Cyan, LastForgeMessage);
	if (UWorld* World = GetWorld())
	{
		for (TActorIterator<AVillageRuntime> It(World); It; ++It)
		{
			It->SaveVillageState(Character);
			break;
		}
	}
	return true;
}

FString ABlacksmithForge::ForgeStatusLine(AIsekaiVillageCharacter* Character) const
{
	if (!Character || !Character->Gather)
	{
		return TEXT("Blacksmith Forge: Stand closer with materials.");
	}

	UGatherInventoryComponent* Gather = Character->Gather;
	auto Cost = [Character](int32 Base, bool bCrystal = false) { return UGatherInventoryComponent::ForgeCost(Character, Base, bCrystal); };
	FString Line = TEXT("Forge: ");

	if (Gather->AxeTier == EAxeTier::Stone)
	{
		Line += FString::Printf(TEXT("Iron Axe (%d Iron, %d Wood) "), Cost(6), Cost(4));
	}
	else if (Gather->AxeTier == EAxeTier::Iron)
	{
		Line += FString::Printf(TEXT("Steel Axe (%d Crystal, %d Iron) "), Cost(4, true), Cost(8));
	}

	if (Gather->PickaxeTier == EAxeTier::Stone)
	{
		Line += FString::Printf(TEXT("Iron Pickaxe (%d Iron, %d Wood) "), Cost(8), Cost(2));
	}
	else if (Gather->PickaxeTier == EAxeTier::Iron)
	{
		Line += FString::Printf(TEXT("Steel Pickaxe (%d Crystal, %d Iron) "), Cost(6, true), Cost(6));
	}

	if (Character->PartyReserve && !Character->PartyReserve->Reserve.IsEmpty())
	{
		const FHiredAdventurer* Target = nullptr;
		for (const auto& A : Character->PartyReserve->Reserve)
		{
			if (A.bInActiveParty && (A.WeaponTier < 2 || A.ArmorTier < 2))
			{
				Target = &A;
				break;
			}
		}
		if (!Target)
		{
			for (const auto& A : Character->PartyReserve->Reserve)
			{
				if (A.WeaponTier < 2 || A.ArmorTier < 2)
				{
					Target = &A;
					break;
				}
			}
		}

		if (Target)
		{
			if (Target->WeaponTier == 0)
			{
				Line += FString::Printf(TEXT("| %s: Iron Wpn (%d Iron, %d Wood) "), *Target->Name.ToString(), Cost(4), Cost(2));
			}
			else if (Target->WeaponTier == 1)
			{
				Line += FString::Printf(TEXT("| %s: Runic Wpn (%d Crystal, %d Iron) "), *Target->Name.ToString(), Cost(4, true), Cost(6));
			}

			if (Target->ArmorTier == 0)
			{
				Line += FString::Printf(TEXT("| Iron Arm (%d Iron, %d Stone)"), Cost(4), Cost(2));
			}
			else if (Target->ArmorTier == 1)
			{
				Line += FString::Printf(TEXT("| Runic Arm (%d Crystal, %d Iron)"), Cost(4, true), Cost(6));
			}
			if (Target->TemperLevel < 2)
			{
				Line += FString::Printf(TEXT("| Temper +%d (%d ToolParts)"), Target->TemperLevel + 1, Cost(2));
			}
		}
		else
		{
			Line += TEXT("| All adventurer gear maxed!");
		}
	}
	else
	{
		Line += TEXT("| Hire adventurers at Guild Hall to forge gear.");
	}

	return Line;
}

void ABlacksmithForge::OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearBlacksmith = true;
	}
}

void ABlacksmithForge::OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearBlacksmith = false;
	}
}
