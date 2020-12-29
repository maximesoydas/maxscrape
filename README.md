
#  SCRAPE DATA FROM URLS (w/ Python, BeautifulSoup)

In this project we will create a python script that will fecth certain information out of a specfic website.

# Environment Installation

First you will need to install python3 and pip.

Then in your project's folder install the *BeautifulSoup4*, *lxml*, *requests* and *csv* modules with pip as such :
 ```shell
 # use pip commands
 pip install requests
 pip install csv
 pip install os
 pip install zipfile
 pip install shutil
 pip install lxml
 pip install time
 pip install multiprocessing

# or use the requirements file
pip install -r requirements.txt
 ```


# Scraping Objectives

The url for this project is : https://books.toscrape.com/

It hosts an online library, from which we will: 

A. **extract** specific data from *categories* and *books*

B. **inject** the fetched data into different CSV files.

The script should be able to extract :

- Specific data from a book/product_page:
    * product_page_url
    * universal_ product_code (upc)
    * title
    * price_including_tax
    * price_excluding_tax
    * number_available
    * product_description
    * category
    * review_rating
    * image_url
- All the books' urls
- All the categories
- All the books from each category
- All books' images (save in folder).

# Scraping Outputs

The script generates CSV files :

 1. product.csv (contains all the specified data above about one book)
 2. products_urls_category.csv ( contains all the books' url from a specified category)
 3. products_data_category_name.csv (contains all the books' specific data for each specific category, up to 50 files)
    * It generates ONE csv file for EACH category (50 categories total) containing all specific data:

The script generates image files :

1. Download Product Image from each product page
2. Save Product Images in project_folder/'category_name'/'book_name'/'product_img.png'

at last the script returns all generated files and images into a compressed zip file, named 'books_to_scrape_data'
 
