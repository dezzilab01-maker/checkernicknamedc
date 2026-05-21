import requests
import json
import time

# ========== KONFIGURACJA ==========
DISCORD_TOKEN = input("🔑 Podaj TOKEN konta Discord: ").strip()
DISCORD_PASSWORD = "gOrBFyXCq4TqRHI"  # Twoje hasło na stałe
CAPMONSTER_API_KEY = "bf1316d12774482f0402018ae62af244"  # Wpisz swój klucz z capmonster.cloud

# ========== FUNKCJA ROZWIĄZUJĄCA CAPTCHA ==========
def solve_captcha(site_key, page_url):
    """Wysyła CAPTCHA do CapMonster Cloud i zwraca token rozwiązania"""
    
    create_payload = {
        "clientKey": CAPMONSTER_API_KEY,
        "task": {
            "type": "NoCaptchaTaskProxyless",
            "websiteURL": page_url,
            "websiteKey": site_key
        }
    }
    
    try:
        resp = requests.post("https://api.capmonster.cloud/createTask", json=create_payload)
        task_id = resp.json().get("taskId")
    except:
        print("❌ Błąd połączenia z CapMonster")
        return None
    
    if not task_id:
        print("❌ Błąd CapMonster:", resp.text)
        return None
    
    print(f"🧩 Zadanie CAPTCHA utworzone (ID: {task_id})")
    
    while True:
        time.sleep(2)
        result_payload = {
            "clientKey": CAPMONSTER_API_KEY,
            "taskId": task_id
        }
        result = requests.post("https://api.capmonster.cloud/getTaskResult", json=result_payload).json()
        
        if result.get("status") == "ready":
            captcha_token = result["solution"]["gRecaptchaResponse"]
            print("✅ CAPTCHA rozwiązana pomyślnie!")
            return captcha_token
        elif result.get("status") == "processing":
            print("⏳ CapMonster rozwiązuje CAPTCHA...")
        else:
            print("⚠️ Nieoczekiwany status:", result)
            return None

# ========== FUNKCJA ZMIANY NAZWY ==========
def change_discord_nickname(token, password, new_nickname):
    headers = {
        "Authorization": token,
        "Content-Type": "application/json",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
    }
    
    payload = {
        "username": new_nickname,
        "password": password  # Hasło na stałe w kodzie
    }
    
    print("\n📡 Wysyłanie żądania zmiany nazwy...")
    response = requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)
    
    if response.status_code == 200:
        print(f"✨ Sukces! Nazwa zmieniona na: {new_nickname}")
        return True
    
    if response.status_code == 400 and "captcha" in response.text.lower():
        print("🔒 Discord wymaga rozwiązania CAPTCHA!")
        
        SITE_KEY = "4c672d35-0701-42b2-88c3-78380b0db560"
        PAGE_URL = "https://discord.com/login"
        
        captcha_token = solve_captcha(SITE_KEY, PAGE_URL)
        if not captcha_token:
            print("❌ Nie udało się rozwiązać CAPTCHA")
            return False
        
        payload["captcha_key"] = captcha_token
        response = requests.patch("https://discord.com/api/v9/users/@me", headers=headers, json=payload)
        
        if response.status_code == 200:
            print(f"✨ Sukces! Nazwa zmieniona na: {new_nickname} (po CAPTCHA)")
            return True
        else:
            print(f"❌ Błąd po CAPTCHA: {response.status_code}")
            print(f"Odpowiedź: {response.text}")
            return False
    else:
        print(f"❌ Błąd: {response.status_code}")
        print(f"Odpowiedź: {response.text}")
        
        if response.status_code == 400 and "password" in response.text.lower():
            print("⚠️ Hasło jest niepoprawne!")
        return False

# ========== GŁÓWNA CZĘŚĆ PROGRAMU ==========
if __name__ == "__main__":
    print("=" * 50)
    print("   Discord Nickname Changer + CapMonster")
    print("=" * 50)
    
    NEW_NAME = input("✏️ Podaj NOWĄ NAZWĘ użytkownika: ").strip()
    
    if not DISCORD_TOKEN or not NEW_NAME:
        print("❌ Token i nowa nazwa są wymagane!")
        exit(1)
    
    if CAPMONSTER_API_KEY == "TWOJ_KLUCZ_API_Z_CAPMONSTER":
        print("\n⚠️ UWAGA: Nie podałeś klucza CapMonster!")
        print("   Jeśli Discord zażąda CAPTCHA – skrypt nie zadziała.")
        kontynuuj = input("Czy chcesz kontynuować bez CapMonster? (t/n): ")
        if kontynuuj.lower() != 't':
            exit(0)
    
    print(f"\n📝 Nowa nazwa: {NEW_NAME}")
    print(f"🔒 Hasło: {DISCORD_PASSWORD[:3]}*** (ustawione w kodzie)")
    print("-" * 50)
    
    success = change_discord_nickname(DISCORD_TOKEN, DISCORD_PASSWORD, NEW_NAME)
    
    if success:
        print("\n🎉 Wszystko gotowe!")
    else:
        print("\n💀 Zmiana nazwy nie powiodła się.")
