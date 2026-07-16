import re

from slugify import slugify


def clean_text(text):

    if text is None:
        return ""

    text = re.sub(r"\s+", " ", text)

    return text.strip()


def make_filename(brand, title):

    name = f"{brand} {title}"

    return slugify(name)


def remove_empty(items):

    return [x for x in items if str(x).strip()]


def unique(items):

    seen = set()

    output = []

    for item in items:

        if item in seen:
            continue

        seen.add(item)

        output.append(item)

    return output