from playwright.sync_api import sync_playwright
import time
import os

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        page.goto('http://localhost:8501')
        
        # Wait for Streamlit to finish loading
        page.wait_for_selector('.stTabs', timeout=60000)
        time.sleep(3)
        
        for i in range(1, 13):
            tab_name = f'Q{i}'
            print(f'Clicking tab {tab_name}...')
            page.click(f'text={tab_name}')
            time.sleep(1.5) # Wait for chart to render
            page.screenshot(path=f'q{i}_screen.png', full_page=True)
            print(f'Saved q{i}_screen.png')
            
        browser.close()

run()
