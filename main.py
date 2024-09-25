# دالة للتحقق مما إذا كان المستخدم قد انضم إلى القنوات المطلوبة
def check(id):
    for channel in CHANNELS:
        try:
            check = bot.get_chat_member(channel, id)
            if check.status == 'left':
                return False
        except Exception as e:
            bot.send_message(OWNER_ID, f"Error checking membership for user {id} in channel {channel}: {str(e)}")
            return False  # في حالة حدوث خطأ، نعتبر أنه لم ينضم للقناة
    return True

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
