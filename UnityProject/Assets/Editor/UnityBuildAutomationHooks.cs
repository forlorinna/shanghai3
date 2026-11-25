namespace Skyline.Editor
{
    public static class UnityBuildAutomationHooks
    {
        // Unity's hosted exporter owns the build invocation and any configured signing credentials.
        public static void PreExport()
        {
            BuildPipelineEntry.SetupProject();
        }
    }
}
