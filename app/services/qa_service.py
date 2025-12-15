# 整合服務層

from services.database import MySQLConnector
from services.rag_agent import RAGAgent

class QAService:
    def __init__(self, db_config: dict, agent_configs: str):
        self.db = MySQLConnector(db_config)
        self.agents = {
            config["name"]: RAGAgent(
                name=config["name"],
                index_path=config["index_path"],
            )
            for config in agent_configs
        }

    def process_question(self, question: str, agent_name: str) -> str:
        agent = self.agents.get(agent_name)
        if not agent:
            return f"❌ 未找到 Agent：{agent_name}"
        answer = agent.answer_question(question)
        self.db.insert_log(question, answer)
        return answer

    def shutdown(self):
        self.db.close()