from bs4 import BeautifulSoup
import re
import config
import sys

FILEPATH = ""

# =====================================================================
# HEURISTIC PARSING
# =====================================================================

def get_price(html):

	soup = BeautifulSoup(html, "lxml")

	for tag in soup([config.EXCLUDED_TAGS):
		tag.decompose()


	possible_prices = soup.find_all(string=re.compile(config.NUMBER_PATTERN))

	price_candidates = []

	for element in possible_prices:
		is_valid = True
		curr = element
		for _ in range(3):
			if not curr or not is_valid:
				break

			if any(et in curr.parent.text.lower() for et in config.EXCLUDED_TERMS):
				is_valid = False

			curr = curr.parent

		if not is_valid:
			continue

		classes = " ".join(curr.get("class", [])) if isinstance(curr.get("class"), list) else curr.get("class", "")
		element_ids = curr.get("id", "")
		combined_attributes = f"{classes} {element_ids}".lower()

		if any(s in curr.text for s in config.CURRENCY_SYMBOLS) or re.search(config.PRICE_TAGS, combined_attributes):
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

