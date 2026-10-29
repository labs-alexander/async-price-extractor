from bs4 import BeautifulSoup
import re
import config
import sys

# =====================================================================
# UTILS/TEMPORARY
# =====================================================================

def test_function(html_path):
    with open(html_path, "r", encoding="utf-8") as f:
        return f.read()

# =====================================================================
# FLOW TEST
# =====================================================================

FILEPATH = ""

def main():
    html_file = test_function(FILEPATH)
    results = get_price(html=html_file)
    print(results)

# =====================================================================
# HEURISTIC PARSING
# =====================================================================

def parser1(html, pattern=config.PRICE_TAGS):
    results = re.findall(pattern, html)
    return results


def get_price(html, pattern=config.PRICE_TAGS):
    soup = BeautifulSoup(html, "lxml")
    for tag in soup(config.EXCLUDED_TAGS):
        tag.decompose()

    possible_prices = soup.find_all(string=re.compile(config.NUMBER_PATTERN))

    price_candidates = []
    for element in possible_prices:
        is_valid = True
        curr = element

        for _ in range(3):
            if not curr:
                break
                
            if any(excluded_word in curr.text.lower() for excluded_word in config.EXCLUDED_TERMS):
                is_valid = False

            curr = curr.parent

        if not is_valid:
            continue

        classes = " ".join(curr.get("class", [])) if isinstance(curr.get("class"), list) else curr.get("class", "")
        element_id = curr.get("id", "")
        combined_attributes = f"{classes} {element_id}".lower()

        if re.search(config.PRICE_TAGS, combined_attributes) or any(w in curr.text for w in config.CURRENCY_SYMBOLS):
            parent = element.parent
            if not parent:
                continue

            price_candidates.append(parent)

    return price_candidates


def find_name_candidates(html):
    name_candidates = []
    soup = BeautifulSoup(html, "lxml")

    h1 = soup.find("h1")
    if h1:
        name_candidates.append(h1)

    return name_candidates


def clean_html():
    pass    


def find_candidates(html_bruto):
    soup_clean = BeautifulSoup(html_bruto, "lxml")
    for tag in soup_clean(config.EXCLUDED_TAGS):
        tag.decompose()

    number_pattern = re.compile(config.NUMBER_PATTERN)
    currency_symbols = config.CURRENCY_SYMBOLS

    price_candidates = []
    for element in soup_clean.find_all(string=lambda text: text and number_pattern.search(text)):
        parent = element.find_parent()
        if not parent:
            continue

        texto_parent = parent.text
        if not any(s in texto_parent for s in currency_symbols):
            continue

        texto_lower = texto_parent.lower()
        if any(p in texto_lower for p in config.EXCLUDED_TERMS):
            continue

        price_candidates.append(str(parent))

    name_candidates = []
    h1 = soup_clean.find("h1")
    if h1:
        name_candidates.append(str(h1))

    return price_candidates, name_candidates

if __name__ == "__main__":
    html = test_function(FILEPATH)
    price, name = find_candidates(html)
    print(f"Old version: {price}")
    print("New version:")
    main()
    print(find_name_candidates(html))
