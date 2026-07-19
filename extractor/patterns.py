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

