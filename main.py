import os
from aiogram import Bot, Dispatcher, types, executor
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
import httpx
import asyncio

# المتغيرات من البيئة
BOT_TOKEN = os.getenv("BOT_TOKEN")
ADSTERRA_LINK = os.getenv("ADSTERRA_LINK")
FAL_API_KEY = os.getenv("FAL_API_KEY")

bot = Bot(token=BOT_TOKEN, parse_mode="HTML")
dp = Dispatcher(bot)

@dp.message_handler(commands=['start'])
async def start(message: types.Message):
    keyboard = InlineKeyboardMarkup()
    keyboard.add(InlineKeyboardButton("🚀 ابدأ توليد الصور", callback_data="generate"))
    await message.reply(
        "<b>مرحباً بك في بوت توليد الصور Flux AI 🎨</b>\n\n"
        "اكتب أي وصف تريده وسيتم توليد الصورة فوراً!\n"
        "مثال: فتاة انمي جميلة في غابة سحرية",
        reply_markup=keyboard
    )

@dp.message_handler(content_types=['text'])
async def handle_text(message: types.Message):
    prompt = message.text.strip()
    if len(prompt) < 3:
        await message.reply("📝 اكتب وصف أطول شوية 😅")
        return

    sent = await message.reply("🌀 جاري توليد الصورة... انتظر 5-15 ثانية")

    async with httpx.AsyncClient(timeout=60.0) as client:
        try:
            response = await client.post(
                "https://fal.run/fal-ai/flux/schnell",
                headers={"Authorization": f"Key {FAL_API_KEY}"},
                json={"prompt": prompt, "image_size": "square"}
            )
            result = response.json()
            image_url = result['images'][0]['url']
        except Exception as e:
            await sent.edit_text("❌ حصل خطأ، جرب مرة ثانية")
            return

    keyboard = InlineKeyboardMarkup(row_width=1)
    keyboard.add(
        InlineKeyboardButton("⚡ تحميل الصورة بدقة عالية", url=ADSTERRA_LINK)
    )

    await sent.delete()
    await message.reply_photo(
        photo=image_url,
        caption=f"<b>تم التوليد بنجاح! 🎉</b>\n\n"
                f"<i>الوصف:</i> <code>{prompt}</code>\n\n"
                "اضغط الزر تحت الصورة لحفظها بأعلى جودة 👇",
        reply_markup=keyboard
    )

@dp.callback_query_handler(lambda c: c.data == "generate")
async def generate_callback(call: types.CallbackQuery):
    await call.message.edit_text(
        "اكتب الآن الوصف الذي تريده وسيتم توليد الصورة فوراً 🚀\n"
        "مثال: قطة ترتدي نظارات شمسية على شاطئ"
    )

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
