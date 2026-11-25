# 魔都天际线 · 第一批执行记录

当前关卡为 G0，最小 APK 构建受阻。已完整读取 MASTER 的 43 章。工作区的 `.git` 挂载为空，未配置项目仓库或分支，未找到原 Godot 工程、旧签名 APK、存档或构建脚本。当前新增文件已保存在独立 UnityProject、Tools、Docs 和 AssetSources 目录。

- `Tools/build_android.sh` 与 Unity Editor 构建入口已落地并运行预检。退出状态为 69，原因是缺少 Unity Editor。当前磁盘容量小于官方 Linux Editor 安装后体积，且当前环境无已激活许可。详情见 `Docs/ANDROID_BUILD_REPORT.md`。
- 已下载并验证四张 CC0 摄影 PBR 贴图。Unity 材质与场景由 Editor 构建入口生成，尚待实际运行。
- Blender 生成了环球金融中心参考几何样件。源模型封闭且拓扑流形，具有贯通倒梯形空腔。BLEND 与 GLB 都通过七项几何射线检查，最大标高 492 m。模型仅用于形体与拓扑核验，截面尺寸为估计，缺少幕墙、裙楼、地理配准、运行时材质和 Unity 碰撞验收。样件在 Unity 工程外。
- 已建立外滩及陆家嘴建筑种子档案、来源记录与迁移矩阵。逐栋建模验收、完整玩法和离线 APK 均待执行。

继续执行 G0 需要原 Godot 源码，以及具备足够磁盘、已激活 Unity 6 LTS、Android Build Support、SDK/NDK 和配套 OpenJDK 的环境。在该环境执行 `Tools/build_android.sh` 后，检查设备安装、飞行模式首次启动和触控。当前无 APK。

另已保存 8 个方向的 Blender CPU 轮廓图及合成预览 `AssetSources/Processed/SWFC/SWFC-review.png`。对岸实拍原图及署名已随源资料保存。轮廓预览只供几何评审，Unity/Android 视觉验收待运行。

## GitHub Actions 迁移

云端构建已改走 GitHub 私有仓库 `forlorinna/shanghai3` 的标准托管 Runner 和 GameCI 固定镜像。[磁盘预检](https://github.com/forlorinna/shanghai3/actions/runs/45527428488)通过，镜像拉取后实际可用 8.9 GiB。[首次构建](https://github.com/forlorinna/shanghai3/actions/runs/45528088581)因缺少 `UNITY_LICENSE` 在 Secrets 检查退出。请在仓库 Actions Secrets 配置合法 Unity 凭据，随后可恢复 G0。外滩五栋建筑身份及门牌已查证，旧版玩法状态继续标记为未知。当前无 Unity APK。
