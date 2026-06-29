import re
from typing import Dict, Iterable, List, Set

from app.ats_checker import run_ats_check
from app.schemas import ResumeInfo, JDInfo, MatchResult, ScoreDimension, EvidenceItem
from app.semantic_matcher import is_semantic_match


SKILL_ALIASES: Dict[str, List[str]] = {
    "java": ["java", "java语言", "java基础", "javase", "javaee"],
    "python": ["python", "python3", "py"],
    "javascript": ["javascript", "js", "es6", "ecmascript"],
    "typescript": ["typescript", "ts"],
    "html": ["html", "html5"],
    "css": ["css", "css3"],

    "springboot": ["springboot", "spring boot", "spring-boot", "spring_boot"],
    "spring": ["spring", "springmvc", "spring mvc"],
    "mybatis": ["mybatis", "mybatis-plus", "mybatisplus", "mybatis plus"],
    "maven": ["maven"],
    "gradle": ["gradle"],

    "mysql": ["mysql", "sql", "关系型数据库", "数据库", "rdbms"],
    "postgresql": ["postgresql", "postgres", "pgsql"],
    "redis": ["redis", "缓存", "cache", "缓存数据库"],
    "mongodb": ["mongodb", "mongo"],

    "linux": ["linux", "ubuntu", "centos", "shell", "bash", "命令行"],
    "docker": ["docker", "容器", "容器化", "dockerfile"],
    "nginx": ["nginx"],
    "git": ["git", "github", "gitlab", "版本控制"],

    "vue": ["vue", "vuejs", "vue.js", "vue2", "vue3"],
    "react": ["react", "reactjs", "react.js"],
    "nodejs": ["node", "nodejs", "node.js"],
    "vite": ["vite"],

    "fastapi": ["fastapi", "fast api"],
    "flask": ["flask"],
    "django": ["django"],

    "机器学习": ["机器学习", "machinelearning", "ml"],
    "深度学习": ["深度学习", "deeplearning", "dl"],
    "大模型": ["大模型", "llm", "large language model", "ai大模型"],
    "rag": ["rag", "检索增强生成", "retrieval augmented generation"],
    "agent": ["agent", "ai agent", "智能体", "多智能体"],
    "langchain": ["langchain"],
    "langgraph": ["langgraph"],
    "向量数据库": ["向量数据库", "vectordatabase", "vector db", "chroma", "faiss", "milvus"],

    "消息队列": ["消息队列", "mq", "rabbitmq", "kafka", "rocketmq"],
    "微服务": ["微服务", "microservice", "microservices"],
    "分布式": ["分布式", "distributed"],
    "接口开发": ["接口开发", "api", "restful", "rest api", "后端接口"],
    "单元测试": ["单元测试", "unittest", "unit test", "pytest", "junit"],

    "数据分析": ["数据分析", "dataanalysis", "pandas", "numpy"],
    "可视化": ["可视化", "visualization", "matplotlib", "echarts"],
}


def normalize_text(text: str) -> str:
    if not text:
        return ""

    text = str(text).lower().strip()
    text = re.sub(r"[\s\-_/.]+", "", text)
    text = re.sub(r"[^\w\u4e00-\u9fff#+]", "", text)
    return text


def build_alias_index() -> Dict[str, str]:
    alias_index = {}

    for canonical, aliases in SKILL_ALIASES.items():
        canonical_norm = normalize_text(canonical)
        alias_index[canonical_norm] = canonical_norm

        for alias in aliases:
            alias_norm = normalize_text(alias)
            if alias_norm:
                alias_index[alias_norm] = canonical_norm

    return alias_index


ALIAS_INDEX = build_alias_index()


def canonicalize_term(term: str) -> str:
    norm = normalize_text(term)
    return ALIAS_INDEX.get(norm, norm)


def get_alias_norms_for_canonical(canonical: str) -> Set[str]:
    canonical_norm = normalize_text(canonical)
    result = {canonical_norm}

    for alias_norm, mapped_canonical in ALIAS_INDEX.items():
        if mapped_canonical == canonical_norm:
            result.add(alias_norm)

    return result


def unique_keep_order(items: Iterable[str]) -> List[str]:
    result = []
    seen = set()

    for item in items:
        item = str(item).strip()
        if not item:
            continue

        canonical = canonicalize_term(item)

        if not canonical or canonical in seen:
            continue

        seen.add(canonical)
        result.append(item)

    return result


def build_canonical_display_map(items: Iterable[str]) -> Dict[str, str]:
    result = {}

    for item in items:
        item = str(item).strip()
        if not item:
            continue

        canonical = canonicalize_term(item)
        if canonical and canonical not in result:
            result[canonical] = item

    return result


def to_canonical_set(items: Iterable[str]) -> Set[str]:
    return {canonicalize_term(item) for item in items if canonicalize_term(item)}


def flatten_resume_text(resume: ResumeInfo) -> str:
    parts = []

    parts.extend(resume.education)
    parts.extend(resume.skills)
    parts.extend(resume.internships)
    parts.extend(resume.certificates)

    for project in resume.projects:
        parts.append(project.name)
        parts.extend(project.tech_stack)
        parts.extend(project.responsibilities)
        parts.extend(project.achievements)

    return " ".join([str(item) for item in parts if item])


def flatten_project_text(resume: ResumeInfo) -> str:
    parts = []

    for project in resume.projects:
        parts.append(project.name)
        parts.extend(project.tech_stack)
        parts.extend(project.responsibilities)
        parts.extend(project.achievements)

    return " ".join([str(item) for item in parts if item])


def build_resume_semantic_candidates(resume: ResumeInfo) -> List[str]:
    candidates = []

    candidates.extend(resume.skills)
    candidates.extend(resume.education)
    candidates.extend(resume.internships)
    candidates.extend(resume.certificates)

    for project in resume.projects:
        candidates.append(project.name)
        candidates.extend(project.tech_stack)
        candidates.extend(project.responsibilities)
        candidates.extend(project.achievements)

    return [str(item).strip() for item in candidates if str(item).strip()]


def build_project_semantic_candidates(resume: ResumeInfo) -> List[str]:
    candidates = []

    for project in resume.projects:
        candidates.append(project.name)
        candidates.extend(project.tech_stack)
        candidates.extend(project.responsibilities)
        candidates.extend(project.achievements)

    return [str(item).strip() for item in candidates if str(item).strip()]


def calculate_ratio_score(
    matched_count: int,
    total_count: int,
    max_score: int,
    full_score_when_empty: bool = True,
) -> int:
    if total_count == 0:
        return max_score if full_score_when_empty else 0

    score = matched_count / total_count * max_score
    return round(score)


def canonical_term_appears_in_text(canonical: str, normalized_text: str) -> bool:
    if not canonical or not normalized_text:
        return False

    alias_norms = get_alias_norms_for_canonical(canonical)

    for alias_norm in alias_norms:
        if alias_norm and alias_norm in normalized_text:
            return True

    return False


def display_terms(
    canonical_terms: Iterable[str],
    *display_maps: Dict[str, str],
) -> List[str]:
    result = []

    for canonical in sorted(canonical_terms):
        display = None

        for display_map in display_maps:
            if canonical in display_map:
                display = display_map[canonical]
                break

        result.append(display or canonical)

    return result


def add_semantic_evidence(
    semantic_matches: List[str],
    semantic_match_details: List[str],
    evidence_items: List[EvidenceItem],
    name: str,
    detail: str,
    target_text: str,
    source_text: str,
    source_type: str,
    match_method: str,
    similarity: float,
) -> None:
    if name and name not in semantic_matches:
        semantic_matches.append(name)

    if detail and detail not in semantic_match_details:
        semantic_match_details.append(detail)

    exists = any(
        item.target_text == target_text
        and item.source_text == source_text
        and item.match_method == match_method
        for item in evidence_items
    )

    if not exists:
        evidence_items.append(
            EvidenceItem(
                title=name,
                target_text=target_text,
                source_text=source_text,
                source_type=source_type,
                match_method=match_method,
                similarity=round(float(similarity), 4),
                explanation=detail,
            )
        )


def calculate_match_score(resume: ResumeInfo, jd: JDInfo) -> MatchResult:
    """
    V2.5 混合匹配算法。

    总分 100：
    1. 必备技能匹配：50 分
    2. 加分技能匹配：20 分
    3. 项目相关度：20 分
    4. JD 关键词覆盖：10 分

    匹配方式：
    - 规则别名匹配
    - 模糊字符串匹配
    - TF-IDF 相似度
    - Embedding 语义相似度
    """

    resume_skills = unique_keep_order(resume.skills)
    required_skills = unique_keep_order(jd.required_skills)
    preferred_skills = unique_keep_order(jd.preferred_skills)
    jd_keywords = unique_keep_order(jd.keywords)

    resume_skill_set = to_canonical_set(resume_skills)
    required_skill_set = to_canonical_set(required_skills)
    preferred_skill_set = to_canonical_set(preferred_skills)

    resume_skill_map = build_canonical_display_map(resume_skills)
    required_skill_map = build_canonical_display_map(required_skills)
    preferred_skill_map = build_canonical_display_map(preferred_skills)
    keyword_map = build_canonical_display_map(jd_keywords)

    matched_required = resume_skill_set & required_skill_set
    matched_preferred = resume_skill_set & preferred_skill_set

    missing_required = required_skill_set - resume_skill_set
    missing_preferred = preferred_skill_set - resume_skill_set

    resume_full_text_norm = normalize_text(flatten_resume_text(resume))
    project_text_norm = normalize_text(flatten_project_text(resume))

    resume_semantic_candidates = build_resume_semantic_candidates(resume)
    project_semantic_candidates = build_project_semantic_candidates(resume)

    semantic_matches = []
    semantic_match_details = []
    evidence_items = []

    semantic_required_matched = set()

    for missing_item in list(missing_required):
        display_name = required_skill_map.get(missing_item, missing_item)

        matched, semantic_score, matched_text, method = is_semantic_match(
            display_name,
            resume_semantic_candidates,
            threshold=0.56,
        )

        if matched:
            semantic_required_matched.add(missing_item)

            detail = (
                f"必备技能「{display_name}」与简历内容「{matched_text}」"
                f"通过 {method} 匹配，相似度 {semantic_score:.2f}"
            )

            add_semantic_evidence(
                semantic_matches,
                semantic_match_details,
                evidence_items,
                display_name,
                detail,
                display_name,
                matched_text,
                "resume",
                method,
                semantic_score,
            )

    missing_required = missing_required - semantic_required_matched
    matched_required = matched_required | semantic_required_matched

    semantic_preferred_matched = set()

    for missing_item in list(missing_preferred):
        display_name = preferred_skill_map.get(missing_item, missing_item)

        matched, semantic_score, matched_text, method = is_semantic_match(
            display_name,
            resume_semantic_candidates,
            threshold=0.56,
        )

        if matched:
            semantic_preferred_matched.add(missing_item)

            detail = (
                f"加分技能「{display_name}」与简历内容「{matched_text}」"
                f"通过 {method} 匹配，相似度 {semantic_score:.2f}"
            )

            add_semantic_evidence(
                semantic_matches,
                semantic_match_details,
                evidence_items,
                display_name,
                detail,
                display_name,
                matched_text,
                "resume",
                method,
                semantic_score,
            )

    missing_preferred = missing_preferred - semantic_preferred_matched
    matched_preferred = matched_preferred | semantic_preferred_matched

    required_skill_score = calculate_ratio_score(
        matched_count=len(matched_required),
        total_count=len(required_skill_set),
        max_score=50,
        full_score_when_empty=True,
    )

    preferred_skill_score = calculate_ratio_score(
        matched_count=len(matched_preferred),
        total_count=len(preferred_skill_set),
        max_score=20,
        full_score_when_empty=True,
    )

    project_target_terms = unique_keep_order(
        required_skills + preferred_skills + jd_keywords
    )
    project_target_set = to_canonical_set(project_target_terms)
    project_target_map = build_canonical_display_map(project_target_terms)

    project_related_set = set()

    for item in project_target_set:
        display_name = project_target_map.get(item, item)

        if canonical_term_appears_in_text(item, project_text_norm):
            project_related_set.add(item)
            continue

        matched, semantic_score, matched_text, method = is_semantic_match(
            display_name,
            project_semantic_candidates,
            threshold=0.50,
        )

        if matched:
            project_related_set.add(item)

            detail = (
                f"项目相关词「{display_name}」与项目内容「{matched_text}」"
                f"通过 {method} 匹配，相似度 {semantic_score:.2f}"
            )

            add_semantic_evidence(
                semantic_matches,
                semantic_match_details,
                evidence_items,
                display_name,
                detail,
                display_name,
                matched_text,
                "project",
                method,
                semantic_score,
            )

    project_relevance_score = calculate_ratio_score(
        matched_count=len(project_related_set),
        total_count=len(project_target_set),
        max_score=20,
        full_score_when_empty=True,
    )

    keyword_set = to_canonical_set(jd_keywords)

    covered_keyword_set = set()

    for item in keyword_set:
        display_name = keyword_map.get(item, item)

        if canonical_term_appears_in_text(item, resume_full_text_norm):
            covered_keyword_set.add(item)
            continue

        matched, semantic_score, matched_text, method = is_semantic_match(
            display_name,
            resume_semantic_candidates,
            threshold=0.50,
        )

        if matched:
            covered_keyword_set.add(item)

            detail = (
                f"JD关键词「{display_name}」与简历内容「{matched_text}」"
                f"通过 {method} 匹配，相似度 {semantic_score:.2f}"
            )

            add_semantic_evidence(
                semantic_matches,
                semantic_match_details,
                evidence_items,
                display_name,
                detail,
                display_name,
                matched_text,
                "resume",
                method,
                semantic_score,
            )

    missing_keyword_set = keyword_set - covered_keyword_set

    keyword_coverage_score = calculate_ratio_score(
        matched_count=len(covered_keyword_set),
        total_count=len(keyword_set),
        max_score=10,
        full_score_when_empty=True,
    )

    total_score = (
        required_skill_score
        + preferred_skill_score
        + project_relevance_score
        + keyword_coverage_score
    )
    total_score = max(0, min(100, total_score))

    matched_skill_set = matched_required | matched_preferred

    matched_skills = display_terms(
        matched_skill_set,
        resume_skill_map,
        required_skill_map,
        preferred_skill_map,
    )

    missing_required_skills = display_terms(
        missing_required,
        required_skill_map,
    )

    missing_preferred_skills = display_terms(
        missing_preferred,
        preferred_skill_map,
    )

    project_related_keywords = display_terms(
        project_related_set,
        project_target_map,
        required_skill_map,
        preferred_skill_map,
        keyword_map,
    )

    covered_keywords = display_terms(
        covered_keyword_set,
        keyword_map,
    )

    missing_keywords = display_terms(
        missing_keyword_set,
        keyword_map,
    )

    score_breakdown = [
        ScoreDimension(
            name="必备技能匹配",
            score=required_skill_score,
            max_score=50,
            explanation=(
                f"必备技能匹配 {len(matched_required)}/{len(required_skill_set)}，"
                f"包含规则别名、模糊匹配、TF-IDF 和 Embedding 语义匹配。"
                if required_skill_set
                else "JD 未提取到必备技能，该项不扣分。"
            ),
        ),
        ScoreDimension(
            name="加分技能匹配",
            score=preferred_skill_score,
            max_score=20,
            explanation=(
                f"加分技能匹配 {len(matched_preferred)}/{len(preferred_skill_set)}，"
                f"包含规则别名、模糊匹配、TF-IDF 和 Embedding 语义匹配。"
                if preferred_skill_set
                else "JD 未提取到加分技能，该项不扣分。"
            ),
        ),
        ScoreDimension(
            name="项目相关度",
            score=project_relevance_score,
            max_score=20,
            explanation=(
                f"项目经历覆盖岗位相关技术/关键词 {len(project_related_set)}/{len(project_target_set)}，"
                f"包含关键词命中和语义相似度判断。"
                if project_target_set
                else "岗位相关技术关键词不足，该项不扣分。"
            ),
        ),
        ScoreDimension(
            name="JD关键词覆盖",
            score=keyword_coverage_score,
            max_score=10,
            explanation=(
                f"简历覆盖 JD 关键词 {len(covered_keyword_set)}/{len(keyword_set)}，"
                f"包含关键词命中和语义相似度判断。"
                if keyword_set
                else "JD 未提取到关键词，该项不扣分。"
            ),
        ),
    ]

    ats_report = run_ats_check(resume)

    explanation = (
        f"综合匹配分 {total_score}/100。"
        f"必备技能 {required_skill_score}/50，"
        f"加分技能 {preferred_skill_score}/20，"
        f"项目相关度 {project_relevance_score}/20，"
        f"关键词覆盖 {keyword_coverage_score}/10。"
        f"系统已启用规则别名匹配、模糊匹配、TF-IDF 和 Embedding 语义匹配，并生成结构化证据链。"
    )

    return MatchResult(
        score=total_score,
        matched_skills=matched_skills,
        missing_required_skills=missing_required_skills,
        missing_preferred_skills=missing_preferred_skills,
        explanation=explanation,
        required_skill_score=required_skill_score,
        preferred_skill_score=preferred_skill_score,
        project_relevance_score=project_relevance_score,
        keyword_coverage_score=keyword_coverage_score,
        score_breakdown=score_breakdown,
        project_related_keywords=project_related_keywords,
        covered_keywords=covered_keywords,
        missing_keywords=missing_keywords,
        semantic_matches=semantic_matches,
        semantic_match_details=semantic_match_details,
        evidence_items=evidence_items,
        ats_report=ats_report,
    )