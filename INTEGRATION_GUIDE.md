# Agent 工具集成指南

## 📋 概述

本项目已实现完整的工具链，Agent 可以自动识别和调用以下工具：

1. **get_current_location()** - 获取当前位置
2. **get_weather_by_location(location)** - 查询天气
3. **query_history(keyword, limit)** - 查询历史对话
4. **get_history_stats()** - 获取历史统计

---

## 🔧 文件结构

```
agent/
├── tool.py                    # 工具函数实现（已添加完整文档）
├── use.py                     # Agent 启动程序（已添加工具说明）
├── history.py                 # 历史记录管理
├── register_tools.py          # 工具注册和测试脚本 ⭐ NEW
├── AGENT_TOOLS.md             # 详细工具文档 ⭐ NEW
└── README_TOOL.md             # 原有工具说明
```

---

## ✅ 已完成的改进

### 1. **tool.py - 增强文档**

每个工具函数都添加了：
- ✅ Agent 工具描述
- ✅ 参数说明
- ✅ 返回格式
- ✅ 使用场景提示

**示例**:
```python
def query_history(keyword=None, limit=10):
    """查询历史对话记录
    
    Agent 工具描述：搜索和查看用户与 AI 的历史对话记录
    参数:
        keyword (str, optional): 搜索关键词，会同时匹配问题和答案
        limit (int, optional): 返回的记录数量，默认 10 条
    返回格式：{'success': bool, 'count': int, 'records': [...]}
    """
```

### 2. **use.py - 工具提示**

在启动时显示可用工具信息：
```
🤖 正在启动 agent 模型...

==================================================
提示：输入 'quit' 或 'exit' 退出对话
可用工具：位置查询、天气查询、历史记录查询
==================================================
```

### 3. **register_tools.py - 工具验证** ⭐

运行此脚本可以：
- 测试所有工具是否正常工作
- 显示每个工具的详细信息
- 验证 Agent 可以使用这些工具

**使用方法**:
```bash
# 显示工具信息并运行测试
python register_tools.py

# 只显示工具信息
python register_tools.py --info

# 只运行测试
python register_tools.py --test
```

### 4. **AGENT_TOOLS.md - 完整文档** ⭐

包含：
- 每个工具的详细说明
- 使用场景和示例
- Agent 调用指南
- 最佳实践
- Modelfile 配置示例

---

## 🚀 如何让 Agent 使用工具

### 方法 1: Ollama Modelfile 配置

创建或修改 `Modelfile`：

```dockerfile
FROM agent:latest

SYSTEM """
你是一个智能助手，可以调用以下 Python 工具：

1. get_current_location() - 获取用户当前位置
   用途：当用户问"我在哪里"时使用

2. get_weather_by_location(location) - 查询天气
   用途：当用户询问天气时使用
   参数：location (可选) - 城市名称

3. query_history(keyword, limit) - 查询历史对话
   用途：当用户想查看聊天记录时使用
   参数：keyword (可选) - 搜索关键词
         limit (可选) - 返回数量，默认 10

4. get_history_stats() - 获取历史统计
   用途：当用户询问对话次数时使用

当你需要这些功能时，请明确告诉用户你将调用相应的工具。
"""
```

然后创建模型：
```bash
ollama create agent -f Modelfile
```

### 方法 2: Python 代码集成

在 `use.py` 中已经导入了工具模块。要让 Agent 真正能够调用，有两种方案：

#### 方案 A: 使用 Ollama Functions（推荐）

Ollama 支持函数调用功能。参考官方文档设置函数定义。

#### 方案 B: 提示词工程

在系统提示词中说明工具的存在，让 Agent 知道可以调用：

```python
SYSTEM_PROMPT = """
你是一个智能助手。你可以使用以下工具来帮助用户：

工具列表：
- get_current_location(): 获取用户位置
- get_weather_by_location(city): 查询指定城市天气
- query_history(keyword): 搜索历史对话
- get_history_stats(): 查看对话统计

当用户请求相关信息时，你可以说：
"让我使用 [工具名] 来帮你查询..."

然后实际调用 Python 函数获取结果。
"""
```

---

## 💡 实际应用示例

### 示例 1: 位置和天气

**用户**: "我在哪里？这里天气怎么样？"

**Agent 应该**:
1. 识别需要位置信息 → 调用 `get_current_location()`
2. 识别需要天气信息 → 调用 `get_weather_by_location()`
3. 组合结果回复用户

**Python 实现**:
```python
from tool import get_current_location, get_weather_by_location

location = get_current_location()
weather = get_weather_by_location()

print(f"你在 {location['city']}")
print(f"今天天气：{weather['description']}, {weather['temperature']}°C")
```

### 示例 2: 历史查询

**用户**: "我之前问过关于天气的问题吗？"

**Agent 应该**:
1. 识别需要搜索历史 → 调用 `query_history(keyword='天气')`
2. 分析结果并回复

**Python 实现**:
```python
from tool import query_history

history = query_history(keyword='天气')
if history['count'] > 0:
    print(f"是的，您问过 {history['count']} 次关于天气的问题")
else:
    print("没有找到相关记录")
```

### 示例 3: 统计信息

**用户**: "我和你对过多少次话？"

**Agent 应该**:
1. 识别需要统计 → 调用 `get_history_stats()`
2. 格式化结果回复

**Python 实现**:
```python
from tool import get_history_stats

stats = get_history_stats()
print(f"我们进行了 {stats['total_sessions']} 次会话")
print(f"总共 {stats['total_conversations']} 轮对话")
```

---

## 🧪 测试工具

### 快速测试

```bash
# 测试所有工具
python register_tools.py

# 预期输出:
# ✓ 位置查询成功
# ✓ 天气查询成功  
# ✓ 历史查询成功
# ✓ 关键词搜索成功
# ✓ 统计查询成功
# 所有工具都已就绪
```

### 单独测试某个工具

```python
# 测试位置查询
python -c "import tool; print(tool.get_current_location())"

# 测试天气查询
python -c "import tool; print(tool.get_weather_by_location('北京'))"

# 测试历史查询
python -c "import tool; print(tool.query_history(limit=5))"

# 测试统计
python -c "import tool; print(tool.get_history_stats())"
```

---

## 📊 工具调用流程

```
用户问题
  ↓
Agent 识别意图
  ↓
选择合适的工具
  ↓
调用 Python 函数
  ↓
解析返回结果
  ↓
生成自然语言回复
```

---

## ⚠️ 注意事项

### 1. **错误处理**

工具可能失败（网络问题、API 限制等），Agent 应该：
```python
result = get_weather_by_location()
if 'error' in result:
    return f"抱歉，无法获取天气信息：{result['error']}"
else:
    return f"今天天气是：{result['description']}"
```

### 2. **结果格式化**

不要直接显示 JSON，要转换为自然语言：
```python
# ❌ 不好
print(result)  # {'location': '上海', 'temperature': 18.2, ...}

# ✅ 好
print(f"上海今天温度 {result['temperature']}°C，{result['description']}")
```

### 3. **隐私保护**

位置和历史信息属于隐私，使用时要：
- 只在用户明确请求时使用
- 不要在公开场合显示
- 提供删除历史的选项

---

## 🔗 相关文档

- **AGENT_TOOLS.md** - 详细工具文档
- **README_TOOL.md** - 原工具说明
- **README_HISTORY_USAGE.md** - 历史记录使用说明

---

## 🎯 下一步

要让 Agent 真正能够自动调用这些工具，你需要：

1. **配置 Ollama Functions**（如果支持）
   - 参考 Ollama 官方文档的函数调用功能
   
2. **或者使用 LangChain/Ollama 集成**
   ```python
   from langchain_community.llms import Ollama
   from langchain.tools import Tool
   
   # 定义工具
   tools = [
       Tool(name="Location", func=get_current_location),
       Tool(name="Weather", func=get_weather_by_location),
       Tool(name="History", func=query_history),
       Tool(name="Stats", func=get_history_stats),
   ]
   
   # 创建带工具的 Agent
   llm = Ollama(model="agent")
   agent = initialize_agent(tools, llm, agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION)
   ```

3. **或者自定义工具调用逻辑**
   - 在 `use.py` 中添加命令解析
   - 检测特定关键词自动调用工具

---

## 📞 快速验证

运行以下命令验证所有工具：

```bash
cd C:\Users\sanjin\Desktop\agent
python register_tools.py
```

如果看到所有测试都通过（✓），说明工具已经准备好可以被 Agent 使用了！
