import time
import json
import telebot

# توكنات وإعدادات البوت
TOKEN = "TON"  # استبدل باسم العملة التي تستخدمها
BOT_TOKEN = "7502491167:AAHzJCYyIsrfah-JvM16iJP4i-8vz6OO9Rk"
PAYMENT_CHANNEL = "@TONixshift_bot"  # قناة الدفع
OWNER_ID = 1725235943  # معرف مالك البوت
CHANNELS = ["@TONixshift_bot"]  # القنوات التي يجب الانضمام إليها
DAILY_BONUS = 1  # مكافأة يومية
MINI_WITHDRAW = 0.5  # الحد الأدنى للسحب
PER_REFER = 0.0001  # مكافأة الإحالة

bot = telebot.TeleBot(BOT_TOKEN)

# دالة للتحقق مما إذا كان المستخدم قد انضم إلى القنوات المطلوبة
def check(id):
    for channel in CHANNELS:
        check = bot.get_chat_member(channel, id)
        if check.status == 'left':
            return False
    return True

bonus = {}  # لتخزين معلومات المكافآت اليومية

# دالة لعرض قائمة الخيارات الرئيسية
def menu(user_id):
    keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
    keyboard.row('🆔 Account')
    keyboard.row('🙌🏻 Referrals', '🎁 Bonus', '💸 Withdraw')
    keyboard.row('⚙️ Set Wallet', '📊 Statistics')
    bot.send_message(user_id, "*🏡 Home*", parse_mode="Markdown", reply_markup=keyboard)

# دالة التعامل مع الأمر /start
@bot.message_handler(commands=['start'])
def start(message):
    user_id = str(message.chat.id)
    try:
        data = json.load(open('users.json', 'r'))

        # إضافة مستخدم جديد إلى قاعدة البيانات إذا لم يكن موجودًا
        if user_id not in data['referred']:
            data['referred'][user_id] = 0
            data['total'] += 1
        
        # إضافة معلومات المستخدم
        for key in ['referby', 'checkin', 'DailyQuiz', 'balance', 'wallet', 'withd', 'id']:
            if user_id not in data[key]:
                data[key][user_id] = 0 if key != 'wallet' else "none"
        
        # حفظ البيانات
        json.dump(data, open('users.json', 'w'))

        # إعداد الرسالة والترحيب
        markup = telebot.types.InlineKeyboardMarkup()
        markup.add(telebot.types.InlineKeyboardButton(text='🤼‍♂️ Joined', callback_data='check'))
        
        msg_start = "*🍔 To Use This Bot You Need To Join This Channel - " + "\n➡️ ".join(CHANNELS) + "*"
        bot.send_message(user_id, msg_start, parse_mode="Markdown", reply_markup=markup)

    except Exception as e:
        bot.send_message(message.chat.id, "حدث خطأ أثناء معالجة الأمر، يرجى الانتظار حتى يتم إصلاح المشكلة.")
        bot.send_message(OWNER_ID, f"حدث خطأ في البوت: {str(e)}")

# دالة للتعامل مع ردود الاستعلامات
@bot.callback_query_handler(func=lambda call: True)
def query_handler(call):
    try:
        if call.data == 'check':
            if check(call.message.chat.id):
                data = json.load(open('users.json', 'r'))
                user_id = str(call.message.chat.id)

                # إضافة معلومات الإحالة
                if user_id not in data['refer']:
                    data['refer'][user_id] = True
                    data['referby'][user_id] = user_id
                    json.dump(data, open('users.json', 'w'))

                bot.answer_callback_query(call.id, text='✅ You joined! Now you can earn money.')
                bot.delete_message(call.message.chat.id, call.message.message_id)
                return menu(call.message.chat.id)
            else:
                bot.answer_callback_query(call.id, text='❌ You have not joined the required channels.')
                return

    except Exception as e:
        bot.send_message(call.message.chat.id, "حدث خطأ أثناء معالجة الأمر، يرجى الانتظار حتى يتم إصلاح المشكلة.")
        bot.send_message(OWNER_ID, f"حدث خطأ في البوت: {str(e)}")

# دالة لمعالجة الرسائل النصية
@bot.message_handler(content_types=['text'])
def send_text(message):
    try:
        user_id = str(message.chat.id)
        data = json.load(open('users.json', 'r'))

        if message.text == '🆔 Account':
            accmsg = '*👮 User : {}\n\n⚙️ Wallet : *`{}`*\n\n💸 Balance : *`{}`* {}*'
            wallet = data['wallet'].get(user_id, "none")
            balance = data['balance'].get(user_id, 0)
            msg = accmsg.format(message.from_user.first_name, wallet, balance, TOKEN)
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")

        elif message.text == '🙌🏻 Referrals':
            ref_msg = "*⏯️ Total Invites : {} Users\n\n👥 Refferrals System\n\n1 Level:\n🥇 Level°1 - {} {}\n\n🔗 Referral Link ⬇️\n{}*"
            bot_name = bot.get_me().username
            ref_count = data['referred'].get(user_id, 0)
            ref_link = f'https://telegram.me/{bot_name}?start={user_id}'
            msg = ref_msg.format(ref_count, PER_REFER, TOKEN, ref_link)
            bot.send_message(message.chat.id, msg, parse_mode="Markdown")

        elif message.text == "⚙️ Set Wallet":
            keyboard = telebot.types.ReplyKeyboardMarkup(resize_keyboard=True)
            keyboard.row('🚫 Cancel')
            send = bot.send_message(message.chat.id, "_⚠️Send your TRX Wallet Address._", parse_mode="Markdown", reply_markup=keyboard)
            bot.register_next_step_handler(message, trx_address)

        elif message.text == "🎁 Bonus":
            cur_time = int(time.time())
            if (user_id not in bonus) or (cur_time - bonus[user_id] > 60*60*24):
                data['balance'][user_id] += DAILY_BONUS
                bot.send_message(user_id, f"Congrats! You just received {DAILY_BONUS} {TOKEN}")
                bonus[user_id] = cur_time
                json.dump(data, open('users.json', 'w'))
            else:
                bot.send_message(message.chat.id, "❌*You can only take bonus once every 24 hours!*", parse_mode="Markdown")

        elif message.text == "📊 Statistics":
            msg = "*📊 Total members : {} Users\n\n🥊 Total successful Withdraw : {} {}*"
            msg = msg.format(data['total'], data.get('totalwith', 0), TOKEN)
            bot.send_message(user_id, msg, parse_mode="Markdown")

        elif message.text == "💸 Withdraw":
            wall = data['wallet'].get(user_id, "none")
            if wall == "none":
                bot.send_message(user_id, "_❌ wallet Not set_", parse_mode="Markdown")
                return
            bal = data['balance'].get(user_id, 0)
            if bal >= MINI_WITHDRAW:
                bot.send_message(user_id, "_Enter Your Amount_", parse_mode="Markdown")
                bot.register_next_step_handler(message, amo_with)
            else:
                bot.send_message(user_id, f"_❌ Your balance low, you should have at least {MINI_WITHDRAW} {TOKEN} to Withdraw_", parse_mode="Markdown")

    except Exception as e:
        bot.send_message(message.chat.id, "حدث خطأ أثناء معالجة الأمر، يرجى الانتظار حتى يتم إصلاح المشكلة.")
        bot.send_message(OWNER_ID, f"حدث خطأ في البوت: {str(e)}")

# دالة لتحديث عنوان المحفظة
def trx_address(message):
    user_id = str(message.chat.id)
    data = json.load(open('users.json', 'r'))
    
    if message.text == "🚫 Cancel":
        return menu(message.chat.id)
    
    if len(message.text) == 34:
        data['wallet'][user_id] = message.text
        bot.send_message(message.chat.id, f"*💹 Your TRX wallet set to {data['wallet'][user_id]}*", parse_mode="Markdown")
        json.dump(data, open('users.json', 'w'))
        return menu(message.chat.id)
    else:
        bot.send_message(message.chat.id, "*⚠️ It's Not a Valid TRX Address!*", parse_mode="Markdown")
        return menu(message.chat.id)

# دالة لمعالجة طلبات السحب
def amo_with(message):
    user_id = str(message.chat.id)
    amo = message.text
    data = json.load(open('users.json', 'r'))
    
    if not amo.isdigit():
        bot.send_message(user_id, "_📛 Invalid value. Enter only numeric value. Try again_", parse_mode="Markdown")
        return
    
    bal = data['balance'].get(user_id, 0)
    if int(amo) < MINI_WITHDRAW:
        bot.send_message(user_id, f"_❌ Minimum withdraw {MINI_WITHDRAW} {TOKEN}._", parse_mode="Markdown")
        return
    
    if bal >= int(amo):
        # تنفيذ عملية السحب
        data['balance'][user_id] -= int(amo)
        bot.send_message(user_id, f"*✔ Withdraw {amo} {TOKEN} process initiated. Check your wallet soon.*", parse_mode="Markdown")
        json.dump(data, open('users.json', 'w'))
    else:
        bot.send_message(user_id, "_❌ You don't have enough balance._", parse_mode="Markdown")

# بدء تشغيل البوت
bot.polling()
