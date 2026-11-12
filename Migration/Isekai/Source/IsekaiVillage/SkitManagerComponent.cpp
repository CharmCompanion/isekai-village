// Copyright Epic Games, Inc. All Rights Reserved.
// SkitManagerComponent.cpp — Manages Skit Queueing, Corner Prompts, and Manga Panel Playback

#include "SkitManagerComponent.h"

USkitManagerComponent::USkitManagerComponent()
{
	PrimaryComponentTick.bCanEverTick = true;
}

void USkitManagerComponent::TickComponent(float DeltaTime, ELevelTick TickType, FActorComponentTickFunction* ThisTickFunction)
{
	Super::TickComponent(DeltaTime, TickType, ThisTickFunction);

	// 1. Manage Corner Prompt Expiration
	if (PromptSkit && !bIsSkitPlaying)
	{
		PromptTimer -= DeltaTime;
		if (PromptTimer <= 0.0f)
		{
			PromptSkit = nullptr;
			OnSkitPromptExpired.Broadcast();

			// If there are queued skits, show the next one!
			if (QueuedSkits.Num() > 0)
			{
				USkitDataAsset* NextSkit = QueuedSkits[0];
				QueuedSkits.RemoveAt(0);
				QueueSkit(NextSkit);
			}
		}
	}

	// 2. Manage Active Skit Auto-Advancement
	if (bIsSkitPlaying && bAutoAdvance && ActiveSkit)
	{
		LineAutoTimer -= DeltaTime;
		if (LineAutoTimer <= 0.0f)
		{
			NextLine();
		}
	}
}

void USkitManagerComponent::QueueSkit(USkitDataAsset* InSkit)
{
	if (!InSkit) return;

	if (!PromptSkit && !bIsSkitPlaying)
	{
		PromptSkit = InSkit;
		PromptTimer = InSkit->PromptDuration;
		OnSkitPromptAvailable.Broadcast(InSkit->SkitTitle, PromptTimer);
	}
	else
	{
		if (!QueuedSkits.Contains(InSkit))
		{
			QueuedSkits.Add(InSkit);
		}
	}
}

bool USkitManagerComponent::PlayPromptedSkit()
{
	if (!PromptSkit) return false;

	ActiveSkit = PromptSkit;
	PromptSkit = nullptr;
	bIsSkitPlaying = true;
	CurrentLineIndex = 0;

	OnSkitStarted.Broadcast(ActiveSkit);

	if (ActiveSkit->DialogueLines.Num() > 0)
	{
		const FSkitDialogueLine& FirstLine = ActiveSkit->DialogueLines[0];
		LineAutoTimer = FirstLine.AutoAdvanceDelay > 0.5f ? FirstLine.AutoAdvanceDelay : 3.5f;
		OnSkitLineUpdated.Broadcast(FirstLine, 0, ActiveSkit->DialogueLines.Num());
	}
	else
	{
		SkipSkit();
	}

	return true;
}

void USkitManagerComponent::NextLine()
{
	if (!bIsSkitPlaying || !ActiveSkit) return;

	CurrentLineIndex++;

	if (CurrentLineIndex < ActiveSkit->DialogueLines.Num())
	{
		const FSkitDialogueLine& Line = ActiveSkit->DialogueLines[CurrentLineIndex];
		LineAutoTimer = Line.AutoAdvanceDelay > 0.5f ? Line.AutoAdvanceDelay : 3.5f;
		OnSkitLineUpdated.Broadcast(Line, CurrentLineIndex, ActiveSkit->DialogueLines.Num());
	}
	else
	{
		// Finished all dialogue lines!
		SkipSkit();
	}
}

void USkitManagerComponent::SkipSkit()
{
	bIsSkitPlaying = false;
	ActiveSkit = nullptr;
	CurrentLineIndex = 0;
	LineAutoTimer = 0.0f;

	OnSkitFinished.Broadcast();

	// Check if more skits are queued
	if (QueuedSkits.Num() > 0)
	{
		USkitDataAsset* NextSkit = QueuedSkits[0];
		QueuedSkits.RemoveAt(0);
		QueueSkit(NextSkit);
	}
}
