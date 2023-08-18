import os
import pandas as pd

import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from common.const import Const


class CreateArtistAnalysisService:
    def __init__(self):
        """
        Spotify APIの認証フローの設定するコンストラクタです。
        """
        client_id = os.environ.get('SPOTIFY_CLIENT_ID')
        client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
        client_credentials_manager = SpotifyClientCredentials(
            client_id=client_id, client_secret=client_secret
        )
        self.spotify = spotipy.Spotify(
            client_credentials_manager=client_credentials_manager, language='ja'
        )

    def create_artist_analysis_data(self, artist_id):
        """
        Spotifyからアーティストのデータを取得し、CSVファイルに書き込む関数です。
        params:artist_id:Spotify上のアーティストID
        return:None
        """
        try:
            all_tracks = self.extract_artist_tracks(artist_id)

            artist_analysis_df = pd.DataFrame(all_tracks)

            # リリース日降順でソート
            artist_analysis_df = artist_analysis_df.sort_values('release_date', ascending=False)

            chart_audio_features_df = pd.DataFrame()
            for i, row in artist_analysis_df.iterrows():
                # artist_analysis_dfのtrack_uriを元にaudio_featuresを取得
                audio_features = self.spotify.audio_features(row['id'])
                audio_features = audio_features[0]
                audio_features_df = pd.DataFrame(audio_features, index=[0])
                chart_audio_features_df = chart_audio_features_df._append(audio_features_df)

            artist_analysis_df = pd.merge(artist_analysis_df, chart_audio_features_df, on='id')

            # データの整形
            artist_analysis_df['key'] = artist_analysis_df['key'].map(Const.PITCH_CLASS) + artist_analysis_df['mode'].map(Const.MODE_DEC)
            artist_analysis_df['tempo'] = artist_analysis_df['tempo'].astype(int).astype(str) + 'bpm'
            artist_analysis_df['duration_ms'] = (artist_analysis_df['duration_ms'] // 1000 // 60).astype(int).astype(str) + ':' + (
                (artist_analysis_df['duration_ms'] // 1000) % 60).astype(int).astype(str).str.zfill(2)
            artist_analysis_df['time_signature'] = artist_analysis_df['time_signature'].astype(int).astype(str) + '/4拍子'
            artist_analysis_df['danceability'] = (artist_analysis_df['danceability'] * 100).astype(int).astype(str) + '%'
            artist_analysis_df['energy'] = (artist_analysis_df['energy'] * 100).astype(int).astype(str) + '%'
            artist_analysis_df['valence'] = (artist_analysis_df['valence'] * 100).astype(int).astype(str) + '%'
            artist_analysis_df['popularity'] = artist_analysis_df['popularity'].astype(int).astype(str) + '%'
            artist_analysis_df['release_date'] = pd.to_datetime(artist_analysis_df['release_date']).dt.strftime('%Y年%m月%d日')
            artist_analysis_df['acousticness'] = (artist_analysis_df['acousticness'] * 100).astype(int).astype(str) + '%'
            artist_analysis_df['speechiness'] = (artist_analysis_df['speechiness'] * 100).astype(int).astype(str) + '%'
            artist_analysis_df['loudness'] = artist_analysis_df['loudness'].astype(int).astype(str) + 'dB'
            artist_analysis_df = artist_analysis_df.rename(columns=Const.ARTIST_ANALYSIS_COLUMN_NAME_MAPPING)
            artist_analysis_df = artist_analysis_df.drop(columns=Const.ARTIST_ANALYSIS_DROP_LIST).reindex(columns=Const.ARTIST_ANALYSIS_COLUMN_ORDER)

            # 楽曲名とアーティスト名が全く重複している場合は収録されているアルバムが違うだけで同じ曲なので、片方を削除
            artist_analysis_df = artist_analysis_df.drop_duplicates(subset=['アーティスト名', '楽曲名'], keep='first')
            
            return  artist_analysis_df

        except Exception as e:
            print(e)
            raise e

    def extract_artist_tracks(self, artist_id):
        """
        アーティストIDに対応するトラックデータをSpotifyから取得し、
        そのアーティストが実際に参加しているトラックのみを抽出するメソッドです。
        params:artist_id: アーティストID
        return:track_list: アーティストが参加しているトラックデータ
        """
        try:
            album_types = ['album', 'single', 'appears_on', 'compilation']
            track_list = []

            for album_type in album_types:
                tracks_data = self.get_artist_tracks(artist_id, album_type)

                for track_data in tracks_data:
                    # アーティストIDの取得
                    artist_ids = [artist['id'] for artist in track_data['artists']]
                    # アーティストIDが一致する場合はリストに追加
                    if artist_id in artist_ids:
                        # artistには複数のアーティストが含まれる場合があるので、artistの数分コンマ(,)で結合
                        artist_names = ','.join(artist['name'] for artist in track_data['artists'])
                        track_list.append({
                            'id': track_data['id'],
                            'artist': artist_names,
                            'name': track_data['name'],
                            'album_name': track_data['album_name'],
                            'track_uri': track_data['uri'],
                            'popularity': track_data['popularity'],
                            'release_date': track_data['release_date']
                        })

            return track_list
        
        except Exception as e:
            print(e)
            raise e

    def get_artist_tracks(self, artist_id, album_type):
        """
        アーティストのアルバムからトラックデータを取得する関数です。
        params:artist_id: アーティストID
        params:album_type: アルバムの種類(album, single, appears_on, compilation)
        return:tracks: トラックデータ
        """
        try:
            tracks = []
            offset = 0
            limit = 50

            while True:
                albums = self.spotify.artist_albums(artist_id, album_type=album_type, limit=limit, offset=offset)['items']
                
                if len(albums) == 0:
                    break

                for album in albums:
                    album_id = album['id']
                    album_name = album['name']
                    album_tracks = self.spotify.album_tracks(album_id)['items']

                    for track in album_tracks:
                        track_info = self.spotify.track(track['id'])
                        track['album_name'] = album_name
                        track['popularity'] = track_info['popularity']
                        track['release_date'] = track_info['album']['release_date']

                    tracks.extend(album_tracks)

                offset += limit

            return tracks
        
        except Exception as e:
            print(e)
            raise e