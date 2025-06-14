import websocket
import threading
import time
import queue
import ssl

try:
    _create_unverified_https_context = ssl._create_unverified_context
except AttributeError:
    # Legacy Python that doesn't verify HTTPS certificates by default
    pass
else:
    # Handle target environment that doesn't support HTTPS verification
    ssl._create_default_https_context = _create_unverified_https_context
# Mesajları saklamak için bir kuyruk oluşturun
message_queue = queue.Queue()

# Global değişkenler
last_message = None
last_message_lock = threading.Lock()

def send_ping(ws, interval):
    while True:
        try:
            ws.sock.ping()  # WebSocketApp nesnesinin sock özelliği üzerinden ping göndermek
            print("Ping sent")
            time.sleep(interval)
        except websocket.WebSocketConnectionClosedException:
            print("Connection closed")
            break

def on_message(ws, message):
    global last_message
    print(f"Message received: {message}")
    # Mesajı kuyrukta saklayın
    message_queue.put(message)
    with last_message_lock:
        last_message = message

def on_error(ws, error):
    print(f"Error: {error}")

def on_close(ws, close_status_code, close_msg):
    print("Connection closed")

def on_open(ws):
    # Ping gönderen thread'i başlat
    ping_thread = threading.Thread(target=send_ping, args=(ws, 5))
    ping_thread.start()

def process_messages():
    while True:
        # Kuyruktan mesajı alın ve işleyin
        message = message_queue.get()
        if message is None:
            break
        print(f"Processing message: {message}")
        # Burada mesajları işlemek için ek kod ekleyebilirsiniz

def get_last_message():
    global last_message
    with last_message_lock:
        return last_message

def connect_to_spotify(token, proxy_host=None, proxy_port=None, proxy_username=None, proxy_password=None):
    url = f"wss://gew4-dealer.spotify.com/?access_token={token}"
    ws_headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/127.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Accept-Language": "en-GB,en;q=0.5",
        "Accept-Encoding": "gzip, deflate, br, zstd",
        "Sec-WebSocket-Version": "13",
        "Origin": "https://open.spotify.com",
        "Sec-WebSocket-Extensions": "permessage-deflate",
        "DNT": "1",
        "Sec-GPC": "1",
        "Connection": "keep-alive, Upgrade",
        "Sec-Fetch-Dest": "empty",
        "Sec-Fetch-Mode": "websocket",
        "Sec-Fetch-Site": "same-site",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "Upgrade": "websocket"
    }

    ws = websocket.WebSocketApp(
        url,
        header=ws_headers,
        on_message=on_message,
        on_error=on_error,
        on_close=on_close,
        on_open=on_open
    )
    
    proxy_opts = {
        "http_proxy_host": "127.0.0.1",
        "http_proxy_port": "8080",
        "proxy_type": "http"
    }
    
    if proxy_username and proxy_password:
        proxy_opts["http_proxy_auth"] = ("uqGsIqmJiskE0wh-res-any", "6XPBuKiPvRKTICQ")
    
    ws.run_forever(http_proxy_host=proxy_host, http_proxy_port=proxy_port,
                   http_proxy_auth=(proxy_username, proxy_password),
  proxy_type="http",sslopt={"cert_reqs": ssl.CERT_NONE,
                   "check_hostname": False,
                   })
    ws.run_forever()
    if proxy_host and proxy_port:
        if proxy_username and proxy_password:
            ws.run_forever(**proxy_opts)
        else:
            ws.run_forever(http_proxy_host=proxy_host, http_proxy_port=proxy_port)
    else:
        ws.run_forever()

# Örnek kullanım
headers = {
    'authorization': 'Bearer YOUR_ACCESS_TOKEN_HERE'
}
proxy_host = 'your.proxy.host'
proxy_port = 8080
proxy_username = 'your_username'
proxy_password = 'your_password'

#connect_to_spotify(headers, proxy_host, proxy_port, proxy_username, proxy_password)
