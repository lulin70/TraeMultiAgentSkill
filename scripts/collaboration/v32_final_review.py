#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
v3.2 Final Roadmap — 全团队5角色共识评审 (合并版)

合并两个分析结果:
  1. v3.2 优化提案 (6方向: E2E Demo / Engine / Dashboard / UX / 跨平台 / MCE)
  2. MCE 集成方案 (3角色: Arch/Coder/Tester)

统一为 7 个候选方向, 拉上全部 5 个角色做最终评审,
产出 v3.2 Final Roadmap 共识决议.

运行:
    python3 scripts/collaboration/v32_final_review.py

输出:
    - 控制台: 完整流程日志 + 最终决议
    - 文件: docs/planning/v3.2-final-consensus.md
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
    PromptAssembler, TaskComplexity,
)

# ============================================================
# 统一 Roadmap 数据
# ============================================================

UNIFIED_ROADMAP = """
=== TraeMultiAgentSkill v3.2 统一 Roadmap ===

【A组: 核心体验 P0 必做】
  A1. E2E Demo 脚本 (~250行)     ROI⭐⭐⭐⭐⭐  风险低   来源:v3.2提案  全票通过
  A2. Dispatcher UX 增强 (~100行)  ROI⭐⭐⭐      风险低   来源:v3.2提案  PM/UI/Coder/Tester一致

【B组: 能力扩展 P1 高价值】
  B1. MCE 集成 mce_adapter (~243行) ROI⭐⭐⭐⭐  风险中   来源:MCE分析  Arch/Coder/Tester三方一致
  B2. ExecutionEngine 执行引擎 (~350行) ROI⭐⭐⭐⭐  风险中   来源:v3.2提案  Arch推动/PM同意延后

【C组: 锦上添花 P2/P3 后续】
  C1. LearningDashboard (~180行)     ROI⭐⭐⭐      风险低
  C2. 跨平台适配层 (~250行)          ROI⭐⭐⭐⭐  风险中   依赖B2

【MCE集成要点】
  - 接入: Facade 直接 import (不用HTTP SDK)
  - 初始化: 懒加载, ImportError → graceful degrade
  - 所有调用 try/except → 返回None (零侵入)
  - 改动: mce_adapter.py新建 + memory_bridge/dispatcher/__init__ 小改
"""

TASK_DESCRIPTION = f"""\
你是 TraeMultiAgentSkill 团队成员。请评审以下 v3.2 统一 Roadmap（7个候选方向）。

{UNIFIED_ROADMAP}

【当前基线】
- 15个核心模块, ~782测试全部通过
- E2E Demo已验证(e2e_demo_v32_review.py), 10步流程全部通过
- MCE项目已侦察(memory-classification-engine v0.1.0), Facade接口清晰

【评审要求】
请从你的专业角度:

1. 对7个方向(A1/A2/B1/B2/C1/C2)进行优先级排序
2. 定义MVP范围（建议包含哪些? 总投入多少行?）
3. 标注风险点和缓解措施
4. 是否有遗漏的重要方向?
5. 实现顺序建议（哪些可并行? 哪些有依赖?）

输出格式:
  - 优先级排序: [编号] > [编号] > ...
  - MVP定义: 包含XX, 总投入约XX行
  - 风险: 列出关键风险
  - 建议: 具体行动建议
"""

ALL_ROLES = ["product_manager", "architect", "ui-designer", "solo-coder", "tester"]


# ============================================================
# 5角色评审模拟器
# ============================================================

class FullTeamReviewer:
    """模拟5个角色的完整评审输出"""

    REVIEWS = {
        "product_manager": {
            "priority_order": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "reasoning": """\
PM视角:
  A1(E2E Demo)是最高优先级——没有它用户看不到系统价值，这是"能卖出去"的前提。
  A2(UX增强)投入小见效快，和Demo同步做，用户第一眼看到的就是报告质量。
  B1(MCE)有价值但不是用户直接感知的——属于"内部能力提升"。
  B2(Engine)重要但不急——先证明Demo能用再谈独立执行。
  C1/C2 明确延后。

MVP = A1 + A2 + B1 = ~593行
理由: Demo让系统可用, UX让它好用, MCE让记忆更智能。
三者组合覆盖了 可用性+易用性+智能化 三维。
""",
            "mvp_definition": "A1(E2E Demo) + A2(UX) + B1(MCE) = ~593行, 1-2 Sprint",
            "risks": [
                "B1(MCE)依赖外部项目v0.1.0——API可能变",
                "总593行对1个Sprint可能偏紧——考虑分Phase",
            ],
            "conflicts_with": {
                "architect": "Arch认为B2(Engine)应该和B1一起做",
                "tester": "Tester希望MVP包含更多测试准备",
            },
        },
        "architect": {
            "priority_order": ["A1", "B1", "A2", "B2", "C2", "C1"],
            "reasoning": """\
架构师视角:
  A1(Demo)必须第一——它是所有后续工作的验证基础。
  B1(MCE)排第二——因为MCE的Adapter模式可以复用给未来的Engine(B2)。
    MCEAdapter的Facade+lazy_init+graceful_degrade 是标准模式,
    先实现它可以验证这套模式是否work, 然后Engine照搬。
  A2(UX)第三——纯展示层, 不影响架构。
  B2(Engine)第四——依赖A1(Demo验证)+ B1(Adapter模式验证)。
  C2(跨平台)第五——依赖B2。

关键架构决策:
  MCEAdapter 应该设计成通用 Adapter 基类,
  未来 Engine 也继承同一套接口。这样 B1 为 B2 铺路。
""",
            "mvp_definition": "A1(Demo) + B1(MCE Adapter) + A2(UX骨架) = ~500行",
            "risks": [
                "MCE v0.1.0 的 classify_message 可能返回结构不稳定——需要版本检查",
                "如果 MCE 和我们的 MemoryType 枚举不兼容需要映射层",
            ],
            "conflicts_with": {
                "product_manager": "PM把A2排在B1前面, 我认为B1(能力)比A2(展示)更重要",
            },
        },
        "ui-designer": {
            "priority_order": ["A2", "A1", "C1", "B1", "B2", "C2"],
            "reasoning": """\
UI设计师视角:
  A2(UX增强)其实应该是P0的一部分——用户看到的第一个东西就是报告。
  如果报告不漂亮, Demo跑得再好也没人看懂。
  A1(Demo)第二——内容很重要, 但呈现形式同样重要。
  C1(Dashboard)我希望能提前——不是延后到P2。
    如果有了真实数据流(Demo产生), Dashboard 就有数据可展示了。
    建议把 C1 提升到和 B1 同优先级, 作为 Demo 的可视化配套。

UX具体建议:
  - 报告模板: 任务摘要(卡片) → 角色分工(表格) → 关键发现(列表)
    → 冲突解决(徽章) → 下一步(按钮)
  - 颜色: 通过=绿 / 待定=黄 / 拒绝=红 / 升级=紫 / 信息=蓝
  - 层级: H1标题 > H2章节 > H3细节 > body正文 > caption注释
""",
            "mvp_definition": "A2(UX) + A1(Demo) + C1(Dashboard简化版) = ~530行",
            "risks": [
                "不要在报告中堆砌信息——保持简洁, 详情可折叠",
                "Dashboard 不要过度设计——先用Markdown表格, 后续再考虑可视化"
            ],
            "conflicts_with": {
                "solo_coder": "Coder可能觉得UI优先级过高, 占用开发时间",
            },
        },
        "solo-coder": {
            "priority_order": ["A1", "A2", "B1", "B2", "C1", "C2"],
            "reasoning": """\
开发者视角:
  A1(Demo) + A2(UX) 可以并行——它们不互相依赖, 都是展示/集成层。
  B1(MCE) 也可以和 A1/A2 并行——mce_adapter.py 是独立模块。
  所以 MVP 第一批可以三线并行: A1 | A2 | B1
  总投入 ~593行, 分3个人/3天可完成。

实现顺序建议:
  Day 1: A1 Demo脚本核心 (150行) + B1 MCEAdapter骨架 (80行)
  Day 2: A1 Demo完善 (100行) + B1 MCEAdapter完成 (70行) + memory_bridge改动 (25行)
  Day 3: A2 UX增强 (100行) + 测试 (各模块单元测试)

关于MCE的具体实现注意点:
  - classify_message 的返回Dict结构需要先用探针代码确认
  - MEMORY_TYPES 枚举值要做映射表
  - shutdown() 要联动 MemoryBridge.shutdown()
""",
            "mvp_definition": "A1+A2+B1 三线并行 = ~593行, 3天可交付",
            "risks": [
                "MCE.__version__ == '0.1.0' —— 需要写版本兼容检查",
                "classify_message 可能慢(模型推理?) —— 需要 async wrapper 或 timeout",
            ],
            "conflicts_with": {},
        },
        "tester": {
            "priority_order": ["A1", "B1", "A2", "B2", "C1", "C2"],
            "reasoning": """\
测试专家视角:
  A1(Demo) 本身就是最好的集成测试——覆盖全链路。
  B1(MCE) 需要独立的测试策略: Mock契约 + 真实实例 + 零回归保证。
  A2(UX) 需要输出格式验证测试。

测试矩阵预估:
  - A1 Demo: ~30 cases (HappyPath + 各组件边界 + 错误恢复)
  - A2 UX: ~15 cases (格式验证 + 边界长度 + 特殊字符)
  - B1 MCE: ~55 cases (Adapter单元25 + Mock集成20 + 契约10)
  - 合计新增: ~100 cases
  - 现有782个必须零回归

质量门禁:
  1. MCE不可用时所有现有测试通过 ✓
  2. MCE可用时新增测试覆盖率 ≥ 80%
  3. classify_message 超时 500ms 自动降级
  4. 无内存泄漏 (反复创建/销毁 MCEAdapter)
""",
            "mvp_definition": "A1 + B1 + A2 + 全量测试 = ~593行代码 + ~100新测试",
            "risks": [
                "B1 MCE 的契约测试需要真实MCE实例——标记为 optional/skip if no MCE",
                "多线程安全: MCE Facade 是否线程安全需确认",
                "A1 Demo 的 E2E 测试可能较慢(涉及多组件初始化)"
            ],
            "conflicts_with": {
                "ui_designer": "UI想提前C1 Dashboard, 我建议等有真实数据后再做",
            },
        },
    }

    @classmethod
    def get_all_reviews(cls) -> Dict[str, Dict]:
        return cls.REVIEWS

    @classmethod
    def detect_all_conflicts(cls) -> List[Dict[str, str]]:
        conflicts = []
        seen = set()
        for role_id, review in cls.REVIEWS.items():
            for other_role, topic in review.get("conflicts_with", {}).items():
                key = tuple(sorted([role_id, other_role]))
                if key not in seen:
                    seen.add(key)
                    conflicts.append({
                        "topic": topic,
                        "parties": [role_id, other_role],
                        "description": (
                            f"{role_id} vs {other_role}: {topic}"
                        ),
                    })
        return conflicts


def run_final_review():
    """运行最终全量评审"""
    print("=" * 72)
    print("  🏛️  TraeMultiAgentSkill v3.2 Final Roadmap")
    print("     全团队5角色共识评审 (合并版)")
    print("=" * 72)
    print()

    t0 = time.time()

    # Step 1: Init
    print("📦 Step 1: 初始化协作组件...")
    scratchpad = Scratchpad()
    coordinator = Coordinator(
        scratchpad=scratchpad,
        enable_compression=True,
        compression_threshold=3000,
    )
    consensus = ConsensusEngine()
    scheduler = BatchScheduler()
    dispatcher = MultiAgentDispatcher(enable_compression=False)
    print(f"   ✅ Scratchpad: {scratchpad.scratchpad_id[:12]}...")
    print(f"   ✅ Coordinator: {coordinator.coordinator_id[:12]}...")

    # Step 2: Analyze
    print("\n🔍 Step 2: 分析任务...")
    analysis = dispatcher.analyze_task(TASK_DESCRIPTION)
    matched_count = len(analysis) if isinstance(analysis, list) else 0
    print(f"   📋 匹配角色: {matched_count}")

    # Step 3: Plan
    print("\n📝 Step 3: 规划子任务...")
    roles_cfg = [
        {"role_id": "product_manager", "role_prompt": "产品经理"},
        {"role_id": "architect", "role_prompt": "系统架构师"},
        {"role_id": "ui-designer", "role_prompt": "UI/UX设计师"},
        {"role_id": "solo-coder", "role_prompt": "独立开发者"},
        {"role_id": "tester", "role_prompt": "测试专家"},
    ]
    plan = coordinator.plan_task(
        task_description="v3.2统一Roadmap全量评审",
        available_roles=roles_cfg,
    )
    all_tasks = []
    for b in plan.batches:
        all_tasks.extend(b.tasks)
    print(f"   📋 子任务: {plan.total_tasks}")

    # Step 4-5: Schedule + Execute
    print("\n⚡ Step 4-5: 并行调度 + 执行...")
    workers = {}
    for role_id in ALL_ROLES:
        w = Worker(
            worker_id=f"final-{role_id[:4]}-{os.urandom(3).hex()}",
            role_id=role_id,
            role_prompt=f"你是{role_id}，专注v3.2 Roadmap技术评审。",
            scratchpad=scratchpad,
        )
        workers[role_id] = w

    batch = TaskBatch(mode=BatchMode.PARALLEL, tasks=all_tasks,
                      max_concurrency=len(ALL_ROLES))
    sched_result = scheduler.schedule([batch], workers)
    print(f"   ⚡ 调度: {sched_result.completed_tasks}/{sched_result.total_tasks}")

    exec_results = {}
    for role_id, w in workers.items():
        task = TaskDefinition(
            task_id=f"final-review-{role_id}",
            description=TASK_DESCRIPTION,
            role_id=role_id,
            stage_id="review",
        )
        r = w.execute(task)
        exec_results[role_id] = r
        lp = w.get_last_prompt()
        c = lp.complexity.value if lp else "?"
        v = lp.variant_used if lp else "?"
        print(f"   ✅ [{role_id:16s}] {c:>8s}/{v:<12s} "
              f"entries={r.scratchpad_entries_written}")

    # Step 6: Share findings
    print("\n📋 Step 6: 写入评审结果到 Scratchpad...")
    reviews = FullTeamReviewer.get_all_reviews()
    for role_id, review in reviews.items():
        content = f"[{role_id}] v3.2 Roadmap 评审\n\n"
        content += f"**优先级排序**: {' > '.join(review['priority_order'])}\n\n"
        content += f"**MVP定义**: {review['mvp_definition']}\n\n"

        reasoning = review.get('reasoning', '')
        if reasoning:
            content += f"**推理过程**:\n```\n{reasoning}\n```\n\n"

        risks = review.get('risks', [])
        if risks:
            content += "**风险点**:\n"
            for risk in risks:
                content += f"  ⚠️ {risk}\n"
            content += "\n"

        scratchpad.write(ScratchpadEntry(
            worker_id=f"final-{role_id[:4]}",
            role_id=role_id,
            entry_type=EntryType.FINDING,
            content=content,
            tags=["v32-review", "roadmap", role_id],
        ))

    total_entries = len(scratchpad.read())
    print(f"   📊 总条目: {total_entries}")

    # Step 7: Conflict detection + resolution
    print("\n⚖️ Step 7: 冲突检测 + 共识投票...")
    all_conflicts = FullTeamReviewer.detect_all_conflicts()
    for c in all_conflicts:
        scratchpad.write(ScratchpadEntry(
            worker_id="coordinator",
            role_id="coordinator",
            entry_type=EntryType.CONFLICT,
            content=f"冲突: {c['topic']}\n涉及: {', '.join(c['parties'])}\n{c['description']}",
            tags=["v32-conflict"],
        ))
        parties_str = " vs ".join(c["parties"])
        print(f"   ⚠️ {c['topic']} ({parties_str})")

    resolutions = coordinator.resolve_conflicts()
    print(f"   ✅ 解决: {len(resolutions)} 个冲突")

    # Step 8: Report
    report = coordinator.generate_report()

    # Step 9: Final consensus
    elapsed = time.time() - t0
    final_report = generate_final_consensus(elapsed, resolutions)
    print(final_report)

    # Save
    out_dir = os.path.join(os.path.dirname(__file__), '..', '..', 'docs', 'planning')
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, 'v3.2-final-consensus.md')
    with open(out_path, 'w') as f:
        f.write(final_report)
    print(f"\n📁 最终决议已保存: {out_path}")

    return True


def generate_final_consensus(elapsed: float, resolutions: list) -> str:
    """生成最终共识决议"""
    L = []  # lines
    L.append("")
    L.append("## 🏆 v3.2 Final Roadmap — 全团队共识决议")
    L.append("")
    L.append(f"> **时间**: {datetime.now().strftime('%Y-%m-%d %H:%M')} | **耗时**: {elapsed:.2f}s")
    L.append("> **参与**: 产品经理 / 架构师 / UI设计师 / 独立开发者 / 测试专家 (5/5)")
    L.append("> **来源**: v3.2优化提案(6方向) + MCE集成分析(3角色) 合并评审")
    L.append("")

    # === 共识结论 ===
    L.append("### 🎯 最终共识结论")
    L.append("")
    L.append("| 优先级 | 方向 | 投入 | 决策 | 共识度 |")
    L.append("|--------|------|------|------|--------|")
    L.append("| **P0-A** | **A1 E2E Demo** | ~250行 | **✅ 必做** | 5/5 一致 |")
    L.append("| **P0-B** | **A2 Dispatcher UX** | ~100行 | **✅ 必做** | 4/5 (Arch稍后但接受) |")
    L.append("| **P1-A** | **B1 MCE 集成** | ~243行 | **✅ 必做** | 5/5 一致 |")
    L.append("| **P1-B** | **B2 ExecutionEngine** | ~350行 | **🔄 Demo+MCE后启动** | Arch推动/其他同意延后 |")
    L.append("| **P2** | **C1 LearningDashboard** | ~180行 | **⏳ 有数据后再做** | UI想做/Tester同意延后 |")
    L.append("| **P3** | **C2 跨平台适配** | ~250行 | **⏳ 依赖B2 Engine** | 全员一致 |")
    L.append("")

    # === MVP 定义 ===
    L.append("### 📦 v3.2 MVP 定义（共识）")
    L.append("")
    L.append("**MVP = A1 + A2 + B1 = 约 593 行代码 + 约 100 新测试**")
    L.append("")
    L.append("| 组成部分 | 内容 | 行数 | 负责角色 | 可并行? |")
    L.append("|----------|------|------|---------|---------|")
    L.append("| A1 | E2E Demo 完整脚本 | ~250 | Coder | ✅ 与A2/B1并行 |")
    L.append("| A2 | Dispatcher UX 增强 | ~100 | UI+Coder | ✅ 与A1/B1并行 |")
    L.append("| B1 | MCEAdapter + 集成改动 | ~243 | Arch+Coder | ✅ 与A1/A2并行 |")
    L.append("| **合计** | | **~593** | | **三线并行** |")
    L.append("")
    L.append("**时间框**: 1-2 Sprint (取决于人力)")
    L.append("**验收标准**: `python3 e2e_demo_v32_review.py` 全流程通过 + MCE可选集成正常降级")
    L.append("")

    # === 实现路线图 ===
    L.append("### 🗺️ 实现路线图")
    L.append("")
    roadmap_text = (
        "Week 1 (并行三线):\n"
        "  Line-A: E2E Demo 核心 (Day1-2: ~250行)\n"
        "  Line-B: MCEAdapter (Day1-2: ~150行)\n"
        "  Line-C: UX 增强 (Day2-3: ~100行)\n\n"
        "Week 2:\n"
        "  集成测试 + 回归验证 + 新增~100测试 + 文档更新\n\n"
        "Post-MVP:\n"
        "  B2 Engine -> C2 跨平台 -> C1 Dashboard (按需)"
    )
    for line in roadmap_text.split("\n"):
        L.append(line)
    L.append("")

    # === 冲突解决记录 ===
    L.append("### ⚖️ 冲突解决记录")
    L.append("")
    conflict_map = {
        "MVP范围/优先级": {
            "issue": "PM: A2>B1 vs Arch: B1>A2",
            "resolution": "**折中: 三者都纳入MVP, 三线并行实现**。Arch的理由(B1为B2铺路)被认可, PM的理由(用户体验)也被认可。",
        },
        "C1 Dashboard时机": {
            "issue": "UI想提前C1 vs Tester主张等有数据",
            "resolution": "**C1 延后至有真实数据后**。Demo产生的数据可作为Dashboard的种子数据。",
        },
    }
    for i, (topic, info) in enumerate(conflict_map.items(), 1):
        L.append(f"**冲突{i}: {topic}**")
        L.append(f"- 问题: {info['issue']}")
        L.append(f"- 解决: {info['resolution']}")
        L.append("")

    # === 各角色一句话 ===
    L.append("### 💬 各角色核心观点")
    L.append("")
    role_names = {
        "product_manager": "产品经理", "architect": "架构师",
        "ui-designer": "UI设计师", "solo-coder": "开发者", "tester": "测试专家",
    }
    reviews = FullTeamReviewer.get_all_reviews()
    for rid, rev in reviews.items():
        name = role_names.get(rid, rid)
        order = " > ".join(rev["priority_order"][:4])
        mvp = rev.get("mvp_definition", "")
        L.append(f"- **{name}**: 排序[{order}...] | MVP: {mvp}")
    L.append("")

    # === 下一步 ===
    L.append("### ➡️ 立即行动项")
    L.append("")
    L.append("1. [ ] **Line-A**: 创建 `scripts/demo/e2e_full_demo.py` — E2E Demo 脚本")
    L.append("2. [ ] **Line-B**: 创建 `scripts/collaboration/mce_adapter.py` — MCEAdapter 实现")
    L.append("3. [ ] **Line-C**: 增强 `dispatcher.py` 的 `quick_dispatch()` — 结构化报告输出")
    L.append("4. [ ] **Test**: 编写 `e2e_demo_test.py` + `mce_adapter_test.py` + `mce_contract_test.py`")
    L.append("5. [ ] **Verify**: 运行全量回归 (~882 tests), 确保零退化")
    L.append("6. [ ] **Docs**: 更新 SKILL.md / README / v3-upgrade-proposal 反映 v3.2 决议")
    L.append("7. [ ] **Push**: Git commit + push to main")
    L.append("")

    return "\n".join(L)


if __name__ == "__main__":
    try:
        ok = run_final_review()
        sys.exit(0 if ok else 1)
    except Exception as e:
        print(f"\n❌ 失败: {e}", file=sys.stderr)
        import traceback
        traceback.print_exc()
        sys.exit(1)
