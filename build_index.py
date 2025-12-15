import os
import json
import time
from embeddings_factory import get_embeddings
from langchain_community.vectorstores import FAISS

JSON_PATH = os.getenv("AGENT_CORPORA_JSON", "agent_corpora.json")
OUTPUT_DIR = os.getenv("FAISS_OUTPUT_DIR", "faiss_index")

def load_corpora(json_path: str) -> dict:
    if not os.path.exists(json_path):
        raise FileNotFoundError(f"❌ 找不到 JSON 檔案：{json_path}")
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if not isinstance(data, dict) or not data:
        raise ValueError("❌ JSON 結構不正確或為空，預期為 {category: [texts, ...]}")
    # 基本驗證：每個 category 都應是 list[str]
    for cat, items in data.items():
        if not isinstance(items, list) or not all(isinstance(x, str) for x in items):
            raise ValueError(f"❌ 類別 {cat} 的內容不是文字陣列 (list[str])")
    return data

def build_single_index(category: str, texts: list, embedding, output_dir: str):
    index_path = os.path.join(output_dir, category)
    os.makedirs(index_path, exist_ok=True)

    print(f"🔧 建立 Agent：{category} 的向量資料庫... (docs={len(texts)})")
    # optional: 建立 metadatas，利於後續檢索時過濾或顯示
    metadatas = [{"category": category, "id": f"{category}_{i:04d}"} for i in range(len(texts))]

    for attempt in range(1, 4):
        try:
            db = FAISS.from_texts(texts, embedding, metadatas=metadatas)
            db.save_local(index_path)
            print(f"✅ 已儲存到：{index_path}")
            return
        except Exception as e:
            print(f"⚠️ 建立 {category} 失敗（第 {attempt} 次）：{e}")
            time.sleep(5)
    print(f"❌ 建立 {category} 失敗，已略過。")

def main():
    # 取得 embeddings
    embedding = get_embeddings()

    # 載入 JSON corpora
    corpora = load_corpora(JSON_PATH)

    # 逐類別建立 index
    for agent_name, texts in corpora.items():
        build_single_index(agent_name, texts, embedding, OUTPUT_DIR)

    print("✅ 所有 Agent 的 FAISS index 建立完成！")

if __name__ == "__main__":
    main()