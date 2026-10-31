import time

_AVVIO = time.perf_counter()  # serve a misurare quanto impiega ad aprirsi la finestra (avvio.log)

import copy
import hashlib
import json
import math
import os
import re
import secrets
import shutil
import sqlite3
import subprocess
import sys
import threading
import traceback
import webbrowser
from collections import deque
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from html import escape
from pathlib import Path
from urllib.parse import quote
import urllib.request

try:
    import tkinter as tk
    from tkinter import filedialog, messagebox, simpledialog, ttk
except ImportError:  # Python senza tkinter: lo spieghiamo invece di far chiudere la console di colpo
    print("ERRORE / ERROR: questo Python non include tkinter (l'interfaccia grafica) / "
          "this Python does not include tkinter.\n"
          "Reinstalla Python da python.org lasciando attiva l'opzione 'tcl/tk and IDLE'.")
    if sys.stdin and sys.stdin.isatty():
        input("\nPremi Invio per chiudere... / Press Enter to close...")
    sys.exit(1)

VERSIONE = "5.41"
AUTORE = "Roby77"
# Logo: un ciak in bianco e nero come quello vero, disegnato per questo programma. Sul tema chiaro è nero con le strisce
# bianche, sul tema scuro è bianco con le strisce nere. Per l'icona della finestra e della scheda del browser, dove non si sa
# se lo sfondo è chiaro o scuro, c'è una versione nera con un filo chiaro intorno.
LOGO_SVG_REPORT = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><g transform="translate(0 3)"><rect x="8" y="30" width="48" height="25" rx="3" class="lg-k"/><clipPath id="fr"><rect x="8" y="22" width="48" height="8" rx="2"/></clipPath><g clip-path="url(#fr)"><polygon points="0,30 8,30 16,22 8,22" class="lg-w"/><polygon points="8,30 16,30 24,22 16,22" class="lg-k"/><polygon points="16,30 24,30 32,22 24,22" class="lg-w"/><polygon points="24,30 32,30 40,22 32,22" class="lg-k"/><polygon points="32,30 40,30 48,22 40,22" class="lg-w"/><polygon points="40,30 48,30 56,22 48,22" class="lg-k"/><polygon points="48,30 56,30 64,22 56,22" class="lg-w"/><polygon points="56,30 64,30 72,22 64,22" class="lg-k"/></g><g transform="rotate(-14 8 20)"><clipPath id="mr"><rect x="8" y="11" width="48" height="8" rx="2"/></clipPath><g clip-path="url(#mr)"><polygon points="0,19 8,19 16,11 8,11" class="lg-w"/><polygon points="8,19 16,19 24,11 16,11" class="lg-k"/><polygon points="16,19 24,19 32,11 24,11" class="lg-w"/><polygon points="24,19 32,19 40,11 32,11" class="lg-k"/><polygon points="32,19 40,19 48,11 40,11" class="lg-w"/><polygon points="40,19 48,19 56,11 48,11" class="lg-k"/><polygon points="48,19 56,19 64,11 56,11" class="lg-w"/><polygon points="56,19 64,19 72,11 64,11" class="lg-k"/></g></g><g class="lg-t" stroke-width="1.7" stroke-linecap="round" fill="none"><line x1="12" y1="38.5" x2="52" y2="38.5"/><line x1="12" y1="46" x2="52" y2="46"/><line x1="32" y1="38.5" x2="32" y2="52"/></g></g></svg>'  # solo classi: i colori li dà il CSS del report secondo il tema
LOGO_SVG_ICONA = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><g transform="translate(0 3)"><rect x="8" y="30" width="48" height="25" rx="3" fill="#111111" stroke="#d0d0d0" stroke-width="1.6"/><clipPath id="fu"><rect x="8" y="22" width="48" height="8" rx="2"/></clipPath><g clip-path="url(#fu)"><polygon points="0,30 8,30 16,22 8,22" fill="#ffffff"/><polygon points="8,30 16,30 24,22 16,22" fill="#111111"/><polygon points="16,30 24,30 32,22 24,22" fill="#ffffff"/><polygon points="24,30 32,30 40,22 32,22" fill="#111111"/><polygon points="32,30 40,30 48,22 40,22" fill="#ffffff"/><polygon points="40,30 48,30 56,22 48,22" fill="#111111"/><polygon points="48,30 56,30 64,22 56,22" fill="#ffffff"/><polygon points="56,30 64,30 72,22 64,22" fill="#111111"/></g><g transform="rotate(-14 8 20)"><clipPath id="mu"><rect x="8" y="11" width="48" height="8" rx="2"/></clipPath><g clip-path="url(#mu)"><polygon points="0,19 8,19 16,11 8,11" fill="#ffffff"/><polygon points="8,19 16,19 24,11 16,11" fill="#111111"/><polygon points="16,19 24,19 32,11 24,11" fill="#ffffff"/><polygon points="24,19 32,19 40,11 32,11" fill="#111111"/><polygon points="32,19 40,19 48,11 40,11" fill="#ffffff"/><polygon points="40,19 48,19 56,11 48,11" fill="#111111"/><polygon points="48,19 56,19 64,11 56,11" fill="#ffffff"/><polygon points="56,19 64,19 72,11 64,11" fill="#111111"/></g></g><rect x="8" y="22" width="48" height="8" rx="2" fill="none" stroke="#d0d0d0" stroke-width="1.6"/><g transform="rotate(-14 8 20)"><rect x="8" y="11" width="48" height="8" rx="2" fill="none" stroke="#d0d0d0" stroke-width="1.6"/></g><g stroke="#ffffff" stroke-width="1.7" stroke-linecap="round" fill="none"><line x1="12" y1="38.5" x2="52" y2="38.5"/><line x1="12" y1="46" x2="52" y2="46"/><line x1="32" y1="38.5" x2="32" y2="52"/></g></g></svg>'
LOGO_PNG_40 = {  # accanto al titolo della finestra, uno per tema (sfondo trasparente)
    "chiaro": (
        "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAHEUlEQVR42tVY32tTaRp+vnNO2pycpEnaNDFGQWEcURELBdeliKDC"
        "jKAUhAoysywOeDGLF7ujXghCqzjrerPSm91OZf+AbVHWm8UL2birXolFpoJY3QsLrWzbaRJsmnNyzvc9ezHnhNimbarSZV8I4SRP"
        "8j7neX997wE20EgKADoAA4AGAJqm4X9mJAVJnaThk3vPotFoCkDIvxQbwammUCNCb9++TXd2dn6ZTCa/TyaTD9rb24v37t17QDIM"
        "QDT6zSdRKJ/PG/UKCCGC79Mkv5BSXiP54Pr163OhUIjZbJZCCJ49e5YkWS6XD/h4/ZMolM/nGypkWVZ6y5YtXwC41tfX9w8p5Tx9"
        "m5mZYSaTYTwel21tbW4ul6vOzMxUSLrVavWCT9BYt0J9fX1BUi8j9O7duwzJL2dnZ69t3bo139bWVujo6GA0GuXY2BhJ0rZtSbJ6"
        "+vRpRwghs9msBOAODQ3ZJD2f/9+aJkhSWympt2/fntF1/djr16+/J/lP13ULJHnz5k3qus5sNksA8uLFixWSnk9O3r9/3zYMw81k"
        "MmxtbeWJEydIklLKKslx13VPfFCISW46c+bMMdM0f59Op/+l63qxt7eX9fbixYuqZVlOMpn0otGo3LZtW3V+ft5xXddTStG2bXZ1"
        "dTESiTCVSlXD4fD46OjoDyR/Zdv2500XRgAk+QuSf5BSPiwWi/N79uxhLBZjR0cHE4kEX716VSXpOo7jkfR6e3sdXx0PAEdHR+v5"
        "V4eHh58BGM7lcl/HYrGGhEhqzZJLkywH/37hwgUCkNls1gXgXb161fFD55L0bt++LTVN46ZNmxgOh3ns2DGb5I+u694i+TXJz+ur"
        "OrD+/n7DTyOtKQXrCCY8z/uPlNJ9+vSpbZqml0qlZDgcdnfu3OksLCzUpFlcXOSuXbsqpmn+2NnZ+YNlWV/duHFjx1KHPjmjbnqI"
        "D+1pmv/+d5Lu4cOHyy0tLUyn07Qsi/l8niQd13WfkRzK5/OnAXzWaFT56hj+f4pP1XQN//27u3fvEgDT6bRtWdaz7u7uP5E8XalU"
        "PmugTk2h/v5+7ZNPgwZhjuzdu/e37e3tv+7q6trRoPSNwcHB1sHBwdaRkZGWOrUMf6K89zp06JBRj1kJFxwePth0Xa8ptjTpVxw7"
        "onkxV8KKpSoKITg3N7fLsqxfSimVZVliYmJC7tu3T0QiEREOhzE9PY2enh716NEjIaUUrusiHA5jYmJCrRfX0tLCYrEI27YfA3jt"
        "c+JKg1+QDJP8d1CtSikeP36clmUxk8nQsizmcrnaKPtYnGma3LFjBx8/fjxB0lzxVFOXg+3VarVI0i0Wi/aBAwdsAG4mk3FN0/Q2"
        "b97sjI+P2/6Qd0l6hULB+VBcNpu1nz9/7pIsTk5OttdzaUhwcnKyneRPhUJB9fT0VING7Lccb2xszA36IEkWi0Wvp6fH/QhclaSy"
        "bfsnkmsTJBmdmpqaP3LkCIUQKpPJMBqNcvfu3d6bN2/c+nAVCoWa04/AKR9WJBldSnApU03TNNXd3X1qfHz8z9FoNKGUEo7j4Ny5"
        "c2r//v16uVwO9gjeunVLPXz4UE+lUvA8D47jcL24hYUF1dbWVjx69OhvYrHYX0lqQgi1IkEAtCxryDTNb6SUAoAuhEClUkGlUoGm"
        "aSB/LjLTNBGJRCClrLWKD8BJAFRK/QXAtz6nhgQFACaTyTiAtwBMv9xFsH3VOxVCQCkFpdTSEKwXRyGEUEpVlFLZQqFQqm81y06w"
        "SilN07QKALO+OTdqqIGTtRrvajgA8DwPACpKqWWglY7YgiTm5uY2ZD1NJBIQK4ySZQTj8ThKpRJaW1sxPDyMdDoNKeWqCpCEpmko"
        "l8vB8gSl1KqjTikFXdcxMzODy5cvw3Gcmu9VCZZKJQghQBJTU1OoVCprOgvInTp1CgAwMjJSI7nWTc3Pz4MkhBDLyK0YYiEEXNfF"
        "lStXmh70JJFIJAAAly5dqn22jhA3xBurOU2lUk05MQwDs7OzsCyrpmhnZ2eQ/GveXNB+msrB+hAEebKWLa3S4LqZB0NSylqI11Uk"
        "kUgEd+7cQS6XWzMHAxVSqRQA4ODBg9B1fVX1gxycmprCyZMnsbi42HyRaJoGx3Fw/vx5mKa5ZpgNw0ChUMDAwAAAYGBgAMlkcs0Q"
        "BxPFcRxomtZ8kQR3ODY2tmol1hNcXFzE9PQ0AODJkyeIRCJN5aCmaTBNs/kc9E8SDPpZM2YYBmzbRiwWqzmNxWJNEQx64s+ulx+z"
        "lhEMhUKulDIkhKBSSjazzEgpIYTAy5cv38vJZtT3DwY6yVAoFHJX3Ul8MiqRSPxR07TfrXdkBe2imcpvoOLNYrH4XcABaz12jcfj"
        "3YZhxD3PY7PLt2EY9cO/qW3XMAzheV6pVCo9Xe+Dyo02sV4i2gYSZX1Y/6/svwMjlhbRnsn2AAAAAElFTkSuQmCC"),
    "scuro": (
        "iVBORw0KGgoAAAANSUhEUgAAACgAAAAoCAYAAACM/rhtAAAHmklEQVR42s1YS2wU2RU9r7pc7a5uXO12u9rljwB5jGQjG6yASRDI"
        "EiwYLyKBwIshEyGxQCSrKPw2CIvPRJEXIyFBMpMoK3bAgg2RV7FJAMkCC8QIgRDjjYEAttvd7mp3/U8WdDvG/4bA5EoldZdu1T3v"
        "3Hvuu68EPqORFAAkAAJAIIQI8BObABACIBd/zwecJFkxB/ynZ4hkiOQCQEIIdHR06KZpflkoFL4pFApDlmVl9u/fPwSgsghQfBKG"
        "uru75cUY6Ojo0KuqqvYYhnEBwNCFCxcmOMeuXLnCUCjEhoaGnxcfCf1PGOru7l4qZXomk9lD8sLNmzf/EY1G07W1tYxGo2xvb+fU"
        "1BRN0/Tz+bz7+vVrp7m5uRCLxdyamprjxVfIZTN09erVEMlFGdJ1PaWq6pcbNmy4MDExMVgoFKaCICBJ9vT0UFEU6rruh0Ih58aN"
        "GzZJf2JiwifpHjt2zALgpVIpapp2oxyAUqmohXgfUy6XS5Hs2bZt2zeqqt7SdX1KCMH+/n6SZDabJUn/0qVLBQBeXV2dL4Tw9+3b"
        "Z/m+72YyGZLk8PAw16xZw0Qi4SQSiR/i8fgvy06xJEkAUHft2rUekn/IZrP/JJm5desWNU1jMplkJBJhV1eXY1mWncvlvEKh4L98"
        "+dJpamqyq6qqvHg8zvr6er548YIkOT097Xie98Phw4e/B/Dr9evXbyhHGAIAEonEtmQy+cdoNPqvdevWpUsvJ8mZmRl2dnY6iqK4"
        "tbW1nqIo3sDAgE3SnZyc9EjyyJEjlCSJdXV1VBTFOX78+EOSf8lms19bljULaF52pFWBi0ajejwez6dSKQohePnyZZL0x8fHXZJe"
        "f3+/DcAzDMMF4B06dMifq8qhoSFLVdVHNTU1f43H418nk8kNodDCrPX19cnFMpJWy6AAAE3T4jU1NW/C4bDb3d1t2bbtZTIZ33Vd"
        "d3R01NZ1ndXV1dQ0jc3NzRwdHS24rvsol8t973ner86dO9eyWMDBwUG5KDTpY3qdBADxePzv4XDYvX37dp4kHcchSR48eJCSJNm6"
        "rj9UVfW73t7er0h+sWCl71JXNkOrMbkojN+fPn26pErLdd2HT548+VM0Gv2qsbHxi8UeLDHU19cnfYrdYM7iBQCoT58+/V06nT70"
        "/PnzlpL0ZVlGKBQCSfnixYvhixcvhnt7e5Vi05YByMUd5b1rcHBQnsPokn7F9H8Q6p/E7z1xzPvPlpaW1nw+/4tQKBSMjY2Jrq4u"
        "/+7du8KyLJHP56HrOh48eBBs375dqKoqKisr8erVK3R1dQXl+OXzeeH7PqurqwHgjhDiOUkhhOBSYMXatWsr4/H4j7quMxqNsr6+"
        "nsPDw3O7CS3LYk9PD6PRKFOpFGOx2Ef77dmz51ljY2NkualGAEBVVVUimUxmVFV1DcOwRkZGrGIjdm3b9t6+fWt3dXVZANxUKuWq"
        "quoZhmF/qN/4+Li1detWVwiRaWtrSyyR2f/ebGxsTCiKMmkYRjAyMuKQ5OTkJIMgYDqd9nbs2OGGw2E2NDRQVVUahuHdv3/f/VC/"
        "nTt3OuFwONB1fbKqqmp5gEIItLW1xVpbW9P37t0jySCdTtOyLD579sxrbW11AbCyspIAaBiGd+/ePZckP8IviEQi1DQtU1tbG5sP"
        "cO54wyAIJCGE+ejRo6Pt7e1/zuVy8YqKCgDAwMAANm3aJO/atQue58G2bR49ehRbtmyRs9ksin4sx6+jo0PevXt3kM1mp4aGhn47"
        "NjZm9vX1SWfPng0WVXGxF9G27e8kSTrsOI4AECKJSCSC+fuq53mYmZmZvf+Bfj4AAvgbgN8UM7kQYEne6XRak2X535WVlRHbtlnq"
        "3kEQIAiC2T5GEpIklcayWSvXDwAVRRGO4xSCIDASiUR2bqtZMMFWV1dLpmkWgiCI+L6/2Ni/WJAP9is171AoVNA0bcFuIi+37Wma"
        "9lnOpo7jLKncBQBLhew4Dk6dOoU3b95AUZT3GFmKMVVVAQAzMzMrbmlCCDiOg1QqhfPnz0OSJGSzWayKQZIQQqC+vh7hcBiyvPxZ"
        "xvd9RCIR3Ljx7uyzd+9eFAoFLDaszhdPTU0NhBBLErAgsqZpME0TiqLgxIkTZaXKNE0AwJkzZ8pOseM4i5aUvFzKpqenVzV9eJ4H"
        "TdOQz+dnRZHNZldkvhQnHA4vPaQuVyNCiPdaxnJB5qo0CAKQXFXdSpK07PuXFIllWThw4ADGxsYQDoeXDVYKNDk5CQC4c+fOigsT"
        "QsC2bTQ1NeH69euQZXlRkSxo1CSrTdP8UZbl6sePH7NQKIj5TXYxkcRiMfT39wMATp48CdM0VxRJEASIRCLcuHGj8DxvKhaLNQsh"
        "ppZt1HNXuHnz5hWDAIDruqioqIBhGACAzs7O2Xsrme/78DyvrBoU7wgl8vl8WSLJ5XKzzJimuWqRKIqC4n4sVgPQBVAhSRIlSfJX"
        "c+qXJAkk0dLSsurin5OpQJKkEICKYuxlVyMV+9m3JOn7PoMgWPVVsnKe8f13HydM0/x2LgYsN7kCQD6f/5miKJrnefQ875OcdWVZ"
        "pizLwnGcbDQaHSn3Y/dntaViihXS/bmA8v/hi/8H2X8Aok2hOq01I3AAAAAASUVORK5CYII="),
}
LOGO_PNG_40["colore"] = LOGO_PNG_40["scuro"]  # il tema Colore ha lo sfondo scuro: stesso ciak chiaro
LOGO_PNG_40["verde"] = LOGO_PNG_40["scuro"]   # anche il tema verde usa lo stesso ciak chiaro
LOGO_PNG_64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAEAAAABACAYAAACqaXHeAAAONUlEQVR42u1be2xVVZf/7X32Ofdxbm/pm4IQeSQg0Aq04nwC4ZHo"
    "HzKjUQN+Ucwk/qERkmEyfgmaGFvCQx6JgtEx/jMhPuI3rYIE4xedkPajfMqjvQp9KJ2p0N62pECft/f23nv23mv+mHuYWitt6a2W"
    "5NvJSW56zj5n/dZav7XWXnsXuIsHEbGKigqDiAQRGVVVVaKiosKYyDvE3Qa4srKS5+XlsRs3bhBjTAFQoz3HGKO7XgFjAT506JC9"
    "evXqpbZt/8Hn8/1BCOF0dXW9zxg7M14lsOkKeP369Zoxpoffb2hoCEQikaV+v/8hn8+31jTNUsMw5nDOEQ6HYZomgsGgGhgY2FBS"
    "UnKmsrKSb9myRU1bD/gVwLcE/uGHHzKIaJnW+iEp5VopZens2bNnM8bQ0dGBS5cu4cKFC1RfX68aGxvpk08+ScybNy8wMDDwr4yx"
    "GiKaXhQYC/CHH34YXL58eRHn/CEp5dqhoaESIcQsv98Py7KQSCSwd+9eHQqF9NWrV1lfXx/jnPNEIiGeffbZ5KZNm3xtbW0A8MCV"
    "K1e8jLH4WFQQvyfgioqKzDlz5hTZtr3a6/WuNU1zZSwWK/T5fDAMA5xzWJZFXq9XBYNB7Nu3T77//vse27aFEAKZmZnQWiMrK0vt"
    "37+fAzBM0yQhxD0DAwNLAIQqKyv5aIFyShQwFuCWlpbM3t7eYiHEmhSHV1iWNZOI0NHRgfPnz+ORRx5RBQUFZFkWE0LwVJwSLS0t"
    "zsGDB82cnBzGGINSCowx9PT04PDhw+qee+6xiAjBYFANDQ2JaDS6GkAoLy+PTVkQHCtoXblyZUYsFismotUpDq/MyckpME0TbW1t"
    "tzjc1NSk6urq2KZNm+SxY8dMADz1fiilIISgp556yjlx4oSVnZ0NKSU454hGoygqKnLOnDnDDcMwOOdgjMm2tjaju7u7YuXKlX8k"
    "IiOVPSbvAWNZ+Pjx4zPmz59fzDlfI6Vc29vbu8KyrAK/3w/GGILBII4ePeocPXqUdXV1sd7eXk5EzDAMkZGRod555x0DAFdKwTAM"
    "aK0hhMDJkyedzz//3MzJyYFSCpxzGIYBpRQdOnSILMtyix9KJBIKgHB5X11dze44CI4HcEFBwf22ba/xer1rPB7PSqVUPmPsZxz2"
    "+/3K5/OxtrY2VV5ezhOJhPD7/QgGgzBNE11dXXjttdfUrFmzLBc8EYExhlgspl599VUeCAQYACilIKVENBql559/PrFu3ToRiURk"
    "LBYzkskk01p7YrEYOOf/DgA3btygO1JARUWFMbLwaG1tzerv7y8mojWpoLXC4/HkK6Vw7do11NTUoKCgwHnyySfZcA4TkWCM0csv"
    "v6yGhoZETk4OkskkAKC/vx8lJSXOtm3bDK01OOdwgQohsH//ftXY2Gh5PB7E43GdlZVF8+bNo2XLlhnbt2/3dnR0IB6PY2hoCEqp"
    "Do/HUxuNRt994IEHasrKysasA9ivWZ4xRs3NzUGl1MpkMrkGwBop5YpAIJBv2zZaW1tx8eJF1NbW6vr6et3S0sLi8TiFQiFatGiR"
    "6VpQSgkhBL744ovk448/bubk5DApJQDAMAz09fXRV1995WzcuPGW9d1x8eLF5MMPP4yFCxfy+++/3ygtLWXFxcWYNWsWAKCnp6dT"
    "KVUnhKgRQvwtNze3Pi8vLzKRcliMAp4zxnRdXd2/OY7zJyIqzMjIAGMMHo8H4XDYefrpp9He3s77+/u51pr7/X4eiURw5MiR5KJF"
    "iywXNBG5wUrt3LmT+3w+5v7NNE1cv34dW7dudTZu3GimFKKVUjQ0NETRaNTo6+uzjh07hgULFkApBcdxOhzHqbt582bN4ODg3wA0"
    "rFmzJjLScwHgdoEPt3N7AKivr1/f0tJCP/30E3V1daloNOokk0lJRHLLli0JAJSdnU05OTmUn59Pfr+fSktLnUQiIZVSpLUmIiIp"
    "JRER7d69O8E5p4KCAgoGg+Tz+QgA5ebmJsPh8FAkEnE6Ozt1OBymq1evUktLC126dImamprCzc3Nn3///fcvnz179h8qKioCoxnM"
    "XQUS0YSz2s88wM2ZUsp/NAxDFxYWSsuyrJRX4OTJk8lPP/3UzM/Ph5QSWmswxuA4Dh08eJAsyxJulHbd+fLly87u3bsNxhj6+vp0"
    "VlYWzZ8/n5YtW2Y8+uijpmmaZldXF6LRKLTWYcZYnRDitMfj+WZoaKhhyZIl0ZFGchdHmzdvdgOzvtNUPmoQZIx1KqW4lJKbpgmt"
    "NeLxuHrllVe41+tlSikQEYQQ6O7uxnPPPeds2LDBHM7hVJpSZWVlcvHixea6deuwYsUKXlxcjJkzZ4KIEIvFwp2dnbVer/e01+v9"
    "JhgMNhYWFo4FWKWzePuZAtyUIYQ4E41GMTg4aLhl6Ztvvqmampqs/Pz8WxHacRzk5uaqN954gwFghmFoKSXF43GKRqNicHDQ2LFj"
    "h+/ee++FlBJKqdZkMlnb3d1dMzg4+E13d3fjY489FvstAd82C7iRs6Ojw3/t2rX/zsvLmzV37ly0tLQ4q1at4owxQ0qJRCIBrTWS"
    "yaQ+fPhwYvv27eb169eF1hpaa0gpEYlEAKDVtu0L0Wi0ZnBw8JvGxsamF198cSzAhN9wiBGuTxUVFcbs2bNjoVCojohmaq3ltm3b"
    "0NPTY/j9fh0MBmnp0qW0fPlysWrVKr5+/XpfOBzGwMAAtNZXhRAXOOenPR7Pt7ZtN82dO3doNMDr16/XAGiqLTzhGOAGQq31XzIy"
    "Mv7p1KlTqq+vz9y+fTtKS0t5UVERZs6cCaUUlFJX+vv7LxiGcdq27W8XLlzYxBiLT2fA4ymEGBHh4sWLfsbYsUAg8IjX64XjONBa"
    "/+Q4zoV4PH56cHDw26+//vqHXbt2xUfQyKiurv7dXDpty1pXGZcvX360oaHhn2tqau4/cuSIZ+SzVVVVora21iQio6ysjBMRmyYX"
    "JyJjUt5xJ4XFNDbmxBZDqVqe6urqtnq93ucTiURQa03D7weDQTDGRqsjCACLRCLQWo96X2vNpmg+CSGIc95//fr1/2CM/bmsrIzv"
    "2rVLT2QxZDDG1HfffbclMzPzP93lLWMMbqPR4/Ggrq4OjuP8TAj3mXg8jpKSEliW9QvFTvV8pRSCwSAWLFiAnp6eLStWrKgcqzHy"
    "i/oaAEKhUFVra6tyHCdORIqIpOM4ioicPXv2xIQQTkZGhrRtW9q2LQOBgAwGgwqAs2/fvphSyiEiOfz6rea/9dZbkZs3b+rz589X"
    "Dcc0Id7U1taea29vJyKSWmtyHIeISO/ZsycOQGdnZ1N2djZlZWVRdnY25ebmEmNMHzp0KE5EevjC6HeY77S1tVFtbe258cSCURUQ"
    "CoW+dRUw8uO5ubm/+DiAW8I7jnNb4ad6vpRShcNhCoVC305KAeFwmKSUajLCp5bFv+l8IpLt7e2TU0Btbe25trY2IiK5d+/eOACd"
    "l5dHruu51+2ET/3Wv8N82d7efscU4ABw7ty56t7eXjpw4EAMgM7MzKRAIEC2bVMgEKCMjAwyTVMfPHgwTkQ6mUzeEtq1XDKZ1GVl"
    "ZXEAOhgMTvl8pRQRETmO46QoUDW82TOuOqCyspKllsVv37hx44HFixd7P/vsM+a2udx0o7WGx+NBSUmJ1draykbmZMYYEokE7rvv"
    "PuvEiRNseBqbyvlaa4pGo1wIERNCvH1HTVEAaGxsNKWUjXl5eQubm5t1LBbjI4UkIkSjUTDGMNo9zjls2x61oJmK+Vpr+Hw+vWTJ"
    "Eh6JRP6nubl56ebNm51hBdbYHlBdXW1s2LBB1tbW/mn27NkLy8vL5UcffSTcbs/wXVf3w6NVdO6zvyb8VMxPFUL8mWeeka+//vpC"
    "KeXLjLE3qqqqBAA5Xg/gjDH9448//rWzs3Ptpk2btGVZhrthMZ2HWwkmk0n15Zdf8sLCwtOLFy9e72Ia+fyvVUeU6ut5UlvQGM7/"
    "ab74gRACnHP09vYywzC8wzGNVwH//wDnIKK7AvxwJbjxI60HJFK7r3cF+Em1xX+NW9Fo9Nae3nQdlmXBtu30KoAxhmQyiZUrV2LR"
    "okW3NkQm3ZAU//d5d69wspbnnOPy5cuor68ft3xiPOBTuz947733UFxcPK094NKlS3jwwQchhBiXEsR4OWVZFl566aW0eYDWGgcO"
    "HAAA7Ny5c1wBa7weYFkW3N2rtFCAiGCaJkKhEM6ePZsWS2mtUVZWBgD44IMPJq2AkTFgvLQSE9GwbdsIBAJpEdQ95wMAM2bMuBUP"
    "pm0WcK2WrqGU+tnvdKbXibxrQn6XLjedyjFRGSdEgWg0+osu7WQo4LpqOtKgO5LJJPx+f3oVwDlHIpHAu+++i40bN2LkWZ475eqc"
    "OXMAAA0NDZOmgCvTqVOnsGPHjnF7wvT36Snk/7g9wO28bNu2DR6PJ20UaGxsBAAsW7YsbVkgkUjAtm0kEon0rwUyMjLSmglcawkh"
    "0qYAy7ImlAYnRIF0gp+qMVEZxd0k7FQMMR4h3QVRupsiGRkZUxYI3QbpnSqAASCtdTwzM1O7B5Qnm/qGC+g4Dk6ePAkAcBxnwtwd"
    "K8BqrTFjxgytlIoPxzQuBVRXV3MAOhKJfF1cXLxu69atiY8//hiGYTBKk5SGYeCFF14AAHi9XsTj8XQplymlaOvWrbKoqMjT2tr6"
    "9XBMo1l6tCKFlZeXsyeeeMLHOf9LYWHh2vr6egwMDKS1HHbflc5YoLVGMBhEUVERrl27dlpr/ejx48eHysvLabR9AXabSo0xxqiq"
    "qsqbnZ39L7ZtP0xEmSkHmK6NQUod5uiPRCL/1dPT8/aGDRviE/lHyl8o4W6vDCeNgYhYVVWVSJ26YnfJxVMy3/UG/Pv4+5ji8b9Q"
    "d6m+xGs1EgAAAABJRU5ErkJggg==")  # icona della finestra e della barra di Windows
URL_FFMPEG = "https://ffmpeg.org/download.html"  # dove scaricare FFmpeg (include ffprobe)
EMAIL_CONTATTI = "roby77dopa@gmail.com"
URL_GITHUB = "https://github.com/Roby77ita/Media-Directory-Lister"  # per suggerimenti e segnalazioni (finestra del pulsante «?»)
MAX_RECENTI = 10  # quante cartelle scansionate ricordare nel menu a tendina
# file ignorati: non compaiono nel report né nei totali
ESTENSIONI_ESCLUSE = {"ini", "log", "txt", "jpg", "m3u", "png", "info", "pdf", "cue", "nfo", "m3u8", "sfv", "md5", "accurip", "jpeg", "toc", "avif", "gif", "bmp", "tif", "tiff", "webp", "svg", "heic", "ico", "raw", "cr2", "nef", "arw", "psd"}  # per estensione (maiuscole/minuscole indifferenti)
NOMI_ESCLUSI = {"thumbs.db", "folder.jpg", "cover.jpg"}  # per nome completo del file
IS_WIN = sys.platform == "win32"

# Estensioni considerate Â«immagineÂ»: usato dal filtro Â«Solo immaginiÂ» del report e dall'opzione
# Â«Includi le immagini nel reportÂ» del profilo (che le toglie da ESTENSIONI_ESCLUSE).
ESTENSIONI_IMMAGINE = {"jpg", "jpeg", "png", "gif", "bmp", "tif", "tiff", "webp", "svg",
                       "heic", "ico", "raw", "cr2", "nef", "arw", "psd", "avif"}

# ffprobe viene lanciato solo sui file con queste estensioni (evita chiamate inutili su .txt, .jpg, ecc.)
ESTENSIONI_MEDIA = {
    "mp4", "mkv", "avi", "mov", "wmv", "flv", "webm", "m4v", "mpg", "mpeg", "ts", "m2ts", "3gp",
    "mp3", "flac", "wav", "aac", "m4a", "ogg", "opus", "wma", "aiff", "ac3", "mka",
}


# id di tutte le colonne disponibili nel report (i titoli sono nelle traduzioni: "col_<id>")
COLONNE = ["nome", "artista", "album", "titolo", "anno", "traccia", "tipo", "est", "dim", "data", "durata",
           "ris", "colore", "hdr", "dv", "fps", "cv", "ca", "canali", "formato", "qualita", "copertina", "tracce", "bitrate_video", "bitrate_audio"]

# come si raggruppano le caselle delle colonne nella finestra (chiave del titolo del gruppo, colonne in ordine di
# visualizzazione, 3 per riga). Vale solo per la finestra: nel report le colonne escono nell'ordine di COLONNE.
# Una colonna nuova non elencata qui compare comunque, in coda al primo gruppo.
GRUPPI_COLONNE = [
    ("gr_file", ["nome", "tipo", "est", "dim", "data", "durata"]),
    ("gr_tag", ["artista", "album", "titolo", "anno", "traccia", "copertina"]),
    ("gr_video", ["ris", "fps", "cv", "colore", "hdr", "dv", "bitrate_video"]),
    ("gr_audio", ["ca", "formato", "canali", "tracce", "qualita", "bitrate_audio"]),
]

LAYOUT = ("verticale", "orizzontale")  # disposizione della finestra del programma (menù in alto)


# ---------------------------------------------------------------- traduzioni
# Per aggiungere una lingua: copia il blocco "it", traduci i valori e aggiungila anche a LINGUE.
# Prefissi: col_/th_ = titoli delle colonne (finestra / intestazioni del report), r_ = testi fissi del
# report HTML, j_ = testi usati dal JavaScript del report, tutto il resto = finestra del programma.

LINGUE = {"it": "Italiano", "en": "English"}

TESTI = {
    "it": {
        "sottotitolo": "v{v}  ·  Report HTML",
        "cartella_titolo": "Cartella multimediale",
        "sfoglia": "Sfoglia...",
        "nota_recenti": "Nel menu a tendina trovi le ultime cartelle scansionate.",
        "mostra_come": "Nel report mostra la cartella come:",
        "percorso_completo": "Nome e percorso",
        "solo_nome": "Solo nome",
        "usa_cache": "Usa la cache (rianalizza solo i file nuovi o modificati)",
        "svuota_cache": "Svuota cache", "usa_cache_breve": "Usa la cache",
        "svuota_cronologia": "Svuota cronologia", "cronologia_titolo": "Cronologia sorgenti",
        "cronologia_conferma": "Svuotare l'elenco delle cartelle recenti del menu a tendina?\n\nLa cartella scritta ora nella casella e quelle salvate nei profili non cambiano.",
        "cronologia_svuotata": "Cronologia delle cartelle svuotata.",
        "colonne_titolo": "Colonne del report", "colonne_conteggio": "{n} selezionate",
        "gr_file": "File", "gr_tag": "Tag musicali", "gr_video": "Video", "gr_audio": "Audio",
        "layout_verticale": "Layout verticale", "layout_orizzontale": "Layout orizzontale",
        "aspetto_menu": "Impostazioni", "lingua_menu": "Lingua", "tema_scuro": "Tema scuro", "tema_chiaro": "Tema chiaro", "tema_colore": "Tema colore",
        "tutte": "Tutte",
        "nessuna": "Nessuna",
        "attesa": "In attesa...",
        "genera": "Genera report HTML",
        "annulla": "Annulla",
        "versione_ff": "versione {v}",
        "versione_nd": "versione non rilevata",
        "percorso_ff": "Percorso: {p}",
        "ffprobe_mancante": "ERRORE: ffprobe non trovato! Mettilo nella cartella del programma o nel PATH.",
        "errore": "Errore",
        "info": "Info",
        "cartella_non_valida": "Seleziona una cartella valida!",
        "nessuna_colonna": "Seleziona almeno una colonna!",
        "salva_titolo": "Salva report",
        "ricerca_file": "Ricerca dei file...",
        "ricerca_file_n": "Ricerca dei file... {n} trovati",
        "analisi": "Analisi: {n}/{totale} ({pct}%)",
        "analisi_stima": "Analisi: {n}/{totale} ({pct}%) · circa {tempo} rimasti",
        "cartella_vuota": "Cartella vuota.",
        "annullata": "Operazione annullata.",
        "salvataggio_fallito": "Impossibile salvare il report:\n{errore}",
        "errore_imprevisto": "Errore imprevisto:\n{errore}",
        "report_salvato": "Report HTML salvato!",
        "dettaglio_cache": "  ·  dalla cache: {h}, analizzati: {a}",
        "completato_aperto": "Completato! Report aperto nel browser.",
        "completato_salvato": "Completato! Report salvato.",
        "salvato_titolo": "Report salvato",
        "apertura_fallita": "Non è stato possibile aprirlo automaticamente.\n\n{percorso}",
        "cache_titolo": "Cache",
        "cache_svuotata": "Cache svuotata: la prossima scansione analizzerà di nuovo tutti i file.",
        "cache_gia_vuota": "La cache è già vuota.",
        "cache_errore": "Impossibile svuotare la cache:\n{errore}",
        "apri_config": "Apri cartella configurazione",
        "scarica_ffmpeg": "Scarica FFmpeg (include ffprobe): {url}",
        "tipo_etichetta": "Tipo:", "tipo_generale": "Generale", "tipo_musica": "Musica", "tipo_film": "Film",
        "tipo_titolo": "Tipo di profilo",
        "tipo_testo": "Il profilo diventa di tipo «{tipo}».\n\nVuoi anche impostare le colonne predefinite di questo tipo? Le colonne attuali del profilo verranno sostituite.",
        "profilo_titolo": "Profilo",
        "profilo_nota": "Cartella, tipo, colonne, esclusioni e opzioni si ricordano per ogni profilo.",
        "profilo_gestisci": "Gestisci", "profilo_nuovo": "Nuovo profilo...",
        "profilo_elimina": "Elimina profilo",
        "escl_bottone": "Esclusioni ({n})...",
        "nuovo_titolo": "Nuovo profilo", "nuovo_testo": "Nome del nuovo profilo (parte da una copia di «{nome}»):",
        "nuovo_nome": "Nome del profilo (per esempio Animazione):", "nuovo_tipo": "Tipo:",
        "nuovo_modello": "Parti dalle colonne predefinite del tipo (altrimenti copia quelle attuali)",
        "nuovo_usa_corrente": "Usa la cartella corrente",
        "nuovo_nota": "Esclusioni e opzioni attuali vengono copiate nel nuovo profilo; la cartella no: dopo la creazione scegli la sua cartella e premi Salva.",
        "profilo_auto_generale": "Cartella nuova: non so cosa contiene, quindi uso il profilo «{nome}» (tipo Generale).",
        "profilo_auto_noto": "Questa cartella è quella del profilo «{nome}»: passo a quel profilo.",
        "elimina_ultimo_testo": "«{nome}» è l'ultimo profilo.\n\nEliminandolo ne viene creato uno nuovo, «Generale», con le impostazioni predefinite (tutte le colonne, esclusioni predefinite). La casella della cartella resta com'è. Continuare?",
        "nuovo_crea": "Crea profilo", "profilo_salvato_breve": "✓ Salvato", "profilo_modifica": "Modifica profilo...", "modifica_titolo": "Modifica profilo", "modifica_nome": "Nome del profilo:", "modifica_cartella": "Cartella sorgente del profilo:", "profilo_salva": "Salva", "profilo_salvato": "Profilo «{nome}» salvato.",
        "elimina_titolo": "Elimina profilo", "elimina_testo": "Eliminare il profilo «{nome}»?",
        "profilo_ultimo": "Deve restare almeno un profilo.",
        "nome_vuoto": "Scrivi un nome per il profilo.", "nome_esiste": "Esiste già un profilo chiamato «{nome}».",
        "nome_lungo": "Il nome è troppo lungo (massimo 40 caratteri).",
        "escl_titolo": "Esclusioni del profilo «{nome}»", "escl_estensioni": "Estensioni escluse",
        "escl_estensioni_nota": "Separate da spazi, virgole o a capo; il punto è facoltativo (txt oppure .txt). Maiuscole e minuscole sono uguali.",
        "escl_nomi": "Nomi di file esclusi", "escl_nomi_nota": "Un nome completo per riga, per esempio thumbs.db o folder.jpg.",
        "escl_ripristina": "Ripristina predefinite", "escl_salva": "Salva",
        "escl_ignorate": "Voci ignorate perché non valide: {voci}",
        "contatti_titolo": "Suggerimenti e contatti", "profilo_generale_nome": "Generale", "tema_sistema": "Tema sistema", "colonne_predefinite": "Predefinite", "search_help": "Cerca file... (es. ext:mkv size:>10GB year:2020 res:4k hdr:sì durata:>60)",
        "contatti_testo": "Hai suggerimenti, idee per migliorare il programma, richieste di modifica oppure vuoi segnalare un problema tecnico?",
        "contatti_email_intro": "Per contattarmi via email:",
        "contatti_github_intro": "Per vedere il codice sorgente o segnalare un problema su GitHub:",
        "chiudi": "Chiudi",
        "tempi": "  ·  tempi: elenco file {a} s, analisi {b} s, report {c} s",
        "errore_fatale": "Si è verificato un errore:\n{errore}\n\nI dettagli sono stati salvati in:\n{log}",
        "dividi_sottocartelle": "Dividi il report per sottocartelle",
        "includi_immagini": "Includi immagini",
        "includi_immagini_nota": "I file con estensione immagine (jpg, jpeg, png, gif, bmp, tif, tiff, webp, svg, heic, ico, raw, cr2, nef, arw, psd, avif) compaiono nel report; senza questa opzione sono tutti esclusi.",
        "r_solo_immagini": "Solo immagini",
        # titoli delle colonne (finestra) e, se diversi, delle intestazioni del report
        "col_bitrate_audio": "Bitrate audio",
        "col_nome": "Nome file", "col_tipo": "Tipo", "col_est": "Estensione", "col_dim": "Dimensione",
        "col_durata": "Durata", "col_ris": "Risoluzione", "col_colore": "Profondità di colore", "col_hdr": "HDR", "col_dv": "Dolby Vision",
        "col_fps": "FPS", "col_cv": "Codec video", "col_ca": "Codec audio", "col_canali": "Canali audio",
        "col_formato": "Formato audio", "col_tracce": "Tracce audio", "col_bitrate_video": "Bitrate video", "col_bitrate_audio": "Bitrate audio", 
        "th_est": "Est.", "th_colore": "Prof. colore", "th_cv": "Codec V", "th_ca": "Codec A",
        "col_artista": "Artista", "col_album": "Album", "col_titolo": "Titolo", "col_anno": "Anno",
        "col_traccia": "Numero traccia", "col_data": "Data modifica", "col_qualita": "Qualità (lossless/lossy)",
        "col_copertina": "Copertina incorporata", "th_traccia": "N.", "th_data": "Modificato",
        "th_qualita": "Qualità", "th_copertina": "Copertina",
        # report HTML
        "r_cartella": "Cartella:", "r_generato": "Generato il:",
        "r_formato_data": "%d/%m/%Y alle %H:%M:%S", "r_totali": "File totali:", "r_n_cartelle": "Cartelle:", "r_spazio": "Spazio occupato:",
        "r_sep_migliaia": ".", "r_cerca": "Cerca file...", "r_tutti": "Tutti", "r_video": "Video",
        "r_audio": "Audio", "r_solo_hdr": "Solo HDR", "r_res_qualsiasi": "Qualsiasi risoluzione",
        "r_res_720": "Sotto 720p (SD)", "r_res_1080": "Sotto 1080p (HD)", "r_res_1440": "Sotto 1440p",
        "r_res_4k": "Sotto 4K", "r_azzera": "Azzera filtri", "r_unica": "Pagina unica", "r_stampa": "Stampa", "r_tema": "Tema", "r_per_pagina": "per pagina", "r_gruppi": "Dividi per sottocartelle", "r_prec": "Precedente", "r_succ": "Successiva",
        "r_data_qualsiasi": "Qualsiasi data di modifica", "r_data_7": "Modificati negli ultimi 7 giorni",
        "r_data_30": "Modificati negli ultimi 30 giorni", "r_csv": "Esporta CSV", "r_colonne": "Colonne", "r_riepilogo": "Riepilogo",
        # JavaScript del report
        "j_pagina": "Pagina", "j_tema_chiaro": "Tema chiaro", "j_tema_scuro": "Tema scuro", "j_tema_colore": "Tema colore", "j_tema_verde": "Tema verde", "j_filtri": "Filtri attivi",
        "j_conferma_stampa": "Stampare {n} file può richiedere moltissime pagine e rendere lento il browser. Continuare?", "j_pagina_unica": "Tutti i file in un'unica pagina",
        "j_conferma": "Mostrare {n} file in un'unica pagina può rendere il browser molto lento. Continuare?", "j_di": "di", "j_mostrati": "file mostrati", "j_su": "su",
        "j_radice": "(cartella principale)", "j_file": "file", "j_si": "Sì", "j_no": "No", "j_profilo": "Profilo", "j_con_el": "(con EL)",
        "j_tipo_video": "Video", "j_tipo_audio": "Audio", "j_tipo_generico": "Generico",
        "j_fmt_data": "dmy", "j_csv_sep": ";", "j_cartella": "Cartella",
        "j_riep_titolo": "Riepilogo", "j_riep_ore": "ore", "j_riep_artisti": "artisti", "j_riep_album": "album",
        "j_riep_altro": "Altro", "j_riep_altri": "Altri", "j_riep_sdr": "Senza HDR", "j_riep_hdr_altro": "HDR (altro)",
        "j_riep_video": "video", "j_riep_brani": "brani",
        "j_col_tutte": "Tutte", "j_col_predef": "Predefinite", "j_gr_file": "File", "j_gr_tag": "Tag musicali",
        "j_gr_video": "Video", "j_gr_audio": "Audio",
    },
    "en": {
        "sottotitolo": "v{v}  ·  HTML report",
        "cartella_titolo": "Media folder",
        "sfoglia": "Browse...",
        "nota_recenti": "The drop-down menu lists the folders you scanned most recently.",
        "mostra_come": "Show the folder in the report as:",
        "percorso_completo": "Name and path",
        "solo_nome": "Name only",
        "usa_cache": "Use the cache (re-analyze only new or modified files)",
        "svuota_cache": "Clear cache", "usa_cache_breve": "Use the cache",
        "svuota_cronologia": "Clear history", "cronologia_titolo": "Source history",
        "cronologia_conferma": "Clear the list of recent folders in the drop-down menu?\n\nThe folder currently in the box and the ones saved in profiles are not changed.",
        "cronologia_svuotata": "Folder history cleared.",
        "colonne_titolo": "Report columns", "colonne_conteggio": "{n} selected",
        "gr_file": "File", "gr_tag": "Music tags", "gr_video": "Video", "gr_audio": "Audio",
        "layout_verticale": "Vertical layout", "layout_orizzontale": "Horizontal layout",
        "aspetto_menu": "Settings", "lingua_menu": "Language", "tema_scuro": "Dark theme", "tema_chiaro": "Light theme", "tema_colore": "Color theme",
        "tutte": "All",
        "nessuna": "None",
        "attesa": "Waiting...",
        "genera": "Generate HTML report",
        "annulla": "Cancel",
        "versione_ff": "version {v}",
        "versione_nd": "version not detected",
        "percorso_ff": "Path: {p}",
        "ffprobe_mancante": "ERROR: ffprobe not found! Put it in the program folder or in the PATH.",
        "errore": "Error",
        "info": "Info",
        "cartella_non_valida": "Select a valid folder!",
        "nessuna_colonna": "Select at least one column!",
        "salva_titolo": "Save report",
        "ricerca_file": "Searching for files...",
        "ricerca_file_n": "Searching for files... {n} found",
        "analisi": "Analyzing: {n}/{totale} ({pct}%)",
        "analisi_stima": "Analyzing: {n}/{totale} ({pct}%) · about {tempo} left",
        "cartella_vuota": "Empty folder.",
        "annullata": "Operation cancelled.",
        "salvataggio_fallito": "Could not save the report:\n{errore}",
        "errore_imprevisto": "Unexpected error:\n{errore}",
        "report_salvato": "HTML report saved!",
        "dettaglio_cache": "  ·  from cache: {h}, analyzed: {a}",
        "completato_aperto": "Done! Report opened in the browser.",
        "completato_salvato": "Done! Report saved.",
        "salvato_titolo": "Report saved",
        "apertura_fallita": "It could not be opened automatically.\n\n{percorso}",
        "cache_titolo": "Cache",
        "cache_svuotata": "Cache cleared: the next scan will analyze all files again.",
        "cache_gia_vuota": "The cache is already empty.",
        "cache_errore": "Could not clear the cache:\n{errore}",
        "apri_config": "Open configuration folder",
        "scarica_ffmpeg": "Download FFmpeg (includes ffprobe): {url}",
        "tipo_etichetta": "Type:", "tipo_generale": "General", "tipo_musica": "Music", "tipo_film": "Movies",
        "tipo_titolo": "Profile type",
        "tipo_testo": "The profile becomes type \"{tipo}\".\n\nDo you also want to set the default columns for this type? The profile's current columns will be replaced.",
        "profilo_titolo": "Profile",
        "profilo_nota": "Folder, type, columns, exclusions and options are remembered for each profile.",
        "profilo_gestisci": "Manage", "profilo_nuovo": "New profile...",
        "profilo_elimina": "Delete profile",
        "escl_bottone": "Exclusions ({n})...",
        "nuovo_titolo": "New profile", "nuovo_testo": "Name of the new profile (starts as a copy of «{nome}»):",
        "nuovo_nome": "Profile name (for example Animation):", "nuovo_tipo": "Type:",
        "nuovo_modello": "Start from the default columns of the type (otherwise copy the current ones)",
        "nuovo_usa_corrente": "Use the current folder",
        "nuovo_nota": "The current exclusions and options are copied into the new profile, but not the folder: after creating it, choose its folder and press Save.",
        "profilo_auto_generale": "New folder: I can't know what it contains, so I'm using the \"{nome}\" profile (General type).",
        "profilo_auto_noto": "This folder belongs to the \"{nome}\" profile: switching to it.",
        "elimina_ultimo_testo": "\"{nome}\" is the last profile.\n\nDeleting it creates a new one, \"Generale\", with the default settings (all columns, default exclusions). The folder box stays as it is. Continue?",
        "nuovo_crea": "Create profile", "profilo_salvato_breve": "✓ Saved", "profilo_modifica": "Edit profile...", "modifica_titolo": "Edit profile", "modifica_nome": "Profile name:", "modifica_cartella": "Profile source folder:", "profilo_salva": "Save", "profilo_salvato": "Profile «{nome}» saved.",
        "elimina_titolo": "Delete profile", "elimina_testo": "Delete the profile «{nome}»?",
        "profilo_ultimo": "At least one profile must remain.",
        "nome_vuoto": "Enter a name for the profile.", "nome_esiste": "A profile named «{nome}» already exists.",
        "nome_lungo": "The name is too long (40 characters maximum).",
        "escl_titolo": "Exclusions for profile «{nome}»", "escl_estensioni": "Excluded extensions",
        "escl_estensioni_nota": "Separated by spaces, commas or new lines; the dot is optional (txt or .txt). Case does not matter.",
        "escl_nomi": "Excluded file names", "escl_nomi_nota": "One full name per line, for example thumbs.db or folder.jpg.",
        "escl_ripristina": "Restore defaults", "escl_salva": "Save",
        "escl_ignorate": "Entries ignored as invalid: {voci}",
        "contatti_titolo": "Feedback and contact", "profilo_generale_nome": "General", "tema_sistema": "System theme", "colonne_predefinite": "Default", "search_help": "Search files... (e.g. ext:mkv size:>10GB year:2020 res:4k hdr:yes durata:>60)",
        "contatti_testo": "Do you have suggestions, ideas to improve the program, change requests, or do you want to report a technical problem?",
        "contatti_email_intro": "To contact me by email:",
        "contatti_github_intro": "To see the source code or report an issue on GitHub:",
        "chiudi": "Close",
        "tempi": "  ·  times: file listing {a} s, analysis {b} s, report {c} s",
        "errore_fatale": "An error occurred:\n{errore}\n\nDetails were saved to:\n{log}",
        "dividi_sottocartelle": "Group the report by subfolder",
        "includi_immagini": "Include images",
        "includi_immagini_nota": "Files with an image extension (jpg, jpeg, png, gif, bmp, tif, tiff, webp, svg, heic, ico, raw, cr2, nef, arw, psd, avif) appear in the report; without this option they are all excluded.",
        "r_solo_immagini": "Images only",
        "col_bitrate_audio": "Audio bitrate",
        "col_nome": "File name", "col_tipo": "Type", "col_est": "Extension", "col_dim": "Size",
        "col_durata": "Duration", "col_ris": "Resolution", "col_colore": "Color depth", "col_hdr": "HDR", "col_dv": "Dolby Vision",
        "col_fps": "FPS", "col_cv": "Video codec", "col_ca": "Audio codec", "col_canali": "Audio channels",
        "col_formato": "Audio format", "col_tracce": "Audio tracks", "col_bitrate_video": "Video bitrate", "col_bitrate_audio": "Audio bitrate", 
        "th_est": "Ext.", "th_colore": "Color depth",
        "col_artista": "Artist", "col_album": "Album", "col_titolo": "Title", "col_anno": "Year",
        "col_traccia": "Track number", "col_data": "Modified date", "col_qualita": "Quality (lossless/lossy)",
        "col_copertina": "Embedded cover art", "th_traccia": "No.", "th_data": "Modified",
        "th_qualita": "Quality", "th_copertina": "Cover",
        "r_cartella": "Folder:", "r_generato": "Generated on:",
        "r_formato_data": "%Y-%m-%d %H:%M:%S", "r_totali": "Total files:", "r_n_cartelle": "Folders:", "r_spazio": "Space used:",
        "r_sep_migliaia": ",", "r_cerca": "Search files...", "r_tutti": "All", "r_video": "Video",
        "r_audio": "Audio", "r_solo_hdr": "HDR only", "r_res_qualsiasi": "Any resolution",
        "r_res_720": "Below 720p (SD)", "r_res_1080": "Below 1080p (HD)", "r_res_1440": "Below 1440p",
        "r_res_4k": "Below 4K", "r_azzera": "Reset filters", "r_unica": "Single page", "r_stampa": "Print", "r_tema": "Theme", "r_per_pagina": "per page", "r_gruppi": "Group by subfolder", "r_prec": "Previous", "r_succ": "Next",
        "r_data_qualsiasi": "Any modified date", "r_data_7": "Modified in the last 7 days",
        "r_data_30": "Modified in the last 30 days", "r_csv": "Export CSV", "r_colonne": "Columns", "r_riepilogo": "Summary",
        "j_pagina": "Page", "j_tema_chiaro": "Light theme", "j_tema_scuro": "Dark theme", "j_tema_colore": "Color theme", "j_tema_verde": "Green theme", "j_filtri": "Active filters",
        "j_conferma_stampa": "Printing {n} files may take a great many pages and make the browser very slow. Continue?", "j_pagina_unica": "All files on a single page",
        "j_conferma": "Showing {n} files on a single page may make the browser very slow. Continue?", "j_di": "of", "j_mostrati": "files shown", "j_su": "of",
        "j_radice": "(root folder)", "j_file": "files", "j_si": "Yes", "j_no": "No", "j_profilo": "Profile", "j_con_el": "(with EL)",
        "j_tipo_video": "Video", "j_tipo_audio": "Audio", "j_tipo_generico": "Generic",
        "j_fmt_data": "ymd", "j_csv_sep": ",", "j_cartella": "Folder",
        "j_riep_titolo": "Summary", "j_riep_ore": "hours", "j_riep_artisti": "artists", "j_riep_album": "albums",
        "j_riep_altro": "Other", "j_riep_altri": "Others", "j_riep_sdr": "No HDR", "j_riep_hdr_altro": "HDR (other)",
        "j_riep_video": "video", "j_riep_brani": "tracks",
        "j_col_tutte": "All", "j_col_predef": "Default", "j_gr_file": "File", "j_gr_tag": "Music tags",
        "j_gr_video": "Video", "j_gr_audio": "Audio",
    },
}

# Iniezione di sicurezza per la traduzione dell'aggiornamento (evita KeyError)
TESTI["it"]["nuova_versione"] = "⬆ È disponibile la versione {v}! Clicca qui per scaricarla."
TESTI["it"]["tema_verde"] = "Tema verde"
TESTI["it"]["j_tema_verde"] = "Tema verde"
TESTI["en"]["nuova_versione"] = "⬆ Version {v} is available! Click here to download it."
TESTI["en"]["tema_verde"] = "Green theme"
TESTI["en"]["j_tema_verde"] = "Green theme"


def traduci(lingua, chiave, **valori):
    """Testo nella lingua scelta (se manca, ricade sull'italiano); i {segnaposto} si riempiono con `valori`."""
    testo = TESTI.get(lingua, TESTI["it"]).get(chiave)
    if testo is None:
        testo = TESTI["it"][chiave]
    return testo.format(**valori) if valori else testo


# ---------------------------------------------------------------- tempi di avvio

FASI_AVVIO = []


def segna_fase(nome):
    """Registra (e scrive sulla console) a che punto è l'avvio: se si blocca, l'ultima riga dice dove."""
    secondi = time.perf_counter() - _AVVIO
    FASI_AVVIO.append((nome, secondi))
    print(f"[avvio {secondi:6.2f} s] {nome}", file=sys.stderr, flush=True)


def salva_log_avvio():
    """Scrive avvio.log (accanto a config.json) con i tempi di ogni fase dell'ultima apertura."""
    try:
        percorso = os.path.join(os.path.dirname(percorso_config()), "avvio.log")
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with open(percorso, "w", encoding="utf-8") as f:
            f.write(f"Media Directory Lister v{VERSIONE} - tempi di avvio (secondi dall'inizio, e durata di ogni fase)\n")
            precedente = 0.0
            for nome, secondi in list(FASI_AVVIO):
                f.write(f"{secondi:7.2f}  (+{secondi - precedente:5.2f})  {nome}\n")
                precedente = secondi
    except OSError:
        pass


# ---------------------------------------------------------------- ffprobe

def trova_ffprobe():
    """Cerca ffprobe prima accanto al programma (un solo controllo, istantaneo) e solo dopo nel PATH:
    scorrere il PATH può essere lentissimo se contiene dischi di rete spenti o irraggiungibili."""
    nome = "ffprobe.exe" if IS_WIN else "ffprobe"
    if getattr(sys, "frozen", False):
        cartelle = [os.path.dirname(sys.executable), getattr(sys, "_MEIPASS", "")]
    else:
        cartelle = [os.path.dirname(os.path.abspath(__file__))]
    for c in cartelle:
        locale = os.path.join(c, nome)
        if c and os.path.exists(locale):
            return locale
    return shutil.which("ffprobe")


def _opzioni_senza_finestra():
    """Su Windows evita che compaia una finestra nera a ogni chiamata di ffprobe."""
    if not IS_WIN:
        return {}
    si = subprocess.STARTUPINFO()
    si.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    return {"startupinfo": si, "creationflags": subprocess.CREATE_NO_WINDOW}


def versione_ffprobe(ffprobe):
    """Versione di ffprobe (es. '7.1-essentials_build-www.gyan.dev'), oppure None se non rilevabile."""
    if not ffprobe:
        return None
    try:
        r = subprocess.run([ffprobe, "-version"], capture_output=True, text=True, encoding="utf-8",
                           errors="ignore", timeout=10, **_opzioni_senza_finestra())
    except (OSError, subprocess.SubprocessError):
        return None
    righe = r.stdout.splitlines()
    parti = righe[0].split() if righe else []
    return parti[2] if len(parti) >= 3 and parti[1] == "version" else None


def a_capo(testo, righe=3, minimo=50):
    """Spezza un testo lungo (senza spazi, come un percorso) in al massimo `righe` righe, preferendo i separatori."""
    if len(testo) <= minimo:
        return testo
    n = max(minimo, -(-len(testo) // righe) + 10)  # lunghezza di riga: tre righe bastano sempre a coprire il testo
    out = []
    while len(testo) > n and len(out) < righe - 1:
        taglio = n
        for i in range(n, n - 11, -1):  # cerca un separatore poco prima del limite
            if testo[i - 1] in "\\/":
                taglio = i
                break
        out.append(testo[:taglio])
        testo = testo[taglio:]
    out.append(testo)
    return "\n".join(out)


def esegui_ffprobe(ffprobe, percorso):
    extra = _opzioni_senza_finestra()
    r = subprocess.run(
        [ffprobe, "-v", "error", "-print_format", "json", "-show_format", "-show_streams", percorso],
        capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=30, **extra,
    )
    return json.loads(r.stdout) if r.stdout.strip() else {}


def _numero(valore):
    try:
        return float(valore)
    except (TypeError, ValueError):
        return None


def _fps(valore):
    try:
        n, d = (valore or "0/0").split("/")
        return round(float(n) / float(d), 2) if float(d) else None
    except ValueError:
        return None


def _is_hdr(video):
    """HDR10/HLG (curva di trasferimento PQ o HLG) oppure Dolby Vision (side data)."""
    if video.get("color_transfer") in ("smpte2084", "arib-std-b67"):
        return True
    for sd in video.get("side_data_list", []):
        tipo = str(sd.get("side_data_type", "")).upper()
        if "DOVI" in tipo or "DOLBY VISION" in tipo or sd.get("dv_profile") is not None:
            return True
    return False


def elenca_file(cartella, statistiche=None, estensioni=None, nomi=None, annulla=None, avanzamento=None):
    """Elenco ordinato [(percorso, dimensione, data_modifica_ns)] di tutti i file, esclusi quelli con le estensioni
    in `estensioni` o i nomi in `nomi` (insiemi in minuscolo; se mancano valgono ESTENSIONI_ESCLUSE e NOMI_ESCLUSI).

    Usa os.scandir: la dimensione arriva insieme all'elenco della cartella (su Windows senza altri accessi
    al disco), invece di una chiamata a getsize() per ogni file. L'ordine (cartella, nome) è calcolato
    una volta sola qui, così il report esce già ordinato.
    Se si passa un dizionario come `statistiche`, vi si scrive "cartelle": il numero di sottocartelle
    attraversate (quella di partenza esclusa), anche se vuote o con soli file esclusi.
    `annulla` (threading.Event): se viene impostato la ricerca si ferma e la funzione restituisce None.
    `avanzamento(n)`: chiamata ogni tanto (al massimo 5 volte al secondo) con il numero di file trovati finora."""
    estensioni = ESTENSIONI_ESCLUSE if estensioni is None else estensioni
    nomi = NOMI_ESCLUSI if nomi is None else nomi
    trovati, da_visitare, n_cartelle = [], [cartella], 0
    visti, ultimo = 0, time.perf_counter()
    while da_visitare:
        if annulla is not None and annulla.is_set():
            return None
        try:
            with os.scandir(da_visitare.pop()) as voci:
                for v in voci:
                    visti += 1
                    if visti % 64 == 0:  # ogni tanto: controlla l'annullamento e aggiorna il conteggio
                        if annulla is not None and annulla.is_set():
                            return None
                        adesso = time.perf_counter()
                        if avanzamento is not None and adesso - ultimo >= 0.2:
                            avanzamento(len(trovati))
                            ultimo = adesso
                    try:
                        if v.is_dir(follow_symlinks=False):
                            da_visitare.append(v.path)
                            n_cartelle += 1
                            continue
                        if not v.is_file():
                            continue
                    except OSError:
                        continue  # voce illeggibile: la salta
                    nome = v.name.lower()
                    if nome in nomi or os.path.splitext(nome)[1].lstrip(".") in estensioni:
                        continue
                    try:
                        info = v.stat()
                        dimensione, modifica = info.st_size, info.st_mtime_ns
                    except OSError:
                        dimensione, modifica = 0, None
                    trovati.append((v.path, dimensione, modifica))
        except OSError:
            continue  # cartella non accessibile
    trovati.sort(key=lambda t: (os.path.dirname(t[0]).lower(), os.path.basename(t[0]).lower()))
    if statistiche is not None:
        statistiche["cartelle"] = n_cartelle
    return trovati


def _imposta(rec, **valori):
    """Aggiunge al record solo i valori presenti: meno memoria e un report più leggero."""
    rec.update({k: v for k, v in valori.items() if v is not None and v != ""})


def _tipo_hdr(video):
    """Tipo di HDR dalla curva di trasferimento: PQ = HDR10 (e compatibili), HLG = broadcast."""
    t = video.get("color_transfer")
    return "HDR10" if t == "smpte2084" else ("HLG" if t == "arib-std-b67" else None)


def _rapporto(v):
    """ffprobe scrive molti valori come frazione («10000000/10000»)."""
    try:
        if isinstance(v, str) and "/" in v:
            n, d = v.split("/")
            return float(n) / float(d) if float(d) else None
        return float(v)
    except (TypeError, ValueError):
        return None


def _luminanza_hdr(video):
    """(picco di luminanza del master in nit, MaxCLL, MaxFALL) dai metadati statici, quando ci sono."""
    mx = mc = mf = None
    for sd in video.get("side_data_list", []):
        tipo = str(sd.get("side_data_type", "")).lower()
        if "mastering display" in tipo:
            mx = _rapporto(sd.get("max_luminance"))
        elif "content light level" in tipo:
            mc, mf = _numero(sd.get("max_content")), _numero(sd.get("max_average"))
    intero = lambda x: int(round(x)) if x and x > 0 else None
    return intero(mx), intero(mc), intero(mf)


_NOMI_CODEC_AUDIO = {"aac": "AAC", "flac": "FLAC", "opus": "Opus", "mp3": "MP3", "mp2": "MP2", "vorbis": "Vorbis",
                     "alac": "ALAC", "ac3": "AC3", "eac3": "E-AC3", "truehd": "TrueHD", "wavpack": "WavPack"}


def _codec_audio(stream):
    """Nome abituale del codec audio; per DTS e Dolby si guarda il profilo (DTS-HD MA, DTS:X, Atmos...)."""
    nome = str(stream.get("codec_name") or "").lower()
    profilo = str(stream.get("profile") or "").lower()
    if nome == "dts":
        if "dts:x" in profilo:
            return "DTS:X"
        return "DTS-HD MA" if "dts-hd ma" in profilo else ("DTS-HD HRA" if "dts-hd hra" in profilo else "DTS")
    base = "PCM" if nome.startswith("pcm") else _NOMI_CODEC_AUDIO.get(nome, nome.upper())
    return base + " Atmos" if "atmos" in profilo and nome in ("truehd", "eac3") else base


def _canali_testo(stream):
    """Canali nella notazione abituale: 2.0, 5.1, 7.1, 7.1.4..."""
    layout = str(stream.get("channel_layout") or "")
    m = re.match(r"(\d+\.\d+(?:\.\d+)?)", layout)
    if m:
        return m.group(1)
    if layout in ("stereo", "mono"):
        return "2.0" if layout == "stereo" else "1.0"
    n = int(_numero(stream.get("channels")) or 0)
    return {1: "1.0", 2: "2.0", 3: "2.1", 4: "4.0", 5: "5.0", 6: "5.1", 7: "6.1", 8: "7.1"}.get(n) or (f"{n}ch" if n else None)


def _tracce_audio(streams, ffprobe=None, percorso=None, durata=None):
    """Elenco delle tracce audio, es. ["ITA E-AC3 5.1 640 kbps", "ENG TrueHD Atmos 7.1"]. 
    Include il bitrate se disponibile (da ffprobe, dai tag o calcolato)."""
    tracce = []
    for st in streams:
        if st.get("codec_type") != "audio":
            continue
        tag = {str(k).lower(): v for k, v in (st.get("tags") or {}).items()}
        lingua = str(tag.get("language") or "").upper()
        parti = [lingua] if lingua and lingua != "UND" else []
        parti.append(_codec_audio(st))
        canali = _canali_testo(st)
        if canali:
            parti.append(canali)
        
        # Bitrate: prima da ffprobe, poi dai tag, poi calcolo a pacchetti
        ba = _numero(st.get("bit_rate"))
        if not ba:
            tag_audio = _tag_minuscoli(st.get("tags"))
            ba = _numero(tag_audio.get("bps")) or _numero(tag_audio.get("bps-eng"))
        if not ba and ffprobe and percorso:
            ba = _bitrate_audio_reale(ffprobe, percorso, durata)
        if ba:
            parti.append(f"{int(round(ba / 1000))} kbps")
        
        tracce.append(" ".join(parti))
    if len(tracce) > 8:
        tracce = tracce[:8] + [f"+{len(tracce) - 8}"]
    return tracce or None


def _bit_video(video):
    """Bit per canale del video: dal campo bits_per_raw_sample, altrimenti dal formato dei pixel (pix_fmt)."""
    raw = _numero(video.get("bits_per_raw_sample"))
    if raw:
        return int(raw)
    pf = str(video.get("pix_fmt") or "")
    alto = re.search(r"(?:p0?|[a-z])(9|10|12|14|16)(?:le|be)$", pf)  # yuv420p10le, p010le, gbrp12le, gray10le (non nv12!)
    if alto:
        return int(alto.group(1))
    if re.search(r"(yuvj?4\d\dp|nv12|nv21|gray|gbrp|rgb24|bgr24|pal8|yuyv422|uyvy422|rgba?|bgra?|argb|abgr)$", pf):
        return 8
    return None


def _profilo(video):
    p = str(video.get("profile") or "").strip()
    return None if p.lower() in ("", "unknown") or p.startswith("-") else p


def _livello(video):
    """Livello del codec nella notazione abituale (es. 5.1). ffprobe lo dà come numero che dipende dal codec."""
    liv = _numero(video.get("level"))
    if liv is None or liv <= 0:
        return None
    liv, codec = int(liv), video.get("codec_name")
    if codec == "hevc":
        return f"{liv // 30}.{(liv % 30) // 3}"      # 153 -> 5.1
    if codec == "h264":
        return f"{liv // 10}.{liv % 10}"             # 41 -> 4.1
    if codec == "av1":
        return f"{2 + (liv >> 2)}.{liv & 3}"         # indice del livello -> 4.0, 5.1...
    return None


# codec audio senza perdita (lossless); il PCM (wav, aiff...) si riconosce dal prefisso "pcm"
_CODEC_LOSSLESS = {"flac", "alac", "ape", "wavpack", "tta", "wmalossless", "mlp", "truehd", "shorten", "tak"}


def _lossless(stream):
    """True se il codec audio non perde informazione (FLAC, ALAC, WAV...), False se è lossy (MP3, AAC, Opus...)."""
    nome = str(stream.get("codec_name") or "").lower()
    if nome.startswith("pcm") or nome in _CODEC_LOSSLESS:
        return True
    return nome == "dts" and "dts-hd ma" in str(stream.get("profile") or "").lower()


def _tag_minuscoli(*gruppi):
    """Unisce gruppi di tag con le chiavi in minuscolo (cambiano da formato a formato: TITLE, title, TIT2...);
    i primi gruppi hanno la precedenza."""
    unito = {}
    for gruppo in gruppi:
        if isinstance(gruppo, dict):
            for k, v in gruppo.items():
                unito.setdefault(str(k).lower(), v)
    return unito


def _primo_tag(tag, *nomi):
    """Il primo tag non vuoto tra `nomi` (testo ripulito e limitato a 200 caratteri), oppure None."""
    for nome in nomi:
        valore = str(tag.get(nome) or "").strip()
        if valore:
            return valore[:200]
    return None


def _tag_musicali(formato, stream_audio):
    """Artista, album, titolo, anno e numero di traccia dai tag del file. ffprobe li mette nel contenitore
    (mp3, flac, m4a) oppure nel flusso audio (ogg, opus): si guardano entrambi."""
    tag = _tag_minuscoli(formato.get("tags"), (stream_audio or {}).get("tags"))
    anno = re.match(r"\s*(\d{4})", _primo_tag(tag, "date", "year", "originaldate", "originalyear", "tdrc") or "")
    traccia = re.match(r"\s*(\d{1,4})", _primo_tag(tag, "track", "tracknumber") or "")  # "3" oppure "3/12"
    anno = int(anno.group(1)) if anno and 1000 <= int(anno.group(1)) <= 2999 else None
    traccia = int(traccia.group(1)) if traccia and int(traccia.group(1)) > 0 else None
    return {"ar": _primo_tag(tag, "artist", "album_artist", "albumartist"), "al": _primo_tag(tag, "album"),
            "ti": _primo_tag(tag, "title"), "an": anno, "tr": traccia}


def analizza(percorso, ffprobe, annulla, dimensione=None, cache=None, modifica=None, calcola_audio=False):
    """Restituisce un dizionario con valori NUMERICI grezzi (la formattazione la fa il browser).
    I campi senza valore non vengono inclusi: nel report risultano 'null' e compaiono come '-'.
    Con `cache` (e la data di modifica del file) ffprobe parte solo se il file è nuovo o cambiato."""
    if annulla.is_set():
        return None
    if dimensione is None:
        try:
            dimensione = os.path.getsize(percorso)
        except OSError:
            dimensione = 0
    nome = os.path.basename(percorso)
    ext = os.path.splitext(nome)[1].lstrip(".")
    rec = {"p": nome, "t": "Generico", "e": ext.upper(), "d": dimensione}
    if modifica is not None:
        rec["m"] = modifica // 1_000_000_000
    
    if ext.lower() in ESTENSIONI_IMMAGINE:
        rec["t"] = "Foto"
        if cache is not None and modifica is not None:
            cache.registra(os.path.normcase(percorso), dimensione, modifica, rec)
        return rec

    if not ffprobe or ext.lower() not in ESTENSIONI_MEDIA:
        return rec
        
    usa_cache = cache is not None and modifica is not None
    chiave = os.path.normcase(percorso)
    if usa_cache:
        trovato = cache.cerca(chiave, dimensione, modifica)
        if trovato is not None:
            return trovato
            
    try:
        dati = esegui_ffprobe(ffprobe, percorso)
    except (OSError, subprocess.SubprocessError, ValueError):
        return rec

    fmt = dati.get("format", {})
    _imposta(rec, du=_numero(fmt.get("duration")), bi=_numero(fmt.get("bit_rate")))
    streams = dati.get("streams", [])
    
    video = next((s for s in streams if s.get("codec_type") == "video"
                  and not s.get("disposition", {}).get("attached_pic")), None)
    audio = next((s for s in streams if s.get("codec_type") == "audio"), None)
    
    if video:
        rec["t"] = "Video"
        mx, mc, mf = _luminanza_hdr(video)
        
        bv = _numero(video.get("bit_rate"))
        if not bv:
            tag_vid = _tag_minuscoli(video.get("tags"))
            bv = _numero(tag_vid.get("bps")) or _numero(tag_vid.get("bps-eng"))
            
        _imposta(rec, vc=str(video.get("codec_name", "")).upper(),
                 w=video.get("width"), h=video.get("height"),
                 f=_fps(video.get("avg_frame_rate")) or _fps(video.get("r_frame_rate")),
                 hdr=_is_hdr(video),
                 cb=_bit_video(video), pr=_profilo(video), lv=_livello(video),
                 ht=_tipo_hdr(video), mx=mx, mc=mc, mf=mf, at=_tracce_audio(streams, ffprobe, percorso, rec.get("du")),
                 bv=bv)
        
        # Fallback: se manca il bitrate video, lo calcoliamo (totale - audio)
        if not rec.get("bv") and rec.get("bi"):
            audio_tot = sum(float(st.get("bit_rate", 0) or 0) for st in streams if st.get("codec_type") == "audio")
            stima_video = rec["bi"] - audio_tot
            if stima_video > 0:
                rec["bv"] = stima_video
                 
        dovi = next((sd for sd in video.get("side_data_list", []) if sd.get("dv_profile") is not None), None)
        if dovi:
            profilo = _numero(dovi.get("dv_profile"))
            compat = _numero(dovi.get("dv_bl_signal_compatibility_id"))
            _imposta(rec, dvp=int(profilo) if profilo is not None else None,
                     dvc=int(compat) if compat is not None else None,
                     dve=True if dovi.get("el_present_flag") else None)
                     
    if audio:
        frequenza = _numero(audio.get("sample_rate"))
        profondita = _numero(audio.get("bits_per_raw_sample")) or _numero(audio.get("bits_per_sample"))
        
        
        ba = _numero(audio.get("bit_rate"))
        if not ba:
            ba = _numero(fmt.get("bit_rate"))
        if not ba:
            tag_aud = _tag_minuscoli(audio.get("tags"))
            ba = _numero(tag_aud.get("bps")) or _numero(tag_aud.get("bps-eng"))
            
        if calcola_audio and not ba and ffprobe and rec.get("du"):
            ba = _bitrate_audio_reale(ffprobe, percorso, rec["du"])
            
        _imposta(rec, ac=str(audio.get("codec_name", "")).upper(),
                 ch=audio.get("channels"), cl=audio.get("channel_layout"),
                 sr=int(frequenza) if frequenza else None,
                 bd=int(profondita) if profondita else None,
                 ba=ba)
                 
        if not video:
            rec["t"] = "Audio"
            copertina = any(s.get("codec_type") == "video" for s in streams)
            _imposta(rec, lo=_lossless(audio), cp=True if copertina else None, **_tag_musicali(fmt, audio))
            
    if usa_cache:
        cache.registra(chiave, dimensione, modifica, rec)
    return rec


def _bitrate_audio_reale(ffprobe, percorso, durata_audio):
    if not durata_audio or durata_audio <= 0:
        return None
    secondi = min(2.0, durata_audio)
    try:
        r = subprocess.run(
            [ffprobe, "-v", "error", "-select_streams", "a:0", "-show_entries", "packet=size",
             "-of", "csv=p=0", "-read_intervals", f"%+{secondi}", percorso],
            capture_output=True, text=True, encoding="utf-8", errors="ignore", timeout=10,
            **_opzioni_senza_finestra()
        )
        dimensioni = [int(x) for x in r.stdout.strip().split("\n") if x.strip().isdigit()]
        if dimensioni:
            return (sum(dimensioni) * 8) / secondi
    except (OSError, subprocess.SubprocessError, ValueError):
        pass
    return None


def percorso_config():
    base = (os.environ.get("APPDATA") if IS_WIN else os.path.join(os.path.expanduser("~"), ".config")) \
        or os.path.expanduser("~")
    return os.path.join(base, "MediaDirLister", "config.json")


def carica_config():
    try:
        with open(percorso_config(), encoding="utf-8") as f:
            dati = json.load(f)
        return dati if isinstance(dati, dict) else {}
    except (OSError, ValueError):
        return {}


def salva_config(config):
    """Scrittura atomica: si scrive un file temporaneo e poi lo si sostituisce, così un blocco a metà
    non lascia un config.json troncato (e si perderebbero profili e colonne)."""
    config["versione_programma"] = VERSIONE  # serve a riconoscere la prima apertura di una versione nuova
    percorso = percorso_config()
    temporaneo = percorso + ".tmp"
    try:
        os.makedirs(os.path.dirname(percorso), exist_ok=True)
        with open(temporaneo, "w", encoding="utf-8") as f:
            json.dump(config, f, ensure_ascii=False, indent=2)
        os.replace(temporaneo, percorso)
    except (OSError, TypeError, ValueError):
        try:
            os.remove(temporaneo)
        except OSError:
            pass  # non è critico: al massimo la cartella non viene ricordata


# ---------------------------------------------------------------- profili (esclusioni + colonne)

COLONNE_TAG_MUSICA = ["artista", "album", "titolo", "anno", "traccia", "qualita", "copertina"]  # tag musicali (v3.9g)
# «Tipo» non c'è: in questi profili è uguale su ogni riga. Nel profilo Film non ci sono Codec audio e Canali audio:
# «Tracce audio» li contiene già (per tutte le tracce, con la lingua e il nome leggibile del codec)
COLONNE_MUSICA = ["nome", "artista", "album", "titolo", "anno", "traccia", "est", "dim", "durata", "ca",
                  "canali", "formato", "qualita", "copertina", "bitrate_audio"]
COLONNE_FILM = ["nome", "est", "dim", "durata", "ris", "colore", "hdr", "dv", "fps", "cv", "tracce", "bitrate_video"]
TIPI_PROFILO = ("generale", "musica", "film")  # il tipo dice su quale modello di colonne si basa il profilo
TIPO_DA_NOME = {"Generale": "generale", "Musica": "musica", "Film": "film"}  # per i profili già esistenti con questi nomi
COLONNE_PER_TIPO = {"generale": COLONNE, "musica": COLONNE_MUSICA, "film": COLONNE_FILM}
MAX_NOME_PROFILO = 40


def profili_predefiniti():
    """I profili con cui si parte: ognuno ha le sue esclusioni e le sue colonne e si può modificare dalla finestra."""
    def profilo(colonne, tipo):  # liste nuove per ogni profilo: nessuna è condivisa con gli altri
        return {"estensioni_escluse": sorted(ESTENSIONI_ESCLUSE), "nomi_esclusi": sorted(NOMI_ESCLUSI),
                "colonne": list(colonne), "tipo": tipo, "sorgente": "", "mostra": "percorso", "dividi": False,
                "usa_cache": True}
    return {"Generale": profilo(COLONNE, "generale"), "Musica": profilo(COLONNE_MUSICA, "musica"),
            "Film": profilo(COLONNE_FILM, "film")}


def normalizza_estensioni(testo, scartate=None):
    """Estensioni da un testo libero (spazi, virgole, ; o a capo; il punto iniziale è facoltativo): minuscole, senza doppioni.
    Le voci non valide vengono aggiunte alla lista `scartate`, se data."""
    parti = re.split(r"[\s,;]+", testo) if isinstance(testo, str) else [str(x) for x in testo]
    risultato = []
    for voce in parti:
        voce = voce.strip()
        if not voce:
            continue
        pulita = voce.lower().lstrip("*").strip(".")
        if re.fullmatch(r"[a-z0-9_+-]{1,20}", pulita):
            if pulita not in risultato:
                risultato.append(pulita)
        elif scartate is not None:
            scartate.append(voce)
    return sorted(risultato)


def normalizza_nomi(testo, scartate=None):
    """Nomi completi di file da un testo (uno per riga, oppure separati da ; o virgole): minuscoli, senza doppioni."""
    parti = re.split(r"[\n;,]+", testo) if isinstance(testo, str) else [str(x) for x in testo]
    risultato = []
    for voce in parti:
        voce = voce.strip()
        if not voce:
            continue
        if "/" in voce or "\\" in voce or len(voce) > 255:    # un nome di file non contiene separatori di percorso
            if scartate is not None:
                scartate.append(voce)
            continue
        if voce.lower() not in risultato:
            risultato.append(voce.lower())
    return sorted(risultato)


def pulisci_profilo(dati):
    """Rende valido un profilo letto da config.json (il file può essere stato modificato a mano). None se non è un profilo."""
    if not isinstance(dati, dict):
        return None
    predefinito = profili_predefiniti()["Generale"]
    estensioni = normalizza_estensioni(dati["estensioni_escluse"]) if isinstance(dati.get("estensioni_escluse"), list) else predefinito["estensioni_escluse"]
    nomi = normalizza_nomi(dati["nomi_esclusi"]) if isinstance(dati.get("nomi_esclusi"), list) else predefinito["nomi_esclusi"]
    colonne = [c for c in COLONNE if isinstance(dati.get("colonne"), list) and c in dati["colonne"]] or list(COLONNE)
    # tipo, cartella sorgente e opzioni: None = mancante o non valido (lo completa carica_profili)
    return {"estensioni_escluse": estensioni, "nomi_esclusi": nomi, "colonne": colonne,
            "tipo": dati.get("tipo") if dati.get("tipo") in TIPI_PROFILO else None,
            "sorgente": dati["sorgente"].strip() if isinstance(dati.get("sorgente"), str) else "",
            "mostra": dati.get("mostra") if dati.get("mostra") in ("percorso", "nome") else None,
            "dividi": dati["dividi"] if isinstance(dati.get("dividi"), bool) else None,
            "usa_cache": dati["usa_cache"] if isinstance(dati.get("usa_cache"), bool) else None,
            "includi_immagini": dati["includi_immagini"] if isinstance(dati.get("includi_immagini"), bool) else None}


def carica_profili(config):
    """(profili, nome_del_profilo_attivo). Se non ci sono profili salvati si parte da quelli predefiniti, portando
    nel profilo «Generale» le colonne scelte nelle versioni precedenti; ne resta sempre almeno uno."""
    profili = {}
    grezzi = config.get("profili")
    if isinstance(grezzi, dict):
        for nome, dati in grezzi.items():
            nome = nome.strip() if isinstance(nome, str) else ""
            profilo = pulisci_profilo(dati)
            if nome and profilo is not None and nome not in profili:
                profili[nome] = profilo
    if False:  # Migrazione disabilitata
        nuove = set(COLONNE_TAG_MUSICA) | {"data"}  # una volta sola: poi le colonne si scelgono dalla finestra
        profili["Musica"]["colonne"] = [c for c in COLONNE if c in nuove or c in profili["Musica"]["colonne"]]
    if False:  # Migrazione disabilitata
        # una volta sola, per i profili Film e Musica già salvati: si tolgono solo le colonne ridondanti (Tipo; nel Film
        # anche Codec audio e Canali audio, se c'è Tracce audio che li contiene). Il resto delle scelte non si tocca e dopo
        # le colonne si cambiano dalla finestra come sempre.
        for nome, togliere in (("Film", {"tipo", "ca", "canali"}), ("Musica", {"tipo"})):
            if nome in profili:
                colonne = profili[nome]["colonne"]
                if "tracce" not in colonne:
                    togliere = togliere & {"tipo"}  # senza Tracce audio, codec e canali sono l'unica informazione audio
                rimaste = [c for c in colonne if c not in togliere]
                if rimaste:
                    profili[nome]["colonne"] = rimaste
    if not profili:
        profili = profili_predefiniti()
        vecchie = config.get("colonne")
        if isinstance(vecchie, list):
            valide = [c for c in COLONNE if c in vecchie]
            if valide:
                profili["Generale"]["colonne"] = valide
    attivo = config.get("profilo_attivo")
    if attivo not in profili:
        attivo = "Generale" if "Generale" in profili else next(iter(profili))
    # profili salvati da versioni precedenti: il tipo si ricava dal nome, le opzioni ripartono da quelle che si usavano
    # (prima valevano per tutti), la cartella sorgente da quella usata per ultima, ma solo per il profilo attivo
    mostra = config.get("mostra_cartella") if config.get("mostra_cartella") in ("percorso", "nome") else "percorso"
    for nome, profilo in profili.items():
        if not profilo["tipo"]: profilo["tipo"] = "generale"
        profilo["mostra"] = profilo["mostra"] or mostra
        if profilo["dividi"] is None:
            profilo["dividi"] = config.get("dividi_sottocartelle") is True
        if profilo["usa_cache"] is None:
            profilo["usa_cache"] = config.get("usa_cache", True) is not False
        if profilo.get("includi_immagini") is None:
            profilo["includi_immagini"] = False  # i profili salvati prima non includevano le immagini
    if not any(profilo["sorgente"] for profilo in profili.values()):
        recenti = cartelle_recenti(config, controlla=False)
        if recenti:
            profili[attivo]["sorgente"] = recenti[0]
    # Pulizia una-tantum (v5.0z13): rimuove dal config i campi vecchi o non piu' usati
    if not config.get("pulizia_5_0z13"):
        for profilo in profili.values():
            profilo.pop("includi_immagini", None)   # opzione di sessione, non piu' salvata
        config.pop("migrazione_3_9g", None)          # vecchi flag di migrazione
        config.pop("migrazione_3_9t", None)
        config.pop("cartella_scansione", None)        # vecchio campo (una sola cartella)
        config.pop("colonne", None)                   # vecchio campo (ora le colonne stanno nei profili)
        config["pulizia_5_0z13"] = True
        salva_config(config)                          # scrive il config pulito, una volta sola
        # Avviso per chi ha gia' aggiornato dal vecchio comportamento delle immagini
        try:
            from tkinter import messagebox
            messagebox.showinfo("Aggiornamento profili",
                "I profili sono stati aggiornati per la nuova gestione delle immagini.\n\n"
                "Se nelle vecchie versioni avevi spuntato \"Includi le immagini nel report\", "
                "quell\'opzione ora e\' un\'opzione di sessione (non viene salvata).\n"
                "Controlla le tue esclusioni se necessario.")
        except Exception:
            pass
    return profili, attivo


def errore_nome_profilo(nome, esistenti, ignora=None):
    """Chiave di traduzione dell'errore se il nome non va bene (vuoto, troppo lungo, già usato), altrimenti None."""
    if not nome:
        return "nome_vuoto"
    if len(nome) > MAX_NOME_PROFILO:
        return "nome_lungo"
    if any(e.lower() == nome.lower() and e != ignora for e in esistenti):
        return "nome_esiste"
    return None


MAX_COPIE_CONFIG = 5   # copie di sicurezza della configurazione che si tengono
MARGINE_FINESTRA = 48  # pixel tolti all'altezza disponibile per la barra del titolo e i bordi della finestra


def copia_di_sicurezza_config(config):
    """Alla prima apertura di una versione nuova salva una copia di config.json (profili, cartelle, colonne) prima che
    le migrazioni la modifichino: config.json.bak_<versione che l'aveva scritto> (bak_precedente se non si sa).
    Se la versione non cambia non fa nulla. Si tengono le ultime MAX_COPIE_CONFIG. Restituisce il percorso o None."""
    sorgente = percorso_config()
    if config.get("versione_programma") == VERSIONE or not os.path.exists(sorgente):
        return None
    vecchia = re.sub(r"[^\w.\-]", "_", str(config.get("versione_programma") or "precedente"))
    destinazione = f"{sorgente}.bak_{vecchia}"
    try:
        shutil.copy2(sorgente, destinazione)
        cartella, prefisso = os.path.dirname(sorgente), os.path.basename(sorgente) + ".bak_"
        copie = sorted((os.path.join(cartella, f) for f in os.listdir(cartella) if f.startswith(prefisso)),
                       key=os.path.getmtime, reverse=True)
        for vecchia_copia in copie[MAX_COPIE_CONFIG:]:
            os.remove(vecchia_copia)
        return destinazione
    except OSError:
        return None  # la copia è una cautela in più: se non riesce, il programma parte lo stesso


def area_di_lavoro():
    """(larghezza, altezza) dello schermo senza la barra delle applicazioni di Windows, oppure None se non si sa."""
    if os.name == "nt":
        try:
            import ctypes
            from ctypes import wintypes
            area = wintypes.RECT()
            if ctypes.windll.user32.SystemParametersInfoW(0x0030, 0, ctypes.byref(area), 0):  # SPI_GETWORKAREA
                return area.right - area.left, area.bottom - area.top
        except (OSError, AttributeError, ValueError):
            pass
    return None


def cartelle_recenti(config, controlla=True):
    """Elenco delle cartelle scansionate, dalla più recente. Con controlla=True tiene solo quelle che esistono
    ancora; all'avvio si usa controlla=False perché isdir() su un disco di rete irraggiungibile può bloccarsi
    per decine di secondi, e la finestra non comparirebbe."""
    elenco = config.get("cartelle_recenti")
    if not isinstance(elenco, list):  # compatibilità con la versione precedente (una sola cartella)
        vecchia = config.get("cartella_scansione")
        elenco = [vecchia] if isinstance(vecchia, str) else []
    return [c for c in elenco if isinstance(c, str) and (not controlla or os.path.isdir(c))]


# ---------------------------------------------------------------- cache delle scansioni

FORMATO_CACHE = 2  # cambia solo se cambia la struttura dei record in cache, non i dati dei file
GIORNI_CACHE = 180  # le voci che nessuna scansione completa ha riconfermato per tanti giorni si eliminano (cartelle o dischi non più usati)


def _rappresenta(valore):
    """Testo stabile tra un avvio e l'altro: gli insiemi (set) hanno un ordine casuale, quindi si ordinano."""
    if hasattr(valore, "co_code"):                       # oggetto codice: funzioni annidate e lambda
        return "<" + _impronta_codice(valore) + ">"
    if isinstance(valore, (tuple, list)):
        return "(" + ",".join(_rappresenta(v) for v in valore) + ")"
    if isinstance(valore, (set, frozenset)):
        return "{" + ",".join(sorted(_rappresenta(v) for v in valore)) + "}"
    return repr(valore)


def _impronta_codice(codice):
    """Impronta del codice compilato di una funzione (ignora commenti, spazi e numeri di riga)."""
    h = hashlib.sha1()
    h.update(codice.co_code)
    for parte in (codice.co_names, codice.co_varnames, codice.co_consts):
        h.update(_rappresenta(parte).encode("utf-8"))
    return h.hexdigest()[:12]


def _versione_cache():
    """La versione della cache si calcola dal codice che produce i dati dei file: se lo si modifica (nuove colonne,
    nuovi campi, nuove regole) cambia da sola e le voci vecchie vengono scartate, senza doverla aumentare a mano."""
    h = hashlib.sha1()
    for funzione in (esegui_ffprobe, _codec_audio, _canali_testo, _tracce_audio, _numero, _fps, _is_hdr, _tipo_hdr, _rapporto, _luminanza_hdr, _bit_video,
                     _profilo, _livello, _imposta, _lossless, _tag_minuscoli, _primo_tag, _tag_musicali, analizza, _bitrate_audio_reale):
        h.update(_impronta_codice(funzione.__code__).encode("ascii"))
        h.update(_rappresenta(funzione.__defaults__).encode("utf-8"))
    h.update(_rappresenta(sorted(ESTENSIONI_MEDIA)).encode("utf-8"))   # quali file passano da ffprobe
    h.update(_rappresenta(sorted(_NOMI_CODEC_AUDIO.items())).encode("utf-8"))   # tabelle usate dalle funzioni sopra
    h.update(_rappresenta(sorted(_CODEC_LOSSLESS)).encode("utf-8"))
    h.update(_rappresenta(sorted(ESTENSIONI_IMMAGINE)).encode("utf-8"))   # comportamento delle immagini
    return f"{FORMATO_CACHE}-{h.hexdigest()[:10]}"


CACHE_VERSIONE = _versione_cache()


def percorso_cache():
    return os.path.join(os.path.dirname(percorso_config()), "cache_scansioni.db")


def percorso_cache_json():
    """Cache delle versioni fino alla 3.9g (un unico file JSON): si importa una volta sola e poi si elimina."""
    return os.path.join(os.path.dirname(percorso_config()), "cache_scansioni.json")


def svuota_cache_su_disco():
    """Elimina la cache (e l'eventuale vecchia cache JSON). True se c'era qualcosa da eliminare; OSError se non ci riesce."""
    trovata = False
    for percorso in (percorso_cache(), percorso_cache() + "-journal", percorso_cache_json()):
        try:
            os.remove(percorso)
            trovata = True
        except FileNotFoundError:
            pass
    return trovata


def _limite_superiore(prefisso):
    """Primo testo che viene dopo tutti quelli che iniziano con `prefisso`: serve a cercare una cartella intera
    con un intervallo (chiave >= prefisso AND chiave < limite), che usa l'indice invece di scorrere tutta la tabella."""
    return prefisso[:-1] + chr(ord(prefisso[-1]) + 1)


class CacheScansioni:
    """Ricorda l'esito di ffprobe per ogni file in un database SQLite: ffprobe viene rilanciato solo se il file è
    nuovo, se cambiano dimensione o data di modifica, oppure se cambia la versione di ffprobe (o del codice).

    All'apertura si leggono solo le voci della cartella da scansionare; al termine si scrivono solo le righe nuove
    o cambiate, in un'unica transazione (un blocco a metà non rovina la cache). Il database è usato solo dal
    thread di lavoro: i thread di analisi toccano soltanto i dizionari in memoria."""

    def __init__(self, versione_ff):
        self.versione_ff = versione_ff
        self._ff = versione_ff or ""
        self.vecchia = {}      # voci della cartella lette dal disco: {percorso: [dimensione, data_modifica_ns, record]}
        self.nuova = {}        # voci valide in questa scansione
        self.da_scrivere = {}  # tra queste, solo quelle nuove o cambiate (le uniche righe da scrivere)
        self.dalla_cache = 0
        self.analizzati = 0
        self._azzera = False   # il database è di un'altra versione (o è nuovo): al salvataggio si ricomincia da zero
        self._lock = threading.Lock()

    @staticmethod
    def _apri():
        """Apre (o crea) il database. Se il file è rovinato lo ricrea: la cache è solo un acceleratore.
        Restituisce None se non si riesce (disco pieno, file bloccato...): in quel caso si lavora senza cache."""
        for tentativo in (1, 2):
            try:
                os.makedirs(os.path.dirname(percorso_cache()), exist_ok=True)
                conn = sqlite3.connect(percorso_cache(), timeout=10)
                try:
                    conn.execute("CREATE TABLE IF NOT EXISTS meta (chiave TEXT PRIMARY KEY, valore TEXT)")
                    conn.execute("CREATE TABLE IF NOT EXISTS file (chiave TEXT PRIMARY KEY, dimensione INTEGER, "
                                 "modifica INTEGER, record TEXT NOT NULL, visto INTEGER NOT NULL) WITHOUT ROWID")
                    conn.commit()
                    return conn
                except sqlite3.Error:
                    conn.close()
                    raise
            except sqlite3.OperationalError:
                return None  # bloccato da un'altra istanza o disco non scrivibile: non è un file rovinato
            except sqlite3.DatabaseError:  # "file is not a database", "malformed": si elimina e si riprova
                try:
                    os.remove(percorso_cache())
                except OSError:
                    return None
            except (sqlite3.Error, OSError):
                return None
        return None

    def _importa_json(self, conn):
        """Primo avvio dopo l'aggiornamento: porta nel database la vecchia cache JSON (se è ancora valida),
        così non si rianalizzano tutti i file; poi la elimina."""
        vecchio = percorso_cache_json()
        if not os.path.exists(vecchio):
            return
        try:
            with open(vecchio, encoding="utf-8") as f:
                dati = json.load(f)
            if (dati.get("versione") == CACHE_VERSIONE and (dati.get("ffprobe") or "") == self._ff
                    and isinstance(dati.get("file"), dict)):
                adesso = int(time.time())
                righe = [(k, v[0], v[1], json.dumps(v[2], ensure_ascii=False, separators=(",", ":")), adesso)
                         for k, v in dati["file"].items()
                         if isinstance(v, list) and len(v) == 3 and isinstance(v[0], int)
                         and isinstance(v[1], int) and isinstance(v[2], dict)]
                with conn:
                    conn.executemany("INSERT OR REPLACE INTO file VALUES (?, ?, ?, ?, ?)", righe)
                    conn.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)",
                                     [("versione", CACHE_VERSIONE), ("ffprobe", self._ff)])
        except sqlite3.Error:
            return  # riproverà al prossimo avvio: il JSON resta dov'è
        except (OSError, ValueError, AttributeError, TypeError):
            pass  # JSON illeggibile o di un'altra versione: non serve più
        try:
            os.remove(vecchio)
        except OSError:
            pass

    def carica(self, cartella):
        """Legge dal database solo le voci della `cartella` che si sta per scansionare."""
        prefisso = os.path.normcase(cartella).rstrip(os.sep) + os.sep
        conn = self._apri()
        if conn is None:
            return
        try:
            meta = dict(conn.execute("SELECT chiave, valore FROM meta"))
            if not meta:
                self._importa_json(conn)
                meta = dict(conn.execute("SELECT chiave, valore FROM meta"))
            if meta.get("versione") != CACHE_VERSIONE or meta.get("ffprobe") != self._ff:
                self._azzera = True  # database nuovo oppure di un'altra versione di codice/ffprobe: voci non valide
                return
            for chiave, dimensione, modifica, record in conn.execute(
                    "SELECT chiave, dimensione, modifica, record FROM file WHERE chiave >= ? AND chiave < ?",
                    (prefisso, _limite_superiore(prefisso))):
                try:
                    self.vecchia[chiave] = [dimensione, modifica, json.loads(record)]
                except ValueError:
                    pass  # riga rovinata: quel file verrà rianalizzato
        except sqlite3.OperationalError:
            self.vecchia = {}
        except sqlite3.DatabaseError:  # file rovinato: lo si elimina, al salvataggio si ricrea
            self.vecchia, self._azzera = {}, True
            conn.close()
            try:
                os.remove(percorso_cache())
            except OSError:
                pass
        finally:
            conn.close()

    def cerca(self, chiave, dimensione, modifica):
        voce = self.vecchia.get(chiave)
        if not (isinstance(voce, list) and len(voce) == 3 and voce[0] == dimensione
                and voce[1] == modifica and isinstance(voce[2], dict)):
            return None
        with self._lock:
            self.dalla_cache += 1
        self.nuova[chiave] = voce
        return voce[2]

    def registra(self, chiave, dimensione, modifica, rec):
        voce = [dimensione, modifica, rec]
        with self._lock:
            self.analizzati += 1
        self.nuova[chiave] = voce
        self.da_scrivere[chiave] = voce

    def salva(self, cartella, pota=True):
        """Scrive su disco solo ciò che è cambiato. pota=True: elimina i file di `cartella` che non esistono più
        e conferma tutti gli altri (data dell'ultimo controllo). pota=False (scansione annullata): conserva anche
        le voci vecchie non ancora riesaminate. In ogni caso elimina le voci non confermate da più di GIORNI_CACHE giorni."""
        prefisso = os.path.normcase(cartella).rstrip(os.sep) + os.sep
        adesso = int(time.time())
        conn = self._apri()
        if conn is None:
            return  # la cache è solo un acceleratore: se non si salva, nessun danno
        try:
            with conn:  # un'unica transazione: o si scrive tutto o niente
                if self._azzera:
                    conn.execute("DELETE FROM file")
                    conn.executemany("INSERT OR REPLACE INTO meta VALUES (?, ?)",
                                     [("versione", CACHE_VERSIONE), ("ffprobe", self._ff)])
                if pota:
                    conn.executemany("DELETE FROM file WHERE chiave = ?",
                                     [(k,) for k in self.vecchia if k not in self.nuova])
                    conn.execute("UPDATE file SET visto = ? WHERE chiave >= ? AND chiave < ?",
                                 (adesso, prefisso, _limite_superiore(prefisso)))
                conn.executemany(
                    "INSERT OR REPLACE INTO file VALUES (?, ?, ?, ?, ?)",
                    [(k, v[0], v[1], json.dumps(v[2], ensure_ascii=False, separators=(",", ":")), adesso)
                     for k, v in self.da_scrivere.items()])
                conn.execute("DELETE FROM file WHERE visto < ?", (adesso - GIORNI_CACHE * 86400,))
            self._azzera = False
        except (sqlite3.Error, OSError, ValueError, TypeError):
            pass
        finally:
            conn.close()


# ---------------------------------------------------------------- report HTML

CSS = """
/* temi: scuro (predefinito) e chiaro; la scelta si cambia con il pulsante e si ricorda nel browser */
:root{color-scheme:dark;--sfondo:#2b2b2b;--pannello:#1e1e1e;--testo:#e0e0e0;--titolo:#0d6efd;--campo:#333;--campo-testo:#fff;--bordo:#555;--bordo-tab:#444;--testata:#212529;--testata-testo:#fff;--riga-pari:#2a2a2a;--btn-hover:#3d3d3d;--accento:#0d6efd;--disabilitato:#555;--gruppo:#1f3b63;--gruppo-testo:#fff}
:root[data-tema="colore"]{color-scheme:dark;--sfondo:#181a1f;--pannello:#21242b;--testo:#e6e8ec;--titolo:#6ba0ff;--campo:#2a2e37;--campo-testo:#e6e8ec;--bordo:#3a3f4b;--bordo-tab:#343a46;--testata:#2a2e37;--testata-testo:#e6e8ec;--riga-pari:#262a33;--btn-hover:#353b47;--accento:#4c8dff;--disabilitato:#3a3f4b;--gruppo:#2b3a57;--gruppo-testo:#e6e8ec}
:root[data-tema="verde"]{color-scheme:dark;--sfondo:#1e2321;--pannello:#2b312e;--testo:#e0e6e2;--titolo:#34d399;--campo:#383f3a;--campo-testo:#e0e6e2;--bordo:#555f59;--bordo-tab:#444d48;--testata:#2b312e;--testata-testo:#e0e6e2;--riga-pari:#232826;--btn-hover:#4a5550;--accento:#10b981;--disabilitato:#3a423e;--gruppo:#1f3b2e;--gruppo-testo:#ffffff}
:root[data-tema="chiaro"]{color-scheme:light;--sfondo:#eef1f5;--pannello:#fff;--testo:#1f2937;--titolo:#0b5ed7;--campo:#fff;--campo-testo:#111827;--bordo:#bcc5d1;--bordo-tab:#d5dbe3;--testata:#e6ebf2;--testata-testo:#1f2937;--riga-pari:#f4f6f9;--btn-hover:#eef2f7;--accento:#0b5ed7;--disabilitato:#a8b2c0;--gruppo:#dbe7f7;--gruppo-testo:#12305b}
body{font-family:sans-serif;padding:20px;background:var(--sfondo);color:var(--testo)}
.container{background:var(--pannello);padding:20px;border-radius:8px}
h2{color:var(--titolo)}
.logo{display:inline-block;width:1.3em;height:1.3em;vertical-align:-.25em;margin-right:.45em}
.logo svg{display:block;width:100%;height:100%}
.logo .lg-k{fill:#f4f4f4}.logo .lg-w{fill:#111}.logo .lg-t{stroke:#111}
:root[data-tema="chiaro"] .logo .lg-k{fill:#111}:root[data-tema="chiaro"] .logo .lg-w{fill:#fff}:root[data-tema="chiaro"] .logo .lg-t{stroke:#fff}
.percorso{font-size:22px;word-break:break-all}
input,select{padding:8px;background:var(--campo);color:var(--campo-testo);border:1px solid var(--bordo);border-radius:4px;font-size:14px}
input{width:100%;max-width:260px}
.filtri{display:flex;flex-wrap:wrap;gap:10px;align-items:center;margin-bottom:15px}
.gruppo{display:flex;gap:6px}
.fbtn{padding:8px 14px;background:var(--campo);color:var(--testo);border:1px solid var(--bordo);border-radius:4px;cursor:pointer;font-size:14px}
.fbtn:hover{background:var(--btn-hover)}
.fbtn.attivo{background:var(--accento);border-color:var(--accento);color:#fff}
#fStampa{background:#c74e00;border-color:#c74e00;color:#fff;font-weight:bold}
#fStampa:hover{background:#a84300;border-color:#a84300}
tr.grp td{background:var(--gruppo);color:var(--gruppo-testo);font-weight:bold;font-size:15px}
.tabella{overflow-x:auto}
table{width:100%;border-collapse:collapse;margin-top:10px;font-size:14px}
th,td{padding:10px;border:1px solid var(--bordo-tab);text-align:left}
th{background:var(--testata);color:var(--testata-testo);cursor:pointer;white-space:nowrap;user-select:none}
tr:nth-child(even){background:var(--riga-pari)}
.badge{padding:4px 8px;border-radius:4px;font-size:12px;font-weight:bold;color:#fff;display:inline-block}
.bg-danger{background:#dc3545}.bg-primary{background:#0d6efd}.bg-success{background:#198754}.bg-secondary{background:#6c757d}.bg-warning{background:#fd7e14;color:#fff}.bg-warning{background:#fd7e14;color:#fff}
.paginazione{margin:15px 0;display:flex;gap:8px;align-items:center}
.pag-btn{padding:5px 10px;background:var(--accento);color:#fff;border:none;border-radius:4px;cursor:pointer}
.pag-btn:disabled{background:var(--disabilitato);cursor:not-allowed}
.pannello-col{display:flex;flex-wrap:wrap;gap:10px 32px;align-items:flex-start;border:1px solid var(--bordo);border-radius:6px;padding:12px 16px;margin-bottom:15px}
.pannello-col[hidden]{display:none}
.pc-gruppo{display:flex;flex-direction:column;gap:5px;min-width:150px}
.pc-gruppo b{font-size:13px;color:var(--titolo)}
.pc-gruppo label{display:flex;gap:7px;align-items:center;cursor:pointer;font-size:14px;white-space:nowrap}
.pannello-col input{width:auto;max-width:none;padding:0;margin:0}
.pc-azioni{display:flex;flex-direction:column;gap:6px;margin-left:auto}
.riepilogo{border:1px solid var(--bordo);border-radius:6px;padding:12px 16px;margin-bottom:15px}
.riep-testa{display:flex;align-items:center;gap:8px;width:100%;background:none;border:0;padding:0;color:var(--titolo);font-size:15px;font-weight:600;cursor:pointer;text-align:left}
.riep-tot{margin:6px 0 0;font-size:14px}
.riep-gruppi{display:grid;grid-template-columns:repeat(auto-fit,minmax(230px,1fr));gap:14px 26px;margin-top:12px}
.riep-gruppi[hidden]{display:none}
.riep-gruppi h3{margin:0 0 6px;font-size:13px;color:var(--titolo)}
.riep-riga{display:grid;grid-template-columns:minmax(70px,max-content) 1fr 46px;gap:8px;align-items:center;width:100%;background:none;border:0;border-radius:4px;padding:3px 4px;color:var(--testo);font-size:13px;text-align:left;box-sizing:border-box}
button.riep-riga{cursor:pointer}
button.riep-riga:hover{background:var(--btn-hover)}
.riep-riga.attivo{background:var(--gruppo);color:var(--gruppo-testo)}
.riep-barra{height:8px;background:var(--bordo-tab);border-radius:4px;overflow:hidden}
.riep-barra i{display:block;height:100%;background:var(--accento);border-radius:4px;-webkit-print-color-adjust:exact;print-color-adjust:exact}
.riep-n{text-align:right}
.riep-altri{opacity:.75}
.solo-stampa{display:none}
.ctx-menu{position:absolute;background:var(--pannello);border:1px solid var(--bordo);border-radius:4px;box-shadow:0 2px 10px rgba(0,0,0,0.5);display:none;z-index:1000;min-width:150px}
.ctx-menu a{display:block;padding:8px 12px;color:var(--testo);text-decoration:none;font-size:13px;cursor:pointer}
.ctx-menu a:hover{background:var(--btn-hover)}
td.nome-cell{cursor:context-menu}
@page{size:A4 landscape;margin:10mm}
@media print{
*{-webkit-print-color-adjust:exact;print-color-adjust:exact}
body{background:#fff;color:#000;padding:0;font-size:10pt}
.container{background:#fff;padding:0;border-radius:0}
h2{color:#000;font-size:16pt;margin:0 0 6px}
.logo .lg-k{fill:#111!important}.logo .lg-w{fill:#fff!important}.logo .lg-t{stroke:#fff!important}
p{margin:2px 0;color:#000}
.percorso{font-size:11pt;word-break:break-all}
.filtri,.paginazione,.ord,.pannello-col,.riep-freccia{display:none}
.solo-stampa{display:block}
.tabella{overflow:visible}
table{font-size:8.5pt;margin-top:8px}
th,td{padding:3px 5px;border:1px solid #888;color:#000;overflow-wrap:break-word}
th{background:#e5e5e5;cursor:default;white-space:normal}
thead{display:table-header-group}
tr{break-inside:avoid}
tr:nth-child(even){background:#f2f2f2}
.badge{background:none !important;color:#000;border:1px solid #000;padding:0 4px;font-size:8pt}
tr.grp{break-after:avoid}
tr.grp td{background:#d9d9d9;color:#000;font-size:10pt;border-top:2px solid #000}
}
"""

JS = r"""
let perPagina = 50;   // risultati per pagina (scelti dal menu)
const SOGLIA_UNICA = 5000;   // oltre questi file la pagina unica rallenta il browser: si chiede conferma
const BADGE = {Video: 'danger', Audio: 'primary', Immagine: 'warning'};
const p2 = n => String(n).padStart(2, '0');
const fmtDim = b => b >= 1073741824 ? (b / 1073741824).toFixed(2) + ' GB' : (b / 1048576).toFixed(2) + ' MB';
const fmtDur = s => {
  if (s == null) return '-';
  s = Math.floor(s);
  const o = Math.floor(s / 3600), m = Math.floor(s % 3600 / 60), c = s % 60;
  return o ? `${o}:${p2(m)}:${p2(c)}` : `${p2(m)}:${p2(c)}`;
};
const dash = v => (v == null || v === '') ? '-' : String(v);
// bitrate: sotto 10.000 kbps -> kbps con separatore migliaia; sopra -> Mb/s con 2 decimali
// (formato della lingua del report: '9.122 kbps' in italiano, '9,122 kbps' in inglese)
const SOGLIA_MBPS = 10000;
const fmtBitrate = kbps => {
  if (kbps == null) return '-';
  if (kbps >= SOGLIA_MBPS) return (kbps / 1000).toLocaleString(lingua, {minimumFractionDigits: 2, maximumFractionDigits: 2}) + ' Mb/s';
  return Math.round(kbps).toLocaleString(lingua) + ' kbps';
};
// data di modifica (secondi) nel formato della lingua del report: 17/10/2026 oppure 2026-10-17
const fmtData = s => {
  const d = new Date(s * 1000), a = d.getFullYear(), me = p2(d.getMonth() + 1), g = p2(d.getDate());
  return L.fmt_data === 'ymd' ? `${a}-${me}-${g}` : `${g}/${me}/${a}`;
};

// HDR: "HDR10", "HLG", "HDR10 + DV", "Dolby Vision", con il picco di luminanza del master se noto
const fmtHdr = m => {
  if (m.hdr == null) return '-';
  if (!m.hdr) return L.no;
  const tipi = [];
  if (m.ht) tipi.push(m.ht);
  if (m.dvp != null) tipi.push(m.ht ? 'DV' : 'Dolby Vision');
  let s = tipi.length ? tipi.join(' + ') : L.si;   // HDR di tipo non riconosciuto
  if (m.mx) s += ' · ' + m.mx + ' nit';
  return s;
};
const tipHdr = m => {   // dettagli nel suggerimento che compare passando il mouse
  const p = [];
  if (m.mx) p.push('Mastering: ' + m.mx + ' nit');
  if (m.mc) p.push('MaxCLL: ' + m.mc);
  if (m.mf) p.push('MaxFALL: ' + m.mf);
  return p.join(' · ');
};
// ordine: senza HDR, HLG, HDR10, Dolby Vision senza base, HDR10/HLG + Dolby Vision
const rangoHdr = m => m.hdr == null ? null : (m.ht === 'HLG' ? 1 : m.ht === 'HDR10' ? 2 : 0) + (m.dvp != null ? 2 : 0) + (m.hdr && !m.ht && m.dvp == null ? 1 : 0);

// Profondità di colore: "10 bit · Main 10 @ L5.1"
const fmtColore = m => {
  if (m.t !== 'Video') return '-';
  const parti = [];
  if (m.cb) parti.push(m.cb + ' bit');
  if (m.pr) parti.push(m.pr + (m.lv ? ' @ L' + m.lv : ''));
  else if (m.lv) parti.push('L' + m.lv);
  return parti.length ? parti.join(' · ') : '-';
};

// Dolby Vision: "Profilo 8.1 (HDR10)", "Profilo 5", "Profilo 7 (con EL)"...
const BASE_DV = {1: 'HDR10', 2: 'SDR', 4: 'HLG'};
const fmtDV = m => {
  if (m.t !== 'Video') return '-';
  if (m.dvp == null) return L.no;
  let s = L.profilo + ' ' + m.dvp;
  if ((m.dvp === 8 || m.dvp === 10) && m.dvc != null) {
    s += '.' + m.dvc + (BASE_DV[m.dvc] ? ' (' + BASE_DV[m.dvc] + ')' : '');
  } else if (m.dvp === 7 && m.dve) {
    s += ' ' + L.con_el;                  // doppio layer: FEL o MEL (ffprobe non distingue i due casi)
  }
  return s;
};

// show = testo mostrato, key = valore usato per ordinare (numerico dove serve)
const TUTTE = [
  {id: 'nome', t: L.th.nome,   show: m => m.p,                          key: m => m.p.toLowerCase()},
  {id: 'artista', t: L.th.artista, show: m => dash(m.ar),                key: m => m.ar ? m.ar.toLowerCase() : null},
  {id: 'album',   t: L.th.album,   show: m => dash(m.al),                key: m => m.al ? m.al.toLowerCase() : null},
  {id: 'titolo',  t: L.th.titolo,  show: m => dash(m.ti),                key: m => m.ti ? m.ti.toLowerCase() : null},
  {id: 'anno',    t: L.th.anno,    show: m => dash(m.an),                key: m => m.an},
  {id: 'traccia', t: L.th.traccia, show: m => dash(m.tr),                key: m => m.tr},
  {id: 'tipo', t: L.th.tipo,        show: m => EXT_IMMAGINI.has((m.e || '').toLowerCase()) ? 'Foto' : (L.tipi[m.t] || m.t), key: m => EXT_IMMAGINI.has((m.e || '').toLowerCase()) ? 'Foto' : m.t},
  {id: 'est', t: L.th.est,        show: m => m.e,                          key: m => m.e},
  {id: 'dim', t: L.th.dim,  show: m => fmtDim(m.d),                  key: m => m.d},
  {id: 'data', t: L.th.data,  show: m => m.m == null ? '-' : fmtData(m.m),   key: m => m.m},
  {id: 'durata', t: L.th.durata,      show: m => fmtDur(m.du),                 key: m => m.du},
  {id: 'ris', t: L.th.ris, show: m => m.w ? m.w + 'x' + m.h : '-',  key: m => m.w ? m.w * m.h : null},
  {id: 'colore',  t: L.th.colore,  show: fmtColore, key: m => m.t !== 'Video' || !m.cb ? null : m.cb},
  {id: 'hdr',     t: L.th.hdr,         show: fmtHdr, tip: tipHdr, key: rangoHdr},
  {id: 'dv',      t: L.th.dv, show: fmtDV, key: m => m.t !== 'Video' ? null : (m.dvp == null ? 0 : m.dvp * 10 + (m.dvc || 0))},
  {id: 'fps', t: L.th.fps,         show: m => dash(m.f),                    key: m => m.f},
  {id: 'cv', t: L.th.cv,     show: m => dash(m.vc),                   key: m => m.vc || null},
  {id: 'ca', t: L.th.ca,     show: m => dash(m.ac),                   key: m => m.ac || null},
  {id: 'canali',  t: L.th.canali, show: m => m.ch == null ? '-' : (m.cl ? m.cl + ' (' + m.ch + ')' : m.ch + ' ch'), key: m => m.ch},
  {id: 'formato', t: L.th.formato, show: m => m.sr == null ? '-' : parseFloat((m.sr / 1000).toFixed(3)) + ' kHz' + (m.bd ? ' · ' + m.bd + ' bit' : ''), key: m => m.sr == null ? null : m.sr * 100 + (m.bd || 0)},
  {id: 'qualita', t: L.th.qualita, show: m => m.lo == null ? '-' : (m.lo ? 'Lossless' : 'Lossy'), key: m => m.lo == null ? null : (m.lo ? 1 : 0)},
  {id: 'copertina', t: L.th.copertina, show: m => m.t !== 'Audio' ? '-' : (m.cp ? L.si : L.no), key: m => m.t !== 'Audio' ? null : (m.cp ? 1 : 0)},
  {id: 'tracce',  t: L.th.tracce,   show: m => m.t === 'Video' && m.at ? m.at.join(' · ') : '-', key: m => m.t === 'Video' && m.at ? m.at.length : null},
  {id: 'bitrate_video', t: L.th.bitrate_video, show: m => (m.t !== 'Video' || m.bv == null) ? '-' : fmtBitrate(m.bv / 1000), key: m => m.t !== 'Video' ? null : m.bv},
  {id: 'bitrate_audio', t: L.th.bitrate_audio, show: m => (m.t !== 'Audio' || m.ba == null) ? '-' : fmtBitrate(m.ba / 1000), key: m => m.t !== 'Audio' ? null : m.ba},
];
// colonne mostrate: all'apertura quelle scelte nella finestra del programma; dal pulsante "Colonne" si cambiano
// al volo (i dati di tutte le colonne sono comunque nel report)
const attive = new Set(VISIBILI);
let COLS = TUTTE.filter(c => attive.has(c.id));

let filtrati = [...DATI], vista = filtrati, pagina = 1, colOrd = -1, asc = true, unica = false, inStampa = false;
// raggruppamento per sottocartella: attivo se il report è stato generato con i dati delle cartelle
let raggruppa = CARTELLE.length > 0, statGruppi = new Map();
// testo di ricerca in minuscolo, calcolato una volta; '\n' impedisce match a cavallo di due campi
// la ricerca non distingue maiuscole/minuscole né accenti: «bjork» trova «Björk», «beyonce» trova «Beyoncé»; le lettere che
// non si scompongono in lettera + accento (ø, æ, œ, ß, đ, ł) si riconducono alle lettere semplici
const SPECIALI = {'ø': 'o', 'æ': 'ae', 'œ': 'oe', 'ß': 'ss', 'đ': 'd', 'ł': 'l'};
const semplifica = t => t.toLowerCase().normalize('NFD').replace(/[\u0300-\u036f]/g, '').replace(/[øæœßđł]/g, c => SPECIALI[c]);
// la ricerca guarda nome file, estensione, tipo, tag e anche la sottocartella (CARTELLE[k]): il nome dell'album sta spesso solo lì
DATI.forEach(m => m._h = semplifica(m.p + '\n' + m.e + '\n' + (L.tipi[m.t] || m.t) + '\n' + (m.ar || '') + '\n' + (m.al || '') + '\n' + (m.ti || '') + '\n' + (m.k != null && CARTELLE[m.k] ? CARTELLE[m.k] : '')));
const tbody = document.querySelector('#mTable tbody');
const info = document.getElementById('infoPagina');
const prec = document.getElementById('btnPrec');
const succ = document.getElementById('btnSucc');

const thead = document.querySelector('#mTable thead');
function costruisciIntestazione() {
  const riga = document.createElement('tr');
  COLS.forEach((c, i) => {
    const th = document.createElement('th');
    th.textContent = c.t;
    const freccia = document.createElement('span');   // la freccia dell'ordinamento non si stampa
    freccia.className = 'ord';
    freccia.textContent = ' ↕';
    th.appendChild(freccia);
    th.onclick = () => ordina(i);
    riga.appendChild(th);
  });
  thead.replaceChildren(riga);
}
costruisciIntestazione();

function intestazioneGruppo(k) {
  const g = statGruppi.get(k) || {n: 0, d: 0};
  const riga = document.createElement('tr');
  riga.className = 'grp';
  const td = document.createElement('td');
  td.colSpan = COLS.length;
  td.textContent = '📁 ' + (CARTELLE[k] || L.radice) + '  —  ' + g.n + ' ' + L.file + '  ·  ' + fmtDim(g.d);
  riga.appendChild(td);
  return riga;
}

function render() {
  const tutte = unica || inStampa;                  // in stampa escono tutti i risultati, non solo la pagina corrente
  const tot = tutte ? 1 : Math.max(1, Math.ceil(filtrati.length / perPagina));
  pagina = Math.min(pagina, tot);
  tbody.replaceChildren();
  const frag = document.createDocumentFragment();   // un solo inserimento nella pagina: molto più veloce
  const visibili = tutte ? vista : vista.slice((pagina - 1) * perPagina, pagina * perPagina);
  visibili.forEach((m, i, pag) => {
    // intestazione della sottocartella: a ogni cambio di gruppo e all'inizio di ogni pagina
    if (raggruppa && (i === 0 || pag[i - 1].k !== m.k)) frag.appendChild(intestazioneGruppo(m.k));
    const riga = document.createElement('tr');
    COLS.forEach(c => {
      const td = document.createElement('td');
      if (c.id === 'tipo') {
        const sp = document.createElement('span');
        const chiaveTipo = EXT_IMMAGINI.has((m.e || '').toLowerCase()) ? 'Immagine' : m.t;
        sp.className = 'badge bg-' + (BADGE[chiaveTipo] || 'secondary');
        sp.textContent = EXT_IMMAGINI.has((m.e || '').toLowerCase()) ? 'Foto' : (L.tipi[m.t] || m.t);
        td.appendChild(sp);
      } else {
        td.textContent = c.show(m);   // textContent: i nomi dei file non vengono mai interpretati come HTML
        const sugg = c.tip && c.tip(m);
        if (sugg) td.title = sugg;
        if (c.id === 'nome') {
          td.className = 'nome-cell';
          td.oncontextmenu = (e) => mostraMenuContext(e, m);
        }
      }
      riga.appendChild(td);
    });
    frag.appendChild(riga);
  });
  tbody.appendChild(frag);
  const conteggio = `${L.mostrati}: ${filtrati.length}` + (filtrati.length !== DATI.length ? ` ${L.su} ${DATI.length}` : '');
  info.textContent = tutte ? `${L.pagina_unica} (${conteggio})` : `${L.pagina} ${pagina} ${L.di} ${tot} (${conteggio})`;
  prec.disabled = pagina <= 1;
  succ.disabled = pagina >= tot;
  selPP.disabled = unica;               // in pagina unica il numero per pagina non serve
}

function ordinaLista() {
  if (colOrd >= 0) ordinaPerColonna();
  // con il raggruppamento i file restano insieme per cartella (l'ordinamento è stabile: dentro ogni
  // gruppo vale l'ordine scelto)
  vista = raggruppa ? filtrati.slice().sort((a, b) => a.k - b.k) : filtrati;
}

function ordinaPerColonna() {
  const key = COLS[colOrd].key, dir = asc ? 1 : -1;
  // la chiave di ogni riga si calcola una volta sola, non a ogni confronto
  const righe = filtrati.map(m => [key(m), m]);
  righe.sort((a, b) => {
    const x = a[0], y = b[0];
    if (x == null && y == null) return 0;
    if (x == null) return 1;           // i valori mancanti vanno sempre in fondo
    if (y == null) return -1;
    return (x > y ? 1 : x < y ? -1 : 0) * dir;
  });
  filtrati = righe.map(r => r[1]);
}

function ordina(i) {
  if (colOrd === i) asc = !asc; else { colOrd = i; asc = true; }
  ordinaLista();
  pagina = 1;
  render();
}

// --- filtri: ricerca testuale, tipo, HDR e risoluzione si combinano tra loro
const filtro = {q: '', parole: [], tipo: 'Tutti', hdr: false, res: null, giorni: null, riep: null, img: false};   // riep = riga del riepilogo scelta con un clic

// estensioni considerate Â«immagineÂ» (allineate al programma)
const EXT_IMMAGINI = new Set(['jpg','jpeg','png','gif','bmp','tif','tiff','webp','svg','heic','ico','raw','cr2','nef','arw','psd','avif']);

// conRiep = false: tutti i filtri tranne quello scelto dal riepilogo (serve a mostrare, nel gruppo scelto, anche le alternative)
function parseAvanzato(q) {
  const adv = {ext: [], size: null, year: null, res: null, hdr: null, durata: null};
  const words = [];
  const tokens = q.split(/\s+/);
  tokens.forEach(t => {
    const lower = t.toLowerCase();
    if (lower.startsWith('ext:')) adv.ext.push(...lower.slice(4).split(','));
    else if (lower.startsWith('size:')) adv.size = lower.slice(5);
    else if (lower.startsWith('year:')) adv.year = lower.slice(5);
    else if (lower.startsWith('res:')) adv.res = lower.slice(4);
    else if (lower.startsWith('hdr:')) adv.hdr = lower.slice(4);
    else if (lower.startsWith('durata:')) adv.durata = lower.slice(7);
    else words.push(t);
  });
  return {adv, words};
}

function checkAdv(m, adv) {
  if (!adv) return true;
  if (adv.ext && adv.ext.length > 0 && !adv.ext.includes((m.e || '').toLowerCase())) return false;
  if (adv.year) {
    const op = adv.year[0];
    const val = parseInt(adv.year.replace(/[<>=]/g, ''));
    if (isNaN(val)) return true; // se non è un numero, ignora il filtro
    if (!m.an) return false;
    if (op === '>' && !(m.an > val)) return false;
    if (op === '<' && !(m.an < val)) return false;
    if (op !== '>' && op !== '<' && m.an !== val) return false;
  }
  if (adv.size) {
    const cleanSize = adv.size.replace(/\\s+/g, '').toUpperCase();
    const match = cleanSize.match(/^([<>]?)([0-9.,]+)(GB|MB|KB|B)?$/);
    if (match) {
      const op = match[1] || '=';
      let val = parseFloat(match[2].replace(',', '.'));
      if (isNaN(val)) return true;
      const unit = match[3] || 'B';
      let mult = 1;
      if (unit === 'GB') mult = 1024**3; else if (unit === 'MB') mult = 1024**2; else if (unit === 'KB') mult = 1024;
      const target = val * mult;
      const bytes = m.d || 0;
      if (op === '>' && !(bytes > target)) return false;
      if (op === '<' && !(bytes < target)) return false;
      if (op === '=' && Math.abs(bytes - target) > (target * 0.1)) return false;
    }
  }
  if (adv.res) {
    if (!m.w || !m.h) return false;
    const maxW = m.w > m.h ? m.w : m.h;
    const val = parseInt(adv.res.replace(/[^0-9]/g, ''));
    if (adv.res === '4k' && maxW < 3840) return false;
    else if (adv.res === '1080' && (maxW < 1920 || maxW >= 3840)) return false;
    else if (adv.res === '720' && (maxW < 1280 || maxW >= 1920)) return false;
    else if (!isNaN(val) && !adv.res.includes('k') && maxW !== val && val > 100) return false;
  }
  if (adv.hdr) {
    const h = adv.hdr.toLowerCase();
    if (['si', 'sì', 'yes', 'true', '1'].includes(h) && m.hdr !== true) return false;
    if (['no', 'false', '0'].includes(h) && m.hdr === true) return false;
  }
  if (adv.durata) {
    if (!m.du) return false;
    const min = m.du / 60;
    const op = adv.durata[0];
    const val = parseInt(adv.durata.replace(/[<>=]/g, ''));
    if (isNaN(val)) return true;
    if (op === '>' && !(min > val)) return false;
    if (op === '<' && !(min < val)) return false;
    if (op !== '>' && op !== '<' && Math.round(min) !== val) return false;
  }
  return true;
}

function passaFiltri(m, limite, conRiep) {
  return (filtro.tipo === 'Tutti' || m.t === filtro.tipo) &&
    (!filtro.hdr || m.hdr === true) &&
    // "sotto X" = sia larghezza sia altezza inferiori (così un film 1920x800 non è "sotto 1080p")
    (!filtro.res || (m.w != null && m.h != null && m.w < filtro.res[0] && m.h < filtro.res[1])) &&
    (!filtro.giorni || (m.m != null && m.m >= limite)) &&
    (!filtro.img || EXT_IMMAGINI.has((m.e || '').toLowerCase())) &&
    filtro.parole.every(w => m._h.includes(w)) &&   // più parole: devono esserci tutte, in qualsiasi punto (nome, tag, cartella)
    checkAdv(m, filtro.adv) &&
    (!conRiep || !filtro.riep || valoreRiep(filtro.riep.gruppo, m) === filtro.riep.valore);
}

function applicaFiltri() {
  const limite = filtro.giorni ? Date.now() / 1000 - filtro.giorni * 86400 : 0;   // "ultimi N giorni" rispetto a ora
  filtrati = DATI.filter(m => passaFiltri(m, limite, true));
  // pagina unica: se i filtri allargano molto l'elenco, si chiede di nuovo conferma (altrimenti si torna alle pagine)
  if (unica && filtrati.length > SOGLIA_UNICA && !chiediUnica(filtrati.length)) {
    unica = false;
    bUnica.classList.remove('attivo');
  }
  statGruppi = new Map();              // quanti file e quanto spazio per ogni cartella (dopo i filtri)
  if (CARTELLE.length) for (const m of filtrati) {
    let g = statGruppi.get(m.k);
    if (!g) statGruppi.set(m.k, g = {n: 0, d: 0});
    g.n++; g.d += m.d;
  }
  aggiornaRiepilogo(limite);
  ordinaLista();                       // mantiene l'ordinamento scelto
  pagina = 1;
  render();
}

// --- riepilogo in testa al report: totali e ripartizioni dei file filtrati. Un clic su una riga filtra la tabella;
// nel gruppo scelto restano visibili anche le altre voci, così si può passare da una all'altra (come nei filtri di un negozio online)
const lingua = document.documentElement.lang || 'it';
const num = (n, dec) => n.toLocaleString(lingua, {maximumFractionDigits: dec || 0});
const fmtGrande = b => b >= 1099511627776 ? num(b / 1099511627776, 2) + ' TB' : b >= 1073741824 ? num(b / 1073741824, 2) + ' GB' : num(b / 1048576, 1) + ' MB';
const fmtOre = sec => (sec >= 36000 ? num(Math.round(sec / 3600)) : num(sec / 3600, 1)) + ' ' + L.riep_ore;
// risoluzione per larghezza (così 1920x800 è 1080p); i formati più quadrati (4:3, 1440x1080) si ricondurono al 16:9 dall'altezza
const classeRis = (w, h) => {
  const ef = h && w / h < 1.7 ? h * 16 / 9 : w;
  return ef >= 3200 ? '4K' : ef >= 2300 ? '1440p' : ef >= 1700 ? '1080p' : ef >= 1150 ? '720p' : L.riep_altro;
};
const etichettaHdr = m => {
  if (m.hdr == null) return null;
  if (!m.hdr) return L.riep_sdr;
  const t = [];
  if (m.ht) t.push(m.ht);
  if (m.dvp != null) t.push(m.ht ? 'DV' : 'Dolby Vision');
  return t.length ? t.join(' + ') : L.riep_hdr_altro;
};
// per = tipo di file a cui il gruppo si applica; val(m) = la voce in cui cade il file (null = non conta); fisso = ordine fisso
const GRUPPI_RIEP = [
  {id: 'ris', per: 'Video', fisso: ['4K', '1440p', '1080p', '720p'], val: m => m.w && m.h ? classeRis(m.w, m.h) : null},
  {id: 'hdr', per: 'Video', val: etichettaHdr},
  {id: 'cv', per: 'Video', val: m => m.vc || null},
  {id: 'ca', per: 'Video', val: m => m.ac || null},
  {id: 'caA', col: 'ca', per: 'Audio', val: m => m.ac || null},
  {id: 'formato', per: 'Audio', val: m => m.sr == null ? null : parseFloat((m.sr / 1000).toFixed(3)) + ' kHz' + (m.bd ? ' \u00b7 ' + m.bd + ' bit' : '')},
  {id: 'qualita', per: 'Audio', val: m => m.lo == null ? null : (m.lo ? 'Lossless' : 'Lossy')},
];
const valoreRiep = (g, m) => m.t === g.per ? g.val(m) : null;
const titoloGruppo = g => L.nomi_col[g.col || g.id] +
  ((g.id === 'ca' || g.id === 'caA') && haVideo && haAudio ? ' (' + (g.per === 'Video' ? L.riep_video : L.riep_brani) + ')' : '');
const MAX_RIGHE = 6;   // oltre, le voci meno frequenti si raccolgono in "Altri"

function impostaRiep(g, valore) {   // lo stesso clic due volte toglie il filtro
  const r = filtro.riep;
  filtro.riep = r && r.gruppo === g && r.valore === valore ? null : {gruppo: g, valore};
  applicaFiltri();
}

function rigaRiep(etichetta, n, max, attivo, g, valore) {
  const el = document.createElement(g ? 'button' : 'div');
  el.className = 'riep-riga' + (attivo ? ' attivo' : '') + (g ? '' : ' riep-altri');
  if (g) { el.type = 'button'; el.setAttribute('aria-pressed', String(attivo)); el.onclick = () => impostaRiep(g, valore); }
  const l = document.createElement('span'); l.textContent = etichetta;
  const barra = document.createElement('span'); barra.className = 'riep-barra';
  const i = document.createElement('i'); i.style.width = (max ? Math.max(n ? 2 : 0, n / max * 100) : 0) + '%'; barra.appendChild(i);
  const c = document.createElement('span'); c.className = 'riep-n'; c.textContent = num(n);
  el.append(l, barra, c);
  return el;
}

function aggiornaRiepilogo(limite) {
  let spazio = 0, durata = 0;
  const artisti = new Set(), album = new Set();
  for (const m of filtrati) {
    spazio += m.d || 0; durata += m.du || 0;
    if (m.t === 'Audio') { if (m.ar) artisti.add(m.ar); if (m.al) album.add((m.ar || '') + '\n' + m.al); }
  }
  document.getElementById('riepTot').textContent = [
    num(filtrati.length) + ' ' + L.file, fmtGrande(spazio), durata ? fmtOre(durata) : '',
    artisti.size ? num(artisti.size) + ' ' + L.riep_artisti : '', album.size ? num(album.size) + ' ' + L.riep_album : ''
  ].filter(Boolean).join(' \u00b7 ');
  const base = filtro.riep ? DATI.filter(m => passaFiltri(m, limite, false)) : filtrati;   // senza il filtro del riepilogo
  const corpo = document.getElementById('riepCorpo');
  corpo.replaceChildren();
  for (const g of GRUPPI_RIEP) {
    if (!(g.per === 'Video' ? haVideo : haAudio)) continue;
    const attivo = filtro.riep && filtro.riep.gruppo === g ? filtro.riep.valore : null;
    const conta = new Map();
    for (const m of (attivo !== null ? base : filtrati)) {
      const v = valoreRiep(g, m);
      if (v !== null) conta.set(v, (conta.get(v) || 0) + 1);
    }
    if (attivo !== null && !conta.has(attivo)) conta.set(attivo, 0);   // la voce scelta resta sempre visibile (per poterla togliere)
    if (!conta.size) continue;
    let voci = [...conta.entries()];
    if (g.fisso) {
      const pos = v => g.fisso.indexOf(v) < 0 ? 99 : g.fisso.indexOf(v);
      voci.sort((a, b) => pos(a[0]) - pos(b[0]));
    } else voci.sort((a, b) => b[1] - a[1] || a[0].localeCompare(b[0]));
    let altri = 0;
    if (voci.length > MAX_RIGHE) {
      const tieni = voci.slice(0, MAX_RIGHE - 1);
      const scelta = voci.find(v => v[0] === attivo);
      if (scelta && !tieni.includes(scelta)) tieni[MAX_RIGHE - 2] = scelta;   // la voce scelta resta sempre visibile
      altri = voci.filter(v => !tieni.includes(v)).reduce((t, v) => t + v[1], 0);
      voci = tieni;
    }
    const max = Math.max(altri, ...voci.map(v => v[1]));
    const box = document.createElement('div');
    const h = document.createElement('h3'); h.textContent = titoloGruppo(g); box.appendChild(h);
    voci.forEach(([v, n]) => box.appendChild(rigaRiep(v, n, max, v === attivo, g, v)));
    if (altri) box.appendChild(rigaRiep(L.riep_altri, altri, max, false, null, null));
    corpo.appendChild(box);
  }
}

// apri/chiudi: chiuso resta la riga dei totali; la scelta si ricorda per questo report
const bRiep = document.getElementById('riepTesta');
const corpoRiep = document.getElementById('riepCorpo');
const mostraRiep = (aperto, salva) => {
  corpoRiep.hidden = !aperto;
  bRiep.setAttribute('aria-expanded', String(aperto));
  document.getElementById('riepFreccia').textContent = aperto ? '\u25be' : '\u25b8';
  if (salva) { try { localStorage.setItem('mdl-riep-' + ID_REPORT, aperto ? '1' : '0'); } catch (e) {} }
};
bRiep.onclick = () => mostraRiep(corpoRiep.hidden, true);
let riepAperto = true;
try { riepAperto = localStorage.getItem('mdl-riep-' + ID_REPORT) !== '0'; } catch (e) {}
mostraRiep(riepAperto, false);

// --- filtri sensati per il contenuto: un report di sola musica non offre Video, HDR e risoluzione; uno di soli
// film non offre i tag musicali. Conta ciò che c'è nel report, non il nome del profilo.
const haVideo = DATI.some(m => m.t === 'Video');
const haAudio = DATI.some(m => m.t === 'Audio');
if (!(haVideo && haAudio)) document.getElementById('gTipo').style.display = 'none';   // con un solo tipo, Tutti/Video/Audio non filtrerebbero nulla
if (!haVideo) {
  document.getElementById('fHdr').style.display = 'none';
  document.getElementById('fRes').style.display = 'none';
}
const bottoniTipo = document.querySelectorAll('#gTipo .fbtn');
bottoniTipo.forEach(b => b.onclick = () => {
  filtro.tipo = b.dataset.tipo;
  bottoniTipo.forEach(x => x.classList.toggle('attivo', x === b));
  applicaFiltri();
});
const bHdr = document.getElementById('fHdr');
bHdr.onclick = () => { filtro.hdr = !filtro.hdr; bHdr.classList.toggle('attivo', filtro.hdr); applicaFiltri(); };
const bImg = document.getElementById('fImg');
if (bImg) bImg.onclick = () => { filtro.img = !filtro.img; bImg.classList.toggle('attivo', filtro.img); applicaFiltri(); };
const selRes = document.getElementById('fRes');
selRes.onchange = () => { filtro.res = selRes.value ? selRes.value.split(',').map(Number) : null; applicaFiltri(); };
const selData = document.getElementById('fData');
selData.onchange = () => { filtro.giorni = selData.value ? Number(selData.value) : null; applicaFiltri(); };
const inputCerca = document.getElementById('cercaInput');
let timer;
inputCerca.addEventListener('input', () => {
  clearTimeout(timer);
  timer = setTimeout(() => {
    const rawQuery = inputCerca.value;
    filtro.q = rawQuery.toLowerCase().trim();
    const parsed = parseAvanzato(rawQuery);
    filtro.adv = parsed.adv;
    filtro.parole = semplifica(parsed.words.join(" ")).split(/\s+/).filter(Boolean);
    applicaFiltri();
  }, 200);
});
document.getElementById('fReset').onclick = () => {
  filtro.q = ''; filtro.parole = []; filtro.tipo = 'Tutti'; filtro.hdr = false; filtro.res = null; filtro.giorni = null; filtro.riep = null; filtro.img = false; filtro.adv = {};
  inputCerca.value = ''; selRes.value = ''; selData.value = '';
  bHdr.classList.remove('attivo');
  const bImgReset = document.getElementById('fImg'); if (bImgReset) bImgReset.classList.remove('attivo');
  bottoniTipo.forEach(x => x.classList.toggle('attivo', x.dataset.tipo === 'Tutti'));
  applicaFiltri();
};
prec.onclick = () => { if (pagina > 1) { pagina--; render(); } };
succ.onclick = () => { pagina++; render(); };
const bGruppi = document.getElementById('fGruppi');
if (!CARTELLE.length) bGruppi.style.display = 'none';   // report senza dati delle cartelle: niente pulsante
bGruppi.classList.toggle('attivo', raggruppa);
bGruppi.onclick = () => {
  raggruppa = !raggruppa;
  bGruppi.classList.toggle('attivo', raggruppa);
  ordinaLista();
  pagina = 1;
  render();
};

// pagina unica: tutti i risultati in una sola pagina, senza paginazione
const chiediUnica = n => confirm(L.conferma.replace('{n}', n.toLocaleString()));
const bUnica = document.getElementById('fUnica');
bUnica.onclick = () => {
  if (!unica && filtrati.length > SOGLIA_UNICA && !chiediUnica(filtrati.length)) return;
  unica = !unica;
  bUnica.classList.toggle('attivo', unica);
  pagina = 1;
  render();
};

// --- colonne: il pannello elenca tutte le colonne per gruppo (File, Tag musicali, Video, Audio); le caselle
// mostrano o nascondono la colonna subito, senza rigenerare il report. Deve restarne almeno una.
const pCol = document.getElementById('pColonne');
const bCol = document.getElementById('fColonne');
const caselle = new Map();   // id colonna -> casella

function applicaColonne() {
  const idOrd = colOrd >= 0 ? COLS[colOrd].id : null;   // la colonna per cui si sta ordinando
  COLS = TUTTE.filter(c => attive.has(c.id));
  colOrd = idOrd ? COLS.findIndex(c => c.id === idOrd) : -1;
  costruisciIntestazione();
  if (idOrd && colOrd < 0) applicaFiltri();   // la colonna ordinata è sparita: si torna all'ordine di partenza
  else render();                              // altrimenti si resta sulla stessa pagina
}

function cambiaColonna(id, mostra) {
  if (!mostra && attive.size <= 1) { caselle.get(id).checked = true; return; }
  if (mostra) attive.add(id); else attive.delete(id);
  applicaColonne();
}

function impostaColonne(ids) {
  attive.clear();
  ids.forEach(id => attive.add(id));
  caselle.forEach((cb, id) => { cb.checked = attive.has(id); });
  applicaColonne();
}

(function costruisciPannello() {
  const note = new Set(GRUPPI.flatMap(g => g[1]));
  const gruppi = GRUPPI.map(g => [g[0], g[1].slice()]);
  TUTTE.forEach(c => { if (!note.has(c.id)) gruppi[0][1].push(c.id); });   // colonne non previste: nel primo gruppo
  const utili = {gr_video: haVideo, gr_tag: haAudio};   // gruppi che servono solo se nel report ci sono file di quel tipo
  gruppi.forEach(([titolo, ids]) => {
    if (utili[titolo] === false && !ids.some(id => attive.has(id))) return;   // gruppo inutile e nessuna sua colonna in uso
    const box = document.createElement('div');
    box.className = 'pc-gruppo';
    const h = document.createElement('b');
    h.textContent = L[titolo] || titolo;
    box.appendChild(h);
    ids.forEach(id => {
      const etichetta = document.createElement('label');
      const cb = document.createElement('input');
      cb.type = 'checkbox';
      cb.checked = attive.has(id);
      cb.onchange = () => cambiaColonna(id, cb.checked);
      etichetta.appendChild(cb);
      etichetta.appendChild(document.createTextNode(L.nomi_col[id] || id));
      box.appendChild(etichetta);
      caselle.set(id, cb);
    });
    pCol.appendChild(box);
  });
  const azioni = document.createElement('div');
  azioni.className = 'pc-azioni';
  [[L.col_tutte, () => [...caselle.keys()]], [L.col_predef, () => VISIBILI]].forEach(([testo, ids]) => {
    const b = document.createElement('button');
    b.className = 'fbtn';
    b.textContent = testo;
    b.onclick = () => impostaColonne(ids());
    azioni.appendChild(b);
  });
  pCol.appendChild(azioni);
})();
bCol.onclick = () => {
  pCol.hidden = !pCol.hidden;
  bCol.classList.toggle('attivo', !pCol.hidden);
  bCol.setAttribute('aria-expanded', String(!pCol.hidden));
};

// tema chiaro / scuro (o Colore, se il report è nato con quel tema): il pulsante propone l'altro; la scelta resta salvata nel browser
const bTema = document.getElementById('fTema');
const aggiornaTema = () => {
  const chiaro = !!document.documentElement && document.documentElement.getAttribute('data-tema') === 'chiaro';
  if (chiaro) bTema.textContent = TEMA_BASE === 'colore' ? L.tema_colore : (TEMA_BASE === 'verde' ? L.tema_verde : L.tema_scuro);
  else bTema.textContent = L.tema_chiaro;
};
bTema.onclick = () => {
  const radice = document.documentElement;
  if (!radice) return;
  const nuovo = radice.getAttribute('data-tema') === 'chiaro' ? TEMA_BASE : 'chiaro';
  radice.setAttribute('data-tema', nuovo);
  try { localStorage.setItem('mdl-tema-' + ID_REPORT, nuovo); } catch (e) {}   // vale per questo report; senza memoria del browser, solo per questa pagina
  aggiornaTema();
};
aggiornaTema();

// risultati per pagina: 50 / 100 / 500 / 1000. Si resta sui file che si stavano guardando.
const selPP = document.getElementById('fPerPagina');
selPP.onchange = () => {
  const primo = (pagina - 1) * perPagina;       // indice del primo file visibile
  perPagina = Number(selPP.value);
  pagina = Math.floor(primo / perPagina) + 1;
  render();
};

// esportazione CSV: tutte le righe che i filtri lasciano visibili (non solo la pagina corrente), nell'ordine
// scelto e con le colonne mostrate in quel momento; separatore e BOM UTF-8 perché Excel apra bene accenti e colonne
const csvCella = v => {
  let s = String(v == null ? '' : v);
  if (/^[=+\-@\t\r]/.test(s) && s !== '-') s = "'" + s;   // evita che Excel scambi il testo per una formula
  return '"' + s.replace(/"/g, '""') + '"';
};
document.getElementById('fCsv').onclick = () => {
  const sep = L.csv_sep || ';';
  const conCartelle = CARTELLE.length > 0;
  const righe = [(conCartelle ? [L.cartella] : []).concat(COLS.map(c => c.t)).map(csvCella).join(sep)];
  for (const m of vista) {
    const celle = conCartelle ? [CARTELLE[m.k] || L.radice] : [];
    COLS.forEach(c => celle.push(c.show(m)));
    righe.push(celle.map(csvCella).join(sep));
  }
  const blob = new Blob(['\ufeff' + righe.join('\r\n')], {type: 'text/csv;charset=utf-8'});
  const oggi = new Date(), a = document.createElement('a');
  a.href = URL.createObjectURL(blob);
  a.download = `media_report_${oggi.getFullYear()}-${p2(oggi.getMonth() + 1)}-${p2(oggi.getDate())}.csv`;
  document.body.appendChild(a);
  a.click();
  a.remove();
  setTimeout(() => URL.revokeObjectURL(a.href), 2000);
};

// stampa: il layout è nel CSS (@media print); qui si prepara il contenuto
function descrizioneFiltri() {
  const f = [];
  if (filtro.tipo !== 'Tutti') f.push(L.tipi[filtro.tipo] || filtro.tipo);
  if (filtro.hdr) f.push(bHdr.textContent);
  if (filtro.res && selRes.options && selRes.options[selRes.selectedIndex]) f.push(selRes.options[selRes.selectedIndex].text);
  if (filtro.giorni && selData.options && selData.options[selData.selectedIndex]) f.push(selData.options[selData.selectedIndex].text);
  if (filtro.riep) f.push(titoloGruppo(filtro.riep.gruppo) + ': ' + filtro.riep.valore);
  if (filtro.q) f.push('"' + inputCerca.value + '"');
  const n = filtrati.length + (filtrati.length !== DATI.length ? ` ${L.su} ${DATI.length}` : '');
  return (f.length ? `${L.filtri}: ${f.join(' · ')}  —  ` : '') + `${n} ${L.file}`;
}
const bStampa = document.getElementById('fStampa');
bStampa.onclick = () => {
  if (filtrati.length > SOGLIA_UNICA && !confirm(L.conferma_stampa.replace('{n}', filtrati.length.toLocaleString()))) return;
  window.print();
};
if (typeof window !== 'undefined') {   // vale anche per Ctrl+P: prima della stampa si mostrano tutti i risultati
  window.addEventListener('beforeprint', () => {
    document.getElementById('stampaFiltri').textContent = descrizioneFiltri();
    inStampa = true;
    render();
  });
  window.addEventListener('afterprint', () => { inStampa = false; render(); });
}
applicaFiltri();

// --- Menu contestuale per copiare nome e percorso
const ctxMenu = document.getElementById("ctxMenu");
document.getElementById("ctxCopyName").textContent = L.copia_nome;
document.getElementById("ctxCopyPath").textContent = L.copia_percorso;
let ctxTestoNome = "";
let ctxTestoPercorso = "";

function mostraMenuContext(e, m) {
  e.preventDefault();
  ctxTestoNome = m.p;
  ctxTestoPercorso = (PERCORSO_BASE ? PERCORSO_BASE + "\\" : "") + (m.rp || m.p);
  ctxMenu.style.display = "block";
  ctxMenu.style.left = e.pageX + "px";
  ctxMenu.style.top = e.pageY + "px";
}

function copiaAppunti(testo, elemento) {
  navigator.clipboard.writeText(testo).then(() => {
    const orig = elemento.textContent;
    elemento.textContent = "Copiato!";
    setTimeout(() => elemento.textContent = orig, 1000);
    setTimeout(() => ctxMenu.style.display = "none", 1000);
  }).catch(err => {
    alert("Impossibile copiare: " + err);
  });
}

document.getElementById("ctxCopyName").onclick = function() { copiaAppunti(ctxTestoNome, this); };
document.getElementById("ctxCopyPath").onclick = function() { copiaAppunti(ctxTestoPercorso, this); };

document.addEventListener("click", () => { ctxMenu.style.display = "none"; });
document.addEventListener("scroll", () => { ctxMenu.style.display = "none"; });

// --- Logica finestra di aiuto
const helpModal = document.getElementById("helpModal");
document.getElementById("fAiutoRicerca").onclick = () => { helpModal.style.display = "flex"; };
document.getElementById("closeHelp").onclick = () => { helpModal.style.display = "none"; };
helpModal.onclick = (e) => { if (e.target === helpModal) helpModal.style.display = "none"; };
"""

TEMPLATE = """<!DOCTYPE html>
<html lang="__LANG__"><head><meta charset="UTF-8">
<title>__TITOLO__ - Media Report</title>
<script>var t="__TEMA__";try{var m=localStorage.getItem("mdl-tema-__IDREP__");if(m==="chiaro"||m==="scuro"||m==="colore"||m==="verde")t=m}catch(e){}document.documentElement.setAttribute("data-tema",t)</script>
<link rel="icon" type="image/svg+xml" href="data:image/svg+xml,__FAVICON__">
<style>__CSS__</style></head>
<body><div class="container">
<h2><span class="logo">__LOGO__</span>Media Report v__VER__</h2>
<p class="percorso"><strong>__T_R_CARTELLA__</strong> __CARTELLA__</p>
<p><strong>__T_R_GENERATO__</strong> __DATA__ &nbsp;&middot;&nbsp; <strong>ffprobe:</strong> __FFPROBE__</p>
<p><strong>__T_R_TOTALI__</strong> __NFILE__ &nbsp;&middot;&nbsp; <strong>__T_R_N_CARTELLE__</strong> __NCARTELLE__ &nbsp;&middot;&nbsp; <strong>__T_R_SPAZIO__</strong> __SPAZIO__</p>
<div class="riepilogo" id="riepilogo">
  <button class="riep-testa" id="riepTesta" aria-expanded="true" aria-controls="riepCorpo"><span>__T_R_RIEPILOGO__</span><span class="riep-freccia" id="riepFreccia">&#9662;</span></button>
  <p class="riep-tot" id="riepTot"></p>
  <div class="riep-gruppi" id="riepCorpo"></div>
</div>
<p id="stampaFiltri" class="solo-stampa"></p>
<div class="filtri">
  <div style="display:flex; gap:5px; align-items:center;">
    <input type="text" id="cercaInput" placeholder="__T_R_CERCA__">
    <button class="fbtn" id="fAiutoRicerca" style="padding:8px 12px; font-weight:bold;" title="Mostra comandi">?</button>
  </div>
  <div class="gruppo" id="gTipo">
    <button class="fbtn attivo" data-tipo="Tutti">__T_R_TUTTI__</button>
    <button class="fbtn" data-tipo="Video">__T_R_VIDEO__</button>
    <button class="fbtn" data-tipo="Audio">__T_R_AUDIO__</button>
  </div>
  <button class="fbtn" id="fHdr">__T_R_SOLO_HDR__</button>
  <button class="fbtn" id="fImg">__T_R_SOLO_IMMAGINI__</button>
  <select id="fRes">
    <option value="">__T_R_RES_QUALSIASI__</option>
    <option value="1280,720">__T_R_RES_720__</option>
    <option value="1920,1080">__T_R_RES_1080__</option>
    <option value="2560,1440">__T_R_RES_1440__</option>
    <option value="3840,2160">__T_R_RES_4K__</option>
  </select>
  <select id="fData">
    <option value="">__T_R_DATA_QUALSIASI__</option>
    <option value="7">__T_R_DATA_7__</option>
    <option value="30">__T_R_DATA_30__</option>
  </select>
  <button class="fbtn" id="fGruppi">__T_R_GRUPPI__</button>
  <button class="fbtn" id="fColonne" aria-controls="pColonne" aria-expanded="false">__T_R_COLONNE__</button>
  <button class="fbtn" id="fReset">__T_R_AZZERA__</button>
  <button class="fbtn" id="fCsv">__T_R_CSV__</button>
  <button class="fbtn" id="fStampa">__T_R_STAMPA__</button>
  <button class="fbtn" id="fTema">__T_R_TEMA__</button>
</div>
<div class="pannello-col" id="pColonne" hidden></div>
<div class="paginazione">
  <button id="btnPrec" class="pag-btn">__T_R_PREC__</button>
  <span id="infoPagina"></span>
  <button id="btnSucc" class="pag-btn">__T_R_SUCC__</button>
  <select id="fPerPagina">
    <option value="50">50 __T_R_PER_PAGINA__</option>
    <option value="100">100 __T_R_PER_PAGINA__</option>
    <option value="500">500 __T_R_PER_PAGINA__</option>
    <option value="1000">1000 __T_R_PER_PAGINA__</option>
  </select>
  <button class="fbtn" id="fUnica">__T_R_UNICA__</button>
</div>
<div class="tabella"><table id="mTable"><thead></thead><tbody></tbody></table></div>
<div id="helpModal" style="display:none; position:fixed; top:0; left:0; width:100%; height:100%; background:rgba(0,0,0,0.6); z-index:2000; align-items:center; justify-content:center;">
  <div style="background:var(--pannello); padding:20px; border-radius:8px; max-width:500px; width:90%; border:1px solid var(--bordo); box-shadow:0 4px 20px rgba(0,0,0,0.5);">
    <h3 style="margin-top:0; color:var(--titolo);">Ricerca Avanzata</h3>
    <p style="font-size:14px; margin-bottom:15px;">Puoi usare questi comandi nella barra di ricerca per filtrare istantaneamente i file (es. <code>Dragon size:&gt;5GB</code>):</p>
    <ul style="font-size:14px; line-height:1.6; padding-left:20px;">
      <li><code>ext:mkv</code> — Cerca per estensione (es. <code>ext:mkv,mp4</code>)</li>
      <li><code>size:&gt;10GB</code> — Cerca per dimensione (es. <code>size:&lt;500MB</code>)</li>
      <li><code>year:2020</code> — Cerca per anno (es. <code>year:&gt;2015</code>)</li>
      <li><code>res:4k</code> — Cerca per risoluzione (es. <code>res:1080</code>)</li>
      <li><code>hdr:sì</code> — Solo file HDR (o <code>hdr:no</code>)</li>
      <li><code>durata:&gt;60</code> — Cerca per durata in minuti</li>
    </ul>
    <div style="text-align:right; margin-top:20px;">
      <button class="fbtn" id="closeHelp" style="background:var(--accento); color:#fff; border-color:var(--accento);">Chiudi</button>
    </div>
  </div>
</div>
<div id="ctxMenu" class="ctx-menu">
  <a id="ctxCopyName"></a>
  <a id="ctxCopyPath"></a>
</div>
</div>
<script>const PERCORSO_BASE = __PERC_BASE__; const ID_REPORT = "__IDREP__"; const TEMA_BASE = "__TEMABASE__"; const DATI = __DATI__; const VISIBILI = __COLONNE__; const L = __LING__; const CARTELLE = __CARTELLE__; const GRUPPI = __GRUPPI__;</script>
<script>__JS__</script>
</body></html>"""


def formatta_dimensione(byte):
    for unita, soglia in (("TB", 1024 ** 4), ("GB", 1024 ** 3), ("MB", 1024 ** 2), ("KB", 1024)):
        if byte >= soglia:
            return f"{byte / soglia:.2f} {unita}"
    return f"{byte} B"


def _unc_di_unita(unita):
    r"""Percorso di rete di un disco di rete mappato (Y: -> \\192.168.8.191\Arma Film), oppure None. Solo Windows."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        buf = ctypes.create_unicode_buffer(1024)
        lunghezza = ctypes.c_ulong(len(buf))
        if ctypes.windll.mpr.WNetGetConnectionW(unita, buf, ctypes.byref(lunghezza)) == 0 and buf.value:
            return buf.value
    except (OSError, AttributeError, ValueError):
        pass
    return None


def _etichetta_volume(unita):
    """Etichetta del volume di un disco (D: -> Dati), oppure None. Solo Windows."""
    if os.name != "nt":
        return None
    try:
        import ctypes
        etichetta = ctypes.create_unicode_buffer(261)
        if ctypes.windll.kernel32.GetVolumeInformationW(unita + "\\", etichetta, 261, None, None, None, None, 0):
            return etichetta.value or None
    except (OSError, AttributeError, ValueError):
        pass
    return None


def info_cartella(cartella):
    r"""(nome, percorso, percorso di rete) della cartella scansionata, per il report e per il nome del file.

    Il nome è l'ultima cartella del percorso. Una radice non ha un nome di cartella, quindi si usa quello che
    mostra Esplora risorse: la condivisione per \\server\condivisione e per un disco di rete mappato (Y:\ ->
    Arma Film), l'etichetta del volume per un disco locale, altrimenti la lettera dell'unità.
    Il percorso di rete è quello vero di un disco mappato (Y:\Serie -> \\192.168.8.191\Arma Film\Serie); vuoto se non c'è."""
    percorso = os.path.normpath(cartella)
    unita, resto = os.path.splitdrive(percorso)
    unc = _unc_di_unita(unita) if unita and not unita.startswith("\\\\") else None
    rete = os.path.normpath(unc.rstrip("\\") + resto).rstrip("\\") if unc else ""  # senza barra finale (\\server\condivisione)
    nome = os.path.basename(percorso)
    if not nome:  # radice
        if unita.startswith("\\\\"):
            nome = unita.rstrip("\\").split("\\")[-1]
        elif unc:
            nome = unc.rstrip("\\").split("\\")[-1]
        elif unita:
            nome = _etichetta_volume(unita) or unita.rstrip(":")
    return nome or percorso, percorso, rete


def testo_sorgente(cartella):
    r"""Come si scrive la cartella nella casella della sorgente: il percorso e, per un disco di rete mappato, il suo
    percorso di rete tra parentesi (W:\ (\\192.168.8.191\USBDisk1\Music\Flac)). Il testo si può rileggere con
    percorso_da_casella()."""
    _nome, percorso, rete = info_cartella(cartella)
    return percorso + (f" ({rete})" if rete else "")


def percorso_da_casella(testo):
    r"""Il percorso vero contenuto nel testo della casella: toglie l'eventuale « (\\server\condivisione)» finale."""
    return re.sub(r"\s*\(\\\\.*\)\s*$", "", testo.strip())


def nome_file_proposto(cartella):
    """Nome che la finestra di salvataggio propone per il report: quello della cartella scansionata
    (per una radice, come Y:\\, il nome che le dà Esplora risorse; se non c'è nulla di usabile, media_report)."""
    nome, percorso, _rete = info_cartella(cartella)
    if nome == percorso:  # radice senza nome (es. "/"): il percorso non è un nome di file
        nome = ""
    nome = re.sub(r'[<>:"/\\|?*\x00-\x1f]', "_", nome).strip(" .")  # caratteri vietati nei nomi di file
    return (nome or "media_report") + ".html"


_SEGNAPOSTO = re.compile(r"__[A-Z0-9_]+__")


STIMA_MINIMA_MOSTRATA = 10  # secondi: sotto questa soglia la stima non si mostra (a fine scansione sarebbe solo rumore)


class StimaTempo:
    """Quanto manca alla fine dell'analisi, calcolato dal ritmo degli ultimi secondi e non dalla media dall'inizio:
    i file già in cache passano in un istante e falserebbero la media, mentre il ritmo recente segue quello vero
    (se all'inizio ci sono molti file in cache e poi tutti nuovi, la stima si corregge da sola in pochi secondi)."""
    FINESTRA = 10.0  # secondi di storia usati per misurare il ritmo
    MINIMO = 3.0     # secondi dall'inizio prima di cominciare a stimare
    SPAN = 2.0       # secondi di storia necessari per una misura attendibile

    def __init__(self, inizio):
        self.inizio = inizio
        self.campioni = deque()  # (istante, file passati in rassegna)

    def aggiorna(self, n, totale, adesso=None):
        """Registra l'avanzamento e restituisce i secondi stimati, oppure None se non si può ancora dire."""
        adesso = time.perf_counter() if adesso is None else adesso
        self.campioni.append((adesso, n))
        while len(self.campioni) > 2 and adesso - self.campioni[1][0] >= self.FINESTRA:
            self.campioni.popleft()  # si tiene un campione appena più vecchio della finestra
        t0, n0 = self.campioni[0]
        if n >= totale or adesso - self.inizio < self.MINIMO or adesso - t0 < self.SPAN or n <= n0:
            return None
        return (totale - n) / ((n - n0) / (adesso - t0))


def formatta_durata_breve(secondi):
    """«45 s», «3 min», «1 h 05 min». Arrotonda per eccesso: una stima non deve promettere meno del vero."""
    secondi = max(1, math.ceil(secondi))
    if secondi <= 55:
        return f"{(secondi + 4) // 5 * 5} s"  # a passi di 5 secondi
    minuti = math.ceil(secondi / 60)
    if minuti < 60:
        return f"{minuti} min"
    return f"{minuti // 60} h {minuti % 60:02d} min"


def genera_html(cartella, records, colonne, percorso_completo=True, versione_ff=None, lingua="it",
                cartelle=None, n_cartelle=None, tema="scuro", id_report=None):
    if lingua not in TESTI:
        lingua = "it"
    if tema not in TEMI:
        tema = "scuro"  # tema di partenza del report: quello scelto nella finestra del programma
    id_report = id_report or secrets.token_hex(4)  # la scelta fatta nel report si ricorda per ogni report, non per tutti
    tr = lambda chiave: traduci(lingua, chiave)
    nome_cartella, percorso_cartella, rete = info_cartella(cartella)  # nome anche per le radici (es. Y:\ -> Arma Film)
    # intestazione: «nome e percorso» (con il percorso di rete se la cartella sta su un disco mappato) oppure solo il nome
    if percorso_completo and percorso_cartella != nome_cartella:
        nome_mostrato = f"{nome_cartella} \u2014 {percorso_cartella}" + (f" ({rete})" if rete else "")
    elif percorso_completo:
        nome_mostrato = percorso_cartella + (f" ({rete})" if rete else "")
    else:
        nome_mostrato = nome_cartella
    testi = TESTI[lingua]
    per_js = {  # testi usati dal JavaScript del report
        **{k[2:]: v for k, v in testi.items() if k.startswith("j_") and not k.startswith("j_tipo_")},
        "copia_nome": "Copia nome file" if lingua == "it" else "Copy file name",
        "copia_percorso": "Copia percorso" if lingua == "it" else "Copy path",
        "tipi": {"Video": tr("j_tipo_video"), "Audio": tr("j_tipo_audio"), "Generico": tr("j_tipo_generico")},
        "th": {cid: testi.get("th_" + cid) or testi["col_" + cid] for cid in COLONNE},
        "nomi_col": {cid: testi["col_" + cid] for cid in COLONNE},  # nomi completi, per il pannello "Colonne"
    }
    valori = {
        "__LANG__": lingua, "__VER__": VERSIONE, "__CSS__": CSS, "__JS__": JS,
        "__PERC_BASE__": json.dumps(percorso_cartella).replace("</", "<\\/"),
        "__TEMA__": tema, "__TEMABASE__": "colore" if tema == "colore" else "scuro", "__IDREP__": id_report, "__LOGO__": LOGO_SVG_REPORT, "__FAVICON__": quote(LOGO_SVG_ICONA),
        "__CARTELLA__": escape(nome_mostrato),
        "__TITOLO__": escape(nome_cartella),  # sempre solo il nome (anche con "percorso completo"): il titolo resta corto
        "__DATA__": datetime.now().strftime(tr("r_formato_data")),
        "__FFPROBE__": escape(versione_ff or tr("versione_nd")),
        "__NFILE__": f"{len(records):,}".replace(",", tr("r_sep_migliaia")),
        "__NCARTELLE__": "-" if n_cartelle is None else f"{n_cartelle:,}".replace(",", tr("r_sep_migliaia")),
        "__SPAZIO__": formatta_dimensione(sum(r["d"] for r in records)),
        # "</" -> "<\/" impedisce a un nome file strano di chiudere il tag <script>
        "__DATI__": json.dumps(records, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/"),
        "__COLONNE__": json.dumps(colonne),
        "__GRUPPI__": json.dumps(GRUPPI_COLONNE),  # [[chiave titolo, [colonne]], ...] come nella finestra
        # elenco delle sottocartelle (indice = campo "k" dei record); se c'è, il report si apre raggruppato
        "__CARTELLE__": json.dumps(cartelle or [], ensure_ascii=False).replace("</", "<\\/"),
        "__LING__": json.dumps(per_js, ensure_ascii=False).replace("</", "<\\/"),
        **{f"__T_{k.upper()}__": escape(v) for k, v in testi.items() if k.startswith("r_")},
    }
    # una sola passata sul template: i valori inseriti (anche l'enorme elenco dei file) non vengono
    # riesaminati, quindi niente copie ripetute della stringa e niente sostituzioni accidentali
    return _SEGNAPOSTO.sub(lambda m: valori.get(m.group(0), m.group(0)), TEMPLATE)


# ---------------------------------------------------------------- GUI

# Temi della finestra (coerenti con quelli del report HTML). Ogni colore usato dall'interfaccia sta qui: nessuno
# è scritto altrove, tranne il bianco del testo sopra il colore d'accento. imposta_palette() copia il tema scelto
# nelle variabili globali qui sotto, che applica_stile() e le finestre di dialogo leggono quando vengono costruite.
TEMI = {
    "scuro": {"BG": "#1e1f22", "CARD": "#2b2d31", "CAMPO": "#383a40", "TESTO": "#e6e6e6", "SOTTILE": "#9aa0a6",
              "ACCENT": "#0d6efd", "ACCENT_HOVER": "#3d8bfd", "ERRORE": "#ff6b6b", "OK": "#4cd07d",
              "HOVER": "#4a4d55", "OFF_FG": "#6b6f76", "ACCENT_OFF": "#2a3f66", "ACCENT_OFF_FG": "#8fa6cc",
              "BORDO": "#555555", "LINK": "#3d8bfd", "FG_ATTIVO": "#ffffff"},
    "chiaro": {"BG": "#e9edf2", "CARD": "#ffffff", "CAMPO": "#d9dfe8", "TESTO": "#1f2937", "SOTTILE": "#566072",
               "ACCENT": "#0b5ed7", "ACCENT_HOVER": "#1f6fe5", "ERRORE": "#c92a2a", "OK": "#1d7a33",
               "HOVER": "#c5cdda", "OFF_FG": "#8b95a5", "ACCENT_OFF": "#a9c4ee", "ACCENT_OFF_FG": "#f4f7fc",
               "BORDO": "#bcc5d1", "LINK": "#0b5ed7", "FG_ATTIVO": "#111827"},
}

# Colore: blu notte con accento blu e verde (la palette dei render). Il testo bianco sul blu d'accento ha un contrasto di
# circa 3,2:1: va bene per il testo in grassetto dei pulsanti, non per testi piccoli. Al passaggio del mouse il pulsante
# diventa un blu più scuro (4,1:1 con il bianco), non più chiaro.
TEMI["colore"] = {"BG": "#181a1f", "CARD": "#21242b", "CAMPO": "#2a2e37", "TESTO": "#e6e8ec", "SOTTILE": "#9aa0ac",
                  "ACCENT": "#4c8dff", "ACCENT_HOVER": "#3b7ae8", "ERRORE": "#ff7b72", "OK": "#3fb950",
                  "HOVER": "#353b47", "OFF_FG": "#6b7280", "ACCENT_OFF": "#2a3f66", "ACCENT_OFF_FG": "#8fa6cc",
                  "BORDO": "#343a46", "LINK": "#6ba0ff", "FG_ATTIVO": "#ffffff"}
TEMI["sistema"] = TEMI["scuro"]  # verra' sostituito dinamicamente
TEMI["verde"] = {"BG": "#1e2321", "CARD": "#2b312e", "CAMPO": "#383f3a", "TESTO": "#e0e6e2", "SOTTILE": "#9aa89e",
                "ACCENT": "#10b981", "ACCENT_HOVER": "#34d399", "ERRORE": "#f87171", "OK": "#4ade80",
                "HOVER": "#4a5550", "OFF_FG": "#6b7a70", "ACCENT_OFF": "#2a3f36", "ACCENT_OFF_FG": "#8fa6cc",
                "BORDO": "#555f59", "LINK": "#34d399", "FG_ATTIVO": "#ffffff"}

def tema_di_sistema():
    """Restituisce "chiaro" o "scuro" in base alle impostazioni di Windows."""
    if os.name == "nt":
        try:
            import winreg
            chiave = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\\Microsoft\\Windows\\CurrentVersion\\Themes\\Personalize")
            valore, _ = winreg.QueryValueEx(chiave, "AppsUseLightTheme")
            winreg.CloseKey(chiave)
            return "chiaro" if valore == 1 else "scuro"
        except Exception:
            pass
    return "scuro"

def imposta_palette(nome):
    """Rende attivo il tema `nome` (uno sconosciuto ripiega sullo scuro)."""
    global BG, CARD, CAMPO, TESTO, SOTTILE, ACCENT, ACCENT_HOVER, ERRORE, OK
    global HOVER, OFF_FG, ACCENT_OFF, ACCENT_OFF_FG, BORDO, LINK, FG_ATTIVO
    p = TEMI.get(nome, TEMI["scuro"])
    BG, CARD, CAMPO, TESTO, SOTTILE = p["BG"], p["CARD"], p["CAMPO"], p["TESTO"], p["SOTTILE"]
    ACCENT, ACCENT_HOVER, ERRORE, OK = p["ACCENT"], p["ACCENT_HOVER"], p["ERRORE"], p["OK"]
    HOVER, OFF_FG, ACCENT_OFF, ACCENT_OFF_FG = p["HOVER"], p["OFF_FG"], p["ACCENT_OFF"], p["ACCENT_OFF_FG"]
    BORDO, LINK, FG_ATTIVO = p["BORDO"], p["LINK"], p["FG_ATTIVO"]


imposta_palette("scuro")
FONT = ("Segoe UI", 11)


def applica_stile(root):
    st = ttk.Style(root)
    st.theme_use("clam")  # il tema ttk più personalizzabile nei colori
    root.configure(bg=BG)

    # elenco a discesa del menu delle cartelle recenti (è un widget tk classico)
    root.option_add("*TCombobox*Listbox.background", CAMPO)
    root.option_add("*TCombobox*Listbox.foreground", TESTO)
    root.option_add("*TCombobox*Listbox.selectBackground", ACCENT)
    root.option_add("*TCombobox*Listbox.selectForeground", "#ffffff")
    root.option_add("*TCombobox*Listbox.font", FONT)

    st.configure(".", background=BG, foreground=TESTO, font=FONT)
    st.configure("Card.TFrame", background=CARD)
    st.configure("Sezione.TLabel", background=CARD, font=("Segoe UI", 11, "bold"))
    st.configure("Nota.TLabel", background=CARD, foreground=SOTTILE, font=("Segoe UI", 9))
    st.configure("Gruppo.TLabel", background=CARD, foreground=SOTTILE, font=("Segoe UI", 9, "bold"))
    st.configure("TitoloScheda.TLabel", background=CARD, foreground=SOTTILE, font=("Segoe UI", 9))  # CARTELLA MULTIMEDIALE, PROFILO...
    st.configure("TSeparator", background=SOTTILE)  # linea sotto l'intestazione
    st.configure("Titolo.TLabel", font=("Segoe UI", 18, "bold"))
    st.configure("Sotto.TLabel", foreground=SOTTILE)
    st.configure("Stato.TLabel", foreground=SOTTILE)
    st.configure("Ok.TLabel", foreground=OK, font=("Segoe UI", 10, "bold"))
    st.configure("Errore.TLabel", foreground=ERRORE, font=("Segoe UI", 10, "bold"))
    st.configure("Link.TLabel", foreground=LINK, font=("Segoe UI", 10, "underline"))

    def pulsante(nome, bg, hover, fg, bg_off, fg_off, padding):
        st.configure(nome, background=bg, foreground=fg, bordercolor=bg, lightcolor=bg, darkcolor=bg,
                     focuscolor=bg, padding=padding, relief="flat")
        st.map(nome,
               background=[("disabled", bg_off), ("active", hover)],
               bordercolor=[("disabled", bg_off), ("active", hover)],
               lightcolor=[("disabled", bg_off), ("active", hover)],
               darkcolor=[("disabled", bg_off), ("active", hover)],
               foreground=[("disabled", fg_off)])

    pulsante("TButton", CAMPO, HOVER, TESTO, CARD, OFF_FG, (14, 6))
    st.configure("TMenubutton", background=CAMPO, foreground=TESTO, bordercolor=CAMPO, arrowcolor=TESTO,
                 padding=(14, 6), relief="flat")
    st.map("TMenubutton", background=[("active", HOVER)])
    pulsante("Accent.TButton", ACCENT, ACCENT_HOVER, "#ffffff", ACCENT_OFF, ACCENT_OFF_FG, (22, 10))
    st.configure("Accent.TButton", font=("Segoe UI", 11, "bold"))

    def _fg_su(colore):  # testo bianco o scuro, a seconda della luminosità dello sfondo
        r, g, b = (int(colore[i:i + 2], 16) for i in (1, 3, 5))
        return "#10151c" if (0.299 * r + 0.587 * g + 0.114 * b) > 140 else "#ffffff"

    pulsante("FfOk.TButton", OK, OK, _fg_su(OK), OK, _fg_su(OK), (14, 6))        # ffprobe trovato
    pulsante("FfErr.TButton", ERRORE, ERRORE, _fg_su(ERRORE), ERRORE, _fg_su(ERRORE), (14, 6))  # ffprobe mancante

    st.configure("Card.TCheckbutton", background=CARD, foreground=TESTO, focuscolor=CARD, padding=4,
                 indicatorbackground=CAMPO, indicatorforeground="#ffffff")
    st.map("Card.TCheckbutton",
           background=[("active", CARD)],
           foreground=[("active", FG_ATTIVO)],
           indicatorbackground=[("selected", ACCENT), ("active", HOVER)],
           indicatorforeground=[("selected", "#ffffff")])

    st.configure("Card.TLabel", background=CARD)
    st.configure("Card.TRadiobutton", background=CARD, foreground=TESTO, focuscolor=CARD, padding=4,
                 indicatorbackground=CAMPO, indicatorforeground="#ffffff")
    st.map("Card.TRadiobutton",
           background=[("active", CARD)],
           foreground=[("active", FG_ATTIVO)],
           indicatorbackground=[("selected", ACCENT), ("active", HOVER)],
           indicatorforeground=[("selected", "#ffffff")])

    st.configure("TCombobox", fieldbackground=CAMPO, background=CAMPO, foreground=TESTO,
                 arrowcolor=TESTO, bordercolor=CAMPO, lightcolor=CAMPO, darkcolor=CAMPO, padding=7,
                 selectbackground=ACCENT, selectforeground="#ffffff")
    st.map("TCombobox",
           fieldbackground=[("readonly", CAMPO)], foreground=[("readonly", TESTO)],
           selectbackground=[("readonly", CAMPO)], selectforeground=[("readonly", TESTO)],
           bordercolor=[("focus", ACCENT)], lightcolor=[("focus", ACCENT)], darkcolor=[("focus", ACCENT)], font=[("readonly", ("Segoe UI", 12))])

    st.configure("Barra.Horizontal.TProgressbar", troughcolor=CAMPO, background=ACCENT,
                 bordercolor=CAMPO, lightcolor=ACCENT, darkcolor=ACCENT, thickness=14)


class App:
    def __init__(self, root):
        self.root = root
        self.ffprobe = None  # lo cerca un thread in background: non ritarda l'apertura della finestra
        self.versione_ff = None
        self.ver_pronta = threading.Event()  # impostato quando ffprobe è stato cercato e la sua versione letta
        self.btn_ffprobe = None
        self.lbl_link = None  # link per scaricare FFmpeg, visibile solo se ffprobe manca
        self.lbl_aggiornamento = None  # avviso di nuova versione su GitHub
        self.versione_remota = None
        self.stato = None
        self._larg_testi = 0  # ultima larghezza usata per far andare a capo stato e ffprobe
        self.annulla = threading.Event()
        self.occupato = False
        self.modifiche_non_salvate = False
        config = carica_config()
        copia_di_sicurezza_config(config)  # prima di ogni migrazione, alla prima apertura di una versione nuova
        segna_fase("impostazioni lette")
        self.lingua = config.get("lingua") if config.get("lingua") in LINGUE else "it"
        self.layout = config.get("layout") if config.get("layout") in LAYOUT else "verticale"
        self.tema = config.get("tema") if config.get("tema") in TEMI else "scuro"
        self.tema_effettivo = tema_di_sistema() if self.tema == "sistema" else self.tema
        # scheda delle colonne aperta o chiusa, per ogni layout: in verticale parte chiusa (risparmia altezza)
        self.colonne_aperte = {nome: config.get("colonne_aperte_" + nome) if isinstance(config.get("colonne_aperte_" + nome), bool)
                               else nome == "orizzontale" for nome in LAYOUT}
        self.lbl_colonne = None

        # variabili dell'interfaccia: restano le stesse quando la finestra viene ricostruita (cambio lingua)
        self.recenti = cartelle_recenti(config, controlla=False)
        self.var_cartella = tk.StringVar(value=self.recenti[0] if self.recenti else "")
        salvato = config.get("mostra_cartella")
        self.mostra = tk.StringVar(value=salvato if salvato in ("percorso", "nome") else "percorso")
        self.usa_cache = tk.BooleanVar(value=config.get("usa_cache", True) is not False)
        self.dividi = tk.BooleanVar(value=config.get("dividi_sottocartelle") is True)
        self.includi_immagini = tk.BooleanVar(value=False)  # viene impostata dal profilo attivo
        # profili: ognuno ricorda le sue esclusioni e le sue colonne (la casella delle colonne mostra quelle del profilo attivo)
        self.profili, self.profilo_attivo = carica_profili(config)
        self.var_profilo = tk.StringVar(value=self.profilo_attivo)
        attive = self.profili[self.profilo_attivo]["colonne"]
        self.colonne = {cid: tk.BooleanVar(value=cid in attive) for cid in COLONNE}
        self._applica_opzioni_profilo()  # cartella sorgente e opzioni del profilo attivo

        root.title(f"Media Directory Lister v{VERSIONE} by {AUTORE}")
        self._icona = self._immagine_logo(LOGO_PNG_64)  # icona della finestra e della barra di Windows
        if self._icona is not None:
            try:
                root.iconphoto(True, self._icona)
            except tk.TclError:
                pass  # versioni di Tk senza supporto dell'icona: resta quella predefinita
        root.resizable(True, False)  # le dimensioni minime le imposta costruisci(), secondo il layout
        self.var_layout = tk.StringVar(value=self.layout)  # voci del menù «Aspetto»
        self.var_tema = tk.StringVar(value=self.tema)
        imposta_palette(self.tema_effettivo)
        applica_stile(root)
        self.corpo = None
        self.costruisci()
        self.root.protocol("WM_DELETE_WINDOW", self._on_closing)
        segna_fase("interfaccia costruita")
        threading.Thread(target=self._cerca_ffprobe, daemon=True).start()
        threading.Thread(target=self._controlla_aggiornamenti, daemon=True).start()

    def t(self, chiave, **valori):
        return traduci(self.lingua, chiave, **valori)

    def costruisci(self):
        """Crea (o ricrea, dopo un cambio di lingua o di layout) tutti i widget della finestra."""
        ricostruzione = self.corpo is not None
        if ricostruzione:
            self.corpo.destroy()
        t = self.t
        orizzontale = self.layout == "orizzontale"
        self._larg_testi = 0
        corpo = self.corpo = ttk.Frame(self.root, padding=(24, 20))
        corpo.pack(fill="both", expand=True)
        corpo.bind("<Configure>", self._adatta_testi)
        # in basso: avanzamento, stato e pulsanti. Si impacchettano per primi (side="bottom"): se lo schermo è basso,
        # restano sempre visibili e si taglia la parte sopra
        pie = ttk.Frame(corpo)
        pie.pack(side="bottom", fill="x")

        # --- intestazione con i selettori di layout e di lingua
        testa = ttk.Frame(corpo)
        testa.pack(fill="x", pady=(0, 10))
        self._logo = self._immagine_logo(LOGO_PNG_40[self.tema_effettivo])  # va tenuto in una variabile, altrimenti Tk lo scarta
        if self._logo is not None:
            # in alto, all'altezza della riga del titolo (la «M» di Media), e non al centro del blocco titolo + sottotitolo
            ttk.Label(testa, image=self._logo).pack(side="left", anchor="n", padx=(0, 10), pady=(3, 0))
        titoli = ttk.Frame(testa)
        titoli.pack(side="left", anchor="n")
        ttk.Label(titoli, text="Media Directory Lister", style="Titolo.TLabel").pack(anchor="w")
        ttk.Label(titoli, text=t("sottotitolo", v=VERSIONE), style="Sotto.TLabel", justify="left",
                  wraplength=0 if orizzontale else 280).pack(anchor="w")  # 280: il sottotitolo va a capo e il titolo non si avvicina ai pulsanti
        destra = ttk.Frame(testa)  # a destra, in una sola riga: Aspetto, ?, lingua e ffprobe
        destra.pack(side="right", anchor="n", padx=(32, 0))  # almeno 32 px tra il titolo e i pulsanti: se serve la finestra si allarga
        self.btn_aspetto = ttk.Menubutton(destra, text=t("aspetto_menu"))
        self.btn_aspetto["menu"] = self._menu_aspetto(self.btn_aspetto)
        self.btn_aspetto.grid(row=0, column=0, sticky="n", padx=(0, 8))
        ttk.Button(destra, text="?", width=3, command=self.apri_contatti).grid(row=0, column=1, sticky="n", padx=(0, 8))
        # (menu lingua spostato sotto Impostazioni)

        testo_ff, stile_ff = self._aspetto_ffprobe()
        self.btn_ffprobe = ttk.Button(destra, text=testo_ff, style=stile_ff, command=self.mostra_info_ffprobe)
        self.btn_ffprobe.grid(row=0, column=3, sticky="n", padx=(8, 0))
        self.btn_ffprobe.bind("<Enter>", self._tip_mostra)
        self.btn_ffprobe.bind("<Leave>", self._tip_nascondi)
        self.btn_ffprobe.bind("<Destroy>", self._tip_nascondi)

        ttk.Separator(corpo, orient="horizontal").pack(fill="x", pady=(0, 14))

        # --- parte centrale: verticale = schede una sotto l'altra; orizzontale = cartella e profilo a sinistra,
        # colonne a destra (la finestra è più larga e molto più bassa)
        if orizzontale:
            centro = ttk.Frame(corpo)
            centro.pack(fill="x")
            centro.columnconfigure(1, weight=1)
            sinistra = ttk.Frame(centro)
            sinistra.grid(row=0, column=0, sticky="nsew", padx=(0, 14))
            self._scheda_cartella(sinistra, compatto=True).pack(fill="x")
            self._scheda_profilo(sinistra, compatto=True).pack(fill="both", expand=True, pady=(14, 0))
            card2 = ttk.Frame(centro, style="Card.TFrame", padding=16)
            card2.grid(row=0, column=1, sticky="nsew")
            self._colonne_report(card2)
        else:
            self._scheda_cartella(corpo, compatto=False).pack(fill="x")
            self._scheda_profilo(corpo, compatto=False).pack(fill="x", pady=(14, 0))
            card2 = ttk.Frame(corpo, style="Card.TFrame", padding=16)
            card2.pack(fill="x", pady=14)
            self._colonne_report(card2)

        # --- avanzamento e azioni
        self.barra = ttk.Progressbar(pie, orient="horizontal", mode="determinate",
                                     style="Barra.Horizontal.TProgressbar")
        self.barra.pack(fill="x", pady=(14 if orizzontale else 0, 6))
        self.stato = ttk.Label(pie, text=t("attesa"), style="Stato.TLabel", wraplength=612, justify="left")
        self.stato.pack(anchor="w")

        azioni = ttk.Frame(pie)
        azioni.pack(fill="x", pady=(16, 0))
        self.btn_genera = ttk.Button(azioni, text=t("genera"), style="Accent.TButton", command=self.avvia)
        self.btn_genera.pack(side="right")
        self.btn_annulla = ttk.Button(azioni, text=t("annulla"), command=self.annulla.set, state=tk.DISABLED)  # si mostra solo scansionando


        self.lbl_link = ttk.Label(pie, text=t("scarica_ffmpeg", url=URL_FFMPEG), style="Link.TLabel",
                                  cursor="hand2")
        self.lbl_link.bind("<Button-1>", lambda _evento: self.apri_download_ffmpeg())
        self.aggiorna_stato_ffprobe()

        # dimensioni: in verticale larga almeno 700; in orizzontale non si stringe sotto la larghezza dei suoi widget.
        # L'altezza è quella del contenuto, ma mai più dell'area visibile dello schermo.
        self.root.update_idletasks()
        self.root.minsize(self.root.winfo_reqwidth() if orizzontale else 780, 300)
        self._adatta_altezza()

    def _adatta_altezza(self):
        """La finestra prende l'altezza del contenuto, ma non più dell'area visibile dello schermo (senza la barra delle
        applicazioni): se non ci sta, si accorcia e a sparire è la parte sopra, mai la barra con Genera in basso."""
        self.root.geometry("")  # dimensione richiesta dal contenuto (anche dopo aver aperto o chiuso le colonne)
        self.root.update_idletasks()
        area = area_di_lavoro()
        altezza = area[1] if area else self.root.winfo_screenheight() - 80  # senza Windows: si lascia un po' di margine
        massima = max(300, altezza - MARGINE_FINESTRA)
        if self.root.winfo_reqheight() > massima:
            self.root.geometry(f"{self.root.winfo_reqwidth()}x{massima}")

    @staticmethod
    def _immagine_logo(dati_base64):
        """Immagine Tk dal PNG incorporato; None se questa versione di Tk non la legge (il programma funziona uguale)."""
        try:
            return tk.PhotoImage(data=dati_base64)
        except tk.TclError:
            return None

    def _adatta_testi(self, evento):
        """Lo stato va a capo alla larghezza della finestra, anche se la si allarga."""
        if evento.widget is not self.corpo or evento.width == self._larg_testi:
            return
        self._larg_testi = evento.width
        spazio = max(300, evento.width - 48)
        try:
            if self.stato is not None:
                self.stato.config(wraplength=spazio)
        except tk.TclError:
            pass  # widget già distrutto (ricostruzione della finestra in corso)

    def _scheda_cartella(self, genitore, compatto):
        """Scheda con la cartella da scansionare e le opzioni. compatto = per la colonna stretta del layout orizzontale."""
        t = self.t
        card1 = ttk.Frame(genitore, style="Card.TFrame", padding=16)
        header_frame = ttk.Frame(card1, style="Card.TFrame")
        header_frame.pack(fill="x", pady=(0, 8))
        ttk.Label(header_frame, text=t("cartella_titolo").upper(), style="TitoloScheda.TLabel").pack(side="left")

        if self.versione_remota:
            lbl_agg = ttk.Label(header_frame, text=self.t("nuova_versione", v=self.versione_remota), style="Link.TLabel", cursor="hand2", font=("Segoe UI", 9))
            lbl_agg.pack(side="right")
            lbl_agg.bind("<Button-1>", lambda _evento: webbrowser.open("https://github.com/Roby77ita/Media-Directory-Lister/releases/latest"))
        riga = ttk.Frame(card1, style="Card.TFrame")
        riga.pack(fill="x")
        self.entry = ttk.Combobox(riga, values=self._valori_recenti(), textvariable=self.var_cartella, font=("Segoe UI", 12))
        self.entry.bind("<<ComboboxSelected>>", self._sorgente_scelta)
        self.entry.bind("<Return>", self._sorgente_cambiata)    # cartella scritta a mano: si valuta quando si conferma o si esce dalla casella
        self.entry.bind("<FocusOut>", self._sorgente_cambiata)
        self.entry.pack(side="left", fill="x", expand=True)
        ttk.Button(riga, text=t("sfoglia"), command=self.scegli_cartella).pack(side="left", padx=(10, 0))
        ttk.Label(card1, text=t("nota_recenti"), style="Nota.TLabel").pack(anchor="w", pady=(8, 0))

        opzione = ttk.Frame(card1, style="Card.TFrame")
        opzione.pack(fill="x", pady=(10, 0))
        etichetta = ttk.Label(opzione, text=t("mostra_come"), style="Card.TLabel")
        scelte = opzione
        if compatto:  # etichetta sopra, i due pulsanti sotto
            etichetta.pack(anchor="w")
            scelte = ttk.Frame(opzione, style="Card.TFrame")
            scelte.pack(anchor="w", pady=(4, 0))
        else:
            etichetta.pack(side="left")
        ttk.Radiobutton(scelte, text=t("percorso_completo"), variable=self.mostra, value="percorso",
                        style="Card.TRadiobutton").pack(side="left", padx=(0 if compatto else 12, 0))
        ttk.Radiobutton(scelte, text=t("solo_nome"), variable=self.mostra, value="nome",
                        style="Card.TRadiobutton").pack(side="left", padx=(8, 0))

        # layout verticale: «dividi» e «usa la cache» sulla stessa riga (risparmia altezza); compatto: righe separate
        if compatto:
            ttk.Checkbutton(card1, text=t("dividi_sottocartelle"), variable=self.dividi,
                            style="Card.TCheckbutton").pack(anchor="w", pady=(6, 0))
        riga_cache = ttk.Frame(card1, style="Card.TFrame")
        riga_cache.pack(fill="x", pady=(6, 0))
        if not compatto:
            ttk.Checkbutton(riga_cache, text=t("dividi_sottocartelle"), variable=self.dividi,
                            style="Card.TCheckbutton").pack(side="left", padx=(0, 16))
        ttk.Checkbutton(riga_cache, text=t("usa_cache" if compatto else "usa_cache_breve"), variable=self.usa_cache,
                        style="Card.TCheckbutton").pack(side="left")
        

        return card1

    def _scheda_profilo(self, genitore, compatto):
        """Scheda «PROFILO»: menù del profilo, tipo, esclusioni e Salva."""
        card = ttk.Frame(genitore, style="Card.TFrame", padding=16)
        ttk.Label(card, text=self.t("profilo_titolo").upper(), style="TitoloScheda.TLabel").pack(anchor="w", pady=(0, 8))
        self._riga_profilo(card, compatto).pack(fill="x")
        return card

    def _riga_profilo(self, genitore, compatto):
        """Sezione profilo: nome e tipo, esclusioni, gestione."""
        t = self.t
        riga_p = ttk.Frame(genitore, style="Card.TFrame")
        prima = ttk.Frame(riga_p, style="Card.TFrame")
        prima.pack(fill="x")
        
        seconda = ttk.Frame(riga_p, style="Card.TFrame") if compatto else prima
        if compatto:
            seconda.pack(fill="x", pady=(8, 0))
            
        # Menu Profilo (font normale)
        ttk.Style().configure("Profilo.TMenubutton", font=("Segoe UI", 10, "bold"))
        self.btn_profilo = ttk.Menubutton(prima, text=self._testo_profilo(), width=24, style="Profilo.TMenubutton")
        menu = tk.Menu(self.btn_profilo, tearoff=0, bg=CAMPO, fg=TESTO, activebackground=ACCENT,
                       activeforeground="#ffffff", selectcolor=TESTO, bd=0,
                       postcommand=lambda: self._riempi_menu_profilo(menu))
        self.btn_profilo["menu"] = menu
        self.btn_profilo.pack(side="left")
        
        # Label "Tipo:" (font normale)
        ttk.Label(prima, text=t("tipo_etichetta"), style="Card.TLabel").pack(side="left", padx=(14, 0))
        
        # Menu Tipo (font grande 14)
        
        self.combo_tipo = ttk.Combobox(prima, values=[t("tipo_" + tp) for tp in TIPI_PROFILO], state="readonly", width=10, font=("Segoe UI", 12, "bold"))
        self.combo_tipo.set(t("tipo_" + self.profili[self.profilo_attivo]["tipo"]))
        self.combo_tipo.pack(side="left", padx=(8, 0))
        self.combo_tipo.bind("<<ComboboxSelected>>", self.cambia_tipo)
        
        # Pulsante Esclusioni
        self.btn_escl = ttk.Button(seconda, text=self.testo_esclusioni(), command=self.modifica_esclusioni)
        self.btn_escl.pack(side="left", padx=(0 if compatto else 14, 0))
        
        ttk.Label(riga_p, text=t("profilo_nota"), style="Nota.TLabel", justify="left",
                  wraplength=420 if compatto else 560).pack(anchor="w", pady=(8, 0))
        return riga_p
    def _nome_visibile_profilo(self, nome):
        if nome == "Generale":
            return self.t("profilo_generale_nome")
        return nome

    def _testo_profilo(self):
        return self._nome_visibile_profilo(self.profilo_attivo)

    def _riempi_menu_profilo(self, menu):
        """Ricostruisce il menù ogni volta che si apre: profili esistenti, poi le azioni di gestione."""
        menu.delete(0, "end")
        for nome in self.profili:
            menu.add_radiobutton(label=self._nome_visibile_profilo(nome), variable=self.var_profilo, value=nome, command=self.cambia_profilo)
        menu.add_separator()
        menu.add_command(label=self.t("profilo_nuovo"), command=self.nuovo_profilo)
        menu.add_command(label=self.t("profilo_modifica"), command=self.modifica_profilo)
        menu.add_command(label=self.t("profilo_elimina"), command=self.elimina_profilo)

    def _colonne_report(self, card2):
        """Scheda delle colonne. La riga di intestazione («▸ COLONNE DEL REPORT · 12 selezionate») resta sempre visibile e
        si apre e si chiude con un clic; aperta mostra Tutte/Nessuna e i quattro gruppi di caselle, uno per colonna."""
        t = self.t
        intest = ttk.Frame(card2, style="Card.TFrame")
        intest.pack(fill="x")
        self.lbl_colonne = ttk.Label(intest, text="", style="TitoloScheda.TLabel", cursor="hand2")
        self.lbl_colonne.pack(side="left")
        self.lbl_colonne.bind("<Button-1>", lambda _evento: self._toggle_colonne())
        self.riga_tn = ttk.Frame(intest, style="Card.TFrame")  # Tutte / Nessuna: solo a scheda aperta
        ttk.Button(self.riga_tn, text=t("nessuna"), command=lambda: self.imposta_colonne(False)).pack(side="right")
        ttk.Button(self.riga_tn, text=t("tutte"), command=lambda: self.imposta_colonne(True)).pack(side="right", padx=(0, 6))
        ttk.Button(self.riga_tn, text=t("colonne_predefinite"), command=self.ripristina_colonne_predefinite).pack(side="right", padx=(0, 6))
        griglia = self.griglia_colonne = ttk.Frame(card2, style="Card.TFrame")
        raggruppate = {cid for _, cols in GRUPPI_COLONNE for cid in cols}
        gruppi = [(titolo, list(cols)) for titolo, cols in GRUPPI_COLONNE]
        gruppi[0][1].extend(cid for cid in COLONNE if cid not in raggruppate)  # colonne non previste: nel primo gruppo
        for g, (titolo, cols) in enumerate(gruppi):
            griglia.columnconfigure(g, weight=1, uniform="gruppo")
            ttk.Label(griglia, text=t(titolo).upper(), style="Gruppo.TLabel").grid(row=0, column=g, sticky="w", pady=(10, 6))
            for n, cid in enumerate(cols):
                def cambia_colonna(var=self.colonne.setdefault(cid, tk.BooleanVar(value=False))):
                    self.modifiche_non_salvate = True
                    self._aggiorna_conteggio_colonne()
                ttk.Checkbutton(griglia, text=t("col_" + cid) if "col_" + cid in TESTI[self.lingua] else cid, variable=self.colonne.setdefault(cid, tk.BooleanVar(value=False)), style="Card.TCheckbutton",
                                command=cambia_colonna).grid(row=1 + n, column=g, sticky="w", pady=2)
            
            # Se siamo nel gruppo FILE, aggiungiamo il checkbox "Includi immagini" subito dopo l'ultima casella
            if titolo == "gr_file":
                chk_imm = ttk.Checkbutton(griglia, text=t("includi_immagini"), variable=self.includi_immagini, style="Card.TCheckbutton", command=self._aggiorna_esclusioni_immagini)
                chk_imm.grid(row=1 + len(cols), column=g, sticky="w", pady=(10, 2))  # una riga in fondo al gruppo
                self._aggiungi_tip(chk_imm, t("includi_immagini_nota"))
        self._mostra_colonne()
    def _mostra_colonne(self):
        """Mostra o nasconde le caselle secondo lo stato del layout in uso e aggiorna l'intestazione."""
        if self.colonne_aperte[self.layout]:
            self.riga_tn.pack(side="right")
            self.griglia_colonne.pack(fill="x", pady=(6, 0))
        else:
            self.riga_tn.pack_forget()
            self.griglia_colonne.pack_forget()
        self._aggiorna_conteggio_colonne()

    def _aggiorna_conteggio_colonne(self, *_):
        """«▸ COLONNE DEL REPORT · 12 selezionate»: la freccia dice se la scheda è aperta, il numero quante colonne."""
        if self.lbl_colonne is None:
            return
        n = sum(1 for var in self.colonne.values() if var.get())
        freccia = "\u25be" if self.colonne_aperte[self.layout] else "\u25b8"
        try:
            self.lbl_colonne.config(text=f"{freccia} {self.t('colonne_titolo').upper()}  \u00b7  {self.t('colonne_conteggio', n=n)}")
        except tk.TclError:
            pass  # finestra ricostruita nel frattempo

    def _toggle_colonne(self):
        self.colonne_aperte[self.layout] = not self.colonne_aperte[self.layout]
        config = carica_config()
        config["colonne_aperte_" + self.layout] = self.colonne_aperte[self.layout]
        salva_config(config)
        self._mostra_colonne()
        self._adatta_altezza()  # la finestra si accorcia o si allunga con la scheda

    def apri_download_ffmpeg(self):
        try:
            webbrowser.open(URL_FFMPEG)
        except webbrowser.Error:
            pass

    def testo_ffprobe(self):
        """Testo completo su ffprobe (versione e percorso): per il suggerimento al passaggio del mouse e per il clic."""
        if not self.ver_pronta.is_set():
            return "ffprobe: ..."  # ancora in ricerca
        if not self.ffprobe:
            return self.t("ffprobe_mancante")
        ver = self.t("versione_ff", v=self.versione_ff) if self.versione_ff else self.t("versione_nd")
        return f"ffprobe: {ver}\n" + a_capo(self.t("percorso_ff", p=self.ffprobe))

    def _aspetto_ffprobe(self):
        """Scritta breve e stile del pulsante: ✓ verde se ffprobe c'è, ✗ rosso se manca, neutro durante la ricerca."""
        if not self.ver_pronta.is_set():
            return "ffprobe …", "TButton"
        if not self.ffprobe:
            return "ffprobe ✗", "FfErr.TButton"
        return "ffprobe ✓", "FfOk.TButton"

    def mostra_info_ffprobe(self):
        self._tip_nascondi()
        if self.ver_pronta.is_set() and not self.ffprobe:
            messagebox.showwarning("ffprobe", self.testo_ffprobe(), parent=self.root)
        else:
            messagebox.showinfo("ffprobe", self.testo_ffprobe(), parent=self.root)

    def _tip_mostra(self, _evento=None):
        self._tip_nascondi()
        try:
            tip = self._tip = tk.Toplevel(self.root)
            tip.wm_overrideredirect(True)
            x = self.btn_ffprobe.winfo_rootx()
            y = self.btn_ffprobe.winfo_rooty() + self.btn_ffprobe.winfo_height() + 4
            tip.wm_geometry(f"+{x}+{y}")
            tk.Label(tip, text=self.testo_ffprobe(), justify="left", bg=CAMPO, fg=TESTO, font=FONT,
                     bd=1, relief="solid", padx=8, pady=5).pack()
        except tk.TclError:
            self._tip = None

    def _tip_nascondi(self, _evento=None):
        tip = getattr(self, "_tip", None)
        self._tip = None
        if tip is not None:
            try:
                if isinstance(tip, tk.Misc): tip.destroy()
            except tk.TclError:
                pass

    def _cerca_ffprobe(self):
        """Thread in background: cerca ffprobe e ne legge la versione (operazioni che possono essere lente)."""
        self.ffprobe = trova_ffprobe()
        segna_fase("ffprobe cercato: " + (self.ffprobe or "non trovato"))
        self.versione_ff = versione_ffprobe(self.ffprobe)
        segna_fase("versione di ffprobe letta: " + str(self.versione_ff))
        self.ver_pronta.set()
        salva_log_avvio()
        try:
            self.root.after(0, self.aggiorna_stato_ffprobe)
        except Exception:
            pass  # finestra già chiusa

    def _controlla_aggiornamenti(self):
        """Interroga l'API di GitHub per vedere se c'è una versione più recente."""
        import json
        print("[aggiornamenti] Controllo in corso...", file=sys.stderr)
        try:
            url = "https://api.github.com/repos/Roby77ita/Media-Directory-Lister/releases/latest"
            req = urllib.request.Request(url, headers={"User-Agent": "MediaDirectoryLister"})
            with urllib.request.urlopen(req, timeout=10) as response:
                dati = json.loads(response.read().decode("utf-8"))
                tag = dati.get("tag_name", "").lstrip("vV")
                print(f"[aggiornamenti] Trovata versione remota: {tag}", file=sys.stderr)
                if tag:
                    # Confronto robusto: divide per "." e confronta i numeri
                    def versione_a_tuple(v):
                        try:
                            return tuple(int(x) for x in v.split(".") if x.isdigit())
                        except Exception:
                            return (0,)
                    tupla_remota = versione_a_tuple(tag)
                    tupla_locale = versione_a_tuple(VERSIONE)
                    print(f"[aggiornamenti] Confronto: {tupla_remota} vs {tupla_locale}", file=sys.stderr)
                    if tupla_remota > tupla_locale:
                        print(f"[aggiornamenti] Aggiornamento disponibile!", file=sys.stderr)
                        self.root.after(0, self._mostra_avviso_aggiornamento, tag)
        except Exception as e:
            print(f"[aggiornamenti] Errore: {e}", file=sys.stderr)

    def _mostra_avviso_aggiornamento(self, nuova_versione):
        self.versione_remota = nuova_versione
        try:
            # Chiama il ridisegno per far apparire la scritta in fondo
            self.root.after(0, self.costruisci)
        except Exception as e:
            print(f"[aggiornamenti] Errore nel mostrare l'avviso: {e}", file=sys.stderr)

    def aggiorna_stato_ffprobe(self):
        """Adegua etichetta, pulsante e messaggio a quanto si sa di ffprobe: in ricerca, trovato o mancante."""
        if self.btn_ffprobe is not None:
            testo_ff, stile_ff = self._aspetto_ffprobe()
            self.btn_ffprobe.config(text=testo_ff, style=stile_ff)
        if self.lbl_link is not None:  # il link compare solo quando la ricerca è finita e ffprobe non c'è
            if self.ver_pronta.is_set() and not self.ffprobe:
                self.lbl_link.pack(anchor="w", pady=(4, 0), after=self.stato)
            else:
                self.lbl_link.pack_forget()
        if self.occupato:
            return
        if not self.ver_pronta.is_set():
            self.btn_genera.config(state=tk.DISABLED)  # si può generare solo quando ffprobe è noto
        elif self.ffprobe:
            self.btn_genera.config(state=tk.NORMAL)
        else:
            self.btn_genera.config(state=tk.DISABLED)
            self.stato.config(text=self.t("ffprobe_mancante"), style="Errore.TLabel")

    def _cambia_lingua_menu(self, codice):
        if codice == self.lingua or self.occupato:
            return
        self.lingua = codice
        config = carica_config()
        config["lingua"] = codice
        salva_config(config)
        self.root.after(0, self.costruisci)

    def _menu_aspetto(self, genitore):
        """Menù «Impostazioni»: layout, tema, cronologia e cache."""
        menu = tk.Menu(genitore, tearoff=0, bg=CAMPO, fg=TESTO, activebackground=ACCENT,
                       activeforeground="#ffffff", bd=0)
        for nome in LAYOUT:
            menu.add_radiobutton(label=self.t("layout_" + nome), variable=self.var_layout, value=nome,
                                 command=lambda n=nome: self.cambia_layout(n))
        menu.add_separator()
        for nome in TEMI:
            menu.add_radiobutton(label=self.t("tema_" + nome), variable=self.var_tema, value=nome,
                                 command=lambda n=nome: self.cambia_tema(n))
        menu.add_separator()
        # Sottomenu per la lingua
        lang_menu = tk.Menu(menu, tearoff=0, bg=CAMPO, fg=TESTO, activebackground=ACCENT,
                            activeforeground="#ffffff", bd=0)
        var_lingua = tk.StringVar(value=self.lingua)
        for codice, nome in LINGUE.items():
            lang_menu.add_radiobutton(label=nome, variable=var_lingua, value=codice,
                                      command=lambda c=codice: self._cambia_lingua_menu(c))
        menu.add_cascade(label=self.t("lingua_menu"), menu=lang_menu)
        menu.add_separator()
        menu.add_command(label=self.t("svuota_cronologia"), command=self.svuota_cronologia)
        menu.add_command(label=self.t("svuota_cache"), command=self.svuota_cache)
        menu.add_separator()
        menu.add_command(label=self.t("apri_config"), command=self.apri_cartella_config)
        return menu

    def cambia_layout(self, scelta):
        if scelta == self.layout or self.occupato:
            self.var_layout.set(self.layout)  # durante la scansione resta quello attuale
            return
        self.layout = scelta
        self.var_layout.set(scelta)  # il segno di spunta nel menù segue sempre la scelta effettiva
        config = carica_config()
        config["layout"] = scelta
        salva_config(config)
        self.root.after(0, self.costruisci)  # dopo l'evento: un widget non va distrutto dentro il proprio callback

    def cambia_tema(self, scelta):
        if scelta == self.tema or self.occupato:
            self.var_tema.set(self.tema)
            return
        self.tema = scelta
        self.var_tema.set(scelta)
        self.tema_effettivo = tema_di_sistema() if scelta == "sistema" else scelta
        config = carica_config()
        config["tema"] = scelta
        salva_config(config)
        imposta_palette(self.tema_effettivo)
        applica_stile(self.root)  # ricolora gli stili ttk; i widget si ricreano con i colori nuovi
        self.root.after(0, self.costruisci)

    # --- profili
    def _sorgente(self):
        """La cartella sorgente scritta nella casella, senza l'eventuale percorso di rete tra parentesi."""
        return percorso_da_casella(self.var_cartella.get())

    def _valori_recenti(self):
        return [testo_sorgente(c) for c in self.recenti]

    def _sorgente_scelta(self, _evento=None):
        """Scelta una cartella recente: si scrive con il suo percorso completo."""
        self.var_cartella.set(testo_sorgente(self._sorgente()))
        self._sorgente_cambiata()

    def _colonne_scelte(self):
        return [cid for cid in COLONNE if self.colonne[cid].get()]

    @staticmethod
    def _stesso_percorso(a, b):
        return os.path.normcase(os.path.normpath(a)) == os.path.normcase(os.path.normpath(b))

    def _profilo_per_sorgente(self, percorso):
        """Il profilo che ha già questa cartella come sorgente (quello attivo escluso), oppure None."""
        return next((nome for nome, p in self.profili.items()
                     if nome != self.profilo_attivo and p["sorgente"] and self._stesso_percorso(p["sorgente"], percorso)), None)

    def _profilo_generale(self):
        """Un profilo di tipo Generale: «Generale» se c'è, altrimenti il primo che lo è; se non ce n'è nessuno se ne crea uno."""
        generali = [nome for nome, p in self.profili.items() if p["tipo"] == "generale"]
        if "Generale" in generali:
            return "Generale"
        if generali:
            return generali[0]
        nome, n = "Generale", 1
        while nome in self.profili:  # esiste un profilo con questo nome ma di un altro tipo
            n += 1
            nome = f"Generale {n}"
        self.profili[nome] = profili_predefiniti()["Generale"]
        return nome

    def _sorgente_cambiata(self, _evento=None):
        """Si è scelta (o scritta) una cartella. Se il profilo attivo ha già una sua cartella e questa è un'altra, non si sa
        cosa contenga: si passa al profilo che ha già quella cartella o, altrimenti, a un profilo Generale. Il profilo che
        si lascia non cambia (la sua cartella non si sovrascrive; per cambiarla c'è «Modifica profilo»). Un profilo senza
        cartella, per esempio appena creato, riceve quella scelta."""
        if self.occupato:
            return
        nuova = self._sorgente()
        profilo = self.profili[self.profilo_attivo]
        if not nuova or not profilo["sorgente"] or self._stesso_percorso(nuova, profilo["sorgente"]) or not os.path.isdir(nuova):
            return
        noto = self._profilo_per_sorgente(nuova)
        destinazione = noto or self._profilo_generale()
        if destinazione == self.profilo_attivo:
            return
        self._memorizza_colonne(con_sorgente=False)  # colonne e opzioni modificate restano al profilo che si lascia, la cartella no
        self.profilo_attivo = destinazione
        self._profilo_cambiato()                      # carica colonne, tipo, esclusioni e opzioni del nuovo profilo
        self.var_cartella.set(testo_sorgente(nuova))  # e la cartella scelta resta nella casella
        self.stato.config(text=self.t("profilo_auto_noto" if noto else "profilo_auto_generale", nome=destinazione), style="Stato.TLabel")

    def _memorizza_colonne(self, con_sorgente=True):
        """Tutto ciò che si imposta nella finestra appartiene al profilo attivo e si salva lì: colonne spuntate (se non
        ne resta nessuna, restano le vecchie), cartella sorgente, «mostra come», sottocartelle e cache."""
        profilo = self.profili[self.profilo_attivo]
        scelte = self._colonne_scelte()
        if scelte:
            profilo["colonne"] = scelte
        if con_sorgente:
            profilo["sorgente"] = self._sorgente()
        profilo["mostra"] = self.mostra.get()
        profilo["dividi"] = bool(self.dividi.get())
        profilo["usa_cache"] = bool(self.usa_cache.get())

    def _applica_colonne_profilo(self):
        attive = self.profili[self.profilo_attivo]["colonne"]
        for cid, var in self.colonne.items():
            var.set(cid in attive)
        self._aggiorna_conteggio_colonne()

    def _applica_opzioni_profilo(self, svuota_sorgente=False):
        """Mette nella finestra cartella sorgente e opzioni del profilo attivo. Se il profilo non ha una sorgente la
        casella resta com'è, tranne con svuota_sorgente (cambio di profilo): così non si genera il report sulla
        cartella dell'altro profilo."""
        profilo = self.profili[self.profilo_attivo]
        if profilo["sorgente"]:
            self.var_cartella.set(testo_sorgente(profilo["sorgente"]))
        elif svuota_sorgente:
            self.var_cartella.set("")
        self.mostra.set(profilo["mostra"])
        self.dividi.set(profilo["dividi"])
        self.usa_cache.set(profilo["usa_cache"])
        self.includi_immagini.set(False)  # opzione di sessione: parte sempre spenta

    def _salva_profili(self):
        self._memorizza_colonne()
        config = carica_config()
        config["profili"] = self.profili
        config["profilo_attivo"] = self.profilo_attivo
        config["migrazione_3_9g"] = True
        config["migrazione_3_9t"] = True
        config.pop("colonne", None)  # ora le colonne stanno nei profili
        salva_config(config)
        self.modifiche_non_salvate = False

    def _esclusioni_attive(self):
        profilo = self.profili[self.profilo_attivo]
        escluse = set(profilo["estensioni_escluse"])
        if self.includi_immagini.get():
            escluse -= ESTENSIONI_IMMAGINE  # solo per questa scansione: il profilo non cambia
        return escluse, set(profilo["nomi_esclusi"])

    def testo_esclusioni(self):
        profilo = self.profili[self.profilo_attivo]
        return self.t("escl_bottone", n=len(profilo["estensioni_escluse"]) + len(profilo["nomi_esclusi"]))

    def _aggiungi_tip(self, widget, testo):
        """Suggerimento al passaggio del mouse (una piccola finestra senza bordi)."""
        def mostra(_evento=None):
            self._tip_nascondi()
            try:
                tip = self._tip_finestra = tk.Toplevel(self.root)
                tip.wm_overrideredirect(True)
                x = widget.winfo_rootx() + 12
                y = widget.winfo_rooty() + widget.winfo_height() + 4
                tip.wm_geometry(f"+{x}+{y}")
                tk.Label(tip, text=testo, justify="left", bg=CAMPO, fg=TESTO, font=FONT,
                         bd=1, relief="solid", padx=8, pady=5, wraplength=420).pack()
            except tk.TclError:
                self._tip_finestra = None

        def nascondi(_evento=None):
            tip = getattr(self, "_tip_finestra", None)
            self._tip_finestra = None
            if tip is not None:
                try:
                    tip.destroy()
                except tk.TclError:
                    pass
        widget.bind("<Enter>", mostra, add="+")
        widget.bind("<Leave>", nascondi, add="+")
        widget.bind("<Destroy>", nascondi, add="+")

    def _aggiorna_esclusioni_immagini(self):
        """Opzione «Includi immagini»: vale solo per la scansione in corso e non viene ricordata nel profilo."""
        if self.occupato:
            return
        if self.includi_immagini.get():
            messagebox.showinfo("Includi immagini", "Attenzione: spuntando questa opzione, le esclusioni impostate nel profilo per i file immagine (jpg, png, gif, ecc.) verranno ignorate per questa scansione.", parent=self.root)
    def _profilo_cambiato(self, svuota_sorgente=False):
        """Allinea finestra e file di configurazione dopo un cambio, un inserimento o una cancellazione di profilo."""
        self.var_profilo.set(self.profilo_attivo)
        self.btn_profilo.config(text=self._testo_profilo())
        self._applica_colonne_profilo()
        self._applica_opzioni_profilo(svuota_sorgente)
        self.combo_tipo.set(self.t("tipo_" + self.profili[self.profilo_attivo]["tipo"]))
        self.btn_escl.config(text=self.testo_esclusioni())
        self._salva_profili()  # salva subito tutte le modifiche al profilo (incluso lo stato delle colonne)

    def cambia_profilo(self, _evento=None):
        nuovo = self.var_profilo.get()
        if self.occupato or nuovo == self.profilo_attivo or nuovo not in self.profili:
            self.var_profilo.set(self.profilo_attivo)
            return
        self._sorgente_cambiata()  # una cartella scritta a mano non deve finire nel profilo che si lascia
        self._memorizza_colonne()  # le colonne modificate restano nel profilo che si lascia
        self.profilo_attivo = nuovo
        self._profilo_cambiato(svuota_sorgente=True)  # la casella mostra la cartella del nuovo profilo

    def nuovo_profilo(self):
        """Finestra per creare un profilo (es. Animazione): nome e tipo; le colonne partono da quelle predefinite del
        tipo oppure da una copia di quelle attuali. Cartella, esclusioni e opzioni attuali si copiano."""
        if self.occupato:
            return
        t = self.t
        fin = tk.Toplevel(self.root)
        fin.title(t("nuovo_titolo"))
        fin.configure(bg=BG)
        fin.transient(self.root)
        fin.resizable(False, False)
        corpo = ttk.Frame(fin, padding=20)
        corpo.pack(fill="both", expand=True)
        var_nome = tk.StringVar(value="")
        var_tipo = tk.StringVar(value=t("tipo_" + self.profili[self.profilo_attivo]["tipo"]))
        var_modello = tk.BooleanVar(value=True)
        cartella_corrente = self._sorgente()
        var_usa_corrente = tk.BooleanVar(value=bool(cartella_corrente))
        var_cartella_nuova = tk.StringVar(value=cartella_corrente or "")

        ttk.Label(corpo, text=t("nuovo_nome"), style="Sezione.TLabel").pack(anchor="w", pady=(0, 6))
        campo = tk.Entry(corpo, textvariable=var_nome, width=44, bg=CAMPO, fg=TESTO, insertbackground=TESTO,
                         relief="flat", font=FONT, highlightthickness=1, highlightbackground=BORDO, highlightcolor=ACCENT)
        campo.pack(fill="x", pady=(0, 14), ipady=4)
        riga_tipo = ttk.Frame(corpo)
        riga_tipo.pack(fill="x", pady=(0, 8))
        ttk.Label(riga_tipo, text=t("nuovo_tipo"), style="Sezione.TLabel").pack(side="left")
        ttk.Combobox(riga_tipo, values=[t("tipo_" + tp) for tp in TIPI_PROFILO], textvariable=var_tipo,
                     state="readonly", width=12).pack(side="left", padx=(10, 0))
        ttk.Checkbutton(corpo, text=t("nuovo_modello"), variable=var_modello).pack(anchor="w", pady=(0, 8))
        # cartella del nuovo profilo: quella corrente oppure una scelta
        riga_cartella = ttk.Frame(corpo)
        riga_cartella.pack(fill="x", pady=(0, 4))
        chk_corrente = ttk.Checkbutton(riga_cartella, text=t("nuovo_usa_corrente"), variable=var_usa_corrente)
        chk_corrente.pack(anchor="w")
        riga_scelta = ttk.Frame(corpo)
        riga_scelta.pack(fill="x", pady=(0, 8))
        entry_cartella = tk.Entry(riga_scelta, textvariable=var_cartella_nuova, bg=CAMPO, fg=TESTO,
                                  insertbackground=TESTO, relief="flat", font=FONT,
                                  highlightthickness=1, highlightbackground=BORDO, highlightcolor=ACCENT)
        entry_cartella.pack(side="left", fill="x", expand=True, ipady=4)
        def sfoglia_cartella():
            attuale = percorso_da_casella(var_cartella_nuova.get())
            opzioni = {"parent": fin}
            if attuale and os.path.isdir(attuale):
                opzioni["initialdir"] = attuale
            scelta = filedialog.askdirectory(**opzioni)
            if scelta:
                var_cartella_nuova.set(testo_sorgente(scelta))
                var_usa_corrente.set(False)
        ttk.Button(riga_scelta, text=t("sfoglia"), command=sfoglia_cartella).pack(side="left", padx=(10, 0))
        def aggiorna_stato_cartella(*_):
            stato = "disabled" if var_usa_corrente.get() else "normal"
            entry_cartella.config(state=stato)
        var_usa_corrente.trace_add("write", aggiorna_stato_cartella)
        aggiorna_stato_cartella()
        ttk.Label(corpo, text=t("nuovo_nota"), style="Nota.TLabel", wraplength=420, justify="left").pack(anchor="w", pady=(0, 10))
        errore = ttk.Label(corpo, text="", style="Errore.TLabel", wraplength=420, justify="left")
        errore.pack(anchor="w", pady=(0, 8))

        def crea(_evento=None):
            nome = var_nome.get().strip()
            chiave = errore_nome_profilo(nome, self.profili)
            if chiave:
                errore.config(text=t(chiave, nome=nome))
                return
            tipo = next((tp for tp in TIPI_PROFILO if t("tipo_" + tp) == var_tipo.get()), "generale")
            self._memorizza_colonne()
            nuovo = copy.deepcopy(self.profili[self.profilo_attivo])  # esclusioni, opzioni e colonne attuali
            nuovo["tipo"] = tipo
            if var_usa_corrente.get():
                nuovo["sorgente"] = cartella_corrente or ""
            else:
                scelta_cartella = percorso_da_casella(var_cartella_nuova.get())
                nuovo["sorgente"] = os.path.abspath(scelta_cartella) if scelta_cartella and os.path.isdir(scelta_cartella) else ""
            if var_modello.get():
                modello = set(COLONNE_PER_TIPO[tipo])
                nuovo["colonne"] = [c for c in COLONNE if c in modello]
            self.profili[nome] = nuovo
            self.profilo_attivo = nome
            fin.destroy()
            self._profilo_cambiato(svuota_sorgente=False)

        azioni = ttk.Frame(corpo)
        azioni.pack(fill="x")
        ttk.Button(azioni, text=t("nuovo_crea"), style="Accent.TButton", command=crea).pack(side="right")
        ttk.Button(azioni, text=t("annulla"), command=fin.destroy).pack(side="right", padx=(0, 10))
        campo.bind("<Return>", crea)
        campo.focus_set()
        fin.grab_set()

    def modifica_profilo(self):
        """Finestra per modificare il profilo attivo: nome, cartella sorgente (il percorso) e tipo."""
        if self.occupato:
            return
        t = self.t
        vecchio = self.profilo_attivo
        profilo = self.profili[vecchio]
        fin = tk.Toplevel(self.root)
        fin.title(t("modifica_titolo"))
        fin.configure(bg=BG)
        fin.transient(self.root)
        fin.resizable(False, False)
        corpo = ttk.Frame(fin, padding=20)
        corpo.pack(fill="both", expand=True)
        var_nome = tk.StringVar(value=vecchio)
        var_cartella = tk.StringVar(value=testo_sorgente(profilo["sorgente"]) if profilo["sorgente"] else "")
        var_tipo = tk.StringVar(value=t("tipo_" + profilo["tipo"]))

        def campo_testo(genitore, variabile, **opzioni):
            return tk.Entry(genitore, textvariable=variabile, bg=CAMPO, fg=TESTO, insertbackground=TESTO,
                            relief="flat", font=FONT, highlightthickness=1, highlightbackground=BORDO,
                            highlightcolor=ACCENT, **opzioni)

        ttk.Label(corpo, text=t("modifica_nome"), style="Sezione.TLabel").pack(anchor="w", pady=(0, 6))
        campo_nome = campo_testo(corpo, var_nome, width=52)
        campo_nome.pack(fill="x", pady=(0, 14), ipady=4)
        ttk.Label(corpo, text=t("modifica_cartella"), style="Sezione.TLabel").pack(anchor="w", pady=(0, 6))
        riga_c = ttk.Frame(corpo)
        riga_c.pack(fill="x", pady=(0, 14))
        campo_testo(riga_c, var_cartella).pack(side="left", fill="x", expand=True, ipady=4)

        def sfoglia():
            opzioni = {"parent": fin}
            attuale = percorso_da_casella(var_cartella.get())
            if attuale and os.path.isdir(attuale):
                opzioni["initialdir"] = attuale
            scelta = filedialog.askdirectory(**opzioni)
            if scelta:
                var_cartella.set(testo_sorgente(scelta))

        ttk.Button(riga_c, text=t("sfoglia"), command=sfoglia).pack(side="left", padx=(10, 0))
        riga_tipo = ttk.Frame(corpo)
        riga_tipo.pack(fill="x", pady=(0, 10))
        ttk.Label(riga_tipo, text=t("nuovo_tipo"), style="Sezione.TLabel").pack(side="left")
        ttk.Combobox(riga_tipo, values=[t("tipo_" + tp) for tp in TIPI_PROFILO], textvariable=var_tipo,
                     state="readonly", width=12).pack(side="left", padx=(10, 0))
        errore = ttk.Label(corpo, text="", style="Errore.TLabel", wraplength=480, justify="left")
        errore.pack(anchor="w", pady=(0, 8))

        def applica(_evento=None):
            nome = var_nome.get().strip()
            chiave = errore_nome_profilo(nome, self.profili, ignora=vecchio)
            if chiave:
                errore.config(text=t(chiave, nome=nome))
                return
            cartella = percorso_da_casella(var_cartella.get())
            if cartella and not os.path.isdir(cartella):
                errore.config(text=t("cartella_non_valida"))
                return
            tipo = next((tp for tp in TIPI_PROFILO if t("tipo_" + tp) == var_tipo.get()), profilo["tipo"])
            tipo_cambiato = tipo != profilo["tipo"]
            self._memorizza_colonne()  # le colonne modificate nella finestra restano nel profilo
            profilo["sorgente"] = os.path.abspath(cartella) if cartella else ""
            profilo["tipo"] = tipo
            if nome != vecchio:
                self.profili = {(nome if k == vecchio else k): v for k, v in self.profili.items()}  # stessa posizione
                self.profilo_attivo = nome
            fin.destroy()
            if tipo_cambiato and messagebox.askyesno(t("tipo_titolo"), t("tipo_testo", tipo=t("tipo_" + tipo))):
                modello = set(COLONNE_PER_TIPO[tipo])
                profilo["colonne"] = [c for c in COLONNE if c in modello]
            self._profilo_cambiato(svuota_sorgente=True)  # la casella della cartella mostra quella del profilo

        azioni = ttk.Frame(corpo)
        azioni.pack(fill="x")
        ttk.Button(azioni, text=t("profilo_salva"), style="Accent.TButton", command=applica).pack(side="right")
        ttk.Button(azioni, text=t("annulla"), command=fin.destroy).pack(side="right", padx=(0, 10))
        campo_nome.bind("<Return>", applica)
        campo_nome.focus_set()
        fin.grab_set()

    def cambia_tipo(self, _evento=None):
        profilo = self.profili[self.profilo_attivo]
        scelto = next((tp for tp in TIPI_PROFILO if self.t("tipo_" + tp) == self.combo_tipo.get()), profilo["tipo"])
        if self.occupato or scelto == profilo["tipo"]:
            self.combo_tipo.set(self.t("tipo_" + profilo["tipo"]))
            return
        
        if messagebox.askyesno(self.t("tipo_titolo"), self.t("tipo_testo", tipo=self.t("tipo_" + scelto))):
            self._memorizza_colonne()
            profilo["tipo"] = scelto
            modello = set(COLONNE_PER_TIPO[scelto])
            profilo["colonne"] = [c for c in COLONNE if c in modello]
            self._applica_colonne_profilo()
            self.modifiche_non_salvate = True
        else:
            self.combo_tipo.set(self.t("tipo_" + profilo["tipo"]))
    def elimina_profilo(self):
        if self.occupato:
            return
        ultimo = len(self.profili) <= 1
        testo = "elimina_ultimo_testo" if ultimo else "elimina_testo"  # il programma ha sempre un profilo: l'ultimo si sostituisce
        if not messagebox.askyesno(self.t("elimina_titolo"), self.t(testo, nome=self.profilo_attivo)):
            return
        if ultimo:
            self.profili = {"Generale": profili_predefiniti()["Generale"]}
            self.profilo_attivo = "Generale"
        else:
            del self.profili[self.profilo_attivo]
            self.profilo_attivo = "Generale" if "Generale" in self.profili else next(iter(self.profili))
        self._profilo_cambiato(svuota_sorgente=not ultimo)

    def _applica_esclusioni(self, testo_estensioni, testo_nomi):
        """Salva nel profilo attivo le esclusioni scritte nella finestra. Restituisce le voci non valide, ignorate."""
        scartate = []
        profilo = self.profili[self.profilo_attivo]
        profilo["estensioni_escluse"] = normalizza_estensioni(testo_estensioni, scartate)
        profilo["nomi_esclusi"] = normalizza_nomi(testo_nomi, scartate)
        self._memorizza_colonne()
        self._salva_profili()  # salva subito le esclusioni
        self.btn_escl.config(text=self.testo_esclusioni())
        return scartate

    def modifica_esclusioni(self):
        """Finestra per modificare le estensioni e i nomi di file esclusi dal profilo attivo."""
        if self.occupato:
            return
        t = self.t
        profilo = self.profili[self.profilo_attivo]
        fin = tk.Toplevel(self.root)
        fin.title(t("escl_titolo", nome=self.profilo_attivo))
        fin.configure(bg=BG)
        fin.transient(self.root)
        fin.resizable(False, False)
        corpo = ttk.Frame(fin, padding=20)
        corpo.pack(fill="both", expand=True)

        def casella(titolo, nota, contenuto, righe):
            ttk.Label(corpo, text=titolo, style="Sezione.TLabel").pack(anchor="w", pady=(0, 2))
            ttk.Label(corpo, text=nota, style="Sotto.TLabel", wraplength=520, justify="left").pack(anchor="w", pady=(0, 6))
            c = tk.Text(corpo, width=64, height=righe, wrap="word", bg=CAMPO, fg=TESTO, insertbackground=TESTO,
                        relief="flat", font=FONT, highlightthickness=1, highlightbackground=BORDO,
                        highlightcolor=ACCENT, padx=8, pady=6)
            c.insert("1.0", contenuto)
            c.pack(fill="x", pady=(0, 14))
            return c

        txt_est = casella(t("escl_estensioni"), t("escl_estensioni_nota"), " ".join(profilo["estensioni_escluse"]), 5)
        txt_nomi = casella(t("escl_nomi"), t("escl_nomi_nota"), "\n".join(profilo["nomi_esclusi"]), 4)

        def ripristina():
            for campo, valore in ((txt_est, " ".join(sorted(ESTENSIONI_ESCLUSE))), (txt_nomi, "\n".join(sorted(NOMI_ESCLUSI)))):
                campo.delete("1.0", "end")
                campo.insert("1.0", valore)

        def salva():
            scartate = self._applica_esclusioni(txt_est.get("1.0", "end"), txt_nomi.get("1.0", "end"))
            fin.destroy()
            if scartate:
                messagebox.showinfo(t("info"), t("escl_ignorate", voci=", ".join(scartate)))

        azioni = ttk.Frame(corpo)
        azioni.pack(fill="x")
        ttk.Button(azioni, text=t("escl_ripristina"), command=ripristina).pack(side="left")
        ttk.Button(azioni, text=t("escl_salva"), style="Accent.TButton", command=salva).pack(side="right")
        ttk.Button(azioni, text=t("annulla"), command=fin.destroy).pack(side="right", padx=(0, 10))
        fin.grab_set()

    # --- contatti
    def scrivi_email(self):
        """Apre il programma di posta con l'indirizzo e un oggetto già pronti (con la versione, utile per le segnalazioni)."""
        oggetto = quote(f"Media Directory Lister v{VERSIONE}")
        try:
            webbrowser.open(f"mailto:{EMAIL_CONTATTI}?subject={oggetto}")
        except webbrowser.Error:
            pass

    def apri_contatti(self):
        """Finestrella del pulsante «?»: invito a scrivere (suggerimenti, richieste, segnalazioni) con l'email cliccabile."""
        t = self.t
        fin = tk.Toplevel(self.root)
        fin.title(t("contatti_titolo"))
        fin.configure(bg=BG)
        fin.transient(self.root)
        fin.resizable(False, False)
        corpo = ttk.Frame(fin, padding=24)
        corpo.pack(fill="both", expand=True)
        ttk.Label(corpo, text=t("contatti_testo"), wraplength=420, justify="left").pack(anchor="w")
        ttk.Label(corpo, text=t("contatti_email_intro"), wraplength=420, justify="left").pack(anchor="w", pady=(14, 2))
        link = ttk.Label(corpo, text=EMAIL_CONTATTI, style="Link.TLabel", cursor="hand2")
        link.pack(anchor="w")
        link.bind("<Button-1>", lambda _evento: self.scrivi_email())
        
        ttk.Label(corpo, text=t("contatti_github_intro"), wraplength=420, justify="left").pack(anchor="w", pady=(14, 2))
        link_github = ttk.Label(corpo, text=URL_GITHUB, style="Link.TLabel", cursor="hand2")
        link_github.pack(anchor="w")
        link_github.bind("<Button-1>", lambda _evento: webbrowser.open(URL_GITHUB))
        
        ttk.Button(corpo, text=t("chiudi"), command=fin.destroy).pack(anchor="e", pady=(18, 0))
        fin.grab_set()

    def ripristina_colonne_predefinite(self):
        tipo = self.profili[self.profilo_attivo]["tipo"]
        modello = set(COLONNE_PER_TIPO.get(tipo, COLONNE))
        for cid, var in self.colonne.items():
            var.set(cid in modello)
        self.modifiche_non_salvate = True
        self._aggiorna_conteggio_colonne()

    def imposta_colonne(self, valore):
        for var in self.colonne.values():
            var.set(valore)
        self.modifiche_non_salvate = True
        self._aggiorna_conteggio_colonne()

    def svuota_cronologia(self):
        """Svuota l'elenco delle cartelle recenti del menu a tendina; la cartella scritta nella casella e quelle
        salvate nei profili restano dove sono."""
        if self.occupato:
            return
        if not messagebox.askyesno(self.t("cronologia_titolo"), self.t("cronologia_conferma")):
            return
        config = carica_config()
        config["cartelle_recenti"] = []
        config.pop("cartella_scansione", None)
        salva_config(config)
        self.recenti = []
        self.entry["values"] = []
        messagebox.showinfo(self.t("cronologia_titolo"), self.t("cronologia_svuotata"))

    def svuota_cache(self):
        try:
            if svuota_cache_su_disco():
                messagebox.showinfo(self.t("cache_titolo"), self.t("cache_svuotata"))
            else:
                messagebox.showinfo(self.t("cache_titolo"), self.t("cache_gia_vuota"))
        except OSError as e:
            messagebox.showerror(self.t("errore"), self.t("cache_errore", errore=e))

    def apri_cartella_config(self):
        """Apre la cartella dove il programma salva config.json, cache e log."""
        cartella = os.path.dirname(percorso_config())
        try:
            os.makedirs(cartella, exist_ok=True)
            if IS_WIN:
                os.startfile(cartella)
            else:
                webbrowser.open(Path(cartella).resolve().as_uri())
        except OSError as e:
            messagebox.showerror(self.t("errore"), str(e), parent=self.root)

    def scegli_cartella(self):
        opzioni = {}
        attuale = self._sorgente()
        if os.path.isdir(attuale):
            opzioni["initialdir"] = attuale
        c = filedialog.askdirectory(**opzioni)
        if c:
            self.var_cartella.set(testo_sorgente(c))
            self._sorgente_cambiata()

    def avvia(self):
        self._sorgente_cambiata()  # una cartella scritta a mano e non ancora valutata: prima si sceglie il profilo
        if not self._sorgente():  # casella vuota: abspath("") sarebbe la cartella di lavoro corrente
            messagebox.showerror(self.t("errore"), self.t("cartella_non_valida"))
            return
        cartella = os.path.abspath(self._sorgente())
        if not os.path.isdir(cartella):
            messagebox.showerror(self.t("errore"), self.t("cartella_non_valida"))
            return
        scelte = [cid for cid in COLONNE if self.colonne[cid].get()]
        if not scelte:
            messagebox.showerror(self.t("errore"), self.t("nessuna_colonna"))
            return
        config = carica_config()
        recenti = [cartella] + [c for c in cartelle_recenti(config, controlla=False)
                                if os.path.normcase(c) != os.path.normcase(cartella)]
        recenti = recenti[:MAX_RECENTI]
        config.pop("cartella_scansione", None)
        self.var_cartella.set(testo_sorgente(cartella))  # percorso normalizzato e completo (con il percorso di rete, se c'è)
        self._memorizza_colonne()  # colonne, cartella sorgente e opzioni si salvano nel profilo attivo
        config.update(cartelle_recenti=recenti, mostra_cartella=self.mostra.get(), usa_cache=self.usa_cache.get(),
                      dividi_sottocartelle=self.dividi.get(),
                      profili=self.profili, profilo_attivo=self.profilo_attivo,
                      migrazione_3_9g=True, migrazione_3_9t=True)
        config.pop("colonne", None)
        self.recenti = recenti
        self.entry["values"] = self._valori_recenti()
        salva_config(config)  # salva le recenti e la cartella: non e' una modifica al profilo
        self.modifiche_non_salvate = False  # le modifiche al profilo le ha gia' gestite _memorizza_colonne
        opzioni = {"defaultextension": ".html", "filetypes": [("HTML", "*.html")], "title": self.t("salva_titolo"),
                   "initialfile": nome_file_proposto(cartella)}  # propone il nome della cartella scansionata
        ultima = config.get("cartella_salvataggio", "")
        if os.path.isdir(ultima):
            opzioni["initialdir"] = ultima  # riparte dall'ultima cartella usata per salvare
        out = filedialog.asksaveasfilename(**opzioni)
        if not out:
            return
        self.annulla.clear()
        self.occupato = True
        # (menu lingua spostato, niente da disabilitare)  # durante la scansione la lingua non si cambia
        self.btn_aspetto.config(state="disabled")  # e nemmeno layout e tema
        self.btn_genera.config(state=tk.DISABLED)
        self.btn_annulla.config(state=tk.NORMAL)
        self.btn_annulla.pack(side="right", padx=(0, 10))  # a sinistra di Genera, finché la scansione dura
        self.barra["value"] = 0
        self.stato.config(text=self.t("ricerca_file"), style="Stato.TLabel")
        threading.Thread(target=self.lavora, daemon=True,
                         args=(cartella, out, scelte, self.mostra.get(), self.usa_cache.get(),
                               self.dividi.get(), self._esclusioni_attive())).start()

    # --- thread di lavoro (non tocca mai direttamente i widget)
    def lavora(self, cartella, out, colonne, mostra, usa_cache=True, dividi=False, esclusioni=None):
        try:
            self._lavora(cartella, out, colonne, mostra, usa_cache, dividi, esclusioni)
        except Exception as e:  # qualsiasi imprevisto: l'interfaccia non deve restare bloccata
            self.root.after(0, self.fine, self.t("errore_imprevisto", errore=e), True)

    def _lavora(self, cartella, out, colonne, mostra, usa_cache=True, dividi=False, esclusioni=None):
        t_inizio = time.perf_counter()
        statistiche = {}
        estensioni, nomi = esclusioni if esclusioni else (None, None)
        files = elenca_file(cartella, statistiche, estensioni, nomi, self.annulla, self._avanza_ricerca)
        if files is None:
            self.root.after(0, self.fine, self.t("annullata"), False)
            return
        t_elenco = time.perf_counter()
        totale = len(files)
        if totale == 0:
            self.root.after(0, self.fine, self.t("cartella_vuota"), False)
            return

        self.ver_pronta.wait(120)
        cache = None
        if usa_cache and self.ffprobe:
            cache = CacheScansioni(self.versione_ff)
            cache.carica(cartella)

        records, cartelle, indici = [], [], {}
        stima = StimaTempo(t_elenco)
        workers = min(8, (os.cpu_count() or 2) * 2)
        with ThreadPoolExecutor(max_workers=workers) as ex:
            risultati = ex.map(lambda f: analizza(f[0], self.ffprobe, self.annulla, f[1], cache, f[2]), files)
            for n, rec in enumerate(risultati, 1):
                if rec:
                    rel = os.path.dirname(files[n - 1][0])[len(cartella):].strip(os.sep)
                    rp = os.path.join(rel, rec["p"]) if rel else rec["p"]
                    rec = {**rec, "rp": rp}
                    if dividi:
                        if rel not in indici:
                            indici[rel] = len(cartelle)
                            cartelle.append(rel)
                        rec = {**rec, "k": indici[rel]}
                    records.append(rec)
                if n % 10 == 0 or n == totale:
                    self.root.after(0, self.progresso, n, totale, stima.aggiorna(n, totale))

        t_analisi = time.perf_counter()
        if cache:
            cache.salva(cartella, pota=not self.annulla.is_set())
        if self.annulla.is_set():
            self.root.after(0, self.fine, self.t("annullata"), False)
            return
        try:
            with open(out, "w", encoding="utf-8", errors="replace") as f:
                f.write(genera_html(cartella, records, colonne, mostra == "percorso", self.versione_ff,
                                    self.lingua, cartelle if len(cartelle) > 1 else None, statistiche.get("cartelle"),
                                    tema=self.tema))
        except OSError as e:
            self.root.after(0, self.fine, self.t("salvataggio_fallito", errore=e), True)
            return
        dettaglio = ""
        if cache and (cache.dalla_cache or cache.analizzati):
            dettaglio = self.t("dettaglio_cache", h=cache.dalla_cache, a=cache.analizzati)
        dettaglio += self.t("tempi", a=f"{t_elenco - t_inizio:.1f}", b=f"{t_analisi - t_elenco:.1f}",
                            c=f"{time.perf_counter() - t_analisi:.1f}")
        self.root.after(0, self.fine, self.t("report_salvato"), False, True, out, dettaglio)

    def _avanza_ricerca(self, n):
        """Chiamata dal thread di lavoro durante la ricerca dei file: l'aggiornamento della finestra passa dal thread principale."""
        try:
            self.root.after(0, self.progresso_ricerca, n)
        except Exception:
            pass  # finestra già chiusa

    def progresso_ricerca(self, n):
        if self.occupato and not self.annulla.is_set():
            self.stato.config(text=self.t("ricerca_file_n", n=n))

    def progresso(self, n, totale, stima=None):
        pct = int(n / totale * 100)
        self.barra["value"] = pct
        if stima is None or stima < STIMA_MINIMA_MOSTRATA:  # troppo presto per stimare, oppure ormai quasi finito
            self.stato.config(text=self.t("analisi", n=n, totale=totale, pct=pct))
        else:
            self.stato.config(text=self.t("analisi_stima", n=n, totale=totale, pct=pct,
                                          tempo=formatta_durata_breve(stima)))

    def fine(self, messaggio, errore, ok=False, percorso=None, dettaglio=""):
        self.occupato = False
        self.modifiche_non_salvate = False
        # (menu lingua spostato, niente da riabilitare)
        self.btn_aspetto.config(state="normal")
        self.btn_genera.config(state=tk.NORMAL)
        self.btn_annulla.config(state=tk.DISABLED)
        self.btn_annulla.pack_forget()
        if ok and percorso:
            config = carica_config()  # qui, nel thread principale: la configurazione la scrive solo lui
            config["cartella_salvataggio"] = os.path.dirname(os.path.abspath(percorso))
            salva_config(config)
            try:  # apre il report nel browser predefinito
                aperto = webbrowser.open(Path(percorso).resolve().as_uri())
            except webbrowser.Error:
                aperto = False
            if aperto:
                self.stato.config(text=self.t("completato_aperto") + dettaglio, style="Ok.TLabel")
            else:
                self.stato.config(text=self.t("completato_salvato") + dettaglio, style="Ok.TLabel")
                messagebox.showinfo(self.t("salvato_titolo"), self.t("apertura_fallita", percorso=percorso))
            return
        self.stato.config(text=messaggio.split("\n")[0],
                          style="Errore.TLabel" if errore else "Stato.TLabel")
        if errore:
            messagebox.showerror(self.t("errore"), messaggio)
        else:
            messagebox.showinfo(self.t("info"), messaggio)


    def _on_closing(self):
        if getattr(self, "modifiche_non_salvate", False):
            risposta = messagebox.askyesnocancel(
                "Modifiche non salvate",
                "Il profilo «" + self.profilo_attivo + "» ha modifiche non salvate.\n\nVuoi salvarle prima di uscire?",
                parent=self.root
            )
            if risposta is None:
                return
            if risposta:
                self._salva_profili()
        self.root.destroy()
def percorso_log_errori():
    return os.path.join(os.path.dirname(percorso_config()), "errore.log")


def segnala_errore(tipo, valore, traccia):
    """Registra e mostra un errore non gestito. Senza questo, con il doppio clic la console si chiude
    all'istante e non si capisce cosa è successo."""
    testo = "".join(traceback.format_exception(tipo, valore, traccia))
    log = percorso_log_errori()
    try:
        os.makedirs(os.path.dirname(log), exist_ok=True)
        with open(log, "a", encoding="utf-8") as f:
            f.write(f"--- {datetime.now():%Y-%m-%d %H:%M:%S}  v{VERSIONE} ---\n{testo}\n")
    except OSError:
        log = "-"
    print(testo, file=sys.stderr)
    try:
        lingua = carica_config().get("lingua")
        messagebox.showerror("Media Directory Lister", traduci(lingua if lingua in LINGUE else "it", "errore_fatale",
                                                         errore=valore, log=log))
    except Exception:
        pass  # se nemmeno la finestra di errore funziona, restano la console e il file di log


def main():
    if IS_WIN:
        try:
            import ctypes
            ctypes.windll.shcore.SetProcessDpiAwareness(1)  # testo nitido sugli schermi ad alta risoluzione
        except (AttributeError, OSError):
            pass
    segna_fase("moduli importati")
    try:
        root = tk.Tk()
        segna_fase("finestra Tk creata")
        root.report_callback_exception = segnala_errore  # errore in un pulsante: avviso + log, si continua
        App(root)
        root.after_idle(lambda: (segna_fase("finestra mostrata"), salva_log_avvio()))
        root.mainloop()
    except Exception:
        segnala_errore(*sys.exc_info())
        if sys.stdin and sys.stdin.isatty():
            input("\nPremi Invio per chiudere... / Press Enter to close...")
        sys.exit(1)


if __name__ == "__main__":
    main()