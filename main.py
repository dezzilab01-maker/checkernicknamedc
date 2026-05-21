#!/usr/bin/env python3
import requests
import time
import random
import json
from colorama import Fore, Style, init
import sys

init(autoreset=True)

def banner():
    print(f"""{Fore.CYAN}
    ╔══════════════════════════════════════╗
    ║     GUNS.LOL CLICKER FOR TERMUX     ║
    ║     Works without Playwright        ║
    ╚══════════════════════════════════════╝
    {Style.RESET_ALL}""")

def get_proxies_from_api():
    """Pobiera proxy z API"""
    try:
        print(f"{Fore.YELLOW}Pobieram proxy z API...{Style.RESET_ALL}")
        response = requests.get(
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
            timeout=20
        )
        if response.status_code == 200:
            proxies = [p.strip() for p in response.text.split('\n') if p.strip()]
            print(f"{Fore.GREEN}Pobrano {len(proxies)} proxy{Style.RESET_ALL}")
            return proxies
    except Exception as e:
        print(f"{Fore.RED}Błąd API: {e}{Style.RESET_ALL}")
    return []

def test_proxy(proxy):
    """Testuje czy proxy działa"""
    try:
        test_url = "http://httpbin.org/ip"
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get(test_url, proxies=proxies, timeout=10)
        return response.status_code == 200
    except:
        return False

def click_guns(proxy, nick):
    """Wykonuje kliknięcie przez proxy"""
    url = f"http://guns.lol/{nick}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.9',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive'
    }
    
    try:
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get(url, proxies=proxies, headers=headers, timeout=10)
        return response.status_code == 200, response.status_code
    except Exception as e:
        return False, str(e)

def main():
    banner()
    
    nick = input(f"{Fore.YELLOW}Twój nick: {Style.RESET_ALL}")
    if not nick:
        nick = "dezzi7"
    
    ile_proxy = int(input(f"{Fore.YELLOW}Ile proxy użyć (max 20): {Style.RESET_ALL}") or "5")
    ile_proxy = min(ile_proxy, 20)
    
    wszystkie_proxy = get_proxies_from_api()
    
    if not wszystkie_proxy:
        print(f"{Fore.RED}Nie pobrano proxy. Uruchom ponownie.{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\n{Fore.YELLOW}Szukam {ile_proxy} działających proxy...{Style.RESET_ALL}")
    
    dobre_proxy = []
    for proxy in wszystkie_proxy[:50]:
        if len(dobre_proxy) >= ile_proxy:
            break
        
        print(f"{Fore.CYAN}Testuję: {proxy}...{Style.RESET_ALL}", end=" ")
        if test_proxy(proxy):
            dobre_proxy.append(proxy)
            print(f"{Fore.GREEN}✓ Działa! ({len(dobre_proxy)}/{ile_proxy}){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nie działa{Style.RESET_ALL}")
        time.sleep(0.5)
    
    if not dobre_proxy:
        print(f"{Fore.RED}Brak działających proxy!{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\n{Fore.GREEN}Znaleziono {len(dobre_proxy)} działających proxy{Style.RESET_ALL}")
    
    ile_klik = int(input(f"{Fore.YELLOW}Ile kliknięć na proxy: {Style.RESET_ALL}") or "1")
    
    print(f"\n{Fore.YELLOW}Startuję...{Style.RESET_ALL}")
    
    sukcesy = 0
    bledy = 0
    
    for i in range(ile_klik):
        print(f"\n{Fore.CYAN}Runda {i+1}/{ile_klik}{Style.RESET_ALL}")
        
        for proxy in dobre_proxy:
            status, kod = click_guns(proxy, nick)
            if status:
                sukcesy += 1
                print(f"{Fore.GREEN}✓ {proxy} - Klik!{Style.RESET_ALL}")
            else:
                bledy += 1
                print(f"{Fore.RED}✗ {proxy} - Błąd: {kod}{Style.RESET_ALL}")
            time.sleep(0.5)
        
        if i < ile_klik - 1:
            time.sleep(2)
    
    print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.GREEN}Sukcesy: {sukcesy}{Style.RESET_ALL}")
    print(f"{Fore.RED}Błędy: {bledy}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}Razem: {sukcesy + bledy}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")

if __name__ == "__main__":
    # Wyłącz warningi SSL
    import urllib3
    urllib3.disable_warnings()
    
    try:
        main()
    except KeyboardInterrupt:
        print(f"\n{Fore.YELLOW}Przerwano!{Style.RESET_ALL}")
        sys.exit(0)
