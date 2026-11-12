// Copyright Epic Games, Inc. All Rights Reserved.
// SkitManagerComponent.h — Manages Skit Queueing, Corner Prompts, and Manga Panel Playback

#pragma once

#include "CoreMinimal.h"
#include "Components/ActorComponent.h"
#include "SkitSystemTypes.h"
#include "SkitManagerComponent.generated.h"

DECLARE_DYNAMIC_MULTICAST_DELEGATE_TwoParams(FOnSkitPromptAvailable, FText, SkitTitle, float, Duration);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnSkitPromptExpired);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_OneParam(FOnSkitStarted, USkitDataAsset*, ActiveSkit);
DECLARE_DYNAMIC_MULTICAST_DELEGATE_ThreeParams(FOnSkitLineUpdated, const FSkitDialogueLine&, Line, int32, LineIndex, int32, TotalLines);
DECLARE_DYNAMIC_MULTICAST_DELEGATE(FOnSkitFinished);

UCLASS(ClassGroup = (TalesTemplate), meta = (BlueprintSpawnableComponent))
class ISEKAIVILLAGE_API USkitManagerComponent : public UActorComponent
{
	GENERATED_BODY()

public:
	USkitManagerComponent();

	virtual void TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction) override;

	// ── State ──
	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	TArray<TObjectPtr<USkitDataAsset>> QueuedSkits;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	TObjectPtr<USkitDataAsset> PromptSkit = nullptr;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	float PromptTimer = 0.0f;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	TObjectPtr<USkitDataAsset> ActiveSkit = nullptr;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	int32 CurrentLineIndex = 0;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	bool bIsSkitPlaying = false;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	bool bAutoAdvance = true;

	UPROPERTY(VisibleAnywhere, BlueprintReadOnly, Category = "Skit")
	float LineAutoTimer = 0.0f;

	// ── Delegates ──
	UPROPERTY(BlueprintAssignable, Category = "Skit|Events")
	FOnSkitPromptAvailable OnSkitPromptAvailable;

	UPROPERTY(BlueprintAssignable, Category = "Skit|Events")
	FOnSkitPromptExpired OnSkitPromptExpired;

	UPROPERTY(BlueprintAssignable, Category = "Skit|Events")
	FOnSkitStarted OnSkitStarted;

	UPROPERTY(BlueprintAssignable, Category = "Skit|Events")
	FOnSkitLineUpdated OnSkitLineUpdated;

	UPROPERTY(BlueprintAssignable, Category = "Skit|Events")
	FOnSkitFinished OnSkitFinished;

	// ── Core Operations ──
	UFUNCTION(BlueprintCallable, Category = "Skit")
	void QueueSkit(USkitDataAsset* InSkit);

	UFUNCTION(BlueprintCallable, Category = "Skit")
	bool PlayPromptedSkit();

	UFUNCTION(BlueprintCallable, Category = "Skit")
	void NextLine();

	UFUNCTION(BlueprintCallable, Category = "Skit")
	void SkipSkit();
};
