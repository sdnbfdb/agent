# Agent - 智能对话助手（带历史记录功能）

基于 Ollama 和 DeepSeek 模型的本地智能对话助手，支持工具调用和历史记录管理。

## ✨ 功能特性

### 🧠 核心能力

- **DeepSeek 模型推理** - 使用 DeepSeek-R1 模型进行深度思考和推理
- **智能工具调用** - 自动识别用户意图并调用相应工具

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

### 🔧 配置说明

Agent 会自动识别用户意图并调用相应工具：
- "我在哪里？" → 调用位置查询
- "天气怎么样？" → 调用天气查询
- "查看历史记录" → 调用历史查询
- "我们对话过多少次？" → 调用统计查询

## 📁 项目结构

```
agent/
├── use.py              # Agent 启动程序（主入口）
├── tool.py             # 工具函数集合
├── history.py          # 历史记录管理
├── history.txt         # 数据存储文件（自动生成）
├── .gitignore
└── README.md
```

## 🚀 快速开始

### 环境要求

- Python 3.8+
- Ollama（已安装并配置）
- 网络连接（用于位置和天气 API）

### 安装与运行

1. **克隆项目**
```bash
git clone <your-repo-url>
cd agent
```

2. **运行 Agent**
```bash
python use.py
```

3. **开始对话**
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

### 🔧 配置说明

#### Ollama 配置

编辑 `use.py` 中的配置：

```python
OLLAMA_EXE = r"C:\Users\sanjin\AppData\Local\Programs\Ollama\ollama.exe"
OLLAMA_MODELS_PATH = r"E:\ollama_models"
MODEL_NAME = "deepseek-r1"  # DeepSeek-R1 模型
```

#### 模型要求

- **推理模型**: DeepSeek-R1 (通过 Ollama 运行)
- **安装方法**: 
  ```bash
  ollama pull deepseek-r1
  ```

### API 说明

- **位置查询**: 使用 ipapi.co、ip-api.com、ipinfo.io（自动故障转移）
- **天气查询**: 使用 Open-Meteo API（免费，无需 API key）

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

如有问题请提交 Issue。
