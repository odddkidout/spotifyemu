import time
from multiprocessing import Manager


class Stats:
    def __init__(self, threads,songs):
        manager = Manager()
        songmanager = Manager()
        self.threads = threads
        self.songs = songs
        self.runtime = 0
        self.thread = manager.dict({i+1: manager.dict({'logins': 0, 'streams': 0, 'status': 'Not started'}) for i in range(threads)})
        self.song_stats = songmanager.dict({song['uri']: manager.dict({'name':song['context']['track_name'],'streams': 0, 'image': song['image']}) for song in songs})
        
    
    def get_stats(self):
        runtime_seconds = 0 if self.runtime == 0 else time.time() - self.runtime
        runtime_formatted = time.strftime('%H:%M:%S', time.gmtime(runtime_seconds))

        total_logins = sum(thread['logins'] for thread in self.thread.values())
        total_streams = sum(thread['streams'] for thread in self.thread.values())

        streams_per_hour_per_thread = 0
        streams_per_hour = 0
        streams_per_day = 0
        if runtime_seconds > 0:
            hours = runtime_seconds / 3600
            days = hours / 24
            streams_per_hour = round(total_streams / hours)
            streams_per_hour_per_thread = round(streams_per_hour / self.threads)
            streams_per_day = round(total_streams / days)
            

        return {
            'threads': self.threads,
            'runtime': runtime_formatted,
            'logins': format(total_logins, ',').replace(',', '.'),
            'streams': format(total_streams, ',').replace(',', '.'),
            'streams_per_hour_per_thread': format(streams_per_hour_per_thread, ',').replace(',', '.'),
            'streams_per_hour': format(streams_per_hour, ',').replace(',', '.'),
            'streams_per_day': format(streams_per_day, ',').replace(',', '.'),
            'thread_stats': {k: dict(v) for k, v in self.thread.items()},
            'song_stats': {k: dict(v) for k, v in self.song_stats.items()},
            
        }

    def increment_login(self, threadID):
        self.thread[threadID]['logins'] += 1
    
    def increment_stream(self, threadID):
        self.thread[threadID]['streams'] += 1
    
    def update_status(self, threadID, status):
        self.thread[threadID]['status'] = status

    def increment_stream_song(self, songid):

        self.song_stats[songid]['streams'] += 1

    def get_stream_song(self, songid):
        data = {k: dict(v) for k, v in self.song_stats.items()}
        """print(data)
        print(data[songid]['streams'])"""
        return data[songid]['streams']
        #return self.song_stats[songid]['streams']    
    