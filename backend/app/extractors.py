import os
from pathlib import Path

from dotenv import load_dotenv
from langchain_deepseek import ChatDeepSeek

from app.schemas import ResumeInfo, JDInfo


# 读取 backend/.env
BASE_DIR = Path(__file__).resolve().parents[1]
ENV_PATH = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_PATH)


deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
deepseek_model = os.getenv("DEEPSEEK_MODEL", "deepseek-v4-flash")
deepseek_thinking = os.getenv("DEEPSEEK_THINKING", "disabled").lower()


if not deepseek_api_key:
    raise RuntimeError(
        "没有读取到 DEEPSEEK_API_KEY。请检查 backend/.env 文件是否存在，"
        "以及里面是否写了 DEEPSEEK_API_KEY=你的key"
    )


def build_deepseek_llm() -> ChatDeepSeek:
    """
    初始化 DeepSeek 模型。

    当前项目使用 deepseek-v4-flash，并默认关闭 thinking 模式：
    1. 响应更快；
    2. 成本更低；
    3. 更适合简历解析、JD 解析、JSON 结构化输出这类任务。
    """

    extra_body = {
        "thinking": {
            "type": deepseek_thinking
        }
    }

    return ChatDeepSeek(
        model=deepseek_model,
        temperature=0,
        api_key=deepseek_api_key,
        max_retries=2,
        timeout=60,
        extra_body=extra_body,
    )


llm = build_deepseek_llm()


def get_current_model_name() -> str:
    return deepseek_model


def get_current_thinking_mode() -> str:
    return deepseek_thinking


def extract_resume_info(resume_text: str) -> ResumeInfo:
    structured_llm = llm.with_structured_output(ResumeInfo)

    prompt = f"""
你是一个专业的中文技术简历解析助手。

请从下面的简历文本中提取结构化信息。

要求：
1. 不要编造简历中不存在的信息。
2. 技能必须来自原文。
3. 项目经历要提取项目名称、技术栈、职责、成果。
4. 如果某字段不存在，返回空数组或空字符串。
5. 请严格按照指定结构返回结果。

简历文本：
{resume_text}
"""

    return structured_llm.invoke(prompt)


def extract_jd_info(jd_text: str) -> JDInfo:
    structured_llm = llm.with_structured_output(JDInfo)

    prompt = f"""
你是一个岗位 JD 分析助手。

请从下面的岗位描述中提取结构化信息。

要求：
1. required_skills 表示岗位明确要求的技能。
2. preferred_skills 表示加分项。
3. keywords 表示 JD 中重要关键词。
4. responsibilities 表示岗位职责。
5. 不要编造 JD 中不存在的信息。
6. 请严格按照指定结构返回结果。

岗位描述：
{jd_text}
"""

    return structured_llm.invoke(prompt)