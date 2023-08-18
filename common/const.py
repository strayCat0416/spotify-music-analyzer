class ConsMeta(type):
    """
    Constの上書きを防ぐためのメタクラスです。
    """
    def __setattr__(self, name, value):
        if name in self.__dict__:
            raise ValueError(f'Can\'t rebind const  ({name})')
        else:
            self.__setattr__(name, value)
        
class Const(metaclass=ConsMeta):
    PITCH_CLASS = {0:'C', 1:'C#', 2:'D', 3:'D#', 4:'E', 5:'F',
                6:'F#', 7:'G', 8:'G#', 9:'A', 10:'A#', 11:'B'}

    MODE_DEC = {0:'minor', 1:'major'}

    CHART_SHEET = 'ヒットチャート分析'
    CHART_COLUMN_DROP_LIST=['id','primary_color','track','added_at','added_by','is_local','video_thumbnail','instrumentalness','liveness','type','uri','track_href','analysis_url',"mode",'speechiness']
    CHART_COLUMN_NAME_MAPPING = {
        'name': '楽曲名',
        'artist': 'アーティスト名',
        'album_name': 'アルバム名',
        'duration_ms': '再生時間',
        'release_date': 'リリース日',
        'acousticness'  : 'アコースティックさ',
        'loudness': '全体的な音量',
        'speechiness': '話し言葉の割合',
        'danceability': '踊りやすさ',
        'energy': 'エネルギッシュさ',
        'valence': 'ポジティブさ',
        'key': 'キー',
        'tempo': 'BPM',
        'time_signature': '拍子',
        'duration_ms': '再生時間',
    }

    ARTIST_ANALYSIS_SHEET = 'アーティスト楽曲データ分析'
    ARTIST_ANALYSIS_DROP_LIST=['instrumentalness','liveness','analysis_url',"mode",'speechiness','track_uri','uri','track_href','type']
    ARTIST_ANALYSIS_COLUMN_NAME_MAPPING = {
        'id': 'Spotify上の楽曲ID',
        'name': '楽曲名',
        'album_name': 'アルバム名',
        'artist': 'アーティスト名',
        'popularity': '再生数+最近よく聴かれてる度',
        'release_date': 'リリース日',
        'duration_ms': '再生時間',
        'acousticness'  : 'アコースティックさ',
        'loudness': '全体的な音量',
        'danceability': '踊りやすさ',
        'energy': 'エネルギッシュさ',
        'valence': 'ポジティブさ',
        'key': 'キー',
        'tempo': 'BPM',
        'time_signature': '拍子',
        'duration_ms': '再生時間',
    }
    ARTIST_ANALYSIS_COLUMN_ORDER = ['楽曲名','アーティスト名','アルバム名','再生数+最近よく聴かれてる度','リリース日','全体的な音量','キー','BPM','拍子','再生時間','アコースティックさ','踊りやすさ','エネルギッシュさ','ポジティブさ','Spotify上の楽曲ID']


    WEEKLY_TOP_PLAYLIST_IDS_DICT = dict(
    Global='37i9dQZEVXbNG2KDcFcKOF',  # グローバル
    Japan='37i9dQZEVXbKqiTGXuCOsB',  # 日本
    Korea='37i9dQZEVXbJZGli0rRP3r',  # 韓国
    America='37i9dQZEVXbLp5XoPON0wI',  # アメリカ
    Italy='37i9dQZEVXbJUPkgaWZcWG',  # イタリア
    India='37i9dQZEVXbMWDif5SCBJq',  # インド
    Brazil='37i9dQZEVXbKzoK95AbRy9',  # ブラジル
)