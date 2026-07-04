from playwright.sync_api import sync_playwright
import time

def run():
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page(viewport={'width': 1920, 'height': 1080})
        print('Navigating to Streamlit...')
        page.goto('http://localhost:8501')
        
        # Wait for Streamlit to finish loading
        page.wait_for_selector('.stTabs', timeout=60000)
        time.sleep(3) # Give it a bit more time to render charts
        
        # Screenshot Q1
        page.screenshot(path='q1_screenshot.png', full_page=True)
        print('Saved q1_screenshot.png')
        
        # Click on Q11 tab
        page.click('text=Q11')
        time.sleep(3) # Wait for Q11 to render
        page.screenshot(path='q11_screenshot.png', full_page=True)
        print('Saved q11_screenshot.png')
        
        browser.close()

run()
