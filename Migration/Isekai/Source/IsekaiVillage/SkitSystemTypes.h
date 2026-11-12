// Copyright Epic Games, Inc. All Rights Reserved.
// SkitSystemTypes.h — Tales of Manga Comic-Panel Skit Data Structures

#pragma once

#include "CoreMinimal.h"
#include "Engine/DataAsset.h"
#include "SkitSystemTypes.generated.h"

class UTexture2D;
class USoundBase;

UENUM(BlueprintType)
enum class ESkitPanelPosition : uint8
{
	Left       UMETA(DisplayName = "Left Panel"),
	Center     UMETA(DisplayName = "Center Panel"),
	Right      UMETA(DisplayName = "Right Panel"),
	TopLeft    UMETA(DisplayName = "Top Left Pop-In"),
	TopRight   UMETA(DisplayName = "Top Right Pop-In")
};

UENUM(BlueprintType)
enum class ESkitEmotion : uint8
{
	Neutral    UMETA(DisplayName = "Neutral / Default"),
	Happy      UMETA(DisplayName = "Happy / Smiling"),
	Angry      UMETA(DisplayName = "Angry / Furious"),
	Shocked    UMETA(DisplayName = "Shocked / Exclamation"),
	Sweatdrop  UMETA(DisplayName = "Embarrassed / Sweatdrop"),
	Sad        UMETA(DisplayName = "Sad / Dejected")
};

USTRUCT(BlueprintType)
struct ISEKAIVILLAGE_API FSkitDialogueLine
{
	GENERATED_BODY()

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	FText SpeakerName;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit", meta = (MultiLine = true))
	FText DialogueText;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	TObjectPtr<UTexture2D> PortraitTexture = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	ESkitEmotion Emotion = ESkitEmotion::Neutral;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	ESkitPanelPosition PanelPosition = ESkitPanelPosition::Left;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	TObjectPtr<USoundBase> VoiceClip = nullptr;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	float AutoAdvanceDelay = 3.5f;
};

/**
 * Data Asset representing a complete multi-line anime comic-panel Skit.
 */
UCLASS(BlueprintType, ClassGroup = (TalesTemplate))
class ISEKAIVILLAGE_API USkitDataAsset : public UPrimaryDataAsset
{
	GENERATED_BODY()

public:
	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	FName SkitID;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	FText SkitTitle;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	TArray<FSkitDialogueLine> DialogueLines;

	UPROPERTY(EditAnywhere, BlueprintReadWrite, Category = "Skit")
	float PromptDuration = 15.0f; // How long notification stays in corner
};
