import time
import random
from multiprocessing import Process, Event
import traceback
import os
from managers.song import SongManager
from managers.spotify import Spotify


debug = True


def weighted_random(chances):
    options = list(chances.keys())
    weights = list(chances.values())
    return random.choices(options, weights, k=1)[0]


class BotThread(Process):
    def __init__(self, threadID, config, account, proxy, stats,songmanager):
        # super().__init__()
        self.threadID = threadID
        self.config = config
        self.account_manager = account
        self.proxy_manager = proxy
        self.stats = stats
        self._stop_event = Event()
        self.songs_manager = songmanager
        self.session = None
        self.proxy = ""
        self.plays = 0

    def run(self):
        while sum(thread['streams'] for thread in self.stats.thread.values()) < self.config.plays and not self.stopped():
            try:
                self.bot()
            except Exception as e:
                self.account = ""
                continue
            # except MercuryClient.MercuryException:
            #     continue
            # except (OSError):
            #     continue
            except:
                if debug:
                    print(traceback.format_exc())
                    # time.sleep(100000)
                continue
            finally:
                # self.account_manager.release(self.account)
                if self.session:
                    self.session.close()
                if self.plays > 0 and self.account:
                    print("Released account: {} after {} streams.".format(self.account, self.plays))
                    self.plays = 0

    def stop(self):
        self._stop_event.set()

    def stopped(self):
        return self._stop_event.is_set()

    def bot(self):
        self.login()
        print("Login done done")
        self.stream()

    def login(self):
        
        if self.config.generate:
            self.stats.update_status(self.threadID, 'Generating account')
        else:
            self.stats.update_status(self.threadID, 'Logging in')
            self.account = self.account_manager.get()
        if self.config.use_proxy:
            self.proxy = self.proxy_manager.get_stream()
        self.session  = Spotify(self.account.split(":")[0],self.account.split(":")[1])
        if os.path.isfile('./sessions/'+self.account.split(":")[0]+".json"):
            try:
                if self.session.loginWithToken():
                    self.session.saveSession()
            except Exception as e:
                print(e)
        else:
            if self.session.LoggedIn == False:
                self.session.login()
                self.session.saveSession()
                
        if self.session.LoggedIn == False:
            print(f"Login failed {self.account}")
            self.account_manager.release(self.account)
            return False
            
        if self.session.LoggedIn == True:
            self.session.connectSocket()
            if self.session.createDevice():
                print("Device created")
            else:
                print("Device not created Premium account needed")
     
        self.username = self.session.username
        self.stats.increment_login(self.threadID)

    def stream(self):
        self.stats.update_status(self.threadID, 'Streaming')
        for song in self.songs_manager.songs:
            for play in range(song['plays']):
                if sum(thread['streams'] for thread in self.stats.thread.values()) >= self.config.plays or self.stopped():
                    return
                if self.stats.get_stream_song(song['uri']) > song['streams'] :
                    criteria = lambda doc: doc['uri'] == song['uri']
                    print(self.songs_manager.songs)
                    self.songs_manager.songs = [doc for doc in self.songs_manager.songs if not criteria(doc)]
                    print(self.songs_manager.songs)
                    print("full streams done for link")
                    break 
                
                choice = weighted_random(song['chance'])
                match choice:
                    case 'artist':
                        self.send_artist(song)
                    case 'album':
                        self.send_album(song)
                    case 'playlist':
                        self.send_playlist(song, song['context']['playlist_uri'])
                    case 'collection':
                        self.send_collection(song)
                    case 'search':
                        self.send_search(song)
                    case 'extra_playlist':
                        self.send_playlist(song, song['context']['extra_playlist_uri'])
                self.stats.increment_stream(self.threadID)
                self.stats.increment_stream_song(song['uri'])
                
                self.plays += 1
                 

    def send_artist(self, song):
        pass
        
    def send_album(self, song):
        pass

    def send_playlist(self, song, playlist):
        pass

    def send_collection(self, song):
        pass

    def send_search(self, song):
        pass