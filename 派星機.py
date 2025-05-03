import discord
from discord.ext import commands
import os
import random

# 設置 Discord 機器人
intents = discord.Intents.default()
intents.message_content = True
bot = commands.Bot(command_prefix='!', intents=intents)

# 資料夾路徑設定
BASE_DIR = os.path.dirname(__file__)
MEME_FOLDER = os.path.join(BASE_DIR, 'memes')
CORRECT_FOLDER = os.path.join(BASE_DIR, 'correct')
WRONG_FOLDER = os.path.join(BASE_DIR, 'wrong')

# DEBUG 資訊
print("=== DEBUG 資訊 ===")
print("當前工作目錄：", os.getcwd())
print("memes 資料夾存在嗎？", os.path.exists(MEME_FOLDER))
print("memes 資料夾完整路徑：", os.path.abspath(MEME_FOLDER))

# 儲存頻道的猜數字狀態
channel_game = {}  # {channel_id: {'answer': int, 'attempts': int}}

# 當機器人準備好時
@bot.event
async def on_ready():
    print(f'已登入為 {bot.user}')

# !抽：隨機梗圖
@bot.command(name='抽')
async def draw_meme(ctx):
    try:
        meme_files = [f for f in os.listdir(MEME_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if not meme_files:
            await ctx.send('抱歉，沒有找到任何梗圖！')
            return
        random_meme = random.choice(meme_files)
        meme_path = os.path.join(MEME_FOLDER, random_meme)
        with open(meme_path, 'rb') as f:
            picture = discord.File(f)
            await ctx.send(file=picture)
    except FileNotFoundError:
        await ctx.send('錯誤：找不到 memes 資料夾或檔案！')
    except discord.errors.Forbidden:
        await ctx.send('錯誤：我沒有權限在這個頻道傳送訊息或檔案！')
    except Exception as e:
        await ctx.send(f'發生錯誤：{str(e)}')
        print(f'錯誤：{str(e)}')

# !猜數字：群組猜數字
@bot.command(name='猜數字')
async def guess_number(ctx, guess: int):
    channel_id = ctx.channel.id

    if channel_id not in channel_game:
        channel_game[channel_id] = {
            'answer': random.randint(1, 100),
            'attempts': 0
        }
        print(f"頻道 {ctx.channel} 的目標數字是 {channel_game[channel_id]['answer']}")

    game = channel_game[channel_id]
    game['attempts'] += 1
    answer = game['answer']

    if guess == answer:
        attempts = game['attempts']
        del channel_game[channel_id]
        correct_imgs = [f for f in os.listdir(CORRECT_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        await ctx.send(f'🎉 {ctx.author.display_name} 猜對了！數字是 {guess}，全體共猜了 {attempts} 次！')
        if correct_imgs:
            img_path = os.path.join(CORRECT_FOLDER, random.choice(correct_imgs))
            await ctx.send(file=discord.File(img_path))
    elif guess < answer:
        await ctx.send(f'{ctx.author.display_name} 猜的太小了 👇')
        wrong_imgs = [f for f in os.listdir(WRONG_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if wrong_imgs:
            img_path = os.path.join(WRONG_FOLDER, random.choice(wrong_imgs))
            await ctx.send(file=discord.File(img_path))
    else:
        await ctx.send(f'{ctx.author.display_name} 猜的太大了 👆')
        wrong_imgs = [f for f in os.listdir(WRONG_FOLDER) if f.endswith(('.png', '.jpg', '.jpeg', '.gif'))]
        if wrong_imgs:
            img_path = os.path.join(WRONG_FOLDER, random.choice(wrong_imgs))
            await ctx.send(file=discord.File(img_path))

# !猜幾次：顯示目前猜的次數
@bot.command(name='猜幾次')
async def guess_attempts(ctx):
    channel_id = ctx.channel.id
    if channel_id in channel_game:
        attempts = channel_game[channel_id]['attempts']
        await ctx.send(f'這個頻道已經猜了 {attempts} 次！')
    else:
        await ctx.send('這個頻道目前還沒開始猜數字喔，輸入 `!猜數字 數字` 來開始！')

# !放棄：顯示答案並重設
@bot.command(name='放棄')
async def give_up(ctx):
    channel_id = ctx.channel.id
    if channel_id in channel_game:
        answer = channel_game[channel_id]['answer']
        del channel_game[channel_id]
        await ctx.send(f'遊戲結束，正確答案是：{answer}')
    else:
        await ctx.send('目前沒有正在進行的猜數字遊戲。')

# !測試：測試用
@bot.command(name='測試')
async def test(ctx):
    await ctx.send('機器人正常運作！')

# 啟動 bot（請改成你的 Token）
bot.run('MTM2NzkwMjg1MjIzOTk4MjY0Mw.GgbL6c.x6SlFD5cI_Wedi7T-ULIL5B4VqDeQXpP_9CVeo')
