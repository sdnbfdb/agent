# DeepSeek API 集成指南

## 📋 概述

本项目使用 **DeepSeek Chat API** 作为主要的 LLM 模型，实现智能对话和工具调用功能。

## 🔑 API 配置

### 获取 API Key

1. 访问 [DeepSeek 开放平台](https://platform.deepseek.com/)
2. 注册/登录账号
3. 创建 API Key
4. 复制 API Key（格式：`sk-xxxxxxxxxxxxxxxx`）

### 配置文件

编辑 `use.py` 文件，设置 API Key：

```python
# use.py 第 30 行
DEEPSEEK_API_KEY = "sk-your-actual-api-key"  # 替换为你的 API Key
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"
```

## 🚀 使用方法

### 基本用法

```bash
# 启动交互式对话
python use.py

# 单次提问
python use.py "你好，请介绍一下自己"
```

### 可用工具

Agent 支持以下 4 个工具：

| 工具 | 功能 | 触发关键词 |
|------|------|-----------|
| `get_current_location()` | 获取当前位置 | "我在哪里"、"我的位置" |
| `get_weather_by_location(location)` | 查询天气 | "天气"、"温度"、"下雨" |
| `query_history(keyword, limit)` | 查询历史对话 | "历史记录"、"聊天记录" |
| `get_history_stats()` | 获取统计信息 | "多少次对话"、"统计" |

### 示例对话

```
你：我在哪里？
🔧 调用工具：get_current_location
agent: 根据定位，你现在位于上海市...

你：这里天气怎么样？
🔧 调用工具：get_weather_by_location
agent: 上海今天部分多云，温度 18°C...

你：我之前问过关于天气的问题吗？
🔧 调用工具：query_history(keyword='天气')
agent: 是的！您在 2026-03-25 15:31:57 问过："你好，请问今天天气如何？"
```

## 💡 技术实现

### 核心流程

```python
# 1. 检测工具调用意图
def detect_tool_call(user_input: str) -> tuple:
    # 关键词匹配
    if '天气' in user_input.lower():
        return 'get_weather_by_location', {'location': city}

# 2. 调用工具
def call_tool(tool_name: str, params: dict):
    if tool_name == 'get_weather_by_location':
        result = get_weather_by_location(params['location'])
        return format_result(result)

# 3. 构建增强提示词
messages = [
    {'role': 'user', 'content': f"""
用户问题：{user_input}

--- 工具查询结果 ---
{tool_result}
--- 结束 ---

请根据上面的工具查询结果，用自然语言回答用户的问题。
"""}
]

# 4. 调用 DeepSeek API
def call_deepseek_api(messages: list) -> str:
    headers = {
        'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
        'Content-Type': 'application/json'
    }
    
    payload = {
        'model': MODEL_NAME,
        'messages': messages,
        'temperature': 0.7,
        'max_tokens': 2048
    }
    
    response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers)
    return response.json()['choices'][0]['message']['content']
```

### API 参数说明

```python
payload = {
    'model': 'deepseek-chat',      # 模型名称
    'messages': [...],              # 对话历史
    'temperature': 0.7,             # 创造性 (0-1)
    'max_tokens': 2048              # 最大输出长度
}
```

## 📊 项目结构

```
agent/
├── use.py                      # 主程序（DeepSeek API 调用）
├── tool.py                     # 工具函数集合
│   ├── get_current_location()
│   ├── get_weather_by_location()
│   ├── query_history()
│   └── get_history_stats()
├── history.py                  # 历史记录管理
└── DEEPSEEK_CONFIG.md          # 配置说明
```

## 🔒 安全建议

### ⚠️ 重要提醒

**不要将 API Key 提交到 Git！**

1. 在 `.gitignore` 中添加：
```
.env
*.key
config_secret.json
```

2. 使用环境变量（推荐）：
```python
import os
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY')
```

3. 或使用配置文件：
```python
# config.py (不提交到 Git)
DEEPSEEK_API_KEY = "sk-your-key"

# use.py
from config import DEEPSEEK_API_KEY
```

## 💰 费用说明

- DeepSeek API 是付费服务
- 价格参考：[DeepSeek 定价页面](https://platform.deepseek.com/pricing)
- 建议设置使用限额和告警

## 🐛 常见问题

### Q1: API 调用失败
```
错误：401 Unauthorized
原因：API Key 无效或过期
解决：检查 DEEPSEEK_API_KEY 配置
```

### Q2: 网络连接超时
```
错误：Connection timeout
原因：网络问题或 API 服务不可用
解决：检查网络连接，稍后重试
```

### Q3: 工具不调用
```
原因：关键词匹配失败
解决：检查 detect_tool_call() 中的关键词列表
```

## 🔗 相关资源

- [DeepSeek 官方文档](https://platform.deepseek.com/docs)
- [API 参考](https://platform.deepseek.com/api-docs)
- [模型介绍](https://platform.deepseek.com/models)

## 📝 更新日志

### v1.0 - 2026-03-26
- ✅ 集成 DeepSeek Chat API
- ✅ 支持 4 个实用工具
- ✅ 增强的工具调用检测
- ✅ 历史记录管理
- ✅ 上下文记忆功能

---

**提示**: 本文件已提交到 GitHub，团队成员可以参考此文档配置和使用 DeepSeek API。
