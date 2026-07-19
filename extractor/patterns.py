"""
ProductExtractorV4
patterns.py

Central knowledge base used by all parsers.

Every parser imports from here instead of maintaining its own
lists of fabrics, colors and garment keywords.
"""

# ==========================================================
# FABRIC DATABASE
# ==========================================================

FABRICS = {

    # ---------- Lawn ----------

    "Digital Printed Lawn": [
        "digital printed lawn",
        "digital print lawn",
        "printed digital lawn"
    ],

    "Printed Lawn": [
        "printed lawn",
        "print lawn"
    ],

    "Dyed Lawn": [
        "dyed lawn"
    ],

    "Embroidered Lawn": [
        "embroidered lawn"
    ],

    "Luxury Lawn": [
        "luxury lawn"
    ],

    "Swiss Lawn": [
        "swiss lawn"
    ],

    "Premium Lawn": [
        "premium lawn"
    ],

    "Lawn": [
        "lawn"
    ],

    # ---------- Cambric ----------

    "Printed Cambric": [
        "printed cambric"
    ],

    "Dyed Cambric": [
        "dyed cambric"
    ],

    "Cambric": [
        "cambric"
    ],

    # ---------- Cotton ----------

    "Digital Printed Cotton": [
        "digital printed cotton"
    ],

    "Printed Cotton": [
        "printed cotton"
    ],

    "Dyed Cotton": [
        "dyed cotton"
    ],

    "Cotton": [
        "cotton"
    ],

    # ---------- Silk ----------

    "Digital Printed Silk": [
        "digital printed silk"
    ],

    "Printed Silk": [
        "printed silk"
    ],

    "Dyed Silk": [
        "dyed silk"
    ],

    "Raw Silk": [
        "raw silk",
        "rawsilk"
    ],

    "PK Silk": [
        "pk silk"
    ],

    "Poly Silk": [
        "poly silk"
    ],

    "Russian Silk": [
        "russian silk"
    ],

    "Korean Silk": [
        "korean silk"
    ],

    "Italian Silk": [
        "italian silk"
    ],

    "Grip Silk": [
        "grip silk"
    ],

    "Mashru Silk": [
        "mashru silk"
    ],

    "Tissue Silk": [
        "tissue silk"
    ],

    "Silk": [
        "silk"
    ],

    # ---------- Chiffon ----------

    "Digital Printed Chiffon": [
        "digital printed chiffon"
    ],

    "Printed Chiffon": [
        "printed chiffon"
    ],

    "Dyed Chiffon": [
        "dyed chiffon"
    ],

    "Embroidered Chiffon": [
        "embroidered chiffon"
    ],

    "Chiffon": [
        "chiffon"
    ],

    # ---------- Organza ----------

    "Printed Organza": [
        "printed organza"
    ],

    "Dyed Organza": [
        "dyed organza"
    ],

    "Embroidered Organza": [
        "embroidered organza"
    ],

    "Organza": [
        "organza"
    ],

    # ---------- Net ----------

    "Rocket Net": [
        "rocket net"
    ],

    "Khaddi Net": [
        "khaddi net"
    ],

    "Cotton Net": [
        "cotton net"
    ],

    "Soft Net": [
        "soft net"
    ],

    "Net": [
        "net"
    ],

    # ---------- Others ----------

    "Jacquard": [
        "jacquard"
    ],

    "Dobby": [
        "dobby"
    ],

    "Khaddar": [
        "khaddar"
    ],

    "Karandi": [
        "karandi"
    ],

    "Linen": [
        "linen"
    ],

    "Viscose": [
        "viscose"
    ],

    "Velvet": [
        "velvet"
    ],

    "Poly Cotton": [
        "poly cotton"
    ],

    "Wash & Wear": [
        "wash & wear",
        "wash and wear"
    ],

    "Habotai": [
        "habotai"
    ]
}
# ==========================================================
# DESIGNER COLOUR DATABASE
# ==========================================================

COLORS = [

    # ---------- White ----------

    "White",
    "Off White",
    "Ivory",
    "Pearl White",
    "Cream",
    "Snow White",

    # ---------- Beige ----------

    "Beige",
    "Light Beige",
    "Dark Beige",
    "Sand",
    "Camel",
    "Nude",
    "Taupe",

    # ---------- Pink ----------

    "Pink",
    "Baby Pink",
    "Tea Pink",
    "Powder Pink",
    "Blush Pink",
    "Rose Pink",
    "Dusty Pink",
    "Hot Pink",
    "Deep Pink",
    "Shocking Pink",
    "Coral Pink",

    # ---------- Peach ----------

    "Peach",
    "Light Peach",
    "Dark Peach",
    "Coral",
    "Salmon",

    # ---------- Red ----------

    "Red",
    "Deep Red",
    "Cherry Red",
    "Ruby",
    "Crimson",
    "Scarlet",
    "Maroon",
    "Wine",
    "Burgundy",

    # ---------- Orange ----------

    "Orange",
    "Burnt Orange",
    "Rust",
    "Terracotta",

    # ---------- Yellow ----------

    "Yellow",
    "Mustard",
    "Mustard Yellow",
    "Lemon",
    "Lemon Yellow",
    "Golden Yellow",
    "Sunflower",

    # ---------- Green ----------

    "Green",
    "Sea Green",
    "Sage Green",
    "Olive Green",
    "Bottle Green",
    "Mint",
    "Mint Green",
    "Emerald",
    "Emerald Green",
    "Parrot Green",
    "Mehndi",
    "Pista",
    "Pista Green",
    "Apple Green",
    "Forest Green",

    # ---------- Blue ----------

    "Blue",
    "Sky Blue",
    "Ice Blue",
    "Powder Blue",
    "Royal Blue",
    "Navy Blue",
    "Midnight Blue",
    "Turquoise",
    "Turquoise Blue",
    "Aqua",
    "Aqua Blue",
    "Teal",
    "Ferozi",
    "Peacock Blue",

    # ---------- Purple ----------

    "Purple",
    "Lavender",
    "Lilac",
    "Mauve",
    "Deep Purple",
    "Violet",
    "Plum",

    # ---------- Brown ----------

    "Brown",
    "Chocolate",
    "Chocolate Brown",
    "Coffee",
    "Coffee Brown",
    "Mocha",

    # ---------- Grey ----------

    "Grey",
    "Light Grey",
    "Dark Grey",
    "Charcoal",
    "Silver",
    "Ash Grey",

    # ---------- Black ----------

    "Black",
    "Jet Black",
    "Charcoal Black",

]
# ==========================================================
# GARMENT COMPONENTS
# Canonical embroidery locations
# ==========================================================

GARMENT_COMPONENTS = {

    # ------------------------------------------------------
    # Neckline
    # ------------------------------------------------------

    "neckline": [
        "neckline",
        "neck line",
        "neck",
        "neck patch",
        "neckline patch",
        "neck motif",
        "neck motifs",
        "neck embroidery"
    ],

    # ------------------------------------------------------
    # Front
    # ------------------------------------------------------

    "front": [
        "front",
        "shirt front",
        "front body",
        "front kali",
        "front kalli",
        "front center",
        "front centre"
    ],

    # ------------------------------------------------------
    # Front Panels
    # ------------------------------------------------------

    "front panels": [

        "front panel",
        "front panels",

        "front left panel",
        "front right panel",

        "left front panel",
        "right front panel",

        "front side panel",
        "front side panels",

        "front center panel",
        "front centre panel",

        "center panel",
        "centre panel",

        "left panel",
        "right panel",

        "left kali",
        "right kali",

        "kali",
        "kalis"
    ],

    # ------------------------------------------------------
    # Front Motifs
    # ------------------------------------------------------

    "front motifs": [

        "front motif",
        "front motifs",

        "motif",
        "motifs",

        "bunch",
        "bunches"
    ],

    # ------------------------------------------------------
    # Back
    # ------------------------------------------------------

    "back": [

        "back",

        "shirt back",

        "back body",

        "back panel",

        "back panels",

        "back side panel",

        "back side panels"
    ],

    # ------------------------------------------------------
    # Sleeves
    # ------------------------------------------------------

    "sleeves": [

        "sleeve",

        "sleeves",

        "full sleeve",

        "full sleeves",

        "half sleeve",

        "half sleeves",

        "cuff",

        "cuffs"
    ],

    # ------------------------------------------------------
    # Daman
    # ------------------------------------------------------

    "daman": [

        "daman",

        "shirt daman",

        "hem",

        "shirt hem"
    ],

    # ------------------------------------------------------
    # Yoke
    # ------------------------------------------------------

    "yoke": [

        "yoke",

        "front yoke",

        "back yoke"
    ],

    # ------------------------------------------------------
    # Dupatta
    # ------------------------------------------------------

    "dupatta": [

        "dupatta"
    ],

    # ------------------------------------------------------
    # Dupatta Pallu
    # ------------------------------------------------------

    "dupatta pallu": [

        "pallu",

        "dupatta pallu",

        "pallu border",

        "dupatta pallu border"
    ],

    # ------------------------------------------------------
    # Trouser
    # ------------------------------------------------------

    "trouser": [

        "trouser",

        "pants",

        "shalwar",

        "bottom"
    ],

    # ------------------------------------------------------
    # Trouser Border
    # ------------------------------------------------------

    "trouser border": [

        "trouser border",

        "pant border",

        "shalwar border"
    ]
}
# ==========================================================
# GARMENT COMPONENTS
# Canonical embroidery locations
# ==========================================================

GARMENT_COMPONENTS = {

    # ------------------------------------------------------
    # Neckline
    # ------------------------------------------------------

    "neckline": [
        "neckline",
        "neck line",
        "neck",
        "neck patch",
        "neckline patch",
        "neck motif",
        "neck motifs",
        "neck embroidery"
    ],

    # ------------------------------------------------------
    # Front
    # ------------------------------------------------------

    "front": [
        "front",
        "shirt front",
        "front body",
        "front kali",
        "front kalli",
        "front center",
        "front centre"
    ],

    # ------------------------------------------------------
    # Front Panels
    # ------------------------------------------------------

    "front panels": [

        "front panel",
        "front panels",

        "front left panel",
        "front right panel",

        "left front panel",
        "right front panel",

        "front side panel",
        "front side panels",

        "front center panel",
        "front centre panel",

        "center panel",
        "centre panel",

        "left panel",
        "right panel",

        "left kali",
        "right kali",

        "kali",
        "kalis"
    ],

    # ------------------------------------------------------
    # Front Motifs
    # ------------------------------------------------------

    "front motifs": [

        "front motif",
        "front motifs",

        "motif",
        "motifs",

        "bunch",
        "bunches"
    ],

    # ------------------------------------------------------
    # Back
    # ------------------------------------------------------

    "back": [

        "back",

        "shirt back",

        "back body",

        "back panel",

        "back panels",

        "back side panel",

        "back side panels"
    ],

    # ------------------------------------------------------
    # Sleeves
    # ------------------------------------------------------

    "sleeves": [

        "sleeve",

        "sleeves",

        "full sleeve",

        "full sleeves",

        "half sleeve",

        "half sleeves",

        "cuff",

        "cuffs"
    ],

    # ------------------------------------------------------
    # Daman
    # ------------------------------------------------------

    "daman": [

        "daman",

        "shirt daman",

        "hem",

        "shirt hem"
    ],

    # ------------------------------------------------------
    # Yoke
    # ------------------------------------------------------

    "yoke": [

        "yoke",

        "front yoke",

        "back yoke"
    ],

    # ------------------------------------------------------
    # Dupatta
    # ------------------------------------------------------

    "dupatta": [

        "dupatta"
    ],

    # ------------------------------------------------------
    # Dupatta Pallu
    # ------------------------------------------------------

    "dupatta pallu": [

        "pallu",

        "dupatta pallu",

        "pallu border",

        "dupatta pallu border"
    ],

    # ------------------------------------------------------
    # Trouser
    # ------------------------------------------------------

    "trouser": [

        "trouser",

        "pants",

        "shalwar",

        "bottom"
    ],

    # ------------------------------------------------------
    # Trouser Border
    # ------------------------------------------------------

    "trouser border": [

        "trouser border",

        "pant border",

        "shalwar border"
    ]
}
IGNORE_EMBROIDERY_COMPONENTS = [

    "border",

    "front border",

    "back border",

    "sleeve border",

    "neck border",

    "organza border",

    "lace",

    "patti",

    "patch",

    "strip",

    "tassel",

    "frill",

    "ruffle",

    "hem lace",

    "gota",

    "piping",

    "edging"
]
# ==========================================================
# IGNORE PHRASES
# Entire lines containing these phrases are discarded
# ==========================================================

IGNORE_PHRASES = [

    # -------------------------
    # Model
    # -------------------------

    "model is wearing",
    "model wears",
    "model height",
    "height of model",
    "model size",
    "size worn",
    "wearing size",

    # -------------------------
    # Care
    # -------------------------

    "dry clean",
    "machine wash",
    "hand wash",
    "wash separately",
    "do not bleach",
    "iron inside out",
    "care instructions",
    "washing instructions",

    # -------------------------
    # Colour Disclaimer
    # -------------------------

    "actual color may vary",
    "actual colour may vary",
    "colour may vary",
    "color may vary",
    "screen resolution",
    "lighting effect",
    "photography",
    "monitor settings",

    # -------------------------
    # Shipping
    # -------------------------

    "shipping",
    "delivery",
    "dispatch",
    "free shipping",
    "worldwide shipping",

    # -------------------------
    # Return
    # -------------------------

    "return policy",
    "exchange policy",
    "refund policy",
    "returns",
    "refunds",

    # -------------------------
    # Availability
    # -------------------------

    "availability",
    "in stock",
    "out of stock",
    "sold out",
    "only few left",

    # -------------------------
    # Add-on
    # -------------------------

    "add-on",
    "addon",
    "optional",
    "accessories",
    "accessory",
    "jewellery",
    "jewelry",
    "shoes",
    "heels",
    "bag",
    "clutch",

    # -------------------------
    # Decorative
    # -------------------------

    "illustrative purposes",
    "decorative accessories",
    "not included",
    "for shoot purpose",
    "used for styling",

    # -------------------------
    # Technical
    # -------------------------

    "sku:",
    "product code",
    "barcode",
    "ean",
    "upc",

    # -------------------------
    # Generic
    # -------------------------

    "click here",
    "read more",
    "view details",
    "share",
    "wishlist",
    "compare",
    "customer reviews",
    "review",
    "rating",
]
# ==========================================================
# IGNORE PHRASES
# Entire lines containing these phrases are discarded
# ==========================================================

IGNORE_PHRASES = [

    # -------------------------
    # Model
    # -------------------------

    "model is wearing",
    "model wears",
    "model height",
    "height of model",
    "model size",
    "size worn",
    "wearing size",

    # -------------------------
    # Care
    # -------------------------

    "dry clean",
    "machine wash",
    "hand wash",
    "wash separately",
    "do not bleach",
    "iron inside out",
    "care instructions",
    "washing instructions",

    # -------------------------
    # Colour Disclaimer
    # -------------------------

    "actual color may vary",
    "actual colour may vary",
    "colour may vary",
    "color may vary",
    "screen resolution",
    "lighting effect",
    "photography",
    "monitor settings",

    # -------------------------
    # Shipping
    # -------------------------

    "shipping",
    "delivery",
    "dispatch",
    "free shipping",
    "worldwide shipping",

    # -------------------------
    # Return
    # -------------------------

    "return policy",
    "exchange policy",
    "refund policy",
    "returns",
    "refunds",

    # -------------------------
    # Availability
    # -------------------------

    "availability",
    "in stock",
    "out of stock",
    "sold out",
    "only few left",

    # -------------------------
    # Add-on
    # -------------------------

    "add-on",
    "addon",
    "optional",
    "accessories",
    "accessory",
    "jewellery",
    "jewelry",
    "shoes",
    "heels",
    "bag",
    "clutch",

    # -------------------------
    # Decorative
    # -------------------------

    "illustrative purposes",
    "decorative accessories",
    "not included",
    "for shoot purpose",
    "used for styling",

    # -------------------------
    # Technical
    # -------------------------

    "sku:",
    "product code",
    "barcode",
    "ean",
    "upc",

    # -------------------------
    # Generic
    # -------------------------

    "click here",
    "read more",
    "view details",
    "share",
    "wishlist",
    "compare",
    "customer reviews",
    "review",
    "rating",
]

# ==========================================================
# IGNORE WORDS
# Remove these words from parsed text
# ==========================================================

IGNORE_WORDS = [

    "meter",
    "meters",
    "metre",
    "metres",

    "yard",
    "yards",

    "piece",
    "pieces",

    "pc",
    "pcs",

    "set",

    "cm",
    "cms",

    "inch",
    "inches",

    "approx",

    "only",

    "new",

    "exclusive",

    "premium",

    "collection",

    "volume",

    "edition"
]
# ==========================================================
# REGEX CLEANUP
# ==========================================================

REMOVE_PATTERNS = [

    # measurements

    r"\d+(\.\d+)?\s*meters?",

    r"\d+(\.\d+)?\s*metres?",

    r"\d+(\.\d+)?\s*m\b",

    r"\d+(\.\d+)?\s*yards?",

    r"\d+(\.\d+)?\s*pcs?",

    r"\d+(\.\d+)?\s*pieces?",

    r"\d+(\.\d+)?\s*pc",

    r"\d+(\.\d+)?\s*inch",

    r"\d+(\.\d+)?\s*inches",

    r"\(\s*\d+.*?\)",

]
# ==========================================================
# BRAND ALIASES
# Normalize designer names
# ==========================================================

BRAND_ALIASES = {

    "j.": "Junaid Jamshed",
    "junaid jamshed": "Junaid Jamshed",
    "jj": "Junaid Jamshed",

    "gul ahmed": "Gul Ahmed",
    "ideas by gul ahmed": "Gul Ahmed",
    "ideas": "Gul Ahmed",

    "sana safinaz muzlin": "Sana Safinaz",
    "muzlin": "Sana Safinaz",
    "sana safinaz": "Sana Safinaz",

    "asim jofa": "Asim Jofa",

    "maria b": "Maria B",
    "mariab": "Maria B",

    "baroque": "Baroque",

    "ramsha": "Ramsha",

    "charizma": "Charizma",

    "cross stitch": "Cross Stitch",

    "ethnic": "Ethnic",

    "iznik": "Iznik",

    "junaid jamshed": "Junaid Jamshed",

    "khaadi": "Khaadi",

    "alkaram": "Alkaram",

    "alkaram studio": "Alkaram",

    "sapphire": "Sapphire",

    "limelight": "Limelight",

    "zellbury": "Zellbury",

    "so kamal": "So Kamal",

    "nishat linen": "Nishat Linen",

    "edenrobe": "Edenrobe",

    "azure": "Azure",

    "elan": "Elan",

    "faiza saqlain": "Faiza Saqlain",

    "republic womenswear": "Republic Womenswear",

    "jeem": "Jeem",

    "kanwal malik": "Kanwal Malik",

    "imrozia": "Imrozia",

    "noor by saadia asad": "Noor by Saadia Asad",

    "rang rasiya": "Rang Rasiya",

    "qalamkar": "Qalamkar",

    "bin saeed": "Bin Saeed",

    "adan libas": "Adan Libas"

}

# ==========================================================
# GARMENT PRIORITY
# ==========================================================

GARMENT_PRIORITY = [

    "shirt",

    "trouser",

    "dupatta"

]
# ==========================================================
# COMPONENT PRIORITY
# ==========================================================

COMPONENT_PRIORITY = [

    "front panels",

    "front motifs",

    "neckline",

    "front",

    "back",

    "sleeves",

    "daman",

    "yoke",

    "dupatta pallu",

    "dupatta",

    "trouser border",

    "trouser"

]
# ==========================================================
# FABRIC PRIORITY
# ==========================================================

FABRIC_PRIORITY = [

    "Digital Printed Lawn",

    "Printed Lawn",

    "Dyed Lawn",

    "Luxury Lawn",

    "Swiss Lawn",

    "Embroidered Lawn",

    "Lawn",

    "Digital Printed Cotton",

    "Printed Cotton",

    "Dyed Cotton",

    "Cotton",

    "Digital Printed Chiffon",

    "Printed Chiffon",

    "Dyed Chiffon",

    "Embroidered Chiffon",

    "Chiffon",

    "Digital Printed Silk",

    "Printed Silk",

    "Dyed Silk",

    "Raw Silk",

    "PK Silk",

    "Poly Silk",

    "Russian Silk",

    "Korean Silk",

    "Italian Silk",

    "Grip Silk",

    "Mashru Silk",

    "Tissue Silk",

    "Silk",

    "Rocket Net",

    "Khaddi Net",

    "Cotton Net",

    "Soft Net",

    "Net",

    "Poly Cotton",

    "Jacquard",

    "Dobby",

    "Karandi",

    "Khaddar",

    "Linen",

    "Viscose",

    "Velvet",

    "Wash & Wear",

    "Habotai"

]

# ==========================================================
# DETECTION PRIORITY
# ==========================================================

SEARCH_PRIORITY = [

    "json_ld",

    "product_json",

    "meta",

    "variants",

    "product_attributes",

    "product_description",

    "visible_html",

    "image_alt",

    "breadcrumbs",

    "url"

]
