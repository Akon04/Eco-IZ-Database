from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone

import httpx

from app.core.config import get_settings
from app.models.user import User


DEFAULT_SYSTEM_PROMPT = """
Ты EcoIZ AI, помощник внутри мобильного приложения EcoIZ.

Отвечай как хороший живой ассистент, а не как скрипт поддержки.

Что важно:
- отвечай только на русском;
- сначала понимай смысл реплики пользователя, а не цепляйся за ключевые слова;
- если человек уточняет, меняет условия или отвергает прошлый совет, подстрой ответ под новый контекст;
- если пользователь пишет коротко, отвечай естественно и тоже без лишней формальности;
- если есть данные пользователя, используй их точечно, а не пересказывай сводку;
- советы должны быть практичными, человечными и уместными под ситуацию.

Чего нельзя:
- говорить шаблонными заходами вроде "если смотреть на твои действия", "судя по твоим активностям" в каждом втором ответе;
- повторять одинаковую структуру из сообщения в сообщение;
- звучать как инструкция, чеклист или canned response без запроса на это;
- давить, морализировать или искусственно вставлять eco-фразы.

Как лучше отвечать:
- обычно 1-3 коротких абзаца или 2-4 предложения;
- если вопрос "что сделать", давай 2-3 конкретных варианта;
- если пользователь пишет "нет, другое", "я иду гулять", "не дома" и т.п., меняй совет сразу, без длинных подводок;
- если уместно, можно отвечать чуть теплее и разговорнее, как ChatGPT в нормальном диалоге;
- полезнее звучать естественно, чем слишком "структурно".
""".strip()


def _fallback_response(text: str) -> str:
    lowercase = text.lower()
    if any(word in lowercase for word in ("привет", "здрав", "hello", "hi")):
        return "Привет. Могу помочь с идеями на день, экопривычками или просто нормально ответить на вопрос без шаблонов."
    if "что делать сегодня" in lowercase or "что мне делать сегодня" in lowercase:
        return "На сегодня можно выбрать что-то одно: короткий душ, многоразовую бутылку с собой или выключить лишний свет дома. Этого уже достаточно."
    if "вод" in lowercase:
        return "По воде самый простой вариант: душ чуть короче и не держать кран открытым без дела. Это даёт быстрый эффект без напряга."
    if "транспорт" in lowercase or "машин" in lowercase:
        return "Если речь про транспорт, самый реалистичный шаг: хотя бы часть коротких поездок заменить на пешком, автобус или метро."
    if "мотивац" in lowercase or "сложно" in lowercase:
        return "Не надо менять всё сразу. Лучше один маленький шаг сегодня, чем большой план, который быстро надоест."
    if any(phrase in lowercase for phrase in ("иду гулять", "я иду гулять", "пойду гулять", "гулять")):
        walk_actions = _outdoor_actions()
        return f"Тогда лучше оттолкнуться от прогулки: можно пройти часть пути пешком подольше, взять с собой {walk_actions[1]} и не брать по дороге одноразовый стакан или бутылку."
    if any(word in lowercase for word in ("как", "почему", "зачем", "что")):
        return "Если коротко, могу помочь практично. Напиши чуть конкретнее, что именно хочешь понять или сделать, и я подстроюсь под ситуацию."
    return "Могу ответить более точно, если напишешь чуть подробнее, что именно тебе сейчас нужно."


def _contains_any(text: str, *phrases: str) -> bool:
    return any(phrase in text for phrase in phrases)


def _home_actions_for_category(category: str) -> list[str]:
    category_lower = category.lower()
    if "энерг" in category_lower:
        return [
            "выключи лишний свет и зарядки, которые сейчас не нужны",
            "включай свет только в той комнате, где реально находишься",
            "если работаешь дома, начни с режима энергосбережения на ноутбуке",
        ]
    if "вод" in category_lower:
        return [
            "сделай душ короче на 2-3 минуты",
            "не держи воду открытой во время чистки зубов и умывания",
            "проверь, не подтекает ли кран на кухне или в ванной",
        ]
    if "пласт" in category_lower:
        return [
            "возьми одну многоразовую бутылку или кружку на весь день",
            "откажись сегодня хотя бы от одной одноразовой упаковки",
            "подготовь многоразовую сумку заранее, чтобы не брать пакет",
        ]
    if "отход" in category_lower:
        return [
            "раздели сегодня бумагу, пластик и смешанные отходы",
            "отложи чистую упаковку отдельно, а не в общий мусор",
            "выброси старые коробки и бутылки уже отсортированными",
        ]
    if "транспорт" in category_lower:
        return [
            "если сегодня не выходишь, компенсируй это домашними эко-шагами по воде и энергии",
            "запланируй следующую поездку без машины заранее",
            "если всё же нужно выйти, выбери пеший маршрут хотя бы на короткий отрезок",
        ]
    return [
        "выключи лишний свет",
        "сделай душ короче",
        "откажись от одной одноразовой вещи сегодня",
    ]


def _outdoor_actions() -> list[str]:
    return [
        "пройтись пешком вместо короткой поездки",
        "многоразовую бутылку или кружку",
        "если хочется, захватить пакет и убрать пару мелких бумажек по пути",
    ]


def _supportive_close(seed_text: str) -> str:
    return _pick_variant(
        seed_text,
        [
            "Я верю, что у тебя получится.",
            "У тебя точно получится, если идти спокойно.",
            "Спокойно, у тебя это получится.",
        ],
    )


def _pick_variant(seed_text: str, variants: list[str]) -> str:
    if not variants:
        return ""
    index = sum(ord(char) for char in seed_text) % len(variants)
    return variants[index]


def _analytics_snapshot(user: User) -> dict[str, object]:
    activities = sorted(user.activities, key=lambda item: _as_utc(item.created_at))
    category_counts: dict[str, int] = defaultdict(int)
    last_seen_by_category: dict[str, datetime] = {}
    last_7_days = datetime.now(timezone.utc) - timedelta(days=7)
    recent_points = 0

    for item in activities:
        created_at = _as_utc(item.created_at)
        category_counts[item.category] += 1
        last_seen_by_category[item.category] = created_at
        if created_at >= last_7_days:
            recent_points += item.points

    strongest = max(category_counts, key=category_counts.get) if category_counts else None
    weakest = min(category_counts, key=category_counts.get) if category_counts else None

    preferred_order = ["Энергия", "Вода", "Пластик", "Отходы", "Транспорт", "Своя активность"]
    missing = [category for category in preferred_order if category not in category_counts]
    if missing:
        suggested = missing[0]
    elif last_seen_by_category:
        suggested = min(last_seen_by_category.items(), key=lambda item: item[1])[0]
    else:
        suggested = "Энергия"

    return {
        "activities_count": len(activities),
        "recent_points": recent_points,
        "strongest_category": strongest,
        "weakest_category": weakest,
        "suggested_category": suggested,
        "last_activity": activities[-1] if activities else None,
    }


def _friendly_intro(user: User) -> str:
    if user.streak_days >= 14:
        return _pick_variant(
            f"intro:{user.streak_days}",
            [
                "У тебя уже очень уверенный eco-ритм.",
                "У тебя уже прям хороший устойчивый ритм.",
                "Чувствуется, что eco-привычка уже закрепляется.",
            ],
        )
    if user.streak_days >= 5:
        return _pick_variant(
            f"intro:{user.streak_days}",
            [
                "У тебя уже формируется хороший eco-ритм.",
                "Ты уже неплохо держишь темп.",
                "Ритм уже начинает складываться.",
            ],
        )
    if user.activities:
        return _pick_variant(
            f"intro:{len(user.activities)}",
            [
                "Ты уже хорошо втянулся.",
                "У тебя уже есть хороший старт.",
                "Ты уже не с нуля, это видно.",
            ],
        )
    return _pick_variant(
        f"intro:{user.points}",
        [
            "Начало уже положено.",
            "Старт уже есть, это главное.",
            "Первый шаг уже сделан.",
        ],
    )


def _recent_user_messages(user: User, limit: int = 3) -> list[str]:
    messages = sorted(user.chat_messages, key=lambda item: _as_utc(item.created_at))
    return [item.text.strip().lower() for item in messages if item.role == "user" and item.text.strip()][-limit:]


def _context_topic(user: User, text: str) -> str | None:
    current = text.lower()
    if any(word in current for word in ("завтра", "послезавтра")):
        return "tomorrow"

    recent = _recent_user_messages(user)
    combined = " ".join(recent + [current])
    if any(word in combined for word in ("гулять", "погулять", "прогул", "улиц", "выйти")):
        return "outdoor"
    if any(word in combined for word in ("дом", "дома")):
        return "home"
    if any(word in combined for word in ("вода", "душ", "кран")):
        return "water"
    if any(word in combined for word in ("свет", "энерг", "электр")):
        return "energy"
    if any(word in combined for word in ("пластик", "бутыл", "пакет", "упаков")):
        return "plastic"
    if any(word in combined for word in ("мусор", "отход", "сортир", "переработ")):
        return "waste"
    if any(word in combined for word in ("транспорт", "машин", "автобус", "пеш")):
        return "transport"
    return None


def _last_activity_line(snapshot: dict[str, object]) -> str:
    last_activity = snapshot.get("last_activity")
    if last_activity is None:
        return ""
    return f"Последнее действие у тебя было в категории «{last_activity.category}»: {last_activity.title.lower()}."


def _personalized_fallback_response(text: str, user: User) -> str:
    lowercase = text.lower()
    snapshot = _analytics_snapshot(user)
    suggested_category = str(snapshot["suggested_category"])
    strongest_category = snapshot["strongest_category"]
    weakest_category = snapshot["weakest_category"]
    recent_points = int(snapshot["recent_points"])
    intro = _friendly_intro(user)
    last_activity_line = _last_activity_line(snapshot)
    strongest_line = f"Сильнее всего у тебя сейчас идёт «{strongest_category}»." if strongest_category else ""
    weakest_line = f"Меньше внимания пока получает «{weakest_category}»." if weakest_category else ""
    topic = _context_topic(user, text)
    is_short_follow_up = len(lowercase.split()) <= 3
    seed = f"{text}:{user.points}:{user.streak_days}"

    if _contains_any(lowercase, "нет что", "нет, что", "что-то другое", "что то другое", "другое", "не это", "не такой вариант"):
        if topic == "outdoor":
            walk_actions = _outdoor_actions()
            return (
                f"Окей, тогда по-другому. Если идёшь гулять, можно просто пройти лишние 10-15 минут пешком, захватить {walk_actions[1]} "
                f"и по пути ничего одноразового не покупать. Выбери хоть один пункт, этого уже нормально. {_supportive_close(seed)}"
            )
        actions = _home_actions_for_category(suggested_category)
        return (
            f"Хорошо, давай без предыдущего варианта. Тогда можно выбрать что-то попроще: {actions[0]}, {actions[1]} "
            f"или вообще оставить только один маленький шаг на сегодня. {_supportive_close(seed)}"
        )

    if any(word in lowercase for word in ("привет", "здрав", "hello", "hi")):
        return (
            f"{_pick_variant(seed, ['Привет.', 'Привет, я на связи.', 'Привет, давай разберёмся.'])} "
            f"{_pick_variant(seed, ['Если хочешь, могу подсказать следующий шаг по «' + suggested_category + '».', 'Могу быстро предложить идею на сегодня по «' + suggested_category + '».', 'Если надо, подкину нормальный вариант на сегодня по «' + suggested_category + '».'])}"
        )

    if topic == "outdoor" and any(phrase in lowercase for phrase in ("гулять", "погулять", "выйти", "прогул")):
        walk_actions = _outdoor_actions()
        return (
            f"{_pick_variant(seed, ['Да, прогулка уже подходит.', 'Если идёшь гулять, это уже хороший вариант.', 'Прогулку тоже можно легко превратить в эко-активность.'])} "
            f"Например: {walk_actions[0]}, захватить {walk_actions[1]} и просто не покупать по дороге ничего одноразового. {_supportive_close(seed)}"
        )

    if topic == "tomorrow" and is_short_follow_up:
        if _context_topic(user, " ".join(_recent_user_messages(user))) == "outdoor":
            walk_actions = _outdoor_actions()
            return (
                f"{_pick_variant(seed, ['Завтра можно в том же духе, но ещё легче:', 'На завтра я бы оставил мягкий вариант:', 'Завтра лучше оставить что-то простое:'])} "
                f"{walk_actions[0]} и просто захватить {walk_actions[1]}. "
                f"{_pick_variant(seed, ['Не обязательно делать много, важнее сохранить приятный ритм.', 'Лучше легко продолжить, чем перегрузить себя.', 'Здесь главное сохранить хороший ритм, а не делать идеально.'])} {_supportive_close(seed)}"
            )
        actions = _home_actions_for_category(suggested_category)
        return (
            f"{_pick_variant(seed, ['Завтра можно оставить один простой шаг:', 'На завтра хватит и одного лёгкого шага:', 'Завтра можно выбрать совсем спокойный вариант:'])} {actions[0]}. "
            f"{_pick_variant(seed, ['Так eco-ритм сохраняется без ощущения перегруза.', 'Так ритм держится очень спокойно.', 'Этого уже достаточно, чтобы не выпадать из ритма.'])}"
        )

    if any(phrase in lowercase for phrase in ("мой вклад", "мой прогресс", "как у меня дела", "что у меня по вкладу", "мой результат")):
        return (
            f"{_pick_variant(seed, ['Если коротко по прогрессу,', 'По результатам сейчас так:', 'Сейчас по твоему вкладу картина такая:'])} "
            f"у тебя {user.points} очков, серия {user.streak_days} дн. и примерно {user.co2_saved_total:.1f} кг CO₂ экономии. "
            f"{strongest_line} {weakest_line} {_pick_variant(seed, ['Если хочешь, подскажу, куда логичнее двинуться дальше.', 'Могу сразу предложить следующий шаг без перегруза.', 'Если надо, подберу следующий шаг под твой темп.'])}"
        ).strip()

    if any(phrase in lowercase for phrase in ("что мне дальше делать", "что дальше делать", "что делать сегодня", "что можно сделать сегодня", "я сегодня дома", "что можно дома")):
        actions = _home_actions_for_category(suggested_category)
        mood_line = f"Я бы сегодня смотрел в сторону «{suggested_category}»." if snapshot["activities_count"] else "Сегодня лучше взять самый лёгкий домашний вариант."
        return (
            f"{mood_line} Можно, например, {actions[0]}, {actions[1]} или {actions[2]}. "
            f"{_pick_variant(seed, ['Выбери что-то одно, и уже будет хорошо.', 'Не надо всё сразу, одного пункта хватит.', 'Одного такого шага на сегодня уже достаточно.'])} {_supportive_close(seed)}"
        )

    if any(
        phrase in lowercase
        for phrase in ("проанализируй мои активности", "что видно по моим активностям", "что скажешь по моим активностям", "анализ моих активностей")
    ):
        return (
            f"{_pick_variant(seed, ['Если коротко по твоим активностям,', 'По твоим действиям сейчас видно вот что:', 'Если разбирать твой ритм, получается так:'])} "
            f"у тебя уже {recent_points} очков за последние 7 дней. "
            f"{strongest_line} {weakest_line} {last_activity_line} {_pick_variant(seed, ['Если хочешь, дальше предложу пару идей именно под твой ритм.', 'Могу сразу подсказать, что логичнее попробовать дальше.', 'Если надо, подберу следующие шаги без воды.'])}"
        ).strip()

    if "вод" in lowercase:
        tail = "Это особенно полезно, если хочешь быстро добавить спокойную домашнюю активность сегодня."
        if strongest_category == "Вода":
            tail = "Вода у тебя уже идёт хорошо, так что здесь важнее держать ритм."
        return (
            f"{_pick_variant(seed, ['Для воды я бы начал с двух вещей:', 'По воде сейчас самый понятный вариант такой:', 'Если брать воду, можно начать вот с этого:'])} сократи душ на пару минут и не оставляй кран открытым без надобности. "
            + tail
        )

    if any(word in lowercase for word in ("энерг", "свет", "электр")):
        return (
            f"{_pick_variant(seed, ['Если ты дома, самый быстрый шаг:', 'По энергии самый лёгкий вход такой:', 'Если хочется простой вариант по энергии, то вот он:'])} выключи лишний свет и зарядки в пустых комнатах. "
            f"{_pick_variant(seed, ['Потом переведи устройства в энергосбережение, это простой и понятный вклад без лишних усилий.', 'Потом можно включить энергосбережение на устройствах, это даёт спокойный и понятный эффект.', 'А дальше просто оставь устройства в энергосбережении, это лёгкий и полезный шаг.'])}"
        )

    if any(word in lowercase for word in ("пластик", "упаков", "бутыл", "пакет")):
        return (
            f"{_pick_variant(seed, ['На сегодня хороший шаг без пластика такой:', 'Если брать пластик, я бы выбрал вот это:', 'По пластику самый жизненный вариант сейчас:'])} использовать одну многоразовую бутылку или кружку и не брать лишний пакет. "
            f"{_pick_variant(seed, ['Это небольшой шаг, но он хорошо усиливает регулярность и вклад.', 'Шаг маленький, но для ритма он очень рабочий.', 'Выглядит просто, но именно такие вещи хорошо закрепляются.'])}"
        )

    if any(word in lowercase for word in ("отход", "мусор", "сортир", "переработ")):
        return (
            f"{_pick_variant(seed, ['Если хочешь полезный шаг прямо сегодня,', 'По отходам можно начать очень приземлённо:', 'Тут лучше всего работает простой вариант:'])} начни с сортировки того, что уже есть дома: бумага, пластик, смешанные отходы. "
            f"{_pick_variant(seed, ['Это даёт понятный результат и хорошо дополняет другие привычки.', 'Такой шаг сразу ощущается как что-то реальное.', 'Это спокойный и очень понятный формат действия.'])}"
        )

    if any(word in lowercase for word in ("мотивац", "не хочу", "лень", "сложно")):
        focus = weakest_category or suggested_category
        return (
            f"{_pick_variant(seed, ['Не тащи всё сразу.', 'Лучше не перегружать себя.', 'Тут не нужно делать много.'])} "
            f"Выбери одну простую вещь, например из категории «{focus}», и закрой её спокойно за 5 минут. "
            f"{_pick_variant(seed, ['В EcoIZ правда лучше работает ритм, а не идеальность.', 'Здесь важнее ритм, чем идеальный результат.', 'Лучше маленький реальный шаг, чем большой план без сил.'])}"
        )

    if any(word in lowercase for word in ("как", "почему", "зачем", "что")):
        return (
            f"{_pick_variant(seed, ['Если коротко:', 'По сути:', 'Если по-простому:'])} сейчас логичнее всего дать чуть больше внимания категории «{suggested_category}». "
            f"Но лучше не распыляться: выбери один понятный шаг и на нём остановись."
        )

    return (
        f"Сейчас логичнее всего попробовать что-то из категории «{suggested_category}». "
        f"{last_activity_line} {_pick_variant(seed, ['Если хочешь, подберу варианты под дом, прогулку, воду, энергию или пластик.', 'Могу быстро предложить варианты под твой день: дома, на прогулке или по конкретной категории.', 'Если надо, сразу дам несколько вариантов под твою ситуацию.'])}"
    )


def _is_too_generic_response(text: str) -> bool:
    normalized = " ".join(text.lower().split())
    generic_markers = [
        "если коротко: начни с самого простого практического шага",
        "если хочешь, уточни вопрос, и я отвечу точнее",
        "напиши вопрос чуть точнее",
    ]
    return any(marker in normalized for marker in generic_markers)


def _is_low_quality_model_response(user_text: str, response_text: str) -> bool:
    normalized_user = " ".join(user_text.lower().split())
    normalized_response = " ".join(response_text.lower().split())

    awkward_markers = [
        "давайте посмотрим в конкретности",
        "улучшить баланс",
        "это подойдет для",
        "сработает для твоего",
        "для твоего «своей активности»",
        "наслаждаться природой",
        "судя по твоим активностям",
        "если смотреть на твои действия",
        "если опираться на твой ритм",
    ]
    if any(marker in normalized_response for marker in awkward_markers):
        return True

    if len(normalized_user.split()) <= 4 and len(normalized_response.split()) > 45:
        return True

    if _contains_any(normalized_user, "нет что", "что-то другое", "что то другое", "другое", "не это"):
        if not _contains_any(
            normalized_response,
            "друг",
            "тогда",
            "окей",
            "хорошо",
            "можно",
            "вместо",
        ):
            return True

    if _contains_any(normalized_user, "гулять", "погулять", "иду гулять", "выйти"):
        if not _contains_any(
            normalized_response,
            "гуля",
            "пеш",
            "пройти",
            "прогул",
            "бутыл",
            "однораз",
        ):
            return True

    return False


def _fmt_dt(value: datetime) -> str:
    return value.strftime("%Y-%m-%d")


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def _activities_summary(user: User, limit: int) -> str:
    activities = sorted(user.activities, key=lambda item: _as_utc(item.created_at), reverse=True)[:limit]
    if not activities:
        return "Нет записанных активностей."
    return "\n".join(
        f"- {_fmt_dt(item.created_at)} | {item.title} | категория: {item.category} | "
        f"баллы: {item.points} | co2Saved: {item.co2_saved}"
        for item in activities
    )


def _challenges_summary(user: User, limit: int) -> str:
    items = sorted(
        user.user_challenges,
        key=lambda item: (item.is_completed, item.challenge.title),
    )[:limit]
    if not items:
        return "Нет челленджей."
    lines: list[str] = []
    for item in items:
        status = "completed" if item.is_completed else "active"
        lines.append(
            f"- {item.challenge.title} | {item.current_count}/{item.challenge.target_count} | "
            f"status: {status} | reward: {item.challenge.reward_points}"
        )
    return "\n".join(lines)


def _posts_summary(user: User, limit: int) -> str:
    posts = sorted(user.posts, key=lambda item: _as_utc(item.created_at), reverse=True)[:limit]
    if not posts:
        return "Нет постов."
    return "\n".join(
        f"- {_fmt_dt(item.created_at)} | {item.text[:120]}"
        for item in posts
    )


def _user_analytics_summary(user: User) -> str:
    activities = sorted(user.activities, key=lambda item: _as_utc(item.created_at))
    if not activities:
        return (
            "- recordedActivities: 0\n"
            "- adviceMode: onboarding\n"
            "- focus: начать с 1-2 простых действий и сформировать первую серию"
        )

    now = datetime.now(timezone.utc)
    last_7_days = now - timedelta(days=7)
    last_30_days = now - timedelta(days=30)

    category_counts: dict[str, int] = defaultdict(int)
    category_points: dict[str, int] = defaultdict(int)
    category_co2: dict[str, float] = defaultdict(float)
    active_days: set[datetime.date] = set()
    last_week_points = 0
    last_month_points = 0
    last_week_co2 = 0.0

    for item in activities:
        created_at = _as_utc(item.created_at)
        category_counts[item.category] += 1
        category_points[item.category] += item.points
        category_co2[item.category] += item.co2_saved
        active_days.add(created_at.date())
        if created_at >= last_7_days:
            last_week_points += item.points
            last_week_co2 += item.co2_saved
        if created_at >= last_30_days:
            last_month_points += item.points

    strongest_category = max(category_counts.items(), key=lambda value: (value[1], category_points[value[0]]))[0]
    weakest_category = min(category_counts.items(), key=lambda value: (value[1], category_points[value[0]]))[0]
    avg_points_per_activity = user.points / max(len(activities), 1)
    avg_co2_per_activity = user.co2_saved_total / max(len(activities), 1)
    recent_categories = [item.category for item in activities if _as_utc(item.created_at) >= last_7_days]
    unique_recent_categories = sorted(set(recent_categories))
    consistency = round(len(active_days) / max((activities[-1].created_at.date() - activities[0].created_at.date()).days + 1, 1), 2)

    top_categories = sorted(
        category_counts.items(),
        key=lambda value: (-value[1], -category_points[value[0]], value[0]),
    )[:3]
    top_categories_text = ", ".join(
        f"{name}: {count} активн., {category_points[name]} очк., {category_co2[name]:.2f} CO2"
        for name, count in top_categories
    )

    return "\n".join(
        [
            f"- recordedActivities: {len(activities)}",
            f"- activeDays: {len(active_days)}",
            f"- currentStreakDays: {user.streak_days}",
            f"- totalPoints: {user.points}",
            f"- totalCo2Saved: {user.co2_saved_total:.2f}",
            f"- pointsLast7Days: {last_week_points}",
            f"- pointsLast30Days: {last_month_points}",
            f"- co2Last7Days: {last_week_co2:.2f}",
            f"- avgPointsPerActivity: {avg_points_per_activity:.1f}",
            f"- avgCo2PerActivity: {avg_co2_per_activity:.2f}",
            f"- strongestCategory: {strongest_category}",
            f"- weakestCategory: {weakest_category}",
            f"- recentCategoryCoverage: {', '.join(unique_recent_categories) if unique_recent_categories else 'нет'}",
            f"- consistencyIndex: {consistency}",
            f"- topCategories: {top_categories_text}",
        ]
    )


def _user_impact_summary(user: User) -> str:
    claimed = sum(1 for item in user.user_challenges if item.claimed_at is not None)
    completed = sum(1 for item in user.user_challenges if item.is_completed)
    pending_claim = max(completed - claimed, 0)
    last_activity = max(user.activities, key=lambda item: _as_utc(item.created_at), default=None)
    return "\n".join(
        [
            f"- completedChallenges: {completed}",
            f"- claimedChallenges: {claimed}",
            f"- pendingChallengeClaims: {pending_claim}",
            f"- postsCreated: {len(user.posts)}",
            f"- lastActivityDate: {_fmt_dt(last_activity.created_at) if last_activity else 'нет'}",
            f"- contributionSummary: {user.co2_saved_total:.2f} CO2 saved and {user.points} points earned",
        ]
    )


def _build_prompt(user: User, text: str) -> str:
    display_name = user.full_name.strip() or user.username
    return f"""
Пользователь:
- name: {display_name}
- username: {user.username}
- points: {user.points}
- streakDays: {user.streak_days}
- co2SavedTotal: {user.co2_saved_total}

Последние активности:
{_activities_summary(user, 6)}

Челленджи:
{_challenges_summary(user, 5)}

Последние посты:
{_posts_summary(user, 3)}

Аналитика пользователя:
{_user_analytics_summary(user)}

Вклад пользователя:
{_user_impact_summary(user)}
""".strip() + f"\n\nСообщение пользователя:\n{text.strip()}"


def _conversation_messages(user: User, text: str, history_limit: int) -> list[dict[str, str]]:
    messages: list[dict[str, str]] = [
        {"role": "system", "content": DEFAULT_SYSTEM_PROMPT},
        {
            "role": "system",
            "content": (
                "Ниже контекст пользователя EcoIZ. Используй его только как вспомогательный персональный контекст. "
                "Не перечисляй всё подряд, если это не помогает ответу. Если пользователь спрашивает совет, "
                "опирайся на реальные категории, активность, серию, вклад и слабые места пользователя.\n\n"
                f"{_build_prompt(user, text)}"
            ),
        },
    ]

    history = sorted(user.chat_messages, key=lambda item: _as_utc(item.created_at))[-history_limit:]
    for item in history:
        if not item.text.strip():
            continue
        role = "assistant" if item.role == "assistant" else "user"
        messages.append({"role": role, "content": item.text.strip()})

    messages.append({"role": "user", "content": text.strip()})
    return messages


def _openrouter_response(messages: list[dict[str, str]]) -> str | None:
    settings = get_settings()
    if not settings.openrouter_api_key:
        return None

    response = httpx.post(
        "https://openrouter.ai/api/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openrouter_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.openrouter_model,
            "messages": messages,
            "temperature": settings.ai_temperature,
            "max_tokens": settings.ai_max_tokens,
        },
        timeout=settings.ai_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"].strip()
    return content or None


def _openai_response(messages: list[dict[str, str]]) -> str | None:
    settings = get_settings()
    if not settings.openai_api_key:
        return None

    response = httpx.post(
        "https://api.openai.com/v1/chat/completions",
        headers={
            "Authorization": f"Bearer {settings.openai_api_key}",
            "Content-Type": "application/json",
        },
        json={
            "model": settings.openai_model,
            "messages": messages,
            "temperature": settings.ai_temperature,
            "max_tokens": settings.ai_max_tokens,
        },
        timeout=settings.ai_timeout_seconds,
    )
    response.raise_for_status()
    payload = response.json()
    content = payload["choices"][0]["message"]["content"].strip()
    return content or None


def ai_response(text: str, *, user: User | None = None) -> str:
    settings = get_settings()
    if user is None:
        return _fallback_response(text)

    messages = _conversation_messages(user, text, settings.ai_history_limit)
    personalized_fallback = _personalized_fallback_response(text, user)

    if settings.ai_provider == "openrouter" and not settings.openrouter_api_key:
        return personalized_fallback
    if settings.ai_provider == "openai" and not settings.openai_api_key:
        return personalized_fallback

    try:
        if settings.ai_provider == "openai":
            content = _openai_response(messages)
        else:
            content = _openrouter_response(messages)
        if not content or _is_too_generic_response(content) or _is_low_quality_model_response(text, content):
            return personalized_fallback
        return content
    except Exception:
        return personalized_fallback
