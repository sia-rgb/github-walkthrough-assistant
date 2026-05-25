const analyzeForm = document.getElementById("analyzeForm");
const repoUrlInput = document.getElementById("repoUrlInput");
const overviewContent = document.getElementById("overviewContent");
const readmeContent = document.getElementById("readmeContent");
const plainExplainButton = document.getElementById("plainExplainButton");
const plainExplainContent = document.getElementById("plainExplainContent");

function escapeHtml(value) {
  return value
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;");
}

function processInline(text) {
  var escaped = escapeHtml(text);
  return escaped.replace(
    /\[([^\]]+)\]\(([^)]+)\)/g,
    '<a href="$2" target="_blank" rel="noopener">$1</a>'
  );
}

function isTableSeparator(line) {
  var trimmed = line.trim();
  return /^\|[-:\s|]+\|$/.test(trimmed) && trimmed.indexOf("-") !== -1;
}

function looksLikeTableRow(line) {
  var trimmed = line.trim();
  return trimmed.startsWith("|") && trimmed.endsWith("|");
}

function splitTableCells(line) {
  var trimmed = line.trim();
  var inner = trimmed.slice(1, -1);
  return inner.split("|").map(function (c) { return c.trim(); });
}

function renderMarkdown(markdown) {
  var lines = markdown.split(/\r?\n/);
  var html = [];
  var inList = false;
  var inCodeBlock = false;
  var codeLines = [];
  var tableBuffer = [];

  function closeList() {
    if (inList) {
      html.push("</ul>");
      inList = false;
    }
  }

  function flushTable() {
    if (tableBuffer.length === 0) return;

    if (tableBuffer.length >= 2 && isTableSeparator(tableBuffer[1])) {
      html.push("<table>");
      var headerCells = splitTableCells(tableBuffer[0]);
      html.push("<thead><tr>");
      for (var h = 0; h < headerCells.length; h++) {
        html.push("<th>" + processInline(headerCells[h]) + "</th>");
      }
      html.push("</tr></thead>");

      if (tableBuffer.length > 2) {
        html.push("<tbody>");
        for (var r = 2; r < tableBuffer.length; r++) {
          var cells = splitTableCells(tableBuffer[r]);
          html.push("<tr>");
          for (var c = 0; c < cells.length; c++) {
            html.push("<td>" + processInline(cells[c]) + "</td>");
          }
          html.push("</tr>");
        }
        html.push("</tbody>");
      }
      html.push("</table>");
    } else {
      for (var t = 0; t < tableBuffer.length; t++) {
        html.push("<p>" + processInline(tableBuffer[t]) + "</p>");
      }
    }
    tableBuffer = [];
  }

  for (var i = 0; i < lines.length; i++) {
    var rawLine = lines[i];
    var line = rawLine.trimEnd();
    var trimmed = line.trim();

    if (inCodeBlock) {
      if (trimmed.startsWith("```")) {
        html.push("<pre><code>");
        html.push(escapeHtml(codeLines.join("\n")));
        html.push("</code></pre>");
        inCodeBlock = false;
        codeLines = [];
        continue;
      }
      codeLines.push(rawLine);
      continue;
    }

    if (trimmed.startsWith("```")) {
      closeList();
      flushTable();
      inCodeBlock = true;
      codeLines = [];
      continue;
    }

    if (looksLikeTableRow(trimmed) && !isTableSeparator(trimmed)) {
      closeList();
      tableBuffer.push(trimmed);
      continue;
    }

    if (isTableSeparator(trimmed)) {
      tableBuffer.push(trimmed);
      continue;
    }

    flushTable();

    if (!trimmed) {
      closeList();
      continue;
    }

    if (trimmed.startsWith("# ")) {
      closeList();
      html.push("<h1>" + processInline(trimmed.slice(2)) + "</h1>");
      continue;
    }
    if (trimmed.startsWith("## ")) {
      closeList();
      html.push("<h2>" + processInline(trimmed.slice(3)) + "</h2>");
      continue;
    }
    if (trimmed.startsWith("### ")) {
      closeList();
      html.push("<h3>" + processInline(trimmed.slice(4)) + "</h3>");
      continue;
    }

    if (trimmed.startsWith("- ") || trimmed.startsWith("* ")) {
      if (!inList) {
        html.push("<ul>");
        inList = true;
      }
      html.push("<li>" + processInline(trimmed.slice(2)) + "</li>");
      continue;
    }

    closeList();
    html.push("<p>" + processInline(line) + "</p>");
  }

  if (inCodeBlock) {
    html.push("<pre><code>");
    html.push(escapeHtml(codeLines.join("\n")));
    html.push("</code></pre>");
  }
  flushTable();
  closeList();

  return html.join("");
}

async function postJson(url, payload) {
  console.info("[postJson] request", {
    url: url,
    payload: buildDebugPayload(url, payload),
  });

  var response = await fetch(url, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(payload),
  });
  var data = await readResponseBody(response);

  console.info("[postJson] response", {
    url: url,
    status: response.status,
    body: data,
  });

  if (!response.ok) {
    var message = buildHttpErrorMessage(response, data);
    console.error("[postJson] error", {
      url: url,
      status: response.status,
      body: data,
      message: message,
    });
    throw new Error(message);
  }
  return data;
}

function buildDebugPayload(url, payload) {
  if (url === "api/plain-explain" && payload.selected_text) {
    return { selected_text_length: payload.selected_text.length };
  }
  return payload;
}

async function readResponseBody(response) {
  var text = await response.text();
  if (!text) {
    return null;
  }

  try {
    return JSON.parse(text);
  } catch (error) {
    return { raw: text };
  }
}

function stringifyDebugValue(value) {
  try {
    return JSON.stringify(value, null, 2);
  } catch (error) {
    return String(value);
  }
}

function buildHttpErrorMessage(response, data) {
  var message = "HTTP " + response.status + " " + response.statusText;
  message += "\nresponse body: " + stringifyDebugValue(data);

  if (data && data.detail) {
    message += "\ndetail: " + stringifyDebugValue(data.detail);
  }

  if (data && data.error) {
    message += "\nerror: " + data.error;
  }

  return message;
}

analyzeForm.addEventListener("submit", async function (event) {
  event.preventDefault();
  var button = analyzeForm.querySelector("button");
  var requestPath = "api/analyze";
  var rawRepoUrl = repoUrlInput.value;
  var repoUrl = rawRepoUrl.trim();
  var analyzePayload = { repo_url: repoUrl };

  console.info("[analyze] input", {
    requestPath: requestPath,
    repoUrlInputValue: rawRepoUrl,
    trimmedRepoUrl: repoUrl,
    payload: analyzePayload,
  });

  if (!repoUrl) {
    overviewContent.textContent = "请输入 GitHub 仓库 URL";
    readmeContent.textContent = "分析失败";
    return;
  }

  button.disabled = true;
  overviewContent.textContent = "正在生成项目概览...";
  readmeContent.textContent = "正在翻译 README...";
  plainExplainContent.classList.add("empty-state");
  plainExplainContent.textContent = "选中 README 中的文本后点击\"大白话说明\"按钮";

  try {
    var data = await postJson(requestPath, analyzePayload);
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

plainExplainButton.addEventListener("click", async function () {
  var selectedText = window.getSelection().toString().trim();
  if (!selectedText) {
    plainExplainContent.classList.add("empty-state");
    plainExplainContent.textContent = "请先在右侧 README 区域选中一段中文文本。";
    return;
  }

  plainExplainButton.disabled = true;
  plainExplainContent.classList.remove("empty-state");
  plainExplainContent.textContent = "正在生成大白话说明...";

  try {
    var data = await postJson("api/plain-explain", { selected_text: selectedText });
    plainExplainContent.innerHTML = renderMarkdown(data.plain_explanation);
  } catch (error) {
    plainExplainContent.textContent = error.message;
  } finally {
    plainExplainButton.disabled = false;
  }
});

