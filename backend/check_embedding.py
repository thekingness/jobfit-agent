import os
from pathlib import Path

model_path = os.getenv(
    "JOBFIT_LOCAL_EMBEDDING_MODEL_PATH",
    r"D:\agentprogram\jobfit-agent\models\paraphrase-multilingual-MiniLM-L12-v2",
)

path = Path(model_path)

print("当前模型路径：", path)

if not path.exists():
    print("模型路径不存在")
    raise SystemExit(1)

print("模型路径存在，文件列表：")
for item in path.iterdir():
    print("-", item.name)

required_files = [
    "config.json",
    "modules.json",
    "sentence_bert_config.json",
    "tokenizer_config.json",
]

missing_files = []

for file_name in required_files:
    if not (path / file_name).exists():
        missing_files.append(file_name)

has_weight_file = (path / "model.safetensors").exists() or (path / "pytorch_model.bin").exists()

if not has_weight_file:
    missing_files.append("model.safetensors 或 pytorch_model.bin")

if missing_files:
    print("模型文件不完整，缺少：")
    for item in missing_files:
        print("-", item)
    raise SystemExit(1)

try:
    from sentence_transformers import SentenceTransformer

    print("正在加载本地模型...")
    model = SentenceTransformer(str(path))

    print("正在测试 embedding...")
    embeddings = model.encode(
        ["接口联调", "配合前端完成 API 对接"],
        normalize_embeddings=True,
        show_progress_bar=False,
    )

    score = float(embeddings[0] @ embeddings[1])

    print("模型加载成功")
    print("测试相似度：", round(score, 4))

except Exception as error:
    print("模型加载失败：")
    print(error)
    raise SystemExit(1)