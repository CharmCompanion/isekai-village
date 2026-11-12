#if WITH_DEV_AUTOMATION_TESTS
#include "Misc/AutomationTest.h"
#include "SlimeRunicMagic.h"
#include "Engine/World.h"
#include "Engine/Engine.h"
#include "Engine/GameInstance.h"
#include "Engine/DamageEvents.h"
#include "Components/CapsuleComponent.h"
#include "GameFramework/CharacterMovementComponent.h"

IMPLEMENT_SIMPLE_AUTOMATION_TEST(FSlimeRunicRulesTest,"IsekaiVillage.Magic.SlimeRunicRules",EAutomationTestFlags::EditorContext|EAutomationTestFlags::EngineFilter)
bool FSlimeRunicRulesTest::RunTest(const FString& Parameters)
{
 const UWorld::InitializationValues IV=UWorld::InitializationValues().AllowAudioPlayback(false).CreatePhysicsScene(true).CreateNavigation(false).CreateAISystem(false).ShouldSimulatePhysics(false).SetTransactional(false);
 UWorld* W=UWorld::CreateWorld(EWorldType::Game,false,NAME_None,nullptr,true,ERHIFeatureLevel::Num,&IV);
 GEngine->CreateNewWorldContext(EWorldType::Game).SetCurrentWorld(W);
 W->SetGameInstance(NewObject<UGameInstance>(GEngine));
 FURL URL; URL.AddOption(TEXT("game=/Script/Engine.GameModeBase"));
 TestTrue(TEXT("Damage fixture has an authority game mode"),W->SetGameMode(URL));
 FActorSpawnParameters P; P.SpawnCollisionHandlingOverride=ESpawnActorCollisionHandlingMethod::AlwaysSpawn;
 ASlimeRunicMage* C=W->SpawnActor<ASlimeRunicMage>(FVector(0,0,100),FRotator::ZeroRotator,P);
 ASlimeRunicMage* T=W->SpawnActor<ASlimeRunicMage>(FVector(500,0,100),FRotator::ZeroRotator,P);
 T->Tags.Empty(); C->bAutoCast=false; T->bAutoCast=false;
 URunicSlimeSpell* S=NewObject<URunicSlimeSpell>(W);S->SpellName=TEXT("Cinder Bloom");S->EffectWord=TEXT("Ignite");S->Effect=ERunicEffect::Burn;S->Power=3;S->Duration=3;
 TestEqual(TEXT("Semantic grammar"),S->GetSentence(),FString(TEXT("Ignite - Enemy - Cinder Bloom")));
 C->Spell=S; C->TP=0; TestFalse(TEXT("No TP prevents cast"),C->TryCast(T));
 C->TP=100; TestFalse(TEXT("Self target rejected"),C->TryCast(C));
 T->Tags.Add(TEXT("RunicSlime"));TestFalse(TEXT("Friendly target rejected"),C->TryCast(T));T->Tags.Empty();
 TestTrue(TEXT("Valid target begins charge"),C->TryCast(T));TestEqual(TEXT("Cost paid once"),C->TP,88.f);
 TestFalse(TEXT("No overlapping casts"),C->TryCast(T));C->InterruptCast();TestEqual(TEXT("Interrupted cast releases no spell"),C->CastsReleased,0);
 T->Ailments->ApplySpell(S,C);T->Ailments->ApplySpell(S,C);
 T->Ailments->TickComponent(5,LEVELTICK_All,nullptr);
 TestEqual(TEXT("Burn refreshes, does not stack, clamps long frame at expiry"),T->Health,91.f);
 S->Effect=ERunicEffect::Poison;S->Power=4;S->Duration=5;T->Ailments->ApplySpell(S,C);T->Ailments->TickComponent(5,LEVELTICK_All,nullptr);
 TestEqual(TEXT("Poison total"),T->Health,71.f);
 const float Speed=T->GetCharacterMovement()->MaxWalkSpeed;
 S->Effect=ERunicEffect::Chill;S->Duration=3;T->Ailments->ApplySpell(S,C);TestEqual(TEXT("Chill halves speed"),T->GetCharacterMovement()->MaxWalkSpeed,Speed*.5f);
 S->Effect=ERunicEffect::Bind;S->Duration=1;T->Ailments->ApplySpell(S,C);TestEqual(TEXT("Bind takes priority"),T->GetCharacterMovement()->MaxWalkSpeed,Speed*.15f);
 T->Ailments->TickComponent(1.1f,LEVELTICK_All,nullptr);TestEqual(TEXT("Expired bind retains chill"),T->GetCharacterMovement()->MaxWalkSpeed,Speed*.5f);
 T->Ailments->TickComponent(3,LEVELTICK_All,nullptr);TestEqual(TEXT("Speed restored after ailments"),T->GetCharacterMovement()->MaxWalkSpeed,Speed);
 T->Health=100;T->Ward=25;FDamageEvent D;
 T->SetCanBeDamaged(false); T->TakeDamage(10,D,nullptr,C);
 TestEqual(TEXT("Immune target keeps ward"),T->Ward,25.f);
 TestEqual(TEXT("Immune target keeps health"),T->Health,100.f); T->SetCanBeDamaged(true);
 T->TakeDamage(10,D,nullptr,C);TestEqual(TEXT("Ward absorbs damage"),T->Health,100.f);TestEqual(TEXT("Ward depletes"),T->Ward,15.f);
 T->TakeDamage(30,D,nullptr,C);TestEqual(TEXT("Ward overflow reaches health"),T->Health,85.f);
 T->GetCapsuleComponent()->SetCollisionResponseToChannel(ECC_Visibility,ECR_Block);
 S->Effect=ERunicEffect::Ward;S->Damage=18;S->Speed=1000;
 ARunicSlimeBolt* Bolt=W->SpawnActor<ARunicSlimeBolt>(FVector(100,0,100),FRotator::ZeroRotator,P);
 // Receiver shares the native class, but is intentionally outside the slime faction.
 Bolt->Initialize(S,C,FVector::ForwardVector);Bolt->Tick(.6f);
 TestEqual(TEXT("Swept bolt hits once even across a long frame"),T->Health,67.f);
 S->Effect=ERunicEffect::Poison;S->Power=4;S->Duration=1;T->Ailments->ApplySpell(S,C);C->Destroy();T->Ailments->TickComponent(1,LEVELTICK_All,nullptr);
 TestEqual(TEXT("Poison persists when caster is removed"),T->Health,63.f);
 W->DestroyWorld(false); GEngine->DestroyWorldContext(W);
 return true;
}
#endif
