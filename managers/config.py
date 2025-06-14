import configparser

class ConfigManager:
    def __init__(self):
        config = configparser.ConfigParser()
        config.read('config.ini')

       

        # Settings
        self.threads = config.getint('settings', 'num_threads')
        self.generate = config.getboolean('settings', 'generate')
        self.delay = config.getfloat('settings', 'delay')

        # Stream
        self.use_proxy = config.getboolean('stream', 'use_proxy')
        self.plays = config.getint('stream', 'total_plays')

        # Files
        self.accounts = config.get('files', 'accounts')
        self.songs = config.get('files', 'songs')
        self.stream = config.get('files', 'stream_proxies')
        self.gen = config.get('files', 'gen_proxies')