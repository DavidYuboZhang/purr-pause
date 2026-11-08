# PP 目录整理与模块重构计划

日期：2026-11-07（Asia/Shanghai）。本方案来自用户明确批准的同名实施计划。执行状态见 STATUS，验证结果见 docs/baselines/2026-11-07-layout-refactor.md。

## 目标与约束

根目录应用包 purr_pause，保留 python main.py、增加 python -m purr_pause，不安装项目本身。保持产品行为、动画算法、视觉、0.1.2 版本和 JSON 格式；保留现有暂停修复，以 87 项测试和 Windows 实测基线对照。先机械迁移再拆分职责，分别验证，不自动提交/推送/发布。

## 目标结构

- main.py：薄启动入口；purr_pause/__main__.py 提供模块入口，__init__.py 保持轻量。
- purr_pause/app.py：QApplication、装配、退出；controller.py：设置/暂停继续/提醒协调；rest_session.py：单次休息及窗口生命周期；version.py：唯一版本。
- core/timer.py、core/animation_model.py：原计时器与纯 Python 动画模型；不依赖 UI/配置。
- infrastructure/config_store.py、paths.py、windows.py：JSON 存储、源码/冻结路径、原点击穿透辅助；不依赖 UI。
- ui/tray.py、settings_dialog.py、rest_card.py、animation_window.py、card_widgets.py：视图与意图信号，绘制行为不变。
- config/config.default.json：迁移默认模板；config/environment.yml：实装环境清单。
- tests/unit、tests/integration、tests/conftest.py：保留原 87 项行为覆盖，并新增集成测试。
- assets、scripts、site、deploy、历史 docs 保留位置；611 帧及资源不改。生成图标/spec/中间产物统一 build，发行文件仍在 dist。
- 旧根级模块迁移后删除，仅 main.py 保留为启动兼容入口，不保留长期转发层。

## 接口

- ConfigStore(config_path, default_path).load() -> dict，save(config) -> None；保留未知字段、默认/错误处理，不引入 schema 迁移。
- SettingsDialog 保留构造参数和输入范围，将两个信号合为 saved(interval_minutes, rest_duration_seconds)，取消不发信号。
- TrayIcon 只发 pause_toggle_requested、settings_requested、quit_requested；set_paused(bool) 同步文字，不写配置或控制计时。
- ApplicationController 注入 timer/store/tray/session/dialog_factory；读取当前配置合并两字段写一次，再按现有 reset 语义更新计时。运行保存重置，暂停保存仍暂停。
- RestSession 注入资源目录与窗口工厂，start(config)->bool、is_active、finished；显示/淡出时抑制重复提醒，卡片完成/提前关闭通知动画结束，窗口销毁后释放引用。
- 保持既有计时、模型和窗口业务方法语义，Windows 标志仅迁出。

## 路径与工具

源码用户配置仍为根 config.json，发行版仍为 AppData。源码资源以模块位置推导仓库根，不使用 cwd；冻结资源以 _MEIPASS 为根，匹配打包目录。构建/OSS/发行工作流统一引用包内版本，读取版本不初始化 Qt 或创建配置。

保留现有脚本命令；去除测试中的 sys.path 修改、全局 PyInstaller 伪造；只在真正构建入口检查打包依赖。默认配置内容不变，资源哈希不变。

## 实施步骤

1. 新快照保护工作区、配置、资源和既有产物；安装 PyInstaller 6.22.3、altgraph 0.17.5、pefile 2024.8.26、hooks-contrib 2026.9、pywin32-ctypes 0.2.3，同步环境；执行基线测试和当前源码真实构建。先处理重构前构建失败，不误归因于重构。
2. 完整模块机械迁移，更新导入/入口/资源/构建路径，不拆行为；原测试通过再进行下一步。
3. 依次拆配置和设置 UI、托盘和控制器、休息会话和入口，最后控件/平台辅助。每步执行对应测试，再完整验证。
4. 构建最终 exe，真实源码/发行版验收，更新管理文档、README、资源说明、架构决定及验证报告。

## 验收

- 原 87 项逐项迁移，保留/等价增强断言，不删/跳过/弱化失败；新增单次组合写入、未知字段、取消、暂停保存/继续、重复提醒、自然/提前结束、销毁等集成覆盖。
- 不同 cwd 的资源/源码配置、冻结路径、版本、默认模板/帧/图片/字体完整性，以及构建路径覆盖。
- Windows 源码验收暂停/保存/继续/提醒；exe 验证启动/托盘/设置持久化/资源/自然结束/提前关闭/退出，优先隔离子进程 AppData。
- 真实桌面采用用户点击、助手核验，用户桌面启动避免工具会话生命周期干扰，记录本轮 PID/退出码；按新快照恢复配置、保护真实 AppData、清理本轮进程/入口。
- 必须完整测试、真实 exe 构建与冒烟、资源哈希与文档链接均通过才算完成；辅助构建测试不能替代实际 exe。

不重设计核心机制，不处理网站部署/macOS 发布/长时稳定性。旧退出历史未知保持，原生 UIA/RPC 诊断照实保留，不关闭诊断来掩盖问题。
