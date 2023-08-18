# AWS LambdaのPython 3.10ランタイムをベースイメージとして使用します。
FROM public.ecr.aws/lambda/python:3.10

# コンテナ内の作業ディレクトリを設定します。
WORKDIR /var/task

# 必要なPythonライブラリをインストールします。まず、requirements.txtをコンテナにコピーします。
COPY requirements.txt .
# そして、pipを使ってこれらのライブラリをインストールします。
RUN pip install --no-cache-dir -r requirements.txt

# ラムダ関数のコードと共通のモジュールをコンテナにコピーします。
COPY index.py .
COPY create_artist_analysis_service.py .
COPY common/ common/

# ラムダ関数のエントリーポイント（ハンドラ関数）を設定します。
# この例では、lambda_function.py内の`handler_function`という関数をエントリーポイントとしています。
# 必要に応じて適切なハンドラ関数名に変更してください。
CMD ["index.handler"]
