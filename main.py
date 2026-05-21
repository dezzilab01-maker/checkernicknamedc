#!/usr/bin/env python3
import time
import random
import sys
import json
from datetime import datetime
from colorama import Fore, Style, init

init(autoreset=True)

def banner():
    print(f"""{Fore.CYAN}
    ╔══════════════════════════════════════════════════════════╗
    ║         GUNS.LOL REAL CLICKER v1.0                       ║
    ║         [PRAWIDŁOWE kliknięcia - wymaga przeglądarki]    ║
    ╚══════════════════════════════════════════════════════════╝
    {Style.RESET_ALL}""")

def check_dependencies():
    """Sprawdza czy wymagane pakiety są zainstalowane"""
    try:
        import selenium
        return True
    except ImportError:
        return False

def install_instructions():
    print(f"{Fore.RED}Wymagane pakiety! Uruchom w Termux:{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}")
    print("pkg update && pkg upgrade -y")
    print("pkg install python chromium chromedriver -y")
    print("pip install selenium colorama")
    print("")
    print("LUB jeśli nie działa chromedriver:")
    print("pkg install tur-repo")
    print("pkg install chromium chromedriver")
    print(f"{Style.RESET_ALL}")

def click_with_selenium(nick, proxy=None, headless=False):
    """Prawdziwe kliknięcie używając Selenium"""
    from selenium import webdriver
    from selenium.webdriver.common.action_chains import ActionChains
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    
    options = webdriver.ChromeOptions()
    
    if headless:
        options.add_argument('--headless')
    
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-blink-features=AutomationControlled')
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option('useAutomationExtension', False)
    
    if proxy:
        options.add_argument(f'--proxy-server=http://{proxy}')
    
    driver = None
    try:
        driver = webdriver.Chrome(options=options)
        driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
        
        url = f"https://guns.lol/{nick}"
        driver.get(url)
        
        time.sleep(random.uniform(2, 4))
        
        # Znajdź element do kliknięcia (całe body)
        body = driver.find_element(By.TAG_NAME, "body")
        
        # Symuluj prawdziwe kliknięcie
        action = ActionChains(driver)
        action.move_to_element(body).click().perform()
        
        time.sleep(random.uniform(1, 2))
        
        # Dodatkowe kliknięcia losowych elementów
        elements = driver.find_elements(By.CSS_SELECTOR, "button, a, div[onclick]")
        if elements:
            random.choice(elements).click()
            time.sleep(random.uniform(0.5, 1))
        
        return True, driver.current_url
        
    except Exception as e:
        return False, str(e)
    finally:
        if driver:
            driver.quit()

def click_with_playwright(nick, proxy=None):
    """Prawdziwe kliknięcie używając Playwright"""
    from playwright.sync_api import sync_playwright
    
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(
                headless=False,
                args=['--disable-blink-features=AutomationControlled']
            )
            
            context = browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            )
            
            if proxy:
                context.set_extra_http_headers({'Proxy': proxy})
            
            page = context.new_page()
            
            # Ukryj że to bot
            page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                window.chrome = {runtime: {}};
            """)
            
            page.goto(f"https://guns.lol/{nick}")
            
            time.sleep(random.uniform(2, 4))
            
            # Prawdziwe kliknięcie
            page.click('body', button='left')
            
            # Losowe ruchy myszą
            for _ in range(random.randint(1, 3)):
                page.mouse.move(
                    random.randint(100, 800),
                    random.randint(100, 600)
                )
                time.sleep(random.uniform(0.1, 0.3))
            
            time.sleep(random.uniform(1, 2))
            
            browser.close()
            return True, "Kliknięto!"
            
    except Exception as e:
        return False, str(e)

def main():
    banner()
    
    if not check_dependencies():
        install_instructions()
        sys.exit(1)
    
    print(f"{Fore.GREEN}✓ Wymagane pakiety są zainstalowane{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}\nUWAGA: To NAPRAWDĘ klika w stronę!{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Wymaga to otwarcia przeglądarki.{Style.RESET_ALL}")
    
    nick = input(f"\n{Fore.YELLOW}Podaj nick (np. dezzi7): {Style.RESET_ALL}").strip()
    if not nick:
        nick = "dezzi7"
    
    ile_klik = int(input(f"{Fore.YELLOW}Ile kliknięć wykonać: {Style.RESET_ALL}") or "1")
    
    use_proxy = input(f"{Fore.YELLOW}Czy użyć proxy? (t/n): {Style.RESET_ALL}").lower() == 't'
    proxy = None
    if use_proxy:
        proxy = input(f"{Fore.YELLOW}Podaj proxy (ip:port): {Style.RESET_ALL}")
    
    engine = input(f"{Fore.YELLOW}Wybierz silnik (1 - Selenium, 2 - Playwright): {Style.RESET_ALL}") or "1"
    
    sukcesy = 0
    bledy = 0
    
    print(f"\n{Fore.CYAN}Rozpoczynam {ile_klik} prawdziwych kliknięć...{Style.RESET_ALL}")
    
    for i in range(ile_klik):
        print(f"\n{Fore.CYAN}[{i+1}/{ile_klik}] Klikam...{Style.RESET_ALL}")
        
        if engine == "1":
            sukces, wynik = click_with_selenium(nick, proxy, headless=False)
        else:
            sukces, wynik = click_with_playwright(nick, proxy)
        
        if sukces:
            sukcesy += 1
            print(f"{Fore.GREEN}✓ Kliknięto!{Style.RESET_ALL}")
        else:
            bledy += 1
            print(f"{Fore.RED}✗ Błąd: {wynik}{Style.RESET_ALL}")
        
        if i < ile_klik - 1:
            wait = random.uniform(3, 7)
            print(f"{Fore.YELLOW}Czekam {wait:.1f} sekund...{Style.RESET_ALL}")
            time.sleep(wait)
    
    print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Udanych: {sukcesy}{Style.RESET_ALL}")
    print(f"{Fore.RED}✗ Nieudanych: {bledy}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 Razem: {ile_klik}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Przerwano!{Style.RESET_ALL}")
        sys.exit(0)
    except Exception as e:
        print(f"{Fore.RED}Błąd: {e}{Style.RESET_ALL}")
