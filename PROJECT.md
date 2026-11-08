# Purr Pause 项目说明

## 项目概况与产品目标

Purr Pause，项目代码 PP，通过可爱的猫咪动画提醒用户定时休息放松。产品采用轻量、可关闭的桌面提醒，围绕 20-20-20 休息节奏提供陪伴。

- 仓库：[DavidYuboZhang/purr-pause](https://github.com/DavidYuboZhang/purr-pause)，默认分支为 `main`。
- 许可证：[MIT](LICENSE)；二进制资源的来源与许可说明见 [ASSETS.md](ASSETS.md)。
- 版本以 [purr_pause/version.py](purr_pause/version.py) 为准；发行变化见 [CHANGELOG.md](CHANGELOG.md)。

## 功能范围

- 默认每工作 20 分钟提醒休息 20 秒，显示休息卡片、倒计时和猫咪动画。
- 系统托盘提供暂停、继续、设置和退出；关闭窗口不等同于退出整个应用。
- 同一实例中，暂停及暂停时保存设置均停止新的周期提醒；只有明确继续才按最新间隔重新计时。已开始的休息可自行结束或关闭；暂停状态不跨重启保存。运行中保存设置仍从完整工作间隔重新计时，取消不改变配置或暂停状态。
- 设置窗口支持提醒间隔 1–60 分钟、休息时长 10–60 秒，并保存配置。
- 可提前关闭休息提醒；正常结束和提前关闭均涉及卡片与动画窗口的协调。
- 配置保留 `cat_image_path`，供休息卡片加载自定义图片；现有设置窗口未提供路径编辑控件。卡片图片与独立的走动猫咪动画是两套资源。
- 当前发行平台为 Windows 10/11。macOS 尚未发布，发布工作流明确停用其构建；已知图标生成问题见 [STATUS.md](STATUS.md)。

运行时代码采用本地计时、配置和资源，不包含自动更新检查。仓库中的站点部署及 OSS 镜像工具属于发行基础设施，不是桌面应用的运行前提。

## 技术架构

应用使用 Python 和 PyQt6，运行代码集中在根目录应用包 `purr_pause/`，无需安装项目本身。`main.py` 与 `python -m purr_pause` 共用 `app.main()`：创建 QApplication，装配存储、计时器、托盘、控制器和休息会话，再进入 Qt 事件循环。退出时停止计时并关闭本实例的休息窗口。

`ApplicationController` 协调操作意图、配置和工作计时；组合设置保存只写一次，并保留未知配置字段。UI 只显示及发出信号，不写配置或改变工作计时。`RestSession` 持有一轮提醒的卡片和动画窗口，显示或淡出期间抑制重复创建，待两者销毁后释放引用。

计时器周期发出提醒信号；休息卡片负责倒计时，独立透明窗口播放猫咪动画。动画模型按经过时间和目标休息时长选择帧，Qt 窗口按需读取、缩放并绘制当前帧，连续序列播放一次覆盖休息时长。绘制控件独立在 `ui/card_widgets.py`；Windows 点击穿透辅助位于基础设施层，沿用原窗口标志。

暂停状态由 `RestTimer` 维护，通过 `paused_changed(bool)` 信号同步托盘文字；设置更新间隔时保留该状态。具体行为依据见 [D-005](DECISIONS.md#d-005)，验证范围见 STATUS。

完整开发依赖声明见 [requirements.txt](requirements.txt)：PyQt6、NumPy、Pillow、pytest、pytest-qt 和 PyInstaller。测试使用 pytest + pytest-qt；Windows 单文件发行包使用 PyInstaller。该清单包含运行、测试及打包用途，不要求创建基础环境时一次性安装。

当前源码运行及现有测试的直接依赖为 PyQt6、Pillow、pytest、pytest-qt；打包辅助函数可直接导入，PyInstaller 依赖仅在实际构建入口检查。完整测试通过不代表发行包可用，发行包须实际构建和桌面验证。素材重制依赖在执行对应任务时另行安装。

## 开发与运行环境

主要开发和验收环境为 Windows + PowerShell，使用名为 `PP` 的 Conda 环境。发布工作流使用 Python 3.11；初始化优先对齐该版本的依据见 [D-003](DECISIONS.md#d-003)，最小环境及按需补充依赖的安排见 [D-004](DECISIONS.md#d-004)。具体本机解释器、安装状态和实测结果统一查看 [STATUS.md](STATUS.md)。

[config/environment.yml](config/environment.yml) 保存 Windows 运行、测试与构建环境的 Python、pip、Conda 运行库及 pip 包版本；Conda 包使用 `defaults` 渠道，不包含构建编号或本机绝对路径。该文件面向 Windows 环境重建，尚未作为跨平台锁定文件验证。`requirements.txt` 保留完整依赖声明，两者用途不同。

以下为在项目根目录执行的环境重建及检查命令。创建命令用于尚不存在 `PP` 的机器，须先确保 Conda 可用且 shell 支持激活；已有环境使用更新命令。已验证范围及本机启动器的替代调用方式见 STATUS。

```powershell
conda env create --file config/environment.yml
conda activate PP
python --version
python -m pip check
```

已有 `PP` 环境按清单更新：`conda env update --name PP --file config/environment.yml`。先建立可用的 Python 与 pip 基础环境，再按运行、测试、打包或研究任务补充所需依赖；安装后同步实装版本至环境文件。完整安装 `requirements.txt` 仅用于确实需要完整开发工具链的场景。

在对应依赖齐备并激活环境后，使用 `python -m pytest -v -ra` 执行测试、`python main.py` 或 `python -m purr_pause` 启动源码版、`python scripts/build_dist.py` 构建发行包。也可从其他工作目录通过 `python "<仓库绝对路径>\main.py"` 启动；内置资源及源码用户配置位置不随工作目录改变。

Qt 测试使用 Windows 原生平台，可在子会话设置 `PYTEST_QT_API=pyqt6`、`QT_QPA_PLATFORM=windows`。若运行环境的默认临时目录不可写，使用 `python -m pytest -v -ra --basetemp '<新的可写临时目录>'`；目标必须是新建且仅供本次测试使用的目录，pytest 会管理该目录内容。无界面测试不能代替真实桌面验收。

环境文件依据 `conda env export --name PP --no-builds` 的实际输出维护，并移除 `prefix` 字段；保留必要注释。该导出记录全部当前包版本，其中包括自动解析的传递依赖。创建、重建与导出方式参见 [Conda 官方环境管理文档](https://docs.conda.io/projects/conda/en/stable/user-guide/tasks/manage-environments.html)。

打包产物为 `dist/PurrPause-{VERSION}-windows.exe`，其中版本取自 `purr_pause/version.py`。生成图标、spec 和 PyInstaller 中间文件分别位于 `build/icons/`、`build/specs/`、`build/pyinstaller/`。Windows 构建脚本仅对子进程将系统 `System32` 放到 PATH 首位，再补充当前 Conda 环境的 `Library/bin`，避免外部工具同名 ICU DLL 被误收集；不改变系统或父进程 PATH。本地构建不发布版本；发布工作流由版本标签推送触发，并检查标签与代码版本一致。官网另有部署工作流，涉及 `site/` 等路径的主分支推送可能触发部署，具体条件以工作流为准。

### 配置、资源与专用工具

- 默认配置由 [config/config.default.json](config/config.default.json) 提供；JSON 格式和缺省处理不作迁移。
- 源码运行时写入根目录 `config.json`；Windows 打包运行时写入 `%APPDATA%\PurrPause\config.json`，未设置 APPDATA 时回退至用户目录下 `AppData\Roaming\PurrPause`。
- 只读资源通过 [infrastructure/paths.py](purr_pause/infrastructure/paths.py) 解析：源码以模块位置确定仓库根，冻结模式以 `_MEIPASS` 定位；打包默认配置目标为 `config/`，与运行时解析一致。依据见 [PyInstaller 运行时说明](https://pyinstaller.org/en/stable/runtime-information.html)。用户配置和构建产物的忽略规则见 [.gitignore](.gitignore)。
- 常规运行使用已提交的动画 PNG 和 manifest；无需重新提取视频。重新生成动画另需未纳入 Git 的源视频及 OpenCV，执行前须阅读提取脚本和资源说明。
- OSS 同步脚本另需 `oss2` 和相应凭据；macOS 打包另需专用环境及 `dmgbuild`。常规本地开发无需配置这些发行工具。

## 项目结构与协作安排

| 路径 | 职责 |
|---|---|
| 四份根目录管理文档 | 协作入口、稳定事实、当前状态和重要决定；分工见 [AGENTS.md](AGENTS.md) |
| `main.py`、`purr_pause/__main__.py` | 兼容脚本入口和模块入口，共用 app.main |
| `purr_pause/app.py`、`controller.py`、`rest_session.py` | 对象装配/退出、业务协调、一轮休息窗口生命周期 |
| `purr_pause/core/` | QtCore 工作计时及纯 Python 动画模型；不依赖 UI 或配置存储 |
| `purr_pause/infrastructure/` | ConfigStore JSON 读写、源码/冻结路径、Windows 点击穿透；不依赖 UI |
| `purr_pause/ui/` | 托盘、设置界面、休息卡片、动画窗口和卡片绘制控件 |
| `purr_pause/version.py` | 唯一版本来源，导入不初始化 Qt 或创建配置 |
| `config/` | `environment.yml` 保存实装 Conda 环境；`config.default.json` 为应用默认配置 |
| `requirements.txt`、`pytest.ini` | 完整依赖声明、测试入口配置 |
| `tests/unit/`、`tests/integration/`、`tests/conftest.py` | 单元、集成及共享测试安排；自动测试隐藏托盘，不改原生 Qt 平台 |
| `assets/` | 内置动画、图片和字体 |
| `scripts/` | 打包、动画提取、演示素材生成及发行辅助工具 |
| `docs/` | 专项设计、技术分析、历史计划及演示素材 |
| `site/`、`deploy/` | 下载站点及服务器配置 |
| `.github/workflows/` | 发行、OSS 镜像及站点部署自动化 |
| `build/`、`dist/` | 已忽略的构建中间文件与本地发行文件 |
| `.vscode/` | 已有编辑器配置；环境管理器设置不代替实际解释器核查 |
| `.git/` | Git 管理数据，由 Git 工具维护 |

目录和模块边界依据见 [D-006](DECISIONS.md#d-006)；不保留旧根模块转发层。内部管理文档使用中文，代码标识符及命令保留原文；README 保持现有中英文安排。协作、维护和会话规则统一遵循 [AGENTS.md](AGENTS.md)。

## 文档导航

- 使用、下载和产品介绍：[中文 README](README.md)、[English README](README.en.md)。
- 当前任务、验证和接手信息：[STATUS.md](STATUS.md)。
- 重要选择及变更依据：[DECISIONS.md](DECISIONS.md)。
- 初始设计：[产品设计规格](docs/superpowers/specs/2026-05-10-purr-pause-design.md)；动画历史方案：[动画 v2 设计](docs/superpowers/specs/2026-06-12-cat-animation-v2-design.md)；发行方案：[分发设计](docs/superpowers/specs/2026-05-30-distribution-rollout-design.md)。

`docs/superpowers/` 中的设计和计划保留为历史参考，部分描述早于当前实现。阅读时须对照代码和测试，不将旧计划直接当作当前任务清单；已发现的差异在 STATUS 中维护。
