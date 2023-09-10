import redis
import pickle
from functools import lru_cache 
from PlayerInterface import FormalPlayerInterface, NowPlayingItem


class Datastore():
    def __init__(self):
        self.now_playing: NowPlayingItem = None
        self.current_player: FormalPlayerInterface = None
        self.r = redis.Redis(host='localhost', port=6379)

    def getPlaylistCount(self):
        return len(self.r.keys("playlist-index:*"))

    def getSavedTrackCount(self):
        return len(self.r.keys("track:*"))

    def getArtistCount(self):
        return len(self.r.keys("artist:*"))

    def getAlbumCount(self):
        return len(self.r.keys("album-index:*"))

    def getNewReleasesCount(self):
        return len(self.r.keys("nr-index:*"))

    def getShowsCount(self):
        return len(self.r.keys("show-index:*"))

    def setShow(self, show, episodes, index = -1):
        show_id = show.uri.split(":")[-1]
        self.r.set("show-uri:"+str(show_id), pickle.dumps(show))
        self.r.set("show-episodes:"+str(show_id), pickle.dumps(episodes))
        if(index > -1):
            self.r.set("show-index:"+str(index), show_id)

    def setNewRelease(self, album, tracks, index = -1):
        album_id = album.uri.split(":")[-1]
        self.r.set("nr-uri:"+str(album_id), pickle.dumps(album))
        self.r.set("playlist-tracks:"+str(album_id), pickle.dumps(tracks))
        if (index > -1):
            self.r.set("nr-index:"+str(index), album_id)

    def setAlbum(self, album, tracks, index = -1):
        album_id = album.uri.split(":")[-1]
        self.r.set("album-uri:"+str(album_id), pickle.dumps(album))
        self.r.set("playlist-tracks:"+str(album_id), pickle.dumps(tracks))
        if (index > -1):
            self.r.set("album-index:"+str(index), album_id)

    def setPlaylist(self, playlist, tracks, index = -1):
        playlist_id = playlist.uri.split(":")[-1]
        self.r.set("playlist-uri:"+str(playlist_id), pickle.dumps(playlist))
        self.r.set("playlist-tracks:"+str(playlist_id), pickle.dumps(tracks))
        if (index > -1):
            self.r.set("playlist-index:"+str(index), playlist_id)

    def setArtist(self, index, artist):
        self.r.set("artist:"+str(index), pickle.dumps(artist))
    
    @lru_cache(maxsize=50)
    def getShow(self, index):
        show_uri = self.r.get("show-index:"+str(index))
        if(show_uri is None):
            return None
        return self.getShowUri(show_uri.decode('utf-8'))

    @lru_cache(maxsize=50)
    def getPlaylist(self, index):
        playlist_uri = self.r.get("playlist-index:"+str(index))
        if (playlist_uri is None):
            return None
        return self.getPlaylistUri(playlist_uri.decode('utf-8'))

    def getShowEpisodes(self, show_uri):
        show_id = show_uri.split(":")[-1]
        pickled_sh = self.r.get("show-episodes:"+str(show_id))
        if(pickled_sh is None):
            return None
        return pickle.loads(pickled_sh)

    def getPlaylistTracks(self, playlist_uri):
        playlist_id = playlist_uri.split(":")[-1]
        pickled_pl = self.r.get("playlist-tracks:"+str(playlist_id))
        if (pickled_pl is None):
            return None
        return pickle.loads(pickled_pl)

    @lru_cache(maxsize=50)
    def getAlbum(self, index):
        album_uri = self.r.get("album-index:"+str(index))
        if (album_uri is None):
            return None
        return self.getAlbumUri(album_uri.decode('utf-8'))

    @lru_cache(maxsize=50)
    def getNewRelease(self, index):
        album_uri = self.r.get("nr-index:"+str(index))
        if (album_uri is None):
            return None
        return self.getNewReleaseUri(album_uri.decode('utf-8'))

    @lru_cache(maxsize=50)
    def getShowUri(self, uri):
        show_id = str(uri).split(":")[-1]
        pickled_sh = self.r.get("show-uri:"+str(show_id))
        if(not pickled_sh):
            return None
        return pickle.loads(pickled_sh)

    @lru_cache(maxsize=50)
    def getPlaylistUri(self, uri):
        playlist_id = str(uri).split(":")[-1]
        pickled_pl = self.r.get("playlist-uri:"+str(playlist_id))
        if (not pickled_pl):
            return None
        return pickle.loads(pickled_pl)

    @lru_cache(maxsize=50)
    def getAlbumUri(self, uri):
        album_id = str(uri).split(":")[-1]
        pickled_pl = self.r.get("album-uri:"+str(album_id))
        if (not pickled_pl):
            return None
        return pickle.loads(pickled_pl)

    @lru_cache(maxsize=50)
    def getNewReleaseUri(self, uri):
        album_id = str(uri).split(":")[-1]
        pickled_pl = self.r.get("nr-uri:"+str(album_id))
        if (not pickled_pl):
            return None
        return pickle.loads(pickled_pl)

    def getArtist(self, index):
        pickled_pl = self.r.get("artist:"+str(index))
        return pickle.loads(pickled_pl)

    def setSavedTrack(self, index, track):
        self.r.set("track:"+str(index), pickle.dumps(track))

    def getSavedTrack(self, index):
        pickled_pl = self.r.get("track:"+str(index))
        return pickle.loads(pickled_pl)

    def setUserDevice(self, device):
        print("device:"+ str(device.id))
        self.r.set("device:"+ str(device.id), pickle.dumps(device))

    def getSavedDevice(self, id):
        return self._getSavedItem("device:"+id)

    def _getSavedItem(self, id):
        pickled_device = self.r.get(id)
        return pickle.loads(pickled_device)

    def getAllSavedDevices(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("device:*")))

    def getAllSavedPlaylists(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("playlist-uri:*")))

    def getAllSavedAlbums(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("album-uri:*")))

    def getAllNewReleases(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("nr-uri:*")))

    def getAllSavedShows(self):
        return list(map(lambda idx: self._getSavedItem(idx), self.r.keys("show-uri:*")))

    def clearDevices(self):
        devices = self.r.keys("device:*")
        if len(devices) == 0:
            return
        self.r.delete(*devices)

    def clear(self):
        self.r.flushdb()
