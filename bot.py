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
app = Flask('')

@app.route('/')
def home():
    return "I'm alive"

def run_web_server():
    app.run(host='0.0.0.0', port=8080)

# --- 这是您熟悉的回顶指令【已修复 Bug 的版本】 ---
@tree.command(name="回顶", description="创建一个按钮，点击后跳转到本频道的第一条消息")
async def jump_to_top(interaction: discord.Interaction):
    try:
        # 【第1处修改】立刻回应 Discord，告诉它“请稍等”，以遵守 3 秒规则
        # ephemeral=True 表示这个"思考中..."的消息只有用户自己能看到
        await interaction.response.defer(ephemeral=True)

        async for first_message in interaction.channel.history(limit=1, oldest_first=True):
            jump_button = Button(label="🚀 点我回到顶部", style=discord.ButtonStyle.link, url=first_message.jump_url)
            view = View()
            view.add_item(jump_button)
            
            # 【第2处修改】因为我们已经 defer() 过了，所以现在要用 followup.send 来发送最终结果
            await interaction.followup.send("已为你生成回顶按钮：", view=view)
            return
            
    except discord.Forbidden:
        # 【第3处修改】在错误处理中，也使用 followup.send
        await interaction.followup.send("错误：我没有权限读取这个频道的历史消息！")
    except Exception as e:
        print(f"发生错误: {e}")
        # 【第4处修改】在错误处理中，也使用 followup.send
        await interaction.followup.send("发生未知错误，无法找到第一条消息。")

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
web_thread = threading.Thread(target=run_web_server)
web_thread.start()

bot.run(TOKEN)