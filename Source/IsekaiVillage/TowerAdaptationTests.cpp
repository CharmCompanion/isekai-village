#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "TowerAdaptation.h"
#include "GolemSparring.h"

static FTowerFloorLog MakeLog(TMap<ETowerHabit,float> Habits,int32 Actions,float DamageTaken,int32 PartySize=1)
{
 FTowerFloorLog L;L.Habits=MoveTemp(Habits);L.Actions=Actions;L.Fights=1;L.PartySize=PartySize;L.PartyMaxHealth=100.f*PartySize;L.DamageTaken=DamageTaken;return L;
}

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FTowerAdaptationRulesTest,"IsekaiVillage.Tower.AdaptationRules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FTowerAdaptationRulesTest::RunTest(const FString& Parameters)
{
 const TArray<FTowerCounterRule> Rules=UTowerAdaptationLibrary::DefaultCounterRules();
 FTowerMemory Fresh;
 const FTowerFloorPlan First=UTowerAdaptationLibrary::PlanFloor(1,Fresh,Rules,0);
 TestEqual(TEXT("Floor 1 with no memory keeps base health"),First.Modifiers.HealthMult,1.f);
 TestEqual(TEXT("Floor 1 with no memory keeps base damage"),First.Modifiers.DamageMult,1.f);
 TestTrue(TEXT("Floor 1 enemies fight on instinct with no counters"),First.Intelligence==ETowerIntelligence::Instinct && First.Rules.IsEmpty() && !First.bTowerUnsure);

 FTowerMemory Striker;UTowerAdaptationLibrary::RecordFloor(Striker,MakeLog({{ETowerHabit::Physical,6}},6,20),false);
 TestTrue(TEXT("One physical-only floor is noticed"),UTowerAdaptationLibrary::NoticedHabits(Striker,3,false).Contains(ETowerHabit::Physical));
 const FTowerFloorPlan Second=UTowerAdaptationLibrary::PlanFloor(2,Striker,Rules,0);
 TestTrue(TEXT("Physical habit buys the Hardened counter"),Second.Rules.Contains(FName(TEXT("Hardened"))));
 TestEqual(TEXT("Hardened blunts physical damage"),Second.Modifiers.PhysicalTakenMult,.7f);
 TestTrue(TEXT("Hardened leaves magic as the opening"),Second.Modifiers.MagicTakenMult>1.f && Second.Announcement.Contains(TEXT("magic")));

 FTowerMemory Faded=Striker;for(int32 I=0;I<2;++I)UTowerAdaptationLibrary::RecordFloor(Faded,MakeLog({{ETowerHabit::Magic,6}},6,20),false);
 const TArray<ETowerHabit> Now=UTowerAdaptationLibrary::NoticedHabits(Faded,3,false);
 TestTrue(TEXT("Two floors of magic fade the physical habit and teach magic"),!Now.Contains(ETowerHabit::Physical) && Now.Contains(ETowerHabit::Magic));

 FTowerMemory Varied;UTowerAdaptationLibrary::RecordFloor(Varied,MakeLog({{ETowerHabit::Physical,2},{ETowerHabit::Magic,2},{ETowerHabit::Guard,2},{ETowerHabit::Healing,2}},5,20),false);
 const FTowerFloorPlan Unsure=UTowerAdaptationLibrary::PlanFloor(2,Varied,Rules,0);
 TestTrue(TEXT("Varied play leaves the tower unsure"),Unsure.bTowerUnsure && Unsure.Rules.IsEmpty());
 TestEqual(TEXT("An unsure tower pays better rewards"),Unsure.RewardMult,1.25f);

 const FTowerFloorPlan Boss=UTowerAdaptationLibrary::PlanFloor(5,Varied,Rules,0);
 TestTrue(TEXT("Floor 5 is a boss exam"),Boss.bBoss && !Boss.bTowerUnsure);
 TestTrue(TEXT("Bosses test several habits even when the tower is unsure"),Boss.Rules.Num()>=2);
 TestTrue(TEXT("Bosses are tougher"),Boss.Modifiers.HealthMult>=1.8f*.85f*.9f);

 const FTowerFloorPlan Echo=UTowerAdaptationLibrary::PlanFloor(-1,Varied,Rules,0);
 TestTrue(TEXT("Echo floors start harder than floor 100"),Echo.Budget>UTowerAdaptationLibrary::BaseBudget(100));
 TestTrue(TEXT("Echo floors stack counters"),Echo.Rules.Num()>=2 && Echo.Intelligence==ETowerIntelligence::Mimic);
 FTowerMemory Held=Striker;UTowerAdaptationLibrary::RecordFloor(Held,MakeLog({{ETowerHabit::Magic,6}},6,20),true);
 TestTrue(TEXT("Echo floors do not let memory fade"),Held.Weights.FindRef(ETowerHabit::Physical)>=Striker.Weights.FindRef(ETowerHabit::Physical));

 TestEqual(TEXT("Leap is not offered on early floors"),UTowerAdaptationLibrary::LeapDistance(1,3),0);
 TestEqual(TEXT("Leap stops on the boss floor"),UTowerAdaptationLibrary::LeapDistance(3,3),2);
 TestEqual(TEXT("Leap is not offered right before a boss"),UTowerAdaptationLibrary::LeapDistance(4,3),0);
 TestEqual(TEXT("A strong clear offers Leap +2"),UTowerAdaptationLibrary::LeapDistance(6,2),2);
 TestEqual(TEXT("A perfect clear offers Leap +3"),UTowerAdaptationLibrary::LeapDistance(6,3),3);
 TestEqual(TEXT("Leap +3 shortens so it never skips a boss"),UTowerAdaptationLibrary::LeapDistance(8,3),2);
 TestEqual(TEXT("An ordinary clear offers no Leap"),UTowerAdaptationLibrary::LeapDistance(6,1),0);

 TestEqual(TEXT("Rank D: one trip home"),UTowerAdaptationLibrary::TripsHomeForRank(0),1);
 TestEqual(TEXT("Rank C: two trips home"),UTowerAdaptationLibrary::TripsHomeForRank(1),2);
 TestEqual(TEXT("Rank B: three trips home"),UTowerAdaptationLibrary::TripsHomeForRank(2),3);
 TestEqual(TEXT("Rank A: still three trips home"),UTowerAdaptationLibrary::TripsHomeForRank(3),3);

 TestEqual(TEXT("Water beats Fire"),AGolemSparring::ElementMultiplier(EElement::Water,EElement::Fire),1.5f);
 TestEqual(TEXT("Earth resists Water"),AGolemSparring::ElementMultiplier(EElement::Water,EElement::Earth),.6f);
 TestEqual(TEXT("Water against Wind is neutral"),AGolemSparring::ElementMultiplier(EElement::Water,EElement::Wind),1.f);
 const FTowerCounterRule* Bedrock=Rules.FindByPredicate([](const FTowerCounterRule& R){return R.Habit==ETowerHabit::Water;});
 TestTrue(TEXT("The Water counter turns enemies to Earth and leaves Wind open"),Bedrock && Bedrock->EnemyElement==EElement::Earth && Bedrock->Opening==TEXT("Wind"));

 TestEqual(TEXT("A quick, untouched clear is perfect"),UTowerAdaptationLibrary::ClearGrade(UTowerAdaptationLibrary::EaseScore(MakeLog({},3,0))),3);
 TestEqual(TEXT("A near wipe is a struggle"),UTowerAdaptationLibrary::ClearGrade(UTowerAdaptationLibrary::EaseScore(MakeLog({},12,90))),0);

 FTowerMemory Carry;FTowerFloorLog CarryLog=MakeLog({{ETowerHabit::Physical,6}},6,20,2);CarryLog.MemberDamage.Add(FName(TEXT("Ace")),90.f);CarryLog.MemberDamage.Add(FName(TEXT("Helper")),10.f);
 for(int32 I=0;I<2;++I)UTowerAdaptationLibrary::RecordFloor(Carry,CarryLog,false);
 TestEqual(TEXT("The tower marks the carry"),Carry.CarryId,FName(TEXT("Ace")));
 TestTrue(TEXT("Repeated carrying is noticed"),UTowerAdaptationLibrary::NoticedHabits(Carry,5,false).Contains(ETowerHabit::Carry));
 return true;
}
#endif
