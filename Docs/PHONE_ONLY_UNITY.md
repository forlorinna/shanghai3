# 仅用手机浏览器构建《魔都天际线》

核验日期 2026-11-25。推荐先尝试 Unity 官方 Build Automation。它使用 Unity 托管的构建服务，目标是产出 G0 APK，不会为 GitHub Actions 签发 Personal 的 `.ulf`。现有 GameCI 工作流保留。本次未替用户开通订阅或连接账号。

## 手机浏览器配置 Unity Build Automation

1. 登录 [Unity Dashboard](https://cloud.unity.com/)，打开 **Development → Products → DevOps**，选择或创建项目。选择 **Start free trial** 的免费方案，确认页面显示免费额度。若页面只提供付费订阅，停在该页。公开定价列出每月 100 分钟 Linux Micro；用量、机器和账单以组织页面显示为准。 [Unity 开通文档](https://docs.unity.com/en-us/devops/get-started-end-users) · [免费方案](https://docs.unity.com/en-us/devops/pricing/free-plan) · [公开定价](https://unity.com/products/pricing-updates)
2. 在 **Build Automation → Configurations** 创建 Android 目标，从 Unity 界面连接私有 GitHub 仓库 `forlorinna/shanghai3`，分支 `main`，子目录 `UnityProject`。授权前核对 GitHub 范围，只将本项目所需的仓库访问提供给 Unity。任何 GitHub 凭据仅填入 Unity 官方页面，不发聊天。 [构建配置](https://docs.unity.com/en-us/build-automation/basic-build-configuration/overview)
3. Unity 版本选 **Auto detect**，工程锁定 `6000.3.29f1`。如果列表提供 Linux Micro 和 Android SDK 36，选择这两项。服务文档确认支持 6000.3 LTS 系列；当前账号是否已列出固定补丁和 SDK 36 仍须在页面核对。保留 APK，关闭 AAB 和自动触发，先手动构建一次。 [支持版本](https://docs.unity.com/en-us/build-automation/reference/supported-unity-versions)
4. 在 **Advanced settings → Script hooks → Pre-export Method** 填 `Skyline.Editor.UnityBuildAutomationHooks.PreExport`。该方法准备验证场景和 Android 设置。签名由 Unity 托管配置负责。如果页面要求 Android keystore，仅使用独立测试证书并通过 Unity 官方签名配置上传。已有游戏签名和任何私钥都不发聊天。 [预导出入口](https://docs.unity.com/en-us/build-automation/advanced-build-configuration/run-custom-scripts-during-the-build-process) · [Android 签名](https://docs.unity.com/en-us/build-automation/sign-build-artifacts/sign-an-android-application)
5. 点击 **Build**，构建完成后在该次记录下载 APK。实际制品仍需要 APK 完整性、签名、Manifest、ARM64 和 SHA-256 检查，再做断网安装与启动。若手机页面有按钮折叠，使用浏览器的桌面网站视图。

## 私有云桌面与 GameCI

- 已下载并用 Unity 官方签署的软件包索引验证 Hub 4.0.2。当前 Debian 13 云桌面能启动窗口，但窗口黑屏，终端记录 `MESA: Failed to attach to x11 shm`。软件渲染重试依旧黑屏。当前未验证手机能接管该桌面，也未取得许可证。
- 若已有允许个人开发用途的私有临时桌面，且提供手机浏览器可访问的身份验证入口，可由本人进入桌面，使用受支持版 Linux 和官方 Hub，在同一桌面的浏览器完成 Unity OAuth 回调。随后在 Hub 的 **Licenses → Add → Get a free personal license** 查看是否生成 `.ulf`。桌面提供方应允许该用途和包安装。桌面访问全程保持私有。 [Unity Hub Linux 安装](https://docs.unity.com/en-us/hub/install-hub-linux) · [Unity 授权管理](https://docs.unity.com/en-us/hub/manage-license) · [Unity Editor 条款](https://unity.com/legal/editor-terms-of-service/software)
- GitHub Codespaces 有浏览器访问和默认私有的转发端口，属于可实验的项目开发环境。尚未验证该环境的 Hub 图形支持、浏览器回调和许可证可移植性，因此不视作已确认的免费激活服务。 [Codespaces 安全](https://docs.github.com/en/codespaces/reference/security-in-github-codespaces)
- GameCI 当前 Personal 流程要求先由 Hub 生成 `.ulf`，再把它和 Unity 邮箱、密码分别填到 [GitHub Actions Secrets](https://github.com/forlorinna/shanghai3/settings/secrets/actions) 的 `UNITY_LICENSE`、`UNITY_EMAIL`、`UNITY_PASSWORD`。即使 Hub 显示 Personal 已激活，也可能没有生成该文件。提交后按 GameCI 指引退出 Hub，避免席位占用；若没有文件或运行仍拒绝授权，交由 Unity 支持确认，不使用旧版 ALF 手工激活流程。 [GameCI 激活文档](https://game.ci/docs/github/activation/) · [Unity 手工激活范围](https://docs.unity.com/en-us/engine/6000.3/manual/get-started/install-and-upgrade/licenses-and-activation/manual-license-activation/manual-activation-cmd-win)

当前免费官方托管构建有明确配置路线，但尚未有本项目的成功构建记录。当前也没有端到端验证成功的免费纯云端 Personal 授权方案。
