import csv
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Survey data
survey = [
    {
        "question": "Что ты чувствуешь, когда тебя хвалят за твою работу?",
        "answers": [
            {"text": "Чувствую, что похвала заслуженная", "score": 2},
            {"text": "Приятно, но не фокусируюсь на этом", "score": 4},
            {"text": "Немного неловко, потому что мог(ла) бы сделать лучше", "score": 6},
            {"text": "Думаю, что люди просто вежливые и не говорят правду", "score": 8},
            {"text": "Ощущаю, что меня переоценивают", "score": 10},
            {"text": "test", "score": 20}
        ]
    },
    {
        "question": "Как ты относишься к своим успехам?",
        "answers": [
            {"text": "Чувствую, что мои достижения – результат моих усилий и навыков", "score": 2},
            {"text": "Иногда думаю, что успех связан с удачей", "score": 4},
            {"text": "Стараюсь не придавать им большого значения", "score": 6},
            {"text": "Думаю, что просто оказался(ась) в нужное время в нужном месте", "score": 8},
            {"text": "Ощущаю, что я просто хорошо маскируюсь, и скоро это вскроется", "score": 10}
        ]
    },
    {
        "question": "Как ты реагируешь, когда кто-то просит тебя поделиться своим опытом?",
        "answers": [
            {"text": "Охотно делюсь, ведь знаю, что у меня есть полезный опыт", "score": 2},
            {"text": "Иногда делюсь, но чувствую, что есть люди, знающие больше", "score": 4},
            {"text": "Сомневаюсь, стоит ли мне делиться, вдруг скажу что-то не так", "score": 6},
            {"text": "Думаю, что недостаточно компетентен(на) и мне ещё рано", "score": 8},
            {"text": "Отказываюсь, потому что не хочу, чтобы узнали, что я «не эксперт»", "score": 10}
        ]
    },
    {
        "question": "Когда ты начинаешь новый проект или работу, что ты чувствуешь?",
        "answers": [
            {"text": "Волнение, но я уверен(а) в своих силах", "score": 2},
            {"text": "Иногда сомневаюсь, но всё равно двигаюсь вперёд", "score": 4},
            {"text": "Откладываю старт, потому что боюсь, что не справлюсь", "score": 6},
            {"text": "Думаю, что мне нужно ещё подготовиться, прежде чем начать", "score": 8},
            {"text": "Прокрастинирую и откладываю, потому что боюсь провала", "score": 10}
        ]
    },
    {
        "question": "Как ты относишься к ошибкам?",
        "answers": [
            {"text": "Воспринимаю их как опыт и уроки", "score": 2},
            {"text": "Иногда переживаю, но знаю, что это часть пути", "score": 4},
            {"text": "Испытываю сильное разочарование, даже если ошибка небольшая", "score": 6},
            {"text": "Думаю, что из-за ошибки люди поймут, что я недостаточно хорош(а)", "score": 8},
            {"text": "Ощущаю, что ошибки доказывают, что я вообще некомпетентен(на)", "score": 10}
        ]
    },
    {
        "question": "Как ты реагируешь на успехи коллег/конкурентов?",
        "answers": [
            {"text": "Радуюсь за них, это мотивирует меня развиваться", "score": 2},
            {"text": "Думаю, что мне нужно ещё больше стараться", "score": 4},
            {"text": "Сравниваю себя и чувствую, что отстаю", "score": 6},
            {"text": "Думаю, что мне никогда не достичь их уровня", "score": 8},
            {"text": "Ощущаю, что я вообще не в их лиге и не имею права себя с ними сравнивать", "score": 10}
        ]
    },
    {
        "question": "Как ты принимаешь решения?",
        "answers": [
            {"text": "Делаю выводы и действую", "score": 2},
            {"text": "Иногда сомневаюсь, но не откладываю надолго", "score": 4},
            {"text": "Долго думаю и откладываю решение", "score": 6},
            {"text": "Собираю максимум информации, но всё равно сомневаюсь", "score": 8},
            {"text": "Откладываю до последнего, потому что боюсь ошибиться", "score": 10}
        ]
    },
    {
        "question": "Как ты относишься к своему уровню знаний?",
        "answers": [
            {"text": "Я знаю достаточно, чтобы работать в своей сфере", "score": 2},
            {"text": "Иногда мне кажется, что мне нужно ещё немного поучиться", "score": 4},
            {"text": "Думаю, что мой уровень недостаточно высок", "score": 6},
            {"text": "Мне кажется, что я вообще ничего не знаю, в отличие от других", "score": 8},
            {"text": "Уверен(а), что мне ещё рано начинать, надо доучиться", "score": 10}
        ]
    },
    {
        "question": "Что ты чувствуешь, когда тебе дают сложное задание?",
        "answers": [
            {"text": "Уверенность, что справлюсь", "score": 2},
            {"text": "Немного волнения, но понимаю, что разберусь", "score": 4},
            {"text": "Сомневаюсь, справлюсь ли", "score": 6},
            {"text": "Думаю, что меня переоценили и я не вытяну", "score": 8},
            {"text": "Хочу отказаться, потому что боюсь провала", "score": 10}
        ]
    },
    {
        "question": "Если бы ты мог(ла) избавиться от синдрома самозванца, что бы изменилось в твоей жизни?",
        "answers": [
            {"text": "Я бы продолжил(а) работать, как и сейчас, но с большим удовольствием", "score": 2},
            {"text": "Я бы перестал(а) бояться говорить о своих достижениях", "score": 4},
            {"text": "Я бы смог(ла) уверенно брать клиентов", "score": 6},
            {"text": "Я бы начал(а) действовать, а не сомневаться", "score": 8},
            {"text": "Моя жизнь изменилась бы полностью, потому что я смог(ла) бы делать то, чего давно боюсь", "score": 10}
        ]
    },
]

# States
WELCOME, QUESTION, SHOW_RESULT, FINAL_MESSAGE = range(4)

# Where we store per-user info during the survey
user_data = {}


# Result messages based on score
def get_result_message(score):
    if score <= 25:
        return ("🌟 Cиндром самозванца отсутствует или минимальный уровень\n\nТы умеешь признавать свои достижения и "
                "уверенно идёшь вперёд. Даже если иногда возникают сомнения, они не мешают тебе двигаться дальше. Ты "
                "можешь спокойно принимать похвалу, не списываешь свои успехи на случайность и умеешь работать с "
                "критикой.\n\n📌 На что стоит обратить внимание:\nДаже если синдром самозванца выражен слабо, "
                "он может проявляться в стрессовых ситуациях. Иногда люди, которые чувствуют себя уверенно, "
                "всё равно занижают свою ценность и не используют свой потенциал на 100%.\n\n🎁 Что дальше?\nЧтобы "
                "ещё глубже понять, чего ты хочешь, и уверенно двигаться к своим целям, я подготовила мини-гайд «Как "
                "определить свои ценности и цели». Он поможет тебе чётко увидеть направление, в котором стоит "
                "двигаться.")
    elif score <= 50:
        return "🙂 You are balanced and thoughtful."
    else:
        return "🧘 You are introspective and calm."


# Start command — send welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    start_button = [[KeyboardButton("🚀 Начать тест")]]
    markup = ReplyKeyboardMarkup(start_button, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(
        "👋 Привет, ты только что открыл тест на синдром самозванца, и это уже первый шаг к пониманию, что происходит "
        "в твоей голове!\n\nЭтот тест поможет тебе понять:\n\nЕсть ли у тебя синдром самозванца и насколько он "
        "выражен\n\nКак он мешает тебе развиваться, работать с клиентами, проявляться\n\nЧто именно тебя стопорит — "
        "страх разоблачения, перфекционизм, прокрастинация или синдром вечного ученика\n\nКакие шаги можно сделать "
        "прямо сейчас, чтобы перестать занижать свою ценность\n\nЧто ты получишь в конце теста:\n\nЕсли у тебя есть "
        "синдром самозванца – разбор твоей ситуации и рекомендации, как с этим работать\n\nЕсли его нет – подарок: "
        "мини-гайд «Как определить свои ценности и цели», чтобы уверенно двигаться дальше\n\nТест займет всего 1 "
        "минуту – жми «Начать» и узнавай, что мешает тебе двигаться вперёд.",
        reply_markup=markup
    )
    return WELCOME


# Handle "Start Survey" button
async def begin_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_data[user_id] = {"score": 0, "index": 0}
    return await ask_question(update, context)


# Ask a survey question
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    index = user_data[user_id]["index"]

    if index >= len(survey):
        score = user_data[user_id]["score"]
        result_text = get_result_message(score)

        # Save name and score only
        username = update.effective_user.full_name or update.effective_user.username or f"user_{user_id}"
        with open("survey_results.csv", "a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([username, user_id, score, result_text])

        # Show result + "Next" button
        next_button = [[KeyboardButton("➡️ Далее")]]
        markup = ReplyKeyboardMarkup(next_button, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(f"✅ Опрос пройден!\nВаш результат: {score}\n\n{result_text}",
                                        reply_markup=markup)
        return SHOW_RESULT

    # Otherwise ask next question
    question_data = survey[index]
    keyboard = [[ans["text"]] for ans in question_data["answers"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)
    await update.message.reply_text(question_data["question"], reply_markup=markup)
    return QUESTION


# Handle each answer
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text
    index = user_data[user_id]["index"]
    question_data = survey[index]

    # Match selected answer to score
    for ans in question_data["answers"]:
        if ans["text"] == text:
            user_data[user_id]["score"] += ans["score"]
            break

    user_data[user_id]["index"] += 1
    return await ask_question(update, context)


# Final message after result
async def final_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "🎉 Thanks for completing the survey!\n\nIf you'd like to share your results, feel free to forward them to a friend or retake the survey any time using /start.")
    return ConversationHandler.END


# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Survey cancelled.")
    return ConversationHandler.END


# Set up bot
def main():
    app = ApplicationBuilder().token("8090138169:AAGUFHYeKJNqNE3ng0IsLo83CYAWCt0fL3o").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [MessageHandler(filters.Regex("🚀 Начать тест"), begin_survey)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            SHOW_RESULT: [MessageHandler(filters.Regex("➡️ Далее"), final_message)],
        },
        fallbacks=[CommandHandler("cancel", cancel)]
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == '__main__':
    main()
