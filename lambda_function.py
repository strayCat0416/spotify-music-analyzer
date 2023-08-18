import json
import os
import requests
import logging
import spotipy
from spotipy.oauth2 import SpotifyClientCredentials
from create_artist_analysis_service import CreateArtistAnalysisService

logger = logging.getLogger()
logger.setLevel(logging.INFO)

# LINE API関連の定数
LINE_API_ENDPOINT = "https://api.line.me/v2/bot/message/push"
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['LINE_ACCESS_TOKEN']}"
}

def lambda_handler(event, context):
    try:
        request_body = json.loads(event["body"])
        user_id = request_body["events"][0]["source"]["userId"]  # ユーザーIDの取得
        artist_id = request_body["events"][0]["message"]["text"]
    
        # Spotify APIの認証とアーティスト情報の取得
        try:
            spotify_api = setup_spotify_api()
            send_line_push(user_id,"Spotifyとの疎通に成功しました。")
        except SpotifyOauthError:
            send_line_push(user_id,"Spotifyとの疎通に失敗しました。")
            return {
                "statusCode": 200,
                "body": "Failed to connect with Spotify"
            }
        
        artist_info = spotify_api.artist(artist_id)
        
        if "error" in artist_info:
            error_message = artist_info["error"]["message"]
            send_line_push(user_id,"該当のアーティストIDの楽曲はSpotifyには存在しません。")
            return {
                "statusCode": 200,
                "body": "Failed to connect with Spotify"
            }
        send_line_push(user_id, f"{artist_info['name']}の楽曲情報を取得しています... しばらくお待ちください.")
        
        analysis_data = create_artist_analysis(artist_id)
        message = create_message(analysis_data)
        send_line_push(user_id, message)
        
        return {
            "statusCode": 200,
            "body": "Success"
        }
    except Exception as e:
        send_line_push(user_id,f"不明なエラーが発生しました。{e}")
        raise(e)


def setup_spotify_api():
    spotify_client_id = os.environ.get('SPOTIFY_CLIENT_ID')
    spotify_client_secret = os.environ.get('SPOTIFY_CLIENT_SECRET')
    client_credentials_manager = SpotifyClientCredentials(client_id=spotify_client_id, client_secret=spotify_client_secret)
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


def create_artist_analysis(artist_id):
    service = CreateArtistAnalysisService()
    return service.create_artist_analysis_data(artist_id=artist_id)

def create_message(analysis_data):
    message = "アーティスト分析データ:\n"
    for index, row in analysis_data.iterrows():
        message += f"楽曲名: {row['楽曲名']}\n"
        message += f"アーティスト名: {row['アーティスト名']}\n"
        # ... 他のデータの表示 ...
        message += "----------\n"
    return message

def send_line_push(user_id, message):
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(LINE_API_ENDPOINT, json=payload, headers=LINE_HEADERS)
    logger.info("Push Response status code: %s", response.status_code)
    logger.info("Push Response text: %s", response.text)


