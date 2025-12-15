import os
from dotenv import load_dotenv

# LangChain OpenAI embeddings
from langchain_openai import OpenAIEmbeddings

# Hugging Face embeddings
from sentence_transformers import SentenceTransformer
from langchain_community.embeddings import HuggingFaceEmbeddings

load_dotenv()

def get_embeddings():
    engine = os.getenv("EMBEDDING_ENGINE", "huggingface").lower()

    if engine == "openai":
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise ValueError("❌ 未找到 OPENAI_API_KEY，請確認 .env 檔案是否正確設定")
        print("✅ 使用 OpenAI Embeddings")
        return OpenAIEmbeddings(openai_api_key=api_key)

    elif engine == "huggingface":
        print("✅ 使用 Hugging Face Embeddings (all-MiniLM-L6-v2)")
        model_name = "sentence-transformers/all-MiniLM-L6-v2"
        return HuggingFaceEmbeddings(model_name=model_name)

    else:
        raise ValueError(f"❌ 未知的 EMBEDDING_ENGINE: {engine}")
