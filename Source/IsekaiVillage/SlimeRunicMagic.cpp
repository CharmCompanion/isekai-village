#include "SlimeRunicMagic.h"
#include "ProceduralMagicCircle.h"
#include "NiagaraComponent.h"
#include "NiagaraFunctionLibrary.h"
#include "Components/CapsuleComponent.h"
#include "Components/SkeletalMeshComponent.h"
#include "GameFramework/CharacterMovementComponent.h"
#include "Kismet/GameplayStatics.h"
#include "Engine/World.h"

URunicAilmentComponent::URunicAilmentComponent()
{
 PrimaryComponentTick.bCanEverTick=true;
 PrimaryComponentTick.bStartWithTickEnabled=false;
}
void URunicAilmentComponent::ApplySpell(URunicSlimeSpell* S, AActor* Source)
{
 if (!S || Source==GetOwner()) return;
 if (S->Effect==ERunicEffect::Push)
 {
  if (ACharacter* C=Cast<ACharacter>(GetOwner()); C && Source)
   C->LaunchCharacter((C->GetActorLocation()-Source->GetActorLocation()).GetSafeNormal2D()*S->Power + FVector(0,0,80),false,false);
  return;
 }
 if (S->Effect==ERunicEffect::Ward || S->Duration<=0) return;
 FAilment& A=Active.FindOrAdd(S->Effect);
 A.Remaining=FMath::Max(A.Remaining,S->Duration); A.Power=FMath::Max(A.Power,S->Power); A.Source=Source;
 SetComponentTickEnabled(true);
 UpdateSlow();
}
void URunicAilmentComponent::UpdateSlow()
{
 ACharacter* C=Cast<ACharacter>(GetOwner()); if (!C) return;
 const bool Slow=Active.Contains(ERunicEffect::Bind)||Active.Contains(ERunicEffect::Chill);
 if (Slow)
 {
  if (!bOwnsSlow) { OriginalSpeed=C->GetCharacterMovement()->MaxWalkSpeed; bOwnsSlow=true; }
  C->GetCharacterMovement()->MaxWalkSpeed=OriginalSpeed*(Active.Contains(ERunicEffect::Bind)?0.15f:0.5f);
 }
 else if (bOwnsSlow) { C->GetCharacterMovement()->MaxWalkSpeed=OriginalSpeed; bOwnsSlow=false; }
}
void URunicAilmentComponent::TickComponent(float D,ELevelTick T,FActorComponentTickFunction* F)
{
 Super::TickComponent(D,T,F);
 // Copy keys: damage may synchronously kill the receiver and clear its ailments.
 TArray<ERunicEffect> Keys; Active.GetKeys(Keys);
 for (ERunicEffect Key:Keys)
 {
  FAilment* A=Active.Find(Key); if (!A) continue;
  const float Step=FMath::Min(D,A->Remaining);
  const float Damage=A->Power*Step; const TWeakObjectPtr<AActor> Source=A->Source;
  A->Remaining-=Step;
  if (A->Remaining<=KINDA_SMALL_NUMBER) Active.Remove(Key);
  if (Key==ERunicEffect::Burn||Key==ERunicEffect::Poison)
   UGameplayStatics::ApplyDamage(GetOwner(),Damage,Source.IsValid()?Source->GetInstigatorController():nullptr,Source.Get(),nullptr);
 }
 UpdateSlow(); if (Active.IsEmpty()) SetComponentTickEnabled(false);
}
void URunicAilmentComponent::EndPlay(const EEndPlayReason::Type R)
{
 Active.Empty(); UpdateSlow(); Super::EndPlay(R);
}

ASlimeRunicMage::ASlimeRunicMage()
{
 PrimaryActorTick.bCanEverTick=true;
 GetCapsuleComponent()->InitCapsuleSize(42,42);
 GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
 GetMesh()->SetRelativeLocation(FVector(0,0,-42));
 GetMesh()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
 Ailments=CreateDefaultSubobject<URunicAilmentComponent>(TEXT("RunicAilments"));
 GetCharacterMovement()->MaxWalkSpeed=180;
 GetCharacterMovement()->bRunPhysicsWithNoController=true;
 Tags.Add(TEXT("RunicSlime"));
}
void ASlimeRunicMage::BeginPlay()
{
 Super::BeginPlay(); Health=MaxHealth; Recovery=FMath::FRandRange(0.4f,2.4f);
 if (IdleAnimation) GetMesh()->PlayAnimation(IdleAnimation,true);
}
bool ASlimeRunicMage::HasSight(AActor* Other) const
{
 if (!IsValid(Other)) return false;
 FHitResult Hit; FCollisionQueryParams Q(SCENE_QUERY_STAT(RunicCastSight),false,this);
 const bool Blocked=GetWorld()->LineTraceSingleByChannel(Hit,GetActorLocation(),Other->GetActorLocation(),ECC_Visibility,Q);
 return !Blocked||Hit.GetActor()==Other;
}
bool ASlimeRunicMage::TryCast(AActor* NewTarget)
{
 if (!HasAuthority()||Health<=0||!Spell||CastingSpell||Recovery>0||TP<Spell->TPCost||!IsValid(NewTarget)||NewTarget==this) return false;
 if (NewTarget->ActorHasTag(TEXT("RunicSlime")) || FVector::Dist(GetActorLocation(),NewTarget->GetActorLocation())>CastRange || !HasSight(NewTarget)) return false;
 CastingSpell=Spell; CastTarget=NewTarget; Charge=0;
 TP=FMath::Clamp(TP-Spell->TPCost,0.f,100.f);
 if (!Circle)
 {
  FActorSpawnParameters P; P.Owner=this;
  Circle=GetWorld()->SpawnActor<AProceduralMagicCircle>(GetActorLocation()-FVector(0,0,38),FRotator::ZeroRotator,P);
  if (Circle) Circle->AttachToActor(this,FAttachmentTransformRules::KeepWorldTransform);
 }
 if (Circle) { Circle->ConfigureRunes(Spell->Element,Spell->RuneTexture,Spell->Color); Circle->SetChargeProgress(0); }
 return true;
}
void ASlimeRunicMage::InterruptCast()
{
 if (CastingSpell) Recovery=FMath::Max(Recovery,0.6f);
 CastingSpell=nullptr; CastTarget.Reset(); Charge=0;
 if (Circle) Circle->DeactivateCircle();
}
void ASlimeRunicMage::Release()
{
 URunicSlimeSpell* S=CastingSpell; AActor* T=CastTarget.Get();
 if (!S||!T||!HasSight(T)||FVector::Dist(GetActorLocation(),T->GetActorLocation())>CastRange) { InterruptCast(); return; }
 if (S->Effect==ERunicEffect::Ward) { Ward=FMath::Max(Ward,S->Power); WardTime=S->Duration; }
 if (S->Effect==ERunicEffect::Bind) Health=FMath::Min(MaxHealth,Health+8.f);
 const FVector Aim=(T->GetActorLocation()-GetActorLocation()).GetSafeNormal();
 FActorSpawnParameters P; P.Owner=this; P.Instigator=this;
 if (ARunicSlimeBolt* B=GetWorld()->SpawnActor<ARunicSlimeBolt>(GetActorLocation()+Aim*65,Aim.Rotation(),P)) B->Initialize(S,this,Aim);
 if (Circle) Circle->ActivateSpellBurst(false);
 if (AttackAnimation) GetMesh()->PlayAnimation(AttackAnimation,false);
 ++CastsReleased; Recovery=FMath::Max(0.2f,S->Cooldown); CastingSpell=nullptr; CastTarget.Reset();
}
void ASlimeRunicMage::Tick(float D)
{
 Super::Tick(D); if (Health<=0||!HasAuthority()) return;
 TP=FMath::Min(100.f,TP+8.f*D);
 WardTime=FMath::Max(0.f,WardTime-D); if (WardTime<=0) Ward=0;
 Recovery=FMath::Max(0.f,Recovery-D);
 if (CastingSpell)
 {
  if (!CastTarget.IsValid()) { InterruptCast(); return; }
  Charge+=D;
  if (Circle) Circle->SetChargeProgress(Charge/FMath::Max(0.2f,CastingSpell->CastTime));
  if (Charge>=CastingSpell->CastTime) Release();
 }
 else
 {
  if (IdleAnimation && !GetMesh()->IsPlaying()) GetMesh()->PlayAnimation(IdleAnimation,true);
  if (bAutoCast)
  {
   if (bTargetPlayer) Target=UGameplayStatics::GetPlayerPawn(this,0);
   TryCast(Target);
  }
 }
}
float ASlimeRunicMage::TakeDamage(float Amount,const FDamageEvent& E,AController* I,AActor* C)
{
 if (Health<=0||Amount<=0||!ShouldTakeDamage(Amount,E,I,C)) return 0;
 const float Absorbed=FMath::Min(Ward,Amount); Ward-=Absorbed;
 const float Applied=Super::TakeDamage(Amount-Absorbed,E,I,C); Health=FMath::Max(0.f,Health-Applied);
 if (Health<=0)
 {
  InterruptCast(); GetCharacterMovement()->DisableMovement(); Ailments->SetComponentTickEnabled(false);
  GetCapsuleComponent()->SetCollisionEnabled(ECollisionEnabled::NoCollision);
  if (DeathAnimation) GetMesh()->PlayAnimation(DeathAnimation,false);
  SetLifeSpan(3.f);
 }
 return Applied;
}
void ASlimeRunicMage::EndPlay(const EEndPlayReason::Type R)
{
 if (Circle) Circle->Destroy(); Super::EndPlay(R);
}

ARunicSlimeBolt::ARunicSlimeBolt()
{
 PrimaryActorTick.bCanEverTick=true;
 FX=CreateDefaultSubobject<UNiagaraComponent>(TEXT("SpellFX")); SetRootComponent(FX); FX->bAutoActivate=false;
 SetLifeSpan(4);
}
void ARunicSlimeBolt::Initialize(URunicSlimeSpell* S,AActor* C,const FVector& D)
{
 Spell=S; SetOwner(C); Velocity=D.GetSafeNormal()*FMath::Max(100.f,S->Speed);
 TArray<AActor*> Friends; UGameplayStatics::GetAllActorsOfClass(this,ASlimeRunicMage::StaticClass(),Friends);
 for (AActor* Friend:Friends) if (Friend->ActorHasTag(TEXT("RunicSlime"))) FriendlyActors.Add(Friend);
 FX->SetAsset(S->BoltFX); FX->SetVariableLinearColor(TEXT("User.Color"),S->Color);
 FX->SetVariableLinearColor(TEXT("User.Color002"),S->Color);
 FX->SetVariableFloat(TEXT("User.SwordLength"),70);
 FX->SetVariableVec3(TEXT("User.EndParticle_Position"),FVector(70,0,0));
 FX->SetWorldScale3D(FVector(0.45f)); FX->Activate(true);
}
void ARunicSlimeBolt::Tick(float D)
{
 Super::Tick(D); if (!Spell||bHit) return;
 const FVector Start=GetActorLocation(),End=Start+Velocity*D;
 FCollisionQueryParams Q(SCENE_QUERY_STAT(RunicBolt),false,this); Q.AddIgnoredActor(GetOwner());
 for (const TWeakObjectPtr<AActor>& Friend:FriendlyActors) if (Friend.IsValid()) Q.AddIgnoredActor(Friend.Get());
 FHitResult H;
 FCollisionObjectQueryParams Objects; Objects.AddObjectTypesToQuery(ECC_Pawn); Objects.AddObjectTypesToQuery(ECC_WorldStatic); Objects.AddObjectTypesToQuery(ECC_WorldDynamic);
 if (!GetWorld()->SweepSingleByObjectType(H,Start,End,FQuat::Identity,Objects,FCollisionShape::MakeSphere(12),Q)) { SetActorLocation(End); return; }
 bHit=true;
 if (AActor* Other=H.GetActor())
 {
  if (Other->ActorHasTag(TEXT("RunicSlime"))) { Destroy(); return; }
  UGameplayStatics::ApplyDamage(Other,Spell->Damage,GetInstigatorController(),GetOwner(),nullptr);
  if (Cast<APawn>(Other))
  {
   URunicAilmentComponent* A=Other->FindComponentByClass<URunicAilmentComponent>();
   if (!A) { A=NewObject<URunicAilmentComponent>(Other); A->RegisterComponent(); }
   A->ApplySpell(Spell,GetOwner());
  }
 }
 if (Spell->ImpactFX)
  if (UNiagaraComponent* N=UNiagaraFunctionLibrary::SpawnSystemAtLocation(this,Spell->ImpactFX,H.ImpactPoint))
  { N->SetVariableLinearColor(TEXT("User.Color"),Spell->Color); N->SetWorldScale3D(FVector(0.55f)); }
 Destroy();
}
