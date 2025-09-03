# -*- coding: utf-8 -*-
import requests
import json
import time
import sct_server_send

# 此处填入小鲸卡卡号
card_number = 9014

def get_card_info():
    output_lines = []  # 存储所有输出行的列表
    
    def add_output(text, level=0):
        """添加输出文本到列表"""
        if level > 0:
            indent = "  " * (level - 1) + "- "
            formatted_text = f"{indent}{text}"
        else:
            formatted_text = text
        output_lines.append(formatted_text)
        print(text)  # 同时打印到控制台
    
    # 第一次尝试直接获取信息
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36',
        'Accept': 'application/json, text/plain, */*',
        'Accept-Language': 'zh-CN,zh;q=0.9,en;q=0.8',
        'Origin': 'https://xjxj.iot889.cn',
        'Referer': 'https://xjxj.iot889.cn/',
        'X-Requested-With': 'XMLHttpRequest'
    }
    
    try:
        # 第一次尝试直接获取信息
        add_output("## 第一次尝试直接获取卡片信息", 0)
        first_response = requests.get(
            'https://xjxj.iot889.cn/app/client/card/get', 
            headers=headers
        )
        
        # 如果返回400状态码，从响应头获取Set-Cookie
        if first_response.status_code == 400 and 'Set-Cookie' in first_response.headers:
            add_output("收到400状态码，从响应头获取Cookie", 1)
            
            # 解析Set-Cookie头
            set_cookie = first_response.headers['Set-Cookie']
            add_output(f"获取到Set-Cookie: `{set_cookie}`", 2)
            
            # 提取APPLICATION_SESSION_NAME值
            if 'APPLICATION_SESSION_NAME=' in set_cookie:
                cookie_start = set_cookie.find('APPLICATION_SESSION_NAME=') + len('APPLICATION_SESSION_NAME=')
                cookie_end = set_cookie.find(';', cookie_start)
                if cookie_end == -1:
                    cookie_end = len(set_cookie)
                session_cookie = set_cookie[cookie_start:cookie_end]
                
                cookies = {
                    'APPLICATION_SESSION_NAME': session_cookie
                }
                
                add_output(f"提取到APPLICATION_SESSION_NAME: `{session_cookie}`", 2)
                
                # 使用获取的Cookie进行登录
                add_output(f"使用卡号 `{card_number}` 登录中", 1)
                login_data = {'card': card_number}
                login_response = requests.post(
                    'https://xjxj.iot889.cn/app/card/login', 
                    data=login_data, 
                    headers=headers,
                    cookies=cookies
                )
                
                # 检查登录是否成功
                if login_response.status_code != 200:
                    add_output(f"登录请求失败，状态码: `{login_response.status_code}`", 2)
                    return None, "\n".join(output_lines)
                    
                login_result = login_response.json()
                if login_result.get('code') != 0:
                    add_output(f"登录失败: {login_result.get('msg', '未知错误')}", 2)
                    return None, "\n".join(output_lines)
                    
                add_output("✅ 登录成功", 2)
                
                # 使用相同的Cookie获取卡片信息
                add_output("使用登录后的Cookie获取卡片信息", 1)
                info_response = requests.get(
                    'https://xjxj.iot889.cn/app/client/card/get', 
                    headers=headers,
                    cookies=cookies
                )
                
                if info_response.status_code != 200:
                    add_output(f"获取信息请求失败，状态码: `{info_response.status_code}`", 2)
                    return None, "\n".join(output_lines)
                    
                card_info = info_response.json()
                if card_info.get('code') != 0:
                    add_output(f"获取信息失败: {card_info.get('msg', '未知错误')}", 2)
                    return None, "\n".join(output_lines)
                    
                add_output("✅ 成功获取卡片信息", 2)
                return card_info, "\n".join(output_lines)
            else:
                add_output("❌ Set-Cookie中未找到APPLICATION_SESSION_NAME", 2)
                return None, "\n".join(output_lines)
        else:
            # 如果第一次请求就成功了（不太可能，但处理一下）
            add_output(f"第一次请求状态码: `{first_response.status_code}`", 1)
            if first_response.status_code == 200:
                card_info = first_response.json()
                if card_info.get('code') == 0:
                    add_output("✅ 第一次请求直接成功", 2)
                    return card_info, "\n".join(output_lines)
                else:
                    add_output(f"第一次请求返回错误: {card_info.get('msg', '未知错误')}", 2)
                    return None, "\n".join(output_lines)
            else:
                add_output(f"❌ 意外的状态码: `{first_response.status_code}`", 2)
                return None, "\n".join(output_lines)
                
    except requests.exceptions.RequestException as e:
        error_msg = f"❌ 网络请求错误: `{e}`"
        add_output(error_msg, 1)
        return None, "\n".join(output_lines)
    except json.JSONDecodeError as e:
        error_msg = f"❌ JSON解析错误: `{e}`"
        add_output(error_msg, 1)
        return None, "\n".join(output_lines)

def format_card_info(card_info):
    """格式化卡片信息并返回Markdown字符串"""
    if not card_info or 'data' not in card_info:
        return "❌ 无有效卡片信息"
    
    data = card_info['data']
    output_lines = []
    
    output_lines.append("# 📱 物联网卡详细信息")
    output_lines.append("")
    
    # 基本信息表格
    output_lines.append("## 📋 基本信息")
    output_lines.append("")
    output_lines.append("| 项目 | 值 |")
    output_lines.append("|------|-----|")
    output_lines.append(f"| **卡号** | `{data.get('card', 'N/A')}` |")
    output_lines.append(f"| **ICCID** | `{data.get('iccid', 'N/A')}` |")
    output_lines.append(f"| **API卡号** | `{data.get('apiCard', 'N/A')}` |")
    output_lines.append(f"| **实名卡号** | `{data.get('realNameCard', 'N/A')}` |")
    output_lines.append(f"| **用户ID** | `{data.get('userId', 'N/A')}` |")
    output_lines.append(f"| **卡片ID** | `{data.get('id', 'N/A')}` |")
    output_lines.append(f"| **系列ID** | `{data.get('seriesId', 'N/A')}` |")
    output_lines.append("")
    
    # 流量信息表格
    output_lines.append("## 📊 流量使用情况")
    output_lines.append("")
    output_lines.append("| 指标 | 数值 |")
    output_lines.append("|------|------|")
    output_lines.append(f"| **已用流量** | {data.get('used', 0):.2f} MB |")
    output_lines.append(f"| **剩余流量** | {data.get('free', 0):.2f} MB |")
    output_lines.append(f"| **实际上行流量** | {data.get('upstreamFlow', 0):.2f} MB |")
    output_lines.append(f"| **实际使用流量** | {data.get('realUsed', 0):.2f} MB |")
    output_lines.append(f"| **余额** | ¥{data.get('balance', 0):.2f} |")
    output_lines.append("")
    
    # 状态信息
    output_lines.append("## 🔍 状态信息")
    output_lines.append("")
    state = data.get('state', -1)
    state_map = {0: "✅ 正常", 1: "⛔ 停机", 2: "❌ 销户", -1: "❓ 未知"}
    output_lines.append(f"- **卡片状态**: {state_map.get(state, '❓ 未知状态')} (`{state}`)")
    
    online = data.get('online', -1)
    online_map = {0: "🔴 离线", 1: "🟢 在线", -1: "❓ 未知"}
    output_lines.append(f"- **在线状态**: {online_map.get(online, '❓ 未知状态')} (`{online}`)")
    output_lines.append("")
    
    # 时间信息
    output_lines.append("## ⏰ 时间信息")
    output_lines.append("")
    output_lines.append(f"- **创建时间**: `{data.get('createTime', 'N/A')}`")
    output_lines.append(f"- **有效期至**: `{data.get('expirationTime', 'N/A')}`")
    output_lines.append(f"- **首次支付时间**: `{data.get('firstPayTime', 'N/A')}`")
    output_lines.append(f"- **末次支付时间**: `{data.get('lastPayTime', 'N/A')}`")
    output_lines.append(f"- **流量刷新时间**: `{data.get('flowRefreshTime', 'N/A')}`")
    output_lines.append(f"- **状态刷新时间**: `{data.get('stateRefreshTime', 'N/A')}`")
    output_lines.append(f"- **首次登录时间**: `{data.get('firstLoginTime', 'N/A')}`")
    output_lines.append(f"- **末次登录时间**: `{data.get('lastLoginTime', 'N/A')}`")
    output_lines.append("")
    
    # 其他信息
    output_lines.append("## 📈 其他信息")
    output_lines.append("")
    output_lines.append(f"- **支付次数**: {data.get('payNumber', 0)}")
    output_lines.append(f"- **优惠券总额**: ¥{data.get('couponAllAmount', 0):.2f}")
    
    return "\n".join(output_lines)

def main():
    """主函数"""
        
    # 获取卡片信息
    start_time = time.time()
    card_info, process_output = get_card_info()
    end_time = time.time()
    
    # 构建完整的输出字符串
    full_output = "# 🔍 物联网卡查询报告\n\n"
    full_output += f"**查询卡号**: `{card_number}`\n\n"
    full_output += "## 🚀 执行流程\n"
    full_output += process_output + "\n\n"
    
    if card_info:
        # 格式化卡片信息
        card_info_output = format_card_info(card_info)
        full_output += card_info_output + "\n\n"
        
        # 添加统计信息
        full_output += "## 📊 统计信息\n"
        full_output += f"- **请求耗时**: {end_time - start_time:.2f} 秒\n"
        full_output += f"- **查询时间**: {time.strftime('%Y-%m-%d %H:%M:%S')}\n"
        full_output += "- **查询状态**: ✅ 成功\n"
    else:
        full_output += "## ❌ 查询结果\n"
        full_output += "获取卡片信息失败，请检查：\n"
        full_output += "- 卡号是否正确\n"
        full_output += "- 网络连接是否正常\n"
        full_output += "- 卡片是否有效\n\n"
        full_output += f"**查询耗时**: {end_time - start_time:.2f} 秒\n"
    
    # 返回完整的输出字符串
    return full_output

if __name__ == "__main__":
    result = main()
    title = f"{card_number} 信息一览"
    send_result = sct_server_send.sc_send(title, result)
    print(result)
    print(send_result)
