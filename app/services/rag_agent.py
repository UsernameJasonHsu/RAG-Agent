# RAG 與 AI Agent 封裝 (新版 LangChain 架構，使用 HuggingFace InferenceClient)

import os
import time
from dotenv import load_dotenv
from langchain_community.vectorstores import FAISS
from langchain.chains import create_retrieval_chain
from langchain.chains.combine_documents import create_stuff_documents_chain
from langchain_core.prompts import ChatPromptTemplate

from langchain_openai import OpenAIEmbeddings, ChatOpenAI
from langchain_community.embeddings import HuggingFaceEmbeddings

# ✅ 新增：直接使用 huggingface_hub.InferenceClient
from huggingface_hub import InferenceClient
from langchain_core.language_models import LLM
from typing import Optional, List
from pydantic import Field

# ✅ 建立一個簡單的 LangChain LLM wrapper，封裝 InferenceClient chat.completions
class HuggingFaceLLM(LLM):
    temperature: float = Field(default=0.0)
    max_tokens: int = Field(default=512)
    client: Optional[InferenceClient] = Field(default=None, exclude=True)
    model: str = Field(default="Qwen/Qwen2-7B-Instruct")

    def __init__(self, model: str, token: Optional[str] = None, provider: str = "auto", **kwargs):
        super().__init__(**kwargs)
        object.__setattr__(self, "client", InferenceClient(provider=provider, api_key=token))
        object.__setattr__(self, "model", model)

    def _call(self, prompt: str, stop: Optional[List[str]] = None) -> str:
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a helpful assistant."},
                    {"role": "user", "content": prompt},
                ],
                max_tokens=self.max_tokens,
                temperature=self.temperature,
            )
            return resp.choices[0].message.content
        except Exception as e:
            return f"[Error] HuggingFace LLM 呼叫失敗: {repr(e)}"

    @property
    def _llm_type(self) -> str:
        return "huggingface_chat_completions"

class RAGAgent:
    def __init__(self, name: str, index_path: str, max_retries: int = 3, retry_delay: int = 5, debug_prompt: bool = True):
        load_dotenv()
        self.name = name
        self.api_key = os.getenv("OPENAI_API_KEY")
        self.max_retries = max_retries
        self.retry_delay = retry_delay
        self.debug_prompt = debug_prompt

        # Embeddings
        engine = os.getenv("EMBEDDING_ENGINE", "huggingface").lower()
        if engine == "openai":
            if not self.api_key:
                raise ValueError("❌ 未找到 OPENAI_API_KEY，請確認 .env 檔案是否正確設定")
            print(f"✅ 使用 OpenAI Embeddings for agent: {self.name}")
            self.embeddings = OpenAIEmbeddings(model="text-embedding-3-small")
        elif engine == "huggingface":
            print(f"✅ 使用 HuggingFace Embeddings (all-MiniLM-L6-v2) for agent: {self.name}")
            self.embeddings = HuggingFaceEmbeddings(model_name="sentence-transformers/all-MiniLM-L6-v2")
        else:
            raise ValueError(f"❌ 未知的 EMBEDDING_ENGINE: {engine}")

        print(f"✅ 已載入 OpenAI API 金鑰：{self.api_key[:5]}...（已遮蔽）")

        # Vector DB
        self.vector_db = FAISS.load_local(
            index_path,
            self.embeddings,
            allow_dangerous_deserialization=True
        )
        self.retriever = self.vector_db.as_retriever()  # ✅ 保存 retriever

        # LLM
        llm_engine = os.getenv("LLM_ENGINE", "huggingface").lower()
        if llm_engine == "openai":
            if not self.api_key:
                raise ValueError("❌ 未找到 OPENAI_API_KEY，請確認 .env 檔案是否正確設定")
            print(f"✅ 使用 OpenAI LLM for agent: {self.name}")
            self.llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
        elif llm_engine == "huggingface":
            print(f"✅ 使用 HuggingFace InferenceClient ChatCompletions for agent: {self.name}")
            repo_id = os.getenv("HF_REPO_ID", "Qwen/Qwen2-7B-Instruct")
            self.llm = HuggingFaceLLM(
                model=repo_id,
                token=os.getenv("HUGGINGFACEHUB_API_TOKEN"),
                provider="featherless-ai",
                temperature=0,
                max_tokens=512
            )
        else:
            raise ValueError(f"❌ 未知的 LLM_ENGINE: {llm_engine}")

        # Prompt → ✅ 保存為成員
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "你是一個知識型助理，請根據檢索到的文件回答問題。"),
            ("human", "{input}\n\n檢索到的內容：{context}")
        ])

        # Docs chain → ✅ 保存為成員
        self.docs_chain = create_stuff_documents_chain(self.llm, self.prompt)

        # QA chain
        self.qa_chain = create_retrieval_chain(self.retriever, self.docs_chain)

    def answer_question(self, question: str) -> str:
        import traceback
        for attempt in range(1, self.max_retries + 1):
            try:
                print(f"🔍 嘗試第 {attempt} 次處理問題：{question}")

                # 先用 retriever 取得相關文件並組成 context
                docs = self.retriever.get_relevant_documents(question)
                context_text = "\n\n".join([d.page_content for d in docs])

                # ✅ 只有在 debug_prompt=True 時才印出完整 Prompt
                if self.debug_prompt:
                    formatted_prompt = self.prompt.format(
                        input=question,
                        context=context_text
                    )
                    print("📝 AI 看到的 Prompt:\n", formatted_prompt)

                # 執行 QA chain
                result = self.qa_chain.invoke({"input": question})
                return result.get("answer") or str(result)

            except Exception as e:
                print(f"⚠️ 嘗試第 {attempt} 次失敗，錯誤如下：")
                print("Exception repr:", repr(e))
                traceback.print_exc()
                if hasattr(e, "errors"):
                    print("Pydantic errors:", e.errors())
                time.sleep(self.retry_delay)
        print("❌ 所有重試皆失敗")
        return None