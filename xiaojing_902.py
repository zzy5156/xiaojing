import requests
import json
from datetime import datetime
import sct_server_send

# 此处填入小鲸卡卡号
card_number = 9022

def fetch_and_format_data():
    url = "https://xj.iot998.cn/app/simCard/getCardFlow?card=" + str(card_number)
    
    try:
        # 发送GET请求
        response = requests.get(url)
        response.raise_for_status()  # 如果请求失败，抛出异常
        
        # 解析JSON响应
        data = response.json()
        
        # 判断状态并添加相应表情
        status_emoji = "✅" if data['status'] else "❌"
        msg_emoji = "🎯" if data['code'] == 0 else "⚠️"
        
        # 流量使用情况表情
        flow_ratio = data['data']['consumeFlow'] / data['data']['sumFlow']
        if flow_ratio < 0.2:
            flow_emoji = "💚"  # 使用率低
        elif flow_ratio < 0.7:
            flow_emoji = "💛"  # 使用率中等
        else:
            flow_emoji = "❤️"  # 使用率高
            
        # 剩余流量表情
        surplus_emoji = "👍" if data['data']['surplusFlow'] > 10000 else "👀"
        
        # 结束时间表情
        max_end_time = data['data']['maxEndTime']
        end_date = datetime.strptime(max_end_time, "%Y-%m-%d %H:%M:%S")
        days_remaining = (end_date - datetime.now()).days
        if days_remaining > 180:
            time_emoji = "🕒"
        elif days_remaining > 30:
            time_emoji = "⏰"
        else:
            time_emoji = "🚨"
            
        # 使用Markdown语法格式化数据并添加表情符号
        markdown_output = f"""
# 📱 SIM卡流量使用情况

| 指标 | 值 | 状态 |
|------|-----|------|
| 📶 状态码 | {data['code']} | {msg_emoji} |
| 🚦 请求状态 | {data['status']} | {status_emoji} |
| 💬 消息 | {data['msg']} | {msg_emoji} |
| 📊 总流量(MB) | {data['data']['sumFlow']} | 📦 |
| 🎯 已使用流量(MB) | {data['data']['consumeFlow']} | {flow_emoji} |
| ✅ 剩余流量(MB) | {data['data']['surplusFlow']} | {surplus_emoji} |
| 🔄 是否变更 | {data['data']['isChange']} | {"🔄" if data['data']['isChange'] else "➡️"} |
| ⏰ 最大结束时间 | {data['data']['maxEndTime']} | {time_emoji} |
| 🔔 结束提醒 | {data['data']['endRemind']} | {"🔔" if data['data']['endRemind'] else "🔕"} |

## 📈 流量使用比例

{get_flow_progress_bar(data['data']['consumeFlow'], data['data']['sumFlow'])}

> 📅 数据更新时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
"""
        
        return markdown_output
        
    except requests.exceptions.RequestException as e:
        return f"❌ 请求错误: {e}"
    except json.JSONDecodeError as e:
        return f"❌ JSON解析错误: {e}"
    except Exception as e:
        return f"❌ 未知错误: {e}"

def get_flow_progress_bar(used, total):
    """生成流量使用进度条"""
    ratio = used / total
    filled_length = int(20 * ratio)
    bar = "▇" * filled_length + "─" * (20 - filled_length)
    percentage = ratio * 100
    return f"{used:.2f}MB / {total:.0f}MB  [{bar}] {percentage:.1f}%"

# 执行函数并获取结果
formatted_data = fetch_and_format_data()
title = f"{card_number} 信息一览"
send_result = sct_server_send.sc_send(title, formatted_data)

print(formatted_data)
print(send_result)
