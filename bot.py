import os
from dotenv import load_dotenv
import discord
load_dotenv()
from discord import app_commands
from discord.ui import Button, View

# --- 机器人设置 ---
# 定义机器人的意图（权限），读取消息历史是必须的
intents = discord.Intents.default()
intents.message_content = True # 如果需要读取消息内容，也建议开启
intents.messages = True      # 明确需要读取消息的权限

# 创建机器人客户端实例
bot = discord.Client(intents=intents)
# 创建指令树，用于处理斜杠指令
tree = app_commands.CommandTree(bot)

# --- 指令定义 ---
# 定义一个名为 "回顶" 的斜杠指令
@tree.command(name="回顶", description="创建一个按钮，点击后跳转到本频道的第一条消息")
async def jump_to_top(interaction: discord.Interaction):
    """处理 /回顶 指令的函数"""
    try:
        # 在当前频道中，寻找历史消息。limit=1 表示只找1条，oldest_first=True 表示从最旧的开始找
        async for first_message in interaction.channel.history(limit=1, oldest_first=True):
            # 创建一个链接按钮
            # first_message.jump_url 会自动生成跳转到该消息的链接
            jump_button = Button(label="🚀 点我回到顶部", style=discord.ButtonStyle.link, url=first_message.jump_url)
            
            # 创建一个视图 (View) 来容纳这个按钮
            view = View()
            view.add_item(jump_button)
            
            # 回复用户的指令，发送带有按钮的消息
            # ephemeral=True 表示这条消息只有发送指令的用户自己能看到，非常推荐！
            await interaction.response.send_message("已为你生成回顶按钮：", view=view, ephemeral=True)
            return # 找到消息并发送按钮后，结束函数

    except discord.Forbidden:
        # 如果机器人没有 "读取消息历史" 的权限，会触发这个错误
        await interaction.response.send_message("错误：我没有权限读取这个频道的历史消息！请检查机器人角色权限。", ephemeral=True)
    except Exception as e:
        # 捕获其他可能的错误
        print(f"发生错误: {e}")
        await interaction.response.send_message("发生未知错误，无法找到第一条消息。", ephemeral=True)

# --- 机器人事件 ---
@bot.event
async def on_ready():
    """当机器人成功连接到 Discord 后会执行这个函数"""
    # 同步指令到 Discord，这样斜杠指令才能显示出来
    await tree.sync()
    print("-----------------------------------------")
    print(f"机器人 {bot.user} 已成功登录！")
    print(f"ID: {bot.user.id}")
    print("可以开始使用了！")
    print("-----------------------------------------")

# --- 运行机器人 ---
# 在下面这行代码的引号内，粘贴你自己的机器人令牌
bot.run(os.getenv('DISCORD_TOKEN'))