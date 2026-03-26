# 历史对话记录功能 - 使用说明

## 📝 保存格式

```
时间:[第一次询问：第一次回答。第二次询问：第二次回答...第 n 次询问：第 n 次回答]
```

**示例：**
```
2026-03-25 15:31:57:[第 1 次询问：你好，请问今天天气如何？。第 1 次回答：今天天气晴朗，温度适宜...。第 2 次询问：谢谢！。第 2 次回答：不客气，有其他问题吗？]
```

---

## 🚀 使用方法

### 方式 1：交互式对话（推荐）

```bash
python C:\Users\sanjin\Desktop\agent\use.py
```

**交互过程：**
1. 运行后自动开始新会话
2. 输入你的问题，按回车发送
3. AI 回复后会自动保存对话
4. 输入 `exit` 或 `quit` 结束对话
5. 所有对话会一次性保存到 `history.txt`

**示例对话：**
```
╔════════════════════════════════════════╗
║       Agent 启动程序（带历史记录）     ║
╚════════════════════════════════════════╝


🤖 正在启动 agent 模型...

==================================================
提示：输入 'quit' 或 'exit' 退出对话
==================================================


📝 新会话开始于 2026-03-25 15:31:57

你：你好

agent: 你好！有什么可以帮助你的吗？

你：今天天气怎么样

agent: 今天天气晴朗，温度适宜，适合外出活动。

你：exit

再见！

💾 已保存 2 条对话记录
```

---

### 方式 2：单次查询

```bash
python C:\Users\sanjin\Desktop\agent\use.py "今天天气怎么样"
```

**说明：**
- 自动开始并结束一个会话
- 查询结果会保存到 `history.txt`
- 适合快速查询并记录

---

## 📂 文件位置

- **程序文件**：
  - `C:\Users\sanjin\Desktop\agent\use.py` - Agent 启动程序（带历史记录）
  - `C:\Users\sanjin\Desktop\agent\history.py` - 历史记录管理模块

- **数据文件**：
  - `C:\Users\sanjin\Desktop\agent\history.txt` - 对话记录存储文件

---

## 💡 功能特点

### ✅ 自动保存
- 每次对话都会自动记录
- 无需手动操作保存
- 支持中文编码（UTF-8）

### ✅ 会话管理
- 每次运行自动创建新会话
- 会话开始时间作为时间戳
- 多条记录追加到文件，不会覆盖

### ✅ 异常保护
- 正常退出（输入 exit/quit）会保存
- Ctrl+C 中断会保存已有记录
- 程序出错也会尝试保存记录

### ✅ 简洁格式
- 一行一条完整会话记录
- 时间戳 + 所有对话内容
- 方便查看和解析

---

## 📊 记录示例

### history.txt 内容示例

```
2026-03-25 15:31:57:[第 1 次询问：你好。第 1 次回答：你好！有什么可以帮助你的吗？。第 2 次询问：北京明天的天气。第 2 次回答：北京明天晴朗，最高温度 25°C。第 3 次询问：谢谢。第 3 次回答：不客气！]
2026-03-25 16:20:33:[第 1 次询问：帮我写一首诗。第 1 次回答：春眠不觉晓，处处闻啼鸟...]
```

### 说明

- **每行一条记录**：每次会话的所有对话保存在一行
- **时间戳**：会话开始的精确时间
- **序号**：每次询问和回答都有编号
- **分隔符**：使用 `:` 和 `。` 分隔不同部分

---

## ⚙️ 技术细节

### ConversationHistory 类

**主要方法：**
- `start_session()` - 开始新会话
- `add_conversation(询问，回答)` - 添加对话
- `save_session()` - 保存会话到文件
- `get_session_summary()` - 获取会话摘要

### 保存流程

1. 用户启动程序 → 创建 ConversationHistory 实例
2. 开始对话 → 调用 `start_session()` 记录开始时间
3. 每次问答 → 调用 `add_conversation()` 添加到内存
4. 结束对话 → 调用 `save_session()` 写入文件

### 文件格式化代码

```python
# 构建对话内容
conv_parts = []
for i, (question, answer) in enumerate(self.conversations, 1):
    conv_parts.append(f"第{i}次询问:{question}")
    conv_parts.append(f"第{i}次回答:{answer}")

# 合并所有对话
conversations_text = "。".join(conv_parts)

# 完整格式：时间:[第一次询问：第一次回答。第二次询问：第二次回答...]
record = f"{time_str}:[{conversations_text}]\n"
```

---

## 🔍 查看历史记录

### Windows 记事本
```bash
notepad C:\Users\sanjin\Desktop\agent\history.txt
```

### PowerShell 查看
```powershell
Get-Content C:\Users\sanjin\Desktop\agent\history.txt
```

### Python 读取
```python
with open(r"C:\Users\sanjin\Desktop\agent\history.txt", 'r', encoding='utf-8') as f:
    for line in f:
        print(line.strip())
```

---

## ⚠️ 注意事项

1. **编码格式**：文件使用 UTF-8 编码，确保中文正常显示
2. **追加模式**：新会话会追加到文件末尾，不会删除旧记录
3. **文件大小**：长期使用后文件会变大，可定期清理
4. **隐私保护**：记录包含完整对话内容，注意保管

---

## 🎯 快速开始

```bash
# 1. 运行 Agent（带历史记录）
python C:\Users\sanjin\Desktop\agent\use.py

# 2. 开始对话
你：你好
AI: 你好！有什么可以帮助你的？

你：今天天气如何
AI: 今天天气晴朗...

# 3. 结束对话
你：exit

# 4. 查看记录
notepad C:\Users\sanjin\Desktop\agent\history.txt
```

---

## 📞 常见问题

**Q: 如何清空历史记录？**  
A: 直接删除或清空 `history.txt` 文件即可
```bash
# PowerShell 清空文件
Clear-Content C:\Users\sanjin\Desktop\agent\history.txt
```

**Q: 可以保存多少次对话？**  
A: 没有数量限制，直到关闭终端或输入 exit

**Q: 如果程序崩溃了会怎样？**  
A: 程序会尝试保存已有的对话记录

**Q: 能否自定义保存路径？**  
A: 可以修改 `history.py` 中的 `HISTORY_FILE_PATH` 变量
