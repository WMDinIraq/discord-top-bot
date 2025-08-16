import discord
from discord import app_commands
from discord.ui import Button, View
import os
from dotenv import load_dotenv
from flask import Flask
import threading

# --- 环境变量和机器人设置 ---
load_dotenv()
TOKEN = os.getenv('DISCORD_TOKEN')

intents = discord.Intents.default()
intents.message_content = True
intents.messages = True

bot = discord.Client(intents=intents)
tree = app_commands.CommandTree(bot)

# --- 这是一个全新的部分：迷你网站 ---
# 创建一个 Flask web 应用实例
app = Flask('')

# 定义网站的根目录（'/'），当有人访问时，就执行下面的函数
@app.route('/')
def home():
    # 返回一个简单的消息，告诉 Render 和 UptimeRobot "我还活着！"
    return "I'm alive"

# 定义一个函数，用来在后台运行这个网站
def run_web_server():
    # '0.0.0.0' 表示监听所有网络接口，port=8080 是 Render 常用的端口
    app.run(host='0.0.0.0', port=8080)

# --- 这是您熟悉的回顶指令 ---
@tree.command(name="回顶", description="创建一个按钮，点击后跳转到本频道的第一条消息")
async def jump_to_top(interaction: discord.Interaction):
    try:
        async for first_message in interaction.channel.history(limit=1, oldest_first=True):
            jump_button = Button(label="🚀 点我回到顶部", style=discord.ButtonStyle.link, url=first_message.jump_url)
            view = View()
            view.add_item(jump_button)
            await interaction.response.send_message("已为你生成回顶按钮：", view=view, ephemeral=True)
            return
    except discord.Forbidden:
        await interaction.response.send_message("错误：我没有权限读取这个频道的历史消息！请检查机器人角色权限。", ephemeral=True)
    except Exception as e:
        print(f"发生错误: {e}")
        await interaction.response.send_message("发生未知错误，无法找到第一条消息。", ephemeral=True)

# --- 机器人上线事件 ---
@bot.event
async def on_ready():
    await tree.sync()
    print("-----------------------------------------")
    print(f"机器人 {bot.user} 已成功登录！")
    print(f"ID: {bot.user.id}")
    print("迷你网站也在后台运行中...")
    print("-----------------------------------------")

# --- 最终的启动部分 ---
# 创建一个“线程”，让我们的迷你网站在后台悄悄运行，不影响机器人
web_thread = threading.Thread(target=run_web_server)
web_thread.start()

# 启动我们的机器人！
bot.run(TOKEN)