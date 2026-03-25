#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
历史对话记录管理模块
用于保存和加载与 Ollama Agent 的对话历史
"""

import os
from datetime import datetime
from typing import List, Tuple, Optional


class ConversationHistory:
    """对话历史管理类"""
    
    def __init__(self, file_path: str = None):
        if file_path is None:
            self.file_path = r"C:\Users\sanjin\Desktop\agent\history.txt"
        else:
            self.file_path = file_path
        self.session_start_time: Optional[datetime] = None
        self.conversations: List[Tuple[str, str]] = []  # [(询问，回答), ...]
        self._ensure_directory()
    
    def _ensure_directory(self):
        """确保目录存在"""
        dir_path = os.path.dirname(self.file_path)
        if dir_path and not os.path.exists(dir_path):
            os.makedirs(dir_path, exist_ok=True)
    
    def start_session(self):
        """开始新会话"""
        self.session_start_time = datetime.now()
        self.conversations = []
        print(f"\n📝 新会话开始于 {self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')}")
    
    def add_conversation(self, user_input: str, assistant_response: str):
        """添加一条对话记录
        
        Args:
            user_input: 用户输入
            assistant_response: AI 回复
        """
        self.conversations.append((user_input, assistant_response))
    
    def save_session(self):
        """保存当前会话到文件"""
        if not self.session_start_time or len(self.conversations) == 0:
            return
        
        try:
            # 格式化时间
            time_str = self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')
            
            # 构建对话内容
            conv_parts = []
            for i, (question, answer) in enumerate(self.conversations, 1):
                conv_parts.append(f"第{i}次询问:{question}")
                conv_parts.append(f"第{i}次回答:{answer}")
            
            # 合并所有对话
            conversations_text = "。".join(conv_parts)
            
            # 完整格式：时间:[第一次询问：第一次回答。第二次询问：第二次回答...]
            record = f"{time_str}:[{conversations_text}]\n"
            
            # 追加到文件
            with open(self.file_path, 'a', encoding='utf-8') as f:
                f.write(record)
            
            print(f"\n💾 已保存 {len(self.conversations)} 条对话记录")
            
        except Exception as e:
            print(f"❌ 保存历史记录失败：{e}")
    
    def get_session_summary(self) -> str:
        """获取当前会话摘要"""
        if not self.session_start_time:
            return "未开始会话"
        
        time_str = self.session_start_time.strftime('%Y-%m-%d %H:%M:%S')
        return f"会话开始于 {time_str}, 共 {len(self.conversations)} 轮对话"
    
    def clear(self):
        """清空当前会话"""
        self.session_start_time = None
        self.conversations = []


def query_history(keyword=None, limit=10):
    """查询历史对话记录（供 tool.py 调用）
    
    Args:
        keyword: 可选的搜索关键词，如果为 None 则返回最近的记录
        limit: 返回的记录数量，默认 10 条
        
    Returns:
        历史记录字典
    """
    history_file = r"C:\Users\sanjin\Desktop\agent\history.txt"
    
    if not os.path.exists(history_file):
        return {'error': '暂无历史记录文件'}
    
    results = []
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            content = f.read()
            
            # 使用正则表达式匹配完整的会话记录
            # 格式：时间:[第 n 次询问:...。第 n 次回答:...]
            import re
            # 使用 DOTALL 模式让 . 匹配包括换行符在内的所有字符
            pattern = r'(\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}):\[(.+?)\]'
            matches = re.findall(pattern, content, re.DOTALL)
            
            for timestamp, session_content in matches:
                # 找到所有"第 n 次 xxx:"的位置 - 不使用正则表达式，直接用字符串查找
                positions = []
                idx = 0
                while idx < len(session_content):
                    # 查找下一个"第"
                    next_di = session_content.find('第', idx)
                    if next_di == -1:
                        break
                    
                    # 检查后面是否跟着数字和"次"
                    rest = session_content[next_di:]
                    if len(rest) >= 3 and rest[1].isdigit() and rest[2] == '次':
                        # 提取数字
                        num_str = ''
                        i = 1
                        while i < len(rest) and rest[i].isdigit():
                            num_str += rest[i]
                            i += 1
                        
                        # 现在 i 指向'次'后面的字符，检查是否是'询问:'或'回答:'
                        if rest.startswith('次询问:', i):
                            positions.append((next_di, num_str, '询问'))
                        elif rest.startswith('次回答:', i):
                            positions.append((next_di, num_str, '回答'))
                    
                    idx = next_di + 1
                
                # 提取每个标记后的内容
                conversations = {}
                for i in range(len(positions)):
                    start_pos, num_str, qatype = positions[i]
                    num = int(num_str)
                    
                    # 确定内容的结束位置（下一个标记的开始或字符串末尾）
                    if i + 1 < len(positions):
                        end_pos = positions[i + 1][0]
                    else:
                        end_pos = len(session_content)
                    
                    # 提取内容（跳过标记本身）
                    content_start = start_pos + len(f'第{num_str}次{qatype}:')
                    content = session_content[content_start:end_pos].strip()
                    
                    # 保存到对话记录
                    if num not in conversations:
                        conversations[num] = {}
                    
                    if qatype == '询问':
                        conversations[num]['question'] = content
                    elif qatype == '回答':
                        conversations[num]['answer'] = content
                
                # 如果有对话内容
                if conversations:
                    # 如果有关键词，进行过滤
                    if keyword:
                        matched = False
                        for qa in conversations.values():
                            if (keyword in qa.get('question', '') or 
                                keyword in qa.get('answer', '')):
                                matched = True
                                break
                        if not matched:
                            continue
                    
                    # 添加记录
                    record = {
                        'timestamp': timestamp,
                        'conversations': conversations,
                        'total_pairs': len(conversations)
                    }
                    results.append(record)
        
        # 按时间倒序排序（最新的在前）
        results.sort(key=lambda x: x['timestamp'], reverse=True)
        
        # 限制返回数量
        if limit > 0:
            results = results[:limit]
        
        return {
            'success': True,
            'count': len(results),
            'records': results
        }
        
    except Exception as e:
        return {'error': f'查询历史记录失败：{str(e)}'}


def get_history_stats():
    """获取历史记录统计信息
    
    Returns:
        统计信息字典
    """
    history_file = r"C:\Users\sanjin\Desktop\agent\history.txt"
    
    if not os.path.exists(history_file):
        return {'error': '暂无历史记录文件'}
    
    total_sessions = 0
    total_conversations = 0
    earliest_time = None
    latest_time = None
    
    try:
        with open(history_file, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if not line or '[' not in line:
                    continue
                
                total_sessions += 1
                
                # 提取时间戳
                timestamp_end = line.find(':[')
                if timestamp_end != -1:
                    timestamp = line[:timestamp_end]
                    if earliest_time is None:
                        earliest_time = timestamp
                    latest_time = timestamp
                
                # 统计对话对数
                content = line[timestamp_end+2:-1] if timestamp_end != -1 else ''
                questions = content.count('次询问:')
                answers = content.count('次回答:')
                total_conversations += min(questions, answers)
        
        return {
            'success': True,
            'total_sessions': total_sessions,
            'total_conversations': total_conversations,
            'earliest_session': earliest_time,
            'latest_session': latest_time
        }
        
    except Exception as e:
        return {'error': f'获取统计信息失败：{str(e)}'}


# 示例用法
if __name__ == "__main__":
    print("╔════════════════════════════════════════╗")
    print("║   历史对话记录管理工具                 ║")
    print("╚════════════════════════════════════════╝\n")
    
    # 测试会话保存
    history = ConversationHistory()
    history.start_session()
    
    print("\n测试添加对话记录...")
    history.add_conversation("你好，请问今天天气如何？", "今天天气晴朗，温度适宜...")
    history.add_conversation("谢谢！", "不客气，有其他问题吗？")
    history.add_conversation("再见", "再见，祝你有美好的一天！")
    
    print(f"\n会话摘要：{history.get_session_summary()}")
    
    # 保存会话
    print("\n保存会话...")
    history.save_session()
    
    print(f"\n✅ 测试完成！记录已保存到：{history.file_path}")
