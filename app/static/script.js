const answerBox = document.getElementById("answer-box");
const answerCard = document.getElementById("answer-card");
const loadingBar = document.getElementById("loading-bar");
const feedbackBlock = document.getElementById("feedback");

function typeWriterEffect(element, text, speed = 40, callback) {
  element.textContent = "";
  let i = 0;
  const interval = setInterval(() => {
    element.textContent += text.charAt(i);
    i++;
    if (i >= text.length) {
      clearInterval(interval);
      if (callback) callback(); // 完成後呼叫 callback
    }
  }, speed);
}

function setAnswerState(state, text) {
  answerBox.className = "answer " + state;
  answerCard.classList.add("show");

  if (state === "loading") {
    answerBox.textContent = text;
    loadingBar.classList.add("active");
    feedbackBlock.classList.add("hidden"); // 查詢中隱藏反饋
  } else {
    loadingBar.classList.remove("active");
    typeWriterEffect(answerBox, text, 40, () => {
      setTimeout(() => {
        feedbackBlock.classList.remove("hidden");
        feedbackBlock.classList.add("show"); // 延遲 1 秒後淡入＋滑入
      }, 1000);
    });
  }
}


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

    if (!res.ok) throw new Error("伺服器回應錯誤");

    const data = await res.json();
    setAnswerState("success", "💡 回答：" + data.answer);
  } catch (err) {
    setAnswerState("error", "⚠️ 發生錯誤，請稍後再試。");
    console.error(err);
  }
});

// 反饋按鈕事件
document.querySelectorAll(".btn-feedback").forEach(btn => {
  btn.addEventListener("click", () => {
    const type = btn.getAttribute("data-type");
    console.log("使用者反饋:", type); 
    // 這裡可以改成 fetch('/feedback', {method:'POST', body: JSON.stringify({type})})
    alert("感謝你的反饋：" + (type === "yes" ? "有幫助" : "沒幫助"));
  });
});

// 文字反饋表單事件
document.getElementById("feedback-form").addEventListener("submit", e => {
  e.preventDefault();
  const text = document.getElementById("feedback-text").value.trim();
  if (text) {
    console.log("使用者意見:", text);
    // 這裡可以改成 fetch('/feedback', {method:'POST', body: JSON.stringify({text})})
    alert("感謝你的意見，我們已收到！");
    e.target.reset();
  } else {
    alert("請輸入意見再送出。");
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

// 導覽列高亮當前區塊
const sections = document.querySelectorAll("section");
const navLinks = document.querySelectorAll(".nav-right a");

window.addEventListener("scroll", () => {
  let current = "";
  sections.forEach(section => {
    const sectionTop = section.offsetTop - 70; // 導覽列高度偏移
    if (window.scrollY >= sectionTop) {
      current = section.getAttribute("id");
    }
  });

  navLinks.forEach(link => {
    link.classList.remove("active");
    if (link.getAttribute("href").includes(current)) {
      link.classList.add("active");
    }
  });
});

// FAQ 展開/收合
const faqItems = document.querySelectorAll(".faq-item");

faqItems.forEach(item => {
  const question = item.querySelector(".faq-question");
  question.addEventListener("click", () => {
    // 收合其他 FAQ
    faqItems.forEach(i => {
      if (i !== item) i.classList.remove("active");
    });
    // 切換當前 FAQ
    item.classList.toggle("active");
  });
});
