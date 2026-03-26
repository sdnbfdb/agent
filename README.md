# Agent - 智能对话助手（DeepSeek + RAG）

基于 **DeepSeek** 和 **ChromaDB** 的智能对话助手，支持工具调用、历史记录管理和 RAG 文档向量化。

## ✨ 核心功能

### 🤖 DeepSeek 对话
- 使用 DeepSeek Chat API 进行智能对话
- 支持上下文记忆（保留最近 10 轮对话）
- 自动工具调用和结果整合

## ✨ 功能特性

### 🛠️ 可用工具

1. **位置查询** - 自动获取用户当前位置
2. **天气查询** - 查询指定地点或当前位置的天气
3. **历史对话查询** - 搜索和查看历史对话记录
4. **统计信息** - 获取对话统计数据

### 💾 历史记录

- 自动保存每次对话到 `history.txt`
- 支持关键词搜索历史记录
- 按时间戳组织会话
- 隐私数据本地存储

### 🤖 智能工具调用

Agent 会自动识别用户意图并调用相应工具：
- "我在哪里？" → 调用位置查询
- "天气怎么样？" → 调用天气查询
- "查看历史记录" → 调用历史查询
- "我们对话过多少次？" → 调用统计查询

### 📚 RAG 文档处理（新增）
- Markdown 文本智能分片（typing 类型标注）
- sentence-transformers 向量化（BAAI/bge-small-zh-v1.5）
- ChromaDB 向量数据库存储
- 语义相似度搜索

## 📁 项目结构

```
agent/
├── use.py                      # Agent 主程序（DeepSeek API）
├── tool.py                     # 工具函数集合
├── history.py                  # 历史记录管理
├── markdown_chunker.py         # Markdown 分片处理器
├── chrome.py                   # 文本向量化生成器
├── chroma_manager.py           # ChromaDB 管理器
├── test_chroma.py              # 简单测试脚本
├── cc.md                       # 示例文本（朱自清《匆匆》）
├── chroma_db/                  # 向量数据库目录
├── DEEPSEEK_INTEGRATION.md     # DeepSeek 集成指南 ⭐
└── README.md
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- DeepSeek API Key（获取方式见 [DEEPSEEK_CONFIG.md](DEEPSEEK_CONFIG.md)）
- 网络连接（用于 API 调用和工具查询）

### 安装与运行

1. **克隆项目**
```bash
git clone https://github.com/sdnbfdb/agent.git
cd agent
```

2. **配置 DeepSeek API Key**
编辑 `use.py` 文件，设置你的 API Key：
```python
DEEPSEEK_API_KEY = "sk-your-actual-api-key"  # 替换为真实 API Key
```

3. **运行 Agent**
```bash
python use.py
```

4. **开始对话**
```
你：你好
你：我在哪里？
你：天气怎么样？
你：查看历史记录
```

## 📊 数据格式

### 历史记录格式

```
2026-03-25 15:31:57:[第 1 次询问：你好。第 1 次回答：你好！有什么可以帮助你的？。第 2 次询问：天气如何。第 2 次回答：今天天气晴朗...]
```

### 工具返回格式

**位置查询**:
```python
{
    'ip': '120.208.155.54',
    'city': 'Shanghai',
    'region': 'Shanghai',
    'country': 'CN',
    'latitude': 31.2222,
    'longitude': 121.4581
}
```

**天气查询**:
```python
{
    'location': '上海',
    'temperature': 18.2,
    'wind_speed': 4.7,
    'description': '部分多云'
}
```

**历史查询**:
```python
{
    'success': True,
    'count': 2,
    'records': [{
        'timestamp': '2026-03-25 15:31:57',
        'conversations': {
            1: {'question': '你好', 'answer': '你好！'},
            2: {'question': '天气', 'answer': '晴朗'}
        }
    }]
}
```

## 🔧 配置说明

### DeepSeek API 配置

详细配置说明请查看：[DEEPSEEK_CONFIG.md](DEEPSEEK_CONFIG.md) 或 [DEEPSEEK_INTEGRATION.md](DEEPSEEK_INTEGRATION.md) ⭐

**快速配置**：
1. 获取 API Key：https://platform.deepseek.com/
2. 编辑 `use.py`，设置 `DEEPSEEK_API_KEY`
3. 运行 `python use.py` 开始使用

### API 说明

- **位置查询**: 使用 ipapi.co、ip-api.com、ipinfo.io（自动故障转移）
- **天气查询**: 使用 Open-Meteo API（免费，无需 API key）

## 🆕 新功能

### RAG 文档向量化流程

```bash
# 1. 分片处理
python markdown_chunker.py

# 2. 生成向量并存储到 ChromaDB
$env:HF_ENDPOINT="https://hf-mirror.com"; python chrome.py

# 3. 查询测试
$env:HF_ENDPOINT="https://hf-mirror.com"; python test_chroma.py
```

## 🆕 新功能

### RAG 文档向量化流程

```bash
# 1. 分片处理
python markdown_chunker.py

# 2. 生成向量并存储到 ChromaDB
$env:HF_ENDPOINT="https://hf-mirror.com"; python chrome.py

# 3. 查询测试
$env:HF_ENDPOINT="https://hf-mirror.com"; python test_chroma.py
```

## 📝 使用示例

### 示例 1: 查询位置和天气

```
你：我在哪里？
🔧 调用工具：get_current_location
agent: 根据定位，你现在位于上海市...

你：这里天气怎么样？
🔧 调用工具：get_weather_by_location
agent: 上海今天部分多云，温度 18°C...
```

### 示例 2: 查看历史记录

```
你：我之前问过关于天气的问题吗？
🔧 调用工具：query_history(keyword='天气')
agent: 是的！您在 2026-03-25 15:31:57 问过："你好，请问今天天气如何？"
```

### 示例 3: 统计信息

```
你：我们进行过多少次对话？
🔧 调用工具：get_history_stats
agent: 到目前为止，我们已经进行了 5 次会话，总共 20 轮对话...
```

## 🐛 已知问题

暂无

## 📄 许可证

MIT License

## 🤝 贡献

欢迎提交 Issue 和 Pull Request！

## 📧 联系方式

- **Email**: sanjnw378@gmail.com
- **GitHub**: https://github.com/sdnbfdb/agent

如有问题或建议，请通过以下方式联系：
1. 提交 GitHub Issue
2. 发送邮件至 sanjnw378@gmail.com
