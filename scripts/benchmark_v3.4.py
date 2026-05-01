#!/usr/bin/env python3
"""
DevSquad v3.4 性能基准测试

用途：
- 测量 v3.4 的性能基线
- 为 v3.5 优化提供对比基准

测试场景：
1. 单 Agent 执行
2. 3 Agent 串行执行
3. 5 Agent 串行执行
4. 缓存读写性能
5. 重试机制性能
"""

import time
import json
import psutil
import sys
from pathlib import Path
from typing import Dict, Any, List
from dataclasses import dataclass, asdict

# 添加项目根目录到 Python 路径
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


@dataclass
class BenchmarkResult:
    """基准测试结果"""
    scenario: str
    duration: float  # 秒
    token_count: int
    memory_mb: float
    success: bool
    metadata: Dict[str, Any]


class V34Benchmark:
    """v3.4 性能基准测试"""
    
    def __init__(self):
        self.results: List[BenchmarkResult] = []
        self.process = psutil.Process()
    
    def estimate_tokens(self, text: str) -> int:
        """估算 token 数量（简单启发式：1 token ≈ 4 字符）"""
        return len(text) // 4
    
    def get_memory_mb(self) -> float:
        """获取当前内存占用（MB）"""
        return self.process.memory_info().rss / 1024 / 1024
    
    def benchmark_single_agent(self) -> BenchmarkResult:
        """测试单 Agent 执行"""
        print("📊 测试场景 1：单 Agent 执行")
        
        # 模拟 Agent 执行
        task = "Design a REST API for user management"
        
        start_time = time.time()
        start_memory = self.get_memory_mb()
        
        # 模拟 LLM 调用（生成约 2K tokens 的响应）
        response = self._simulate_llm_call(task, response_tokens=2000)
        
        duration = time.time() - start_time
        memory_used = self.get_memory_mb() - start_memory
        token_count = self.estimate_tokens(task) + 2000
        
        result = BenchmarkResult(
            scenario="single_agent",
            duration=duration,
            token_count=token_count,
            memory_mb=memory_used,
            success=True,
            metadata={
                "agent_role": "Architect",
                "task_length": len(task),
                "response_length": len(response)
            }
        )
        
        self.results.append(result)
        print(f"  ✅ 完成：{duration:.2f}s, {token_count} tokens, {memory_used:.1f}MB")
        return result
    
    def benchmark_3_agents_serial(self) -> BenchmarkResult:
        """测试 3 Agent 串行执行（完整历史传递）"""
        print("📊 测试场景 2：3 Agent 串行执行（完整历史）")
        
        task = "Design and implement a REST API"
        
        start_time = time.time()
        start_memory = self.get_memory_mb()
        
        # Agent 1: Architect
        history = [{"role": "user", "content": task}]
        response1 = self._simulate_llm_call(task, response_tokens=3000)
        history.append({"role": "assistant", "content": response1})
        
        # Agent 2: PM（接收完整历史）
        context2 = self._build_context(history)
        response2 = self._simulate_llm_call(context2, response_tokens=2000)
        history.append({"role": "assistant", "content": response2})
        
        # Agent 3: Developer（接收完整历史）
        context3 = self._build_context(history)
        response3 = self._simulate_llm_call(context3, response_tokens=4000)
        
        duration = time.time() - start_time
        memory_used = self.get_memory_mb() - start_memory
        
        # 计算总 token 消耗（累积传递）
        token_count = (
            self.estimate_tokens(task) + 3000 +  # Agent 1
            self.estimate_tokens(context2) + 2000 +  # Agent 2
            self.estimate_tokens(context3) + 4000  # Agent 3
        )
        
        result = BenchmarkResult(
            scenario="3_agents_serial_full_history",
            duration=duration,
            token_count=token_count,
            memory_mb=memory_used,
            success=True,
            metadata={
                "agents": ["Architect", "PM", "Developer"],
                "history_length": len(history),
                "context2_length": len(context2),
                "context3_length": len(context3)
            }
        )
        
        self.results.append(result)
        print(f"  ✅ 完成：{duration:.2f}s, {token_count} tokens, {memory_used:.1f}MB")
        return result
    
    def benchmark_5_agents_serial(self) -> BenchmarkResult:
        """测试 5 Agent 串行执行（完整历史传递）"""
        print("📊 测试场景 3：5 Agent 串行执行（完整历史）")
        
        task = "Design, implement, and test a REST API"
        
        start_time = time.time()
        start_memory = self.get_memory_mb()
        
        history = [{"role": "user", "content": task}]
        total_tokens = self.estimate_tokens(task)
        
        # 5 个 Agent 串行执行
        agent_responses = [3000, 2000, 4000, 2500, 3000]
        
        for i, response_tokens in enumerate(agent_responses):
            context = self._build_context(history)
            response = self._simulate_llm_call(context, response_tokens)
            history.append({"role": "assistant", "content": response})
            
            total_tokens += self.estimate_tokens(context) + response_tokens
        
        duration = time.time() - start_time
        memory_used = self.get_memory_mb() - start_memory
        
        result = BenchmarkResult(
            scenario="5_agents_serial_full_history",
            duration=duration,
            token_count=total_tokens,
            memory_mb=memory_used,
            success=True,
            metadata={
                "agents": ["Architect", "PM", "Developer", "Tester", "Security"],
                "history_length": len(history)
            }
        )
        
        self.results.append(result)
        print(f"  ✅ 完成：{duration:.2f}s, {total_tokens} tokens, {memory_used:.1f}MB")
        return result
    
    def benchmark_cache_performance(self) -> BenchmarkResult:
        """测试缓存读写性能"""
        print("📊 测试场景 4：缓存读写性能")
        
        try:
            from scripts.collaboration.llm_cache import LLMCache
            
            cache = LLMCache()
            
            # 写入测试
            write_times = []
            for i in range(100):
                prompt = f"test_prompt_{i}"
                response = "x" * 1000
                
                start = time.time()
                cache.set(prompt, response, "openai", "gpt-4")
                write_times.append(time.time() - start)
            
            # 读取测试
            read_times = []
            for i in range(100):
                prompt = f"test_prompt_{i}"
                
                start = time.time()
                cache.get(prompt, "openai", "gpt-4")
                read_times.append(time.time() - start)
            
            avg_write = sum(write_times) / len(write_times) * 1000  # ms
            avg_read = sum(read_times) / len(read_times) * 1000  # ms
            
            result = BenchmarkResult(
                scenario="cache_performance",
                duration=sum(write_times) + sum(read_times),
                token_count=0,
                memory_mb=0,
                success=True,
                metadata={
                    "avg_write_ms": round(avg_write, 2),
                    "avg_read_ms": round(avg_read, 2),
                    "operations": 200
                }
            )
            
            self.results.append(result)
            print(f"  ✅ 完成：写入 {avg_write:.2f}ms, 读取 {avg_read:.2f}ms")
            return result
            
        except ImportError:
            print("  ⚠️ 跳过：LLMCache 未找到")
            return None
    
    def benchmark_retry_performance(self) -> BenchmarkResult:
        """测试重试机制性能"""
        print("📊 测试场景 5：重试机制性能")
        
        try:
            from scripts.collaboration.llm_retry import LLMRetry
            
            retry = LLMRetry()
            
            # 模拟成功调用（无重试）
            success_times = []
            for _ in range(50):
                start = time.time()
                retry.retry_with_fallback(lambda: "success")
                success_times.append(time.time() - start)
            
            avg_success = sum(success_times) / len(success_times) * 1000  # ms
            
            result = BenchmarkResult(
                scenario="retry_performance",
                duration=sum(success_times),
                token_count=0,
                memory_mb=0,
                success=True,
                metadata={
                    "avg_success_ms": round(avg_success, 2),
                    "operations": 50
                }
            )
            
            self.results.append(result)
            print(f"  ✅ 完成：平均 {avg_success:.2f}ms")
            return result
            
        except (ImportError, AttributeError) as e:
            print(f"  ⚠️ 跳过：LLMRetry 未找到或接口不匹配 ({e})")
            return None
    
    def _simulate_llm_call(self, prompt: str, response_tokens: int) -> str:
        """模拟 LLM 调用（生成指定 token 数的响应）"""
        # 模拟网络延迟
        time.sleep(0.1)
        
        # 生成响应（1 token ≈ 4 字符）
        return "x" * (response_tokens * 4)
    
    def _build_context(self, history: List[Dict[str, str]]) -> str:
        """构建上下文（完整历史）"""
        context_parts = []
        for msg in history:
            context_parts.append(f"{msg['role']}: {msg['content']}")
        return "\n\n".join(context_parts)
    
    def run_all(self):
        """运行所有基准测试"""
        print("=" * 60)
        print("DevSquad v3.4 性能基准测试")
        print("=" * 60)
        print()
        
        # 运行测试
        self.benchmark_single_agent()
        print()
        
        self.benchmark_3_agents_serial()
        print()
        
        self.benchmark_5_agents_serial()
        print()
        
        self.benchmark_cache_performance()
        print()
        
        self.benchmark_retry_performance()
        print()
        
        # 生成报告
        self.generate_report()
    
    def generate_report(self):
        """生成基准测试报告"""
        print("=" * 60)
        print("基准测试报告")
        print("=" * 60)
        print()
        
        # 汇总表格
        print("| 场景 | 时长 | Token 消耗 | 内存占用 |")
        print("|------|------|-----------|----------|")
        
        for result in self.results:
            if result:
                print(f"| {result.scenario} | {result.duration:.2f}s | "
                      f"{result.token_count:,} | {result.memory_mb:.1f}MB |")
        
        print()
        
        # 保存到 JSON
        output_file = project_root / "benchmarks" / "v3.4_baseline.json"
        output_file.parent.mkdir(exist_ok=True)
        
        baseline_data = {
            "version": "3.4",
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
            "results": {
                result.scenario: {
                    "duration": result.duration,
                    "token_count": result.token_count,
                    "memory_mb": result.memory_mb,
                    "metadata": result.metadata
                }
                for result in self.results if result
            }
        }
        
        with open(output_file, "w") as f:
            json.dump(baseline_data, f, indent=2)
        
        print(f"✅ 基准数据已保存到：{output_file}")
        print()
        
        # 关键指标
        print("🎯 关键指标（v3.5 优化目标）：")
        print()
        
        for result in self.results:
            if result and "agents" in result.scenario:
                if "3_agents" in result.scenario:
                    print(f"  3 Agent 场景：")
                    print(f"    - Token 消耗：{result.token_count:,} → 目标 ≤ 6,000 (减少 76%)")
                    print(f"    - 响应延迟：{result.duration:.1f}s → 目标 ≤ 10s")
                elif "5_agents" in result.scenario:
                    print(f"  5 Agent 场景：")
                    print(f"    - Token 消耗：{result.token_count:,} → 目标 ≤ 12,000 (减少 80%)")
                    print(f"    - 响应延迟：{result.duration:.1f}s → 目标 ≤ 15s")
        
        print()


def main():
    """主函数"""
    benchmark = V34Benchmark()
    benchmark.run_all()


if __name__ == "__main__":
    main()
