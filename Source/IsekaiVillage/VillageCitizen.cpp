// Copyright Epic Games, Inc. All Rights Reserved.
#include "VillageCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "GatherInventoryComponent.h"
#include "PartyReserveComponent.h"
#include "Components/SphereComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Materials/MaterialInstanceDynamic.h"
#include "Engine/StaticMesh.h"
#include "Engine/Engine.h"

AVillageCitizen::AVillageCitizen()
{
	PrimaryActorTick.bCanEverTick = true;
	Root = CreateDefaultSubobject<USceneComponent>(TEXT("Root"));
	RootComponent = Root;

	Body = CreateDefaultSubobject<UStaticMeshComponent>(TEXT("Body"));
	Body->SetupAttachment(Root);
	Body->SetCollisionEnabled(ECollisionEnabled::NoCollision);
	Body->SetRelativeScale3D(FVector(0.35f, 0.35f, 1.55f));
	Body->SetRelativeLocation(FVector(0.0f, 0.0f, 80.0f));

	Reach = CreateDefaultSubobject<USphereComponent>(TEXT("Reach"));
	Reach->SetupAttachment(Root);
	Reach->InitSphereRadius(140.0f);
	Reach->SetCollisionEnabled(ECollisionEnabled::QueryOnly);
	Reach->SetCollisionResponseToAllChannels(ECR_Ignore);
	Reach->SetCollisionResponseToChannel(ECC_Pawn, ECR_Overlap);
	Reach->SetGenerateOverlapEvents(true);
}

void AVillageCitizen::BeginPlay()
{
	Super::BeginPlay();
	if (!Body->GetStaticMesh())
	{
		if (UStaticMesh* Cyl = LoadObject<UStaticMesh>(nullptr, TEXT("/Engine/BasicShapes/Cylinder.Cylinder")))
		{
			Body->SetStaticMesh(Cyl);
		}
	}
	if (Reach)
	{
		Reach->OnComponentBeginOverlap.AddDynamic(this, &AVillageCitizen::OnBeginOverlap);
		Reach->OnComponentEndOverlap.AddDynamic(this, &AVillageCitizen::OnEndOverlap);
	}
	Restyle();
}

void AVillageCitizen::OnBeginOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex, bool bFromSweep, const FHitResult& SweepResult)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		Character->bNearCitizen = true;
		Character->NearbyCitizen = this;
	}
}

void AVillageCitizen::OnEndOverlap(UPrimitiveComponent* OverlappedComponent, AActor* OtherActor, UPrimitiveComponent* OtherComp, int32 OtherBodyIndex)
{
	if (AIsekaiVillageCharacter* Character = Cast<AIsekaiVillageCharacter>(OtherActor))
	{
		if (Character->NearbyCitizen.Get() == this)
		{
			Character->NearbyCitizen = nullptr;
			Character->bNearCitizen = false;
		}
	}
}

void AVillageCitizen::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
	if (bUseStreetMovement || Goal.IsNearlyZero())
	{
		return;
	}
	const FVector Here = GetActorLocation();
	FVector Next = FMath::VInterpConstantTo(Here, Goal, DeltaSeconds, WalkSpeed);
	Next.Z = FMath::FInterpTo(Here.Z, Goal.Z, DeltaSeconds, 2.0f);
	SetActorLocation(Next, false);
	const FVector Flat = (Goal - Here).GetSafeNormal2D();
	if (!Flat.IsNearlyZero())
	{
		SetActorRotation(Flat.Rotation());
	}
}

void AVillageCitizen::SetGoal(EVillagePlace Place, const FVector& World)
{
	GoalPlace = Place;
	Goal = World;
}

void AVillageCitizen::Restyle()
{
	FLinearColor Color(0.55f, 0.5f, 0.42f);
	switch (Mind.Job)
	{
	case ECitizenJob::Guard: Color = FLinearColor(0.35f, 0.42f, 0.62f); break;
	case ECitizenJob::Adventurer: Color = FLinearColor(0.72f, 0.38f, 0.22f); break;
	case ECitizenJob::Clerk: Color = FLinearColor(0.55f, 0.48f, 0.22f); break;
	case ECitizenJob::Hauler: Color = FLinearColor(0.42f, 0.38f, 0.28f); break;
	default: break;
	}
	if (Mind.Status == ECitizenStatus::Visitor)
	{
		Color += FLinearColor(0.12f, 0.08f, 0.0f);
	}
	if (UMaterialInterface* Base = Body->GetMaterial(0))
	{
		if (UMaterialInstanceDynamic* Dyn = UMaterialInstanceDynamic::Create(Base, this))
		{
			Dyn->SetVectorParameterValue(TEXT("Color"), Color);
			Body->SetMaterial(0, Dyn);
		}
	}
}

FText AVillageCitizen::BarkLine() const
{
	if (Mind.bSick) return FText::FromString(TEXT("needs rest"));
	if (Mind.Mutex == ECitizenMutex::Gather) return FText::FromString(TEXT("hauling wood"));
	if (Mind.Mutex == ECitizenMutex::Train) return FText::FromString(TEXT("on the yard"));
	if (Mind.Mutex == ECitizenMutex::Guard) return FText::FromString(TEXT("walking a watch"));
	if (Mind.Mutex == ECitizenMutex::Tower) return FText::FromString(TEXT("heading for a tower"));
	if (Mind.Mutex == ECitizenMutex::Shop) return FText::FromString(TEXT("at the stall"));
	if (Mind.Mutex == ECitizenMutex::Food) return FText::FromString(TEXT("looking for a meal"));
	if (Mind.Mutex == ECitizenMutex::Chapel) return FText::FromString(TEXT("at chapel"));
	if (Mind.Mutex == ECitizenMutex::Sleep) return FText::FromString(TEXT("turning in"));
	if (Mind.Status == ECitizenStatus::Visitor) return FText::FromString(TEXT("passing through"));
	return FText::FromString(TEXT("about town"));
}

FText AVillageCitizen::OfferLine() const
{
	if (Mind.Job == ECitizenJob::Adventurer || Mind.bHasAttack)
	{
		return FText::FromString(FString::Printf(TEXT("T  Ask %s to walk with you"), *Mind.DisplayName.ToString()));
	}
	if (Mind.TotalBag() > 0)
	{
		return FText::FromString(FString::Printf(TEXT("T  Buy from %s"), *Mind.DisplayName.ToString()));
	}
	return FText::FromString(FString::Printf(TEXT("T  Speak with %s"), *Mind.DisplayName.ToString()));
}

bool AVillageCitizen::TryPlayerOffer(AIsekaiVillageCharacter* Player)
{
	if (!Player)
	{
		return false;
	}

	auto Say = [](const FString& Line, const FColor& Color)
	{
		if (GEngine)
		{
			GEngine->AddOnScreenDebugMessage(-1, 3.0f, Color, Line);
		}
	};

	if (Mind.Job == ECitizenJob::Adventurer || (Mind.bHasAttack && Mind.TrainHours >= 2))
	{
		const bool bRefuse = (Mind.Trait == ECitizenTrait::Cautious && Mind.BondPlayer < 8)
			|| Mind.bSick
			|| Mind.Wound > 40
			|| (Mind.Trait == ECitizenTrait::Lazy && Mind.Rest < 35);
		if (bRefuse)
		{
			Mind.BondPlayer = FMath::Max(0, Mind.BondPlayer - 1);
			Say(FString::Printf(TEXT("%s shakes their head. Not today."), *Mind.DisplayName.ToString()), FColor::Orange);
			return true;
		}
		if (!Player->PartyReserve || !Player->PartyReserve->HireAdventurer(Mind.DisplayName))
		{
			Say(TEXT("Your reserve is full."), FColor::Red);
			return true;
		}
		Mind.Mutex = ECitizenMutex::Party;
		Mind.BondPlayer += 12;
		Mind.BondTown += 4;
		Restyle();
		Say(FString::Printf(TEXT("%s joins your reserve."), *Mind.DisplayName.ToString()), FColor::Cyan);
		return true;
	}

	if (Mind.TotalBag() > 0 && Player->Gather)
	{
		const bool bGreedyHold = Mind.Trait == ECitizenTrait::Greedy && Mind.BondPlayer < 6 && Mind.Coin < 20;
		if (bGreedyHold)
		{
			Say(FString::Printf(TEXT("%s wants a better price later."), *Mind.DisplayName.ToString()), FColor::Orange);
			return true;
		}
		TArray<FName> Ids = Mind.BagIds;
		TArray<int32> Counts = Mind.BagCounts;
		Mind.BagIds.Reset();
		Mind.BagCounts.Reset();
		int32 Moved = 0;
		for (int32 i = 0; i < Ids.Num(); ++i)
		{
			Player->Gather->AddItem(Ids[i], Counts[i]);
			Moved += Counts[i];
		}
		Mind.Coin += Moved * 2;
		Mind.BondPlayer += 6;
		Mind.bLastSaleFair = true;
		Say(FString::Printf(TEXT("Bought %d from %s."), Moved, *Mind.DisplayName.ToString()), FColor::Yellow);
		return true;
	}

	if (Mind.Trait == ECitizenTrait::Stoic && FMath::RandHelper(100) < 25)
	{
		Say(FString::Printf(TEXT("%s nods and keeps walking."), *Mind.DisplayName.ToString()), FColor::Silver);
		return true;
	}
	Mind.BondPlayer += 3;
	Mind.Morale = FMath::Clamp(Mind.Morale + 5, 0, 100);
	Say(FString::Printf(TEXT("%s: %s"), *Mind.DisplayName.ToString(), *BarkLine().ToString()), FColor::White);
	return true;
}

bool AVillageCitizen::AtGoal(float Dist) const
{
	return FVector::DistSquared2D(GetActorLocation(), Goal) <= Dist * Dist;
}
