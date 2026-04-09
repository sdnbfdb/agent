#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
飞书机器人接口（使用长连接 WebSocket）
集成 DeepSeek AI 和工具调用能力
无需公网 IP，无需 ngrok
"""

import json
import requests
from typing import Dict, Any, Optional

# 导入飞书 SDK
try:
    import lark_oapi as lark
    from lark_oapi.api.im.v1 import *
    from lark_oapi.api.im.v1 import P2ImMessageReceiveV1
except ImportError as e:
    print(f"❌ 未安装 lark_oapi SDK: {e}")
    print("请运行：pip install lark-oapi")
    import sys
    sys.exit(1)

# 导入现有工具
from tool import (
    get_current_location,
    get_weather_by_location,
    query_history,
    get_history_stats
)

# 导入 DeepSeek 配置
from use import (
    DEEPSEEK_API_KEY,
    DEEPSEEK_API_URL,
    MODEL_NAME,
    call_deepseek_api,
    detect_tool_call,
    call_tool
)

# 飞书配置
FEISHU_APP_ID = "cli_a95c454f0d389bc0"  # 飞书应用 ID
FEISHU_APP_SECRET = "gPhVvBs0iD69JVkJkAtfafBEfide37tG"  # 飞书应用密钥

# 创建飞书客户端占位符，将在 main() 中初始化
cli = None
# 创建 HTTP 客户端用于发送消息
http_client = None


def send_feishu_message(chat_id: str, content: str) -> bool:
    """
    发送消息到飞书
    
    Args:
        chat_id: 会话 ID
        content: 消息内容
        
    Returns:
        是否发送成功
    """
    global http_client
    
    try:
        # 创建请求
        request = CreateMessageRequest.builder() \
            .receive_id_type("chat_id") \
            .request_body(CreateMessageRequestBody.builder()
                .receive_id(chat_id)
                .msg_type("text")
                .content(json.dumps({"text": content}))
                .build()) \
            .build()
        
        # 发送消息（使用 HTTP 客户端）
        response = http_client.im.v1.message.create(request)
        
        if response.success():
            print(f"✅ 消息发送成功到 {chat_id}")
            return True
        else:
            print(f"❌ 消息发送失败: {response.code}, {response.msg}")
            return False
            
    except Exception as e:
        print(f"❌ 发送消息异常：{e}")
        import traceback
        traceback.print_exc()
        return False


def process_message(user_message: str) -> str:
    """
    处理用户消息并调用 DeepSeek 回复
    
    Args:
        user_message: 用户消息
        
    Returns:
        AI 回复内容
    """
    try:
        # 检测是否需要调用工具
        tool_name, tool_params = detect_tool_call(user_message)
        
        if tool_name:
            print(f"🔧 调用工具：{tool_name}")
            tool_result = call_tool(tool_name, tool_params)
            
            # 构建增强提示词
            enhanced_prompt = f"""用户问题：{user_message}

--- 工具查询结果 ---
{tool_result}
--- 结束 ---

请根据上面的工具查询结果，用自然语言回答用户的问题。"""
            
            messages = [{'role': 'user', 'content': enhanced_prompt}]
            response = call_deepseek_api(messages)
            
        else:
            # 直接对话
            messages = [{'role': 'user', 'content': user_message}]
            response = call_deepseek_api(messages)
        
        return response.strip()
        
    except Exception as e:
        error_msg = f"处理消息失败：{str(e)}"
        print(error_msg)
        return error_msg


# 事件处理函数
def on_message_receive(data: P2ImMessageReceiveV1):
    """
    处理接收到的消息事件
    
    Args:
        data: 消息事件数据
    """
    print(f"\n🔔 收到事件回调！")
    print(f"事件数据: {data}")
    
    try:
        # 获取消息内容
        event = data.event
        message = event.message
        
        print(f"消息类型: {message.message_type}")
        print(f"消息内容: {message.content}")
        
        # 只处理文本消息
        if message.message_type != "text":
            print(f"⚠️  跳过非文本消息: {message.message_type}")
            return
        
        # 解析消息内容
        content_obj = json.loads(message.content)
        user_message = content_obj.get("text", "").strip()
        
        # 移除 @机器人 的部分
        if user_message.startswith("@_user_1"):
            user_message = user_message.replace("@_user_1", "").strip()
        
        if not user_message:
            print("⚠️  消息内容为空")
            return
        
        chat_id = message.chat_id
        print(f"\n✅ 收到消息 [{chat_id}]: {user_message}")
        
        # 处理消息
        reply = process_message(user_message)
        
        # 发送回复
        send_feishu_message(chat_id, reply)
        
    except Exception as e:
        print(f"❌ 处理消息异常：{e}")
        import traceback
        traceback.print_exc()


def main():
    """主函数"""
    global cli, http_client
    
    print("╔════════════════════════════════════════╗")
    print("║   飞书机器人 - DeepSeek Agent         ║")
    print("║   (长连接 WebSocket 模式)              ║")
    print("╚════════════════════════════════════════╝\n")
    
    print("配置信息:")
    print(f"  - App ID: {FEISHU_APP_ID}")
    print(f"  - DeepSeek API: {'已配置' if DEEPSEEK_API_KEY != 'sk-your-api-key-here' else '未配置'}")
    print()
    
    print("功能特性:")
    print("  ✅ 无需公网 IP")
    print("  ✅ 无需 ngrok")
    print("  ✅ 自动重连")
    print("  ✅ 支持工具调用")
    print()
    
    # 创建 HTTP 客户端（用于发送消息）
    print("初始化 HTTP 客户端...")
    http_client = lark.Client.builder() \
        .app_id(FEISHU_APP_ID) \
        .app_secret(FEISHU_APP_SECRET) \
        .log_level(lark.LogLevel.DEBUG) \
        .build()
    print("✅ HTTP 客户端初始化成功\n")
    
    # 注册事件处理器
    print("注册事件处理器...")
    event_handler = (
        lark.EventDispatcherHandler.builder("", "")
        .register_p2_im_message_receive_v1(on_message_receive)
        .build()
    )
    print("✅ 事件处理器注册成功\n")
    
    # 创建飞书客户端（用于长连接）
    cli = lark.ws.Client(
        app_id=FEISHU_APP_ID,
        app_secret=FEISHU_APP_SECRET,
        log_level=lark.LogLevel.DEBUG,
        event_handler=event_handler
    )
    
    print("=" * 60)
    print("正在连接到飞书服务器...")
    print("=" * 60)
    print()
    print("提示：")
    print("  - 保持此程序运行")
    print("  - 在飞书中 @机器人 即可使用")
    print("  - 按 Ctrl+C 退出")
    print()
    
    # 启动长连接
    cli.start()


if __name__ == "__main__":
    main()
