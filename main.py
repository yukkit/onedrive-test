import logging
import os
from typing import Optional

from flask import Flask, Response, jsonify, request

from client import Client

# 初始化Flask应用
app = Flask(__name__)
app.config["JSON_AS_ASCII"] = False
app.secret_key = os.urandom(24)

client_secret = os.getenv("CLIENT_SECRET")

# 配置（替换为你的实际配置）
CONFIG = {
    "client_id": "5846bd51-d602-4afa-9d54-8d0f3ddaad2e",  # 与前端一致
    "client_secret": client_secret,
    "graph_api_endpoint": "https://graph.microsoft.com/v1.0/me/drive/root/children",
}

client = Client(client_id=CONFIG["client_id"], client_secret=CONFIG["client_secret"])


# 跨域配置（内网前端访问后端需跨域）
@app.after_request
def after_request(response):
    response.headers["Access-Control-Allow-Origin"] = "*"
    response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
    response.headers["Access-Control-Allow-Headers"] = "Content-Type"
    return response


@app.route("/onedrive/oauthurl", methods=["GET"])
def oauth_url():
    try:
        if (redirect_uri := request.args.get("redirect_uri")) is None:
            return jsonify({"success": False, "message": "缺少redirect_uri参数"}), 400

        scope = request.args.get("scope")
        scope_list = scope.split(" ") if scope else []

        authorization_url = client.oauth_provider.oauth_get_authorization_url(
            redirect_uri=redirect_uri, scopes=scope_list
        )
        print(f"Generated authorization URL: {authorization_url}")
        return jsonify({"success": True, "authorization_url": authorization_url})
    except Exception as e:
        return jsonify({"success": False, "message": f"服务器错误：{str(e)}"}), 500


# 1. 兑换令牌接口
@app.route("/onedrive/token", methods=["POST", "OPTIONS"])
async def exchange_token():
    if request.method == "OPTIONS":
        return jsonify({"success": True}), 200

    # 获取前端参数
    data = request.get_json()
    code = data.get("code")
    redirect_uri = data.get("redirect_uri")

    try:
        client.oauth_provider.oauth_get_credentials(
            redirect_uri=redirect_uri,
            code=code,
        )
        return jsonify({"success": True, "message": "令牌兑换成功，已加密存储"})
    except Exception as e:
        logging.error(f"Error exchanging token: {e}")
        return jsonify({"success": False, "message": f"兑换令牌失败：{str(e)}"}), 400


async def list_children(
    client, drive_id: Optional[str] = "me", drive_item_id: str = "root"
):
    # 1) 先获取 drive 信息
    if drive_id is None:
        if drive := await client.me.drive.get():
            drive_id = drive.id

    if not drive_id:
        raise Exception("未能获取到Drive ID")
    # 2) 用 drive id + root item id 拿 children
    return (
        await client.drives.by_drive_id(drive_id)
        .items.by_drive_item_id(drive_item_id)
        .children.get()
    )


async def list_followed_items(
    client,
    drive_id: Optional[str] = "me",
):
    # 1) 先获取 drive 信息
    if drive_id is None:
        if drive := await client.me.drive.get():
            drive_id = drive.id

    if drive_id is None:
        raise Exception("未能获取到Drive ID")
    # 2) 用 drive id + root item id 拿 children
    return await client.drives.by_drive_id(drive_id).following.get()


# 3. 获取OneDrive文件列表接口
@app.route("/onedrive/list", methods=["GET"])
async def get_onedrive_files():
    try:
        xclient = client.client
        children = await list_children(xclient)
        if children is None:
            return jsonify({"error": "未能获取到OneDrive文件列表"}), 500

        print("Fetched children items from OneDrive.")

        # followed_items = await list_followed_items(xclient)
        # if followed_items and followed_items.value:
        #     if children.value is None:
        #         children.value = []
        #     children.value.extend(followed_items.value)

        # print("Fetched followed items from OneDrive.")

        from kiota_serialization_json.json_serialization_writer import (
            JsonSerializationWriter,
        )

        writer = JsonSerializationWriter()
        children.serialize(writer)

        result = writer.get_serialized_content()
        print(result)

        return Response(result, content_type="application/json")
    except Exception as e:
        logging.error(f"Error fetching OneDrive files: {e}")
        return jsonify({"error": f"服务器错误：{str(e)}"}), 500


# 启动后端服务
if __name__ == "__main__":
    # 监听内网IP，无需暴露公网
    app.run(
        host="0.0.0.0",  # 后端内网IP
        port=18080,  # 后端端口
        debug=False,  # 生产环境关闭debug
        threaded=True,  # 支持多线程
    )
