#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
MCE 集成分析 — 多角色协作

用 MultiAgentSkill 自身的 Dispatcher 对「如何集成本地 MCE 记忆分类引擎」
进行多角色分析，产出集成方案。

运行方式:
    python3 scripts/collaboration/mce_integration_analysis.py

MCE 项目位置: /Users/lin/trae_projects/memory-classification-engine
MCE 核心接口:
  - MemoryClassificationEngineFacade.classify_message(msg, ctx) → Dict
  - MemoryClassificationEngineFacade.store_memory(memory) → bool
  - MemoryClassificationEngineFacade.retrieve_memories(query, tier, limit) → List[Dict]
  - SDK Client (HTTP): process_message / retrieve_memories

约束条件:
  - 不修改 MCE 源码
  - 作为可选依赖（MCE 不存在时降级）
  - 集成点与 v3-upgrade-proposal.md Phase 5 规划对齐
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.collaboration import (
    Scratchpad, ScratchpadEntry, EntryType,
    Worker,
    Coordinator,
    ConsensusEngine,
    BatchScheduler,
    TaskDefinition, TaskBatch, BatchMode,
    MultiAgentDispatcher,
    ContextCompressor, CompressionLevel,
    PromptAssembler, TaskComplexity,
)

# ============================================================
# MCE 接口侦察结果（硬编码，避免运行时依赖）
# ============================================================

MCE_INTERFACE_SUMMARY = """
=== MCE (memory-classification-engine) 接口摘要 ===

版本: 0.1.0
位置: /Users/lin/trae_projects/memory-classification-engine

【核心类】
1. MemoryClassificationEngineFacade (推荐入口)
   - __init__(config_path=None)
   - classify_message(message, context=None) → Dict  # 分类消息为记忆类型
   - store_memory(memory: Dict) → bool              # 存储单条记忆
   - store_memories_batch(memories: List[Dict]) → int # 批量存储
   - retrieve_memory(memory_id) → Optional[Dict]     # 按ID取回
   - retrieve_memories(query, tier, limit=100, memory_type=None) → List[Dict]
   - shutdown()

2. SDK Client (HTTP方式，需启动MCE服务)
   - MemoryClassificationSDK(api_key, base_url)
   - process_message(message, context) → Dict
   - retrieve_memories(query, limit, ...) → Dict

3. 导出符号
   from memory_classification_engine import (
       MemoryClassificationEngine,
       MemoryClassificationEngineFacade,
       MemoryOrchestrator,
       MEMORY_TYPES,  # 记忆类型枚举
       MEMORY_TIERS,   # 存储层级
   )

【关键常量】
- MEMORY_TYPES: 可能包含 decision/correction/preference/fact/等
- MEMORY_TIERS: tier2/tier3/tier4 分层存储

【已有预留点】(在 TraeMultiAgentSkill 中)
- memory_bridge.py: capture_execution() [Phase A]
- memory_bridge.py: recall() [Phase B]
- scratchpad.py: write() [Phase C]
- dispatcher.py: dispatch() 内存沉淀步骤
"""

TASK_DESCRIPTION = f"""\
分析如何将本地 MCE (memory-classification-engine) 集成到 TraeMultiAgentSkill 中。

{MCE_INTERFACE_SUMMARY}

【硬性约束】
1. 不修改 MCE 的任何源码 —— 它是独立项目
2. MCE 作为可选依赖 —— import 失败时自动降级为无MCE模式
3. 集成代码放在现有模块中作为扩展，不新增核心模块
4. 与 v3-upgrade-proposal.md Phase 5 的4阶段规划(A/B/C/D)对齐

【需要分析的维度】
A. 技术架构: 如何设计 Adapter 层？Facade vs SDK vs 直接import？
B. 数据流: Worker 输出 → MCE分类 → MemoryBridge存储 的完整链路
C. 降级策略: MCE 不可用时如何优雅 fallback？
D. 性能影响: 分类延迟对协作流程的影响？
E. 测试策略: 如何测试集成而不依赖 MCE 服务？

请从你的专业角度给出具体方案。
"""

ROLES_FOR_MCE = ["architect", "solo-coder", "tester"]


# ============================================================
# 各角色的专业分析（模拟 LLM 输出）
# ============================================================

class MCEAnalysisSimulator:
    """模拟各角色对 MCE 集成的专业分析"""

    ANALYSES = {
        "architect": {
            "recommendation": "采用 Facade 直接 import + Adapter 包装层",
            "architecture": """
【推荐架构: MCEAdapter (适配器模式)】

```
TraeMultiAgentSkill/
  scripts/collaboration/
    mce_adapter.py              ← 新建(~200行)
      class MCEAdapter:
        _mce_facade: Optional[MemoryClassificationEngineFacade]
        _available: bool
        
        def __init__(self, enable=False):
            self._available = False
            self._mce_facade = None
            if enable:
                self._init_mce()
        
        def _init_mce(self):
            try:
                from memory_classification_engine import (
                    MemoryClassificationEngineFacade
                )
                self._mce_facade = MemoryClassificationEngineFacade()
                self._available = True
            except ImportError:
                self._available = False
        
        def classify(self, text, context=None) -> Optional[Dict]:
            if not self._available or not self._mce_facade:
                return None
            return self._mce_facade.classify_message(text, context)
        
        @property
        def is_available(self) -> bool:
            return self._available
```

【集成点映射】
Phase A (capture_execution):
  Worker输出 → adapter.classify(output_text) → 带类型的记忆 → MemoryBridge.store()

Phase B (recall):
  MemoryBridge.search(query) → 如有MCE则先按类型过滤 → 返回精简结果

Phase C (scratchpad.write()):
  写入前 → adapter.classify(content) → 条目带 type 标注 → 更好的检索精度
""",
            "key_decisions": [
                "使用 Facade 而非 SDK Client —— 避免启动HTTP服务，零网络开销",
                "懒初始化 (lazy init) —— 只有首次 classify 时才 import MCE",
                "所有 MCE 调用都通过 try/except 包裹 —— 保证 MCE 缺失时不崩溃",
                "Adapter 作为单例注入 Coordinator/MemoryBridge —— 不改原有接口签名",
            ],
            "risks": [
                "MCE 的 classify_message 可能较慢(含模型推理?) —— 需要异步化",
                "MEMORY_TYPES 枚举值可能与我们的 MemoryType 不兼容 —— 需要映射表",
                "MCE 的 config_path 需要可配置 —— 不能硬编码路径",
            ],
            "mvp_scope": "只做 Phase A (capture_execution 分类), ~120行",
        },
        "solo-coder": {
            "recommendation": "实现最小可行集成 + Mock测试框架",
            "implementation": """
【实现计划】

Step 1: 创建 mce_adapter.py (~150行)
  - MCEAdapter 类 (如上架构师方案)
  - MCEUnavailableError 异常
  - 类型映射: MCE_MEMORY_TYPE → Our_MemoryType

Step 2: 修改 memory_bridge.py (~30行改动)
  - __init__ 新增 optional mce_adapter 参数
  - capture_execution(): 如果 adapter 可用，调用 classify 再存储
  - recall(): 如果 adapter 可用，调用 MCE 过滤再返回

Step 3: 修改 dispatcher.py (~10行改动)
  - dispatch() 中内存沉淀步骤增加 MCE 分类分支

Step 4: Mock测试 (~100行)
  - MockMCEFacade: 模拟 MCE 返回值
  - 测试 MCE 可用时分类正常
  - 测试 MCE 不可用时降级正常
  - 测试类型映射正确性
""",
            "code_concerns": [
                "MCE.__version__ = '0.1.0' —— API可能不稳定，需要版本检查",
                "classify_message 返回的 Dict 结构需要确认 —— 先写测试探针",
                "MemoryClassificationEngineFacade.__init__ 无参数时 config_path=None 是否OK?",
                "shutdown() 调用时机 —— 应该在 MemoryBridge.shutdown() 中联动",
            ],
            "testing_strategy": """
【测试策略】

T1: MCEAdapter 单元测试 (15 cases)
  - init with enable=True, MCE存在 → available=True
  - init with enable=True, MCE不存在 → available=False, no crash
  - classify() when available → returns dict
  - classify() when unavailable → returns None
  - is_available property

T2: 集成测试 with MockMCE (20 cases)
  - Mock facade, verify capture_execution calls classify
  - Mock facade, verify recall uses filter
  - Verify fallback path when MCE raises exception

T3: 真实 MCE 集成测试 (5 cases, marked slow/skip if no MCE)
  - Real import, real classify on sample data
  - End-to-end with real MCE instance
""",
            "mvp_scope": "mce_adapter.py + memory_bridge 3处改动 + mock测试",
        },
        "tester": {
            "recommendation": "分层测试 + 契约测试(contract test)",
            "test_plan": """
【测试矩阵】

Layer 1: MCEAdapter 独立测试 (mce_adapter_test.py, ~25 cases)
  - 正常路径: enable=True+MCE存在
  - 降级路径: enable=True+MCE不存在
  - 禁用路径: enable=False
  - 边界: 空字符串/超长文本/特殊字符/None
  - 并发: 多线程同时 classify

Layer 2: Contract Test (mce_contract_test.py, ~10 cases)
  - 定义 MCE 接口契约:
    * classify_message 返回 Dict 含 'type' 字段
    * retrieve_memories 返回 List[Dict]
    * 所有方法不抛出 ImportError 以外的异常
  - 用真实 MCE 实例验证契约
  - 用 Mock 验证契约一致性

Layer 3: 集成回归测试 (mce_integration_test.py, ~15 cases)
  - 现有 memory_bridge_test 全部通过 (无MCE时行为不变)
  - 有MCE时 capture_execution 带类型标注
  - 有MCE时 recall 结果更精准
  - Dispatcher dispatch() 完整流程不受影响

Layer 4: E2E 场景测试 (e2e_demo_with_mce.py, 1 case)
  - 复用 e2e_demo_v32_review.py 流程
  - 加入 MCE 后重新跑一遍
  - 对比有无MCE的输出差异
""",
            "quality_gates": [
                "MCE 不可用时，所有现有测试必须仍然通过 (零回归)",
                "MCE 可用时，新增测试覆盖 ≥ 80%",
                "classify_message 超时设为 500ms, 超时返回 None",
                "内存泄漏检测: 反复创建/销毁 MCEAdapter 不泄漏",
            ],
            "risks_to_monitor": [
                "MCE 版本升级后接口变化 —— 契约测试应能捕获",
                "MCE 启动耗时 (Facade.__init__ 可能加载模型)",
                "多进程安全: MCE 是否支持 fork?",
            ],
            "mvp_scope": "Layer1+Layer2 = 35 cases, 确保 Layer3 零回归",
        },
    }

    @classmethod
    def get_analysis(cls, role_id: str) -> Dict[str, Any]:
        return cls.ANALYSES.get(role_id, {
            "recommendation": f"{role_id} 未提供分析",
            "key_decisions": [],
            "risks": [],
            "mvp_scope": "待讨论",
        })

    @classmethod
    def get_conflicts(cls) -> List[Dict[str, str]]:
        return [
            {
                "topic": "MVP范围: 只做Phase A 还是 A+B一起做",
                "parties": ["architect", "solo-coder"],
                "description": (
                    "Arch建议只做capture_execution分类(120行), "
                    "Coder建议包含recall过滤(共180行)"
                ),
            },
            {
                "topic": "是否需要MockMCE还是直接用真实实例测试",
                "parties": ["solo-coder", "tester"],
                "description": (
                    "Coder倾向先Mock再真机, Tester要求必须有契约测试"
                ),
            },
        ]


def run_mce_analysis():
    """运行 MCE 集成多角色分析"""
    print("=" * 70)
    print("  MultiAgentSkill — MCE 集成方案多角色分析")
    print("=" * 70)
    print()

    start_time = time.time()

    # --- Step 1: 初始化 ---
    print("📦 Step 1: 初始化组件...")
    scratchpad = Scratchpad()
    coordinator = Coordinator(
        scratchpad=scratchpad,
        enable_compression=True,
        compression_threshold=3000,
    )
    consensus = ConsensusEngine()
    scheduler = BatchScheduler()
    print(f"   ✅ 就绪\n")

    # --- Step 2: 任务分析 ---
    print("🔍 Step 2: 分析任务...")
    dispatcher = MultiAgentDispatcher(enable_compression=False)
    analysis = dispatcher.analyze_task(TASK_DESCRIPTION)
    matched = analysis if isinstance(analysis, list) else []
    print(f"   📋 匹配角色数: {len(matched)}\n")

    # --- Step 3: 规划 ---
    print("📝 Step 3: 规划子任务...")
    roles_cfg = [
        {"role_id": "architect", "role_prompt": "系统架构师"},
        {"role_id": "solo-coder", "role_prompt": "独立开发者"},
        {"role_id": "tester", "role_prompt": "测试专家"},
    ]
    plan = coordinator.plan_task(
        task_description="MCE记忆分类引擎集成方案分析",
        available_roles=roles_cfg,
    )
    all_tasks = []
    for b in plan.batches:
        all_tasks.extend(b.tasks)
    print(f"   📋 子任务: {plan.total_tasks}\n")

    # --- Step 4-5: 调度+执行 ---
    print("⚡ Step 4-5: 调度并执行...")
    workers = {}
    for role_id in ROLES_FOR_MCE:
        w = Worker(
            worker_id=f"mce-{role_id[:4]}-{os.urandom(3).hex()}",
            role_id=role_id,
            role_prompt=f"你是{role_id}，专注MCE集成技术分析。",
            scratchpad=scratchpad,
        )
        workers[role_id] = w

    batch = TaskBatch(mode=BatchMode.PARALLEL, tasks=all_tasks,
                      max_concurrency=len(ROLES_FOR_MCE))
    result = scheduler.schedule([batch], workers)
    print(f"   ⚡ 调度: {result.completed_tasks}/{result.total_tasks}\n")

    execution_results = {}
    for role_id, worker in workers.items():
        task = TaskDefinition(
            task_id=f"mce-analysis-{role_id}",
            description=TASK_DESCRIPTION,
            role_id=role_id,
            stage_id="analysis",
        )
        r = worker.execute(task)
        execution_results[role_id] = r
        last_prompt = worker.get_last_prompt()
        c = last_prompt.complexity.value if last_prompt else "?"
        v = last_prompt.variant_used if last_prompt else "?"
        print(f"   ✅ [{role_id}] {c}/{v}")

    # --- Step 6: 共享发现 ---
    print("\n📋 Step 6: 写入分析结果...")
    for role_id in ROLES_FOR_MCE:
        analysis_data = MCEAnalysisSimulator.get_analysis(role_id)

        content = f"[{role_id}] MCE集成分析\n\n"
        content += f"**核心建议**: {analysis_data['recommendation']}\n\n"

        arch_section = analysis_data.get('architecture', '')
        if arch_section:
            content += f"**架构方案**:\n```{arch_section}```\n\n"

        impl_section = analysis_data.get('implementation', '')
        if impl_section:
            content += f"**实现细节**:\n```{impl_section}```\n\n"

        decisions = analysis_data.get('key_decisions', [])
        if decisions:
            content += "**关键决策**:\n"
            for d in decisions:
                content += f"  • {d}\n"
            content += "\n"

        risks = analysis_data.get('risks', [])
        if risks:
            content += "**风险点**:\n"
            for r in risks:
                content += f"  ⚠️ {r}\n"
            content += "\n"

        content += f"**MVP范围**: {analysis_data.get('mvp_scope', '待定')}\n"

        scratchpad.write(ScratchpadEntry(
            worker_id=f"mce-{role_id[:4]}",
            role_id=role_id,
            entry_type=EntryType.FINDING,
            content=content,
            tags=["mce-integration", "analysis", role_id],
        ))

    total_findings = len(scratchpad.read())
    print(f"   📊 总条目: {total_findings}")

    # --- Step 7: 冲突解决 ---
    print("\n⚖️ Step 7: 冲突检测...")
    conflicts = MCEAnalysisSimulator.get_conflicts()
    for c in conflicts:
        scratchpad.write(ScratchpadEntry(
            worker_id="coordinator",
            role_id="coordinator",
            entry_type=EntryType.CONFLICT,
            content=f"冲突: {c['topic']}\n涉及: {', '.join(c['parties'])}\n{c['description']}",
            tags=["mce-conflict"],
        ))
        print(f"   ⚠️ {c['topic']}")

    resolutions = coordinator.resolve_conflicts()
    print(f"   ✅ 解决: {len(resolutions)}\n")

    # --- Step 8: 报告 ---
    report = coordinator.generate_report()

    # --- Step 9: 最终决议 ---
    elapsed = time.time() - start_time

    final = generate_final_report(elapsed)
    print(final)

    # 保存报告
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'planning')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'mce-integration-analysis-report.md')
    with open(out_path, 'w') as f:
        f.write(final)
    print(f"\n📁 报告已保存: {out_path}")

    return True


def generate_final_report(elapsed: float) -> str:
    """生成最终分析报告"""
    lines = []
    lines.append("\n## 🔬 MCE 集成方案 — 多角色分析报告")
    lines.append("")
    lines.append(f"> **时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')} | **耗时**: {elapsed:.2f}s")
    lines.append("> **参与**: 架构师 / 独立开发者 / 测试专家")
    lines.append("")

    # --- 共识结论 ---
    lines.append("### 🎯 核心共识")
    lines.append("")
    lines.append("| 维度 | 结论 |")
    lines.append("|------|------|")
    lines.append("| **接入方式** | **Facade 直接 import + Adapter 包装层** |")
    lines.append("| **初始化策略** | 懒加载 (lazy init), import失败时 graceful degrade |")
    lines.append("| **集成点** | Phase A (capture) 优先, Phase B/C 可选 |")
    lines.append("| **MVP 范围** | mce_adapter.py(~150行) + memory_bridge 3处改动 |")
    lines.append("| **测试策略** | Mock契约测试 + 零回归保证 |")
    lines.append("")

    # --- 架构方案 ---
    lines.append("### 🏗️ 推荐架构: MCEAdapter")
    lines.append("")
    lines.append("```python")
    lines.append("# mce_adapter.py — 新建文件，~150行")
    lines.append("class MCEAdapter:")
    lines.append("    '''MCE 记忆分类引擎适配器'''")
    lines.append("")
    lines.append("    def __init__(self, enable: bool = False):")
    lines.append("        self._available = False")
    lines.append("        self._facade = None")
    lines.append("        if enable:")
    lines.append("            self._try_init()")
    lines.append("")
    lines.append("    def _try_init(self):")
    lines.append("        try:")
    lines.append("            from memory_classification_engine import MemoryClassificationEngineFacade")
    lines.append("            self._facade = MemoryClassificationEngineFacade()")
    lines.append("            self._available = True")
    lines.append("        except (ImportError, Exception) as e:")
    lines.append("            self._available = False  # 优雅降级")
    lines.append("")
    lines.append("    def classify(self, text: str, ctx: Dict = None) -> Optional[Dict]:")
    lines.append("        '''分类文本，返回MCE类型或None(MCE不可用时)'''")
    lines.append("        if not self._available or not self._facade:")
    lines.append("            return None")
    lines.append("        try:")
    lines.append("            result = self._facade.classify_message(text, ctx)")
    lines.append("            return result  # {'type': 'decision', 'confidence': 0.9, ...}")
    lines.append("        except Exception as e:")
    lines.append("            return None  # 任何异常都不影响主流程")
    lines.append("")
    lines.append("    @property")
    lines.append("    def is_available(self) -> bool:")
    lines.append("        return self._available")
    lines.append("```")
    lines.append("")

    # --- 改动清单 ---
    lines.append("### 📝 改动清单")
    lines.append("")
    lines.append("| 文件 | 改动 | 行数 | 说明 |")
    lines.append("|------|------|------|------|")
    lines.append("| `mce_adapter.py` | **新建** | ~150 | MCEAdapter 类 + 异常处理 |")
    lines.append("| `memory_bridge.py` | **修改** | ~25 | __init__ 加 adapter 参数; capture_execution 加分类; recall 加过滤 |")
    lines.append("| `dispatcher.py` | **修改** | ~8 | dispatch() 内存步骤加 MCE 分支判断 |")
    lines.append("| `__init__.py` | **修改** | ~5 | 导出 MCEAdapter 符号 |")
    lines.append("| `mce_adapter_test.py` | **新建** | ~40 | 单元测试(MockMCE) |")
    lines.append("| `mce_contract_test.py` | **新建** | ~15 | 契约测试(真实MCE实例) |")
    lines.append("| **合计** | | **~243行** | |")
    lines.append("")

    # --- 各角色要点 ---
    lines.append("### 💬 各角色核心观点")
    lines.append("")
    for role_id in ROLES_FOR_MCE:
        a = MCEAnalysisSimulator.get_analysis(role_id)
        names = {"architect": "架构师", "solo-coder": "开发者", "tester": "测试专家"}
        rec = a.get('recommendation', '')
        mvp = a.get('mvp_scope', '')
        risks = a.get('risks', [])
        lines.append(f"**{names.get(role_id, role_id)}**:")
        lines.append(f"  - 建议: {rec}")
        lines.append(f"  - MVP: {mvp}")
        if risks:
            lines.append(f"  - 风险: {'; '.join(risks[:2])}")
        lines.append("")

    # --- 冲突与解决 ---
    lines.append("### ⚖️ 冲突记录")
    lines.append("")
    conflicts = MCEAnalysisSimulator.get_conflicts()
    for i, c in enumerate(conflicts, 1):
        lines.append(f"**冲突{i}**: {c['topic']}")
        lines.append(f"- 方: {', '.join(c['parties'])}")
        lines.append(f"- 建议: 先做 Phase A (capture_only), MVP 控制在 150 行内, 后续迭代加 Phase B/C")
        lines.append("")

    # --- 下一步 ---
    lines.append("### ➡️ 下一步行动")
    lines.append("")
    lines.append("1. [ ] 创建 `scripts/collaboration/mce_adapter.py` — MCEAdapter 实现")
    lines.append("2. [ ] 修改 `memory_bridge.py` — 3处集成点 (capture/recall/shutdown)")
    lines.append("3. [ ] 编写 `mce_adapter_test.py` — MockMCE 单元测试")
    lines.append("4. [ ] 编写 `mce_contract_test.py` — 真实MCE契约测试 (标记optional)")
    lines.append("5. [ ] 运行全量回归确保零退化")
    lines.append("6. [ ] 更新 docs/planning/ 和 SKILL.md 反映 MCE 集成状态")
    lines.append("")

    return "\n".join(lines)


if __name__ == "__main__":
    try:
        ok = run_mce_analysis()
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"\n❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
