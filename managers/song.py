import json
import random
import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials

client_credentials_manager = SpotifyClientCredentials(
    client_id="ede736c5d04f4d9298779f80f52e9284",
    client_secret="904122bbe1e04f759b60ba31e13c8cf2",
)
sp = spotipy.Spotify(client_credentials_manager=client_credentials_manager)


class SongManager:
    def __init__(self, config):
        self.songs = []
        self._load(config.songs)
        self.configured = True


    def _load(self, filename):
        with open(filename, 'r') as file:
            songs = json.load(file)
        if songs == []:
            self.configured = False
            return
        random.shuffle(songs)
        for song in songs:
            self._process(song)
        
    def trackdetails(self, track):
        if os.path.exists("./tracks/"+track+".json"):
            with open("./tracks/"+track+".json", 'r') as file:
                text = json.load(file)
                return text
        else:
            trackdetails = sp.track(track)
            with open("./tracks/"+track+".json", 'w') as file:
                text = json.dump(trackdetails,file)
            return trackdetails    
        
    def _process(self, song):
        if song['type'] == 'track':
            track = self.trackdetails(song['id'])
            self.songs.append({
                'uri': encode(song['id']),
                'streams' : song['streams'], 
                'plays': song['ppa'],
                'full_play': song['full_play'],
                'image' : track['album']['images'][0]['url'],
                'context': {
                    'artist_name': track['artists'][0]['name'],
                    'track_name': track['name'],
                    'artist_uri': track['artists'][0]['uri'],
                    'album_uri': track['album']['uri'],
                    'extra_playlist_uri': "spotify:playlist:" + song['extra_playlist_id'] if song['extra_playlist_id'] else None
                },
                'chance': song['context'],
                "like": song['like'],
                "like_album": song['like_album'],
                "like_playlist": song['like_playlist'],
                "follow_artist": song['follow_artist'],
                'duration': track['duration_ms'],
            })
        elif song['type'] == 'playlist':
            playlist = sp.playlist(song['id'])
            playlist_name = playlist['name']
            playlist_uri = playlist['uri']
            playlist_tracks = playlist['tracks']['items']
            random_tracks = random.sample(playlist_tracks, song['ppa'])
            for track in random_tracks:
                track = track['track']
                self.songs.append({
                    'uri': encode(track['id']),
                    'plays': 1,
                    'full_play': song['full_play'],
                    'context': {
                        'artist_name': track['artists'][0]['name'],
                        'track_name': track['name'],
                        'playlist_name': playlist_name,
                        'artist_uri': track['artists'][0]['uri'],
                        'album_uri': track['album']['uri'],
                        'playlist_uri': playlist_uri,
                        'extra_playlist_uri': "spotify:playlist:" + song['extra_playlist_id'] if song['extra_playlist_id'] else None
                    },
                    'chance': song['context'],
                    "like": song['like'],
                    "like_album": song['like_album'],
                    "like_playlist": song['like_playlist'],
                    "follow_artist": song['follow_artist'],
                    'duration': track['duration_ms'],
                    })

        

    def _old_process(self, uri):
        track = self.sp.track(uri)
        artist = track['artists'][0]['uri']
        album = track['album']['uri']
        duration = track['duration_ms']
        encoded_uri = encode(uri)
        return {
            'uri': encoded_uri,
            'artist': artist,
            'album': album,
            'duration': duration
        }

def encode(uri):
    s = "0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
    ret = 0
    for i in range(len(uri) - 1, -1, -1):
        ret = ret + s.index(uri[i]) * (62 ** (len(uri) - i - 1))
    encoded_uri = f"{ret:0x}"
    return encoded_uri