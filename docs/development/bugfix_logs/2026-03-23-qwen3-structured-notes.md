# Bug 修复记录 - qwen3 结构化笔记全为空

> **修复日期**: 2026-03-23
> **影响模块**: `services/llm_service.py`, `services/api_config.py`
> **影响功能**: 结构化笔记生成（论文总结）
> **状态**: ✅ 已修复
> **测试模型**: qwen3-max-preview via Friday One-API（美团内部）
> **测试 PDF**: `AL_iLQR_Tutorial.pdf`

---

## 📋 问题描述

用户使用本地 ollama 部署的 qwen3:8b/4b 模型，或通过 Friday One-API 接入 qwen3-max-preview 时，上传论文后结构化笔记（研究问题、相关工作、方法论等）全部为空白，无任何内容。思维导图显示「论文标题未提供」。

---

## 🔍 根因分析（三层）

### 第一层：JSON 模板触发「直接复制」行为

**现象**：qwen3 始终返回 69~77 个 completion tokens，内容为空 JSON 结构。

**原因**：当 prompt 中包含 JSON 模板（无论是描述性占位符还是空字符串）且 JSON 模板出现在论文内容**之前**时，qwen3 将 JSON 模板视为「最终输出格式示例」，直接复制返回，不阅读后续的论文内容。

```
❌ 触发行为的 prompt 结构：
指令 → JSON模板（含字段描述） → 论文全文

✅ 正确的 prompt 结构：
极简指令 → 论文全文 → 空 JSON 模板
```

---

### 第二层：复杂 Markdown 格式指令触发「空输出」

**现象**：即使将 JSON 模板移到论文之后，只要指令部分包含复杂 Markdown 格式，qwen3 仍返回空 JSON。

**原因**：`SUMMARIZE_PAPER_PROMPT` 包含大量 Markdown 格式指令，包括：
- `**粗体**` 强调
- 有序/无序列表（`1.` / `-`）
- `` `代码格式` `` 标注
- `**输出格式（仅输出有效的 JSON，不要有其他文本）：**` ← 最关键的触发行

其中 `**输出格式...：**` 这一行会让 qwen3 立即进入「输出 JSON」模式，看到 JSON 模板后直接复制空结构返回。

---

### 第三层：`summary_struct` 嵌套结构导致字段为空

**现象**：去掉触发行后，qwen3 能填充 `title`、`authors`，但 `summary_struct` 内的所有字段仍为空。

**原因**：qwen3 对嵌套 JSON 字段（`summary_struct.problem_definition` 等）不填充，只填充顶层字段。

```json
// qwen3 的行为：只填顶层
{
  "title": "AL-iLQR Tutorial",     ✅ 填充
  "authors": ["Brian Jackson"],    ✅ 填充
  "summary_struct": {
    "problem_definition": "",      ❌ 不填充
    "contribution": ""             ❌ 不填充
  }
}
```

---

### 额外发现：prompt 超长时完全失效

**现象**：论文全文约 30000 字符，即使修复了前三层问题，qwen3 仍返回空 JSON。

**原因**：qwen3-max-preview 在 Friday 接口上对超过约 3500 tokens（约 10500 字符）的 prompt 直接输出空 JSON，不受 prompt 工程影响。

**临界点测试**：

| 文本长度 | prompt tokens | completion tokens | 是否有内容 |
|---------|--------------|------------------|---------|
| 4000 字符 | ~1677 | 1524 | ✅ 有 |
| 8000 字符 | ~3010 | 1590 | ✅ 有 |
| 12000 字符 | ~4344 | 69 | ❌ 空 |
| 16000 字符 | ~5677 | 69 | ❌ 空 |
| 30000 字符 | ~10348 | 69 | ❌ 空 |

---

## 🛠️ 修复方案

所有修复集中在 `services/llm_service.py` 的 `_preprocess_prompt_for_model` 方法中，**仅对 qwen3 系列模型生效，非 qwen3 模型（Gemini、豆包、DeepSeek 等）prompt 完全不受影响**。

### 修复1：极简指令替换复杂 Markdown 指令

```python
# 对 qwen3，丢弃原有复杂 Markdown 格式指令
instructions = '你是学术研究专家。请仔细阅读以下论文，用中文详细分析，每个字段至少100字。'
```

### 修复2：重排 prompt 结构（论文在前，JSON 在后）

```
原结构：极简指令 → [论文全文] → 请填写以下JSON → {空JSON模板}
```

### 修复3：展开 `summary_struct` 嵌套为顶层扁平字段

```json
// qwen3 接收的扁平 JSON 模板
{
  "title": "",
  "authors": [],
  "one_sentence_summary": "",
  "problem_definition": "",
  "existing_solutions": "",
  "limitations": "",
  "contribution": "",
  "methodology": "",
  "results": "",
  "future_work_paper": "",
  "future_work_insights": ""
}
```

### 修复4：截断论文文本到安全长度

```python
QWEN3_MAX_PAPER_CHARS = 8000  # ~2700 tokens，留足余量
```

### 修复5：postprocess 重新包装为标准嵌套格式

`_postprocess_qwen3_response` 将 qwen3 返回的扁平 JSON 重新包装为含 `summary_struct` 的标准格式，确保下游代码（`summarizer.py`、`paper_detail.py` 等）正常工作。

---

## 📐 完整修复流程图

```
用户上传论文
    ↓
pdf_parser 提取全文文本（最长 30000 字符）
    ↓
summarizer.generate_json(prompt)
    ↓
llm_service._call_api(prompt)
    ↓
_preprocess_prompt_for_model(prompt)
    ├── 非 qwen3：直接返回原 prompt（不做任何修改）
    └── qwen3：
        ├── 1. 替换为极简指令（去掉复杂 Markdown）
        ├── 2. 截断论文文本到 8000 字符
        ├── 3. 重排：极简指令 → 论文全文 → 扁平 JSON 模板
        └── 返回 processed prompt
    ↓
_call_openai_api(processed_prompt)
    ├── _should_use_stream() → qwen3 返回 True（streaming 模式）
    └── 调用 Friday API，streaming 采集完整输出
    ↓
generate_json 中：
    └── qwen3：_postprocess_qwen3_response(text)
        → 将扁平 JSON 重新包装为 {summary_struct: {...}} 格式
    ↓
extract_json_from_text(text)
    ↓
返回标准结构化笔记 JSON
```

---

## ✅ 验证结果

| 测试项 | 修复前 | 修复后 |
|-------|--------|--------|
| qwen3-max-preview 结构化笔记 | 全空（69 tokens） | **完整填充（1500+ tokens）** |
| Gemini prompt 是否变化 | — | **完全不变（直接返回原 prompt）** |
| 豆包 prompt 是否变化 | — | **完全不变** |
| DeepSeek prompt 是否变化 | — | **完全不变** |
| 思维导图标题 | 「论文标题未提供」 | **正确显示论文标题** |

---

## 📝 同步修复：requirements.txt 缺失依赖

用户反馈部署后部分功能报错，排查发现 `requirements.txt` 缺少两个已使用的库：

| 库 | 用途 | 修复 |
|----|------|------|
| `plotly>=5.0.0` | 数据可视化（v1.4.0 新增） | 补全 |
| `arxiv>=2.0.0` | Auto-Scholar 论文抓取 | 补全 |

---

## 📝 同步新增：Friday One-API 提供商

在 `services/api_config.py` 的 `PROVIDERS` 中新增 `friday` 条目，用户在设置页面可直接选择：

```python
"friday": {
    "name": "Friday One-API (美团内部)",
    "api_base": "https://aigc.sankuai.com/v1/openai/native/chat/completions",
    "models": [
        "qwen3-max-preview",
        "deepseek-v3-friday",
        "deepseek-r1-friday",
        "gpt-4o-mini",
        "gpt-4.1",
        "LongCat-8B-128K-Chat",
    ],
    "default_model": "qwen3-max-preview",
    "custom_ssl": True,  # 内网证书
}
```

**使用方式**：设置页面 → 主 LLM → 标准模式 → API 提供商选「Friday One-API (美团内部)」→ 填入 AppId → 选择模型 → 保存。

---

## ⚠️ 已知局限

1. **qwen3 结构化笔记质量**：由于论文文本截断到 8000 字符（约全文的 25%），分析深度不如使用全文的 Gemini。建议用 qwen3 做快速验证，正式使用推荐 Gemini 或 DeepSeek。

2. **qwen3 指令遵循**：极简指令下，qwen3 可能不完全遵循原有的 Markdown 格式要求（粗体、五级标题等），输出格式可能与 Gemini 有差异。

3. **本地 ollama qwen3**：本次修复基于 Friday qwen3-max-preview 测试，本地 ollama qwen3:8b/4b 的行为可能略有不同，但修复逻辑同样适用（模型名含 `qwen3` 即生效）。

---

## 🔗 相关文件

| 文件 | 改动 |
|------|------|
| `services/llm_service.py` | 新增 `_preprocess_prompt_for_model`、`_postprocess_qwen3_response`、`_should_use_stream`、`_call_openai_api_stream` |
| `services/api_config.py` | 新增 `friday` 提供商，`get_effective_api_params` 支持 provider 的 `custom_ssl` 字段 |
| `requirements.txt` | 补全 `plotly`、`arxiv`、`urllib3` |
