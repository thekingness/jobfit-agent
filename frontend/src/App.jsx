import { useEffect, useState } from "react";
import axios from "axios";
import "./App.css";

const API_URL = "http://127.0.0.1:8000/api/analyze";
const HISTORY_KEY = "jobfit_analysis_history_v25";

function App() {
  const [resumeFile, setResumeFile] = useState(null);
  const [fileInputKey, setFileInputKey] = useState(Date.now());
  const [jdText, setJdText] = useState("");
  const [result, setResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [errorMsg, setErrorMsg] = useState("");
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [multiJdMode, setMultiJdMode] = useState(false);
  const [multiResults, setMultiResults] = useState([]);
  const [progressText, setProgressText] = useState("");

  useEffect(() => {
    try {
      const savedHistory = localStorage.getItem(HISTORY_KEY);
      if (savedHistory) {
        setAnalysisHistory(JSON.parse(savedHistory));
      }
    } catch (error) {
      console.error("读取历史记录失败：", error);
      setAnalysisHistory([]);
    }
  }, []);

  const saveHistory = (newHistory) => {
    setAnalysisHistory(newHistory);

    try {
      localStorage.setItem(HISTORY_KEY, JSON.stringify(newHistory));
    } catch (error) {
      console.error("保存历史记录失败：", error);
    }
  };

  const buildHistoryItem = (responseData, sourceType = "单岗位分析") => {
    const now = new Date();

    const resumeName =
      responseData?.resume_info?.name ||
      resumeFile?.name ||
      "未命名简历";

    const position =
      responseData?.jd_info?.position ||
      "未知岗位";

    const score =
      responseData?.match_result?.score ?? 0;

    return {
      id: `${Date.now()}-${Math.random().toString(16).slice(2)}`,
      created_at: now.toLocaleString(),
      resume_name: resumeName,
      position,
      score,
      source_type: sourceType,
      result: responseData,
    };
  };

  const addToHistory = (responseData, sourceType = "单岗位分析") => {
    const item = buildHistoryItem(responseData, sourceType);

    const newHistory = [
      item,
      ...analysisHistory,
    ].slice(0, 12);

    saveHistory(newHistory);
  };

  const addBatchToHistory = (items) => {
    const newItems = items.map((item) =>
      buildHistoryItem(item.result, "多岗位对比")
    );

    const newHistory = [
      ...newItems,
      ...analysisHistory,
    ].slice(0, 12);

    saveHistory(newHistory);
  };

  const handleLoadHistory = (item) => {
    setResult(item.result);
    setErrorMsg("");
    setMultiResults([]);
  };

  const handleDeleteHistory = (id) => {
    const newHistory = analysisHistory.filter((item) => item.id !== id);
    saveHistory(newHistory);
  };

  const handleClearHistory = () => {
    saveHistory([]);
  };

  const fillDemoJD = () => {
    setMultiJdMode(false);
    setJdText(`岗位名称：Java 后端开发实习生

岗位职责：
1. 参与后端接口开发和业务模块实现；
2. 参与数据库表设计和 SQL 优化；
3. 配合前端完成接口联调；
4. 参与系统性能优化和问题排查。

任职要求：
1. 熟悉 Java 基础；
2. 熟悉 Spring Boot、MyBatis 等后端开发框架；
3. 熟悉 MySQL 数据库；
4. 了解 Redis、Linux、Docker 者优先；
5. 有完整后端项目经验者优先。`);
  };

  const fillDemoMultiJD = () => {
    setMultiJdMode(true);
    setJdText(`岗位名称：Java 后端开发实习生

岗位职责：
1. 参与后端接口开发和业务模块实现；
2. 参与数据库表设计和 SQL 优化；
3. 配合前端完成接口联调；
4. 参与系统性能优化和问题排查。

任职要求：
1. 熟悉 Java 基础；
2. 熟悉 Spring Boot、MyBatis 等后端开发框架；
3. 熟悉 MySQL 数据库；
4. 了解 Redis、Linux、Docker 者优先；
5. 有完整后端项目经验者优先。

---

岗位名称：AI 应用开发实习生

岗位职责：
1. 参与 AI Agent、RAG、智能问答系统开发；
2. 负责大模型 API 调用、提示词优化和结果解析；
3. 参与向量数据库检索和知识库构建；
4. 配合前端完成 AI 应用功能联调。

任职要求：
1. 熟悉 Python；
2. 了解 FastAPI、LangChain、RAG、向量数据库；
3. 了解大模型应用开发流程；
4. 有 AI 项目或智能体项目经验优先。

---

岗位名称：前端开发实习生

岗位职责：
1. 负责 Web 页面开发和交互实现；
2. 根据产品需求完成前端组件开发；
3. 与后端进行接口联调；
4. 优化页面体验和响应速度。

任职要求：
1. 熟悉 HTML、CSS、JavaScript；
2. 熟悉 React 或 Vue；
3. 了解 Axios、Vite、组件化开发；
4. 有完整前端项目经验优先。`);
  };

  const splitMultiJDText = (text) => {
    if (!text.trim()) return [];

    let parts = text
      .split(/\n\s*(?:-{3,}|={3,}|#{3,})\s*\n/g)
      .map((item) => item.trim())
      .filter(Boolean);

    if (parts.length <= 1) {
      parts = text
        .split(/(?=岗位名称[:：])/g)
        .map((item) => item.trim())
        .filter(Boolean);
    }

    return parts;
  };

  const requestAnalyze = async (singleJDText) => {
    const formData = new FormData();
    formData.append("resume_file", resumeFile);
    formData.append("jd_text", singleJDText);

    const response = await axios.post(API_URL, formData, {
      headers: {
        "Content-Type": "multipart/form-data",
      },
    });

    return response.data;
  };

  const getBackendErrorMessage = (error) => {
    return (
      error?.response?.data?.detail ||
      error?.response?.data?.message ||
      "分析失败。请检查后端服务是否启动，或查看后端命令行报错信息。"
    );
  };

  const handleAnalyze = async () => {
    if (!resumeFile) {
      setErrorMsg("请先上传简历文件");
      return;
    }

    if (!jdText.trim()) {
      setErrorMsg("请填写岗位 JD");
      return;
    }

    if (multiJdMode) {
      await handleAnalyzeMultiJD();
    } else {
      await handleAnalyzeSingleJD();
    }
  };

  const handleAnalyzeSingleJD = async () => {
    setLoading(true);
    setProgressText("正在分析当前岗位...");
    setErrorMsg("");
    setResult(null);
    setMultiResults([]);

    try {
      const responseData = await requestAnalyze(jdText);

      setResult(responseData);
      addToHistory(responseData, "单岗位分析");
    } catch (error) {
      console.error(error);
      setErrorMsg(getBackendErrorMessage(error));
    } finally {
      setLoading(false);
      setProgressText("");
    }
  };

  const handleAnalyzeMultiJD = async () => {
    const jdList = splitMultiJDText(jdText);

    if (jdList.length < 2) {
      setErrorMsg("多 JD 对比模式下，请至少输入 2 个 JD。可以用 --- 分隔不同岗位。");
      return;
    }

    setLoading(true);
    setErrorMsg("");
    setResult(null);
    setMultiResults([]);

    try {
      const tempResults = [];

      for (let index = 0; index < jdList.length; index += 1) {
        setProgressText(`正在分析第 ${index + 1}/${jdList.length} 个岗位...`);

        const responseData = await requestAnalyze(jdList[index]);

        const score = responseData?.match_result?.score ?? 0;
        const position = responseData?.jd_info?.position || `岗位 ${index + 1}`;

        tempResults.push({
          id: `${Date.now()}-${index}`,
          index,
          position,
          score,
          jd_text: jdList[index],
          result: responseData,
        });
      }

      const sortedResults = [...tempResults].sort((a, b) => b.score - a.score);

      setMultiResults(sortedResults);
      setResult(sortedResults[0]?.result || null);
      addBatchToHistory(sortedResults);
    } catch (error) {
      console.error(error);
      setErrorMsg(getBackendErrorMessage(error));
    } finally {
      setLoading(false);
      setProgressText("");
    }
  };

  const handleReset = () => {
    setResumeFile(null);
    setFileInputKey(Date.now());
    setJdText("");
    setResult(null);
    setErrorMsg("");
    setMultiResults([]);
    setProgressText("");
  };

  const handleExportReport = () => {
    window.print();
  };

  const score = result?.match_result?.score ?? 0;
  const matchedSkills = result?.match_result?.matched_skills || [];
  const missingRequired = result?.match_result?.missing_required_skills || [];
  const missingPreferred = result?.match_result?.missing_preferred_skills || [];
  const scoreBreakdown = result?.match_result?.score_breakdown || [];
  const projectRelatedKeywords = result?.match_result?.project_related_keywords || [];
  const coveredKeywords = result?.match_result?.covered_keywords || [];
  const missingKeywords = result?.match_result?.missing_keywords || [];
  const semanticMatches = result?.match_result?.semantic_matches || [];
  const semanticMatchDetails = result?.match_result?.semantic_match_details || [];
  const evidenceItems = result?.match_result?.evidence_items || [];
  const backendATSReport = result?.match_result?.ats_report || null;

  const resumeInfo = result?.resume_info || {};
  const jdInfo = result?.jd_info || {};

  const report = result?.report_json || {};
  const advantages = report.advantages || [];
  const skillGaps = report.skill_gaps || [];
  const projectSuggestions = report.project_suggestions || [];
  const rewriteSuggestions = report.rewrite_suggestions || [];
  const learningPlan = report.learning_plan || [];
  const interviewQuestions = report.interview_questions || [];
  const riskTips = report.risk_tips || [];

  return (
    <div className="page">
      <header className="hero">
        <div className="hero-inner">
          <div className="hero-badge">JobFit Agent V2.5</div>
          <h1>智能求职分析系统</h1>
          <p>
            支持单岗位分析、多 JD 对比、ATS 检查、Embedding 语义匹配、结构化证据链、简历改写建议和面试题预测。
          </p>
        </div>
      </header>

      <main className="main-layout">
        <section className="left-panel no-print">
          <div className="card">
            <h2>开始分析</h2>

            <div className="mode-switch">
              <button
                className={!multiJdMode ? "mode-btn active" : "mode-btn"}
                onClick={() => setMultiJdMode(false)}
              >
                单 JD 分析
              </button>
              <button
                className={multiJdMode ? "mode-btn active" : "mode-btn"}
                onClick={() => setMultiJdMode(true)}
              >
                多 JD 对比
              </button>
            </div>

            <div className="form-group">
              <label>1. 上传简历</label>
              <div className="file-box">
                <input
                  key={fileInputKey}
                  type="file"
                  accept=".pdf,.docx,.txt"
                  onChange={(e) => setResumeFile(e.target.files[0])}
                />
              </div>
              <p className="hint">
                支持 PDF、DOCX、TXT。建议上传包含技能栈、项目经历、实习经历的简历。
              </p>
            </div>

            <div className="form-group">
              <div className="label-row">
                <label>
                  {multiJdMode ? "2. 粘贴多个岗位 JD" : "2. 粘贴目标岗位 JD"}
                </label>
                <div className="label-actions">
                  <button type="button" className="link-btn" onClick={fillDemoJD}>
                    单 JD 示例
                  </button>
                  <button type="button" className="link-btn" onClick={fillDemoMultiJD}>
                    多 JD 示例
                  </button>
                </div>
              </div>

              <textarea
                value={jdText}
                onChange={(e) => setJdText(e.target.value)}
                placeholder={
                  multiJdMode
                    ? "请粘贴多个 JD，并用 --- 分隔不同岗位..."
                    : "请粘贴岗位职责、任职要求、技术栈等内容..."
                }
              />

              {multiJdMode && (
                <p className="hint">
                  多 JD 对比模式下，用三条横线 --- 分隔不同岗位。系统会逐个分析并按匹配分排序。
                </p>
              )}
            </div>

            {errorMsg && <div className="error-box">{errorMsg}</div>}

            {progressText && <div className="progress-box">{progressText}</div>}

            <button className="primary-btn" onClick={handleAnalyze} disabled={loading}>
              {loading
                ? "正在分析，请稍等..."
                : multiJdMode
                  ? "开始多 JD 对比"
                  : "开始智能分析"}
            </button>
          </div>

          <HistoryPanel
            history={analysisHistory}
            onLoad={handleLoadHistory}
            onDelete={handleDeleteHistory}
            onClear={handleClearHistory}
          />
        </section>

        <section className="right-panel">
          {!result && (
            <div className="empty-state">
              <div className="empty-icon">📄</div>
              <h2>等待分析</h2>
              <p>
                上传简历并填写岗位 JD 后，这里会展示匹配分、岗位对比、ATS 检查、语义匹配证据、结构化证据链、简历改写建议和面试题预测。
              </p>
            </div>
          )}

          {result && (
            <>
              <div className="action-bar no-print">
                <button className="secondary-btn" onClick={handleReset}>
                  重新分析
                </button>
                <button className="export-btn" onClick={handleExportReport}>
                  导出报告 / 保存 PDF
                </button>
              </div>

              {multiResults.length > 0 && (
                <MultiJDCompareCard
                  items={multiResults}
                  currentResult={result}
                  onSelect={(item) => setResult(item.result)}
                />
              )}

              <div className="overview-card">
                <div className="score-ring">
                  <span>{score}</span>
                  <small>匹配分</small>
                </div>

                <div className="overview-content">
                  <h2>岗位匹配分析完成</h2>
                  <p>{result.match_result?.explanation}</p>

                  <div className="meta-row">
                    <span>
                      模型：{result.provider || "DeepSeek"} / {result.model || "未知模型"}
                    </span>
                    <span>Thinking：{result.thinking || "未知"}</span>
                  </div>
                </div>
              </div>

              <ATSCheckCard
                resumeFile={resumeFile}
                resumeInfo={resumeInfo}
                atsReport={backendATSReport}
              />

              <ScoreBreakdownCard items={scoreBreakdown} />

              <SummaryCards resumeInfo={resumeInfo} jdInfo={jdInfo} />

              <div className="skill-grid">
                <SkillCard
                  title="已匹配技能"
                  type="success"
                  items={matchedSkills}
                  empty="暂无明显匹配技能"
                />
                <SkillCard
                  title="缺失必备技能"
                  type="danger"
                  items={missingRequired}
                  empty="必备技能匹配较好"
                />
                <SkillCard
                  title="缺失加分技能"
                  type="warning"
                  items={missingPreferred}
                  empty="暂无明显缺失加分项"
                />
              </div>

              <KeywordPanel
                projectRelatedKeywords={projectRelatedKeywords}
                coveredKeywords={coveredKeywords}
                missingKeywords={missingKeywords}
              />

              <EvidenceChainCard
                semanticMatchDetails={semanticMatchDetails}
                rewriteSuggestions={rewriteSuggestions}
                evidenceItems={evidenceItems}
              />

              <SemanticMatchCard
                semanticMatches={semanticMatches}
                semanticMatchDetails={semanticMatchDetails}
              />

              <section className="report-section">
                <div className="section-title">
                  <p>Analysis Report</p>
                  <h2>结构化求职分析报告</h2>
                </div>

                <div className="report-card">
                  <h3>总体评价</h3>
                  <p>{report.overall_review || "暂无总体评价"}</p>
                </div>

                <TwoColumnCards
                  leftTitle="匹配优势"
                  leftItems={advantages}
                  rightTitle="技能缺口"
                  rightItems={skillGaps}
                />

                <ListCard
                  title="项目经历优化建议"
                  items={projectSuggestions}
                  empty="暂无项目优化建议"
                />

                <RewriteCard suggestions={rewriteSuggestions} />

                <ListCard
                  title="学习计划"
                  items={learningPlan}
                  empty="暂无学习计划"
                />

                <InterviewCard questions={interviewQuestions} />

                <ListCard
                  title="风险提示"
                  items={riskTips}
                  empty="请注意不要在简历中添加没有实际经历支撑的内容。"
                />
              </section>
            </>
          )}
        </section>
      </main>
    </div>
  );
}

function HistoryPanel({ history, onLoad, onDelete, onClear }) {
  return (
    <div className="history-card">
      <div className="history-header">
        <div>
          <h3>分析历史</h3>
          <p>最近 12 次分析会自动保存在本地浏览器中。</p>
        </div>

        {history.length > 0 && (
          <button className="history-clear-btn" onClick={onClear}>
            清空
          </button>
        )}
      </div>

      {history.length === 0 && (
        <div className="history-empty">
          暂无历史记录。完成一次分析后会自动保存。
        </div>
      )}

      {history.length > 0 && (
        <div className="history-list">
          {history.map((item) => (
            <div className="history-item" key={item.id}>
              <button className="history-main" onClick={() => onLoad(item)}>
                <div className="history-top">
                  <strong>{item.position}</strong>
                  <span>{item.score} 分</span>
                </div>

                <p>{item.resume_name}</p>
                <small>{item.source_type || "分析记录"} · {item.created_at}</small>
              </button>

              <button
                className="history-delete-btn"
                onClick={() => onDelete(item.id)}
                title="删除该记录"
              >
                ×
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}

function MultiJDCompareCard({ items, currentResult, onSelect }) {
  const currentPosition = currentResult?.jd_info?.position || "";

  return (
    <div className="multi-compare-card">
      <div className="multi-compare-header">
        <div>
          <h3>多 JD 岗位适配度排序</h3>
          <p>系统已按匹配分从高到低排序，点击任意岗位可查看对应完整报告。</p>
        </div>
        <span>{items.length} 个岗位</span>
      </div>

      <div className="multi-rank-list">
        {items.map((item, index) => {
          const active = item.position === currentPosition;

          return (
            <button
              key={item.id}
              className={active ? "multi-rank-item active" : "multi-rank-item"}
              onClick={() => onSelect(item)}
            >
              <div className="rank-number">#{index + 1}</div>

              <div className="rank-content">
                <strong>{item.position}</strong>
                <p>
                  {index === 0
                    ? "当前最推荐投递岗位"
                    : "可作为备选岗位继续优化简历"}
                </p>
              </div>

              <div className="rank-score">{item.score}</div>
            </button>
          );
        })}
      </div>
    </div>
  );
}

function ATSCheckCard({ resumeFile, resumeInfo, atsReport }) {
  if (atsReport) {
    const finalScore = atsReport.ats_score ?? 0;
    const issues = atsReport.issues || [];
    const suggestions = atsReport.suggestions || [];

    return (
      <div className="ats-card">
        <div className="ats-score-box">
          <span>{finalScore}</span>
          <small>ATS 兼容分</small>
        </div>

        <div className="ats-content">
          <h3>ATS 兼容性检查</h3>
          <p>
            {atsReport.summary || "系统已基于后端结构化解析结果生成 ATS 兼容性评估。"}
          </p>

          <div className="ats-check-list">
            {issues.map((item, index) => (
              <div
                className={`ats-check-item ${
                  item.status === "danger"
                    ? "bad"
                    : item.status === "good"
                      ? "good"
                      : "warn"
                }`}
                key={index}
              >
                <strong>{item.title}</strong>
                <p>{item.message}</p>
              </div>
            ))}
          </div>

          {suggestions.length > 0 && (
            <div className="ats-suggestions">
              <h4>ATS 优化建议</h4>
              <ul className="clean-list">
                {suggestions.map((item, index) => (
                  <li key={index}>{item}</li>
                ))}
              </ul>
            </div>
          )}
        </div>
      </div>
    );
  }

  const checks = buildATSChecks(resumeFile, resumeInfo);
  const score = checks.reduce((sum, item) => sum + item.score, 0);
  const finalScore = Math.max(0, Math.min(100, score));

  return (
    <div className="ats-card">
      <div className="ats-score-box">
        <span>{finalScore}</span>
        <small>ATS 兼容分</small>
      </div>

      <div className="ats-content">
        <h3>ATS 兼容性检查</h3>
        <p>
          该检查基于文件类型、结构化解析结果、技能区、项目区和成果量化情况进行轻量评估。
        </p>

        <div className="ats-check-list">
          {checks.map((item, index) => (
            <div className={`ats-check-item ${item.type}`} key={index}>
              <strong>{item.title}</strong>
              <p>{item.message}</p>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}

function buildATSChecks(resumeFile, resumeInfo) {
  const checks = [];

  const fileName = resumeFile?.name || "";
  const fileSizeMB = resumeFile?.size ? resumeFile.size / 1024 / 1024 : 0;
  const ext = fileName.split(".").pop()?.toLowerCase() || "";

  if (["pdf", "docx", "txt"].includes(ext)) {
    checks.push({
      type: "good",
      title: "文件类型可解析",
      message: `当前文件格式为 ${ext.toUpperCase()}，系统支持解析。`,
      score: 15,
    });
  } else {
    checks.push({
      type: "bad",
      title: "文件类型风险",
      message: "建议使用 PDF、DOCX 或 TXT 格式，避免 ATS 无法读取。",
      score: 0,
    });
  }

  if (fileSizeMB > 0 && fileSizeMB <= 5) {
    checks.push({
      type: "good",
      title: "文件大小合理",
      message: `当前文件约 ${fileSizeMB.toFixed(2)} MB，大小正常。`,
      score: 10,
    });
  } else if (fileSizeMB > 5) {
    checks.push({
      type: "warn",
      title: "文件偏大",
      message: "文件体积较大，建议压缩图片或减少复杂排版。",
      score: 4,
    });
  } else {
    checks.push({
      type: "warn",
      title: "文件大小未知",
      message: "未检测到文件大小信息。",
      score: 4,
    });
  }

  const skills = resumeInfo?.skills || [];
  const projects = resumeInfo?.projects || [];
  const internships = resumeInfo?.internships || [];
  const certificates = resumeInfo?.certificates || [];

  if (skills.length >= 6) {
    checks.push({
      type: "good",
      title: "技能区较完整",
      message: `已识别 ${skills.length} 项技能，方便 ATS 进行关键词匹配。`,
      score: 20,
    });
  } else if (skills.length > 0) {
    checks.push({
      type: "warn",
      title: "技能数量偏少",
      message: `当前仅识别 ${skills.length} 项技能，建议补充技术栈关键词。`,
      score: 10,
    });
  } else {
    checks.push({
      type: "bad",
      title: "缺少技能区",
      message: "未明显识别到技能信息，建议添加“专业技能 / 技术栈”模块。",
      score: 0,
    });
  }

  if (projects.length >= 2) {
    checks.push({
      type: "good",
      title: "项目经历充分",
      message: `已识别 ${projects.length} 个项目，便于展示岗位相关经验。`,
      score: 20,
    });
  } else if (projects.length === 1) {
    checks.push({
      type: "warn",
      title: "项目数量略少",
      message: "当前仅识别 1 个项目，建议补充另一个课程项目、实习项目或个人项目。",
      score: 12,
    });
  } else {
    checks.push({
      type: "bad",
      title: "缺少项目经历",
      message: "未明显识别到项目经历，技术岗简历建议至少包含 1-2 个项目。",
      score: 0,
    });
  }

  const achievementTexts = projects.flatMap((project) => project.achievements || []);
  const quantifiedCount = achievementTexts.filter((item) =>
    /\d|%|提升|降低|减少|增长|优化|加速/.test(String(item))
  ).length;

  if (quantifiedCount >= 2) {
    checks.push({
      type: "good",
      title: "成果表达较量化",
      message: `已识别 ${quantifiedCount} 条较明确的成果表达。`,
      score: 20,
    });
  } else if (quantifiedCount === 1) {
    checks.push({
      type: "warn",
      title: "量化成果偏少",
      message: "建议增加性能提升、接口耗时、用户量、数据量等量化描述。",
      score: 10,
    });
  } else {
    checks.push({
      type: "warn",
      title: "缺少量化成果",
      message: "项目描述中缺少明显量化结果，建议使用数字增强说服力。",
      score: 4,
    });
  }

  if (internships.length > 0 || certificates.length > 0) {
    checks.push({
      type: "good",
      title: "补充经历可识别",
      message: "系统识别到实习或证书信息，有助于补充背景可信度。",
      score: 15,
    });
  } else {
    checks.push({
      type: "warn",
      title: "补充经历较少",
      message: "如果有实习、比赛、证书或开源经历，建议补充到简历中。",
      score: 7,
    });
  }

  return checks;
}

function EvidenceChainCard({ semanticMatchDetails, rewriteSuggestions, evidenceItems }) {
  const rewriteEvidence = rewriteSuggestions
    .filter((item) => item.evidence)
    .map((item) => ({
      title: item.optimized || item.original || "改写建议",
      evidence: item.evidence,
      risk: item.risk_level || "低",
    }));

  return (
    <div className="evidence-card">
      <div className="evidence-header">
        <h3>证据链追踪</h3>
        <p>
          用于说明匹配结论和改写建议分别基于哪些简历内容，降低 AI 幻觉风险。
        </p>
      </div>

      <div className="evidence-grid">
        <div className="evidence-column">
          <h4>结构化匹配证据</h4>

          {evidenceItems && evidenceItems.length > 0 ? (
            <div className="evidence-item-list">
              {evidenceItems.slice(0, 8).map((item, index) => (
                <div className="evidence-item-card" key={index}>
                  <div className="evidence-item-top">
                    <strong>{item.title}</strong>
                    <span>
                      {item.match_method} · {Number(item.similarity || 0).toFixed(2)}
                    </span>
                  </div>

                  <p>
                    <b>JD目标：</b>
                    {item.target_text}
                  </p>
                  <p>
                    <b>简历依据：</b>
                    {item.source_text}
                  </p>
                  <small>{item.explanation}</small>
                </div>
              ))}
            </div>
          ) : semanticMatchDetails.length > 0 ? (
            <ul className="clean-list">
              {semanticMatchDetails.slice(0, 6).map((item, index) => (
                <li key={index}>{item}</li>
              ))}
            </ul>
          ) : (
            <p className="muted-left">暂无语义匹配证据。</p>
          )}
        </div>

        <div className="evidence-column">
          <h4>改写依据</h4>

          {rewriteEvidence.length > 0 ? (
            <div className="rewrite-evidence-list">
              {rewriteEvidence.slice(0, 4).map((item, index) => (
                <div className="rewrite-evidence-item" key={index}>
                  <strong>{item.title}</strong>
                  <p>{item.evidence}</p>
                  <span>幻觉风险：{item.risk}</span>
                </div>
              ))}
            </div>
          ) : (
            <p className="muted-left">暂无改写依据。</p>
          )}
        </div>
      </div>
    </div>
  );
}

function ScoreBreakdownCard({ items }) {
  return (
    <div className="score-breakdown-card">
      <div className="score-breakdown-header">
        <h3>评分拆解</h3>
        <p>总分由必备技能、加分技能、项目相关度和关键词覆盖度组成。</p>
      </div>

      <div className="score-breakdown-grid">
        {items.length > 0 ? (
          items.map((item, index) => {
            const percent = item.max_score
              ? Math.min(100, Math.round((item.score / item.max_score) * 100))
              : 0;

            return (
              <div className="score-dimension" key={index}>
                <div className="score-dimension-top">
                  <span>{item.name}</span>
                  <strong>
                    {item.score}/{item.max_score}
                  </strong>
                </div>

                <div className="score-bar">
                  <div
                    className="score-bar-fill"
                    style={{ width: `${percent}%` }}
                  />
                </div>

                <p>{item.explanation}</p>
              </div>
            );
          })
        ) : (
          <p className="muted-left">暂无评分拆解数据</p>
        )}
      </div>
    </div>
  );
}

function SummaryCards({ resumeInfo, jdInfo }) {
  const resumeProjects = resumeInfo?.projects || [];
  const resumeSkills = resumeInfo?.skills || [];
  const requiredSkills = jdInfo?.required_skills || [];
  const preferredSkills = jdInfo?.preferred_skills || [];
  const jdKeywords = jdInfo?.keywords || [];

  return (
    <div className="summary-grid">
      <div className="summary-card">
        <h3>简历摘要</h3>
        <p>
          技能数量：<strong>{resumeSkills.length}</strong>
        </p>
        <p>
          项目数量：<strong>{resumeProjects.length}</strong>
        </p>
        <div className="mini-chip-list">
          {resumeSkills.slice(0, 8).map((item, index) => (
            <span className="mini-chip" key={index}>
              {item}
            </span>
          ))}
        </div>
      </div>

      <div className="summary-card">
        <h3>岗位摘要</h3>
        <p>
          岗位方向：<strong>{jdInfo?.position || "未识别"}</strong>
        </p>
        <p>
          必备技能：<strong>{requiredSkills.length}</strong>，
          加分技能：<strong>{preferredSkills.length}</strong>
        </p>
        <div className="mini-chip-list">
          {jdKeywords.slice(0, 8).map((item, index) => (
            <span className="mini-chip" key={index}>
              {item}
            </span>
          ))}
        </div>
      </div>
    </div>
  );
}

function KeywordPanel({ projectRelatedKeywords, coveredKeywords, missingKeywords }) {
  return (
    <div className="keyword-panel">
      <KeywordColumn
        title="项目相关关键词"
        items={projectRelatedKeywords}
        empty="暂无项目相关关键词"
      />
      <KeywordColumn
        title="已覆盖 JD 关键词"
        items={coveredKeywords}
        empty="暂无已覆盖关键词"
      />
      <KeywordColumn
        title="未覆盖 JD 关键词"
        items={missingKeywords}
        empty="暂无明显缺失关键词"
      />
    </div>
  );
}

function KeywordColumn({ title, items, empty }) {
  return (
    <div className="keyword-column">
      <h3>{title}</h3>
      <div className="chip-list">
        {items.length > 0 ? (
          items.map((item, index) => (
            <span className="keyword-chip" key={index}>
              {item}
            </span>
          ))
        ) : (
          <p className="muted">{empty}</p>
        )}
      </div>
    </div>
  );
}

function SemanticMatchCard({ semanticMatches, semanticMatchDetails }) {
  return (
    <div className="report-card semantic-card">
      <h3>语义匹配证据</h3>

      {semanticMatchDetails.length === 0 && (
        <p className="muted-left">
          暂无语义匹配证据，当前结果主要来自规则匹配和关键词匹配。
        </p>
      )}

      {semanticMatches.length > 0 && (
        <div className="semantic-chip-list">
          {semanticMatches.map((item, index) => (
            <span className="keyword-chip" key={index}>
              {item}
            </span>
          ))}
        </div>
      )}

      {semanticMatchDetails.length > 0 && (
        <ul className="clean-list semantic-detail-list">
          {semanticMatchDetails.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      )}
    </div>
  );
}

function SkillCard({ title, items, empty, type }) {
  return (
    <div className="skill-card">
      <h3>{title}</h3>
      <div className="chip-list">
        {items.length > 0 ? (
          items.map((item, index) => (
            <span className={`chip chip-${type}`} key={index}>
              {item}
            </span>
          ))
        ) : (
          <p className="muted">{empty}</p>
        )}
      </div>
    </div>
  );
}

function ListCard({ title, items, empty }) {
  return (
    <div className="report-card">
      <h3>{title}</h3>
      {items.length > 0 ? (
        <ul className="clean-list">
          {items.map((item, index) => (
            <li key={index}>{item}</li>
          ))}
        </ul>
      ) : (
        <p className="muted-left">{empty}</p>
      )}
    </div>
  );
}

function TwoColumnCards({ leftTitle, leftItems, rightTitle, rightItems }) {
  return (
    <div className="two-column">
      <ListCard title={leftTitle} items={leftItems} empty="暂无内容" />
      <ListCard title={rightTitle} items={rightItems} empty="暂无内容" />
    </div>
  );
}

function getRiskClass(riskLevel) {
  if (!riskLevel) return "risk-low";
  if (riskLevel.includes("高")) return "risk-high";
  if (riskLevel.includes("中")) return "risk-medium";
  return "risk-low";
}

function copyText(text) {
  if (!text) return;

  if (navigator.clipboard) {
    navigator.clipboard.writeText(text);
  } else {
    const textarea = document.createElement("textarea");
    textarea.value = text;
    document.body.appendChild(textarea);
    textarea.select();
    document.execCommand("copy");
    document.body.removeChild(textarea);
  }
}

function RewriteCard({ suggestions }) {
  return (
    <div className="report-card">
      <h3>简历改写前后对比</h3>

      {suggestions.length === 0 && (
        <p className="muted-left">暂无简历改写建议</p>
      )}

      {suggestions.map((item, index) => {
        const riskLevel = item.risk_level || "低";
        const riskClass = getRiskClass(riskLevel);

        return (
          <div className="rewrite-item" key={index}>
            <div className="rewrite-header">
              <span>建议 {index + 1}</span>
              <div className="rewrite-actions">
                <span className={`risk ${riskClass}`}>风险：{riskLevel}</span>
                <button
                  className="copy-btn"
                  onClick={() => copyText(item.optimized || "")}
                >
                  复制优化版
                </button>
              </div>
            </div>

            <div className="compare-grid">
              <div className="before-box">
                <h4>原始描述</h4>
                <p>{item.original || "暂无原始描述"}</p>
              </div>

              <div className="after-box">
                <h4>优化后</h4>
                <p>{item.optimized || "暂无优化内容"}</p>
              </div>
            </div>

            <div className="reason-box">
              <p>
                <strong>优化原因：</strong>
                {item.reason || "暂无原因"}
              </p>
              <p>
                <strong>简历依据：</strong>
                {item.evidence || "暂无依据"}
              </p>

              <div className="keyword-row">
                <strong>对应 JD 关键词：</strong>
                {(item.jd_keywords || []).length > 0 ? (
                  item.jd_keywords.map((keyword, idx) => (
                    <span className="keyword-chip" key={idx}>
                      {keyword}
                    </span>
                  ))
                ) : (
                  <span className="muted-inline">暂无关键词</span>
                )}
              </div>
            </div>
          </div>
        );
      })}
    </div>
  );
}

function InterviewCard({ questions }) {
  return (
    <div className="report-card">
      <h3>面试题预测</h3>

      {questions.length === 0 && <p className="muted-left">暂无面试题</p>}

      <div className="question-list">
        {questions.map((item, index) => (
          <div className="question-item" key={index}>
            <div className="question-index">{index + 1}</div>
            <div>
              <h4>{item.question}</h4>
              <p>考察点：{item.focus}</p>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;