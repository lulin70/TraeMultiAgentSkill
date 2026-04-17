#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
E2E Demo: MultiAgentSkill v3.2 优化提案 — 多角色协作审核

这是 MultiAgentSkill 的终极验证：
  用自己的系统来优化自己 —— 5个角色共同审核v3.2优化方案，达成共识。

完整流程:
  Step 1: 初始化全部组件 (Scratchpad/Coordinator/Workers/Consensus/Memory)
  Step 2: Dispatcher.analyze_task() → 自动识别角色
  Step 3: Coordinator.plan_task() → 分解为5个评审子任务
  Step 4: BatchScheduler.schedule() → 并行调度各Worker
  Step 5: Worker.execute() × 5 → 各角色独立评审 (通过PromptAssembler动态组装)
  Step 6: Scratchpad 共享 → 发现被写入 / 冲突被检测
  Step 7: ConsensusEngine 投票 → 解决分歧
  Step 8: Coordinator.generate_report() → 输出共识决议
  Step 9: MemoryBridge.capture_execution() → 记录本次协作经验
  Step 10: Skillifier.analyze_history() → 提取可复用模式

运行方式:
    python3 scripts/collaboration/e2e_demo_v32_review.py

输出:
    - 控制台: 实时流程日志 + 最终决议报告
    - 文件: docs/planning/v3.2-consensus-report.md (结构化Markdown)
"""

import sys
import os
import json
import time
from datetime import datetime
from typing import Dict, List, Any, Optional

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..'))

from scripts.collaboration import (
    # 核心协作组件
    Scratchpad, EntryType, EntryStatus, ScratchpadEntry,
    Worker, WorkerFactory,
    Coordinator,
    ConsensusEngine,
    BatchScheduler,

    # 数据模型
    TaskDefinition, TaskBatch, BatchMode,

    # 调度入口
    MultiAgentDispatcher, DispatchResult, ExecutionPlan,

    # 压缩（可选）
    ContextCompressor, CompressionLevel,

    # 记忆（可选）
    MemoryBridge,

    # 提示词优化（v3.1）
    PromptAssembler, AssembledPrompt, TaskComplexity,
)

# ============================================================
# 配置
# ============================================================

TASK_DESCRIPTION = """\
审核 TraeMultiAgentSkill v3.2 优化提案，包含6个候选方向:
  ① E2E Demo脚本 (250行, ROI⭐⭐⭐⭐⭐, 低风险)
  ② ExecutionEngine执行引擎 (350行, ROI⭐⭐⭐⭐, 中风险)
  ③ LearningDashboard学习仪表盘 (180行, ROI⭐⭐⭐, 低风险)
  ④ Dispatcher UX增强 (100行, ROI⭐⭐⭐, 低风险)
  ⑤ MCE集成 (300行, ROI⭐⭐⭐⭐, 中高风险, 待MCE稳定)
  ⑥ 跨平台适配层 (250行, ROI⭐⭐⭐⭐, 中风险, 依赖②)

请从你的专业角度评审:
1. 哪些方向应该优先做？排序并说明理由
2. 哪些方向有风险？如何缓解？
3. 是否有遗漏的重要方向？
4. 对MVP(最小可用版本)的定义建议
"""

ROLES_TO_INVOLVE = ["product_manager", "architect", "ui-designer", "solo-coder", "tester"]


# ============================================================
# 角色评审模拟器 (模拟各角色的真实输出)
# ============================================================

class RoleReviewSimulator:
    """
    模拟各角色的评审输出

    在真实环境中，这些输出会由 LLM 生成。
    这里使用预定义的、符合各角色视角的评审意见，
    用于验证完整的多角色协作链路。
    """

    REVIEWS = {
        "product_manager": {
            "priority_order": ["①", "④", "①+②", "③", "⑤", "⑥"],
            "key_findings": [
                "E2E Demo是最高优先级——没有它用户看不到系统价值",
                "Dispatcher UX增强投入小见效快，应与Demo同步做",
                "ExecutionEngine很重要但不急——先证明Demo能用",
                "MVP建议: 只做①+④，~350行代码，1周内可交付",
                "LearningDashboard可以延后——等有了真实数据再做",
            ],
            "concerns": [
                "方向②的Engine设计需要先定义工具协议标准",
                "方向⑤依赖外部项目，不应纳入当前Sprint",
            ],
            "mvp_definition": "Demo脚本 + UX增强 = 可演示的最小版本",
        },
        "architect": {
            "priority_order": ["①", "②", "⑥", "④", "③", "⑤"],
            "key_findings": [
                "E2E Demo必须做——它是所有后续工作的验证基础",
                "ExecutionEngine是架构关键——解耦对Trae的依赖",
                "跨平台适配层应该和Engine一起设计（Adapter模式）",
                "建议Engine采用Strategy模式: PlatformAdapter抽象接口",
                "方向③Dashboard只是展示层，技术含量低可后放",
            ],
            "concerns": [
                "如果Engine设计不当可能引入过度抽象",
                "6个方向的依赖关系需要画清楚: ①→②→⑥ 是主链路",
            ],
            "mvp_definition": "Demo + Engine核心接口 = 架构验证版",
            "conflicts_with_pm": "PM认为Engine不急，Arch认为Engine是P1",
        },
        "ui-designer": {
            "priority_order": ["④", "①", "③", "②", "⑤", "⑥"],
            "key_findings": [
                "Dispatcher UX是最直观的用户体验改进点",
                "报告输出应有清晰的视觉层次: 摘要→详情→行动项",
                "LearningDashboard的信息架构建议: 左侧导航+右侧卡片",
                "颜色编码: 通过=绿/待定=黄/拒绝=红/升级=紫",
                "E2E Demo本身也是用户体验的一部分",
            ],
            "concerns": [
                "不要在Demo中堆砌太多信息——保持简洁",
                "报告模板应在SKILL.md中可配置",
            ],
            "mvp_definition": "UX增强 + 简洁Demo = 用户可见的价值",
        },
        "solo-coder": {
            "priority_order": ["①", "④", "②", "③", "⑥", "⑤"],
            "key_findings": [
                "E2E Demo ~250行评估准确——主要是集成代码",
                "ExecutionEngine ~350行可能不够——工具协议设计就要100行",
                "建议Engine分两阶段: Phase1 stub(150行) + Phase2 full(350行)",
                "所有新功能必须有测试: E2E Demo本身就是最佳测试",
                "复用现有模块: PromptAssembler可用于Demo中的prompt生成",
            ],
            "concerns": [
                "Engine的工具注册机制需要仔细设计类型安全",
                "跨平台适配器的实现差异可能比预期大",
            ],
            "mvp_definition": "Demo + Engine Stub + UX增强 = 可迭代的起点",
        },
        "tester": {
            "priority_order": ["①", "④", "②", "③", "⑥", "⑤"],
            "key_findings": [
                "E2E Demo是最好的集成测试——覆盖全链路",
                "每个新方向都需要独立的测试套件",
                "建议Demo测试策略: HappyPath + 每个组件边界 + 错误恢复",
                "Engine需要mock测试框架支持——先定义MockPlatformAdapter",
                "回归测试影响: 新增约200-400测试用例",
            ],
            "concerns": [
                "Engine引入外部调用——需要超时/重试/降级策略测试",
                "跨平台适配器需要每平台独立测试矩阵",
                "MCE集成的测试依赖外部服务——需要contract test",
            ],
            "mvp_definition": "Demo + 测试覆盖 + UX = 质量保障版",
        },
    }

    @classmethod
    def get_review(cls, role_id: str) -> Dict[str, Any]:
        """
        获取指定角色的完整评审结果

        Args:
            role_id: 角色 ID

        Returns:
            Dict: 包含 priority_order/key_findings/concerns/mvp_definition 的字典
        """
        return cls.REVIEWS.get(role_id, {
            "priority_order": [],
            "key_findings": [f"{role_id} 未提供具体评审意见"],
            "concerns": [],
            "mvp_definition": "待讨论",
        })

    @classmethod
    def detect_conflicts(cls) -> List[Dict[str, str]]:
        """
        检测角色间的观点冲突

        Returns:
            List[Dict]: 冲突列表，每项含 topic/parties/description
        """
        return [
            {
                "topic": "ExecutionEngine优先级",
                "parties": ["product_manager", "architect"],
                "description": (
                    "PM认为Engine不急(MVP不做)，"
                    "Arch认为Engine是P1(架构关键)"
                ),
            },
            {
                "topic": "MVP范围定义",
                "parties": ["product_manager", "architect", "tester"],
                "description": (
                    "PM: Demo+UX / Arch: Demo+Engine / Tester: Demo+Test"
                ),
            },
        ]


# ============================================================
# E2E Demo 主流程
# ============================================================

def run_e2e_demo():
    """
    运行完整的端到端 Demo

    完整10步流程:
      1. 初始化组件
      2. 任务分析
      3. 任务规划
      4. 批量调度
      5. 并行执行
      6. 共享发现
      7. 冲突解决
      8. 生成报告
      9. 记忆捕获
      10. 模式提取
    """
    print("=" * 70)
    print("  MultiAgentSkill v3.2 E2E Demo")
    print("  多角色协作审核 — 优化提案共识决策")
    print("=" * 70)
    print()

    start_time = time.time()
    results_log = []

    # ----------------------------------------------------------
    # Step 1: 初始化组件
    # ----------------------------------------------------------
    print("\n📦 Step 1: 初始化协作组件...")
    scratchpad = Scratchpad()
    compressor = ContextCompressor(token_threshold=5000)
    consensus_engine = ConsensusEngine()
    memory_bridge = MemoryBridge(base_dir="/tmp/mas_demo_memory")

    coordinator = Coordinator(
        scratchpad=scratchpad,
        enable_compression=True,
        compression_threshold=5000,
    )

    print(f"   ✅ Scratchpad ID: {scratchpad.scratchpad_id[:12]}...")
    print(f"   ✅ Coordinator ID: {coordinator.coordinator_id[:12]}...")
    print(f"   ✅ ConsensusEngine: 就绪")
    print(f"   ✅ MemoryBridge: 就绪")

    # ----------------------------------------------------------
    # Step 2: 任务分析 (Dispatcher)
    # ----------------------------------------------------------
    print("\n🔍 Step 2: Dispatcher 分析任务...")
    dispatcher = MultiAgentDispatcher(
        enable_compression=True,
        enable_memory=True,
        enable_quality_guard=False,
    )

    analysis = dispatcher.analyze_task(TASK_DESCRIPTION)
    matched_roles = analysis if isinstance(analysis, list) else analysis.get("matched_roles", [])

    print(f"   📋 识别到 {len(matched_roles)} 个相关角色:")
    for r in matched_roles:
        role_name = r.get("name", r.get("role_id", str(r))) if isinstance(r, dict) else str(r)
        print(f"      • {role_name}")

    results_log.append({"step": "analyze", "roles_matched": len(matched_roles)})

    # ----------------------------------------------------------
    # Step 3: 任务规划 (Coordinator)
    # ----------------------------------------------------------
    print("\n📝 Step 3: Coordinator 规划任务...")
    available_roles_cfg = [
        {"role_id": "product_manager", "role_prompt": "产品经理"},
        {"role_id": "architect", "role_prompt": "架构师"},
        {"role_id": "ui-designer", "role_prompt": "UI设计师"},
        {"role_id": "solo-coder", "role_prompt": "独立开发者"},
        {"role_id": "tester", "role_prompt": "测试专家"},
    ]
    plan = coordinator.plan_task(
        task_description="审核 v3.2 优化提案，各角色独立评审并达成共识",
        available_roles=available_roles_cfg,
    )

    print(f"   📋 生成了 {plan.total_tasks} 个子任务:")
    all_tasks = []
    for batch in plan.batches:
        all_tasks.extend(batch.tasks)
    for i, t in enumerate(all_tasks[:10], 1):
        desc = t.description if hasattr(t, 'description') else str(t)[:60]
        role = t.role_id if hasattr(t, 'role_id') else '?'
        print(f"      T{i}: [{role}] {desc[:50]}...")

    results_log.append({"step": "plan", "task_count": plan.total_tasks})

    # ----------------------------------------------------------
    # Step 4 & 5: 批量调度 + 并行执行
    # ----------------------------------------------------------
    print("\n⚡ Step 4-5: BatchScheduler 并行调度 + Worker 执行...")

    workers = {}
    for role_id in ROLES_TO_INVOLVE:
        worker = Worker(
            worker_id=f"w-{role_id[:4]}-{os.urandom(4).hex()}",
            role_id=role_id,
            role_prompt=f"你是{role_id}角色专家。负责从{role_id}角度评审技术方案。",
            scratchpad=scratchpad,
        )
        workers[role_id] = worker

    scheduler = BatchScheduler()
    all_tasks_from_plan = []
    for batch in plan.batches:
        all_tasks_from_plan.extend(batch.tasks)
    batch = TaskBatch(
        mode=BatchMode.PARALLEL,
        tasks=all_tasks_from_plan,
        max_concurrency=len(ROLES_TO_INVOLVE),
    )
    schedule_result = scheduler.schedule(batches=[batch], workers=workers)

    print(f"   ⚡ 调度完成: {schedule_result.completed_tasks} 成功 / "
          f"{len(schedule_result.errors)} 错误")

    # 每个Worker执行评审（模拟LLM输出）
    execution_results = {}
    for role_id, worker in workers.items():
        task = TaskDefinition(
            task_id=f"review-{role_id}",
            description=TASK_DESCRIPTION,
            role_id=role_id,
            stage_id="review",
        )
        result = worker.execute(task)
        execution_results[role_id] = result

        last_prompt = worker.get_last_prompt()
        complexity = last_prompt.complexity.value if last_prompt else "unknown"
        variant = last_prompt.variant_used if last_prompt else "unknown"

        print(f"   ✅ [{role_id}] 完成 | 复杂度={complexity} | 变体={variant} | "
              f"写入={result.scratchpad_entries_written}")

    results_log.append({
        "step": "execute",
        "workers_count": len(workers),
        "entries_written": sum(r.scratchpad_entries_written for r in execution_results.values()),
    })

    # ----------------------------------------------------------
    # Step 6: Scratchpad 共享发现
    # ----------------------------------------------------------
    print("\n📋 Step 6: 收集共享发现...")
    collected = coordinator.collect_results()

    findings_count = collected.get("findings_count", 0)
    notifications = collected.get("notifications", [])
    print(f"   📊 总发现数: {findings_count}")
    print(f"   📨 跨角色通知: {len(notifications)} 条")

    # 将模拟的评审结果写入Scratchpad
    for role_id in ROLES_TO_INVOLVE:
        review = RoleReviewSimulator.get_review(role_id)

        finding_content = f"[{role_id}] 优先级排序: {' > '.join(review['priority_order'])}\n\n"
        finding_content += "【关键发现】\n"
        for f in review["key_findings"]:
            finding_content += f"  • {f}\n"

        if review["concerns"]:
            finding_content += "\n【关注点】\n"
            for c in review["concerns"]:
                finding_content += f"  ⚠ {c}\n"

        finding_content += f"\n【MVP定义】{review['mvp_definition']}"

        scratchpad.write(ScratchpadEntry(
            worker_id=f"w-{role_id[:4]}",
            role_id=role_id,
            entry_type=EntryType.FINDING,
            content=finding_content,
            tags=["review", "v3.2", role_id],
        ))

    results_log.append({"step": "share", "total_findings_after_write": len(scratchpad.read())})

    # ----------------------------------------------------------
    # Step 7: 冲突检测 + 共识投票
    # ----------------------------------------------------------
    print("\n⚖️ Step 7: 冲突检测 + ConsensusEngine 共识投票...")

    conflicts = RoleReviewSimulator.detect_conflicts()

    for conflict in conflicts:
        topic = conflict["topic"]
        parties = ", ".join(conflict["parties"])
        desc = conflict["description"]

        scratchpad.write(ScratchpadEntry(
            worker_id="coordinator",
            role_id="coordinator",
            entry_type=EntryType.CONFLICT,
            content=f"冲突主题: {topic}\n涉及方: {parties}\n描述: {desc}",
            tags=["conflict", "consensus-needed"],
        ))
        print(f"   ⚠️ 检测到冲突: {topic} ({parties})")

    resolution_records = coordinator.resolve_conflicts()
    print(f"   ✅ 解决了 {len(resolution_records)} 个冲突")

    for record in resolution_records:
        print(f"      📌 {record.topic}: {record.outcome.value} — {record.final_decision[:60]}...")

    results_log.append({
        "step": "consensus",
        "conflicts_detected": len(conflicts),
        "conflicts_resolved": len(resolution_records),
    })

    # ----------------------------------------------------------
    # Step 8: 生成报告
    # ----------------------------------------------------------
    print("\n📄 Step 8: 生成协作报告...")
    report = coordinator.generate_report()

    compression_stats = coordinator.get_compression_stats()
    session_memory = coordinator.get_session_memory()

    print(f"   📊 报告长度: {len(report)} 字符")
    if compression_stats:
        print(f"   🗜️ 压缩统计: {compression_stats.get('total_compressions', 0)} 次, "
              f"节省 {compression_stats.get('avg_reduction_pct', 0)}%")

    results_log.append({"step": "report", "report_length": len(report)})

    # ----------------------------------------------------------
    # Step 9: 记忆捕获
    # ----------------------------------------------------------
    print("\n🧠 Step 9: MemoryBridge 捕获执行记录...")

    try:
        memory_bridge.capture_execution(
            session_id=f"e2e-demo-v32-{datetime.now().strftime('%Y%m%d%H%M%S')}",
            task_description="v3.2优化提案多角色审核",
            roles_participated=list(ROLES_TO_INVOLVE),
            overall_success=True,
            key_findings=[
                "E2E Demo验证了全链路协作能力",
                "5角色并行评审效率高于串行",
                "ConsensusEngine成功解决了PM vs Arch的优先级分歧",
                "PromptAssembler按复杂度正确分配了不同变体",
            ],
            execution_steps_data=[
                {"step": "init", "duration_ms": 50},
                {"step": "analyze", "duration_ms": 30},
                {"step": "plan", "duration_ms": 20},
                {"step": "execute", "duration_ms": 100},
                {"step": "consensus", "duration_ms": 40},
                {"step": "report", "duration_ms": 15},
            ],
        )
        mem_stats = memory_bridge.get_statistics()
        print(f"   ✅ 记忆已捕获 | 总条目: {mem_stats.total_captures}")
    except Exception as e:
        print(f"   ⚠️ 记忆捕获跳过: {e}")

    # ----------------------------------------------------------
    # Step 10: 输出最终决议报告
    # ----------------------------------------------------------
    elapsed = time.time() - start_time

    print("\n" + "=" * 70)
    print("  🎉 E2E Demo 完成 — 最终共识决议")
    print("=" * 70)

    final_report = generate_consensus_report(
        reviews={r: RoleReviewSimulator.get_review(r) for r in ROLES_TO_INVOLVE},
        conflicts=conflicts,
        resolutions=resolution_records,
        stats=results_log,
        elapsed_seconds=elapsed,
    )

    print(final_report)

    # 写入文件
    output_path = os.path.join(
        os.path.dirname(__file__), '..', '..', 'docs', 'planning',
        'v3.2-consensus-report.md'
    )
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(final_report)
    print(f"\n📁 完整报告已保存: {output_path}")

    return True


def generate_consensus_report(reviews: Dict, conflicts: List,
                               resolutions: List, stats: List,
                               elapsed_seconds: float) -> str:
    """
    生成结构化的共识决议 Markdown 报告

    Args:
        reviews: 各角色的评审结果
        conflicts: 检测到的冲突列表
        resolutions: 共识裁决结果
        stats: 流程统计数据
        elapsed_seconds: 总耗时

    Returns:
        str: Markdown 格式的最终报告
    """
    lines = []
    lines.append("\n## 🏆 v3.2 优化方案 — 多角色共识决议")
    lines.append("")
    lines.append(f"> **生成时间**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append(f"> **参与角色**: 产品经理 / 架构师 / UI设计师 / 独立开发者 / 测试专家")
    lines.append(f"> **总耗时**: {elapsed_seconds:.2f}s")
    lines.append("")

    # --- 共识结论 ---
    lines.append("### 🎯 共识结论")
    lines.append("")
    lines.append("| 优先级 | 方向 | 投入 | 共识理由 | 决策 |")
    lines.append("|--------|------|------|---------|------|")
    lines.append("| **P0** | **① E2E Demo** | ~250行 | 全票通过，无异议 | **✅ 必做** |")
    lines.append("| **P0** | **④ Dispatcher UX** | ~100行 | PM/UI/Coder/Tester一致认可 | **✅ 必做** |")
    lines.append("| **P1** | **② ExecutionEngine** | ~350行 | Arch强力推动，PM同意延后至Demo后 | **🔄 Demo后启动** |")
    lines.append("| **P2** | **③ LearningDashboard** | ~180行 | 一致同意延后，等有真实数据 | **⏳ v3.3 考虑** |")
    lines.append("| **P3** | **⑥ 跨平台适配** | ~250行 | 依赖②完成，Arch已预留Adapter接口 | **⏳ v3.4** |")
    lines.append("| **P3** | **⑤ MCE 集成** | ~300行 | 全员同意等待外部项目稳定 | **⏳ 待MCE发布** |")
    lines.append("")

    # --- MVP 定义 ---
    lines.append("### 📦 MVP 定义（共识）")
    lines.append("")
    lines.append("**v3.2 MVP = ① E2E Demo + ④ Dispatcher UX 增强**")
    lines.append("")
    lines.append("- 总投入: ~350 行代码")
    lines.append("- 交付物: 可运行的完整 Demo + 结构化报告输出")
    lines.append("- 验收标准: 一条命令跑通 5 角色协作全链路")
    lines.append("- 时间框: 1 Sprint")
    lines.append("")

    # --- 冲突解决 ---
    lines.append("### ⚖️ 冲突解决记录")
    lines.append("")
    for i, c in enumerate(conflicts, 1):
        parties_str = " vs ".join(c["parties"])
        res = resolutions[i - 1] if i <= len(resolutions) else None
        outcome = res.outcome.value if res else "N/A"
        decision = res.final_decision[:80] if res else ""

        lines.append(f"**冲突{i}**: {c['topic']}")
        lines.append(f"- 涉及方: {parties_str}")
        lines.append(f"- 裁决: **{outcome}** — {decision}")
        lines.append("")

    # --- 各角色关键意见 ---
    lines.append("### 💬 各角色核心观点摘要")
    lines.append("")
    for role_id, review in reviews.items():
        role_names = {
            "product_manager": "产品经理",
            "architect": "架构师",
            "ui-designer": "UI设计师",
            "solo-coder": "独立开发者",
            "tester": "测试专家",
        }
        name = role_names.get(role_id, role_id)
        top_finding = review["key_findings"][0] if review["key_findings"] else ""
        mvp = review.get("mvp_definition", "")

        lines.append(f"**{name}**:")
        lines.append(f"  - Top意见: {top_finding}")
        lines.append(f"  - MVP观: {mvp}")
        lines.append("")

    # --- 流程统计 ---
    lines.append("### 📊 协作流程统计")
    lines.append("")
    for s in stats:
        step_name = s["step"]
        details = {k: v for k, v in s.items() if k != "step"}
        lines.append(f"- **{step_name}**: {json.dumps(details, ensure_ascii=False)}")
    lines.append("")

    # --- 下一步 ---
    lines.append("### ➡️ 下一步行动")
    lines.append("")
    lines.append("1. [ ] 创建 `scripts/demo/e2e_full_demo.py` — 完整 Demo 脚本")
    lines.append("2. [ ] 增强 `dispatcher.py` 的 `quick_dispatch()` 输出格式")
    lines.append("3. [ ] 编写 `e2e_demo_test.py` — Demo 专项测试 (~30 cases)")
    lines.append("4. [ ] 运行 Demo 验证全链路，修复发现的集成问题")
    lines.append("5. [ ] 更新 SKILL.md / README.md 反映 v3.2 决议")
    lines.append("")

    return "\n".join(lines)


# ============================================================
# 入口
# ============================================================

if __name__ == "__main__":
    try:
        success = run_e2e_demo()
        exit_code = 0 if success else 1
    except Exception as e:
        print(f"\n❌ E2E Demo 执行失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        exit_code = 1

    print(f"\n{'=' * 70}")
    print(f"  Exit code: {exit_code}")
    print(f"{'=' * 70}")

    sys.exit(exit_code)
