import socket
import json
import os
import requests
import time
import re
import uuid
import subprocess
from datetime import datetime, timedelta

# 基础配置
config = {
    "base_url": "http://10.101.2.194:6060",  # 登录页面基础URL
    "check_url": "http://10.101.2.239:8081/user/check-only",  # 预验证接口
    "login_url": "http://10.101.2.194:6060/quickauth.do",  # 实际登录接口
    "test_url": "https://www.baidu.com",
    "check_interval": 60,
    "timeout": 5
}

# 从配置文件加载账号信息
def load_account_config():
    config_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "config.json")
    try:
        with open(config_file, 'r', encoding='utf-8') as f:
            account_config = json.load(f)
            # 将账号信息合并到全局config中
            config.update(account_config)
            print(f"成功从配置文件加载账号信息: {config_file}")
            return True
    except Exception as e:
        print(f"加载配置文件失败: {str(e)}")
        print("请确保config.json文件存在并且格式正确")
        return False

# 初始化加载配置
load_account_config()

# 需要动态获取的参数（示例值，实际运行时需要更新）
dynamic_params = {
    # "wlanuserip": "10.104.104.247",  # 需要动态获取本机IP
    # "mac": "30:63:09:b4:cc:bf",  # 需要获取本机MAC地址
    # "vlan": "19961077",  # 从网络响应中解析
    # "portalpageid": "41",  # 从登录页面HTML中获取
    "vlan":None,
    "portalpageid":None,
    "wlanuserip":None,
    "hostname":None,
    "mac":None,
    "uuid": str(uuid.uuid4()),  # 每次生成新的UUID
    "timestamp": int(datetime.now().timestamp() * 1000)  # 当前时间戳
}

def parse_login_page():
    """从登录页面HTML提取动态参数（改进版）"""
    try:
        # 先主动获取本地IP和MAC地址
        local_ip = get_local_ip()
        mac = get_mac_address()
        dynamic_params["wlanuserip"] = local_ip
        dynamic_params["mac"] = mac
        
        print(f"已获取本地IP: {local_ip}, MAC: {mac}")

        # 更新时间戳和UUID
        dynamic_params["timestamp"] = int(datetime.now().timestamp() * 1000)
        dynamic_params["uuid"] = str(uuid.uuid4())

        # 尝试从页面获取其他参数
        try:
            response = requests.get(config["base_url"], timeout=5)
            html = response.text

            # 使用更通用的正则表达式
            def extract_param(pattern, html):
                match = re.search(pattern, html)
                return match.group(1) if match else None

            # 尝试从页面提取参数
            vlan = extract_param(r'vlan=([^&"\']+)', html)
            portalpageid = extract_param(r'portalpageid=([^&"\']+)', html)
            hostname = extract_param(r'hostname=([^&"\']+)', html)
            
            # 如果能从页面获取，就更新；否则使用备用值
            if vlan:
                dynamic_params["vlan"] = vlan
            elif not dynamic_params.get("vlan"):
                # 使用HAR文件中看到的值作为备用
                dynamic_params["vlan"] = "19961077"
                print("使用备用VLAN值")
                
            if portalpageid:
                dynamic_params["portalpageid"] = portalpageid
            elif not dynamic_params.get("portalpageid"):
                # 使用HAR文件中看到的值作为备用
                dynamic_params["portalpageid"] = "41"
                print("使用备用portalpageid值")
                
            if hostname:
                dynamic_params["hostname"] = hostname
            else:
                # 获取计算机名称
                try:
                    import platform
                    hostname = platform.node()
                    dynamic_params["hostname"] = hostname
                    print(f"使用系统主机名: {hostname}")
                except:
                    dynamic_params["hostname"] = "DESKTOP-IPMD9L3"  # 使用HAR中的值作为备用

            print("参数提取/更新成功:", dynamic_params)
            return True
        except Exception as page_e:
            print(f"从页面提取参数失败，使用本地参数: {str(page_e)}")
            # 如果从页面提取失败，确保有基本参数
            if not dynamic_params.get("vlan"):
                dynamic_params["vlan"] = "19961077"
            if not dynamic_params.get("portalpageid"):
                dynamic_params["portalpageid"] = "41"
            if not dynamic_params.get("hostname"):
                dynamic_params["hostname"] = "DESKTOP-IPMD9L3"
            return True
    except Exception as e:
        print("解析登录页面失败:", str(e))
        # 保留本地参数，不清空
        return False


def get_mac_address():
    """获取本机MAC地址（Windows）"""
    result = subprocess.check_output("getmac", shell=True).decode('gbk')
    return re.search(r"([0-9A-F]{2}-){5}[0-9A-F]{2}", result).group().replace("-", ":")

def get_local_ip():
    """获取本机IP地址"""
    s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        s.connect(("8.8.8.8", 80))
        return s.getsockname()[0]
    finally:
        s.close()

def is_connected():
    """检测网络连接"""
    start_time = time.time()  # 记录请求开始时间
    try:
        response = requests.get(config["test_url"], timeout=config["timeout"])
        elapsed = time.time() - start_time  # 计算实际耗时
        return (response.status_code == 200, elapsed)
    except requests.exceptions.Timeout:
        return (False, config["timeout"])  # 超时时返回预设超时值
    except:
        elapsed = time.time() - start_time  # 其他异常也计算实际耗时
        return (False, elapsed)
    # try:
    #     return requests.get(config["test_url"], timeout=config["timeout"]).status_code == 200
    # except:
    #     return False


def pre_check():
    """预验证账号密码"""
    # 1. 先更新动态参数
    parse_login_page()
    
    # 2. 从HAR文件中发现的新的认证接口
    auth_url = "http://10.101.2.205:8081/aaa-auth/api/v1/auth"
    
    payload = {
        "username": config["username"],
        "password": config["password"],
        "operatorSuffix": f"@{config['operator']}"
    }

    headers = {
        "Referer": config["base_url"] + "/",
        "Origin": config["base_url"],
        "Content-Type": "application/json"
    }

    # 尝试多种验证方式
    # 方式1: 新接口
    try:
        print("尝试预验证方式1 (新接口)...")
        response = requests.post(
            auth_url,
            json=payload,  # 使用json而不是data，确保正确的Content-Type
            headers=headers,
            timeout=config["timeout"]
        )
        print(f"预验证响应状态码: {response.status_code}")
        print(f"预验证响应内容: {response.text}")
        
        # 检查是否成功，不同接口可能返回格式不同
        try:
            result = response.json()
            if result.get("code") == "0" or result.get("success") or result.get("code") == 1:
                return True
        except ValueError:
            # 非JSON响应
            if "success" in response.text.lower() or "ok" in response.text.lower():
                return True
    except Exception as e:
        print("预验证方式1失败:", str(e))
    
    # 方式2: 原接口
    try:
        print("尝试预验证方式2 (原接口)...")
        response = requests.post(
            config["check_url"],
            json=payload,  # 使用json而不是data
            headers=headers,
            timeout=config["timeout"]
        )
        print(f"原接口预验证响应状态码: {response.status_code}")
        print(f"原接口预验证响应内容: {response.text}")
        
        try:
            result = response.json()
            if result.get("code") == "0" or result.get("success") or result.get("code") == 1:
                return True
        except ValueError:
            # 非JSON响应
            if "success" in response.text.lower() or "ok" in response.text.lower():
                return True
    except Exception as e:
        print("预验证方式2失败:", str(e))
    
    # 方式3: 直接返回True，跳过预验证（作为备用方案）
    print("所有预验证方式都失败，尝试跳过预验证直接登录...")
    return True  # 允许直接进入登录流程


def real_login():
    """执行实际登录"""
    # 再次确认动态参数已更新
    parse_login_page()
    
    # 构造GET请求参数
    params = {
        "userid": f"{config['username']}@{config['operator']}",
        "passwd": config["password"],
        "wlanuserip": dynamic_params.get("wlanuserip", get_local_ip()),
        "wlanacname": "HSD-BRAS-1",  # 固定值
        "wlanacIp": "10.101.2.37",  # 从HAR文件中提取
        "ssid": "",
        "vlan": dynamic_params.get("vlan", "19961077"),
        "mac": dynamic_params.get("mac", get_mac_address()).replace(":", "%3A"),  # URL编码冒号
        "version": "0",
        "portalpageid": dynamic_params.get("portalpageid", "41"),
        "timestamp": dynamic_params.get("timestamp", int(datetime.now().timestamp() * 1000)),
        "uuid": dynamic_params.get("uuid", str(uuid.uuid4())),
        "portaltype": "0",
        "hostname": dynamic_params.get("hostname", "DESKTOP-IPMD9L3"),
        "bindCtrlId": ""
    }

    # 动态构造Referer头
    referer = f"{config['base_url']}/portal.do?wlanuserip={params['wlanuserip']}&wlanacname={params['wlanacname']}"
    headers = {
        "Referer": referer,
        "X-Requested-With": "XMLHttpRequest",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/143.0.0.0 Safari/537.36 Edg/143.0.0.0"
    }

    print(f"准备登录，参数: {params}")
    print(f"请求头: {headers}")
    
    try:
        response = requests.get(
            config["login_url"],
            params=params,
            headers=headers,
            timeout=config["timeout"]
        )
        print(f"登录响应状态码: {response.status_code}")
        print(f"登录响应内容: {response.text}")
        
        # 检查不同可能的成功响应格式
        try:
            result = response.json()
            if result.get("code") == "0" or result.get("success") or result.get("result") == "success":
                return True
        except ValueError:
            # 非JSON响应，检查是否包含成功信息
            if "success" in response.text.lower() or "成功" in response.text or "已在线" in response.text:
                return True
                
        return False
    except Exception as e:
        print("登录请求失败:", str(e))
        return False


def main_flow():
    """完整登录流程"""
    print("开始执行登录流程...")
    
    # 确保先获取动态参数
    parse_login_page()
    
    # 优化：直接尝试登录，跳过预验证流程
    print("优化：直接尝试登录，跳过预验证流程...")
    if real_login():
        print("登录成功！")
        return True
    
    # 如果直接登录失败，再尝试包含预验证的传统方式
    print("直接登录失败，尝试传统登录流程...")
    parse_login_page()  # 再次更新参数
    
    # 步骤1：预验证
    if not pre_check():
        print(datetime.now().strftime("%H:%M:%S"),"预验证失败，请先检查是否连接到校园网，再检查账号密码")
        return False

    # 步骤2：实际登录
    if real_login():
        print("登录成功！")
        return True
    else:
        print(datetime.now().strftime("%H:%M:%S"),"最终登录失败")
        return False


# 守护进程主循环
if __name__ == "__main__":
    # 确保配置加载成功
    if not load_account_config():
        print("无法继续，缺少必要的账号配置信息")
        exit(1)
    
    # 使用时间戳记录网络正常开始时间
    network_ok_start_time = None
    
    while True:
        status, response_time = is_connected()
        if not status :
            print(datetime.now().strftime("%H:%M:%S"),"检测到网络断开，尝试登录...")
            main_flow()
            network_ok_start_time = None  # 重置网络正常计时
        else:
            # 首次检测到网络正常
            if network_ok_start_time is None:
                network_ok_start_time = datetime.now()
                print(f"{datetime.now().strftime('%H:%M:%S')} 网络已连接，响应时间：{response_time:.2f}秒")
            else:
                # 计算网络持续正常时间
                network_ok_duration = datetime.now() - network_ok_start_time
                minutes = network_ok_duration.total_seconds() / 60
                print(f"{datetime.now().strftime('%H:%M:%S')} 网络正常，响应时间：{response_time:.2f}秒,持续正常：{minutes:.1f}分钟")
                
        time.sleep(config["check_interval"])
