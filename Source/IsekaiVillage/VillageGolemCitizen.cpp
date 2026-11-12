#include "VillageGolemCitizen.h"
#include "GolemSparring.h"
#include "VillageRuntime.h"
#include "LinchpinProp.h"
#include "IsekaiVillageCharacter.h"
#include "DrawDebugHelpers.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "Components/StaticMeshComponent.h"
#include "Animation/AnimSequence.h"
#include "EngineUtils.h"
#include "Engine/Engine.h"

AVillageGolemCitizen::AVillageGolemCitizen()
{
	bUseStreetMovement = true;
	WalkSpeed = 200.f;
	MovementCapsule = CreateDefaultSubobject<UCapsuleComponent>(TEXT("WorkerCollision"));
	MovementCapsule->InitCapsuleSize(35.f, 97.f);
	MovementCapsule->SetCollisionProfileName(TEXT("Pawn"));
	MovementCapsule->SetCollisionResponseToChannel(ECC_Camera, ECR_Ignore);
	SetRootComponent(MovementCapsule);
	Root->SetupAttachment(MovementCapsule);
	Body->SetVisibility(false);
	Body->SetHiddenInGame(true);
	GolemMesh = CreateDefaultSubobject<USkeletalMeshComponent>(TEXT("GolemMesh"));
	GolemMesh->SetupAttachment(MovementCapsule);
	GolemMesh->SetRelativeLocation(FVector(0, 0, -97));
	GolemMesh->SetRelativeRotation(FRotator(0, -90, 0));
	GolemMesh->SetCollisionEnabled(ECollisionEnabled::NoCollision);
}

void AVillageGolemCitizen::BeginPlay()
{
	Super::BeginPlay();
	Body->SetHiddenInGame(true);
}

void AVillageGolemCitizen::Configure(AVillageRuntime* InVillage, const FVillageGolemRecord& Record)
{
	Village = InVillage;
	GolemId = Record.Id;
	WorkPlot = Record.WorkPlot;AppearanceClass=Record.ClassId;bFemaleAppearance=Record.bFemale;
	Mind.DisplayName = FText::FromString(Record.Name);
	Mind.HomeId = Record.HomePlot;
	Mind.Status = ECitizenStatus::Resident;
	Mind.Job = Record.AdventurerId.IsNone() ? ECitizenJob::Clerk : ECitizenJob::Adventurer;
	IdleAnimation = Record.bFemale ? Village->FemaleWorkerIdle : Village->MaleWorkerIdle;
	WalkAnimation = Record.bFemale ? Village->FemaleWorkerWalk : Village->MaleWorkerWalk;
	USkeletalMesh* Mesh = Village->FindAdventurerMesh(Record.ClassId,Record.bFemale);
 if(!Mesh)Mesh=Record.bFemale ? Village->FemaleWorkerMesh.Get() : Village->MaleWorkerMesh.Get();
	GolemMesh->SetSkeletalMesh(Mesh);
	GolemMesh->SetAnimationMode(EAnimationMode::AnimationSingleNode);
	if (IdleAnimation) GolemMesh->PlayAnimation(IdleAnimation, true);
	bWalking = false;
}

void AVillageGolemCitizen::SetWalking(bool bMoving)
{
	if (bWalking == bMoving) return;
	bWalking = bMoving;
	if (bMoving && bHarvesting)
	{
		SetHarvesting(false, HarvestPlace);
	}
	if (bMoving && CurrentRoutine != EGolemWorkRoutine::None)
	{
		SetWorkRoutine(EGolemWorkRoutine::None, nullptr);
	}
	UAnimSequence* Animation = bMoving ? WalkAnimation.Get() : IdleAnimation.Get();
	if (Animation) GolemMesh->PlayAnimation(Animation, true);
}

void AVillageGolemCitizen::SetWorkRoutine(EGolemWorkRoutine InRoutine, ALinchpinProp* InStation)
{
	if (CurrentRoutine == InRoutine && CurrentStationProp == InStation)
	{
		return;
	}

	CurrentRoutine = InRoutine;
	CurrentStationProp = InStation;
	RoutineTimer = 0.0f;

	if (CurrentRoutine == EGolemWorkRoutine::None)
	{
		if (GolemMesh)
		{
			GolemMesh->SetRelativeLocation(FVector(0, 0, -97));
			GolemMesh->SetRelativeRotation(FRotator(0, -90, 0));
		}
	}
	else if (CurrentRoutine == EGolemWorkRoutine::Sleeping_In_Bed)
	{
		SetWalking(false);
		if (InStation)
		{
			SetActorRotation(InStation->GetActorRotation());
			if (GolemMesh)
			{
				GolemMesh->SetRelativeRotation(FRotator(90.0f, -90.0f, 0.0f));
				GolemMesh->SetRelativeLocation(FVector(0, 0, -50.0f));
			}
		}
	}
	else
	{
		SetWalking(false);
		if (InStation)
		{
			const FVector Dir = (InStation->GetActorLocation() - GetActorLocation()).GetSafeNormal2D();
			if (!Dir.IsNearlyZero())
			{
				SetActorRotation(Dir.Rotation());
			}
		}
	}
}

void AVillageGolemCitizen::TickRoutineBehaviors(float DeltaSeconds)
{
	if (CurrentRoutine == EGolemWorkRoutine::None)
	{
		return;
	}

	RoutineTimer += DeltaSeconds;
	if (GreetCooldown > 0.0f)
	{
		GreetCooldown -= DeltaSeconds;
	}

	AIsekaiVillageCharacter* NearPlayer = nullptr;
	for (TActorIterator<AIsekaiVillageCharacter> PIt(GetWorld()); PIt; ++PIt)
	{
		if (FVector::DistSquared(GetActorLocation(), (*PIt)->GetActorLocation()) < FMath::Square(380.0f))
		{
			NearPlayer = *PIt;
			break;
		}
	}

	switch (CurrentRoutine)
	{
	case EGolemWorkRoutine::Blacksmith_Hammering:
		if (GolemMesh)
		{
			const float Cycle = FMath::Fmod(RoutineTimer, 1.4f);
			const float HammerPitch = (Cycle < 0.4f) ? FMath::Sin(Cycle / 0.4f * PI) * -28.0f : 0.0f;
			const float BobZ = (Cycle < 0.4f) ? FMath::Sin(Cycle / 0.4f * PI) * -8.0f : 0.0f;
			GolemMesh->SetRelativeRotation(FRotator(HammerPitch, -90.0f, 0.0f));
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f + BobZ));

			if (Cycle < DeltaSeconds && CurrentStationProp.IsValid())
			{
				if (GEngine && NearPlayer)
				{
					const FVector SparkOrigin = CurrentStationProp->GetActorLocation() + FVector(0, 0, 45.0f);
					DrawDebugPoint(GetWorld(), SparkOrigin, 14.0f, FColor(255, 190, 40), false, 0.4f);
					for (int32 S = 0; S < 4; ++S)
					{
						const FVector SparkVel = FVector(FMath::RandRange(-25.f, 25.f), FMath::RandRange(-25.f, 25.f), FMath::RandRange(15.f, 40.f));
						DrawDebugLine(GetWorld(), SparkOrigin, SparkOrigin + SparkVel, FColor(255, 230, 100), false, 0.25f, 0, 1.5f);
					}
				}
			}
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 8.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Orange, FString::Printf(TEXT("%s: Strike while the iron glows, traveler! The forge sings today."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	case EGolemWorkRoutine::Innkeeper_Hosting:
		if (GolemMesh)
		{
			const float Breath = FMath::Sin(RoutineTimer * 2.0f) * 2.0f;
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f + Breath));
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 7.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Yellow, FString::Printf(TEXT("%s: Welcome to the hearth, adventurer! Rest your feet and drink warm cider."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	case EGolemWorkRoutine::Shopkeeper_Trading:
		if (GolemMesh)
		{
			const float Bob = FMath::Sin(RoutineTimer * 1.5f) * 2.5f;
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f + Bob));
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 7.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Green, FString::Printf(TEXT("%s: Fresh supplies straight from the valley! Fair prices for true crafters."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	case EGolemWorkRoutine::Baker_Baking:
		if (GolemMesh)
		{
			const float Knead = FMath::Sin(RoutineTimer * 3.0f) * 12.0f;
			GolemMesh->SetRelativeRotation(FRotator(Knead, -90.0f, 0.0f));
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f));
			if (NearPlayer && CurrentStationProp.IsValid())
			{
				const float PuffCycle = FMath::Fmod(RoutineTimer, 0.9f);
				if (PuffCycle < DeltaSeconds * 1.5f)
				{
					const FVector OvenTop = CurrentStationProp->GetActorLocation() + FVector(0, 0, 75.0f);
					DrawDebugPoint(GetWorld(), OvenTop + FVector(FMath::RandRange(-8.f, 8.f), FMath::RandRange(-8.f, 8.f), 15.f), 10.0f, FColor(220, 215, 200, 180), false, 0.5f);
				}
			}
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 8.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Yellow, FString::Printf(TEXT("%s: Crust is golden brown! Fresh bread restores energy in the tower."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	case EGolemWorkRoutine::Craftsman_Working:
		if (GolemMesh)
		{
			const float Chisel = FMath::Abs(FMath::Sin(RoutineTimer * 4.0f)) * -10.0f;
			GolemMesh->SetRelativeRotation(FRotator(Chisel, -90.0f, 0.0f));
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f));
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 8.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor::Cyan, FString::Printf(TEXT("%s: Precision joints and sturdy pegs make walls that last centuries."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	case EGolemWorkRoutine::Sleeping_In_Bed:
		if (GolemMesh)
		{
			const float SnorePulse = FMath::Sin(RoutineTimer * 1.5f) * 3.0f;
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -50.0f + SnorePulse));
			if (NearPlayer)
			{
				const float ZzzCycle = FMath::Fmod(RoutineTimer, 2.0f);
				if (ZzzCycle < DeltaSeconds * 1.5f)
				{
					DrawDebugString(GetWorld(), GetActorLocation() + FVector(0, 0, 80.0f), TEXT("Zzz..."), nullptr, FColor(160, 210, 255), 1.2f, true, 1.1f);
				}
			}
		}
		if (Village)
		{
			if (FVillageGolemRecord* Rec = Village->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& R) { return R.Id == GolemId; }))
			{
				Rec->Drives.Fatigue = FMath::Max(0.0f, Rec->Drives.Fatigue - DeltaSeconds * 5.0f);
			}
		}
		break;

	case EGolemWorkRoutine::Alchemist_Brewing:
		if (GolemMesh)
		{
			const float Stir = FMath::Sin(RoutineTimer * 2.5f) * 10.0f;
			GolemMesh->SetRelativeRotation(FRotator(0.0f, -90.0f + Stir, 0.0f));
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f));
			if (NearPlayer && CurrentStationProp.IsValid())
			{
				const FVector CauldronRim = CurrentStationProp->GetActorLocation() + FVector(0, 0, 50.0f);
				DrawDebugPoint(GetWorld(), CauldronRim + FVector(FMath::RandRange(-10.f, 10.f), FMath::RandRange(-10.f, 10.f), 10.f), 9.0f, FColor(180, 80, 255), false, 0.4f);
			}
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 8.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor(190, 110, 255), FString::Printf(TEXT("%s: Distilling mountain essences... Potions of warding will aid the climb."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	case EGolemWorkRoutine::Enchanter_Inscribing:
		if (GolemMesh)
		{
			const float Chant = FMath::Sin(RoutineTimer * 1.8f) * 4.0f;
			GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f + Chant));
			if (NearPlayer && CurrentStationProp.IsValid())
			{
				const FVector TableTop = CurrentStationProp->GetActorLocation() + FVector(0, 0, 60.0f);
				DrawDebugPoint(GetWorld(), TableTop + FVector(FMath::RandRange(-12.f, 12.f), FMath::RandRange(-12.f, 12.f), 8.f), 10.0f, FColor(90, 220, 255), false, 0.35f);
			}
		}
		if (NearPlayer && GreetCooldown <= 0.0f)
		{
			GreetCooldown = 8.0f;
			if (GEngine)
			{
				GEngine->AddOnScreenDebugMessage(-1, 3.5f, FColor(100, 225, 255), FString::Printf(TEXT("%s: The leylines flow into our runes. Every glyph strengthens the ward."), *Mind.DisplayName.ToString()));
			}
		}
		break;

	default:
		break;
	}
}

void AVillageGolemCitizen::SetHarvesting(bool bInHarvesting, EVillagePlace InPlace)
{
	bHarvesting = bInHarvesting;
	HarvestPlace = InPlace;
	if (!bHarvesting && GolemMesh)
	{
		HarvestAnimTime = 0.0f;
		GolemMesh->SetRelativeLocation(FVector(0, 0, -97));
		GolemMesh->SetRelativeRotation(FRotator(0, -90, 0));
	}
}

void AVillageGolemCitizen::Tick(float DeltaSeconds)
{
	Super::Tick(DeltaSeconds);
 if(ActorHasTag(TEXT("ElrhunSparring"))){SetHarvesting(false,HarvestPlace);SetWalking(false);return;}
	if (!Village) return;
	if (!bWalking && CurrentRoutine != EGolemWorkRoutine::None)
	{
		TickRoutineBehaviors(DeltaSeconds);
	}
	if (bHarvesting && !bWalking && GolemMesh)
	{
		HarvestAnimTime += DeltaSeconds;
		const float Phase = HarvestAnimTime * (HarvestPlace == EVillagePlace::Lake ? 2.4f : 5.2f);
		const float Pitch = (HarvestPlace == EVillagePlace::Lake)
			? FMath::Sin(Phase) * 6.0f
			: -FMath::Abs(FMath::Sin(Phase)) * 12.0f;
		const float BobZ = (HarvestPlace == EVillagePlace::Lake) ? 0.0f : FMath::Abs(FMath::Sin(Phase)) * 4.0f;
		GolemMesh->SetRelativeRotation(FRotator(Pitch, -90.0f, 0.0f));
		GolemMesh->SetRelativeLocation(FVector(0.0f, 0.0f, -97.0f + BobZ));
	}
	RetryIn -= DeltaSeconds;
	if (!Goal.Equals(RoutedGoal, 1.f) || (Route.IsEmpty() && bRouteBlocked && RetryIn <= 0))
	{
		RoutedGoal = Goal;
		RouteIndex = 0;
		bRouteBlocked = !Village->BuildStreetRoute(GetActorLocation(), Goal, Route);
		RetryIn = 2.f;
	}
	while (Route.IsValidIndex(RouteIndex) && FVector::DistSquared2D(GetActorLocation(), Route[RouteIndex]) < FMath::Square(32.f)) ++RouteIndex;
	if (AtGoal(32.f)) { RouteIndex = Route.Num(); SetWalking(false); return; }
	if (!Route.IsValidIndex(RouteIndex)) { SetWalking(false); return; }
	const FVector Here = GetActorLocation();
	const FVector Target = Route[RouteIndex];
	FVector Direction = (Target - Here).GetSafeNormal2D();
 // Keep right when another worker is approaching or waiting in our lane.
 // Remain inside the current street segment and retain all collision sweeps.
 const FVector Right = FVector::CrossProduct(FVector::UpVector, Direction);
 for (TActorIterator<AVillageGolemCitizen> It(GetWorld()); It; ++It)
 {
  if (*It == this) continue;
  const FVector Delta = It->GetActorLocation() - Here;
  if (Delta.SizeSquared2D() > FMath::Square(170.f) || FVector::DotProduct(Delta,Direction) <= 0 || FMath::Abs(FVector::DotProduct(Delta,Right)) > 100.f) continue;
  const FVector SideStep = Here + Right * 45.f;
  const FVector SegmentStart = RouteIndex > 0 ? Route[RouteIndex-1] : Here;
  if (FMath::PointDistToSegment(FVector(SideStep.X,SideStep.Y,0),FVector(SegmentStart.X,SegmentStart.Y,0),FVector(Target.X,Target.Y,0)) < 160.f)
   Direction = (Direction + Right * 1.7f).GetSafeNormal2D();
  break;
 }
	const float Step = FMath::Min(WalkSpeed * DeltaSeconds, FVector::Dist2D(Here, Target));
	FVector Next = Here + Direction * Step;
	FHitResult Ground;
	FCollisionQueryParams Query(SCENE_QUERY_STAT(GolemStreetGround), true, this);
	if (!GetWorld()->LineTraceSingleByChannel(Ground, Next + FVector(0, 0, 250), Next - FVector(0, 0, 500), ECC_Visibility, Query)
		|| Ground.ImpactNormal.Z < .6f || FMath::Abs(Ground.ImpactPoint.Z + 99.f - Here.Z) > 45.f)
	{
		bRouteBlocked = true; SetWalking(false); return;
	}
	const float GroundHeight = Ground.ImpactPoint.Z + 99.f + 35.f * (1.f / Ground.ImpactNormal.Z - 1.f);
	// Raise for an uphill step before moving. On a descent, retain current
	// support until the capsule has moved beyond the higher edge behind it.
	if (GroundHeight > Here.Z)
	{
		FHitResult Ceiling;
		SetActorLocation(FVector(Here.X, Here.Y, GroundHeight), true, &Ceiling);
		if (Ceiling.bBlockingHit) { bRouteBlocked = true; SetWalking(false); return; }
	}
	Next.Z = GetActorLocation().Z;
	FHitResult Block;
	SetActorLocation(Next, true, &Block);
	const float Moved = FVector::Dist2D(Here, GetActorLocation());
	FVector Supported = GetActorLocation(); Supported.Z = GroundHeight;
	FHitResult Floor;
	SetActorLocation(Supported, true, &Floor);
	bRouteBlocked = Block.bBlockingHit && Moved < Step * .25f;

 if (bRouteBlocked && Cast<AVillageGolemCitizen>(Block.GetActor()))
 {
  // From touching capsules, a forward diagonal remains blocked. Step purely
  // sideways first, checking both ground and physical collision.
  for (float Sign : {1.f,-1.f})
  {
   const FVector Before=GetActorLocation(); FVector Side=Before+Right*Step*Sign;
   FHitResult SideGround;
   if (!GetWorld()->LineTraceSingleByChannel(SideGround,Side+FVector(0,0,250),Side-FVector(0,0,500),ECC_Visibility,Query) || SideGround.ImpactNormal.Z<.6f) continue;
   const float Height=SideGround.ImpactPoint.Z+99.f+35.f*(1.f/SideGround.ImpactNormal.Z-1.f);
   if (FMath::Abs(Height-Before.Z)>45.f) continue;
   FHitResult Ceiling;
   if (Height>Before.Z) SetActorLocation(FVector(Before.X,Before.Y,Height),true,&Ceiling);
   if (Ceiling.bBlockingHit) continue;
   Side.Z=GetActorLocation().Z;FHitResult Other;SetActorLocation(Side,true,&Other);
   FVector Support=GetActorLocation();Support.Z=Height;FHitResult SupportHit;SetActorLocation(Support,true,&SupportHit);
   if (FVector::DistSquared2D(Before,GetActorLocation())>FMath::Square(Step*.25f)) { bRouteBlocked=false;break; }
  }
 }
 const bool bMoved=FVector::DistSquared2D(Here,GetActorLocation())>.01f;
 if (bMoved) SetActorRotation(Direction.Rotation());
 SetWalking(bMoved);
}

bool AVillageGolemCitizen::TryPlayerOffer(AIsekaiVillageCharacter* Player)
{
	if (!Village) return false;
 if(Village->bUseOrganicGolemNeeds)
  if(const auto* R=Village->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& X){return X.Id==GolemId;});R && !R->AdventurerId.IsNone())
  { if(GEngine)GEngine->AddOnScreenDebugMessage(-1,6.f,FColor::Cyan,Village->GolemWantLine(GolemId).ToString());return true; }
	const FTownPlot* Work = Village->FindPlot(WorkPlot);
	if (Work && Work->Kind != ETownBuilding::Shop) return Village->WithdrawHallSupplies(Player);
	return Village->TradeWood(WorkPlot, false, Player);
}

FText AVillageGolemCitizen::OfferLine() const
{
	if (CurrentRoutine != EGolemWorkRoutine::None)
	{
		switch (CurrentRoutine)
		{
		case EGolemWorkRoutine::Blacksmith_Hammering:
			return FText::FromString(FString::Printf(TEXT("%s - Blacksmith (Forging iron at anvil)"), *Mind.DisplayName.ToString()));
		case EGolemWorkRoutine::Innkeeper_Hosting:
			return FText::FromString(FString::Printf(TEXT("%s - Innkeeper (Hosting guests at hearth counter)"), *Mind.DisplayName.ToString()));
		case EGolemWorkRoutine::Shopkeeper_Trading:
			return FText::FromString(FString::Printf(TEXT("%s - Merchant (Trading goods at counter)"), *Mind.DisplayName.ToString()));
		case EGolemWorkRoutine::Baker_Baking:
			return FText::FromString(FString::Printf(TEXT("%s - Baker (Baking bread in stone oven)"), *Mind.DisplayName.ToString()));
		case EGolemWorkRoutine::Craftsman_Working:
			return FText::FromString(FString::Printf(TEXT("%s - Artisan (Crafting components at workbench)"), *Mind.DisplayName.ToString()));
		case EGolemWorkRoutine::Sleeping_In_Bed:
			return FText::FromString(FString::Printf(TEXT("%s - Resting (Sleeping in bed)"), *Mind.DisplayName.ToString()));
		default:
			break;
		}
	}
	if (bHarvesting)
	{
		const TCHAR* Verb = (HarvestPlace == EVillagePlace::Lake)
			? TEXT("Fishing at SkyLake")
			: (HarvestPlace == EVillagePlace::Mine ? TEXT("Quarrying stone & ore at Whisperwood Mine") : TEXT("Chopping timber in Whispering Forest"));
		return FText::FromString(FString::Printf(TEXT("%s - %s"), *Mind.DisplayName.ToString(), Verb));
	}
 if(Village && Village->bUseOrganicGolemNeeds)return Village->GolemWantLine(GolemId);
	if (Village) if (const FTownPlot* Work = Village->FindPlot(WorkPlot); Work && Work->Kind != ETownBuilding::Shop)
 {
  const TCHAR* Job=Work->Kind==ETownBuilding::Farm ? TEXT("farmer") : Work->Kind==ETownBuilding::Bakery ? TEXT("baker") : Work->Kind==ETownBuilding::Smith ? TEXT("smith") : TEXT("hall courier");
  return FText::FromString(Mind.DisplayName.ToString()+TEXT(" - ")+Job+TEXT(" | supplies delivered to hall"));
 }
	return FText::FromString(FString::Printf(TEXT("%s - shopkeeper   T: sell wood   Y: buy wood   U: store menu"), *Mind.DisplayName.ToString()));
}

float AVillageGolemCitizen::TakeDamage(float Amount,const FDamageEvent& Event,AController* InstigatorController,AActor* Causer)
{
 if(!CanBeDamaged())return 0;
 if(ActorHasTag(TEXT("ElrhunSparring")))
 {
  for(TActorIterator<AGolemSparring> It(GetWorld());It;++It)
   if(It->Members.ContainsByPredicate([&](const FGolemSparringMember& M){return M.Actor==this;}))return It->ReceiveDamage(this,Amount,Causer);
  return 0;
 }
 return Super::TakeDamage(Amount,Event,InstigatorController,Causer);
}
