#include "TowerExpedition.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "GatherInventoryComponent.h"
#include "GolemSparring.h"
#include "GolemHallWidget.h"
#include "TownConstructionSave.h"
#include "Components/InstancedStaticMeshComponent.h"
#include "Components/TextRenderComponent.h"
#include "Components/CapsuleComponent.h"
#include "Engine/StaticMesh.h"
#include "EngineUtils.h"
#include "UObject/ConstructorHelpers.h"
#include "GameFramework/CharacterMovementComponent.h"

ATowerExpedition::ATowerExpedition()
{
 PrimaryActorTick.bCanEverTick=true;
 RootComponent=CreateDefaultSubobject<USceneComponent>(TEXT("TowerGate"));
 Stone=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("RegionStone"));
 Moss=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("RegionMoss"));
 Gems=CreateDefaultSubobject<UInstancedStaticMeshComponent>(TEXT("Deposits"));
 static ConstructorHelpers::FObjectFinder<UStaticMesh> Cube(TEXT("/Engine/BasicShapes/Cube.Cube"));
 for(auto* C:{Stone.Get(),Moss.Get(),Gems.Get()}){C->SetupAttachment(RootComponent);if(Cube.Succeeded())C->SetStaticMesh(Cube.Object);C->SetCanEverAffectNavigation(false);}
 Stone->SetCollisionProfileName(TEXT("BlockAll"));Moss->SetCollisionEnabled(ECollisionEnabled::NoCollision);Gems->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 const TCHAR* Ids[]={TEXT("Entry"),TEXT("Garden"),TEXT("Hollow"),TEXT("Camp")};
 const TCHAR* Names[]={TEXT("Arrival Terrace"),TEXT("Root Garden"),TEXT("Crystal Hollow"),TEXT("Quiet Camp")};
 const FVector Centers[]={FVector(0,0,0),FVector(1900,0,0),FVector(3800,0,0),FVector(1900,-1900,0)};
 for(int32 I=0;I<4;++I){FTowerRegionModule M;M.Id=Ids[I];M.Label=FText::FromString(Names[I]);M.Center=Centers[I];M.Size=I==3?FVector2D(1800,1800):FVector2D(2000,2200);Regions.Add(M);}
 Connections={FIntPoint(0,1),FIntPoint(1,2),FIntPoint(1,3)};
 CounterRules=UTowerAdaptationLibrary::DefaultCounterRules();
}
ATowerExpedition* ATowerExpedition::Find(const AActor* Context)
{if(Context && Context->GetWorld())for(TActorIterator<ATowerExpedition> It(Context->GetWorld());It;++It)return *It;return nullptr;}
bool ATowerExpedition::LinkVillage()
{if(IsValid(Village))return true;for(TActorIterator<AVillageRuntime> It(GetWorld());It;++It)if(It->bUseGolemVillage && It->bUseOrganicGolemNeeds){Village=*It;return true;}return false;}
bool ATowerExpedition::Fail(const FString& Message){LastMessage=Message;return false;}
bool ATowerExpedition::Busy() const{return IsValid(Commander) && AGolemSparring::FindFor(Commander);}
bool ATowerExpedition::At(AIsekaiVillageCharacter* P,const FVector& Point,float Radius) const
{return IsValid(P) && P->GetWorld()==GetWorld() && FVector::DistSquared(P->GetActorLocation(),Point)<FMath::Square(Radius);}
FVector ATowerExpedition::RegionCenter(FName Id) const{if(const auto* R=Regions.FindByPredicate([&](const auto& X){return X.Id==Id;}))return FloorOrigin+R->Center;return FloorOrigin;}
FVector ATowerExpedition::EntryPoint() const{return RegionCenter(TEXT("Entry"))+FVector(-700,0,103);}
FVector ATowerExpedition::CampPoint() const{return RegionCenter(TEXT("Camp"))+FVector(0,0,103);}
FVector ATowerExpedition::GuardianPoint() const{return RegionCenter(TEXT("Hollow"))+FVector(0,-350,103);}
FVector ATowerExpedition::AltarPoint() const{return RegionCenter(TEXT("Garden"))+FVector(0,260,103);}
FString ATowerExpedition::RelicName(ETowerRelic Relic)
{
 switch(Relic)
 {
 case ETowerRelic::RunicSurge:return TEXT("Runic Surge");
 case ETowerRelic::QuarryBlessing:return TEXT("Quarry Blessing");
 case ETowerRelic::AegisOath:return TEXT("Aegis Oath");
 case ETowerRelic::BerserkerBrand:return TEXT("Berserker Brand");
 default:return TEXT("Empty Relic");
 }
}
FString ATowerExpedition::RelicDescription(ETowerRelic Relic)
{
 switch(Relic)
 {
 case ETowerRelic::RunicSurge:return TEXT("+20 starting TP & +15% speed this run");
 case ETowerRelic::QuarryBlessing:return TEXT("+1 extra yield per deposit gathered this run");
 case ETowerRelic::AegisOath:return TEXT("+25 Max HP & +15% passive guard this run");
 case ETowerRelic::BerserkerBrand:return TEXT("+35% attack damage, +15% incoming damage this run");
 default:return TEXT("No active boon");
 }
}
bool ATowerExpedition::FloorAltarAvailable() const
{
 return Village && !Village->TowerFloor.RelicClaimedFloors.Contains(Village->TowerFloor.Floor) && !Village->TowerFloor.CurrentPlan.bRespawn;
}
ETowerRelic ATowerExpedition::CurrentFloorAltarRelic() const
{
 if(!Village)return ETowerRelic::RunicSurge;
 const auto& TF=Village->TowerFloor;
 static const ETowerRelic Pool[]={ETowerRelic::RunicSurge,ETowerRelic::QuarryBlessing,ETowerRelic::AegisOath,ETowerRelic::BerserkerBrand};
 TArray<ETowerRelic> Candidates;
 for(ETowerRelic R:Pool)if(!TF.RunRelics.Contains(R))Candidates.Add(R);
 if(Candidates.IsEmpty())for(ETowerRelic R:Pool)Candidates.Add(R);
 const uint32 Roll=static_cast<uint32>(TF.Seed?TF.Seed:72331)+static_cast<uint32>(FMath::Abs(TF.Floor))*37u;
 return Candidates[Roll%Candidates.Num()];
}
void ATowerExpedition::AddBox(UInstancedStaticMeshComponent* C,const FVector& Center,const FVector& Size,float Yaw)
{C->AddInstance(FTransform(FRotator(0,Yaw,0),Center,Size/100.f),true);}
void ATowerExpedition::AddLabel(const FString& Text,const FVector& P)
{
 auto* T=NewObject<UTextRenderComponent>(this);T->SetupAttachment(RootComponent);T->SetHorizontalAlignment(EHTA_Center);T->SetWorldSize(38);T->SetTextRenderColor(FColor(190,235,235));T->SetText(FText::FromString(Text));T->SetCollisionEnabled(ECollisionEnabled::NoCollision);T->RegisterComponent();T->SetWorldLocation(P);T->SetWorldRotation(FRotator(0,-90,0));Labels.Add(T);
}
bool ATowerExpedition::BuildFloor()
{
 if(!LinkVillage() || Regions.Num()<4)return Fail(TEXT("The tower floor needs four configured modules and a village."));
 for(const auto& C:Connections)if(!Regions.IsValidIndex(C.X) || !Regions.IsValidIndex(C.Y) || C.X==C.Y)return Fail(TEXT("Invalid region connection."));
 for(FName Id:{FName(TEXT("Entry")),FName(TEXT("Garden")),FName(TEXT("Hollow")),FName(TEXT("Camp"))})if(Regions.FilterByPredicate([&](const auto& X){return X.Id==Id;}).Num()!=1)return Fail(TEXT("Each entry, garden, hollow and camp module needs a unique ID."));
 for(const auto& M:Regions)if(M.Size.X<1800 || M.Size.Y<1800 || M.Center.ContainsNaN())return Fail(TEXT("A tower module needs safe dimensions."));
 Stone->ClearInstances();Moss->ClearInstances();Gems->ClearInstances();for(const auto& L:Labels)if(L)L->DestroyComponent();Labels.Reset();Deposits.Reset();
 if(StoneMaterial)Stone->SetMaterial(0,StoneMaterial);if(MossMaterial)Moss->SetMaterial(0,MossMaterial);if(CrystalMaterial)Gems->SetMaterial(0,CrystalMaterial);
 for(int32 I=0;I<Regions.Num();++I)
 {
  const auto& M=Regions[I];const FVector P=FloorOrigin+M.Center;
  AddBox(Stone,P-FVector(0,0,50),FVector(M.Size.X,M.Size.Y,100));AddBox(Moss,P+FVector(0,0,1),FVector(M.Size.X*.62f,M.Size.Y*.6f,2));
  for(int32 Side=0;Side<4;++Side)
  {
   const bool XSide=Side<2;const float Sign=Side%2==0?1.f:-1.f;bool Opening=false;
   for(const auto& C:Connections)
   {
    int32 Other=C.X==I?C.Y:C.Y==I?C.X:INDEX_NONE;if(Other==INDEX_NONE)continue;const FVector D=Regions[Other].Center-M.Center;
    if(XSide?Sign*D.X>1 && FMath::Abs(D.X)>FMath::Abs(D.Y):Sign*D.Y>1 && FMath::Abs(D.Y)>FMath::Abs(D.X))Opening=true;
   }
   const float Length=XSide?M.Size.Y:M.Size.X;const float Edge=(XSide?M.Size.X:M.Size.Y)*.5f-25;
   auto Rail=[&](float Along,float L){AddBox(Stone,P+(XSide?FVector(Sign*Edge,Along,70):FVector(Along,Sign*Edge,70)),XSide?FVector(55,L,140):FVector(L,55,140));};
   if(Opening){const float L=(Length-850)*.5f;Rail((Length+850)*.25f,L);Rail(-(Length+850)*.25f,L);}else Rail(0,Length);
  }
  for(float X:{-1.f,1.f})for(float Y:{-1.f,1.f}){AddBox(Stone,P+FVector(X*(M.Size.X*.5f-90),Y*(M.Size.Y*.5f-90),200),FVector(130,130,400));AddBox(Gems,P+FVector(X*(M.Size.X*.5f-90),Y*(M.Size.Y*.5f-90),425),FVector(70,70,70),45);}
  AddLabel(M.Label.ToString(),P+FVector(0,750,260));
 }
 for(const auto& C:Connections)
 {
  const FVector A=FloorOrigin+Regions[C.X].Center,B=FloorOrigin+Regions[C.Y].Center,Delta=B-A;const float L=Delta.Size2D(),Yaw=Delta.Rotation().Yaw;const FVector Side=FVector::CrossProduct(FVector::UpVector,Delta.GetSafeNormal2D());
  AddBox(Stone,(A+B)*.5f-FVector(0,0,30),FVector(L,700,60),Yaw);
  // Rails only span the open bridge gap, leaving region intersections unobstructed.
  const float HalfA=FMath::Abs(Delta.X)>FMath::Abs(Delta.Y)?Regions[C.X].Size.X*.5f:Regions[C.X].Size.Y*.5f;
  const float HalfB=FMath::Abs(Delta.X)>FMath::Abs(Delta.Y)?Regions[C.Y].Size.X*.5f:Regions[C.Y].Size.Y*.5f;
  const FVector Start=A+Delta.GetSafeNormal2D()*HalfA,End=B-Delta.GetSafeNormal2D()*HalfB;
  if(L>HalfA+HalfB)for(float Sign:{-1.f,1.f})AddBox(Stone,(Start+End)*.5f+Side*Sign*350+FVector(0,0,70),FVector(L-HalfA-HalfB,45,140),Yaw);
 }
 const auto& TF=Village->TowerFloor;
 FRandomStream Random(static_cast<int32>(static_cast<uint32>(TF.Seed?TF.Seed:72331)+static_cast<uint32>(TF.Floor-1)*7919u));
 for(int32 I=0;I<4;++I)
 {
  FTowerDeposit N;N.Id=FName(*FString::Printf(TEXT("F%d_Deposit%d"),TF.Floor,I));
  const bool bIron=(TF.Floor>=3 || TF.Floor<0) && I==1;
  N.Item=I<2?(bIron?FName(TEXT("Iron")):FName(TEXT("Stone"))):FName(TEXT("Crystal"));
  const float RewardMult=FMath::Max(0.5f,TF.CurrentPlan.RewardMult>0.f?TF.CurrentPlan.RewardMult:1.0f);
  const int32 BaseYield=I<2?Random.RandRange(3,5):Random.RandRange(1,3);
  N.Yield=FMath::Max(1,FMath::RoundToInt(BaseYield*(I>=2?RewardMult:1.0f)));
  N.bGuarded=I>=2;
  N.Offset=(RegionCenter(I<2?FName(TEXT("Garden")):FName(TEXT("Hollow")))-FloorOrigin)+FVector(I%2==0?-650:650,Random.FRandRange(-500,-150),55);Deposits.Add(N);
  const bool Available=DepositAvailable(N.Id);AddBox(Available?Gems.Get():Moss.Get(),FloorOrigin+N.Offset,FVector(90,90,Available?110:35),45);
  AddLabel(N.Item.ToString()+(Available?TEXT(" | G gather"):TEXT(" | depleted today")),FloorOrigin+N.Offset+FVector(0,0,135));
 }
 AddBox(Gems,EntryPoint()-FVector(0,0,80),FVector(320,320,35),45);AddLabel(TEXT("RETURN GATE | G / V: end run"),EntryPoint()+FVector(0,0,155));
 AddBox(Gems,GuardianPoint()-FVector(0,0,80),FVector(210,210,30),45);
 AddLabel(FloorCleared()?TEXT("GUARDIAN | cleared"):TF.CurrentPlan.bBoss?TEXT("BOSS EXAM | G challenge"):TEXT("GUARDIAN | G challenge"),GuardianPoint()+FVector(0,0,160));
 static const TCHAR* PortalNames[]={TEXT("VILLAGE"),TEXT("CAMP"),TEXT("FORWARD"),TEXT("LEAP")};
 for(ETowerPortal Portal:AvailablePortals())
 {
  AddBox(Gems,PortalPoint(Portal)-FVector(0,0,80),FVector(180,180,30),45);AddBox(Moss,PortalPoint(Portal)+FVector(0,0,90),FVector(30,30,260));
  AddLabel(Portal==ETowerPortal::Leap?FString::Printf(TEXT("LEAP +%d | G"),TF.LeapOffer):FString::Printf(TEXT("%s | G"),PortalNames[(int32)Portal]),PortalPoint(Portal)+FVector(0,0,250));
 }
 const FVector Camp=CampPoint()-FVector(0,0,103);AddBox(Moss,Camp+FVector(0,0,3),FVector(450,450,6));
 if(Village->TowerFloor.bCampBuilt){for(float X:{-250.f,250.f})AddBox(Stone,Camp+FVector(X,-180,120),FVector(35,35,240));AddBox(Moss,Camp+FVector(0,-180,255),FVector(600,450,35));AddBox(Stone,Camp+FVector(0,-250,40),FVector(300,70,80));}
 AddLabel(Village->TowerFloor.bCampBuilt?TEXT("CAMP | G rest | V trip home"):FString::Printf(TEXT("CAMP | G establish: %d wood + %d stone"),CampWoodCost,CampStoneCost),Camp+FVector(0,0,210));
 const FVector AltarBase=AltarPoint()-FVector(0,0,103);const bool bAltarOpen=FloorAltarAvailable();const ETowerRelic AltarRelic=CurrentFloorAltarRelic();
 AddBox(Stone,AltarBase+FVector(0,0,45),FVector(160,160,90));AddBox(bAltarOpen?Gems.Get():Moss.Get(),AltarBase+FVector(0,0,120),FVector(65,65,65),45);
 AddLabel(bAltarOpen?FString::Printf(TEXT("RELIC ALTAR: %s | G claim"),*RelicName(AltarRelic)):TEXT("RELIC ALTAR | claimed"),AltarPoint()+FVector(0,0,175));
 RenderDay=Village->DayIndex;bBuilt=true;return true;
}
bool ATowerExpedition::CheckStanding(const FVector& Point,AActor* Ignore) const
{
 if(Point.ContainsNaN() || !GetWorld())return false;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(TowerStanding),true,Ignore);if(IsValid(Commander))Q.AddIgnoredActor(Commander);for(const auto& C:Companions)if(C.Actor)Q.AddIgnoredActor(C.Actor);
 FHitResult H;if(!GetWorld()->LineTraceSingleByChannel(H,Point+FVector(0,0,100),Point-FVector(0,0,250),ECC_Visibility,Q) || H.ImpactNormal.Z<.85f || FMath::Abs(H.ImpactPoint.Z-(Point.Z-103))>35)return false;
 float Radius=36,Half=97;if(auto* P=Cast<AIsekaiVillageCharacter>(Ignore)){Radius=P->GetCapsuleComponent()->GetScaledCapsuleRadius();Half=P->GetCapsuleComponent()->GetScaledCapsuleHalfHeight();}
 return !GetWorld()->OverlapBlockingTestByChannel(Point,FQuat::Identity,ECC_Pawn,FCollisionShape::MakeCapsule(Radius,Half),Q);
}
void ATowerExpedition::SyncDrives()
{
 if(!Village || !Commander || !Commander->PartyReserve)return;
 for(const auto& A:Commander->PartyReserve->Reserve)for(auto& R:Village->GolemResidents)if(R.AdventurerId==A.AdventurerID)R.Drives=A.Drives;
}
bool ATowerExpedition::Depart(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || bInside || !LinkVillage() || !P || !P->PartyReserve || !P->Gather || !At(P,GetActorLocation(),450))return Fail(TEXT("Stand at the tower gate to depart."));
 if(P->bSphereGridOpen || (P->HallWidget && P->HallWidget->IsInViewport()) || Village->bBuildingCatalogOpen || AGolemSparring::FindFor(P))return Fail(TEXT("Close menus and finish the current encounter first."));
 Village->ReconcileGolemPopulation();Companions.Reset();
 for(const auto& A:P->PartyReserve->Reserve)
 {
  if(!A.bInActiveParty)continue;
  if(A.bAssignedToRampage || A.Drives.Fatigue>=90)return Fail(TEXT("An active adventurer is away or exhausted. Rest or choose another at the hall."));
  const auto* R=Village->GolemResidents.FindByPredicate([&](const auto& X){return X.AdventurerId==A.AdventurerID && !X.HomePlot.IsNone();});
  AVillageGolemCitizen* Actor=nullptr;if(R)for(TActorIterator<AVillageGolemCitizen> It(GetWorld());It;++It)if(It->GetOwner()==Village && It->GolemId==R->Id){Actor=*It;break;}
  if(!Actor)return Fail(TEXT("Every selected adventurer needs housing and a village actor."));
  FTowerTravellingCompanion C;C.Actor=Actor;C.Id=A.AdventurerID;C.Home=Actor->GetActorLocation();C.bTickWasEnabled=Actor->IsActorTickEnabled();Companions.Add(C);
 }
 if(Companions.IsEmpty() || Companions.Num()>P->PartyReserve->GetMaxCompanions())return Fail(TEXT("Choose a valid active party at the adventure hall first."));
 if(BreadCost<0 || P->Gather->GetCount(TEXT("Bread"))<BreadCost)return Fail(FString::Printf(TEXT("Pack %d bread for the expedition. Workers can make it at a bakery."),BreadCost));
 Commander=P;const auto Before=Village->TowerFloor;auto& TF=Village->TowerFloor;if(!TF.Seed)TF.Seed=FMath::RandRange(1,MAX_int32-1);
 // Version 1 saves had one floor and a camp that never reset; treat a built camp as a run in progress.
 if(TF.Version<2){TF.Version=2;TF.Floor=1;TF.bRunActive=TF.bCampBuilt;TF.ClearedFloor=TF.GuardianClearedVisit==TF.Visit?1:0;}
 const bool bResume=TF.bRunActive;
 if(!bResume)
 {
  const TArray<int32> Startable=StartableFloors();
  TF.Floor=Startable.Contains(TF.StartFloor)?TF.StartFloor:Startable.Last();
  TF.bRunActive=true;TF.bCampBuilt=false;TF.ClearedFloor=0;TF.GuardianClearedVisit=0;TF.LeapOffer=0;TF.TripsHomeUsed=0;TF.CampRests=0;TF.RunLoot.Reset();TF.BossesDefeated.Reset();TF.RunRelics.Reset();TF.RelicClaimedFloors.Reset();
  PlanCurrentFloor(0,false);
 }
 else if(TF.ClearedFloor==TF.Floor && !TF.BossesDefeated.Contains(TF.Floor)){TF.ClearedFloor=0;TF.LeapOffer=0;PlanCurrentFloor(TF.CampRests*RespawnBudgetPerRest,true);}
 else if(TF.CurrentPlan.Floor!=TF.Floor)PlanCurrentFloor(0,false);
 if(!BuildFloor()){Village->TowerFloor=Before;return false;}
 const FVector Spawn=bResume && TF.bCampBuilt?CampPoint():EntryPoint();
 if(!CheckStanding(Spawn,P)){Village->TowerFloor=Before;return Fail(TEXT("The arrival point is obstructed."));}
 for(int32 I=0;I<Companions.Num();++I)if(!CheckStanding(Spawn+FVector(0,140.f*(I+1),0),Companions[I].Actor)){Village->TowerFloor=Before;return Fail(TEXT("A companion arrival point is obstructed."));}
 const auto OldInventory=P->Gather->Stacks;P->Gather->Consume(TEXT("Bread"),BreadCost);++Village->TowerFloor.Visit;
 if(!Village->SaveVillageState(P)){Village->TowerFloor=Before;P->Gather->Stacks=OldInventory;return Fail(TEXT("Could not save departure. Provisions were returned."));}
 ReturnPoint=P->GetActorLocation();bInside=true;Trail={Spawn};P->GetCharacterMovement()->StopMovementImmediately();P->SetActorLocation(Spawn,false,nullptr,ETeleportType::TeleportPhysics);
 for(int32 I=0;I<Companions.Num();++I){auto& C=Companions[I];C.Actor->Tags.AddUnique(TEXT("ElrhunTowerParty"));C.Actor->SetActorTickEnabled(false);C.Actor->SetExpeditionWalking(false);C.Actor->SetActorLocation(Spawn+FVector(0,140.f*(I+1),0),false,nullptr,ETeleportType::TeleportPhysics);C.TrailIndex=0;}
 LastMessage=(bResume?TEXT("Run resumed. "):TEXT("Run started. "))+TF.CurrentPlan.Announcement;return true;
}
bool ATowerExpedition::DepositAvailable(FName Id) const
{
 if(!Village)return false;const int32* Day=Village->TowerFloor.HarvestDays.Find(Id);return !Day || *Day<Village->DayIndex;
}
bool ATowerExpedition::GatherDeposit(AIsekaiVillageCharacter* P,FName Id)
{
 if(!HasAuthority() || !bInside || P!=Commander || !P || !P->Gather || Busy())return Fail(TEXT("Finish and close the encounter before gathering."));
 const auto* N=Deposits.FindByPredicate([&](const auto& X){return X.Id==Id;});if(!N || !At(P,FloorOrigin+N->Offset,250))return Fail(TEXT("Move closer to the deposit."));
 if(!DepositAvailable(Id))return Fail(TEXT("This deposit is depleted. It renews on a later village day."));
 if(N->bGuarded && !FloorCleared())return Fail(TEXT("The slime guardian protects these crystals. Challenge it at the rune marker first."));
 if(N->bGuarded && Village->TowerFloor.CurrentPlan.bRespawn)return Fail(TEXT("Respawned enemies guard basic materials only. These crystals stay sealed until the next floor."));
 const auto Old=Village->TowerFloor;const auto Inventory=P->Gather->Stacks;const FName Item=N->Item;const int32 Amount=N->Yield+(Village->TowerFloor.RunRelics.Contains(ETowerRelic::QuarryBlessing)?1:0)+(P->HasSphereSkill(TEXT("CatalystExtract"))?1:0)+(N->bGuarded && P->HasSphereSkill(TEXT("MasterHunter"))?1:0);
 Village->TowerFloor.HarvestDays.Add(Id,Village->DayIndex);P->Gather->AddItem(Item,Amount);if(Village->TowerFloor.bRunActive)Village->TowerFloor.RunLoot.FindOrAdd(Item)+=Amount;
 if(!Village->SaveVillageState(P)){Village->TowerFloor=Old;P->Gather->Stacks=Inventory;return Fail(TEXT("Could not save gathering. The deposit and inventory were restored."));}
 BuildFloor();LastMessage=FString::Printf(TEXT("Gathered %d %s. Saved; this deposit is depleted for today."),Amount,*Item.ToString());return true;
}
bool ATowerExpedition::UseCamp(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || !bInside || P!=Commander || !P || !P->Gather || Busy() || !At(P,CampPoint()))return Fail(TEXT("Reach the quiet camp and close any encounter first."));
 const auto Before=Village->TowerFloor;const auto Inventory=P->Gather->Stacks;const auto Roster=P->PartyReserve->Reserve;bool bRespawned=false;
 const bool bSanctuary=P->HasSphereSkill(TEXT("SanctuaryCamp"));
 if(!Village->TowerFloor.bCampBuilt)
 {
  const int32 NeedWood=bSanctuary?FMath::Max(1,CampWoodCost-1):CampWoodCost;
  const int32 NeedStone=bSanctuary?FMath::Max(1,CampStoneCost-1):CampStoneCost;
  if(CampWoodCost<0 || CampStoneCost<0 || P->Gather->GetCount(TEXT("Wood"))<NeedWood || P->Gather->GetCount(TEXT("Stone"))<NeedStone)return Fail(FString::Printf(TEXT("Camp needs %d wood and %d stone."),NeedWood,NeedStone));
  P->Gather->Consume(TEXT("Wood"),NeedWood);P->Gather->Consume(TEXT("Stone"),NeedStone);Village->TowerFloor.bCampBuilt=true;
 }
 else
 {
  auto& TF=Village->TowerFloor;
  if(TF.RestedVisit==TF.Visit)return Fail(TEXT("The party has rested this expedition. V takes a trip home; the camp stays built for this run."));
  TF.RestedVisit=TF.Visit;++TF.CampRests;
  const float RestDrop=bSanctuary?60.f:35.f;
  for(auto& A:P->PartyReserve->Reserve)if(Companions.ContainsByPredicate([&](const auto& C){return C.Id==A.AdventurerID;}))A.Drives.Fatigue=FMath::Max(0.f,A.Drives.Fatigue-RestDrop);
  if(bSanctuary || P->HasSphereSkill(TEXT("RunicTonic"))){P->RestoreHP(P->MaxHP);P->RestoreTP(P->MaxTP);}
  SyncDrives();
  bRespawned=TF.ClearedFloor==TF.Floor && !TF.BossesDefeated.Contains(TF.Floor);
  if(bRespawned){TF.ClearedFloor=0;TF.GuardianClearedVisit=0;TF.LeapOffer=0;PlanCurrentFloor(TF.CampRests*RespawnBudgetPerRest,true);}
 }
 if(!Village->SaveVillageState(P)){Village->TowerFloor=Before;P->Gather->Stacks=Inventory;P->PartyReserve->Reserve=Roster;SyncDrives();return Fail(TEXT("Could not save camp. Materials and needs were restored."));}
 BuildFloor();
 if(!Before.bCampBuilt)LastMessage=TEXT("Camp established for this run. G rests once per visit; V takes a trip home. Ending the run loses the camp.");
 else LastMessage=bRespawned?TEXT("Party rested: fatigue reduced by 35. Regular enemies respawned stronger; beat the guardian again to reopen the portals."):TEXT("Party rested: fatigue reduced by 35. V takes a trip home.");
 return true;
}
bool ATowerExpedition::ShareRations(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || !bInside || P!=Commander || !P || !P->Gather || Busy())return Fail(TEXT("Finish and close the current encounter first."));
 if(P->Gather->GetCount(TEXT("Bread"))<1)return Fail(TEXT("No bread in pack. Workers can bake more in the village bakery."));
 P->Gather->Consume(TEXT("Bread"),1);
 const bool bTonic=P->HasSphereSkill(TEXT("RunicTonic"));
 const float FatigueDrop=bTonic?38.f:25.f;
 for(auto& A:P->PartyReserve->Reserve)
 {
  if(Companions.ContainsByPredicate([&](const auto& C){return C.Id==A.AdventurerID;}))
   A.Drives.Fatigue=FMath::Max(0.f,A.Drives.Fatigue-FatigueDrop);
 }
 if(bTonic){P->RestoreHP(25.f);P->RestoreTP(15.f);}
 SyncDrives();
 if(!Village->SaveVillageState(P))return Fail(TEXT("Could not save rations. State restored."));
 LastMessage=FString::Printf(TEXT("Shared bread: party fatigue reduced by %.0f%s. (%d bread remaining)"),FatigueDrop,bTonic?TEXT(" + Runic Tonic (+25 HP, +15 TP)"):TEXT(""),P->Gather->GetCount(TEXT("Bread")));
 return true;
}
bool ATowerExpedition::ActivateAltar(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || !bInside || P!=Commander || !P || !LinkVillage() || Busy() || !At(P,AltarPoint(),250))return Fail(TEXT("Step beside the Relic Altar in the Garden first."));
 if(!FloorAltarAvailable())return Fail(TEXT("This floor's Relic Altar is dormant."));
 auto& TF=Village->TowerFloor;const auto Before=TF;const auto OldInventory=P->Gather?P->Gather->Stacks:TArray<FGatherStack>();
 const ETowerRelic Boon=CurrentFloorAltarRelic();
 TF.RelicClaimedFloors.AddUnique(TF.Floor);
 FString Outcome;
 if(!TF.RunRelics.Contains(Boon))
 {
  TF.RunRelics.Add(Boon);
  Outcome=FString::Printf(TEXT("Relic Altar blessed your run: %s (%s)."),*RelicName(Boon),*RelicDescription(Boon));
 }
 else
 {
  const int32 CrystalGain=P->HasSphereSkill(TEXT("RelicEmpowered"))?3:2;
  if(P->Gather){P->Gather->AddItem(TEXT("Crystal"),CrystalGain);TF.RunLoot.FindOrAdd(TEXT("Crystal"))+=CrystalGain;}
  Outcome=FString::Printf(TEXT("All relics already active! The altar distilled +%d Crystals instead."),CrystalGain);
 }
 if(!Village->SaveVillageState(P)){TF=Before;if(P->Gather)P->Gather->Stacks=OldInventory;return Fail(TEXT("Could not save the altar blessing. State restored."));}
 BuildFloor();LastMessage=Outcome;return true;
}
bool ATowerExpedition::ChallengeGuardian(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || !bInside || P!=Commander || Busy() || !At(P,GuardianPoint(),500))return Fail(TEXT("Reach the guardian rune with your party and close any previous encounter."));
 if(FloorCleared())return Fail(Village->TowerFloor.BossesDefeated.Contains(Village->TowerFloor.Floor)?TEXT("This boss stays defeated until the run ends."):TEXT("This floor's guardian is already cleared. Choose a portal."));
 if(Village->TowerFloor.CurrentPlan.Floor!=Village->TowerFloor.Floor)PlanCurrentFloor(0,false);
 TArray<AVillageGolemCitizen*> Allies;for(const auto& C:Companions){if(!IsValid(C.Actor) || FVector::DistSquared(C.Actor->GetActorLocation(),GuardianPoint())>FMath::Square(1100.f))return Fail(TEXT("Wait for the whole active party to reach the guardian rune."));Allies.Add(C.Actor);}
 FActorSpawnParameters S;S.Owner=this;auto* B=GetWorld()->SpawnActor<AGolemSparring>(GuardianPoint(),FRotator::ZeroRotator,S);
 const int32 Variant=FRandomStream(static_cast<int32>(static_cast<uint32>(Village->TowerFloor.Seed)+static_cast<uint32>(Village->TowerFloor.Visit))).RandRange(0,2);
 if(B)B->ApplyFloorPlan(Village->TowerFloor.CurrentPlan,static_cast<int32>(static_cast<uint32>(Village->TowerFloor.Seed)^static_cast<uint32>(Village->TowerFloor.Visit*131+Village->TowerFloor.Floor)));
 if(!B || !B->BeginFieldEncounter(Village,P,Allies,GuardianPoint()+FVector(0,800,-103),Variant)){const FString Why=B?B->LastError:TEXT("No encounter could be created.");if(B)B->Destroy();return Fail(Why);}
 GuardianBattle=B;for(const auto& C:Companions)C.Actor->SetExpeditionWalking(false);LastMessage=TEXT("Guardian encounter: 1-6 command skills, J retreat / close. If the whole party falls, the run fails.");return true;
}
void ATowerExpedition::PreserveVillagePositions(UTownConstructionSave* Saved) const
{if(!bInside || !Saved)return;for(const auto& C:Companions)if(C.Actor)for(auto& R:Saved->Golems)if(R.Id==C.Actor->GolemId){R.Position=C.Home;R.bHasPosition=true;}}
void ATowerExpedition::RestoreParty()
{
 for(auto& C:Companions)if(IsValid(C.Actor)){C.Actor->SetExpeditionWalking(false);C.Actor->SetActorLocation(C.Home,false,nullptr,ETeleportType::TeleportPhysics);C.Actor->Tags.Remove(TEXT("ElrhunTowerParty"));C.Actor->SetActorTickEnabled(C.bTickWasEnabled);}
 Companions.Reset();Trail.Reset();bInside=false;
}
bool ATowerExpedition::ReturnToVillage(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || !bInside || P!=Commander || Busy())return Fail(TEXT("Finish and close the current encounter before returning."));
 if(At(P,EntryPoint()))return EndRun(P,false);
 if(!(Village->TowerFloor.bCampBuilt && At(P,CampPoint())))return Fail(TEXT("Return from the arrival gate or your established camp."));
 auto& TF=Village->TowerFloor;const int32 Allowed=TripsHomeAllowed();
 if(TF.TripsHomeUsed>=Allowed)return Fail(FString::Printf(TEXT("No trips home left this run (guild rank allows %d). Take the Village portal or the arrival gate to end the run."),Allowed));
 const auto Before=TF;++TF.TripsHomeUsed;
 return GoHome(P,Before,FString::Printf(TEXT("Trip home: the run continues from camp on floor %d. %d trip(s) left. Regular enemies will respawn."),TF.Floor,Allowed-TF.TripsHomeUsed));
}
bool ATowerExpedition::GoHome(AIsekaiVillageCharacter* P,const FTowerFloorProgress& Before,const FString& Message)
{
 auto Abort=[&](const TCHAR* Why){Village->TowerFloor=Before;return Fail(Why);};
 if(!CheckStanding(ReturnPoint,P))return Abort(TEXT("The village landing is temporarily obstructed. Try again shortly."));
 for(const auto& C:Companions)if(!CheckStanding(C.Home,C.Actor))return Abort(TEXT("A companion landing is temporarily obstructed. Try again shortly."));
 SyncDrives();if(!Village->SaveVillageState(P))return Abort(TEXT("Could not save the return. You remain in the floor; try again."));
 P->GetCharacterMovement()->StopMovementImmediately();P->SetActorLocation(ReturnPoint,false,nullptr,ETeleportType::TeleportPhysics);RestoreParty();GuardianBattle=nullptr;LastMessage=Message;return true;
}
bool ATowerExpedition::EndRun(AIsekaiVillageCharacter* P,bool bFailed)
{
 if(!HasAuthority() || !bInside || P!=Commander || !P || !P->Gather || (!bFailed && Busy()))return Fail(TEXT("Finish and close the current encounter before ending the run."));
 auto& TF=Village->TowerFloor;const auto Before=TF;const auto Inventory=P->Gather->Stacks;
 FString Lost;
 if(bFailed)for(const TPair<FName,int32>& Item:TF.RunLoot)
 {
  const int32 Loss=FMath::Min(P->Gather->GetCount(Item.Key),FMath::FloorToInt(Item.Value*FMath::Clamp(FailureLootLoss,0.f,1.f)));
  if(Loss>0 && P->Gather->Consume(Item.Key,Loss))Lost+=FString::Printf(TEXT(" %d %s"),Loss,*Item.Key.ToString());
 }
 TF.bRunActive=false;TF.bCampBuilt=false;TF.BossesDefeated.Reset();TF.TripsHomeUsed=0;TF.CampRests=0;TF.RunLoot.Reset();TF.RunRelics.Reset();TF.RelicClaimedFloors.Reset();TF.ClearedFloor=0;TF.GuardianClearedVisit=0;TF.LeapOffer=0;TF.RestedVisit=0;
 const FString Message=bFailed?FString::Printf(TEXT("The run failed. Bosses respawn and the camp is lost. Lost:%s. The tower keeps its memory of you."),Lost.IsEmpty()?TEXT(" nothing"):*Lost)
  :FString(TEXT("Run ended safely. All loot kept; bosses respawn and the camp is lost. The tower keeps its memory of you."));
 if(!GoHome(P,Before,Message)){P->Gather->Stacks=Inventory;return false;}
 return true;
}
bool ATowerExpedition::FloorCleared() const
{
 if(!Village)return false;const auto& TF=Village->TowerFloor;
 return TF.BossesDefeated.Contains(TF.Floor) || (TF.ClearedFloor==TF.Floor && TF.GuardianClearedVisit==TF.Visit && TF.Visit>0);
}
TArray<ETowerPortal> ATowerExpedition::AvailablePortals() const
{
 TArray<ETowerPortal> Out;if(!FloorCleared())return Out;
 Out.Add(ETowerPortal::Village);if(Village->TowerFloor.bCampBuilt)Out.Add(ETowerPortal::Camp);Out.Add(ETowerPortal::Forward);
 if(Village->TowerFloor.LeapOffer>=2)Out.Add(ETowerPortal::Leap);return Out;
}
FVector ATowerExpedition::PortalPoint(ETowerPortal Portal) const{return RegionCenter(TEXT("Hollow"))+FVector(-900+600*(int32)Portal,850,103);}
static int32 StepFloor(int32 Floor,int32 Steps){return Floor<0?Floor-Steps:Floor+Steps;}
FString ATowerExpedition::PortalPreview(ETowerPortal Portal) const
{
 if(!Village)return FString();const auto& TF=Village->TowerFloor;
 auto Next=[&](int32 Steps)
 {
  const int32 To=StepFloor(TF.Floor,Steps);FString S=FString::Printf(TEXT("floor %d%s."),To,UTowerAdaptationLibrary::IsBossFloor(To,BossInterval)?TEXT(" (boss exam)"):TEXT(""));
  const TArray<ETowerHabit> Seen=UTowerAdaptationLibrary::NoticedHabits(TF.Memory,1,false);
  S+=Seen.IsEmpty()?FString(TEXT(" The tower cannot read you yet.")):FString::Printf(TEXT(" The tower will remember your %s."),*UTowerAdaptationLibrary::HabitName(Seen[0]));return S;
 };
 switch(Portal)
 {
 case ETowerPortal::Village:return TEXT("Village: end the run safely. Loot kept; camp lost; bosses respawn.");
 case ETowerPortal::Camp:return TEXT("Camp: pause. Resting respawns regular enemies here, a little stronger each rest.");
 case ETowerPortal::Forward:return TEXT("Forward: ")+Next(1);
 default:return FString::Printf(TEXT("Leap +%d: "),TF.LeapOffer)+Next(TF.LeapOffer)+FString::Printf(TEXT(" Harder; reward x%d."),TF.LeapOffer);
 }
}
int32 ATowerExpedition::GuildRank() const
{
	int32 Rank=0;
	if(IsValid(Village))Rank=Village->TownGuildRank;
	else if(UWorld* W=GetWorld())for(TActorIterator<AVillageRuntime> It(W);It;++It){if(It->bUseGolemVillage){Rank=It->TownGuildRank;break;}}
	if(IsValid(Commander) && Commander->PartyReserve)for(const auto& A:Commander->PartyReserve->Reserve)Rank=FMath::Max(Rank,A.Rank);return Rank;
}
int32 ATowerExpedition::TripsHomeAllowed() const{return UTowerAdaptationLibrary::TripsHomeForRank(GuildRank())+((IsValid(Commander) && Commander->HasSphereSkill(TEXT("SanctuaryCamp")))?1:0);}
TArray<int32> ATowerExpedition::StartableFloors() const
{
 TArray<int32> Out;if(!Village){Out.Add(1);return Out;}const auto& TF=Village->TowerFloor;
 for(int32 F=1;F<=TF.HighestFloor+1;++F)Out.Add(F);
 if(TF.bNewGamePlus)for(int32 D=1;D<=TF.HighestEcho+1;++D)Out.Add(-D);
 return Out;
}
bool ATowerExpedition::CycleStartFloor(AIsekaiVillageCharacter* P)
{
 if(!HasAuthority() || bInside || !LinkVillage() || !At(P,GetActorLocation(),450))return Fail(TEXT("Stand at the tower gate to choose a starting floor."));
 auto& TF=Village->TowerFloor;if(TF.bRunActive)return Fail(FString::Printf(TEXT("A run is in progress on floor %d. G resumes it at camp."),TF.Floor));
 const TArray<int32> Floors=StartableFloors();const int32 Current=Floors.Contains(TF.StartFloor)?TF.StartFloor:Floors.Last();
 TF.StartFloor=Floors[(Floors.IndexOfByKey(Current)+1)%Floors.Num()];
 LastMessage=FString::Printf(TEXT("The gate will open on floor %d."),TF.StartFloor);return true;
}
void ATowerExpedition::PlanCurrentFloor(float ExtraBudget,bool bRespawn)
{
 auto& TF=Village->TowerFloor;TF.CurrentPlan=UTowerAdaptationLibrary::PlanFloor(TF.Floor,TF.Memory,CounterRules,ExtraBudget,BossInterval);
 if(bRespawn){TF.CurrentPlan.bRespawn=true;TF.CurrentPlan.RewardMult=.5f;TF.CurrentPlan.Announcement+=TEXT(" Respawned enemies: basic materials only.");}
}
bool ATowerExpedition::PartyCanStand(const FVector& Spawn) const
{
 if(!CheckStanding(Spawn,Commander))return false;
 for(int32 I=0;I<Companions.Num();++I)if(!CheckStanding(Spawn+FVector(0,140.f*(I+1),0),Companions[I].Actor))return false;
 return true;
}
void ATowerExpedition::PlaceParty(const FVector& Spawn)
{
 Commander->GetCharacterMovement()->StopMovementImmediately();Commander->SetActorLocation(Spawn,false,nullptr,ETeleportType::TeleportPhysics);Trail={Spawn};
 for(int32 I=0;I<Companions.Num();++I)if(IsValid(Companions[I].Actor)){Companions[I].TrailIndex=0;Companions[I].Actor->SetExpeditionWalking(false);Companions[I].Actor->SetActorLocation(Spawn+FVector(0,140.f*(I+1),0),false,nullptr,ETeleportType::TeleportPhysics);}
}
bool ATowerExpedition::MoveToFloor(AIsekaiVillageCharacter* P,int32 Steps,bool bLeap)
{
 auto& TF=Village->TowerFloor;const auto Before=TF;
 float Extra=0;for(int32 S=1;S<Steps;++S)Extra+=UTowerAdaptationLibrary::BaseBudget(StepFloor(TF.Floor,S))*FMath::Max(0.f,LeapBudgetShare);
 TF.Floor=StepFloor(TF.Floor,Steps);TF.ClearedFloor=0;TF.GuardianClearedVisit=0;TF.LeapOffer=0;
 PlanCurrentFloor(Extra,false);if(bLeap)TF.CurrentPlan.RewardMult*=Steps;
 if(!BuildFloor() || !PartyCanStand(EntryPoint())){TF=Before;BuildFloor();return Fail(TEXT("The next floor's arrival point is obstructed."));}
 if(!Village->SaveVillageState(P)){TF=Before;BuildFloor();return Fail(TEXT("Could not save the floor change. You remain on this floor."));}
 PlaceParty(EntryPoint());LastMessage=TF.CurrentPlan.Announcement;return true;
}
bool ATowerExpedition::ChoosePortal(AIsekaiVillageCharacter* P,ETowerPortal Portal)
{
 if(!HasAuthority() || !bInside || P!=Commander || Busy())return Fail(TEXT("Close the encounter result (J) before taking a portal."));
 if(!AvailablePortals().Contains(Portal))return Fail(TEXT("That portal is not open. Clear the floor's guardian first."));
 if(!At(P,PortalPoint(Portal),220))return Fail(TEXT("Step onto the portal."));
 switch(Portal)
 {
 case ETowerPortal::Village:return EndRun(P,false);
 case ETowerPortal::Camp:
  if(!PartyCanStand(CampPoint()))return Fail(TEXT("The camp is obstructed."));
  PlaceParty(CampPoint());LastMessage=TEXT("At camp. G rests (regular enemies respawn); V takes a trip home. Walk back to the Hollow portals to continue.");return true;
 case ETowerPortal::Forward:return MoveToFloor(P,1,false);
 default:return MoveToFloor(P,Village->TowerFloor.LeapOffer,true);
 }
}
bool ATowerExpedition::CommitGuardianClear(const FTowerFloorLog& Log)
{
 if(!Village || !IsValid(Commander))return false;if(FloorCleared())return true;
 auto& TF=Village->TowerFloor;const auto Before=TF;
 TF.GuardianClearedVisit=TF.Visit;TF.ClearedFloor=TF.Floor;
 if(TF.CurrentPlan.bBoss)
 {
  TF.BossesDefeated.AddUnique(TF.Floor);
  if(TF.Floor>=10)TF.bNewGamePlus=true;
  if(Commander && Commander->Gather)
  {
   const int32 BossBonus=5;
   Commander->Gather->AddItem(TEXT("Crystal"),BossBonus);
   TF.RunLoot.FindOrAdd(TEXT("Crystal"))+=BossBonus;
  }
 }
 UTowerAdaptationLibrary::RecordFloor(TF.Memory,Log,TF.Floor<0);
 TF.LastGrade=UTowerAdaptationLibrary::ClearGrade(TF.Memory.LastEase);
 TF.LeapOffer=TF.CurrentPlan.bRespawn?0:UTowerAdaptationLibrary::LeapDistance(TF.Floor,TF.LastGrade,BossInterval);
 if(TF.Floor>0)TF.HighestFloor=FMath::Max(TF.HighestFloor,TF.Floor);else TF.HighestEcho=FMath::Max(TF.HighestEcho,-TF.Floor);
 if(!Village->SaveVillageState(Commander)){TF=Before;return false;}
 static const TCHAR* Grades[]={TEXT("struggle"),TEXT("clear"),TEXT("strong"),TEXT("perfect")};
 BuildFloor();LastMessage=FString::Printf(TEXT("Floor %d cleared (%s). Portals opened in the Hollow%s. J closes the result."),TF.Floor,Grades[TF.LastGrade],TF.LeapOffer?*FString::Printf(TEXT(", including Leap +%d"),TF.LeapOffer):TEXT(""));
 return true;
}
bool ATowerExpedition::Interact(AIsekaiVillageCharacter* P)
{
 if(!bInside)return Depart(P);
 if(P!=Commander)return false;
 if(At(P,EntryPoint()))return ReturnToVillage(P);
 if(At(P,CampPoint()))return UseCamp(P);
 if(At(P,AltarPoint(),250))return ActivateAltar(P);
 if(At(P,GuardianPoint(),500))return ChallengeGuardian(P);
 for(ETowerPortal Portal:AvailablePortals())if(At(P,PortalPoint(Portal),220))return ChoosePortal(P,Portal);
 for(const auto& N:Deposits)if(At(P,FloorOrigin+N.Offset,250))return GatherDeposit(P,N.Id);
 if(P->Gather && P->Gather->GetCount(TEXT("Bread"))>0)return ShareRations(P);
 return Fail(TEXT("G interacts with a deposit, camp, guardian rune, portal or return gate. Follow the connected paths."));
}
void ATowerExpedition::FollowParty(float D)
{
 if(!Commander || Trail.IsEmpty())return;
 const FVector Here=Commander->GetActorLocation();if(FVector::DistSquared(Here,Trail.Last())>FMath::Square(120.f))Trail.Add(Here);
 if(Trail.Num()>4096){Trail.RemoveAt(0,1024);for(auto& C:Companions)C.TrailIndex=FMath::Max(0,C.TrailIndex-1024);}
 FCollisionQueryParams Q(SCENE_QUERY_STAT(TowerFollow),true);if(IsValid(Commander))Q.AddIgnoredActor(Commander);for(const auto& C:Companions)if(C.Actor)Q.AddIgnoredActor(C.Actor);
 for(int32 I=0;I<Companions.Num();++I)
 {
  auto& C=Companions[I];if(!IsValid(C.Actor))continue;const int32 End=Trail.Num()-1-2*(I+1);
  if(End<0){C.Actor->SetExpeditionWalking(false);continue;}
  auto Waypoint=[&](int32 Index){const FVector Along=Index>0?(Trail[Index]-Trail[Index-1]).GetSafeNormal2D():(Trail.Num()>1?(Trail[1]-Trail[0]).GetSafeNormal2D():FVector::ForwardVector);return Trail[Index]+FVector::CrossProduct(FVector::UpVector,Along)*130.f;};
  C.TrailIndex=FMath::Min(C.TrailIndex,End);FVector P=C.Actor->GetActorLocation();while(C.TrailIndex<End && (FVector::DistSquared2D(P,Waypoint(C.TrailIndex))<FMath::Square(50.f) || FVector::DistSquared2D(P,Trail[C.TrailIndex])<FMath::Square(160.f)))++C.TrailIndex;
  const FVector Goal=Waypoint(C.TrailIndex);FVector Direction=(Goal-P).GetSafeNormal2D();const float Step=FMath::Min(260.f*FMath::Clamp(D,0.f,.1f),FVector::Dist2D(P,Goal));
  if(Step<2){C.Actor->SetExpeditionWalking(false);continue;}
  auto TryStep=[&](const FVector& Dir,float Dist,FHitResult& OutBlock)->bool
  {
   if(Dir.IsNearlyZero() || Dist<1.f)return false;
   FVector Next=P+Dir*Dist;FHitResult H;
   if(!GetWorld()->LineTraceSingleByChannel(H,Next+FVector(0,0,100),Next-FVector(0,0,250),ECC_Visibility,Q) || H.ImpactNormal.Z<.85f || FMath::Abs(H.ImpactPoint.Z+103-P.Z)>35)return false;
   Next.Z=H.ImpactPoint.Z+103;C.Actor->SetActorLocation(Next,true,&OutBlock);
   return FVector::DistSquared(P,C.Actor->GetActorLocation())>1;
  };
  FHitResult Block,RetryBlock;FVector MovedDir=Direction;bool Moved=TryStep(Direction,Step,Block);
  if(!Moved)
  {
   if(Block.bBlockingHit)
   {
    const FVector HitN=Block.ImpactNormal.GetSafeNormal2D();
    const FVector Slide=(Direction-FVector::DotProduct(Direction,HitN)*HitN).GetSafeNormal2D();
    if(TryStep(Slide,Step,RetryBlock)){Moved=true;MovedDir=Slide;}
   }
   if(!Moved)
   {
    const FVector CenterDir=(Trail[C.TrailIndex]-P).GetSafeNormal2D();
    const float CenterStep=FMath::Min(260.f*FMath::Clamp(D,0.f,.1f),FVector::Dist2D(P,Trail[C.TrailIndex]));
    if(TryStep(CenterDir,CenterStep,RetryBlock)){Moved=true;MovedDir=CenterDir;}
   }
   if(!Moved)
   {
    const FVector Perp(-Direction.Y,Direction.X,0.f);
    if(TryStep(Perp,Step,RetryBlock)){Moved=true;MovedDir=Perp;}
    else if(TryStep(-Perp,Step,RetryBlock)){Moved=true;MovedDir=-Perp;}
   }
  }
  C.Actor->SetExpeditionWalking(Moved);if(Moved)C.Actor->SetActorRotation(MovedDir.Rotation());
 }
}
void ATowerExpedition::Tick(float D)
{
 Super::Tick(D);if(IsValid(Commander))for(const auto& L:Labels)if(L)L->SetWorldRotation((Commander->GetActorLocation()+FVector(0,0,100)-L->GetComponentLocation()).Rotation());
 if(!bInside || !IsValid(Commander) || !IsValid(Village))return;
 if(RenderDay!=Village->DayIndex && !Busy())BuildFloor();
 if(IsValid(GuardianBattle) && GuardianBattle->Phase==TEXT("Result") && GuardianBattle->bVictory && !FloorCleared())
 {
  RetrySaveIn-=D;if(RetrySaveIn<=0){RetrySaveIn=1;if(!CommitGuardianClear(GuardianBattle->EncounterLog))LastMessage=TEXT("Guardian defeated, but saving failed. Retrying the floor clear.");}
 }
 if(IsValid(GuardianBattle) && GuardianBattle->Phase==TEXT("Result") && GuardianBattle->bPartyDefeated)bFailurePending=true;
 if(bFailurePending)
 {
  RetrySaveIn-=D;if(RetrySaveIn>0)return;RetrySaveIn=1;
  if(IsValid(GuardianBattle)){GuardianBattle->Destroy();GuardianBattle=nullptr;}
  if(EndRun(Commander,true))bFailurePending=false;
  return;
 }
 if(Busy()){for(const auto& C:Companions)if(C.Actor)C.Actor->SetExpeditionWalking(false);return;}
 if(Commander->GetActorLocation().Z<FloorOrigin.Z-500)
 {Commander->GetCharacterMovement()->StopMovementImmediately();Commander->SetActorLocation(Village->TowerFloor.bCampBuilt?CampPoint():EntryPoint(),false,nullptr,ETeleportType::TeleportPhysics);Trail={Commander->GetActorLocation()};for(int32 I=0;I<Companions.Num();++I)if(Companions[I].Actor){Companions[I].TrailIndex=0;Companions[I].Actor->SetActorLocation(Commander->GetActorLocation()+FVector(0,140.f*(I+1),0));}LastMessage=TEXT("Recovered to the last safe gate. This prototype does not apply permanent death.");}
 FollowParty(D);NeedsIn+=FMath::Max(0.f,D);
 if(NeedsIn>=1){const float Effort=FMath::Min(NeedsIn,2.f)*.12f;NeedsIn=0;for(auto& A:Commander->PartyReserve->Reserve)if(Companions.ContainsByPredicate([&](const auto& C){return C.Id==A.AdventurerID;}))A.Drives.Fatigue=FMath::Min(100.f,A.Drives.Fatigue+Effort);SyncDrives();}
}
void ATowerExpedition::EndPlay(const EEndPlayReason::Type Reason)
{RestoreParty();Super::EndPlay(Reason);}
FText ATowerExpedition::StatusLine(AIsekaiVillageCharacter* P) const
{
 if(!P)return FText::GetEmpty();
 if(!bInside)
 {
  if(!At(P,GetActorLocation(),650))return FText::GetEmpty();
  FString Gate=TEXT("TOWER GATE | ");
  if(Village && Village->TowerFloor.bRunActive)Gate+=FString::Printf(TEXT("G resume the run on floor %d\n"),Village->TowerFloor.Floor);
  else if(Village){const TArray<int32> Floors=StartableFloors();Gate+=FString::Printf(TEXT("G depart for floor %d | V change start floor\n"),Floors.Contains(Village->TowerFloor.StartFloor)?Village->TowerFloor.StartFloor:Floors.Last());}
  return FText::FromString(Gate+FString::Printf(TEXT("Pack %d bread and choose an active, housed adventurer.\n%s"),BreadCost,*LastMessage));
 }
 FString Text;
 if(Village)
 {
  const auto& TF=Village->TowerFloor;
  const FString FloorTheme=TF.Floor<0?FString::Printf(TEXT("Echo Depth %d"),-TF.Floor):TF.Floor==5?TEXT("Arboreal Crucible"):TF.Floor==10?TEXT("Sanctum of the Crazed Wizard"):TF.Floor>5?TEXT("Verdant Stratum"):TEXT("Rootbound Threshold");
   Text+=FString::Printf(TEXT("%s %d | %s%s\nG interact / share bread | P eat bread | V return | F5 save\n"),TF.Floor<0?TEXT("ECHO FLOOR"):TEXT("FLOOR"),TF.Floor,*FloorTheme,TF.CurrentPlan.bBoss?TEXT(" | BOSS EXAM"):TEXT(""));
  Text+=FString::Printf(TEXT("Day %d | Camp %s | Trips home %d/%d | Guardian %s\n"),Village->DayIndex,TF.bCampBuilt?TEXT("built"):TEXT("not built"),TF.TripsHomeUsed,TripsHomeAllowed(),FloorCleared()?TEXT("cleared"):TEXT("waiting"));
  if(!TF.RunRelics.IsEmpty()){FString RelicsLine=TEXT("Relics: ");for(int32 I=0;I<TF.RunRelics.Num();++I){if(I>0)RelicsLine+=TEXT(", ");RelicsLine+=RelicName(TF.RunRelics[I]);}Text+=RelicsLine+TEXT("\n");}
  if(!FloorCleared() && !TF.CurrentPlan.Announcement.IsEmpty())Text+=TF.CurrentPlan.Announcement+TEXT("\n");
  for(ETowerPortal Portal:AvailablePortals())if(At(P,PortalPoint(Portal),220))Text+=TEXT("G: ")+PortalPreview(Portal)+TEXT("\n");
 }
 for(const auto& C:Companions)if(C.Actor && P->PartyReserve)if(const auto* A=P->PartyReserve->Reserve.FindByPredicate([&](const auto& X){return X.AdventurerID==C.Id;}))Text+=FString::Printf(TEXT("%s | fatigue %.0f/100\n"),*A->Name.ToString(),A->Drives.Fatigue);
 if(At(P,CampPoint()))Text+=Village->TowerFloor.bCampBuilt?TEXT("Camp: G rest once this visit (regular enemies respawn); V trip home.\n"):FString::Printf(TEXT("Establish camp: %d wood + %d stone.\n"),CampWoodCost,CampStoneCost);
 if(At(P,AltarPoint(),250)){const ETowerRelic Offered=CurrentFloorAltarRelic();Text+=FloorAltarAvailable()?FString::Printf(TEXT("G: Claim Relic [%s] (%s)\n"),*RelicName(Offered),*RelicDescription(Offered)):TEXT("Relic Altar: Already claimed on this floor.\n");}
 for(const auto& N:Deposits)if(At(P,FloorOrigin+N.Offset,250))Text+=FString::Printf(TEXT("G: %s x%d%s\n"),*N.Item.ToString(),N.Yield+(Village && Village->TowerFloor.RunRelics.Contains(ETowerRelic::QuarryBlessing)?1:0),DepositAvailable(N.Id)?(N.bGuarded?(FloorCleared()?TEXT(" (guardian cleared)"):TEXT(" (guardian protected)")):TEXT("")):TEXT(" (depleted today)"));
 Text+=LastMessage;return FText::FromString(Text);
}
