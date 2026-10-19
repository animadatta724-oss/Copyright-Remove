import os
import random
import subprocess
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters

# --- CONFIGURATION ---
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

def pro_anti_copyright_process(input_path, output_path):
    speed = round(random.uniform(1.03, 1.07), 3)
    pitch = round(random.uniform(0.93, 0.97), 2)
    
    video_filter = (
        f"setpts=PTS/{speed},"
        "hflip,"
        "colorchannelmixer=rr=0.98:rg=0.02:rb=0.0:gr=0.0:gg=0.96:gb=0.04:br=0.0:bg=0.02:bb=0.98,"
        "vignette=angle=PI/4,"
        "eq=contrast=1.15:brightness=0.06:saturation=1.18:gamma=1.1,"
        "noise=alls=22:allf=t+u,"
        "scale=iw*0.95:ih*0.95,"
        "drawtext=text='@filmyhubofficial':fontcolor=white@0.7:fontsize=24:x=w-tw-20:y=h-th-20,"
        "fps=30"
    )
    
    audio_filter = (
        f"asetrate=44100*{speed}*{pitch},"
        "aresample=44100,"
        "pan=stereo|c0=0.8*c0+0.2*c1|c1=0.2*c0+0.8*c1,"
        "highpass=f=250,"
        "lowpass=f=11000,"
        "volume=0.85"
    )
    
    command = [
        "ffmpeg", "-y", "-i", input_path,
        "-vf", video_filter, "-af", audio_filter,
        "-map_metadata", "-1", "-map_chapters", "-1", "-fflags", "+bitexact",
        "-c:v", "libx264", "-preset", "medium", "-crf", "18",
        "-c:a", "aac", "-b:a", "192k", output_path
    ]
    subprocess.run(command, check=True)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 **Welcome!**\n\nAnti-Copyright Bot is Active via Telegram Bot Library!")

async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message = update.message
    file = message.video or message.document
    if not file:
        return

    status_msg = await message.reply_text("📥 Video download ho raha hai...")
    
    # File download
    new_file = await context.bot.get_file(file.file_id)
    input_file = f"downloads_{message.from_user.id}.mp4"
    output_file = f"processed_{message.from_user.id}.mp4"
    os.makedirs(".", exist_ok=True)
    
    await new_file.download_to_drive(input_file)
    await status_msg.edit_text("⚙️ **Processing, Watermarking & Stripping Metadata...**")
    
    try:
        pro_anti_copyright_process(input_file, output_file)
        await status_msg.edit_text("📤 **Processing Complete! Video bheja ja raha hai...**")
        
        with open(output_file, 'rb') as f:
            await message.reply_video(video=f, caption="✅ **Processed Anti-Copyright Video Ready!**\n- Watermark: `@filmyhubofficial`")
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ **Error Aaya:** `{str(e)}`")
    finally:
        if os.path.exists(input_file): os.remove(input_file)
        if os.path.exists(output_file): os.remove(output_file)

if __name__ == "__main__":
    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video))
    print("🤖 Telegram Bot Started Successfully!")
    app.run_polling()
    
