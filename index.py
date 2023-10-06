import json
import os
import requests
import logging
import spotipy
import boto3
from spotipy.oauth2 import SpotifyClientCredentials
from create_artist_analysis_service import CreateArtistAnalysisService

# ログレベルの設定
logger = logging.getLogger()
logger.setLevel(logging.INFO)

# LINE API関連の定数
LINE_API_ENDPOINT = "https://api.line.me/v2/bot/message/push"
LINE_HEADERS = {
    "Content-Type": "application/json",
    "Authorization": f"Bearer {os.environ['LINE_ACCESS_TOKEN']}",
}


# Lambda関数のエントリーポイント
def handler(event, context):
    try:
        # リクエストボディの取得
        request_body = json.loads(event["body"])
        user_id = request_body["events"][0]["source"]["userId"]  # ユーザーIDの取得
        artist_id = request_body["events"][0]["message"]["text"]

        # Spotify APIの認証とアーティスト情報の取得
        try:
            spotify_api = setup_spotify_api()
            message = "Spotifyとの疎通に成功しました。"
            send_line_push(user_id, message)
        except SpotifyOauthError:
            message = "Spotifyとの疎通に失敗しました。"
            send_line_push(
                user_id,
            )
            return {"statusCode": 400, "body": message}

        # アーティスト情報の取得
        artist_info = spotify_api.artist(artist_id)

        # アーティスト情報が存在しない場合の処理
        if "error" in artist_info:
            message = "該当のアーティストIDの楽曲はSpotifyには存在しません。"
            send_line_push(user_id, message)
            return {"statusCode": 400, "body": message}

        # ユーザーに対して処理中であることを通知
        send_line_push(user_id, f"{artist_info['name']}の楽曲情報を取得しています... しばらくお待ちください.")

        # アーティストの分析データを作成
        analysis_data = create_artist_analysis(artist_id)

        # アーティストの分析データをCSVとしてS3にアップロード
        csv_content = analysis_data.to_csv(
            index=False, encoding="utf-8"
        )  # pandas DataFrameをCSV文字列に変換
        file_name = f"{artist_id}_analysis.csv"
        csv_url = upload_to_s3(file_name, csv_content.encode("utf-8"))

        # ユーザーにCSVのダウンロードリンクを送信
        send_line_push(user_id, f"分析データはこちらのリンクからダウンロードできます: {csv_url}")

        return {"statusCode": 200, "body": "処理が完了しました。"}
    except Exception as e:
        # エラーが発生した場合の処理
        send_line_push(user_id, f"不明なエラーが発生しました。{e}")
        raise (e)


# Spotify APIの認証
def setup_spotify_api():
    spotify_client_id = os.environ.get("SPOTIFY_CLIENT_ID")
    spotify_client_secret = os.environ.get("SPOTIFY_CLIENT_SECRET")
    client_credentials_manager = SpotifyClientCredentials(
        client_id=spotify_client_id, client_secret=spotify_client_secret
    )
    return spotipy.Spotify(client_credentials_manager=client_credentials_manager)


# アーティストの分析データを作成
def create_artist_analysis(artist_id):
    service = CreateArtistAnalysisService()
    return service.create_artist_analysis_data(artist_id=artist_id)


# S3にファイルをアップロード
def upload_to_s3(file_name, file_content):
    s3 = boto3.client("s3")
    BUCKET_NAME = os.environ["AWS_S3_BUCKET"]
    s3.put_object(
        Bucket=BUCKET_NAME,
        Key=file_name,
        Body=file_content,
        ACL="public-read",
    )
    url = f"https://s3.amazonaws.com/{BUCKET_NAME}/{file_name}"
    return url


# LINE APIを使用してユーザーにメッセージを送信
def send_line_push(user_id, message):
    payload = {"to": user_id, "messages": [{"type": "text", "text": message}]}
    response = requests.post(LINE_API_ENDPOINT, json=payload, headers=LINE_HEADERS)
    logger.info("Push Response status code: %s", response.status_code)
    logger.info("Push Response text: %s", response.text)
