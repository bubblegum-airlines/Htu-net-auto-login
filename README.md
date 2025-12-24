# HTU校园网自动登录脚本使用指南

本文档将详细介绍如何从Python安装开始，配置并运行河南师范大学校园网自动登录脚本。

## 目录
- [1. Python环境安装](#1-python环境安装)
- [2. 下载脚本文件](#2-下载脚本文件)
- [3. 配置账号信息](#3-配置账号信息)
- [4. 安装依赖包](#4-安装依赖包)
- [5. 运行脚本](#5-运行脚本)
- [6. 设置开机自启动](#6-设置开机自启动)
- [7. 日志说明](#7-日志说明)
- [8. 常见问题排查](#8-常见问题排查)

## 1. Python环境安装

### Windows系统

1. **下载Python安装包**
   - 访问 [Python官网](https://www.python.org/downloads/windows/)
   - 推荐下载Python 3.8或更高版本
   - 选择适合你系统的安装包（通常是64位）

2. **安装Python**
   - 运行下载的安装程序
   - **重要：勾选** "Add Python to PATH"
   - 点击 "Install Now" 进行默认安装

3. **验证安装**
   - 按下 `Win + R` 键，输入 `cmd` 打开命令提示符
   - 输入以下命令检查Python版本：
     ```bash
     python --version
     ```
   - 如果显示类似 `Python 3.10.x` 的输出，表示安装成功

### macOS系统

1. **通过Homebrew安装（推荐）**
   - 打开终端
   - 安装Homebrew（如果尚未安装）：
     ```bash
     /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/master/install.sh)"
     ```
   - 安装Python：
     ```bash
     brew install python
     ```

2. **通过官网安装**
   - 访问 [Python官网](https://www.python.org/downloads/mac-osx/)
   - 下载并安装Python安装包

3. **验证安装**
   - 打开终端
   - 输入命令：
     ```bash
     python3 --version
     ```

### Linux系统

大多数Linux发行版已经预装了Python，但可能不是最新版本。

1. **更新包管理器**
   - Ubuntu/Debian：
     ```bash
     sudo apt update
     ```
   - CentOS/RHEL：
     ```bash
     sudo yum update
     ```

2. **安装Python**
   - Ubuntu/Debian：
     ```bash
     sudo apt install python3 python3-pip
     ```
   - CentOS/RHEL：
     ```bash
     sudo yum install python3 python3-pip
     ```

3. **验证安装**
   - 输入命令：
     ```bash
     python3 --version
     pip3 --version
     ```

## 2. 下载脚本文件

1. **创建文件夹**
   - 在任意位置创建一个文件夹，例如 `Htu-auto-login`
   - Windows: 右键桌面 → 新建 → 文件夹 → 命名为 `Htu-auto-login`
   - macOS/Linux: 打开终端，输入 `mkdir ~/Htu-auto-login`

2. **下载必要文件**
   - 将以下文件复制到刚创建的文件夹中：
     - `login - share.pyw`（主脚本文件）
     - `config.json`（配置文件）

## 3. 配置账号信息

1. **编辑配置文件**
   - 使用记事本或任何文本编辑器打开 `config.json` 文件
   - 修改以下信息：
   ```json
   {
       "username": "",  
       "password": "",  
       "operator": ""
   }
   ```

2. **参数说明**
   - `username`: 你的校园网账号（学号）
   - `password`: 你的校园网密码
   - `operator`: 运营商代码
     - `yd`: 移动
     - `lt`: 联通
     - `dx`: 电信

3. **保存文件**
   - 修改完成后，按 `Ctrl + S` 保存文件

## 4. 安装依赖包

脚本需要使用 `requests` 库来发送网络请求。

1. **打开命令行工具**
   - Windows: `Win + R` → 输入 `cmd` → 回车
   - macOS/Linux: 打开终端应用

2. **安装requests库**
   - Windows: 输入以下命令：
     ```bash
     pip install requests
     ```
   - macOS/Linux: 输入以下命令：
     ```bash
     pip3 install requests
     ```

## 5. 运行脚本

### 方法一：直接双击运行

1. **找到脚本文件**
   - 进入 `Htu-auto-login` 文件夹
   - 找到 `login - share.pyw` 文件

2. **双击运行**
   - Windows: 直接双击 `.pyw` 文件即可在后台运行（无命令窗口）
   - macOS/Linux: 右键选择 "打开方式" → 选择Python应用

### 方法二：通过命令行运行

1. **打开命令行工具**

2. **切换到脚本目录**
   ```bash
   cd "e:\Htu-auto-login"  # Windows系统示例
   # 或
   cd "~/Htu-auto-login"  # macOS/Linux系统示例
   ```

3. **运行脚本**
   - Windows:
     ```bash
     python "login - share.pyw"
     # 或
     "login - share.pyw"
     ```
   - macOS/Linux:
     ```bash
     python3 "login - share.pyw"
     ```

## 6. 设置开机自启动

### Windows系统

**使用任务计划程序**
   - 按下win键，搜索任务计划程序，打开任务计划程序
   - 点击左侧的“创建基本任务”
   - 输入任务名称，例如“校园网自动登录”
   - 选择“触发器”，设置为“在登录时”
   - 选择“操作”，设置为“启动程序”
   - 浏览并选择 `python.exe` 文件（通常位于 `C:\PythonXX\python.exe`）
   - 在“添加参数”中输入脚本路径，例如 `e:\Htu-auto-login\login.pyw`
   - 点击“完成”



## 7. 日志说明

脚本运行时会在命令窗口显示以下类型的信息：

- **网络连接状态**：显示当前网络是否正常连接
- **响应时间**：测试网站的响应时间（秒）
- **持续正常时间**：网络连接正常的持续时间（分钟）
- **登录尝试**：当网络断开时，自动尝试登录的信息

## 8. 常见问题排查

### 问题1：脚本无法运行，提示缺少模块

**解决方案**：确保已正确安装所有依赖包
```bash
pip install requests
```

### 问题2：登录失败，提示账号或密码错误

**解决方案**：
- 检查 `config.json` 文件中的账号和密码是否正确
- 确认运营商代码是否选择正确（yd/lt/dx）
- 尝试手动在网页上登录一次，确认账号状态正常

### 问题3：脚本运行但无法检测到网络状态

**解决方案**：
- 确认你当前连接的是校园网WiFi
- 检查校园网登录页面URL是否有变化（如需要，修改脚本中的URL配置）

### 问题4：脚本启动后闪退

**解决方案**：
- 通过命令行方式运行脚本，查看具体错误信息
- 检查Python版本是否兼容（推荐3.6及以上版本）

---

## 注意事项

- 请妥善保管 `config.json` 文件，其中包含你的账号密码信息
- 脚本会定期检查网络状态，默认每60秒检查一次
- 如需修改检查间隔或其他高级配置，请编辑脚本中的 `config` 字典
- 如有任何问题，请联系脚本提供者获取帮助
