\# JobFit Agent



JobFit Agent 是一个面向求职场景的智能简历-JD 匹配分析系统。系统支持上传简历、粘贴岗位 JD，自动生成岗位匹配分、技能缺口、ATS 兼容性检查、语义匹配证据、简历改写建议、学习计划和面试题预测。



\## 核心功能



\- 简历上传与岗位 JD 分析

\- 简历与 JD 的结构化解析

\- 四维岗位匹配评分

\- 必备技能、加分技能、项目相关度和 JD 关键词覆盖度拆解

\- 技能别名归一化、模糊匹配、TF-IDF 相似度和本地可选 Embedding 匹配

\- 结构化证据链追踪

\- ATS 兼容性检查

\- 简历改写前后对比与幻觉风险标注

\- 多 JD 岗位适配度排序

\- 分析历史记录与报告导出

\- Windows 一键启动前端和后端



\## 技术栈



\- Frontend: React, Vite, Axios, CSS

\- Backend: FastAPI, Pydantic, Python

\- Matching: RapidFuzz, scikit-learn TF-IDF, optional sentence-transformers embedding

\- LLM: DeepSeek API

\- Storage: Browser LocalStorage



\## 项目亮点



1\. 设计四维岗位匹配评分模型，将匹配度拆解为必备技能、加分技能、项目相关度和关键词覆盖度。

2\. 实现混合匹配算法，结合技能别名归一化、模糊匹配、TF-IDF 相似度和本地可选 Embedding 语义匹配。

3\. 设计结构化证据链 EvidenceItem，将匹配结果关联到 JD 目标文本、简历依据、匹配方法和相似度。

4\. 在简历改写模块中加入 evidence 和 risk\_level 字段，降低生成式 AI 编造经历的风险。

5\. 支持快速模式和本地 Embedding 模式，并在模型不可用时自动降级到轻量匹配方案。

6\. 支持一份简历与多个 JD 进行对比分析，生成岗位适配度排序。

7\. 提供 Windows 一键启动脚本，降低本地运行成本。



\## 本地运行



\### 1. 安装依赖



首次运行：



```bash

setup\_once.bat

