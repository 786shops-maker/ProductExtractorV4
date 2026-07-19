"""
description_rules.py
"""

FABRICS=["raw silk","silk","poly silk","poly cotton","rocket net","chiffon","organza","cambric","cotton","lawn","slub lawn","swiss lawn","khaddar","karandi","linen","jacquard","dobby","velvet","viscose","net","habotai","wash & wear"]

PRINT_TYPES=["digital printed","printed","foil printed","screen printed","floral printed","dyed","plain"]

EMBROIDERY_LOCATIONS=["front","back","front panel","back panel","left panel","right panel","side panel","kali","neckline","sleeves","cuff","hem","border","motif","motifs","patch","pallu","lace"]

SHIRT_KEYWORDS=["shirt","front","back","panel","kali","neckline","sleeves","motif","patch"]
TROUSER_KEYWORDS=["trouser","trousers","pants","shalwar","bottom"]
DUPATTA_KEYWORDS=["dupatta","shawl","pallu"]

IGNORE_PATTERNS=[
"sku","availability","model is wearing","actual color may vary",
"accessories not included","care instructions","dry clean",
"wash separately","shipping","returns"
]

MEASUREMENT_REGEX=r"\b\d+(?:\.\d+)?\s*(?:m|meter|meters|yard|yards|pcs|pc|pieces?)\b"
