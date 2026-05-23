const analyzeForm = document.getElementById("analyzeForm");
const repoUrlInput = document.getElementById("repoUrlInput");
const overviewContent = document.getElementById("overviewContent");
const readmeContent = document.getElementById("readmeContent");
const plainExplainButton = document.getElementById("plainExplainButton");
const plainExplainResult = document.getElementById("plainExplainResult");

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function renderMarkdown(markdown) {
  const lines = markdown.split(/\r?\n/);
  const html = [];
  let inList = false;

  for (const rawLine of lines) {
    const line = rawLine.trimEnd();
    if (!line.trim()) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      continue;
    }
    if (line.startsWith("## ")) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<h2>${escapeHtml(line.slice(3))}</h2>`);
      continue;
    }
    if (line.startsWith("### ")) {
      if (inList) {
        html.push("</ul>");
        inList = false;
      }
      html.push(`<h3>${escapeHtml(line.slice(4))}</h3>`);
      continue;
    }
    if (line.startsWith("- ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push(`<li>${escapeHtml(line.slice(2))}</li>`);
      continue;
    }
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
    html.push(`<p>${escapeHtml(line)}</p>`);
  }

  if (inList) {
    html.push("</ul>");
  }
  return html.join("");
}

async function postJson(url, payload) {
  const response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  const data = await response.json();
  if (!response.ok) {
    throw new Error(data.error || "请求失败");
  }
  return data;
}

analyzeForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  const button = analyzeForm.querySelector("button");
  button.disabled = true;
  overviewContent.textContent = "正在生成项目概览...";
  readmeContent.textContent = "正在翻译 README...";
  plainExplainResult.hidden = true;

  try {
    const data = await postJson("/api/analyze", { repo_url: repoUrlInput.value });
    overviewContent.classList.remove("empty-state");
    readmeContent.classList.remove("empty-state");
    overviewContent.innerHTML = renderMarkdown(data.project_overview);
    readmeContent.innerHTML = renderMarkdown(data.readme_translation);
  } catch (error) {
    overviewContent.textContent = error.message;
    readmeContent.textContent = "分析失败";
  } finally {
    button.disabled = false;
  }
});

plainExplainButton.addEventListener("click", async () => {
  const selectedText = window.getSelection().toString().trim();
  if (!selectedText) {
    plainExplainResult.hidden = false;
    plainExplainResult.textContent = "请先在右侧 README 区域选中一段中文文本。";
    return;
  }

  plainExplainButton.disabled = true;
  plainExplainResult.hidden = false;
  plainExplainResult.textContent = "正在生成大白话说明...";

  try {
    const data = await postJson("/api/plain-explain", { selected_text: selectedText });
    plainExplainResult.innerHTML = renderMarkdown(data.plain_explanation);
  } catch (error) {
    plainExplainResult.textContent = error.message;
  } finally {
    plainExplainButton.disabled = false;
  }
});
