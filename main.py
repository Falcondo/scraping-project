import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import tkinter as tk
from tkinter import messagebox

# آدرس دسته‌بندی‌ها
category_urls = [
'https://www.tme.eu/en/katalog/memory-modules_118182/?page=1'
]

# لیست برای ذخیره اطلاعات محصولات
products_data = []

# تابعی برای دریافت اطلاعات محصول از صفحه جزئیات
def scrape_product_details(product_url):
    try:
        response = requests.get(product_url)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # توضیح کامل‌تر
        full_description = soup.find('div', class_='product attribute description').text.strip() if soup.find('div', class_='product attribute description') else 'N/A'
        
        # تصویر با کیفیت بالاتر
        high_res_image = soup.find('img', class_='fotorama__img')['src'] if soup.find('img', class_='fotorama__img') else 'N/A'
        
        return full_description, high_res_image
    except Exception as e:
        print(f"Error fetching product details: {e}")
        return 'N/A', 'N/A'

# تابع برای استخراج اطلاعات از هر صفحه دسته‌بندی
def scrape_category(url):
    while url:
        response = requests.get(url)
        soup = BeautifulSoup(response.text, 'html.parser')

        # پیدا کردن محصولات در صفحه
        products = soup.find_all('div', class_='product-item-info')

        for product in products:
            title = product.find('a', class_='product-item-link').text.strip() if product.find('a', class_='product-item-link') else 'N/A'
            
            # یافتن قیمت در چندین ساختار
            price_tag = product.find('span', class_='price') or product.find('span', class_='special-price')
            price = price_tag.text.strip() if price_tag else 'N/A'

            link = product.find('a', class_='product-item-link')['href'] if product.find('a', class_='product-item-link') else 'N/A'
            description = product.find('div', class_='product-item-description').text.strip() if product.find('div', class_='product-item-description') else 'N/A'
            image = product.find('img', class_='product-image-photo')['src'] if product.find('img', class_='product-image-photo') else 'N/A'
            
            # جمع‌آوری اطلاعات بیشتر از صفحه جزئیات محصول
            full_description, high_res_image = scrape_product_details(link)

            # افزودن به لیست
            products_data.append({
                'Title': title,
                'Price': price,
                'Link': link,
                'Short Description': description,
                'Image': image,
                'Full Description': full_description,
                'High-Res Image': high_res_image
            })

        # پیدا کردن لینک صفحه بعدی
        next_page = soup.find('a', class_='action next')
        url = next_page['href'] if next_page else None
        
        # تاخیر بین درخواست‌ها
        time.sleep(1)

# تابع اصلی برای شروع عملیات اسکرپینگ و ذخیره در فایل اکسل
def start_scraping():
    global products_data
    products_data = []  # پاک کردن داده‌ها در صورت اجرای چندباره
    for url in category_urls:
        scrape_category(url)
    
    # ذخیره اطلاعات در فایل اکسل
    df = pd.DataFrame(products_data)
    df.to_excel('products_detailed_full.xlsx', index=False)
    
    # نمایش پیغام موفقیت
    messagebox.showinfo("اطلاعات ذخیره شد", "اطلاعات در فایل products_detailed_full.xlsx ذخیره شد.")

# ایجاد رابط کاربری با Tkinter
app = tk.Tk()
app.title("Web Scraper")
app.geometry("300x150")

label = tk.Label(app, text="برای شروع استخراج اطلاعات دکمه زیر را فشار دهید.")
label.pack(pady=10)

scrape_button = tk.Button(app, text="شروع استخراج", command=start_scraping)
scrape_button.pack(pady=20)

app.mainloop()


