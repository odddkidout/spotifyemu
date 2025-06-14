import json
from managers.mobile import Spotify as loginclient
import os
import binascii
import requests
from requests.adapters import HTTPAdapter
from spotify.login5.v3.client_info_pb2 import ClientInfo
import spotify.login5.v3.login5_pb2 as login0
from google.protobuf.json_format import MessageToJson
from spotify.login5.v3.credentials.credentials_pb2 import Password, StoredCredential
from spotify.login5.v3.challenges.hashcash_pb2 import HashcashSolution
from google.protobuf import duration_pb2
from managers.helper import get_traceback, solver
from protobuf_to_dict import protobuf_to_dict
import threading
from managers.spotify_websocket import connect_to_spotify,get_last_message
def random_hex_string(length: int):
    get_random_bytes = os.urandom
    buffer = get_random_bytes(int(length / 2))
    return binascii.hexlify(buffer).decode()


class Spotify:
    def __init__(self,email: str, password: str,deviceid=None,proxy=None) -> None:
        self.username = None
        self.email = None
        self.password = None
        self.refreshtoken = None
        self._device_id = None
        self.client_id = None
        self.connection_id = None
        if email:
            self.email = email
        if password:
            self.password = password


        self.client_secret = None
        self.email = email.strip()
        self.LoggedIn = False
        self.password = password.strip()
        self._client_id = "9a8d2f0ce77a4e248bb71fefcb557637"
        
        self._app = "Spotify"
        self._version = "8.9.52.552"
        self._androidMdodel = "(SM-G996B)"
        self.androidmanufacturer = "Samsung"
        self._androidVersion = "Android/32"
        if deviceid:
            self._device_id = deviceid
        else:    
            self._device_id = random_hex_string(16)
        self.client_token = ""
        self.s = requests.Session()
        self.s.mount('http://', HTTPAdapter(max_retries=5))
        self.s.mount('https://', HTTPAdapter(max_retries=5))
        self.authToken = None
        if True:
            self.s.proxies.update({
                "http": f"http://127.0.0.1:8080",
                "https": f"http://127.0.0.1:8080" 
            })
            print("Using proxy: ", "http://127.0.0.1:8080")



    def login(self) -> None:
        try:
            #print("Logging in with: ", self.email, self.password)
            self.s.headers.update({
                "Cache-Control": "no-cache, no-store, max-age=0",
                "User-Agent": f"{self._app}/{self._version} Android/{self._androidVersion} ({self._androidMdodel})",
                "Content-Type": "application/x-protobuf",
                'Accept-Encoding': 'gzip, deflate',
            })
            #print("Sending login request")
            protoreq = login0.LoginRequest(client_info=ClientInfo(client_id=self._client_id, device_id=self._device_id),
                                        password=Password(id=self.email, password=self.password,
                                                            padding=binascii.unhexlify(
                                                                b'151515151515151515151515151515151515151515')))
                                                 
            while True: 
                try:
                    #print("Sending login request 2")
                    resp = self.s.post("https://login5.spotify.com/v3/login",
                                    protoreq.SerializeToString(),timeout=10 ,verify=False)
                    if resp.content == b'\n<html><head>\n<meta http-equiv="content-type" content="text/html;charset=utf-8">\n<title>403 Forbidden</title>\n</head>\n<body text=#000000 bgcolor=#ffffff>\n<h1>Error: Forbidden</h1>\n<h2>Your client does not have permission to get URL <code>/v3/login</code> from this server.</h2>\n<h2></h2>\n</body></html>\n':
                        continue
                    break
                    #print("Got login response")
                except requests.exceptions.Timeout:
                    print(self.threadnum, "Proxy error")
                    continue
                except requests.exceptions.ProxyError:
                    print(self.threadnum, "Proxy error")
                    #print("Proxy error")
                    continue
                except requests.exceptions.ConnectionError:
                    print(self.threadnum, "Connection error")
                    #print("Connection error")
                    continue
                except Exception as e:
                    print(self.threadnum, get_traceback(e))
                    #print("Error: ", get_traceback(e))
                    return False
                
                
            
            if resp.content == b'\x10\x01':
                print("Wrong password")
                return False

            #print("Got login response")
            proto_res = login0.LoginResponse()
            proto_res.ParseFromString(resp.content)
            #print(proto_res)
            ch = proto_res.challenges
            hashcash = ch.challenges[0].hashcash.prefix
            con = proto_res.login_context
            sufx, rep = solver(con, hashcash)
            #print("Solved captcha")
            if not sufx:
                return False
            dur = duration_pb2.Duration(nanos=1000000000, seconds=1)
            challengesolution = HashcashSolution(suffix=sufx, duration=dur)
            challengesolutions = login0.ChallengeSolution(hashcash=challengesolution)
            protoreqq = login0.LoginRequest(client_info=ClientInfo(client_id=self._client_id, device_id=self._device_id),
                                            password=Password(id=self.email, password=self.password,
                                                            padding=binascii.unhexlify(
                                                                b'151515151515151515151515151515151515151515')),
                                            login_context=con,
                                            challenge_solutions=login0.ChallengeSolutions(solutions=[challengesolutions]))
            #print("Sending login request with captcha")
            while True:
                try:
                    respp = self.s.post("https://login5.spotify.com/v3/login",
                                        protoreqq.SerializeToString(),timeout=10,verify=False)
                    break
                except requests.exceptions.Timeout:
                    print(self.threadnum, "Proxy error")
                    continue
                except requests.exceptions.ProxyError:
                    print(self.threadnum, "Proxy error")
                    #print("Proxy error")
                    continue
                except requests.exceptions.ConnectionError:
                    print(self.threadnum, "Connection error")
                    #print("Connection error")
                    continue
                except Exception as e:
                    print(self.threadnum, get_traceback(e))
                    #print("Error: ", get_traceback(e))
                    return False    
            
            if respp.content == b'\x10\x01':
                print("Wrong password")
                return False                    
            if respp.content == b'\x10\x04':
                print("Wrong password")
                return False                    
            
            if respp.status_code == 200: 
                proto_ress = login0.LoginResponse()
                proto_ress.ParseFromString(respp.content)
                self.username = (protobuf_to_dict(proto_ress)['ok']['username'])
                self.authToken = (protobuf_to_dict(proto_ress)['ok']['access_token'])
                self.refreshToken = (protobuf_to_dict(proto_ress)['ok']['stored_credential'])
                print(proto_ress)
                print("Logged in")
                self.LoggedIn = True
                return True
            
            return False
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write("error in login: " + str(get_traceback(e)) + "\n")
                print("Error: ", get_traceback(e))
            return False

    def saveSession(self) -> None:

        with open(f'./sessions/{self.email}.json', 'w') as file:
            file.write(self.email+":"+self.password+":"+str(self.refreshToken)+":"+self.username+":"+self.authToken+":"+self._device_id)
            



    def loginWithToken(self) -> None:
        with open(f'./sessions/{self.email}.json', 'r') as file:
            data = file.read().split(":")
            self.email = data[0]
            self.password = data[1]
            

            self.refreshToken = data[2].split("'")[1]
            self.refreshToken = bytes(self.refreshToken, 'utf-8')
            self.username = data[3]
            self.authToken = data[4]
            self._device_id = data[5]
        
        
            self.s.headers.clear()
            self.s.headers.update({
                    "Cache-Control": "no-cache, no-store, max-age=0",
                    "User-Agent": f"{self._app}/{self._version} Android/{self._androidVersion} ({self._androidMdodel})",
                    "Content-Type": "application/x-protobuf",
                    'Accept-Encoding': 'gzip, deflate,br',
                })
            protoreq = login0.LoginRequest(client_info=ClientInfo(client_id=self._client_id, device_id=self._device_id),
                                            stored_credential=StoredCredential(username=self.username,data=self.refreshToken))
            while True: 
                try:
                    #print("Sending login request 2")
                    resp = self.s.post("https://login5.spotify.com/v3/login",
                                    protoreq.SerializeToString(),timeout=10,verify=False )
                    if resp.content == b'\n<html><head>\n<meta http-equiv="content-type" content="text/html;charset=utf-8">\n<title>403 Forbidden</title>\n</head>\n<body text=#000000 bgcolor=#ffffff>\n<h1>Error: Forbidden</h1>\n<h2>Your client does not have permission to get URL <code>/v3/login</code> from this server.</h2>\n<h2></h2>\n</body></html>\n':
                        continue
                    break
                    #print("Got login response")
                except requests.exceptions.Timeout:
                    print(self.threadnum, "Proxy error")
                    continue
                except requests.exceptions.ProxyError:
                    print(self.threadnum, "Proxy error")
                    #print("Proxy error")
                    continue
                except requests.exceptions.ConnectionError:
                    print(self.threadnum, "Connection error")
                    #print("Connection error")
                    continue
                except Exception as e:
                    print(self.threadnum, get_traceback(e))
                    #print("Error: ", get_traceback(e))
                    return False
            if resp.content == b'\x10\x01':
                print("Wrong password")
                return False
            if resp.status_code == 200: 
                    proto_ress = login0.LoginResponse()
                    proto_ress.ParseFromString(resp.content)
                    self.username = (protobuf_to_dict(proto_ress)['ok']['username'])
                    self.authToken = (protobuf_to_dict(proto_ress)['ok']['access_token'])
                    self.refreshToken = (protobuf_to_dict(proto_ress)['ok']['stored_credential'])
                    print(proto_ress)
                    print("Logged in")
                    self.LoggedIn = True
                    return True
                    


    def getOTT(self,auth=None) -> str:
        if not self.authToken:
            self.authToken = auth
        self.s.headers.clear()
        pos = '{"url":"https://accounts.spotify.com/en/status"}'
        headerstk = {"Accept-Language": "en",
                     "Authorization": f"Bearer {self.authToken}",
                     "Content-Type": "application/json",
                     "User-Agent": "Spotify/116500643 Win32/Windows 10 (10.0.19043; x64)",
                     "Origin": "https://spclient.wg.spotify.com",
                     "Sec-Fetch-Site": "same-origin",
                     "Sec-Fetch-Mode": "no-cors",
                     "Sec-Fetch-Dest": "empty",
                     "Accept-Encoding": "gzip, deflate",
                     "Content-Length": '112'}
        self.s.headers.update(headerstk)
        for i in range(3):
            try:
                resp = self.s.post("https://spclient.wg.spotify.com/sessiontransfer/v1/token", data=pos,timeout=10,verify=False)
                if resp.status_code == 200:
                    tok = resp.json()["token"]
                    print(tok)
                    self.ott =  tok
                    return tok
            except Exception as e:
                with open('error.txt', 'a') as f:
                    f.write("error in reset password: " + str(e) + "\n")

    def GetSPDC(self):
        csrf = self.warmup()
        header = { "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Chromium\";v=\"112\"",
        "Content-Type": "text/plain;charset=UTF-8",
        "X-Csrf-Token": csrf,
        "Sec-Ch-Ua-Mobile": "0",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Accept": "*/*",
        "Origin": "https://accounts.spotify.com",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Referer": "https://accounts.spotify.com/login/ott/v2",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9"
        }
        self.s.headers.update(header)
        
        r = self.s.post("https://accounts.spotify.com/api/login/ott/verify", data = "{\"token\":\""+ self.ott+"\"}",verify=False)
        
        print(self.s.cookies["sp_dc"])
        
        self.spdc = self.s.cookies["sp_dc"]
         

    def warmup(self):
        self.s.headers.clear()
        header = {
        "Sec-Ch-Ua": "\"Not:A-Brand\";v=\"99\", \"Chromium\";v=\"112\"",
        "Sec-Ch-Ua-Mobile": "0",
        "Sec-Ch-Ua-Platform": "\"Windows\"",
        "Upgrade-Insecure-Requests": "1",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.5615.50 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
        "Sec-Fetch-Site": "none",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-User": "1",
        "Sec-Fetch-Dest": "document",
        "Accept-Encoding": "gzip, deflate",
        "Accept-Language": "en-US,en;q=0.9",
        }
        self.s.headers.update(header)
        r = self.s.get("https://accounts.spotify.com/login/ott/v2",verify=False)
        csrfToken = r.text.split("initialToken")[1].split("\"")[2]
        
        return csrfToken

    def get_access_token(self):
        

        headers = {
            "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0.0.0 Mobile Safari/537.36",
            "Accept-Encoding": "gzip, deflate",
        }
        self.s.headers.update(headers)
        r = self.s.get("https://open.spotify.com/get_access_token?reason=transport&productType=mobile-web-player",verify=False)
        print(json.loads(r.text))
        self.client_id = json.loads(r.text)['clientId']
        self.accessToken = json.loads(r.text)['accessToken']

        
    def getClientToken(self):

        url = "https://clienttoken.spotify.com/v1/clienttoken"
        headers = {
            "Content-Type": "application/json",
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36",
            "Origin": "https://open.spotify.com",
            "Referer": "https://open.spotify.com/",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-site",
            "sec-gpc": "1",
            "Accept": "application/json",
            "Accept-Language": "en-US,en;q=0.7",
            "Accept-Encoding": "gzip, deflate",
        }

        data = {
            "client_data": {
                "client_version": "1.2.28.53.g27d691b8",
                "client_id": self.client_id,
                "js_sdk_data": {
                    "device_id": self._device_id,
                    "device_type": "computer",
                    "device_brand": "unknown",
                    "device_model": "unknown",
                    "os": "Windows",
                    "os_version": "NT 10.0"
                }
            }
        }

        response = requests.post(url, headers=headers, json=data,verify=False)
        print(response.text)
        self.client_token = response.json()["granted_token"]["token"]
        return response.json()

    def connectSocket(self):

        self.ott = self.getOTT()
        self.GetSPDC()
        self.get_access_token()
        self.getClientToken()


        """if self.proxies:"""
        if True:
                if self.s.proxies["http"].__contains__("@"):
                    
                    proxy_host = f'{self.s.proxies["http"].split("//")[1].split("@")[1].split(":")[0]}'
                    proxy_port = f'{self.s.proxies["http"].split("//")[1].split("@")[1].split(":")[1]}'
                    proxy_username = f'{self.s.proxies["http"].split("//")[1].split("@")[0].split(":")[0]}'
                    proxy_password = f'{self.s.proxies["http"].split("//")[1].split("@")[0].split(":")[1]}'
                    print(proxy_host, proxy_port, proxy_username, proxy_password)
                else:
                    proxy_host = f'{self.s.proxies["http"].split("//")[1].split(":")[0]}'
                    proxy_port = f'{self.s.proxies["http"].split("//")[1].split(":")[1]}'
                    proxy_username= None
                    proxy_password = None
                    print(proxy_host, proxy_port, proxy_username, proxy_password)
                
                websocket_thread = threading.Thread(target=connect_to_spotify, args=(self.accessToken, proxy_host, proxy_port, proxy_username, proxy_password))
                websocket_thread.start()
        else:
            websocket_thread = threading.Thread(target=connect_to_spotify, args=(self.accessToken,))
            websocket_thread.start()
        response = self.wait_for_message("Spotify-Connection-Id")
        self.connection_id = json.loads(response)["headers"]["Spotify-Connection-Id"]
        print(self.connection_id)           

    def wait_for_message(self, msg):
        while True:
            last_message = get_last_message()
            if last_message is not None:
                if msg in str(last_message):
                    print("last message:\n\n" )
                    print(last_message)
                    return last_message


    def createDevice(self):

        url = "https://gew4-spclient.spotify.com/track-playback/v1/devices"
        
        payload = {
        "device": {
            "brand": "spotify",
            "capabilities": {
            "change_volume": True,
            "enable_play_token": True,
            "supports_file_media_type": True,
            "play_token_lost_behavior": "pause",
            "disable_connect": False,
            "audio_podcasts": True,
            "video_playback": True,
            "manifest_formats": [
            "file_ids_mp3",
            "file_urls_mp3",
            "manifest_ids_video",
            "file_urls_external",
            "file_ids_mp4",
            "file_ids_mp4_dual"
        ]
            },
            "device_id": self._device_id,
            "device_type": "smartphone",
            "metadata": {},
            "model": "SM-G9666F",
            "name": "SM-G9666F",
            "platform_identifier": "Android OS 10.1 API 32 (samsung, SM-G9666F)",
            "is_group": False
        },
        "outro_endcontent_snooping": False,
        "connection_id": self.connection_id,
        "client_version": "harmony:4.43.3-ecaa5cb8",
        "volume": 65535
        }
        
        self.auth = "Bearer " + self.authToken
        headers = {
        "Authorization": self.auth,
        "client-token": self.client_token,
        "sec-ch-ua": '"Chromium"; v="112", "Google Chrome";v="112", "Not:A-Brand";v = "99"',
        "sec-ch-ua-mobile": "?1",
        "sec-ch-ua-platform": "Android",
        "Accept": "*/*",
        "Origin": "https://open.spotify.com",
        "sec-fetch-site": "same-site",
        "sec-fetch-mode": "cors",
        "sec-fetch-dest": "empty",
        "Referer": "https://open.spotify.com/",
        "Accept-Language": "nl-NL, nl; q=0.9, en-US; q=0.8, en; q=0.7",
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-A037U) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/112.0.0.0 Mobile Safari/537.36 uacq",
        "Content-Type": "application/json; charset=utf-8",
        }
        
        
        print("\n\n")
        print("Headers : \n" )
        print(headers)
        print("data : \n" )
        print(payload)        
        self.s.headers.clear()
        self.s.cookies.clear()
        response = self.s.post(url, json=payload, headers=headers,verify=False)
        print("Response: \n")
        print(response.json())
        self.seq_number = response.json()["initial_seq_num"]
        if "PREMIUM_REQUIRED" in str(response.json()):
                return False
        return response.json()




