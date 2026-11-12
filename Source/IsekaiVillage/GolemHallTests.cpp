#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "IsekaiVillageCharacter.h"
#include "PartyReserveComponent.h"
#include "GatherInventoryComponent.h"
#include "GolemSparring.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/SkeletalMesh.h"
#include "Components/SkeletalMeshComponent.h"
#include "EngineUtils.h"
#include "Kismet/GameplayStatics.h"

struct FHallFixture
{
 UWorld* W;AVillageRuntime* V;AIsekaiVillageCharacter* P;FString Slot;
 FHallFixture(int32 Beds)
 {
  const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
  W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
  FActorSpawnParameters S;S.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
  V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,S);P=W->SpawnActor<AIsekaiVillageCharacter>(FVector(0,-500,99),FRotator::ZeroRotator,S);
  V->bUseAuthoredPlots=true;V->bUseGolemVillage=true;V->bUseOrganicGolemNeeds=true;Slot=TEXT("Automation_GolemHall_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);V->ConstructionSaveSlot=Slot;
  FTownPlot Hall;Hall.Id=TEXT("Hall");Hall.Kind=ETownBuilding::Guild;Hall.bBuilt=true;Hall.StakeOffset=FVector(0,-500,0);
  FTownPlot Home=Hall;Home.Id=TEXT("Home");Home.Kind=ETownBuilding::House;Home.BedBonus=Beds;Home.Location=FVector(2000,0,0);V->AuthoredPlots={Hall,Home};
  for(const TCHAR* Body:{TEXT("BodyA"),TEXT("BodyB")})for(const TCHAR* Role:{TEXT("Tank"),TEXT("Mage"),TEXT("Ranger"),TEXT("Healer")})
  {
   const FName Key(*FString::Printf(TEXT("%s_%s"),Body,Role));const FString Path=FString::Printf(TEXT("/Game/Elrhun/Golems/PlayerBody/Outfits/SK_Native_%s_%s.SK_Native_%s_%s"),Body,Role,Body,Role);V->AdventurerMeshes.Add(Key,LoadObject<USkeletalMesh>(nullptr,*Path));
  }
  V->InitializeConstruction();V->SaveVillageState(P);P->Gather->Stacks.Reset();P->Gather->AddItem(TEXT("Stone"),100);P->Gather->AddItem(TEXT("Wood"),100);
 }
 ~FHallFixture(){V->bUseGolemVillage=false;UGameplayStatics::DeleteGameInSlot(Slot,0);W->DestroyWorld(false);GEngine->DestroyWorldContext(W);}
};
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHallCreationTest,"IsekaiVillage.Golems.HallCreationAndParty",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHallCreationTest::RunTest(const FString& Parameters)
{
 FHallFixture F(12);auto* V=F.V;auto* P=F.P;
 TestFalse(TEXT("Unknown special classes cannot be crafted as basic golems"),V->CreateGolemAdventurer(P,TEXT("Necromancer"),false,FText::GetEmpty()));
 TestFalse(TEXT("Names cannot inject extra UI lines"),V->CreateGolemAdventurer(P,TEXT("Tank"),false,FText::FromString(TEXT("Bad\nName"))));
 P->SetActorLocation(FVector(10000,0,99));TestFalse(TEXT("Creation requires the hall frontage"),V->CreateGolemAdventurer(P,TEXT("Tank"),false,FText::GetEmpty()));P->SetActorLocation(FVector(0,-500,99));
 const FName Roles[]={TEXT("Tank"),TEXT("Mage"),TEXT("Ranger"),TEXT("Healer")};const FName Interests[]={TEXT("Guard"),TEXT("Magic"),TEXT("Scout"),TEXT("Aid")};
 for(int32 I=0;I<7;++I)
 {
  TestTrue(TEXT("Craft housed adventurer"),V->CreateGolemAdventurer(P,Roles[I%4],I%2!=0,FText::FromString(FString::Printf(TEXT("Golem %d"),I))));
  const auto& A=P->PartyReserve->Reserve.Last();TestEqual(TEXT("Class sets practice focus"),A.Drives.Interest,Interests[I%4]);TestTrue(TEXT("Skills are earned rather than gifted"),A.Drives.Skills.IsEmpty() && A.Drives.Passives.IsEmpty());
  TestEqual(TEXT("Body choice is explicit"),A.bFemaleBody,I%2!=0);
  for(TActorIterator<AVillageGolemCitizen> It(F.W);It;++It)if(It->GolemId==A.GolemId)TestTrue(TEXT("Created actor uses the selected approved outfit"),It->GolemMesh->GetSkeletalMeshAsset()==V->FindAdventurerMesh(A.ClassId,A.bFemaleBody));
 }
 TestEqual(TEXT("Crafted roster can exceed the old six-recruit cap"),P->PartyReserve->Reserve.Num(),7);TestEqual(TEXT("Stone charged exactly once per creation"),P->Gather->GetCount(TEXT("Stone")),58);TestEqual(TEXT("Wood charged exactly once per creation"),P->Gather->GetCount(TEXT("Wood")),72);
 TestEqual(TEXT("Active party still respects current companion capacity"),P->PartyReserve->GetActiveCompanionCount(),1);
 const FName First=P->PartyReserve->Reserve[0].AdventurerID,Last=P->PartyReserve->Reserve[6].AdventurerID;const FGuid Id=P->PartyReserve->Reserve[6].GolemId;
 TestFalse(TEXT("Cannot activate a second member while party is full"),V->SetAdventurerActive(P,Last,true));TestTrue(TEXT("Bench existing active member"),V->SetAdventurerActive(P,First,false));TestTrue(TEXT("Choose a different reserve member"),V->SetAdventurerActive(P,Last,true));
 const float Personality=P->PartyReserve->Reserve[6].Drives.Diligence;
 V->ReloadVillageState(P);TestEqual(TEXT("Whole roster survives reload"),P->PartyReserve->Reserve.Num(),7);TestEqual(TEXT("Identity survives reload"),P->PartyReserve->Reserve[6].GolemId,Id);TestTrue(TEXT("Party selection survives reload"),P->PartyReserve->Reserve[6].bInActiveParty && !P->PartyReserve->Reserve[0].bInActiveParty);TestEqual(TEXT("Class survives reload"),P->PartyReserve->Reserve[6].ClassId,FName(TEXT("Ranger")));TestEqual(TEXT("Personality survives reload"),P->PartyReserve->Reserve[6].Drives.Diligence,Personality);TestTrue(TEXT("Female choice survives reload"),P->PartyReserve->Reserve[1].bHasChosenBody && P->PartyReserve->Reserve[1].bFemaleBody);
 V->ConstructionSaveSlot.Empty();TestFalse(TEXT("Failed save rolls back creation"),V->CreateGolemAdventurer(P,TEXT("Healer"),true,FText::FromString(TEXT("Not saved"))));TestEqual(TEXT("Failed save refunds stone"),P->Gather->GetCount(TEXT("Stone")),58);TestEqual(TEXT("Failed save refunds wood"),P->Gather->GetCount(TEXT("Wood")),72);TestEqual(TEXT("Failed save leaves no extra roster member"),P->PartyReserve->Reserve.Num(),7);V->ConstructionSaveSlot=F.Slot;
 int32 Actors=0;for(TActorIterator<AVillageGolemCitizen> It(F.W);It;++It)if(It->GetOwner()==V)++Actors;TestEqual(TEXT("Rollback removes only the unsaved actor"),Actors,8);
 return true;
}
IMPLEMENT_SIMPLE_AUTOMATION_TEST(FHallGuardsTest,"IsekaiVillage.Golems.HallResourceAndHousingGuards",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FHallGuardsTest::RunTest(const FString& Parameters)
{
 FHallFixture F(1);auto* V=F.V;auto* P=F.P;
 TestFalse(TEXT("A workplace's occupied bed is unavailable for a new adventurer"),V->CreateGolemAdventurer(P,TEXT("Mage"),true,FText::GetEmpty()));TestEqual(TEXT("Rejected housing request keeps resources"),P->Gather->GetCount(TEXT("Stone")),100);
 V->AuthoredPlots[1].BedBonus=4;V->InitializeConstruction();P->Gather->Stacks.Reset();P->Gather->AddItem(TEXT("Stone"),6);P->Gather->AddItem(TEXT("Wood"),3);
 TestFalse(TEXT("Partial recipe cannot spend any materials"),V->CreateGolemAdventurer(P,TEXT("Mage"),true,FText::GetEmpty()));TestEqual(TEXT("Insufficient wood does not consume stone"),P->Gather->GetCount(TEXT("Stone")),6);
 P->Gather->AddItem(TEXT("Wood"),1);TestTrue(TEXT("Exact recipe creates one golem"),V->CreateGolemAdventurer(P,TEXT("Mage"),true,FText::GetEmpty()));TestEqual(TEXT("Exact recipe leaves zero stone"),P->Gather->GetCount(TEXT("Stone")),0);TestEqual(TEXT("Exact recipe leaves zero wood"),P->Gather->GetCount(TEXT("Wood")),0);
 FActorSpawnParameters S;auto* Battle=F.W->SpawnActor<AGolemSparring>(FVector::ZeroVector,FRotator::ZeroRotator,S);Battle->Commander=P;Battle->Phase=TEXT("Assembling");TestFalse(TEXT("Party cannot change during an encounter"),V->SetAdventurerActive(P,P->PartyReserve->Reserve[0].AdventurerID,false));Battle->Destroy();
 P->PartyReserve->Reserve[0].bAssignedToRampage=true;TestFalse(TEXT("Away members cannot be reassigned at the hall"),V->SetAdventurerActive(P,P->PartyReserve->Reserve[0].AdventurerID,false));
 return true;
}
#endif
