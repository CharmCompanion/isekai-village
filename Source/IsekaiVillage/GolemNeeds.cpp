#include "GolemNeeds.h"

void UGolemNeedsLibrary::Initialize(FGolemDriveState& S,const FGuid& Id)
{
 if(S.bInitialized)return;
 FRandomStream R(GetTypeHash(Id));S.Diligence=R.FRandRange(.3f,.9f);S.StudyAffinity=R.FRandRange(.3f,.9f);S.Sociability=R.FRandRange(.3f,.9f);
 const FName Interests[]={TEXT("Guard"),TEXT("Magic"),TEXT("Aid"),TEXT("Scout")};S.Interest=Interests[R.RandRange(0,3)];S.bInitialized=true;
}
void UGolemNeedsLibrary::Elapse(FGolemDriveState& S,float Seconds)
{
 if(!FMath::IsFinite(Seconds)||Seconds<=0)return;
 const float D=FMath::Min(Seconds,1.f); // No offline/long-frame learning windfall.
 S.Fatigue=FMath::Clamp(S.Fatigue+D*.035f*FatigueMultiplier(S),0.f,100.f);
 S.Curiosity=FMath::Clamp(S.Curiosity+D*.03f,0.f,100.f);
 S.Loneliness=FMath::Clamp(S.Loneliness+D*.035f,0.f,100.f);
 S.Commitment=FMath::Max(0.f,S.Commitment-D);S.ThinkIn=FMath::Max(0.f,S.ThinkIn-D);S.LeisureCooldown=FMath::Max(0.f,S.LeisureCooldown-D);
}
FName UGolemNeedsLibrary::ChooseActivity(FGolemDriveState& S,bool Work,bool Study,bool Social,bool Cargo,float Urgency,bool Night)
{
 auto Score=[&](FName A)->float{
  if(A==TEXT("Rest"))return S.Fatigue*1.3f+(Night?40.f:0.f);
  if(A==TEXT("Work"))return Work ? 55.f+S.Diligence*15.f+FMath::Clamp(Urgency,0.f,1.f)*25.f+(Cargo?25.f:0.f) : -1000.f;
  if(A==TEXT("Practice"))return Study && S.LeisureCooldown<=0 ? S.Curiosity+S.StudyAffinity*15.f+(Work?5.f:30.f) : -1000.f;
  if(A==TEXT("Socialize"))return Social && S.LeisureCooldown<=0 ? S.Loneliness+S.Sociability*15.f : -1000.f;
  return -1000.f;
 };
 FName Best=TEXT("Rest");float High=Score(Best);
 for(FName A:{FName(TEXT("Work")),FName(TEXT("Practice")),FName(TEXT("Socialize"))})if(Score(A)>High){Best=A;High=Score(A);}
 const bool Emergency=S.Fatigue>=90.f || (S.Activity==TEXT("Rest") && S.Fatigue>35.f);
 const bool Valid=Score(S.Activity)>-500.f;
 if(Emergency)Best=TEXT("Rest");
 else if(Cargo && Work)Best=TEXT("Work");
 else if(Valid && (S.Commitment>0 || High<Score(S.Activity)+10.f))Best=S.Activity;
 if(Best!=S.Activity){S.Activity=Best;S.ActivitySeconds=0;S.Commitment=20;}
 S.Reason=Best==TEXT("Rest") ? TEXT("I need to recharge at home.") : Best==TEXT("Practice") ? FString::Printf(TEXT("I want to practise %s."),*S.Interest.ToString()) : Best==TEXT("Socialize") ? TEXT("I could use some company.") : Cargo ? TEXT("I want to finish this delivery.") : Urgency>.5f ? TEXT("The hall is short of supplies.") : TEXT("My workplace needs me.");
 S.ThinkIn=2.f;return Best;
}
bool UGolemNeedsLibrary::RecordPractice(FGolemDriveState& S,FName Domain,float Effort,bool Success)
{
 if(!Success || !FMath::IsFinite(Effort) || Effort<=0)return false;
 FName Skill,Passive;
 if(Domain==TEXT("Guard")){Skill=TEXT("GuardStance");Passive=TEXT("EnduringCore");}
 else if(Domain==TEXT("Magic")){Skill=TEXT("ArcaneBolt");Passive=TEXT("FocusedMind");}
 else if(Domain==TEXT("Aid")){Skill=TEXT("FirstAid");Passive=TEXT("CalmCore");}
 else if(Domain==TEXT("Scout")){Skill=TEXT("EvasiveStep");Passive=TEXT("FleetFooted");}
 else if(Domain==TEXT("Logistics")){Skill=TEXT("CarefulHandling");Passive=TEXT("FleetFooted");}
 else if(Domain==TEXT("Craft")){Skill=TEXT("Repair");Passive=TEXT("PractisedHands");}
 else return false;
 float& Progress=S.Practice.FindOrAdd(Domain);
 Progress=FMath::Min(100000.f,Progress+FMath::Min(Effort,5.f)*(S.Passives.Contains(TEXT("FocusedMind"))?1.1f:1.f));
 bool Learned=false;
 auto Unlock=[&](TArray<FName>& List,FName Id,const TCHAR* Kind){if(List.Contains(Id))return;List.Add(Id);S.LearningLog.Add(FString::Printf(TEXT("Learned %s %s through %s."),Kind,*FName::NameToDisplayString(Id.ToString(),false),*Domain.ToString()));while(S.LearningLog.Num()>4)S.LearningLog.RemoveAt(0);Learned=true;};
 if(Progress>=120.f)Unlock(S.Skills,Skill,TEXT("skill"));if(Progress>=300.f)Unlock(S.Passives,Passive,TEXT("passive"));return Learned;
}
float UGolemNeedsLibrary::WalkingMultiplier(const FGolemDriveState& S){return S.Passives.Contains(TEXT("FleetFooted"))?1.1f:1.f;}
float UGolemNeedsLibrary::WorkMultiplier(const FGolemDriveState& S){return S.Passives.Contains(TEXT("PractisedHands"))?1.1f:1.f;}
float UGolemNeedsLibrary::FatigueMultiplier(const FGolemDriveState& S){return S.Passives.Contains(TEXT("EnduringCore")) || S.Passives.Contains(TEXT("CalmCore")) ? .75f:1.f;}
