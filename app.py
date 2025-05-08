import paramiko
import logging
import time
import configparser
from flask import Flask, render_template_string
from flask_sock import Sock
from ansi2html import Ansi2HTMLConverter  # 用于转义ANSI字符

# 读取配置文件
config = configparser.ConfigParser()
config.read('config.ini')

# 从配置文件中获取配置
ssh_host = config.get('ssh', 'host')
ssh_username = config.get('ssh', 'username')
ssh_password = config.get('ssh', 'password')
elog_path = config.get('Paths', 'elog_path')
flask_host = config.get('flask', 'host')
flask_port = config.getint('flask', 'port')

app = Flask(__name__)
sock = Sock(app)

logging.basicConfig(level=logging.INFO)

# 初始化 ANSI 转换器
converter = Ansi2HTMLConverter()

class SSHAgent:
    def __init__(self):
        self.client = paramiko.SSHClient()
        self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
        try:
            self.client.connect(ssh_host, username=ssh_username, password=ssh_password, timeout=10)
            logging.info("SSH连接成功")
        except Exception as e:
            logging.error(f"SSH连接失败: {e}")

    def execute_command(self, command):
        """执行命令并获取输出"""
        stdin, stdout, stderr = self.client.exec_command(command, get_pty=True, timeout=60)
        return stdout, stderr

    @staticmethod
    def split_utf8(buffer):
        """从buffer中尽量解出完整的UTF8字符串，保留不完整部分用于下次处理"""
        for i in range(4):
            try:
                text = buffer[:-i] if i else buffer
                remaining = buffer[-i:] if i else b''
                return text.decode('utf-8'), remaining
            except UnicodeDecodeError:
                continue
        return buffer.decode('utf-8', errors='ignore'), b''

ssh_agent = SSHAgent()

@app.route('/')
def index():
    return render_template_string('''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Notion同步助手</title>
        <link rel="icon" href="https://img.icons8.com/ios/452/synchronize.png"> <!-- 设置同步图标 -->
        <link href="https://fonts.googleapis.com/css2?family=Pacifico&display=swap" rel="stylesheet"> <!-- 加载Pacifico字体 -->
        <script src="https://cdn.tailwindcss.com"></script>
        <script src="https://cdn.jsdelivr.net/npm/ansi-to-html@0.7.2/lib/ansi_to_html.min.js"></script>
        <style>
            body { font-family: Arial, sans-serif; background-color: #f4f4f4; padding: 20px; }
            /* 标题区域样式 */
            .header {
                background-color: #3b82f6; /* 背景颜色 */
                color: white; /* 文字颜色 */
                padding: 40px 20px; /* 上下内边距 */
                text-align: center; /* 居中对齐 */
                border-radius: 12px; /* 边角圆滑 */
                margin-bottom: 40px; /* 标题区域与下方内容间距 */
            }
            h1 {
                font-family: 'Pacifico', cursive;
                font-size: 4rem;
                font-weight: bold;
                margin: 0;
            }
            /* 输出区域样式 */
            .output { background-color: black; color: green; font-family: monospace; padding: 15px; height: 400px; overflow-y: scroll; border-radius: 8px; }
            button {
                padding: 16px 30px;
                font-size: 20px;
                border-radius: 12px;
                transition: all 0.3s ease;
                width: 250px;
                text-align: center;
            }
            .sync-btn { background-color: #4CAF50; color: white; border: none; }
            .sync-btn:hover { background-color: #45a049; }
            .clean-btn { background-color: #f44336; color: white; border: none; }
            .clean-btn:hover { background-color: #da190b; }
            .loading { color: #aaa; }
            /* 按钮区域样式 */
            .flex-container { display: flex; justify-content: center; gap: 40px; flex-wrap: wrap; margin-bottom: 30px; }
            @media (max-width: 768px) {
                h1 { font-size: 3rem; }
                button { width: 200px; padding: 14px 25px; font-size: 18px; }
            }
            @media (max-width: 480px) {
                h1 { font-size: 2.5rem; }
                button { width: 180px; padding: 12px 20px; font-size: 16px; }
            }
        </style>
    </head>
    <body>
        <!-- 标题区域 -->
        <div class="header">
            <h1>Notion同步助手</h1>
        </div>
        <!-- 按钮区域 -->
        <div class="flex-container">
            <button onclick="executeCommand('elog sync -e .elog.env')" class="sync-btn">同步文章</button>
            <button onclick="executeCommand('elog clean')" class="clean-btn">清除缓存</button>
        </div>
        <!-- 输出区域 -->
        <div class="output" id="output">
            <pre>等待命令执行...</pre>
        </div>
        <script>
            let socket = null;

            function initWebSocket() {
                protocol = window.location.protocol === "https:" ? "wss://" : "ws://";
                socket = new WebSocket(`${protocol}${window.location.host}/terminal`);

                socket.onopen = () => {
                    console.log('WebSocket连接已建立');
                    document.getElementById('output').innerHTML = "<pre class='text-green-500'>终端已连接</pre>";
                };

                socket.onmessage = (event) => {
                    const output = document.getElementById('output');
                    output.innerHTML += event.data;  // 实时更新输出
                    output.scrollTop = output.scrollHeight;  // 滚动到底部
                };

                socket.onerror = (error) => {
                    document.getElementById('output').innerHTML = "<pre class='text-red-500'>连接错误</pre>";
                };
            }

            function executeCommand(command) {
                const output = document.getElementById('output');
                output.innerHTML = "<pre class='loading'>执行中...</pre>";

                if (socket && socket.readyState === WebSocket.OPEN) {
                    socket.send(command);  // 发送命令到后端
                } else {
                    output.innerHTML = "<pre class='text-red-500'>错误：未连接到终端</pre>";
                }
            }

            window.addEventListener('load', initWebSocket);
        </script>
    </body>
    </html>
    ''')

@sock.route('/terminal')
def terminal(ws):
    logging.info("客户端连接到终端")
    while True:
        try:
            command = ws.receive()
            logging.info(f"执行命令: {command}")
            # 执行命令并获取输出
            stdout, stderr = ssh_agent.execute_command(f'cd "{elog_path}" && {command}')

            buffer = b""
            while True:
                # 检查是否有新输出
                if stdout.channel.recv_ready():
                    buffer += stdout.channel.recv(1024)
                if stderr.channel.recv_stderr_ready():
                    buffer += stderr.channel.recv_stderr(1024)

                # 如果有输出，逐行处理并发送给客户端
                if buffer:
                    decoded_output, remaining = SSHAgent.split_utf8(buffer)
                    if decoded_output:
                        # 转换ANSI字符为HTML
                        html_output = converter.convert(decoded_output)
                        ws.send(html_output)  # 发送经过转换的HTML
                    buffer = remaining

                if stdout.channel.exit_status_ready():  # 命令执行完毕
                    break

                time.sleep(0.1)  # 避免CPU占用过高

            ws.send("<pre class='text-green-500'>命令执行完成</pre>")

        except Exception as e:
            logging.error(f"执行命令时发生错误: {e}")
            ws.send(f"<pre class='text-red-500'>系统错误: {e}</pre>")

if __name__ == '__main__':
    app.run(host=flask_host, port=flask_port, debug=False)
