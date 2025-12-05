path = r"C:\Users\wangg\AppData\Local\Programs\Python\Python313\Lib\site-packages\playwright_stealth\stealth.py"
try:
    with open(path, "r", encoding="utf-8") as f:
        print(f.read())
except Exception as e:
    print(f"Error: {e}")
