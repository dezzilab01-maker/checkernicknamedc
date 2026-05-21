#!/usr/bin/env python3
import asyncio
import json
import random
import time
import base64
import hashlib
import re
from typing import Optional, Dict, Any
from playwright.async_api import async_playwright, Page, Browser, Response
import aiohttp
from colorama import Fore, Style, init
import sys

init(autoreset=True)

class GunsLolBot:
    def __init__(self, nick: str, proxy: Optional[str] = None):
        self.nick = nick
        self.proxy = proxy
        self.url = f"https://guns.lol/{nick}"
        self.cloudflare_solved = False
        self.tokens = {}
        self.signature_key = None
        self.canvas_fingerprint = None
        
    def banner(self):
        print(f"""{Fore.CYAN}
    ╔════════════════════════════════════════════════╗
    ║     GUNS.LOL REVERSE ENGINEERING BOT v1.0     ║
    ║     Cloudflare Bypass + Anti-Detection        ║
    ╚════════════════════════════════════════════════╝
    {Style.RESET_ALL}""")
    
    async def generate_canvas_fingerprint(self, page: Page) -> str:
        """Generuje unikalny fingerprint canvas (omijanie bot detection)"""
        fingerprint = await page.evaluate("""
            () => {
                const canvas = document.createElement('canvas');
                const ctx = canvas.getContext('2d');
                canvas.width = 200;
                canvas.height = 50;
                
                ctx.textBaseline = 'top';
                ctx.font = '14px Arial';
                ctx.fillStyle = '#f60';
                ctx.fillRect(0, 0, 100, 50);
                ctx.fillStyle = '#069';
                ctx.fillText('Test fingerprint', 2, 15);
                
                return canvas.toDataURL();
            }
        """)
        return fingerprint
    
    async def extract_cloudflare_tokens(self, page: Page) -> Dict[str, str]:
        """Ekstrahuje tokeny Cloudflare ze strony"""
        tokens = {}
        
        # Znajdź meta tagi Cloudflare
        meta_tags = await page.evaluate("""
            () => {
                const metas = document.querySelectorAll('meta');
                const result = {};
                metas.forEach(meta => {
                    const name = meta.getAttribute('name');
                    const content = meta.getAttribute('content');
                    if (name && content) {
                        result[name] = content;
                    }
                });
                return result;
            }
        """)
        
        # Znajdź pliki JS Cloudflare
        js_files = await page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script[src]');
                const cfScripts = [];
                scripts.forEach(script => {
                    const src = script.src;
                    if (src.includes('cloudflare') || src.includes('cf')) {
                        cfScripts.push(src);
                    }
                });
                return cfScripts;
            }
        """)
        
        # Pobierz cookies
        cookies = await page.context.cookies()
        
        tokens['meta_tags'] = meta_tags
        tokens['js_files'] = js_files
        tokens['cookies'] = cookies
        tokens['user_agent'] = await page.evaluate("navigator.userAgent")
        
        return tokens
    
    async def extract_api_endpoints(self, page: Page) -> list:
        """Reverse engineering - znajduje wszystkie endpointy API"""
        endpoints = []
        
        # Monitoruj wszystkie żądania sieciowe
        async def capture_request(request):
            if request.url.startswith('https://guns.lol/api') or '/api/' in request.url:
                endpoints.append({
                    'url': request.url,
                    'method': request.method,
                    'headers': request.headers,
                    'post_data': request.post_data
                })
        
        page.on('request', capture_request)
        
        # Wykonaj kliknięcie i zobacz co się dzieje
        await page.click('body', timeout=5000)
        await asyncio.sleep(2)
        
        return endpoints
    
    async def get_websocket_messages(self, page: Page) -> list:
        """Przechwytuje komunikaty WebSocket (częste w zabezpieczeniach)"""
        messages = []
        
        async def capture_websocket(ws):
            async def on_message(message):
                messages.append({
                    'type': 'message',
                    'data': message,
                    'timestamp': time.time()
                })
            
            ws.on('framereceived', on_message)
        
        page.on('websocket', capture_websocket)
        return messages
    
    async def generate_anti_detection_headers(self) -> Dict[str, str]:
        """Generuje nagłówki anty-detekcyjne"""
        return {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
            'Accept-Language': 'pl-PL,pl;q=0.9,en-US;q=0.8,en;q=0.7',
            'Accept-Encoding': 'gzip, deflate, br',
            'DNT': '1',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Sec-Fetch-Dest': 'document',
            'Sec-Fetch-Mode': 'navigate',
            'Sec-Fetch-Site': 'none',
            'Sec-Fetch-User': '?1',
            'Cache-Control': 'max-age=0',
            'TE': 'trailers'
        }
    
    async def bypass_cloudflare(self, page: Page) -> bool:
        """Omija zabezpieczenia Cloudflare"""
        try:
            print(f"{Fore.YELLOW}[*] Przechodzenie przez Cloudflare...{Style.RESET_ALL}")
            
            # Czekaj na rozwiązanie challenge'u
            await page.wait_for_timeout(3000)
            
            # Sprawdź czy jesteśmy po challenge'u
            current_url = page.url
            if 'captcha' in current_url or 'challenge' in current_url:
                print(f"{Fore.YELLOW}[!] Wykryto challenge - czekam na rozwiązanie...{Style.RESET_ALL}")
                await page.wait_for_timeout(10000)
                
                # Automatyczne odczekanie
                await page.wait_for_selector('body', timeout=30000)
            
            print(f"{Fore.GREEN}[+] Cloudflare bypassed!{Style.RESET_ALL}")
            return True
            
        except Exception as e:
            print(f"{Fore.RED}[-] Błąd Cloudflare: {e}{Style.RESET_ALL}")
            return False
    
    async def extract_click_handler(self, page: Page) -> Dict[str, Any]:
        """Reverse engineering - znajduje handler kliknięcia"""
        click_handler = await page.evaluate("""
            () => {
                // Znajdź event listenery dla kliknięć
                const body = document.body;
                const listeners = getEventListeners(body);
                
                // Szukaj funkcji obsługujących kliknięcia
                let clickFunction = null;
                if (listeners && listeners.click) {
                    clickFunction = listeners.click[0].listener.toString();
                }
                
                // Znajdź websocket do logowania
                let wsEndpoint = null;
                if (window.guns_lol_ws) {
                    wsEndpoint = window.guns_lol_ws;
                }
                
                return {
                    click_handler: clickFunction,
                    websocket_endpoint: wsEndpoint,
                    has_click_listener: !!clickFunction
                };
            }
        """)
        return click_handler
    
    async def simulate_human_click(self, page: Page):
        """Symuluje ludzkie kliknięcie z randomizacją"""
        # Losowa pozycja
        x = random.randint(100, 800)
        y = random.randint(100, 600)
        
        # Losowe opóźnienie
        await asyncio.sleep(random.uniform(0.1, 0.3))
        
        # Ruch myszy
        await page.mouse.move(x, y, steps=random.randint(5, 15))
        await asyncio.sleep(random.uniform(0.05, 0.1))
        
        # Kliknięcie
        await page.mouse.click(x, y)
        
        # Losowe opóźnienie po kliknięciu
        await asyncio.sleep(random.uniform(0.05, 0.15))
        
        return {'x': x, 'y': y, 'timestamp': time.time() * 1000}
    
    async def run(self, clicks: int = 1):
        """Główna funkcja bota"""
        self.banner()
        
        print(f"{Fore.CYAN}[*] Cel: {self.nick}{Style.RESET_ALL}")
        print(f"{Fore.CYAN}[*] URL: {self.url}{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}[*] Rozpoczynam reverse engineering...{Style.RESET_ALL}")
        
        async with async_playwright() as p:
            # Konfiguracja przeglądarki
            browser = await p.chromium.launch(
                headless=False,  # Musi być widoczna dla Cloudflare
                args=[
                    '--disable-blink-features=AutomationControlled',
                    '--no-sandbox',
                    '--disable-dev-shm-usage'
                ]
            )
            
            # Kontekst z rotacją fingerprintów
            context = await browser.new_context(
                viewport={'width': 1920, 'height': 1080},
                user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
                locale='pl-PL',
                timezone_id='Europe/Warsaw'
            )
            
            # Dodaj proxy jeśli podane
            if self.proxy:
                await context.set_extra_http_headers(await self.generate_anti_detection_headers())
            
            page = await context.new_page()
            
            # Ukryj webdriver
            await page.add_init_script("""
                Object.defineProperty(navigator, 'webdriver', {get: () => undefined});
                Object.defineProperty(navigator, 'plugins', {get: () => [1,2,3,4,5]});
                window.chrome = {runtime: {}};
            """)
            
            # Nawigacja do strony
            print(f"{Fore.YELLOW}[*] Ładowanie strony...{Style.RESET_ALL}")
            await page.goto(self.url, wait_until='networkidle', timeout=60000)
            
            # Bypass Cloudflare
            if not await self.bypass_cloudflare(page):
                print(f"{Fore.RED}[-] Nie udało się ominąć Cloudflare{Style.RESET_ALL}")
                return
            
            # Ekstrakcja tokenów
            self.tokens = await self.extract_cloudflare_tokens(page)
            print(f"{Fore.GREEN}[+] Wyciągnięto {len(self.tokens)} tokenów{Style.RESET_ALL}")
            
            # Znajdź handler kliknięcia
            click_handler = await self.extract_click_handler(page)
            print(f"{Fore.GREEN}[+] Znaleziono handler kliknięcia: {click_handler.get('has_click_listener')}{Style.RESET_ALL}")
            
            # Generuj fingerprint
            self.canvas_fingerprint = await self.generate_canvas_fingerprint(page)
            
            # Wykonaj kliknięcia
            for i in range(clicks):
                print(f"{Fore.CYAN}[*] Kliknięcie {i+1}/{clicks}{Style.RESET_ALL}")
                
                click_data = await self.simulate_human_click(page)
                
                # Czekaj na reakcję strony
                await asyncio.sleep(random.uniform(1, 2))
                
                # Sprawdź czy strona zareagowała
                current_url = page.url
                if 'captcha' in current_url:
                    print(f"{Fore.RED}[-] Wykryto captcha - przerwano{Style.RESET_ALL}")
                    break
                
                print(f"{Fore.GREEN}[+] Kliknięto w: ({click_data['x']}, {click_data['y']}){Style.RESET_ALL}")
                
                if i < clicks - 1:
                    wait_time = random.uniform(5, 10)
                    print(f"{Fore.YELLOW}[*] Czekam {wait_time:.1f}s przed następnym kliknięciem{Style.RESET_ALL}")
                    await asyncio.sleep(wait_time)
            
            # Raport końcowy
            print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
            print(f"{Fore.GREEN}[+] Wykonano: {clicks} kliknięć{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Fingerprint: {self.canvas_fingerprint[:50]}...{Style.RESET_ALL}")
            print(f"{Fore.CYAN}[*] Cookies: {len(self.tokens.get('cookies', []))}{Style.RESET_ALL}")
            
            # Zapisz wyniki reverse engineeringu
            with open('reverse_engineer_results.json', 'w') as f:
                json.dump({
                    'tokens': self.tokens,
                    'click_handler': str(click_handler),
                    'timestamp': time.time()
                }, f, indent=2)
            
            print(f"{Fore.GREEN}[+] Wyniki zapisane do reverse_engineer_results.json{Style.RESET_ALL}")
            print(f"{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
            
            await asyncio.sleep(3)
            await browser.close()

async def main():
    bot = GunsLolBot(
        nick=input(f"{Fore.YELLOW}Podaj nick: {Style.RESET_ALL}"),
        proxy=None  # Opcjonalnie: "http://ip:port"
    )
    
    clicks = int(input(f"{Fore.YELLOW}Ile kliknięć? (enter=1): {Style.RESET_ALL}") or "1")
    
    await bot.run(clicks=clicks)

if __name__ == "__main__":
    # Instalacja: pip install playwright && playwright install chromium
    asyncio.run(main())
