import csv
import re
from telegram import Update, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes, ConversationHandler

# Your Telegram ID for admin notifications
ADMIN_ID = 3572078  # actual Telegram ID

# Survey data
survey = [
    {
        "question": "Что ты чувствуешь, когда тебя хвалят за твою работу?",
        "answers": [
            {"text": "Чувствую, что похвала заслуженная", "score": 2},
            {"text": "Приятно, но не фокусируюсь на этом", "score": 4},
            {"text": "Немного неловко, потому что мог(ла) бы сделать лучше", "score": 6},
            {"text": "Ощущаю, что меня переоценивают", "score": 8}
        ]
    },
    {
        "question": "Как ты относишься к своим успехам?",
        "answers": [
            {"text": "Чувствую, что мои достижения – результат моих усилий и навыков", "score": 2},
            {"text": "Иногда думаю, что успех связан с удачей", "score": 4},
            {"text": "Стараюсь не придавать им большого значения", "score": 6},
            {"text": "Ощущаю, что я просто хорошо маскируюсь, и скоро это вскроется", "score": 8}
        ]
    },
    {
        "question": "Как ты реагируешь, когда кто-то просит тебя поделиться своим опытом?",
        "answers": [
            {"text": "Охотно делюсь, ведь знаю, что у меня есть полезный опыт", "score": 2},
            {"text": "Иногда делюсь, но чувствую, что есть люди, знающие больше", "score": 4},
            {"text": "Думаю, что недостаточно компетентен(на) и мне ещё рано", "score": 6},
            {"text": "Отказываюсь, потому что не хочу, чтобы узнали, что я «не эксперт»", "score": 8}
        ]
    },
    {
        "question": "Когда ты начинаешь новый проект или работу, что ты чувствуешь?",
        "answers": [
            {"text": "Волнение, но я уверен(а) в своих силах", "score": 2},
            {"text": "Иногда сомневаюсь, но всё равно двигаюсь вперёд", "score": 4},
            {"text": "Откладываю старт, потому что боюсь, что не справлюсь", "score": 6},
            {"text": "Прокрастинирую и откладываю, потому что боюсь провала", "score": 8}
        ]
    },
    {
        "question": "Как ты относишься к ошибкам?",
        "answers": [
            {"text": "Воспринимаю их как опыт и уроки", "score": 2},
            {"text": "Иногда переживаю, но знаю, что это часть пути", "score": 4},
            {"text": "Испытываю сильное разочарование, даже если ошибка небольшая", "score": 6},
            {"text": "Ощущаю, что ошибки доказывают, что я вообще некомпетентен(на)", "score": 8}
        ]
    },
    {
        "question": "Как ты реагируешь на успехи коллег/конкурентов?",
        "answers": [
            {"text": "Радуюсь за них, это мотивирует меня развиваться", "score": 2},
            {"text": "Думаю, что мне нужно ещё больше стараться", "score": 4},
            {"text": "Сравниваю себя и чувствую, что отстаю", "score": 6},
            {"text": "Ощущаю, что я вообще не в их лиге и не имею права себя с ними сравнивать", "score": 8}
        ]
    },
    {
        "question": "Как ты принимаешь решения?",
        "answers": [
            {"text": "Делаю выводы и действую", "score": 2},
            {"text": "Иногда сомневаюсь, но не откладываю надолго", "score": 4},
            {"text": "Долго думаю и откладываю решение", "score": 6},
            {"text": "Откладываю до последнего, потому что боюсь ошибиться", "score": 8}
        ]
    },
    {
        "question": "Как ты относишься к своему уровню знаний?",
        "answers": [
            {"text": "Я знаю достаточно, чтобы работать в своей сфере", "score": 2},
            {"text": "Иногда мне кажется, что мне нужно ещё немного поучиться", "score": 4},
            {"text": "Думаю, что мой уровень недостаточно высок", "score": 6},
            {"text": "Мне кажется, что я вообще ничего не знаю, в отличие от других", "score": 8}
        ]
    },
    {
        "question": "Что ты чувствуешь, когда тебе дают сложное задание?",
        "answers": [
            {"text": "Уверенность, что справлюсь", "score": 2},
            {"text": "Сомневаюсь, справлюсь ли", "score": 4},
            {"text": "Думаю, что меня переоценили и я не вытяну", "score": 6},
            {"text": "Хочу отказаться, потому что боюсь провала", "score": 8}
        ]
    },
    {
        "question": "Если бы ты мог(ла) избавиться от синдрома самозванца, что бы изменилось в твоей жизни?",
        "answers": [
            {"text": "Я бы продолжил(а) работать, как и сейчас, но с большим удовольствием", "score": 2},
            {"text": "Я бы смог(ла) уверенно брать клиентов, новые более сложные проекты", "score": 4},
            {"text": "Я бы начал(а) активно действовать, а не сомневаться", "score": 6},
            {"text": "Моя жизнь изменилась бы полностью, потому что я смог(ла) бы делать то, чего давно боюсь",
             "score": 8}
        ]
    },
]

# States
WELCOME, QUESTION, RESULT, STAGE_1, STAGE_2, FINAL_STAGE, PHONE_REQUEST, COMPLETE = range(8)

# Where we store per-user info during the survey
user_data = {}

def escape_markdown_v2(text: str) -> str:
    escape_chars = r'_[]()`>#+-=|{}.!'
    return re.sub(rf'([{re.escape(escape_chars)}])', r'\\\1', text)

# Result messages based on score
def get_result_message(score):
    if score <= 30:
        return ("🌟 Синдром самозванца отсутствует или минимален\n\n✨ Ты умеешь признавать свои достижения и "
                "уверенно идёшь вперёд. Спокойно воспринимаешь похвалу, не обесцениваешь успехи и не приписываешь их "
                "случайности — ты стоишь на прочной внутренней опоре."
                "\n\n📌 Но будь внимателен(а):\nВ моменты масштабирования, публичности или перемен может включаться "
                "внутренний критик."
                "\nТы можешь не использовать свой потенциал на 100%, просто потому что что-то внутри шепчет:"
                "\n\n«А вдруг это было случайно? А вдруг я переоцениваю себя?..»\n\n🎯 Что дальше?"
                "\nТы готов(а) на следующий уровень — но без внутреннего напряжения, в своём темпе, с удовольствием."
                "\nНа коуч-сессиях мы:\n— уберём остаточные блоки,\n— укрепим уверенность,\n— построим стратегию "
                "роста без выгорания."
                "\n\n👉 Хочешь выйти на новый уровень без страха и откатов?\nНапиши «Уверенность» — и я расскажу, "
                "как это может выглядеть именно для тебя.")
    elif score <= 50:
        return ("Умеренный уровень синдрома самозванца\n\n✨ Ты действуешь. Ты умеешь."
                "\nНо внутри будто живёт голос, который мешает почувствовать опору:\n«А может, это просто "
                "повезло?..»\n«Другие точно знают больше…»\n«Если я ошибусь, обо мне подумают не то…»"
                "\n\n📌 Как это влияет:\n— Откладываешь запуск своего проекта\n— Не говоришь о своих результатах\n— "
                "Боишься просить"
                "больше\n— Берёшь меньше клиентов/проектов/задач, чем мог(ла) бы"
                "\n\nТы будто держишь себя «в тени» — хотя потенциал огромный."
                "\n\n🎯 Что дальше?\nСомнения не должны быть фоном твоей карьеры.\nС этим можно работать — и "
                "освободить себя от страха быть собой."
                "\n\n👉 Хочешь наконец поверить в себя и перестать тормозить рост?\nНапиши «Уверенность» — расскажу, "
                "с чего начать и как можно выйти из этого круга.")
    elif score <= 65:
        return ("Выраженный синдром самозванца\n\nТы много работаешь, учишься, стараешься — но внутри будто "
                "пусто.\n\n«Я не настоящий профессионал своего дела»\n«Когда-нибудь это раскроется и все поймут что я "
                "недостаточно хорош(а)...»\n«Я просто хорошо"
                "скрываю свое истинное я…»\n\n📌 Что происходит:\n— Ты боишься просить больше\n— Не говоришь о себе "
                "публично\n—"
                "Отказываешься от проектов «на вырост»\n— Не можешь отпустить контроль — и устаёшь\n\nЭто не про "
                "объективную реальность. Это про внутреннего критика, который управляет решениями.\n\n🎯 Что "
                "дальше?\nВажно вернуть себе право быть, проявляться, зарабатывать, расти — с уважением к себе.\n\n👉 "
                "Напиши «Уверенность», если хочешь начать путь к жизни, где ты больше не доказываешь — ты просто "
                "живёшь, дышишь и делаешь своё дело.")
    else:
        return ("🚨 Критический уровень синдрома самозванца\n\nТы живёшь в режиме выживания.\nТы работаешь, "
                "но не чувствуешь, что заслуживаешь.\nТы боишься показаться «самоуверенным(ой)».\nТы не начинаешь. Не "
                "просишь. Не заявляешь.\n\n📌 Как это выглядит:\n— Ты учишься бесконечно, но не запускаешь\n— Ты "
                "дорабатываешь, но не показываешь\n— Ты сравниваешь — и всегда в минус\n— Ты живёшь в напряжении, "
                "что «вот-вот всё рухнет»\n\n📌 Важно понять:\nТы не некомпетентен(а).\nТы просто долго живёшь с "
                "голосом, который говорит:\n«Ты недостаточн(а)…»\n«Ты не имеешь права…»\n\n🎯 Что дальше?\nС этим "
                "реально работать. Без стыда. Без давления.\nВ поддержке, с методикой, которая помогает.\n\n👉 Напиши "
                "«Уверенность», если хочешь выдохнуть и, наконец, разрешить себе жить свою жизнь — без страха быть "
                "собой.")


def get_stage_1_message(score):
    if score <= 30:
        return ("🧭 Ты уверенно идёшь вперёд — это чувствуется. Но даже при стабильной внутренней опоре могут быть "
                "зоны, в которых ты ещё не реализован(а) на полную мощность. Особенно в моменты стресса, "
                "масштабирования или перехода на новый уровень.\n\nЕсли ты хочешь глубже понять, "
                "чего ты действительно хочешь от своей деятельности, как выстроить цели, которые соответствуют тебе, "
                "а не «надо», и как двигаться к ним спокойно, без напряжения — я приглашаю тебя в личную "
                "работу.\n\nНа коуч-сессиях мы:\n— Разберём, какие твои настоящие ценности могут стать точкой "
                "опоры\n— Определим цели, которые будут вдохновлять, а не выжимать\n— Уберём внутренние напряжения, "
                "которые мешают раскрыться полностью даже в комфортном состоянии\n\nЕсли ты хочешь идти глубже и "
                "развиваться осознанно — напиши мне **«Коучинг»**, и я расскажу, как это может выглядеть для тебя.")
    elif score <= 50:
        return ("🔍 Ты умеешь действовать. Но когда появляется что-то новое, амбициозное или публичное — появляется и "
                "внутренний критик. Сомнения в стиле «а вдруг я недостаточно хорош(а)?» начинают мешать расти.\n\n"
                "Если ты хочешь перестать замирать перед возможностями, научиться спокойно говорить о себе и своих "
                "успехах,"
                "брать уверенно проекты и зарабатывать без стыда — я приглашаю тебя на индивидуальную работу.\n\n"
                "В процессе коучинга мы:\n"
                " — Найдём ключевые убеждения, которые включают синдром самозванца в стрессовых точках\n"
                " — Переопределим внутреннюю систему оценки себя\n"
                " — Построим поддерживающую стратегию, чтобы ты мог(ла) расти без надрыва и страха\n\n"
                "Если чувствуешь, что хочешь перестать сомневаться в том, что уже внутри тебя есть — напиши мне "
                "**«Коучинг»**, "
                "и я расскажу о формате работы.")
    elif score <= 65:
        return ("💡 Ты не просто иногда сомневаешься.\nТы часто живёшь **на тонкой грани** - между «я справляюсь» и "
                "«я на пределе»⚖️\nКак будто всё держится"
                "на контроле, усилиях и страхе «не облажаться»😓\nИ даже когда снаружи все выглядит ок — внутри "
                "накапливается тревога,"
                "усталость и мысль «А вдруг все это не по-настоящему?..»💭\n\n"
                "Если ты хочешь:\n"
                " — 🌿 Перестать обесценивать себя\n"
                " — 🔥 Брать те самые проекты, от которых по-настоящему загораешься\n"
                " — 🧘‍♀️ Работать в своём темпе, без чувства вины и самокопания\n"
                " — 🌟 Начать видеть и признавать свою экспертность\n"
                " — 📈 Расти — устойчиво, без выгорания и гонки\n\n"
                "Я приглашаю тебя в личный коучинг.\n\n"
                "На сессиях мы:\n"
                " ✔ Разберем, как именно синдром самозванца влияет на твои решения\n"
                " ✔ Снимем внутренние запреты на уверенность, проявленность и право быть «достаточно»\n"
                " ✔ Подружим твою логику и чувства — чтобы они перестали тянуть в разные стороны 🤝\n\n"
                "Ты не обязана всё тянуть сама 🤍\n"
                "Если хочешь перестать бороться и начать жить с ощущением: «я могу, я умею, я имею право» — напиши мне "
                "**«Коучинг»**, и мы обсудим, как начать.")
    else:
        return ("🆘 Если внутри всё время ощущение, что ты как будто «не совсем настоящая», что любое новое действие "
                "— это риск быть разоблаченной, а твои достижения будто случайны или преувеличены…\n"
                "Знаешь, это не про то, что ты недостаточен(а)."
                "Это про то, что ты слишком долго живешь рядом с голосом, который так говорит. 💭\n\n"
                "Я знаю, как тяжело всё время держаться, чтобы никто не заметил: *я на пределе*.\n"
                "Жить с ощущением, что ты *почти соответствуешь, почти справляешься, почти имеешь право быть здесь…*\n"
                "Это выматывает. Очень. 😔\n"
                "Но с этим можно по-другому.\nБез давления. Без «давай, соберись».\nС уважением к тому пути, "
                "который ты уже прошел(а)."
                "И с мягкой, честной перестройкой изнутри. 🌱\n\n"
                "На коуч-сессиях мы:\n"
                "✔ Разберем, откуда на самом деле растет этот страх быть «недостаточным(ой)»\n"
                "✔ Начнём менять внутренний голос, который обесценивает\n"
                "✔ Поможем тебе собрать опору — не придуманный идеальный образ, а настоящего(ую) тебя, живого(ую), "
                "уверенного(ую), устойчивого(ую) 💪\n\n"
                "Ты не обязан(а) справляться с этим один(а). 🤍\n"
                "Если ты чувствуешь, что хочешь начать жить иначе — напиши мне **«Коучинг»**, "
                "и я расскажу, как это может быть именно для тебя ✨")


welcome_text = (
    "👋 Привет, ты только что открыл тест на синдром самозванца, и это уже первый шаг к пониманию, что происходит "
    "в твоей голове!\n\n**Этот тест поможет тебе понять:**\n\nЕсть ли у тебя синдром самозванца и насколько он "
    "выражен\n\nЧто именно тебя стопорит — страх разоблачения, перфекционизм, прокрастинация или синдром вечного "
    "ученика\n\nКакие шаги можно сделать"
    "прямо сейчас, чтобы избавится от самозванца внутри себя\n\nЧто ты получишь в конце теста:\n\n"
    "Разбор твоей ситуации и рекомендации, как с этим работать\nУзнаешь есть ли у тебя синдром самозванца и в "
    "какой степени он выражен"
    "\nПолучишь рекомендации что делать с твоим случаем\n\nТест займет всего 1 "
    "минуту – жми «Начать тест» и узнавай, что мешает тебе двигаться вперёд."
)

stage_2_message = (
    "**Ты уже знаешь, что что-то внутри мешает тебе двигаться свободно.**\n"
    "Ты работаешь, умеешь, стараешься. Но всё равно живёшь с этим фоновым напряжением — как будто в любой момент "
    "кто-то поймёт, что ты “не тот”. Что ты — случайность. И тогда всё рухнет.\n\n"
    "Я знаю это чувство.\n"
    "Я сама через него проходила. И сейчас работаю с людьми, которые внешне всё делают правильно, "
    "но внутри постоянно обесценивают себя.\n"
    "⠀\n"
    "📌 Я не буду говорить тебе “просто поверь в себя” — это не работает.\n"
    "⠀\n"
    "Я работаю в CBC — это когнитивно-поведенческий подход, один из самых изученных и эффективных в мире.\n"
    "⠀\n"
    "Без эзотерики. Без магии. Только конкретные мысли, реакции, действия — и то, как мы с ними обращаемся.\n\n"
    "Как устроена работа:\n"
    " — Мы не будем “разговаривать по душам”, чтобы стало полегче.\n"
    "   Мы будем **менять то, как ты думаешь, действуешь и относишься к себе.**\n\n"
    " — Ты получишь упражнения, которые реально что-то двигают.\n"
    " — Я буду рядом в чате между сессиями — ты не останешься вариться в себе.\n"
    " — И да, ты научишься **самокоучингу** — чтобы не зависеть от меня и дальше опираться на себя."
)

final_message = (
    "✨ **Хватит замирать. Время расти уверенно.**\n"
    "**Индивидуальная работа с синдромом самозванца, страхами и внутренними блоками**\n\n"
    "Ты много знаешь, стараешься, учишься. Но...\n"
    " 🔸 боишься заявить о себе громко\n"
    " 🔸 не берёшь достойную цену\n"
    " 🔸 откладываешь важные шаги\n"
    " 🔸 не чувствуешь, что ты «достаточно хорош(а)»\n"
    " 🔸 сравниваешь себя с другими и замираешь\n\n"
    "Я не буду говорить тебе «поверь в себя».\n"
    "Мы вместе перестроим мышление, укрепим опору и сделаем так, чтобы ты начал(а) **двигаться с легкостью, "
    "уверенностью и уважением к себе.**\n\n"
    "🎯 **Выбирай формат, который тебе подойдет:**\n\n"
)

price_option_1 = (
    "Для тех, кто хочет навести порядок в голове и понять, что делать дальше.\n\n"
    "Ты получаешь:\n"
    "✔ 1 индивидуальную сессию (60 минут) — **цена отдельно: 50$**\n"
    "✔ Диагностику — в чём конкретно тебя стопорит синдром самозванца — **цена отдельно: 50$**\n"
    "✔ Поймем четкий фокус: куда двигаться, чтобы не сливаться — **цена отдельно: 50$**\n\n"
    "**Подарки**:\n"
    "✔ Гайд «Как справиться со страхами, если у тебя синдром самозванца?» — **цена отдельно: 30$**\n"
    "✔ Гайд: как создать свою персональную аудио-практику «5 минут уверенности» для тех моментов, "
    "когда тебя что-то останавливает — **цена отдельно: 50$**\n"
    "Вместе общая ценность ~*230$*~\n"
    "🎁 **Прямо сейчас вы можете забрать этот пакет за 30$**\n"
    "🔑 Уже после одной сессии ты начнёшь чувствовать: *я могу. Имею право. Хватит тормозить.*"
)

price_option_2 = (
    "Для тех, кто хочет глубоко проработать страхи, выйти на новый уровень и перестать обесценивать себя.\n\n"
    "**Ты получаешь:**\n"
    "✔ 4 коуч-сессии (60 мин) — **цена отдельно: 100$**\n"
    "✔ Персональные упражнения и обратную связь от коуча\n"
    "*🎁 + Только для участников этого формата:*\n"
    "✔ Гайд «Знаю, но не делаю»: как преодолеть прокрастинацию?» — **цена отдельно: 30$**\n"
    "✔ Гайд «Ценности и цели: как понять, чего ты хочешь и какое твоё большое зачем?» — **цена отдельно: 50$**\n"
    "✔ Практикум: как создать медитацию «Безусловная уверенность и опора на себя» — **цена отдельно: 60$**\n"
    "✔ Плейлист «Уверенность включена» — для фона, фокуса и вдохновения, на частоте, которая помогает мозгу "
    "исцелиться — **цена отдельно: 20$**\n"
    "✔ PDF-чеклист «Ты уже достоин(на)» — твоя ежедневная практика для роста ценности и самоощущения — **цена "
    "отдельно: 20$**\n\n"
    "Вместе общая ценность ~*280$*~\n\n"
    "🎁 Прямо сейчас вы можете забрать этот пакет за **100$**"
)


# Start command — send welcome message
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    payload = context.args[0] if context.args else "direct"

    # Save the source to user_data
    user_data[user_id] = user_data.get(user_id, {})
    user_data[user_id]["source"] = payload

    start_button = [[KeyboardButton("🚀 Начать тест")]]
    markup = ReplyKeyboardMarkup(start_button, one_time_keyboard=True, resize_keyboard=True)

    escaped_welcome_text = escape_markdown_v2(welcome_text)
    await update.message.reply_text(escaped_welcome_text, reply_markup=markup, parse_mode="MarkdownV2")
    return WELCOME


# Handle "Start Survey" button
async def begin_survey(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    user_data[user_id]["score"] = 0
    user_data[user_id]["index"] = 0
    return await ask_question(update, context)


# Ask a survey question
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    index = user_data[user_id]["index"]

    if index >= len(survey):
        score = user_data[user_id]["score"]
        result_msg = get_result_message(score)
        user_data[user_id]["score_result"] = result_msg

        next_button = [[KeyboardButton("Уверенность")]]
        markup = ReplyKeyboardMarkup(next_button, one_time_keyboard=True, resize_keyboard=True)

        await update.message.reply_text(f"✅ Опрос пройден!\nРезультат теста: {score} баллов\n\n{result_msg}",
                                        reply_markup=markup)
        return RESULT

    q = survey[index]
    keyboard = [[a["text"]] for a in q["answers"]]
    markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(q["question"], reply_markup=markup)
    return QUESTION


# Ответы
async def handle_answer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_chat.id
    text = update.message.text
    index = user_data[user_id]["index"]
    for ans in survey[index]["answers"]:
        if ans["text"] == text:
            user_data[user_id]["score"] += ans["score"]
            break
    user_data[user_id]["index"] += 1
    return await ask_question(update, context)


# "Уверенность"
async def stage_1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    score = user_data[update.effective_chat.id]["score"]
    msg = get_stage_1_message(score)
    escaped_msg = escape_markdown_v2(msg)
    btn = [[KeyboardButton("Коучинг")]]
    markup = ReplyKeyboardMarkup(btn, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(escaped_msg, reply_markup=markup, parse_mode="MarkdownV2")
    return STAGE_1


# "Коучинг"
async def stage_2(update: Update, context: ContextTypes.DEFAULT_TYPE):
    btn = [[KeyboardButton("Узнать больше")]]
    markup = ReplyKeyboardMarkup(btn, one_time_keyboard=True, resize_keyboard=True)

    escaped_stage_2_message = escape_markdown_v2(stage_2_message)
    await update.message.reply_text(escaped_stage_2_message, reply_markup=markup, parse_mode="MarkdownV2")
    return STAGE_2


# "Узнать больше"
async def final_stage(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # Show buttons for options or skip to the next step
    markup = get_final_stage_buttons()

    # Show the final message
    escaped_final_message = escape_markdown_v2(final_message)
    await update.message.reply_text(escaped_final_message, reply_markup=markup, parse_mode="MarkdownV2")
    return FINAL_STAGE


def get_final_stage_buttons():
    buttons = [
        ["Разовая коуч-сессия"],
        ["Сопровождение 1 месяц"],
        ["📞 Понял(а) — хочу связаться"]
    ]
    return ReplyKeyboardMarkup(buttons, resize_keyboard=True, one_time_keyboard=False)


async def handle_final_stage_buttons(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = update.message.text

    if text == "Разовая коуч-сессия":
        esc_price_option_1 = escape_markdown_v2(price_option_1)
        await update.message.reply_text(esc_price_option_1, reply_markup=get_final_stage_buttons(), parse_mode="MarkdownV2")
        return FINAL_STAGE

    elif text == "Сопровождение 1 месяц":
        esc_price_option_2 = escape_markdown_v2(price_option_2)
        await update.message.reply_text(esc_price_option_2, reply_markup=get_final_stage_buttons(), parse_mode="MarkdownV2")
        return FINAL_STAGE

    elif text == "📞 Понял(а) — хочу связаться":
        return await phone_request(update, context)

    else:
        await update.message.reply_text("Выбери один из вариантов ниже 👇", reply_markup=get_final_stage_buttons(), parse_mode="MarkdownV2")
        return FINAL_STAGE


async def phone_request(update: Update, context: ContextTypes.DEFAULT_TYPE):
    buttons = [
        [KeyboardButton("Я иду! 📞 Отправить номер телефона", request_contact=True)],
        [KeyboardButton("Пропустить")]
    ]
    markup = ReplyKeyboardMarkup(buttons, one_time_keyboard=True, resize_keyboard=True)

    await update.message.reply_text(
        "📲 Чтобы я могла с тобой связаться, нажми кнопку ниже. Я получу твой номер.\n"
        "Или нажми «Пропустить», если пока не готов(а) делиться контактом.",
        reply_markup=markup
    )
    return PHONE_REQUEST


async def handle_contact_or_skip(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.full_name or user.username or f"user_{user_id}"
    score = user_data[user_id]["score"]
    source = user_data[user_id].get("source", "unknown")

    # Handle contact OR skip
    if update.message.contact:
        phone_number = update.message.contact.phone_number
    else:
        phone_number = "не указан"

    # Save to CSV with all final info
    with open("final_signups.csv", "a", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([username, user_id, score, phone_number, source])

    # Save to user_data for use in complete()
    user_data[user_id]["final_phone"] = phone_number

    return await complete(update, context)


# "Я иду"
async def complete(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    user_id = user.id
    username = user.full_name or user.username or f"user_{user_id}"
    score = user_data[user_id]["score"]
    phone_number = user_data[user_id].get("final_phone", "не указал(а)")
    source = user_data[user_id].get("source", "unknown")

    msg = (
        f"🚨 Новый пользователь прошёл весь путь:\n\n"
        f"👤 {username}\n"
        f"🆔 {user_id}\n"
        f"📞 Телефон: {phone_number}\n"
        f"🎯 Баллы: {score}\n"
        f"🌐 Источник: {source}"
    )
    await context.bot.send_message(chat_id=ADMIN_ID, text=msg)

    await update.message.reply_text("Ссылка на реквизиты оплаты. Скиньте квитанцию об оплате в формате PDF.\n"
                                    "Спасибо! Я свяжусь с тобой в течение 24 часов 💌")
    return ConversationHandler.END


# Cancel command
async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Тест отменён.")
    return ConversationHandler.END


# Set up bot
def main():
    app = ApplicationBuilder().token("8090138169:AAGUFHYeKJNqNE3ng0IsLo83CYAWCt0fL3o").build()

    conv_handler = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            WELCOME: [MessageHandler(filters.Regex("🚀 Начать тест"), begin_survey)],
            QUESTION: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_answer)],
            RESULT: [MessageHandler(filters.Regex("Уверенность"), stage_1)],
            STAGE_1: [MessageHandler(filters.Regex("Коучинг"), stage_2)],
            STAGE_2: [MessageHandler(filters.Regex("Узнать больше"), final_stage)],
            FINAL_STAGE: [MessageHandler(filters.TEXT & ~filters.COMMAND, handle_final_stage_buttons)],
            PHONE_REQUEST: [
                MessageHandler(filters.CONTACT, handle_contact_or_skip),
                MessageHandler(filters.Regex("Пропустить"), handle_contact_or_skip)
            ]
        },
        fallbacks=[CommandHandler("cancel", cancel)],
    )

    app.add_handler(conv_handler)
    app.run_polling()


if __name__ == "__main__":
    main()
