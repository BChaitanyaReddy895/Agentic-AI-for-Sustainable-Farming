// AgriSmart AI - Voice Interface Module
// Fully offline-capable voice recognition and text-to-speech
// Supports 10+ Indian languages with natural speech understanding
// Designed for illiterate farmers - understands colloquial speech

class VoiceInterface {
    constructor() {
        this.recognition = null;
        this.synthesis = window.speechSynthesis;
        this.isListening = false;
        this.isSupported = false;
        this.currentLanguage = 'hi-IN'; // Default to Hindi for farmers
        this.detectedLanguage = null;
        this.voiceCommands = {};
        this.onResultCallback = null;
        this.onErrorCallback = null;
        this.autoStart = false;
        this.continuousMode = false;
        this.confidenceThreshold = 0.5;
        
        // Language mappings (BCP 47 codes)
        this.languages = {
            'en': { code: 'en-IN', name: 'English', voiceName: 'English India' },
            'hi': { code: 'hi-IN', name: 'हिंदी', voiceName: 'Hindi' },
            'kn': { code: 'kn-IN', name: 'ಕನ್ನಡ', voiceName: 'Kannada' },
            'ta': { code: 'ta-IN', name: 'தமிழ்', voiceName: 'Tamil' },
            'te': { code: 'te-IN', name: 'తెలుగు', voiceName: 'Telugu' },
            'bn': { code: 'bn-IN', name: 'বাংলা', voiceName: 'Bengali' },
            'gu': { code: 'gu-IN', name: 'ગુજરાતી', voiceName: 'Gujarati' },
            'mr': { code: 'mr-IN', name: 'मराठी', voiceName: 'Marathi' },
            'pa': { code: 'pa-IN', name: 'ਪੰਜਾਬੀ', voiceName: 'Punjabi' },
            'ml': { code: 'ml-IN', name: 'മലയാളം', voiceName: 'Malayalam' },
            'or': { code: 'or-IN', name: 'ଓଡ଼ିଆ', voiceName: 'Odia' }
        };

        // =====================================================
        // COMPREHENSIVE MULTI-LANGUAGE KEYWORD DATABASE
        // Includes: Native script, Transliteration (Roman), 
        // Colloquial variations, Common misspellings
        // =====================================================
        
        // Crop names in all languages + transliterations
        this.cropDictionary = {
            rice: {
                canonical: 'rice',
                keywords: [
                    // English
                    'rice', 'paddy', 'chawal',
                    // Hindi + transliteration
                    'चावल', 'धान', 'chawal', 'dhaan', 'chaawal', 'dhan',
                    // Kannada + transliteration
                    'ಅಕ್ಕಿ', 'ಭತ್ತ', 'akki', 'bhatta', 'aki', 'batta',
                    // Telugu + transliteration
                    'వరి', 'బియ్యం', 'vari', 'biyyam', 'vaari', 'biryam',
                    // Tamil + transliteration
                    'அரிசி', 'நெல்', 'arisi', 'nel', 'arushi', 'nell',
                    // Bengali + transliteration
                    'চাল', 'ধান', 'chal', 'dhan', 'chaal',
                    // Marathi + transliteration
                    'तांदूळ', 'भात', 'tandool', 'bhaat', 'tandul', 'bhat',
                    // Gujarati + transliteration
                    'ચોખા', 'ડાંગર', 'chokha', 'dangar', 'chokaa',
                    // Punjabi + transliteration
                    'ਚਾਵਲ', 'ਝੋਨਾ', 'chawal', 'jhona', 'chaval',
                    // Malayalam + transliteration
                    'അരി', 'നെല്ല്', 'ari', 'nellu', 'nelluu',
                    // Odia + transliteration
                    'ଚାଉଳ', 'ଧାନ', 'chaula', 'dhana'
                ]
            },
            wheat: {
                canonical: 'wheat',
                keywords: [
                    'wheat', 'gehun', 'gehoon',
                    // Hindi
                    'गेहूं', 'गेंहू', 'gehun', 'gehoon', 'gehu', 'gandum',
                    // Kannada
                    'ಗೋಧಿ', 'godhi', 'godi', 'godhii',
                    // Telugu
                    'గోధుమ', 'godhuma', 'goduma', 'godhumaa',
                    // Tamil
                    'கோதுமை', 'kothumai', 'godhumai', 'kodumai',
                    // Bengali
                    'গম', 'gom', 'gam', 'gamm',
                    // Marathi
                    'गहू', 'gahu', 'gahuu', 'gavhu',
                    // Gujarati
                    'ઘઉં', 'ghau', 'ghaun', 'gahun',
                    // Punjabi
                    'ਕਣਕ', 'kanak', 'kannak', 'kanek',
                    // Malayalam
                    'ഗോതമ്പ്', 'gothambu', 'godambu',
                    // Odia
                    'ଗହମ', 'gahama', 'gahma'
                ]
            },
            corn: {
                canonical: 'corn',
                keywords: [
                    'corn', 'maize', 'makka', 'makki', 'bhutta',
                    // Hindi
                    'मक्का', 'भुट्टा', 'makka', 'bhutta', 'makai', 'makayi',
                    // Kannada
                    'ಮೆಕ್ಕೆಜೋಳ', 'ಜೋಳ', 'mekkejola', 'jola', 'makkejola', 'jolla',
                    // Telugu
                    'మొక్కజొన్న', 'mokkajonna', 'mokka jonna', 'makai',
                    // Tamil
                    'மக்காச்சோளம்', 'சோளம்', 'makka cholam', 'cholam', 'solam',
                    // Bengali
                    'ভুট্টা', 'bhutta', 'vutta', 'bhuta',
                    // Marathi
                    'मका', 'maka', 'makaa', 'maki',
                    // Gujarati
                    'મકાઈ', 'makai', 'makaai', 'maakaii',
                    // Punjabi
                    'ਮੱਕੀ', 'makki', 'maki', 'makiii',
                    // Malayalam
                    'ചോളം', 'cholam', 'choolam',
                    // Odia
                    'ମକା', 'maka', 'makaa'
                ]
            },
            cotton: {
                canonical: 'cotton',
                keywords: [
                    'cotton', 'kapas', 'rui',
                    // Hindi
                    'कपास', 'रुई', 'kapas', 'kapaas', 'rui', 'rooi',
                    // Kannada
                    'ಹತ್ತಿ', 'hatti', 'hattti', 'hati',
                    // Telugu
                    'పత్తి', 'patti', 'pattti', 'paththi',
                    // Tamil
                    'பருத்தி', 'paruthi', 'paruththi', 'parutthi',
                    // Bengali
                    'তুলা', 'tula', 'tulaa', 'tulo',
                    // Marathi
                    'कापूस', 'kapus', 'kaapus', 'kapoos',
                    // Gujarati
                    'કપાસ', 'kapas', 'kapaas',
                    // Punjabi
                    'ਕਪਾਹ', 'kapah', 'kapaah', 'kapahi',
                    // Malayalam
                    'പരുത്തി', 'paruththi', 'paruthi',
                    // Odia
                    'କପା', 'kapa', 'kapaa'
                ]
            },
            tomato: {
                canonical: 'tomato',
                keywords: [
                    'tomato', 'tamatar', 'tamater',
                    // Hindi
                    'टमाटर', 'tamatar', 'tamater', 'tamaatar', 'tamato',
                    // Kannada
                    'ಟೊಮೆಟೊ', 'ಟಮಾಟೊ', 'tomato', 'tometo', 'tamaato',
                    // Telugu
                    'టమాటా', 'టమాట', 'tamata', 'tamaataa', 'tomato',
                    // Tamil
                    'தக்காளி', 'thakkali', 'thakkaali', 'takali', 'takkali',
                    // Bengali
                    'টমেটো', 'tometo', 'tamatar', 'tomato',
                    // Marathi
                    'टोमॅटो', 'tomato', 'tamatar',
                    // Gujarati
                    'ટામેટું', 'tametu', 'tamaatu', 'tomato',
                    // Punjabi
                    'ਟਮਾਟਰ', 'tamatar', 'tamaatar',
                    // Malayalam
                    'തക്കാളി', 'thakkali', 'thakaali',
                    // Odia
                    'ଟମାଟୋ', 'tomato', 'tamatar'
                ]
            },
            potato: {
                canonical: 'potato',
                keywords: [
                    'potato', 'aloo', 'alu', 'batata',
                    // Hindi
                    'आलू', 'aloo', 'alu', 'aaloo', 'allu',
                    // Kannada
                    'ಆಲೂಗಡ್ಡೆ', 'ಬಟಾಟೆ', 'aalugadde', 'batate', 'aaloo gadde',
                    // Telugu
                    'బంగాళాదుంప', 'ఆలుగడ్డ', 'bangaladumpa', 'alugadda', 'aloo',
                    // Tamil
                    'உருளைக்கிழங்கு', 'urulaikilangu', 'urulai', 'aloo',
                    // Bengali
                    'আলু', 'alu', 'aloo', 'aaloo',
                    // Marathi
                    'बटाटा', 'batata', 'bataata', 'batato',
                    // Gujarati
                    'બટાટા', 'batata', 'bataata',
                    // Punjabi
                    'ਆਲੂ', 'aloo', 'alu', 'aaloo',
                    // Malayalam
                    'ഉരുളക്കിഴങ്ങ്', 'urulakkilangu', 'urula',
                    // Odia
                    'ଆଳୁ', 'aalu', 'alu', 'aloo'
                ]
            },
            sugarcane: {
                canonical: 'sugarcane',
                keywords: [
                    'sugarcane', 'sugar cane', 'ganna', 'oos',
                    // Hindi
                    'गन्ना', 'ईख', 'ganna', 'gaanna', 'eekh', 'gannaa',
                    // Kannada
                    'ಕಬ್ಬು', 'kabbu', 'kabu', 'kabbbu',
                    // Telugu
                    'చెరకు', 'cheraku', 'cheruku', 'cherakku',
                    // Tamil
                    'கரும்பு', 'karumbu', 'karumbbu', 'karimbu',
                    // Bengali
                    'আখ', 'akh', 'aakh', 'aakho',
                    // Marathi
                    'ऊस', 'oos', 'us', 'uus',
                    // Gujarati
                    'શેરડી', 'sherdi', 'serdi', 'sharadi',
                    // Punjabi
                    'ਗੰਨਾ', 'ganna', 'gaanna', 'gannaa',
                    // Malayalam
                    'കരിമ്പ്', 'karimpu', 'karimb',
                    // Odia
                    'ଆଖୁ', 'aakhu', 'akhu', 'aku'
                ]
            },
            onion: {
                canonical: 'onion',
                keywords: [
                    'onion', 'pyaz', 'pyaaz', 'kanda',
                    // Hindi
                    'प्याज', 'pyaz', 'pyaaz', 'piyaj', 'piyaaz', 'pyaaj',
                    // Kannada
                    'ಈರುಳ್ಳಿ', 'ಉಳ್ಳಿ', 'eerulli', 'ulli', 'irulli',
                    // Telugu
                    'ఉల్లి', 'ఉల్లిపాయ', 'ulli', 'ullipaya', 'ullipaaya',
                    // Tamil
                    'வெங்காயம்', 'vengayam', 'vengaayam', 'vengaiam',
                    // Bengali
                    'পেঁয়াজ', 'peyaj', 'pyaaj', 'peeyaj',
                    // Marathi
                    'कांदा', 'kanda', 'kaanda', 'kandaa',
                    // Gujarati
                    'ડુંગળી', 'dungli', 'dungali', 'dungri',
                    // Punjabi
                    'ਪਿਆਜ਼', 'piaz', 'pyaaz', 'piaaz',
                    // Malayalam
                    'ഉള്ളി', 'ulli', 'ullee', 'savala',
                    // Odia
                    'ପିଆଜ', 'piaja', 'pyaaj'
                ]
            },
            soybean: {
                canonical: 'soybean',
                keywords: [
                    'soybean', 'soya', 'soyabean', 'soy',
                    // Hindi
                    'सोयाबीन', 'soyabean', 'soyabeen', 'soya', 'soyaa',
                    // Kannada
                    'ಸೋಯಾಬೀನ್', 'soyabean', 'soyabeen', 'soya',
                    // Telugu
                    'సోయా', 'soya', 'soyaa', 'soyabean',
                    // Tamil
                    'சோயா', 'soya', 'soyaa', 'soyabean',
                    // Bengali
                    'সোয়াবিন', 'soyabin', 'soyabean', 'soya',
                    // Marathi
                    'सोयाबीन', 'soyabean', 'soya', 'soyabeen',
                    // Gujarati
                    'સોયાબીન', 'soyabean', 'soyabeen', 'soya',
                    // Punjabi
                    'ਸੋਇਆਬੀਨ', 'soyabean', 'soyaa',
                    // Malayalam
                    'സോയാബീൻ', 'soyabean', 'soya',
                    // Odia
                    'ସୋୟାବିନ୍', 'soyabean', 'soya'
                ]
            },
            mango: {
                canonical: 'mango',
                keywords: [
                    'mango', 'aam', 'keri',
                    // Hindi
                    'आम', 'आंबा', 'aam', 'amba', 'aamb', 'amm',
                    // Kannada
                    'ಮಾವು', 'ಮಾವಿನಕಾಯಿ', 'maavu', 'mavinakayi', 'mavina',
                    // Telugu
                    'మామిడి', 'mamidi', 'maamidi', 'mamidichettu',
                    // Tamil
                    'மாம்பழம்', 'மா', 'maambalam', 'maa', 'mampazham',
                    // Bengali
                    'আম', 'aam', 'am', 'aamm',
                    // Marathi
                    'आंबा', 'amba', 'aamba', 'ambaa',
                    // Gujarati
                    'કેરી', 'keri', 'keree', 'kerri',
                    // Punjabi
                    'ਅੰਬ', 'amb', 'amba', 'aam',
                    // Malayalam
                    'മാങ്ങ', 'maanga', 'manga', 'maambalam',
                    // Odia
                    'ଆମ୍ବ', 'amba', 'aamba', 'aam'
                ]
            },
            groundnut: {
                canonical: 'groundnut',
                keywords: [
                    'groundnut', 'peanut', 'moongfali', 'mungfali',
                    // Hindi
                    'मूंगफली', 'moongfali', 'mungfali', 'moongphali', 'singdana',
                    // Kannada
                    'ಕಡಲೆಕಾಯಿ', 'ಶೇಂಗಾ', 'kadalekayi', 'shenga', 'kadale',
                    // Telugu
                    'వేరుశెనగ', 'verusenaga', 'palli', 'pallee',
                    // Tamil
                    'நிலக்கடலை', 'nilakadalai', 'verkadalai', 'kadala',
                    // Bengali
                    'চিনাবাদাম', 'chinabadam', 'badam',
                    // Marathi
                    'भुईमूग', 'शेंगदाणे', 'bhuimug', 'shengdane',
                    // Gujarati
                    'મગફળી', 'magfali', 'singdana',
                    // Punjabi
                    'ਮੂੰਗਫਲੀ', 'moongfali', 'mungfali'
                ]
            },
            banana: {
                canonical: 'banana',
                keywords: [
                    'banana', 'kela', 'kele',
                    // Hindi
                    'केला', 'kela', 'kele', 'kelaa', 'kelay',
                    // Kannada
                    'ಬಾಳೆಹಣ್ಣು', 'ಬಾಳೆ', 'balehannu', 'baale', 'bale',
                    // Telugu
                    'అరటి', 'arati', 'aratichettu', 'aratipandu',
                    // Tamil
                    'வாழைப்பழம்', 'vaazhaipazham', 'vaalai', 'vazhai',
                    // Bengali
                    'কলা', 'kola', 'kolaa', 'kela',
                    // Marathi
                    'केळे', 'kele', 'kelay', 'kelaa',
                    // Gujarati
                    'કેળા', 'kela', 'kelaa',
                    // Punjabi
                    'ਕੇਲਾ', 'kela', 'kelaa',
                    // Malayalam
                    'വാഴപ്പഴം', 'vazhappazham', 'vazha',
                    // Odia
                    'କଦଳୀ', 'kadali', 'kela'
                ]
            },
            chilli: {
                canonical: 'chilli',
                keywords: [
                    'chilli', 'chili', 'mirchi', 'mirch',
                    // Hindi
                    'मिर्च', 'मिर्ची', 'mirchi', 'mirch', 'meerchi', 'lalmirch',
                    // Kannada
                    'ಮೆಣಸಿನಕಾಯಿ', 'menasinakayi', 'menasu', 'menasina',
                    // Telugu
                    'మిర్చి', 'mirchi', 'mirapakaya', 'mirapa',
                    // Tamil
                    'மிளகாய்', 'milagai', 'milakkai', 'molgai',
                    // Bengali
                    'মরিচ', 'morich', 'lonka', 'lonkaa',
                    // Marathi
                    'मिरची', 'mirchi', 'mirchee',
                    // Gujarati
                    'મરચું', 'marchu', 'mirchi',
                    // Punjabi
                    'ਮਿਰਚ', 'mirch', 'mirchi',
                    // Malayalam
                    'മുളക്', 'mulaku', 'mulak',
                    // Odia
                    'ଲଙ୍କା', 'lanka', 'mirchi'
                ]
            },
            turmeric: {
                canonical: 'turmeric',
                keywords: [
                    'turmeric', 'haldi', 'haridra',
                    // Hindi
                    'हल्दी', 'haldi', 'haldee', 'haladi',
                    // Kannada
                    'ಅರಿಶಿನ', 'arishina', 'arasina',
                    // Telugu
                    'పసుపు', 'pasupu', 'pasupuu',
                    // Tamil
                    'மஞ்சள்', 'manjal', 'manjall',
                    // Bengali
                    'হলুদ', 'holud', 'halud', 'haldi',
                    // Marathi
                    'हळद', 'halad', 'haldi',
                    // Gujarati
                    'હળદર', 'haldar', 'haldi',
                    // Punjabi
                    'ਹਲਦੀ', 'haldi', 'haldee',
                    // Malayalam
                    'മഞ്ഞൾ', 'manjal', 'manjall'
                ]
            }
        };

        // Action/Intent keywords in all languages
        this.actionDictionary = {
            weather: {
                intent: 'weather',
                keywords: [
                    // English
                    'weather', 'forecast', 'rain', 'temperature', 'climate', 'barish', 'garmi', 'thand',
                    // Hindi + transliteration
                    'मौसम', 'बारिश', 'गर्मी', 'ठंड', 'तापमान', 'mausam', 'baarish', 'garmi', 'thand', 'taapman',
                    'कब बारिश होगी', 'बरसात', 'पानी गिरेगा', 'बरसेगा',
                    // Kannada
                    'ಹವಾಮಾನ', 'ಮಳೆ', 'ಬಿಸಿ', 'ಚಳಿ', 'havamaana', 'male', 'bisi', 'chali',
                    'ಮಳೆ ಯಾವಾಗ', 'ಮಳೆ ಬರುತ್ತಾ',
                    // Telugu
                    'వాతావరణం', 'వర్షం', 'ఎండ', 'చలి', 'vaatavaranam', 'varsham', 'enda', 'chali',
                    // Tamil
                    'வானிலை', 'மழை', 'வெயில்', 'குளிர்', 'vaanilai', 'mazhai', 'veyil', 'kulir',
                    // Bengali
                    'আবহাওয়া', 'বৃষ্টি', 'গরম', 'ঠান্ডা', 'aabohawa', 'brishti', 'gorom', 'thanda',
                    // Marathi
                    'हवामान', 'पाऊस', 'ऊन', 'थंडी', 'havaman', 'paus', 'un', 'thandi',
                    // Common phonetic variations
                    'mosam', 'mousam', 'mousum', 'barsat', 'varshat', 'paani', 'megh'
                ]
            },
            recommendation: {
                intent: 'recommendation',
                keywords: [
                    // English
                    'recommend', 'suggestion', 'suggest', 'which crop', 'what to grow', 'best crop', 'advice',
                    // Hindi
                    'सिफारिश', 'सलाह', 'क्या उगाऊं', 'कौन सी फसल', 'sifarish', 'salah', 'kya ugaaun', 'konsi fasal',
                    'कौन सा बीज', 'क्या बोऊं', 'फसल बताओ', 'खेती बताओ', 'क्या लगाऊं',
                    // Kannada
                    'ಶಿಫಾರಸು', 'ಸಲಹೆ', 'ಯಾವ ಬೆಳೆ', 'ಏನು ಬೆಳೆಯಲಿ', 'shifarasu', 'salahe', 'yaava bele', 'enu beleyali',
                    // Telugu
                    'సిఫార్సు', 'సలహా', 'ఏ పంట', 'ఏమి పండించాలి', 'sifarsu', 'salaha', 'ae panta',
                    // Tamil
                    'பரிந்துரை', 'ஆலோசனை', 'என்ன பயிர்', 'parinthurai', 'aalosanai', 'enna payir',
                    // Bengali
                    'সুপারিশ', 'পরামর্শ', 'কী চাষ', 'suparish', 'poramorsh', 'ki chash',
                    // Colloquial
                    'kya booun', 'kya lagaun', 'kya ugaye', 'konsa beej', 'kaun sa bij',
                    'belo batao', 'fasal batao', 'crop batao'
                ]
            },
            pest: {
                intent: 'pest',
                keywords: [
                    // English
                    'pest', 'disease', 'insect', 'bug', 'worm', 'infection', 'problem', 'attack',
                    // Hindi
                    'कीट', 'कीड़ा', 'रोग', 'बीमारी', 'कीड़े', 'keet', 'keeda', 'rog', 'bimari', 'keede',
                    'फसल में कीड़े', 'पत्ते खराब', 'पत्ते पीले', 'फसल सूख रही', 'कीड़ा लग गया',
                    // Kannada
                    'ಕೀಟ', 'ರೋಗ', 'ಹುಳು', 'keeta', 'roga', 'hulu',
                    'ಎಲೆ ಹಳದಿ', 'ಬೆಳೆ ಹಾಳು', 'ಕೀಟ ಬಂದಿದೆ',
                    // Telugu
                    'పురుగు', 'వ్యాధి', 'పురుగులు', 'purugu', 'vyadhi', 'purugulu',
                    // Tamil
                    'பூச்சி', 'நோய்', 'புழு', 'poochi', 'noi', 'puzhu',
                    // Bengali
                    'পোকা', 'রোগ', 'poka', 'rog',
                    // Marathi
                    'कीड', 'किडा', 'रोग', 'keed', 'kidaa', 'rog',
                    // Colloquial
                    'keeda', 'keede', 'patthe peelay', 'patte peele', 'fasal sukh rahi',
                    'daag lag gaya', 'beemar', 'problem ho gaya'
                ]
            },
            fertilizer: {
                intent: 'fertilizer',
                keywords: [
                    // English
                    'fertilizer', 'fertiliser', 'manure', 'nutrient', 'npk', 'urea', 'dap',
                    // Hindi
                    'खाद', 'उर्वरक', 'गोबर', 'यूरिया', 'डीएपी', 'khaad', 'urvarak', 'gobar', 'yuria', 'dap',
                    'कितना खाद', 'खाद डालना', 'खाद की मात्रा', 'गोबर खाद',
                    // Kannada
                    'ಗೊಬ್ಬರ', 'ಸಾರ', 'gobbara', 'saara', 'gobbar',
                    'ಎಷ್ಟು ಗೊಬ್ಬರ', 'ಗೊಬ್ಬರ ಹಾಕು',
                    // Telugu
                    'ఎరువు', 'eruvulu', 'eruvu', 'ervu',
                    // Tamil
                    'உரம்', 'uram', 'urram', 'uraம்',
                    // Bengali
                    'সার', 'গোবর', 'saar', 'gobar',
                    // Marathi
                    'खत', 'शेणखत', 'khat', 'shenkhat',
                    // Colloquial
                    'khaad', 'khad', 'kitna khaad', 'gobar khaad', 'gobbar', 'saar'
                ]
            },
            price: {
                intent: 'market',
                keywords: [
                    // English
                    'price', 'market', 'sell', 'buy', 'rate', 'mandi', 'cost',
                    // Hindi
                    'कीमत', 'दाम', 'भाव', 'मंडी', 'बाजार', 'बेचना', 'खरीदना',
                    'keemat', 'daam', 'bhav', 'mandi', 'bazaar', 'bechna', 'khareedna',
                    'क्या रेट है', 'कितने में बिकेगा', 'मंडी भाव', 'आज का भाव',
                    // Kannada
                    'ಬೆಲೆ', 'ಮಾರುಕಟ್ಟೆ', 'bele', 'maarukatte', 'dara',
                    'ಎಷ್ಟು ರೇಟ್', 'ಮಾರಾಟ', 'ಖರೀದಿ',
                    // Telugu
                    'ధర', 'మార్కెట్', 'dhara', 'market',
                    // Tamil
                    'விலை', 'சந்தை', 'vilai', 'sandhai',
                    // Bengali
                    'দাম', 'হাট', 'dam', 'hat',
                    // Marathi
                    'किंमत', 'बाजार', 'kimmat', 'bazar',
                    // Colloquial
                    'kitne mein', 'kya rate', 'kya bhav', 'bhaav batao', 'rate batao',
                    'mandii', 'haat', 'sell karna', 'bech doon'
                ]
            },
            water: {
                intent: 'irrigation',
                keywords: [
                    // English
                    'water', 'irrigation', 'watering', 'drip', 'sprinkler', 'pump',
                    // Hindi
                    'पानी', 'सिंचाई', 'सींचना', 'नहर', 'paani', 'sinchai', 'seenchna', 'nahar',
                    'पानी कब दें', 'कितना पानी', 'पानी देना', 'सींचना कब',
                    // Kannada
                    'ನೀರು', 'ನೀರಾವರಿ', 'neeru', 'neeravari',
                    // Telugu
                    'నీరు', 'నీటిపారుదల', 'neeru', 'neetiparudala',
                    // Tamil
                    'நீர்', 'நீர்ப்பாசனம்', 'neer', 'neerpaasanam',
                    // Bengali
                    'জল', 'সেচ', 'jol', 'sech',
                    // Marathi
                    'पाणी', 'सिंचन', 'paani', 'sinchan',
                    // Colloquial
                    'paanee', 'paanii', 'kitna paani', 'kab sinchai', 'motor chalana'
                ]
            },
            soil: {
                intent: 'soil',
                keywords: [
                    // English
                    'soil', 'land', 'earth', 'ground', 'ph', 'fertility', 'testing',
                    // Hindi
                    'मिट्टी', 'जमीन', 'भूमि', 'मृदा', 'mitti', 'zameen', 'bhoomi', 'mrida',
                    'मिट्टी की जांच', 'मिट्टी टेस्ट', 'जमीन कैसी',
                    // Kannada
                    'ಮಣ್ಣು', 'ಭೂಮಿ', 'mannu', 'bhoomi',
                    // Telugu
                    'మట్టి', 'భూమి', 'matti', 'bhoomi',
                    // Tamil
                    'மண்', 'நிலம்', 'mann', 'nilam',
                    // Bengali
                    'মাটি', 'জমি', 'maati', 'jomi',
                    // Marathi
                    'माती', 'जमीन', 'maati', 'jameen',
                    // Colloquial
                    'mittee', 'maittee', 'zamiin', 'khet ki mitti'
                ]
            },
            help: {
                intent: 'help',
                keywords: [
                    // English
                    'help', 'assist', 'support', 'guide', 'how to', 'what is',
                    // Hindi
                    'मदद', 'सहायता', 'कैसे', 'क्या है', 'madad', 'sahayata', 'kaise', 'kya hai',
                    'मदद करो', 'बताओ', 'समझाओ', 'कैसे करें',
                    // Kannada
                    'ಸಹಾಯ', 'ಹೇಗೆ', 'sahaaya', 'hege',
                    // Telugu
                    'సహాయం', 'ఎలా', 'sahaayam', 'ela',
                    // Tamil
                    'உதவி', 'எப்படி', 'udhavi', 'eppadi',
                    // Bengali
                    'সাহায্য', 'কিভাবে', 'sahajjo', 'kibhabe',
                    // Colloquial
                    'help karo', 'batao', 'samjhao', 'kya karna hai'
                ]
            }
        };

        // Response phrases in multiple languages
        this.responses = {
            en: {
                welcome: "Welcome to AgriSmart AI. I am your farming assistant. Ask me about crops, weather, or any farming question.",
                listening: "I am listening. Please speak your question.",
                notUnderstood: "Sorry, I did not understand. Please say again clearly.",
                weatherOpening: "Opening weather forecast for your area.",
                recommendOpening: "Opening crop recommendation. Tell me about your soil and location.",
                pestOpening: "Opening pest prediction. Which crop has problems?",
                fertilizerOpening: "Opening fertilizer calculator. Enter your soil details.",
                marketOpening: "Opening market prices. Which crop price do you want to check?",
                offline: "You are offline. Using saved data for recommendations.",
                helpText: "You can ask me: What crop should I grow? What is the weather? My crop has disease. What is today's price?"
            },
            hi: {
                welcome: "एग्रीस्मार्ट एआई में आपका स्वागत है। मैं आपका खेती सहायक हूं। फसल, मौसम या कोई भी खेती का सवाल पूछें।",
                listening: "मैं सुन रहा हूं। कृपया अपना सवाल बोलें।",
                notUnderstood: "माफ़ करें, मुझे समझ नहीं आया। कृपया फिर से साफ़ बोलें।",
                weatherOpening: "आपके क्षेत्र का मौसम देख रहे हैं।",
                recommendOpening: "फसल सिफारिश खोल रहे हैं। अपनी मिट्टी और जगह के बारे में बताएं।",
                pestOpening: "कीट पूर्वानुमान खोल रहे हैं। किस फसल में समस्या है?",
                fertilizerOpening: "खाद कैलकुलेटर खोल रहे हैं। अपनी मिट्टी की जानकारी दें।",
                marketOpening: "मंडी भाव खोल रहे हैं। किस फसल का भाव देखना है?",
                offline: "इंटरनेट नहीं है। सहेजे गए डेटा से सलाह दे रहे हैं।",
                helpText: "आप पूछ सकते हैं: क्या फसल उगाऊं? मौसम कैसा है? मेरी फसल में रोग है। आज का भाव क्या है?"
            },
            kn: {
                welcome: "ಅಗ್ರಿಸ್ಮಾರ್ಟ್ ಎಐಗೆ ಸ್ವಾಗತ. ನಾನು ನಿಮ್ಮ ಕೃಷಿ ಸಹಾಯಕ. ಬೆಳೆ, ಹವಾಮಾನ ಅಥವಾ ಯಾವುದೇ ಕೃಷಿ ಪ್ರಶ್ನೆ ಕೇಳಿ.",
                listening: "ನಾನು ಕೇಳುತ್ತಿದ್ದೇನೆ. ದಯವಿಟ್ಟು ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಹೇಳಿ.",
                notUnderstood: "ಕ್ಷಮಿಸಿ, ನನಗೆ ಅರ್ಥವಾಗಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಸ್ಪಷ್ಟವಾಗಿ ಹೇಳಿ.",
                weatherOpening: "ನಿಮ್ಮ ಪ್ರದೇಶದ ಹವಾಮಾನ ನೋಡುತ್ತಿದ್ದೇವೆ.",
                recommendOpening: "ಬೆಳೆ ಶಿಫಾರಸು ತೆರೆಯುತ್ತಿದ್ದೇವೆ. ನಿಮ್ಮ ಮಣ್ಣು ಮತ್ತು ಸ್ಥಳದ ಬಗ್ಗೆ ಹೇಳಿ.",
                pestOpening: "ಕೀಟ ಮುನ್ಸೂಚನೆ ತೆರೆಯುತ್ತಿದ್ದೇವೆ. ಯಾವ ಬೆಳೆಯಲ್ಲಿ ಸಮಸ್ಯೆ?",
                fertilizerOpening: "ಗೊಬ್ಬರ ಕ್ಯಾಲ್ಕುಲೇಟರ್ ತೆರೆಯುತ್ತಿದ್ದೇವೆ.",
                marketOpening: "ಮಾರುಕಟ್ಟೆ ಬೆಲೆ ನೋಡುತ್ತಿದ್ದೇವೆ.",
                offline: "ಇಂಟರ್ನೆಟ್ ಇಲ್ಲ. ಉಳಿಸಿದ ಡೇಟಾ ಬಳಸುತ್ತಿದ್ದೇವೆ.",
                helpText: "ನೀವು ಕೇಳಬಹುದು: ಯಾವ ಬೆಳೆ ಬೆಳೆಯಲಿ? ಹವಾಮಾನ ಹೇಗಿದೆ? ನನ್ನ ಬೆಳೆಗೆ ರೋಗ ಬಂದಿದೆ."
            },
            te: {
                welcome: "అగ్రిస్మార్ట్ ఎఐకి స్వాగతం. నేను మీ వ్యవసాయ సహాయకుడిని. పంటలు, వాతావరణం లేదా ఏదైనా వ్యవసాయ ప్రశ్న అడగండి.",
                listening: "నేను వింటున్నాను. దయచేసి మీ ప్రశ్న చెప్పండి.",
                notUnderstood: "క్షమించండి, నాకు అర్థం కాలేదు. దయచేసి మళ్ళీ స్పష్టంగా చెప్పండి.",
                weatherOpening: "మీ ప్రాంత వాతావరణం చూస్తున్నాము.",
                recommendOpening: "పంట సిఫార్సు తెరుస్తున్నాము.",
                pestOpening: "పురుగు అంచనా తెరుస్తున్నాము. ఏ పంటలో సమస్య?",
                offline: "ఇంటర్నెట్ లేదు. సేవ్ చేసిన డేటా ఉపయోగిస్తున్నాము."
            },
            ta: {
                welcome: "அக்ரிஸ்மார்ட் AI க்கு வரவேற்கிறோம். நான் உங்கள் விவசாய உதவியாளர். பயிர்கள், வானிலை அல்லது எந்த விவசாய கேள்வியும் கேளுங்கள்.",
                listening: "நான் கேட்கிறேன். தயவுசெய்து உங்கள் கேள்வியை சொல்லுங்கள்.",
                notUnderstood: "மன்னிக்கவும், புரியவில்லை. தயவுசெய்து மீண்டும் தெளிவாக சொல்லுங்கள்.",
                weatherOpening: "உங்கள் பகுதி வானிலை பார்க்கிறோம்.",
                offline: "இணையம் இல்லை. சேமித்த தரவைப் பயன்படுத்துகிறோம்."
            }
        };

        // Farming keywords for each language (kept for backward compatibility)
        this.farmingKeywords = {
            'en': {
                crops: ['rice', 'wheat', 'corn', 'cotton', 'tomato', 'potato', 'sugarcane', 'soybean', 'onion', 'mango'],
                actions: ['recommend', 'weather', 'pest', 'fertilizer', 'water', 'help', 'sell', 'buy', 'price'],
                queries: ['what', 'when', 'how', 'which', 'why']
            },
            'hi': {
                crops: ['चावल', 'गेहूं', 'मक्का', 'कपास', 'टमाटर', 'आलू', 'गन्ना', 'सोयाबीन', 'प्याज', 'आम'],
                actions: ['सिफारिश', 'मौसम', 'कीट', 'खाद', 'पानी', 'मदद', 'बेचना', 'खरीदना', 'कीमत'],
                queries: ['क्या', 'कब', 'कैसे', 'कौन', 'क्यों']
            },
            'kn': {
                crops: ['ಅಕ್ಕಿ', 'ಗೋಧಿ', 'ಮೆಕ್ಕೆಜೋಳ', 'ಹತ್ತಿ', 'ಟೊಮೆಟೊ', 'ಆಲೂಗಡ್ಡೆ', 'ಕಬ್ಬು', 'ಸೋಯಾ', 'ಈರುಳ್ಳಿ', 'ಮಾವು'],
                actions: ['ಶಿಫಾರಸು', 'ಹವಾಮಾನ', 'ಕೀಟ', 'ಗೊಬ್ಬರ', 'ನೀರು', 'ಸಹಾಯ', 'ಮಾರಾಟ', 'ಖರೀದಿ', 'ಬೆಲೆ'],
                queries: ['ಏನು', 'ಯಾವಾಗ', 'ಹೇಗೆ', 'ಯಾವ', 'ಏಕೆ']
            },
            'te': {
                crops: ['వరి', 'గోధుమ', 'మొక్కజొన్న', 'పత్తి', 'టమాటా', 'బంగాళాదుంప', 'చెరకు', 'సోయా', 'ఉల్లి', 'మామిడి'],
                actions: ['సిఫార్సు', 'వాతావరణం', 'పురుగు', 'ఎరువు', 'నీరు', 'సహాయం', 'అమ్మకం', 'కొనుగోలు', 'ధర'],
                queries: ['ఏమిటి', 'ఎప్పుడు', 'ఎలా', 'ఏది', 'ఎందుకు']
            },
            'ta': {
                crops: ['அரிசி', 'கோதுமை', 'மக்காச்சோளம்', 'பருத்தி', 'தக்காளி', 'உருளைக்கிழங்கு', 'கரும்பு', 'சோயா', 'வெங்காயம்', 'மாம்பழம்'],
                actions: ['பரிந்துரை', 'வானிலை', 'பூச்சி', 'உரம்', 'நீர்', 'உதவி', 'விற்பனை', 'வாங்குதல்', 'விலை'],
                queries: ['என்ன', 'எப்போது', 'எப்படி', 'எது', 'ஏன்']
            }
        };

        // Voice command mappings to actions
        this.commandActions = {
            // Navigation commands
            'home': () => this.safeNavigate('home'),
            'recommendation': () => this.safeNavigate('recommendation'),
            'weather': () => this.safeNavigate('weather'),
            'market': () => this.safeNavigate('market'),
            'pest': () => this.safeNavigate('pest-prediction'),
            'fertilizer': () => this.safeNavigate('fertilizer'),
            'help': () => this.speakHelp(),
            
            // Action commands
            'analyze soil': () => this.triggerSoilAnalysis(),
            'get recommendation': () => this.triggerRecommendation(),
            'check weather': () => this.triggerWeatherCheck(),
            'predict pest': () => this.triggerPestPrediction(),
            'calculate fertilizer': () => this.triggerFertilizerCalc()
        };

        this.init();
    }

    init() {
        // Check for Web Speech API support
        if ('webkitSpeechRecognition' in window || 'SpeechRecognition' in window) {
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            this.isSupported = true;
            
            // Enhanced settings for better recognition
            this.recognition.continuous = false;
            this.recognition.interimResults = true;
            this.recognition.maxAlternatives = 5; // More alternatives for better matching
            
            this.setupRecognitionEvents();
            console.log('✅ Voice recognition initialized with multi-language support');
        } else {
            console.warn('❌ Speech recognition not supported in this browser');
            this.isSupported = false;
        }

        // Check TTS support
        if (!this.synthesis) {
            console.warn('❌ Speech synthesis not supported');
        }
        
        // Load available voices
        this.loadVoices();
        
        // Try to detect user's preferred language
        this.detectUserLanguage();
    }

    detectUserLanguage() {
        // Check browser language
        const browserLang = navigator.language || navigator.userLanguage;
        
        // Map browser language to our supported languages
        const langMap = {
            'hi': 'hi-IN', 'hi-IN': 'hi-IN',
            'kn': 'kn-IN', 'kn-IN': 'kn-IN',
            'te': 'te-IN', 'te-IN': 'te-IN',
            'ta': 'ta-IN', 'ta-IN': 'ta-IN',
            'bn': 'bn-IN', 'bn-IN': 'bn-IN',
            'gu': 'gu-IN', 'gu-IN': 'gu-IN',
            'mr': 'mr-IN', 'mr-IN': 'mr-IN',
            'pa': 'pa-IN', 'pa-IN': 'pa-IN',
            'ml': 'ml-IN', 'ml-IN': 'ml-IN',
            'or': 'or-IN', 'or-IN': 'or-IN',
            'en': 'en-IN', 'en-IN': 'en-IN', 'en-US': 'en-IN', 'en-GB': 'en-IN'
        };
        
        // Check stored preference first
        const storedLang = localStorage.getItem('agrismart-language');
        if (storedLang && langMap[storedLang]) {
            this.currentLanguage = langMap[storedLang];
        } else if (langMap[browserLang]) {
            this.currentLanguage = langMap[browserLang];
        } else if (langMap[browserLang.split('-')[0]]) {
            this.currentLanguage = langMap[browserLang.split('-')[0]];
        }
        
        console.log(`🌐 Detected language: ${this.currentLanguage}`);
    }

    setupRecognitionEvents() {
        this.recognition.onstart = () => {
            this.isListening = true;
            this.updateUI('listening');
            console.log('🎤 Voice recognition started in:', this.currentLanguage);
        };

        this.recognition.onresult = (event) => {
            let interimTranscript = '';
            let finalTranscript = '';
            let allAlternatives = [];

            for (let i = event.resultIndex; i < event.results.length; i++) {
                const result = event.results[i];
                
                // Collect all alternatives for better matching
                for (let j = 0; j < result.length; j++) {
                    allAlternatives.push({
                        text: result[j].transcript,
                        confidence: result[j].confidence
                    });
                }
                
                const transcript = result[0].transcript;
                if (result.isFinal) {
                    finalTranscript += transcript;
                } else {
                    interimTranscript += transcript;
                }
            }

            // Show interim results
            if (interimTranscript) {
                this.updateTranscript(interimTranscript, false);
            }

            // Process final results
            if (finalTranscript) {
                console.log('📝 Recognized:', finalTranscript);
                console.log('📝 All alternatives:', allAlternatives);
                this.updateTranscript(finalTranscript, true);
                
                // Try to match with all alternatives
                this.processVoiceCommandEnhanced(finalTranscript, allAlternatives);
                
                if (this.onResultCallback) {
                    this.onResultCallback(finalTranscript);
                }
            }
        };

        this.recognition.onerror = (event) => {
            console.error('❌ Speech recognition error:', event.error);
            this.isListening = false;
            this.updateUI('error');
            
            let errorMessage = '';
            const langCode = this.currentLanguage.split('-')[0];
            
            switch(event.error) {
                case 'no-speech':
                    errorMessage = this.getLocalizedMessage('noSpeech', langCode);
                    break;
                case 'audio-capture':
                    errorMessage = this.getLocalizedMessage('noMic', langCode);
                    break;
                case 'not-allowed':
                    errorMessage = this.getLocalizedMessage('micDenied', langCode);
                    break;
                case 'network':
                    errorMessage = this.getLocalizedMessage('offline', langCode);
                    // Don't block - can still work offline
                    break;
                default:
                    errorMessage = `Error: ${event.error}`;
            }
            
            if (this.onErrorCallback) {
                this.onErrorCallback(errorMessage);
            }
            
            if (errorMessage) {
                this.speak(errorMessage);
            }
        };

        this.recognition.onend = () => {
            this.isListening = false;
            this.updateUI('idle');
            
            // Restart if continuous mode
            if (this.continuousMode && this.autoStart) {
                setTimeout(() => this.startListening(), 500);
            }
        };
    }

    getLocalizedMessage(key, langCode) {
        const messages = {
            noSpeech: {
                en: 'No speech detected. Please try again.',
                hi: 'आवाज़ नहीं सुनाई दी। कृपया फिर से बोलें।',
                kn: 'ಧ್ವನಿ ಕೇಳಿಸಲಿಲ್ಲ. ದಯವಿಟ್ಟು ಮತ್ತೆ ಮಾತನಾಡಿ.',
                te: 'ధ్వని వినబడలేదు. దయచేసి మళ్ళీ మాట్లాడండి.',
                ta: 'குரல் கேட்கவில்லை. மீண்டும் பேசுங்கள்.'
            },
            noMic: {
                en: 'Microphone not found. Please check your device.',
                hi: 'माइक्रोफोन नहीं मिला। अपना डिवाइस जांचें।',
                kn: 'ಮೈಕ್ರೋಫೋನ್ ಕಂಡುಬಂದಿಲ್ಲ.',
                te: 'మైక్రోఫోన్ కనుగొనబడలేదు.',
                ta: 'மைக்ரோஃபோன் கிடைக்கவில்லை.'
            },
            micDenied: {
                en: 'Microphone access denied. Please allow microphone.',
                hi: 'माइक्रोफोन की अनुमति नहीं है। कृपया अनुमति दें।',
                kn: 'ಮೈಕ್ರೋಫೋನ್ ಅನುಮತಿ ನಿರಾಕರಿಸಲಾಗಿದೆ.',
                te: 'మైక్రోఫోన్ అనుమతి నిరాకరించబడింది.',
                ta: 'மைக்ரோஃபோன் அனுமதி மறுக்கப்பட்டது.'
            },
            offline: {
                en: 'Offline mode. Using saved data.',
                hi: 'ऑफ़लाइन मोड। सहेजे गए डेटा का उपयोग कर रहे हैं।',
                kn: 'ಆಫ್‌ಲೈನ್ ಮೋಡ್. ಉಳಿಸಿದ ಡೇಟಾ ಬಳಸುತ್ತಿದೆ.',
                te: 'ఆఫ్‌లైన్ మోడ్. సేవ్ చేసిన డేటా ఉపయోగిస్తున్నాము.',
                ta: 'ஆஃப்லைன் பயன்முறை. சேமிக்கப்பட்ட தரவைப் பயன்படுத்துகிறது.'
            }
        };
        
        return messages[key]?.[langCode] || messages[key]?.['en'] || '';
    }

    loadVoices() {
        // Load available voices
        const loadVoicesList = () => {
            this.voices = this.synthesis.getVoices();
            console.log('Available voices:', this.voices.length);
            
            // Log Indian language voices
            const indianVoices = this.voices.filter(v => v.lang.includes('IN'));
            console.log('Indian language voices:', indianVoices.map(v => `${v.name} (${v.lang})`));
        };

        loadVoicesList();
        if (speechSynthesis.onvoiceschanged !== undefined) {
            speechSynthesis.onvoiceschanged = loadVoicesList;
        }
    }

    setLanguage(langCode) {
        const lang = this.languages[langCode];
        if (lang) {
            this.currentLanguage = lang.code;
            if (this.recognition) {
                this.recognition.lang = lang.code;
            }
            localStorage.setItem('agrismart-language', langCode);
            console.log(`Language set to: ${lang.name} (${lang.code})`);
            return true;
        }
        return false;
    }

    startListening() {
        if (!this.isSupported) {
            this.speak('Voice recognition is not supported. Please type your query.');
            return false;
        }

        if (this.isListening) {
            this.stopListening();
            return false;
        }

        try {
            this.recognition.lang = this.currentLanguage;
            this.recognition.start();
            return true;
        } catch (error) {
            console.error('Failed to start recognition:', error);
            return false;
        }
    }

    stopListening() {
        if (this.recognition && this.isListening) {
            this.recognition.stop();
        }
    }

    speak(text, lang = null) {
        if (!this.synthesis) {
            console.warn('TTS not available');
            return false;
        }

        // Cancel any ongoing speech
        this.synthesis.cancel();

        const utterance = new SpeechSynthesisUtterance(text);
        utterance.lang = lang || this.currentLanguage;
        utterance.rate = 0.85;  // Slower for clarity
        utterance.pitch = 1;
        utterance.volume = 1;

        // Find appropriate voice
        const targetLang = lang || this.currentLanguage;
        const voice = this.voices?.find(v => v.lang === targetLang) || 
                      this.voices?.find(v => v.lang.startsWith(targetLang.split('-')[0]));
        if (voice) {
            utterance.voice = voice;
        }

        utterance.onstart = () => {
            this.updateUI('speaking');
        };

        utterance.onend = () => {
            this.updateUI('idle');
        };

        this.synthesis.speak(utterance);
        return true;
    }

    stopSpeaking() {
        if (this.synthesis) {
            this.synthesis.cancel();
        }
    }

    // =====================================================
    // ENHANCED MULTI-LANGUAGE VOICE COMMAND PROCESSING
    // =====================================================

    processVoiceCommandEnhanced(primaryText, alternatives = []) {
        const textsToCheck = [primaryText, ...alternatives.map(a => a.text)];
        
        let matchedCrop = null;
        let matchedIntent = null;
        let matchConfidence = 0;
        
        // Check each alternative for matches
        for (const text of textsToCheck) {
            const normalizedText = this.normalizeText(text);
            
            // Try to find crop
            const cropResult = this.findCropInText(normalizedText);
            if (cropResult && cropResult.confidence > matchConfidence) {
                matchedCrop = cropResult.crop;
                matchConfidence = cropResult.confidence;
            }
            
            // Try to find intent
            const intentResult = this.findIntentInText(normalizedText);
            if (intentResult && intentResult.confidence > (matchedIntent?.confidence || 0)) {
                matchedIntent = intentResult;
            }
        }

        console.log('🎯 Matched crop:', matchedCrop);
        console.log('🎯 Matched intent:', matchedIntent);

        // Execute based on matches
        if (matchedIntent) {
            this.executeIntent(matchedIntent.intent, matchedCrop, primaryText);
            return true;
        } else if (matchedCrop) {
            this.handleCropQuery(matchedCrop);
            return true;
        }
        
        // Try legacy processing
        return this.processVoiceCommand(primaryText);
    }

    normalizeText(text) {
        // Normalize text for better matching
        return text
            .toLowerCase()
            .trim()
            // Remove common filler words
            .replace(/\b(please|kripya|dayavittu|please|um|uh)\b/gi, '')
            // Normalize spaces
            .replace(/\s+/g, ' ')
            .trim();
    }

    findCropInText(text) {
        for (const [cropName, cropData] of Object.entries(this.cropDictionary)) {
            for (const keyword of cropData.keywords) {
                // Check for exact word match or substring
                const regex = new RegExp(`\\b${this.escapeRegex(keyword)}\\b`, 'i');
                if (regex.test(text) || text.includes(keyword.toLowerCase())) {
                    return {
                        crop: cropData.canonical,
                        matched: keyword,
                        confidence: keyword.length > 3 ? 0.9 : 0.7
                    };
                }
            }
        }
        return null;
    }

    findIntentInText(text) {
        for (const [actionName, actionData] of Object.entries(this.actionDictionary)) {
            for (const keyword of actionData.keywords) {
                const regex = new RegExp(`\\b${this.escapeRegex(keyword)}\\b`, 'i');
                if (regex.test(text) || text.includes(keyword.toLowerCase())) {
                    return {
                        intent: actionData.intent,
                        matched: keyword,
                        confidence: keyword.length > 4 ? 0.9 : 0.7
                    };
                }
            }
        }
        return null;
    }

    escapeRegex(string) {
        return string.replace(/[.*+?^${}()|[\]\\]/g, '\\$&');
    }

    executeIntent(intent, crop = null, originalText = '') {
        const langCode = this.currentLanguage.split('-')[0];
        const responses = this.responses[langCode] || this.responses['en'];
        
        switch(intent) {
            case 'weather':
                this.speak(responses.weatherOpening);
                this.triggerWeatherCheck();
                break;
            case 'recommendation':
                this.speak(responses.recommendOpening);
                this.triggerRecommendation();
                break;
            case 'pest':
                this.speak(responses.pestOpening);
                this.triggerPestPrediction();
                if (crop) {
                    // Pre-fill crop if mentioned
                    setTimeout(() => {
                        const cropSelect = document.getElementById('pest-crop-select');
                        if (cropSelect) {
                            cropSelect.value = crop;
                        }
                    }, 500);
                }
                break;
            case 'fertilizer':
                this.speak(responses.fertilizerOpening);
                this.triggerFertilizerCalc();
                break;
            case 'market':
                this.speak(responses.marketOpening);
                this.safeNavigate('market');
                break;
            case 'irrigation':
                this.speak(this.getIrrigationAdvice(crop, langCode));
                break;
            case 'soil':
                this.triggerSoilAnalysis();
                break;
            case 'help':
                this.speakHelp();
                break;
            default:
                // Send to chatbot as fallback
                this.sendToChatbot(originalText);
        }
    }

    getIrrigationAdvice(crop, langCode) {
        const cropInfo = OFFLINE_CROP_DATA[crop];
        if (cropInfo) {
            if (langCode === 'hi') {
                return `${crop} को ${cropInfo.water === 'high' ? 'ज्यादा' : cropInfo.water === 'medium' ? 'मध्यम' : 'कम'} पानी की जरूरत है।`;
            } else if (langCode === 'kn') {
                return `${crop} ಗೆ ${cropInfo.water === 'high' ? 'ಹೆಚ್ಚು' : cropInfo.water === 'medium' ? 'ಮಧ್ಯಮ' : 'ಕಡಿಮೆ'} ನೀರು ಬೇಕು.`;
            }
            return `${crop} needs ${cropInfo.water} water.`;
        }
        return 'Please select a crop first.';
    }

    sendToChatbot(text) {
        const chatInput = document.getElementById('chat-input');
        if (chatInput && typeof sendChatMessage === 'function') {
            chatInput.value = text;
            sendChatMessage();
        }
    }

    // Legacy command processing (fallback)
    processVoiceCommand(text) {
        const lowerText = text.toLowerCase().trim();
        
        // Check for exact command matches
        for (const [command, action] of Object.entries(this.commandActions)) {
            if (lowerText.includes(command)) {
                console.log(`Executing command: ${command}`);
                action();
                return true;
            }
        }

        // Check for crop queries
        const crops = ['rice', 'wheat', 'corn', 'cotton', 'tomato', 'potato', 'sugarcane', 'soybean'];
        for (const crop of crops) {
            if (lowerText.includes(crop)) {
                this.handleCropQuery(crop);
                return true;
            }
        }

        // Check for action words in multiple languages
        if (this.matchesAnyKeyword(lowerText, ['weather', 'mausam', 'ಹವಾಮಾನ', 'వాతావరణం', 'வானிலை', 'mosam', 'barish', 'male'])) {
            this.triggerWeatherCheck();
            return true;
        }
        
        if (this.matchesAnyKeyword(lowerText, ['pest', 'keet', 'keeda', 'ಕೀಟ', 'పురుగు', 'பூச்சி', 'rog', 'bimari'])) {
            this.triggerPestPrediction();
            return true;
        }
        
        if (this.matchesAnyKeyword(lowerText, ['fertilizer', 'khad', 'khaad', 'ಗೊಬ್ಬರ', 'ఎరువు', 'உரம்', 'gobar'])) {
            this.triggerFertilizerCalc();
            return true;
        }
        
        if (this.matchesAnyKeyword(lowerText, ['recommend', 'suggest', 'sifarish', 'salah', 'ಶಿಫಾರಸು', 'సిఫార్సు', 'பரிந்துரை', 'batao'])) {
            this.triggerRecommendation();
            return true;
        }
        
        if (this.matchesAnyKeyword(lowerText, ['price', 'market', 'mandi', 'keemat', 'daam', 'bhav', 'ಬೆಲೆ', 'ధర', 'விலை'])) {
            this.safeNavigate('market');
            this.speak('Opening market prices page');
            return true;
        }

        // Default: send to chatbot
        this.sendToChatbot(text);
        return true;
    }

    matchesAnyKeyword(text, keywords) {
        return keywords.some(kw => text.includes(kw.toLowerCase()));
    }

    handleCropQuery(crop) {
        const cropInfo = OFFLINE_CROP_DATA[crop];
        const langCode = this.currentLanguage.split('-')[0];
        
        if (cropInfo) {
            let response;
            
            if (langCode === 'hi') {
                response = `${crop} ${cropInfo.season} में उगाया जाता है। 
                    इसे ${cropInfo.water === 'high' ? 'ज्यादा' : cropInfo.water === 'medium' ? 'मध्यम' : 'कम'} पानी चाहिए।
                    ${cropInfo.soil} मिट्टी में अच्छा उगता है।
                    पीएच ${cropInfo.ph} होना चाहिए।`;
            } else if (langCode === 'kn') {
                response = `${crop} ಅನ್ನು ${cropInfo.season} ನಲ್ಲಿ ಬೆಳೆಯಲಾಗುತ್ತದೆ.
                    ${cropInfo.water === 'high' ? 'ಹೆಚ್ಚು' : cropInfo.water === 'medium' ? 'ಮಧ್ಯಮ' : 'ಕಡಿಮೆ'} ನೀರು ಬೇಕು.
                    ${cropInfo.soil} ಮಣ್ಣಿನಲ್ಲಿ ಚೆನ್ನಾಗಿ ಬೆಳೆಯುತ್ತದೆ.`;
            } else if (langCode === 'te') {
                response = `${crop} ను ${cropInfo.season} లో పండిస్తారు.
                    ${cropInfo.water === 'high' ? 'ఎక్కువ' : cropInfo.water === 'medium' ? 'మధ్యస్థ' : 'తక్కువ'} నీరు అవసరం.
                    ${cropInfo.soil} మట్టిలో బాగా పెరుగుతుంది.`;
            } else {
                response = `${crop} is best grown in ${cropInfo.season} season. 
                    It needs ${cropInfo.water} water and grows well in ${cropInfo.soil} soil. 
                    pH level should be ${cropInfo.ph}.`;
            }
            
            this.speak(response);
            if (typeof showNotification === 'function') {
                showNotification(response, 'info');
            }
        } else {
            this.speak(`Getting information about ${crop}`);
            this.safeNavigate('recommendation');
        }
    }

    safeNavigate(page) {
        if (typeof navigate === 'function') {
            navigate(page);
        } else {
            console.warn('Navigation function not available');
        }
    }

    triggerSoilAnalysis() {
        this.safeNavigate('soil-analysis');
        const langCode = this.currentLanguage.split('-')[0];
        const msg = langCode === 'hi' ? 'मिट्टी विश्लेषण खोल रहे हैं। अपनी मिट्टी की जानकारी दें।' :
                    langCode === 'kn' ? 'ಮಣ್ಣು ವಿಶ್ಲೇಷಣೆ ತೆರೆಯುತ್ತಿದ್ದೇವೆ.' :
                    'Opening soil analysis. Please enter your soil details.';
        this.speak(msg);
    }

    triggerRecommendation() {
        this.safeNavigate('recommendation');
        const langCode = this.currentLanguage.split('-')[0];
        const responses = this.responses[langCode] || this.responses['en'];
        this.speak(responses.recommendOpening);
    }

    triggerWeatherCheck() {
        this.safeNavigate('weather');
        const langCode = this.currentLanguage.split('-')[0];
        const responses = this.responses[langCode] || this.responses['en'];
        this.speak(responses.weatherOpening);
        if (typeof getWeatherForecast === 'function') {
            setTimeout(() => getWeatherForecast(), 1000);
        }
    }

    triggerPestPrediction() {
        this.safeNavigate('pest-prediction');
        const langCode = this.currentLanguage.split('-')[0];
        const responses = this.responses[langCode] || this.responses['en'];
        this.speak(responses.pestOpening);
    }

    triggerFertilizerCalc() {
        this.safeNavigate('fertilizer');
        const langCode = this.currentLanguage.split('-')[0];
        const responses = this.responses[langCode] || this.responses['en'];
        this.speak(responses.fertilizerOpening);
    }

    speakHelp() {
        const langCode = this.currentLanguage.split('-')[0];
        
        const helpMessages = {
            en: `Welcome to AgriSmart AI. Here is how to use voice commands:
                Say "recommend crop" or "kya ugaaun" for crop suggestions.
                Say "check weather" or "mausam batao" for weather forecast.
                Say "pest problem" or "keeda laga hai" for pest prediction.
                Say "fertilizer" or "khaad" for fertilizer calculator.
                Say "market price" or "mandi bhav" for crop prices.
                You can speak in Hindi, Kannada, Telugu, Tamil or English.`,
            hi: `एग्रीस्मार्ट एआई में आपका स्वागत है। आप ये बोल सकते हैं:
                "क्या उगाऊं" या "फसल बताओ" - फसल सिफारिश के लिए
                "मौसम बताओ" या "बारिश कब होगी" - मौसम जानने के लिए  
                "कीड़ा लगा है" या "फसल में रोग" - कीट जानकारी के लिए
                "खाद कितना डालें" - खाद जानने के लिए
                "भाव बताओ" या "मंडी भाव" - बाजार भाव के लिए
                आप हिंदी, कन्नड़, तेलुगु या अंग्रेजी में बोल सकते हैं।`,
            kn: `ಅಗ್ರಿಸ್ಮಾರ್ಟ್ ಎಐಗೆ ಸ್ವಾಗತ. ನೀವು ಈ ರೀತಿ ಹೇಳಬಹುದು:
                "ಯಾವ ಬೆಳೆ ಬೆಳೆಯಲಿ" - ಬೆಳೆ ಶಿಫಾರಸಿಗಾಗಿ
                "ಹವಾಮಾನ ಹೇಳಿ" - ಹವಾಮಾನ ತಿಳಿಯಲು
                "ಕೀಟ ಬಂದಿದೆ" - ಕೀಟ ಮಾಹಿತಿಗಾಗಿ
                "ಗೊಬ್ಬರ ಎಷ್ಟು" - ಗೊಬ್ಬರ ತಿಳಿಯಲು
                "ಬೆಲೆ ಹೇಳಿ" - ಮಾರುಕಟ್ಟೆ ಬೆಲೆಗಾಗಿ`,
            te: `అగ్రిస్మార్ట్ ఎఐకి స్వాగతం. మీరు ఇలా చెప్పవచ్చు:
                "ఏ పంట పండించాలి" - పంట సిఫార్సు కోసం
                "వాతావరణం చెప్పండి" - వాతావరణం తెలుసుకోవడానికి
                "పురుగు వచ్చింది" - పురుగు సమాచారం కోసం`,
            ta: `அக்ரிஸ்மார்ட் AI க்கு வரவேற்கிறோம். நீங்கள் இப்படி சொல்லலாம்:
                "என்ன பயிர் செய்யலாம்" - பயிர் பரிந்துரைக்கு
                "வானிலை சொல்லுங்கள்" - வானிலை அறிய
                "பூச்சி வந்தது" - பூச்சி தகவலுக்கு`
        };
        
        this.speak(helpMessages[langCode] || helpMessages['en']);
    }

    handleOfflineRecognition() {
        const langCode = this.currentLanguage.split('-')[0];
        const responses = this.responses[langCode] || this.responses['en'];
        this.speak(responses.offline);
        if (typeof showNotification === 'function') {
            showNotification('Offline mode: Basic voice commands only', 'warning');
        }
    }

    updateUI(state) {
        const voiceBtn = document.getElementById('voice-btn');
        const voiceIndicator = document.getElementById('voice-indicator');
        
        if (voiceBtn) {
            voiceBtn.classList.remove('listening', 'speaking', 'error');
            voiceBtn.classList.add(state);
        }
        
        if (voiceIndicator) {
            const langCode = this.currentLanguage.split('-')[0];
            const texts = {
                listening: {
                    en: 'Listening...',
                    hi: 'सुन रहे हैं...',
                    kn: 'ಕೇಳುತ್ತಿದ್ದೇವೆ...',
                    te: 'వింటున్నాము...',
                    ta: 'கேட்கிறோம்...'
                },
                speaking: {
                    en: 'Speaking...',
                    hi: 'बोल रहे हैं...',
                    kn: 'ಮಾತನಾಡುತ್ತಿದ್ದೇವೆ...',
                    te: 'మాట్లాడుతున్నాము...',
                    ta: 'பேசுகிறோம்...'
                },
                error: {
                    en: 'Error',
                    hi: 'त्रुटि',
                    kn: 'ದೋಷ',
                    te: 'లోపం',
                    ta: 'பிழை'
                },
                idle: {
                    en: 'Tap to speak',
                    hi: 'बोलने के लिए टैप करें',
                    kn: 'ಮಾತನಾಡಲು ಟ್ಯಾಪ್ ಮಾಡಿ',
                    te: 'మాట్లాడటానికి టాప్ చేయండి',
                    ta: 'பேச தட்டவும்'
                }
            };
            
            switch(state) {
                case 'listening':
                    voiceIndicator.innerHTML = `<i class="fas fa-microphone-alt pulse"></i> ${texts.listening[langCode] || texts.listening.en}`;
                    voiceIndicator.className = 'voice-indicator listening';
                    break;
                case 'speaking':
                    voiceIndicator.innerHTML = `<i class="fas fa-volume-up"></i> ${texts.speaking[langCode] || texts.speaking.en}`;
                    voiceIndicator.className = 'voice-indicator speaking';
                    break;
                case 'error':
                    voiceIndicator.innerHTML = `<i class="fas fa-exclamation-circle"></i> ${texts.error[langCode] || texts.error.en}`;
                    voiceIndicator.className = 'voice-indicator error';
                    break;
                default:
                    voiceIndicator.innerHTML = `<i class="fas fa-microphone"></i> ${texts.idle[langCode] || texts.idle.en}`;
                    voiceIndicator.className = 'voice-indicator';
            }
        }
    }

    updateTranscript(text, isFinal) {
        const transcriptEl = document.getElementById('voice-transcript');
        if (transcriptEl) {
            transcriptEl.textContent = text;
            transcriptEl.className = isFinal ? 'transcript final' : 'transcript interim';
        }
    }

    // Set callbacks
    onResult(callback) {
        this.onResultCallback = callback;
    }

    onError(callback) {
        this.onErrorCallback = callback;
    }

    // Auto-start listening mode for hands-free operation
    enableContinuousMode(enabled = true) {
        this.continuousMode = enabled;
        this.autoStart = enabled;
        if (enabled && !this.isListening) {
            this.startListening();
        }
    }
}

// Offline crop data for voice responses when offline
const OFFLINE_CROP_DATA = {
    rice: { season: 'Kharif (monsoon)', water: 'high', soil: 'clay or loamy', ph: '5.5 to 6.5', hindi: 'खारीफ', kannada: 'ಮಳೆಗಾಲ' },
    wheat: { season: 'Rabi (winter)', water: 'medium', soil: 'loamy', ph: '6.0 to 7.0', hindi: 'रबी', kannada: 'ಚಳಿಗಾಲ' },
    corn: { season: 'Kharif', water: 'medium', soil: 'loamy', ph: '5.8 to 7.0', hindi: 'खारीफ', kannada: 'ಮಳೆಗಾಲ' },
    cotton: { season: 'Kharif', water: 'medium', soil: 'black or alluvial', ph: '6.0 to 8.0', hindi: 'खारीफ', kannada: 'ಮಳೆಗಾಲ' },
    tomato: { season: 'all seasons', water: 'medium', soil: 'sandy loam', ph: '6.0 to 6.8', hindi: 'सभी मौसम', kannada: 'ಎಲ್ಲಾ ಋತುಗಳು' },
    potato: { season: 'Rabi', water: 'medium', soil: 'sandy loam', ph: '5.0 to 6.5', hindi: 'रबी', kannada: 'ಚಳಿಗಾಲ' },
    sugarcane: { season: 'all year', water: 'high', soil: 'loamy', ph: '6.0 to 7.5', hindi: 'पूरे साल', kannada: 'ವರ್ಷಪೂರ್ತಿ' },
    soybean: { season: 'Kharif', water: 'medium', soil: 'loamy', ph: '6.0 to 7.0', hindi: 'खारीफ', kannada: 'ಮಳೆಗಾಲ' },
    onion: { season: 'Rabi and Kharif', water: 'low to medium', soil: 'sandy loam', ph: '6.0 to 7.0', hindi: 'रबी और खारीफ', kannada: 'ಎರಡೂ ಋತುಗಳು' },
    mango: { season: 'perennial', water: 'low', soil: 'deep loamy', ph: '5.5 to 7.5', hindi: 'बारहमासी', kannada: 'ಬಹುವಾರ್ಷಿಕ' },
    groundnut: { season: 'Kharif', water: 'medium', soil: 'sandy loam', ph: '5.5 to 7.0', hindi: 'खारीफ', kannada: 'ಮಳೆಗಾಲ' },
    banana: { season: 'all year', water: 'high', soil: 'rich loamy', ph: '6.0 to 7.5', hindi: 'पूरे साल', kannada: 'ವರ್ಷಪೂರ್ತಿ' },
    chilli: { season: 'Kharif and Rabi', water: 'medium', soil: 'loamy', ph: '6.0 to 7.0', hindi: 'दोनों मौसम', kannada: 'ಎರಡೂ ಋತುಗಳು' },
    turmeric: { season: 'Kharif', water: 'medium to high', soil: 'loamy', ph: '5.0 to 7.5', hindi: 'खारीफ', kannada: 'ಮಳೆಗಾಲ' }
};

// Initialize voice interface
let voiceInterface = null;

function initVoiceInterface() {
    voiceInterface = new VoiceInterface();
    
    // Set up voice button
    const voiceBtn = document.getElementById('voice-btn');
    if (voiceBtn) {
        voiceBtn.addEventListener('click', () => {
            if (voiceInterface.isListening) {
                voiceInterface.stopListening();
            } else {
                voiceInterface.startListening();
            }
        });
    }
    
    // Set up language selector
    setupLanguageSelector();
    
    // Welcome message on first load
    if (!localStorage.getItem('agrismart-welcomed')) {
        setTimeout(() => {
            const langCode = voiceInterface.currentLanguage.split('-')[0];
            const welcomeMessages = {
                hi: 'एग्रीस्मार्ट एआई में आपका स्वागत है। माइक्रोफोन बटन दबाएं और अपना सवाल बोलें।',
                kn: 'ಅಗ್ರಿಸ್ಮಾರ್ಟ್ ಎಐಗೆ ಸ್ವಾಗತ. ಮೈಕ್ರೋಫೋನ್ ಬಟನ್ ಒತ್ತಿ ನಿಮ್ಮ ಪ್ರಶ್ನೆ ಹೇಳಿ.',
                te: 'అగ్రిస్మార్ట్ ఎఐకి స్వాగతం. మైక్రోఫోన్ బటన్ నొక్కి మీ ప్రశ్న చెప్పండి.',
                ta: 'அக்ரிஸ்மார்ட் AIக்கு வரவேற்கிறோம். மைக்ரோஃபோன் பொத்தானை அழுத்தி உங்கள் கேள்வியை சொல்லுங்கள்.',
                en: 'Welcome to AgriSmart AI. Tap the microphone button and speak your farming question.'
            };
            voiceInterface.speak(welcomeMessages[langCode] || welcomeMessages['en']);
            localStorage.setItem('agrismart-welcomed', 'true');
        }, 2000);
    }
    
    return voiceInterface;
}

function setupLanguageSelector() {
    // Create language selector if it doesn't exist
    let langSelector = document.getElementById('language-selector');
    
    if (!langSelector) {
        // Create floating language selector
        langSelector = document.createElement('div');
        langSelector.id = 'language-selector';
        langSelector.className = 'language-selector';
        langSelector.innerHTML = `
            <button class="lang-btn" id="lang-toggle" title="Change Language">
                <i class="fas fa-language"></i>
                <span id="current-lang">हिंदी</span>
            </button>
            <div class="lang-dropdown" id="lang-dropdown">
                <button class="lang-option" data-lang="hi">🇮🇳 हिंदी (Hindi)</button>
                <button class="lang-option" data-lang="en">🇬🇧 English</button>
                <button class="lang-option" data-lang="kn">🇮🇳 ಕನ್ನಡ (Kannada)</button>
                <button class="lang-option" data-lang="te">🇮🇳 తెలుగు (Telugu)</button>
                <button class="lang-option" data-lang="ta">🇮🇳 தமிழ் (Tamil)</button>
                <button class="lang-option" data-lang="bn">🇮🇳 বাংলা (Bengali)</button>
                <button class="lang-option" data-lang="mr">🇮🇳 मराठी (Marathi)</button>
                <button class="lang-option" data-lang="gu">🇮🇳 ગુજરાતી (Gujarati)</button>
                <button class="lang-option" data-lang="pa">🇮🇳 ਪੰਜਾਬੀ (Punjabi)</button>
                <button class="lang-option" data-lang="ml">🇮🇳 മലയാളം (Malayalam)</button>
                <button class="lang-option" data-lang="or">🇮🇳 ଓଡ଼ିଆ (Odia)</button>
            </div>
        `;
        document.body.appendChild(langSelector);
        
        // Add styles for language selector
        const style = document.createElement('style');
        style.textContent = `
            .language-selector {
                position: fixed;
                top: 80px;
                right: 20px;
                z-index: 999;
            }
            .lang-btn {
                display: flex;
                align-items: center;
                gap: 8px;
                padding: 10px 16px;
                background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
                color: white;
                border: none;
                border-radius: 25px;
                font-size: 14px;
                cursor: pointer;
                box-shadow: 0 4px 15px rgba(102,126,234,0.4);
                transition: all 0.3s ease;
            }
            .lang-btn:hover {
                transform: translateY(-2px);
                box-shadow: 0 6px 20px rgba(102,126,234,0.5);
            }
            .lang-btn i {
                font-size: 18px;
            }
            .lang-dropdown {
                display: none;
                position: absolute;
                top: 100%;
                right: 0;
                margin-top: 10px;
                background: white;
                border-radius: 15px;
                box-shadow: 0 10px 40px rgba(0,0,0,0.2);
                overflow: hidden;
                min-width: 200px;
            }
            .lang-dropdown.show {
                display: block;
                animation: slideDown 0.3s ease;
            }
            @keyframes slideDown {
                from { opacity: 0; transform: translateY(-10px); }
                to { opacity: 1; transform: translateY(0); }
            }
            .lang-option {
                display: block;
                width: 100%;
                padding: 12px 20px;
                background: none;
                border: none;
                text-align: left;
                font-size: 15px;
                cursor: pointer;
                transition: background 0.2s;
            }
            .lang-option:hover {
                background: #f0f4ff;
            }
            .lang-option.active {
                background: #667eea;
                color: white;
            }
            
            /* Mobile responsiveness */
            @media (max-width: 600px) {
                .language-selector {
                    top: auto;
                    bottom: 160px;
                    right: 15px;
                }
                .lang-btn span {
                    display: none;
                }
                .lang-btn {
                    width: 50px;
                    height: 50px;
                    border-radius: 50%;
                    justify-content: center;
                    padding: 0;
                }
                .lang-dropdown {
                    right: 0;
                    bottom: 100%;
                    top: auto;
                    margin-bottom: 10px;
                }
            }
        `;
        document.head.appendChild(style);
        
        // Event listeners
        const langToggle = document.getElementById('lang-toggle');
        const langDropdown = document.getElementById('lang-dropdown');
        
        langToggle.addEventListener('click', (e) => {
            e.stopPropagation();
            langDropdown.classList.toggle('show');
        });
        
        // Close dropdown when clicking outside
        document.addEventListener('click', () => {
            langDropdown.classList.remove('show');
        });
        
        // Language selection
        document.querySelectorAll('.lang-option').forEach(btn => {
            btn.addEventListener('click', (e) => {
                const lang = e.target.dataset.lang;
                if (voiceInterface) {
                    voiceInterface.setLanguage(lang);
                    document.getElementById('current-lang').textContent = voiceInterface.languages[lang].name;
                    
                    // Mark active
                    document.querySelectorAll('.lang-option').forEach(b => b.classList.remove('active'));
                    e.target.classList.add('active');
                    
                    // Announce change
                    const announcements = {
                        hi: 'हिंदी भाषा चुनी गई',
                        en: 'English language selected',
                        kn: 'ಕನ್ನಡ ಭಾಷೆ ಆಯ್ಕೆಯಾಗಿದೆ',
                        te: 'తెలుగు భాష ఎంపిక చేయబడింది',
                        ta: 'தமிழ் மொழி தேர்ந்தெடுக்கப்பட்டது',
                        bn: 'বাংলা ভাষা নির্বাচিত',
                        mr: 'मराठी भाषा निवडली',
                        gu: 'ગુજરાતી ભાષા પસંદ થઈ',
                        pa: 'ਪੰਜਾਬੀ ਭਾ਷ਾ ਚੁਣੀ ਗਈ',
                        ml: 'മലയാളം ഭാഷ തിരഞ്ഞെടുത്തു',
                        or: 'ଓଡ଼ିଆ ଭାଷା ଚୟନ ହେଲା'
                    };
                    voiceInterface.speak(announcements[lang] || announcements['en']);
                }
                langDropdown.classList.remove('show');
            });
        });
        
        // Set initial active language
        const currentLang = voiceInterface?.currentLanguage.split('-')[0] || 'hi';
        document.querySelector(`[data-lang="${currentLang}"]`)?.classList.add('active');
        if (voiceInterface) {
            document.getElementById('current-lang').textContent = voiceInterface.languages[currentLang]?.name || 'Hindi';
        }
    }
}

// Export for global use
window.VoiceInterface = VoiceInterface;
window.initVoiceInterface = initVoiceInterface;
window.voiceInterface = null;
window.OFFLINE_CROP_DATA = OFFLINE_CROP_DATA;

// Auto-initialize when DOM is ready
document.addEventListener('DOMContentLoaded', () => {
    window.voiceInterface = initVoiceInterface();
});
// Removed: Migrated to farm-growth-hub
