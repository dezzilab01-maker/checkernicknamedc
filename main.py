#!/usr/bin/env python3
import requests
import threading
import time
import random
from colorama import Fore, Style, init
import sys

init(autoreset=True)

def banner():
    print(f"""{Fore.CYAN}
    ╔══════════════════════════════════════╗
    ║     GUNS.LOL AUTO CLICKER v3.0      ║
    ║     HTTPS Proxy Compatible          ║
    ╚══════════════════════════════════════╝
    {Style.RESET_ALL}""")

def check_proxy(proxy):
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

def check_https_proxy(proxy):
    try:
        test_url = "https://httpbin.org/ip"
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        response = requests.get(test_url, proxies=proxies, timeout=10, verify=False)
        return response.status_code == 200
    except:
        return False

def click_screen(nick, proxy):
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
        proxies = {
            "http": f"http://{proxy}",
            "https": f"http://{proxy}"
        }
        
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
            
            click_response = requests.post(
                url, 
                proxies=proxies, 
                headers=headers,
                json=click_data,
                timeout=15,
                verify=False
            )
            
            return True, response.status_code
        else:
            return False, response.status_code
    except Exception as e:
        return False, str(e)

def worker(nick, proxy, stats):
    status, code = click_screen(nick, proxy)
    with stats['lock']:
        if status:
            stats['success'] += 1
            print(f"{Fore.GREEN}✓ {proxy} - Kliknięto! (Status: {code}){Style.RESET_ALL}")
        else:
            stats['failed'] += 1
            print(f"{Fore.RED}✗ {proxy} - Błąd: {code}{Style.RESET_ALL}")
        stats['total'] += 1

def main():
    banner()
    
    nick = input(f"{Fore.YELLOW}Podaj swój nick (np. dezzi7): {Style.RESET_ALL}")
    if not nick:
        print(f"{Fore.RED}Nick nie może być pusty!{Style.RESET_ALL}")
        sys.exit(1)
    
    try:
        with open('proxy.txt', 'r') as f:
            all_proxies = [line.strip() for line in f if line.strip()]
    except FileNotFoundError:
        print(f"{Fore.RED}Nie znaleziono pliku proxy.txt!{Style.RESET_ALL}")
        print(f"{Fore.YELLOW}Tworzę przykładowy plik proxy.txt...{Style.RESET_ALL}")
        with open('proxy.txt', 'w') as f:
            f.write("# Wpisz swoje proxy w formacie IP:PORT\n")
            f.write("# Przykład:\n")
            f.write("# 123.123.123.123:8080\n")
        sys.exit(1)
    
    if not all_proxies:
        print(f"{Fore.RED}Plik proxy.txt jest pusty!{Style.RESET_ALL}")
        sys.exit(1)
    
    threads_count = int(input(f"{Fore.YELLOW}Ile wątków (szukam tyle działających proxy): {Style.RESET_ALL}") or "5")
    threads_count = min(threads_count, 50)
    
    print(f"\n{Fore.YELLOW}Szukam {threads_count} działających proxy HTTPS...{Style.RESET_ALL}")
    
    working_proxies = []
    for proxy in all_proxies:
        if len(working_proxies) >= threads_count:
            break
            
        print(f"{Fore.CYAN}Sprawdzam: {proxy}...{Style.RESET_ALL}")
        
        if check_https_proxy(proxy):
            working_proxies.append(proxy)
            print(f"{Fore.GREEN}✓ Działa HTTPS! Znaleziono: {len(working_proxies)}/{threads_count}{Style.RESET_ALL}")
        elif check_proxy(proxy):
            print(f"{Fore.YELLOW}⚠ Działa tylko HTTP, może mieć problemy{Style.RESET_ALL}")
            working_proxies.append(proxy)
            print(f"{Fore.GREEN}✓ Dodano (HTTP): {len(working_proxies)}/{threads_count}{Style.RESET_ALL}")
        else:
            print(f"{Fore.RED}✗ Nie działa{Style.RESET_ALL}")
        time.sleep(0.3)
    
    if len(working_proxies) < threads_count:
        print(f"\n{Fore.RED}Znaleziono tylko {len(working_proxies)} działających proxy z {threads_count} potrzebnych!{Style.RESET_ALL}")
        kontynuuj = input(f"{Fore.YELLOW}Czy kontynuować z {len(working_proxies)} proxy? (t/n): {Style.RESET_ALL}")
        if kontynuuj.lower() != 't':
            sys.exit(1)
    else:
        print(f"\n{Fore.GREEN}Znaleziono {len(working_proxies)} działających proxy!{Style.RESET_ALL}")
    
    ilosc_klik = input(f"{Fore.YELLOW}Ile kliknięć na proxy? (enter = 1): {Style.RESET_ALL}")
    if ilosc_klik.isdigit():
        ilosc_klik = int(ilosc_klik)
    else:
        ilosc_klik = 1
    
    input(f"{Fore.YELLOW}Naciśnij Enter aby rozpocząć...{Style.RESET_ALL}")
    
    stats = {
        'success': 0,
        'failed': 0,
        'total': 0,
        'lock': threading.Lock()
    }
    
    for klik in range(ilosc_klik):
        print(f"\n{Fore.CYAN}=== Runda {klik+1}/{ilosc_klik} ==={Style.RESET_ALL}")
        
        threads = []
        for proxy in working_proxies:
            t = threading.Thread(target=worker, args=(nick, proxy, stats))
            t.start()
            threads.append(t)
            time.sleep(0.1)
        
        for t in threads:
            t.join()
        
        if klik < ilosc_klik - 1:
            print(f"{Fore.YELLOW}Odczekuję 2 sekundy przed następną rundą...{Style.RESET_ALL}")
            time.sleep(2)
    
    print(f"\n{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")
    print(f"{Fore.GREEN}✓ Udanych kliknięć: {stats['success']}{Style.RESET_ALL}")
    print(f"{Fore.RED}✗ Nieudanych: {stats['failed']}{Style.RESET_ALL}")
    print(f"{Fore.YELLOW}📊 Razem: {stats['total']}{Style.RESET_ALL}")
    print(f"{Fore.CYAN}═══════════════════════════════════{Style.RESET_ALL}")

if __name__ == "__main__":
    # Wyłącz warningi SSL
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)
    main()
