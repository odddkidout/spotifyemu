import time
from multiprocessing import Process

from managers.config import ConfigManager
from managers.account import AccountManager
from managers.proxy import ProxyManager
from managers.thread import BotThread
from managers.stats import Stats
from managers.song import SongManager

def run_bot_thread(thread):
    thread.run()

class BotManager:
    def __init__(self):
        self.config = ConfigManager()
        self.account = AccountManager(self.config)
        self.proxy = ProxyManager(self.config)
        self.songs_manager = SongManager(self.config)
        self.stats = Stats(self.config.threads,self.songs_manager.songs)
        self.threads = [BotThread(i+1, self.config, self.account, self.proxy, self.stats,self.songs_manager) for i in range(self.config.threads)]
        self.processes = []

    def is_configured(self):
        return self.account.configured and self.proxy.configured
    
    def start(self):
        self.stats.runtime = time.time()
        for thread in self.threads:
            p = Process(target=run_bot_thread, args=(thread,))
            p.start()
            self.processes.append(p)
            time.sleep(self.config.delay)

    def stop(self):
        for process in self.processes:
            process.terminate()
