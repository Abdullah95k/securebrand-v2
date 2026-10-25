"""Mixed-language, English (Arabizi included) and other-language cases (docs/plans/F7.md). None is an
anchor: the Python twin computes every text_norm from the specification, and a script detects the
rows. Every sentence is invented; names are public organisations, brands and places.
"""

from corpus.model import KAF_AR, MAKSURA, TATWEEL, YEH_AR, ZWNJ, Case

_ARABIZI = "Arabizi is only case-folded, never transliterated (documented gap)"
_KURMANJI = "Kurmanji is folded like any other text (documented gap)"
_ARABIC_KEYBOARD = "Sorani typed with the Arabic-keyboard kaf U+0643 and yaa U+064A"

MIXED: list[Case] = [
    # --- Arabic and English -------------------------------------------------------------------
    Case("mix-0003", "mixed", "mixed", "شنو الأحسن: iPhone لو Samsung؟ أريد تلفون كامرته زينة", ()),
    Case("mix-0004", "mixed", "mixed", "WhatsApp واگف عندكم لو بس عدنا؟", ()),
    Case("mix-0005", "mixed", "mixed", f"باقة Zain الجديدة ٢٠ گيگا ب{TATWEEL} ١٠ آلاف", ()),
    Case("mix-0006", "mixed", "mixed", "Asiacell شبكتها بالكرادة صايرة زينة هالفترة", ()),
    Case("mix-0007", "mixed", "mixed", "منو جرّب انترنت Korek بدهوك؟ يگولون سريع", ()),
    Case("mix-0008", "mixed", "mixed", "باچر اكو جلسة Q&A ويا الطلاب بالجامعة التكنولوجية", ()),
    Case("mix-0009", "mixed", "mixed", "حطيت الفيديو على TikTok وصار ترند بيوم واحد", ()),
    Case(
        "mix-0010",
        "mixed",
        "mixed",
        f"شفت الإعلان بال{TATWEEL}Facebook بس ما لگيت السعر",
        (),
        note="an Arabic prefix and a tatweel joined to a Latin word: one token in two scripts",
    ),
    Case("mix-0011", "mixed", "mixed", "اشتراك Netflix غلا هواية، منو يعرف عرض أرخص؟", ()),
    Case("mix-0012", "mixed", "mixed", "PUBG يقطع كل شوية، البنگ ٢٠٠ وفوق", ()),
    Case("mix-0013", "mixed", "mixed", f"ال{TATWEEL} delivery تأخر ساعة ونص والأكل وصل بارد", ()),
    Case("mix-0014", "mixed", "mixed", "عندي exam الصبح والكهرباء طافية من نص الليل", ()),
    Case(
        "mix-0015", "mixed", "mixed", "نزلت صور الأكلة على Instagram وهواية ناس سألوا عن المحل", ()
    ),
    Case("mix-0016", "mixed", "mixed", "الاجتماع صار online لأن الشوارع مقطوعة من المطر", ()),
    Case("mix-0017", "mixed", "mixed", "OMG شنو هالحر؟ ٥٠ درجة بالبصرة!!", ()),
    Case("mix-0018", "mixed", "mixed", "Wi-Fi مال المطار مجاني بس بطيء كلش", ()),
    Case("mix-0019", "mixed", "mixed", "Black Friday بالمولات: خصم ٥٠٪ على الموبايلات", ()),
    Case("mix-0020", "mixed", "mixed", "خابرت Customer Service مال الشركة ثلث مرات ومحد رد", ()),
    Case("mix-0021", "mixed", "mixed", "سويت order من التطبيق والطلبية لهسه ما وصلت", ()),
    Case("mix-0022", "mixed", "mixed", "تطبيق ZainCash ما يفتح عندي من البارحة", ()),
    Case(
        "mix-0023",
        "mixed",
        "ar",
        "النت هسه OK بس الصبح چان مگطوع",
        (),
        note="one short English word in an Arabic text labelled ar",
    ),
    Case("mix-0024", "mixed", "ar", "شبكة 4G بالكوت ضعيفة كلش", ()),
    Case("mix-0025", "mixed", "ar", "lol هاي الصورة تموت ضحك", ()),
    # --- Sorani and English -------------------------------------------------------------------
    Case("mix-0026", "mixed", "mixed", "ئینتەرنێتی Asiacell لە سلێمانی ئەمڕۆ زۆر خاوە", ()),
    Case(
        "mix-0027",
        "mixed",
        "mixed",
        f"{KAF_AR}ێ دەزانێت بۆچ{YEH_AR} WhatsApp {KAF_AR}ار نا{KAF_AR}ات؟",
        (),
        note=_ARABIC_KEYBOARD,
    ),
    Case(
        "mix-0028",
        "mixed",
        "mixed",
        "یاریی Real Madrid و Barcelona ئەمشەو کاتژمێر ١٠ دەست پێدەکات",
        (),
    ),
    Case(
        "mix-0029",
        "mixed",
        "mixed",
        "شاشەی iPhoneەکەم شکا، لەکوێ چاکی دەکەنەوە؟",
        (),
        note="a Sorani suffix written onto a Latin brand name: one token in two scripts",
    ),
    Case(
        "mix-0030",
        "mixed",
        "mixed",
        f"پا{KAF_AR}ێج{YEH_AR} نوێ{YEH_AR} Korek: ٣٠ گ{YEH_AR}گابا{YEH_AR}ت بە ١٥ هەزار د{YEH_AR}نار",
        (),
        note=_ARABIC_KEYBOARD,
    ),
    Case("mix-0031", "mixed", "mixed", "سبەی exam هەیە و کارەبا نییە، چۆن بخوێنم؟", ()),
    Case("mix-0032", "mixed", "mixed", "ڤیدیۆکەم خستە سەر TikTok و زۆر بینەری هەبوو", ()),
    Case(
        "mix-0033",
        "mixed",
        "mixed",
        f"Netflix لە {KAF_AR}وردستان ژێرنووس{MAKSURA} {KAF_AR}ورد{MAKSURA} هە{YEH_AR}ە؟",
        (),
        note="Sorani typed on an Arabic keyboard: alef maksura for a final yaa, U+064A inside a word",
    ),
    Case("mix-0034", "mixed", "mixed", "Good morning هەولێر، ئەمڕۆ هەوا خۆشە", ()),
    Case("mix-0035", "mixed", "mixed", "پینگی PUBG شەوان زۆر بەرزە", ()),
    Case(
        "mix-0036",
        "mixed",
        "mixed",
        "داواکارییەکەم لە ئەپەکە کرد بەڵام delivery هێشتا نەگەیشتووە",
        (),
    ),
    Case("mix-0037", "mixed", "mixed", "لە Instagram وێنەی بەفری پێنجوێنم بینی، زۆر جوان بوو", ()),
    Case(
        "mix-0038",
        "mixed",
        "mixed",
        f"ئ{YEH_AR}نتەرنێت{YEH_AR} زان{KAF_AR}ۆ هەر {KAF_AR}ار نا{KAF_AR}ات، IT دەڵێن {KAF_AR}ێشە{YEH_AR} سێرڤەرە",
        (),
        note=_ARABIC_KEYBOARD,
    ),
    Case(
        "mix-0039",
        "mixed",
        "mixed",
        "ئۆفەری Black Friday لە بازاڕەکانی سلێمانی، داشکاندن تا ٧٠٪",
        (),
    ),
    Case("mix-0040", "mixed", "mixed", "Thank you هاوڕێیان، یارییەکە زۆر خۆش بوو", ()),
    Case(
        "mix-0041",
        "mixed",
        "ckb",
        f"هێڵ{YEH_AR} Zain لە دهۆ{KAF_AR} لاوازە",
        (),
        note=_ARABIC_KEYBOARD,
    ),
    Case("mix-0042", "mixed", "ckb", "هەواڵەکەم لە Facebook خوێندەوە", ()),
    Case(
        "mix-0043",
        "mixed",
        "ckb",
        f"{KAF_AR}ارت{YEH_AR} Asiacell لە بازاڕ نەماوە",
        (),
        note=_ARABIC_KEYBOARD,
    ),
    Case("mix-0044", "mixed", "ckb", "سەیری یارییەکە لە YouTube بکەن", ()),
    Case("mix-0045", "mixed", "mixed", "Happy New Year! ساڵێکی خۆش بێت بۆ هەمووان", ()),
    # --- Arabic and Sorani --------------------------------------------------------------------
    Case(
        "mix-0046",
        "mixed",
        "mixed",
        "الكهرباء عدكم بالسليمانية؟\nنەخێر، ئێمەش کارەبامان نییە",
        (),
        note="an Arabic question answered in Sorani on the next line",
    ),
    Case(
        "mix-0047",
        "mixed",
        "mixed",
        "منو يعرف مطعم زين بأربيل؟ لە شەقامی ٦٠ مەتری چەند چێشتخانەیەکی باش هەیە",
        (),
        note="the Iraqi zain (good) here, spelled like the operator's name",
    ),
    Case("mix-0048", "mixed", "mixed", "الطريق مسدود؟ بەڵێ، ڕێگای هەولێر-کەرکووک داخراوە", ()),
    Case("mix-0049", "mixed", "mixed", "سعر الطماطة اليوم شگد؟ کیلۆیەک بە ١٠٠٠ دینارە", ()),
    Case("mix-0050", "mixed", "mixed", "مبروك للمنتخب! پیرۆز بێت، یارییەکی زۆر جوان بوو", ()),
    Case("mix-0051", "mixed", "mixed", "سوپاس بۆ یارمەتییەکەت، شكراً جزيلاً", ()),
    Case("mix-0052", "mixed", "mixed", "ئەمڕۆ لە سلێمانی بەفر باری، وببغداد شلون الجو؟", ()),
    Case(
        "mix-0053",
        "mixed",
        "mixed",
        "الامتحانات الوزارية بدت؟ \N{EM DASH} بەڵێ، لە سبەینێوە دەست پێدەکات",
        (),
    ),
    Case("mix-0054", "mixed", "mixed", "النت بطيء كلش عدنا، لای ئێوەش وایە؟", ()),
    Case(
        "mix-0055",
        "mixed",
        "mixed",
        "وين موقف الباص؟ پاسەکە لە بەردەم زانکۆی سەلاحەددین دەوەستێت",
        (),
    ),
    Case(
        "mix-0056",
        "mixed",
        "ckb",
        "مامۆستاکە وتی «بالتوفيق للجميع» و تاقیکردنەوەکە دەستی پێکرد",
        (),
        note="an Arabic phrase quoted inside a Sorani sentence labelled ckb",
    ),
    Case("mix-0057", "mixed", "ckb", "ئەم هەفتەیە لە بازاڕ هەمووان دەڵێن «الأسعار نار»", ()),
    Case(
        "mix-0058",
        "mixed",
        "ar",
        "سافرنا إلى ڕانیە والجو كان بارد كلش",
        (),
        note="Ranya in its Sorani spelling inside an Arabic sentence labelled ar",
    ),
    Case(
        "mix-0059",
        "mixed",
        "ar",
        "الطريق بين هەولێر وكركوك زحمة اليوم",
        (),
        note="Erbil in its Sorani spelling and Kirkuk in its Arabic one, labelled ar",
    ),
    Case(
        "mix-0060",
        "mixed",
        "ar",
        "شكد كيلو بين زاخۆ ودهۆک؟",
        (),
        note="Zakho and Duhok in Sorani spelling, Duhok with the Arabic conjunction attached",
    ),
    # --- Arabic and English, continued --------------------------------------------------------
    Case(
        "mix-0061",
        "mixed",
        "mixed",
        f"اشتريت شاحن Samsung أصلي من شارع الصناعة ب{TATWEEL}٢٥ ألف",
        (),
    ),
]

ENGLISH: list[Case] = [
    Case(
        "en-0006",
        "english",
        "en",
        "Asiacell's 4G in Erbil has been terrible all week, 0.5 Mbps at best",
        (),
    ),
    Case("en-0007", "english", "en", "KOREK NETWORK DOWN AGAIN IN DUHOK!!!", ()),
    Case("en-0008", "english", "en", "Power cuts in Baghdad: 12 hours a day & no fix in sight", ()),
    Case(
        "en-0009",
        "english",
        "en",
        "It's 49\N{DEGREE SIGN}C in Basra today... stay hydrated, everyone",
        (),
    ),
    Case("en-0010", "english", "en", "Iraq's national team won 2-1 tonight, what a game!", ()),
    Case("en-0011", "english", "en", "Don't buy the new Zain bundle, it's not worth the price", ()),
    Case("en-0012", "english", "en", "Heavy Rain Warning For Mosul And Kirkuk Tomorrow", ()),
    Case("en-0013", "english", "und", "Same here...", ()),
    Case("en-0014", "english", "en", "Traffic on the Baghdad-Basra highway is crazy right now", ()),
    Case(
        "en-0015", "english", "en", "Fiber-optic internet finally reached our street in Najaf", ()
    ),
    Case("en-0016", "english", "en", "Live Q&A with the Ministry of Electricity at 3 PM today", ()),
    Case(
        "en-0017",
        "english",
        "en",
        "Sandstorm in Anbar... flights delayed at Baghdad International Airport",
        (),
    ),
    Case("en-0018", "english", "en", "Can't top up my balance, the app keeps crashing ugh", ()),
    Case(
        "en-0019",
        "english",
        "en",
        "Erbil\N{EN DASH}Sulaymaniyah road reopened after the snow",
        (),
        note="an en dash between two place names",
    ),
    Case("en-0020", "english", "en", "WHO'S WATCHING THE GAME TONIGHT? Iraq vs. Saudi Arabia", ()),
    Case(
        "en-0021",
        "english",
        "en",
        "Prices at Shorja market went up again: tomatoes 1,500 IQD/kg",
        (),
    ),
    Case("en-0022", "english", "en", "Student-friendly cafés in Sulaymaniyah with fast Wi-Fi?", ()),
    Case("en-0023", "english", "en", "Electricity's back!!! Only took 6 hours lol", ()),
    Case(
        "en-0024",
        "english",
        "en",
        "It\N{RIGHT SINGLE QUOTATION MARK}s finally raining in Duhok, the dams needed it",
        (),
        note="a typographic apostrophe U+2019, as phone keyboards type it",
    ),
    Case("en-0025", "english", "und", "OK!!!", ()),
    Case(
        "en-0026",
        "english",
        "en",
        "Cheap flights from İzmir to Erbil this summer? Asking for my family",
        (),
        note="full case folding of the Turkish dotted capital I",
    ),
    Case(
        "en-0027",
        "english",
        "en",
        "Iraqi Straßenfest in Köln this Saturday: masgouf & kubba for everyone!",
        (),
        note="full case folding of the German sharp s",
    ),
    Case(
        "en-0028",
        "english",
        "en",
        "Trucks from Şırnak are stuck at the border again, 8+ hours",
        (),
        note="the Turkish S with cedilla and dotless i under full case folding",
    ),
    # --- Arabizi ------------------------------------------------------------------------------
    Case("en-0029", "english", "en", "shlonak 7abibi? el net 3indkum zain?", (), note=_ARABIZI),
    Case(
        "en-0030", "english", "en", "shaku maku? el kahraba mgtoo3a mn el sub7", (), note=_ARABIZI
    ),
    Case(
        "en-0031",
        "english",
        "en",
        "inta wein? ana bil Mansour w el share3 za7ma",
        (),
        note=_ARABIZI,
    ),
    Case("en-0032", "english", "en", "el net mgata3 kolish, ya5i shnsawi?", (), note=_ARABIZI),
    Case(
        "en-0033", "english", "en", "Zain 3dhom 3ard jdeed 3al internet bil lail", (), note=_ARABIZI
    ),
    Case(
        "en-0034", "english", "en", "3ammi el jaw 7aar hwaya el yom, 50 daraja", (), note=_ARABIZI
    ),
    Case(
        "en-0035", "english", "en", "Mabrook 3al fawz!!! el muntakhab ykhabbil", (), note=_ARABIZI
    ),
    Case("en-0036", "english", "en", "SHAKU 3ARD 3ALA ASIACELL?", (), note=_ARABIZI),
    Case("en-0037", "english", "und", "ya5i...", (), note=_ARABIZI),
    Case(
        "en-0038", "english", "en", "el ishtirak b Korek sar 25 alf, 8ali wallah", (), note=_ARABIZI
    ),
    Case("en-0039", "english", "en", "tislam eedak 3al musa3ada, ma gassart", (), note=_ARABIZI),
    Case("en-0040", "english", "en", "el jaw b Erbil 7ilo hal ayam, ta3alu", (), note=_ARABIZI),
]

OTHER: list[Case] = [
    # --- Persian ------------------------------------------------------------------------------
    Case(
        "oth-0003", "other", "other", "هوای امروز خیلی گرم است، دمای هوا به چهل و پنج درجه رسید", ()
    ),
    Case(
        "oth-0004",
        "other",
        "other",
        f"قیمت خانه{ZWNJ}ها در تهران امسال خیلی بالا رفته است",
        (),
        note="a ZWNJ after heh in a Persian plural",
    ),
    Case("oth-0005", "other", "other", f"اینترنت خیلی کند است و نمی{ZWNJ}توانم ویدیو ببینم", ()),
    Case(
        "oth-0006",
        "other",
        "other",
        f"می{ZWNJ}خواهم تابستان به اربیل سفر کنم ولی بلیت هواپیما گران است",
        (),
    ),
    Case(
        "oth-0007",
        "other",
        "other",
        f"مسابقه\N{ARABIC HAMZA ABOVE} فوتبال ایران و عراق امشب ساعت هشت شروع می{ZWNJ}شود",
        (),
        note="the Persian ezafe written as heh followed by U+0654 ARABIC HAMZA ABOVE",
    ),
    # --- Kurmanji (Badini) in Latin letters ---------------------------------------------------
    Case(
        "oth-0008", "other", "other", "Havîn li Zaxoyê gelek germ e, 48 pile!", (), note=_KURMANJI
    ),
    Case(
        "oth-0009", "other", "other", "Em ê sibê biçin Duhokê bo kirîna cilan", (), note=_KURMANJI
    ),
    Case(
        "oth-0010",
        "other",
        "other",
        "Li gundê me înternet gelek hêdî ye, çi bikin?",
        (),
        note=_KURMANJI,
    ),
    Case(
        "oth-0011", "other", "other", "Bihayê goştî li bazarê gelek bilind bûye", (), note=_KURMANJI
    ),
    Case("oth-0012", "other", "other", "TÎMA DUHOKÊ ÎŞEV BI SER KET!!!", (), note=_KURMANJI),
]
