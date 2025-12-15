# export_corpora_to_json.py
import json

agent_corpora = {
    "default": [
        "地球是太陽系中的第三顆行星，擁有豐富的生命與水資源。",
        "水的沸點在標準大氣壓下是攝氏100度。",
        "Python 是一種廣泛使用的高階程式語言，適合資料分析與網頁開發。",
        "FastAPI 是一個用於建構 API 的 Python 框架，具有高效能與簡潔語法。"
    ],
    "finance": [
        "股票是企業籌資的一種方式，投資人可透過股價波動獲利。",
        "ETF 是一種追蹤指數的投資工具，具有低成本與高流動性。",
        "比特幣是一種去中心化的加密貨幣，使用區塊鏈技術。"
    ],
    "medical": [
        "感冒通常由病毒引起，症狀包括喉嚨痛、流鼻水與咳嗽。",
        "高血壓是指血壓持續高於正常範圍，可能導致心血管疾病。",
        "疫苗能刺激免疫系統產生抗體，預防特定疾病。"
    ],
    "legal": [
        "契約是雙方基於合意所成立的法律關係。",
        "刑法規範犯罪行為與相應的法律責任。",
        "智慧財產權包括著作權、專利權與商標權。"
    ],
    "tech": [
        "人工智慧是模擬人類智能的技術，包含機器學習與自然語言處理。",
        "Docker 是一種容器化技術，可封裝應用程式與其依賴環境。",
        "HTML 是網頁的標記語言，CSS 用於樣式設計，JavaScript 負責互動行為。"
    ]
}

with open("agent_corpora.json", "w", encoding="utf-8") as f:
    json.dump(agent_corpora, f, ensure_ascii=False, indent=2)

print("✅ Exported agent_corpora.json")