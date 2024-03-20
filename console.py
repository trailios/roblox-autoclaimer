import os, shutil, time, ctypes, pyfiglet, threading, asyncio
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
    "\\"
]

def run():
    thread1 = threading.Thread(target=asyncio.run, args=(wait(),))
    thread1.daemon = True
    thread1.start()

async def wait():
    global stuff
    while True:
        for spinner in stuff:
            print(f"{timet()}{Style.BRIGHT}{Fore.LIGHTBLUE_EX}GROUPS {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK}> {Fore.WHITE}{spinner}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} Waiting for groups {Fore.RESET}{Fore.WHITE}", end="\r")
            await asyncio.sleep(0.0525)

def startup(object):
    print(
        f"{timet()}{Style.BRIGHT}{Fore.LIGHTCYAN_EX}STARTUP {Fore.WHITE}{Fore.RESET}{Style.BRIGHT}{Fore.BLACK} >  {Fore.RESET}{Fore.WHITE}{object}",
        end="\n",
    )

# credits to visions4k for all below this (https://github.com/visions4k/)

def setTitle(title: str):
    ctypes.windll.kernel32.SetConsoleTitleW(title)

def logo():
    columns, rows = shutil.get_terminal_size()
    ascii_text = pyfiglet.figlet_format("TK-Claimer", font="speed")
    lines = ascii_text.split("\n")
    positions = []
    x = int(columns / 2 - len(max(lines, key=len)) / 2)
    for i in range(len(lines)):
        y = int(rows / 2 - len(lines) / 2 + i)
        positions.append(y)

    print("\033[1m\033[36m", end="")
    for i in range(len(lines)):
        print(f"\033[{positions[i]};{x}H{lines[i]}")

    print("\033[1m\033[33;7m", end="")
    versionText = f"Version: 5.3.5"
    versionText_x = int(columns / 2 - len(versionText) / 2)
    versionText_y = positions[-1] + 2
    print(f"\033[{versionText_y};{versionText_x}H{versionText}")

    print("\033[0m", end="")
    print("\n")
    
def clear():
    if 'nt' in os.name:
        os.system('cls')
    else:
        os.system('clear')

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