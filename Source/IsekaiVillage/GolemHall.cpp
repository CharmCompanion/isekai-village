#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "GatherInventoryComponent.h"
#include "GolemSparring.h"
#include "Engine/SkeletalMesh.h"
#include "Animation/AnimSequence.h"
#include "EngineUtils.h"

bool AVillageRuntime::CanUseAdventureHall(AIsekaiVillageCharacter* P) const
{
 if(!bUseGolemVillage || !bUseOrganicGolemNeeds || !IsValid(P) || P->GetWorld()!=GetWorld())return false;
 return Plots.ContainsByPredicate([&](const FTownPlot& Plot){return Plot.bBuilt && !Plot.bScenery && Plot.Kind==ETownBuilding::Guild && FVector::DistSquared2D(P->GetActorLocation(),Plot.Location+Plot.StakeOffset)<=FMath::Square(450.f);});
}
int32 AVillageRuntime::FreeAdventurerBeds(AIsekaiVillageCharacter* P) const
{
 int32 Beds=0,Occupied=0;TSet<FName> Housed;
 for(const auto& Plot:Plots)if(Plot.bBuilt && !Plot.bScenery && Plot.Kind==ETownBuilding::House)Beds+=FMath::Max(0,Plot.BedBonus-(Plot.CatalogId==TEXT("InheritedHouse")?1:0));
 for(const auto& R:GolemResidents)if(!R.HomePlot.IsNone()){++Occupied;if(!R.AdventurerId.IsNone())Housed.Add(R.AdventurerId);}
 if(P && P->PartyReserve)for(const auto& A:P->PartyReserve->Reserve)if(!Housed.Contains(A.AdventurerID))++Occupied;
 return FMath::Max(0,Beds-Occupied);
}
USkeletalMesh* AVillageRuntime::FindAdventurerMesh(FName ClassId,bool Female) const
{
 if(ClassId.IsNone())return nullptr;
 const FName Key(*FString::Printf(TEXT("%s_%s"),Female?TEXT("BodyB"):TEXT("BodyA"),*ClassId.ToString()));
 const auto* Mesh=AdventurerMeshes.Find(Key);return Mesh?Mesh->Get():nullptr;
}
bool AVillageRuntime::CreateGolemAdventurer(AIsekaiVillageCharacter* P,FName ClassId,bool Female,FText Name)
{
 auto Fail=[&](const TCHAR* Why){LastHallMessage=Why;return false;};
 if(!HasAuthority() || !CanUseAdventureHall(P) || !P->PartyReserve || !P->Gather)return Fail(TEXT("Stand at your adventure hall to create a golem."));
 if(AGolemSparring::FindFor(P))return Fail(TEXT("Close the sparring encounter first."));
 if(ClassId!=TEXT("Tank") && ClassId!=TEXT("Mage") && ClassId!=TEXT("Ranger") && ClassId!=TEXT("Healer"))return Fail(TEXT("Choose a basic golem class."));
 USkeletalMesh* Mesh=FindAdventurerMesh(ClassId,Female);
 if(!Mesh)return Fail(TEXT("This body and outfit are not available."));
 UAnimSequence* Idle=Female?FemaleWorkerIdle.Get():MaleWorkerIdle.Get();UAnimSequence* Walk=Female?FemaleWorkerWalk.Get():MaleWorkerWalk.Get();
 if((Idle && Idle->GetSkeleton()!=Mesh->GetSkeleton()) || (Walk && Walk->GetSkeleton()!=Mesh->GetSkeleton()))return Fail(TEXT("This outfit needs compatible movement animations."));
 FString Label=Name.ToString().TrimStartAndEnd();
 if(Label.Len()>40 || Label.Contains(TEXT("\n")) || Label.Contains(TEXT("\r")) || Label.Contains(TEXT("\t")))return Fail(TEXT("Use a single-line name of 40 characters or fewer."));
 VillagePlayer=P;RestoreVillagePlayer();ReconcileGolemPopulation();
 if(FreeAdventurerBeds(P)<1)return Fail(TEXT("Build or upgrade housing to provide a free bed."));
 if(GolemStoneCost<0 || GolemWoodCost<0 || (GolemStoneCost==0 && GolemWoodCost==0))return Fail(TEXT("The creation recipe needs a valid resource cost."));
 if(P->Gather->GetCount(TEXT("Stone"))<GolemStoneCost || P->Gather->GetCount(TEXT("Wood"))<GolemWoodCost)return Fail(TEXT("Not enough stone and wood. Collect worker deliveries at the hall."));
 const auto PreviousRoster=P->PartyReserve->Reserve;const auto PreviousResidents=GolemResidents;
 FHiredAdventurer A;A.GolemId=FGuid::NewGuid();A.AdventurerID=FName(*(TEXT("Golem_")+A.GolemId.ToString(EGuidFormats::Digits)));A.ClassId=ClassId;A.bHasChosenBody=true;A.bFemaleBody=Female;
 A.Name=FText::FromString(Label.IsEmpty()?FString::Printf(TEXT("%s %d"),*ClassId.ToString(),PreviousRoster.Num()+1):Label);
 UGolemNeedsLibrary::Initialize(A.Drives,A.GolemId);A.Drives.Interest=ClassId==TEXT("Tank")?FName(TEXT("Guard")):ClassId==TEXT("Mage")?FName(TEXT("Magic")):ClassId==TEXT("Ranger")?FName(TEXT("Scout")):FName(TEXT("Aid"));
 A.bInActiveParty=P->PartyReserve->GetActiveCompanionCount()<P->PartyReserve->GetMaxCompanions();
 if(GolemStoneCost>0)P->Gather->Consume(TEXT("Stone"),GolemStoneCost);if(GolemWoodCost>0)P->Gather->Consume(TEXT("Wood"),GolemWoodCost);
 P->PartyReserve->Reserve.Add(A);P->PartyReserve->bUseGolemRoster=true;ReconcileGolemPopulation();
 if(!SaveVillageState(P))
 {
  for(TActorIterator<AVillageGolemCitizen> It(GetWorld());It;++It)if(It->GetOwner()==this && It->GolemId==A.GolemId)It->Destroy();
  P->PartyReserve->Reserve=PreviousRoster;GolemResidents=PreviousResidents;P->Gather->AddItem(TEXT("Stone"),GolemStoneCost);P->Gather->AddItem(TEXT("Wood"),GolemWoodCost);
  return Fail(TEXT("Could not save. Creation was cancelled and resources returned."));
 }
 LastHallMessage=FString::Printf(TEXT("Created %s. %s"),*A.Name.ToString(),A.bInActiveParty?TEXT("Added to the active party."):TEXT("Added to the reserve; choose who to bring below."));return true;
}
bool AVillageRuntime::SetAdventurerActive(AIsekaiVillageCharacter* P,FName Id,bool Active)
{
 auto Fail=[&](const TCHAR* Why){LastHallMessage=Why;return false;};
 if(!HasAuthority() || !CanUseAdventureHall(P) || !P->PartyReserve)return Fail(TEXT("Manage your party at the adventure hall."));
 if(AGolemSparring::FindFor(P))return Fail(TEXT("Close the sparring encounter first."));
 VillagePlayer=P;RestoreVillagePlayer();ReconcileGolemPopulation();
 auto* A=P->PartyReserve->Reserve.FindByPredicate([&](const FHiredAdventurer& X){return X.AdventurerID==Id;});if(!A)return Fail(TEXT("Choose an existing adventurer."));
 if(A->bAssignedToRampage)return Fail(TEXT("This adventurer is away on an expedition."));
 if(A->bInActiveParty==Active){LastHallMessage=TEXT("Party selection is already set.");return true;}
 if(Active)
 {
  if(!GolemResidents.ContainsByPredicate([&](const auto& R){return R.AdventurerId==Id && !R.HomePlot.IsNone();}))return Fail(TEXT("This adventurer needs housing first."));
  if(P->PartyReserve->GetActiveCompanionCount()>=P->PartyReserve->GetMaxCompanions())return Fail(TEXT("The active party is full. Bench someone first."));
 }
 const bool Before=A->bInActiveParty;A->bInActiveParty=Active;
 if(!SaveVillageState(P)){A->bInActiveParty=Before;return Fail(TEXT("Could not save. Party selection was restored."));}
 LastHallMessage=Active?TEXT("Adventurer added to the active party."):TEXT("Adventurer moved to the reserve.");return true;
}
