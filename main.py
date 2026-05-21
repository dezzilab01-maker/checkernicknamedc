import requests
import json
import time
import sys

# KONFIGURACJA
CAPMONSTER_API_KEY = "bf1316d12774482f0402018ae62af244"  # https://capmonster.cloud/ -> Dashboard
DISCORD_TOKEN = input("Podaj token Discorda: ")

def solve_captcha(site_key, page_url):
    """Wysyła CAPTCHA do CapMonster i czeka na rozwiązanie"""
    
    # Tworzenie zadania
    create_task_payload = {
        "clientKey": CAPMONSTER_API_KEY,
        "task": {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key
        }
    }
    
    response = requests.post("https://api.capmonster.cloud/createTask", json=create_task_payload)
    task_id = response.json().get("taskId")
    
    if not task_id:
        print("❌ Błąd tworzenia zadania:", response.text)
        return None
    
    print(f"🧩 Zadanie CAPTCHA utworzone (ID: {task_id}), czekam na rozwiązanie...")
    
    # Pobieranie wyniku
    while True:
        time.sleep(2)
        result_payload = {
            "clientKey": CAPMONSTER_API_KEY,
            "taskId": task_id
        }
        result = requests.post("https://api.capmonster.cloud/getTaskResult", json=result_payload)
        status = result.json().get("status")
        
        if status == "ready":
            solution = result.json()["solution"]["gRecaptchaResponse"]
            print("✅ CAPTCHA rozwiązana!")
            return solution
        elif status == "processing":
            print("⏳ CapMonster jeszcze rozwiązuje...")
        else:
            print("⚠️ Nieznany status:", result.text)
            return None

def change_discord_nickname(new_nickname):
    headers = {
        "Authorization": DISCORD_TOKEN,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    # Najpierw próbujemy bez CAPTCHA
    payload = {"username": new_nickname}
    response = requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✨ Nazwa zmieniona na: {new_nickname}")
        return True
    
    # Jeśli wymagana CAPTCHA (kod 400 lub 429)
    if response.status_code == 400 and "captcha" in response.text.lower():
        print("🔒 Discord wymaga CAPTCHA!")
        
        # Pobieramy site_key i url z odpowiedzi (można też ręcznie)
        # Dla Discorda site_key to zwykle "4c672d35-0701-42b2-88c3-78380b0db560"
        site_key = "4c672d35-0701-42b2-88c3-78380b0db560"  # klucz reCAPTCHA Discorda
        page_url = "https://discord.com/login"
        
        captcha_token = solve_captcha(site_key, page_url)
        if not captcha_token:
            print("❌ Nie udało się rozwiązać CAPTCHA")
            return False
        
        # Powtarzamy żądanie z tokenem CAPTCHA
        payload["captcha_key"] = captcha_token
        response = requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✨ Nazwa zmieniona na: {new_nickname} (po CAPTCHA)")
            return True
        else:
            print(f"❌ Błąd po CAPTCHA: {response.status_code} - {response.text}")
            return False
    else:
        print(f"❌ Błąd: {response.status_code} - {response.text}")
        return False

# GŁÓWNY PROGRAM
if __name__ == "__main__":
    print("=== Discord Nickname Changer z CapMonster ===")
    new_name = input("Podaj nową nazwę użytkownika: ")
    
    if change_discord_nickname(new_name):
        print("✅ Gotowe!")
    else:
        print("❌ Zmiana nazwy nie powiodła się")
