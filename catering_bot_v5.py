import telebot
import random
from telebot.types import (
    ReplyKeyboardMarkup, KeyboardButton,
    InlineKeyboardMarkup, InlineKeyboardButton
)

# ══════════════════════════════════════════════
#  🔑 ТАНЗИМОТ
# ══════════════════════════════════════════════
API_TOKEN        = "8737402890:AAHTsnXVfJVbYlMVUCMWgFHkWmTTwsPxbpc"
ADMIN_ID         = 7411414635
CARD_NUMBER      = "4439 2000 2793 1202"
CARD_NAME        = "Shukhrat Zainulloev"
PRICE_PER_PERSON = 100

bot = telebot.TeleBot(API_TOKEN)

user_data          = {}  # Фармоишҳои нопурра  {uid: {...}}
orders             = {}  # Фармоишҳои тасдиқшуда {order_id: {...}}
pending_screenshot = {}  # Интизори скриншот   {uid: order_id}

# ══════════════════════════════════════════════
#  ⌨️  КЛАВИАТУРАҲО
# ══════════════════════════════════════════════
def main_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🍽 Меню"),
        KeyboardButton("💰 Цены"),
        KeyboardButton("📝 Заказать"),
        KeyboardButton("📞 Контакты"),
    )
    return kb

def food_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    kb.add(
        KeyboardButton("🍚 Плов"),
        KeyboardButton("🍢 Шашлык"),
        KeyboardButton("🥟 Самса"),
        KeyboardButton("🥗 Салаты"),
    )
    kb.add(KeyboardButton("❌ Отмена"))
    return kb

def cancel_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("❌ Отмена"))
    return kb

def phone_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📱 Поделиться номером", request_contact=True))
    kb.add(KeyboardButton("❌ Отмена"))
    return kb

def location_kb():
    kb = ReplyKeyboardMarkup(resize_keyboard=True)
    kb.add(KeyboardButton("📍 Отправить местоположение", request_location=True))
    kb.add(KeyboardButton("✏️ Ввести адрес вручную"))
    kb.add(KeyboardButton("❌ Отмена"))
    return kb

def admin_confirm_kb(order_id, user_id):
    """Тугмаҳои админ: Қабул / Рад"""
    kb = InlineKeyboardMarkup(row_width=2)
    kb.add(
        InlineKeyboardButton("✅ Қабул кардам", callback_data=f"ok:{order_id}:{user_id}"),
        InlineKeyboardButton("❌ Рад кардам",   callback_data=f"no:{order_id}:{user_id}"),
    )
    return kb

# ══════════════════════════════════════════════
#  📦 ФУНКСИЯИ ФИНАЛИ ФАРМОИШ
# ══════════════════════════════════════════════
def _finish_order(m, phone):
    uid = m.chat.id
    user_data[uid]['phone'] = phone

    order_id = random.randint(1000, 9999)
    d = user_data[uid]
    orders[order_id] = {**d, 'uid': uid, 'status': 'pending'}

    user  = m.from_user
    uname = f"@{user.username}" if user.username else "–"

    # ── Огоҳӣ ба АДМИН ──
    admin_msg = (
        f"🔔 <b>ФАРМОИШИ НАВ #{order_id}</b>\n\n"
        f"👤 Муштарӣ: <b>{user.full_name}</b>\n"
        f"📱 Username: {uname}\n"
        f"🆔 ID: <code>{uid}</code>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🍽 Таом:    <b>{d['food']}</b>\n"
        f"👥 Нафар:   <b>{d['people']} нафар</b>\n"
        f"📅 Сана:    <b>{d['date']}</b>\n"
        f"📍 Манзил:  <b>{d['address']}</b>\n"
        f"📞 Телефон: <b>{d['phone']}</b>\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 <b>МАБЛАҒ: {d['total']} сомонӣ</b>\n\n"
        f"⏳ Интизори скриншоти пардохт..."
    )
    try:
        bot.send_message(ADMIN_ID, admin_msg, parse_mode="HTML")
        if 'location' in d:
            bot.send_location(ADMIN_ID, d['location'][0], d['location'][1])
    except Exception as e:
        print(f"Хато ба админ: {e}")

    # ── Паём ба МУШТАРӢ ──
    bot.send_message(
        uid,
        f"🎉 <b>ФАРМОИШ #{order_id} ҚАБУЛ ШУД!</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"🍽 {d['food']} × {d['people']} нафар\n"
        f"📅 Сана: {d['date']}\n"
        f"📍 Манзил: {d['address']}\n"
        f"📞 Телефон: {d['phone']}\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💰 Маблағ: <b>{d['total']} сомонӣ</b>\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"💳 <b>РАҚАМИ КАРТА:</b>\n"
        f"<code>{CARD_NUMBER}</code>\n"
        f"👤 {CARD_NAME}\n\n"
        f"━━━━━━━━━━━━━━━\n"
        f"📸 Пул фиристед ва <b>скриншоти чекро ба ин ҷо фиристед</b>\n"
        f"Мо фавран тасдиқ мекунем! ✅",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

    # Муштариро дар рӯйхати интизори скриншот мегузорем
    pending_screenshot[uid] = order_id
    del user_data[uid]

# ══════════════════════════════════════════════
#  📸 СКРИНШОТ — МУШТАРӢ РАСМ МЕФИРИСТАД
# ══════════════════════════════════════════════
@bot.message_handler(content_types=['photo'])
def handle_screenshot(m):
    uid   = m.chat.id
    user  = m.from_user
    uname = f"@{user.username}" if user.username else "–"

    # Рақами фармоишро муайян мекунем
    if uid in pending_screenshot:
        order_id = pending_screenshot[uid]
        order_text = f"🔔 Фармоиш: <b>#{order_id}</b>\n"
    else:
        order_text = "🔔 Фармоиш: <b>номаълум</b>\n"
        order_id   = 0

    # ── Скриншотро ҲАМЕША ба АДМИН фиристед ──
    caption = (
        f"📸 <b>СКРИНШОТИ ПАРДОХТ</b>\n\n"
        f"{order_text}"
        f"👤 Муштарӣ: <b>{user.full_name}</b>\n"
        f"📱 {uname}\n"
        f"🆔 ID: <code>{uid}</code>\n\n"
        f"👇 Пардохтро санҷед ва қарор қабул кунед:"
    )
    try:
        bot.send_photo(
            ADMIN_ID,
            m.photo[-1].file_id,
            caption=caption,
            parse_mode="HTML",
            reply_markup=admin_confirm_kb(order_id, uid)
        )
        # Муштарӣ ба интизор монад
        bot.send_message(
            uid,
            "⏳ <b>Скриншоти шумо ба администратор фиристода шуд!</b>\n\n"
            "Мо дар тӯли 5–10 дақиқа тасдиқ мекунем.\n"
            "📞 Савол: +992 123 456 789",
            parse_mode="HTML",
            reply_markup=main_kb()
        )
    except Exception as e:
        print(f"Хато скриншот: {e}")
        bot.send_message(uid, "❗ Хато рӯй дод. Лутфан дубора фиристед.")

    # Аз рӯйхати интизор хориҷ кун
    pending_screenshot.pop(uid, None)

# ══════════════════════════════════════════════
#  👨‍💼 АДМИН: ✅ Қабул / ❌ Рад
# ══════════════════════════════════════════════
@bot.callback_query_handler(func=lambda c: c.data.startswith("ok:") or c.data.startswith("no:"))
def admin_decision(call):
    parts    = call.data.split(":")
    action   = parts[0]
    order_id = int(parts[1])
    user_id  = int(parts[2])

    # Тугмаҳоро аз паёми админ хориҷ кун
    bot.edit_message_reply_markup(call.message.chat.id, call.message.message_id)

    if action == "ok":
        # Ба муштарӣ хабари хуш
        try:
            bot.send_message(
                user_id,
                f"✅ <b>ПАРДОХТИ ФАРМОИШ #{order_id} ТАСДИҚ ШУД!</b>\n\n"
                f"🎊 Ташаккур барои фармоиш!\n"
                f"🚚 Мо фармоишатонро омода мекунем.\n\n"
                f"📞 Савол бошад: +992 123 456 789",
                parse_mode="HTML",
                reply_markup=main_kb()
            )
        except Exception as e:
            print(f"Хато ба муштарӣ: {e}")

        bot.answer_callback_query(call.id, "✅ Пардохт тасдиқ шуд!")
        bot.send_message(ADMIN_ID,
            f"✅ Фармоиш #{order_id} — <b>ҚАБУЛ ШУД</b>",
            parse_mode="HTML"
        )

    elif action == "no":
        # Ба муштарӣ хабари рад
        try:
            bot.send_message(
                user_id,
                f"❌ <b>Фармоиш #{order_id} рад шуд.</b>\n\n"
                f"Пардохт тасдиқ нашуд.\n"
                f"📞 Барои маълумот: +992 123 456 789",
                parse_mode="HTML",
                reply_markup=main_kb()
            )
        except Exception as e:
            print(f"Хато ба муштарӣ: {e}")

        bot.answer_callback_query(call.id, "❌ Рад шуд.")
        bot.send_message(ADMIN_ID,
            f"❌ Фармоиш #{order_id} — <b>РАД ШУД</b>",
            parse_mode="HTML"
        )

# ══════════════════════════════════════════════
#  /start
# ══════════════════════════════════════════════
@bot.message_handler(commands=['start'])
def start(msg):
    user_data.pop(msg.chat.id, None)
    name = msg.from_user.first_name or "дӯст"
    bot.send_message(
        msg.chat.id,
        f"👋 Салом, <b>{name}</b>!\n\n"
        "🍽 Хуш омадед ба <b>Catering Service</b>!\n\n"
        "Мо барои мероприятияи шумо:\n"
        "   🎊 Тӯйҳо ва зиёфатҳо\n"
        "   💼 Корпоративҳо\n"
        "   🎂 Таваллудҳо\n\n"
        "Чиро интихоб мекунед? 👇",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

# ══════════════════════════════════════════════
#  МЕНЮИ АСОСӢ
# ══════════════════════════════════════════════
@bot.message_handler(func=lambda m: m.text == "🍽 Меню")
def show_menu(m):
    bot.send_message(
        m.chat.id,
        "📋 <b>Менюи мо:</b>\n\n"
        "🍚 <b>Плов</b> — 100 сомонӣ/нафар\n"
        "   Классикии ӯзбекӣ бо гӯшти гӯсфанд\n\n"
        "🍢 <b>Шашлык</b> — 100 сомонӣ/нафар\n"
        "   Гӯшти тару тоза дар оташ\n\n"
        "🥟 <b>Самса</b> — 100 сомонӣ/нафар\n"
        "   Аз танӯр, тару тоза\n\n"
        "🥗 <b>Салаты</b> — 100 сомонӣ/нафар\n"
        "   3 навъи салати тоза\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📦 Зарфу кошуқ — <b>ройгон</b>\n"
        "🚚 Расондан — <b>ройгон</b>",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

@bot.message_handler(func=lambda m: m.text == "💰 Цены")
def show_prices(m):
    bot.send_message(
        m.chat.id,
        "💰 <b>Прайс-лист:</b>\n\n"
        "   👤 1 нафар  — <b>100 сомонӣ</b>\n"
        "   👥 10 нафар — <b>1 000 сомонӣ</b>\n"
        "   👨‍👩‍👧‍👦 20 нафар — <b>2 000 сомонӣ</b>\n"
        "   🏟 50 нафар — <b>5 000 сомонӣ</b>\n\n"
        "📌 Ҳадди ақал — <b>2 нафар</b>\n"
        "🎁 Зарфу кошуқ — <b>ройгон</b>\n"
        "🚚 Расондан — <b>ройгон</b>",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

@bot.message_handler(func=lambda m: m.text == "📞 Контакты")
def show_contacts(m):
    bot.send_message(
        m.chat.id,
        "📞 <b>Тамос бо мо:</b>\n\n"
        "📱 Телефон: <b>+992 123 456 789</b>\n"
        "💬 WhatsApp: <b>+992 123 456 789</b>\n"
        "📍 Шаҳр: <b>Душанбе</b>\n"
        "🕐 Кор: <b>08:00 – 22:00</b>",
        parse_mode="HTML",
        reply_markup=main_kb()
    )

@bot.message_handler(func=lambda m: m.text == "📝 Заказать")
def order_start(m):
    user_data[m.chat.id] = {'step': 1}
    bot.send_message(
        m.chat.id,
        "🛒 <b>Оформлении фармоиш</b>\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📍 Шаг <b>1</b> аз 5 — Таомро интихоб кунед 👇",
        parse_mode="HTML",
        reply_markup=food_kb()
    )

# ══════════════════════════════════════════════
#  📱 CONTACT — АЛОҲИДА HANDLER
# ══════════════════════════════════════════════
@bot.message_handler(content_types=['contact'])
def handle_contact(m):
    uid = m.chat.id
    if uid not in user_data or user_data[uid].get('step') != 5:
        bot.send_message(uid, "⚠️ Аввал фармоишро оғоз кунед: 📝 Заказать",
                         reply_markup=main_kb())
        return
    phone = m.contact.phone_number
    if not phone.startswith("+"):
        phone = "+" + phone
    _finish_order(m, phone)

# ══════════════════════════════════════════════
#  📍 LOCATION — АЛОҲИДА HANDLER
# ══════════════════════════════════════════════
@bot.message_handler(content_types=['location'])
def handle_location(m):
    uid = m.chat.id
    if uid not in user_data or user_data[uid].get('step') != 4:
        return
    lat = m.location.latitude
    lon = m.location.longitude
    user_data[uid]['address']  = f"📍 GPS: {lat:.5f}, {lon:.5f}"
    user_data[uid]['location'] = (lat, lon)
    user_data[uid]['step']     = 5
    bot.send_message(
        uid,
        "✅ Мавқеъ қабул шуд!\n\n"
        "━━━━━━━━━━━━━━━\n"
        "📍 Шаг <b>5</b> аз 5 — Рақами телефони шумо?\n\n"
        "Тугмаро пахш кунед ё дастӣ нависед:",
        parse_mode="HTML",
        reply_markup=phone_kb()
    )

# ══════════════════════════════════════════════
#  🔄 HANDLER БАРОИ МАТН (қадамҳо 1–5)
# ══════════════════════════════════════════════
@bot.message_handler(
    content_types=['text'],
    func=lambda m: m.chat.id in user_data
)
def handle_steps(m):
    uid  = m.chat.id
    step = user_data[uid].get('step', 0)

    if m.text == "❌ Отмена":
        del user_data[uid]
        bot.send_message(uid, "❌ Фармоиш бекор шуд.", reply_markup=main_kb())
        return

    # ШАГ 1: Таом
    if step == 1:
        foods = ["🍚 Плов", "🍢 Шашлык", "🥟 Самса", "🥗 Салаты"]
        if m.text not in foods:
            bot.send_message(uid, "⚠️ Лутфан аз рӯйхат интихоб кунед 👆")
            return
        user_data[uid]['food'] = m.text
        user_data[uid]['step'] = 2
        bot.send_message(
            uid,
            f"✅ <b>{m.text}</b> интихоб шуд!\n\n"
            "━━━━━━━━━━━━━━━\n"
            "📍 Шаг <b>2</b> аз 5 — Шумораи меҳмонон?\n\n"
            "🔢 Рақамро нависед (ҳадди ақал 2):",
            parse_mode="HTML",
            reply_markup=cancel_kb()
        )

    # ШАГ 2: Шумора
    elif step == 2:
        if not m.text.isdigit():
            bot.send_message(uid, "⚠️ Рақам ворид кунед (масалан: 15)")
            return
        people = int(m.text)
        if people < 2:
            bot.send_message(uid, "⚠️ Ҳадди ақал 2 нафар!")
            return
        total = people * PRICE_PER_PERSON
        user_data[uid]['people'] = people
        user_data[uid]['total']  = total
        user_data[uid]['step']   = 3
        bot.send_message(
            uid,
            f"✅ <b>{people} нафар</b>\n"
            f"💰 Маблағ: <b>{total} сомонӣ</b>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "📍 Шаг <b>3</b> аз 5 — Санаи чорабинӣ?\n\n"
            "📅 Нависед (масалан: 20.07.2025):",
            parse_mode="HTML",
            reply_markup=cancel_kb()
        )

    # ШАГ 3: Сана
    elif step == 3:
        if len(m.text.strip()) < 3:
            bot.send_message(uid, "⚠️ Санаро муфассалтар нависед")
            return
        user_data[uid]['date'] = m.text.strip()
        user_data[uid]['step'] = 4
        bot.send_message(
            uid,
            f"✅ Сана: <b>{m.text.strip()}</b>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "📍 Шаг <b>4</b> аз 5 — Манзили расондан\n\n"
            "Мавқеи худро фиристед ё дастӣ нависед 👇",
            parse_mode="HTML",
            reply_markup=location_kb()
        )

    # ШАГ 4: Манзили матнӣ
    elif step == 4:
        if m.text == "✏️ Ввести адрес вручную":
            bot.send_message(uid,
                "✏️ Манзилро нависед:\n(масалан: Душанбе, кӯчаи Рӯдакӣ, 100)",
                reply_markup=cancel_kb()
            )
            return
        if len(m.text.strip()) < 5:
            bot.send_message(uid, "⚠️ Манзилро пурратар нависед")
            return
        user_data[uid]['address'] = m.text.strip()
        user_data[uid]['step']    = 5
        bot.send_message(
            uid,
            f"✅ Манзил: <b>{m.text.strip()}</b>\n\n"
            "━━━━━━━━━━━━━━━\n"
            "📍 Шаг <b>5</b> аз 5 — Рақами телефони шумо?\n\n"
            "Тугмаро пахш кунед ё дастӣ нависед:",
            parse_mode="HTML",
            reply_markup=phone_kb()
        )

    # ШАГ 5: Телефони матнӣ
    elif step == 5:
        digits = [c for c in m.text if c.isdigit()]
        if len(digits) < 7:
            bot.send_message(uid,
                "⚠️ Рақами телефонро дуруст нависед\n"
                "(масалан: +992 900 123 456)\n\n"
                "Ё тугмаи 📱 зеринро пахш кунед:",
                reply_markup=phone_kb()
            )
            return
        _finish_order(m, m.text.strip())

# ══════════════════════════════════════════════
#  ПАЁМҲОИ ДИГАР
# ══════════════════════════════════════════════
@bot.message_handler(func=lambda m: True, content_types=['text'])
def unknown(m):
    bot.send_message(m.chat.id, "🤖 Тугмаҳоро истифода баред 👇",
                     reply_markup=main_kb())

# ══════════════════════════════════════════════
print("✅ БОТ ЗАПУЩЕН!")
bot.infinity_polling()
