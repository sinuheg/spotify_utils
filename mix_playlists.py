import os
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials, SpotifyOAuth

'''
Make sure to add the following env variables
export SPOTIPY_CLIENT_ID='asdf'
export SPOTIPY_CLIENT_SECRET='asdf'
export SPOTIPY_REDIRECT_URI='https://asdf.com'
export SPOTIPY_MIXER_PLAYLIST_ID='asdf'
export SPOTIPY_RELEASE_RADAR_PLAYLIST_ID='asdf'
'''
scope = "user-library-read,playlist-read-private,playlist-modify-private"

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(scope=scope))

def get_playlist_by_id(playlist_id):
    playlist = sp.playlist(playlist_id)
    print(playlist['name'],'owner', playlist['owner']['display_name'], len(playlist['tracks']['items']))
    
    return playlist

def get_playlist_by_search(query):
    results = sp.search(q=query, type='playlist')
    items = results['playlists']['items']

    playlist_id = items[0]['id']

    playlist = sp.playlist(playlist_id)
    print(playlist['name'],'owner', playlist['owner']['display_name'], len(playlist['tracks']['items']))
    
    return playlist

def get_liked_songs_extended_limit(upper_limit):
    remain = upper_limit
    offset = 0
    page_size = 50
    lkd_songs = {
        "items": []
    }
    while remain > page_size:
        page = sp.current_user_saved_tracks(limit=page_size, offset=offset)
        lkd_songs['items'].extend(page['items'])
        offset += page_size
        remain -= page_size
    page = sp.current_user_saved_tracks(limit=remain, offset=offset)
    lkd_songs['items'].extend(page['items'])

    return lkd_songs


def remove_all_playlist_items(playlist):
    item_uris = []
    items = playlist['tracks']['items']
    results = playlist['tracks']
    while results['next']:
        results = sp.next(results)
        items.extend(results['items'])

    for item in items:
        item_uris.append(item['track']['uri'])
    print('to remove', len(item_uris))

    remove_index = 0
    max_delete_count = 100

    while len(item_uris) - remove_index > 100:
        sp.playlist_remove_all_occurrences_of_items(playlist['id'], item_uris[remove_index:(remove_index + max_delete_count)])
        remove_index += max_delete_count

    sp.playlist_remove_all_occurrences_of_items(playlist['id'], item_uris[remove_index:])

def mix_playlists_and_add(source_playlists, liked_songs, target_playlist):
    max_item_count = 0
    for source_playlist in source_playlists:

        max_item_count = max(len(source_playlist['tracks']['items']), max_item_count)
    
    items_to_add = []
    liked_counter = 0
    for i in range(max_item_count):
        for source_playlist in source_playlists:
            if i < len(source_playlist['tracks']['items']):
                items_to_add.append(source_playlist['tracks']['items'][i]['track']['uri'])
            if liked_counter < len(liked_songs['items']):
                items_to_add.append(liked_songs['items'][liked_counter]['track']['uri'])
                liked_counter += 1
    print('items to add', len(items_to_add))
    playlist_add_items_no_limit(target_playlist['id'], items_to_add)

def playlist_add_items_no_limit(target_playlist_id, items_to_add):
    add_limit = 100
    insert_index = 0
    while len(items_to_add) - insert_index > add_limit:
        sp.playlist_add_items(target_playlist_id, items_to_add[insert_index:(insert_index + add_limit)])
        insert_index += add_limit
    sp.playlist_add_items(target_playlist_id, items_to_add[insert_index:])
    



discover_playlist = get_playlist_by_search('Discover+Weekly')
release_playlist = get_playlist_by_id(os.getenv('SPOTIPY_RELEASE_RADAR_PLAYLIST_ID')) # Release Radar playlist
mixer_playlist = get_playlist_by_id(os.getenv('SPOTIPY_MIXER_PLAYLIST_ID')) # Mixer Playlist
remove_all_playlist_items(mixer_playlist)
lkd_songs = get_liked_songs_extended_limit(70)
mix_playlists_and_add([discover_playlist,release_playlist], lkd_songs, mixer_playlist)