while True:
    restart = False
    try:
        # WebSocket shit
        ######
        import websockets, json, asyncio, threading
        import os, ctypes, re, shutil
        import time, random, aiosonic

        try:
            import uvloop # type: ignore
        except ImportError:
            pass

        from datetime import datetime
        from curl_cffi import requests
        from typing import List, Dict, Optional, Any
        from colorama import Fore, Style
        from rich.console import Console

        loop = asyncio.new_event_loop()
        
        groupsids: List[int] = []
        groupsid: int = 0
        userid: int = None

        session: requests.Session = requests.Session()
        session.impersonate = "chrome"

        try:
            with open("config.json", "r", encoding="utf-8") as daat2:
                data = json.load(daat2)
                webhooks = data["webhooks"]
                token = data["token"]
                # prefix = "+"
        except FileNotFoundError:
            print("Config file not found. Please make sure config.json exists.")
            exit(1)
        except json.JSONDecodeError:
            print("Error decoding JSON in config file.")
            exit(1)

        class DiscordBot:
            def __init__(
                self,
                token: str,
                prefix: Optional[str] = "--",
                bot: Optional[bool] = False,
            ):
                """Initializes the bot."""
                self.session_id: str = None
                self.heartbeat_interval: int = 30
                self.seq_num: int = 1337
                self.resume_url: str = None
                self.ws: websockets.WebSocketClientProtocol = None
                self.started: bool = False
                self.token: str = f"{'Bot ' if bot else ''}{token}"
                self.prefix: str = prefix

            def send_startup_embed(self):
                embed: Dict[str, Any] = {
                    "username": "TK Claimer 7.0",
                    "embeds": [
                        {
                            "title": "TK Claimer 7.0",
                            "description": "Claimer started. Waiting for groups now.",
                            "footer": {
                                "text": "I feel dizzy 🥹🤭",
                                "icon_url": "https://cdn.discordapp.com/avatars/1058766073568174231/e05509a85a378ed3fc8c7e7274cbfcd7.webp?size=1024&format=webp&width=0&height=256",
                            },
                        }
                    ],
                }
                requests.post(webhooks["logs"], json=embed)

            async def on_message(self, message):
                """Called when we receive a message from the Discord gateway."""
                global groupsids, groupsid, userid
                try:
                    data: Dict[str, Any] = json.loads(message)
                except json.JSONDecodeError:
                    print("Error decoding JSON message:", message)
                    return

                try:
                    self.seq_num = data["s"]
                except:
                    pass

                event_type: str = data.get("t")

                if not self.started:

                    if data["op"] == 10:

                        self.heartbeat_interval = data["d"]["heartbeat_interval"] / 1000

                    if event_type == "READY":

                        self.session_id = data["d"]["session_id"]
                        self.resume_url = data["d"]["resume_gateway_url"]

                        clear()
                        logo()
                        startup(f"Logged in as {data['d']['user']['username']}")
                        startup(f"Resume URL: {self.resume_url}")
                        startup(f"Session id: {self.session_id}")
                        # startup("Session id: " + self.session_id)
                        run()  # spinner

                        userid = data["d"]["user"]["id"]
                        self.started = True

                        asyncio.create_task(self.send_heartbeat())

                elif event_type == "MESSAGE_CREATE":
                    content: str = data["d"]["content"]
                    author: Dict[str, Any] = data["d"]["author"]
                    if content.startswith(self.prefix):
                        if author["id"] == userid:
                            if content == f"{self.prefix}groups":
                                async with aiosonic.HTTPClient() as client:
                                    response = await client.post(
                                        f"https://discord.com/api/v9/channels/{data['d']['channel_id']}/messages",
                                        json={
                                            "content": f"> **TK SB** \n\n> Roblox Groups:\n> {groupsids}",
                                        },
                                        headers={"authorization": token},
                                    )

                    elif "roblox.com/groups" in content:
                        message_parts: List[str] = content.split("/")
                        group_id_index: int = message_parts.index("groups") + 1
                        if group_id_index < len(message_parts):
                            numbers: List[str] = re.findall(
                                r"\d+", message_parts[group_id_index]
                            )
                            if numbers and numbers[0] != groupsid:
                                groupsid = numbers[0]
                                groupsids.append(numbers[0])
                                await main(numbers[0])

                elif data["op"] == 7:
                    self.started = False
                    await self.ws.close(1001)
                    await self.reconnect()

                elif data["op"] == 9:
                    self.started = False
                    await self.ws.close(1000)
                    await self.resume()

            async def send_heartbeat(self):
                """Sends our heartbeat."""
                await self.ws.send(json.dumps({"op": 1, "d": self.seq_num}))
                while True:
                    await asyncio.sleep(float(self.heartbeat_interval))
                    await self.ws.send(json.dumps({"op": 1, "d": self.seq_num}))

            async def resume(self):
                """Resumes the session."""
                async with websockets.connect(
                    self.resume_url, max_size=2**24
                ) as self.ws:
                    payload: Dict[str, Any] = {
                        "op": 6,
                        "d": {
                            "token": self.token,
                            "session_id": self.session_id,
                            "seq": self.seq_num,
                        },
                    }
                    await self.ws.send(
                        json.dumps(payload)
                    )  # never tested it, chance that it works very unlikely
                    log("Resumed")

            async def reconnect(self):
                """Closes the websocket and reconnects."""
                async with websockets.connect(
                    "wss://gateway.discord.gg", max_size=2**24
                ) as self.ws:  # Why not use "wss://gateway.discord.gg/?v=10&encoding=json" stfu. thanks
                    payload: Dict[str, Any] = {
                        "op": 2,
                        "d": {
                            "token": self.token,
                            "intents": 513
                            | (1 << 15)
                            | (1 << 12)
                            | (1 << 9),  # discord i will hate your forever for this
                            "properties": {
                                "os": "linux",
                                "browser": "chrome",
                                "device": "chrome",
                            },
                        },
                    }
                    await self.ws.send(json.dumps(payload))
                    await self.listen()
                    log("Reconnected")

            async def listen(self):
                """Listens to the websocket."""
                async for message in self.ws:
                    await self.on_message(message)  # dont complain

            async def websocket_connect(self):
                """Connects to the websocket."""
                async with websockets.connect(
                    "wss://gateway.discord.gg", max_size=2**24
                ) as self.ws:
                    payload: Dict[str, Any] = {
                        "op": 2,
                        "d": {
                            "token": self.token,
                            "intents": 513
                            | (1 << 15)
                            | (1 << 12)
                            | (1 << 9),  # discord i will hate your forever for this
                            "properties": {
                                "os": "linux",
                                "browser": "chrome",
                                "device": "chrome",
                            },
                        },
                    }
                    await self.ws.send(json.dumps(payload))
                    await self.listen()

        # claimer shit
        ########

        Host = "groups.roblox.com"
        Port = 443

        cookie = ""
        xcsrf = ""

        MESSAGES = ["Catch me if you can!", "Catch me if you can!"]

        data = json.load(open("config.json"))
        webhook = data["webhooks"]

        async def joinclaim(id, cookie, xcsrf):
            start_time = time.time()
            xtoken = xcsrf


            async def send_join():
                response = session.post(
                    f"https://groups.roblox.com/v1/groups/{id}/users",
                    headers={
                        "Content-Type": "application/json",
                        "Cookie": f"GuestData=UserID=-174948669; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
                        "X-CSRF-TOKEN": xtoken,
                    },
                )
                return response
                

            async def send_claim():
                response = session.post(
                    f"https://groups.roblox.com/v1/groups/{id}/claim-ownership",
                    headers={
                        "Content-Type": "application/json",
                        "Cookie": f"GuestData=UserID=-174948669; .ROBLOSECURITY={cookie}; RBXEventTrackerV2=CreateDate=11/19/2023 12:07:42 PM&rbxid=5189165742&browserid=200781876902;",
                        "X-CSRF-TOKEN": xtoken,
                    },
                )
                return response

            async def main():
                response_join, response_claim = await asyncio.gather(
                    send_join(), send_claim()
                )
                return response_join, response_claim

            response_join, response_claim = await main()
            end_time = time.time()
            total_time = round(end_time - start_time, 2)

            return response_join, response_claim, total_time

        def leave(groupid):
            global cookie, xcsrf
            headers = {
                "Content-Type": "application/json",
                "Cookie": f"GuestData=UserID=-174948669; _ga=GA1.1.1287590589.{random.randint(1714508310, 1715908310)}; _ga_BK4ZY0C59K=GS1.1.{random.randint(1714508310, 1715908310)}.1.0.{random.randint(1714508310, 1715908310)}.0.0.0; .RBXIDCHECK=; __utmz=200924205.1720883879.1.1.utmcsr=(direct)|utmccn=(direct)|utmcmd=(none); __utma=200924205.{random.randint(1714508310, 1715908310)}.{random.randint(1714508310, 1715908310)}.{random.randint(1714508310, 1715908310)}.{random.randint(1714508310, 1715908310)}.2; _ga_F8VP9T1NT3=GS1.1.{random.randint(1714508310, 1715908310)}.1.0.{random.randint(1714508310, 1715908310)}.0.0.0; RBXSource=rbx_acquisition_time={datetime.utcnow().isoformat().split('.')[0]}&rbx_acquisition_referrer=&rbx_medium=Social&rbx_source=&rbx_campaign=&rbx_adgroup=&rbx_keyword=&rbx_matchtype=&rbx_send_info=0; RBXSessionTracker=sessionid=b5350dd5-4455-4c7d-bd71-d85d85dc95af; .ROBLOSECURITY={cookie}; rbxas=4b686901874c1ed11c90636c76b19abf24b7dc7bf72284d0065c03b1ec321029; RBXEventTrackerV2=CreateDate={datetime.utcnow().isoformat().split('.')[0]}&rbxid={random.randint(1, 7324119409)}&browserid=1712940919028017; rbx-ip2=1",
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
                "x-csrf-token": xcsrf,
            }
            today = datetime.now().strftime("%Y-%m-%d")

            GamesandVisits, Funds, PFunds, clothes, thumbnail = await asyncio.gather(
                client.get(
                    f"https://games.roblox.com/v2/groups/{groupid}/gamesV2?accessFilter=2&limit=100&sortOrder=Asc"
                ),
                client.get(
                    f"https://economy.roblox.com/v1/groups/{groupid}/currency",
                    headers=headers,
                ),
                client.get(
                    f"https://economy.roblox.com/v1/groups/{groupid}/revenue/summary/{today}",
                    headers=headers,
                ),
                client.get(
                    f"https://catalog.roblox.com/v1/search/items/details?Category=3&SortType=Relevance&CreatorTargetId={groupid}&ResultsPerPage=100&CreatorType=2",
                    headers=headers,
                ),
                client.get(
                    f"https://thumbnails.roblox.com/v1/groups/icons?groupIds={groupid}&size=150x150&format=Png&isCircular=false",
                    headers=headers,
                ),
            )

            thumbnailicon, robux, revenue, groupgames, groupVisits, clothing = (
                None,
                0,
                0,
                0,
                0,
                0,
            )

            if thumbnail.status_code == 200:
                thumbnailicon: str = (await thumbnail.json())["data"][0]["imageUrl"]
            if Funds.status_code == 200:
                robux: int = (await Funds.json())["robux"]
            if PFunds.status_code == 200:
                revenue: int = (await PFunds.json())["pendingRobux"]

            if GamesandVisits.status_code == 200:
                games: list = (await GamesandVisits.json()).get("data", [])
                groupVisits: int = sum(game.get("placeVisits", 0) for game in games)
                groupgames: int = len(games)
            if clothes.status_code == 200:
                json = await clothes.json()

                while True:
                    next_cursor: str = json.get("nextPageCursor")
                    clothing += len(json["data"])

                    if not next_cursor:
                        break

                    url: str = (
                        f"https://catalog.roblox.com/v1/search/items/details?Category=3&SortType=Relevance&CreatorTargetId={groupid}&ResultsPerPage=100&CreatorType=2&Cursor={next_cursor}"
                    )
                    clothing_request: aiosonic.HttpResponse = await client.get(
                        url, headers=headers
                    )
                    json: dict = await clothing_request.json()

            embed: Dict[str, Any] = {
                "username": "TK - Detections",
                "embeds": [
                    {
                        "title": f"Group | {groupid}",
                        "fields": [
                            {"name": "Robux", "value": f"{robux}", "inline": True},
                            {"name": "Pending", "value": f"{revenue}", "inline": True},
                            {"name": "Games", "value": f"{groupgames}", "inline": True},
                            {
                                "name": "Visits",
                                "value": f"{groupVisits}",
                                "inline": True,
                            },
                            {
                                "name": "Clothing",
                                "value": f"{clothing}",
                                "inline": True,
                            },
                            {"name": "Members", "value": f"N/A", "inline": True},
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

            if any(
                [
                    robux >= 100,
                    revenue >= 100,
                    groupgames >= 5,
                    groupVisits >= 100,
                    clothing >= 10,
                ]
            ):
                await client.post(webhookurl, json={"content": f"<@"})
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
            join: requests.Response
            join, claim, time = await joinclaim(groupid, cookie, xcsrf)

            logs = webhooks["logs"]
            detections = webhooks["detections"]
            erors = webhooks["errors"]

            if join.status_code == 200 and claim.status_code == 200:
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
                join.status_code == 200
                and claim.status_code == 403
                or join.status_code == 200
                and claim.status_code == 500
            ):
                warn(f"Someone already claimed")
                requests.post(
                    erors,
                    json={"content": f"Someone already claimed {groupid} / {time}"},
                )
                lev = leave(groupid)
                if lev.status_code == 200:
                    log(f"Left the group {groupid}")
                else:
                    warn(f"Something happend on leave at {groupid}")

            elif join.status_code == 403 and not "Token" in claim.text :
                warn(f"Cookied flagged? changing cookie...")
                await client.post(
                    erors, json={"content": f"Cookied flagged? changing cookie..."}
                )
                await changecookie1()

            elif (
                join.status_code == 403
                and claim.status_code == 403
            ):
                warn(f"XCSRF Invalidatedc (auto fix)")

            elif join.status_code == 429 or claim.status_code == 429:	
                warn(f"Ratelimited, changing cookie...")
                await client.post(
                    erors, json={"content": f"Ratelimited, changing cookie..."}
                )
                await changecookie1()

            else:
                if "maximum" in join.text or "maximum" in claim.text.lower():
                    fatal(f"Failed to claim {groupid} | {join.status_code} | {claim.text}")
                    await client.post(
                        erors,
                        json={
                            "content": f"Failed to claim {groupid} | {join.status_code} | {claim.text}"
                        },
                    )
                    await changecookie1()
                fatal(f"Failed to claim {groupid} | {join.status_code} | {claim.text}")
                await client.post(
                    erors,
                    json={
                        "content": f"Failed to claim {groupid} | {join.status_code} | {claim.text}"
                    },
                )
                leave(groupid)

        asyncio.run(changecookie1())
        thread = threading.Thread(target=asyncio.run, args=(xcsrftoken(),))
        thread.daemon = True
        thread.start()
        ######
        # console shit
        ######

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
                if restart:
                    break
                for spinner in stuff:
                    print(
                        f"{timet()}{Style.BRIGHT}{Fore.LIGHTBLUE_EX}GROUPS {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK}> {Fore.WHITE}{spinner}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} Waiting for groups {Fore.RESET}{Fore.WHITE}",
                        end="\r",
                        flush=True,
                    )
                    await asyncio.sleep(0.0525)

        def startup(object):
            print(
                f"{timet()}{Style.BRIGHT}{Fore.LIGHTCYAN_EX}STARTUP {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
                end="\n",
                flush=True,
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

            versionText = f"Version: V7.0.0"
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
            return (
                Style.BRIGHT + Fore.BLACK + f"[{datetime.now().strftime('%I:%M:%S')}] "
            )

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
            try:
                asyncio.set_event_loop_policy(uvloop.EventLoopPolicy())
            except Exception as e:
                print(e)
            Bot = DiscordBot(token)
            Bot.send_startup_embed()
            asyncio.run(Bot.websocket_connect())
    except Exception as e:
        print(e)
        time.sleep(10)
        restart = True
        continue
