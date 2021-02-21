from ..deps import *
from uuid import UUID
from fastapi.responses import HTMLResponse
from typing import List
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

security = HTTPBearer()

router = APIRouter(
    prefix = "/api",
    include_in_schema = True
)

class PromoDelete(BaseModel):
    promo_id: Optional[uuid.UUID] = None

class Promo(BaseModel):
    title: str
    info: str
    css: Optional[str] = None

class PromoPatch(Promo):
    promo_id: uuid.UUID

class APIResponse(BaseModel):
    done: bool
    reason: Optional[str] = None

@router.delete("/bots/{bot_id}/promotions", tags = ["API"], response_model = APIResponse)
async def delete_promotion(request: Request, bot_id: int, promo: PromoDelete, Authorization: str = Header("INVALID_API_TOKEN")):
    """Deletes a promotion for a bot or deletes all promotions from a bot (WARNING: DO NOT DO THIS UNLESS YOU KNOW WHAT YOU ARE DOING).

    **API Token**: You can get this by clicking your bot and clicking edit and scrolling down to API Token or clicking APIWeb

    **Event ID**: This is the ID of the event you wish to delete. Not passing this will delete ALL events, so be careful
    """
    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    id = id["bot_id"]
    if promo.promo_id is not None:
        eid = await db.fetchrow("SELECT id FROM promotions WHERE id = $1", promo.promo_id)
        if eid is None:
            return {"done":  False, "reason": "NO_PROMOTION_FOUND"}
        await db.execute("DELETE FROM promotions WHERE bot_id = $1 AND id = $2", id, promo.promo_id)
    else:
        await db.execute("DELETE FROM promotions WHERE bot_id = $1", id)
    return {"done":  True, "reason": None}

@router.put("/bots/{bot_id}/promotions", tags = ["API"], response_model = APIResponse)
async def create_promotion(request: Request, bot_id: int, promo: Promo, Authorization: str = Header("INVALID_API_TOKEN")):
    """Creates a promotion for a bot. Events can be used to set guild/shard counts, enter maintenance mode or to show promotions

    **API Token**: You can get this by clicking your bot and clicking edit and scrolling down to API Token or clicking APIWeb

    **Promotion**: This is the name of the event in question. There are a few special events as well:

    """
    if len(promo.title) < 3:
        return {"done":  False, "reason": "TEXT_TOO_SMALL"}
    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    id = id["bot_id"]
    await add_promotion(id, promo.title, promo.info, promo.css)
    return {"done":  True, "reason": None}

@router.patch("/bots/{bot_id}/promotions", tags = ["API"], response_model = APIResponse)
async def edit_promotion(request: Request, bot_id: int, promo: PromoPatch, Authorization: str = Header("INVALID_API_TOKEN")):
    """Edits an promotion for a bot given its promotion ID.

    **API Token**: You can get this by clicking your bot and clicking edit and scrolling down to API Token or clicking APIWeb

    **Promotion ID**: This is the ID of the promotion you wish to edit 

    """
    if len(promo.title) < 3:
        return {"done":  False, "reason": "TEXT_TOO_SMALL"}
    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    id = id["bot_id"]
    pid = await db.fetchrow("SELECT id, events FROM api_event WHERE id = $1", promo.promo_id)
    if eid is None:
        return {"done":  False, "reason": "NO_MESSAGE_FOUND"}
    await db.execute("UPDATE promotions SET title = $1, info = $2 WHERE bot_id = $3", promo.title, promo.info, id)
    return {"done": True, "reason": None}

@router.patch("/bots/{bot_id}/token", tags = ["API"], response_model = APIResponse)
async def regenerate_token(request: Request, bot_id: int, Authorization: str = Header("INVALID_API_TOKEN")):
    """Regenerate the API token

    **API Token**: You can get this by clicking your bot and clicking edit and scrolling down to API Token or clicking APIWeb
    """
    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    await db.execute("UPDATE bots SET api_token = $1 WHERE bot_id = $2", get_token(132), id["bot_id"])
    return {"done": True, "reason": None}

class RandomBotsAPI(BaseModel):
    bot_id: str
    description: str
    banner: str
    certified: bool
    username: str
    avatar: str
    servers: str
    invite: str
    votes: int

@router.get("/bots/random", tags = ["API"], response_model = RandomBotsAPI)
async def random_bots_api(request: Request):
    random_unp = await db.fetchrow("SELECT description, banner,certified,votes,servers,bot_id,invite FROM bots WHERE queue = false AND banned = false AND disabled = false ORDER BY RANDOM() LIMIT 1") # Unprocessed
    bot = (await get_bot(random_unp["bot_id"])) | dict(random_unp)
    bot["bot_id"] = str(bot["bot_id"])
    bot["servers"] = human_format(bot["servers"])
    return bot

@router.get("/bots/{bot_id}", tags = ["API"])
async def get_bots_api(request: Request, bot_id: int, Authorization: str = Header("INVALID_API_TOKEN")):
    """Gets bot information given a bot ID. If not found, 404 will be returned. If a proper API Token is provided, sensitive information (System API Events will also be provided)"""
    api_ret = await db.fetchrow("SELECT bot_id AS id, description, tags, html_long_description, long_description, servers AS server_count, shard_count, shards, prefix, invite, invite_amount, owner AS _owner, extra_owners AS _extra_owners, features, bot_library AS library, queue, banned, certified, website, discord AS support, github, user_count, votes, css FROM bots WHERE bot_id = $1", bot_id)
    if api_ret is None:
        return abort(404)
    api_ret = dict(api_ret)
    bot_obj = await get_bot(bot_id)
    api_ret["username"] = bot_obj["username"]
    api_ret["avatar"] = bot_obj["avatar"]
    if api_ret["_extra_owners"] is None:
        api_ret["owners"] = [api_ret["_owner"]]
    else:
        api_ret["owners"] = [api_ret["_owner"]] + api_ret["_extra_owners"]
    api_ret["id"] = str(api_ret["id"])
    if Authorization is not None:
        check = await db.fetchrow("SELECT bot_id FROM bots WHERE api_token = $1", str(Authorization))
        if check is None or check["bot_id"] != bot_id:
            sensitive = False
        else:
            sensitive = True
    else:
        sensitive = False
    if sensitive:
        api_ret["sensitive"] = await get_events(bot_id = bot_id)
    else:
        api_ret["sensitive"] = {}
    api_ret["promotions"] = await get_promotions(bot_id = bot_id)
    api_ret["maint"] = await in_maint(bot_id = bot_id)
    vanity = await db.fetchrow("SELECT vanity_url FROM vanity WHERE redirect = $1", bot_id)
    if vanity is None:
        api_ret["vanity"] = None
    else:
        api_ret["vanity"] = vanity["vanity_url"]
    api_ret["_reviews"] = await parse_reviews(bot_id)
    api_ret["reviews"] = api_ret["_reviews"][0]
    api_ret["average_stars"] = api_ret["_reviews"][1]
    del api_ret["_reviews"]
    return api_ret

class BotVoteCheck(BaseModel):
    votes: int
    voted: bool
    vote_right_now: bool
    vote_epoch: int
    time_to_vote: int

@router.get("/bots/{bot_id}/votes", tags = ["API"], response_model = BotVoteCheck)
async def get_votes_api(request: Request, bot_id: int, user_id: Optional[int] = None, Authorization: str = Header("INVALID_API_TOKEN")):
    """Endpoint to check amount of votes a user has."""
    if user_id is None:
        return dict((await db.fetchrow("SELECT votes FROM bots WHERE bot_id = $1", bot_id))) | {"vote_epoch": 0, "voted": False, "time_to_vote": 1, "vote_right_now": False}
    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    voters = await db.fetchrow("SELECT timestamps FROM bots_voters WHERE bot_id = $1 AND userid = $2", int(bot_id), int(user_id))
    if voters is None:
        return {"votes": 0, "voted": False, "vote_epoch": 0, "time_to_vote": 0, "vote_right_now": True}
    voter_count = len(voters["timestamps"])
    vote_epoch = await db.fetchrow("SELECT vote_epoch FROM users WHERE userid = $1", user_id)
    if vote_epoch is None:
        vote_epoch = 0
    else:
        vote_epoch = vote_epoch["vote_epoch"]
    WT = 60*60*8 # Wait Time
    time_to_vote = WT - (time.time() - vote_epoch)
    if time_to_vote < 0:
        time_to_vote = 0
    return {"votes": voter_count, "voted": voter_count != 0, "vote_epoch": vote_epoch, "time_to_vote": time_to_vote, "vote_right_now": time_to_vote == 0}

@router.get("/bots/{bot_id}/votes/timestamped", tags = ["API"])
async def timestamped_get_votes_api(request: Request, bot_id: int, user_id: Optional[int] = None, Authorization: str = Header("INVALID_API_TOKEN")):
    """Endpoint to check amount of votes a user has with timestamps. This does not return whether a user can vote"""
    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    elif user_id is not None:
        ldata = await db.fetch("SELECT userid, timestamps FROM bots_voters WHERE bot_id = $1 AND userid = $2", int(bot_id), int(user_id))
    else:
        ldata = await db.fetch("SELECT userid, timestamps FROM bots_voters WHERE bot_id = $1", int(bot_id))
    ret = {}
    for data in ldata:
        ret[str(data["userid"])] = data["timestamps"]
    return {"user": "timestamp"} | ret

# TODO
#@router.get("/templates/{code}", tags = ["Core API"])
#async def get_template_api(request: Request, code: str):
#    guild =  await client.fetch_template(code).source_guild
#    return template

class BotStats(BaseModel):
    guild_count: int
    shard_count: Optional[int] = None
    shards: Optional[list] = None
    user_count: Optional[int] = None

@router.post("/bots/{bot_id}/stats", tags = ["API"], response_model = APIResponse)
async def set_bot_stats_api(request: Request, bt: BackgroundTasks, bot_id: int, api: BotStats, Authorization: str = Header("INVALID_API_TOKEN")):
    """
    This endpoint allows you to set the guild + shard counts for your bot
    """
    id = await db.fetchrow("SELECT bot_id, shard_count, shards, user_count FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    if api.shard_count is None:
        shard_count = id["shard_count"]
    else:
        shard_count = api.shard_count
    if api.shards is None:
        shards = id["shards"]
    else:
        shards = api.shards
    if api.user_count is None:
        user_count = id["user_count"]
    else:
        user_count = api.user_count
    bt.add_task(set_stats, bot_id = id["bot_id"], guild_count = api.guild_count, shard_count = shard_count, shards = shards, user_count = user_count)
    return {"done": True, "reason": None}

# set_stats(*, bot_id: int, guild_count: int, shard_count: int, user_count: Optiona;int] = None):

class APISMaint(BaseModel):
    mode: int = 1
    reason: str

@router.post("/bots/{bot_id}/maintenances", tags = ["API"], response_model = APIResponse)
async def set_maintenance_mode(request: Request, bot_id: int, api: APISMaint, Authorization: str = Header("INVALID_API_TOKEN")):
    """This is just an endpoing for enabling or disabling maintenance mode. As of the new API Revamp, this isi the only way to add a maint

    **API Token**: You can get this by clicking your bot and clicking edit and scrolling down to API Token

    **Mode**: Whether you want to enter or exit maintenance mode. Setting this to 1 will enable maintenance and setting this to 0 will disable maintenance mode. Different maintenance modes are planned
    """
    
    if api.mode not in [0, 1]:
        return ORJSONResponse({"done":  False, "reason": "UNSUPPORTED_MODE"}, status_code = 400)

    id = await db.fetchrow("SELECT bot_id FROM bots WHERE bot_id = $1 AND api_token = $2", bot_id, str(Authorization))
    if id is None:
        return abort(401)
    await add_maint(id["bot_id"], api.mode, api.reason)
    return {"done": True, "reason": None}

@router.get("/features/{name}", tags = ["API"])
async def get_feature_api(request: Request, name: str):
    """Gets a feature given its internal name (custom_prefix, open_source etc)"""
    if name not in features.keys():
        return abort(404)
    return features[name]

class VanityAPI(BaseModel):
    type: str
    redirect: str

@router.get("/vanity/{vanity}", tags = ["API"], response_model = VanityAPI)
async def get_vanity(request: Request, vanity: str):
    vb = await vanity_bot(vanity, compact = True)
    if vb is None:
        return abort(404)
    return {"type": vb[0], "redirect": vb[1]}

@router.get("/bots/ext/index", tags = ["API (Other)"])
async def bots_index_page_api_do(request: Request):
    """For any potential Android/iOS app, crawlers etc."""
    return await render_index(request = request, api = True)

@router.get("/bots/ext/search", tags = ["API (Other)"])
async def bots_search_page(request: Request, query: str):
    """For any potential Android/iOS app, crawlers etc. Query is the query to search for"""
    return await render_search(request = request, q = query, api = True)

async def ws_send_events():
    manager.fl_loaded = True
    while True:
        for ws in manager.active_connections:
            for bid in ws.bot_id:
                ws_events = {str(bid): (await redis_db.hgetall(str(bid) + "_ws", encoding = 'utf-8'))}
                if ws_events[str(bid)].get("status") == "READY":
                    # Make sure payload is made a dict
                    for key in ws_events[str(bid)].keys():
                        try:
                            ws_events[str(bid)][key] = orjson.loads(ws_events[str(bid)][key])
                            del ws_events[str(bid)][key]['id']
                            print("KEY: " + ws_events[str(bid)][key])
                        except:
                            pass
                    rc = await manager.send_personal_message({"payload": "EVENTS", "type": "EVENTS_V1", "data": ws_events}, ws)
                    for key in (await redis_db.hkeys(str(bid) + "_ws", encoding = "utf-8")):
                        await redis_db.hdel(str(bid) + "_ws", key)
                    await redis_db.hset(str(bid) + "_ws", mapping = {"status": "IDLE"})

async def ws_close(websocket: WebSocket, code: int):
    try:
        return await websocket.close(code=code)
    except:
        return
        
@router.websocket("/api/ws")
async def websocker_real_time_api(websocket: WebSocket):
    await manager.connect(websocket)
    if websocket.api_token == []:
        await manager.send_personal_message({"payload": "IDENTITY", "type": "API_TOKEN"}, websocket)
        try:
            api_token = await websocket.receive_json()
            print("HERE")
            if api_token.get("payload") != "IDENTITY_RESPONSE" or api_token.get("type") != "API_TOKEN":
                raise TypeError
        except:
            await manager.send_personal_message({"payload": "KILL_CONN", "type": "INVALID_IDENTITY_RESPONSE"}, websocket)
            return await ws_close(websocket, 4004)
        api_token = api_token.get("data")
        if api_token is None or type(api_token) == int or type(api_token) == str:
            await manager.send_personal_message({"payload": "KILL_CONN", "type": "INVALID_IDENTITY_RESPONSE"}, websocket)
            return await ws_close(websocket, 4004)
        for bot in api_token:
            bid = await db.fetchrow("SELECT bot_id FROM bots WHERE api_token = $1", str(bot))
            if bid is None:
                pass
            else:
                websocket.api_token.append(api_token)
                websocket.bot_id.append(bid["bot_id"])
        if websocket.api_token == [] or websocket.bot_id == []:
            await manager.send_personal_message({"payload": "KILL_CONN", "type": "NO_AUTH"}, websocket)
            return await ws_close(websocket, 4004)
    await manager.send_personal_message({"payload": "STATUS", "type": "READY"}, websocket)
    try:
        while True:
            if manager.fl_loaded == False:
                asyncio.create_task(ws_send_events())
            await asyncio.sleep(1) # Keep Waiting Forever
    except WebSocketDisconnect:
        await manager.disconnect(websocket)

