from bs4 import BeautifulSoup
import re
import config
import sys

FILEPATH = ""

# =====================================================================
# HEURISTIC PARSING
# =====================================================================

def get_price_candidates(html):

	soup = BeautifulSoup(html, "lxml")

	for tag in soup(config.EXCLUDED_TAGS):
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


def extract_element(html, selector):
	if not selector or not html:
		return
	soup = BeautifulSoup(html, "lxml")
	return soup.select_one(selector)

#=====================================================================
# 	 						    HELPER
#=====================================================================

def build_css_selector(element):
	if element.get("id"):
		return f"#{element['id']}"

	classes = element.get("class")
	if classes:
		return f"{element.name}.{'.'.join(classes)}"

	return element.name


def choose_price(candidates):
	return candidates[0].text, candidates[0]
