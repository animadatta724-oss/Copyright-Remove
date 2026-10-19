import asyncio
import os
import random
import subprocess
import requests
from pyrogram import Client, filters
from pyrogram.types import Message

# --- SECURE CONFIGURATION (Render Environment Variables se uthayega) ---
API_ID = int(os.environ.get("API_ID", 0))
API_HASH = os.environ.get("API_HASH", "")
BOT_TOKEN = os.environ.get("BOT_TOKEN", "")

# Facebook Page Credentials (Render Environment Variables me set karein)
FB_PAGE_ID = os.environ.get("FB_PAGE_ID", "")
FB_ACCESS_TOKEN = os.environ.get("FB_ACCESS_TOKEN", "")

app = Client(
    "facebook_bypass_bot",
    api_id=API_ID,
    api_hash=API_HASH,
    bot_token=BOT_TOKEN,
)


def pro_anti_copyright_process(input_path, output_path):
  speed = round(random.uniform(1.03, 1.07), 3)
  pitch = round(random.uniform(0.93, 0.97), 2)

  # God-Mode Filters + Watermark (@filmyhubofficial)
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

  # Advanced Metadata Stripping (-map_metadata -1)
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
      "medium",
      "-crf",
      "18",
      "-c:a",
      "aac",
      "-b:a",
      "192k",
      output_path,
  ]

  subprocess.run(command, check=True)


def upload_video_to_facebook_page(video_path, caption):
  """Facebook Graph API se Video ko Draft/Unpublished Mode me upload karta hai."""
  url = f"https://graph-video.facebook.com/v19.0/{FB_PAGE_ID}/videos"
  payload = {
      "description": caption,
      "published": "false",  # Draft mode (Owner baad me public karega)
      "access_token": FB_ACCESS_TOKEN,
  }

  with open(video_path, "rb") as video_file:
    files = {"source": video_file}
    response = requests.post(url, data=payload, files=files)
    return response.json()


@app.on_message(filters.command("start"))
async def start_cmd(client, message: Message):
  await message.reply_text(
      "👋 **Welcome!**\n\nRender Cloud Par Telegram-to-Facebook Page Auto-Upload"
      " Bot Active Hai!"
  )


@app.on_message(filters.video | filters.document)
async def handle_video(client, message: Message):
  if message.document and not message.document.mime_type.startswith("video/"):
    return

  status_msg = await message.reply_text("📥 Video download ho raha hai...")
  input_file = f"downloads/{message.from_user.id}_{message.id}.mp4"
  output_file = f"downloads/processed_{message.from_user.id}_{message.id}.mp4"
  os.makedirs("downloads", exist_ok=True)

  try:
    await message.download(file_name=input_file)
    await status_msg.edit_text(
        "⚙️ **Processing, Watermarking & Stripping Metadata...**"
    )

    loop = asyncio.get_event_loop()
    await loop.run_in_executor(
        None, pro_anti_copyright_process, input_file, output_file
    )

    await status_msg.edit_text(
        "📤 **Processing Complete! Facebook Page par Draft upload ho raha"
        " hai...**"
    )

    caption = (
        "🎬 New Movie Clip\n\n- Watermark: @filmyhubofficial\n- Status:"
        " Anti-Copyright Processed"
    )

    # Facebook Page upload
    fb_response = upload_video_to_facebook_page(output_file, caption)

    if "id" in fb_response:
      await status_msg.edit_text(
          "✅ **Facebook Page Par Successful Draft Upload Ho Gaya!**\n\nAap Meta"
          " Business Suite khol kar video publish kar sakte hain."
      )
    else:
      await status_msg.edit_text(
          f"⚠️ **Facebook Upload Error:** `{str(fb_response)}`"
      )

  except Exception as e:
    await status_msg.edit_text(f"❌ **Error Aaya:** `{str(e)}`")
  finally:
    if os.path.exists(input_file):
      os.remove(input_file)
    if os.path.exists(output_file):
      os.remove(output_file)


if __name__ == "__main__":
  print("🤖 Render Bot Active & Running!")
  app.run()
  
