using UnrealBuildTool;
public class ElrhunEquipmentEditor : ModuleRules {
 public ElrhunEquipmentEditor(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new[]{"Core","CoreUObject","Engine"});
  PrivateDependencyModuleNames.AddRange(new[]{"UnrealEd","ClothingSystemEditorInterface","ClothingSystemRuntimeCommon","ClothingSystemRuntimeInterface","ChaosCloth"});
 }
}
