"""AI Engine — explain ONLY. Never invent predictions. Multi-language."""

from __future__ import annotations

from typing import Any

from app.core.constants import (
    DISCLAIMER_EN,
    DISCLAIMER_GU,
    DISCLAIMER_HI,
    DISCLAIMER_KN,
    DISCLAIMER_MR,
    DISCLAIMER_TA,
    DISCLAIMER_TE,
)

SYSTEM = {
    "en": "AstroOS explainer: only rephrase evidence+rules+sources. Never invent.",
    "mr": "फक्त पुरावे/नियम/ग्रंथ स्पष्ट करा. नवीन भविष्य शोधू नका.",
    "hi": "केवल साक्ष्य/नियम/ग्रंथ समझाएँ। नई भविष्यवाणी न गढ़ें।",
    "gu": "ફક્ત પુરાવા/નિયમ/ગ્રંથ સમજાવો. નવી આગાહી ન બનાવો.",
    "kn": "ಪುರಾವೆ/ನಿಯಮ/ಗ್ರಂಥ ಮಾತ್ರ ವಿವರಿಸಿ. ಹೊಸ ಭವಿಷ್ಯ ಸೃಷ್ಟಿಸಬೇಡಿ.",
    "ta": "சான்று/விதி/நூல் மட்டும் விளக்கவும். புதிய கணிப்பு உருவாக்க வேண்டாம்.",
    "te": "సాక్ష్యం/నియమం/గ్రంథం మాత్రమే వివరించండి. కొత్త భవిష్యం కల్పించవద్దు.",
}

# Short vernacular labels for common conclusion keys (evidence-backed display only)
_KEY_LABELS: dict[str, dict[str, str]] = {
    "marriage_delay": {
        "en": "Marriage delay / later maturity theme",
        "mr": "विवाह विलंब / नंतर परिपक्वता — पारंपरिक सूचक",
        "hi": "विवाह विलंब / बाद में परिपक्वता — पारंपरिक संकेत",
        "gu": "લગ્ન વિલંબ / પછી પરિપક્વતા — પારંપરિક સંકેત",
        "kn": "ವಿವಾಹ ವಿಳಂಬ / ನಂತರ ಪರಿಪಕ್ವತೆ — ಪಾರಂಪರಿಕ ಸೂಚಕ",
        "ta": "திருமண தாமதம் / பின்னர் முதிர்ச்சி — பாரம்பரிய குறிப்பு",
        "te": "వివాహ విలంబం / తర్వాత పరిపక్వత — సాంప్రదాయ సూచన",
    },
    "marriage_supportive": {
        "en": "Supportive marriage / partnership theme",
        "mr": "विवाह / नातेसंबंधात सहाय्यक सूचक",
        "hi": "विवाह / संबंध में सहायक संकेत",
        "gu": "લગ્ન / સંબંધમાં સહાયક સંકેત",
        "kn": "ವಿವಾಹ / ಸಂಬಂಧದಲ್ಲಿ ಸಹಾಯಕ ಸೂಚಕ",
        "ta": "திருமண / உறவில் ஆதரவு குறிப்பு",
        "te": "వివాహ / సంబంధంలో సహాయక సూచన",
    },
    "spouse_navamsa_active": {
        "en": "Spouse themes active in Navamsa",
        "mr": "नवमांशात जोडीदार संबंधित सूचक सक्रिय",
        "hi": "नवमांश में जीवनसाथी संबंधी संकेत सक्रिय",
        "gu": "નવમાંશમાં જીવનસાથી સંબંધિત સંકેત સક્રિય",
        "kn": "ನವಾಂಶದಲ್ಲಿ ಜೀವನಸಂಗಾತಿ ಸೂಚಕ ಸಕ್ರಿಯ",
        "ta": "நவாம்சத்தில் வாழ்க்கைத் துணை குறிப்பு செயலில்",
        "te": "నవాంశలో జీవిత భాగస్వామి సూచన చురుకు",
    },
}


def _disclaimer(lang: str) -> str:
    return {
        "en": DISCLAIMER_EN,
        "mr": DISCLAIMER_MR,
        "hi": DISCLAIMER_HI,
        "gu": DISCLAIMER_GU,
        "kn": DISCLAIMER_KN,
        "ta": DISCLAIMER_TA,
        "te": DISCLAIMER_TE,
    }.get(lang, DISCLAIMER_EN)


def _localized_title(conclusion: dict[str, Any], language: str) -> str:
    key = conclusion.get("conclusion_key") or ""
    labels = _KEY_LABELS.get(key)
    if labels:
        return labels.get(language) or labels["en"]
    return conclusion.get("title") or key.replace("_", " ").title()


def _source_snip(sources: list[dict[str, Any]], language: str) -> str:
    field = {
        "en": "english",
        "mr": "marathi",
        "hi": "hindi",
        "gu": "gujarati",
        "kn": "kannada",
        "ta": "tamil",
        "te": "telugu",
    }.get(language, "english")
    for s in sources:
        text = s.get(field) or s.get("english")
        if text:
            book = s.get("text") or "classical text"
            return f"{book}: {text}"
    return ""


def _final_conclusion(
    conclusion: dict[str, Any],
    language: str,
    conf: float,
    title_local: str,
    books: list[str],
) -> str:
    """Plain-language final verdict — only restates matched evidence; never invents."""
    snip = _source_snip(conclusion.get("sources") or [], language)
    n_ev = len(conclusion.get("evidence") or [])
    n_rules = len(conclusion.get("used_rules") or [])
    bk = ", ".join(books) if books else "—"
    templates = {
        "en": (
            f"Final conclusion: {title_local} "
            f"(confidence ≈ {conf}%). "
            f"Based on {n_ev} chart evidence check(s) and {n_rules} matched rule(s) "
            f"citing {bk}. "
            f"{snip + ' ' if snip else ''}"
            f"This is a traditional interpretive theme — not a definite prediction."
        ),
        "mr": (
            f"अंतिम निष्कर्ष: {title_local} "
            f"(विश्वासार्हता ≈ {conf}%). "
            f"हे {n_ev} पुरावा तपासणी व {n_rules} जुळलेल्या नियमांवर आधारित आहे "
            f"(संदर्भ: {bk}). "
            f"{snip + ' ' if snip else ''}"
            f"हे पारंपरिक अर्थ आहे — निश्चित भविष्यवाणी नाही."
        ),
        "hi": (
            f"अंतिम निष्कर्ष: {title_local} "
            f"(विश्वास ≈ {conf}%). "
            f"यह {n_ev} साक्ष्य जाँच और {n_rules} मेल खाते नियमों पर आधारित है "
            f"(संदर्भ: {bk}). "
            f"{snip + ' ' if snip else ''}"
            f"यह पारंपरिक व्याख्या है — निश्चित भविष्यवाणी नहीं।"
        ),
        "gu": (
            f"અંતિમ નિષ્કર્ષ: {title_local} "
            f"(વિશ્વાસ ≈ {conf}%). "
            f"{n_ev} પુરાવા અને {n_rules} નિયમો પર આધારિત (સંદર્ભ: {bk}). "
            f"{snip + ' ' if snip else ''}"
            f"પારંપરિક અર્થ — નિશ્ચિત ભવિષ્યવાણી નથી."
        ),
        "kn": (
            f"ಅಂತಿಮ ತೀರ್ಮಾನ: {title_local} "
            f"(ವಿಶ್ವಾಸ ≈ {conf}%). "
            f"{n_ev} ಪುರಾವೆ ಮತ್ತು {n_rules} ನಿಯಮಗಳ ಆಧಾರ (ಉಲ್ಲೇಖ: {bk}). "
            f"{snip + ' ' if snip else ''}"
            f"ಪಾರಂಪರಿಕ ವ್ಯಾಖ್ಯಾನ — ನಿಶ್ಚಿತ ಭವಿಷ್ಯವಾಣಿ ಅಲ್ಲ."
        ),
        "ta": (
            f"இறுதி முடிவு: {title_local} "
            f"(நம்பிக்கை ≈ {conf}%). "
            f"{n_ev} சான்றுகளும் {n_rules} விதிகளும் அடிப்படை (ஆதாரம்: {bk}). "
            f"{snip + ' ' if snip else ''}"
            f"பாரம்பரிய விளக்கம் — உறுதியான கணிப்பு அல்ல."
        ),
        "te": (
            f"చివరి నిర్ణయం: {title_local} "
            f"(విశ్వాసం ≈ {conf}%). "
            f"{n_ev} సాక్ష్యాలు, {n_rules} నియమాల ఆధారం (సూచన: {bk}). "
            f"{snip + ' ' if snip else ''}"
            f"సాంప్రదాయ వ్యాఖ్యానం — ఖచ్చిత భవిష్యవాణి కాదు."
        ),
    }
    return templates.get(language, templates["en"])


def explain_from_evidence(
    conclusion: dict[str, Any],
    language: str = "mr",
) -> dict[str, Any]:
    conf = conclusion.get("confidence", 0)
    title = conclusion.get("title", "")
    title_local = _localized_title(conclusion, language)
    evidence = conclusion.get("evidence", [])
    rules = conclusion.get("used_rules", [])
    sources = conclusion.get("sources", [])
    books = sorted({s.get("text") for s in sources if s.get("text")})
    ev = "; ".join(evidence) if evidence else "—"
    ru = ", ".join(rules)
    bk = ", ".join(books) if books else "—"
    final = _final_conclusion(conclusion, language, conf, title_local, books)

    templates = {
        "en": (
            f"«{title_local}» is derived from AstroOS matched evidence (confidence ≈ {conf}%). "
            f"Used rules: {ru}. Evidence: {ev}. Sources: {bk}. "
            f"Traditional interpretive analysis, not a definite prediction. {_disclaimer('en')}"
        ),
        "mr": (
            f"«{title_local}» AstroOS पुराव्यांवर आधारित (विश्वास ~{conf}%). "
            f"नियम: {ru}. पुरावे: {ev}. ग्रंथ: {bk}. "
            f"पारंपरिक अर्थ; निश्चित भविष्य नाही. {_disclaimer('mr')}"
        ),
        "hi": (
            f"«{title_local}» AstroOS साक्ष्यों पर आधारित (विश्वास ~{conf}%). "
            f"नियम: {ru}. साक्ष्य: {ev}. ग्रंथ: {bk}. "
            f"पारंपरिक व्याख्या; निश्चित भविष्य नहीं. {_disclaimer('hi')}"
        ),
        "gu": (
            f"«{title_local}» AstroOS પુરાવા પર આધારિત (વિશ્વાસ ~{conf}%). "
            f"નિયમ: {ru}. પુરાવા: {ev}. ગ્રંથ: {bk}. {_disclaimer('gu')}"
        ),
        "kn": (
            f"«{title_local}» AstroOS ಪುರಾವೆ ಆಧಾರಿತ (ವಿಶ್ವಾಸ ~{conf}%). "
            f"ನಿಯಮ: {ru}. ಪುರಾವೆ: {ev}. ಗ್ರಂಥ: {bk}. {_disclaimer('kn')}"
        ),
        "ta": (
            f"«{title_local}» AstroOS சான்றடிப்படையில் (நம்பிக்கை ~{conf}%). "
            f"விதிகள்: {ru}. சான்று: {ev}. நூல்: {bk}. {_disclaimer('ta')}"
        ),
        "te": (
            f"«{title_local}» AstroOS సాక్ష్యం ఆధారంగా (విశ్వాసం ~{conf}%). "
            f"నియమాలు: {ru}. సాక్ష్యం: {ev}. గ్రంథం: {bk}. {_disclaimer('te')}"
        ),
    }
    text = templates.get(language, templates["en"])

    return {
        "language": language,
        "provider": "astroos_evidence_explainer",
        "invented": False,
        "inputs_used": ["evidence", "matched_rules", "classical_sources", "confidence"],
        "title_localized": title_local,
        "final_conclusion": final,
        "explanation": text,
        "system_constraint": SYSTEM.get(language, SYSTEM["en"]),
        "disclaimer": _disclaimer(language),
    }


async def maybe_llm_rephrase(
    conclusion: dict[str, Any],
    language: str = "mr",
) -> dict[str, Any]:
    return explain_from_evidence(conclusion, language)
