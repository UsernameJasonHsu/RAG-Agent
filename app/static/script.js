const answerBox = document.getElementById("answer-box");

function setAnswerState(state, text) {
  answerBox.textContent = text;
  answerBox.classList.remove("loading", "success", "error", "show"); 
  answerBox.classList.add("answer", state, "show");
}

// 表單送出事件
document.getElementById("qa-form").addEventListener("submit", async function (e) {
  e.preventDefault();
  const question = document.getElementById("question").value;
  const agentName = document.getElementById("agent-select").value;

  setAnswerState("loading", "⏳ 正在思考中...");

  try {
    const res = await fetch("/ask", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ question, agent_name: agentName })
    });
    const data = await res.json();
    setAnswerState("success", "💡 回答：" + data.answer);
  } catch (err) {
    setAnswerState("error", "⚠️ 發生錯誤，請稍後再試。");
  }
});

// 鍵盤快捷：Ctrl/Cmd+K 聚焦輸入框
document.addEventListener("keydown", (e) => {
  if ((e.ctrlKey || e.metaKey) && e.key.toLowerCase() === "k") {
    e.preventDefault();
    document.getElementById("question").focus();
  }
});

// 新增功能：點擊回答區塊即可複製文字
answerBox.addEventListener("click", () => {
  if (answerBox.textContent.trim() !== "") {
    navigator.clipboard.writeText(answerBox.textContent).then(() => {
      // 顯示提示效果
      const original = answerBox.textContent;
      answerBox.textContent = "✅ 已複製到剪貼簿";
      setTimeout(() => {
        answerBox.textContent = original;
      }, 1500);
    });
  }
});

// 導覽列滾動陰影效果
window.addEventListener("scroll", () => {
  const navbar = document.querySelector(".navbar");
  if (window.scrollY > 20) {
    navbar.classList.add("scrolled");
  } else {
    navbar.classList.remove("scrolled");
  }
});
