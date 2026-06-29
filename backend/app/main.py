import tempfile
from pathlib import Path

from fastapi import FastAPI, UploadFile, File, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware

from app.parsers import parse_resume
from app.extractors import (
    extract_resume_info,
    extract_jd_info,
    get_current_model_name,
    get_current_thinking_mode,
)
from app.matcher import calculate_match_score
from app.reporter import generate_report, structured_report_to_markdown


tags_metadata = [
    {
        "name": "系统状态",
        "description": "用于检查后端服务是否正常运行，以及查看当前模型配置。",
    },
    {
        "name": "求职分析",
        "description": "上传简历和岗位 JD，生成匹配度、技能缺口、简历优化建议和面试题。",
    },
]


app = FastAPI(
    title="JobFit Agent 智能求职分析系统",
    description="""
JobFit Agent 是一个面向计算机实习求职场景的智能分析系统。

核心能力：
- 上传 PDF / DOCX / TXT 简历
- 解析岗位 JD
- 提取简历技能、项目经历、实习经历
- 计算简历与岗位的匹配度
- 分析已匹配技能和缺失技能
- 生成结构化求职分析报告
- 生成简历改写建议
- 生成面试题预测
""",
    version="0.3.0",
    openapi_tags=tags_metadata,
    swagger_ui_parameters={
        "docExpansion": "list",
        "defaultModelsExpandDepth": -1,
        "displayRequestDuration": True,
        "filter": True,
    },
)


app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5173",
        "http://127.0.0.1:5173",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


ALLOWED_EXTENSIONS = {".pdf", ".docx", ".txt"}
MAX_UPLOAD_SIZE = 10 * 1024 * 1024  # 10MB


@app.get(
    "/",
    tags=["系统状态"],
    summary="健康检查",
    description="用于测试 JobFit Agent 后端服务是否已经成功启动。",
)
def health_check():
    return {
        "message": "JobFit Agent 后端服务运行正常",
        "status": "ok",
    }


@app.get(
    "/api/model-info",
    tags=["系统状态"],
    summary="查看当前接入模型",
    description="查看当前后端配置的模型名称和 thinking 模式，不会返回 API Key。",
)
def model_info():
    return {
        "provider": "DeepSeek",
        "model": get_current_model_name(),
        "thinking": get_current_thinking_mode(),
        "api_key_loaded": True,
    }


@app.post(
    "/api/analyze",
    tags=["求职分析"],
    summary="上传简历并分析岗位匹配度",
    description="""
上传一份简历文件，并填写目标岗位 JD。

系统会自动完成：
1. 简历文本解析
2. 简历结构化提取
3. 岗位 JD 结构化提取
4. 技能匹配度计算
5. 技能缺口分析
6. 结构化报告生成
7. 简历改写建议生成
8. 面试题预测
""",
)
async def analyze_resume(
    resume_file: UploadFile = File(
        ...,
        description="请上传 PDF、DOCX 或 TXT 格式的简历文件",
    ),
    jd_text: str = Form(
        ...,
        description="请粘贴目标岗位的完整 JD 文本",
    ),
):
    filename = resume_file.filename or ""
    suffix = Path(filename).suffix.lower()
    tmp_path = None

    if suffix not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail="文件格式不支持，请上传 PDF、DOCX 或 TXT 格式的简历。",
        )

    if not jd_text.strip():
        raise HTTPException(
            status_code=400,
            detail="岗位 JD 不能为空，请粘贴完整岗位描述。",
        )

    try:
        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
            tmp_path = tmp.name

            content = await resume_file.read()

            if not content:
                raise HTTPException(
                    status_code=400,
                    detail="上传的简历文件为空，请重新选择文件。",
                )

            if len(content) > MAX_UPLOAD_SIZE:
                raise HTTPException(
                    status_code=413,
                    detail="简历文件过大，请上传 10MB 以内的文件。",
                )

            tmp.write(content)

        resume_text = parse_resume(tmp_path)

        if not resume_text.strip():
            raise HTTPException(
                status_code=400,
                detail="未能从简历中解析出有效文本，请检查文件内容，或换成 DOCX/TXT 格式。",
            )

        resume_info = extract_resume_info(resume_text)
        jd_info = extract_jd_info(jd_text)

        match_result = calculate_match_score(
            resume=resume_info,
            jd=jd_info,
        )

        structured_report = generate_report(
            resume=resume_info,
            jd=jd_info,
            match_result=match_result,
        )

        report_text = structured_report_to_markdown(structured_report)

        return {
            "message": "分析成功",
            "provider": "DeepSeek",
            "model": get_current_model_name(),
            "thinking": get_current_thinking_mode(),
            "resume_info": resume_info.model_dump(),
            "jd_info": jd_info.model_dump(),
            "match_result": match_result.model_dump(),
            "report_json": structured_report.model_dump(),
            "report": report_text,
        }

    finally:
        if tmp_path:
            Path(tmp_path).unlink(missing_ok=True)