#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 启动程序
用于调用 DeepSeek 模型进行思考推理，并整合工具调用能力

支持的工具 (来自 tool.py):
- get_current_location(): 获取当前位置
- get_weather_by_location(location): 查询天气
- query_history(keyword, limit): 查询历史对话
- get_history_stats(): 获取历史统计

模型：DeepSeek（通过 API 调用）
"""

import subprocess
import sys
import os
import re
import requests
from history import ConversationHistory
from tool import (
    get_current_location,
    get_weather_by_location,
    query_history,
    get_history_stats
)

# DeepSeek API 配置
DEEPSEEK_API_KEY = "sk-a980b787224a402ab52e0e8dd000494d"  # 从 Ollama Modelfile 中获取
DEEPSEEK_API_URL = "https://api.deepseek.com/v1/chat/completions"
MODEL_NAME = "deepseek-chat"


def setup_environment():
    """设置环境变量（DeepSeek 不需要特殊配置，保留此函数以兼容）"""
    env = os.environ.copy()
    return env


def check_ollama_running(env):
    """检查 DeepSeek API 是否可用（保留函数名以兼容）"""
    try:
        # 简单的 API 连通性测试
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        test_data = {
            'model': MODEL_NAME,
            'messages': [{'role': 'user', 'content': 'Hello'}],
            'max_tokens': 5
        }
        response = requests.post(DEEPSEEK_API_URL, json=test_data, headers=headers, timeout=10)
        return response.status_code == 200
    except Exception as e:
        print(f"⚠️  API 连接测试失败：{e}")
        return False


def call_deepseek_api(messages: list, system_prompt: str = None) -> str:
    """调用 DeepSeek API 进行思考推理
    
    Args:
        messages: 对话消息列表
        system_prompt: 可选的系统提示词
        
    Returns:
        DeepSeek 返回的回复内容
    """
    try:
        headers = {
            'Authorization': f'Bearer {DEEPSEEK_API_KEY}',
            'Content-Type': 'application/json'
        }
        
        # 构建请求数据
        payload = {
            'model': MODEL_NAME,
            'messages': messages,
            'temperature': 0.7,
            'max_tokens': 2048
        }
        
        # 如果有系统提示，添加到消息开头
        if system_prompt:
            payload['messages'].insert(0, {'role': 'system', 'content': system_prompt})
        
        response = requests.post(DEEPSEEK_API_URL, json=payload, headers=headers, timeout=60)
        response.raise_for_status()
        
        result = response.json()
        return result['choices'][0]['message']['content']
        
    except Exception as e:
        return f"DeepSeek API 调用失败：{str(e)}"


def start_ollama_service():
    """启动 Ollama 服务（保留以兼容，但 DeepSeek 模式不需要）"""
    print("⚠️  DeepSeek 模式不需要启动 Ollama 服务")
    return True


def call_tool(tool_name: str, params: dict = None):
    """调用工具函数
    
    Args:
        tool_name: 工具名称
        params: 工具参数
        
    Returns:
        格式化后的工具结果（文本格式）
    """
    try:
        if tool_name == 'get_current_location':
            result = get_current_location()
            if 'error' in result:
                return f"位置查询失败：{result['error']}"
            return f"当前位置：{result.get('city', '未知')}，{result.get('region', '未知')}，{result.get('country', '未知')}\n经纬度：{result.get('latitude', 0)}, {result.get('longitude', 0)}\nIP: {result.get('ip', '未知')}"
        
        elif tool_name == 'get_weather_by_location':
            location = params.get('location') if params else None
            result = get_weather_by_location(location)
            if 'error' in result:
                return f"天气查询失败：{result['error']}"
            return f"{result.get('location', '未知')}天气：{result.get('description', '未知')}\n温度：{result.get('temperature', 0)}°C\n风速：{result.get('wind_speed', 0)} km/h\n时间：{result.get('time', '未知')}"
        
        elif tool_name == 'query_history':
            keyword = params.get('keyword') if params else None
            limit = params.get('limit', 10) if params else 10
            result = query_history(keyword, limit)
            
            if 'error' in result:
                return f"历史查询失败：{result['error']}"
            
            if not result.get('success') or result.get('count', 0) == 0:
                return "未找到相关历史记录"
            
            # 格式化历史记录为易读的文本
            output_lines = [f"找到 {result['count']} 条历史记录:"]
            
            for i, record in enumerate(result['records'][:3], 1):  # 只显示前 3 条
                timestamp = record.get('timestamp', '未知时间')
                total = record.get('total_pairs', 0)
                output_lines.append(f"\n【会话 {i}】{timestamp} (共{total}轮对话)")
                
                # 显示前 2 组问答
                conversations = record.get('conversations', {})
                for qa_num, qa in list(conversations.items())[:2]:
                    question = qa.get('question', '')[:50]
                    answer = qa.get('answer', '')[:100]
                    output_lines.append(f"  问：{question}")
                    output_lines.append(f"  答：{answer}")
                
                if total > 2:
                    output_lines.append(f"  ... 还有 {total - 2} 轮对话")
            
            return "\n".join(output_lines)
        
        elif tool_name == 'get_history_stats':
            result = get_history_stats()
            if 'error' in result:
                return f"统计查询失败：{result['error']}"
            
            if not result.get('success'):
                return "获取统计信息失败"
            
            return (f"历史统计:\n"
                    f"总会话数：{result.get('total_sessions', 0)}\n"
                    f"总对话数：{result.get('total_conversations', 0)}\n"
                    f"最早会话：{result.get('earliest_session', '无')}\n"
                    f"最新会话：{result.get('latest_session', '无')}")
        
        else:
            return f'未知工具：{tool_name}'
    except Exception as e:
        return f'工具调用失败：{str(e)}'


def detect_tool_call(user_input: str) -> tuple:
    """检测用户输入是否需要调用工具
    
    Args:
        user_input: 用户输入
        
    Returns:
        (tool_name, params) 或 (None, None)
    """
    user_lower = user_input.lower()
    
    # 位置查询
    if any(kw in user_lower for kw in ['我在哪里', '我的位置', '当前位置', 'where am i']):
        return 'get_current_location', {}
    
    # 天气查询
    if any(kw in user_lower for kw in ['天气', 'weather', '温度', '气温', '下雨', '晴天', '阴天']):
        # 尝试提取城市名
        city_match = re.search(r'(北京 | 上海 | 广州 | 深圳 | 杭州|beijing|shanghai|guangzhou|shenzhen|hangzhou)', user_lower)
        city = city_match.group(0) if city_match else None
        return 'get_weather_by_location', {'location': city}
    
    # 历史查询
    if any(kw in user_lower for kw in ['历史记录', '聊天记录', '之前的对话', '之前问过', 'history', '记录', '对话历史', '查看历史']):
        # 尝试提取关键词
        keyword = None
        if '关于' in user_input:
            kw_match = re.search(r'关于 (.+?)(?:的 |$)', user_input)
            if kw_match:
                keyword = kw_match.group(1)
        return 'query_history', {'keyword': keyword, 'limit': 5}
    
    # 统计查询
    if any(kw in user_lower for kw in ['多少次对话', '对过话', '活跃度', '统计', 'statistics']):
        return 'get_history_stats', {}
    
    return None, None


def run_agent_interactive(env, history: ConversationHistory):
    """交互式运行 agent 模型（带工具调用）"""
    print(f"\n🤖 正在启动 {MODEL_NAME} 模型...\n")
    print("=" * 50)
    print("提示：输入 'quit' 或 'exit' 退出对话")
    print("可用工具：位置查询、天气查询、历史记录查询")
    print("示例：问'我在哪里'、'天气怎么样'、'查看历史记录'")
    print("=" * 50 + "\n")
    
    # 开始新会话
    history.start_session()
    
    # 对话历史（用于保持上下文）
    conversation_history = []
    
    try:
        while True:
            user_input = input("\n你：").strip()
            
            if not user_input:
                continue
            
            if user_input.lower() in ['quit', 'exit']:
                print("\n再见！")
                break
            
            # 检测是否需要调用工具
            tool_name, tool_params = detect_tool_call(user_input)
            
            if tool_name:
                print(f"\n🔧 调用工具：{tool_name}")
                tool_result = call_tool(tool_name, tool_params)
                
                # 将工具结果添加到对话历史中
                messages = conversation_history.copy()
                messages.append({
                    'role': 'user', 
                    'content': f"""用户问题：{user_input}

--- 工具查询结果 ---
{tool_result}
--- 结束 ---

请根据上面的工具查询结果，用自然语言回答用户的问题。如果工具返回了数据，就基于数据回答；如果没有数据，就如实告知用户。"""
                })
                
                print(f"{MODEL_NAME}: ", end="", flush=True)
                output = call_deepseek_api(messages)
                print(output)
                
                # 保存到历史记录
                history.add_conversation(user_input, output.strip())
                
                # 更新对话历史（保留最近的 10 轮）
                conversation_history.append({'role': 'user', 'content': user_input})
                conversation_history.append({'role': 'assistant', 'content': output})
                if len(conversation_history) > 20:  # 保留最近 10 轮（每轮 2 条消息）
                    conversation_history = conversation_history[-20:]
                    
            else:
                # 不需要调用工具，直接对话
                print(f"{MODEL_NAME}: ", end="", flush=True)
                
                messages = conversation_history.copy()
                messages.append({'role': 'user', 'content': user_input})
                
                output = call_deepseek_api(messages)
                print(output)
                
                # 保存到历史记录
                history.add_conversation(user_input, output.strip())
                
                # 更新对话历史
                conversation_history.append({'role': 'user', 'content': user_input})
                conversation_history.append({'role': 'assistant', 'content': output})
                if len(conversation_history) > 20:
                    conversation_history = conversation_history[-20:]
        
        # 会话结束时保存所有记录
        history.save_session()
        
    except KeyboardInterrupt:
        print("\n\n对话已中断")
        # 即使中断也保存已有记录
        if len(history.conversations) > 0:
            history.save_session()
    except Exception as e:
        print(f"运行错误：{e}")
        # 出错时也尝试保存记录
        if len(history.conversations) > 0:
            history.save_session()


def run_agent_prompt(prompt, env, history: ConversationHistory):
    """单次提示运行（DeepSeek API 模式）"""
    print(f"\n🤖 向 {MODEL_NAME} 提问：{prompt}\n")
    print("=" * 50)
    
    # 开始会话
    history.start_session()
    
    try:
        # 调用 DeepSeek API
        messages = [{'role': 'user', 'content': prompt}]
        output = call_deepseek_api(messages)
        print(output)
        
        # 保存对话
        history.add_conversation(prompt, output.strip())
        history.save_session()
        
    except Exception as e:
        print(f"运行错误：{e}")


def main():
    """主函数"""
    print("╔════════════════════════════════════════╗")
    print("║  Agent - DeepSeek 智能对话助手         ║")
    print("║  (带历史记录功能)                      ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 初始化历史记录管理器
    history = ConversationHistory()
    
    # 设置环境变量
    env = setup_environment()
    
    # 检查 API 配置
    if DEEPSEEK_API_KEY == "sk-your-api-key-here":
        print("⚠️  警告：DeepSeek API Key 未配置！")
        print("请编辑 use.py 文件，设置 DEEPSEEK_API_KEY")
        print("获取 API Key: https://platform.deepseek.com/")
        print("\n按 Enter 继续（使用演示模式）...")
        input()
    
    # 测试 API 连接
    print("🔍 正在测试 DeepSeek API 连接...")
    if not check_ollama_running(env):
        print("❌ 无法连接到 DeepSeek API，请检查网络和 API Key 配置")
        print("程序将继续运行，但可能会失败...\n")
    else:
        print("✅ DeepSeek API 连接正常\n")
    
    # 选择运行模式
    if len(sys.argv) > 1:
        # 命令行参数模式
        prompt = " ".join(sys.argv[1:])
        run_agent_prompt(prompt, env, history)
    else:
        # 交互式模式
        run_agent_interactive(env, history)


if __name__ == "__main__":
    main()
