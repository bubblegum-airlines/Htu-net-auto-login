import socket

import requests
import time
import re
import uuid
import subprocess
from datetime import datetime

# 配置信息（需要用户修改的部分）
config = {
    "username": "",  # 校园网账号
    "password": "",  # 真实密码（本次请求中的值）
    "operator": "yd",  # 运营商代码：yd/lt/dx
    "base_url": "http://10.101.2.194:6060",  # 登录页面基础URL
    "check_url": "http://10.101.2.239:8081/user/check-only",  # 预验证接口
    "login_url": "http://10.101.2.194:6060/quickauth.do",  # 实际登录接口
    "test_url": "https://www.baidu.com",
    "check_interval": 60,
    "timeout": 5
}

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
    # """从登录页面HTML提取动态参数"""
    # response = requests.get(config["base_url"])
    # html = response.text
    # dynamic_params["vlan"] = re.search(r'vlan=(\d+)', html).group(1)
    # dynamic_params["portalpageid"] = re.search(r'portalpageid=(\d+)', html).group(1)
    # # dynamic_params["wlanuserip"] = re.search(r'wlanuserip=([^&]+)', html).group(1)
    # dynamic_params["hostname"] = re.search(r'hostname=([^&]+)', html).group(1)
    # dynamic_params["wlanuserip"] = get_local_ip()
    """从登录页面HTML提取动态参数（改进版）"""
    try:

        response = requests.get(config["base_url"], timeout=5)
        html = response.text

        # 使用更通用的正则表达式
        def extract_param(pattern, html):
            match = re.search(pattern, html)
            return match.group(1) if match else None

        dynamic_params["vlan"] = extract_param(r'vlan=([^&]+)', html)  # 匹配非&字符
        dynamic_params["portalpageid"] = extract_param(r'portalpageid=([^&]+)', html)
        dynamic_params["wlanuserip"] = extract_param(r'wlanuserip=([^&]+)', html)
        dynamic_params["hostname"] = extract_param(r'hostname=([^&]+)', html)  # 匹配任意字符直到遇到&

        # 验证必要参数是否存在
        required_params = ["vlan", "portalpageid", "wlanuserip"]
        for param in required_params:
            if not dynamic_params.get(param):
                raise ValueError(f"未找到必要参数: {param}")

        print("参数提取成功:", dynamic_params)
    except Exception as e:
        print("解析登录页面失败:", str(e))
        dynamic_params.clear()  # 清空无效参数


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
    try:
        return requests.get(config["test_url"], timeout=config["timeout"]).status_code == 200
    except:
        return False


def pre_check():
    """预验证账号密码"""
    payload = {
        "username": config["username"],
        "password": config["password"],
        "operatorSuffix": f"@{config['operator']}"
    }

    headers = {
        "Referer": config["base_url"] + "/",
        "Origin": config["base_url"]
    }

    try:
        response = requests.post(
            config["check_url"],
            data=payload,
            headers=headers
        )
        return response.json().get("code") == 1
    except Exception as e:
        print("预验证请求失败:", str(e))
        return False


def real_login():
    """执行实际登录"""
    # 构造GET请求参数
    params = {
        "userid": f"{config['username']}@{config['operator']}",
        "passwd": config["password"],
        "wlanuserip": get_local_ip(),
        "wlanacname": "HSD-BRAS-1",  # 固定值（需确认）
        "wlanacIp": "10.101.2.37",  # 从历史请求中提取
        "ssid": "",
        "vlan": dynamic_params["vlan"],
        # "mac": dynamic_params["mac"].replace(":", "%3A"),  # URL编码冒号
        "mac": get_mac_address(),
        "version": "0",
        "portalpageid": dynamic_params["portalpageid"],
        "timestamp": dynamic_params["timestamp"],
        "uuid": dynamic_params["uuid"],
        "portaltype": "0",
        # "hostname": "LAPTOP-EQMUGP5Q",  # 可自定义或留空
        "hostname": dynamic_params["hostname"],
        "bindCtrlId": ""
    }

    headers = {
        "Referer": config["base_url"] + "/portal.do?wlanuserip=...",  # 需动态构造
        "X-Requested-With": "XMLHttpRequest"
    }

    try:
        response = requests.get(
            config["login_url"],
            params=params,
            headers=headers
        )
        return response.json().get("code") == "0"
    except Exception as e:
        print("登录请求失败:", str(e))
        return False


def main_flow():
    """完整登录流程"""
    print("开始执行登录流程...")

    # 步骤1：预验证
    if not pre_check():
        print("预验证失败，请检查账号密码")
        return False

    # 步骤2：实际登录
    if real_login():
        print("登录成功！")
        return True
    else:
        print("最终登录失败")
        return False


# 守护进程主循环
if __name__ == "__main__":
    while True:
        if not is_connected():
            print("检测到网络断开，尝试登录...")
            main_flow()
        else:
            print("网络状态正常")
        time.sleep(config["check_interval"])