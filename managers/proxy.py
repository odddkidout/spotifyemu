from multiprocessing import Manager


class ProxyManager:
    def __init__(self, config):
        self.configured = True
        manager = Manager()
        if config.use_proxy:
            self.stream = manager.Queue()
            self._load(config.stream, self.stream)
        if config.generate:
            self.gen = manager.Queue()
            self._load(config.gen, self.gen)

    def _load(self, filename, queue):
        with open(filename, 'r') as file:
            proxies = [line.strip() for line in file]
        if proxies == []:
            self.configured = False
            return
        for proxy in proxies:
            queue.put(proxy)

    def get_stream(self):
        proxy = self.stream.get()
        self.stream.put(proxy)
        return proxy

    def get_gen_proxy(self):
        proxy = self.gen.get()
        self.gen.put(proxy)
        return proxy