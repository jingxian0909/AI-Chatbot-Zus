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

def scrape_outlets():
    url = "https://zuscoffee.com/category/store/kuala-lumpur-selangor/"
    headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
    response = requests.get(url, headers=headers)
    response.raise_for_status() 
    soup = BeautifulSoup(response.text, 'html.parser')
    articles = soup.select("article.elementor-post")
    #print(articles)
    with open("zus_outlets_raw.html", "w", encoding="utf-8") as f:
        for a in articles:
            f.write(str(a))
            f.write("\n\n")


def scrape_zus_outlets():
    """
    Scrape Zus Coffee outlets in KL/Selangor
    """
    url = "https://zuscoffee.com/category/store/kuala-lumpur-selangor/"
    
    print("Fetching Zus Coffee outlets page...")
    
    # Headers to mimic a browser request
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Save raw HTML for inspection
        with open("zus_outlets_raw.html", "w", encoding="utf-8") as f:
            f.write(soup.prettify())
        print("✓ Saved raw HTML to zus_outlets_raw.html")
        
        outlets = []
        
        # Try to find outlet cards/sections
        # Common patterns: article, div with class containing 'store', 'outlet', 'location'
        
        # Method 1: Look for article tags (common for blog/store listings)
        store_items = soup.find_all('article')
        
        if not store_items:
            # Method 2: Look for divs with store-related classes
            store_items = soup.find_all('div', class_=re.compile(r'store|outlet|location', re.I))
        
        if not store_items:
            # Method 3: Look for list items
            store_items = soup.find_all('li', class_=re.compile(r'store|outlet|location', re.I))
        
        print(f"Found {len(store_items)} potential outlet elements")
        
        for idx, item in enumerate(store_items, 1):
            outlet = {}
            
            # Try to extract store name
            name_elem = (item.find('h2') or item.find('h3') or 
                        item.find('h4') or item.find('h1') or
                        item.find(class_=re.compile(r'title|name', re.I)))
            
            if name_elem:
                outlet['name'] = name_elem.get_text(strip=True)
            
            # Try to extract address
            address_elem = (item.find(class_=re.compile(r'address|location', re.I)) or
                           item.find('address'))
            
            if address_elem:
                outlet['address'] = address_elem.get_text(strip=True)
            else:
                # Try to find any text that looks like an address
                text = item.get_text()
                # Look for text with postal codes or area names
                if re.search(r'\d{5}', text):  # Malaysian postal code pattern
                    outlet['address'] = text.strip()
            
            # Try to extract phone number
            phone_elem = item.find(class_=re.compile(r'phone|tel|contact', re.I))
            if phone_elem:
                outlet['phone'] = phone_elem.get_text(strip=True)
            else:
                # Look for phone patterns in text
                text = item.get_text()
                phone_match = re.search(r'(\+?6?0?1[0-9]-?[0-9]{7,8})', text)
                if phone_match:
                    outlet['phone'] = phone_match.group(1)
            
            # Try to extract operating hours
            hours_elem = item.find(class_=re.compile(r'hours|time|operating', re.I))
            if hours_elem:
                outlet['operating_hours'] = hours_elem.get_text(strip=True)
            
            # Try to extract link
            link_elem = item.find('a', href=True)
            if link_elem:
                outlet['url'] = link_elem['href']
                if not outlet['url'].startswith('http'):
                    outlet['url'] = 'https://zuscoffee.com' + outlet['url']
            
            # Only add if we found at least a name or address
            if outlet.get('name') or outlet.get('address'):
                outlet['id'] = idx
                outlets.append(outlet)
                print(f"\n✓ Outlet {idx}:")
                for key, value in outlet.items():
                    print(f"  {key}: {value}")
        
        # Save to JSON
        output = {
            "region": "Kuala Lumpur/Selangor",
            "total_outlets": len(outlets),
            "outlets": outlets
        }
        
        with open("zus_outlets_kl_selangor.json", "w", encoding="utf-8") as f:
            json.dump(output, f, indent=2, ensure_ascii=False)
        
        print(f"\n{'='*50}")
        print(f"✓ Scraped {len(outlets)} outlets")
        print(f"✓ Saved to zus_outlets_kl_selangor.json")
        print(f"{'='*50}")
        
        # If no outlets found, provide helpful info
        if len(outlets) == 0:
            print("\n⚠ No outlets found. The page might be:")
            print("  1. Dynamically loaded with JavaScript (need Selenium)")
            print("  2. Protected by anti-scraping measures")
            print("  3. Using a different HTML structure")
            print("\nCheck 'zus_outlets_raw.html' to see the page structure")
        
        return output
        
    except requests.exceptions.RequestException as e:
        print(f"✗ Error fetching page: {e}")
        return None
    
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
    #scraped_data = scrape_products(filter_tags=['Tumbler', 'BYSS'])
    #print(f"\n📊 Total products scraped: {len(scraped_data['products'])}")
    data = get_all_pages()
    print(f"\nTotal outlets found: {len(data)}\n")

    # Save to JSON
    with open("zus_kl_selangor_outlets.json", "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

    print("Saved to zus_kl_selangor_outlets.json")
    #scrape_outlets()