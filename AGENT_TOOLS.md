# Agent 工具描述 - 用于 Ollama 模型识别

## 🤖 可用工具列表

以下是 Agent 可以调用的所有工具函数。当用户请求相关功能时，Agent 应该调用相应的工具。

---

### 1. **get_current_location()** - 获取当前位置

**功能**: 获取用户当前的地理位置信息

**何时使用**: 
- 用户问"我在哪里？"、"我的位置"、"当前位置"等问题时
- 需要根据位置提供其他服务（如天气）时

**返回数据**:
```python
{
    'ip': '120.208.155.54',
    'city': 'Shanghai',
    'region': 'Shanghai', 
    'country': 'CN',
    'latitude': 31.2222,
    'longitude': 121.4581,
    'loc': '31.2222,121.4581'
}
```

**调用示例**:
```python
import tool
location = tool.get_current_location()
print(f"你在：{location['city']}")
```

---

### 2. **get_weather_by_location(location=None)** - 查询天气

**功能**: 查询指定地点或当前位置的天气情况

**何时使用**:
- 用户问"天气怎么样"、"今天冷吗"、"需要带伞吗"等问题时
- 用户提供城市名或要求查询当前位置天气时

**参数**:
- `location` (可选): 城市名称，如 "北京"、"Shanghai"。不提供则使用当前位置

**返回数据**:
```python
{
    'location': '上海',
    'temperature': 18.2,
    'wind_speed': 4.7,
    'wind_direction': 45,
    'weather_code': 2,
    'description': '部分多云',
    'time': '2026-03-25T06:45'
}
```

**调用示例**:
```python
import tool

# 查询当前位置天气
weather = tool.get_weather_by_location()

# 查询指定城市天气
weather = tool.get_weather_by_location("北京")
```

---

### 3. **query_history(keyword=None, limit=10)** - 查询历史对话

**功能**: 搜索和查看用户与 AI 的历史对话记录

**何时使用**:
- 用户问"我之前问过什么"、"查找历史记录"、"我之前说过..."等问题时
- 用户想回顾之前的对话内容时
- 用户提到"上次你说过..."时

**参数**:
- `keyword` (可选): 搜索关键词，会同时匹配问题和答案
- `limit` (可选): 返回的记录数量，默认 10 条

**返回数据**:
```python
{
    'success': True,
    'count': 2,
    'records': [{
        'timestamp': '2026-03-25 15:31:57',
        'conversations': {
            1: {'question': '你好', 'answer': '你好！有什么可以帮助你的？'},
            2: {'question': '天气如何', 'answer': '今天天气晴朗'}
        },
        'total_pairs': 2
    }]
}
```

**调用示例**:
```python
import tool

# 获取最近 10 条记录
history = tool.query_history()

# 搜索包含"天气"的对话
history = tool.query_history(keyword='天气')

# 获取最近 5 条记录
history = tool.query_history(limit=5)
```

**Agent 回复示例**:
- "我找到了您之前的 X 条对话记录..."
- "根据历史记录，您在 [时间] 问过：[问题]"
- "让我查一下您的历史记录..."

---

### 4. **get_history_stats()** - 获取历史统计

**功能**: 获取用户历史对话的统计信息

**何时使用**:
- 用户问"我和你对过多少次话"、"我的活跃度如何"等问题时
- 用户想了解自己的使用情况时

**返回数据**:
```python
{
    'success': True,
    'total_sessions': 5,
    'total_conversations': 20,
    'earliest_session': '2026-03-25 15:31:57',
    'latest_session': '2026-03-25 18:45:22'
}
```

**调用示例**:
```python
import tool
stats = tool.get_history_stats()
print(f"我们进行过 {stats['total_sessions']} 次对话")
```

**Agent 回复示例**:
- "到目前为止，我们已经进行了 X 次会话，总共 Y 轮对话"
- "您从 [时间] 开始使用，最近一次对话是在 [时间]"

---

## 🎯 Agent 使用指南

### 如何选择合适的工具

**场景 1: 位置相关**
```
用户："我在哪里？"
→ 调用 get_current_location()
```

**场景 2: 天气查询**
```
用户："北京天气怎么样？"
→ 调用 get_weather_by_location("北京")

用户："我这里天气如何？"
→ 先调用 get_current_location()，再调用 get_weather_by_location()
```

**场景 3: 历史查询**
```
用户："我之前问过关于天气的问题吗？"
→ 调用 query_history(keyword='天气')

用户："查看我的聊天记录"
→ 调用 query_history(limit=10)

用户："我们第一次对话是什么时候？"
→ 调用 get_history_stats()，然后查看 earliest_session
```

**场景 4: 统计信息**
```
用户："我和你对过多少次话？"
→ 调用 get_history_stats()
```

---

## 📝 工具调用最佳实践

### 1. **组合使用工具**
```python
# 用户："我这里天气怎么样？之前也问过吧"
# Agent 应该:
location = get_current_location()  # 获取位置
weather = get_weather_by_location()  # 查询天气
history = query_history(keyword='天气')  # 查找历史
```

### 2. **错误处理**
```python
result = get_weather_by_location()
if 'error' in result:
    return f"抱歉，无法获取天气信息：{result['error']}"
else:
    return f"今天天气是：{result['description']}，温度 {result['temperature']}°C"
```

### 3. **结果展示**
- 不要直接显示原始 JSON 数据
- 将结果转换为自然语言回复
- 只展示用户关心的关键信息

---

## 🔧 在 Ollama 中配置工具

### Modelfile 示例

```dockerfile
FROM agent:latest

# 定义系统提示词
SYSTEM """
你是一个智能助手，可以调用以下工具：

1. get_current_location() - 获取用户当前位置
2. get_weather_by_location(location) - 查询天气
3. query_history(keyword, limit) - 查询历史对话
4. get_history_stats() - 获取历史统计

当用户询问相关问题时，你应该：
1. 识别用户意图
2. 选择合适的工具
3. 调用工具并解析返回结果
4. 用自然语言回复用户

记住：
- 如果工具返回 error 字段，告诉用户出错了
- 尽量提供有帮助的、友好的回复
"""
```

### Python 中的工具注册

```python
# use.py 中添加工具导入
from tool import (
    get_current_location,
    get_weather_by_location,
    query_history,
    get_history_stats
)

# 在 Agent 启动时加载工具
tools = {
    'get_current_location': get_current_location,
    'get_weather_by_location': get_weather_by_location,
    'query_history': query_history,
    'get_history_stats': get_history_stats
}
```

---

## 💡 实际应用示例

### 示例 1: 完整对话流程

```
用户：我在哪里？
Agent: [调用 get_current_location()]
       你在上海市，经纬度是 31.2222°N, 121.4581°E

用户：那这里天气怎么样？
Agent: [调用 get_weather_by_location()]
       今天上海部分多云，温度 18.2°C，风速 4.7 km/h

用户：我之前问过天气吗？
Agent: [调用 query_history(keyword='天气')]
       是的，根据您的历史记录，您在 2026-03-25 15:31:57 
       问过："你好，请问今天天气如何？"
       我当时回答："今天天气晴朗，温度适宜..."
```

### 示例 2: 统计分析

```
用户：我和你对过多少次话？
Agent: [调用 get_history_stats()]
       到目前为止，我们已经进行了 5 次会话，
       总共 20 轮对话。
       第一次对话是在 2026-03-25 15:31:57，
       最近一次是在 2026-03-25 18:45:22。
```

### 示例 3: 历史搜索

```
用户：我之前问过关于位置的问题吗？
Agent: [调用 query_history(keyword='位置')]
       找到了！您在 2026-03-25 15:33:58 问过：
       "我在哪里"
       我回答了您的位置信息...
```

---

## ⚠️ 注意事项

1. **工具调用频率**: 避免短时间内频繁调用同一工具
2. **错误提示**: 工具失败时，友好地告知用户
3. **隐私保护**: 历史和位置信息属于隐私，谨慎处理
4. **结果限制**: 默认返回 10 条记录，避免信息过载

---

## 📊 工具优先级

当多个工具都适用时，按以下优先级选择：

1. **直接相关** > **间接相关**
2. **简单查询** > **复杂分析**
3. **实时数据** > **历史数据**

例如：
- 用户问"天气" → 优先调用 get_weather_by_location()
- 用户问"我之前问过天气吗" → 调用 query_history(keyword='天气')
