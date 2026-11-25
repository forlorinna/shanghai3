# G0 Android 构建记录

| 检查 | 结果 |
| --- | --- |
| 宿主 | Debian 13 x86-64，AMD EPYC 9V74，cgroup 限额 2 核与 8 GiB。 |
| 存储 | 工作区和临时目录同一卷，可用约 7.5 GiB。 |
| 图形与 Android 设备 | `/dev/dri`、`/dev/kvm` 不存在，未发现 ADB 或可连接的真机。 |
| 已安装 | Blender 4.3.2，系统 OpenJDK 21。 |
| Unity | 未发现 Linux Editor、Hub、已激活许可证、Android SDK/NDK 或 Unity 配套 OpenJDK。 |
| 官方发布 | 6000.3.29f1 (96d2fe17529c)。Unity 发布接口列出 Linux Editor 压缩包 4,559,304,568 B、安装后 8,749,926,400 B。安装后体积单项已超过可用空间。发布方 URL、完整性值和 Android 组件清单见 `unity-toolchain-release.json`。 |
| 官方支持 | [Unity 6.3 系统要求](https://docs.unity.com/en-us/engine/6000.3/manual/get-started/install-and-upgrade/getting-started-installing-unity/system-requirements)列出的 Linux 发行版为 Ubuntu 22.04 和 24.04。[Unity Personal](https://docs.unity.com/en-us/hub/manage-license)通过本人登录 Hub 激活。 |
| 下载访问 | 默认命令沙箱无法连接代理。启用单次命令网络权限后，Unity 发布接口和 Poly Haven 资源下载均成功。 |
| 执行 | `./Tools/build_android.sh` 返回 69。见 `Builds/g0-preflight.log`。 |
| Android | APK、签名、安装、离线首次运行、16 KB 原生库兼容、Vulkan 和 Android 16 真机测试均未执行。 |

G0 构建源码已配置显示名《魔都天际线》、独立测试 applicationId、URP、线性色彩、ARM64、IL2CPP、Vulkan、横屏及 API 36 目标。首次受支持环境执行将生成验证场景、材质和包锁定文件，目前尚无 Unity 编译结果或生成场景。

后续托管构建已切换至 GitHub Actions，固定 GameCI 镜像成功拉取后剩余 8.9 GiB。完整构建在 GitHub Secrets 检查因缺少 `UNITY_LICENSE` 退出，详见 [当前 CI 记录](GITHUB_ANDROID_CI.md)。
