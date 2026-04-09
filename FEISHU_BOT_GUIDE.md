# 飞书机器人配置指南（长连接模式）

## 📋 概述

飞书机器人集成 DeepSeek AI 能力，支持工具调用（天气查询、位置查询、历史记录等）。

**重要特性**：
- ✅ **无需公网 IP**
- ✅ **无需 ngrok**
- ✅ **使用 WebSocket 长连接**
- ✅ **自动重连**

## 🔑 前置准备

### 1. 创建飞书应用

1. 访问 [飞书开放平台](https://open.feishu.cn/)
2. 登录并创建企业自建应用
3. 记录以下信息：
   - **App ID**
   - **App Secret**
   - **Verification Token**

### 2. 配置应用权限

在飞书开放平台 -> 应用功能 -> 权限管理中，添加以下权限：

- `im:message` - 发送消息
- `im:message:send_as_bot` - 以应用身份发送消息
- `im:chat` - 获取群组信息
- `contact:user.id:readonly` - 读取用户 ID

### 3. 配置事件订阅

1. 进入 **事件与回调** -> **事件配置**
2. 添加事件：`im.message.receive_v1`（接收消息）
3. 设置请求地址：`https://your-domain.com/webhook/event`

### 4. 配置机器人能力

1. 进入 **应用功能** -> **机器人**
2. 启用机器人能力
3. 配置机器人名称和头像

## ⚙️ 配置

编辑 `robot.py` 文件，修改以下配置：

```python
# 飞书配置（第 42-43 行）
FEISHU_APP_ID = "cli_a95c454f0d389bc0"  # 飞书应用 ID
FEISHU_APP_SECRET = "gPhVvBs0iD69JVkJkAtfafBEfide37tG"  # 飞书应用密钥
```

## 🚀 安装依赖

```bash
pip install lark-oapi requests
```

## 🏃 启动服务

### 本地运行

```bash
python robot.py
```

或使用启动脚本（推荐）：

```bash
python start_robot.py
```

### 生产环境

使用 systemd 或 supervisor 管理进程：

```bash
# 使用 systemd
sudo systemctl start feishu-bot
sudo systemctl enable feishu-bot
```

## 🔧 工作原理

### 长连接模式

飞书机器人使用 **WebSocket 长连接**：

1. 启动后，程序主动连接飞书服务器
2. 建立 WebSocket 连接
3. 飞书通过此连接推送消息事件
4. 程序处理消息并回复

**优势**：
- 不需要公网 IP
- 不需要 ngrok 或内网穿透
- 自动重连机制
- 更稳定可靠

## 💡 使用示例

### 在飞书中使用

1. 将机器人添加到群组
2. @机器人 并发送消息

### 支持的命令

| 命令 | 功能 |
|------|------|
| "我在哪里？" | 查询位置 |
| "天气怎么样？" | 查询长治天气（默认） |
| "北京天气" | 查询指定城市天气 |
| "查看历史记录" | 查询历史对话 |
| "对话统计" | 查看对话统计信息 |
| 任意问题 | DeepSeek 智能对话 |

## 🔒 安全建议

### 1. 使用 HTTPS

生产环境必须使用 HTTPS，可以通过：
- Nginx 反向代理
- 云服务商的负载均衡
- Let's Encrypt 免费证书

### 2. 验证签名

飞书会发送签名验证，可以在代码中添加：

```python
def verify_signature(timestamp, nonce, encrypt_key, signature):
    """验证飞书请求签名"""
    content = timestamp + nonce + encrypt_key
    sha256 = hashlib.sha256(content.encode('utf-8')).hexdigest()
    return sha256 == signature
```

### 3. 限制访问 IP

在防火墙或 WAF 中限制只允许飞书服务器 IP 访问。

## 🐛 常见问题

### Q1: 收不到消息
```
原因：事件订阅 URL 配置错误或服务未启动
解决：
1. 检查 /webhook/event 是否可以访问
2. 查看服务日志
3. 验证 URL 验证是否通过
```

### Q2: 消息发送失败
```
原因：权限不足或 token 过期
解决：
1. 检查应用权限配置
2. 查看 tenant_access_token 是否获取成功
3. 查看 API 返回的错误信息
```

### Q3: DeepSeek API 调用失败
```
原因：API Key 配置错误或网络问题
解决：
1. 检查 DEEPSEEK_API_KEY 配置
2. 测试网络连通性
3. 查看错误日志
```

## 📊 日志查看

服务运行时会输出详细日志：

```
收到消息 [oc_xxxxx]: 天气怎么样？
🔧 调用工具：get_weather_by_location
消息发送成功到 oc_xxxxx
```

## 🔄 更新和维护

### 更新代码

```bash
git pull origin main
python robot.py  # 重启服务
```

### 查看状态

```bash
curl http://localhost:5000/health
```

## 📝 注意事项

1. **Token 有效期**: tenant_access_token 有效期为 2 小时，代码会自动刷新
2. **消息长度限制**: 飞书单条消息最大 150KB
3. **频率限制**: 注意飞书 API 的调用频率限制
4. **默认城市**: 天气查询默认使用长治，可在 use.py 中修改

## 🔗 相关资源

- [飞书开放平台文档](https://open.feishu.cn/document)
- [消息收发指南](https://open.feishu.cn/document/uAjLw4CM/ukTMukTMukTM/reference/im-v1/message/create)
- [事件订阅](https://open.feishu.cn/document/home/develop-a-bot-in-5-minutes/create-an-app)

---

**技术支持**: sanjnw378@gmail.com
