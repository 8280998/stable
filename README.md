# stable
stable白名单批量注册程序

## 1 运行环境
### 1.1 安装 Python 3.x

    sudo apt update
    sudo apt install -y libnss3 libatk-bridge2.0-0 libcups2 libxcomposite1 libxrandr2 libxdamage1 libgbm-dev libxshmfence-dev fonts-liberation
    sudo apt install python3 python3-pip
### 1.2 安装 Playwright

 pip3 install playwright
 playwright install
 playwright install-deps
### 1.3 安装其他 Python 依赖
    pip3 install requests imaplib2
## 2 配置邮箱访问
访问 Google 账号设置。

进入 安全性 > 应用密码，生成一个新的应用密码。

准备 mail.txt 文件,在代码运行的目录下创建一个mail.txt 文件，内容格式为：

邮箱名|专用密码

## 3 运行命令
    python3 stable.py
## 3 运行时
<img width="1352" height="1610" alt="image" src="https://github.com/user-attachments/assets/aaf4acef-ade8-4f10-b33d-fa1617df91ed" />
