import re


REMOVE_PATTERNS = [

    r"model\s+height.*",
    r"dry\s+clean.*",
    r"exchange\s+policy.*",
    r"return\s+policy.*",
    r"shipping.*",
    r"delivery.*",
    r"color\s+may\s+vary.*",
    r"actual\s+product.*",
    r"photography.*",
    r"due\s+to\s+lighting.*",
    r"sku.*",
]


class DescriptionCleaner:

    @staticmethod
    def clean(text):

        if not text:
            return ""

        text = text.replace("\r", "\n")

        lines = []

        for line in text.split("\n"):

            line = line.strip()

            if not line:
                continue

            remove = False

            low = line.lower()

            for pattern in REMOVE_PATTERNS:

                if re.search(pattern, low):

                    remove = True
                    break

            if remove:
                continue

            line = re.sub(r"\s+", " ", line)

            lines.append(line)

        return "\n".join(lines)
