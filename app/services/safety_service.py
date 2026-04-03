RED_FLAGS = ['chest pain', 'shortness of breath', 'suicidal', 'stroke', 'unconscious']


def medical_disclaimer(lang: str = 'en') -> str:
    if lang == 'fa':
        return '⚠️ این پاسخ جایگزین پزشک نیست. در شرایط اورژانسی با خدمات اورژانس تماس بگیرید.'
    return '⚠️ This information is educational and not a medical diagnosis. Call emergency services for urgent symptoms.'


def detect_red_flags(text: str) -> list[str]:
    lower = text.lower()
    return [flag for flag in RED_FLAGS if flag in lower]
