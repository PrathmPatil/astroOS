"""Shared Vedic astrology constants."""

from __future__ import annotations

SIGNS: list[str] = [
    "Aries",
    "Taurus",
    "Gemini",
    "Cancer",
    "Leo",
    "Virgo",
    "Libra",
    "Scorpio",
    "Sagittarius",
    "Capricorn",
    "Aquarius",
    "Pisces",
]

SIGNS_MR: list[str] = [
    "मेष",
    "वृषभ",
    "मिथुन",
    "कर्क",
    "सिंह",
    "कन्या",
    "तुला",
    "वृश्चिक",
    "धनु",
    "मकर",
    "कुंभ",
    "मीन",
]

SIGNS_HI: list[str] = [
    "मेष",
    "वृषभ",
    "मिथुन",
    "कर्क",
    "सिंह",
    "कन्या",
    "तुला",
    "वृश्चिक",
    "धनु",
    "मकर",
    "कुंभ",
    "मीन",
]

NAKSHATRAS: list[str] = [
    "Ashwini",
    "Bharani",
    "Krittika",
    "Rohini",
    "Mrigashira",
    "Ardra",
    "Punarvasu",
    "Pushya",
    "Ashlesha",
    "Magha",
    "Purva Phalguni",
    "Uttara Phalguni",
    "Hasta",
    "Chitra",
    "Swati",
    "Vishakha",
    "Anuradha",
    "Jyeshtha",
    "Mula",
    "Purva Ashadha",
    "Uttara Ashadha",
    "Shravana",
    "Dhanishta",
    "Shatabhisha",
    "Purva Bhadrapada",
    "Uttara Bhadrapada",
    "Revati",
]

NAKSHATRA_LORDS: list[str] = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
] * 3

# Vimshottari dasha years
VIMSHOTTARI_YEARS: dict[str, int] = {
    "Ketu": 7,
    "Venus": 20,
    "Sun": 6,
    "Moon": 10,
    "Mars": 7,
    "Rahu": 18,
    "Jupiter": 16,
    "Saturn": 19,
    "Mercury": 17,
}

VIMSHOTTARI_ORDER: list[str] = [
    "Ketu",
    "Venus",
    "Sun",
    "Moon",
    "Mars",
    "Rahu",
    "Jupiter",
    "Saturn",
    "Mercury",
]

PLANET_KEYS: list[str] = [
    "Sun",
    "Moon",
    "Mars",
    "Mercury",
    "Jupiter",
    "Venus",
    "Saturn",
    "Rahu",
    "Ketu",
    "Uranus",
    "Neptune",
    "Pluto",
]

# Sign lords (0=Aries … 11=Pisces)
SIGN_LORDS: list[str] = [
    "Mars",
    "Venus",
    "Mercury",
    "Moon",
    "Sun",
    "Mercury",
    "Venus",
    "Mars",
    "Jupiter",
    "Saturn",
    "Saturn",
    "Jupiter",
]

# Exaltation / debilitation signs (0-based)
EXALTATION: dict[str, int] = {
    "Sun": 0,  # Aries
    "Moon": 1,  # Taurus
    "Mars": 9,  # Capricorn
    "Mercury": 5,  # Virgo
    "Jupiter": 3,  # Cancer
    "Venus": 11,  # Pisces
    "Saturn": 6,  # Libra
    "Rahu": 2,  # Gemini (common school)
    "Ketu": 8,  # Sagittarius (common school)
}

DEBILITATION: dict[str, int] = {
    "Sun": 6,
    "Moon": 7,
    "Mars": 3,
    "Mercury": 11,
    "Jupiter": 9,
    "Venus": 5,
    "Saturn": 0,
    "Rahu": 8,
    "Ketu": 2,
}

OWN_SIGNS: dict[str, list[int]] = {
    "Sun": [4],
    "Moon": [3],
    "Mars": [0, 7],
    "Mercury": [2, 5],
    "Jupiter": [8, 11],
    "Venus": [1, 6],
    "Saturn": [9, 10],
}

# Combustion orbs (degrees from Sun) — classical approximations
COMBUSTION_ORB: dict[str, float] = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,  # 12 if retrograde — handled in engine
    "Jupiter": 11.0,
    "Venus": 10.0,  # 8 if retrograde
    "Saturn": 15.0,
}

# Vargas (divisional charts) — division factor
VARGAS: dict[str, int] = {
    "D1": 1,
    "D2": 2,
    "D3": 3,
    "D4": 4,
    "D5": 5,  # Panchamsha (some schools use 5)
    "D6": 6,
    "D7": 7,
    "D8": 8,
    "D9": 9,
    "D10": 10,
    "D11": 11,
    "D12": 12,
    "D16": 16,
    "D20": 20,
    "D24": 24,
    "D27": 27,
    "D30": 30,
    "D40": 40,
    "D45": 45,
    "D60": 60,
}

DISCLAIMER_EN = (
    "This analysis follows traditional Vedic astrology principles and classical texts. "
    "It is for educational and cultural purposes only and is not a scientifically proven "
    "prediction, nor medical, financial, or legal advice."
)

DISCLAIMER_MR = (
    "ही विश्लेषण पारंपरिक वैदिक ज्योतिष नियम व शास्त्रांनुसार आहे. "
    "हे केवळ शैक्षणिक व सांस्कृतिक हेतूसाठी आहे; वैज्ञानिकरीत्या सिद्ध भविष्यवाणी नाही, "
    "तसेच वैद्यकीय, आर्थिक किंवा कायदेशीर सल्ला नाही."
)

DISCLAIMER_HI = (
    "यह विश्लेषण पारंपरिक वैदिक ज्योतिष सिद्धांतों पर आधारित है। "
    "यह केवल शैक्षणिक और सांस्कृतिक उद्देश्य के लिए है; वैज्ञानिक रूप से सिद्ध भविष्यवाणी नहीं है, "
    "और न ही चिकित्सा, वित्तीय या कानूनी सलाह है।"
)

DISCLAIMER_GU = (
    "આ વિશ્લેષણ પારંપરિક વૈદિક જ્યોતિષ સિદ્ધાંતો પર આધારિત છે. "
    "ફક્ત શૈક્ષણિક/સાંસ્કૃતિક હેતુ માટે; વૈજ્ઞાનિક ભવિષ્યવાણી કે તબીબી/નાણાકીય/કાનૂની સલાહ નથી."
)

DISCLAIMER_KN = (
    "ಇದು ಪಾರಂಪರಿಕ ವೈದಿಕ ಜ್ಯೋತಿಷ ಸಿದ್ಧಾಂತಗಳ ಆಧಾರಿತ ವಿಶ್ಲೇಷಣೆ. "
    "ಕೇವಲ ಶೈಕ್ಷಣಿಕ/ಸಾಂಸ್ಕೃತಿಕ ಉದ್ದೇಶಕ್ಕೆ; ವೈಜ್ಞಾನಿಕ ಭವಿಷ್ಯವಾಣಿ ಅಥವಾ ವೈದ್ಯಕೀಯ/ಹಣಕಾಸು/ಕಾನೂನು ಸಲಹೆ ಅಲ್ಲ."
)

DISCLAIMER_TA = (
    "இது பாரம்பரிய வேத ஜோதிட கொள்கைகளின் அடிப்படையிலான பகுப்பாய்வு. "
    "கல்வி/கலாச்சார நோக்கத்திற்கு மட்டும்; அறிவியல் முன்னறிவிப்பு அல்ல, மருத்துவ/நிதி/சட்ட ஆலோசனையும் அல்ல."
)

DISCLAIMER_TE = (
    "ఇది సాంప్రదాయ వైదిక జ్యోతిష సూత్రాల ఆధారిత విశ్లేషణ. "
    "కేవలం విద్యా/సాంస్కృతిక ప్రయోజనం; శాస్త్రీయ భవిష్యవాణి కాదు, వైద్య/ఆర్థిక/చట్ట సలహా కాదు."
)
