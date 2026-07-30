"""Layer 3 — AI Interpretation."""

from __future__ import annotations

from app.core.constants import DISCLAIMER_EN, DISCLAIMER_HI, DISCLAIMER_MR


def disclaimer(lang: str) -> str:
    return {"en": DISCLAIMER_EN, "mr": DISCLAIMER_MR, "hi": DISCLAIMER_HI}.get(
        lang, DISCLAIMER_EN
    )


SYSTEM_PROMPTS = {
    "en": (
        "You are AstroSutra AI, an assistant that explains Vedic astrology charts. "
        "Only interpret using traditional Jyotish concepts. Never claim scientific proof. "
        "Always remind the reader that meanings are traditional interpretations."
    ),
    "mr": (
        "तुम्ही AstroSutra AI आहात. वैदिक ज्योतिष चार्ट पारंपरिक नियमांनुसार समजावून सांगा. "
        "वैज्ञानिक सिद्धता सांगू नका. नेहमी नमूद करा की हे पारंपरिक अर्थ आहेत."
    ),
    "hi": (
        "आप AstroSutra AI हैं। वैदिक ज्योतिष चार्ट को पारंपरिक नियमों से समझाएँ। "
        "वैज्ञानिक प्रमाण का दावा न करें। सदैव उल्लेख करें कि ये पारंपरिक अर्थ हैं।"
    ),
}


FOCUS_HINTS = {
    "overview": {
        "en": "Give a balanced overview of Lagna, Moon, and key yogas/doshas.",
        "mr": "लग्न, चंद्र आणि मुख्य योग/दोष यांचा समतोल आढावा द्या.",
        "hi": "लग्न, चंद्र और मुख्य योग/दोष का संतुलित अवलोकन दें।",
    },
    "career": {
        "en": "Focus on 10th house, dasha, and career indicators traditionally used.",
        "mr": "१०वा भाव, दशा आणि पारंपरिक करिअर संकेतांवर लक्ष केंद्रित करा.",
        "hi": "दसवें भाव, दशा और पारंपरिक करियर संकेतों पर ध्यान दें।",
    },
    "marriage": {
        "en": "Focus on 7th house, Venus, Jupiter, Navamsa themes (traditionally).",
        "mr": "७वा भाव, शुक्र, गुरु आणि नवांश या पारंपरिक विषयांवर लक्ष द्या.",
        "hi": "सप्तम भाव, शुक्र, गुरु और नवमांश पर पारंपरिक दृष्टि से लिखें।",
    },
    "health": {
        "en": "Discuss traditional health-sensitive tendencies only, not medical advice.",
        "mr": "फक्त पारंपरिक आरोग्य-संवेदनशील प्रवृत्ती; वैद्यकीय सल्ला नाही.",
        "hi": "केवल पारंपरिक स्वास्थ्य प्रवृत्तियाँ; चिकित्सा सलाह नहीं।",
    },
    "wealth": {
        "en": "Discuss 2nd/11th houses and dhana yogas in traditional terms.",
        "mr": "२रा/११वा भाव व धन योग पारंपरिक पद्धतीने सांगा.",
        "hi": "द्वितीय/एकादश भाव व धन योग पारंपरिक रूप से बताएँ।",
    },
    "dasha": {
        "en": "Explain current mahadasha/antardasha themes traditionally.",
        "mr": "सद्य महादशा/अंतर्दशा पारंपरिक अर्थाने समजावा.",
        "hi": "वर्तमान महादशा/अंतर्दशा को पारंपरिक अर्थ में समझाएँ।",
    },
}


def build_prompt(
    language: str,
    focus: str,
    chart_summary: dict,
) -> tuple[str, str]:
    system = SYSTEM_PROMPTS.get(language, SYSTEM_PROMPTS["en"])
    hint = FOCUS_HINTS.get(focus, FOCUS_HINTS["overview"]).get(
        language, FOCUS_HINTS["overview"]["en"]
    )
    user = (
        f"Focus: {hint}\n"
        f"Chart summary JSON:\n{chart_summary}\n"
        f"End with this disclaimer:\n{disclaimer(language)}"
    )
    return system, user


def rule_based_fallback(language: str, focus: str, chart_summary: dict) -> str:
    """Deterministic interpretation when LLM is unavailable."""
    lagna = chart_summary.get("lagna", {})
    moon = chart_summary.get("moon", {})
    dasha = chart_summary.get("current_dasha", {})

    if language == "mr":
        text = (
            f"लग्न: {lagna.get('sign_mr') or lagna.get('sign')} "
            f"(स्वामी: {lagna.get('lord')}). "
            f"चंद्र राशी: {moon.get('sign_mr') or moon.get('sign')}, "
            f"नक्षत्र: {moon.get('nakshatra')} (पाद {moon.get('pada')}). "
            f"सद्य दशा: {dasha.get('mahadasha')} / {dasha.get('antardasha')}. "
            f"फोकस: {focus}. "
        )
    elif language == "hi":
        text = (
            f"लग्न: {lagna.get('sign')} (स्वामी: {lagna.get('lord')}). "
            f"चंद्र राशि: {moon.get('sign')}, नक्षत्र: {moon.get('nakshatra')} "
            f"(पाद {moon.get('pada')}). "
            f"वर्तमान दशा: {dasha.get('mahadasha')} / {dasha.get('antardasha')}. "
            f"फोकस: {focus}. "
        )
    else:
        text = (
            f"Ascendant: {lagna.get('sign')} (lord: {lagna.get('lord')}). "
            f"Moon sign: {moon.get('sign')}, nakshatra: {moon.get('nakshatra')} "
            f"(pada {moon.get('pada')}). "
            f"Current dasha: {dasha.get('mahadasha')} / {dasha.get('antardasha')}. "
            f"Focus: {focus}. "
        )
    return text + "\n\n" + disclaimer(language)
