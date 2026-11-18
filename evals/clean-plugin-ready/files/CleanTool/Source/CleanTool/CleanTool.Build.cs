// Copyright 2026 Example Studio. All rights reserved.
using System.IO;
using UnrealBuildTool;
public class CleanTool : ModuleRules {
 public CleanTool(ReadOnlyTargetRules T) : base(T) {
  PCHUsage = PCHUsageMode.UseExplicitOrSharedPCHs;
  PublicIncludePaths.Add(Path.Combine(ModuleDirectory, "Public"));
  PublicDependencyModuleNames.Add("Core");
 }
}
