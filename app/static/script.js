document.getElementById("qa-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const question = document.getElementById("question").value;
  const agentName = document.getElementById("agent-select").value;
  const answerBox = document.getElementById("answer-box");
  answerBox.textContent = "⏳ 正在思考中...";

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, agent_name: agentName })
    });
    const data = await res.json();
    answerBox.textContent = "💡 回答：" + data.answer;
  } catch (err) {
    answerBox.textContent = "⚠️ 發生錯誤，請稍後再試。";
  }
});
