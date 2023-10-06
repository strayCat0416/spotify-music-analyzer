import json
import os
import requests
import logging
import spotipy
import boto3
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

# S3関連の定数
BUCKET_NAME = 'your-s3-bucket-name'

def handler(event, context):
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
        
        # アーティストの分析データをCSVとしてS3にアップロード
        csv_content = analysis_data.to_csv(index=False, encoding='utf-8')  # pandas DataFrameをCSV文字列に変換
        file_name = f"{artist_id}_analysis.csv"
        csv_url = upload_to_s3(file_name, csv_content.encode('utf-8'))

        # ユーザーにCSVのダウンロードリンクを送信
        send_line_push(user_id, f"分析データはこちらのリンクからダウンロードできます: {csv_url}")
        
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

def upload_to_s3(file_name, file_content):
    s3 = boto3.client('s3')
    s3.put_object(Bucket=BUCKET_NAME, Key=file_name, Body=file_content, ACL='public-read')
    url = f"https://s3.amazonaws.com/{BUCKET_NAME}/{file_name}"
    return url

def send_line_push(user_id, message):
    payload = {
        "to": user_id,
        "messages": [{"type": "text", "text": message}]
    }
    response = requests.post(LINE_API_ENDPOINT, json=payload, headers=LINE_HEADERS)
    logger.info("Push Response status code: %s", response.status_code)
    logger.info("Push Response text: %s", response.text)
