using System;
using System.IO;
using System.Linq;
using UnityEditor;
using UnityEditor.Build;
using UnityEditor.Build.Reporting;
using UnityEditor.SceneManagement;
using UnityEngine;
using UnityEngine.Rendering;
using UnityEngine.Rendering.Universal;

namespace Skyline.Editor
{
    public static class BuildPipelineEntry
    {
        private const string Generated = "Assets/Skyline/BenchmarkGenerated";
        private const string Scene = Generated + "/BenchmarkLab.unity";
        private const string Scans = "Assets/Skyline/BenchmarkTextures/concrete_floor_02_";

        public static void BuildAndroid()
        {
            SetupProject();
            PlayerSettings.Android.useCustomKeystore = false;
            var output = Environment.GetEnvironmentVariable("SKYLINE_APK_PATH");
            if (string.IsNullOrEmpty(output))
            {
                var args = Environment.GetCommandLineArgs();
                var pathArgument = Array.IndexOf(args, "-customBuildPath");
                if (pathArgument >= 0)
                    output = args.Skip(pathArgument + 1).FirstOrDefault();
            }
            if (string.IsNullOrEmpty(output) ||
                !Path.GetExtension(output).Equals(".apk", StringComparison.OrdinalIgnoreCase))
                throw new BuildFailedException("Provide an APK path with SKYLINE_APK_PATH or -customBuildPath.");

            var report = BuildPipeline.BuildPlayer(new BuildPlayerOptions
            {
                target = BuildTarget.Android,
                scenes = new[] { Scene },
                locationPathName = output,
                options = BuildOptions.None
            });
            if (report.summary.result != BuildResult.Succeeded || !File.Exists(output))
                throw new BuildFailedException($"Android build result is {report.summary.result}.");
        }

        public static void SetupProject()
        {
            if (!AssetDatabase.IsValidFolder(Generated))
                AssetDatabase.CreateFolder("Assets/Skyline", "BenchmarkGenerated");

            var renderer = GetOrCreate<UniversalRendererData>("BenchmarkRenderer");
            const string pipelinePath = Generated + "/BenchmarkURP.asset";
            var pipeline = AssetDatabase.LoadAssetAtPath<UniversalRenderPipelineAsset>(pipelinePath);
            if (pipeline == null)
            {
                pipeline = UniversalRenderPipelineAsset.Create(renderer);
                AssetDatabase.CreateAsset(pipeline, pipelinePath);
            }
            GraphicsSettings.defaultRenderPipeline = pipeline;
            QualitySettings.renderPipeline = pipeline;

            PlayerSettings.productName = "魔都天际线";
            PlayerSettings.bundleVersion = "1.0.0";
            PlayerSettings.Android.bundleVersionCode = 1;
            PlayerSettings.SetApplicationIdentifier(NamedBuildTarget.Android, "org.shanghaiskyline.g0");
            PlayerSettings.defaultInterfaceOrientation = UIOrientation.LandscapeLeft;
            PlayerSettings.colorSpace = ColorSpace.Linear;
            PlayerSettings.SetScriptingBackend(NamedBuildTarget.Android, ScriptingImplementation.IL2CPP);
            PlayerSettings.Android.targetArchitectures = AndroidArchitecture.ARM64;
            PlayerSettings.Android.minSdkVersion = AndroidSdkVersions.AndroidApiLevel26;
            PlayerSettings.Android.targetSdkVersion = (AndroidSdkVersions)36;
            PlayerSettings.SetUseDefaultGraphicsAPIs(BuildTarget.Android, false);
            PlayerSettings.SetGraphicsAPIs(BuildTarget.Android, new[] { GraphicsDeviceType.Vulkan });
            EditorUserBuildSettings.buildAppBundle = false;

            GenerateScene();
            EditorBuildSettings.scenes = new[] { new EditorBuildSettingsScene(Scene, true) };
            AssetDatabase.SaveAssets();
        }

        private static void GenerateScene()
        {
            var albedo = ReadScan("diff", true);
            var normal = ReadScan("nor_gl", false, normalMap: true);
            var ao = ReadScan("ao", false);
            var roughness = ReadScan("rough", false, readable: true);
            var smoothness = GetOrCreateMask(roughness);

            var shader = Shader.Find("Universal Render Pipeline/Lit");
            if (shader == null)
                throw new BuildFailedException("URP Lit shader missing.");
            var path = Generated + "/ScannedConcrete.mat";
            var material = AssetDatabase.LoadAssetAtPath<Material>(path);
            if (material == null)
            {
                material = new Material(shader);
                AssetDatabase.CreateAsset(material, path);
            }
            material.SetTexture("_BaseMap", albedo);
            material.SetTexture("_BumpMap", normal);
            material.SetTexture("_OcclusionMap", ao);
            material.SetTexture("_MetallicGlossMap", smoothness);
            material.SetFloat("_Smoothness", 1);
            material.EnableKeyword("_NORMALMAP");
            material.EnableKeyword("_OCCLUSIONMAP");
            material.EnableKeyword("_METALLICSPECGLOSSMAP");
            EditorUtility.SetDirty(material);

            var scene = EditorSceneManager.NewScene(NewSceneSetup.EmptyScene, NewSceneMode.Single);
            var sphere = GameObject.CreatePrimitive(PrimitiveType.Sphere);
            sphere.name = "CC0 scanned concrete reference";
            sphere.transform.position = Vector3.up;
            sphere.transform.localScale = Vector3.one * 1.5f;
            sphere.GetComponent<Renderer>().sharedMaterial = material;

            var lamp = new GameObject("Benchmark main light").AddComponent<Light>();
            lamp.type = LightType.Directional;
            lamp.intensity = 1.2f;
            lamp.transform.rotation = Quaternion.Euler(42, -32, 0);
            RenderSettings.ambientMode = AmbientMode.Flat;
            RenderSettings.ambientLight = new Color(0.38f, 0.38f, 0.38f);

            var camera = new GameObject("Benchmark camera").AddComponent<Camera>();
            camera.clearFlags = CameraClearFlags.SolidColor;
            camera.backgroundColor = new Color(0.17f, 0.17f, 0.17f);
            camera.gameObject.AddComponent<BenchmarkOrbit>();
            if (!EditorSceneManager.SaveScene(scene, Scene))
                throw new BuildFailedException("Cannot save benchmark scene.");
        }

        private static Texture2D ReadScan(string channel, bool srgb, bool normalMap = false,
            bool readable = false)
        {
            var path = Scans + channel + "_1k.jpg";
            if (!(AssetImporter.GetAtPath(path) is TextureImporter importer))
                throw new BuildFailedException("Missing PBR texture: " + path);
            importer.textureType = normalMap ? TextureImporterType.NormalMap : TextureImporterType.Default;
            importer.sRGBTexture = srgb;
            importer.isReadable = readable;
            if (readable)
                importer.textureCompression = TextureImporterCompression.Uncompressed;
            importer.SaveAndReimport();
            return AssetDatabase.LoadAssetAtPath<Texture2D>(path);
        }

        private static Texture2D GetOrCreateMask(Texture2D roughness)
        {
            var path = Generated + "/ConcreteMetallicSmoothness.asset";
            var mask = AssetDatabase.LoadAssetAtPath<Texture2D>(path);
            if (mask == null)
            {
                mask = new Texture2D(roughness.width, roughness.height, TextureFormat.RGBA32,
                    mipChain: true, linear: true);
                AssetDatabase.CreateAsset(mask, path);
            }
            var values = roughness.GetPixels32();
            for (var i = 0; i < values.Length; i++)
                values[i] = new Color32(0, 0, 0, (byte)(255 - values[i].r));
            mask.SetPixels32(values);
            mask.Apply();
            EditorUtility.SetDirty(mask);
            return mask;
        }

        private static T GetOrCreate<T>(string name) where T : ScriptableObject
        {
            var path = Generated + "/" + name + ".asset";
            var asset = AssetDatabase.LoadAssetAtPath<T>(path);
            if (asset == null)
            {
                asset = ScriptableObject.CreateInstance<T>();
                AssetDatabase.CreateAsset(asset, path);
            }
            return asset;
        }
    }
}
