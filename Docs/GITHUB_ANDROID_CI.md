# 魔都天际线 · G0 GitHub Android 构建

仓库为 [forlorinna/shanghai3](https://github.com/forlorinna/shanghai3)。Codex Cloud 维护 Unity 源码、Blender 源模型及授权资产。GitHub 保存这些文件，GitHub Actions 使用 GameCI 在 GitHub 的标准 `ubuntu-24.04` Runner 上生成验证 APK。工作流仅接受手动触发，未配置 larger runner 或付费构建服务。

## Unity 激活与仓库 Secrets

有资格使用 Unity Personal 的账户由本人通过 Unity Hub 登录激活，再按 [GameCI Personal 激活文档](https://game.ci/docs/github/activation/)获取对应的 `.ulf`。按 GameCI 指引处理现有 Hub 席位。仅在 [仓库 → Settings → Secrets and variables → Actions → New repository secret](https://github.com/forlorinna/shanghai3/settings/secrets/actions) 设置：

| 名称 | 值 |
| --- | --- |
| `UNITY_LICENSE` | 本人合法激活的 Unity Personal `.ulf` 文件内容 |
| `UNITY_EMAIL` | 对应 Unity 账号邮箱 |
| `UNITY_PASSWORD` | 对应 Unity 账号密码 |

凭据仅留在 GitHub Secrets，不放入聊天、仓库、工作流参数或构建日志。G0 使用 Android 调试证书签名，无需提供原 Godot 私钥或创建签名 Secrets。GitHub 每次提供干净环境，测试包证书可能随运行变化。真机仅做独立测试安装，旧包申请 ID 与签名仍待原工程核验。

## 执行与证据

在 [Actions → Android APK (G0)](https://github.com/forlorinna/shanghai3/actions/workflows/android-build.yml) 选择 **Run workflow**。选中 **preflight_only** 会测量真实磁盘，拉取固定镜像，无需 Unity Secrets。完整运行时取消选中该选项。私有仓库请核对 GitHub Actions 的包含额度和预算设置。

构建成功且签名、Manifest、ARM64 和 SHA-256 全部通过时，工作流才上传 `Shanghai-Skyline-G0-APK`，保留 7 天。打开该次运行的 **Artifacts** 下载。验证文件含证书指纹、Manifest、ABI、包结构、ZIP 对齐和校验和。实体设备安装及飞行模式运行仍需独立验证。

## 镜像与磁盘

- [Docker Hub 标签](https://hub.docker.com/layers/unityci/editor/ubuntu-6000.3.29f1-android-4/images/sha256-eabac80a6898fc4cb5e210b852c15050cdcfdefd00b30b1898372bd26355d5fe)的 `ubuntu-6000.3.29f1-android-4` 已查询成功，GameCI 默认的 `-android-3` 标签返回 404。固定 Linux/amd64 平台摘要 `sha256:eabac80a6898fc4cb5e210b852c15050cdcfdefd00b30b1898372bd26355d5fe`。
- 直接查询 Docker Registry 得到 33 个压缩层，合计 8,798,579,565 字节（8.19 GiB）。解包与构建的实际空间由托管 Runner 输出为 `Skyline-Android-disk` 制品。24 GiB 拉取前与 6 GiB 拉取后是初次验证预算。清理范围限定在临时 Runner 的四个未使用预装工具目录。
- 如果标准 Runner 清理后仍不足，已有且符合 Unity 许可的自有 Ubuntu 24.04 x64 机器可注册为仓库专用、自托管 Runner。使用 Unity Hub 安装并激活同一版本和 Android 模块，再运行 `Tools/build_android.sh`。直接安装可省去容器压缩层与解包并存空间。该路径无需付费 GitHub Runner，仍取决于是否有可用硬件和合法席位。首次可准备至少 30 GiB 空闲空间，再据实记录峰值。
