import os
import telebot
import yt_dlp

API_TOKEN = '8281853248:AAEUfJ7SmyvzfGW511Qamg_WjlPrCeeSjm8'
bot = telebot.TeleBot(API_TOKEN)

os.makedirs("downloads", exist_ok=True)

print("Music bot is running successfully...")

@bot.message_handler(commands=['start', 'help'])
def send_welcome(message):
    bot.reply_to(message, "👋 Hello! Send me any song name or a YouTube link, and I will find and download it for you for free!")

@bot.message_handler(func=lambda message: True)
def download_and_send_music(message):
    query = message.text
    chat_id = message.chat.id
    
    bot.send_chat_action(chat_id, 'upload_voice')
    msg = bot.reply_to(message, f"🔍 Searching for song: '{query}'... Please wait a moment.")

    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': 'downloads/%(title)s.%(ext)s',
        'default_search': 'ytsearch1',
        'noplaylist': True,
        'ffmpeg_location': '.',  # Käyttää Työpöydällä olevia hyviä tiedostoja
        'postprocessors': [{
            'key': 'FFmpegExtractAudio',
            'preferredcodec': 'mp3',
            'preferredquality': '192',
        }],
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Pakotetaan haku tekstin perusteella oikeassa muodossa
            info = ydl.extract_info(f"ytsearch1:{query}", download=True)
            
            # Korjaus: Tarkistetaan oikealla tavalla, tuliko haku listana vai yksittäisenä videona
            if 'entries' in info and len(info['entries']) > 0:
                video_info = info['entries'][0]
            else:
                video_info = info
                
            title = video_info.get('title', 'audio')
            expected_filename = f"downloads/{title}.mp3"

        # Lähetetään valmis MP3-tiedosto chattiin
        with open(expected_filename, 'rb') as audio:
            bot.send_audio(chat_id, audio, title=title)
            
        # Siivotaan tiedosto pois koneelta
        os.remove(expected_filename)
        bot.delete_message(chat_id, msg.message_id)

    except Exception as e:
        bot.edit_message_text(f"❌ Something went wrong: {str(e)}", chat_id, msg.message_id)

bot.infinity_polling()
