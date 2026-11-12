#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "GolemSparring.h"
#include "VillageRuntime.h"
#include "VillageGolemCitizen.h"
#include "PartyReserveComponent.h"
#include "GatherInventoryComponent.h"
#include "IsekaiVillageCharacter.h"
#include "SlimeRunicMagic.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/StaticMeshActor.h"
#include "Components/StaticMeshComponent.h"
#include "Kismet/GameplayStatics.h"
#include "EngineUtils.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGolemSparringRulesTest,"IsekaiVillage.Combat.LearnedSkillSparring",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGolemSparringRulesTest::RunTest(const FString& Parameters)
{
 const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);W->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/Engine.GameModeBase"));W->SetGameMode(URL);
 FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 auto* Floor=W->SpawnActor<AStaticMeshActor>(FVector(0,0,-50),FRotator::ZeroRotator,P);Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Floor->SetActorScale3D(FVector(80,80,1));
 auto* V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,P);auto* Player=W->SpawnActor<AIsekaiVillageCharacter>(FVector(1000,-500,99),FRotator::ZeroRotator,P);
 V->bUseAuthoredPlots=true;V->bUseGolemVillage=true;V->bUseOrganicGolemNeeds=true;V->SparringSlimeClass=ASlimeRunicMage::StaticClass();V->ConstructionSaveSlot=TEXT("Automation_Sparring_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);
 FTownPlot Home;Home.Id=TEXT("Home");Home.Kind=ETownBuilding::House;Home.bBuilt=true;Home.BedBonus=3;Home.StakeOffset=FVector(0,-500,0);Home.BuildingClass=AStaticMeshActor::StaticClass();
 FTownPlot Hall=Home;Hall.Id=TEXT("Hall");Hall.Kind=ETownBuilding::Guild;Hall.BedBonus=0;Hall.Location=FVector(3000,0,0);
 FTownPlot Yard=Hall;Yard.Id=TEXT("Yard");Yard.Kind=ETownBuilding::Training;Yard.Location=FVector(1000,0,0);V->AuthoredPlots={Home,Hall,Yard};V->InitializeConstruction();V->SaveVillageState(Player);
 Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("Sparring student")));V->ReconcileGolemPopulation();
 auto& A=Player->PartyReserve->Reserve[0];A.Drives.Practice.Add(TEXT("Guard"),119);
 for(auto& R:V->GolemResidents)if(R.AdventurerId==A.AdventurerID)R.Drives=A.Drives;
 auto* B=W->SpawnActor<AGolemSparring>(FVector::ZeroVector,FRotator::ZeroRotator,P);
 TestTrue(TEXT("Housed active adventurer can assemble"),B->BeginSparring(V,Player));TestEqual(TEXT("One active member participates"),B->Members.Num(),1);
 if(B->Members.IsEmpty()){V->bUseGolemVillage=false;W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return false;}
 auto* Actor=B->Members[0].Actor.Get();Actor->SetActorLocation(B->Members[0].Formation+FVector(0,0,99));B->Tick(.1f);
 TestEqual(TEXT("Assembly enters a command turn"),B->Phase,FName(TEXT("AwaitCommand")));TestTrue(TEXT("Village movement is paused only for the sparring member"),Actor->ActorHasTag(TEXT("ElrhunSparring")));
 TestFalse(TEXT("Unlearned bolt rejected"),B->ExecuteAction(TEXT("ArcaneBolt")));TestEqual(TEXT("Locked skill spends no TP"),B->Members[0].TP,40.f);TestEqual(TEXT("Rejected action spends no turn"),B->Phase,FName(TEXT("AwaitCommand")));
 B->Enemy->SetCanBeDamaged(false);TestFalse(TEXT("Immune target does not award a hit"),B->ExecuteAction(TEXT("Strike")));TestEqual(TEXT("Rejected hit grants no practice"),A.Drives.Practice.FindRef(TEXT("Guard")),119.f);B->Enemy->SetCanBeDamaged(true);
 TestTrue(TEXT("Basic defend is available before learning Guard Stance"),B->ExecuteAction(TEXT("Defend")));TestEqual(TEXT("Raising guard alone grants no experience"),A.Drives.Practice.FindRef(TEXT("Guard")),119.f);
 TestFalse(TEXT("Commands rejected during enemy turn"),B->ExecuteAction(TEXT("Strike")));
 TestEqual(TEXT("Outside damage cannot interfere with a training participant"),UGameplayStatics::ApplyDamage(Actor,50.f,nullptr,Player,nullptr),0.f);B->Tick(1.f);
 TestEqual(TEXT("Basic defend reduces actual incoming damage"),B->Members[0].Health,91.f);TestTrue(TEXT("Successful defense can unlock Guard Stance"),A.Drives.Skills.Contains(TEXT("GuardStance")));
 TestTrue(TEXT("New skill is usable on next command"),B->ExecuteAction(TEXT("GuardStance")));TestEqual(TEXT("Guard Stance charges TP once"),B->Members[0].TP,36.f);B->Tick(1.f);TestTrue(TEXT("Learned stance protects more than basic defend"),FMath::IsNearlyEqual(B->Members[0].Health,86.8f,.01f));
 A.Drives.Skills.Append({TEXT("ArcaneBolt"),TEXT("FirstAid"),TEXT("EvasiveStep")});A.Drives.Passives.Append({TEXT("FocusedMind"),TEXT("EnduringCore"),TEXT("CalmCore")});for(auto& R:V->GolemResidents)if(R.AdventurerId==A.AdventurerID)R.Drives=A.Drives;
 const float EnemyBefore=B->Enemy->Health;TestTrue(TEXT("Learned bolt deals damage"),B->ExecuteAction(TEXT("ArcaneBolt")));TestEqual(TEXT("Bolt has its actual damage effect"),B->Enemy->Health,EnemyBefore-30);TestTrue(TEXT("Focused Mind reduces actual TP cost"),FMath::IsNearlyEqual(B->Members[0].TP,28.8f,.01f));B->Tick(1.f);
 const float Injured=B->Members[0].Health;const float TpBeforeHeal=B->Members[0].TP;B->Members[0].Health=100;TestFalse(TEXT("Healing a full-health ally is rejected"),B->ExecuteAction(TEXT("FirstAid"),0));TestEqual(TEXT("Invalid healing spends no TP"),B->Members[0].TP,TpBeforeHeal);B->Members[0].Health=Injured;
 const float Missing=100-B->Members[0].Health;TestTrue(TEXT("Learned First Aid heals"),B->ExecuteAction(TEXT("FirstAid"),0));TestTrue(TEXT("Calm Core improves actual healing"),FMath::IsNearlyEqual(B->Members[0].Health,100-FMath::Max(0.f,Missing-27.5f),.01f));B->Tick(1.f);
 const float HP=B->Members[0].Health;const float Scout=A.Drives.Practice.FindRef(TEXT("Scout"));TestTrue(TEXT("Evasive Step can be readied"),B->ExecuteAction(TEXT("EvasiveStep")));TestEqual(TEXT("Readying evasion alone grants no experience"),A.Drives.Practice.FindRef(TEXT("Scout")),Scout);B->Tick(1.f);
 TestEqual(TEXT("Actual incoming hit is evaded"),B->Members[0].Health,HP);TestTrue(TEXT("Successful evasion earns personal practice"),A.Drives.Practice.FindRef(TEXT("Scout"))>Scout);
 B->Members[0].TP=0;const float Ready=B->Members[0].ReadyAt;TestFalse(TEXT("Insufficient TP rejects bolt"),B->ExecuteAction(TEXT("ArcaneBolt")));TestEqual(TEXT("Failed skill cannot advance initiative"),B->Members[0].ReadyAt,Ready);
 B->CancelSparring();TestEqual(TEXT("Cancel resolves safely"),B->Phase,FName(TEXT("Result")));TestFalse(TEXT("Movement resumes after sparring"),Actor->ActorHasTag(TEXT("ElrhunSparring")));TestTrue(TEXT("Training does not delete a roster member"),Player->PartyReserve->Reserve.Num()==1);
 V->ReloadVillageState(Player);TestTrue(TEXT("Combat-earned skill persists through village reload"),Player->PartyReserve->Reserve[0].Drives.Skills.Contains(TEXT("GuardStance")));TestTrue(TEXT("Actual combat practice survives reload"),Player->PartyReserve->Reserve[0].Drives.Practice.FindRef(TEXT("Scout"))>Scout);
 V->bUseGolemVillage=false;UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot,0);W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return true;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FGolemPartyTurnsTest,"IsekaiVillage.Combat.PartyTurnsAndVictory",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FGolemPartyTurnsTest::RunTest(const FString& Parameters)
{
 const auto IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);W->SetGameInstance(NewObject<UGameInstance>(GEngine));FURL URL;URL.AddOption(TEXT("game=/Script/Engine.GameModeBase"));W->SetGameMode(URL);
 FActorSpawnParameters P;P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 auto* Floor=W->SpawnActor<AStaticMeshActor>(FVector(0,0,-50),FRotator::ZeroRotator,P);Floor->GetStaticMeshComponent()->SetStaticMesh(LoadObject<UStaticMesh>(nullptr,TEXT("/Engine/BasicShapes/Cube.Cube")));Floor->GetStaticMeshComponent()->SetCollisionProfileName(TEXT("BlockAll"));Floor->SetActorScale3D(FVector(80,80,1));
 auto* V=W->SpawnActor<AVillageRuntime>(FVector::ZeroVector,FRotator::ZeroRotator,P);auto* Player=W->SpawnActor<AIsekaiVillageCharacter>(FVector(1000,-500,99),FRotator::ZeroRotator,P);
 V->bUseAuthoredPlots=true;V->bUseGolemVillage=true;V->bUseOrganicGolemNeeds=true;V->SparringSlimeClass=ASlimeRunicMage::StaticClass();V->ConstructionSaveSlot=TEXT("Automation_PartyTurns_")+FGuid::NewGuid().ToString(EGuidFormats::Digits);
 FTownPlot Home;Home.Id=TEXT("Home");Home.Kind=ETownBuilding::House;Home.bBuilt=true;Home.BedBonus=4;Home.StakeOffset=FVector(0,-500,0);Home.BuildingClass=AStaticMeshActor::StaticClass();
 FTownPlot Hall=Home;Hall.Id=TEXT("Hall");Hall.Kind=ETownBuilding::Guild;Hall.BedBonus=0;Hall.Location=FVector(3000,0,0);FTownPlot Yard=Hall;Yard.Id=TEXT("Yard");Yard.Kind=ETownBuilding::Training;Yard.Location=FVector(1000,0,0);V->AuthoredPlots={Home,Hall,Yard};V->InitializeConstruction();V->SaveVillageState(Player);
 Player->PartyReserve->ActivePartyCap=3;Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("First")));Player->PartyReserve->HireAdventurer(FText::FromString(TEXT("Second")));Player->PartyReserve->Reserve[0].Drives.Skills={TEXT("FirstAid"),TEXT("ArcaneBolt")};V->ReconcileGolemPopulation();
 for(auto& R:V->GolemResidents)for(const auto& A:Player->PartyReserve->Reserve)if(R.AdventurerId==A.AdventurerID)R.Drives=A.Drives;
 auto* B=W->SpawnActor<AGolemSparring>(FVector::ZeroVector,FRotator::ZeroRotator,P);TestTrue(TEXT("Multi-member party assembles"),B->BeginSparring(V,Player));
 if(!TestEqual(TEXT("Existing party capacity selects two adventurers"),B->Members.Num(),2)){V->bUseGolemVillage=false;W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return false;}
 for(auto& M:B->Members)M.Actor->SetActorLocation(M.Formation+FVector(0,0,99));B->Tick(.1f);
 TestEqual(TEXT("Stable first turn belongs to first roster member"),B->CurrentMember,0);B->ExecuteAction(TEXT("Strike"));TestEqual(TEXT("Second ready party member acts before the slime"),B->CurrentMember,1);
 TestFalse(TEXT("A member cannot use another member's learned spell"),B->ExecuteAction(TEXT("ArcaneBolt")));B->ExecuteAction(TEXT("Strike"));TestEqual(TEXT("Enemy acts after both ready allies"),B->Phase,FName(TEXT("EnemyTurn")));B->Tick(1.f);
 B->Members[1].Health=40;const float HealerHP=B->Members[0].Health;TestTrue(TEXT("First Aid can target a specific injured ally"),B->ExecuteAction(TEXT("FirstAid"),1));TestEqual(TEXT("Heal affects selected ally"),B->Members[1].Health,65.f);TestEqual(TEXT("Heal does not accidentally heal its caster"),B->Members[0].Health,HealerHP);
 TestEqual(TEXT("Faster pending member gets the next command"),B->CurrentMember,1);B->Enemy->Health=10;const int32 Wood=Player->Gather->GetCount(TEXT("Wood"));B->ExecuteAction(TEXT("Strike"));
 TestEqual(TEXT("Enemy defeat resolves the encounter"),B->Phase,FName(TEXT("Result")));TestTrue(TEXT("Victory removes temporary enemy"),!IsValid(B->Enemy));
 for(const auto& M:B->Members)TestFalse(TEXT("Victory releases every village actor"),M.Actor->ActorHasTag(TEXT("ElrhunSparring")));
 TestEqual(TEXT("Sparring grants no resource loot"),Player->Gather->GetCount(TEXT("Wood")),Wood);TestEqual(TEXT("Sparring does not delete golems"),Player->PartyReserve->Reserve.Num(),2);
 V->bUseGolemVillage=false;UGameplayStatics::DeleteGameInSlot(V->ConstructionSaveSlot,0);W->DestroyWorld(false);GEngine->DestroyWorldContext(W);return true;
}
#endif
