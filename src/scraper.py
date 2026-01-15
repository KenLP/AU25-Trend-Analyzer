import asyncio
from playwright.async_api import async_playwright
from bs4 import BeautifulSoup
import pandas as pd
import json
import os
from .utils import setup_logger, save_json

logger = setup_logger('scraper')

async def get_class_list(page):
    """Scrapes the search results page regarding 2025 classes."""
    # Updated URL for Software Development topic
    url = "https://www.autodesk.com/autodesk-university/search?fields.year=2025&fields.topic=Software+Development&fields.recordtype=class"
    logger.info(f"Navigating to {url}")
    await page.goto(url, timeout=60000)
    
    # Handle cookie banner if present (best effort)
    try:
        await page.click('#onetrust-accept-btn-handler', timeout=3000)
    except:
        pass

    logger.info(f"Page Title: {await page.title()}")

    all_links = {} # {url: title}
    page_num = 1
    
    while True:
        logger.info(f"Processing Page {page_num}...")
        
        # Validation Loop: Ensure we get enough classes per page
        retry_count = 0
        max_retries = 3
        found_links_on_page = []
        next_btn_visible = False
        
        while retry_count < max_retries:
            # Wait for content
            try:
                await page.wait_for_selector('a[href*="/autodesk-university/class/"]', state='visible', timeout=20000)
            except:
                logger.warning("Timeout waiting for links.")
            
            # Scroll slowly
            for _ in range(5):
                await page.mouse.wheel(0, 3000)
                await asyncio.sleep(1)
            
            content = await page.content()
            soup = BeautifulSoup(content, 'html.parser')
            
            found_links_on_page = soup.select('a[href*="/autodesk-university/class/"]')
            count = len(found_links_on_page)
            
            # Check for next button to determine if we expect a full page
            try:
                next_btn_loc = page.locator('button[aria-label="Go to next page"]')
                if await next_btn_loc.count() > 0:
                     next_btn_visible = await next_btn_loc.is_visible() and not await next_btn_loc.is_disabled()
            except:
                next_btn_visible = False
            
            logger.info(f"Detected {count} classes on page {page_num} (Attempt {retry_count+1}). Next Page Available: {next_btn_visible}")
            
            # Heuristic: If there is a next page, this page should be roughly full (>=15 items)
            if next_btn_visible and count < 15:
                # Except if it's the very first page loading weirdly? No, page 1 should be full.
                logger.warning(f"Found only {count} classes but Next button exists. Expected ~18+. Retrying...")
                retry_count += 1
                await asyncio.sleep(5)
                if retry_count == 2:
                    logger.info("Reloading page to force refresh...")
                    await page.reload()
                    await asyncio.sleep(10)
            else:
                break # Count is good or it's the last page

        # Add Links (With Titles for deduplication)
        new_links = 0
        current_page_first_item = None
        
        if found_links_on_page:
            current_page_first_item = found_links_on_page[0].get('href')

        for a in found_links_on_page:
            href = a['href']
            url_full = href if href.startswith('http') else f"https://www.autodesk.com{href}"
            title = a.get_text(strip=True)
            
            if url_full not in all_links:
                all_links[url_full] = title
                new_links += 1
        
        logger.info(f"Found {new_links} new unique classes on this page. Total unique so far: {len(all_links)}")

        # Pagination logic
        if next_btn_visible:
            logger.info("Clicking next page...")
            try:
                await page.locator('button[aria-label="Go to next page"]').click()
                
                # Check for content change
                changed = False
                for _ in range(20):
                    await asyncio.sleep(1)
                    content_check = await page.content()
                    soup_check = BeautifulSoup(content_check, 'html.parser')
                    new_first = soup_check.select_one('a[href*="/autodesk-university/class/"]')
                    if new_first and new_first.get('href') != current_page_first_item:
                        changed = True
                        break
                if not changed:
                    logger.warning("Page content did not appear to change. Might be stuck.")
                    
                page_num += 1
            except Exception as e:
                logger.error(f"Error clicking next: {e}")
                break
        else:
            logger.info("Reached last page.")
            break

    logger.info(f"Found total {len(all_links)} unique classes.")
    return [{'url': u, 'title': t} for u, t in all_links.items()]

async def get_class_details(context, class_item):
    """Visits a class page and extracts detailed info."""
    page = await context.new_page()
    url = class_item['url']
    data = class_item.copy()
    
    try:
        await page.goto(url, timeout=30000)
        
        content = await page.content()
        soup = BeautifulSoup(content, 'html.parser')
        
        # 1. Title (H1)
        h1 = soup.find('h1')
        if h1:
            data['title'] = h1.get_text(strip=True)
            
        # 2. Description
        meta_desc = soup.find('meta', attrs={'name': 'description'})
        if meta_desc:
            data['summary'] = meta_desc['content']
        else:
            data['summary'] = ""

        # 3. Key Learnings
        key_learnings = []
        for header in soup.find_all(['h2', 'h3', 'h4', 'div']):
            if 'key learning' in header.get_text(strip=True).lower():
                sibling = header.find_next('ul')
                if sibling:
                    for li in sibling.find_all('li'):
                        key_learnings.append(li.get_text(strip=True))
                break
        data['key_learnings'] = key_learnings

        # 4. Speakers - REMOVED as requested
        data['speakers'] = [] 

        # 5. Tags (Product, Industry, Topic)
        tags = {'topics': [], 'industries': [], 'products': []}
        tags_header = soup.find(lambda tag: tag.name in ['h2', 'h3'] and 'Tags' in tag.get_text())
        if tags_header:
            rows = soup.find_all('tr')
            for row in rows:
                cells = row.find_all('td')
                if len(cells) >= 2:
                    label = cells[0].get_text(strip=True)
                    chip_elements = cells[1].select('span[class*="MuiChip-label"]')
                    if chip_elements:
                        values = [c.get_text(strip=True) for c in chip_elements]
                    else:
                        links = cells[1].find_all('a')
                        if links:
                            values = [l.get_text(strip=True) for l in links]
                        else:
                            text = cells[1].get_text(strip=True)
                            if text: values = [text]

                    if 'Topics' in label:
                        tags['topics'].extend(values)
                    elif 'Industries' in label:
                        tags['industries'].extend(values)
                    elif 'Product' in label:
                        tags['products'].extend(values)
                            
        data['tags'] = tags
        
    except Exception as e:
        logger.error(f"Error scraping {url}: {e}")
        data['error'] = str(e)
        
    finally:
        await page.close()
        
    return data

async def scrape_all(limit=None):
    # 1. Load existing data for deduplication
    existing_data = []
    output_file = "data/au_2025.json"
    if os.path.exists(output_file):
        try:
            with open(output_file, 'r', encoding='utf-8') as f:
                existing_data = json.load(f)
            logger.info(f"Loaded {len(existing_data)} existing records for incremental update.")
        except Exception as e:
            logger.error(f"Could not load existing data: {e}")

    existing_titles = set(item.get('title', '').strip().lower() for item in existing_data)
    existing_urls = set(item.get('url', '') for item in existing_data)

    async with async_playwright() as p:
        browser = await p.chromium.launch(
            headless=False,
            args=['--disable-blink-features=AutomationControlled', '--no-sandbox', '--disable-setuid-sandbox']
        )
        context = await browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.0.0 Safari/537.36",
            viewport={'width': 1920, 'height': 1080},
            locale='en-US'
        )
        await context.add_init_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        page = await context.new_page()
        
        logger.info("Starting scrape...")
        class_candidates = await get_class_list(page)
        
        # 2. Filter Candidates (Deduplication)
        classes_to_scrape = []
        for c in class_candidates:
            url = c['url']
            title = c['title']
            title_lower = title.strip().lower()
            
            # Rule 1: Skip if URL exists
            if url in existing_urls:
                continue
                
            # Rule 2: Skip if Title exists (exact match)
            if title_lower in existing_titles:
                continue
                
            # Rule 3: Skip if "repeat" in title
            if "repeat" in title_lower:
                continue
            
            classes_to_scrape.append(c)
            # Add to ephemeral set to catch duplicates within the new batch too
            existing_urls.add(url)
            existing_titles.add(title_lower)

        logger.info(f"After deduplication: {len(classes_to_scrape)} new classes to scrape (from {len(class_candidates)} found).")
        
        if not classes_to_scrape:
            logger.info("No new classes to scrape.")
            await browser.close()
            return
            
        results = []
        batch_size = 5
        for i in range(0, len(classes_to_scrape), batch_size):
            batch = classes_to_scrape[i:i+batch_size]
            tasks = [get_class_details(context, item) for item in batch]
            batch_results = await asyncio.gather(*tasks)
            results.extend(batch_results)
            logger.info(f"Progress: {min(i+batch_size, len(classes_to_scrape))}/{len(classes_to_scrape)}")
            
        await browser.close()
        
        # 3. Append and Save
        final_dataset = existing_data + results
        os.makedirs("data", exist_ok=True)
        save_json(final_dataset, output_file)
        logger.info(f"Saved {len(final_dataset)} total records ({len(results)} new) to {output_file}")
        return results

if __name__ == "__main__":
    asyncio.run(scrape_all())
