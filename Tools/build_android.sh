#!/usr/bin/env bash
set -euo pipefail
root="$(cd -- "$(dirname -- "${BASH_SOURCE[0]}")/.." && pwd)"
mkdir -p "$root/Builds"

editor="${UNITY:-}"
if [[ -z "$editor" ]]; then
    editor="$(command -v Unity || command -v unity || true)"
fi
if [[ ! -x "$editor" ]]; then
    echo "G0 blocked: Unity 6000.3.29f1 Linux Editor executable not found. Set UNITY to an installed, activated Editor." >&2
    exit 69
fi
android="$(dirname -- "$editor")/Data/PlaybackEngines/AndroidPlayer"
if [[ ! -d "$android" ]]; then
    echo "G0 blocked: Android Build Support is missing next to $editor." >&2
    exit 69
fi
sdk="${ANDROID_SDK_ROOT:-$android/SDK}"
build_tools="$sdk/build-tools/36.0.0"
for tool in apksigner aapt zipalign; do
    if [[ ! -x "$build_tools/$tool" ]]; then
        echo "G0 blocked: $build_tools/$tool is missing." >&2
        exit 69
    fi
done

output="$(mktemp -d "$root/Builds/g0.XXXXXX")"
export SKYLINE_APK_PATH="$output/Shanghai-Skyline-Unity-G0-arm64-debug-signed.apk"
if [[ -d "$android/OpenJDK" ]]; then
    export JAVA_HOME="$android/OpenJDK"
fi
"$editor" -batchmode -nographics -quit -projectPath "$root/UnityProject" \
    -buildTarget Android -executeMethod Skyline.Editor.BuildPipelineEntry.BuildAndroid \
    -logFile "$output/unity.log"
"$root/Tools/verify_android_apk.sh" "$SKYLINE_APK_PATH" "$build_tools" "$output/verification"
printf '%s\n' "$SKYLINE_APK_PATH"
