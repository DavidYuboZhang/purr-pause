# PP 目录整理与模块重构验证记录

开始日期：2026-11-07；完成核查：2026-11-08（Asia/Shanghai）。方案见[实施计划](../plans/2026-11-07-layout-and-module-refactor.md)，稳定结构及命令见 [PROJECT](../../PROJECT.md)，当前摘要见 [STATUS](../../STATUS.md)。

原始日志与临时程序由维护者离线保留，不随 Git 同步；`<本机证据根目录>` 是本机存档占位符，克隆仓库不包含该目录。下述结果保留实际观察及其限制。

## 结论与范围

目录迁移、职责拆分、自动测试、真实 Windows exe 构建及源码/发行版桌面验收完成，配置和进程现场已恢复。源码保留暂停语义、版本 0.1.2、JSON 格式、动画算法和绘制行为。截至本次桌面验收结束尚未提交、推送或发布，未改动网站部署；后续提交交付见文末，旧设计和原未提交工作均保留。

功能结论采用用户人工观察、工具截图/UIA、配置核查、进程/时钟核查分别作证。电脑接口输入有局限，未宣称全自动验收。最终退出保留一次“报告已退出但进程仍存活”的未确认观察，第二次明确退出后核实为 0；不抹去该差异。

验收为当前 Windows、主屏逻辑 1920×1080、DPR 2.0、物理 3840×2160 像素的功能验收。屏幕信息由独立只读 Qt 查询保存到 final-screen.json，未改显示设置；不扩展为多屏、长期稳定性、性能或 macOS 合格。

## 起点与证据保护

main，提交 06ef603902e34124aefca7ae0d35d5489c8190f7。开始时保留 timer/tray 及对应测试的暂停修复、未提交管理文档、环境和历史报告；无 PP 实例，无既有 build/dist、生成图标或 spec。源码 config.json 不存在，真实 AppData 原配置 20 分钟／30 秒。

证据目录：`<本机证据根目录>\pp-refactor-20261107-201204`。before.json 保存 674 个原跟踪文件哈希及配置原字节，before-files 保存原文本工作区，before.patch 保存原跟踪差异，旧轮次证据未覆盖。

桌面执行前重新核查：pre-ui.json（UTC 11-07 12:32:43）保存 656 个源码/测试/资源/默认配置哈希及新配置快照，pre-ui-processes.json 无 PP。源码仍无配置，真实 AppData SHA-256 为 238b01f1cc72c779018edb044f989734ed14e1c59b6548abd6e0b915cb2658c3。首次空管道未生成进程记录文件造成一次读取错误，改为显式空数组序列化；不是应用异常。exe 启动前另有 pre-exe.json、pre-exe-direct.json 现场复核。

## 环境与自动测试

Conda PP 的 Python 3.11.18、PyQt6/Qt 6.12.0、Pillow 13.0.0、pytest 9.2.0、pytest-qt 4.5.0 不变。按需通过 PP Python 的 pip --no-user 新增 PyInstaller 6.22.3、altgraph 0.17.5、pefile 2024.8.26、pyinstaller-hooks-contrib 2026.9、pywin32-ctypes 0.2.3。未安装 NumPy、视频或 OSS 工具；未改系统 Python/base。

实装 Conda 导出同步到 config/environment.yml，移除 prefix/build 编号；最终核对 20 个 Conda 和 16 个 pip 条目版本全部一致，pip check 通过（final-environment-check.json）。环境未在第二份机器/环境重建，不称为跨平台锁定文件。

使用 PP 解释器、PYTEST_QT_API=pyqt6、QT_QPA_PLATFORM=windows，保留 faulthandler。每轮使用新的可写 basetemp，完整命令形如 `python -m pytest -v -ra --basetemp <新目录> --junitxml <XML路径>`，未用 offscreen 替代原生平台。

| 阶段 | 通过 | 失败／错误／跳过 | 耗时 | 证据 |
|---|---:|---|---|---|
| 重构前 | 87 | 0／0／0 | 3.88 秒 | baseline-tests.log/XML |
| 机械迁移后 | 87 | 0／0／0 | 3.94 秒 | migration-tests.log/XML |
| 接口切换后 | 102 | 0／0／0 | 4.28 秒 | cutover-tests.log/XML |
| 路径/真实窗口/构建契约子集 | 21 | 0／0／0 | 2.69 秒 | contracts-tests.log/XML |
| 首次完整重构 | 113 | 0／0／0 | 6.54 秒 | final-tests.log/XML |
| ICU 构建修正后的最终套件 | 114 | 0／0／0 | 6.69 秒 | icu-corrected-tests.log/XML |

原有 87 项按类、用例名和参数逐项迁移保留，见 final-case-mapping.json。新增 27 项覆盖配置复制/格式/错误、组合保存只写一次并保留未知字段、取消、暂停保存/继续、重复提醒抑制、真实卡片/动画自然结束及提前关闭、两个窗口销毁和下一轮、托盘操作意图、其他工作目录资源定位、冻结路径、无 Qt/配置副作用的版本导入，以及构建 DLL 搜索顺序。移除测试 sys.path 注入及全局 PyInstaller 假模块；实际构建入口单独检查打包依赖。

TDD 缺模块/函数的首次失败保留在 store-red、controller-red、session-red、dll-red、icu-red 日志。ICU 修正首版另有 SystemRoot 在普通 dict 中大小写查找失败，3 失败/111 通过（icu-final-tests）；改用 Windows os.environ 查找后全部通过，不掩盖失败。代码审阅在内存副本反转控制器重复提醒条件，2 项测试失败、5 项通过，产品字节未变（mutation.log）；该受控实验不是最终套件失败。

## 目录与职责核查

运行代码归 purr_pause；main.py 薄入口与包 __main__ 共用 app.main，无需安装项目。core 不依赖 UI/配置存储；infrastructure 处理 JSON、路径、Windows 辅助；ui 发操作意图，不写配置或改变工作计时。controller 组合保存一次并保留暂停状态，rest_session 在显示/淡出期间抑制重复，待两窗口销毁释放引用。绘制控件及原生窗口辅助仅提取，不重设计算法或视觉。

默认配置迁至 config/config.default.json；源码用户配置仍在仓库根，冻结资源与 _MEIPASS/add-data 目标一致，发行用户配置仍在 AppData。构建、OSS、发行工作流改为读取 purr_pause.version，不初始化 Qt 或创建配置。生成图标、spec、中间文件归 build，发行文件归 dist；旧根运行模块移除，仅保留 main.py。

final-integrity.json 核对 18 个原文件迁移、7 个获授权的原跟踪文件改动、649 个其余原跟踪文件未变；617 个 assets 文件哈希不变，默认配置字节未变。计时器、动画模型、CatWindow、进度条、发光控件和两项绘制/字体辅助 AST 与原工作区相同。桌面前 656 个保护文件中，655 个未变，唯一后续变化为新增 ICU 回归测试的 tests/unit/test_build_dist.py；运行时文件没有再改动。

## Windows 构建与首次失败定位

真实执行 `python scripts/build_dist.py`。重构前构建退出 0，129670788 字节，SHA-256 00da9ba75686466339c6019a9eefa857bf5db07bced81745e76f51ee4e8a9ff5，原包保留 baseline-dist/。首次已有 ffi.dll 遗漏警告，PP Library/bin 中存在该 DLL；只对构建子进程补充该目录后重建，警告消失，第二份原代码包另存。这两次构建成功不等于已通过桌面验收。

首次重构后包也构建成功（约 29.6 秒，129567691 字节，SHA-256 bb9dda95472eafc807ae7cd1e5f6d7992782b5e7e7a3db1c390637b6c8743cba），但实际启动失败：UTC11-07 15:30:01，外层 PID33136、运行 PID24300、观察器29792；UIA 文本和日志显示导入 QtWidgets 的 DLL load failed（找不到指定的程序）。尚未创建隔离配置。错误窗口截图受遮挡，不作为图像证明；Close 调用报告 foreground window did not report a process id，后续刷新窗口已关闭，UTC15:33:04 退出 1，具体关闭来源未确认。失败包、Analysis 清单、日志保留 first-failed-dist/、first-failed-build.json、exe-first-failure.json、desktop-exe-first.log。

confirmed-icu-diagnosis.json 核查 91 个归档二进制：Qt6Core 需要 20 个无版本后缀 ICU 函数，打包 PATH 选中的 Poppler icuuc.dll 没有这些函数，Windows System32 ICU 提供；Analysis 清单明确指向执行环境的 Poppler。两份重构前包含同哈希的错误库，属于既有构建环境污染，未归为业务/目录回归。pefile 默认 8192 导出上限曾造成 Qt 大 DLL 假阳性，提高至 200000 后仅 ICU 不匹配；保留并标注诊断修正，无依据的 MSVC 冲突假设未实施。

修正仅作用于构建子进程：PATH 先放 System32，再补 PP Library/bin 及原 PATH，避免工具同名 ICU 遮蔽系统库；不改系统 DLL/PATH、产品行为或包版本。依据 [Microsoft DLL 搜索说明](https://learn.microsoft.com/en-us/windows/win32/dlls/dynamic-link-library-search-order)；冻结路径依据 [PyInstaller 运行时说明](https://pyinstaller.org/en/stable/runtime-information.html)。

最终重建退出 0，约 28.9 秒：`dist/PurrPause-0.1.2-windows.exe`，**115891602 字节（110.5 MiB）**，SHA-256 **c4ba461cf1e13341f53f9fbe897cb581b55bcc8b1677d91e13f90ce5d0758c2a**。证据 icu-fixed-build.log/JSON、final-build.json。归档内默认配置、manifest、611 帧、两张图片、GIF 和字体共 617 项逐字节一致；qwindows.dll、ffi.dll 存在，不再包含错误 ICU。本轮未构建 macOS、未运行 OSS 或发布。

## 桌面验收结果

临时 supervisor 仅启动未修改的应用、记录 PID/起止时间/退出码，不调用产品内部业务方法。源码由用户桌面独立入口以 python -m purr_pause 启动；发行版由助手从其他工作目录启动，并只对子进程设置隔离 APPDATA。用户提出提效后，exe 仅补验打包相关场景，不重复源码暂停、焦点及穿透。

| 场景 | 结果 | 证据来源 |
|---|---|---|
| 源码启动/托盘/版本/初值 | 通过；v0.1.2，20 分钟／20 秒，无额外普通主窗口 | 用户观察；source-step1.json；PID/配置核查 |
| 源码直接暂停 | 通过；UTC15:10:14–15:11:48 共94秒，无新提醒、菜单仍继续 | 用户观察、时钟、进程/配置；source-direct-pause.json |
| 暂停期间保存 | 通过；明确保存1/20、1/30、1/20、2/20、1/20，每次菜单继续；UTC15:15:45–15:17:14 共89秒无新提醒 | 用户观察、时钟、最终配置核查；source-saved-pause.json；文件只证明最终值，不证明5次点击 |
| 源码继续/自然结束 | 通过；菜单变暂停、提醒恢复，中文/20秒倒计时/猫咪完整，两窗口消失，无明显裁切残留 | 用户观察；source-resume-natural-finish.json；未采集精确点击延迟，不评价计时精度 |
| 源码提前关闭/后续交互 | 通过；约3–5秒点×，两窗口消失；下一轮恢复，不抢焦点，可穿透猫咪到记事本编辑区 | 用户观察；source-early-close.json、source-next-reminder-input.json |
| 源码退出/恢复 | 通过；UTC15:25:57.296退出0，进程/观察器/本轮命令窗口均结束，配置恢复不存在 | source-restoration.json、source-after-exit-processes.json；用户收尾报告 |
| exe 修正后启动/设置 | 通过；实际创建隔离默认配置，托盘可打开设置，中文布局/20与20初值可读 | 用户打开设置；工具截图/UIA、exe-fixed-start.json、exe-settings-computer-use.json |
| exe 保存/重启持久化 | 通过；人工保存1/20，文件一致、首次退出0；新进程 GUI 仍1/20，取消不改变文件 | 用户观察、隔离配置及退出码；exe-saved-first-exit.json、exe-restarted-smoke-user-result.json |
| exe 资源/自然结束/提前关闭 | 通过；中文、倒计时、动画正常，自然结束两窗口均消失、无裁切残留；下一轮提前关闭正常 | 用户观察；exe-restarted-smoke-user-result.json；归档资源另作字节核查 |
| exe 最终退出 | 通过，保留首次差异；再次明确点击退出后，2026-11-08 00:00:54.783 正常退出0，三层进程结束 | 用户复核、desktop-exe-fixed-restart.json、final-confirmed-processes.json |

源码主要 PID5304、观察器6556；修正后 exe 首轮外层28436、运行30204、观察器32996（UTC15:40:36–15:53:45，退出0）；重启轮外层12564、运行24112、观察器12248（UTC15:54:58–16:00:54，退出0）。这些运行时长包括等待人工回复，不称为额外长期稳定性验证。

电脑接口的能力限制保留：托盘和无边框窗口未稳定返回；用户打开设置后，工具可截图/UIA读取并 set_value 改为1/20，但元素保存点击、刷新后截图坐标保存点击、一次Tab均无可观测效果，隔离文件仍20/20。停止自动输入，人工保存成功后文件一致且正常退出；不将自动化限制写成产品保存缺陷。

最后收尾的首次“已退出”报告与进程状态不一致：UTC15:57:28及15:58:19仍有12564/24112/12248，退出码null、日志0字节。请求窄范围复核后，用户再次明确点击退出、等5秒并确认无图标；观察器记录UTC16:00:54.783退出0，最终进程查询为空。首个动作状态/原因未确认，不抹去观察，也不声称已修复某个退出代码缺陷；没有强制终止来取得通过结果。

## 最终恢复、审阅与交接

2026-11-08 最终核查（final-restoration.json、final-integrity.json）：无本轮 PP/观察器进程或待办人工请求；源码 config.json 恢复不存在，真实 AppData 原始字节始终一致，SHA-256 238b01f1cc72c779018edb044f989734ed14e1c59b6548abd6e0b915cb2658c3。隔离配置取消后字节未变，归档为 exe-final-isolated-config.json 后移除隔离目录，恢复其原本不存在。三个本轮 TEMP 入口逐个检查路径和哈希后删除（desktop-launcher-cleanup.json）；不删除其他入口、文件或终端。用户已关闭测试记事本并报告删除测试内容，工具未操作用户文档。

最终保留 build/dist、本轮初始及失败 exe、诊断日志和临时诊断程序作为离线证据，无程序在运行。AGENTS 协作规则未变；PROJECT 更新模块/命令/环境/构建说明，STATUS 归纳当前结果，DECISIONS 的 D-006 替代 D-002 后续布局安排，历史决定和设计保留；README 中英文增加模块启动及文档导航，ASSETS 更新默认配置位置。

审阅覆盖正确性、可读性、依赖方向、配置/子进程边界及原有资源开销；无新增长期转发层、功能框架或诊断屏蔽。旧实例退出与0x8001010d的历史结论见[独立诊断报告](2026-11-04-exit-and-native-diagnostic.md)，不据本轮推定旧异常已修复。README旧地址和行为说明已在后续提交准备中修正；CI测试门禁、macOS及第二份环境重建仍为独立事项。

桌面验收结束时全部改动保留未提交，Git将迁移体现为旧文件删除和新目录未跟踪。2026-11-08 用户随后明确授权索引组装、四个提交及草稿 PR；后续过程如下，不改变此前历史记录。

## 2026-11-08 审阅与提交交付

审阅覆盖原 74 个文件变更（7 修改、18 删除、49 未跟踪）；本地与远端 main 同为 06ef603902e34124aefca7ae0d35d5489c8190f7。审阅复跑 114 通过、0 失败/错误/跳过、6.68 秒、退出 0；在真实窗口集成用例再次出现 0x8001010d 诊断后继续完成。沿用既有 UIA/RPC 分类并记录本次观察，未追认本次具体触发者、未屏蔽诊断或宣称旧退出已修复。

随后按用户授权在 codex/pp-handoff-20261108 组装四个提交。每个代码提交从 Git 索引导出到独立临时目录测试，而非测试一个尚未对应提交的混合工作区；当前工作区没有为组装提交反复还原。

| 提交 | 内容 | 索引快照验证 |
|---|---|---|
| c01c496 | 旧布局下暂停保存保持暂停及回归测试 | 87 通过，3.97 秒，退出 0 |
| 47ecde4 | 应用包、职责拆分、测试与必要路径迁移 | 111 通过，6.81 秒，退出 0 |
| c017acc | Windows DLL 搜索与环境清单、三个新增用例 | 114 通过，6.83 秒，退出 0 |
| 最后文档提交（以 Git log 为准） | 管理/验证文档、README、Unreleased、历史链接与本地证据说明 | 对导出索引检查 UTF-8、链接、忽略项、资源、环境及最终文件清单 |

三轮索引测试各保留一次 0x8001010d 原生诊断，均继续完成、无跳过且退出 0；不选择性重跑取得无诊断结果。原始 test-1..3.log/XML、索引树及工作区快照离线保存在 `<本机证据根目录>\pp-handoff-20261108-134914`。文档修正了历史计划中的旧路径、中英文设置/配置说明和仓库地址；本地 exe 改为普通路径及哈希说明，build/dist、用户配置和原始诊断资料不随 Git 上传。

暂存检查额外发现 card_widgets.py、tray.py 的文件尾空行，已仅去除空白；设置集成测试仅修正过期注释。与提交准备前比较，全部运行时 Python AST 不变，既有构建脚本、依赖及默认配置内容未变，继续复用上述 exe 和人工桌面验收，未重建或重复操作用户桌面。

交付通过独立分支和面向 main 的草稿 PR；同步时禁用标签跟随，不更新 main、不合并、不发布、不改站点或 macOS、不新增 CI 工作流。当前 workflow 不提供 PR 自动测试门禁，没有检查记录不代表 CI 通过。远端具体提交与 PR 状态以 GitHub 为准。
