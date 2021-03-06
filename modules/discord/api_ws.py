from ..core import *
from modules.models.api_ws import *

router = APIRouter(
    include_in_schema = True,
    tags = ["Websocket API"]
) # No arguments needed for websocket but keep for chat

bootstrap_info = {
    "versions": ["v1", "v2"],
    "endpoints": {
        "v1": {
            "chat": "/api/v1/ws/chat"
        },
        "v3": {
            "bot_realtime_stats": "/apiws/bot/rtstats"
        }
    }
}

builtins.manager = ConnectionManager()
builtins.manager_chat = ConnectionManager()

@router.get("/api/ws", response_model = Bootstrap, dependencies=[Depends(RateLimiter(times=5, minutes=1))])
async def websocket_bootstrap(request: Request):
    """
        This is the gateway for all websockets. Use this to find which route you need or whether it is available
    """
    return bootstrap_info

@router.websocket("/apiws/bot/rtstats")
async def websocket_bot_rtstats_v1(websocket: WebSocket):
    await manager.connect(websocket)
    if websocket.api_token == [] and not websocket.manager_bot:
        await manager.send_personal_message({"event": enums.APIEvents.ws_identity, "type": [enums.APIEventTypes.auth_token, enums.APIEventTypes.auth_manager_key]}, websocket)
        try:
            api_token = await websocket.receive_json()
            print("HERE")
            if api_token.get("event") != enums.APIEvents.ws_identity_res or api_token["type"] not in [enums.APIEventTypes.auth_token, enums.APIEventTypes.auth_manager_key]:
                raise TypeError
        except:
            await manager.send_personal_message({"event": enums.APIEvents.ws_kill, "type": enums.APIEventTypes.ws_invalid}, websocket)
            return await ws_close(websocket, 4004)
        match api_token["type"]:
            case enums.APIEventTypes.auth_token:
                try:
                    api_token = api_token["context"]["api_token"]
                except:
                    await manager.send_personal_message({"event": enums.APIEvents.ws_kill, "type": enums.APIEventTypes.ws_invalid}, websocket)
                if api_token is None or type(api_token) == int or type(api_token) == str:
                    await manager.send_personal_message({"event": enums.APIEvents.ws_kill, "type": enums.APIEventTypes.ws_invalid}, websocket)
                    return await ws_close(websocket, 4004)
                for bot in api_token:
                    bid = await db.fetchrow("SELECT bot_id FROM bots WHERE api_token = $1", str(bot))
                    if bid:
                        websocket.api_token.append(api_token)
                        websocket.bot_id.append(bid["bot_id"])
                if websocket.api_token == [] or websocket.bot_id == []:
                    await manager.send_personal_message({"event": enums.APIEvents.ws_kill, "type": enums.APIEventTypes.ws_no_auth}, websocket)
                    return await ws_close(websocket, 4004)
                await manager.send_personal_message({"event": enums.APIEvents.ws_status, "type": enums.APIEventTypes.ws_ready, "context": {"bots": [str(bid) for bid in websocket.bot_id]}}, websocket)
            case enums.APIEventTypes.auth_manager_key:
                try:
                    if secure_strcmp(api_token["context"]["key"], test_server_manager_key) or secure_strcmp(api_token["context"]["key"], root_key):
                        websocket.manager_bot = True
                    else:
                        await manager.send_personal_message({"event": enums.APIEvents.ws_kill, "type": enums.APIEventTypes.ws_no_auth}, websocket)
                        return await ws_close(websocket, 4004)
                except:
                    await manager.send_personal_message({"event": enums.APIEvents.ws_kill, "type": enums.APIEventTypes.ws_invalid}, websocket)
                    return await ws_close(websocket, 4004)
                await manager.send_personal_message({"event": enums.APIEvents.ws_status, "type": enums.APIEventTypes.ws_ready, "context": None}, websocket)
    try:
        if not websocket.manager_bot:
            ini_events = {}
            for bot in websocket.bot_id:
                events = await redis_db.hget(str(bot), key = "ws")
            if events is None:
                events = {} # Nothing
            else:
                try:
                    events = orjson.loads(events)
                except Exception as exc:
                    print(exc)
                    events = {}
                ini_events[str(bot)] = events
            await manager.send_personal_message({"event": enums.APIEvents.ws_event, "type": enums.APIEventTypes.ws_event_multi, "context": ini_events}, websocket)
            pubsub = redis_db.pubsub()
            for bot in websocket.bot_id:
                await pubsub.subscribe(str(bot))
        else:
            pubsub = redis_db.pubsub()
            await pubsub.psubscribe("*")
    
        async for msg in pubsub.listen():
            print(msg, websocket.manager_bot)
            if msg is None or type(msg.get("data")) != bytes:
                continue
            await manager.send_personal_message({"event": enums.APIEvents.ws_event, "type": enums.APIEventTypes.ws_event_single, "context": {msg.get("channel").decode("utf-8"): orjson.loads(msg.get("data"))}}, websocket)
    except:
        try:
            await pubsub.unsubscribe()
        except:
            pass
        await ws_close(websocket, 4006)
        await manager.disconnect(websocket)

# Chat

@router.websocket("/api/v1/ws/chat")
async def chat_api(websocket: WebSocket):
    await manager_chat.connect(websocket)
    if not websocket.authorized:
        await manager_chat.send_personal_message({"payload": "IDENTITY", "type": "USER|BOT"}, websocket)
        try:
            identity = await websocket.receive_json()
            print("HERE")
            if identity.get("payload") != "IDENTITY_RESPONSE":
                raise TypeError
        except:
            await manager_chat.send_personal_message({"payload": "KILL_CONN", "type": "INVALID_IDENTITY_RESPONSE"}, websocket)
            return await ws_close(websocket, 4004)
        data = identity.get("data")
        if data is None or type(data) != str:
            await manager_chat.send_personal_message({"payload": "KILL_CONN", "type": "NO_AUTH"}, websocket) # Invalid api token provided
            return await ws_close(websocket, 4004)
        if identity.get("type") == "USER":
            acc_type = 0
            sender = await db.fetchval("SELECT user_id FROM users WHERE api_token = $1", identity.get("data"))
        elif identity.get("type") == "BOT": 
            acc_type = 1
            sender = await db.fetchval("SELECT bot_id FROM bots WHERE api_token = $1", identity.get("data"))
        else:    
            await manager_chat.send_personal_message({"payload": "KILL_CONN", "type": "NOT_IMPLEMENTED"}, websocket)
            return await ws_close(websocket, 4005) # 4005 = Not Implemented
        if sender is None:
            await manager_chat.send_personal_message({"payload": "KILL_CONN", "type": "NO_AUTH"}, websocket) # Invalid api token provided
            return await ws_close(websocket, 4004)
    websocket.authorized = True
    await manager_chat.send_personal_message({"payload": "CHAT_USER", "type": "CHAT", "data": (await get_any(sender))}, websocket)
    try:
        await redis_db.incrbyfloat(str(sender) + "_cli_count")
        messages = await redis_db.hget("global_chat", key = "message")
        if messages is None:
            messages = b"" # No messages
        await manager_chat.send_personal_message({"payload": "MESSAGE", "type": "BULK", "data": messages.decode("utf-8")}, websocket) # Send all messages in bulk
        pubsub = redis_db.pubsub()
        await pubsub.subscribe("global_chat_channel")
        async for msg in pubsub.listen():
            print("Got msg")
            if type(msg['data']) != bytes:
                continue
            try:
                msg_info = orjson.loads(msg['data'].decode('utf-8'))
            except:
                continue
            await manager_chat.send_personal_message(msg_info, websocket) # Send all messages in bulk
    except Exception as e:
        await redis_db.decrby(str(sender) + "_cli_count")
        print(e)
        await pubsub.unsubscribe()
        await manager_chat.disconnect(websocket)

async def chat_publish_message(msg):
    pass

# End Chat
