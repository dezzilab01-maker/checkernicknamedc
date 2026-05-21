#!/usr/bin/env python3
import requests
import threading
import time
import random
from colorama import Fore, Style, init
import sys
import urllib3

urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
init(autoreset=True)

def banner():
    print(f"""{Fore.CYAN}
    ╔══════════════════════════════════════╗
    ║     GUNS.LOL AUTO CLICKER v4.0      ║
    ║     Auto Proxy Downloader           ║
    ╚══════════════════════════════════════╝
    {Style.RESET_ALL}""")

def pobierz_proxy():
    print(f"{Fore.YELLOW}Pobieram listę proxy z API...{Style.RESET_ALL}")
    
    try:
        response = requests.get(
            "https://api.proxyscrape.com/v2/?request=displayproxies&protocol=http&timeout=5000&country=all&ssl=all&anonymity=all",
            timeout=30
        )
        
        if response.status_code == 200:
            proxies = [p.strip() for p in response.text.split('\n') if p.strip()]
            print(f"{Fore.GREEN}Pobrano {len(proxies)} proxy{Style.RESET_ALL}")
            return proxies
        else:
            print(f"{Fore.RED}Nie udało się pobrać proxy{Style.RESET_ALL}")
            return []
    except Exception as e:
        print(f"{Fore.RED}Błąd pobierania: {e}{Style.RESET_ALL}")
        return []

def sprawdz_proxy_http(proxy):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        response = requests.get("http://httpbin.org/ip", proxies=proxies, timeout=8)
        return response.status_code == 200
    except:
        return False

def sprawdz_proxy_https(proxy):
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        response = requests.get("https://httpbin.org/ip", proxies=proxies, timeout=8, verify=False)
        return response.status_code == 200
    except:
        return False

def kliknij(nick, proxy):
    url = f"http://guns.lol/{nick}"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
        'Accept-Language': 'pl-PL,pl;q=0.8,en-US;q=0.5,en;q=0.3',
        'Accept-Encoding': 'gzip, deflate',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
    }
    
    try:
        proxies = {"http": f"http://{proxy}", "https": f"http://{proxy}"}
        
        response = requests.get(url, proxies=proxies, headers=headers, timeout=15, verify=False)
        
        if response.status_code == 200:
            click_data = {
                'x': random.randint(0, 1920),
                'y': random.randint(0, 1080),
                'timestamp': int(time.time() * 1000)
            }
            
            headers['Referer'] = url
            headers['X-Requested-With'] = 'XMLHttpRequest'
            headers['Content-Type'] = 'application/json'
            
            requests.post(url, proxies=proxies, headers=headers, json=click_data, timeout=15, verify=False)
            
            return True, response.status_code
        else:
            return False, response.status_code
    except Exception as e:
        return False, str(e)

def worker(nick, proxy, stats, numer):
    status, kod = kliknij(nick, proxy)
    with stats['lock']:
        if status:
            stats['success'] += 1
            print(f"{Fore.GREEN}✓ [{numer}] {proxy} - Kliknięto! ({kod}){Style.RESET_ALL}")
        else:
            stats['failed'] += 1
            print(f"{Fore.RED}✗ [{numer}] {proxy} - Błąd: {kod}{Style.RESET_ALL}")
        stats['total'] += 1

def main():
    banner()
    
    nick = input(f"{Fore.YELLOW}Podaj swój nick (np. dezzi7): {Style.RESET_ALL}")
    if not nick:
        print(f"{Fore.RED}Nick nie może być pusty!{Style.RESET_ALL}")
        sys.exit(1)
    
    ile_watkow = int(input(f"{Fore.YELLOW}Ile wątków (szukam tyle proxy): {Style.RESET_ALL}") or "5")
    ile_watkow = min(ile_watkow, 30)
    
    wszystkie_proxy = pobierz_proxy()
    
    if not wszystkie_proxy:
        print(f"{Fore.RED}Nie udało się pobrać proxy!{Style.RESET_ALL}")
        sys.exit(1)
    
    print(f"\n{Fore.YELLOW}Szukam {ile_watkow} działających proxy...{Style.RESET_ALL}")
    
    dobre_proxy = []
    
    for proxy in wszystkie_proxy:
        if len(dobre_proxy) >= ile_watkow:
            break
        
        print(f"{Fore.CYAN}Sprawdzam: {proxy}...{Style.RESET_ALL}", end=" ")
        
        if sprawdz_proxy_https(proxy):
            dobre_proxy.append(proxy)
            print(f"{Fore.GREEN}✓ Działa HTTPS! ({len(dobre_proxy)}/{ile_watkow}){Style.RESET_ALL}")
        elif sprawdz_proxy_http(proxy):
            dobre_proxy.append(proxy)
            print(f"{Fore.YELLOW}⚠ Działa tylko HTTP ({len(dobre_proxy)}/{ile_watkow}){Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nie działa{Style.RESET_ALL}")
        
        time.sleep(0.2)
    
    if len(dobre_proxy) < ile_watkow:
        print(f"\n{Fore.RED}Znaleziono tylko {len(dobre_proxy)} z {ile_watkow} potrzebnych!{Style.RESET_ALL}")
        if len(dobre_proxy) == 0:
            print(f"{Fore.RED}Brak działających proxy!{Style.RESET_ALL}")
            sys.exit(1)
        
        kontynuuj = input(f"{Fore.YELLOW}Kontynuować z {len(dobre_proxy)} proxy? (t/n): {Style.RESET_ALL}")
        if kontynuuj.lower() != 't':
            sys.exit(1)
    
    print(f"\n{Fore.GREEN}Używam {len(dobre_proxy)} proxy{Style.RESET_ALL}")
    
    ile_klik = input(f"{Fore.YELLOW}Ile kliknięć na proxy? (enter=1): {Style.RESET_ALL}")
    ile_klik = int(ile_klik) if ile_klik.isdigit() else 1
    
    input(f"{Fore.YELLOW}Naciśnij Enter aby rozpocząć...{Style.RESET_ALL}")
    
    statystyki = {
        'success': 0,
        'failed': 0,
        'total': 0,
        'lock': threading.Lock()
    }
    
    for runda in range(ile_klik):
        print(f"\n{Fore.CYAN}=== Runda {runda+1}/{ile_klik} ==={Style.RESET_ALL}")
        
        watki = []
        for i, proxy in enumerate(dobre_proxy, 1):
            t = threading.Thread(target=worker, args=(nick, proxy, statystyki, i))
            t.start()
            watki.append(t)
            time.sleep(0.1)
        
        for t in watki:
            t.join()
        
        if runda < ile_klik - 1:
            print(f"{Fore.YELLOW}Odczekuję 3 sekundy...{Style.RESET_ALL}")
            time.sleep(3)
    
    print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Udanych: {statystyki['success']}{Style.RESET_ALL}")
    print(f"{Fore.RED}✗ Nieudanych: {statystyki['failed']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 Razem: {statystyki['total']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")

if __name__ == "__main__":
    main()
