#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
交付物质量控制模块 v1.0

本模块负责：
1. 代码质量自动检测
2. 文档标准化验证
3. 交付物质量评分系统
4. 自然语言触发机制

核心功能:
1. 代码质量检测 - 分析代码复杂度、可维护性、安全性等
2. 文档验证 - 检查文档格式、完整性、一致性
3. 质量评分 - 基于多维度指标生成质量评分
4. 自然语言交互 - 支持通过对话触发质量检查
"""

import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple
from dataclasses import dataclass, field
from datetime import datetime
import re
import ast
import concurrent.futures

from multi_role_code_walkthrough import ProjectScanner, CodeAnalyzer, RoleAnalyzer, DocumentAligner


@dataclass
class QualityIssue:
    """质量问题"""
    type: str  # 问题类型: code, documentation, architecture
    category: str  # 具体类别: complexity, security, formatting, etc.
    description: str  # 问题描述
    severity: str  # 严重程度: critical, high, medium, low
    location: str  # 位置: 文件路径或模块
    line: Optional[int] = None  # 行号
    suggestion: Optional[str] = None  # 建议


@dataclass
class QualityScore:
    """质量评分"""
    overall: float  # 总体评分 0-100
    code_quality: float  # 代码质量评分
    documentation_quality: float  # 文档质量评分
    architecture_quality: float  # 架构质量评分
    issues: List[QualityIssue]  # 发现的问题
    recommendations: List[str]  # 改进建议


class CodeQualityDetector:
    """代码质量检测器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.analyzer = CodeAnalyzer(str(project_root))

    def detect_quality_issues(self, file_path: Path) -> List[QualityIssue]:
        """检测单个文件的质量问题"""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            lines = content.splitlines()
            ext = file_path.suffix

            # 检测代码复杂度
            complexity_issues = self._detect_complexity(lines, file_path)
            issues.extend(complexity_issues)

            # 检测代码风格
            style_issues = self._detect_style_issues(lines, file_path, ext)
            issues.extend(style_issues)

            # 检测潜在安全问题
            security_issues = self._detect_security_issues(content, file_path, ext)
            issues.extend(security_issues)

        except Exception as e:
            issues.append(QualityIssue(
                type="code",
                category="error",
                description=f"无法分析文件: {str(e)}",
                severity="medium",
                location=str(file_path)
            ))

        return issues

    def _detect_complexity(self, lines: List[str], file_path: Path) -> List[QualityIssue]:
        """检测代码复杂度"""
        issues = []

        # 检测文件长度
        if len(lines) > 500:
            issues.append(QualityIssue(
                type="code",
                category="complexity",
                description=f"文件过长 ({len(lines)} 行)，建议拆分为多个文件",
                severity="medium",
                location=str(file_path)
            ))

        # 检测函数长度
        function_lines = []
        in_function = False
        function_start = 0

        for i, line in enumerate(lines):
            if re.search(r'\bdef\s+\w+\s*\(', line) or re.search(r'\bfunction\s+\w+\s*\(', line):
                if in_function and len(function_lines) > 50:
                    issues.append(QualityIssue(
                        type="code",
                        category="complexity",
                        description="函数过长，建议拆分为多个函数",
                        severity="medium",
                        location=str(file_path),
                        line=function_start + 1
                    ))
                in_function = True
                function_start = i
                function_lines = [line]
            elif in_function:
                function_lines.append(line)
                if line.strip() == '}' or (line.strip() == 'end' and file_path.suffix in ['.rb']):
                    if len(function_lines) > 50:
                        issues.append(QualityIssue(
                            type="code",
                            category="complexity",
                            description="函数过长，建议拆分为多个函数",
                            severity="medium",
                            location=str(file_path),
                            line=function_start + 1
                        ))
                    in_function = False
                    function_lines = []

        return issues

    def _detect_style_issues(self, lines: List[str], file_path: Path, ext: str) -> List[QualityIssue]:
        """检测代码风格问题"""
        issues = []

        # 检测缩进问题
        for i, line in enumerate(lines):
            if line.strip() and not line.startswith(' ' * 4) and not line.startswith('\t') and ext in ['.py']:
                issues.append(QualityIssue(
                    type="code",
                    category="style",
                    description="缩进不符合标准（建议使用4个空格）",
                    severity="low",
                    location=str(file_path),
                    line=i + 1
                ))

        # 检测空行问题
        consecutive_empty_lines = 0
        for i, line in enumerate(lines):
            if line.strip() == '':
                consecutive_empty_lines += 1
                if consecutive_empty_lines > 2:
                    issues.append(QualityIssue(
                        type="code",
                        category="style",
                        description="过多连续空行",
                        severity="low",
                        location=str(file_path),
                        line=i + 1
                    ))
            else:
                consecutive_empty_lines = 0

        return issues

    def _detect_security_issues(self, content: str, file_path: Path, ext: str) -> List[QualityIssue]:
        """检测潜在安全问题"""
        issues = []

        # 检测硬编码密码
        if re.search(r'password\s*=\s*[\'"][^\'"]+[\'"]', content, re.IGNORECASE):
            issues.append(QualityIssue(
                type="code",
                category="security",
                description="发现硬编码密码，建议使用环境变量或配置文件",
                severity="critical",
                location=str(file_path),
                suggestion="使用环境变量或配置文件存储敏感信息"
            ))

        # 检测SQL注入风险
        if re.search(r'\bSELECT\b.*\bFROM\b.*\+\s*\w+', content, re.IGNORECASE):
            issues.append(QualityIssue(
                type="code",
                category="security",
                description="可能存在SQL注入风险，建议使用参数化查询",
                severity="high",
                location=str(file_path),
                suggestion="使用参数化查询或ORM框架"
            ))

        return issues


class DocumentValidator:
    """文档验证器"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)

    def validate_document(self, file_path: Path) -> List[QualityIssue]:
        """验证单个文档文件"""
        issues = []

        try:
            content = file_path.read_text(encoding='utf-8', errors='ignore')
            ext = file_path.suffix

            if ext == '.md':
                md_issues = self._validate_markdown(content, file_path)
                issues.extend(md_issues)
            elif ext in ['.txt', '.rst', '.adoc']:
                # 基本验证
                if len(content) < 100:
                    issues.append(QualityIssue(
                        type="documentation",
                        category="completeness",
                        description="文档内容过短，可能不完整",
                        severity="low",
                        location=str(file_path)
                    ))

        except Exception as e:
            issues.append(QualityIssue(
                type="documentation",
                category="error",
                description=f"无法分析文档: {str(e)}",
                severity="medium",
                location=str(file_path)
            ))

        return issues

    def _validate_markdown(self, content: str, file_path: Path) -> List[QualityIssue]:
        """验证Markdown文档"""
        issues = []

        # 检测标题层级
        lines = content.splitlines()
        headings = []

        for i, line in enumerate(lines):
            heading_match = re.match(r'(#{1,6})\s+(.*)', line)
            if heading_match:
                level = len(heading_match.group(1))
                headings.append(level)

                # 检测标题层级是否连续
                if len(headings) > 1 and headings[-1] > headings[-2] + 1:
                    issues.append(QualityIssue(
                        type="documentation",
                        category="formatting",
                        description="标题层级不连续",
                        severity="low",
                        location=str(file_path),
                        line=i + 1
                    ))

        # 检测是否有目录
        if '## 目录' not in content and '## Table of Contents' not in content and len(headings) > 3:
            issues.append(QualityIssue(
                type="documentation",
                category="structure",
                description="文档较长，建议添加目录",
                severity="low",
                location=str(file_path),
                suggestion="添加目录以提高可读性"
            ))

        # 检测代码块格式
        code_block_count = content.count('```')
        if code_block_count % 2 != 0:
            issues.append(QualityIssue(
                type="documentation",
                category="formatting",
                description="代码块标记不匹配",
                severity="medium",
                location=str(file_path)
            ))

        return issues


class QualityScorer:
    """质量评分器"""

    def calculate_score(self, issues: List[QualityIssue]) -> QualityScore:
        """计算质量评分"""
        # 初始化评分
        code_score = 100.0
        doc_score = 100.0
        arch_score = 100.0

        # 根据问题严重程度扣分
        for issue in issues:
            if issue.type == "code":
                if issue.severity == "critical":
                    code_score -= 20
                elif issue.severity == "high":
                    code_score -= 10
                elif issue.severity == "medium":
                    code_score -= 5
                elif issue.severity == "low":
                    code_score -= 1
            elif issue.type == "documentation":
                if issue.severity == "critical":
                    doc_score -= 20
                elif issue.severity == "high":
                    doc_score -= 10
                elif issue.severity == "medium":
                    doc_score -= 5
                elif issue.severity == "low":
                    doc_score -= 1
            elif issue.type == "architecture":
                if issue.severity == "critical":
                    arch_score -= 20
                elif issue.severity == "high":
                    arch_score -= 10
                elif issue.severity == "medium":
                    arch_score -= 5
                elif issue.severity == "low":
                    arch_score -= 1

        # 确保评分在0-100之间
        code_score = max(0, min(100, code_score))
        doc_score = max(0, min(100, doc_score))
        arch_score = max(0, min(100, arch_score))

        # 计算总体评分
        overall = (code_score * 0.4 + doc_score * 0.3 + arch_score * 0.3)

        # 生成改进建议
        recommendations = self._generate_recommendations(issues)

        return QualityScore(
            overall=overall,
            code_quality=code_score,
            documentation_quality=doc_score,
            architecture_quality=arch_score,
            issues=issues,
            recommendations=recommendations
        )

    def _generate_recommendations(self, issues: List[QualityIssue]) -> List[str]:
        """生成改进建议"""
        recommendations = []

        # 按类型分组问题
        issues_by_type = {}
        for issue in issues:
            if issue.type not in issues_by_type:
                issues_by_type[issue.type] = []
            issues_by_type[issue.type].append(issue)

        # 生成代码质量建议
        if "code" in issues_by_type:
            code_issues = issues_by_type["code"]
            complexity_issues = [i for i in code_issues if i.category == "complexity"]
            if complexity_issues:
                recommendations.append("重构复杂函数，提高代码可读性")

            security_issues = [i for i in code_issues if i.category == "security"]
            if security_issues:
                recommendations.append("修复安全漏洞，提高代码安全性")

        # 生成文档质量建议
        if "documentation" in issues_by_type:
            doc_issues = issues_by_type["documentation"]
            if doc_issues:
                recommendations.append("完善文档内容，提高文档质量")

        return recommendations


class NaturalLanguageTrigger:
    """自然语言触发器"""

    def __init__(self):
        self.trigger_phrases = [
            r'检查代码质量',
            r'分析文档',
            r'质量评估',
            r'代码审查',
            r'文档验证',
            r'交付物质量',
            r'检测问题',
            r'评分系统',
            r'质量检查'
        ]

    def detect_trigger(self, message: str) -> bool:
        """检测是否触发质量控制"""
        message_lower = message.lower()
        for phrase in self.trigger_phrases:
            if re.search(phrase, message_lower):
                return True
        return False

    def extract_context(self, message: str) -> Dict[str, Any]:
        """提取触发上下文"""
        context = {
            "action": "quality_check",
            "target": "all",
            "details": {}
        }

        # 提取目标
        if "代码" in message or "code" in message.lower():
            context["target"] = "code"
        elif "文档" in message or "document" in message.lower():
            context["target"] = "documentation"

        # 提取具体操作
        if "评分" in message or "score" in message.lower():
            context["details"]["include_score"] = True
        if "问题" in message or "issue" in message.lower():
            context["details"]["include_issues"] = True
        if "建议" in message or "recommendation" in message.lower():
            context["details"]["include_recommendations"] = True

        return context


class DeliverableQualityControl:
    """交付物质量控制主类"""

    def __init__(self, project_root: str):
        self.project_root = Path(project_root)
        self.scanner = ProjectScanner(str(project_root))
        self.code_detector = CodeQualityDetector(str(project_root))
        self.doc_validator = DocumentValidator(str(project_root))
        self.scorer = QualityScorer()
        self.trigger = NaturalLanguageTrigger()

    def run_quality_check(self, target: str = "all") -> Dict[str, Any]:
        """运行质量检查"""
        print(f"开始质量检查，目标: {target}")

        # 扫描项目
        project_data = self.scanner.scan()
        project_info = project_data["project_info"]

        issues = []

        # 检查代码质量
        if target in ["all", "code"]:
            print("检查代码质量...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for file_path in self.scanner.source_files:
                    futures.append(executor.submit(self.code_detector.detect_quality_issues, file_path))

                for future in concurrent.futures.as_completed(futures):
                    try:
                        file_issues = future.result()
                        issues.extend(file_issues)
                    except Exception as e:
                        print(f"分析文件时出错: {str(e)}")

        # 检查文档质量
        if target in ["all", "documentation"]:
            print("检查文档质量...")
            with concurrent.futures.ThreadPoolExecutor() as executor:
                futures = []
                for file_path in self.scanner.doc_files:
                    futures.append(executor.submit(self.doc_validator.validate_document, file_path))

                for future in concurrent.futures.as_completed(futures):
                    try:
                        file_issues = future.result()
                        issues.extend(file_issues)
                    except Exception as e:
                        print(f"分析文档时出错: {str(e)}")

        # 计算质量评分
        score = self.scorer.calculate_score(issues)

        # 生成报告
        report = self._generate_report(project_info, score)

        return {
            "project_info": project_info,
            "score": score,
            "report": report
        }

    def _generate_report(self, project_info: Dict[str, Any], score: QualityScore) -> str:
        """生成质量报告"""
        timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        md_content = f"""
# {project_info['name']} 交付物质量报告

> **生成时间**: {timestamp}
> **项目路径**: `{project_info['project_path']}`

---

## 质量评分

| 类别 | 评分 | 等级 |
|------|------|------|
| **总体质量** | {score.overall:.1f}/100 | {self._get_score_level(score.overall)} |
| **代码质量** | {score.code_quality:.1f}/100 | {self._get_score_level(score.code_quality)} |
| **文档质量** | {score.documentation_quality:.1f}/100 | {self._get_score_level(score.documentation_quality)} |
| **架构质量** | {score.architecture_quality:.1f}/100 | {self._get_score_level(score.architecture_quality)} |

## 发现的问题

"""

        # 按严重程度分组问题
        critical_issues = [i for i in score.issues if i.severity == "critical"]
        high_issues = [i for i in score.issues if i.severity == "high"]
        medium_issues = [i for i in score.issues if i.severity == "medium"]
        low_issues = [i for i in score.issues if i.severity == "low"]

        if critical_issues:
            md_content += "### 严重问题 (需立即处理)\n\n"
            md_content += "| 类型 | 类别 | 描述 | 位置 |\n"
            md_content += "|------|------|------|------|\n"
            for issue in critical_issues:
                md_content += f"| {issue.type} | {issue.category} | {issue.description} | {issue.location} |\n"
            md_content += "\n"

        if high_issues:
            md_content += "### 高优先级问题\n\n"
            md_content += "| 类型 | 类别 | 描述 | 位置 |\n"
            md_content += "|------|------|------|------|\n"
            for issue in high_issues:
                md_content += f"| {issue.type} | {issue.category} | {issue.description} | {issue.location} |\n"
            md_content += "\n"

        if medium_issues:
            md_content += "### 中等优先级问题\n\n"
            md_content += "| 类型 | 类别 | 描述 | 位置 |\n"
            md_content += "|------|------|------|------|\n"
            for issue in medium_issues:
                md_content += f"| {issue.type} | {issue.category} | {issue.description} | {issue.location} |\n"
            md_content += "\n"

        if low_issues:
            md_content += "### 低优先级问题\n\n"
            md_content += "| 类型 | 类别 | 描述 | 位置 |\n"
            md_content += "|------|------|------|------|\n"
            for issue in low_issues:
                md_content += f"| {issue.type} | {issue.category} | {issue.description} | {issue.location} |\n"
            md_content += "\n"

        if not score.issues:
            md_content += "### 未发现明显问题\n\n"

        # 添加改进建议
        if score.recommendations:
            md_content += "## 改进建议\n\n"
            for rec in score.recommendations:
                md_content += f"- {rec}\n"
            md_content += "\n"

        # 添加报告尾部
        md_content += f"""
---

*本报告由交付物质量控制模块自动生成*
*生成时间: {timestamp}*
"""

        return md_content

    def _get_score_level(self, score: float) -> str:
        """根据评分获取等级"""
        if score >= 90:
            return "优秀"
        elif score >= 80:
            return "良好"
        elif score >= 70:
            return "中等"
        elif score >= 60:
            return "及格"
        else:
            return "需改进"

    def handle_natural_language(self, message: str) -> Optional[Dict[str, Any]]:
        """处理自然语言指令"""
        if not self.trigger.detect_trigger(message):
            return None

        context = self.trigger.extract_context(message)
        result = self.run_quality_check(context["target"])

        return {
            "action": "quality_check",
            "result": result,
            "context": context
        }


def main():
    """主函数"""
    parser = argparse.ArgumentParser(
        description="交付物质量控制模块 - 检测代码和文档质量",
        formatter_class=argparse.RawDescriptionHelpFormatter
    )

    parser.add_argument("project_root", help="项目根目录路径")
    parser.add_argument("--target", "-t", default="all", choices=["all", "code", "documentation"],
                        help="检查目标: all (默认), code, documentation")
    parser.add_argument("--output", "-o", default=None, help="输出报告路径")

    args = parser.parse_args()

    if not os.path.exists(args.project_root):
        print(f"错误: 路径不存在: {args.project_root}")
        return 1

    qc = DeliverableQualityControl(args.project_root)
    result = qc.run_quality_check(args.target)

    # 输出报告
    if args.output:
        output_path = Path(args.output)
        output_path.write_text(result["report"], encoding='utf-8')
        print(f"质量报告已生成: {output_path}")
    else:
        print(result["report"])

    return 0


if __name__ == "__main__":
    exit(main())
