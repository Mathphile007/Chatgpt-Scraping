# chatgpt_scraper.py
import time
from contextlib import suppress
from seleniumbase import SB
import json
import os
import random # Ensure random is imported for the sleep delay

# --- SCRIPT EXECUTION ---

# The SB context manager handles driver initialization, UC mode, and driver cleanup.
# We set headless=True for running in GitHub Actions (no screen).
with SB(uc=True, test=True, ad_block=True, headless=True) as sb:
    
    # 1. Configuration
    url = "https://chatgpt.com/"
    # Use a list of queries so the script can be easily extended
    queries = [
        "Compare Playwright to SeleniumBase in under 178 words",
        "What is the best way to handle SessionNotCreatedException in Selenium?",
        "Write a simple Python function to save data to a JSON file."
    ]
    all_results = []
    
    # 2. Open URL and Activate CDP Mode
    # FIXED: Removed 'timeout=15' to resolve the TypeError.
    sb.uc_open_with_reconnect(url,reconnect_time=15)
    
    sb.activate_cdp_mode(url)
    sb.sleep(1)
    
    # Handle Popups
    sb.click_if_visible('button[aria-label="Close dialog"]')
    sb.click_if_visible('button[data-testid="close-button"]')
    sb.sleep(0.5)

    for query in queries:
        print(f'*** Input for ChatGPT: ***\n"{query}"')
        
        # 3. Input Query and Send
        sb.press_keys("#prompt-textarea", query)
        sb.click('button[data-testid="send-button"]')
        sb.sleep(3)

        # 4. Wait for Response Completion
        with suppress(Exception):
            sb.wait_for_element_not_visible(
                'button[data-testid="stop-button"]', timeout=45
            )

        # 5. Scrape and Clean the Response
        try:
            chat = sb.find_element('[data-message-author-role="assistant"] .markdown')
            # Extract clean text using BeautifulSoup
            response_text = sb.get_beautiful_soup(chat.get_html()).text.strip()
            response_text = response_text.replace("\n\n\n", "\n\n")
            print("*** Response received. ***")
            
            all_results.append({
                "query": query,
                "response": response_text
            })

        except Exception as e:
            print(f"Failed to scrape response for '{query}': {e}")
            all_results.append({"query": query, "response": "Error scraping response."})
            
        # Clear the input area for the next query
        sb.clear("#prompt-textarea")
        sb.sleep(random.uniform(2, 4)) # Small delay before next query
        
    # --- FINAL STEP: SAVE THE OUTPUT ---
    output_filename = "chatgpt_output.json"
    with open(output_filename, 'w', encoding='utf-8') as f:
        json.dump(all_results, f, ensure_ascii=False, indent=4)
        
    print(f"\n✅ All results saved to {output_filename}")
