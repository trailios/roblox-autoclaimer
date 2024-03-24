# WebSocket shit
######
import websocket
import json
import time
import threading
import asyncio
import re
import requests

loop = asyncio.new_event_loop()

session_id = None
heartbeat_interval = 30
seq_num = ""
resumeURL = None
ws = None

groupsid = 0
groupsids = []

try:
    with open("config.json", "r", encoding="utf-8") as daat2:
        data = json.load(daat2)
        webhooks = data["webhooks"]
        prefix = "+"
except FileNotFoundError:
    print("Config file not found. Please make sure config.json exists.")
    exit(1)
except json.JSONDecodeError:
    print("Error decoding JSON in config file.")
    exit(1)

embed = {
    "username": "TK - Claimer",
    "embeds": [
        {
            "title": "TK Claimer",
            "description": "Claimer started",
            "footer": {
                "text": "Made by: TK aka Traili your favourite developer",
                "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
            },
        }
    ],
}

requests.post(webhooks["logs"], json=embed)


async def on_message(ws, message):
    global session_id, heartbeat_interval, daat2, seq_num, resumeURL, groupsid, groupsids

    try:
        data = json.loads(message)
    except json.JSONDecodeError:
        print("Error decoding JSON message:", message)
        return

    event_type = data.get("t")
    if event_type == "READY":
        session_id = data.get("d", {}).get("session_id")
        resumeURL = data.get("d", {}).get("resume_gateway_url")
        clear()
        logo()
        startup(f"Logged in as {data['d']['user']['username']}")
        startup("Session id: " + session_id)
        run()
        heartbeatwrapper()
    elif data["op"] == 10:
        heartbeat_interval = data["d"]["heartbeat_interval"] / 1000
        seq_num = data["s"]
    elif data["op"] == 7:
        log("reconnecting")
        ws.close(4000)
        reconnect()
    elif event_type == "MESSAGE_CREATE":
        content: str = data["d"]["content"]
        user: str = data["d"]["author"]["username"]
        channel = data["d"]["channel_id"]
        if content != "":
            if "roblox.com/groups" in content:
                message_parts = content.split("/")
                group_id_index = message_parts.index("groups") + 1
                if group_id_index < len(message_parts):
                    numbers: int = re.findall(r"\d+", message_parts[group_id_index])
                    if numbers != groupsid:
                        groupsid = numbers
                        groupsids.append(numbers[0])
                        await main(numbers[0])
    elif event_type == "RESUMED":
        log("Resumed")


async def on_error(ws, error):
    print("Error:", error)


async def on_close(ws, close_status_code, close_msg):
    if close_status_code != 1000 and close_status_code != 1001:
        await resume()
    elif close_status_code == 1000 or close_status_code == 1001:
        fatal(f"Unfixable error, reconnecting instead of resuming...")
        reconnect()
    else:
        fatal(
            f"Connection closed with status code {close_status_code}. Resuming session"
        )
        await resume()


async def on_open(ws):
    payload = {
        "op": 2,
        "d": {
            "token": token,
            "intents": 513 | (1 << 15) | (1 << 12) | (1 << 9),
            "properties": {"os": "linux", "browser": "chrome", "device": "chrome"},
        },
    }
    ws.send(json.dumps(payload))


def on_open_wrapper(ws):
    loop.run_until_complete(on_open(ws))


def on_message_wrapper(ws, message):
    loop.run_until_complete(on_message(ws, message))


def on_close_wrapper(ws, close_status_code, close_msg):
    loop.run_until_complete(on_close(ws, close_status_code, close_msg))


def on_error_wrapper(ws, error):
    loop.run_until_complete(on_error(ws, error))


def heartbeatwrapper():
    threading.Thread(target=asyncio.run, args=(send_heartbeat(),)).start()


def resumewrapper(ws):
    loop.run_until_complete(resume(ws))


async def send_heartbeat():
    while True:
        await asyncio.sleep(heartbeat_interval)
        ws.send(json.dumps({"op": 1, "d": f"{seq_num}"}))


async def resume():
    ws = websocket.WebSocketApp(
        f"{resumeURL}",
        on_message=on_message_wrapper,
        on_error=on_error_wrapper,
        on_close=on_close_wrapper,
    )
    payload = {
        "op": 6,
        "d": {
            "token": token,
            "intents": 513 | (1 << 15) | (1 << 12) | (1 << 9),
            "session_id": session_id,
            "seq": 1337,
        },
    }
    loop.run_until_complete(ws.run_forever())
    ws.send(json.dumps(payload))
    log("Resumed")


def reconnect():
    ws = websocket.WebSocketApp(
        "wss://gateway.discord.gg",
        on_message=on_message_wrapper,
        on_error=on_error_wrapper,
        on_close=on_close_wrapper,
    )
    ws.on_open = on_open
    loop.run_until_complete(ws.run_forever())


# claimer shit
########
import socket, ssl, time, random, requests, asyncio, threading, json, aiosonic
from console import *

Host = "groups.roblox.com"
Port = 443

cookie = ""
xcsrf = ""

MESSAGES = [
    "People say i am just better",
    "someone said tk is slow?",
    "0.05s claim time go brrrr",
    "well 3x",
    "2 + 2 is 18",
    "4 VPS is fast",
    "this claimer is crazy aint it?",
]

data = json.load(open("config.json"))
webhook = data["webhooks"]


ct = ssl.create_default_context()


async def joinclaim(id, cookie, xcsrf):
    sock = socket.create_connection((Host, Port))
    so = ct.wrap_socket(sock, server_hostname=Host)
    xtoken = xcsrf
    headers = (
        f"Host: {Host}\r\n"
        f"Connection: keep-alive\r\n"
        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36\r\n"
        f"Cookie: GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;\r\n"
        f"x-csrf-token: {xtoken}\r\n"
        f"Content-Type: application/json; charset=utf-8\r\n"
        f"accept: accept-encoding\r\n\r\n"
    )

    datajoin = f"POST /v1/groups/{id}/users HTTP/1.1\r\n{headers}"
    dataclaim = f"POST /v1/groups/{id}/claim-ownership HTTP/1.1\r\n{headers}"

    start_time = time.time()
    so.sendall(datajoin.encode())
    so.sendall(dataclaim.encode())
    response_join = so.recv(16384).decode()
    response_claim = so.recv(16384).decode()
    end_time = time.time()
    total_time = end_time - start_time

    return response_join, response_claim, total_time


def leave(groupid):
    global cookie, xcsrf
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
        "x-csrf-token": f"{xcsrf}",
    }
    res2 = requests.get(
        f"https://users.roblox.com/v1/users/authenticated", headers=headers
    )
    userid = res2.json()["id"]
    url = f"https://groups.roblox.com/v1/groups/{groupid}/users/{userid}"
    response = requests.delete(url, headers=headers)
    return response


async def changecookie1():
    global cookie, xcsrf
    with open("cookies.txt", "r") as f:
        data = f.read().splitlines()

    cookie = random.choice(data)
    try:
        xr = requests.post(
            "https://auth.roblox.com/v2/logout",
            headers={"cookie": f".ROBLOSECURITY={cookie}"},
        )
        if xr.status_code != 200:
            xcsrf = xr.headers.get("x-csrf-token")
    except:
        pass


async def checkgroup(groupid: int, cookie: str, webhookurl: str):
    global xcsrf
    client = aiosonic.HTTPClient()
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
        "x-csrf-token": f"{xcsrf}",
    }
    today = datetime.now().strftime("%Y-%m-%d")
    GamesandVisits = await client.get(
        f"https://games.roblox.com/v2/groups/{groupid}/gamesV2?accessFilter=2&limit=100&sortOrder=Asc"
    )
    Funds = await client.get(
        f"https://economy.roblox.com/v1/groups/{groupid}/currency", headers=headers
    )
    PFunds = await client.get(
        f"https://economy.roblox.com/v1/groups/{groupid}/revenue/summary/{today}",
        headers=headers,
    )
    clothes = await client.get(
        f"https://catalog.roblox.com/v1/search/items/details?Category=3&SortType=Relevance&CreatorTargetId={groupid}&ResultsPerPage=100&CreatorType=2",
        headers=headers,
    )
    thumbnail = await client.get(
        f"https://thumbnails.roblox.com/v1/groups/icons?groupIds={groupid}&size=150x150&format=Png&isCircular=false",
        headers=headers,
    )

    if thumbnail.status_code == 200:
        thumbnailicon = (await thumbnail.json())["data"][0]["imageUrl"]
    if Funds.status_code == 200:
        robux = (await Funds.json())["robux"]
    if PFunds.status_code == 200:
        revenue = (await PFunds.json())["pendingRobux"]
    if GamesandVisits.status_code == 200:
        games = (await GamesandVisits.json()).get("data", [])
        groupVisits = sum(game.get("placeVisits", 0) for game in games)
        groupgames = len(games)
    if clothes.status_code == 200:
        json = await clothes.json()

        clothing = 0
        while True:
            next_cursor: str = json["nextPageCursor"]
            clothing += len(json["data"])

            if next_cursor == None:
                break

            url = f"https://catalog.roblox.com/v1/search/items/details?Category=3&SortType=Relevance&CreatorTargetId={groupid}&ResultsPerPage=100&CreatorType=2&Cursor={next_cursor}"
            clothing_request = await client.get(url, headers=headers)
            json = await clothing_request.json()

    embed = {
        "username": "TK - Detections",
        "embeds": [
            {
                "title": f"Group | {groupid}",
                "fields": [
                    {"name": "Robux", "value": f"{robux}", "inline": True},
                    {"name": "pending", "value": f"{revenue}", "inline": True},
                    {"name": "Games", "value": f"{groupgames}", "inline": True},
                    {"name": "Visits", "value": f"{groupVisits}", "inline": True},
                    {"name": "Clothing", "value": f"{clothing}", "inline": True},
                ],
                "footer": {
                    "text": "Made by: TK aka Traili your favourite developer",
                    "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
                },
                "thumbnail": {"url": thumbnailicon},
                "url": f"https://roblox.com/groups/{groupid}",
                "color": 0x00FF00,
            }
        ],
    }

    if (
        robux >= 100
        or revenue >= 100
        or groupgames >= 5
        or groupVisits >= 100
        or clothing >= 10
    ):
        await client.post(webhookurl, json={"content": "Good group"})
        await client.post(webhookurl, json=embed)
    else:
        await client.post(webhookurl, json=embed)


async def xcsrftoken():
    while True:
        global xcsrf, cookie
        try:
            xr = requests.post(
                "https://auth.roblox.com/v2/logout",
                headers={"cookie": f".ROBLOSECURITY={cookie}"},
            )
            if xr.status_code != 200:
                xcsrf = xr.headers.get("x-csrf-token")
        except:
            pass


async def main(groupid):
    global cookie, xcsrf
    client = aiosonic.HTTPClient()
    join, claim, time = await joinclaim(groupid, cookie, xcsrf)
    claimstatus = claim.splitlines()[0]
    joinstatus = join.splitlines()[0]

    logs = webhooks["logs"]
    detections = webhooks["detections"]
    erors = webhooks["errors"]

    if "HTTP/1.1 200 OK" in joinstatus and "HTTP/1.1 200 OK" in claimstatus:
        ok(f"Joined and claimed {groupid} in {time} seconds")
        await client.post(
            logs,
            json={
                "content": f"Joined and claimed {groupid} in {time} seconds, sending to detections"
            },
        )
        await checkgroup(groupid, cookie, detections)
        requests.patch(
            f"https://groups.roblox.com/v1/groups/{groupid}/status",
            headers={
                "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
                "X-CSRF-TOKEN": f"{xcsrf}",
            },
            json={"message": f"{random.choice(MESSAGES)}"},
        )

    elif (
        "HTTP/1.1 200 OK" in joinstatus
        and "HTTP/1.1 403 Forbidden" in claimstatus
        or "HTTP/1.1 200 OK" in joinstatus
        and "HTTP/1.1 500 Internal Server Error" in claimstatus
    ):
        warn(f"Someone already claimed")
        lev = leave(groupid)
        if lev.status_code == 200:
            log(f"Left the group {groupid}")
        else:
            warn(f"Something happend on leave at {groupid}")

    elif "HTTP/1.1 403 Forbidden" in joinstatus and ["==", "="] in claimstatus:
        warn(f"Cookied flagged? changing cookie...")
        await client.post(
            erors, json={"content": f"Cookied flagged? changing cookie..."}
        )
        await changecookie1()

    elif (
        "HTTP/1.1 403 Forbidden" in joinstatus
        and "HTTP/1.1 403 Forbidden" in claimstatus
    ):
        warn(f"XCSRF Invalidatedc (auto fix)")

    elif "HTTP/1.1 429" in joinstatus or "HTTP/1.1 429" in claimstatus:
        warn(f"Ratelimited, changing cookie...")
        await client.post(erors, json={"content": f"Ratelimited, changing cookie..."})
        await changecookie1()

    else:
        fatal(f"Failed to claim {groupid} | {joinstatus} | {claimstatus}")
        await client.post(
            erors,
            json={
                "content": f"Failed to claim {groupid} | {joinstatus} | {claimstatus}"
            },
        )
        leave(groupid)


asyncio.run(changecookie1())
thread = threading.Thread(target=asyncio.run, args=(xcsrftoken(),))
thread.daemon = True
thread.start()
######
# console shit
#####
import os, shutil, time, ctypes, threading, asyncio
from datetime import datetime
from colorama import Fore, Style
from rich.console import Console

console = Console()

stuff = [
    "|",
    "|",
    "/",
    "/",
    "-",
    "-",
    "\\",
    "\\",
    "|",
    "|",
    "/",
    "/",
    "-",
    "-",
    "\\",
    "\\",
]


def run():
    thread1 = threading.Thread(target=asyncio.run, args=(wait(),))
    thread1.daemon = True
    thread1.start()


async def wait():
    global stuff
    while True:
        for spinner in stuff:
            print(
                f"{timet()}{Style.BRIGHT}{Fore.LIGHTBLUE_EX}GROUPS {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK}> {Fore.WHITE}{spinner}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} Waiting for groups {Fore.RESET}{Fore.WHITE}",
                end="\r",
            )
            await asyncio.sleep(0.0525)


def startup(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTCYAN_EX}STARTUP {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


#####

# credits to visions4k for all below this (https://github.com/visions4k/)


#######
def setTitle(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)


logoascii = """
_____________ __               ______________      _____                        
___  __/__  //_/               __  ____/__  /_____ ___(_)______ ________________
__  /  __  ,<     ________     _  /    __  /_  __ `/_  /__  __ `__ \  _ \_  ___/
_  /   _  /| |    _/_____/     / /___  _  / / /_/ /_  / _  / / / / /  __/  /    
/_/    /_/ |_|                 \____/  /_/  \__,_/ /_/  /_/ /_/ /_/\___//_/     
                                                                                
"""


def logo():
    columns, rows = shutil.get_terminal_size()
    lines = logoascii.split("\n")
    x = int(columns / 2 - len(max(lines, key=len)) / 2)
    y_start = int(rows / 2 - len(lines) / 2)

    start_color = (10, 10, 255)
    end_color = (255, 10, 5)
    steps = len(lines)
    color_step = (
        (end_color[0] - start_color[0]) / steps,
        (end_color[1] - start_color[1]) / steps,
        (end_color[2] - start_color[2]) / steps,
    )

    for i, line in enumerate(lines):
        r = int(start_color[0] + i * color_step[0])
        g = int(start_color[1] + i * color_step[1])
        b = int(start_color[2] + i * color_step[2])

        print(f"\033[38;2;{r};{g};{b}m", end="")
        print(f"\033[{y_start + i};{x}H{line}")

    print("\033[0m")

    versionText = f"Version: 5.3.5"
    versionText_x = int(columns / 2 - len(versionText) / 2)
    versionText_y = y_start + len(lines) + 2

    light_red = (255, 100, 100)
    dark_red = (139, 0, 0)

    steps = len(versionText)
    color_step = (
        (dark_red[0] - light_red[0]) / steps,
        (dark_red[1] - light_red[1]) / steps,
        (dark_red[2] - light_red[2]) / steps,
    )

    for i, char in enumerate(versionText):
        r = int(light_red[0] + i * color_step[0])
        g = int(light_red[1] + i * color_step[1])
        b = int(light_red[2] + i * color_step[2])

        print(f"\033[38;2;{r};{g};{b}m", end="")
        print(f"\033[{versionText_y};{versionText_x + i}H{char}", end="")

    print("\033[0m")
    print("\n")


def clear():
    if "nt" in os.name:
        os.system("cls")
    else:
        os.system("clear")


def timet():
    return Style.BRIGHT + Fore.BLACK + f"[{datetime.now().strftime('%I:%M:%S')}] "


def log(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTMAGENTA_EX}INFO {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def ok(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTGREEN_EX}SUCCESS {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def okreq(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTGREEN_EX}200 {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def fatalreq(object, status):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTRED_EX}{status} {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def important(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTRED_EX}IMPORTANT {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def fatal(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTRED_EX}ERROR {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def warn(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTYELLOW_EX}WARN {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )


def inputt(prompt):
    return input(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTBLUE_EX}ENTER HERE {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{prompt}"
    )


#######

if __name__ == "__main__":
    with open("config.json", "r") as f:
        data = json.load(f)
        token = data["token"]

    ws = websocket.WebSocketApp(
        "wss://gateway.discord.gg",
        on_message=on_message_wrapper,
        on_error=on_error_wrapper,
        on_close=on_close_wrapper,
    )
    ws.on_open = on_open_wrapper

    asyncio.run(ws.run_forever())
