from typing import List, Optional
from pydantic import BaseModel, Field


class ResumeProject(BaseModel):
    name: str = Field(default="", description="项目名称")
    tech_stack: List[str] = Field(default_factory=list, description="项目技术栈")
    responsibilities: List[str] = Field(default_factory=list, description="个人职责")
    achievements: List[str] = Field(default_factory=list, description="项目成果")


class ResumeInfo(BaseModel):
    name: str = ""
    education: List[str] = Field(default_factory=list)
    skills: List[str] = Field(default_factory=list)
    projects: List[ResumeProject] = Field(default_factory=list)
    internships: List[str] = Field(default_factory=list)
    certificates: List[str] = Field(default_factory=list)


class JDInfo(BaseModel):
    position: str = ""
    required_skills: List[str] = Field(default_factory=list)
    preferred_skills: List[str] = Field(default_factory=list)
    responsibilities: List[str] = Field(default_factory=list)
    keywords: List[str] = Field(default_factory=list)
    business_domain: str = ""


class ScoreDimension(BaseModel):
    name: str = Field(default="", description="评分维度名称")
    score: int = Field(default=0, description="该维度得分")
    max_score: int = Field(default=0, description="该维度满分")
    explanation: str = Field(default="", description="该维度评分说明")


class ATSIssue(BaseModel):
    title: str = Field(default="", description="检查项标题")
    status: str = Field(default="warning", description="good/warning/danger")
    message: str = Field(default="", description="检查说明")
    score: int = Field(default=0, description="该检查项得分")


class ATSReport(BaseModel):
    ats_score: int = Field(default=0, description="ATS兼容性总分")
    level: str = Field(default="一般", description="优秀/良好/一般/较弱")
    summary: str = Field(default="", description="ATS总体说明")
    issues: List[ATSIssue] = Field(default_factory=list, description="ATS检查项")
    suggestions: List[str] = Field(default_factory=list, description="ATS优化建议")


class EvidenceItem(BaseModel):
    title: str = Field(default="", description="证据标题")
    target_text: str = Field(default="", description="JD或目标匹配文本")
    source_text: str = Field(default="", description="简历中的证据文本")
    source_type: str = Field(default="", description="skill/project/internship/certificate/resume")
    match_method: str = Field(default="", description="rule/fuzzy/tfidf/embedding")
    similarity: float = Field(default=0.0, description="相似度")
    explanation: str = Field(default="", description="为什么认为相关")


class MatchResult(BaseModel):
    score: int
    matched_skills: List[str]
    missing_required_skills: List[str]
    missing_preferred_skills: List[str]
    explanation: str

    required_skill_score: int = 0
    preferred_skill_score: int = 0
    project_relevance_score: int = 0
    keyword_coverage_score: int = 0

    score_breakdown: List[ScoreDimension] = Field(default_factory=list)

    project_related_keywords: List[str] = Field(default_factory=list)
    covered_keywords: List[str] = Field(default_factory=list)
    missing_keywords: List[str] = Field(default_factory=list)

    semantic_matches: List[str] = Field(default_factory=list)
    semantic_match_details: List[str] = Field(default_factory=list)

    evidence_items: List[EvidenceItem] = Field(default_factory=list)
    ats_report: Optional[ATSReport] = None


class RewriteSuggestion(BaseModel):
    original: str = Field(default="", description="原始简历描述")
    optimized: str = Field(default="", description="优化后的简历描述")
    reason: str = Field(default="", description="为什么这样优化")
    jd_keywords: List[str] = Field(default_factory=list, description="对应的岗位关键词")
    evidence: str = Field(default="", description="该优化建议基于简历中的什么内容")
    risk_level: str = Field(default="低", description="幻觉风险：低/中/高")


class InterviewQuestion(BaseModel):
    question: str = Field(default="", description="面试题")
    focus: str = Field(default="", description="考察点")


class StructuredReport(BaseModel):
    overall_review: str = Field(default="", description="总体评价")
    advantages: List[str] = Field(default_factory=list, description="匹配优势")
    skill_gaps: List[str] = Field(default_factory=list, description="技能缺口")
    project_suggestions: List[str] = Field(default_factory=list, description="项目经历优化建议")
    rewrite_suggestions: List[RewriteSuggestion] = Field(default_factory=list, description="简历改写建议")
    learning_plan: List[str] = Field(default_factory=list, description="学习计划")
    interview_questions: List[InterviewQuestion] = Field(default_factory=list, description="面试题预测")
    risk_tips: List[str] = Field(default_factory=list, description="风险提示")