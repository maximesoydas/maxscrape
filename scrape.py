from bs4 import BeautifulSoup
import requests
import csv
import os
import zipfile
import shutil
import cchardet
import lxml
import time
import re
import multiprocessing as mp
# Intro
# Ce Script de Scraping nous permet de récuperer certaines données de Categories et Livres a partir d'une URL correspondant a une librairie en ligne 
# En utilisant les modules Requests et BeautyfulSoup(bs4) on va recuperer le contenu html d'une url(page) et ecrire les données dans un fichier csv
# Une fois les données récuperer on les ecrit dans un fichier CSV correspondant au nom de la categorie du livre

# Cette fonction nous permet de recuperer les données d'un livre a partir d'une URL de page produit donner.
# Elle nous permet aussi d'ecrire les données recuperer dans le fichier CSV correspondant a la category du produit recuperer.
def gen_product_data(product_url):
    # Extraction from given Product Page URL

    source = requests.get(product_url)
    if source.ok:
        soup = BeautifulSoup(source.text, "lxml")

        # Fecthes the Category from the aside linkbar
        linkbar = soup.find("ul", {"class": "breadcrumb"})
        linkbar = linkbar.findAll("li")
        category = linkbar[2].text.strip().title()
        print('CAT' + category)
        # Writes(append) to the csv file corresponding to the product's category
        with open(f"Categories/{category}/{category}.csv", "a", encoding="utf-16") as csvfile:
            fieldnames = [
                "CATEGORY",
                "PRODUCT URL",
                "TITLE",
                "UPC",
                "PRICE W/ TAX",
                "PRICE W/O TAX",
                "QUANTITY",
                "PRODUCT DESCRIPTION",
                "REVIEW RATING",
                "IMAGE_URL",
            ]   
            # on precise le a fichier dans lequel ecrite et les noms de champs des colonnes a respecter
            writer = csv.DictWriter(csvfile, fieldnames)

            # Fetches the Product Title
            title = soup.find("div", {"class": "col-sm-6 product_main"})
            h1 = title.find("h1")
            titles = []
            for title in h1:
                titles.append(title)
            print(str(titles))

            # Fetches all possible Product Ratings
            rating = soup.find("div", {"class": "col-sm-6 product_main"})
            rating_one = rating.find("p", {"class": "star-rating One"})
            rating_two = rating.find("p", {"class": "star-rating Two"})
            rating_three = rating.find("p", {"class": "star-rating Three"})
            rating_four = rating.find("p", {"class": "star-rating Four"})
            rating_five = rating.find("p", {"class": "star-rating Five"})

            # Fetches the Product Description
            article = soup.find("article", {"class": "product_page"})
            description = article.findAll("p")
            resume = (
                description[3]
                .text.replace("Ã´", "ô")
                .replace("â", "'")
                .replace("Ã¨", "è")
                .replace("Ã©", "é")
                .replace("Ã", "à")
                .replace("â", "'")
            )
            print(resume)

            # Checks and fecthes the correct rating and writes into the CSV file
            if rating_one:
                rating = "Product Rating : 1/5"
            elif rating_two:
                rating = "Product Rating : 2/5"
            elif rating_three:
                rating = "Product Rating : 3/5"
            elif rating_four:
                rating = "Product Rating : 4/5"
            elif rating_five:
                rating = "Product Rating : 5/5"
            else:
                rating = "No Product Rating Found"
            print(rating)

            # Fetches the Product Info Table (UPC, PRICES, TAX, AVAILABILITY)
            table = soup.find("table", {"class": "table table-striped"})
            table_data = []
            for info in table.findAll("tr"):
                td = info.find("td")
                table_data.append(td)
            upc = table_data[0].text
            taxless_price = table_data[2].text.replace("Ã", "").replace("Â", "")
            taxed_price = table_data[3].text.replace("Ã", "").replace("Â", "")
            quantity = table_data[5].text.replace("available ", "")
            print(upc)
            print(taxless_price)
            print(taxed_price)
            print(quantity)

            # Fetches the product_image_url
            image_url = soup.find("div", {"class": "item active"})
            image_url = image_url.find("img")
            image_url = str(image_url["src"]).replace(
                "../../", "https://books.toscrape.com/"
            )
            print(image_url)
            img = requests.get(image_url)

            writer.writerow(
                {
                    "CATEGORY": category,
                    "PRODUCT URL": product_url,
                    "TITLE": title,
                    "UPC": upc,
                    "PRICE W/ TAX": taxed_price,
                    "PRICE W/O TAX": taxless_price,
                    "QUANTITY": quantity,
                    "PRODUCT DESCRIPTION": resume,
                    "REVIEW RATING": rating,
                    "IMAGE_URL": image_url,
                }
            )
            # (img, title, category) = gen_product_data(url, w)
            dir = f"Categories/{category}/Images"
            if not os.path.exists(dir):
                os.mkdir(f"Categories/{category}/Images")
            title = re.sub(r"[- ()\"#/@;:<>{}`+=~|.!?,*]", "", title)
            
        with open(f"Categories/{category}/Images/{title}.jpg", "wb") as f:
            f.write(img.content)




def gen_categories():

    # FETCHES THE CATEGORIES' URLS AND WRITES THEM INTO A LIST

    url = "http://books.toscrape.com/"
    source = requests.get(url)
    if source.ok:
        soup = BeautifulSoup(source.text, "lxml")
        # Creation of the categories' urls list
        ctg_urls = []
        # Fetches the nav list (hosting the categories' links)
        categories = soup.find("ul", {"class": "nav nav-list"})
        categories = categories.find("li")
       
        # Fetches the href tags
        for category in categories.find_all("a"):
            # Appends the urls into a list
            ctg_urls.append(url + category.get("href"))
        ctg_urls.remove(ctg_urls[0])
 
        # FETCHES THE CATEGORIES' NAMES
        category_names = []
        category_tags = soup.findAll("ul", {"class": "nav nav-list"})
        for name in category_tags:
            name = name.find("li")
            name = name.findAll("a", href=True)
            for a in name:
                if a.text:
                    a = a["href"] 
                    a = (
                    a.replace("catalogue/category/books/", "")
                    .replace("/index.html", "")
                    .replace("catalogue/category/", "")
                     )
                    category_names.append(a)
        category_names.remove(category_names[0])
        print(category_names)

        # RETURNS ALL THE PAGES FROM EACH CATEGORY
        ctg_pages = []
        for url in ctg_urls:
            source = requests.get(url)
            soup = BeautifulSoup(source.text, "lxml")
            # If Pager is true creates new urls
            pager = soup.find("li", {"class": "next"})
            # Appends all of the category pages from each category (pagination)
            ctg_pages.append(url)

            if pager:
                # Next page url retrieved
                next_page = pager.find("a")["href"]
                link = url.replace("index.html", "") + next_page
                source = requests.get(link)
                soup = BeautifulSoup(source.text, "lxml")
                # Pager is the footer containing the next and previous button,
                # Proof that more than one page exists for this category
                if soup.find("ul", {"class": "pager"}):
                    # Finds the max number of pages in that category
                    page_number = soup.find("li", {"class": "current"})
                    page_number = page_number.text
                    page_number = page_number.replace("Page 2 of", "").strip()
                    max_pages = int(page_number) + 1
                    # Loops over max number of pages of the fetched category url
                    for i in range(2, max_pages):
                        next_link = link.replace("2", str(i))
                        source = requests.get(next_link)
                        soup = BeautifulSoup(source.text, "lxml")
                        if soup.find("ul", {"class": "pager"}):
                            print(next_link)
                            ctg_pages.append(next_link)
            else:
                print(url)
    print("All Categories URLS and NAMES Fetched ")
    print(ctg_pages)
    return (ctg_pages, category_names)

def gen_products():
    start = time.time()
    dir = f"Categories"
    if not os.path.exists(dir):
        os.mkdir(f"Categories")
    (ctg_pages, ctg_names) = gen_categories()
    # FECTHES EACH URL FROM EACH CATEGORY_PAGES
    
    for url in ctg_pages:
        # print(url)
        ctg_name = []
        for name in ctg_names:
            if name in url:
                ctg_name.append(name)
            else:
                pass
        # print(ctg_name)
        # FECTHES THE CATEGORY NAMES
        i = (
            url.replace("http://books.toscrape.com/catalogue/category/", "")
            .replace("/index.html", "")
            .replace("books/", "")
            .replace("/page-", "")
            .replace(".html", "")
            .replace(f"{ctg_name[0]}", "")
        )
        # print(i)
        category_title = (
            url.replace("http://books.toscrape.com/catalogue/category/", "")
            .replace("/index.html", "")
            .replace("books/", "")
            .replace(f"/page-{i}.html", "")
        )
        category_title = category_title[:-2].replace("_", "").capitalize().replace('-', ' ').title()
        print(f"CATEGORY NAME : {category_title}\n PAGE_NUMBER : {i}")
        # CREATE CATEGORY FOLDER
        dir = f"Categories/{category_title}"
        if not os.path.exists(dir):
            os.mkdir(f"Categories/{category_title}")
        # if non existent create category.csv file:
        filename = f"Categories/{category_title}/{category_title}.csv"

        if not os.path.exists(filename):
            with open(
                f"Categories/{category_title}/{category_title}.csv",
                "w",
                encoding="utf-16",
            ) as csvfile:
                fieldnames = [
                    "CATEGORY",
                    "PRODUCT URL",
                    "TITLE",
                    "UPC",
                    "PRICE W/ TAX",
                    "PRICE W/O TAX",
                    "QUANTITY",
                    "PRODUCT DESCRIPTION",
                    "REVIEW RATING",
                    "IMAGE_URL",
                ]
                writer = csv.DictWriter(csvfile, fieldnames)
                writer.writeheader()

        # Fetches each product url from each category page and 
        # appends product data from each product url into csvfile named after its category

        source = requests.get(url)
        soup = BeautifulSoup(source.text, "lxml")
        links = soup.findAll("div", {"class": "image_container"})
        base_url = "https://books.toscrape.com/catalogue/"
        product_urls = []
        for link in links:
            a = link.find("a")
            link = (
                a["href"]
                .replace("../../../", "")
                .replace("'", "")
                .replace(",", "\n\n")
                .replace("../../", "")
            )
            product_urls.append(base_url + link)
        pool = mp.Pool()
        pool.map(gen_product_data, [url for url in product_urls])
        pool.close()

    folder_to_zip = "Categories"
    with zipfile.ZipFile("Categories.zip", "w", zipfile.ZIP_DEFLATED) as newzip:
        for dirpath, dirnames, files in os.walk(folder_to_zip):
            for file in files:
                newzip.write(os.path.join(dirpath, file))
    shutil.rmtree("Categories")
    end = time.time()
    timing = end - start
    timing = timing / 60
    return print(f"Scraping done in {timing} minutes")


if __name__ == "__main__":
    print('Starting scrapping ...')
    gen_products()

