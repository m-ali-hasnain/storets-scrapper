import re
import scrapy
from selenium import webdriver
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.options import Options
import time
import json
from ..items import StoretsScrapperItem

# Constants
DISALLOWED_CATEGORIES = ["all-top", "all-dress"]
FIT_KEYWORDS = ["Maternity", "Petite", "Plus Size", "Curvy", "Tall"]
NECK_LINE_KEYWORDS = ["Scoop", "Round Neck," "U Neck", "U-Neck", "V Neck",
                      "V-neck", "V Shape", "V-Shape", "Deep", "Plunge", "Square",
                      "Straight", "Sweetheart", "Princess", "Dipped", "Surplice",
                      "Halter", "Asymetric", "One-Shoulder", "One Shoulder",
                      "Turtle", "Boat", "Off- Shoulder", "Collared", "Cowl", "Neckline"]

OCCASIONS_KEYWORDS = ["office", "work", "smart", "workwear", "wedding", "nuptials",
                      "night out", "evening", "spring", "summer", "day", "weekend",
                      "outdoor", "outdoors", "adventure", "black tie", "gown",
                      "formal", "cocktail", "date night", "vacation", "vacay", "fit",
                      "fitness", "athletics", "athleisure", "work out", "sweat",
                      "swim", "swimwear", "lounge", "loungewear"]

LENGTH_KEYWORDS = ["length", "mini", "short", "maxi", "crop", "cropped", "sleeves",
                   "tank", "top", "three quarter", "ankle", "long"]

STYLE_KEYWORDS = ["bohemian", "embellished", "sequin", "floral", "off shoulder",
                  "puff sleeve", "bodysuit", "shell", "crop", "corset", "tunic",
                  "bra", "camisole", "polo", "aviator", "shearling", "sherpa",
                  "biker", "bomber", "harrington", "denim", "jean", "leather",
                  "military", "quilted", "rain", "tuxedo", "windbreaker", "utility",
                  "duster", "faux fur", "overcoat", "parkas", "peacoat", "puffer",
                  "skater", "trench", "Fleece", "a line", "bodycon", "fitted",
                  "high waist", "high-low", "pencil", "pleat", "slip", "tulle",
                  "wrap", "cargo", "chino", "skort", "cigarette", "culottes",
                  "flare", "harem", "relaxed", "skinny", "slim", "straight leg",
                  "tapered", "wide leg", "palazzo", "stirrup", "bootcut", "boyfriend",
                  "loose", "mom", "jeggings", "backless", "bandage", "bandeau",
                  "bardot", "one-shoulder", "slinger", "shift", "t-shirt", "smock",
                  "sweater", "gown"]

AESTHETIC_KEYWORDS = ["E-girl", "VSCO girl", "Soft Girl", "Grunge", "CottageCore",
                      "Normcore", "Light Academia", "Dark Academia ", "Art Collective",
                      "Baddie", "WFH", "Black", "fishnet", "leather"]

NEGLECT_CATEGORIES_LIST = ['New in', 'Joggers', 'Multipacks', 'new-in',
                           'Socks', 'Exclusives at ASOS', 'Tracksuits & Joggers',
                           "Sportswear", "co-ords", "exclusives"]

CATEGORY_KEYWORDS = ['Bottom', 'Shift', 'Swim Brief', 'Quilted', 'Boyfriend',
                     'Padded', 'Track', 'Other', 'Oversized', 'Denim Skirt',
                     'Stick On Bra', 'Cardigan', 'Thong', 'Romper', 'Pea Coat',
                     'Skater', 'Swing', 'Lingerie & Sleepwear', 'Wrap', 'Cargo Pant',
                     'Cape', 'Trucker', 'Nursing', 'Bikini', 'Parka', 'Regular', 'Denim',
                     'Duster', 'Faux Fur', 'Hoodie', 'Bralet', 'Overcoat', 'Corset Top',
                     'T-Shirt', 'Mini', 'Maxi', 'Blazer', 'Super Skinny', 'Summer Dresses',
                     'Chino', 'Short', 'Set', 'Military', 'Overall', 'Vest', 'Bomber Jacket',
                     'Tea', 'Ski Suit', 'Work Dresses', 'High Waisted', 'Culotte', 'Overall Dress',
                     'Jean', 'Loungewear', 'Leather Jacket', 'Unpadded', 'Coats & Jackets', 'Underwired',
                     'Corset', 'Night gown', 'Poncho', 'Pant', 'Cigarette', 'Sweatpant', 'Rain Jacket',
                     'Loose', 'Swimwear & Beachwear', 'Shirt', 'Denim Jacket', 'Co-ord', 'Tight', 'Vacation Dress',
                     'Harrington', 'Bandage', 'Bootcut', 'Biker', 'Crop Top', 'Trench', 'Tracksuit', 'Suit Pant',
                     'Relaxed', 'Day Dresses', 'Tuxedo', 'Tapered', 'Wide Leg', 'Bohemian', 'Pleated', 'Wiggle',
                     'One Shoulder', 'Smock Dress', 'Flare', 'Peg Leg', 'Cover Up', 'Unitard', 'Sweater',
                     'Lounge', 'Top', 'Bodycon', 'Push Up', 'Slip', 'Knitwear', 'Leather', 'Pencil Dress',
                     'Off Shoulder', 'Jersey Short', 'Multiway', 'Balconette', 'Wax Jacket', 'Coat', 'Brief',
                     'Coach', 'Jumpsuits & Rompers', 'Bra', 'Long Sleeve', 'Fleece', 'Activewear', 'Jegging',
                     'Outerwear', 'Bandeau', 'Slim', 'Going Out Dresses', 'Bardot', 'Pajama', 'Sweatsuit',
                     'Blouse', 'Sweaters & Cardigans', 'Straight Leg', 'Windbreaker', 'Tank Top', 'Cold Shoulder',
                     'Halter', 'Dresses', 'T-Shirt', 'Trouser', 'Cami', 'Camis', 'Wedding Guest', 'Bodysuit', 'Triangle',
                     'Casual Dresses', 'Chino Short', 'Boiler Suit', 'Raincoat', 'Formal Dresses', 'Skinny',
                     'Jumper', 'Strapless', 'Cropped', 'Jacket', 'Bridesmaids Dress', 'Tunic', 'A Line',
                     'Denim Dress', 'Cocktail', 'Skirt', 'Jumpsuit', 'Shapewear', 'Occasion Dresses',
                     'Hoodies & Sweatshirts', 'Sweatshirt', 'Aviator', 'Sweater Dress', 'Sports Short',
                     'Shirt', 'Puffer', 'Cargo Short', 'Tulle', 'Swimsuit', 'Mom Jean', 'Legging',
                     'Plunge', 'Teddie', 'Denim Short', 'Intimate', 'Pencil Skirt', 'Backless', 'Tank']

CATEGORY_TO_TYPE = {
    'Co-ords': ['Co-ord', 'Sweatsuit', 'Tracksuit', 'Set'],
    'Coats & Jackets': ['Coats & Jacket', 'Cape', 'Cardigan', 'Coat', 'Jacket', 'Poncho', 'Ski Suit', 'Vest', 'Blazer'],
    'Dresses': ['Dresses', 'Bridesmaids Dress', 'Casual Dress', 'Going Out Dress', 'Occasion Dress',
                'Summer Dress', 'Work Dress', 'Formal Dress', 'Day Dress', 'Wedding Guest', 'Vacation Dress'],
    'Hoodies & Sweatshirts': ['Hoodies & Sweatshirts', 'Fleece', 'Hoodie', 'Sweatshirt'],
    'Denim': ['Denim Jacket', 'Denim Dress', 'Denim Skirt', 'Denim Short', 'Jean', 'Jegging'],
    'Jumpsuits & Rompers': ['Jumpsuits & Rompers', 'Boiler Suit', 'Jumpsuit', 'Overall', 'Romper', 'Unitard'],
    'Lingerie & Sleepwear': ['Lingerie & Sleepwear', 'Intimate', 'Bra', 'Brief', 'Corset', 'Bralet', 'Night gown',
                             'Pajama', 'Shapewear', 'Slip', 'Teddie', 'Thong', 'Tight', 'Bodysuit', 'Camis', 'Cami'],
    'Loungewear': ['Loungewear', 'Lounge', 'Activewear', 'Outerwear', 'Hoodie', 'Legging', 'Overall', 'Pajama',
                   'Sweatpant', 'Sweatshirt', 'Tracksuit', 'T-Shirt'],
    'Bottoms': ['Bottom', 'Chino', 'Legging', 'Pant', 'Suit Pant', 'Sweatpant', 'Tracksuit', 'Short', 'Skirt',
                'Trouser'],
    'Sweaters & Cardigans': ['Sweaters & Cardigans', 'Sweatpant', 'Cardigan', 'Sweater', 'Knitwear'],
    'Swimwear & Beachwear': ['Swimwear & Beachwear', 'Bikini', 'Cover Up', 'Short', 'Skirt', 'Swim Brief', 'Swimsuit'],
    'Tops': ['Top', 'Blouse', 'Bodysuit', 'Bralet', 'Camis', 'Corset Top', 'Crop Top', 'Shirt', 'Sweater',
             'Tank Top', 'T-Shirt', 'Tunic'],
}
CATEGORY_TO_STYLE = {
  'Co-ords' : ['Co-ords'],
  'Coats & Jackets' : ['Coats & Jackets', 'Aviator', 'Biker', 'Bomber Jacket', 'Coach', 'Denim Jacket', 'Duster', 'Faux Fur', 'Harrington', 'Leather', 'Leather Jacket', 'Military', 'Other', 'Overcoat', 'Parkas', 'Pea Coat', 'Puffer', 'Quilted', 'Raincoats', 'Rain Jackets', 'Regular', 'Skater', 'Track', 'Trench', 'Trucker', 'Tuxedo', 'Wax Jacket', 'Windbreaker'],
  'Dresses' : ['Dresses', 'A Line', 'Backless', 'Bandage', 'Bandeau', 'Bardot', 'Bodycon', 'Bohemian', 'Cold Shoulder', 'Denim', 'Jumper', 'Leather', 'Long Sleeve', 'Off Shoulder', 'One Shoulder', 'Other', 'Overall Dress', 'Pencil Dress', 'Shift', 'Shirt', 'Skater', 'Slip', 'Smock Dresses', 'Sweater Dress', 'Swing', 'Tea', 'T-Shirt', 'Wiggle', 'Wrap', 'Cocktail', 'Maxi', 'Mini'],
  'Hoodies & Sweatshirts' : ['Hoodies & Sweatshirts'],
  'Denim' : ['Jeans', 'Bootcut', 'Boyfriend', 'Cropped', 'Flare', 'High Waisted', 'Loose', 'Mom Jeans', 'Other', 'Regular', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg'],
  'Jumpsuits & Rompers' : ['Jumpsuits & Rompers'],
  'Lingerie & Sleepwear' : ['Lingerie & Sleepwear', 'Balconette', 'Halter', 'Multiway', 'Nursing', 'Padded', 'Plunge', 'Push Up', 'Stick On Bra', 'Strapless', 'Triangle', 'T-Shirt', 'Underwired', 'Unpadded'],
  'Loungewear' : ['Loungewear'],
  'Bottoms' : ['Bottoms', 'Cargo Pants', 'Cigarette', 'Cropped', 'Culottes', 'Flare', 'High Waisted', 'Other', 'Oversized', 'Peg Leg', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Straight Leg', 'Super Skinny', 'Tapered', 'Wide Leg', 'Cargo Shorts', 'Chino Shorts', 'Denim', 'High Waisted', 'Jersey Shorts', 'Other', 'Oversized', 'Regular', 'Relaxed', 'Skinny', 'Slim', 'Sports Shorts', 'A Line', 'Bodycon', 'Denim', 'High Waisted', 'Other', 'Pencil Skirt', 'Pleated', 'Skater', 'Slip', 'Tulle', 'Wrap'],
  'Sweaters & Cardigans' : ['Sweaters & Cardigans'],
  'Swimwear & Beachwear' : ['Swimwear & Beachwear', 'Halter', 'High Waisted', 'Multiway', 'Padded', 'Plunge', 'Strapless', 'Triangle', 'Underwired'],
  'Tops' : ['Tops'],
}

WEBSITE_NAME = "storets"

class StoretsSpider(scrapy.Spider):
    name = 'storets'
    allowed_domains = ['www.storets.com']


    def __init__(self, *a, **kw):
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--disable-gpu')
        user_agent = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.116 Safari/537.36'
        options.add_argument(f'user-agent={user_agent}')
        self.driver = webdriver.Chrome(ChromeDriverManager().install(), options=options)
        super().__init__(*a, **kw)


    def start_requests(self):
        url = 'https://www.storets.com/'
        yield scrapy.Request(url=url, callback=self.parse)

    # This function parses category links
    def parse(self, response):
        category_links = response.xpath("//a[@class='site-nav__dropdown-link'] /@href").getall()
        category_links = [("https://www.storets.com" + link) for link in category_links if
                          not re.search("https://www.storets.com", link)]
        for link in category_links:
            if not self.in_disallowed_categories(link):
                yield scrapy.Request(url=link, callback=self.parse_products)

    # This function parses product links for current category
    def parse_products(self, response):
        # Scrolling to bottom of the page
        self.scroll()
        prd_links = response.xpath("//a[@class='grid-product__link '] /@href").getall()
        for prd_link in prd_links:
            yield scrapy.Request(url=response.urljoin(prd_link), callback=self.parse_product_details)


    def parse_product_details(self, response):
        url = response.request.url
        json_meta = json.loads(response.xpath("(//script[@type='application/ld+json'])[3] /text()").get())
        external_id = json_meta["sku"]
        name = response.css("h1.h2.product-single__title::text").get().strip()
        price = response.xpath("//span[@class='product__price'] /span /text()").get()
        if price:
            price = price.strip()
        else:
            price = response.xpath('//span[@class="product__price on-sale"] /span /text()').get()
            if price:
                price = price.strip()

        colors = response.xpath("//fieldset[@name='Color'] //div /@data-value").getall()
        sizes = response.xpath("//fieldset[@name='Size'] //div /@data-value").getall()
        categories = []
        scrapped_categories = response.xpath('//nav[@class="breadcrumb"] /a /text()').getall()
        scrapped_categories = scrapped_categories[1:]
        extracted_categories = extract_categories_from(url)
        if extracted_categories:
            categories = find_actual_parent(scrapped_categories, extracted_categories)
        else:
            extracted_categories = extract_categories_from(name)
            if extracted_categories:
                categories = find_actual_parent(scrapped_categories, extracted_categories)
            else:
                extracted_categories = extract_categories_from(scrapped_categories)
                if extracted_categories:
                    categories = find_actual_parent(scrapped_categories, extracted_categories)

        details = response.xpath("(//div[@class='product-single__description rte'])[1] /ul /li //text()").getall()
        details_meta = details + response.xpath("(//div[@class='product-single__description rte'])[1] /p /text()").getall()
        fabric = self.find_fabric_from_details(details_meta) if details else ""
        fit = self.find_from_target_string_single(details_meta, FIT_KEYWORDS)
        neck_line = self.find_from_target_string_single(details_meta, NECK_LINE_KEYWORDS)
        length = self.find_from_target_string_multiple(details_meta, name, categories, LENGTH_KEYWORDS)
        gender = "women"
        # Extracting Number of reviews
        review_description = []
        number_of_reviews = ""
        top_best_seller = ""
        occasions = self.find_from_target_multiple_list(details, name, categories, OCCASIONS_KEYWORDS)
        style = self.find_from_target_multiple_list(details, name, categories, STYLE_KEYWORDS)
        meta = {}
        # Extracting Images using Selenium
        self.driver.get(response.request.url)
        self.driver.implicitly_wait(10)
        images = self.driver.find_elements(By.XPATH,
                                           '//img[contains(@class, "animation-delay") and contains(@class, "lazyautosizes lazyloaded")]')
        images = ["https:"+(image.get_attribute("srcset").split(",")[-1].strip()) for image in images]

        item = StoretsScrapperItem()
        item["url"] = url
        item["external_id"] = external_id
        item["name"] = name
        item["price"] = price
        item["sizes"] = sizes
        item["categories"] = categories
        item["colors"] = colors
        item["details"] = details
        item["fabric"] = fabric
        item["images"] = images
        item["fit"] = fit
        item["neck_line"] = neck_line
        item["length"] = length
        item["gender"] = gender
        item["number_of_reviews"] = number_of_reviews
        item["review_description"] = review_description
        item["top_best_seller"] = top_best_seller
        item["meta"] = meta
        item["occasions"] = occasions
        item["style"] = style
        item["website_name"] = WEBSITE_NAME
        # item["aesthetics"] = aesthetics
        if details and images and categories:
            yield item

    def in_disallowed_categories(self, link):
        for keyword in DISALLOWED_CATEGORIES:
            if re.search(keyword, link, re.IGNORECASE):
                return True

        return False

        # This function scrolls product detail page to the bottom

    def scroll(self):
        last_height = self.driver.execute_script("return document.body.scrollHeight")
        while True:
            # Scroll down to bottom
            self.driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")

            # Wait to load page
            time.sleep(5)

            # Calculate new scroll height and compare with last scroll height
            new_height = self.driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

    # This helper finds fabric from details and returns it
    def find_fabric_from_details(self, details):
        product_details = ' '.join(details)
        fabrics_founded = re.findall(r"""(\d+ ?%\s?)?(
            velvet\b|silk\b|satin\b|cotton\b|lace\b|
            sheer\b|organza\b|chiffon\b|spandex\b|polyester\b|
            poly\b|linen\b|nylon\b|viscose\b|Georgette\b|Ponte\b|
            smock\b|smocked\b|shirred\b|Rayon\b|Bamboo\b|Knit\b|Crepe\b|
            Leather\b|polyamide\b|Acrylic\b|Elastane\bTencel\bCashmere\b)\)?""", product_details,
                                     flags=re.IGNORECASE | re.MULTILINE)

        return re.sub("\(|\)", "", ' '.join([''.join(tups) for tups in fabrics_founded]))

    def find_from_target_string_single(self, source_data, target_keywords):
        for each_element in source_data:
            for keyword in target_keywords:
                if keyword.lower() in each_element.lower():
                    return keyword
        return ""

    def find_from_target_multiple_list(self, details, name, categories, target_keywords):
        target_list = details[:]
        target_list.extend(name)
        target_list.extend(categories)
        final_list = []

        for each_element in target_list:
            for keyword in target_keywords:
                if keyword.lower() in each_element.lower():
                    final_list.append(keyword)

        return final_list

    def find_from_target_string_multiple(self, details, name, categories, target_keywords):
        target_list = details[:]
        target_list.extend(name)
        target_list.extend(categories)

        for element in target_list:
            for keyword in target_keywords:
                if keyword.lower() in element.lower():
                    return keyword
        return ""


# This function maps category we have extracted from name or url to taxonomy,
# and then it returns the list of extracted keywords.
def map_to_parents(cats):
    # where cats -> categories
    # cat -> category
    finals = []
    for cat in cats:
        for key in CATEGORY_TO_TYPE:
            if re.search(cat, ' '.join(CATEGORY_TO_TYPE[key]), re.IGNORECASE):
                finals.append(key)

    if not finals:
        for cat in cats:
            for key in CATEGORY_TO_STYLE:
                if re.search(cat, ' '.join(CATEGORY_TO_STYLE[key]), re.IGNORECASE):
                    finals.append(key)
    return list(set(finals))


# This function find real parent category from the list of extracted categories we provided
# Arguments: -> here first arg is scrapped categories and second is one which is list of extracted keywords
# we basically loop over scrapped categories and check if any category from scrapped one lies in extracted ones
def find_actual_parent(scrapped_cats, categories):
    finals = []
    final_categories = map_to_parents(categories)
    if len(final_categories) > 1:
        for fc in final_categories:
            if re.search(fc, ' '.join(scrapped_cats), re.IGNORECASE):
                finals.append(fc)

        if finals:
            return finals
        else:
            return []
    else:
        if final_categories:
            return final_categories
        else:
            return []


# This function extracts category keywords from product attribute passed as an argument to it
def extract_categories_from(keyword):
    cats = []  # categories
    if type(keyword) == list:
        keyword = ' '.join(keyword)

    for cat in CATEGORY_KEYWORDS:
        if re.search(cat, keyword, re.IGNORECASE):
            cats.append(cat)

    return cats
