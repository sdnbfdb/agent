# Agent 工具使用说明

## 📦 工具文件位置
- **工具代码**: `C:\Users\sanjin\Desktop\agent\tool.py`

## 🛠️ 可用工具

### 1. 位置查询工具 - `get_current_location()`

**功能**: 获取当前位置信息

**API 来源** (按优先级):
1. ipapi.co (首选)
2. ip-api.com (备用)
3. ipinfo.io (备用)

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

**使用方法**:
```python
import tool
location = tool.get_current_location()
print(location)
```

---

### 2. 天气查询工具 - `get_weather_by_location(location=None)`

**功能**: 查询指定地点或当前位置的天气

**API 来源**: Open-Meteo API (免费，无需 API key)

**参数**:
- `location`: 可选，城市名称（如"北京"、"Shanghai"）
- 如果不提供参数，自动使用当前位置

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

**天气代码说明**:
- 0: 晴朗
- 1: 主要晴朗
- 2: 部分多云
- 3: 阴天
- 45: 雾
- 51-55: 雨
- 61-65: 降雨
- 71-75: 雪
- 95: 雷雨

**使用方法**:
```python
import tool

# 查询当前位置天气
weather = tool.get_weather_by_location()
print(weather)

# 查询指定城市天气
weather = tool.get_weather_by_location("北京")
print(weather)

weather = tool.get_weather_by_location("New York")
print(weather)
```

---

## 🤖 Agent 模型

**模型名称**: `agent:latest`  
**基础模型**: Llama 3.2 (3.2B)  
**存储位置**: `E:\ollama_models`

**配置信息**:
- DeepSeek API Key: `sk-a980b787224a402ab52e0e8dd000494d`
- 支持工具调用
- 支持中文回复

---

## 💡 使用示例

### 方式 1: 直接运行 Python 脚本
```bash
cd C:\Users\sanjin\Desktop\agent
python tool.py
```

### 方式 2: 通过 Agent 对话
```bash
python use.py "我在哪里？"
python use.py "查询我所在位置的天气"
python use.py "北京今天天气怎么样"
```

### 方式 3: 在 Python 代码中调用
```python
from tool import get_current_location, get_weather_by_location

# 获取位置
location = get_current_location()
print(f"我在：{location['city']}")

# 获取天气
weather = get_weather_by_location()
print(f"天气：{weather['description']}, 温度：{weather['temperature']}°C")
```

---

## ⚠️ 注意事项

1. **API 限流**: 
   - ipapi.co 有访问频率限制
   - 如果某个 API 失败，会自动尝试备用 API
   
2. **网络连接**: 
   - 需要联网才能使用
   - 如果所有位置 API 都失败，会返回错误信息

3. **天气 API**:
   - Open-Meteo 是免费的，无需 API key
   - 数据每 15 分钟更新一次

---

## 🔧 环境配置

**Ollama 环境变量**:
```powershell
$env:OLLAMA_MODELS="E:\ollama_models"
```

**Python 环境**:
- 路径：`C:\Users\sanjin\Desktop\agent\python_env`
- 包含：PyTorch, torchvision, requests 等

---

## 📝 完整测试流程

```bash
# 1. 测试位置查询
cd C:\Users\sanjin\Desktop\agent
python -c "import tool; print(tool.get_current_location())"

# 2. 测试天气查询（当前位置）
python -c "import tool; print(tool.get_weather_by_location())"

# 3. 测试天气查询（指定城市）
python -c "import tool; print(tool.get_weather_by_location('Beijing'))"

# 4. 通过 Agent 交互
python use.py "请告诉我现在的位置"
python use.py "查询当前位置的天气"
python use.py "上海的天气怎么样"
```
