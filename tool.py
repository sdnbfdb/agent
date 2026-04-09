import requests
import time
import os
from datetime import datetime

# ============================================================================
# Agent 工具定义
# 这些函数可以被 Ollama Agent 调用
# ============================================================================

def get_current_location(default_city: str = None):
    """获取当前位置信息（使用多个备用 API）
    
    Agent 工具描述：获取用户当前的地理位置信息，包括 IP、城市、经纬度等
    返回格式：{'ip': str, 'city': str, 'region': str, 'country': str, 'latitude': float, 'longitude': float, 'loc': str}
    
    Args:
        default_city (str, optional): 默认城市名称，如果提供则直接返回该城市信息
    
    Returns:
        位置信息字典
    """
    # 如果提供了默认城市，直接返回
    if default_city:
        return {
            'ip': 'N/A',
            'city': default_city,
            'region': default_city,
            'country': 'CN',
            'latitude': 36.1984,
            'longitude': 113.1053,
            'loc': f'36.1984,113.1053'
        }
    
    # API 列表，按优先级排序
    apis = [
        'https://ipapi.co/json',
        'https://ip-api.com/json/',
        'https://ipinfo.io/json'
    ]
    
    for api_url in apis:
        try:
            response = requests.get(api_url, timeout=10)
            response.raise_for_status()
            data = response.json()
            
            # 检查是否有限流错误
            if 'error' in data and isinstance(data, dict):
                print(f"API {api_url} 返回错误：{data.get('error')}")
                continue
            
            # 根据不同 API 的响应格式解析数据
            if 'ipapi.co' in api_url:
                latitude, longitude = data['latitude'], data['longitude']
                location_info = {
                    'ip': data.get('ip'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country_name'),
                    'latitude': latitude,
                    'longitude': longitude,
                    'loc': f"{latitude},{longitude}"
                }
            elif 'ip-api.com' in api_url:
                latitude, longitude = data['lat'], data['lon']
                location_info = {
                    'ip': data.get('query'),
                    'city': data.get('city'),
                    'region': data.get('regionName'),
                    'country': data.get('country'),
                    'latitude': latitude,
                    'longitude': longitude,
                    'loc': f"{latitude},{longitude}"
                }
            else:  # ipinfo.io
                loc = data.get('loc', '0,0').split(',')
                latitude, longitude = float(loc[0]), float(loc[1])
                location_info = {
                    'ip': data.get('ip'),
                    'city': data.get('city'),
                    'region': data.get('region'),
                    'country': data.get('country'),
                    'latitude': latitude,
                    'longitude': longitude,
                    'loc': f"{latitude},{longitude}"
                }
            
            return location_info
            
        except Exception as e:
            print(f"API {api_url} 失败：{str(e)}")
            time.sleep(1)  # 等待 1 秒后尝试下一个 API
            continue
    
    return {'error': '所有位置查询 API 都不可用'}


def get_weather_by_location(location=None):
    """根据位置查询天气
    
    Agent 工具描述：查询指定地点或当前位置的天气情况
    参数:
        location (str, optional): 城市名称，如"北京"、"Shanghai"。如果不提供则使用当前位置
    返回格式：{'location': str, 'temperature': float, 'wind_speed': float, 'wind_direction': int, 'weather_code': int, 'description': str, 'time': str}
    
    Args:
        location: 位置信息，可以是城市名或经纬度
        
    Returns:
        天气信息字典
    """
    try:
        # 如果没有提供位置，先获取当前位置
        if not location:
            location_info = get_current_location()
            if 'error' in location_info:
                return location_info
            location = location_info.get('city')
        
        # 使用 Open-Meteo API 查询天气（免费，无需 API key）
        # 首先通过地理编码获取经纬度
        geocode_url = 'https://geocoding-api.open-meteo.com/v1/search'
        geocode_params = {
            'name': location,
            'count': 1,
            'language': 'zh',
            'format': 'json'
        }
        
        geocode_response = requests.get(geocode_url, params=geocode_params)
        geocode_response.raise_for_status()
        geocode_data = geocode_response.json()
        
        if not geocode_data.get('results'):
            return {'error': f'找不到地点：{location}'}
        
        lat = geocode_data['results'][0]['latitude']
        lon = geocode_data['results'][0]['longitude']
        name = geocode_data['results'][0]['name']
        
        # 查询当前天气
        weather_url = 'https://api.open-meteo.com/v1/forecast'
        weather_params = {
            'latitude': lat,
            'longitude': lon,
            'current_weather': True,
            'temperature_unit': 'celsius'
        }
        
        weather_response = requests.get(weather_url, params=weather_params)
        weather_response.raise_for_status()
        weather_data = weather_response.json()
        
        current = weather_data.get('current_weather', {})
        
        weather_info = {
            'location': name,
            'temperature': current.get('temperature'),
            'wind_speed': current.get('windspeed'),
            'wind_direction': current.get('winddirection'),
            'weather_code': current.get('weathercode'),
            'time': current.get('time')
        }
        
        # 天气代码说明
        weather_codes = {
            0: '晴朗',
            1: '主要晴朗',
            2: '部分多云',
            3: '阴天',
            45: '雾',
            48: '雾凇',
            51: '毛毛雨',
            53: '中雨',
            55: '大雨',
            61: '小雨',
            63: '中雨',
            65: '大雨',
            71: '小雪',
            73: '中雪',
            75: '大雪',
            95: '雷雨'
        }
        
        weather_info['description'] = weather_codes.get(weather_info['weather_code'], '未知')
        
        return weather_info
        
    except Exception as e:
        return {'error': str(e)}


def query_history(keyword=None, limit=10):
    """查询历史对话记录
    
    Agent 工具描述：搜索和查看用户与 AI 的历史对话记录
    参数:
        keyword (str, optional): 搜索关键词，会同时匹配问题和答案
        limit (int, optional): 返回的记录数量，默认 10 条
    返回格式：{'success': bool, 'count': int, 'records': [{'timestamp': str, 'conversations': {id: {'question': str, 'answer': str}}, 'total_pairs': int}]}
    
    Args:
        keyword: 可选的搜索关键词，如果为 None 则返回最近的记录
        limit: 返回的记录数量，默认 10 条
        
    Returns:
        历史记录列表，每条记录包含时间、询问和回答
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
                # 使用字符串查找方法来提取问答（不使用正则表达式）
                conversations = {}
                
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
    
    Agent 工具描述：获取用户历史对话的统计信息，总会话数、总对话数等
    返回格式：{'success': bool, 'total_sessions': int, 'total_conversations': int, 'earliest_session': str, 'latest_session': str}
    
    Returns:
        统计信息字典，包含总会话数、总对话对数等
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


# ============================================================================
# 示例用法
# ============================================================================
if __name__ == "__main__":
    print("=" * 50)
    print("获取当前位置:")
    print("=" * 50)
    location = get_current_location()
    if 'error' not in location:
        print(f"IP: {location['ip']}")
        print(f"位置：{location['city']}, {location['region']}, {location['country']}")
        print(f"经纬度：{location['latitude']}, {location['longitude']}")
    else:
        print(f"错误：{location['error']}")
    
    print("\n" + "=" * 50)
    print("查询当前位置天气:")
    print("=" * 50)
    weather = get_weather_by_location()
    if 'error' not in weather:
        print(f"地点：{weather['location']}")
        print(f"温度：{weather['temperature']}°C")
        print(f"天气：{weather['description']}")
        print(f"风速：{weather['wind_speed']} km/h")
        print(f"时间：{weather['time']}")
    else:
        print(f"错误：{weather['error']}")
    
    print("\n" + "=" * 50)
    print("查询历史记录:")
    print("=" * 50)
    history = query_history(limit=3)
    if 'success' in history and history['success']:
        print(f"找到 {history['count']} 条历史记录\n")
        for i, record in enumerate(history['records'], 1):
            print(f"--- 记录 {i} ---")
            print(f"时间：{record['timestamp']}")
            print(f"对话对数：{record['total_pairs']}")
            for qa_num, qa in list(record['conversations'].items())[:2]:  # 只显示前 2 组问答
                print(f"  问：{qa.get('question', '')}")
                print(f"  答：{qa.get('answer', '')}")
            if record['total_pairs'] > 2:
                print(f"  ... 还有 {record['total_pairs'] - 2} 组对话")
            print()
    else:
        print(f"错误：{history.get('error', '未知错误')}")
    
    print("\n" + "=" * 50)
    print("历史记录统计:")
    print("=" * 50)
    stats = get_history_stats()
    if 'success' in stats and stats['success']:
        print(f"总会话数：{stats['total_sessions']}")
        print(f"总对话对数：{stats['total_conversations']}")
        print(f"最早会话：{stats['earliest_session']}")
        print(f"最新会话：{stats['latest_session']}")
    else:
        print(f"错误：{stats.get('error', '未知错误')}")
