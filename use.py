#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Agent 启动程序
用于启动 Ollama 的 agent 模型并与之交互

支持的工具 (来自 tool.py):
- get_current_location(): 获取当前位置
- get_weather_by_location(location): 查询天气
- query_history(keyword, limit): 查询历史对话
- get_history_stats(): 获取历史统计
"""

import subprocess
import sys
import os
import re
from history import ConversationHistory
from tool import (
    get_current_location,
    get_weather_by_location,
    query_history,
    get_history_stats
)

# 配置路径
OLLAMA_EXE = r"C:\Users\sanjin\AppData\Local\Programs\Ollama\ollama.exe"
OLLAMA_MODELS_PATH = r"E:\ollama_models"
MODEL_NAME = "agent"


def setup_environment():
    """设置环境变量"""
    env = os.environ.copy()
    env["OLLAMA_MODELS"] = OLLAMA_MODELS_PATH
    return env


def check_ollama_running(env):
    """检查 Ollama 服务是否运行"""
    try:
        result = subprocess.run(
            [OLLAMA_EXE, "list"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        return result.returncode == 0
    except Exception as e:
        print(f"检查 Ollama 服务失败：{e}")
        return False


def start_ollama_service():
    """启动 Ollama 服务"""
    print("正在启动 Ollama 服务...")
    try:
        # 创建包含正确环境变量的启动信息
        startupinfo = subprocess.STARTUPINFO()
        startupinfo.dwFlags |= subprocess.STARTF_USESHOWWINDOW
        
        env = os.environ.copy()
        env["OLLAMA_MODELS"] = OLLAMA_MODELS_PATH
        
        subprocess.Popen(
            [OLLAMA_EXE, "serve"],
            creationflags=subprocess.CREATE_NEW_PROCESS_GROUP,
            env=env,
            startupinfo=startupinfo
        )
        import time
        time.sleep(3)  # 等待服务启动
        print("Ollama 服务已启动")
        return True
    except Exception as e:
        print(f"启动 Ollama 服务失败：{e}")
        return False


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
    if any(kw in user_lower for kw in ['历史记录', '聊天记录', '之前的对话', '之前问过', 'history', '记录']):
        # 尝试提取关键词
        keyword = None
        if '关于' in user_input:
            kw_match = re.search(r'关于 (.+?)(?:的|$)', user_input)
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
                
                # 将工具结果添加到用户输入中
                enhanced_prompt = f"""用户问题：{user_input}

--- 工具查询结果 ---
{tool_result}
--- 结束 ---

请根据上面的工具查询结果，用自然语言回答用户的问题。如果工具返回了数据，就基于数据回答；如果没有数据，就如实告知用户。"""
                
                print(f"{MODEL_NAME}: ", end="", flush=True)
                result = subprocess.run(
                    [OLLAMA_EXE, "run", MODEL_NAME, enhanced_prompt],
                    env=env,
                    capture_output=True,
                    timeout=300,
                )
                
                if result.returncode == 0:
                    output = result.stdout.decode('utf-8')
                    print(output)
                    history.add_conversation(user_input, output.strip())
                else:
                    error_msg = result.stderr.decode('utf-8', errors='ignore')
                    print(f"错误：{error_msg}")
            else:
                # 不需要调用工具，直接对话
                print(f"{MODEL_NAME}: ", end="", flush=True)
                result = subprocess.run(
                    [OLLAMA_EXE, "run", MODEL_NAME, user_input],
                    env=env,
                    capture_output=True,
                    timeout=300,
                )
                
                if result.returncode == 0:
                    output = result.stdout.decode('utf-8')
                    print(output)
                    history.add_conversation(user_input, output.strip())
                else:
                    error_msg = result.stderr.decode('utf-8', errors='ignore')
                    print(f"错误：{error_msg}")
        
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
    """单次提示运行"""
    print(f"\n🤖 向 {MODEL_NAME} 提问：{prompt}\n")
    print("=" * 50)
    
    # 开始会话
    history.start_session()
    
    try:
        # 不使用 text=True，而是手动解码为 UTF-8
        result = subprocess.run(
            [OLLAMA_EXE, "run", MODEL_NAME, prompt],
            env=env,
            capture_output=True,
            timeout=300,
        )
        
        if result.returncode == 0:
            # 使用 UTF-8 解码输出
            output = result.stdout.decode('utf-8')
            print(output)
            
            # 保存对话
            history.add_conversation(prompt, output.strip())
            history.save_session()
        else:
            error_msg = result.stderr.decode('utf-8', errors='ignore')
            print(f"错误：{error_msg}")
            
    except subprocess.TimeoutExpired:
        print("请求超时，请尝试更短的问题或增加超时时间")
    except Exception as e:
        print(f"运行错误：{e}")


def main():
    """主函数"""
    print("╔════════════════════════════════════════╗")
    print("║       Agent 启动程序（带历史记录）     ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 初始化历史记录管理器
    history = ConversationHistory()
    
    # 设置环境变量（必须在启动服务前设置）
    env = setup_environment()
    os.environ["OLLAMA_MODELS"] = OLLAMA_MODELS_PATH
    
    # 检查服务状态
    if not check_ollama_running(env):
        if not start_ollama_service():
            print("无法启动 Ollama 服务，程序退出")
            sys.exit(1)
    
    # 检查模型是否存在
    try:
        result = subprocess.run(
            [OLLAMA_EXE, "list"],
            env=env,
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if MODEL_NAME not in result.stdout:
            print(f"错误：未找到模型 '{MODEL_NAME}'")
            print("请先运行：ollama create agent -f E:\\ollama_models\\Modelfile")
            sys.exit(1)
    except Exception as e:
        print(f"检查模型失败：{e}")
        sys.exit(1)
    
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
