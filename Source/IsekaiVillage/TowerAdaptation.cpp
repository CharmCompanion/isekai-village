#include "TowerAdaptation.h"

void FTowerEncounterModifiers::Combine(const FTowerEncounterModifiers& O)
{
 HealthMult*=O.HealthMult;DamageMult*=O.DamageMult;PhysicalTakenMult*=O.PhysicalTakenMult;MagicTakenMult*=O.MagicTakenMult;
 HealingMult*=O.HealingMult;GuardMult*=O.GuardMult;EnemyRecoveryMult*=O.EnemyRecoveryMult;SupportDamageMult*=O.SupportDamageMult;
 EnrageStep+=O.EnrageStep;ShieldHits+=O.ShieldHits;bSureHit|=O.bSureHit;bFocusCarry|=O.bFocusCarry;
}

static FTowerCounterRule MakeRule(FName Id,ETowerHabit Habit,float Cost,const TCHAR* Announcement,const TCHAR* Opening)
{
 FTowerCounterRule R;R.Id=Id;R.Habit=Habit;R.Cost=Cost;R.Announcement=Announcement;R.Opening=Opening;return R;
}

static const TCHAR* ElementName(EElement E)
{
 switch(E){case EElement::Fire:return TEXT("Fire");case EElement::Water:return TEXT("Water");case EElement::Earth:return TEXT("Earth");default:return TEXT("Wind");}
}

static FTowerCounterRule MakeElementRule(FName Id,ETowerHabit Habit,EElement Used,const TCHAR* Announcement)
{
 FTowerCounterRule R=MakeRule(Id,Habit,5,Announcement,TEXT(""));R.bSetsElement=true;R.EnemyElement=UTowerAdaptationLibrary::ElementThatBeats(Used);
 R.Opening=ElementName(UTowerAdaptationLibrary::ElementThatBeats(R.EnemyElement));return R;
}

TArray<FTowerCounterRule> UTowerAdaptationLibrary::DefaultCounterRules()
{
 TArray<FTowerCounterRule> Rules;
 Rules.Add(MakeElementRule("Damp",ETowerHabit::Fire,EElement::Fire,TEXT("Damp halls drown your flame.")));
 Rules.Add(MakeElementRule("Bedrock",ETowerHabit::Water,EElement::Water,TEXT("Packed earth drinks your water.")));
 Rules.Add(MakeElementRule("Gale",ETowerHabit::Earth,EElement::Earth,TEXT("Winds wear down your stone.")));
 Rules.Add(MakeElementRule("Kiln",ETowerHabit::Wind,EElement::Wind,TEXT("Furnace heat swallows your wind.")));
 FTowerCounterRule R=MakeRule("Hardened",ETowerHabit::Physical,6,TEXT("Hardened shells blunt your blades."),TEXT("magic"));R.Modifiers.PhysicalTakenMult=.7f;R.Modifiers.MagicTakenMult=1.2f;Rules.Add(R);
 R=MakeRule("Warded",ETowerHabit::Magic,6,TEXT("Wards drink your spells."),TEXT("physical attacks"));R.Modifiers.MagicTakenMult=.7f;R.Modifiers.PhysicalTakenMult=1.2f;Rules.Add(R);
 R=MakeRule("Sunder",ETowerHabit::Guard,6,TEXT("Heavy blows break your guard."),TEXT("evasion and fast kills"));R.Modifiers.GuardMult=.4f;R.Modifiers.HealthMult=.9f;Rules.Add(R);
 R=MakeRule("SureStrike",ETowerHabit::Evasion,6,TEXT("Patient strikes find you anyway."),TEXT("guarding and healing"));R.Modifiers.bSureHit=true;R.Modifiers.DamageMult=.85f;Rules.Add(R);
 R=MakeRule("Wither",ETowerHabit::Healing,6,TEXT("A withering air spoils your healing."),TEXT("burst damage"));R.Modifiers.HealingMult=.5f;R.Modifiers.DamageMult=.9f;Rules.Add(R);
 R=MakeRule("Shielded",ETowerHabit::Burst,6,TEXT("Shields soak your opening blows."),TEXT("steady pressure"));R.Modifiers.ShieldHits=2;R.Modifiers.HealthMult=.9f;Rules.Add(R);
 R=MakeRule("Enrage",ETowerHabit::Grind,6,TEXT("They grow angrier the longer you wait."),TEXT("a quick finish"));R.Modifiers.EnrageStep=.1f;R.Modifiers.HealthMult=.85f;Rules.Add(R);
 R=MakeRule("Marked",ETowerHabit::Carry,7,TEXT("They hunt the one who carries you."),TEXT("your other members"));R.Modifiers.bFocusCarry=true;R.Modifiers.SupportDamageMult=1.25f;Rules.Add(R);
 R=MakeRule("Elite",ETowerHabit::LargeParty,8,TEXT("Fewer, stronger foes meet your crowd."),TEXT("slow recovery between their turns"));R.Modifiers.HealthMult=1.5f;R.Modifiers.EnemyRecoveryMult=1.3f;Rules.Add(R);
 return Rules;
}

FString UTowerAdaptationLibrary::HabitName(ETowerHabit Habit)
{
 static const TCHAR* Names[]={TEXT("fire"),TEXT("water"),TEXT("earth"),TEXT("wind"),TEXT("physical attacks"),TEXT("magic"),TEXT("guarding"),TEXT("evasion"),TEXT("healing"),TEXT("burst"),TEXT("long fights"),TEXT("carry"),TEXT("large party")};
 const int32 I=(int32)Habit;return I<UE_ARRAY_COUNT(Names)?Names[I]:TEXT("habit");
}

EElement UTowerAdaptationLibrary::ElementThatBeats(EElement Element)
{
 switch(Element){case EElement::Fire:return EElement::Water;case EElement::Wind:return EElement::Fire;case EElement::Earth:return EElement::Wind;default:return EElement::Earth;}
}

float UTowerAdaptationLibrary::EaseScore(const FTowerFloorLog& Log)
{
 if(Log.Fights<=0)return .5f;
 const float HealthLost=Log.PartyMaxHealth>0?Log.DamageTaken/Log.PartyMaxHealth:0;
 const float Knocked=Log.PartySize>0?(float)Log.Knockouts/Log.PartySize:0;
 const float Slow=FMath::Max(0.f,(float)Log.Actions/Log.Fights-4)*.04f;
 return FMath::Clamp(1-HealthLost*.9f-Knocked*.5f-Slow,0.f,1.f);
}

int32 UTowerAdaptationLibrary::ClearGrade(float Ease){return Ease<.35f?0:Ease<.6f?1:Ease<.85f?2:3;}

bool UTowerAdaptationLibrary::IsBossFloor(int32 Floor,int32 BossInterval)
{
 return BossInterval>0&&Floor!=0&&FMath::Abs(Floor)%BossInterval==0;
}

float UTowerAdaptationLibrary::BaseBudget(int32 Floor)
{
 // Negative floors start past floor 100, the working target for the main tower.
 const int32 Depth=Floor<0?100+FMath::Abs(Floor):FMath::Max(1,Floor);
 return 12+3*(Depth-1);
}

int32 UTowerAdaptationLibrary::LeapDistance(int32 Floor,int32 Grade,int32 BossInterval)
{
 const int32 Depth=FMath::Abs(Floor);
 if(Depth<3||Grade<2||IsBossFloor(Depth+1,BossInterval))return 0;
 int32 Distance=Grade>=3?3:2;
 for(int32 Step=1;Step<Distance;++Step)if(IsBossFloor(Depth+Step,BossInterval)){Distance=Step;break;}
 return Distance>=2?Distance:0;
}

int32 UTowerAdaptationLibrary::TripsHomeForRank(int32 GuildRank){return GuildRank<=0?1:GuildRank==1?2:GuildRank>=4?4:3;}

void UTowerAdaptationLibrary::RecordFloor(FTowerMemory& Memory,const FTowerFloorLog& Log,bool bHoldMemory)
{
 TMap<ETowerHabit,float> Shares;float Style=0;
 for(const TPair<ETowerHabit,float>& H:Log.Habits)if(H.Key<ETowerHabit::Burst)Style+=H.Value;
 for(const TPair<ETowerHabit,float>& H:Log.Habits)if(H.Key<ETowerHabit::Burst&&Style>0)Shares.Add(H.Key,H.Value/Style);
 if(Log.Fights>0)
 {
  const float PerFight=(float)Log.Actions/Log.Fights;
  if(PerFight<=3)Shares.Add(ETowerHabit::Burst,.6f);else if(PerFight>=8)Shares.Add(ETowerHabit::Grind,.6f);
 }
 if(Log.PartySize>=3)Shares.Add(ETowerHabit::LargeParty,.6f);
 float Total=0;FName Top;float TopDamage=0;
 for(const TPair<FName,float>& M:Log.MemberDamage){Total+=M.Value;if(M.Value>TopDamage){TopDamage=M.Value;Top=M.Key;}}
 if(Log.PartySize>=2&&Total>0&&TopDamage/Total>=.6f){Shares.Add(ETowerHabit::Carry,.6f);Memory.CarryId=Top;}
 for(int32 I=0;I<(int32)ETowerHabit::Count;++I)
 {
  const ETowerHabit H=(ETowerHabit)I;float& W=Memory.Weights.FindOrAdd(H);
  const float Next=W*MemoryDecay+Shares.FindRef(H)*(1-MemoryDecay);
  W=bHoldMemory?FMath::Max(W,Next):Next;
 }
 Memory.LastEase=EaseScore(Log);++Memory.FloorsRecorded;
}

TArray<ETowerHabit> UTowerAdaptationLibrary::NoticedHabits(const FTowerMemory& Memory,int32 Max,bool bForce)
{
 TArray<TPair<ETowerHabit,float>> Sorted;
 for(const TPair<ETowerHabit,float>& W:Memory.Weights)if(W.Value>(bForce?0.f:NoticeThreshold-KINDA_SMALL_NUMBER))Sorted.Add(W);
 Sorted.Sort([](const TPair<ETowerHabit,float>& A,const TPair<ETowerHabit,float>& B){return A.Value!=B.Value?A.Value>B.Value:A.Key<B.Key;});
 TArray<ETowerHabit> Out;for(int32 I=0;I<Sorted.Num()&&Out.Num()<Max;++I)Out.Add(Sorted[I].Key);return Out;
}

FTowerFloorPlan UTowerAdaptationLibrary::PlanFloor(int32 Floor,const FTowerMemory& Memory,const TArray<FTowerCounterRule>& Rules,float ExtraBudget,int32 BossInterval)
{
 FTowerFloorPlan Plan;Plan.Floor=Floor;Plan.bBoss=IsBossFloor(Floor,BossInterval);
 const bool bNegative=Floor<0;const float Base=BaseBudget(Floor);
 const float Pressure=Memory.FloorsRecorded>0?.85f+.5f*Memory.LastEase:1.f;
 Plan.Budget=Base*Pressure+FMath::Max(0.f,ExtraBudget);
 float Spend=Plan.Budget;

 static const float TierCost[]={0,3,6,10};static const float TierBudget[]={0,18,28,42};
 int32 Tier=0;for(int32 T=3;T>0;--T)if(Plan.Budget>=TierBudget[T]){Tier=T;break;}
 if(Plan.bBoss||bNegative)Tier=FMath::Min(3,Tier+1);
 Plan.Intelligence=(ETowerIntelligence)Tier;Spend-=TierCost[Tier];

 const bool bForce=Plan.bBoss||bNegative;
 const int32 MaxRules=bForce?3:FMath::Abs(Floor)>=10?2:1;
 TArray<FString> Lines;
 for(ETowerHabit Habit:NoticedHabits(Memory,MaxRules,bForce))
 {
  const FTowerCounterRule* Rule=Rules.FindByPredicate([Habit](const FTowerCounterRule& R){return R.Habit==Habit;});
  if(!Rule||Rule->Cost>Spend||(Rule->bSetsElement&&Plan.bHasElement))continue;
  Spend-=Rule->Cost;Plan.Rules.Add(Rule->Id);Plan.Modifiers.Combine(Rule->Modifiers);
  if(Rule->bSetsElement){Plan.bHasElement=true;Plan.EnemyElement=Rule->EnemyElement;}
  if(Rule->Modifiers.bFocusCarry)Plan.CarryId=Memory.CarryId;
  Lines.Add(FString::Printf(TEXT("The tower remembers your %s. %s Opening: %s."),*HabitName(Habit),*Rule->Announcement,*Rule->Opening));
 }
 Plan.bTowerUnsure=!bForce&&Memory.FloorsRecorded>0&&Plan.Rules.IsEmpty();
 if(Plan.bTowerUnsure){Plan.RewardMult*=1.25f;Lines.Add(TEXT("The tower cannot read you. Rewards x1.25."));}

 const float Stat=1+FMath::Max(0.f,Spend-12)/24;
 Plan.Modifiers.HealthMult*=Stat;Plan.Modifiers.DamageMult*=1+(Stat-1)*.5f;
 if(Plan.bBoss){Plan.Modifiers.HealthMult*=1.8f;Plan.RewardMult*=2;}
 if(bNegative)Plan.RewardMult*=1.5f;

 static const ETowerHabit Styles[]={ETowerHabit::Physical,ETowerHabit::Magic,ETowerHabit::Guard,ETowerHabit::Evasion,ETowerHabit::Healing};
 float Best=-1;for(ETowerHabit S:Styles){const float W=Memory.Weights.FindRef(S);if(W>Best){Best=W;Plan.MimicHabit=S;}}

 static const TCHAR* Minds[]={TEXT("on instinct"),TEXT("like hunters"),TEXT("like tacticians"),TEXT("by copying you")};
 const FString Title=bNegative?FString::Printf(TEXT("Echo floor %d"),Floor):FString::Printf(TEXT("Floor %d"),Floor);
 Plan.Announcement=FString::Printf(TEXT("%s%s. Enemies fight %s."),*Title,Plan.bBoss?TEXT(" - exam"):TEXT(""),Minds[Tier]);
 for(const FString& L:Lines)Plan.Announcement+=TEXT(" ")+L;
 return Plan;
}
