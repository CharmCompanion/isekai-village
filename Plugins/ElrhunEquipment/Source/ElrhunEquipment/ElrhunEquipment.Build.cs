using UnrealBuildTool;
public class ElrhunEquipment : ModuleRules {
 public ElrhunEquipment(ReadOnlyTargetRules Target) : base(Target) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicDependencyModuleNames.AddRange(new[]{"Core","CoreUObject","Engine"});
 }
}
