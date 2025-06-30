allowed_keywords = [
    # --- Sexual & Reproductive Health ---
    "sti", "std", "sexually transmitted", "infection", "hiv", "aids", "gonorrhea", "chlamydia",
    "syphilis", "herpes", "hpv", "hepatitis b", "hepatitis c", "trichomoniasis", "genital warts",
    "genital herpes", "condom", "safe sex", "unprotected sex", "birth control", "contraception",
    "iud", "implant", "injection", "menstruation", "period", "cycle", "puberty", "ovulation",
    "pcos", "endometriosis", "vaginal discharge", "yeast infection", "bacterial vaginosis",
    "uti", "cystitis", "pregnancy", "teenage pregnancy", "prenatal", "postnatal", "labor",
    "miscarriage", "abortion", "cesarean", "breastfeeding", "lactation", "weaning",
    "infant nutrition", "fertility", "infertility", "semen", "sperm", "fertilization",
    "obstetrician", "gynecologist", "teen", "teenage", "adolescent", "puberty signs",

    # --- Mental Health ---
    "mental health", "depression", "anxiety", "stress", "self-esteem", "trauma", "ptsd",
    "bullying", "counseling", "therapy", "psychologist", "emotional health", "grief",
    "suicide prevention", "self-harm",

    # --- General Youth Health ---
    "nutrition", "malnutrition", "exercise", "fitness", "hygiene", "personal hygiene",
    "sanitation", "cleanliness", "vaccination", "immunization", "health screening",
    "deworming", "vision", "hearing", "oral health", "dental hygiene", "diet", "balanced diet",
    "body changes", "growth spurt", "hormones", "development", "body image", "peer pressure",

    # --- Social & Risk Issues ---
    "drug abuse", "alcohol", "smoking", "peer pressure", "risky behavior", "early marriage",
    "gender violence", "sexual abuse", "consent", "rape", "domestic violence", "human trafficking",

    # --- Family & Relationship Topics ---
    "relationships", "family planning", "parenting", "communication", "dating", "love",
    "intimacy", "respect", "boundaries", "trust", "empathy", "conflict resolution",

    # --- School & Community Health ---
    "school health", "peer education", "school counseling", "teacher support",
    "community health", "health clubs", "youth programs", "adolescent health services",

    # --- Diseases & Conditions ---
    "malaria", "typhoid", "tuberculosis", "diarrhea", "cholera", "flu", "cold", "fever",
    "headache", "pain", "skin infections", "rashes", "allergy", "asthma", "dehydration",

    # --- Health Access & Rights ---
    "health rights", "health services", "reproductive rights", "youth clinic", "access to care",
    "health education", "adolescent health", "health worker", "clinic", "hospital", "nurse",
    "doctor", "treatment", "diagnosis", "medication", "pharmacy",

    # --- Technology & Media Related ---
    "health app", "online counseling", "telemedicine", "mental health app", "digital health",
    "social media risks", "cyberbullying", "online safety",

    # --- Miscellaneous ---
    "first aid", "injury", "accident", "emergency", "safety", "health insurance", "nutritionist",
    "hygiene kit", "period product", "sanitary pad", "tampon", "menstrual cup",
    # STIs - Symptoms, Slang, Terms
    "vaginal itching", "penile discharge", "burning urination", "pelvic pain", "genital sores",
    "anal discharge", "anal itching", "painful intercourse", "scrotal swelling", "itchy genitals",
    "lesions", "ulcers", "warts", "chancre", "inguinal lymph nodes", "urethral discharge",
    "bacterial std", "viral std", "parasitic std", "stis in males", "stis in females",
    "silent infection", "co-infection", "superinfection", "asymptomatic", "seropositive",
    "syphilitic rash", "congenital syphilis", "pelvic inflammatory disease", "pid", "genital pain",
    "non-gonococcal urethritis", "ngu", "mycoplasma genitalium", "mucopurulent", "serology",
    "discharge smell", "odor", "itching during urination", "rash in genital area", "painful urination",

    # STIs - Prevention, Testing, Treatment
    "sti screening", "rapid hiv test", "sti test", "sti treatment", "partner notification",
    "contact tracing", "post-exposure prophylaxis", "pep", "pre-exposure prophylaxis", "prep",
    "antiviral", "antibiotic treatment", "penicillin shot", "azithromycin", "doxycycline",
    "antiretroviral therapy", "art", "sti prevention", "sti vaccine", "hpv vaccine", "gardasil",
    "hepatitis vaccine", "free testing", "std counseling", "testing center", "walk-in clinic",
    "anonymous testing", "stigma", "sexual health service", "sti recurrence", "reinfection",
    "treatment resistance", "compliance", "testing positive", "partner therapy", "follow-up test",
    "sti clinic", "self-testing", "home test kit",

    # Teenage Pregnancy - Causes, Risks, Education
    "unplanned pregnancy", "early pregnancy", "teen fertility", "pregnancy test", "morning after pill",
    "emergency contraception", "missed period", "first trimester", "teen prenatal care",
    "no antenatal visit", "pregnancy rumors", "teen childbirth", "school dropout", "economic burden",
    "peer pressure pregnancy", "rape-related pregnancy", "teen rape", "incest", "consensual sex",
    "early sex", "first sexual experience", "family rejection", "neglected teen mother",
    "pregnancy scare", "pregnancy myths", "backstreet abortion", "unsafe abortion", "early parenting",
    "child bride", "underage sex", "pregnancy regret", "single teen mother", "fatherless child",
    "multiple abortions", "birth at 15", "birth at 14", "lack of sex education",

    # Teenage Pregnancy - Support, Services, Advocacy
    "youth support group", "pregnancy hotline", "teen mother support", "counseling for teens",
    "crisis pregnancy center", "school reentry", "teen prenatal class", "teen-friendly clinic",
    "community health volunteers", "girl empowerment", "teen outreach", "parenting class",
    "peer counseling", "youth shelter", "emotional support", "young fathers", "teen dad",
    "male involvement", "support circle", "pregnancy resource center", "referral for abortion",
    "pregnancy care plan", "confidential service", "clinic for teens", "family resistance",
    "pregnancy due date", "maternity leave for teens", "government program for teen moms",
    "pregnancy support grant", "teen welfare", "baby daddy", "child custody", "young caregiver",

    # Organizations / Campaigns / Advocacy
    "planned parenthood", "who sti", "unfpa", "teen pregnancy prevention", "adolescent reproductive health",
    "cdc std prevention", "unicef hiv", "youth friendly service", "sex ed", "reproductive justice",
    "girls not brides", "girl child rights", "un women", "reprohealth", "ngo for teens", "public health unit",
    "safe motherhood", "school-based clinic", "ngos fighting teenage pregnancy", "adolescent health initiative",
    "school nurse", "teenage health club", "community awareness", "youth mentorship", "peer educator",

    # Slang/Informal terms (commonly used among teens)
    "burning", "the clap", "drip", "got burnt", "preggo", "baby bump", "wrapped it", "rubber", "pull out", 
    "knocked up", "smashed raw", "skipped period", "positive stick", "clean", "dirty", "raw dog",
    "popped the cherry", "spilled inside", "cream pie", "no glove", "hit it raw",
     "condom", "birthcontrol", "fertility", "miscarriage", "ectopic", "ovulation", "periods", "menopause",
    "cervix", "uterus", "placenta", "follicle", "zygote", "embryo", "fetus", "labor", "delivery", "midwife",
    "doula", "infertility", "toxemia", "preeclampsia", "gestation", "menstrual", "clitoris", "vagina",
    "penis", "testes", "scrotum", "urethra", "semen", "sperm", "ovary", "estrogen", "progesterone",
    "androgen", "hormones", "paptest", "papsmear", "hpv", "chlamydia", "gonorrhea", "syphilis", "herpes",
    "hepatitis", "aids", "hiv", "trichomoniasis", "candida", "puberty", "masturbation", "ejaculation",
    "menstrualcycle", "contraception", "abstinence", "sterilization", "vasectomy", "tubal", "injection",
    "implant", "iud", "diaphragm", "spermicides", "emergency", "contraceptive", "fertilization", "zygote",
    "prenatal", "postnatal", "breastfeeding", "nurture", "parenthood", "adoption", "foster", "abortion",
    "miscarriage", "birthrate", "teenager", "adolescent", "youth", "pregnant", "newborn", "infant",
    "childbirth", "maternal", "neonatal", "stillbirth", "midwifery", "contraceptives", "familyplanning",
    "sexuallytransmitted", "infection", "screening", "diagnosis", "condom", "birthcontrol", "fertility", "miscarriage", "ectopic", "ovulation", "periods", "menopause",
    "cervix", "uterus", "placenta", "follicle", "zygote", "embryo", "fetus", "labor", "delivery", "midwife",
    "doula", "infertility", "toxemia", "preeclampsia", "gestation", "menstrual", "clitoris", "vagina",
    "penis", "testes", "scrotum", "urethra", "semen", "sperm", "ovary", "estrogen", "progesterone",
    "androgen", "hormones", "paptest", "papsmear", "hpv", "chlamydia", "gonorrhea", "syphilis", "herpes",
    "hepatitis", "aids", "hiv", "trichomoniasis", "candida", "puberty", "masturbation", "ejaculation",
    "menstrualcycle", "contraception", "abstinence", "sterilization", "vasectomy", "tubal", "injection",
    "implant", "iud", "diaphragm", "spermicides", "emergency", "contraceptive", "fertilization", "zygote",
    "prenatal", "postnatal", "breastfeeding", "nurture", "parenthood", "adoption", "foster", "abortion",
    "miscarriage", "birthrate", "teenager", "adolescent", "youth", "pregnant", "newborn", "infant",
    "childbirth", "maternal", "neonatal", "stillbirth", "midwifery", "contraceptives", "familyplanning",
    "sexuallytransmitted", "infection", "screening", "diagnosis", "treatment", "prevention", "education",
    "awareness", "testing", "vaccine", "counseling", "support"
]
