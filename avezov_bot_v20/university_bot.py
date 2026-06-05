from http.server import HTTPServer, BaseHTTPRequestHandler
import threading

class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        self.send_response(200)
        self.end_headers()
        self.wfile.write(b'OK')
    def log_message(self, format, *args):
        pass

threading.Thread(
    target=lambda: HTTPServer(('0.0.0.0', 8080), Handler).serve_forever(),
    daemon=True
).start()

import os
import sqlite3
import datetime
import logging
from dotenv import load_dotenv
from telegram import (
    InlineKeyboardButton, InlineKeyboardMarkup, BotCommand,
    ReplyKeyboardMarkup, KeyboardButton
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, ConversationHandler, filters
)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# ⚙️  SOZLAMALAR & DIZAYN
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN", "")
CHANNEL_USERNAME = os.getenv("CHANNEL_USERNAME", "@Auezov_data")
ADMIN_USERNAME = "@Saman2611"
ADMIN_PHONE = "+998996454617"
DB_PATH = "universitet.db"

logging.basicConfig(
    format="%(asctime)s | %(levelname)s | %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Premium va chiroyli dizayn elementlari
SEP = "━" * 22
BULLET = "🔹"
SUCCESS = "✨"

YONALISHLAR_TEXT = (
    "👑 *TA'LIM YO'NALISHLARI*\n"
    f"*{SEP}*\n\n"
    "🔬 *6B05120* — Biotexnologiya\n"
    "🌍 *6B05210* — Ekologiya\n"
    "💻 *6B06120* — Axborot tizimlar\n"
    "⚙️ *6B07150* — Avtomatizatsiya va boshqaruv\n"
    "🚚 *6B07130* — Transport texnikasi\n"
    "⚡ *6B07110* — Elektroenergetika\n"
    "🧑‍🏫 *6B01310* — Pedagogika va boshlang'ich ta'lim\n"
    "🧠 *6B06121* — Sun'iy intellekt texnologiyalari\n"
    "💼 *6B04130* — Hisob va audit\n"
    "✈️ *6B11110* — Turizm\n"
    "⚖️ *6B04210* — Yurisprudensiya\n\n"
    f"*{SEP}*\n"
    "📌 _Hujjat topshirishni boshlash uchun asosiy menyudan 📝 *Hujjat topshirish* tugmasini bosing._"
)

HUJJATLAR_ROYXATI = (
    "📋 *KERAKLI HUJJATLAR RO'YXATI*\n"
    f"*{SEP}*\n\n"
    "1️⃣ 📗 Diplom yoki Attestat\n"
    "2️⃣ 🪪 Pasport nusxasi\n"
    "3️⃣ 🗂 0.86 Meditsina ma'lumotnomasi\n"
    "4️⃣ 📸 3×4 — 6 dona oq-qora rasm\n\n"
    f"*{SEP}*"
)

# Conversation states
TANLA = "tanla"
HUJJAT_FORMAT_1, HUJJAT_FORMAT_2, HUJJAT_FORMAT_3, HUJJAT_FORMAT_4 = (
    "hujjat_format_1", "hujjat_format_2", "hujjat_format_3", "hujjat_format_4"
)
HUJJAT_1, HUJJAT_2, HUJJAT_3, HUJJAT_4 = "hujjat_1", "hujjat_2", "hujjat_3", "hujjat_4"
SOROV_ISM, SOROV_FAMILYA, SOROV_YOSH, SOROV_TELEFON = (
    "sorov_ism", "sorov_familya", "sorov_yosh", "sorov_telefon"
)
YONALISH_ISM, YONALISH_FAMILYA, YONALISH_YOSH, YONALISH_TELEFON = (
    "yonalish_ism", "yonalish_familya", "yonalish_yosh", "yonalish_telefon"
)

def main_menu_markup():
    buttons = [
        ["🎓 Universitet haqida", "🗃️ Yo'nalishlar"],
        ["📝 Hujjat topshirish", "📍 Manzil"],
        ["🗂 So'rovnoma", "📋 Yo'nalish tanlash"],
        ["👤 Admin bilan bog'lanish"],
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True)

def format_tanlash_keyboard(step_num):
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("🖼️ Rasm ko'rinishida", callback_data=f"format_rasm_{step_num}"),
            InlineKeyboardButton("📎 Fayl ko'rinishida", callback_data=f"format_fayl_{step_num}"),
        ]
    ])

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🗄️  MA'LUMOTLAR BAZASI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def db_connect():
    return sqlite3.connect(DB_PATH)

def init_db():
    con = db_connect()
    cur = con.cursor()
    cur.executescript("""
        CREATE TABLE IF NOT EXISTS foydalanuvchilar (
            id            INTEGER PRIMARY KEY,
            first_name    TEXT,
            last_name     TEXT,
            user_name     TEXT,
            birinchi_vaqt TEXT
        );

        CREATE TABLE IF NOT EXISTS sorovnama (
            id            INTEGER PRIMARY KEY,
            first_name    TEXT,
            last_name     TEXT,
            user_name     TEXT,
            vaqt          TEXT,
            ism           TEXT,
            familya       TEXT,
            yosh          INTEGER,
            telefon       TEXT
        );

        CREATE TABLE IF NOT EXISTS yonalish_royxat (
            id            INTEGER PRIMARY KEY,
            first_name    TEXT,
            last_name     TEXT,
            user_name     TEXT,
            vaqt          TEXT,
            ism           TEXT,
            familya       TEXT,
            yosh          INTEGER,
            telefon       TEXT,
            yonalish      TEXT
        );
    """)
    con.commit()
    con.close()

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🚀  /start
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def start(update, context):
    user = update.message.from_user
    con = db_connect()
    cur = con.cursor()

    context.user_data.update({
        'id': user.id,
        'first_name': user.first_name or "",
        'last_name': user.last_name or "",
        'user_name': user.username or "",
    })

    cur.execute("SELECT id FROM foydalanuvchilar WHERE id=?", (user.id,))
    if not cur.fetchone():
        cur.execute(
            "INSERT INTO foydalanuvchilar VALUES (?,?,?,?,?)",
            (user.id, user.first_name, user.last_name, user.username, datetime.datetime.now())
        )
        con.commit()
        try:
            await context.bot.send_message(
                chat_id=CHANNEL_USERNAME,
                text=(
                    f"🔔 *YANGI FOYDALANUVCHI !*\nf*{SEP}*\n\n"
                    f"👤 *Ismi:* {user.first_name} {user.last_name or ''}\n"
                    f"🆔 *ID:* `{user.id}`\n"
                    f"💬 *Username:* @{user.username or 'yoq'}\n"
                    f"⏰ *Vaqt:* {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
                ),
                parse_mode="Markdown"
            )
        except Exception as e:
            logger.warning(f"Kanalga yuborishda xato: {e}")
    con.close()

    await update.message.reply_text(
        f"👋 *Assalomu alaykum, {user.first_name}!* \n\n"
        "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti* Chirchiq filialining rasmiy qabul botiga xush kelibsiz!\n\n"
        f"{BULLET} *Bu yerda siz:*\n"
        "✅ Yo'nalishlarni ko'rishingiz\n"
        "✅ Hujjatlarni onlayn topshirishingiz\n"
        "✅ Ariza va so'rovnomalarni to'ldirishingiz mumkin.\n\n"
        "👇 _Davom etish uchun quyidagi menyudan foydalaning:_",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📋  ASOSIY MENYU INTERFEYSI
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def text(update, context):
    msg = update.message.text

    if msg == "🎓 Universitet haqida":
        await update.message.reply_text(
            "🏛 *M.Auezov nomidagi Janubiy Qozog'iston universiteti*\n"
            f"*{SEP}*\n\n"
            "🔥 Chirchiq shahrida universitetning yangi zamonaviy filiali o'z ishini boshlamoqda! "
            "Xalqaro andozalarga mos ta'lim va eng kuchli professorlar sizni kutmoqda.\n\n"
            "🔗 *Batafsil ma'lumot:* [oliygoh.uz sahifasida](https://oliygoh.uz/post/chirchiqda-mauezov-nomidagi-janubiy-qozogiston-universiteti-filiali-tashkil-etiladi)",
            parse_mode="Markdown",
            disable_web_page_preview=False
        )
        return TANLA

    elif msg == "🗃️ Yo'nalishlar":
        await update.message.reply_text(YONALISHLAR_TEXT, parse_mode="Markdown")
        return TANLA

    elif msg == "📝 Hujjat topshirish":
        await update.message.reply_text(
            f"{HUJJATLAR_ROYXATI}\n\n"
            "🟢 *1-Bosqich: Diplom yoki Attestat*\n\n"
            "❓ Hujjatni qanday formatda yubormoqchisiz?",
            parse_mode="Markdown",
            reply_markup=format_tanlash_keyboard(1)
        )
        return HUJJAT_FORMAT_1

    elif msg == "📍 Manzil":
        await update.message.reply_text(
            "📍 *Bizning manzilimiz:*\n"
            f"*{SEP}*\n\n"
            "🗺 Quyidagi tugma yoki havola orqali Google Maps navigatsiyasidan foydalanishingiz mumkin:\n\n"
            "👉 https://maps.app.goo.gl/rm7LTHWLpZ7JsKmu6",
            parse_mode="Markdown"
        )
        return TANLA

    elif msg == "🗂 So'rovnoma":
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT id FROM sorovnama WHERE id=?", (update.message.from_user.id,))
        mavjud = cur.fetchone()
        con.close()
        if mavjud:
            await update.message.reply_text(
                "✨ *Siz so'rovnomani to'ldirib bo'lgansiz!*\n"
                "ℹ️ _Ma'lumotlaringiz qabul qilingan, qayta yuborish shart emas._",
                parse_mode="Markdown"
            )
            return TANLA
        await update.message.reply_text(
            "📝 *SO'ROVNOMA BOSHLANDI*\n"
            f"*{SEP}*\n\n"
            "✍️ *To'liq ismingizni kiriting:*\n_(Masalan: Abdullayev Ali)_",
            parse_mode="Markdown"
        )
        return SOROV_ISM

    elif msg == "📋 Yo'nalish tanlash":
        con = db_connect()
        cur = con.cursor()
        cur.execute("SELECT id FROM yonalish_royxat WHERE id=?", (update.message.from_user.id,))
        mavjud = cur.fetchone()
        con.close()
        if mavjud:
            await update.message.reply_text(
                "✨ *Siz yo'nalishni tanlab bo'lgansiz!*\n"
                "ℹ️ _Siz tanlagan yo'nalish muvaffaqiyatli saqlangan._",
                parse_mode="Markdown"
            )
            return TANLA
        await update.message.reply_text(
            "📋 *TA'LIM YO'NALISHINI TANLASH*\n"
            f"*{SEP}*\n\n"
            "✍️ *To'liq ismingizni kiriting:*\n_(Masalan: Rustamov Sanjar)_",
            parse_mode="Markdown"
        )
        return YONALISH_ISM

    elif msg == "👤 Admin bilan bog'lanish":
        await update.message.reply_text(
            "👤 *ALOQA VA QO'LLAB-QUVVATLASH*\n"
            f"*{SEP}*\n\n"
            f"💬 *Telegram:* {ADMIN_USERNAME}\n"
            f"📞 *Telefon:* `{ADMIN_PHONE}`\n\n"
            "⏳ *Ish vaqti:* `09:00 — 18:00` (Dushanba - Shanba)",
            parse_mode="Markdown"
        )
        return TANLA

    else:
        await update.message.reply_text(
            "❓ *Noma'lum buyruq.*\n\n"
            "Iltimos, pastdagi menyu tugmalaridan foydalaning yoki qayta /start bosing.",
            parse_mode="Markdown"
        )
        return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📤  HUJJAT FORMAT CALLBACKS
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
HUJJAT_NOMLAR = {
    1: "📗 Diplom / Attestat",
    2: "🪪 Pasport nusxasi",
    3: "🗂 0.86 Meditsina ma'lumotnomasi",
    4: "📸 3×4 oq-qora rasm (6 dona)",
}

HUJJAT_NEXT_MSG = {
    1: "2️⃣ *Pasport nusxasi*ni yuborish navbati 🪪\n\n📥 Qanday formatda yubormoqchisiz?",
    2: "3️⃣ *0.86 Meditsina ma'lumotnomasi*ni yuborish navbati 🗂\n\n📥 Qanday formatda yubormoqchisiz?",
    3: "4️⃣ *3×4 oq-qora rasm*ni yuborish navbati 📸\n\n📥 Qanday formatda yubormoqchisiz?",
}

HUJJAT_STATES = {1: HUJJAT_1, 2: HUJJAT_2, 3: HUJJAT_3, 4: HUJJAT_4}
HUJJAT_FORMAT_STATES = {1: HUJJAT_FORMAT_1, 2: HUJJAT_FORMAT_2, 3: HUJJAT_FORMAT_3, 4: HUJJAT_FORMAT_4}

async def format_callback(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    parts = data.split("_")
    format_turi = parts[1]
    step = int(parts[2])

    context.user_data[f'hujjat_format_{step}'] = format_turi

    if format_turi == "rasm":
        await query.edit_message_text(
            f"🖼️ *Tanlandi:* Rasm ko'rinishida\n\n"
            f"📥 Iltimos, *{HUJJAT_NOMLAR[step]}* rasmini (galereyadan oddiy foto qilib) yuboring:",
            parse_mode="Markdown"
        )
    else:
        await query.edit_message_text(
            f"📎 *Tanlandi:* Fayl (Document) ko'rinishida\n\n"
            f"📥 Iltimos, *{HUJJAT_NOMLAR[step]}* faylini (File ko'rinishida siqilmagan) yuboring:",
            parse_mode="Markdown"
        )

    return HUJJAT_STATES[step]

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📸🛡️  XAFVSIZLIK VA HUJJAT HANDLING PART
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def _send_to_channel(context, update, caption, step):
    user = update.message.from_user
    format_turi = context.user_data.get(f'hujjat_format_{step}', 'rasm')
    full_caption = (
        f"📂 *Yangi Hujjat tushdi!*\n"
        f"📄 *Turi:* {caption}\n"
        f"⚙️ *Kutilgan format:* {format_turi.upper()}\n"
        f"*{SEP}*\n"
        f"👤 *Abituriyent:* {user.full_name}\n"
        f"🆔 *ID:* `{user.id}`\n"
        f"⏰ *Vaqt:* {datetime.datetime.now().strftime('%d.%m.%Y %H:%M')}"
    )
    try:
        if update.message.document:
            await context.bot.send_document(
                chat_id=CHANNEL_USERNAME,
                document=update.message.document.file_id,
                caption=full_caption,
                parse_mode="Markdown"
            )
        elif update.message.photo:
            photo = update.message.photo[-1]
            if format_turi == "fayl":
                await context.bot.send_document(
                    chat_id=CHANNEL_USERNAME,
                    document=photo.file_id,
                    caption=full_caption,
                    parse_mode="Markdown"
                )
            else:
                await context.bot.send_photo(
                    chat_id=CHANNEL_USERNAME,
                    photo=photo.file_id,
                    caption=full_caption,
                    parse_mode="Markdown"
                )
    except Exception as e:
        logger.warning(f"Kanalga yuborishda xato: {e}")

async def hujjat_handler(update, context, step):
    format_turi = context.user_data.get(f'hujjat_format_{step}', 'rasm')

    # FORMAT TEKSHIRUVI: Foydalanuvchi adashib boshqa narsa yuborsa filtrlaymiz
    if format_turi == "rasm":
        if not update.message.photo:
            await update.message.reply_text(
                "⚠️ *Xatolik! Siz rasm ko'rinishida yuborishni tanlagansiz.*\n\n"
                "Iltimos, hujjatni fayl sifatida emas, *oddiy rasm (galereyadan)* ko'rinishida qayta yuklang.",
                parse_mode="Markdown"
            )
            return HUJJAT_STATES[step]
    else:  # fayl format tanlangan bo'lsa
        if not update.message.document:
            await update.message.reply_text(
                "⚠️ *Xatolik! Siz fayl (hujjat) ko'rinishida yuborishni tanlagansiz.*\n\n"
                "Iltimos, hujjatni oddiy rasm formatida emas, *fayl (document) shaklida* qayta yuklang.",
                parse_mode="Markdown"
            )
            return HUJJAT_STATES[step]

    # Agar tekshiruvdan muvaffaqiyatli o'tsa
    await _send_to_channel(context, update, HUJJAT_NOMLAR[step], step)

    if step < 4:
        next_step = step + 1
        await update.message.reply_text(
            f"{SUCCESS} *Muvaffaqiyatli qabul qilindi!*\n"
            f"*{SEP}*\n\n"
            f"{HUJJAT_NEXT_MSG[step]}",
            parse_mode="Markdown",
            reply_markup=format_tanlash_keyboard(next_step)
        )
        return HUJJAT_FORMAT_STATES[next_step]
    else:
        await update.message.reply_text(
            f"🎉 *TABRIKLAYMIZ! Barcha hujjatlar topshirildi.*\n"
            f"*{SEP}*\n\n"
            "📍 Endi hujjatlarning asl nusxasini (originalini) papkaga joylab, tez fursatda universitet binosiga olib kelishingiz so'raladi:\n\n"
            "🗺 *Google Maps locatsiya:* https://maps.app.goo.gl/rm7LTHWLpZ7JsKmu6nn"
            "✅ _Siz bilan tez orada qabul komissiyasi xodimlari bog'lanishadi!_",
            parse_mode="Markdown",
            reply_markup=main_menu_markup()
        )
        return TANLA

async def hujjat_1(update, context): return await hujjat_handler(update, context, 1)
async def hujjat_2(update, context): return await hujjat_handler(update, context, 2)
async def hujjat_3(update, context): return await hujjat_handler(update, context, 3)
async def hujjat_4(update, context): return await hujjat_handler(update, context, 4)

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 📝  SO'ROVNOMA HANDLING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def sorov_ism(update, context):
    context.user_data['sorov_ism'] = update.message.text.strip()
    await update.message.reply_text(
        "✨ *Ism saqlandi!*\n\n✍️ Endi *Familiyangizni* kiriting:",
        parse_mode="Markdown"
    )
    return SOROV_FAMILYA

async def sorov_familya(update, context):
    context.user_data['sorov_familya'] = update.message.text.strip()
    await update.message.reply_text(
        "✨ *Familiya saqlandi!*\n\n✍️ *Yoshingizni* kiriting (raqamlarda):",
        parse_mode="Markdown"
    )
    return SOROV_YOSH

async def sorov_yosh(update, context):
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            "⚠️ *Noto'g'ri yosh kiritildi!*\nIltimos, 14 dan 60 gacha bo'lgan raqam kiriting.",
            parse_mode="Markdown"
        )
        return SOROV_YOSH
    context.user_data['sorov_yosh'] = yosh
    k = [
        [KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton("🔙 Menyuga qaytish")],
    ]
    await update.message.reply_text(
        "✨ *Yosh tasdiqlandi!*\n\n📞 Pastdagi maxsus tugma orqali *Telefon raqamingizni* yuboring:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True)
    )
    return SOROV_TELEFON

async def sorov_telefon(update, context):
    telefon = update.message.contact.phone_number
    user = update.message.from_user
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO sorovnama VALUES (?,?,?,?,?,?,?,?,?)",
        (
            user.id, user.first_name or "", user.last_name or "", user.username or "",
            datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
            context.user_data.get('sorov_ism', ''),
            context.user_data.get('sorov_familya', ''),
            context.user_data.get('sorov_yosh', ''),
            telefon
        )
    )
    con.commit()
    con.close()

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=(
                f"📝 *SO'ROVNOMA TO'LDIRILDI*\nf*{SEP}*\n\n"
                f"👤 *Abituriyent:* {context.user_data.get('sorov_ism')} {context.user_data.get('sorov_familya')}\n"
                f"🎂 *Yosh:* {context.user_data.get('sorov_yosh')}\n"
                f"📞 *Telefon:* {telefon}\n"
                f"💬 *Telegram:* @{user.username or 'yoq'} (`{user.id}`)"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Kanalga xabar yuborishda xato: {e}")

    await update.message.reply_text(
        f"🎉 *So'rovnoma muvaffaqiyatli yakunlandi!*\n"
        "Ma'lumotlaringiz qabul qilindi. Endi yo'nalish tanlashingiz mumkin.",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎓  YO'NALISH TANLASH HANDLING
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def yonalish_ism(update, context):
    context.user_data['yonalish_ism'] = update.message.text.strip()
    await update.message.reply_text(
        "✨ *Ism saqlandi!*\n\n✍️ *Familiyangizni* kiriting:",
        parse_mode="Markdown"
    )
    return YONALISH_FAMILYA

async def yonalish_familya(update, context):
    context.user_data['yonalish_familya'] = update.message.text.strip()
    await update.message.reply_text(
        "✨ *Familiya saqlandi!*\n\n✍️ *Yoshingizni* kiriting:",
        parse_mode="Markdown"
    )
    return YONALISH_YOSH

async def yonalish_yosh(update, context):
    yosh = update.message.text.strip()
    if not yosh.isdigit() or not (14 <= int(yosh) <= 60):
        await update.message.reply_text(
            "⚠️ *Noto'g'ri qiymat!* Yoshni raqamda (14-60) kiriting.",
            parse_mode="Markdown"
        )
        return YONALISH_YOSH
    context.user_data['yonalish_yosh'] = yosh
    k = [
        [KeyboardButton("📞 Telefon raqamni yuborish", request_contact=True)],
        [KeyboardButton("🔙 Menyuga qaytish")],
    ]
    await update.message.reply_text(
        "✨ *Yosh tasdiqlandi!*\n\n📞 Tugmani bosib *Telefon raqamingizni* jo'nating:",
        parse_mode="Markdown",
        reply_markup=ReplyKeyboardMarkup(k, resize_keyboard=True)
    )
    return YONALISH_TELEFON

async def yonalish_telefon(update, context):
    context.user_data['yonalish_telefon'] = update.message.contact.phone_number
    yonalishlar = [
        ("🔬 6B05120 — Biotexnologiya", "Biotexnologiya"),
        ("🌍 6B05210 — Ekologiya", "Ekologiya"),
        ("💻 6B06120 — Axborot tizimlar", "Axborot_tizimlar"),
        ("⚙️ 6B07150 — Avtomatizatsiya", "Avtomatizatsiya"),
        ("🚚 6B07130 — Transport texnikasi", "Transport"),
        ("⚡ 6B07110 — Elektroenergetika", "Elektroenergetika"),
        ("🧑‍🏫 6B01310 — Pedagogika", "Pedagogika"),
        ("🧠 6B06121 — Sun'iy intellekt", "SuniyIntellekt"),
        ("💼 6B04130 — Hisob va audit", "HisobAudit"),
        ("✈️ 6B11110 — Turizm", "Turizm"),
    ]
    keyboard = [[InlineKeyboardButton(t, callback_data=cb)] for t, cb in yonalishlar]
    keyboard.append([InlineKeyboardButton("❌ Bekor qilish", callback_data="bekor")])
    await update.message.reply_text(
        f"🎓 *RO'YXATDAGI YO'NALISHLARDAN BIRINI TANLANG:*\nf*{SEP}*",
        parse_mode="Markdown",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🎛️  CALLBACK DATA DISPATCHER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
YONALISH_MAP = {
    "Biotexnologiya": "🔬 6B05120 — Biotexnologiya",
    "Ekologiya": "🌍 6B05210 — Ekologiya",
    "Axborot_tizimlar": "💻 6B06120 — Axborot tizimlar",
    "Avtomatizatsiya": "⚙️ 6B07150 — Avtomatizatsiya va boshqaruv",
    "Transport": "🚚 6B07130 — Transport texnikasi",
    "Elektroenergetika": "⚡ 6B07110 — Elektroenergetika",
    "Pedagogika": "🧑‍🏫 6B01310 — Pedagogika",
    "SuniyIntellekt": "🧠 6B06121 — Sun'iy intellekt texnologiyalari",
    "HisobAudit": "💼 6B04130 — Hisob va audit",
    "Turizm": "✈️ 6B11110 — Turizm",
}

async def callback_data(update, context):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data == "bekor":
        await query.edit_message_text("❌ *Jarayon bekor qilindi.*", parse_mode="Markdown")
        return TANLA

    yonalish = YONALISH_MAP.get(data)
    if not yonalish:
        await query.edit_message_text("⚠️ Noma'lum tanlov.", parse_mode="Markdown")
        return TANLA

    context.user_data['yonalish'] = yonalish

    kerakli = ['yonalish_ism', 'yonalish_familya', 'yonalish_yosh', 'yonalish_telefon']
    if not all(k in context.user_data for k in kerakli):
        await query.edit_message_text(
            "⚠️ *Sessiya vaqti tugadi yoki ma'lumotlar to'liq emas.*\nIltimos, qaytadan boshlang: /start",
            parse_mode="Markdown"
        )
        return TANLA

    user_id = context.user_data.get('id', query.message.chat_id)
    con = db_connect()
    cur = con.cursor()
    cur.execute(
        "INSERT OR REPLACE INTO yonalish_royxat VALUES (?,?,?,?,?,?,?,?,?,?)",
        (
            user_id,
            context.user_data.get('first_name', ''),
            context.user_data.get('last_name', ''),
            context.user_data.get('user_name', ''),
            datetime.datetime.now().strftime('%d.%m.%Y %H:%M'),
            context.user_data['yonalish_ism'],
            context.user_data['yonalish_familya'],
            context.user_data['yonalish_yosh'],
            context.user_data['yonalish_telefon'],
            yonalish
        )
    )
    con.commit()
    con.close()

    try:
        await context.bot.send_message(
            chat_id=CHANNEL_USERNAME,
            text=(
                f"🎓 *YANGI ARIZA (YO'NALISH)*\nf*{SEP}*\n\n"
                f"🎯 *Yo'nalish:* {yonalish}\n"
                f"👤 *F.I.O:* {context.user_data['yonalish_ism']} {context.user_data['yonalish_familya']}\n"
                f"🎂 *Yoshi:* {context.user_data['yonalish_yosh']}\n"
                f"📞 *Telefon:* {context.user_data['yonalish_telefon']}\n"
                f"🆔 *User ID:* `{user_id}`"
            ),
            parse_mode="Markdown"
        )
    except Exception as e:
        logger.warning(f"Kanalga xabar yuborishda xato: {e}")

    await query.edit_message_text(
        f"🎉 *Arizangiz muvaffaqiyatli ro'yxatga olindi!*\n\n"
        f"🎯 *Siz tanlagan yo'nalish:* \n`{yonalish}`\n\n"
        "📞 Tez orada mas'ul xodimlarimiz aloqaga chiqishadi.",
        parse_mode="Markdown"
    )
    await context.bot.send_message(
        chat_id=query.message.chat_id,
        text="🏠 *Asosiy menyu:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🔙  NAVIGATSIYA
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
async def menyuga_qaytish(update, context):
    await update.message.reply_text(
        "🏠 *Asosiy menyuga qaytdingiz:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

async def menyu(update, context):
    await update.message.reply_text(
        "🏠 *Asosiy menyu:*",
        parse_mode="Markdown",
        reply_markup=main_menu_markup()
    )
    return TANLA

async def tugash(update, context):
    await update.message.reply_text(
        "👋 *Suhbat yakunlandi.* Qayta boshlash uchun /start yuboring.",
        parse_mode="Markdown"
    )
    return ConversationHandler.END

# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
# 🤖  MAIN RUNNER
# ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
def main():
    if not BOT_TOKEN:
        raise ValueError("❌ BOT_TOKEN xatoligi! .env faylini ochib tokeningizni kiriting.")

    init_db()

    app = Application.builder().token(BOT_TOKEN).build()

    back_filter = filters.Regex("^🔙 Menyuga qaytish$")
    media_filter = filters.PHOTO | filters.Document.ALL

    conv = ConversationHandler(
        entry_points=[CommandHandler('start', start)],
        states={
            TANLA: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, text),
                CallbackQueryHandler(callback_data)
            ],

            HUJJAT_FORMAT_1: [
                MessageHandler(back_filter, menyuga_qaytish),
                CallbackQueryHandler(format_callback)
            ],
            HUJJAT_FORMAT_2: [
                MessageHandler(back_filter, menyuga_qaytish),
                CallbackQueryHandler(format_callback)
            ],
            HUJJAT_FORMAT_3: [
                MessageHandler(back_filter, menyuga_qaytish),
                CallbackQueryHandler(format_callback)
            ],
            HUJJAT_FORMAT_4: [
                MessageHandler(back_filter, menyuga_qaytish),
                CallbackQueryHandler(format_callback)
            ],

            HUJJAT_1: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(media_filter | (filters.TEXT & ~filters.COMMAND), hujjat_1),
            ],
            HUJJAT_2: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(media_filter | (filters.TEXT & ~filters.COMMAND), hujjat_2),
            ],
            HUJJAT_3: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(media_filter | (filters.TEXT & ~filters.COMMAND), hujjat_3),
            ],
            HUJJAT_4: [
                MessageHandler(back_filter, menyuga_qaytish),
                MessageHandler(media_filter | (filters.TEXT & ~filters.COMMAND), hujjat_4),
            ],

            SOROV_ISM:     [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_ism)],
            SOROV_FAMILYA: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_familya)],
            SOROV_YOSH:    [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.TEXT & ~filters.COMMAND, sorov_yosh)],
            SOROV_TELEFON: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.CONTACT, sorov_telefon)],

            YONALISH_ISM:     [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_ism)],
            YONALISH_FAMILYA: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_familya)],
            YONALISH_YOSH:    [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.TEXT & ~filters.COMMAND, yonalish_yosh)],
            YONALISH_TELEFON: [MessageHandler(back_filter, menyuga_qaytish), MessageHandler(filters.CONTACT, yonalish_telefon)],
        },
        fallbacks=[
            CommandHandler('tugash', tugash),
            CommandHandler('menyu', menyu),
            CommandHandler('start', start),
            MessageHandler(back_filter, menyuga_qaytish),
        ]
    )

    app.add_handler(conv)

    logger.info("🚀 Bot updated with new UI and strict validation. Polling started...")
    app.run_polling()

if __name__ == '__main__':
    main()
