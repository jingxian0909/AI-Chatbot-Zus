import requests
import json
from tqdm import tqdm

import requests
from bs4 import BeautifulSoup
import re
import time

def filter_by_tags(product, allowed_tags):
    """
    Check if product has any of the allowed tags.
    Tags can be a list or a comma-separated string.
    """
    product_tags = product.get('tags', [])
    
    # Handle both list and string formats
    if isinstance(product_tags, str):
        product_tags = [tag.strip() for tag in product_tags.split(',')]
    
    # Convert to lowercase for case-insensitive matching
    product_tags_lower = [tag.lower() for tag in product_tags]
    allowed_tags_lower = [tag.lower() for tag in allowed_tags]
    
    # Check if any allowed tag is in product tags
    return any(tag in product_tags_lower for tag in allowed_tags_lower)

def extract_product_info(product):
    """
    Extract only the essential product information:
    - Product name
    - Variants with color and price
    """
    extracted = {
        "product_name": product.get('title', 'Unknown'),
        "product_id": product.get('id'),
        "variants": [],
        "source_url": f"https://shop.zuscoffee.com/products/{product.get('handle')}"
    }
    
    # Extract variant information
    for variant in product.get('variants', []):
        variant_info = {
            "color": variant.get('option1') or variant.get('title', 'Unknown'),
            "price": variant.get('price', '0.00'),
            "available": variant.get('available', False)
        }
        extracted['variants'].append(variant_info)
    
    return extracted

def scrape_products(filter_tags=None):
    # List of URLs to scrape
    urls = [
        "https://shop.zuscoffee.com/collections/shop-all-lifestyle/products.json",
        "https://shop.zuscoffee.com/products/all-day-cup-500ml-17oz-sundaze-collection/product.json",
        "https://shop.zuscoffee.com/products/all-day-cup-500ml-17oz/product.json",
        "https://shop.zuscoffee.com/products/zus-og-cup-2-0-with-screw-on-lid/product.json",
        "https://shop.zuscoffee.com/products/frozee-cold-cup-650ml-22oz/product.json"
    ]
    
    # Store all product data
    products_list = []
    filtered_count = 0
    
    # Default filter tags if none provided
    if filter_tags is None:
        filter_tags = ['Tumbler', 'BYSS']
    
    print(f"Scraping products with filter tags: {filter_tags}")
    print()
    
    for url in tqdm(urls, desc="Processing URLs"):
        try:
            response = requests.get(url)
            response.raise_for_status()  # Raise an error for bad status codes
            
            # Parse JSON directly
            data = response.json()
            
            # Extract the 'product' or 'products' key
            if 'product' in data:
                product = data['product']
                
                # Apply filter
                if filter_by_tags(product, filter_tags):
                    # Extract only the essential info
                    product_info = extract_product_info(product)
                    products_list.append(product_info)
                    print(f"✓ Added: {product.get('title', 'Unknown')} ({len(product.get('variants', []))} variants)")
                else:
                    filtered_count += 1
                    print(f"⊘ Filtered out: {product.get('title', 'Unknown')} (tags: {product.get('tags', [])})")
                    
            elif 'products' in data:
                # If it's a collection endpoint with multiple products
                for product in data['products']:
                    if filter_by_tags(product, filter_tags):
                        product_info = extract_product_info(product)
                        products_list.append(product_info)
                        print(f"✓ Added: {product.get('title', 'Unknown')} ({len(product.get('variants', []))} variants)")
                    else:
                        filtered_count += 1
            
        except requests.exceptions.RequestException as e:
            print(f"✗ Error scraping {url}: {e}")
        except json.JSONDecodeError as e:
            print(f"✗ Error parsing JSON from {url}: {e}")
    
    # Combine all products under a single root "products" key
    output_data = {
        "products": products_list
    }
    
    # Save all data to a single JSON file
    with open("zus_products.json", "w", encoding="utf-8") as f:
        json.dump(output_data, f, indent=2, ensure_ascii=False)
    
    print(f"\n{'='*50}")
    print(f"✓ Saved {len(products_list)} products to zus_products.json")
    print(f"⊘ Filtered out {filtered_count} products")
    print(f"{'='*50}")
    
    # Also save a pretty-printed text version for easy reading
    with open("zus_products_readable.txt", "w", encoding="utf-8") as f:
        f.write(json.dumps(output_data, indent=2, ensure_ascii=False))
    
    print("✓ Saved readable version to zus_products_readable.txt")
    
    return output_data

def get_page(url):
    """Fetch HTML content with headers"""
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    return res.text

def parse_store_cards(html):
    soup = BeautifulSoup(html, "html.parser")
    articles = soup.select("article.elementor-post")
    outlets = []

    for art in articles:
        name_tag = art.select_one("p.elementor-heading-title")
        if not name_tag:
            name_tag = art.select_one("span.entry-title")
        name = name_tag.get_text(strip=True) if name_tag else None

        address_tag = name_tag.find_next("p") if name_tag else None
        address = address_tag.get_text(strip=True) if address_tag else None

        map_tag = art.select_one("a[href*='maps'], a[href*='goo.gl'], a[href*='g.page'], a[href*='google.com']")
        map_link = map_tag["href"] if map_tag else None

        if name and address and map_link:
            outlets.append({
                "name": name,
                "address": address,
                "google_map": map_link
            })

    return outlets

def get_all_pages():
    all_stores = []
    page_num = 1
    next_url = "https://zuscoffee.com/category/store/kuala-lumpur-selangor/"

    while True:
        print(f"Scraping page {page_num}: {next_url}")

        html = get_page(next_url)
        stores = parse_store_cards(html)
        all_stores.extend(stores)

        soup = BeautifulSoup(html, "html.parser")
        next_btn = soup.select_one("a.next.page-numbers")

        if not next_btn:
            break  # No more pages

        next_url = next_btn["href"]
        page_num += 1
        time.sleep(1)

    return all_stores

if __name__ == "__main__":
    scraped_data = scrape_products(filter_tags=['Tumbler', 'BYSS'])
    print(f"\n📊 Total products scraped: {len(scraped_data['products'])}")
    data = get_all_pages()
    print(f"\nTotal outlets found: {len(data)}\n")
    # Save to JSON
    with open("zus_kl_selangor_outlets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)
    print("Saved to zus_kl_selangor_outlets.json")
