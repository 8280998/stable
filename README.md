# stable
stabl候补白名单批量注册程序，程序会随机生成一个注册名@你的域名，注册成功后输出到verifymail.txt中

## stable白名单批量注册程序 9月29号官方添加了人机验证，目前已失效

注意：准备一个域名，设置域名转发功能，转发到你的GMAIL邮箱。可以使用cloudflare的转发功能，或其他。

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
## 2.1 配置邮箱访问
访问 Google 账号设置。

进入 安全性 > 应用密码，生成一个新的应用密码。

准备 mail.txt 文件,在代码运行的目录下创建一个mail.txt 文件，内容格式为：

邮箱名|专用密码

## 2.2 域名邮箱配置

修改stable.py中的domain.com为你的注册域名，并且这个域名已设置好转发到google的配置邮箱收取验证码

## 3 运行命令
    python3 stable.py
## 3 运行时
<img width="1352" height="1610" alt="image" src="https://github.com/user-attachments/assets/aaf4acef-ade8-4f10-b33d-fa1617df91ed" />
