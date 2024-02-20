import aiosonic, re, time, requests, os, json, pyfiglet, asyncio, random
from datetime import datetime

with open("config.json", "r") as f:
    config = json.load(f)

with open("cookies.txt", "r") as f:
    cookies = f.read().splitlines()

DISCORD_TOKEN = config.get("token")
CHANNEL_ID = config.get("channel")
VERSION = config.get("version")
logs = config.get("logs")
detections = config.get("detections")
errors = config.get("errors")

lchannel = requests.get(logs).json()["channel_id"]
dchannel = requests.get(detections).json()["channel_id"]
echannel = requests.get(errors).json()["channel_id"]

startupembed = {
    "username": "TK - claimer",
    "embeds": [
        {
            "title": "Started!",
            "description": f"TK - claimer V{VERSION}\n\nTotal cookies: {len(cookies)}\nChannel: <#{CHANNEL_ID}>\n\nLogs: <#{lchannel}>\nDetetions: <#{dchannel}>\nErrors: <#{echannel}>",
            "footer": {
                "text": "Made by: TK aka Traili your favourite developer",
                "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
            },
            "thumbnail": {
                "url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256"
            },
            "color": 0x3498DB,
        }
    ],
}

requests.post(logs, json=startupembed)


def print_success(message):
    print(f"\033[92mSUCCESS --> {message}\033[0m")


def print_warning(message):
    print(f"\033[93mWARNING --> {message}\033[0m")


def print_error(message):
    print(f"\033[91mERROR --> {message}\033[0m")


def print_purple(message):
    print(f"\033[95m{message}\033[0m")


def print_blue(message):
    print(f"\033[94m{message}\033[0m")


api = "https://groups.roblox.com"


if os.name == "nt":
    os.system("cls")
else:
    os.system("clear")


fig = pyfiglet.Figlet(font="speed")
ascii_art = fig.renderText(f"TK - claimer")
print_purple(ascii_art)
print_purple(f"V{VERSION}\n")
print_blue("Made by: TK aka Traili your favourite developer\n")


latest_message_id = None
client = aiosonic.HTTPClient()


async def xtoken(cookie):
    headers1 = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
    }
    url = "https://auth.roblox.com/v2/logout"
    response = await client.post(url, headers=headers1)
    xcsrf_token = response.headers.get("x-csrf-token")
    return xcsrf_token


def join(groupid, cookie, xcsrf_token):
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
        "x-csrf-token": f"{xcsrf_token}",
    }
    url = f"{api}/v1/groups/{groupid}/users"
    response = client.post(url, headers=headers)
    return response


def checkgroup(groupid, cookie, xcsrf_token):
    today = datetime.now().strftime("%Y-%m-%d")
    # https://catalog.roblox.com/v1/search/items/details - with params
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
        "x-csrf-token": f"{xcsrf_token}",
    }
    resp = requests.get(f"{api}/v1/groups/{groupid}")
    resp2 = requests.get(
        f"https://economy.roblox.com/v1/groups/{groupid}/currency", headers=headers
    )
    resp3 = requests.get(
        f"https://economy.roblox.com/v1/groups/{groupid}/revenue/summary/{today}",
        headers=headers,
    )
    try:
        members = resp.json()["memberCount"]
        name = resp.json()["name"]
        robux = resp2.json()["robux"]
        revenue = resp3.json()["pendingRobux"]
        embed = {
            "username": "TK - Detections",
            "embeds": [
                {
                    "title": f"{name}",
                    "description": f"Members: {members}\nRobux: {robux}\nRevenue: {revenue}",
                    "footer": {
                        "text": "Made by: TK aka Traili your favourite developer",
                        "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
                    },
                    "thumbnail": {
                        "url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256"
                    },
                    "color": 0x3498DB,
                }
            ],
        }
        requests.post(detections, json=embed)
    except Exception:
        embed = {
            "embeds": [
                {
                    "title": "Error",
                    "description": "Some errored accoured.",
                    "footer": {
                        "text": "Made by: TK aka Traili your favourite developer",
                        "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
                    },
                    "thumbnail": {
                        "url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256"
                    },
                    "color": 0x3498DB,
                }
            ]
        }
        requests.post(errors, json=embed)
        pass


def claim(groupid, cookie, xcsrf_token):
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
        "x-csrf-token": f"{xcsrf_token}",
    }
    url = f"{api}/v1/groups/{groupid}/claim-ownership"
    response = client.post(url, headers=headers)
    return response


def leave(groupid, cookie, xcsrf_token):
    headers = {
        "Content-Type": "application/json",
        "Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
        "x-csrf-token": f"{xcsrf_token}",
    }
    res2 = requests.get(
        f"https://users.roblox.com/v1/users/authenticated", headers=headers
    )
    userid = res2.json()["id"]
    url = f"{api}/v1/groups/{groupid}/users/{userid}"
    response = requests.delete(url, headers=headers)
    return response


async def main(groupid, cookie, xcsrf_token):
    time1 = time.time()
    join1 = await join(groupid, cookie, xcsrf_token)
    claim1 = await claim(groupid, cookie, xcsrf_token)
    time2 = time.time()
    if join1.status_code == 200 and claim1.status_code == 200:
        print_success(f"Claimed group: {groupid}")
        claimembed = {
            "embeds": [
                {
                    "title": f"Claimed group: {groupid}",
                    "description": f"Detection will be send too <#{dchannel}>\nJoined and claimed in {round(time2 - time1, 2)} seconds",
                    "footer": {
                        "text": "made by the only traili there is",
                        "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
                    },
                    "thumbnail": {
                        "url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256"
                    },
                    "color": 0x3498DB,
                }
            ]
        }
        requests.post(logs, json=claimembed)
        checkgroup(groupid, cookie, xcsrf_token)
    else:
        print_error(f"Failed to claim group: {groupid}")
        failembed = {
            "embeds": [
                {
                    "title": f"Failed to claim group: {groupid}",
                    "description": f"i was to slow..? no this cant be\n\nStatus: join -> {join1.status_code} | claim -> {claim1.status_code}\n\nErrors: {await join1.text()} | {await claim1.text()}",
                    "footer": {
                        "text": "made by the only traili there is",
                        "icon_url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256",
                    },
                    "thumbnail": {
                        "url": "https://cdn.discordapp.com/avatars/1137484045501092012/4ea0960613ba5ac4dc18ccc95fe34b70.webp?size=1024&format=webp&width=0&height=256"
                    },
                    "color": 0x3498DB,
                }
            ]
        }
        requests.post(errors, json=failembed)
        res = leave(groupid, cookie, xcsrf_token)
        if res.status_code == 200:
            print_success(f"Left group: {groupid}")
        else:
            print_error(f"Failed to leave group: {groupid}")


async def getgroup(cookie, xcsrf_token):
    global latest_message_id

    headers = {"authorization": f"{DISCORD_TOKEN}"}

    params = {"limit": 1}
    if latest_message_id:
        params["after"] = latest_message_id

    r = requests.get(
        f"https://discord.com/api/v9/channels/{CHANNEL_ID}/messages",
        headers=headers,
        params=params,
        stream=True,
    )

    if r.status_code == 200:
        jsonn = r.json()
        if jsonn:
            latest_message_id = jsonn[0]["id"]
            content1 = jsonn[0]["content"]
            numbers_only = re.findall(r"\d+", content1)

            if "roblox.com/groups/" in content1:
                await main(numbers_only[0], cookie, xcsrf_token)
            else:
                ...

        else:
            ...

    else:
        print_error(f"fail | {r.status_code} ")


async def check():
    global cookies
    while True:
        cookie = random.choice(cookies)
        xcsrf_token = await xtoken(cookie)
        await getgroup(cookie, xcsrf_token)


loop = asyncio.get_event_loop()
loop.run_until_complete(check())
