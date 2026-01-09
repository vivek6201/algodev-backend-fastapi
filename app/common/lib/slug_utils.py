from slugify import slugify

SLUG_REPLACEMENTS = {
    "+": "p",
    "#": "sharp",
}


def create_slug(text: str) -> str:
    replacements = [[k, v] for k, v in SLUG_REPLACEMENTS.items()]
    return slugify(text, replacements=replacements)
