import asyncio
import os
import random
import subprocess
from pyrogram import Client, filters
from pyrogram.types import Message

# --- SECURE CONFIGURATION ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

app = Client(
    "facebook_bypass_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


def light_anti_copyright_process(input_path, output_path):
  speed = round(random.uniform(1.03, 1.07), 3)
  pitch = round(random.uniform(0.93, 0.97), 2)

  # Low-Memory & Fast Anti-Copyright Filters (Safe for 512MB RAM)
  video_filter = (
      f"setpts=PTS/{speed},"
      "hflip,"
      "colorchannelmixer=rr=0.98:rg=0.02:rb=0.0:gr=0.0:gg=0.96:gb=0.04:br=0.0:bg=0.02:bb=0.98,"
      "eq=contrast=1.12:brightness=0.04:saturation=1.15:gamma=1.05,"
      "scale=iw*0.95:ih*0.95,"
      "drawtext=text='@filmyhubofficial':fontcolor=white@0.7:fontsize=24:x=w-tw-20:y=h-th-20,"
      "fps=30"
  )

  audio_filter = (
      f"asetrate=44100*{speed}*{pitch},"
      "aresample=44100,"
      "highpass=f=200,"
      "lowpass=f=12000,"
      "volume=0.85"
  )

  # Optimized command with low RAM footprint (-threads 2, preset ultrafast)
  command = [
      "ffmpeg",
      "-y",
      "-i",
      input_path,
      "-vf",
      video_filter,
      "-af",
      audio_filter,
      "-map_metadata",
      "-1",
      "-map_chapters",
      "-1",
      "-fflags",
      "+bitexact",
      "-c:v",
      "libx264",
      "-preset",
      "ultrafast",  # RAM aur CPU bachane ke liye
      "-crf",
      "23",
      "-threads",
      "2",  # Strict thread limit for 512MB RAM
      "-c:a",
      "aac",
      "-b:a",
      "128k",
      output_path,
  ]

  subprocess.run(command, check=True)


@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
  await message.reply_text(
      "👋 **Welcome!**\n\nOptimized Anti-Copyright Bot is Active & Running 24/7!"
  )


@app.on_message(filters.video | filters.document)
async def handle_video(client, message: Message):
  if message.document and not message.document.mime_type.startswith("video/"):
    return

  status_msg = await message.reply_text("📥 Video download ho raha hai...")
  input_file = f"downloads_{message.from_user.id}.mp4"
  output_file = f"processed_{message.from_user.id}.mp4"

  try:
    await message.download(file_name=input_file)
    await status_msg.edit_text(
        "⚙️ **Fast Processing & Watermarking Shuru Ho Gayi Hai...**"
    )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, light_anti_copyright_process, input_file, output_file
    )

    await status_msg.edit_text(
        "📤 **Processing Complete! Video bheja ja raha hai...**"
    )

    caption = (
        "✅ **Processed Anti-Copyright Video Ready!**\n\n- Watermark:"
        " `@filmyhubofficial`\n- Metadata Stripped\n- Optimized for Cloud"
    )

    await message.reply_video(
        video=output_file, caption=caption, supports_streaming=True
    )
    await status_msg.delete()

  except Exception as e:
    await status_msg.edit_text(f"❌ **Error Aaya:** `{str(e)}`")
  finally:
    if os.path.exists(input_file):
      os.remove(input_file)
    if os.path.exists(output_file):
      os.remove(output_file)


if __name__ == "__main__":
  print("🤖 Telegram Bot Started Successfully!")
  app.run()
    
