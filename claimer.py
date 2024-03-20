import socket, ssl, time, random, requests, asyncio, threading, json
from console import *

Host = "groups.roblox.com"
Port = 443

ct = ssl.create_default_context()
cookie = ""
xcsrf = ""

MESSAGES = [
    "People say i am just better",
    "someone said tk is slow?",
    "0.05s claim time go brrrr",
    "well 3x",
    "2 + 2 is 18",
    "4 VPS is fast",
    "this claimer is crazy aint it?"
]

data = json.load(open("config.json"))
webhook = data["webhooks"]

s = socket.create_connection((Host, 443))

async def joinclaim(id, cookie, xcsrf):
    with socket.create_connection((Host, 443)) as s:
        with ct.wrap_socket(s, server_hostname=Host) as so:
                xtoken = xcsrf
                headers = f"Host: {Host}\r\n" \
                        f"Connection: keep-alive\r\n" \
                        f"User-Agent: Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/96.0.4664.110 Safari/537.36\r\n" \
                        f"Cookie: GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;\r\n" \
                        f"x-csrf-token: {xtoken}\r\n" \
                        f"Content-Type: application/json; charset=utf-8\r\n" \
                        f"accept: accept-encoding\r\n\r\n"
                
                datajoin = f"POST /v1/groups/{id}/users HTTP/1.1\r\n{headers}"
                dataclaim = f"POST /v1/groups/{id}/claim-ownership HTTP/1.1\r\n{headers}"
                
                start_time = time.time()
                so.sendall(datajoin.encode())
                so.sendall(dataclaim.encode())
                response_join = so.recv(1024).decode()
                response_claim = so.recv(1024).decode()
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
        xr = requests.post("https://auth.roblox.com/v2/logout", headers={"cookie": f".ROBLOSECURITY={cookie}"})
        if xr.status_code != 200:
            xcsrf = xr.headers.get("x-csrf-token")
    except:
        pass

async def xcsrftoken():
    while True:
        global xcsrf, cookie
        try:
            xr = requests.post("https://auth.roblox.com/v2/logout", headers={"cookie": f".ROBLOSECURITY={cookie}"})
            if xr.status_code != 200:
                xcsrf = xr.headers.get("x-csrf-token")
        except:
            pass
        
async def main(groupid):
    global cookie, xcsrf
    join, claim, time = await joinclaim(groupid, cookie, xcsrf)
    claimstatus = claim.splitlines()[0]
    joinstatus = join.splitlines()[0]

    if "HTTP/1.1 200 OK" in joinstatus and "HTTP/1.1 200 OK" in claimstatus:
        ok(f"Joined and claimed {groupid} in {time} seconds")
        requests.patch(f"https://groups.roblox.com/v1/groups/{groupid}/status", headers={"Cookie": f"GuestData=UserID=-1458690174; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;", "X-CSRF-TOKEN": f"{xcsrf}"}, json={"message": f"{random.choice(MESSAGES)}"})

    elif "HTTP/1.1 200 OK" in joinstatus and "HTTP/1.1 403 Forbidden" in claimstatus or "HTTP/1.1 200 OK" in joinstatus and "HTTP/1.1 500 Internal Server Error" in claimstatus:
        warn(f"Someone already claimed")
        lev = leave(groupid)
        if lev.status_code == 200:
            log(f"Left the group {groupid}")
        else:
            warn(f"Something happend on leave at {groupid}")

    elif "HTTP/1.1 403 Forbidden" in joinstatus and "==" in claimstatus:
        warn(f"Cookied flagged? changing cookie...")
        await changecookie1()

    elif "HTTP/1.1 403 Forbidden" in joinstatus and "HTTP/1.1 403 Forbidden" in claimstatus:
        warn(f"XCSRF Invalidated")

    elif "HTTP/1.1 429" in joinstatus or "HTTP/1.1 429" in claimstatus:
        warn(f"Ratelimited, changing cookie...")
        await changecookie1()

    else:
        fatal(f"Failed to claim {groupid} | {joinstatus} | {claimstatus}")
        leave(groupid)

asyncio.run(changecookie1())
thread = threading.Thread(target=asyncio.run, args=(xcsrftoken(),))
thread.daemon = True
thread.start()
