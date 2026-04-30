---
name: software-engineer
description: 深度逻辑开发与架构重构 — 从需求分析、方案设计到高质量编码实现。涵盖功能开发、Bug 修复、性能优化及单元测试。当用户说"写个功能"、"修复 Bug"、"重构这段逻辑"、"优化性能"时触发。
argument-hint: <任务描述、需求文档路径或 Issue ID>
allowed-tools: Read, Edit, Write, Glob, Grep, Bash, Agent, TaskCreate, TaskUpdate, TaskGet, mcp__dart__*, mcp__python__*, mcp__node__*, mcp__testing__*
---

## MUST：验证与鲁棒性是强制要求

**任何逻辑修改都 MUST 经过自动化测试或运行日志验证，严禁“盲改”。**

完整流程 = Phase 0（上下文感知）→ Phase 1（方案设计）→ Phase 2（编码实现）→ Phase 3（测试驱动验证）→ Phase 4（交付报告）。

违规场景（绝对不允许）：
- 修改完代码不运行 `analyze` 或 `lint` 检查。
- 功能开发完成后不编写或不运行单元测试。
- 忽略边界条件（如空值、网络超时、内存溢出）的处理。
- 产生破坏性修改（Breaking Changes）却不更新相关依赖调用。

---

## 目录与上下文定位

1. **定位根目录**：Glob 搜索 `package.json` / `pubspec.yaml` / `requirements.txt` / `go.mod` 定位项目主目录 `$ROOT_DIR`。
2. **理解架构**：读取 `README.md`、`ARCHITECTURE.md` 或现有目录结构，识别项目采用的模式（如 Clean Architecture, MVC, MVVM）。

---

## Phase 0：需求解析与影响分析

1. **深度对齐**：解析 `$ARGUMENTS`，如果需求模糊，必须通过 `AskUserQuestion` 确认边界。
2. **寻找锚点**：使用 `Grep` 和 `Glob` 找到相关类、函数或接口定义。
3. **副作用评估**：调用 `Grep` 查看该组件被哪些模块引用，评估修改可能导致的连带影响。

---

## Phase 1：方案设计（Design Document）

在动手改代码前，必须输出一份简要的技术设计方案：

1. **设计模式选择**：说明将使用什么模式（如 Factory, Observer, Strategy）。
2. **接口定义**：列出新增或修改的函数签名。
3. **任务拆分**：使用 `TaskCreate` 将大任务拆解为原子任务（如：1. 数据模型定义 -> 2. 逻辑实现 -> 3. 单元测试）。

---

## Phase 2：编码实现循环（Implementation Loop）

**核心原则：小步快跑，原子提交。**

```
for each sub_task in tasks:
  TaskUpdate(sub_task.id, status: "in_progress")

  ── Step A: 骨架构建 ──
  编写接口、定义抽象类或 Model 层。

  ── Step B: 逻辑填充 ──
  实现业务逻辑。遵循 SOLID 原则，注释清晰。

  ── Step C: 静态检查 ──
  运行对应的静态分析工具（如 `dart analyze`, `eslint`, `mypy`, `go vet`）。
  如果有 Error/Warning，必须在当前循环修复，不得累积。
```

---

## Phase 3：测试驱动与验证（Verification）

**严禁仅靠运行一次 App 没报错就宣称成功。**

### 3A：编写单元测试
- 针对修改的逻辑编写 `Unit Test`。
- 覆盖正常路径（Happy Path）和异常路径（Edge Cases）。

### 3B：自动化运行与断言
- 执行测试命令：`pytest` / `flutter test` / `npm test`。
- **必须输出测试覆盖率报告**（如果项目支持）。

### 3C：日志监控（针对运行时逻辑）
- 如果是异步或长链路逻辑，必须通过 `Bash` 监控实时日志（如 `tail -f` 或 `app_logs`），确保没有隐藏的内存泄露或异常堆栈。

---

## Phase 4：对比修复循环（REPEAT 模式）

如果测试失败，进入修复循环，**最多 5 轮**：

| 轮次 | 错误现象 | 原因分析 | 修复方案 | 验证结果 |
|---|---|---|---|---|
| R1 | `NullPointer` | 缺少空安全处理 | 增加 `?` 或 `if null` 校验 | 通过 |

---

## Phase 5：交付与文档输出

输出一份标准的工程师交付报告：

```markdown
# 技术交付报告

**任务描述:** [Brief description]
**技术栈:** [Language/Framework]

## 实现明细
| 模块 | 修改说明 | 设计决策 |
|---|---|---|
| Domain | 新增 UserInfo Entity | 采用不可变模型确保线程安全 |
| Service | 接入重试机制 | 应对不稳定的第三方接口 |

## 质量保证 (QA)
- [x] 静态分析通过 (No Linter Warnings)
- [x] 单元测试覆盖率: 85%
- [x] 边界测试: 模拟网络 404/500 场景已处理

## 待办事项/风险
- [ ] 性能风险: 数据量超过 10k 时需增加分页逻辑。
```

---

## 异常处理与恢复逻辑

1. **代码冲突**：如果修改导致了大面积 `Analyze Error`，必须回滚至上一个 Git 提交（或使用备份文件恢复）。
2. **环境崩溃**：
   - 检查依赖：运行 `npm install` / `flutter pub get`。
   - 重新构建：运行项目特有的 `generate` 脚本。
3. **逻辑死循环**：如果 Agent 连续 3 轮无法修复同一个 Bug，必须主动停止并 `AskUserQuestion` 请求人工介入，禁止陷入无意义的代码重试。

---

## 注意事项

- **命名规范**：严格遵守项目既有的命名风格（CamelCase, snake_case 等）。
- **注释质量**：复杂的正则、数学算法或 Hack 逻辑必须附带详细注释。
- **安全性**：禁止将 API Key、密码等硬编码在代码中，必须使用环境变量或 `.env` 文件。
- **国际化**：UI 字符串严禁硬编码，必须放入 `.arb` 或 `i18n` 资源文件。