import asyncio
import logging
import requests
from aiogram import Bot, Dispatcher, types, F
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder

# --- KONFIGURATSIYA ---
API_TOKEN = '8417425492:AAFIh5XXlFrERRChL_fPINkFioX9lx7YpbU'
RAPID_API_KEY = 'fcc987c584mshae4be304af226dfp1d1c35jsn483d541ee632'
RAPID_HOST = 'instagram-reels-downloader-api.p.rapidapi.com'

bot = Bot(token=API_TOKEN)
dp = Dispatcher()

# Foydalanuvchi ma'lumotlarini keshda saqlash
user_cache = {}

@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        "👋 **Xush kelibsiz!**\n\n"
        "Instagram linkini yuboring, men sizga video va musiqasini taqdim etaman! 🚀"
    )

@dp.message()
async def handle_message(message: types.Message):
    link = message.text
    if "instagram.com" in link:
        msg = await message.answer("Tez va oson yuklab olish boshlandi... ⏳")
        
        try:
            url = f"https://{RAPID_HOST}/download"
            headers = {"x-rapidapi-key": RAPID_API_KEY, "x-rapidapi-host": RAPID_HOST}
            response = requests.get(url, headers=headers, params={"url": link})
            res = response.json()
            
            if res.get('success') and 'data' in res:
                info = res['data']
                video_url = None
                audio_url = None
                
                for media in info.get('medias', []):
                    if media['type'] == 'video': video_url = media['url']
                    if media['type'] == 'audio': audio_url = media['url']

                if video_url:
                    # Ma'lumotlarni saqlash
                    user_cache[message.from_user.id] = {'audio': audio_url, 'title': info.get('title', 'Video')}
                    
                    # Tugmalar (Rasmda ko'ringanidek)
                    builder = InlineKeyboardBuilder()
                    builder.add(types.InlineKeyboardButton(text="🎬 Video", callback_data="v_done"))
                    if audio_url:
                        builder.add(types.InlineKeyboardButton(text="🎵 Musiqa", callback_data="get_audio_file"))
                    builder.adjust(2)

                    caption = (
                        f"🎵 **{info.get('title', 'Instagram Video')}**\n\n"
                        f"👤 Avtor: {info.get('author', 'Nomaʼlum')}\n"
                        f"📥 @insta_videomusicBot orqali yuklab olindi"
                    )
                    
                    await bot.delete_message(message.chat.id, msg.message_id)
                    await message.answer_video(
                        video=video_url,
                        caption=caption,
                        reply_markup=builder.as_markup()
                    )
                else:
                    await message.answer("❌ Video manzilini olib bo'lmadi.")
            else:
                await message.answer("❌ Link noto'g'ri yoki profil yopiq.")

        except Exception as e:
            logging.error(f"Xato: {e}")
            await message.answer("⚠️ Texnik xatolik yuz berdi.")
    elif not message.text.startswith('/'):
        await message.answer("Iltimos, faqat Instagram havolasini yuboring! 🔗")

@dp.callback_query(F.data == "get_audio_file")
async def send_audio(callback: types.CallbackQuery):
    data = user_cache.get(callback.from_user.id)
    if data and data['audio']:
        await bot.send_chat_action(callback.message.chat.id, "upload_voice")
        try:
            await callback.message.answer_audio(
                audio=data['audio'],
                caption=f"🎧 {data['title']}\n\n✨ @insta_videomusicBot orqali topildi"
            )
            await callback.answer()
        except Exception:
            await callback.answer("Musiqa yuklashda xato!")
    else:
        await callback.answer("Musiqa topilmadi.")

@dp.callback_query(F.data == "v_done")
async def v_done(callback: types.CallbackQuery):
    await callback.answer("Video yuklab bo'lindi! ✅")

# Doimiy ishlashni ta'minlovchi funksiya
async def main():
    logging.basicConfig(level=logging.INFO)
    while True:
        try:
            print("Bot 24/7 rejimda ishga tushdi...")
            await dp.start_polling(bot)
        except Exception as e:
            print(f"Ulanish uzildi: {e}. 10 soniyadan so'ng qayta ulanadi.")
            await asyncio.sleep(10)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot to'xtatildi.")