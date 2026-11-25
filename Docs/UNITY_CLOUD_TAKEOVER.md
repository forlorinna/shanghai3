# Unity Cloud Android 接管记录

2026-11-25 核查公开仓库 `forlorinna/shanghai3` 的 `main`。初始 HEAD 为 `4058036217b98a1a00264f8feb73fb83c2d8d6ad`。本轮附件与先前已读的 MASTER 哈希一致。

## 源码与目标

| 项目 | 仓库实查 |
| --- | --- |
| Unity | `6000.3.29f1 (96d2fe17529c)` |
| 渲染与依赖 | URP `17.3.0`，IMGUI `1.0.0`，Linear，Vulkan |
| Android | IL2CPP、ARM64、最低 API 26、目标 API 36、APK |
| 应用标识 | `org.shanghaiskyline.g0`，显示名《魔都天际线》，源码版本 `1.0.0`，版本码 `1` |
| 构建入口 | `Assets/Editor` 中公开静态 `Skyline.Editor.UnityBuildAutomationHooks.PreExport` 调用 `SetupProject`，生成并登记 `BenchmarkLab.unity`。Unity 官方服务负责构建及签名。 |
| Unity 工程状态 | 只有 G0 验证工程。场景、渲染资产及部分 ProjectSettings 首次执行时生成。尚未产生 Unity 的 `packages-lock.json` 或 C# 编译结果。 |
| 资源 | 清单 6 条的本地尺寸和 SHA-256 通过。Unity 12 个资产与文件夹的 GUID 唯一。参考照、Blender 源文件和 GLB 哈希通过。 |
| 公开仓库凭据 | Gitleaks 8.28.0 扫描起始 5 个可达提交及 Unity 工作树，未报告凭据命中。公开 refs 仅 `main`。扫描范围不包含 GitHub 或 Unity 的秘密存储。 |

目标的 Windows 11 24H2、Windows Micro、Free tier 及自动构建关闭状态由项目所有者报告。账户侧设置和实际剩余免费分钟数待授权读取。目标级 SDK 需提供 API 36，源码中的 targetSdk 不会安装 SDK。Unity 编译、场景导出、签名、安装和离线运行需真实构建验证。

## Unity Build Automation REST API

[官方 v2 参考](https://docs.unity.com/en-us/oas-build-automation-client/2.0.0)使用 Unity 服务账号 Key ID 与 Secret 的 HTTP Basic 认证。[v3](https://docs.unity.com/en-us/oas-build-automation-client/3.0.0)覆盖项目及源码连接，构建和产物仍使用 v2。服务账号权限应限定在 Shanghai Skyline 项目所需范围，经安全凭据存储提供，不进入公开源码或日志。构建前先核实 Free tier、免费分钟数、目标、机器及是否已有运行。

| 操作 | 端点 |
| --- | --- |
| 检查 Free tier | `GET /v2/orgs/{orgid}/free-tier-status` |
| 获取项目构建配置 | `GET /v2/orgs/{orgid}/projects/{projectid}/buildtargets` |
| 查询项目版本可用的 Android SDK | `GET /v2/orgs/{orgid}/projects/{projectid}/android_sdk_config/{unityVersionValue}` |
| 查已有运行／新建一次 | `GET`／`POST .../buildtargets/{buildtargetid}/builds` |
| 轮询状态／取日志／列出产物 | `GET .../builds/{number}`、`GET .../builds/{number}/log`、`GET .../builds/{number}/artifacts` |

本轮未取得 Unity 会话或服务账号授权，未调用创建构建的 API。现有 GitHub Actions 保留。收到 APK 后使用 `Tools/verify_android_apk.sh` 和 `Tools/verify_android_elf.py` 验证签名、Manifest、原生架构、ELF 与 APK 16 KiB 对齐和 SHA-256。APK 校验与 Android 16 真机运行分别记录。
