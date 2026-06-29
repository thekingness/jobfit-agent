import json

from app.extractors import llm
from app.schemas import ResumeInfo, JDInfo, MatchResult, StructuredReport


def generate_report(
    resume: ResumeInfo,
    jd: JDInfo,
    match_result: MatchResult
) -> StructuredReport:
    structured_llm = llm.with_structured_output(StructuredReport)

    resume_json = json.dumps(
        resume.model_dump(),
        ensure_ascii=False,
        indent=2
    )

    jd_json = json.dumps(
        jd.model_dump(),
        ensure_ascii=False,
        indent=2
    )

    match_json = json.dumps(
        match_result.model_dump(),
        ensure_ascii=False,
        indent=2
    )

    prompt = f"""
你是一个专业的计算机求职辅导 Agent。

请根据候选人简历、岗位 JD 和匹配分析，生成一份结构化中文求职分析报告。

非常重要的规则：
1. 不要编造候选人没有的经历。
2. 简历改写建议必须基于候选人已有简历内容。
3. 如果简历中没有证据，必须在 risk_level 中标为“中”或“高”。
4. rewrite_suggestions 中必须包含 original、optimized、reason、jd_keywords、evidence、risk_level。
5. optimized 要写成适合放进中文技术简历里的 bullet。
6. 面试题要围绕岗位 JD、候选人已有技能、缺失技能和项目经历生成。
7. 学习计划要具体，适合计算机实习求职者执行。
8. 输出必须严格符合指定结构。

候选人简历信息：
{resume_json}

岗位信息：
{jd_json}

匹配结果：
{match_json}
"""

    return structured_llm.invoke(prompt)


def structured_report_to_markdown(report: StructuredReport) -> str:
    """
    兼容旧前端或调试用：把结构化报告转换成 Markdown 文本。
    新前端主要使用 report_json。
    """

    lines = []

    lines.append("# 求职分析报告")
    lines.append("")
    lines.append("## 1. 总体评价")
    lines.append(report.overall_review or "暂无总体评价")
    lines.append("")

    lines.append("## 2. 匹配优势")
    if report.advantages:
        for item in report.advantages:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无明显匹配优势")
    lines.append("")

    lines.append("## 3. 技能缺口")
    if report.skill_gaps:
        for item in report.skill_gaps:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无明显技能缺口")
    lines.append("")

    lines.append("## 4. 项目经历优化建议")
    if report.project_suggestions:
        for item in report.project_suggestions:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无项目优化建议")
    lines.append("")

    lines.append("## 5. 简历改写建议")
    if report.rewrite_suggestions:
        for index, item in enumerate(report.rewrite_suggestions, start=1):
            lines.append(f"### 建议 {index}")
            lines.append(f"- 原始描述：{item.original}")
            lines.append(f"- 优化后：{item.optimized}")
            lines.append(f"- 优化原因：{item.reason}")
            lines.append(f"- 对应关键词：{', '.join(item.jd_keywords)}")
            lines.append(f"- 简历依据：{item.evidence}")
            lines.append(f"- 风险等级：{item.risk_level}")
            lines.append("")
    else:
        lines.append("- 暂无简历改写建议")
    lines.append("")

    lines.append("## 6. 学习计划")
    if report.learning_plan:
        for item in report.learning_plan:
            lines.append(f"- {item}")
    else:
        lines.append("- 暂无学习计划")
    lines.append("")

    lines.append("## 7. 面试题预测")
    if report.interview_questions:
        for index, item in enumerate(report.interview_questions, start=1):
            lines.append(f"{index}. {item.question}")
            lines.append(f"   - 考察点：{item.focus}")
    else:
        lines.append("- 暂无面试题")
    lines.append("")

    lines.append("## 8. 风险提示")
    if report.risk_tips:
        for item in report.risk_tips:
            lines.append(f"- {item}")
    else:
        lines.append("- 请注意不要在简历中添加没有实际经历支撑的内容。")

    return "\n".join(lines)