# app/species_db.py

SPECIES_METADATA = {
    "ahaetulla prasina": {
        "common_name": "Asian Vine Snake",
        "local_names": {"hi": "हरहरा (Harhara)", "gu": "લીલવણ (Lilvan)"},
        "toxicity_status": "MILDLY_VENOMOUS / HARMLESS TO HUMANS",
        "venom_type": "Rear-fanged (Mild)",
        "is_big_four": False
    },
    "amphiesma stolatum": {
        "common_name": "Buff Striped Keelback",
        "local_names": {"hi": "सीता लट (Sita Lat)", "gu": "દંડિયા સાપ (Dandiya)"},
        "toxicity_status": "NON_VENOMOUS",
        "venom_type": "None",
        "is_big_four": False
    },
    "bungarus caeruleus": {
        "common_name": "Common Krait",
        "local_names": {"hi": "करैत (Karait)", "gu": "કળતરા (Kalatra)"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Neurotoxic",
        "is_big_four": True
    },
    "bungarus fasciatus": {
        "common_name": "Banded Krait",
        "local_names": {"hi": "अहिराज (Ahiraj)", "gu": "પીળો કરૈત (Pilo Karait)"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Neurotoxic",
        "is_big_four": False
    },
    "chrysopelea ornata": {
        "common_name": "Ornate Flying Snake",
        "local_names": {"hi": "उड़ने वाला सांप", "gu": "ઉડતો સાપ"},
        "toxicity_status": "MILDLY_VENOMOUS / HARMLESS TO HUMANS",
        "venom_type": "Rear-fanged (Mild)",
        "is_big_four": False
    },
    "daboia russelii": {
        "common_name": "Russell's Viper",
        "local_names": {"hi": "घोणस (Daboia)", "gu": "ચિતળ (Chital)"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Haemotoxic / Cytotoxic",
        "is_big_four": True
    },
    "dendrelaphis pictus": {
        "common_name": "Painted Bronzeback",
        "local_names": {"hi": "कांस्य अजगर प्रकार", "gu": "તાંબડી સાપ"},
        "toxicity_status": "NON_VENOMOUS",
        "venom_type": "None",
        "is_big_four": False
    },
    "naja naja": {
        "common_name": "Indian Cobra",
        "local_names": {"hi": "नाग (Naag)", "gu": "નાગ (Naag)"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Neurotoxic",
        "is_big_four": True
    },
    "ophiophagus hannah": {
        "common_name": "King Cobra",
        "local_names": {"hi": "राजनाग (Rajnag)", "gu": "કિંગ કોબ્રા"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Neurotoxic",
        "is_big_four": False
    },
    "psammodynastes pulverulentus": {
        "common_name": "Mock Viper",
        "local_names": {"hi": "नकली वाइपर", "gu": "મોક વાઇપર"},
        "toxicity_status": "MILDLY_VENOMOUS / HARMLESS TO HUMANS",
        "venom_type": "Rear-fanged (Mild)",
        "is_big_four": False
    },
    "ptyas korros": {
        "common_name": "Indochinese Rat Snake",
        "local_names": {"hi": "धामिन प्रजाति", "gu": "ધામણ જાતિ"},
        "toxicity_status": "NON_VENOMOUS",
        "venom_type": "None",
        "is_big_four": False
    },
    "ptyas mucosa": {
        "common_name": "Oriental / Indian Rat Snake",
        "local_names": {"hi": "धामन (Dhaman)", "gu": "ધામણ (Dhaman)"},
        "toxicity_status": "NON_VENOMOUS",
        "venom_type": "None",
        "is_big_four": False
    },
    "trimeresurus albolabris": {
        "common_name": "White-lipped Pit Viper",
        "local_names": {"hi": "हरा वाइपर", "gu": "લીલો ઝેરી સાપ"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Haemotoxic",
        "is_big_four": False
    },
    "trimeresurus purpureomaculatus": {
        "common_name": "Mangrove Pit Viper",
        "local_names": {"hi": "मैंग्रोव पिट वाइपर", "gu": "મેન્ગ્રોવ વાઇપર"},
        "toxicity_status": "HIGHLY_VENOMOUS",
        "venom_type": "Haemotoxic",
        "is_big_four": False
    },
    "xenochrophis piscator": {
        "common_name": "Checkered Keelback",
        "local_names": {"hi": "ढोंढिया (Dhondhiya)", "gu": "ડંડીયુ (Dandiyu)"},
        "toxicity_status": "NON_VENOMOUS",
        "venom_type": "None",
        "is_big_four": False
    }
}

DEFAULT_METADATA = {
    "common_name": "Unknown Snake Species",
    "local_names": {"hi": "अज्ञात प्रजाति", "gu": "અજ્ઞાત સાપ"},
    "toxicity_status": "UNKNOWN / TREAT AS POTENTIALLY VENOMOUS",
    "venom_type": "Unknown",
    "is_big_four": False
}

def get_species_info(species_name: str) -> dict:
    cleaned_key = species_name.strip().lower()
    return SPECIES_METADATA.get(cleaned_key, DEFAULT_METADATA)