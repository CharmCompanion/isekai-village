#include "GolemSparring.h"
#include "TowerExpedition.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "SlimeRunicMagic.h"
#include "ProceduralMagicCircle.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

AGolemSparring::AGolemSparring(){PrimaryActorTick.bCanEverTick=true;}
AGolemSparring* AGolemSparring::FindFor(const AActor* Context)
{
	if(!Context || !Context->GetWorld())return nullptr;
	for(TActorIterator<AGolemSparring> It(Context->GetWorld());It;++It)if(It->Commander==Context)return *It;
	return nullptr;
}
void AGolemSparring::Log(const FString& Message){BattleLog.Add(Message);while(BattleLog.Num()>5)BattleLog.RemoveAt(0);}

UClass* AGolemSparring::SlimeClassForElement(EElement Elem)
{
	switch(Elem)
	{
	case EElement::Fire:return LoadClass<ASlimeRunicMage>(nullptr,TEXT("/Game/IsekaiVillage/Magic/Slimes/BP_FlameSlimeMage.BP_FlameSlimeMage_C"));
	case EElement::Earth:return LoadClass<ASlimeRunicMage>(nullptr,TEXT("/Game/IsekaiVillage/Magic/Slimes/BP_MeadowSlimeMage.BP_MeadowSlimeMage_C"));
	case EElement::Wind:return LoadClass<ASlimeRunicMage>(nullptr,TEXT("/Game/IsekaiVillage/Magic/Slimes/BP_FrostSlimeMage.BP_FrostSlimeMage_C"));
	case EElement::Water:
	default:return LoadClass<ASlimeRunicMage>(nullptr,TEXT("/Game/IsekaiVillage/Magic/Slimes/BP_WaterSlimeMage.BP_WaterSlimeMage_C"));
	}
}
const TCHAR* AGolemSparring::RuneTextureForElement(EElement Elem)
{
	switch(Elem)
	{
	case EElement::Fire:return TEXT("/Game/IsekaiVillage/Magic/Slimes/T_Runes_Flame.T_Runes_Flame");
	case EElement::Earth:return TEXT("/Game/IsekaiVillage/Magic/Slimes/T_Runes_Meadow.T_Runes_Meadow");
	case EElement::Wind:return TEXT("/Game/IsekaiVillage/Magic/Slimes/T_Runes_Frost.T_Runes_Frost");
	case EElement::Water:
	default:return TEXT("/Game/IsekaiVillage/Magic/Slimes/T_Runes_Water.T_Runes_Water");
	}
}
FLinearColor AGolemSparring::ColorForElement(EElement Elem)
{
	switch(Elem)
	{
	case EElement::Fire:return FLinearColor(1.0f,0.35f,0.1f);
	case EElement::Earth:return FLinearColor(0.2f,0.85f,0.3f);
	case EElement::Wind:return FLinearColor(0.2f,0.8f,0.95f);
	case EElement::Water:
	default:return FLinearColor(0.2f,0.5f,1.0f);
	}
}
AProceduralMagicCircle* AGolemSparring::SpawnElementCircle(FVector Location,EElement Elem,float Scale)
{
	FActorSpawnParameters CP;CP.Owner=this;
	auto* Circle=GetWorld()->SpawnActor<AProceduralMagicCircle>(Location,FRotator::ZeroRotator,CP);
	if(Circle)
	{
		Circle->ConfigureRunes(Elem,LoadObject<UTexture2D>(nullptr,RuneTextureForElement(Elem)),ColorForElement(Elem));
		Circle->SetActorScale3D(FVector(Scale,Scale,1.0f));
	}
	return Circle;
}

void AGolemSparring::ApplyMemberStartingBonuses(FGolemSparringMember& M) const
{
	const bool bEmpowered=IsValid(Commander) && Commander->HasSphereSkill(TEXT("RelicEmpowered"));
	const float RelicScale=bEmpowered?1.25f:1.0f;
	M.MaxHealth=100.f+(M.ArmorTier==1?25.f:(M.ArmorTier>=2?50.f:0.f))+static_cast<float>(FMath::Max(0,M.TemperLevel))*10.f;
	if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("FieldRepair")) && (M.WeaponTier>0 || M.ArmorTier>0))
		M.MaxHealth+=10.f;
	if(HasRelic(ETowerRelic::AegisOath))
		M.MaxHealth+=25.f*RelicScale;
	if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("SpiritGuard")))
		M.MaxHealth+=15.f;
	if(IsValid(Village))
	{
		if(Village->ActiveChapelBlessing==TEXT("Grace"))M.MaxHealth+=20.f;
		if(Village->bBathhouseSoakedToday && Village->HasBuilding(ETownBuilding::Bath))M.MaxHealth+=15.f;
		if(Village->AcademyResearchLevel>=3)M.MaxHealth+=20.f;
	}
	M.Health=M.MaxHealth;
	M.TP=40.f+(M.WeaponTier>=2?10.f:0.f);
	if(HasRelic(ETowerRelic::RunicSurge))
		M.TP+=20.f*RelicScale;
	if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("SpiritGuard")))
		M.TP+=10.f;
	if(IsValid(Village))
	{
		if(Village->ActiveChapelBlessing==TEXT("Grace"))M.TP+=15.f;
		if(Village->AcademyResearchLevel>=1)M.TP+=15.f;
	}
}

bool AGolemSparring::BeginSparring(AVillageRuntime* V,AIsekaiVillageCharacter* Player)
{
	if(Phase!=TEXT("Idle") || !HasAuthority() || !V || !Player || !Player->PartyReserve || V->GetWorld()!=GetWorld() || Player->GetWorld()!=GetWorld())return false;
	Village=V;Commander=Player;
	Minions.Reset();ActiveRelics.Reset();SelectedEnemyIndex=0;ActingEnemyIndex=0;
	const FTownPlot* Yard=nullptr;double Best=FMath::Square(650.f);
	for(const FTownPlot& P:V->Plots)if(P.bBuilt && !P.bScenery && P.Kind==ETownBuilding::Training)
	{const double D=FVector::DistSquared2D(Player->GetActorLocation(),P.Location+P.StakeOffset);if(D<Best){Best=D;Yard=&P;}}
	if(!Yard){LastError=TEXT("Stand at a player-built training yard.");return false;}
	if(!V->SparringSlimeClass){LastError=TEXT("The training slime has not been configured.");return false;}
	V->ReconcileGolemPopulation();
	const FVector Out=Yard->StakeOffset.GetSafeNormal2D();
	if(Out.IsNearlyZero()){LastError=TEXT("This yard needs a clear street frontage.");return false;}
	const FVector Front=Yard->Location+Yard->StakeOffset+Out*150.f;
	const FVector Side=FVector::CrossProduct(FVector::UpVector,Out);
	for(const auto& A:Player->PartyReserve->Reserve)
	{
		if(!A.bInActiveParty || A.bAssignedToRampage || Members.Num()>=Player->PartyReserve->GetMaxCompanions())continue;
		const auto* R=V->GolemResidents.FindByPredicate([&](const FVillageGolemRecord& X){return X.AdventurerId==A.AdventurerID && !X.HomePlot.IsNone();});
		if(!R)continue;
		for(TActorIterator<AVillageGolemCitizen> It(GetWorld());It;++It)if(It->GetOwner()==V && It->GolemId==R->Id)
		{FGolemSparringMember M;M.AdventurerId=A.AdventurerID;M.Actor=*It;M.Formation=Front+Side*(Members.Num()*100.f);M.ReadyAt=Members.Num()*.01f;M.WeaponTier=A.WeaponTier;M.ArmorTier=A.ArmorTier;M.TemperLevel=A.TemperLevel;ApplyMemberStartingBonuses(M);Members.Add(M);break;}
	}
	if(Members.IsEmpty()){LastError=TEXT("An active reserve adventurer needs a home and a village actor before sparring.");return false;}
	for(int32 I=0;I<Members.Num();++I)Members[I].Formation=Front+Side*((I-(Members.Num()-1)*.5f)*100.f);
	FCollisionQueryParams Q(SCENE_QUERY_STAT(SparringGround),true,this);Q.AddIgnoredActor(Player);
	for(const auto& M:Members)Q.AddIgnoredActor(M.Actor);
	auto Ground=[&](FVector& P)->bool{FHitResult H;if(!GetWorld()->LineTraceSingleByChannel(H,P+FVector(0,0,300),P-FVector(0,0,400),ECC_Visibility,Q) || H.ImpactNormal.Z<.8f || FMath::Abs(H.ImpactPoint.Z-P.Z)>70.f)return false;P.Z=H.ImpactPoint.Z;return true;};
	EnemyPosition=Front+Out*280.f;
	for(auto& M:Members)if(!Ground(M.Formation)){LastError=TEXT("The training frontage has no safe standing space.");Members.Reset();return false;}
	if(!Ground(EnemyPosition)){LastError=TEXT("The training slime needs a clear, level frontage.");Members.Reset();return false;}
	for(auto& M:Members)
	{M.Actor->Tags.AddUnique(TEXT("ElrhunBattleAssembly"));M.Actor->SetGoal(EVillagePlace::Training,M.Formation);}
	Phase=TEXT("Assembling");Log(TEXT("Adventurers are walking to the training yard. J cancels."));return true;
}
bool AGolemSparring::BeginFieldEncounter(AVillageRuntime* V,AIsekaiVillageCharacter* P,const TArray<AVillageGolemCitizen*>& Allies,FVector EnemyGround,int32 Variant)
{
	if(Phase!=TEXT("Idle") || !HasAuthority() || !V || !P || Allies.IsEmpty() || V->GetWorld()!=GetWorld() || P->GetWorld()!=GetWorld())return false;
	Minions.Reset();ActiveRelics.Reset();SelectedEnemyIndex=0;ActingEnemyIndex=0;
	FCollisionQueryParams Q(SCENE_QUERY_STAT(FieldEncounterGround),true,this);
	Q.AddIgnoredActor(P);for(const auto* A:Allies)Q.AddIgnoredActor(A);
	FHitResult H;
	if(!GetWorld()->LineTraceSingleByChannel(H,EnemyGround+FVector(0,0,400),EnemyGround-FVector(0,0,600),ECC_Visibility,Q) || H.ImpactNormal.Z<.8f)
	{
		LastError=TEXT("No stable ground for the encounter.");return false;
	}
	ActiveRelics=V->TowerFloor.RunRelics;
	Village=V;Commander=P;bFieldEncounter=true;
	const FVector Side=FVector::CrossProduct(FVector::UpVector,(H.ImpactPoint-P->GetActorLocation()).GetSafeNormal2D());
	for(int32 I=0;I<Allies.Num();++I)
	{
		FGolemSparringMember M;
		M.Actor=Allies[I];
		FName AdvId=NAME_None; const FHiredAdventurer* AdvRecord=nullptr;
		if(P && P->PartyReserve)
		{
			if(const auto* A=P->PartyReserve->Reserve.FindByPredicate([&](const auto& X){return X.GolemId==Allies[I]->GolemId;}))
			{ AdvId=A->AdventurerID; AdvRecord=A; }
		}
		if(AdvId.IsNone() && V)
		{
			if(const auto* R=V->GolemResidents.FindByPredicate([&](const auto& X){return X.Id==Allies[I]->GolemId;}))
			{ AdvId=R->AdventurerId; const FName TId=R->AdventurerId; if(P && P->PartyReserve) AdvRecord=P->PartyReserve->Reserve.FindByPredicate([&](const auto& X){return X.AdventurerID==TId;}); }
		}
		M.AdventurerId=AdvId.IsNone()?FName(*(TEXT("Golem_")+Allies[I]->GolemId.ToString(EGuidFormats::Digits))):AdvId;
		M.Formation=P->GetActorLocation()+Side*((I-(Allies.Num()-1)*.5f)*120.f);
		M.ReadyAt=I*.01f;
		if(AdvRecord){M.WeaponTier=AdvRecord->WeaponTier;M.ArmorTier=AdvRecord->ArmorTier;M.TemperLevel=AdvRecord->TemperLevel;}
		ApplyMemberStartingBonuses(M);
		Members.Add(M);
	}
	EnemyPosition=H.ImpactPoint;
	EncounterHealth=80+20*FMath::Clamp(Variant,0,2);
	EncounterDamage=8+2*FMath::Clamp(Variant,0,2);
	if(bHasFloorPlan)
	{
		EncounterHealth*=FloorPlan.Modifiers.HealthMult;
		EncounterDamage*=FloorPlan.Modifiers.DamageMult;
		ShieldLeft=FloorPlan.Modifiers.ShieldHits;
	}
	EncounterLog=FTowerFloorLog();
	EncounterLog.Fights=1;
	EncounterLog.PartySize=Members.Num();
	EncounterLog.PartyMaxHealth=0.f; for(const auto& M:Members) EncounterLog.PartyMaxHealth += M.MaxHealth;
	for(auto& M:Members)M.Actor->Tags.AddUnique(TEXT("ElrhunBattleAssembly"));
	Phase=TEXT("Assembling");
	Log(TEXT("Tower guardian. J retreats; 1-6 command actions. A full party defeat fails the run."));
	if(bHasFloorPlan)Log(FloorPlan.Announcement);
	return true;
}
void AGolemSparring::ApplyFloorPlan(const FTowerFloorPlan& Plan,int32 Seed)
{
	FloorPlan=Plan;bHasFloorPlan=true;TargetRandom.Initialize(Seed);
}
float AGolemSparring::ElementMultiplier(EElement Attack,EElement Defender)
{
	if(UTowerAdaptationLibrary::ElementThatBeats(Defender)==Attack)return 1.5f;
	if(UTowerAdaptationLibrary::ElementThatBeats(Attack)==Defender)return .6f;
	return 1.f;
}
bool AGolemSparring::HasSkill(int32 I,FName Skill) const
{
	if(!Members.IsValidIndex(I) || !IsValid(Commander) || !Commander->PartyReserve)return false;
	const auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==Members[I].AdventurerId;});
	return A && A->Drives.Skills.Contains(Skill);
}
bool AGolemSparring::HasPassive(int32 I,FName Passive) const
{
	if(!Members.IsValidIndex(I) || !IsValid(Commander) || !Commander->PartyReserve)return false;
	const auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==Members[I].AdventurerId;});
	return A && A->Drives.Passives.Contains(Passive);
}
ASlimeRunicMage* AGolemSparring::GetTargetEnemy(int32 Index) const
{
	if(Index==0)return Enemy.Get();
	const int32 K=Index-1;
	return Minions.IsValidIndex(K)?Minions[K].Actor.Get():nullptr;
}
bool AGolemSparring::AllEnemiesDefeated() const
{
	if(IsValid(Enemy) && Enemy->Health>0.f)return false;
	for(const auto& M:Minions)if(IsValid(M.Actor) && M.Actor->Health>0.f)return false;
	return true;
}
bool AGolemSparring::IsCombatEnemy(const AActor* Actor) const
{
	if(!Actor)return false;
	if(Actor==Enemy)return true;
	for(const auto& M:Minions)if(Actor==M.Actor)return true;
	return false;
}
int32 AGolemSparring::LivingMinionCount() const
{
	int32 Count=0;
	for(const auto& M:Minions)if(IsValid(M.Actor) && M.Actor->Health>0.f)++Count;
	return Count;
}
float AGolemSparring::BossWardReduction() const
{
	return (bFieldEncounter && bHasFloorPlan && FloorPlan.bBoss)?FMath::Min(0.40f,0.20f*LivingMinionCount()):0.f;
}
void AGolemSparring::EnsureValidTarget()
{
	if(ASlimeRunicMage* Cur=GetTargetEnemy(SelectedEnemyIndex); IsValid(Cur) && Cur->Health>0.f)return;
	if(IsValid(Enemy) && Enemy->Health>0.f){SelectedEnemyIndex=0;return;}
	for(int32 K=0;K<Minions.Num();++K)
		if(IsValid(Minions[K].Actor) && Minions[K].Actor->Health>0.f){SelectedEnemyIndex=K+1;return;}
}
bool AGolemSparring::SelectEnemyTarget(int32 Index)
{
	if(ASlimeRunicMage* Tgt=GetTargetEnemy(Index); IsValid(Tgt) && Tgt->Health>0.f)
	{
		SelectedEnemyIndex=Index;
		return true;
	}
	return false;
}
bool AGolemSparring::CycleEnemyTarget()
{
	if(Phase==TEXT("Result") || Phase==TEXT("Idle"))return false;
	TArray<int32> Living;
	if(IsValid(Enemy) && Enemy->Health>0.f)Living.Add(0);
	for(int32 K=0;K<Minions.Num();++K)if(IsValid(Minions[K].Actor) && Minions[K].Actor->Health>0.f)Living.Add(K+1);
	if(Living.Num()<=1){EnsureValidTarget();return false;}
	const int32 Pos=Living.IndexOfByKey(SelectedEnemyIndex);
	SelectedEnemyIndex=Living[(Pos==INDEX_NONE?0:(Pos+1)%Living.Num())];
	const FString TargetLabel=SelectedEnemyIndex==0?TEXT("Apex Sentinel"):Minions[SelectedEnemyIndex-1].Label;
	Log(FString::Printf(TEXT("Targeting: %s."),*TargetLabel));
	return true;
}
bool AGolemSparring::SightToEnemy(int32 I,const ASlimeRunicMage* TargetEnemy) const
{
	const ASlimeRunicMage* Tgt=TargetEnemy?TargetEnemy:GetTargetEnemy(SelectedEnemyIndex);
	if(!Members.IsValidIndex(I) || !IsValid(Members[I].Actor) || !IsValid(Tgt) || Tgt->Health<=0.f)return false;
	if(FVector::DistSquared(Members[I].Actor->GetActorLocation(),Tgt->GetActorLocation())>FMath::Square(1500.f))return false;
	FCollisionQueryParams Q(SCENE_QUERY_STAT(SparringSight),false,Members[I].Actor);Q.AddIgnoredActor(Commander);
	for(const auto& M:Members)if(IsValid(M.Actor))Q.AddIgnoredActor(M.Actor);
	if(IsValid(Enemy) && Enemy!=Tgt)Q.AddIgnoredActor(Enemy);
	for(const auto& M:Minions)if(IsValid(M.Actor) && M.Actor!=Tgt)Q.AddIgnoredActor(M.Actor);
	FHitResult H;return !GetWorld()->LineTraceSingleByChannel(H,Members[I].Actor->GetActorLocation(),Tgt->GetActorLocation(),ECC_Visibility,Q) || H.GetActor()==Tgt;
}
void AGolemSparring::Award(FName Id,FName Domain,float Effort)
{
	if(!IsValid(Commander) || !Commander->PartyReserve)return;
	if(auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==Id;}))A->Drives.Fatigue=FMath::Min(100.f,A->Drives.Fatigue+Effort*.25f);
	Commander->PartyReserve->RecordAdventurerPractice(Id,Domain,Effort,true);
}
void AGolemSparring::SelectTurn()
{
	if(IsValid(GuardianCircle) && (!IsValid(Enemy) || Enemy->Health<=0.f)){GuardianCircle->Destroy();GuardianCircle=nullptr;}
	for(auto& MN:Minions)if(IsValid(MN.Circle) && (!IsValid(MN.Actor) || MN.Actor->Health<=0.f)){MN.Circle->Destroy();MN.Circle=nullptr;}
	if(AllEnemiesDefeated())
	{
		bVictory=true;
		Finish(bFieldEncounter?TEXT("Guardian defeated! Take a portal to advance or end the run."):TEXT("Sparring won. No loot or permanent deaths."));
		return;
	}
	bool Alive=false;for(const auto& M:Members)Alive|=IsValid(M.Actor) && M.Health>0;
	if(!Alive)
	{
		bPartyDefeated=true;
		Finish(bFieldEncounter?TEXT("Party defeated. The expedition has failed."):TEXT("Sparring ended. The party needs more practice."));
		return;
	}
	EnsureValidTarget();
	float BestEnemyReadyAt=FLT_MAX;
	ActingEnemyIndex=INDEX_NONE;
	if(IsValid(Enemy) && Enemy->Health>0.f){BestEnemyReadyAt=EnemyReadyAt;ActingEnemyIndex=0;}
	for(int32 K=0;K<Minions.Num();++K)
	{
		if(IsValid(Minions[K].Actor) && Minions[K].Actor->Health>0.f && Minions[K].ReadyAt<BestEnemyReadyAt)
		{
			BestEnemyReadyAt=Minions[K].ReadyAt;
			ActingEnemyIndex=K+1;
		}
	}
	CurrentMember=INDEX_NONE;float Best=BestEnemyReadyAt;
	for(int32 I=0;I<Members.Num();++I)
		if(IsValid(Members[I].Actor) && Members[I].Health>0 && Members[I].ReadyAt<=Best){Best=Members[I].ReadyAt;CurrentMember=I;}
	if(CurrentMember==INDEX_NONE){Phase=TEXT("EnemyTurn");EnemyDelay=.8f;return;}
	Members[CurrentMember].GuardReduction=0;Members[CurrentMember].bEvading=false;Phase=TEXT("AwaitCommand");
}
bool AGolemSparring::ExecuteAction(FName Action,int32 Target)
{
	LastError.Empty();
	auto Fail=[&](const TCHAR* Why){LastError=Why;return false;};
	if(!HasAuthority() || Phase!=TEXT("AwaitCommand") || !Members.IsValidIndex(CurrentMember))return Fail(TEXT("Wait for an adventurer's turn."));
	auto& M=Members[CurrentMember];if(!IsValid(M.Actor) || M.Health<=0)return Fail(TEXT("This adventurer cannot act."));
	float Cost=0,Delay=100;
	if(Action==TEXT("GuardStance")){if(!HasSkill(CurrentMember,Action))return Fail(TEXT("Guard Stance has not been learned."));Cost=4;Delay=70;}
	else if(Action==TEXT("ArcaneBolt")){if(!HasSkill(CurrentMember,Action))return Fail(TEXT("Arcane Bolt has not been learned."));Cost=8;Delay=120;}
	else if(Action==TEXT("FirstAid")){if(!HasSkill(CurrentMember,Action))return Fail(TEXT("First Aid has not been learned."));Cost=6;Delay=110;}
	else if(Action==TEXT("EvasiveStep")){if(!HasSkill(CurrentMember,Action))return Fail(TEXT("Evasive Step has not been learned."));Cost=5;Delay=80;}
	else if(Action==TEXT("Defend"))Delay=70;
	else if(Action!=TEXT("Strike"))return Fail(TEXT("Unknown action."));
	if(HasPassive(CurrentMember,TEXT("FocusedMind")))Cost*=.9f;
	if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("TPConserve")) && Action==TEXT("ArcaneBolt"))Cost*=.85f;
	if(IsValid(Village) && Village->AcademyResearchLevel>=1)Cost*=.85f;
	if(M.TP+KINDA_SMALL_NUMBER<Cost)return Fail(TEXT("Not enough TP."));
	if(Action==TEXT("Strike") || Action==TEXT("ArcaneBolt"))
	{
		EnsureValidTarget();
		ASlimeRunicMage* TargetEnemy=GetTargetEnemy(SelectedEnemyIndex);
		if(!IsValid(TargetEnemy) || TargetEnemy->Health<=0.f || !SightToEnemy(CurrentMember,TargetEnemy))return Fail(TEXT("The slime is out of range or behind cover."));
		const bool bMagic=Action==TEXT("ArcaneBolt");float Amount=bMagic?30.f:20.f;
		const float BonusAtk=(M.WeaponTier==1?6.f:(M.WeaponTier>=2?12.f:0.f))+static_cast<float>(FMath::Max(0,M.TemperLevel))*4.f;
		Amount+=BonusAtk;
		if(IsValid(Commander))
		{
			if(bMagic)
			{
				Amount+=static_cast<float>(Commander->SphereTotals.Magic)*1.5f;
				if(Commander->HasSphereSkill(TEXT("ArcaneSurge")))Amount*=1.2f;
			}
			else
			{
				Amount+=static_cast<float>(Commander->SphereTotals.Attack)*1.5f;
				if(Commander->HasSphereSkill(TEXT("BeastRoar")))Amount+=6.f;
				if(Commander->HasSphereSkill(TEXT("FieldRepair")) && M.WeaponTier>0)Amount+=4.f;
			}
			if(Commander->HasSphereSkill(TEXT("SoulResonance")))Amount+=8.f;
		}
		if(HasRelic(ETowerRelic::BerserkerBrand))
			Amount*=(IsValid(Commander) && Commander->HasSphereSkill(TEXT("RelicEmpowered")))?1.44f:1.35f;
		if(IsValid(Village))
		{
			if(Village->ActiveChapelBlessing==TEXT("Valor"))Amount*=1.15f;
			if(bMagic && Village->AcademyResearchLevel>=2)Amount*=1.15f;
			if(Village->AcademyResearchLevel>=3)Amount*=1.10f;
			if(Village->HasBuilding(ETownBuilding::Castle))Amount*=1.10f;
		}
		EElement SpellElem=(IsValid(Commander) && Commander->HasSphereSkill(TEXT("ElementLink")))?Commander->ActiveElement:EElement::Water;
		const bool bTargetingMinion=(SelectedEnemyIndex>0 && Minions.IsValidIndex(SelectedEnemyIndex-1));
		if(bHasFloorPlan || bTargetingMinion)
		{
			const FTowerEncounterModifiers EmptyMods;
			const auto& Mods=bHasFloorPlan?FloorPlan.Modifiers:EmptyMods;
			if(bHasFloorPlan)Amount*=bMagic?Mods.MagicTakenMult:Mods.PhysicalTakenMult;
			const bool bTargetHasElem=bTargetingMinion || (bHasFloorPlan && FloorPlan.bHasElement);
			const EElement TargetElem=bTargetingMinion?Minions[SelectedEnemyIndex-1].Element:FloorPlan.EnemyElement;
			if(bMagic && bTargetHasElem)
			{
				if(IsValid(Commander) && Commander->PartyReserve)
				{
					if(const auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const auto& X){return X.AdventurerID==M.AdventurerId;}))
					{
						if(A->ClassId==TEXT("Mage") || A->Drives.Interest==TEXT("Magic"))
							SpellElem=UTowerAdaptationLibrary::ElementThatBeats(TargetElem);
					}
				}
				const float Mult=ElementMultiplier(SpellElem,TargetElem);
				Amount*=Mult;
				if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("ElementLink")))Amount*=1.2f;
				if(Mult>1.2f)
				{
					if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("MasterHunter")))Amount*=1.15f;
					Log(TEXT("Super effective! Elemental spell pierces the rune (+50% damage, target staggered!)."));
					if(bTargetingMinion)Minions[SelectedEnemyIndex-1].ReadyAt+=40.f;
					else EnemyReadyAt+=40.f;
					M.TP=FMath::Min(100.f,M.TP+15.f);
				}
				else if(Mult<0.8f)Log(TEXT("Resisted! The target's element blunts the spell (-40% damage)."));
			}
			else if(!bMagic && IsValid(Commander) && Commander->PartyReserve)
			{
				if(const auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const auto& X){return X.AdventurerID==M.AdventurerId;}))
				{
					if(A->ClassId==TEXT("Ranger") || A->Drives.Interest==TEXT("Scout"))
					{
						const float CritChance=Commander->HasSphereSkill(TEXT("BowSpread"))?0.45f:0.25f;
						if(TargetRandom.FRand()<CritChance)
						{
							Amount*=Commander->HasSphereSkill(TEXT("MasterHunter"))?1.65f:1.5f;
							Log(TEXT("Critical strike! The ranger finds an exposed weak point (+50% damage)."));
						}
					}
				}
			}
			if(bHasFloorPlan && Mods.bFocusCarry && !FloorPlan.CarryId.IsNone() && M.AdventurerId!=FloorPlan.CarryId)Amount*=Mods.SupportDamageMult;
		}
		if(IsValid(Commander) && Commander->HasSphereSkill(TEXT("EchoBreaker")) && ((bHasFloorPlan && (FloorPlan.bBoss || FloorPlan.Floor<0)) || bTargetingMinion))
			Amount*=1.25f;
		float Damage=0;
		if(!bTargetingMinion)
		{
			if(ShieldLeft>0){--ShieldLeft;Log(FString::Printf(TEXT("A tower shield absorbs the blow (%d left)."),ShieldLeft));}
			else if(bEnemyEvading){bEnemyEvading=false;Log(TEXT("The slime copies your evasion and slips the blow."));}
			else
			{
				const float WardRed=BossWardReduction();
				if(WardRed>0.f)Amount*=(1.f-WardRed);
				Amount*=1-EnemyGuard;EnemyGuard=0;
				Damage=UGameplayStatics::ApplyDamage(TargetEnemy,Amount,Commander->GetController(),M.Actor,nullptr);
				if(Damage<=0)return Fail(TEXT("The target did not receive damage."));
				if(WardRed>0.f)
					Log(FString::Printf(TEXT("%s: %s hits Apex Sentinel for %.0f (warded -%.0f%%)."),*M.Actor->Mind.DisplayName.ToString(),bMagic?TEXT("Arcane Bolt"):TEXT("Strike"),Damage,WardRed*100.f));
				else
					Log(FString::Printf(TEXT("%s: %s hits for %.0f."),*M.Actor->Mind.DisplayName.ToString(),bMagic?TEXT("Arcane Bolt"):TEXT("Strike"),Damage));
				if(TargetEnemy->Health<=0.f)
				{
					if(IsValid(GuardianCircle)){GuardianCircle->Destroy();GuardianCircle=nullptr;}
					if(!AllEnemiesDefeated())Log(TEXT("Apex Sentinel has fallen! Defeat the remaining acolytes!"));
					EnsureValidTarget();
				}
			}
		}
		else
		{
			const int32 K=SelectedEnemyIndex-1;
			Damage=UGameplayStatics::ApplyDamage(TargetEnemy,Amount,Commander->GetController(),M.Actor,nullptr);
			if(Damage<=0)return Fail(TEXT("The target did not receive damage."));
			Minions[K].Health=TargetEnemy->Health;
			Log(FString::Printf(TEXT("%s: %s hits %s for %.0f."),*M.Actor->Mind.DisplayName.ToString(),bMagic?TEXT("Arcane Bolt"):TEXT("Strike"),*Minions[K].Label,Damage));
			if(TargetEnemy->Health<=0.f)
			{
				if(IsValid(Minions[K].Circle)){Minions[K].Circle->Destroy();Minions[K].Circle=nullptr;}
				Log(FString::Printf(TEXT("%s defeated!"),*Minions[K].Label));
				if(IsValid(Enemy) && Enemy->Health>0.f && LivingMinionCount()==0)
					Log(TEXT("All acolytes defeated! The Apex Sentinel's runic ward is broken!"));
				EnsureValidTarget();
			}
		}
		Award(M.AdventurerId,bMagic?FName(TEXT("Magic")):FName(TEXT("Guard")),1);
		EncounterLog.Add(bMagic?ETowerHabit::Magic:ETowerHabit::Physical);if(bMagic)EncounterLog.Add(ETowerHabit::Water);
		EncounterLog.MemberDamage.FindOrAdd(M.AdventurerId)+=Damage;
		if(Action==TEXT("ArcaneBolt"))
		{
			if(auto* Circle=SpawnElementCircle(M.Actor->GetActorLocation()-FVector(0,0,95),SpellElem,1.0f))
			{
				Circle->ActivateSpellBurst(false);Circle->SetLifeSpan(1.2f);
			}
		}
	}
	else if(Action==TEXT("FirstAid"))
	{
		const bool bCanRevive=IsValid(Commander) && Commander->HasSphereSkill(TEXT("ReviveGrace"));
		if(Target==INDEX_NONE)
		{
			float Lowest=9999.f;
			for(int32 I=0;I<Members.Num();++I)if(Members[I].Health>0 && Members[I].Health<Members[I].MaxHealth && Members[I].Health<Lowest){Lowest=Members[I].Health;Target=I;}
			if(Target==INDEX_NONE && bCanRevive)
			{
				for(int32 I=0;I<Members.Num();++I)if(IsValid(Members[I].Actor) && Members[I].Health<=0){Target=I;break;}
			}
		}
		if(!Members.IsValidIndex(Target) || !IsValid(Members[Target].Actor))return Fail(TEXT("Choose a valid ally."));
		if(Members[Target].Health<=0)
		{
			if(!bCanRevive)return Fail(TEXT("Choose a living ally with missing health."));
		}
		else if(Members[Target].Health>=Members[Target].MaxHealth)return Fail(TEXT("Choose a living ally with missing health."));
		if(FVector::DistSquared(M.Actor->GetActorLocation(),Members[Target].Actor->GetActorLocation())>FMath::Square(1000.f))return Fail(TEXT("That ally is out of healing range."));
		if(Members[Target].Health<=0 && bCanRevive)
		{
			const float ReviveHP=FMath::Max(10.f,Members[Target].MaxHealth*0.35f);
			Members[Target].Health=ReviveHP;
			Members[Target].ReadyAt=M.ReadyAt+50.f;
			Award(M.AdventurerId,TEXT("Aid"),1);Log(FString::Printf(TEXT("Revive Grace restores %s (%.0f HP)!"),*Members[Target].Actor->Mind.DisplayName.ToString(),ReviveHP));
			EncounterLog.Add(ETowerHabit::Healing);M.bHealer=true;
		}
		else
		{
			float Heal=(HasPassive(CurrentMember,TEXT("CalmCore"))?27.5f:25.f)*(bHasFloorPlan?FloorPlan.Modifiers.HealingMult:1.f);
			if(bHasFloorPlan && IsValid(Commander) && Commander->PartyReserve)
			{
				if(const auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const auto& X){return X.AdventurerID==M.AdventurerId;}))
					if(A->ClassId==TEXT("Healer") || A->Drives.Interest==TEXT("Aid"))
						Heal+=10.f;
			}
			if(IsValid(Commander))
			{
				if(Commander->HasSphereSkill(TEXT("SacredHeal")))Heal*=1.35f;
				if(Commander->HasSphereSkill(TEXT("SoulResonance")))Heal*=1.15f;
			}
			const float Healed=FMath::Min(Members[Target].MaxHealth-Members[Target].Health,Heal);
			Members[Target].Health+=Healed;Award(M.AdventurerId,TEXT("Aid"),1);Log(FString::Printf(TEXT("First Aid restores %.0f health."),Healed));
			EncounterLog.Add(ETowerHabit::Healing);M.bHealer=true;
		}
	}
	else if(Action==TEXT("EvasiveStep")){M.bEvading=true;EncounterLog.Add(ETowerHabit::Evasion);Log(TEXT("Evasive Step is ready for the next incoming attack."));}
	else
	{
		M.GuardReduction=(Action==TEXT("GuardStance")?.65f:.25f)*(bHasFloorPlan?FloorPlan.Modifiers.GuardMult:1.f);EncounterLog.Add(ETowerHabit::Guard);
		Log(Action==TEXT("GuardStance")?TEXT("Guard Stance raised."):TEXT("Defending."));
	}
	const bool bEmpowered=IsValid(Commander) && Commander->HasSphereSkill(TEXT("RelicEmpowered"));
	const float SpeedMult=(HasPassive(CurrentMember,TEXT("FleetFooted"))?1.1f:1.f)*(HasRelic(ETowerRelic::RunicSurge)?(bEmpowered?1.19f:1.15f):1.f)*((IsValid(Commander) && Commander->HasSphereSkill(TEXT("SummonHaste")))?1.15f:1.f);
	++EncounterLog.Actions;M.TP=FMath::Max(0.f,M.TP-Cost);M.ReadyAt+=Delay/SpeedMult;SelectTurn();return true;
}
float AGolemSparring::ReceiveDamage(AVillageGolemCitizen* Actor,float Amount,AActor* Source)
{
	if(Phase!=TEXT("EnemyTurn") || !IsCombatEnemy(Source) || !FMath::IsFinite(Amount) || Amount<=0)return 0;
	const int32 I=Members.IndexOfByPredicate([&](const FGolemSparringMember& M){return M.Actor==Actor;});
	if(I==INDEX_NONE || Members[I].Health<=0)return 0;auto& M=Members[I];
	if(M.bEvading)
	{
		M.bEvading=false;
		if(!bHasFloorPlan || !FloorPlan.Modifiers.bSureHit){Award(M.AdventurerId,TEXT("Scout"),1);Log(TEXT("The incoming strike was evaded."));return 0;}
		Log(TEXT("A sure strike ignores the evasion."));
	}
	const float ArmorGuard=(M.ArmorTier==1?0.10f:(M.ArmorTier>=2?0.20f:0.f))+static_cast<float>(FMath::Clamp(M.TemperLevel,0,2))*0.05f;
	const float RelicGuard=HasRelic(ETowerRelic::AegisOath)?((IsValid(Commander) && Commander->HasSphereSkill(TEXT("RelicEmpowered")))?0.19f:0.15f):0.f;
	const float SphereGuard=(IsValid(Commander) && Commander->HasSphereSkill(TEXT("AegisBarrier"))?0.10f:0.f)+(IsValid(Commander)?Commander->SphereTotals.ResPercent/200.f:0.f);
	const float TownGuard=(IsValid(Village)
		? ((Village->ActiveChapelBlessing==TEXT("Bulwark")?0.15f:0.f)+(Village->AcademyResearchLevel>=3?0.12f:0.f)+(Village->HasBuilding(ETownBuilding::Castle)?0.10f:0.f))
		: 0.f);
	const float EffectiveGuard=FMath::Clamp(M.GuardReduction+ArmorGuard+RelicGuard+SphereGuard+TownGuard,0.f,0.90f);
	const float BerserkTaken=HasRelic(ETowerRelic::BerserkerBrand)?1.15f:1.f;
	float Applied=FMath::Min(M.Health,Amount*BerserkTaken*(1.f-EffectiveGuard)*(HasPassive(I,TEXT("EnduringCore"))?.9f:1.f));
	if(Applied>=M.Health && M.Health>1.f && !M.bVesselAnchorUsed && IsValid(Commander) && Commander->HasSphereSkill(TEXT("VesselAnchor")))
	{
		M.bVesselAnchorUsed=true;
		Applied=M.Health-1.f;
		M.Health=1.f;
		Log(FString::Printf(TEXT("Vessel Anchor preserves %s at 1 HP!"),*Actor->Mind.DisplayName.ToString()));
	}
	else
	{
		M.Health-=Applied;
	}
	if(M.GuardReduction>0)Award(M.AdventurerId,TEXT("Guard"),1);
	EncounterLog.DamageTaken+=Applied;if(M.Health<=0)++EncounterLog.Knockouts;
	Log(FString::Printf(TEXT("%s strikes %s for %.1f."),Source==Enemy?TEXT("Slime"):TEXT("Acolyte"),*Actor->Mind.DisplayName.ToString(),Applied));return Applied;
}
int32 AGolemSparring::PickEnemyTarget()
{
	TArray<int32> Alive;
	for(int32 I=0;I<Members.Num();++I)if(Members[I].Health>0)Alive.Add(I);
	if(Alive.IsEmpty())return INDEX_NONE;
	auto Lowest=[&](auto Pred){int32 Target=INDEX_NONE;float MinHP=MAX_flt;for(int32 I:Alive)if(Pred(Members[I]) && Members[I].Health<MinHP){MinHP=Members[I].Health;Target=I;}return Target;};
	if(!bHasFloorPlan)
	{
		int32 Target=INDEX_NONE;float Best=-1;
		for(int32 I:Alive){const float Priority=(Members[I].GuardReduction>0?200.f:0.f)+Members[I].MaxHealth-Members[I].Health;if(Priority>Best){Best=Priority;Target=I;}}
		return Target;
	}
	if(FloorPlan.Modifiers.bFocusCarry)for(int32 I:Alive)if(Members[I].AdventurerId==FloorPlan.CarryId)return I;
	switch(FloorPlan.Intelligence)
	{
	case ETowerIntelligence::Instinct:return Alive[TargetRandom.RandRange(0,Alive.Num()-1)];
	case ETowerIntelligence::Hunter:return Lowest([](const FGolemSparringMember&){return true;});
	default:
		{
			const int32 Healer=Lowest([](const FGolemSparringMember& M){return M.bHealer;});if(Healer!=INDEX_NONE)return Healer;
			const int32 Open=Lowest([](const FGolemSparringMember& M){return M.GuardReduction<=0;});
			return Open!=INDEX_NONE?Open:Lowest([](const FGolemSparringMember&){return true;});
		}
	}
}
void AGolemSparring::EnemyTurn()
{
	++EnemyTurns;float Damage=EncounterDamage;
	if(bHasFloorPlan)
	{
		Damage*=1+FloorPlan.Modifiers.EnrageStep*(EnemyTurns-1);
		if(FloorPlan.Intelligence==ETowerIntelligence::Mimic && EnemyTurns%3==0)
		{
			switch(FloorPlan.MimicHabit)
			{
			case ETowerHabit::Guard:EnemyGuard=.5f;Log(TEXT("The slime copies your guard."));EnemyReadyAt+=70;return;
			case ETowerHabit::Evasion:bEnemyEvading=true;Log(TEXT("The slime copies your evasion."));EnemyReadyAt+=80;return;
			case ETowerHabit::Healing:
				{const float Healed=FMath::Min(Enemy->MaxHealth-Enemy->Health,Enemy->MaxHealth*.12f);Enemy->Health+=Healed;Log(FString::Printf(TEXT("The slime copies your healing: +%.0f."),Healed));EnemyReadyAt+=110;return;}
			default:Damage*=1.5f;Log(TEXT("The slime copies your favourite attack."));break;
			}
		}
	}
	const int32 Target=PickEnemyTarget();
	if(Target!=INDEX_NONE && Members.IsValidIndex(Target) && Members[Target].Actor)
	{
		const FString TargetName=Members[Target].Actor->Mind.DisplayName.ToString();
		if(bHasFloorPlan)
		{
			if(FloorPlan.Modifiers.bFocusCarry && FloorPlan.CarryId==Members[Target].AdventurerId)
				Log(FString::Printf(TEXT("The hunter corners your party's carry (%s)!"),*TargetName));
			else if(FloorPlan.Intelligence==ETowerIntelligence::Hunter)
				Log(FString::Printf(TEXT("The hunter strikes the wounded %s!"),*TargetName));
			else if(FloorPlan.Intelligence==ETowerIntelligence::Tactician)
			{
				if(Members[Target].bHealer)Log(FString::Printf(TEXT("The tactician focuses your healer (%s)!"),*TargetName));
				else Log(FString::Printf(TEXT("The tactician finds an unguarded opening on %s!"),*TargetName));
			}
		}
		UGameplayStatics::ApplyDamage(Members[Target].Actor,Damage,nullptr,Enemy,nullptr);
	}
	EnemyReadyAt+=100*(bHasFloorPlan?FloorPlan.Modifiers.EnemyRecoveryMult:1.f);
}
void AGolemSparring::MinionTurn(int32 MinionIdx)
{
	if(!Minions.IsValidIndex(MinionIdx))return;
	auto& MN=Minions[MinionIdx];
	if(!IsValid(MN.Actor) || MN.Actor->Health<=0.f)return;
	++MN.Turns;
	if(IsValid(Enemy) && Enemy->Health>0.f && MN.Turns%3==0 && EnemyGuard<0.35f)
	{
		EnemyGuard=FMath::Max(EnemyGuard,0.35f);
		Log(FString::Printf(TEXT("%s weaves a runic shield onto the Apex Sentinel (+35%% guard)!"),*MN.Label));
	}
	else
	{
		const int32 Target=PickEnemyTarget();
		if(Target!=INDEX_NONE && Members.IsValidIndex(Target) && Members[Target].Actor)
		{
			UGameplayStatics::ApplyDamage(Members[Target].Actor,MN.Damage,nullptr,MN.Actor,nullptr);
		}
	}
	MN.ReadyAt+=110.f*(bHasFloorPlan?FloorPlan.Modifiers.EnemyRecoveryMult:1.f);
}
void AGolemSparring::SpawnBossMinions()
{
	if(!bFieldEncounter || !bHasFloorPlan || !FloorPlan.bBoss || Members.IsEmpty() || !IsValid(Members[0].Actor))return;
	const int32 NumMinions=(FloorPlan.Floor>=10 || FloorPlan.Floor<0)?2:1;
	const EElement BossElem=FloorPlan.bHasElement?FloorPlan.EnemyElement:EElement::Earth;
	FVector ForwardToPlayer=(Members[0].Actor->GetActorLocation()-EnemyPosition).GetSafeNormal2D();
	if(ForwardToPlayer.IsNearlyZero())ForwardToPlayer=FVector(0,-1,0);
	FVector Right=FVector::CrossProduct(FVector::UpVector,ForwardToPlayer).GetSafeNormal2D();
	if(Right.IsNearlyZero())Right=FVector::RightVector;
	static const TCHAR* MinionNames[]={TEXT("Flame Acolyte"),TEXT("Tide Acolyte"),TEXT("Meadow Acolyte"),TEXT("Frost Acolyte")};
	for(int32 K=0;K<NumMinions;++K)
	{
		const EElement MinionElem=(EElement)(((int32)BossElem+1+K)%4);
		const bool bAllowBP=!GIsAutomationTesting && (!Village || Village->SparringSlimeClass!=ASlimeRunicMage::StaticClass());
		UClass* MClass=bAllowBP?SlimeClassForElement(MinionElem):nullptr;
		if(!MClass)MClass=(Village && Village->SparringSlimeClass)?Village->SparringSlimeClass.Get():ASlimeRunicMage::StaticClass();
		const float SideSign=(K==0)?1.f:-1.f;
		const FVector MPos=EnemyPosition+Right*(SideSign*260.f)+ForwardToPlayer*80.f;
		FActorSpawnParameters MP;MP.Owner=this;MP.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
		if(ASlimeRunicMage* MinionActor=GetWorld()->SpawnActor<ASlimeRunicMage>(MClass,MPos+FVector(0,0,45),FRotator::ZeroRotator,MP))
		{
			const float MHP=FMath::Clamp(EncounterHealth*0.22f,35.f,65.f);
			const float MDmg=FMath::Max(4.f,EncounterDamage*0.35f);
			MinionActor->bAutoCast=false;MinionActor->bTargetPlayer=false;
			MinionActor->MaxHealth=MHP;MinionActor->Health=MHP;
			MinionActor->GetCharacterMovement()->DisableMovement();
			MinionActor->SetActorScale3D(FVector(0.95f));
			MinionActor->SetActorRotation((Members[0].Actor->GetActorLocation()-MinionActor->GetActorLocation()).Rotation());
			FGolemSparringEnemy Entry;
			Entry.Actor=MinionActor;
			Entry.Circle=SpawnElementCircle(MPos+FVector(0,0,5),MinionElem,1.3f);
			Entry.Label=MinionNames[(int32)MinionElem];
			Entry.Element=MinionElem;
			Entry.Health=MHP;
			Entry.MaxHealth=MHP;
			Entry.Damage=MDmg;
			Entry.ReadyAt=30.f+15.f*K;
			Minions.Add(Entry);
		}
	}
}
void AGolemSparring::Tick(float D)
{
	Super::Tick(D);
	if(!IsValid(Commander) || !IsValid(Village)){if(Phase!=TEXT("Result"))Finish(TEXT("Sparring stopped."));return;}
	if(Phase==TEXT("Assembling"))
	{
		AssemblyTime+=D;bool Arrived=true;
		for(auto& M:Members)
		{
			if(!IsValid(M.Actor)){Finish(TEXT("An adventurer is no longer available."));return;}
			if(!bFieldEncounter)
			{
				M.Actor->SetGoal(EVillagePlace::Training,M.Formation);
				Arrived&=FVector::DistSquared2D(M.Actor->GetActorLocation(),M.Formation)<FMath::Square(80.f);
			}
		}
		if(!bFieldEncounter && AssemblyTime>300){Finish(TEXT("Assembly timed out. Clear the route and try again."));return;}
		if(!Arrived)return;
		const bool bAllowBP=!GIsAutomationTesting && (!Village || Village->SparringSlimeClass!=ASlimeRunicMage::StaticClass());
		UClass* SlimeClass=nullptr;
		if(bFieldEncounter && bHasFloorPlan && bAllowBP)
		{
			if(FloorPlan.bBoss)
				SlimeClass=LoadClass<ASlimeRunicMage>(nullptr,TEXT("/Game/IsekaiVillage/Magic/Slimes/BP_CrystalSlimeMage.BP_CrystalSlimeMage_C"));
			else if(FloorPlan.bHasElement)
				SlimeClass=SlimeClassForElement(FloorPlan.EnemyElement);
		}
		if(!SlimeClass)SlimeClass=(Village && Village->SparringSlimeClass)?Village->SparringSlimeClass.Get():ASlimeRunicMage::StaticClass();
		FActorSpawnParameters P;P.Owner=this;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AdjustIfPossibleButDontSpawnIfColliding;
		Enemy=GetWorld()->SpawnActor<ASlimeRunicMage>(SlimeClass,EnemyPosition+FVector(0,0,45),FRotator::ZeroRotator,P);
		if(!Enemy){Finish(TEXT("No safe space for the training slime."));return;}
		Enemy->bAutoCast=false;Enemy->bTargetPlayer=false;Enemy->MaxHealth=EncounterHealth;Enemy->Health=EncounterHealth;Enemy->GetCharacterMovement()->DisableMovement();
		float SlimeScale=1.0f;
		if(bHasFloorPlan)
		{
			if(FloorPlan.bBoss)SlimeScale=1.6f;
			else if(FloorPlan.Intelligence==ETowerIntelligence::Mimic)SlimeScale=1.3f;
			else if(FloorPlan.Intelligence==ETowerIntelligence::Tactician)SlimeScale=1.15f;
			else if(FloorPlan.Intelligence==ETowerIntelligence::Hunter)SlimeScale=1.05f;
		}
		Enemy->SetActorScale3D(FVector(SlimeScale));
		const EElement CircleElem=FloorPlan.bHasElement?FloorPlan.EnemyElement:(FloorPlan.bBoss?EElement::Earth:(FloorPlan.Intelligence==ETowerIntelligence::Mimic?EElement::Wind:EElement::Water));
		GuardianCircle=SpawnElementCircle(EnemyPosition+FVector(0,0,5),CircleElem,FloorPlan.bBoss?2.4f:1.6f*SlimeScale);
		SpawnBossMinions();
		if(!Minions.IsEmpty() && IsValid(Enemy)){Enemy->MaxHealth*=0.75f;Enemy->Health=Enemy->MaxHealth;EncounterDamage*=0.75f;}
		for(auto& M:Members){M.Actor->Tags.Remove(TEXT("ElrhunBattleAssembly"));M.Actor->Tags.AddUnique(TEXT("ElrhunSparring"));M.Actor->SetActorRotation((Enemy->GetActorLocation()-M.Actor->GetActorLocation()).Rotation());}
		Enemy->SetActorRotation((Members[0].Actor->GetActorLocation()-Enemy->GetActorLocation()).Rotation());
		if(!Minions.IsEmpty())
			Log(FString::Printf(TEXT("Boss acolytes (%d) project a %.0f%% runic ward onto the Apex Sentinel! Tab switches targets."),Minions.Num(),BossWardReduction()*100.f));
		else
			Log(bFieldEncounter?TEXT("Guardian battle begins. Choose an action when your adventurer is ready."):TEXT("Sparring begins. Choose an action when your adventurer is ready."));
		SelectTurn();
	}
	else if(Phase==TEXT("EnemyTurn"))
	{
		EnemyDelay-=FMath::Max(0.f,D);if(EnemyDelay>0)return;
		ASlimeRunicMage* ActingActor=GetTargetEnemy(ActingEnemyIndex);
		if(!IsValid(ActingActor) || ActingActor->Health<=0.f){SelectTurn();return;}
		if(ActingEnemyIndex==0)EnemyTurn();
		else MinionTurn(ActingEnemyIndex-1);
		SelectTurn();
	}
	else if(Phase==TEXT("AwaitCommand") && AllEnemiesDefeated())SelectTurn();
}
void AGolemSparring::ReleaseMembers()
{
	if(bReleased)return;bReleased=true;
	for(auto& M:Members)
	{
		if(IsValid(M.Actor)){M.Actor->Tags.Remove(TEXT("ElrhunBattleAssembly"));M.Actor->Tags.Remove(TEXT("ElrhunSparring"));}
		if(IsValid(Commander) && Commander->PartyReserve)
			if(auto* A=Commander->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==M.AdventurerId;}))
			{
				A->Drives.Activity=TEXT("Work");A->Drives.ThinkIn=0;A->Drives.Commitment=0;
				if(IsValid(Village))for(auto& R:Village->GolemResidents)if(R.AdventurerId==M.AdventurerId)R.Drives=A->Drives;
			}
	}
	if(IsValid(GuardianCircle)){GuardianCircle->Destroy();GuardianCircle=nullptr;}
	if(IsValid(Enemy)){Enemy->Destroy();Enemy=nullptr;}
	for(auto& MN:Minions)
	{
		if(IsValid(MN.Circle)){MN.Circle->Destroy();MN.Circle=nullptr;}
		if(IsValid(MN.Actor)){MN.Actor->Destroy();MN.Actor=nullptr;}
	}
	Minions.Reset();
}
void AGolemSparring::Finish(const FString& Result)
{
	Phase=TEXT("Result");CurrentMember=INDEX_NONE;Log(Result);ReleaseMembers();
	if(IsValid(Village) && IsValid(Commander))
	{
		auto* Tower=Cast<ATowerExpedition>(GetOwner());const bool Clear=bFieldEncounter && bVictory && Tower && Tower->bInside && Tower->Commander==Commander && Tower->GuardianBattle==this;
		if(Clear){if(!Tower->CommitGuardianClear(EncounterLog))LastError=TEXT("Guardian clear could not save. Leave this result open while saving retries.");}
		else Village->SaveVillageState(Commander);
	}
}
void AGolemSparring::CancelSparring(){if(Phase!=TEXT("Result"))Finish(TEXT("Sparring stopped. Training progress kept."));else Destroy();}
void AGolemSparring::EndPlay(const EEndPlayReason::Type Reason){ReleaseMembers();Super::EndPlay(Reason);}
FText AGolemSparring::BattleLine() const
{
	FString Text=bFieldEncounter?TEXT("TOWER GUARDIAN | J retreat / close\n"):TEXT("TRAINING SPARRING | J stop / close\n");
	if(bHasFloorPlan)
	{
		static const TCHAR* Minds[]={TEXT("Instinct"),TEXT("Hunter"),TEXT("Tactician"),TEXT("Mimic")};
		static const TCHAR* Elems[]={TEXT("Fire"),TEXT("Water"),TEXT("Earth"),TEXT("Wind")};
		const FString ElemName=FloorPlan.bHasElement?Elems[(int32)FloorPlan.EnemyElement]:TEXT("");
		if(FloorPlan.bBoss)
		{
			if(FloorPlan.Floor==10)
				Text+=FString::Printf(TEXT("Floor 10 Apex Exam | The Crazed Immortal Wizard [%s]"),Minds[(int32)FloorPlan.Intelligence]);
			else
				Text+=FString::Printf(TEXT("Floor %d exam | %s Apex Sentinel [%s]"),FloorPlan.Floor,ElemName.IsEmpty()?TEXT("Crucible"):*ElemName,Minds[(int32)FloorPlan.Intelligence]);
		}
		else
			Text+=FString::Printf(TEXT("Floor %d%s | %s"),FloorPlan.Floor,FloorPlan.bBoss?TEXT(" exam"):TEXT(""),Minds[(int32)FloorPlan.Intelligence]);
		if(!FloorPlan.bBoss && FloorPlan.bHasElement)Text+=TEXT(" | ")+ElemName;
		if(ShieldLeft>0)Text+=FString::Printf(TEXT(" | shield %d"),ShieldLeft);
		const float Ward=BossWardReduction();
		if(Ward>0.f)Text+=FString::Printf(TEXT(" | Ward -%.0f%%"),Ward*100.f);
		Text+=TEXT("\n");
	}
	if(Phase==TEXT("Assembling"))Text+=TEXT("Waiting for adventurers to walk into formation.\n");
	for(int32 I=0;I<Members.Num();++I)Text+=FString::Printf(TEXT("%s%s  HP %.0f/%.0f  TP %.1f/%.0f\n"),I==CurrentMember?TEXT("> "):TEXT("  "),IsValid(Members[I].Actor)?*Members[I].Actor->Mind.DisplayName.ToString():TEXT("Unavailable"),Members[I].Health,Members[I].MaxHealth,Members[I].TP,(Members[I].WeaponTier>=2?50.f:40.f)+(HasRelic(ETowerRelic::RunicSurge)?20.f:0.f));
	if(IsValid(Enemy) && (Enemy->Health>0.f || !Minions.IsEmpty()))
	{
		const FString BossTitle=(FloorPlan.Floor==10)?TEXT("Crazed Immortal Wizard"):TEXT("Apex Sentinel");
		const FString BossTag=Minions.IsEmpty()?TEXT("Enemy"):(SelectedEnemyIndex==0?FString::Printf(TEXT("* %s"),*BossTitle):FString::Printf(TEXT("  %s"),*BossTitle));
		if(Enemy->Health>0.f)Text+=FString::Printf(TEXT("%s  HP %.0f/%.0f\n"),*BossTag,Enemy->Health,Enemy->MaxHealth);
		else if(!Minions.IsEmpty())Text+=FString::Printf(TEXT("  %s  [DEFEATED]\n"),*BossTitle);
	}
	for(int32 K=0;K<Minions.Num();++K)
	{
		const auto& MN=Minions[K];
		const bool bAlive=IsValid(MN.Actor) && MN.Actor->Health>0.f;
		const FString Mark=(SelectedEnemyIndex==K+1)?TEXT("* "):TEXT("  ");
		if(bAlive)Text+=FString::Printf(TEXT("%s%s  HP %.0f/%.0f\n"),*Mark,*MN.Label,MN.Actor->Health,MN.MaxHealth);
		else Text+=FString::Printf(TEXT("  %s  [DEFEATED]\n"),*MN.Label);
	}
	if(Phase==TEXT("AwaitCommand") || Phase==TEXT("EnemyTurn"))
	{
		TArray<TPair<float,FString>> Order;
		for(const auto& M:Members)if(M.Health>0 && IsValid(M.Actor))Order.Emplace(M.ReadyAt,M.Actor->Mind.DisplayName.ToString());
		if(IsValid(Enemy) && Enemy->Health>0.f)Order.Emplace(EnemyReadyAt,Minions.IsEmpty()?TEXT("Slime"):TEXT("Sentinel"));
		for(const auto& MN:Minions)if(IsValid(MN.Actor) && MN.Actor->Health>0.f)Order.Emplace(MN.ReadyAt,MN.Label);
		Order.StableSort([](const auto& A,const auto& B){return A.Key<B.Key;});
		Text+=TEXT("Ready order: ");for(int32 I=0;I<Order.Num();++I){if(I)Text+=TEXT(" > ");Text+=Order[I].Value;}Text+=TEXT("\n");
	}
	if(Phase==TEXT("AwaitCommand"))
	{
		if(LivingMinionCount()>0 || (!Minions.IsEmpty() && IsValid(Enemy) && Enemy->Health>0.f))
			Text+=TEXT("Tab  Switch target\n");
		Text+=FString::Printf(TEXT("1 Strike  2 Defend%s%s%s%s\n"),HasSkill(CurrentMember,TEXT("GuardStance"))?TEXT("  3 Guard 4TP"):TEXT(""),HasSkill(CurrentMember,TEXT("ArcaneBolt"))?TEXT("  4 Bolt 8TP"):TEXT(""),HasSkill(CurrentMember,TEXT("FirstAid"))?TEXT("  5 Aid 6TP"):TEXT(""),HasSkill(CurrentMember,TEXT("EvasiveStep"))?TEXT("  6 Evade 5TP"):TEXT(""));
	}
	if(!LastError.IsEmpty())Text+=LastError+TEXT("\n");
	for(const FString& L:BattleLog)Text+=L+TEXT("\n");
	return FText::FromString(Text);
}
