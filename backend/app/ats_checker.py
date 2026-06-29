import re
from typing import List

from app.schemas import ResumeInfo, ATSIssue, ATSReport


def has_quantified_result(text: str) -> bool:
    if not text:
        return False

    pattern = r"\d|%|提升|降低|减少|增长|优化|加速|缩短|提高|下降|并发|耗时|响应|用户|数据"
    return bool(re.search(pattern, str(text)))


def calculate_level(score: int) -> str:
    if score >= 85:
        return "优秀"
    if score >= 70:
        return "良好"
    if score >= 55:
        return "一般"
    return "较弱"


def run_ats_check(resume: ResumeInfo) -> ATSReport:
    """
    V2.3 后端 ATS 兼容性检查。

    这里不是模拟完整商业 ATS，而是基于结构化解析结果做轻量评估：
    - 技能区是否完整
    - 项目经历是否充分
    - 成果是否量化
    - 实习/证书/教育信息是否可识别
    - 内容是否适合关键词检索
    """

    issues: List[ATSIssue] = []
    suggestions: List[str] = []

    skills = resume.skills or []
    projects = resume.projects or []
    education = resume.education or []
    internships = resume.internships or []
    certificates = resume.certificates or []

    if len(skills) >= 8:
        issues.append(
            ATSIssue(
                title="技能区完整度较高",
                status="good",
                message=f"已识别 {len(skills)} 项技能，便于 ATS 进行关键词匹配。",
                score=20,
            )
        )
    elif len(skills) >= 4:
        issues.append(
            ATSIssue(
                title="技能区基本完整",
                status="warning",
                message=f"已识别 {len(skills)} 项技能，建议继续补充目标岗位相关技术栈。",
                score=13,
            )
        )
        suggestions.append("建议在技能区补充与 JD 高相关的框架、数据库、中间件和工具关键词。")
    else:
        issues.append(
            ATSIssue(
                title="技能区偏弱",
                status="danger",
                message="技能数量偏少，可能影响 ATS 对岗位关键词的识别。",
                score=5,
            )
        )
        suggestions.append("建议增加“专业技能/技术栈”模块，并按语言、框架、数据库、工具分类。")

    if len(projects) >= 2:
        issues.append(
            ATSIssue(
                title="项目经历较充分",
                status="good",
                message=f"已识别 {len(projects)} 个项目，有利于展示岗位相关经验。",
                score=20,
            )
        )
    elif len(projects) == 1:
        issues.append(
            ATSIssue(
                title="项目经历基本可用",
                status="warning",
                message="当前识别到 1 个项目，建议补充另一个实习项目、课程项目或个人项目。",
                score=12,
            )
        )
        suggestions.append("建议至少准备 2 个项目经历：一个主项目体现深度，一个辅助项目体现广度。")
    else:
        issues.append(
            ATSIssue(
                title="缺少项目经历",
                status="danger",
                message="未明显识别到项目经历，技术岗简历可能缺少核心支撑材料。",
                score=0,
            )
        )
        suggestions.append("建议添加项目经历，并写清技术栈、个人职责、实现难点和成果。")

    all_achievements = []
    for project in projects:
        all_achievements.extend(project.achievements or [])
        all_achievements.extend(project.responsibilities or [])

    quantified_count = sum(1 for item in all_achievements if has_quantified_result(item))

    if quantified_count >= 3:
        issues.append(
            ATSIssue(
                title="成果量化较好",
                status="good",
                message=f"识别到 {quantified_count} 条带有数字或优化结果的表达。",
                score=20,
            )
        )
    elif quantified_count >= 1:
        issues.append(
            ATSIssue(
                title="成果量化一般",
                status="warning",
                message=f"识别到 {quantified_count} 条量化表达，建议继续补充性能、规模或效果数据。",
                score=12,
            )
        )
        suggestions.append("建议使用数字描述项目成果，例如接口耗时、数据量、并发量、准确率、提升比例等。")
    else:
        issues.append(
            ATSIssue(
                title="缺少量化成果",
                status="warning",
                message="项目描述中缺少明显数字或效果表达，简历说服力不足。",
                score=6,
            )
        )
        suggestions.append("建议把“完成/参与/负责”改成“实现了什么功能，带来了什么结果”。")

    if education:
        issues.append(
            ATSIssue(
                title="教育信息可识别",
                status="good",
                message="系统识别到教育经历，基础信息较完整。",
                score=10,
            )
        )
    else:
        issues.append(
            ATSIssue(
                title="教育信息缺失",
                status="warning",
                message="未明显识别到教育经历，建议确认简历中是否有清晰的教育背景模块。",
                score=4,
            )
        )
        suggestions.append("建议保留清晰的教育经历模块，包括学校、专业、时间和学历。")

    if internships:
        issues.append(
            ATSIssue(
                title="实习经历可识别",
                status="good",
                message=f"识别到 {len(internships)} 条实习经历，有助于提升可信度。",
                score=10,
            )
        )
    else:
        issues.append(
            ATSIssue(
                title="实习经历不足",
                status="warning",
                message="未识别到明显实习经历，如果有相关经历建议补充。",
                score=5,
            )
        )

    if certificates:
        issues.append(
            ATSIssue(
                title="证书信息可识别",
                status="good",
                message=f"识别到 {len(certificates)} 条证书或资格信息。",
                score=10,
            )
        )
    else:
        issues.append(
            ATSIssue(
                title="证书信息较少",
                status="warning",
                message="未识别到证书信息。该项不是必须，但有相关证书可补充。",
                score=5,
            )
        )

    score = sum(item.score for item in issues)
    score = max(0, min(100, score))
    level = calculate_level(score)

    if score >= 85:
        summary = "简历结构较完整，ATS 可解析性较好，适合进一步针对目标岗位优化关键词。"
    elif score >= 70:
        summary = "简历整体可解析性较好，但仍可补充量化成果和岗位关键词。"
    elif score >= 55:
        summary = "简历具备基本结构，但技能、项目或成果表达仍需加强。"
    else:
        summary = "简历结构化程度较弱，建议优先完善技能区、项目经历和量化成果。"

    return ATSReport(
        ats_score=score,
        level=level,
        summary=summary,
        issues=issues,
        suggestions=suggestions,
    )