#pragma once

#include "CoreMinimal.h"
#include "GameFramework/Character.h"
#include "Components/ActorComponent.h"
#include "Engine/DataAsset.h"
#include "IsekaiVillageTypes.h"
#include "SlimeRunicMagic.generated.h"

UENUM(BlueprintType)
enum class ERunicEffect : uint8 { Bind, Push, Burn, Chill, Poison, Ward };

/** Affinities specialize the four GDD elements; they do not add player elements. */
UCLASS(BlueprintType)
class ISEKAIVILLAGE_API URunicSlimeSpell : public UDataAsset
{
 GENERATED_BODY()
public:
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FString SpellName;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FString EffectWord;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FString Incantation;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) EElement Element = EElement::Earth;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) ERunicEffect Effect = ERunicEffect::Bind;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) FLinearColor Color = FLinearColor::Green;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<UTexture2D> RuneTexture;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<class UNiagaraSystem> BoltFX;
 UPROPERTY(EditAnywhere, BlueprintReadOnly) TObjectPtr<class UNiagaraSystem> ImpactFX;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0")) float Damage = 12;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0.2")) float CastTime = 1.2f;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0.2")) float Cooldown = 4;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0", ClampMax="100")) float TPCost = 12;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="100")) float Speed = 850;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0")) float Duration = 3;
 UPROPERTY(EditAnywhere, BlueprintReadOnly, meta=(ClampMin="0")) float Power = 3;
 UFUNCTION(BlueprintPure) FString GetSentence() const { return EffectWord + TEXT(" - Enemy - ") + SpellName; }
};

/** Refreshing, non-stacking ailments. Uses the receiver's existing TakeDamage/health. */
UCLASS(ClassGroup=(Magic), meta=(BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API URunicAilmentComponent : public UActorComponent
{
 GENERATED_BODY()
public:
 URunicAilmentComponent();
 UFUNCTION(BlueprintCallable) void ApplySpell(URunicSlimeSpell* Spell, AActor* Source);
 virtual void TickComponent(float Delta, ELevelTick TickType, FActorComponentTickFunction* Function) override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
 struct FAilment { float Remaining=0; float Power=0; TWeakObjectPtr<AActor> Source; };
 TMap<ERunicEffect, FAilment> Active;
 float OriginalSpeed=0;
 bool bOwnsSlow=false;
 void UpdateSlow();
};

UCLASS(Blueprintable)
class ISEKAIVILLAGE_API ASlimeRunicMage : public ACharacter
{
 GENERATED_BODY()
public:
 ASlimeRunicMage();
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") TObjectPtr<URunicSlimeSpell> Spell;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") TObjectPtr<AActor> Target;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") bool bAutoCast = true;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") bool bTargetPlayer = true;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") float CastRange = 1400;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") float MaxHealth = 100;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Slime Magic") float Health = 100;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Slime Magic") float TP = 100;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Slime Magic") float Ward = 0;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category="Slime Magic") int32 CastsReleased = 0;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") TObjectPtr<class UAnimSequence> IdleAnimation;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") TObjectPtr<class UAnimSequence> AttackAnimation;
 UPROPERTY(EditAnywhere, BlueprintReadWrite, Category="Slime Magic") TObjectPtr<class UAnimSequence> DeathAnimation;
 UPROPERTY(VisibleAnywhere, BlueprintReadOnly) TObjectPtr<URunicAilmentComponent> Ailments;
 UFUNCTION(BlueprintCallable) bool TryCast(AActor* NewTarget);
 UFUNCTION(BlueprintCallable) void InterruptCast();
 virtual void Tick(float Delta) override;
 virtual float TakeDamage(float Amount, const FDamageEvent& Event, AController* InstigatorController, AActor* Causer) override;
protected:
 virtual void BeginPlay() override;
 virtual void EndPlay(const EEndPlayReason::Type Reason) override;
private:
 UPROPERTY(Transient) TObjectPtr<class AProceduralMagicCircle> Circle;
 UPROPERTY(Transient) TObjectPtr<URunicSlimeSpell> CastingSpell;
 TWeakObjectPtr<AActor> CastTarget;
 float Charge=0, Recovery=0, WardTime=0;
 bool HasSight(AActor* Other) const;
 void Release();
};

/** Swept, single-hit projectile. Shared slime faction is excluded, including splash. */
UCLASS()
class ISEKAIVILLAGE_API ARunicSlimeBolt : public AActor
{
 GENERATED_BODY()
public:
 ARunicSlimeBolt();
 void Initialize(URunicSlimeSpell* Definition, AActor* Caster, const FVector& Direction);
 virtual void Tick(float Delta) override;
private:
 UPROPERTY() TObjectPtr<URunicSlimeSpell> Spell;
 UPROPERTY() TObjectPtr<class UNiagaraComponent> FX;
 FVector Velocity;
 TArray<TWeakObjectPtr<AActor>> FriendlyActors;
 bool bHit=false;
};
