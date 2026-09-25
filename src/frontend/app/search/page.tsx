"use client";

import {
  Search,
  ArrowUpRight,
  SlidersHorizontal,
  BookOpen,
  ChevronRight,
  Languages,
} from "lucide-react";
import { useState } from "react";

/* =========================================================
   LANGUAGES
========================================================= */

const languages = [
  "English",
  "Hindi",
  "Marathi",
  "Gujarati",
  "Bengali",
  "Tamil",
  "Telugu",
  "Kannada",
  "Malayalam",
  "Punjabi",
];

/* =========================================================
   TRANSLATIONS
========================================================= */

const translations = {
  English: {
    indianStandards: "Indian Standards",
    findRight: "Find the right",
    standard: "standard.",
    description:
      "Search Indian Standards by IS code, title, or describe what you are looking for in multiple Indian languages.",
    placeholder:
      "Search IS codes, standards, or describe your requirement...",
    search: "Search",
    multilingual: "Multilingual search:",
    tenLanguages: "10 Indian Languages",
    categories: "Categories",
    allStandards: "All Standards",
    construction: "Construction",
    electrical: "Electrical",
    fireSafety: "Fire Safety",
    mechanical: "Mechanical",
    civilEngineering: "Civil Engineering",
    showing: "Showing",
    standards: "standards",
    relevance: "Relevance",
    current: "Current",
    viewStandard: "View standard",
    noStandards: "No standards found",
    tryDifferent:
      "Try a different IS code, standard name, or describe your requirement differently.",
    supportedLanguages: "Supported Languages",
  },

  Hindi: {
    indianStandards: "भारतीय मानक",
    findRight: "सही",
    standard: "मानक खोजें।",
    description:
      "IS कोड, शीर्षक या अपनी आवश्यकता का वर्णन करके भारतीय मानकों को खोजें।",
    placeholder:
      "IS कोड, मानक खोजें या अपनी आवश्यकता का वर्णन करें...",
    search: "खोजें",
    multilingual: "बहुभाषी खोज:",
    tenLanguages: "10 भारतीय भाषाएँ",
    categories: "श्रेणियाँ",
    allStandards: "सभी मानक",
    construction: "निर्माण",
    electrical: "विद्युत",
    fireSafety: "अग्नि सुरक्षा",
    mechanical: "यांत्रिक",
    civilEngineering: "सिविल इंजीनियरिंग",
    showing: "दिखाए जा रहे हैं",
    standards: "मानक",
    relevance: "प्रासंगिकता",
    current: "वर्तमान",
    viewStandard: "मानक देखें",
    noStandards: "कोई मानक नहीं मिला",
    tryDifferent:
      "कोई दूसरा IS कोड, मानक नाम या अलग तरीके से अपनी आवश्यकता लिखकर देखें।",
    supportedLanguages: "समर्थित भाषाएँ",
  },

  Marathi: {
    indianStandards: "भारतीय मानके",
    findRight: "योग्य",
    standard: "मानक शोधा.",
    description:
      "IS कोड, शीर्षक किंवा तुमच्या गरजेचे वर्णन करून भारतीय मानके शोधा.",
    placeholder:
      "IS कोड, मानक शोधा किंवा तुमच्या गरजेचे वर्णन करा...",
    search: "शोधा",
    multilingual: "बहुभाषिक शोध:",
    tenLanguages: "10 भारतीय भाषा",
    categories: "श्रेणी",
    allStandards: "सर्व मानके",
    construction: "बांधकाम",
    electrical: "विद्युत",
    fireSafety: "अग्निसुरक्षा",
    mechanical: "यांत्रिक",
    civilEngineering: "सिव्हिल इंजिनिअरिंग",
    showing: "दाखवत आहे",
    standards: "मानके",
    relevance: "संबंधितता",
    current: "सध्याचे",
    viewStandard: "मानक पहा",
    noStandards: "कोणतेही मानक सापडले नाही",
    tryDifferent:
      "वेगळा IS कोड, मानकाचे नाव किंवा तुमची गरज वेगळ्या प्रकारे लिहून पहा.",
    supportedLanguages: "समर्थित भाषा",
  },

  Gujarati: {
    indianStandards: "ભારતીય ધોરણો",
    findRight: "યોગ્ય",
    standard: "ધોરણ શોધો.",
    description:
      "IS કોડ, શીર્ષક અથવા તમારી જરૂરિયાતનું વર્ણન કરીને ભારતીય ધોરણો શોધો.",
    placeholder:
      "IS કોડ, ધોરણ શોધો અથવા તમારી જરૂરિયાતનું વર્ણન કરો...",
    search: "શોધો",
    multilingual: "બહુભાષી શોધ:",
    tenLanguages: "10 ભારતીય ભાષાઓ",
    categories: "શ્રેણીઓ",
    allStandards: "બધા ધોરણો",
    construction: "બાંધકામ",
    electrical: "વિદ્યુત",
    fireSafety: "અગ્નિ સુરક્ષા",
    mechanical: "યાંત્રિક",
    civilEngineering: "સિવિલ એન્જિનિયરિંગ",
    showing: "બતાવી રહ્યા છીએ",
    standards: "ધોરણો",
    relevance: "સુસંગતતા",
    current: "વર્તમાન",
    viewStandard: "ધોરણ જુઓ",
    noStandards: "કોઈ ધોરણ મળ્યું નથી",
    tryDifferent:
      "અલગ IS કોડ, ધોરણનું નામ અથવા તમારી જરૂરિયાત અલગ રીતે લખીને જુઓ.",
    supportedLanguages: "સમર્થિત ભાષાઓ",
  },

  Bengali: {
    indianStandards: "ভারতীয় মান",
    findRight: "সঠিক",
    standard: "মান খুঁজুন।",
    description:
      "IS কোড, শিরোনাম অথবা আপনার প্রয়োজনের বর্ণনা দিয়ে ভারতীয় মান খুঁজুন।",
    placeholder:
      "IS কোড, মান খুঁজুন অথবা আপনার প্রয়োজনের বর্ণনা দিন...",
    search: "অনুসন্ধান",
    multilingual: "বহুভাষিক অনুসন্ধান:",
    tenLanguages: "১০টি ভারতীয় ভাষা",
    categories: "বিভাগ",
    allStandards: "সমস্ত মান",
    construction: "নির্মাণ",
    electrical: "বৈদ্যুতিক",
    fireSafety: "অগ্নি নিরাপত্তা",
    mechanical: "যান্ত্রিক",
    civilEngineering: "সিভিল ইঞ্জিনিয়ারিং",
    showing: "দেখানো হচ্ছে",
    standards: "মান",
    relevance: "প্রাসঙ্গিকতা",
    current: "বর্তমান",
    viewStandard: "মান দেখুন",
    noStandards: "কোনো মান পাওয়া যায়নি",
    tryDifferent:
      "অন্য IS কোড, মানের নাম অথবা আপনার প্রয়োজন অন্যভাবে লিখে দেখুন।",
    supportedLanguages: "সমর্থিত ভাষা",
  },

  Tamil: {
    indianStandards: "இந்திய தரநிலைகள்",
    findRight: "சரியான",
    standard: "தரநிலையை கண்டறியவும்.",
    description:
      "IS குறியீடு, தலைப்பு அல்லது உங்கள் தேவையை விவரிப்பதன் மூலம் இந்திய தரநிலைகளைத் தேடுங்கள்.",
    placeholder:
      "IS குறியீடு, தரநிலையைத் தேடுங்கள் அல்லது உங்கள் தேவையை விவரிக்கவும்...",
    search: "தேடுக",
    multilingual: "பல மொழி தேடல்:",
    tenLanguages: "10 இந்திய மொழிகள்",
    categories: "வகைகள்",
    allStandards: "அனைத்து தரநிலைகள்",
    construction: "கட்டுமானம்",
    electrical: "மின்சாரம்",
    fireSafety: "தீ பாதுகாப்பு",
    mechanical: "இயந்திரம்",
    civilEngineering: "சிவில் பொறியியல்",
    showing: "காட்டப்படுகிறது",
    standards: "தரநிலைகள்",
    relevance: "தொடர்புடையது",
    current: "தற்போதைய",
    viewStandard: "தரநிலையைப் பார்க்கவும்",
    noStandards: "தரநிலைகள் எதுவும் கிடைக்கவில்லை",
    tryDifferent:
      "வேறு IS குறியீடு, தரநிலை பெயர் அல்லது உங்கள் தேவையை வேறு விதமாக உள்ளிடவும்.",
    supportedLanguages: "ஆதரிக்கப்படும் மொழிகள்",
  },

  Telugu: {
    indianStandards: "భారతీయ ప్రమాణాలు",
    findRight: "సరైన",
    standard: "ప్రమాణాన్ని కనుగొనండి.",
    description:
      "IS కోడ్, శీర్షిక లేదా మీ అవసరాన్ని వివరించడం ద్వారా భారతీయ ప్రమాణాలను శోధించండి.",
    placeholder:
      "IS కోడ్, ప్రమాణాన్ని శోధించండి లేదా మీ అవసరాన్ని వివరించండి...",
    search: "శోధించండి",
    multilingual: "బహుభాషా శోధన:",
    tenLanguages: "10 భారతీయ భాషలు",
    categories: "వర్గాలు",
    allStandards: "అన్ని ప్రమాణాలు",
    construction: "నిర్మాణం",
    electrical: "విద్యుత్",
    fireSafety: "అగ్ని భద్రత",
    mechanical: "యాంత్రిక",
    civilEngineering: "సివిల్ ఇంజినీరింగ్",
    showing: "చూపిస్తోంది",
    standards: "ప్రమాణాలు",
    relevance: "సంబంధితత",
    current: "ప్రస్తుత",
    viewStandard: "ప్రమాణాన్ని చూడండి",
    noStandards: "ప్రమాణాలు ఏవీ కనుగొనబడలేదు",
    tryDifferent:
      "వేరే IS కోడ్, ప్రమాణం పేరు లేదా మీ అవసరాన్ని వేరే విధంగా ప్రయత్నించండి.",
    supportedLanguages: "మద్దతు ఉన్న భాషలు",
  },

  Kannada: {
    indianStandards: "ಭಾರತೀಯ ಮಾನದಂಡಗಳು",
    findRight: "ಸರಿಯಾದ",
    standard: "ಮಾನದಂಡವನ್ನು ಹುಡುಕಿ.",
    description:
      "IS ಕೋಡ್, ಶೀರ್ಷಿಕೆ ಅಥವಾ ನಿಮ್ಮ ಅಗತ್ಯವನ್ನು ವಿವರಿಸುವ ಮೂಲಕ ಭಾರತೀಯ ಮಾನದಂಡಗಳನ್ನು ಹುಡುಕಿ.",
    placeholder:
      "IS ಕೋಡ್, ಮಾನದಂಡವನ್ನು ಹುಡುಕಿ ಅಥವಾ ನಿಮ್ಮ ಅಗತ್ಯವನ್ನು ವಿವರಿಸಿ...",
    search: "ಹುಡುಕಿ",
    multilingual: "ಬಹುಭಾಷಾ ಹುಡುಕಾಟ:",
    tenLanguages: "10 ಭಾರತೀಯ ಭಾಷೆಗಳು",
    categories: "ವರ್ಗಗಳು",
    allStandards: "ಎಲ್ಲಾ ಮಾನದಂಡಗಳು",
    construction: "ನಿರ್ಮಾಣ",
    electrical: "ವಿದ್ಯುತ್",
    fireSafety: "ಅಗ್ನಿ ಸುರಕ್ಷತೆ",
    mechanical: "ಯಾಂತ್ರಿಕ",
    civilEngineering: "ಸಿವಿಲ್ ಎಂಜಿನಿಯರಿಂಗ್",
    showing: "ತೋರಿಸಲಾಗುತ್ತಿದೆ",
    standards: "ಮಾನದಂಡಗಳು",
    relevance: "ಸಂಬಂಧಿತತೆ",
    current: "ಪ್ರಸ್ತುತ",
    viewStandard: "ಮಾನದಂಡವನ್ನು ನೋಡಿ",
    noStandards: "ಯಾವುದೇ ಮಾನದಂಡ ಕಂಡುಬಂದಿಲ್ಲ",
    tryDifferent:
      "ಬೇರೆ IS ಕೋಡ್, ಮಾನದಂಡದ ಹೆಸರು ಅಥವಾ ನಿಮ್ಮ ಅಗತ್ಯವನ್ನು ಬೇರೆ ರೀತಿಯಲ್ಲಿ ನಮೂದಿಸಿ.",
    supportedLanguages: "ಬೆಂಬಲಿತ ಭಾಷೆಗಳು",
  },

  Malayalam: {
    indianStandards: "ഇന്ത്യൻ മാനദണ്ഡങ്ങൾ",
    findRight: "ശരിയായ",
    standard: "മാനദണ്ഡം കണ്ടെത്തുക.",
    description:
      "IS കോഡ്, ശീർഷകം അല്ലെങ്കിൽ നിങ്ങളുടെ ആവശ്യകത വിവരിച്ച് ഇന്ത്യൻ മാനദണ്ഡങ്ങൾ തിരയുക.",
    placeholder:
      "IS കോഡ്, മാനദണ്ഡം തിരയുക അല്ലെങ്കിൽ നിങ്ങളുടെ ആവശ്യകത വിവരിക്കുക...",
    search: "തിരയുക",
    multilingual: "ബഹുഭാഷാ തിരയൽ:",
    tenLanguages: "10 ഇന്ത്യൻ ഭാഷകൾ",
    categories: "വിഭാഗങ്ങൾ",
    allStandards: "എല്ലാ മാനദണ്ഡങ്ങളും",
    construction: "നിർമ്മാണം",
    electrical: "വൈദ്യുതി",
    fireSafety: "അഗ്നി സുരക്ഷ",
    mechanical: "മെക്കാനിക്കൽ",
    civilEngineering: "സിവിൽ എഞ്ചിനീയറിംഗ്",
    showing: "കാണിക്കുന്നു",
    standards: "മാനദണ്ഡങ്ങൾ",
    relevance: "പ്രസക്തി",
    current: "നിലവിലുള്ളത്",
    viewStandard: "മാനദണ്ഡം കാണുക",
    noStandards: "മാനദണ്ഡങ്ങളൊന്നും കണ്ടെത്തിയില്ല",
    tryDifferent:
      "മറ്റൊരു IS കോഡ്, മാനദണ്ഡത്തിന്റെ പേര് അല്ലെങ്കിൽ നിങ്ങളുടെ ആവശ്യകത മറ്റൊരു രീതിയിൽ നൽകുക.",
    supportedLanguages: "പിന്തുണയ്ക്കുന്ന ഭാഷകൾ",
  },

  Punjabi: {
    indianStandards: "ਭਾਰਤੀ ਮਿਆਰ",
    findRight: "ਸਹੀ",
    standard: "ਮਿਆਰ ਲੱਭੋ।",
    description:
      "IS ਕੋਡ, ਸਿਰਲੇਖ ਜਾਂ ਆਪਣੀ ਲੋੜ ਦਾ ਵਰਣਨ ਕਰਕੇ ਭਾਰਤੀ ਮਿਆਰ ਲੱਭੋ।",
    placeholder:
      "IS ਕੋਡ, ਮਿਆਰ ਲੱਭੋ ਜਾਂ ਆਪਣੀ ਲੋੜ ਦਾ ਵਰਣਨ ਕਰੋ...",
    search: "ਖੋਜੋ",
    multilingual: "ਬਹੁ-ਭਾਸ਼ਾਈ ਖੋਜ:",
    tenLanguages: "10 ਭਾਰਤੀ ਭਾਸ਼ਾਵਾਂ",
    categories: "ਸ਼੍ਰੇਣੀਆਂ",
    allStandards: "ਸਾਰੇ ਮਿਆਰ",
    construction: "ਨਿਰਮਾਣ",
    electrical: "ਬਿਜਲੀ",
    fireSafety: "ਅੱਗ ਸੁਰੱਖਿਆ",
    mechanical: "ਮਕੈਨੀਕਲ",
    civilEngineering: "ਸਿਵਲ ਇੰਜੀਨੀਅਰਿੰਗ",
    showing: "ਦਿਖਾਇਆ ਜਾ ਰਿਹਾ ਹੈ",
    standards: "ਮਿਆਰ",
    relevance: "ਸੰਬੰਧਿਤਤਾ",
    current: "ਮੌਜੂਦਾ",
    viewStandard: "ਮਿਆਰ ਵੇਖੋ",
    noStandards: "ਕੋਈ ਮਿਆਰ ਨਹੀਂ ਮਿਲਿਆ",
    tryDifferent:
      "ਕੋਈ ਹੋਰ IS ਕੋਡ, ਮਿਆਰ ਦਾ ਨਾਮ ਜਾਂ ਆਪਣੀ ਲੋੜ ਵੱਖਰੇ ਤਰੀਕੇ ਨਾਲ ਲਿਖੋ।",
    supportedLanguages: "ਸਮਰਥਿਤ ਭਾਸ਼ਾਵਾਂ",
  },
};

/* =========================================================
   STANDARD DATA
========================================================= */

const standards = [
  {
    code: "IS 15683:2018",
    category: "Fire Safety",
    keywords: `
      fire extinguisher portable fire safety extinguisher
      अग्निशामक आग बुझाने वाला अग्नि सुरक्षा
      agnishamak aag bujhane wala fire safety
      अग्निशामक अग्निसुरक्षा आग विझवणारे
      અગ્નિશામક આગ સુરક્ષા
      অগ্নিনির্বাপক অগ্নি নিরাপত্তা
      தீயணைப்பான் தீ பாதுகாப்பு
      అగ్నిమాపక అగ్ని భద్రత
      ಅಗ್ನಿಶಾಮಕ ಅಗ್ನಿ ಸುರಕ್ಷತೆ
      അഗ്നിശമന അഗ്നി സുരക്ഷ
      ਅੱਗ ਬੁਝਾਉਣ ਵਾਲਾ ਅੱਗ ਸੁਰੱਖਿਆ
    `,
    translations: {
      English: {
        title:
          "Portable Fire Extinguishers — Performance and Construction",
        description:
          "Specifies requirements for portable fire extinguishers including construction, performance and testing requirements.",
      },
      Hindi: {
        title:
          "पोर्टेबल अग्निशामक — प्रदर्शन और निर्माण",
        description:
          "पोर्टेबल अग्निशामकों के निर्माण, प्रदर्शन और परीक्षण की आवश्यकताओं को निर्दिष्ट करता है।",
      },
      Marathi: {
        title:
          "पोर्टेबल अग्निशामक — कार्यक्षमता आणि बांधणी",
        description:
          "पोर्टेबल अग्निशामकांच्या बांधणी, कार्यक्षमता आणि चाचणीसाठी आवश्यक बाबी निर्दिष्ट करते.",
      },
      Gujarati: {
        title:
          "પોર્ટેબલ અગ્નિશામક — કામગીરી અને બાંધકામ",
        description:
          "પોર્ટેબલ અગ્નિશામકોના બાંધકામ, કામગીરી અને પરીક્ષણ માટેની આવશ્યકતાઓ નક્કી કરે છે.",
      },
      Bengali: {
        title:
          "পোর্টেবল অগ্নিনির্বাপক — কর্মক্ষমতা ও নির্মাণ",
        description:
          "পোর্টেবল অগ্নিনির্বাপকের নির্মাণ, কর্মক্ষমতা এবং পরীক্ষার প্রয়োজনীয়তা নির্ধারণ করে।",
      },
      Tamil: {
        title:
          "கையடக்க தீயணைப்பான்கள் — செயல்திறன் மற்றும் கட்டுமானம்",
        description:
          "கையடக்க தீயணைப்பான்களின் கட்டுமானம், செயல்திறன் மற்றும் சோதனைக்கான தேவைகளை குறிப்பிடுகிறது.",
      },
      Telugu: {
        title:
          "పోర్టబుల్ అగ్నిమాపకాలు — పనితీరు మరియు నిర్మాణం",
        description:
          "పోర్టబుల్ అగ్నిమాపకాల నిర్మాణం, పనితీరు మరియు పరీక్ష అవసరాలను నిర్దేశిస్తుంది.",
      },
      Kannada: {
        title:
          "ಪೋರ್ಟಬಲ್ ಅಗ್ನಿಶಾಮಕಗಳು — ಕಾರ್ಯಕ್ಷಮತೆ ಮತ್ತು ನಿರ್ಮಾಣ",
        description:
          "ಪೋರ್ಟಬಲ್ ಅಗ್ನಿಶಾಮಕಗಳ ನಿರ್ಮಾಣ, ಕಾರ್ಯಕ್ಷಮತೆ ಮತ್ತು ಪರೀಕ್ಷೆಯ ಅವಶ್ಯಕತೆಗಳನ್ನು ನಿರ್ದಿಷ್ಟಪಡಿಸುತ್ತದೆ.",
      },
      Malayalam: {
        title:
          "പോർട്ടബിൾ അഗ്നിശമന ഉപകരണങ്ങൾ — പ്രവർത്തനക്ഷമതയും നിർമ്മാണവും",
        description:
          "പോർട്ടബിൾ അഗ്നിശമന ഉപകരണങ്ങളുടെ നിർമ്മാണം, പ്രവർത്തനക്ഷമത, പരിശോധന എന്നിവയ്ക്കുള്ള ആവശ്യകതകൾ വ്യക്തമാക്കുന്നു.",
      },
      Punjabi: {
        title:
          "ਪੋਰਟੇਬਲ ਅੱਗ ਬੁਝਾਉਣ ਵਾਲੇ ਯੰਤਰ — ਕਾਰਗੁਜ਼ਾਰੀ ਅਤੇ ਨਿਰਮਾਣ",
        description:
          "ਪੋਰਟੇਬਲ ਅੱਗ ਬੁਝਾਉਣ ਵਾਲੇ ਯੰਤਰਾਂ ਦੇ ਨਿਰਮਾਣ, ਕਾਰਗੁਜ਼ਾਰੀ ਅਤੇ ਟੈਸਟਿੰਗ ਦੀਆਂ ਲੋੜਾਂ ਦੱਸਦਾ ਹੈ।",
      },
    },
  },

  {
    code: "IS 2190:2024",
    category: "Fire Safety",
    keywords: `
      fire extinguishing appliances fire equipment fire safety maintenance
      अग्निशमन उपकरण आग सुरक्षा अग्नि उपकरण रखरखाव
      aag bujhane ka upkaran agni suraksha
      अग्निशमन उपकरण आग सुरक्षा उपकरण देखभाल
      અગ્નિશામક સાધનો આગ સુરક્ષા જાળવણી
      অগ্নিনির্বাপক সরঞ্জাম আগুন নিরাপত্তা রক্ষণাবেক্ষণ
      தீயணைப்பு உபகரணங்கள் தீ பாதுகாப்பு பராமரிப்பு
      అగ్నిమాపక పరికరాలు అగ్ని భద్రత నిర్వహణ
      ಅಗ್ನಿಶಾಮಕ ಉಪಕರಣಗಳು ಅಗ್ನಿ ಸುರಕ್ಷತೆ ನಿರ್ವಹಣೆ
      അഗ്നിശമന ഉപകരണങ്ങൾ അഗ്നി സുരക്ഷ പരിപാലനം
      ਅੱਗ ਬੁਝਾਉਣ ਵਾਲੇ ਉਪਕਰਣ ਅੱਗ ਸੁਰੱਖਿਆ
    `,
    translations: {
      English: {
        title:
          "Selection, Installation and Maintenance of First-Aid Fire Extinguishing Appliances",
        description:
          "Provides guidance for selection, installation, inspection and maintenance of fire extinguishing appliances.",
      },
      Hindi: {
        title:
          "प्राथमिक अग्निशमन उपकरणों का चयन, स्थापना और रखरखाव",
        description:
          "अग्निशमन उपकरणों के चयन, स्थापना, निरीक्षण और रखरखाव के लिए मार्गदर्शन प्रदान करता है।",
      },
      Marathi: {
        title:
          "प्राथमिक अग्निशमन उपकरणांची निवड, स्थापना आणि देखभाल",
        description:
          "अग्निशमन उपकरणांच्या निवड, स्थापना, तपासणी आणि देखभालीसाठी मार्गदर्शन प्रदान करते.",
      },
      Gujarati: {
        title:
          "પ્રાથમિક અગ્નિશામક સાધનોની પસંદગી, સ્થાપન અને જાળવણી",
        description:
          "અગ્નિશામક સાધનોની પસંદગી, સ્થાપન, નિરીક્ષણ અને જાળવણી માટે માર્ગદર્શન આપે છે.",
      },
      Bengali: {
        title:
          "প্রাথমিক অগ্নিনির্বাপক সরঞ্জামের নির্বাচন, স্থাপন ও রক্ষণাবেক্ষণ",
        description:
          "অগ্নিনির্বাপক সরঞ্জামের নির্বাচন, স্থাপন, পরিদর্শন এবং রক্ষণাবেক্ষণের জন্য নির্দেশনা প্রদান করে।",
      },
      Tamil: {
        title:
          "முதலுதவி தீயணைப்பு உபகரணங்களின் தேர்வு, நிறுவல் மற்றும் பராமரிப்பு",
        description:
          "தீயணைப்பு உபகரணங்களின் தேர்வு, நிறுவல், ஆய்வு மற்றும் பராமரிப்புக்கான வழிகாட்டுதலை வழங்குகிறது.",
      },
      Telugu: {
        title:
          "ప్రథమ అగ్నిమాపక పరికరాల ఎంపిక, ఏర్పాటు మరియు నిర్వహణ",
        description:
          "అగ్నిమాపక పరికరాల ఎంపిక, ఏర్పాటు, తనిఖీ మరియు నిర్వహణకు మార్గదర్శకత్వాన్ని అందిస్తుంది.",
      },
      Kannada: {
        title:
          "ಪ್ರಾಥಮಿಕ ಅಗ್ನಿಶಾಮಕ ಉಪಕರಣಗಳ ಆಯ್ಕೆ, ಸ್ಥಾಪನೆ ಮತ್ತು ನಿರ್ವಹಣೆ",
        description:
          "ಅಗ್ನಿಶಾಮಕ ಉಪಕರಣಗಳ ಆಯ್ಕೆ, ಸ್ಥಾಪನೆ, ಪರಿಶೀಲನೆ ಮತ್ತು ನಿರ್ವಹಣೆಗೆ ಮಾರ್ಗದರ್ಶನ ನೀಡುತ್ತದೆ.",
      },
      Malayalam: {
        title:
          "പ്രാഥമിക അഗ്നിശമന ഉപകരണങ്ങളുടെ തിരഞ്ഞെടുപ്പ്, സ്ഥാപനം, പരിപാലനം",
        description:
          "അഗ്നിശമന ഉപകരണങ്ങളുടെ തിരഞ്ഞെടുപ്പ്, സ്ഥാപനം, പരിശോധന, പരിപാലനം എന്നിവയ്ക്കുള്ള മാർഗനിർദ്ദേശം നൽകുന്നു.",
      },
      Punjabi: {
        title:
          "ਪਹਿਲੀ ਸਹਾਇਤਾ ਅੱਗ ਬੁਝਾਉਣ ਵਾਲੇ ਉਪਕਰਣਾਂ ਦੀ ਚੋਣ, ਸਥਾਪਨਾ ਅਤੇ ਰੱਖ-ਰਖਾਅ",
        description:
          "ਅੱਗ ਬੁਝਾਉਣ ਵਾਲੇ ਉਪਕਰਣਾਂ ਦੀ ਚੋਣ, ਸਥਾਪਨਾ, ਜਾਂਚ ਅਤੇ ਰੱਖ-ਰਖਾਅ ਲਈ ਮਾਰਗਦਰਸ਼ਨ ਦਿੰਦਾ ਹੈ।",
      },
    },
  },

  {
    code: "IS 732:2019",
    category: "Electrical",
    keywords: `
      electrical wiring electricity wires electrical installation
      विद्युत वायरिंग बिजली तार विद्युत स्थापना
      vidyut wiring bijli wiring bijli ke taar
      विद्युत वायरिंग वीज वायरिंग विद्युत स्थापना
      વિદ્યુત વાયરિંગ વીજળીના તાર વિદ્યુત સ્થાપન
      বৈদ্যুতিক তার বৈদ্যুতিক ওয়্যারিং বিদ্যুৎ
      மின்சார வயரிங் மின் கம்பிகள் மின்சார நிறுவல்
      విద్యుత్ వైరింగ్ విద్యుత్ తీగలు విద్యుత్ సంస్థాపన
      ವಿದ್ಯುತ್ ವೈರಿಂಗ್ ವಿದ್ಯುತ್ ತಂತಿಗಳು ವಿದ್ಯುತ್ ಅಳವಡಿಕೆ
      വൈദ്യുത വയറിംഗ് വൈദ്യുതി വയറുകൾ വൈദ്യുത സ്ഥാപനം
      ਬਿਜਲੀ ਦੀ ਵਾਇਰਿੰਗ ਬਿਜਲੀ ਦੀਆਂ ਤਾਰਾਂ
    `,
    translations: {
      English: {
        title:
          "Code of Practice for Electrical Wiring Installations",
        description:
          "Covers requirements and recommendations for electrical wiring installations and associated equipment.",
      },
      Hindi: {
        title:
          "विद्युत वायरिंग प्रतिष्ठानों के लिए आचार संहिता",
        description:
          "विद्युत वायरिंग प्रतिष्ठानों और संबंधित उपकरणों के लिए आवश्यकताओं और सिफारिशों को शामिल करता है।",
      },
      Marathi: {
        title:
          "विद्युत वायरिंग स्थापनेसाठी आचारसंहिता",
        description:
          "विद्युत वायरिंग स्थापना आणि संबंधित उपकरणांसाठी आवश्यक बाबी आणि शिफारसी समाविष्ट करते.",
      },
      Gujarati: {
        title:
          "વિદ્યુત વાયરિંગ સ્થાપનો માટે પ્રેક્ટિસ કોડ",
        description:
          "વિદ્યુત વાયરિંગ સ્થાપનો અને સંબંધિત સાધનો માટેની આવશ્યકતાઓ અને ભલામણો આવરી લે છે.",
      },
      Bengali: {
        title:
          "বৈদ্যুতিক ওয়্যারিং স্থাপনার জন্য অনুশীলন বিধি",
        description:
          "বৈদ্যুতিক ওয়্যারিং স্থাপনা এবং সংশ্লিষ্ট সরঞ্জামের প্রয়োজনীয়তা ও সুপারিশ অন্তর্ভুক্ত করে।",
      },
      Tamil: {
        title:
          "மின் வயரிங் நிறுவல்களுக்கான நடைமுறை விதிமுறை",
        description:
          "மின் வயரிங் நிறுவல்கள் மற்றும் தொடர்புடைய உபகரணங்களுக்கான தேவைகள் மற்றும் பரிந்துரைகளை உள்ளடக்கியது.",
      },
      Telugu: {
        title:
          "విద్యుత్ వైరింగ్ సంస్థాపనల కోసం ప్రాక్టీస్ కోడ్",
        description:
          "విద్యుత్ వైరింగ్ సంస్థాపనలు మరియు సంబంధిత పరికరాల అవసరాలు మరియు సిఫార్సులను కలిగి ఉంటుంది.",
      },
      Kannada: {
        title:
          "ವಿದ್ಯುತ್ ವೈರಿಂಗ್ ಅಳವಡಿಕೆಗಳಿಗಾಗಿ ಅಭ್ಯಾಸ ಸಂಹಿತೆ",
        description:
          "ವಿದ್ಯುತ್ ವೈರಿಂಗ್ ಅಳವಡಿಕೆಗಳು ಮತ್ತು ಸಂಬಂಧಿತ ಸಾಧನಗಳ ಅವಶ್ಯಕತೆಗಳು ಹಾಗೂ ಶಿಫಾರಸುಗಳನ್ನು ಒಳಗೊಂಡಿದೆ.",
      },
      Malayalam: {
        title:
          "വൈദ്യുത വയറിംഗ് ഇൻസ്റ്റാളേഷനുകൾക്കുള്ള പ്രാക്ടീസ് കോഡ്",
        description:
          "വൈദ്യുത വയറിംഗ് ഇൻസ്റ്റാളേഷനുകൾക്കും അനുബന്ധ ഉപകരണങ്ങൾക്കുമുള്ള ആവശ്യകതകളും ശുപാർശകളും ഉൾക്കൊള്ളുന്നു.",
      },
      Punjabi: {
        title:
          "ਬਿਜਲੀ ਦੀ ਵਾਇਰਿੰਗ ਸਥਾਪਨਾਵਾਂ ਲਈ ਅਭਿਆਸ ਕੋਡ",
        description:
          "ਬਿਜਲੀ ਦੀ ਵਾਇਰਿੰਗ ਸਥਾਪਨਾਵਾਂ ਅਤੇ ਸੰਬੰਧਿਤ ਉਪਕਰਣਾਂ ਲਈ ਲੋੜਾਂ ਅਤੇ ਸਿਫ਼ਾਰਸ਼ਾਂ ਸ਼ਾਮਲ ਕਰਦਾ ਹੈ।",
      },
    },
  },

  {
    code: "IS 2062:2011",
    category: "Construction",
    keywords: `
      steel structural steel construction building material
      इस्पात स्टील निर्माण संरचनात्मक स्टील भवन
      steel loha nirman samagri structural steel bhavan nirman
      स्टील बांधकाम संरचनात्मक स्टील इमारत
      સ્ટીલ બાંધકામ સ્ટ્રક્ચરલ સ્ટીલ મકાન
      ইস্পাত নির্মাণ কাঠামোগত ইস্পাত ভবন
      எஃகு கட்டுமான கட்டமைப்பு எஃகு கட்டிடம்
      ఉక్కు నిర్మాణం స్ట్రక్చరల్ స్టీల్ భవనం
      ಉಕ್ಕು ನಿರ್ಮಾಣ ರಚನಾತ್ಮಕ ಉಕ್ಕು ಕಟ್ಟಡ
      ഉരുക്ക് നിർമ്മാണ ഘടനാപരമായ ഉരുക്ക് കെട്ടിടം
      ਸਟੀਲ ਨਿਰਮਾਣ ਢਾਂਚਾਗਤ ਸਟੀਲ ਇਮਾਰਤ
    `,
    translations: {
      English: {
        title:
          "Hot Rolled Medium and High Tensile Structural Steel",
        description:
          "Specifies requirements for structural steel products used in construction and engineering applications.",
      },
      Hindi: {
        title:
          "हॉट रोल्ड मध्यम और उच्च तन्यता वाला संरचनात्मक इस्पात",
        description:
          "निर्माण और इंजीनियरिंग में उपयोग किए जाने वाले संरचनात्मक इस्पात उत्पादों की आवश्यकताओं को निर्दिष्ट करता है।",
      },
      Marathi: {
        title:
          "हॉट रोल्ड मध्यम आणि उच्च तन्यता असलेले संरचनात्मक स्टील",
        description:
          "बांधकाम आणि अभियांत्रिकीमध्ये वापरल्या जाणाऱ्या संरचनात्मक स्टील उत्पादनांसाठी आवश्यक बाबी निर्दिष्ट करते.",
      },
      Gujarati: {
        title:
          "હોટ રોલ્ડ મધ્યમ અને ઉચ્ચ તાણવાળું સ્ટ્રક્ચરલ સ્ટીલ",
        description:
          "બાંધકામ અને એન્જિનિયરિંગમાં ઉપયોગમાં લેવાતા સ્ટ્રક્ચરલ સ્ટીલ ઉત્પાદનો માટેની આવશ્યકતાઓ નક્કી કરે છે.",
      },
      Bengali: {
        title:
          "হট রোল্ড মাঝারি ও উচ্চ টেনসাইল স্ট্রাকচারাল স্টিল",
        description:
          "নির্মাণ ও প্রকৌশল কাজে ব্যবহৃত স্ট্রাকচারাল স্টিল পণ্যের প্রয়োজনীয়তা নির্ধারণ করে।",
      },
      Tamil: {
        title:
          "சூடாக உருட்டப்பட்ட நடுத்தர மற்றும் உயர் இழுவிசை கட்டமைப்பு எஃகு",
        description:
          "கட்டுமானம் மற்றும் பொறியியல் பயன்பாடுகளில் பயன்படுத்தப்படும் கட்டமைப்பு எஃகு தயாரிப்புகளுக்கான தேவைகளை குறிப்பிடுகிறது.",
      },
      Telugu: {
        title:
          "హాట్ రోల్డ్ మీడియం మరియు హై టెన్సైల్ స్ట్రక్చరల్ స్టీల్",
        description:
          "నిర్మాణ మరియు ఇంజినీరింగ్ ఉపయోగాలలో ఉపయోగించే స్ట్రక్చరల్ స్టీల్ ఉత్పత్తుల అవసరాలను నిర్దేశిస్తుంది.",
      },
      Kannada: {
        title:
          "ಹಾಟ್ ರೋಲ್ಡ್ ಮಧ್ಯಮ ಮತ್ತು ಹೆಚ್ಚಿನ ಟೆನ್ಸೈಲ್ ರಚನಾತ್ಮಕ ಉಕ್ಕು",
        description:
          "ನಿರ್ಮಾಣ ಮತ್ತು ಎಂಜಿನಿಯರಿಂಗ್ ಬಳಕೆಯಲ್ಲಿರುವ ರಚನಾತ್ಮಕ ಉಕ್ಕಿನ ಉತ್ಪನ್ನಗಳ ಅವಶ್ಯಕತೆಗಳನ್ನು ನಿರ್ದಿಷ್ಟಪಡಿಸುತ್ತದೆ.",
      },
      Malayalam: {
        title:
          "ഹോട്ട് റോൾഡ് മീഡിയം, ഹൈ ടെൻസൈൽ സ്ട്രക്ചറൽ സ്റ്റീൽ",
        description:
          "നിർമ്മാണത്തിലും എഞ്ചിനീയറിംഗ് ഉപയോഗങ്ങളിലും ഉപയോഗിക്കുന്ന സ്ട്രക്ചറൽ സ്റ്റീൽ ഉൽപ്പന്നങ്ങളുടെ ആവശ്യകതകൾ വ്യക്തമാക്കുന്നു.",
      },
      Punjabi: {
        title:
          "ਹਾਟ ਰੋਲਡ ਮੀਡੀਅਮ ਅਤੇ ਹਾਈ ਟੈਂਸਾਈਲ ਸਟ੍ਰਕਚਰਲ ਸਟੀਲ",
        description:
          "ਨਿਰਮਾਣ ਅਤੇ ਇੰਜੀਨੀਅਰਿੰਗ ਵਿੱਚ ਵਰਤੇ ਜਾਣ ਵਾਲੇ ਸਟ੍ਰਕਚਰਲ ਸਟੀਲ ਉਤਪਾਦਾਂ ਦੀਆਂ ਲੋੜਾਂ ਦੱਸਦਾ ਹੈ।",
      },
    },
  },
];

/* =========================================================
   CATEGORY TRANSLATIONS
========================================================= */

const categoryKeyMap: Record<
  string,
  keyof typeof translations.English
> = {
  "All Standards": "allStandards",
  Construction: "construction",
  Electrical: "electrical",
  "Fire Safety": "fireSafety",
  Mechanical: "mechanical",
  "Civil Engineering": "civilEngineering",
};

const categories = [
  "All Standards",
  "Construction",
  "Electrical",
  "Fire Safety",
  "Mechanical",
  "Civil Engineering",
];

/* =========================================================
   PAGE
========================================================= */

export default function SearchPage() {
  const [query, setQuery] = useState("");
  const [activeCategory, setActiveCategory] =
    useState("All Standards");
  const [language, setLanguage] = useState("English");
  const [showLanguages, setShowLanguages] = useState(false);

  const t =
    translations[
      language as keyof typeof translations
    ];

  /* =======================================================
     SEARCH
  ======================================================= */

  const filteredStandards = standards.filter(
    (standard) => {
      const searchQuery =
        query.toLowerCase().trim();

      const matchesSearch =
        !searchQuery ||
        standard.code
          .toLowerCase()
          .includes(searchQuery) ||
        standard.keywords
          .toLowerCase()
          .includes(searchQuery);

      const matchesCategory =
        activeCategory === "All Standards" ||
        standard.category === activeCategory;

      return matchesSearch && matchesCategory;
    }
  );

  return (
    <main
      className="min-h-screen bg-[#FBF8F4] text-[#211735]"
      lang={language}
    >
      {/* =================================================
          HEADER
      ================================================= */}

      <header className="border-b border-[#E7DDD7] bg-[#FBF8F4]">
        <div className="mx-auto flex h-[76px] max-w-[1400px] items-center justify-between px-8">

          {/* MANAK LOGO */}

          <a
            href="/"
            className="flex items-center gap-3"
          >
            <div className="flex h-10 w-10 items-center justify-center rounded-full bg-[#74478A] font-serif text-white">
              M
            </div>

            <div>
              <div className="font-serif text-xl tracking-wide">
                MANAK
              </div>

              <div className="text-[8px] uppercase tracking-[0.22em] text-[#806D7B]">
                AI for Smarter Procurement
              </div>
            </div>
          </a>

          {/* RIGHT SIDE */}

          <div className="flex items-center gap-3">

            {/* MULTIPLE LANGUAGES */}

            <div className="relative">
              <button
                type="button"
                onClick={() =>
                  setShowLanguages(!showLanguages)
                }
                className="flex items-center gap-2 rounded-full border border-[#DED2CE] bg-white/60 px-4 py-2 text-xs text-[#493D50] transition hover:border-[#BFA6BD]"
              >
                <Languages
                  size={15}
                  className="text-[#74478A]"
                />

                <span>
                  Multiple Languages
                </span>
              </button>

              {showLanguages && (
                <div className="absolute right-0 top-12 z-50 w-56 rounded-2xl border border-[#E4DAD5] bg-white p-3 shadow-[0_12px_35px_rgba(116,71,138,0.12)]">

                  <p className="px-3 pb-2 text-[10px] uppercase tracking-[0.18em] text-[#A35A91]">
                    {t.supportedLanguages}
                  </p>

                  <div className="grid grid-cols-2 gap-1">
                    {languages.map((item) => (
                      <button
                        type="button"
                        key={item}
                        onClick={() => {
                          setLanguage(item);
                          setShowLanguages(false);
                        }}
                        className={`rounded-lg px-3 py-2 text-left text-xs transition ${
                          language === item
                            ? "bg-[#EDE0EC] font-medium text-[#74478A]"
                            : "text-[#706578] hover:bg-[#F5EEF5]"
                        }`}
                      >
                        {item}
                      </button>
                    ))}
                  </div>

                </div>
              )}
            </div>

            {/* PROFILE */}

            <div className="flex h-9 w-9 items-center justify-center rounded-full bg-[#A35A91] text-xs text-white">
              RS
            </div>

          </div>
        </div>
      </header>

      {/* =================================================
          PAGE
      ================================================= */}

      <section className="mx-auto max-w-[1150px] px-8 py-14">

        {/* HEADING */}

        <div className="max-w-[760px]">

          <div className="mb-4 flex items-center gap-3 text-xs uppercase tracking-[0.28em] text-[#A35A91]">
            <span className="h-px w-8 bg-[#A35A91]" />
            {t.indianStandards}
          </div>

          <h1 className="font-serif text-5xl leading-[1.05] tracking-[-0.03em]">
            {t.findRight}
            <br />
            <span className="text-[#74478A]">
              {t.standard}
            </span>
          </h1>

          <p className="mt-6 max-w-[650px] text-[17px] leading-8 text-[#706578]">
            {t.description}
          </p>

        </div>

        {/* =================================================
            SEARCH BOX
        ================================================= */}

        <div className="mt-10">

          <div className="flex h-[64px] items-center gap-4 rounded-[18px] border border-[#D9C7D6] bg-white px-5 shadow-[0_8px_30px_rgba(116,71,138,0.05)] focus-within:border-[#A35A91]">

            <Search
              size={22}
              strokeWidth={1.7}
              className="shrink-0 text-[#74478A]"
            />

            <input
              type="text"
              value={query}
              onChange={(e) =>
                setQuery(e.target.value)
              }
              placeholder={t.placeholder}
              className="h-full min-w-0 flex-1 bg-transparent text-sm text-[#211735] outline-none placeholder:text-[#A3989D]"
            />

            <button
              type="button"
              onClick={() => {}}
              className="hidden rounded-xl bg-[#74478A] px-6 py-3 text-sm font-medium text-white transition hover:bg-[#653C78] sm:block"
            >
              {t.search}
            </button>

          </div>

          {/* LANGUAGE INFO */}

          <div className="mt-3 flex items-center gap-2 text-xs text-[#806D7B]">

            <Languages
              size={14}
              className="text-[#A35A91]"
            />

            <span>
              {t.multilingual}
            </span>

            <span className="font-medium text-[#74478A]">
              {t.tenLanguages}
            </span>

          </div>

        </div>

        {/* =================================================
            CONTENT
        ================================================= */}

        <div className="mt-12 grid grid-cols-1 gap-10 lg:grid-cols-[220px_1fr]">

          {/* FILTERS */}

          <aside>

            <div className="mb-5 flex items-center gap-2">

              <SlidersHorizontal
                size={17}
                className="text-[#74478A]"
              />

              <h2 className="text-sm font-medium text-[#211735]">
                {t.categories}
              </h2>

            </div>

            <div className="space-y-1">

              {categories.map((category) => {

                const categoryKey =
                  categoryKeyMap[category];

                return (
                  <button
                    type="button"
                    key={category}
                    onClick={() =>
                      setActiveCategory(category)
                    }
                    className={`w-full rounded-xl px-4 py-3 text-left text-sm transition ${
                      activeCategory === category
                        ? "bg-[#EDE0EC] font-medium text-[#74478A]"
                        : "text-[#806D7B] hover:bg-[#F3EBF1]"
                    }`}
                  >
                    {t[categoryKey] as string}
                  </button>
                );

              })}

            </div>

          </aside>

          {/* RESULTS */}

          <div>

            <div className="mb-5 flex items-center justify-between">

              <p className="text-sm text-[#806D7B]">
                {t.showing}{" "}

                <span className="font-medium text-[#493D50]">
                  {filteredStandards.length}
                </span>{" "}

                {t.standards}
              </p>

              <button
                type="button"
                className="flex items-center gap-2 text-xs text-[#806D7B]"
              >
                {t.relevance}
                <ChevronRight size={14} />
              </button>

            </div>

            {/* STANDARD CARDS */}

            <div className="space-y-4">

              {filteredStandards.map((standard) => {

                const translated =
                  standard.translations[
                    language as keyof typeof standard.translations
                  ] ||
                  standard.translations.English;

                return (
                  <article
                    key={standard.code}
                    className="group rounded-[22px] border border-[#E4DAD5] bg-white p-7 transition duration-200 hover:-translate-y-0.5 hover:border-[#C5A7C2] hover:shadow-[0_12px_35px_rgba(116,71,138,0.07)]"
                  >

                    <div className="flex items-start justify-between gap-5">

                      <div className="flex gap-5">

                        <div className="flex h-12 w-12 shrink-0 items-center justify-center rounded-2xl bg-[#F0E3EF] text-[#74478A]">

                          <BookOpen
                            size={21}
                            strokeWidth={1.6}
                          />

                        </div>

                        <div>

                          <div className="flex flex-wrap items-center gap-3">

                            <span className="font-medium text-[#74478A]">
                              {standard.code}
                            </span>

                            <span className="rounded-full bg-[#F2EEE8] px-3 py-1 text-[10px] text-[#806D7B]">
                              {
                                t[
                                  categoryKeyMap[
                                    standard.category
                                  ]
                                ] as string
                              }
                            </span>

                            <span className="rounded-full bg-[#EDF5ED] px-3 py-1 text-[10px] text-[#5D8260]">
                              {t.current}
                            </span>

                          </div>

                          <h3 className="mt-3 max-w-[650px] font-serif text-[22px] leading-7 text-[#211735]">
                            {translated.title}
                          </h3>

                          <p className="mt-3 max-w-[680px] text-sm leading-6 text-[#806D7B]">
                            {translated.description}
                          </p>

                        </div>
                      </div>

                      <button
                        type="button"
                        className="hidden shrink-0 text-[#74478A] sm:block"
                      >
                        <ArrowUpRight
                          size={21}
                          className="transition-transform group-hover:translate-x-1 group-hover:-translate-y-1"
                        />
                      </button>

                    </div>

                    <div className="mt-6 border-t border-[#EEE7E2] pt-4">

                      <button
                        type="button"
                        className="flex items-center gap-2 text-xs font-medium text-[#74478A]"
                      >
                        {t.viewStandard}
                        <ArrowUpRight size={14} />
                      </button>

                    </div>

                  </article>
                );
              })}

              {/* EMPTY STATE */}

              {filteredStandards.length === 0 && (

                <div className="rounded-[22px] border border-dashed border-[#D8C8D6] bg-[#FDF9FC] px-8 py-16 text-center">

                  <div className="mx-auto flex h-14 w-14 items-center justify-center rounded-full bg-[#EDE0EC] text-[#74478A]">
                    <Search size={22} />
                  </div>

                  <h3 className="mt-5 font-serif text-2xl">
                    {t.noStandards}
                  </h3>

                  <p className="mx-auto mt-2 max-w-md text-sm leading-6 text-[#806D7B]">
                    {t.tryDifferent}
                  </p>

                </div>

              )}

            </div>

          </div>

        </div>

      </section>

    </main>
  );
}