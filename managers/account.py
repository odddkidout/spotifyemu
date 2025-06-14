import random
from multiprocessing import Manager


class AccountManager:
    def __init__(self, config):
        self.configured = True
        if not config.generate:
            manager = Manager()
            self.accounts = manager.Queue()
            self._load(config.accounts)

    def _load(self, filename):
        with open(filename, 'r') as file:
            accounts = [line.strip() for line in file]
        if accounts == []:
            self.configured = False
            return
        random.shuffle(accounts)
        
        for account in accounts:
            self.accounts.put(account)

    def get(self):
        return self.accounts.get()

    def release(self, account):
        if account:
            self.accounts.put(account)