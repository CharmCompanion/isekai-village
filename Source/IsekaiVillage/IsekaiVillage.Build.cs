// Copyright Epic Games, Inc. All Rights Reserved.

using UnrealBuildTool;

public class IsekaiVillage : ModuleRules
{
	public IsekaiVillage(ReadOnlyTargetRules Target) : base(Target)
	{
		PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;

		PublicDependencyModuleNames.AddRange(new string[] {
			"Core",
			"CoreUObject",
			"Engine",
			"InputCore",
			"EnhancedInput",
			"Niagara",
			"ProceduralMeshComponent",
			"UMG",
			"Slate",
			"SlateCore",
			"Landscape",
			"PhysicsCore"
		});

		PrivateDependencyModuleNames.AddRange(new string[] { });
		if (Target.bBuildEditor)
		{
			PrivateDependencyModuleNames.AddRange(new string[] { "Foliage", "RenderCore", "RHI" });
		}
	}
}


