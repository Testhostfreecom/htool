# -*- coding: utf-8 -*-
from __future__ import annotations
import subprocess
import sys
import importlib
import os
import threading
import logging
import json
import time
import random
import math
import re
import hashlib
import hmac
import base64
import socket
import ipaddress
import platform
import uuid
import secrets
from collections import defaultdict, deque, Counter
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Dict, Tuple, Optional, List
from urllib.parse import urlparse, parse_qs

# ================== KIỂM TRA VÀ CÀI ĐẶT THƯ VIỆN ==================

REQUIRED_PACKAGES = [
    "pytz",
    "requests",
    "websocket-client",
    "rich",
    "cryptography",
]

def check_and_install_packages():
    missing_packages = []
    
    print("=" * 60)
    print("🔍 ĐANG KIỂM TRA THƯ VIỆN...")
    print("=" * 60)
    
    for package in REQUIRED_PACKAGES:
        try:
            import_name = package
            if package == "websocket-client":
                import_name = "websocket"
            elif package == "cryptography":
                import_name = "cryptography"
            
            importlib.import_module(import_name)
            print(f"✅ {package} - Đã cài đặt")
        except ImportError:
            missing_packages.append(package)
            print(f"❌ {package} - CHƯA CÀI ĐẶT")
    
    if not missing_packages:
        print("\n✅ TẤT CẢ THƯ VIỆN ĐÃ SẴN SÀNG!")
        print("=" * 60)
        return True
    
    print("\n" + "=" * 60)
    print(f"⚠️  PHÁT HIỆN {len(missing_packages)} THƯ VIỆN THIẾU:")
    for pkg in missing_packages:
        print(f"   - {pkg}")
    print("=" * 60)
    print("\n🔄 ĐANG TIẾN HÀNH CÀI ĐẶT TỰ ĐỘNG...")
    print("-" * 60)
    
    for package in missing_packages:
        try:
            print(f"📦 Đang cài đặt {package}...")
            subprocess.check_call([
                sys.executable, 
                "-m", 
                "pip", 
                "install", 
                package,
                "--quiet"
            ])
            print(f"✅ Đã cài đặt {package} thành công!")
        except Exception as e:
            print(f"❌ Lỗi khi cài đặt {package}: {e}")
            print(f"💡 Vui lòng cài đặt thủ công: pip install {package}")
            return False
    
    print("\n" + "=" * 60)
    print("✅ TẤT CẢ THƯ VIỆN ĐÃ ĐƯỢC CÀI ĐẶT XONG!")
    print("=" * 60)
    return True

if not check_and_install_packages():
    print("\n" + "=" * 60)
    print("❌ KHÔNG THỂ CÀI ĐẶT ĐẦY ĐỦ THƯ VIỆN")
    print("💡 VUI LÒNG CÀI ĐẶT THỦ CÔNG:")
    print("   pip install pytz requests websocket-client rich cryptography")
    print("=" * 60)
    sys.exit(1)

# ================== IMPORT THƯ VIỆN ==================

import pytz
import requests
import websocket
from rich.console import Console, Group
from rich.table import Table
from rich.panel import Panel
from rich.live import Live
from rich.align import Align
from rich.prompt import Prompt, Confirm, IntPrompt, FloatPrompt
from rich.rule import Rule
from rich.text import Text
from rich import box
from rich.columns import Columns
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC

# ================== CẤU HÌNH ==================

console = Console()
tz = pytz.timezone("Asia/Ho_Chi_Minh")

# ================== GIAO DIỆN HTOOL ==================

HTOOL_COLORS = {
    "gold": "#FFD700",
    "gold_dark": "#B8860B",
    "platinum": "#E5E4E2",
    "diamond": "#B9F2FF",
    "ruby": "#E0115F",
    "emerald": "#50C878",
    "sapphire": "#0F52BA",
    "amethyst": "#9966CC",
    "onyx": "#353839",
    "rose": "#FF007F",
    "neon_blue": "#00D4FF",
    "neon_pink": "#FF00E5",
    "neon_green": "#39FF14",
    "neon_orange": "#FF5E00",
    "crimson": "#DC143C",
    "turquoise": "#40E0D0",
    "lavender": "#E6E6FA",
}

ICONS = {
    "crown": "👑",
    "diamond": "💎",
    "star": "⭐",
    "fire": "🔥",
    "lightning": "⚡",
    "target": "🎯",
    "shield": "🛡️",
    "sword": "⚔️",
    "brain": "🧠",
    "robot": "🤖",
    "rocket": "🚀",
    "trophy": "🏆",
    "medal": "🏅",
    "gem": "💠",
    "sparkle": "✨",
    "settings": "⚙️",
    "user": "👤",
    "key": "🔑",
    "lock": "🔒",
    "unlock": "🔓",
    "check": "✅",
    "cross": "❌",
    "warning": "⚠️",
    "info": "ℹ️",
    "money": "💰",
    "chart": "📊",
    "clock": "⏰",
    "link": "🔗",
    "wifi": "📶",
    "globe": "🌐",
    "plus": "➕",
    "minus": "➖",
    "arrow": "➡️",
    "heart": "❤️",
    "bell": "🔔",
    "gift": "🎁",
    "magic": "🔮",
    "phone": "📞",
}

LOGO = """
╔════════════════════════════════════════════════════════════════════════════╗
║  ██╗  ██╗████████╗ ██████╗  ██████╗ ██╗     ██╗                           ║
║  ██║  ██║╚══██╔══╝██╔═══██╗██╔═══██╗██║     ██║                           ║
║  ███████║   ██║   ██║   ██║██║   ██║██║     ██║                           ║
║  ██╔══██║   ██║   ██║   ██║██║   ██║██║     ██║                           ║
║  ██║  ██║   ██║   ╚██████╔╝╚██████╔╝███████╗███████╗                     ║
║  ╚═╝  ╚═╝   ╚═╝    ╚═════╝  ╚═════╝ ╚══════╝╚══════╝                     ║
╚════════════════════════════════════════════════════════════════════════════╝
"""

# ================== BIẾN TOÀN CỤC ==================
_ws_status = "⏳ Đang kết nối..."
_is_authenticated = False
_user_key = None
_key_type = "free"
_heartbeat_running = False
_heartbeat_thread = None
_in_menu = False
_ip_info = {}
AI_PERFORMANCE = defaultdict(lambda: {"wins": 0, "losses": 0, "total": 0})
_secure_mode = False
_secure_tool = None
stop_flag = False
USER_ID = None
SECRET_KEY = None

# ================== SUPABASE CONFIG ==================

SUPABASE_URL = "https://ebviepssggyyrdeedpnz.supabase.co"
SUPABASE_KEY = "sb_publishable_B3VF2kG0260fFrOtWBJi1g_ylklAm1_"
ADMIN_SECRET_CODE = "9826665"

# ================== TELEGRAM CONFIG ==================

TELEGRAM_BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
TELEGRAM_CHAT_ID = ""
TELEGRAM_ENABLED = False

# ================== HỆ THỐNG CHỐNG SOI ==================

class AntiDetectionSystem:
    def __init__(self):
        self.is_stealth_mode = False
        self.detection_risk = 0
        self.last_check = time.time()
        self.request_history = []
        self.stealth_session_id = hashlib.md5(str(time.time()).encode()).hexdigest()[:8]
        self.user_agents = [
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:109.0) Gecko/20100101 Firefox/119.0',
            'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.1 Safari/605.1.15',
            'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
            'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
            'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/119.0.0.0 Safari/537.36 Edg/119.0.0.0',
        ]
        self.accept_languages = ['vi-VN,vi;q=0.9,en;q=0.8', 'en-US,en;q=0.9', 'vi;q=0.9,en;q=0.8']
        self.last_request_time = 0
        self.min_delay = 0.3
        self.max_delay = 1.5
    
    def enable_stealth_mode(self):
        self.is_stealth_mode = True
        safe_console_print("[bold green]🛡️ Đã bật chế độ tàng hình![/bold green]")
        self.stealth_session_id = hashlib.md5(str(time.time() + random.random()).encode()).hexdigest()[:8]
    
    def get_random_delay(self) -> float:
        return random.uniform(self.min_delay, self.max_delay)
    
    def wait_before_request(self):
        current_time = time.time()
        elapsed = current_time - self.last_request_time
        if elapsed < self.min_delay:
            wait_time = self.get_random_delay() - elapsed
            if wait_time > 0:
                time.sleep(wait_time)
        self.last_request_time = time.time()
    
    def get_random_headers(self) -> dict:
        return {
            'User-Agent': random.choice(self.user_agents),
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': random.choice(self.accept_languages),
            'Accept-Encoding': 'gzip, deflate, br',
            'Connection': 'keep-alive',
            'Upgrade-Insecure-Requests': '1',
            'Cache-Control': 'no-cache',
            'Pragma': 'no-cache',
        }
    
    def make_stealth_request(self, url: str, method: str = 'GET', **kwargs) -> Optional[requests.Response]:
        self.wait_before_request()
        headers = self.get_random_headers()
        if 'headers' in kwargs:
            headers.update(kwargs['headers'])
        kwargs['headers'] = headers
        if 'timeout' not in kwargs:
            kwargs['timeout'] = random.uniform(8, 15)
        
        try:
            response = requests.request(method, url, **kwargs)
            self.request_history.append({
                'url': url,
                'time': time.time(),
                'status': response.status_code
            })
            self.check_detection_risk()
            return response
        except Exception as e:
            safe_console_print(f"[yellow]⚠️ Request error: {e}[/yellow]")
            return None
    
    def check_detection_risk(self):
        recent_requests = [r for r in self.request_history 
                          if time.time() - r['time'] < 60]
        
        if len(recent_requests) > 30:
            self.detection_risk += 10
        elif len(recent_requests) > 20:
            self.detection_risk += 5
        elif len(recent_requests) > 10:
            self.detection_risk += 2
        
        if self.detection_risk > 70:
            safe_console_print(f"[red]⚠️ Phát hiện rủi ro cao ({self.detection_risk}%)[/red]")
            self.detection_risk = 0
    
    def get_status(self) -> dict:
        return {
            'stealth_mode': self.is_stealth_mode,
            'detection_risk': self.detection_risk,
            'request_count': len(self.request_history),
            'session_id': self.stealth_session_id,
        }
    
    def display_status(self):
        status = self.get_status()
        safe_console_print("\n" + "="*50)
        safe_console_print("🛡️ ANTI-DETECTION STATUS")
        safe_console_print("="*50)
        safe_console_print(f"🔒 Stealth Mode: {'✅ BẬT' if status['stealth_mode'] else '❌ TẮT'}")
        safe_console_print(f"⚠️ Detection Risk: {status['detection_risk']}%")
        safe_console_print(f"📊 Total Requests: {status['request_count']}")
        safe_console_print(f"🔑 Session ID: {status['session_id']}")
        safe_console_print("="*50)

class SecureHTOOL:
    def __init__(self):
        self.anti_detection = AntiDetectionSystem()
        self.is_stealth = False
    
    def start_stealth_mode(self):
        safe_console_print("\n[bold]🛡️ KHỞI ĐỘNG CHẾ ĐỘ CHỐNG SOI[/bold]")
        safe_console_print("="*50)
        self.anti_detection.enable_stealth_mode()
        self.is_stealth = True
        self.anti_detection.display_status()
        safe_console_print("\n[green]✅ Đã sẵn sàng chống soi![/green]")
        time.sleep(2)
    
    def make_secure_request(self, url: str, **kwargs) -> Optional[requests.Response]:
        if self.is_stealth:
            return self.anti_detection.make_stealth_request(url, **kwargs)
        else:
            return requests.request('GET', url, **kwargs)
    
    def secure_post(self, url: str, **kwargs) -> Optional[requests.Response]:
        if self.is_stealth:
            return self.anti_detection.make_stealth_request(url, method='POST', **kwargs)
        else:
            return requests.post(url, **kwargs)
    
    def get_status(self) -> dict:
        if self.is_stealth:
            return self.anti_detection.get_status()
        return {'stealth_mode': False}
    
    def display_status(self):
        if self.is_stealth:
            self.anti_detection.display_status()

# ================== SCAN IP ==================

def get_public_ip() -> Optional[str]:
    try:
        response = requests.get('https://api.ipify.org', timeout=5)
        if response.status_code == 200:
            return response.text.strip()
    except:
        pass
    
    try:
        response = requests.get('https://ip-api.com/json', timeout=5)
        if response.status_code == 200:
            data = response.json()
            return data.get('query')
    except:
        pass
    return None

def get_local_ip() -> Optional[str]:
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(("8.8.8.8", 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except:
        return None

def get_device_fingerprint() -> str:
    try:
        info = []
        try:
            mac = ':'.join(['{:02x}'.format((uuid.getnode() >> elements) & 0xff) 
                           for elements in range(0, 2*6, 2)][::-1])
            info.append(mac)
        except:
            pass
        try:
            info.append(socket.gethostname())
        except:
            pass
        info.append(platform.platform())
        info.append(platform.processor())
        info.append(platform.machine())
        fingerprint_str = ''.join(info)
        return hashlib.sha256(fingerprint_str.encode()).hexdigest()[:16]
    except:
        return hashlib.md5(str(time.time()).encode()).hexdigest()[:16]

def scan_ip_ban_list() -> bool:
    try:
        ip = get_public_ip()
        if not ip:
            return False
        
        blacklist_file = "ip_blacklist.txt"
        if not os.path.exists(blacklist_file):
            with open(blacklist_file, 'w', encoding='utf-8') as f:
                f.write("# Blacklisted IPs\n")
            return False
        
        with open(blacklist_file, 'r', encoding='utf-8') as f:
            blacklist = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if ip in blacklist:
            safe_console_print(f"[red]❌ IP {ip} đã bị cấm![/red]")
            return True
        return False
    except:
        return False

def check_ip_whitelist() -> bool:
    try:
        ip = get_public_ip()
        if not ip:
            return False
        
        whitelist_file = "ip_whitelist.txt"
        if not os.path.exists(whitelist_file):
            return True
        
        with open(whitelist_file, 'r', encoding='utf-8') as f:
            whitelist = [line.strip() for line in f if line.strip() and not line.startswith('#')]
        
        if not whitelist:
            return True
        
        if ip in whitelist:
            return True
        
        for entry in whitelist:
            if '/' in entry:
                try:
                    network = ipaddress.ip_network(entry, strict=False)
                    if ipaddress.ip_address(ip) in network:
                        return True
                except:
                    pass
        
        safe_console_print(f"[red]❌ IP {ip} không có trong whitelist![/red]")
        return False
    except:
        return True

class IPScanner:
    def __init__(self):
        self.public_ip = None
        self.local_ip = None
        self.device_fingerprint = None
        self.location_info = None
        self._scanned = False
    
    def scan(self) -> bool:
        try:
            self.public_ip = get_public_ip()
            self.local_ip = get_local_ip()
            self.device_fingerprint = get_device_fingerprint()
            
            if self.public_ip:
                try:
                    response = requests.get(f'http://ip-api.com/json/{self.public_ip}', timeout=5)
                    if response.status_code == 200:
                        self.location_info = response.json()
                except:
                    pass
            
            self._scanned = True
            
            if scan_ip_ban_list():
                return False
            
            if not check_ip_whitelist():
                return False
            
            self.log_scan_info()
            return True
        except Exception as e:
            safe_console_print(f"[yellow]⚠️ Lỗi scan IP: {e}[/yellow]")
            return False
    
    def log_scan_info(self):
        log_data = {
            "timestamp": datetime.now(tz).isoformat(),
            "public_ip": self.public_ip,
            "local_ip": self.local_ip,
            "fingerprint": self.device_fingerprint,
            "location": self.location_info,
        }
        
        try:
            with open("ip_scan_log.json", "a", encoding="utf-8") as f:
                f.write(json.dumps(log_data, ensure_ascii=False) + "\n")
        except:
            pass
        
        safe_console_print("[dim]📡 SCAN IP:[/dim]")
        if self.public_ip:
            safe_console_print(f"  🌐 Public IP: [bold]{self.public_ip}[/bold]")
        if self.local_ip:
            safe_console_print(f"  🏠 Local IP: [bold]{self.local_ip}[/bold]")
        if self.location_info:
            city = self.location_info.get('city', 'N/A')
            country = self.location_info.get('country', 'N/A')
            safe_console_print(f"  📍 Location: [bold]{city}, {country}[/bold]")
        safe_console_print(f"  🔑 Fingerprint: [dim]{self.device_fingerprint}[/dim]")
        safe_console_print("")
    
    def get_status(self) -> dict:
        return {
            "scanned": self._scanned,
            "public_ip": self.public_ip,
            "local_ip": self.local_ip,
            "fingerprint": self.device_fingerprint,
            "location": self.location_info,
        }
    
    def is_ip_safe(self) -> bool:
        if not self._scanned:
            self.scan()
        if scan_ip_ban_list():
            return False
        if not check_ip_whitelist():
            return False
        return True

def enhanced_auth_check():
    global _ip_info
    ip_scanner = IPScanner()
    if not ip_scanner.scan():
        safe_console_print("[red]❌ Scan IP thất bại! Tool sẽ không chạy.[/red]")
        return False
    if not ip_scanner.is_ip_safe():
        safe_console_print("[red]❌ IP không an toàn! Tool sẽ không chạy.[/red]")
        return False
    _ip_info = ip_scanner.get_status()
    return True

# ================== CHỐNG DEBUG ==================

def detect_debugger() -> bool:
    try:
        if sys.gettrace() is not None:
            return True
        if 'PYCHARM_HOSTED' in os.environ:
            return True
        return False
    except:
        return False

def anti_crack_check() -> bool:
    if detect_debugger():
        console.print("[red]❌ Phát hiện debugger! Tool sẽ không chạy.[/red]")
        return False
    return True

# ================== HÀM XÁC THỰC KEY ==================

def verify_key_with_device(key: str) -> dict:
    if detect_debugger():
        return {"valid": False, "error": "Phát hiện debugger! Không thể xác thực."}

    key = (key or "").strip()
    url = f"{SUPABASE_URL}/rest/v1/keys?key_code=eq.{key}"

    headers = supabase_headers()

    try:
        response = requests.get(url, headers=headers, timeout=15)

        if response.status_code != 200:
            # Fallback: key FREE local nếu Supabase lỗi
            local_ok, local_uid, local_item = validate_local_free_key(key)
            if local_ok and local_item:
                exp = local_item.get("expires")
                expires_at = datetime.fromtimestamp(float(exp), tz=timezone.utc).isoformat() if exp else "forever"
                return {
                    "valid": True,
                    "data": {
                        "key": key,
                        "key_type": "free",
                        "max_ai": 10,
                        "expires_at": expires_at,
                        "note": f"Local FREE key (user {local_uid})",
                        "used_count": 0,
                        "max_uses": None,
                        "source": "local",
                    }
                }
            return {"valid": False, "error": f"HTTP {response.status_code}"}

        data = response.json()

        if not data:
            # Không có trên Supabase → thử key FREE local
            local_ok, local_uid, local_item = validate_local_free_key(key)
            if local_ok and local_item:
                exp = local_item.get("expires")
                expires_at = datetime.fromtimestamp(float(exp), tz=timezone.utc).isoformat() if exp else "forever"
                return {
                    "valid": True,
                    "data": {
                        "key": key,
                        "key_type": "free",
                        "max_ai": 10,
                        "expires_at": expires_at,
                        "note": f"Local FREE key (user {local_uid})",
                        "used_count": 0,
                        "max_uses": None,
                        "source": "local",
                    }
                }
            return {"valid": False, "error": "Key không tồn tại"}

        keyData = data[0]

        if keyData.get('status') != 'active':
            return {"valid": False, "error": "Key đã bị vô hiệu hóa"}

        if keyData.get('expires_at'):
            try:
                expiry = datetime.fromisoformat(keyData['expires_at'].replace('Z', '+00:00'))
                if datetime.now().astimezone() > expiry:
                    return {"valid": False, "error": "Key đã hết hạn"}
            except Exception:
                pass

        used_count = keyData.get('used_count', 0)
        max_uses = keyData.get('max_uses')
        if max_uses and used_count >= max_uses:
            return {"valid": False, "error": "Key đã đạt giới hạn sử dụng"}

        new_count = used_count + 1
        update_url = f"{SUPABASE_URL}/rest/v1/keys?key_code=eq.{key}"
        update_data = {"used_count": new_count}

        try:
            requests.patch(update_url, json=update_data, headers=headers, timeout=10)
        except Exception:
            pass

        return {
            "valid": True,
            "data": {
                "key": key,
                "key_type": keyData.get('key_type', 'free'),
                "max_ai": keyData.get('max_ai', 10),
                "expires_at": keyData.get('expires_at', 'forever'),
                "note": keyData.get('note', ''),
                "used_count": new_count,
                "max_uses": keyData.get('max_uses'),
                "source": "supabase",
            }
        }

    except Exception as e:
        local_ok, local_uid, local_item = validate_local_free_key(key)
        if local_ok and local_item:
            exp = local_item.get("expires")
            expires_at = datetime.fromtimestamp(float(exp), tz=timezone.utc).isoformat() if exp else "forever"
            return {
                "valid": True,
                "data": {
                    "key": key,
                    "key_type": "free",
                    "max_ai": 10,
                    "expires_at": expires_at,
                    "note": f"Local FREE key (user {local_uid})",
                    "used_count": 0,
                    "max_uses": None,
                    "source": "local",
                }
            }
        return {"valid": False, "error": f"Lỗi: {str(e)}"}


def supabase_headers(prefer: Optional[str] = None) -> dict:
    """Headers chuẩn cho Supabase REST API."""
    h = {
        "apikey": SUPABASE_KEY,
        "Authorization": f"Bearer {SUPABASE_KEY}",
        "Content-Type": "application/json",
        "User-Agent": "HTOOL-Secure/3.0",
    }
    if prefer:
        h["Prefer"] = prefer
    return h


def create_key_on_supabase(
    key_code: str,
    key_type: str = "free",
    max_ai: int = 10,
    duration_hours: int = 13,
    note: str = "",
    user_id: str = "",
    max_uses: Optional[int] = None,
) -> tuple:
    """
    Tạo key mới trên Supabase (bảng keys).
    Trả về (success: bool, message_or_data).
    """
    url = f"{SUPABASE_URL}/rest/v1/keys"
    expires_at = (datetime.now(timezone.utc) + timedelta(hours=duration_hours)).isoformat()

    payload = {
        "key_code": key_code,
        "key_type": key_type,
        "status": "active",
        "max_ai": max_ai,
        "expires_at": expires_at,
        "used_count": 0,
        "note": note or f"Đổi xu - user {user_id}" if user_id else "KEY FREE 13H (đổi xu)",
    }
    if max_uses is not None:
        payload["max_uses"] = max_uses

    try:
        response = requests.post(
            url,
            headers=supabase_headers(prefer="return=representation"),
            json=payload,
            timeout=15,
        )

        if response.status_code in (200, 201):
            data = response.json()
            row = data[0] if isinstance(data, list) and data else data
            return True, {
                "key_code": key_code,
                "key_type": key_type,
                "expires_at": expires_at,
                "max_ai": max_ai,
                "supabase": row,
            }

        # Conflict: key đã tồn tại
        if response.status_code == 409:
            return False, "Key đã tồn tại trên Supabase"

        err_text = response.text[:300] if response.text else f"HTTP {response.status_code}"
        return False, f"Supabase lỗi {response.status_code}: {err_text}"

    except Exception as e:
        return False, f"Lỗi kết nối Supabase: {str(e)}"


def parse_datetime_safe(date_str):
    if not date_str or date_str == 'forever':
        return None
    try:
        if 'Z' in date_str or '+' in date_str:
            dt = datetime.fromisoformat(date_str.replace('Z', '+00:00'))
            return dt.astimezone(timezone.utc)
        else:
            dt = datetime.strptime(date_str, "%Y-%m-%d %H:%M:%S")
            return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        try:
            dt = datetime.strptime(date_str, "%Y-%m-%dT%H:%M:%S.%f")
            return dt.replace(tzinfo=timezone.utc)
        except ValueError:
            return None

# ================== HEARTBEAT ==================

def heartbeat_worker():
    global _is_authenticated, _user_key, _heartbeat_running
    
    while _heartbeat_running:
        time.sleep(30)
        
        if _user_key and _is_authenticated:
            result = verify_key_with_device(_user_key)
            if not result.get("valid"):
                _is_authenticated = False
                safe_console_print("[bold red]🔒 KEY ĐÃ BỊ KHÓA HOẶC HẾT HẠN![/bold red]")
                safe_console_print("[bold red]Tool sẽ tự động thoát sau 5 giây...[/bold red]")
                time.sleep(5)
                os._exit(0)

def start_heartbeat():
    global _heartbeat_thread, _heartbeat_running
    _heartbeat_running = True
    _heartbeat_thread = threading.Thread(target=heartbeat_worker, daemon=True)
    _heartbeat_thread.start()

def stop_heartbeat():
    global _heartbeat_running
    _heartbeat_running = False

# ================== MÀN HÌNH XÁC THỰC ==================

def show_auth_choice_menu():
    """Menu xác thực: đổi key, nhập key, hoặc tạo user."""
    while True:
        console.clear()
        gold_color = HTOOL_COLORS["gold"]
        for line in LOGO.split("\n"):
            if line.strip():
                console.print(Align.center(line, style=f"bold {gold_color}"))

        console.print()
        console.print(Align.center("═" * 50, style="dim"))
        console.print(Align.center(f"[bold {gold_color}]XÁC THỰC KEY[/bold {gold_color}]"))
        console.print(Align.center("═" * 50, style="dim"))
        console.print()

        console.print(Panel(
            Text.assemble(
                ("[1] 🎁 ", "bold cyan"), ("ĐỔI KEY", "bold white"),
                ("\n    5 xu → KEY FREE 13 GIỜ\n\n", "dim"),
                ("[2] 🔑 ", "bold cyan"), ("NHẬP KEY", "bold white"),
                ("\n    Nhập key đã có\n\n", "dim"),
                ("[3] 👤 ", "bold cyan"), ("TẠO USER", "bold white"),
                ("\n    Đăng ký ID mới cho hệ thống xu/key", "dim"),
            ),
            title="[bold]CHỌN HÌNH THỨC[/bold]",
            border_style=gold_color,
            box=box.ROUNDED
        ))
        console.print()

        raw = Prompt.ask(
            f"[bold {gold_color}]>> Chọn[/bold {gold_color}]",
            default="2"
        )
        # Admin ẩn từ màn xác thực
        if raw.strip() == ADMIN_SECRET_CODE:
            admin_menu()
            continue
        choice = raw.strip()
        if choice == "1":
            coin_exchange_before_auth()
        elif choice == "3":
            prompt_create_user()
            input("\n[dim]Nhấn Enter để quay lại...[/dim]")
        elif choice == "2":
            return show_auth_screen()
        else:
            console.print("[red]Lựa chọn không hợp lệ[/red]")
            time.sleep(1)


def coin_exchange_before_auth() -> None:
    """Menu đổi key bằng xu: tạo user, nhận xu, đổi key."""
    while True:
        console.clear()
        console.print(Panel(
            Align.center("🎁 ĐỔI KEY BẰNG XU 🎁"),
            border_style=HTOOL_COLORS["gold"],
            box=box.DOUBLE
        ))
        console.print()
        console.print("[1] 👤 Tạo user mới")
        console.print("[2] 🎁 Nhận xu / Đổi KEY FREE 13 GIỜ")
        console.print("[q] 🔙 Quay lại")
        console.print()

        sub = Prompt.ask(
            f"[bold {HTOOL_COLORS['gold']}]>> Chọn[/bold {HTOOL_COLORS['gold']}]",
            choices=["1", "2", "q"],
            default="2"
        )

        if sub == "q":
            return

        if sub == "1":
            prompt_create_user()
            input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")
            continue

        # sub == "2": dùng xu / đổi key
        user_id_text = Prompt.ask(
            "[bold cyan]Nhập ID tài khoản để dùng xu[/bold cyan]",
            default=""
        )
        if not user_id_text.isdigit():
            console.print("[red]❌ ID tài khoản không hợp lệ![/red]")
            time.sleep(1.5)
            continue

        user_id = int(user_id_text)

        # Nếu user chưa tồn tại → hỏi tạo luôn
        data = load_user_data_secure()
        if str(user_id) not in data:
            console.print(f"[yellow]⚠️ User {user_id} chưa tồn tại.[/yellow]")
            create_now = Prompt.ask(
                "[bold cyan]Tạo user này ngay? (y/n)[/bold cyan]",
                choices=["y", "n"],
                default="y"
            )
            if create_now == "y":
                ok, msg = create_user_secure(user_id)
                console.print(f"[green]✅ {msg}[/green]" if ok else f"[red]❌ {msg}[/red]")
                if not ok:
                    time.sleep(1.5)
                    continue
            else:
                time.sleep(1)
                continue

        success, msg = claim_daily_coins_secure(user_id)
        console.print(
            f"[green]✅ {msg}[/green]" if success else f"[yellow]ℹ️ {msg}[/yellow]"
        )

        balance = get_user_balance_secure(user_id)
        console.print(f"\n[bold green]💰 Số dư: {balance.get('coins', 0):.2f} xu[/bold green]")
        console.print("[dim]🔑 5 xu = KEY FREE 13 GIỜ[/dim]\n")

        if balance.get("coins", 0) >= FREE_KEY_PRICE:
            confirm = Prompt.ask(
                "[bold cyan]Đổi 5 xu lấy KEY FREE 13 GIỜ? (y/n)[/bold cyan]",
                choices=["y", "n"],
                default="y"
            )
            if confirm == "y":
                with console.status("[bold yellow]⏳ Đang tạo key trên Supabase...[/bold yellow]", spinner="dots"):
                    ok, result = exchange_free_key_13h_secure(user_id)
                if ok:
                    console.print(Panel(
                        Text.assemble(
                            ("✅ ĐỔI KEY THÀNH CÔNG!\n\n", "bold green"),
                            ("KEY: ", "bold white"), (f"{result}\n", f"bold {HTOOL_COLORS['gold']}"),
                            ("Loại: FREE\n", "bold cyan"),
                            ("Thời hạn: 13 GIỜ\n", "bold green"),
                            ("🌐 Supabase: ", "white"), ("Đã tạo & kích hoạt\n", "bold green"),
                            ("💡 Dùng key này ở menu NHẬP KEY để đăng nhập.", "dim"),
                        ),
                        border_style="green",
                        box=box.HEAVY
                    ))
                else:
                    console.print(f"[red]❌ {result}[/red]")
        else:
            console.print("[yellow]⚠️ Chưa đủ 5 xu để đổi key.[/yellow]")

        input("\n[dim]Nhấn Enter để quay lại...[/dim]")


def show_auth_screen():
    global _key_type, _secure_mode
    
    if not anti_crack_check():
        return False, None, "free"
    
    if not enhanced_auth_check():
        console.print("[red]❌ Xác thực IP thất bại![/red]")
        time.sleep(2)
        return False, None, "free"
    
    console.clear()
    gold_color = HTOOL_COLORS["gold"]
    logo_lines = LOGO.split('\n')
    for line in logo_lines:
        if line.strip():
            console.print(Align.center(line, style=f"bold {gold_color}"))
    
    console.print()
    console.print(Align.center("═" * 50, style="dim"))
    console.print(Align.center(f"[bold {gold_color}]XÁC THỰC KEY[/bold {gold_color}]", style=f"bold {gold_color}"))
    console.print(Align.center("═" * 50, style="dim"))
    console.print()
    
    console.print(Panel(
        Text.assemble(
            ("🔑 KEY FREE: ", "bold white"),
            ("10 AI (VTH/CDTD) · Lotto 5 AI\n", "dim"),
            ("👑 KEY VIP: ", "bold gold"),
            ("Toàn bộ AI (VTH + CDTD + Lotto)\n", "bold gold"),
            ("\n", ""),
            ("🔒 Anti-Crack Active", "bold green"),
            ("\n", ""),
            ("🌐 IP Security Active", "bold green"),
            ("\n", ""),
            ("🛡️ Anti-Detection Active", "bold green"),
        ),
        title="[bold]THÔNG TIN KEY[/bold]",
        border_style=HTOOL_COLORS["gold"],
        box=box.ROUNDED
    ))
    console.print()

    console.print("[bold cyan]Bạn muốn:[/bold cyan]")
    console.print("[1] 🔑 Nhập Key để xác thực")
    console.print("[2] 👤 Tạo User mới (hệ thống xu/key)")
    console.print()
    auth_sub = Prompt.ask(
        f"[bold {gold_color}]>> Chọn[/bold {gold_color}]",
        choices=["1", "2"],
        default="1"
    )
    if auth_sub == "2":
        prompt_create_user()
        input("\n[dim]Nhấn Enter để quay lại nhập key...[/dim]")
        console.clear()
        for line in logo_lines:
            if line.strip():
                console.print(Align.center(line, style=f"bold {gold_color}"))
        console.print()
        console.print(Align.center("═" * 50, style="dim"))
        console.print(Align.center(f"[bold {gold_color}]XÁC THỰC KEY[/bold {gold_color}]", style=f"bold {gold_color}"))
        console.print(Align.center("═" * 50, style="dim"))
        console.print()
    
    console.print(f"[bold cyan]🔑 Nhập Key:[/bold cyan]")
    console.print("[dim]   (Key có dạng: HTOOL_XXXXX hoặc FREE_XXXXX)[/dim]")
    key = Prompt.ask("   >>", default="")
    
    if not key:
        console.print("[red]❌ Key không được để trống![/red]")
        time.sleep(1.5)
        return False, None, "free"
    
    console.print()
    console.print("[bold]🛡️ BẬT CHẾ ĐỘ CHỐNG SOI?[/bold]")
    console.print("[dim]  - Giúp tránh bị phát hiện khi dùng tool[/dim]")
    console.print("[dim]  - Tự động xoay IP và fake headers[/dim]")
    console.print("[dim]  - Giảm nguy cơ bị ban[/dim]")
    stealth_choice = Prompt.ask("[bold cyan]>> Bật chế độ chống soi? (y/n)[/bold cyan]", 
                                 choices=['y', 'n'], default='y')
    
    if stealth_choice == 'y':
        _secure_mode = True
    else:
        _secure_mode = False
        console.print("[dim]⚠️ Chế độ chống soi đã tắt[/dim]")
    
    console.print()
    with console.status(f"[bold yellow]⏳ Đang xác thực...[/bold yellow]", spinner="dots") as status:
        time.sleep(0.5)
        result = verify_key_with_device(key)
    
    if result.get("valid"):
        console.print()
        data = result.get("data", {})
        key_type = data.get("key_type", "free")
        max_ai = data.get("max_ai", 10)
        
        expiry_info = ""
        expires_at = data.get('expires_at')
        if expires_at and expires_at != 'forever':
            try:
                expiry_dt = parse_datetime_safe(expires_at)
                if expiry_dt:
                    now_utc = datetime.now(timezone.utc)
                    time_left = expiry_dt - now_utc
                    days = time_left.days
                    hours = time_left.seconds // 3600
                    minutes = (time_left.seconds % 3600) // 60
                    if days > 0:
                        expiry_info = f"Còn {days} ngày {hours} giờ"
                    elif hours > 0:
                        expiry_info = f"Còn {hours} giờ {minutes} phút"
                    else:
                        expiry_info = f"Còn {minutes} phút"
            except:
                expiry_info = expires_at
        
        key_icon = "👑" if key_type == "vip" else "🔑"
        key_color = "bold gold" if key_type == "vip" else "bold white"
        
        if _secure_mode:
            global _secure_tool
            _secure_tool = SecureHTOOL()
            _secure_tool.start_stealth_mode()
        
        console.print(Panel(
            Text.assemble(
                ("✅ ", "bold green"),
                ("Xác thực thành công!\n", "bold green"),
                (f"Key: ", "white"),
                (f"{key}\n", f"bold {gold_color}"),
                (f"Loại: ", "white"),
                (f"{key_icon} {key_type.upper()}\n", key_color),
                (f"AI: ", "white"),
                (f"{max_ai}/42 AI\n", "bold cyan"),
                (f"Trạng thái: ", "white"),
                (f"Hoạt động\n", "bold green"),
                (f"Hạn: ", "white"),
                (f"{expiry_info}\n", "yellow"),
                (f"Ghi chú: ", "white"),
                (f"{data.get('note', 'N/A')}\n", "dim"),
                (f"Lượt sử dụng: ", "white"),
                (f"{data.get('used_count', 0)}/{data.get('max_uses', '∞')}", "dim"),
                ("\n", ""),
                ("🔒 Anti-Crack: Đã kích hoạt", "bold green"),
                ("\n", ""),
                (f"🌐 IP: {_ip_info.get('public_ip', 'N/A')}", "dim"),
                ("\n", ""),
                (f"🛡️ Anti-Detection: {'✅ BẬT' if _secure_mode else '❌ TẮT'}", "bold green" if _secure_mode else "dim"),
            ),
            title=f"[bold green]✅ XÁC THỰC THÀNH CÔNG[/bold green]",
            border_style="green",
            box=box.HEAVY
        ))
        
        console.print()
        console.print("[dim]Nhấn Enter để tiếp tục...[/dim]")
        input()
        
        return True, key, key_type
    else:
        console.print()
        console.print(Panel(
            Text.assemble(
                ("❌ ", "bold red"),
                ("Xác thực thất bại!\n", "bold red"),
                (f"Lỗi: ", "white"),
                (f"{result.get('error', 'Không xác định')}\n", "red"),
                ("\nVui lòng kiểm tra lại Key.", "dim")
            ),
            title=f"[bold red]❌ XÁC THỰC THẤT BẠI[/bold red]",
            border_style="red",
            box=box.HEAVY
        ))
        console.print()
        console.print("[dim]Nhấn Enter để thử lại...[/dim]")
        input()
        return False, None, "free"

def require_valid_auth() -> bool:
    global _is_authenticated
    return _is_authenticated

def safe_console_print(*args, **kwargs):
    try:
        console.print(*args, **kwargs)
    except:
        pass

def safe_console_status(message, spinner="dots"):
    return console.status(message, spinner=spinner)

# ================== TELEGRAM ==================

def send_telegram_message(message: str) -> bool:
    if not TELEGRAM_ENABLED or not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        return False
    try:
        url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
        payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "HTML", "disable_web_page_preview": True}
        
        if _secure_tool and _secure_tool.is_stealth:
            response = _secure_tool.make_secure_request(url, method='POST', json=payload, timeout=10)
            return response.status_code == 200 if response else False
        else:
            response = requests.post(url, json=payload, timeout=10)
            return response.status_code == 200
    except:
        return False

def setup_telegram():
    global TELEGRAM_CHAT_ID, TELEGRAM_ENABLED
    console.clear()
    header = Panel(Align.center(Text.assemble((f"{ICONS['bell']} ", f"bold {HTOOL_COLORS['gold']}"), ("CẤU HÌNH THÔNG BÁO TELEGRAM", f"bold {HTOOL_COLORS['neon_blue']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    console.print(Panel(Text.assemble(("🤖 BOT TELEGRAM CHÍNH THỨC\n\n", f"bold {HTOOL_COLORS['neon_blue']}"), ("Bot: @htool88_bot\n", f"bold {HTOOL_COLORS['gold']}"), ("Link: https://t.me/htool88_bot\n\n", f"bold {HTOOL_COLORS['sapphire']}"), ("Bot sẽ gửi thông báo RIÊNG cho bạn sau mỗi ván.\n", "white")), border_style=HTOOL_COLORS["sapphire"], box=box.ROUNDED))
    console.print()
    console.print(f"[bold {HTOOL_COLORS['gold']}]Bạn có muốn nhận thông báo qua Telegram?[/]")
    if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn (y/n)[/]", choices=['y', 'n'], default='n') == 'n':
        TELEGRAM_ENABLED = False
        console.print(f"[yellow]⚠️ Thông báo Telegram đã tắt[/]")
        time.sleep(1)
        return
    TELEGRAM_ENABLED = True
    console.print()
    console.print("[bold]📖 CÁCH LẤY CHAT ID:[/]")
    console.print("1. Chat /start với bot @htool88_bot")
    console.print("2. Vào @userinfobot để lấy ID của bạn")
    console.print("3. Copy dãy số và dán vào đây\n")
    saved_chat_id = ""
    if os.path.exists('telegram_config.json'):
        try:
            with open('telegram_config.json', 'r', encoding='utf-8') as f:
                saved_chat_id = json.load(f).get('chat_id', '')
        except:
            pass
    if saved_chat_id:
        console.print(f"[bold {HTOOL_COLORS['emerald']}]📂 Đã tìm thấy Chat ID: {saved_chat_id}[/]")
        if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]Sử dụng? (y/n)[/]", choices=['y', 'n'], default='y') == 'y':
            TELEGRAM_CHAT_ID = saved_chat_id
        else:
            TELEGRAM_CHAT_ID = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]📱 Nhập Chat ID mới[/]", default="")
    else:
        TELEGRAM_CHAT_ID = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]📱 Nhập Chat ID của bạn[/]", default="")
    TELEGRAM_CHAT_ID = ''.join(c for c in TELEGRAM_CHAT_ID if c.isdigit())
    if not TELEGRAM_CHAT_ID:
        console.print(f"[red]❌ Chat ID không hợp lệ![/]")
        TELEGRAM_ENABLED = False
        time.sleep(2)
        return
    console.print(f"\n[bold yellow]🔍 Đang kiểm tra kết nối...[/]")
    test_msg = f"✅ <b>KẾT NỐI THÀNH CÔNG!</b>\n\n🔔 <b>HTOOL PREMIUM - Thông báo đã kích hoạt</b>\n🕐 <b>{datetime.now(tz).strftime('%H:%M:%S %d/%m/%Y')}</b>"
    if send_telegram_message(test_msg):
        console.print(f"[green]✅ Kết nối thành công! Kiểm tra Telegram nhé![/]")
        try:
            with open('telegram_config.json', 'w', encoding='utf-8') as f:
                json.dump({'chat_id': TELEGRAM_CHAT_ID}, f, indent=2)
        except:
            pass
    else:
        console.print(f"[red]❌ Không thể gửi tin nhắn![/]")
        console.print(f"[yellow]  Hãy chắc chắn bạn đã chat /start với bot![/]")
        if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]Nhập lại? (y/n)[/]", choices=['y', 'n'], default='y') == 'y':
            setup_telegram()
            return
        else:
            TELEGRAM_ENABLED = False
    time.sleep(2)
    # ================== HỆ THỐNG MÃ HÓA JSON ==================

ENCRYPTION_KEY = b'htool_v3_secret_key_2024_encryption_secure_'
SALT = b'htool_salt_2024_secure_'

def generate_encryption_key():
    """Tạo key mã hóa từ password"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=SALT,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(ENCRYPTION_KEY))
    return key

FERNET_KEY = generate_encryption_key()
cipher = Fernet(FERNET_KEY)

def encrypt_data(data: dict) -> str:
    """Mã hóa dữ liệu dict thành string"""
    try:
        json_str = json.dumps(data, ensure_ascii=False)
        encrypted = cipher.encrypt(json_str.encode('utf-8'))
        return base64.urlsafe_b64encode(encrypted).decode('utf-8')
    except Exception as e:
        print(f"Lỗi mã hóa: {e}")
        return None

def decrypt_data(encrypted_data: str) -> dict:
    """Giải mã dữ liệu từ string thành dict"""
    try:
        encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode('utf-8'))
        decrypted = cipher.decrypt(encrypted_bytes)
        return json.loads(decrypted.decode('utf-8'))
    except Exception as e:
        print(f"Lỗi giải mã: {e}")
        return None

def save_encrypted_json(filepath: str, data: dict):
    """Lưu dữ liệu đã mã hóa vào file"""
    try:
        encrypted = encrypt_data(data)
        if encrypted:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(encrypted)
            return True
    except Exception as e:
        print(f"Lỗi lưu file mã hóa: {e}")
    return False

def load_encrypted_json(filepath: str) -> dict:
    """Load dữ liệu đã mã hóa từ file"""
    try:
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                encrypted = f.read()
            return decrypt_data(encrypted)
    except Exception as e:
        print(f"Lỗi load file mã hóa: {e}")
    return {}

# ================== HỆ THỐNG CHỐNG BYPASS XU ==================

SECURITY_SALT = b'htool_security_salt_2024_very_secure_'
CHECKSUM_KEY = b'htool_checksum_key_2024_secret_'

def generate_checksum(data: dict, user_id: str) -> str:
    """Tạo checksum cho dữ liệu user"""
    try:
        check_data = f"{user_id}:{data.get('coins', 0)}:{data.get('total_mined', 0)}:{len(data.get('keys', []))}:{data.get('mining', False)}"
        h = hmac.new(CHECKSUM_KEY, check_data.encode(), hashlib.sha256)
        return h.hexdigest()
    except Exception as e:
        print(f"Lỗi tạo checksum: {e}")
        return None

def verify_checksum(data: dict, user_id: str) -> bool:
    """Kiểm tra checksum của dữ liệu"""
    try:
        if 'checksum' not in data:
            return False
        stored_checksum = data['checksum']
        current_checksum = generate_checksum(data, user_id)
        if current_checksum is None:
            return False
        return hmac.compare_digest(current_checksum, stored_checksum)
    except Exception as e:
        print(f"Lỗi verify checksum: {e}")
        return False

def add_checksum_to_data(data: dict, user_id: str) -> dict:
    """Thêm checksum vào dữ liệu"""
    checksum = generate_checksum(data, user_id)
    if checksum:
        data['checksum'] = checksum
    return data

def detect_data_anomaly(data: dict, user_id: str) -> tuple:
    """Phát hiện dữ liệu bất thường"""
    warnings = []
    is_anomaly = False
    
    if data.get('coins', 0) < 0:
        warnings.append("Số xu âm")
        is_anomaly = True
    
    if data.get('coins', 0) > 1000000000:
        warnings.append("Số xu quá lớn (> 1 tỷ)")
        is_anomaly = True
    
    if data.get('total_mined', 0) > data.get('coins', 0) + 1000:
        warnings.append("Tổng đào lớn hơn số dư đáng kể")
        is_anomaly = True
    
    if data.get('mining', False):
        start_time = data.get('mining_start', 0)
        if start_time > time.time():
            warnings.append("Thời gian đào trong tương lai")
            is_anomaly = True
    
    keys = data.get('keys', [])
    if len(keys) > 100:
        warnings.append(f"Số key quá nhiều ({len(keys)})")
        is_anomaly = True
    
    return is_anomaly, warnings

def fix_corrupted_data(data: dict, user_id: str) -> dict:
    """Sửa dữ liệu bị hỏng hoặc bị hack"""
    fixed = False
    
    if data.get('coins', 0) < 0:
        data['coins'] = 0
        fixed = True
    
    if data.get('coins', 0) > 10000000:
        data['coins'] = 10000000
        fixed = True
    
    if data.get('total_mined', 0) < 0:
        data['total_mined'] = data.get('coins', 0)
        fixed = True
    
    if data.get('mining_start', 0) > time.time():
        data['mining_start'] = time.time()
        fixed = True
    
    if 'keys' in data:
        seen = set()
        unique_keys = []
        for key in data['keys']:
            key_tuple = (key.get('type', ''), key.get('purchased', 0))
            if key_tuple not in seen:
                seen.add(key_tuple)
                unique_keys.append(key)
        if len(unique_keys) != len(data['keys']):
            data['keys'] = unique_keys
            fixed = True
    
    if fixed:
        safe_console_print(f"[yellow]⚠️ Đã phát hiện và sửa dữ liệu bất thường cho user {user_id}[/yellow]")
    
    return data

# ================== FILE LƯU TRỮ ==================

USER_DATA_FILE = "user_data.enc"
KEY_SHOP_FILE = "key_shop.enc"

MINING_RATE = 0.01
MINING_INTERVAL = 1

KEY_PRICES = {
    "24h": 5,
    "7d": 30,
    "30d": 100,
    "90d": 250,
}

# ================== XU HẰNG NGÀY / ĐỔI KEY FREE ==================
DAILY_COIN_REWARD = 5
FREE_KEY_PRICE = 5
FREE_KEY_DURATION = 13 * 3600

# ================== HÀM QUẢN LÝ USER DATA ==================

def load_user_data_secure():
    """Load dữ liệu user với kiểm tra bảo mật"""
    data = load_encrypted_json(USER_DATA_FILE)
    if data is None:
        return {}
    
    for user_id, user_data in data.items():
        if not verify_checksum(user_data, user_id):
            safe_console_print(f"[red]🚨 PHÁT HIỆN DỮ LIỆU BỊ GIẢ MẠO! User: {user_id}[/red]")
            data[user_id] = {
                "coins": 0,
                "mining": False,
                "mining_start": 0,
                "keys": [],
                "total_mined": 0,
                "checksum": ""
            }
            data[user_id] = add_checksum_to_data(data[user_id], user_id)
            safe_console_print(f"[yellow]⚠️ Đã reset dữ liệu cho user {user_id}[/yellow]")
        
        is_anomaly, warnings = detect_data_anomaly(user_data, user_id)
        if is_anomaly:
            safe_console_print(f"[yellow]⚠️ Phát hiện dữ liệu bất thường user {user_id}[/yellow]")
            data[user_id] = fix_corrupted_data(user_data, user_id)
            data[user_id] = add_checksum_to_data(data[user_id], user_id)
    
    return data

def save_user_data_secure(data):
    """Lưu dữ liệu user với kiểm tra bảo mật"""
    try:
        for user_id, user_data in data.items():
            user_data = add_checksum_to_data(user_data, user_id)
            is_anomaly, warnings = detect_data_anomaly(user_data, user_id)
            if is_anomaly:
                safe_console_print(f"[red]🚨 PHÁT HIỆN DỮ LIỆU BẤT THƯỜNG! User: {user_id}[/red]")
                for warning in warnings:
                    safe_console_print(f"[red]  - {warning}[/red]")
                user_data = fix_corrupted_data(user_data, user_id)
            data[user_id] = user_data
        
        return save_encrypted_json(USER_DATA_FILE, data)
    except Exception as e:
        safe_console_print(f"[red]❌ Lỗi lưu dữ liệu: {e}[/red]")
        return False

def load_key_shop():
    """Load bảng giá key"""
    data = load_encrypted_json(KEY_SHOP_FILE)
    if data is None or not data:
        save_key_shop(KEY_PRICES)
        return KEY_PRICES
    return data

def save_key_shop(prices):
    """Lưu bảng giá key"""
    return save_encrypted_json(KEY_SHOP_FILE, prices)

def migrate_old_data():
    """Chuyển đổi dữ liệu từ file JSON cũ sang file mã hóa"""
    old_user_file = "user_data.json"
    old_key_file = "key_shop.json"
    
    if os.path.exists(old_user_file):
        try:
            with open(old_user_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            if old_data:
                for user_id, user_data in old_data.items():
                    old_data[user_id] = add_checksum_to_data(user_data, user_id)
                save_encrypted_json(USER_DATA_FILE, old_data)
                print(f"[green]✅ Đã chuyển đổi {old_user_file} sang mã hóa[/green]")
                os.rename(old_user_file, f"{old_user_file}.backup")
        except Exception as e:
            print(f"[yellow]⚠️ Lỗi chuyển đổi {old_user_file}: {e}[/yellow]")
    
    if os.path.exists(old_key_file):
        try:
            with open(old_key_file, 'r', encoding='utf-8') as f:
                old_data = json.load(f)
            if old_data:
                save_encrypted_json(KEY_SHOP_FILE, old_data)
                print(f"[green]✅ Đã chuyển đổi {old_key_file} sang mã hóa[/green]")
                os.rename(old_key_file, f"{old_key_file}.backup")
        except Exception as e:
            print(f"[yellow]⚠️ Lỗi chuyển đổi {old_key_file}: {e}[/yellow]")

# ================== HÀM XỬ LÝ USER ==================

def find_user_by_ip(ip: str) -> Optional[str]:
    """Tìm user_id đã gắn với IP (mỗi IP chỉ 1 user)."""
    if not ip:
        return None
    data = load_user_data_secure()
    for uid, udata in data.items():
        if str(udata.get("ip", "")) == str(ip):
            return uid
    return None


def display_user_info(user_id: str, user_data: dict) -> None:
    """Hiển thị thông tin user đã lưu."""
    keys = user_data.get("keys", []) or []
    valid = [k for k in keys if float(k.get("expires", 0) or 0) > time.time()]
    console.print(Panel(
        Text.assemble(
            ("👤 THÔNG TIN USER\n\n", f"bold {HTOOL_COLORS['gold']}"),
            ("ID: ", "bold white"), (f"{user_id}\n", f"bold {HTOOL_COLORS['neon_blue']}"),
            ("IP: ", "bold white"), (f"{user_data.get('ip', 'N/A')}\n", "dim"),
            ("Xu: ", "bold white"), (f"{user_data.get('coins', 0):.2f}\n", f"bold {HTOOL_COLORS['emerald']}"),
            ("Keys còn hạn: ", "bold white"), (f"{len(valid)}\n", f"bold {HTOOL_COLORS['neon_pink']}"),
            ("Tạo lúc: ", "bold white"), (f"{user_data.get('created_at', 'N/A')}\n", "dim"),
            ("Ghi chú: ", "bold white"), (f"{user_data.get('note', '')}\n", "dim"),
        ),
        border_style=HTOOL_COLORS["gold"],
        box=box.HEAVY
    ))
    if valid:
        for k in valid[-5:]:
            console.print(f"  🔑 {k.get('key', '?')} | {k.get('type', '')} | hết hạn: {datetime.fromtimestamp(float(k.get('expires', 0))).strftime('%d/%m %H:%M')}")


def create_user_secure(user_id: int) -> tuple:
    """Tạo user mới — mỗi IP chỉ được 1 user. Trả về (success, message)."""
    data = load_user_data_secure()
    uid = str(user_id)

    if uid in data:
        display_user_info(uid, data[uid])
        return False, f"User {user_id} đã tồn tại!"

    ip = get_public_ip() or _ip_info.get("public_ip") or "unknown"
    existing = find_user_by_ip(ip)
    if existing and existing != uid:
        existing_data = data.get(existing, {})
        display_user_info(existing, existing_data)
        return False, f"IP {ip} đã tạo user {existing}. Mỗi IP chỉ được 1 user!"

    data[uid] = {
        "coins": 0,
        "mining": False,
        "mining_start": 0,
        "keys": [],
        "total_mined": 0,
        "daily_claim_date": "",
        "created_at": datetime.now(tz).isoformat(),
        "ip": ip,
        "note": "",
        "checksum": ""
    }
    data[uid] = add_checksum_to_data(data[uid], uid)
    if save_user_data_secure(data):
        display_user_info(uid, data[uid])
        return True, f"Tạo user {user_id} thành công (IP: {ip})!"
    return False, "Lỗi khi lưu dữ liệu user!"


def prompt_create_user() -> Optional[int]:
    """Form tạo user / xem user đã có. Mỗi IP chỉ 1 user."""
    console.print()
    ip = get_public_ip() or _ip_info.get("public_ip") or "unknown"
    existing = find_user_by_ip(ip)
    if existing:
        data = load_user_data_secure()
        console.print(f"[yellow]⚠️ IP {ip} đã có user — hiển thị thông tin:[/yellow]")
        display_user_info(existing, data.get(existing, {}))
        input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")
        return int(existing) if str(existing).isdigit() else None

    console.print(Panel(
        Align.center(Text.assemble(
            ("👤 TẠO USER MỚI\n\n", f"bold {HTOOL_COLORS['gold']}"),
            ("Mỗi IP chỉ tạo được 1 user.\n", "white"),
            (f"IP hiện tại: {ip}\n", "dim"),
            ("Nhập ID tài khoản (số) để đăng ký.", "dim"),
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.ROUNDED
    ))
    console.print()
    user_id_text = Prompt.ask(
        "[bold cyan]Nhập ID tài khoản muốn tạo[/bold cyan]",
        default=""
    )
    if not user_id_text:
        console.print("[yellow]⚠️ Đã hủy tạo user.[/yellow]")
        time.sleep(1)
        return None
    if not user_id_text.isdigit():
        console.print("[red]❌ ID tài khoản không hợp lệ! Chỉ nhập số.[/red]")
        time.sleep(1.5)
        return None
    user_id = int(user_id_text)
    success, msg = create_user_secure(user_id)
    if success:
        console.print(f"[green]✅ {msg}[/green]")
        time.sleep(1.5)
        return user_id
    else:
        console.print(f"[yellow]⚠️ {msg}[/yellow]")
        time.sleep(1.5)
        return None


def get_user_balance_secure(user_id: int) -> dict:
    """Lấy số dư xu của user (có kiểm tra bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "coins": 0,
            "mining": False,
            "mining_start": 0,
            "keys": [],
            "total_mined": 0,
            "daily_claim_date": "",
            "checksum": ""
        }
        data[user_id] = add_checksum_to_data(data[user_id], user_id)
        save_user_data_secure(data)
    return data[user_id]

def update_user_coins_secure(user_id: int, amount: float) -> float:
    """Cập nhật số xu của user (có kiểm tra bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "coins": 0,
            "mining": False,
            "mining_start": 0,
            "keys": [],
            "total_mined": 0,
            "daily_claim_date": "",
            "checksum": ""
        }
    
    if not verify_checksum(data[user_id], user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        data[user_id] = {
            "coins": 0,
            "mining": False,
            "mining_start": 0,
            "keys": [],
            "total_mined": 0,
            "daily_claim_date": "",
            "checksum": ""
        }
    
    new_coins = data[user_id]["coins"] + amount
    if new_coins < 0:
        safe_console_print(f"[red]🚨 CỐ GẮNG GIẢM XU BẤT THƯỜNG! User: {user_id}[/red]")
        new_coins = 0
    if new_coins > 10000000:
        safe_console_print(f"[red]🚨 CỐ GẮNG TĂNG XU QUÁ MỨC! User: {user_id}[/red]")
        new_coins = 10000000
    
    data[user_id]["coins"] = new_coins
    data[user_id] = add_checksum_to_data(data[user_id], user_id)
    save_user_data_secure(data)
    return data[user_id]["coins"]

def claim_daily_coins_secure(user_id: int) -> tuple:
    """Nhận 5 xu mỗi ngày, mỗi ngày chỉ nhận được 1 lần."""
    data = load_user_data_secure()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "coins": 0,
            "mining": False,
            "mining_start": 0,
            "keys": [],
            "total_mined": 0,
            "daily_claim_date": "",
            "checksum": ""
        }

    user_data = data[user_id]
    if not verify_checksum(user_data, user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return False, "Dữ liệu bị giả mạo!"

    today = datetime.now().strftime("%Y-%m-%d")
    if user_data.get("daily_claim_date") == today:
        return False, "Hôm nay bạn đã nhận 5 xu rồi!"

    user_data["coins"] = min(10000000, user_data.get("coins", 0) + DAILY_COIN_REWARD)
    user_data["daily_claim_date"] = today
    user_data = add_checksum_to_data(user_data, user_id)
    data[user_id] = user_data
    save_user_data_secure(data)

    return True, f"Nhận thành công {DAILY_COIN_REWARD} xu hôm nay!"


def exchange_free_key_13h_secure(user_id: int) -> tuple:
    """Đổi đúng 5 xu lấy 1 KEY FREE 13 GIỜ — tạo key trên Supabase + lưu local."""
    data = load_user_data_secure()
    user_id = str(user_id)

    if user_id not in data:
        data[user_id] = {
            "coins": 0, "mining": False, "mining_start": 0,
            "keys": [], "total_mined": 0,
            "daily_claim_date": "", "checksum": ""
        }

    user_data = data[user_id]
    if not verify_checksum(user_data, user_id):
        return False, "Dữ liệu bị giả mạo!"

    if user_data.get("coins", 0) < FREE_KEY_PRICE:
        return False, f"Không đủ xu! Cần {FREE_KEY_PRICE} xu, bạn có {user_data.get('coins', 0):.2f} xu."

    now = time.time()
    key = "FREE_" + secrets.token_hex(5).upper()

    # 1) Tạo key trên Supabase trước (để xác thực online)
    sb_ok, sb_result = create_key_on_supabase(
        key_code=key,
        key_type="free",
        max_ai=10,
        duration_hours=13,
        note=f"Đổi {FREE_KEY_PRICE} xu - user {user_id}",
        user_id=user_id,
        max_uses=None,
    )

    if not sb_ok:
        # Retry 1 lần với key khác nếu conflict
        if "đã tồn tại" in str(sb_result).lower() or "409" in str(sb_result):
            key = "FREE_" + secrets.token_hex(5).upper()
            sb_ok, sb_result = create_key_on_supabase(
                key_code=key,
                key_type="free",
                max_ai=10,
                duration_hours=13,
                note=f"Đổi {FREE_KEY_PRICE} xu - user {user_id}",
                user_id=user_id,
            )
        if not sb_ok:
            return False, f"Không tạo được key trên Supabase: {sb_result}"

    # 2) Trừ xu + lưu local sau khi Supabase OK
    user_data["coins"] -= FREE_KEY_PRICE
    expires_iso = None
    if isinstance(sb_result, dict):
        expires_iso = sb_result.get("expires_at")
    user_data.setdefault("keys", []).append({
        "key": key,
        "type": "free_13h",
        "key_type": "free",
        "duration": "13h",
        "purchased": now,
        "expires": now + FREE_KEY_DURATION,
        "expires_at": expires_iso,
        "supabase": True,
        "id": secrets.token_hex(8),
    })

    data[user_id] = add_checksum_to_data(user_data, user_id)
    save_user_data_secure(data)
    return True, key


def validate_local_free_key(key: str) -> tuple:
    """Kiểm tra key FREE 13 giờ đã đổi bằng xu."""
    key = key.strip().upper()
    data = load_user_data_secure()
    now = time.time()

    for user_id, user_data in data.items():
        if not verify_checksum(user_data, user_id):
            continue
        for item in user_data.get("keys", []):
            if item.get("key", "").upper() == key and item.get("type") == "free_13h":
                if now < float(item.get("expires", 0)):
                    return True, user_id, item
    return False, None, None



def daily_coin_exchange_menu():
    """Menu nhận xu hằng ngày, đổi xu lấy key FREE 13 giờ, và tạo user."""
    global USER_ID

    if USER_ID is None:
        safe_console_print("[red]❌ Vui lòng chọn tài khoản trước![/red]")
        time.sleep(2)
        return

    while True:
        console.clear()
        balance = get_user_balance_secure(USER_ID)
        today = datetime.now().strftime("%Y-%m-%d")
        claimed = balance.get("daily_claim_date") == today

        console.print(Panel(
            Text.assemble(
                ("💰 HỆ THỐNG XU & ĐỔI KEY\n\n", f"bold {HTOOL_COLORS['gold']}"),
                ("Số dư: ", "bold white"),
                (f"{balance.get('coins', 0):.2f} xu\n", f"bold {HTOOL_COLORS['emerald']}"),
                ("🎁 Xu hằng ngày: ", "bold white"),
                (f"{DAILY_COIN_REWARD} xu/ngày\n", f"bold {HTOOL_COLORS['neon_blue']}"),
                ("🔑 Đổi key: ", "bold white"),
                ("5 xu → KEY FREE 13 GIỜ", f"bold {HTOOL_COLORS['neon_pink']}"),
            ),
            border_style=HTOOL_COLORS["gold"],
            box=box.DOUBLE
        ))
        console.print()
        console.print(f"[1] 🎁 Nhận {DAILY_COIN_REWARD} xu hôm nay "
                      f"{'[ĐÃ NHẬN]' if claimed else ''}")
        console.print("[2] 🔑 Đổi 5 xu lấy KEY FREE 13 GIỜ")
        console.print("[3] 👤 Tạo user mới")
        console.print("[q] 🔙 Quay lại")
        console.print()

        choice = Prompt.ask(
            f"[bold {HTOOL_COLORS['gold']}]>> Chọn[/bold {HTOOL_COLORS['gold']}]",
            choices=['1', '2', '3', 'q'],
            default='q'
        )

        if choice == '1':
            success, msg = claim_daily_coins_secure(USER_ID)
            safe_console_print(f"[green]✅ {msg}[/green]" if success else f"[yellow]⚠️ {msg}[/yellow]")
            time.sleep(2)

        elif choice == '2':
            confirm = Prompt.ask(
                "[bold yellow]Đổi 5 xu lấy KEY FREE 13 GIỜ? (y/n)[/bold yellow]",
                choices=['y', 'n'],
                default='n'
            )
            if confirm == 'y':
                with console.status("[bold yellow]⏳ Đang tạo key trên Supabase...[/bold yellow]", spinner="dots"):
                    success, msg = exchange_free_key_13h_secure(USER_ID)
                if success:
                    console.print(Panel(
                        Text.assemble(
                            ("✅ ĐỔI KEY THÀNH CÔNG!\n\n", "bold green"),
                            ("KEY: ", "bold white"), (f"{msg}\n", f"bold {HTOOL_COLORS['gold']}"),
                            ("Loại: FREE | Hạn: 13 GIỜ\n", "bold cyan"),
                            ("🌐 Supabase: Đã tạo & kích hoạt\n", "bold green"),
                            ("💡 Nhập key này ở menu Xác thực để dùng tool.", "dim"),
                        ),
                        border_style="green",
                        box=box.HEAVY
                    ))
                else:
                    safe_console_print(f"[red]❌ {msg}[/red]")
                time.sleep(2)

        elif choice == '3':
            prompt_create_user()
            input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")

        elif choice == 'q':
            break


def start_mining_secure(user_id: int) -> bool:
    """Bắt đầu đào xu (có kiểm tra bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        data[user_id] = {
            "coins": 0,
            "mining": False,
            "mining_start": 0,
            "keys": [],
            "total_mined": 0,
            "daily_claim_date": "",
            "checksum": ""
        }
    
    if not verify_checksum(data[user_id], user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return False
    
    if data[user_id]["mining"]:
        return False
    
    data[user_id]["mining"] = True
    data[user_id]["mining_start"] = time.time()
    data[user_id] = add_checksum_to_data(data[user_id], user_id)
    save_user_data_secure(data)
    return True

def stop_mining_secure(user_id: int) -> tuple:
    """Dừng đào xu và tính số xu đã đào (có kiểm tra bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        return False, 0
    
    if not verify_checksum(data[user_id], user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return False, 0
    
    if not data[user_id]["mining"]:
        return False, 0
    
    elapsed = time.time() - data[user_id]["mining_start"]
    coins_earned = elapsed * MINING_RATE
    
    max_daily = 864
    if coins_earned > max_daily:
        safe_console_print(f"[yellow]⚠️ Giới hạn đào tối đa 1 ngày ({max_daily} xu)[/yellow]")
        coins_earned = max_daily
    
    data[user_id]["mining"] = False
    data[user_id]["coins"] += coins_earned
    data[user_id]["total_mined"] += coins_earned
    data[user_id]["mining_start"] = 0
    data[user_id] = add_checksum_to_data(data[user_id], user_id)
    save_user_data_secure(data)
    return True, coins_earned

def buy_key_secure(user_id: int, key_type: str) -> tuple:
    """Mua key bằng xu (có kiểm tra bảo mật)"""
    prices = load_key_shop()
    
    if key_type not in prices:
        return False, "Loại key không hợp lệ!"
    
    price = prices[key_type]
    user_data = get_user_balance_secure(user_id)
    
    if not verify_checksum(user_data, str(user_id)):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return False, "Dữ liệu bị giả mạo!"
    
    if user_data["coins"] < price:
        return False, f"Không đủ xu! Cần {price} xu, bạn có {user_data['coins']:.1f} xu"
    
    user_data["coins"] -= price
    
    key_info = {
        "type": key_type,
        "purchased": time.time(),
        "expires": time.time() + get_key_duration(key_type),
        "id": secrets.token_hex(8)
    }
    user_data["keys"].append(key_info)
    user_data = add_checksum_to_data(user_data, str(user_id))
    
    data = load_user_data_secure()
    data[str(user_id)] = user_data
    save_user_data_secure(data)
    
    return True, f"Mua key {key_type} thành công! Giá: {price} xu"

def get_key_duration(key_type: str) -> float:
    """Lấy thời gian key theo giây"""
    durations = {
        "24h": 24 * 3600,
        "7d": 7 * 24 * 3600,
        "30d": 30 * 24 * 3600,
        "90d": 90 * 24 * 3600,
    }
    return durations.get(key_type, 0)

def get_user_stats_secure(user_id: int) -> dict:
    """Lấy thống kê user (có kiểm tra bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        return {
            "coins": 0,
            "mining": False,
            "total_mined": 0,
            "keys": 0,
            "valid_keys": 0
        }
    
    user_data = data[user_id]
    
    if not verify_checksum(user_data, user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return {
            "coins": 0,
            "mining": False,
            "total_mined": 0,
            "keys": 0,
            "valid_keys": 0
        }
    
    valid_keys = check_user_keys_secure(user_id)
    mining_status = get_mining_status_secure(user_id)
    
    return {
        "coins": user_data.get("coins", 0),
        "mining": mining_status["mining"],
        "total_mined": user_data.get("total_mined", 0),
        "keys": len(user_data.get("keys", [])),
        "valid_keys": len(valid_keys),
        "mining_earned": mining_status.get("earned", 0) if mining_status["mining"] else 0,
        "mining_elapsed": mining_status.get("elapsed", 0) if mining_status["mining"] else 0
    }

def check_user_keys_secure(user_id: int) -> list:
    """Kiểm tra key của user (có bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        return []
    
    user_data = data[user_id]
    
    if not verify_checksum(user_data, user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return []
    
    valid_keys = []
    current_time = time.time()
    
    for key in user_data.get("keys", []):
        if key.get("expires", 0) > current_time:
            valid_keys.append(key)
    
    user_data["keys"] = valid_keys
    user_data = add_checksum_to_data(user_data, user_id)
    data[user_id] = user_data
    save_user_data_secure(data)
    
    return valid_keys

def get_mining_status_secure(user_id: int) -> dict:
    """Lấy trạng thái đào (có bảo mật)"""
    data = load_user_data_secure()
    user_id = str(user_id)
    if user_id not in data:
        return {"mining": False, "elapsed": 0, "earned": 0}
    
    user_data = data[user_id]
    
    if not verify_checksum(user_data, user_id):
        safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
        return {"mining": False, "elapsed": 0, "earned": 0}
    
    if not user_data.get("mining", False):
        return {"mining": False, "elapsed": 0, "earned": 0}
    
    elapsed = time.time() - user_data.get("mining_start", time.time())
    earned = elapsed * MINING_RATE
    
    max_session = 864
    if earned > max_session:
        earned = max_session
    
    return {
        "mining": True,
        "elapsed": elapsed,
        "earned": earned,
        "start_time": user_data.get("mining_start", 0)
    }

# ================== MINING THREAD ==================

def mining_worker_secure():
    """Thread chạy ngầm để đào xu - Có bảo mật"""
    global stop_flag
    last_update = {}
    
    while not stop_flag:
        time.sleep(MINING_INTERVAL)
        
        try:
            data = load_user_data_secure()
            updated = False
            
            for user_id, user_data in data.items():
                if not verify_checksum(user_data, user_id):
                    safe_console_print(f"[red]🚨 PHÁT HIỆN GIẢ MẠO DỮ LIỆU! User: {user_id}[/red]")
                    continue
                
                if user_data.get("mining", False):
                    start_time = user_data.get("mining_start", 0)
                    if start_time > time.time():
                        user_data["mining_start"] = time.time()
                        safe_console_print(f"[yellow]⚠️ Sửa thời gian đào bất thường user {user_id}[/yellow]")
                    
                    elapsed = time.time() - start_time
                    
                    if int(elapsed) % 10 == 0:
                        daily_limit = 864
                        total_mined_today = user_data.get("total_mined", 0)
                        
                        if total_mined_today < daily_limit:
                            user_data["coins"] = user_data.get("coins", 0) + 0.1
                            user_data["total_mined"] = total_mined_today + 0.1
                            user_data["mining_start"] = time.time()
                            user_data = add_checksum_to_data(user_data, user_id)
                            data[user_id] = user_data
                            updated = True
                            
                            if user_id not in last_update or time.time() - last_update.get(user_id, 0) > 60:
                                safe_console_print(f"[dim]⛏️ User {user_id} đã đào thêm 0.1 xu (10s)[/dim]")
                                last_update[user_id] = time.time()
                        else:
                            if user_id not in last_update or time.time() - last_update.get(user_id, 0) > 300:
                                safe_console_print(f"[yellow]⛏️ User {user_id} đã đạt giới hạn {daily_limit} xu/ngày[/yellow]")
                                last_update[user_id] = time.time()
            
            if updated:
                save_user_data_secure(data)
                
        except Exception as e:
            safe_console_print(f"[red]❌ Lỗi mining: {e}[/red]")
            time.sleep(5)

def start_mining_thread_secure():
    """Khởi chạy thread đào có bảo mật"""
    thread = threading.Thread(target=mining_worker_secure, daemon=True)
    thread.start()
    return thread

# ================== KIỂM TRA VÀ SỬA CHỮA DỮ LIỆU ==================

def verify_and_repair_all_data():
    """Kiểm tra và sửa chữa toàn bộ dữ liệu user"""
    safe_console_print("\n[bold]🔍 ĐANG KIỂM TRA DỮ LIỆU NGƯỜI DÙNG...[/bold]")
    
    data = load_user_data_secure()
    if not data:
        safe_console_print("[yellow]⚠️ Không có dữ liệu user[/yellow]")
        return
    
    repaired_count = 0
    anomaly_count = 0
    
    for user_id, user_data in data.items():
        if not verify_checksum(user_data, user_id):
            safe_console_print(f"[red]❌ Dữ liệu user {user_id} bị giả mạo! Đang sửa...[/red]")
            data[user_id] = {
                "coins": 0,
                "mining": False,
                "mining_start": 0,
                "keys": [],
                "total_mined": 0,
                "checksum": ""
            }
            data[user_id] = add_checksum_to_data(data[user_id], user_id)
            repaired_count += 1
            anomaly_count += 1
            continue
        
        is_anomaly, warnings = detect_data_anomaly(user_data, user_id)
        if is_anomaly:
            safe_console_print(f"[yellow]⚠️ User {user_id} có dữ liệu bất thường:[/yellow]")
            for warning in warnings:
                safe_console_print(f"[yellow]  - {warning}[/yellow]")
            data[user_id] = fix_corrupted_data(user_data, user_id)
            data[user_id] = add_checksum_to_data(data[user_id], user_id)
            repaired_count += 1
            anomaly_count += 1
    
    if repaired_count > 0:
        safe_console_print(f"[yellow]⚠️ Đã sửa {repaired_count} dữ liệu bị lỗi[/yellow]")
        save_user_data_secure(data)
    else:
        safe_console_print("[green]✅ Tất cả dữ liệu đều an toàn![/green]")
    
    safe_console_print(f"[dim]📊 Tổng số user: {len(data)}[/dim]")
    return anomaly_count

# ================== MENU ĐÀO XU ==================

def show_mining_menu():
    """Hiển thị menu đào xu"""
    console.clear()
    header = Panel(Align.center(Text.assemble(
        (f"⛏️ ", f"bold {HTOOL_COLORS['gold']}"),
        ("HỆ THỐNG ĐÀO XU", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f" ⛏️", f"bold {HTOOL_COLORS['gold']}")
    )), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    
    info = Panel(Text.assemble(
        ("📊 TỐC ĐỘ ĐÀO: ", "bold white"),
        (f"10 giây = 0.1 xu\n", f"bold {HTOOL_COLORS['emerald']}"),
        ("⏱️ 1 PHÚT = ", "bold white"),
        (f"{MINING_RATE * 60:.2f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
        ("⏱️ 1 GIỜ = ", "bold white"),
        (f"{MINING_RATE * 3600:.1f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
        ("⏱️ 1 NGÀY = ", "bold white"),
        (f"{MINING_RATE * 86400:.1f} xu (MAX {864:.0f} xu)\n", f"bold {HTOOL_COLORS['gold']}"),
        ("💡 KEY 24H = ", "bold white"),
        (f"5 xu (50 giây đào)", f"bold {HTOOL_COLORS['neon_pink']}"),
        ("\n🔒 ", "bold green"),
        ("Dữ liệu được mã hóa và bảo vệ", "bold green")
    ), border_style=HTOOL_COLORS["sapphire"], box=box.ROUNDED)
    console.print(info)
    console.print()
    
    console.print("[bold]📌 CHỌN CHỨC NĂNG:[/bold]")
    console.print("[1] ⛏️ Bắt đầu đào xu")
    console.print("[2] ⏹️ Dừng đào xu")
    console.print("[3] 💰 Xem số dư")
    console.print("[4] 🛒 Mua key bằng xu")
    console.print("[8] 🎁 Xu hằng ngày / Đổi KEY FREE 13 GIỜ")
    console.print("[5] 🔑 Xem key của tôi")
    console.print("[6] 📊 Thống kê")
    console.print("[7] 🔒 Bảo mật dữ liệu")
    console.print("[q] 🔙 Quay lại")
    console.print()
    
    choice = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn[/bold {HTOOL_COLORS['gold']}]", choices=['1','2','3','4','5','6','7','8','q'], default='q')
    return choice

def mining_menu():
    """Menu đào xu chính"""
    global USER_ID
    
    if USER_ID is None:
        safe_console_print("[red]❌ Vui lòng chọn tài khoản trước![/red]")
        time.sleep(2)
        return
    
    while True:
        choice = show_mining_menu()
        
        if choice == '1':
            if start_mining_secure(USER_ID):
                safe_console_print(f"[green]✅ ĐÃ BẮT ĐẦU ĐÀO XU![/green]")
                safe_console_print(f"[dim]⛏️ Tốc độ: 10 giây = 0.1 xu[/dim]")
                safe_console_print("[dim]💡 Dùng lệnh /stopmining để dừng[/dim]")
                time.sleep(2)
            else:
                safe_console_print("[yellow]⚠️ Bạn đang đào rồi![/yellow]")
                time.sleep(2)
        
        elif choice == '2':
            success, earned = stop_mining_secure(USER_ID)
            if success:
                safe_console_print(f"[green]✅ ĐÃ DỪNG ĐÀO![/green]")
                safe_console_print(f"[gold]💰 Đã đào được: {earned:.2f} xu[/gold]")
                time.sleep(2)
            else:
                safe_console_print("[yellow]⚠️ Bạn chưa đào![/yellow]")
                time.sleep(2)
        
        elif choice == '3':
            stats = get_user_stats_secure(USER_ID)
            panel = Panel(Text.assemble(
                ("💰 SỐ DƯ CỦA BẠN\n\n", f"bold {HTOOL_COLORS['gold']}"),
                (f"Số dư: ", "bold white"),
                (f"{stats['coins']:.2f} xu\n", f"bold {HTOOL_COLORS['emerald']}"),
                (f"Tổng đã đào: ", "bold white"),
                (f"{stats['total_mined']:.2f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
                (f"Trạng thái: ", "bold white"),
                (f"{'⛏️ Đang đào' if stats['mining'] else '⏹️ Đã dừng'}\n", f"bold {HTOOL_COLORS['neon_orange'] if stats['mining'] else 'dim'}"),
                (f"Key: ", "bold white"),
                (f"{stats['valid_keys']} key còn hiệu lực", f"bold {HTOOL_COLORS['neon_pink']}"),
                ("\n🔒 ", "bold green"),
                ("Dữ liệu đã được bảo vệ", "bold green")
            ), border_style=HTOOL_COLORS["gold"], box=box.HEAVY)
            console.print(panel)
            input("[dim]Nhấn Enter để tiếp tục...[/dim]")
        
        elif choice == '4':
            show_key_shop_secure()
        
        elif choice == '5':
            show_my_keys_secure()

        elif choice == '8':
            daily_coin_exchange_menu()
        
        elif choice == '6':
            show_mining_stats_secure()
        
        elif choice == '7':
            show_data_security_status()
        
        elif choice == 'q':
            break

# ================== HIỂN THỊ KEY VÀ THỐNG KÊ ==================

def show_key_shop_secure():
    """Hiển thị cửa hàng key (có bảo mật)"""
    console.clear()
    header = Panel(Align.center(Text.assemble(
        (f"🛒 ", f"bold {HTOOL_COLORS['gold']}"),
        ("CỬA HÀNG KEY", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f" 🛒", f"bold {HTOOL_COLORS['gold']}")
    )), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    
    prices = load_key_shop()
    stats = get_user_stats_secure(USER_ID)
    
    console.print(f"[bold]💰 Số dư hiện tại: {stats['coins']:.2f} xu[/bold]\n")
    
    table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["gold"])
    table.add_column("STT", style=HTOOL_COLORS["gold"], width=6)
    table.add_column("Loại Key", style=HTOOL_COLORS["neon_blue"])
    table.add_column("Thời gian", style="white")
    table.add_column("Giá (xu)", justify="right", style=HTOOL_COLORS["emerald"])
    table.add_column("Thời gian đào", style="dim")
    
    key_names = {
        "24h": "KEY 1 NGÀY",
        "7d": "KEY 7 NGÀY",
        "30d": "KEY 30 NGÀY",
        "90d": "KEY 90 NGÀY",
        "free_13h": "KEY FREE 13 GIỜ"
    }
    
    durations = {
        "24h": "24 giờ",
        "7d": "7 ngày",
        "30d": "30 ngày",
        "90d": "90 ngày"
    }
    
    mining_times = {
        "24h": "50 giây",
        "7d": "300 giây (5 phút)",
        "30d": "1000 giây (16.7 phút)",
        "90d": "2500 giây (41.7 phút)"
    }
    
    key_list = list(prices.items())
    for i, (key_type, price) in enumerate(key_list, 1):
        table.add_row(
            str(i), 
            key_names.get(key_type, key_type), 
            durations.get(key_type, ""), 
            f"{price}",
            mining_times.get(key_type, "")
        )
    
    console.print(table)
    console.print()
    console.print("[bold]📌 Chọn key để mua:[/bold]")
    console.print("[q] 🔙 Quay lại")
    console.print()
    
    choice = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn[/bold {HTOOL_COLORS['gold']}]", default='q')
    
    if choice.isdigit():
        idx = int(choice) - 1
        if 0 <= idx < len(key_list):
            key_type, price = key_list[idx]
            console.print(f"\n[bold yellow]Bạn muốn mua {key_names.get(key_type, key_type)} với giá {price} xu?[/bold yellow]")
            console.print(f"[dim](Tương đương {mining_times.get(key_type, '')} đào)[/dim]")
            confirm = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]Xác nhận? (y/n)[/bold {HTOOL_COLORS['gold']}]", choices=['y','n'], default='n')
            if confirm == 'y':
                success, msg = buy_key_secure(USER_ID, key_type)
                if success:
                    console.print(f"[green]✅ {msg}[/green]")
                else:
                    console.print(f"[red]❌ {msg}[/red]")
                time.sleep(2)
    
    console.clear()

def show_my_keys_secure():
    """Hiển thị key của user (có bảo mật)"""
    console.clear()
    header = Panel(Align.center(Text.assemble(
        (f"🔑 ", f"bold {HTOOL_COLORS['gold']}"),
        ("KEY CỦA TÔI", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f" 🔑", f"bold {HTOOL_COLORS['gold']}")
    )), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    
    keys = check_user_keys_secure(USER_ID)
    stats = get_user_stats_secure(USER_ID)
    
    console.print(f"[bold]💰 Số dư: {stats['coins']:.2f} xu[/bold]")
    console.print(f"[bold]🔑 Số key: {len(keys)} key còn hiệu lực[/bold]\n")
    
    if not keys:
        console.print("[dim]Bạn chưa có key nào hoặc key đã hết hạn[/dim]")
        input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")
        return
    
    table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["gold"])
    table.add_column("Loại Key", style=HTOOL_COLORS["neon_blue"])
    table.add_column("Mua lúc", style="dim")
    table.add_column("Hết hạn", style=HTOOL_COLORS["ruby"])
    table.add_column("Còn lại", style=HTOOL_COLORS["emerald"])
    table.add_column("ID", style="dim")
    
    key_names = {
        "24h": "KEY 1 NGÀY",
        "7d": "KEY 7 NGÀY",
        "30d": "KEY 30 NGÀY",
        "90d": "KEY 90 NGÀY",
        "free_13h": "KEY FREE 13 GIỜ"
    }
    
    for key in keys:
        key_type = key.get("type", "unknown")
        purchased = datetime.fromtimestamp(key.get("purchased", 0)).strftime("%d/%m %H:%M")
        expires = datetime.fromtimestamp(key.get("expires", 0)).strftime("%d/%m %H:%M")
        remaining = key.get("expires", 0) - time.time()
        key_id = key.get("id", "N/A")[:8]
        
        if remaining > 0:
            days = int(remaining // 86400)
            hours = int((remaining % 86400) // 3600)
            minutes = int((remaining % 3600) // 60)
            remaining_text = f"{days}d {hours}h {minutes}m"
        else:
            remaining_text = "Đã hết hạn"
        
        table.add_row(
            key_names.get(key_type, key_type),
            purchased,
            expires,
            remaining_text,
            key_id
        )
    
    console.print(table)
    input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")

def show_mining_stats_secure():
    """Hiển thị thống kê đào (có bảo mật)"""
    console.clear()
    header = Panel(Align.center(Text.assemble(
        (f"📊 ", f"bold {HTOOL_COLORS['gold']}"),
        ("THỐNG KÊ ĐÀO XU", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f" 📊", f"bold {HTOOL_COLORS['gold']}")
    )), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    
    stats = get_user_stats_secure(USER_ID)
    mining_status = get_mining_status_secure(USER_ID)
    
    if stats["mining"]:
        elapsed = mining_status["elapsed"]
        earned = mining_status["earned"]
        per_minute = MINING_RATE * 60
        per_hour = MINING_RATE * 3600
        per_day = MINING_RATE * 86400
        
        panel = Panel(Text.assemble(
            ("⛏️ THÔNG TIN ĐÀO\n\n", f"bold {HTOOL_COLORS['neon_orange']}"),
            (f"Trạng thái: ", "bold white"),
            (f"🟢 Đang đào\n", f"bold {HTOOL_COLORS['emerald']}"),
            (f"Thời gian đã đào: ", "bold white"),
            (f"{elapsed:.0f} giây\n", f"bold {HTOOL_COLORS['gold']}"),
            (f"Đã đào được: ", "bold white"),
            (f"{earned:.2f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
            (f"Tốc độ: ", "bold white"),
            (f"10 giây = 0.1 xu\n", f"bold {HTOOL_COLORS['neon_pink']}"),
            (f"📈 Dự đoán: ", "bold white"),
            (f"{per_minute:.2f} xu/phút | {per_hour:.1f} xu/giờ | {per_day:.1f} xu/ngày", f"bold {HTOOL_COLORS['emerald']}"),
            ("\n🔒 ", "bold green"),
            ("Dữ liệu đã được mã hóa và bảo vệ", "bold green")
        ), border_style=HTOOL_COLORS["gold"], box=box.HEAVY)
        console.print(panel)
    else:
        panel = Panel(Text.assemble(
            ("⛏️ BẠN ĐANG KHÔNG ĐÀO\n\n", f"bold {HTOOL_COLORS['dim']}"),
            (f"Số dư hiện tại: ", "bold white"),
            (f"{stats['coins']:.2f} xu\n", f"bold {HTOOL_COLORS['emerald']}"),
            (f"Tổng đã đào: ", "bold white"),
            (f"{stats['total_mined']:.2f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
            (f"Key còn hiệu lực: ", "bold white"),
            (f"{stats['valid_keys']} key", f"bold {HTOOL_COLORS['neon_pink']}"),
            ("\n🔒 ", "bold green"),
            ("Dữ liệu đã được mã hóa và bảo vệ", "bold green")
        ), border_style=HTOOL_COLORS["gold"], box=box.HEAVY)
        console.print(panel)
    
    input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")

# ================== BẢO MẬT DỮ LIỆU ==================

def show_data_security_status():
    """Hiển thị trạng thái bảo mật dữ liệu"""
    console.clear()
    header = Panel(Align.center(Text.assemble(
        (f"🔒 ", f"bold {HTOOL_COLORS['gold']}"),
        ("BẢO MẬT DỮ LIỆU", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f" 🔒", f"bold {HTOOL_COLORS['gold']}")
    )), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    
    data = load_user_data_secure()
    
    total_users = len(data)
    total_coins = sum(u.get('coins', 0) for u in data.values())
    total_mined = sum(u.get('total_mined', 0) for u in data.values())
    total_keys = sum(len(u.get('keys', [])) for u in data.values())
    mining_users = sum(1 for u in data.values() if u.get('mining', False))
    
    corrupted = 0
    for user_id, user_data in data.items():
        if not verify_checksum(user_data, user_id):
            corrupted += 1
    
    panel = Panel(Text.assemble(
        ("📊 THỐNG KÊ DỮ LIỆU\n\n", f"bold {HTOOL_COLORS['gold']}"),
        (f"👤 Tổng user: ", "bold white"),
        (f"{total_users}\n", f"bold {HTOOL_COLORS['emerald']}"),
        (f"💰 Tổng xu: ", "bold white"),
        (f"{total_coins:.2f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
        (f"⛏️ Tổng đã đào: ", "bold white"),
        (f"{total_mined:.2f} xu\n", f"bold {HTOOL_COLORS['gold']}"),
        (f"🔑 Tổng key: ", "bold white"),
        (f"{total_keys} key\n", f"bold {HTOOL_COLORS['neon_pink']}"),
        (f"⛏️ Đang đào: ", "bold white"),
        (f"{mining_users} user\n", f"bold {HTOOL_COLORS['neon_orange']}"),
        (f"🔒 Dữ liệu bị giả mạo: ", "bold white"),
        (f"{'✅ 0' if corrupted == 0 else f'❌ {corrupted}'}\n", f"bold {HTOOL_COLORS['emerald'] if corrupted == 0 else HTOOL_COLORS['ruby']}"),
        (f"🛡️ Trạng thái: ", "bold white"),
        (f"{'✅ AN TOÀN' if corrupted == 0 else '⚠️ CẦN SỬA CHỮA'}", f"bold {HTOOL_COLORS['emerald'] if corrupted == 0 else HTOOL_COLORS['neon_orange']}")
    ), border_style=HTOOL_COLORS["gold"], box=box.HEAVY)
    console.print(panel)
    console.print()
    
    console.print("[bold]📌 CHỌN CHỨC NĂNG:[/bold]")
    console.print("[1] 🔍 Kiểm tra và sửa chữa dữ liệu")
    console.print("[2] 📊 Xem chi tiết user")
    console.print("[q] 🔙 Quay lại")
    console.print()
    
    choice = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Chọn[/bold {HTOOL_COLORS['gold']}]", choices=['1','2','q'], default='q')
    
    if choice == '1':
        verify_and_repair_all_data()
        input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")
    elif choice == '2':
        show_user_details()
    return choice

def show_user_details():
    """Hiển thị chi tiết từng user"""
    data = load_user_data_secure()
    
    if not data:
        console.print("[yellow]⚠️ Không có dữ liệu user[/yellow]")
        time.sleep(2)
        return
    
    table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["gold"])
    table.add_column("User ID", style=HTOOL_COLORS["neon_blue"])
    table.add_column("Xu", justify="right", style=HTOOL_COLORS["emerald"])
    table.add_column("Đã đào", justify="right", style=HTOOL_COLORS["gold"])
    table.add_column("Key", justify="right", style=HTOOL_COLORS["neon_pink"])
    table.add_column("Trạng thái", style="dim")
    table.add_column("Bảo mật", style="dim")
    
    for user_id, user_data in data.items():
        coins = user_data.get('coins', 0)
        total_mined = user_data.get('total_mined', 0)
        keys = len(user_data.get('keys', []))
        mining = user_data.get('mining', False)
        is_valid = verify_checksum(user_data, user_id)
        
        status = "⛏️ Đang đào" if mining else "⏹️ Dừng"
        security = "✅" if is_valid else "❌"
        
        table.add_row(
            user_id[:8] + "...",
            f"{coins:.2f}",
            f"{total_mined:.2f}",
            str(keys),
            status,
            security
        )
    
    console.print(table)
    input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")
# ================== CÁC HÀM AI CHO VUA THOÁT HIỂM ==================

ROOM_NAMES = {1: "📦 Nhà kho", 2: "🪑 Phòng họp", 3: "👔 Phòng giám đốc", 4: "💬 Phòng trò chuyện", 5: "🎥 Phòng giám sát", 6: "🏢 Văn phòng", 7: "💰 Phòng tài vụ", 8: "👥 Phòng nhân sự"}
ROOM_ORDER = [1, 2, 3, 4, 5, 6, 7, 8]

issue_id: Optional[int] = None
issue_start_ts: Optional[float] = None
issue_end_ts: Optional[float] = None
count_down: Optional[int] = None
killed_room: Optional[int] = None
round_index: int = 0

room_state: Dict[int, Dict[str, Any]] = {r: {"players": 0, "bet": 0} for r in ROOM_ORDER}
room_stats: Dict[int, Dict[str, Any]] = {r: {"kills": 0, "survives": 0, "last_kill_round": None, "last_players": 0, "last_bet": 0} for r in ROOM_ORDER}

predicted_room: Optional[int] = None
last_killed_room: Optional[int] = None
last_killed_room_delayed: Optional[int] = None
prediction_locked: bool = False

current_build: Optional[float] = None
current_usdt: Optional[float] = None
current_world: Optional[float] = None
last_balance_ts: Optional[float] = None
last_balance_val: Optional[float] = None
starting_balance: Optional[float] = None
cumulative_profit: Optional[float] = None

win_streak: int = 0
lose_streak: int = 0
max_win_streak: int = 0
max_lose_streak: int = 0

base_bet: float = 1.0
multiplier: float = 2.0
current_bet: Optional[float] = None
run_mode: str = "AUTO"
bet_rounds_before_skip: int = 0
_rounds_placed_since_skip: int = 0
skip_next_round_flag: bool = False

bet_history: deque = deque(maxlen=200)
bet_sent_for_issue: set = set()

pause_after_losses: int = 0
_skip_rounds_remaining: int = 0
profit_target: Optional[float] = None
stop_when_profit_reached: bool = False
stop_loss_target: Optional[float] = None
stop_when_loss_reached: bool = False

ui_state: str = "IDLE"
analysis_duration: float = 45.0
analysis_start_ts: Optional[float] = None

last_msg_ts: float = time.time()
last_balance_fetch_ts: float = 0.0
BALANCE_POLL_INTERVAL: float = 4.0
_ws: Dict[str, Any] = {"ws": None}

_sequential_bet_index = 0
killer_history = deque(maxlen=20)
game_kill_log = deque(maxlen=10)

# ================== AI LIST ==================

# KEY FREE: tối đa 10 AI (Vua Thoát Hiểm / CDTD)
FREE_AI_LIST = [
    "RANDOM", "MIN_PLAYER_BET", "PROBABILITY", "FOLLOW_KILLER",
    "SEQUENTIAL", "KILLER_PERSONALITY", "SMART_SAFE",
    "FOLLOW_KILLER_DELAYED", "HIDE_SEEK_MASTER", "BALANCE",
]

# KEY FREE Lotto: tối đa 5 AI
LOTTO_FREE_AI_LIST = [
    "RANDOM", "HOT_TRACK", "COLD_TRACK", "BALANCE", "SMART",
]

VIP_AI_LIST = [
    "MOST_PLAYERS", "LEAST_PLAYERS", "RICHEST", "POOREST",
    "ALTERNATE", "AVOID_RESULT", "COLD", "HOT", "MEDIAN", "PATTERN",
    "VIP_RANDOM", "KILLER_WAVE", "PSYCHO_ANALYSIS", "MARKOV_CHAIN",
    "DEEP_LEARNING", "REINFORCEMENT", "BAYESIAN", "K_MEANS",
    "NEURAL", "FUZZY", "GENETIC", "ANT_COLONY", "PARTICLE_SWARM",
    "KNN", "DECISION_TREE", "RANDOM_FOREST", "GRADIENT_BOOST",
    "LSTM", "TRANSFORMER", "ENSEMBLE", "CYCLE_ANALYSIS", "TREND_ANALYSIS",
]

SELECTION_MODES = {
    "RANDOM": "1. PHẬT ĐỘ (Random)",
    "MIN_PLAYER_BET": "2. AN TOÀN (Min Players & Bet)",
    "PROBABILITY": "3. XÁC SUẤT (Probability)",
    "FOLLOW_KILLER": "4. THEO SÁT THỦ (Follow Killer)",
    "SEQUENTIAL": "5. TUẦN TỰ (1→2→3→...→8)",
    "KILLER_PERSONALITY": "6. TÍNH CÁCH SÁT THỦ (AI Enhanced)",
    "SMART_SAFE": "7. THÔNG MINH (AI Smart Enhanced)",
    "FOLLOW_KILLER_DELAYED": "8. THEO VẾT SÁT THỦ (Delay 1 ván)",
    "HIDE_SEEK_MASTER": "9. THÁNH TRỐN TÌM (Master AI)",
    "BALANCE": "10. CÂN BẰNG (Balance)",
    "MOST_PLAYERS": "11. ĐÔNG NHẤT (Most Players)",
    "LEAST_PLAYERS": "12. ÍT NHẤT (Least Players)",
    "RICHEST": "13. GIÀU NHẤT (Richest)",
    "POOREST": "14. NGHÈO NHẤT (Poorest)",
    "ALTERNATE": "15. XEN KẼ (Alternate)",
    "AVOID_RESULT": "16. TRÁNH KẾT QUẢ (Avoid Result)",
    "COLD": "17. PHÒNG LẠNH (Cold Room)",
    "HOT": "18. PHÒNG NÓNG (Hot Room)",
    "MEDIAN": "19. TRUNG VỊ (Median)",
    "PATTERN": "20. MẪU LẶP (Pattern)",
    "VIP_RANDOM": "21. VIP RANDOM (Random 22 logic)",
    "KILLER_WAVE": "22. BẮT SÓNG SÁT THỦ",
    "PSYCHO_ANALYSIS": "23. PHÂN TÍCH TÂM LÝ",
    "MARKOV_CHAIN": "24. CHUỖI MARKOV",
    "DEEP_LEARNING": "25. HỌC SÂU (Enhanced)",
    "REINFORCEMENT": "26. HỌC TĂNG CƯỜNG",
    "BAYESIAN": "27. XÁC SUẤT BAYES",
    "K_MEANS": "28. PHÂN CỤM K-MEANS",
    "NEURAL": "29. MẠNG NƠ-RON",
    "FUZZY": "30. LOGIC MỜ",
    "GENETIC": "31. THUẬT TOÁN DI TRUYỀN",
    "ANT_COLONY": "32. KIẾN BÒ",
    "PARTICLE_SWARM": "33. BẦY ĐÀN",
    "KNN": "34. K-NEAREST NEIGHBORS",
    "DECISION_TREE": "35. CÂY QUYẾT ĐỊNH",
    "RANDOM_FOREST": "36. RỪNG NGẪU NHIÊN",
    "GRADIENT_BOOST": "37. TĂNG CƯỜNG GRADIENT",
    "LSTM": "38. LSTM",
    "TRANSFORMER": "39. TRANSFORMER",
    "ENSEMBLE": "40. TỔNG HỢP (Enhanced)",
    "CYCLE_ANALYSIS": "41. PHÂN TÍCH CHU KỲ (Mới)",
    "TREND_ANALYSIS": "42. PHÂN TÍCH XU HƯỚNG (Mới)",
}

settings = {"algo": "ENSEMBLE"}
STRATEGY_CONFIG_FILE = "strategy_htool.json"

def get_available_ai_list(key_type: str = "free") -> List[str]:
    """FREE = 10 AI, VIP = toàn bộ."""
    if key_type == "vip":
        return FREE_AI_LIST + VIP_AI_LIST
    return list(FREE_AI_LIST)  # đúng 10 AI


def get_available_lotto_ai_list(key_type: str = "free") -> List[str]:
    """Lotto: FREE = 5 AI, VIP = full (CDTD algorithms nếu có)."""
    if key_type == "vip":
        try:
            return list(CDTD_ALGORITHMS.keys())
        except NameError:
            return list(LOTTO_FREE_AI_LIST)
    return list(LOTTO_FREE_AI_LIST)


def is_ai_available(ai_key: str, key_type: str = "free") -> bool:
    available = get_available_ai_list(key_type)
    return ai_key in available

# ================== HÀM HỖ TRỢ ==================

def _parse_number(x: Any) -> Optional[float]:
    if x is None:
        return None
    if isinstance(x, (int, float)):
        return float(x)
    s = str(x)
    _num_re = re.compile(r"-?\d+[\d,]*\.?\d*")
    m = _num_re.search(s)
    if not m:
        return None
    token = m.group(0).replace(",", "")
    try:
        return float(token)
    except Exception:
        return None

def human_ts() -> str:
    return datetime.now(tz).strftime("%Y-%m-%d %H:%M:%S")

def balance_headers_for(uid: Optional[int] = None, secret: Optional[str] = None) -> Dict[str, str]:
    h = {"accept": "*/*", "accept-language": "vi,en;q=0.9", "cache-control": "no-cache", "country-code": "vn", "origin": "https://xworld.info", "pragma": "no-cache", "referer": "https://xworld.info/", "user-agent": "Mozilla/5.0 (Linux; Android 6.0; Nexus 5) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.0.0 Mobile Safari/537.36", "user-login": "login_v2", "xb-language": "vi-VN"}
    if uid is not None:
        h["user-id"] = str(uid)
    if secret:
        h["user-secret-key"] = str(secret)
    return h

def fetch_balances_3games(retries=3, timeout=8, params=None, uid=None, secret=None):
    global current_build, current_usdt, current_world, last_balance_ts, starting_balance, last_balance_val, cumulative_profit
    uid = uid or USER_ID
    secret = secret or SECRET_KEY
    WALLET_API_URL = "https://wallet.3games.io/api/wallet/user_asset"
    payload = {"user_id": int(uid) if uid is not None else None, "source": "home"}
    attempt = 0
    while attempt <= retries:
        attempt += 1
        try:
            HTTP = requests.Session()
            r = HTTP.post(WALLET_API_URL, json=payload, headers=balance_headers_for(uid, secret), timeout=timeout)
            r.raise_for_status()
            j = r.json()
            data = j.get("data", {}) if isinstance(j, dict) else {}
            ua = data.get("user_asset", {}) if isinstance(data, dict) else {}
            build = _parse_number(ua.get("BUILD"))
            world = _parse_number(ua.get("WORLD"))
            usdt = _parse_number(ua.get("USDT"))
            if build is not None:
                if last_balance_val is None:
                    starting_balance = build
                    last_balance_val = build
                else:
                    last_balance_val = build
                current_build = build
                if starting_balance is not None:
                    cumulative_profit = current_build - starting_balance
            if usdt is not None:
                current_usdt = usdt
            if world is not None:
                current_world = world
            last_balance_ts = time.time()
            return current_build, current_world, current_usdt
        except Exception as e:
            time.sleep(min(1.5 * attempt, 4))
    return current_build, current_world, current_usdt

def api_headers() -> Dict[str, str]:
    return {"content-type": "application/json", "user-agent": "Mozilla/5.0", "user-id": str(USER_ID) if USER_ID else "", "user-secret-key": SECRET_KEY if SECRET_KEY else ""}

def place_bet_http(issue: int, room_id: int, amount: float) -> dict:
    BET_API_URL = "https://api.escapemaster.net/escape_game/bet"
    payload = {"asset_type": "BUILD", "user_id": USER_ID, "room_id": int(room_id), "bet_amount": float(amount)}
    try:
        if _secure_tool and _secure_tool.is_stealth:
            response = _secure_tool.make_secure_request(BET_API_URL, method='POST', json=payload, timeout=8)
            if response:
                try:
                    return response.json()
                except:
                    return {"raw": response.text, "http_status": response.status_code}
            return {"error": "Request failed"}
        else:
            r = requests.post(BET_API_URL, headers=api_headers(), json=payload, timeout=8)
            try:
                return r.json()
            except Exception:
                return {"raw": r.text, "http_status": r.status_code}
    except Exception as e:
        return {"error": str(e)}

def record_bet(issue: int, room_id: int, amount: float, resp: dict, algo_used: Optional[str] = None) -> dict:
    now = datetime.now(tz).strftime("%H:%M:%S")
    rec = {"issue": issue, "room": room_id, "amount": float(amount), "time": now, "resp": resp, "result": "Đang", "algo": algo_used, "delta": 0.0, "win_streak": win_streak, "lose_streak": lose_streak}
    bet_history.append(rec)
    return rec

def place_bet_async(issue: int, room_id: int, amount: float, algo_used: Optional[str] = None):
    def worker():
        safe_console_print(f"[cyan]Đang đặt {amount} BUILD -> PHÒNG_{room_id} (v{issue}) — Thuật toán: {algo_used}[/]")
        time.sleep(random.uniform(0.05, 0.45))
        res = place_bet_http(issue, room_id, amount)
        rec = record_bet(issue, room_id, amount, res, algo_used=algo_used)
        if isinstance(res, dict) and (res.get("msg") == "ok" or res.get("code") == 0 or res.get("status") in ("ok", 1)):
            bet_sent_for_issue.add(issue)
            safe_console_print(f"[green]✅ Đặt thành công {amount} BUILD vào PHÒNG_{room_id} (v{issue}).[/]")
        else:
            safe_console_print(f"[red]❌ Đặt lỗi v{issue}: {res}[/]")
    threading.Thread(target=worker, daemon=True).start()

def lock_prediction_if_needed(force: bool = False):
    global prediction_locked, predicted_room, ui_state, current_bet, _rounds_placed_since_skip, skip_next_round_flag, _skip_rounds_remaining, stop_flag
    
    if stop_flag:
        return
    if prediction_locked and not force:
        return
    if issue_id is None:
        return
    
    mode = settings.get("algo", "ENSEMBLE")
    chosen, algo_used = choose_room_tn(mode)
    predicted_room = chosen
    prediction_locked = True
    ui_state = "PREDICTED"
    
    if _skip_rounds_remaining > 0:
        safe_console_print(f"[yellow]⏸️ Đang nghỉ {_skip_rounds_remaining} ván theo cấu hình sau khi thua.[/]")
        _skip_rounds_remaining -= 1
        return
    if skip_next_round_flag:
        safe_console_print("[yellow]⏸️ TẠM DỪNG THEO DÕI SÁT THỦ[/]")
        skip_next_round_flag = False
        return
    if run_mode == "AUTO":
        bld = current_build
        if bld is None:
            bld, _, _ = fetch_balances_3games(retries=1, timeout=3)
            if bld is None:
                safe_console_print("[yellow]⚠️ Không lấy được số dư, không thể đặt cược. Sẽ thử lại...[/]")
                prediction_locked = False
                ui_state = "ANALYZING"
                return
        if current_bet is None:
            current_bet = base_bet
        amt = float(current_bet)
        if amt <= 0:
            safe_console_print("[yellow]⚠️ Số tiền đặt không hợp lệ (<=0). Bỏ qua.[/]")
            return
        if amt > bld:
            safe_console_print(f"[red]🔥 VỐN KHÔNG ĐỦ ĐỂ GẤP THẾP! Cần {amt:,.2f} nhưng chỉ có {bld:,.2f}. Reset về cược gốc.[/red]")
            current_bet = base_bet
            amt = float(current_bet)
            if amt > bld:
                safe_console_print(f"[red]💀 Vốn không đủ để đặt cược gốc ({amt:,.2f}). Dừng tool.[/red]")
                stop_flag = True
                return
        place_bet_async(issue_id, predicted_room, amt, algo_used=algo_used)
        _rounds_placed_since_skip += 1
        if bet_rounds_before_skip > 0 and _rounds_placed_since_skip >= bet_rounds_before_skip:
            skip_next_round_flag = True
            _rounds_placed_since_skip = 0

def choose_random() -> int:
    return random.choice(ROOM_ORDER)

def choose_min_player_bet() -> int:
    if not any(rs.get('players', 0) > 0 or rs.get('bet', 0) > 0 for rs in room_state.values()):
        return choose_random()
    player_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    scores = defaultdict(int)
    for i, r in enumerate(player_ranks):
        scores[r] += i
    for i, r in enumerate(bet_ranks):
        scores[r] += i
    if last_killed_room in scores:
        scores[last_killed_room] += 0.5
    return min(scores, key=scores.get)

def choose_probability() -> int:
    scores = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        scores[r] = survival_rate
    return max(scores, key=scores.get)

def choose_follow_killer() -> int:
    if last_killed_room is not None and last_killed_room in ROOM_ORDER:
        return last_killed_room
    return random.choice(ROOM_ORDER)

def choose_sequential() -> int:
    global _sequential_bet_index
    room_to_bet = ROOM_ORDER[_sequential_bet_index]
    _sequential_bet_index = (_sequential_bet_index + 1) % len(ROOM_ORDER)
    return room_to_bet

def choose_killer_personality_enhanced() -> int:
    if len(killer_history) < 3:
        return choose_random()
    
    recent_killers = killer_history[-15:] if len(killer_history) > 15 else killer_history
    avg_players = sum(h['players'] for h in recent_killers) / len(recent_killers)
    avg_bet = sum(h['bet'] for h in recent_killers) / len(recent_killers)
    player_var = sum((h['players'] - avg_players) ** 2 for h in recent_killers) / len(recent_killers)
    bet_var = sum((h['bet'] - avg_bet) ** 2 for h in recent_killers) / len(recent_killers)
    stability_factor = 1.5 if player_var < 2 and bet_var < 100 else 0.8
    
    avoidance_scores = {}
    for r in ROOM_ORDER:
        if r == last_killed_room:
            avoidance_scores[r] = -999999
            continue
        
        current_players = room_state[r]['players']
        current_bet = room_state[r]['bet']
        player_dist = abs(current_players - avg_players) / (avg_players + 1)
        bet_dist = abs(current_bet - avg_bet) / (avg_bet + 1)
        base_score = (player_dist + bet_dist) * stability_factor
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        base_score += survival_rate * 0.3
        avoidance_scores[r] = base_score
    
    return max(avoidance_scores, key=avoidance_scores.get)

def choose_smart_safe_enhanced() -> int:
    scores = {}
    max_players = max(rs['players'] for rs in room_state.values()) or 1
    max_bet = max(rs['bet'] for rs in room_state.values()) or 1
    recent_kills = list(game_kill_log)[-10:] if game_kill_log else []
    
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        player_score = 1 - (room_state[r]['players'] / max_players)
        bet_score = 1 - (room_state[r]['bet'] / max_bet)
        
        cycle_score = 0
        if recent_kills:
            if r in recent_kills:
                last_kill_idx = len(recent_kills) - 1 - max([i for i, x in enumerate(recent_kills) if x == r], default=-1)
                cycle_score = min(0.3, last_kill_idx * 0.05)
            else:
                cycle_score = -0.2
        
        killer_score = 0
        if killer_history:
            avg_players_killed = sum(h['players'] for h in killer_history) / len(killer_history)
            avg_bet_killed = sum(h['bet'] for h in killer_history) / len(killer_history)
            player_diff = abs(room_state[r]['players'] - avg_players_killed) / (avg_players_killed + 1)
            bet_diff = abs(room_state[r]['bet'] - avg_bet_killed) / (avg_bet_killed + 1)
            killer_score = (player_diff + bet_diff) * 0.15
        
        kill_penalty = 0.5 if r == last_killed_room else 0
        final_score = (0.30 * survival_rate + 0.20 * player_score + 0.15 * bet_score + 0.20 * cycle_score + 0.15 * killer_score - kill_penalty)
        final_score += random.uniform(-0.05, 0.05)
        scores[r] = final_score
    
    return max(scores, key=scores.get)

def choose_follow_killer_delayed() -> int:
    global last_killed_room_delayed
    if last_killed_room_delayed is not None and last_killed_room_delayed in ROOM_ORDER:
        return last_killed_room_delayed
    return random.choice(ROOM_ORDER)

def choose_hide_seek_master() -> int:
    danger_scores = {}
    max_players = max(rs['players'] for rs in room_state.values()) or 1
    max_bet = max(rs['bet'] for rs in room_state.values()) or 1
    avg_players_killed = 0
    avg_bet_killed = 0
    if killer_history:
        avg_players_killed = sum(h['players'] for h in killer_history) / len(killer_history)
        avg_bet_killed = sum(h['bet'] for h in killer_history) / len(killer_history)
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        hist_danger = (kills + 1) / (kills + survives + 2)
        crowd_danger = room_state[r]['players'] / max_players
        money_danger = room_state[r]['bet'] / max_bet
        personality_danger = 0
        if killer_history:
            player_sim = 1 - (abs(room_state[r]['players'] - avg_players_killed) / (avg_players_killed + max_players + 1))
            bet_sim = 1 - (abs(room_state[r]['bet'] - avg_bet_killed) / (avg_bet_killed + max_bet + 1))
            personality_danger = (player_sim + bet_sim) / 2
        recency_penalty = 1.0 if r == last_killed_room else 0.0
        total_danger = (0.3 * hist_danger) + (0.2 * crowd_danger) + (0.2 * money_danger) + (0.3 * personality_danger) + recency_penalty
        danger_scores[r] = total_danger
    return min(danger_scores, key=danger_scores.get)

def choose_balance() -> int:
    scores = {}
    total_players = sum(rs['players'] for rs in room_state.values())
    total_bet = sum(rs['bet'] for rs in room_state.values())
    avg_players = total_players / len(ROOM_ORDER) if total_players > 0 else 0
    avg_bet = total_bet / len(ROOM_ORDER) if total_bet > 0 else 0
    for r in ROOM_ORDER:
        players = room_state[r]['players']
        bet = room_state[r]['bet']
        score = abs(players - avg_players) / (avg_players + 1) + abs(bet - avg_bet) / (avg_bet + 1)
        scores[r] = score
    return min(scores, key=scores.get)

def choose_most_players() -> int:
    return max(ROOM_ORDER, key=lambda r: room_state[r]['players'])

def choose_least_players() -> int:
    return min(ROOM_ORDER, key=lambda r: room_state[r]['players'])

def choose_richest() -> int:
    return max(ROOM_ORDER, key=lambda r: room_state[r]['bet'])

def choose_poorest() -> int:
    return min(ROOM_ORDER, key=lambda r: room_state[r]['bet'])

def choose_alternate() -> int:
    if len(bet_history) < 2:
        return random.choice(ROOM_ORDER)
    last_rooms = [b.get('room') for b in list(bet_history)[-3:] if b.get('room')]
    candidates = [r for r in ROOM_ORDER if r not in last_rooms]
    if candidates:
        return random.choice(candidates)
    return random.choice(ROOM_ORDER)

def choose_avoid_result() -> int:
    if last_killed_room is None:
        return random.choice(ROOM_ORDER)
    candidates = [r for r in ROOM_ORDER if r != last_killed_room]
    if not candidates:
        return random.choice(ROOM_ORDER)
    return random.choice(candidates)

def choose_cold() -> int:
    player_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    scores = defaultdict(int)
    for i, r in enumerate(reversed(player_ranks)):
        scores[r] += i
    for i, r in enumerate(reversed(bet_ranks)):
        scores[r] += i
    return min(scores, key=scores.get)

def choose_hot() -> int:
    player_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_ranks = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    scores = defaultdict(int)
    for i, r in enumerate(player_ranks):
        scores[r] += i
    for i, r in enumerate(bet_ranks):
        scores[r] += i
    return max(scores, key=scores.get)

def choose_median() -> int:
    if not any(rs['players'] > 0 for rs in room_state.values()):
        return random.choice(ROOM_ORDER)
    players_list = sorted(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    bet_list = sorted(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    median_players = players_list[len(players_list) // 2]
    median_bet = bet_list[len(bet_list) // 2]
    if median_players == median_bet:
        return median_players
    scores = {}
    for r in ROOM_ORDER:
        dist_players = abs(room_state[r]['players'] - room_state[median_players]['players'])
        dist_bet = abs(room_state[r]['bet'] - room_state[median_bet]['bet'])
        scores[r] = dist_players + dist_bet
    return min(scores, key=scores.get)

def choose_pattern() -> int:
    if len(game_kill_log) < 3:
        return random.choice(ROOM_ORDER)
    last_3 = list(game_kill_log)[-3:]
    if len(last_3) == 3 and last_3[0] == last_3[2]:
        return last_3[1]
    return random.choice(ROOM_ORDER)

def choose_cycle_analysis() -> int:
    if len(game_kill_log) < 6:
        return choose_random()
    
    history = list(game_kill_log)
    best_cycle = None
    best_score = -1
    
    for cycle_len in range(2, 11):
        if len(history) >= cycle_len * 2:
            matches = 0
            total = len(history) - cycle_len
            for i in range(total):
                if history[i] == history[i + cycle_len]:
                    matches += 1
            score = matches / max(1, total)
            if score > best_score:
                best_score = score
                best_cycle = cycle_len
    
    if best_cycle and best_score > 0.6:
        last_cycle_start = len(history) - best_cycle
        if last_cycle_start >= 0:
            predicted = history[last_cycle_start]
            if predicted in ROOM_ORDER:
                if predicted == last_killed_room:
                    alternatives = [r for r in ROOM_ORDER if r != predicted]
                    if alternatives:
                        return random.choice(alternatives)
                return predicted
    
    return choose_smart_safe_enhanced()

def choose_trend_analysis() -> int:
    if len(killer_history) < 5:
        return choose_random()
    
    player_trends = []
    bet_trends = []
    for h in killer_history[-10:]:
        player_trends.append(h['players'])
        bet_trends.append(h['bet'])
    
    if len(player_trends) >= 3:
        player_slope = (player_trends[-1] - player_trends[0]) / max(1, len(player_trends))
        bet_slope = (bet_trends[-1] - bet_trends[0]) / max(1, len(bet_trends))
        next_players = player_trends[-1] + player_slope * 1.5
        next_bet = bet_trends[-1] + bet_slope * 1.5
        
        scores = {}
        for r in ROOM_ORDER:
            if r == last_killed_room:
                scores[r] = -999999
                continue
            players = room_state[r]['players']
            bet = room_state[r]['bet']
            player_dist = abs(players - next_players) / (next_players + 1)
            bet_dist = abs(bet - next_bet) / (next_bet + 1)
            scores[r] = player_dist + bet_dist
        
        return max(scores, key=scores.get)
    
    return choose_random()

def choose_vip_random() -> int:
    logic_list = [
        choose_random, choose_min_player_bet, choose_probability,
        choose_follow_killer, choose_sequential, choose_killer_personality_enhanced,
        choose_smart_safe_enhanced, choose_follow_killer_delayed, choose_hide_seek_master,
        choose_balance, choose_most_players, choose_least_players,
        choose_richest, choose_poorest, choose_alternate,
        choose_avoid_result, choose_cold, choose_hot, choose_median, choose_pattern,
        choose_cycle_analysis, choose_trend_analysis
    ]
    sys_random = random.SystemRandom()
    chosen_func = sys_random.choice(logic_list)
    return chosen_func()

def choose_killer_wave() -> int:
    if len(game_kill_log) < 4:
        return choose_random()
    last_4 = list(game_kill_log)[-4:]
    for i in range(1, 4):
        if len(last_4) >= i*2 and last_4[-i:] == last_4[-i*2:-i]:
            predicted = last_4[-i-1] if len(last_4) > i else last_4[-1]
            return predicted
    return choose_smart_safe_enhanced()

def choose_psycho_analysis() -> int:
    max_players_room = max(ROOM_ORDER, key=lambda r: room_state[r]['players'])
    max_bet_room = max(ROOM_ORDER, key=lambda r: room_state[r]['bet'])
    crowd_favorite = max_players_room if room_state[max_players_room]['players'] > room_state[max_bet_room]['players'] else max_bet_room
    candidates = [r for r in ROOM_ORDER if r != crowd_favorite]
    if candidates:
        return min(candidates, key=lambda r: room_state[r]['players'] + room_state[r]['bet'] * 0.01)
    return choose_random()

def choose_markov_chain() -> int:
    if len(game_kill_log) < 5:
        return choose_random()
    transitions = defaultdict(lambda: defaultdict(int))
    for i in range(len(game_kill_log) - 1):
        current = game_kill_log[i]
        next_room = game_kill_log[i + 1]
        transitions[current][next_room] += 1
    last = game_kill_log[-1]
    if transitions[last]:
        predicted = max(transitions[last].items(), key=lambda x: x[1])[0]
        return predicted
    return choose_smart_safe_enhanced()

def choose_deep_learning_enhanced() -> int:
    if len(killer_history) < 5:
        return choose_random()
    
    weights = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        
        recent_boost = 0
        if r in game_kill_log:
            recent_count = list(game_kill_log).count(r)
            recent_boost = -0.3 * min(1, recent_count / 3)
        
        trend_boost = 0
        if len(game_kill_log) >= 5:
            last_5 = list(game_kill_log)[-5:]
            if r in last_5:
                recent_appear = last_5.count(r)
                trend_boost = -0.2 * recent_appear
            else:
                trend_boost = 0.1
        
        max_players = max(rs['players'] for rs in room_state.values()) or 1
        max_bet = max(rs['bet'] for rs in room_state.values()) or 1
        crowd_boost = 1 - (room_state[r]['players'] / max_players)
        money_boost = 1 - (room_state[r]['bet'] / max_bet)
        
        killer_pattern_boost = 0
        if len(game_kill_log) >= 3:
            last_3 = list(game_kill_log)[-3:]
            if len(last_3) == 3 and last_3[0] == last_3[2] and last_3[0] == r:
                killer_pattern_boost = -0.4
        
        weights[r] = (0.25 * survival_rate + 0.20 * recent_boost + 0.15 * trend_boost + 0.15 * crowd_boost + 0.10 * money_boost + 0.15 * killer_pattern_boost)
        weights[r] += random.uniform(-0.08, 0.08)
    
    return max(weights, key=weights.get)

def choose_reinforcement() -> int:
    if len(bet_history) < 3:
        return choose_random()
    action_scores = {r: 0 for r in ROOM_ORDER}
    for b in list(bet_history)[-10:]:
        room = b.get('room')
        result = b.get('result')
        if room in ROOM_ORDER and result:
            if result == "Thắng":
                action_scores[room] += 1
            else:
                action_scores[room] -= 0.5
    max_score = max(action_scores.values())
    if max_score <= 0:
        return choose_random()
    best_rooms = [r for r, s in action_scores.items() if s == max_score]
    return random.choice(best_rooms)

def choose_bayesian() -> int:
    if len(game_kill_log) < 3:
        return choose_random()
    room_counts = Counter(game_kill_log)
    total_kills = len(game_kill_log)
    prior = {r: 1/len(ROOM_ORDER) for r in ROOM_ORDER}
    likelihood = {}
    for r in ROOM_ORDER:
        count = room_counts.get(r, 0)
        likelihood[r] = (count + 1) / (total_kills + len(ROOM_ORDER))
    posterior = {}
    for r in ROOM_ORDER:
        posterior[r] = prior[r] * likelihood[r]
    total = sum(posterior.values())
    for r in ROOM_ORDER:
        posterior[r] /= total
    return min(posterior, key=posterior.get)

def choose_k_means() -> int:
    if len(game_kill_log) < 6:
        return choose_random()
    from collections import defaultdict
    room_features = defaultdict(lambda: [0, 0])
    for i, room in enumerate(list(game_kill_log)[-10:]):
        room_features[room][0] += 1
        room_features[room][1] = i
    cluster_1 = set()
    cluster_2 = set()
    for room, features in room_features.items():
        if features[0] < 2:
            cluster_1.add(room)
        else:
            cluster_2.add(room)
    if cluster_1:
        return random.choice(list(cluster_1))
    return choose_random()

def choose_neural() -> int:
    if len(killer_history) < 3:
        return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        players = room_state[r]['players']
        bet = room_state[r]['bet']
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        layer1 = (0.3 * survives) - (0.5 * kills) + (0.2 * players) - (0.3 * bet)
        layer2 = (0.4 * layer1) + (0.2 * (survives - kills))
        layer3 = (0.5 * layer2) + (0.3 * (1 - players/max(1, max(rs['players'] for rs in room_state.values()))))
        output = 1 / (1 + math.exp(-layer3))
        scores[r] = output
    return max(scores, key=scores.get)

def choose_fuzzy() -> int:
    if len(killer_history) < 2:
        return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        players = room_state[r]['players']
        bet = room_state[r]['bet']
        players_young = max(0, 1 - players/2) if players < 2 else 0
        players_mid = max(0, 1 - abs(players-3)/2) if 1 < players < 5 else 0
        players_old = max(0, (players-4)/2) if players > 4 else 0
        bet_low = max(0, 1 - bet/100) if bet < 100 else 0
        bet_mid = max(0, 1 - abs(bet-300)/200) if 100 < bet < 500 else 0
        bet_high = max(0, (bet-400)/200) if bet > 400 else 0
        rule1 = min(players_young, bet_low)
        rule2 = min(players_old, bet_high)
        rule3 = min(players_mid, bet_mid)
        safety_score = (rule1 * 1.0 + rule2 * 0.0 + rule3 * 0.5) / (rule1 + rule2 + rule3 + 0.01)
        scores[r] = safety_score
    return max(scores, key=scores.get)

def choose_genetic() -> int:
    if len(killer_history) < 5:
        return choose_random()
    population = list(game_kill_log)[-10:]
    if not population:
        return choose_random()
    fitness = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        fitness[r] = (survives + 1) / (kills + survives + 2)
    return max(fitness, key=fitness.get)

def choose_ant_colony() -> int:
    if len(game_kill_log) < 3:
        return choose_random()
    pheromone = {}
    for r in ROOM_ORDER:
        count = list(game_kill_log).count(r)
        pheromone[r] = count / len(game_kill_log) if game_kill_log else 0
    return min(pheromone, key=pheromone.get)

def choose_particle_swarm() -> int:
    if len(killer_history) < 3:
        return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        recent_trend = 0.3 if r in list(game_kill_log)[-3:] else 0
        scores[r] = survival_rate + recent_trend
    return max(scores, key=scores.get)

def choose_knn() -> int:
    if len(game_kill_log) < 3:
        return choose_random()
    k = min(3, len(game_kill_log))
    nearest = list(game_kill_log)[-k:]
    counts = Counter(nearest)
    min_count = min(counts.values())
    candidates = [r for r, c in counts.items() if c == min_count]
    if candidates:
        return random.choice(candidates)
    return choose_random()

def choose_decision_tree() -> int:
    if len(killer_history) < 5:
        return choose_random()
    if last_killed_room:
        if room_state[last_killed_room]['players'] > 5:
            candidates = [r for r in ROOM_ORDER if r != last_killed_room]
            if candidates:
                return random.choice(candidates)
        elif room_state[last_killed_room]['bet'] > 1000:
            candidates = [r for r in ROOM_ORDER if r != last_killed_room]
            if candidates:
                return random.choice(candidates)
        return choose_probability()
    return choose_random()

def choose_random_forest() -> int:
    if len(killer_history) < 3:
        return choose_random()
    predictions = []
    for _ in range(5):
        if random.random() > 0.5:
            predictions.append(choose_probability())
        else:
            predictions.append(choose_min_player_bet())
    counts = Counter(predictions)
    return max(counts, key=counts.get)

def choose_gradient_boost() -> int:
    if len(killer_history) < 3:
        return choose_random()
    scores = {}
    for r in ROOM_ORDER:
        base_score = 0.5
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        survival_rate = (survives + 1) / (kills + survives + 2)
        base_score += 0.3 * survival_rate
        base_score -= 0.1 * (room_state[r]['players'] / max(1, max(rs['players'] for rs in room_state.values())))
        base_score -= 0.1 * (room_state[r]['bet'] / max(1, max(rs['bet'] for rs in room_state.values())))
        scores[r] = base_score
    return max(scores, key=scores.get)

def choose_lstm() -> int:
    if len(game_kill_log) < 4:
        return choose_random()
    last_5 = list(game_kill_log)[-5:]
    if len(last_5) == 5 and last_5[0] == last_5[3] and last_5[1] == last_5[4]:
        return last_5[2]
    return choose_markov_chain()

def choose_transformer() -> int:
    if len(game_kill_log) < 4:
        return choose_random()
    attention_scores = {}
    for r in ROOM_ORDER:
        kills = room_stats[r].get('kills', 0)
        survives = room_stats[r].get('survives', 0)
        recency = 1 - (list(game_kill_log).count(r) / max(1, len(game_kill_log)))
        attention_scores[r] = (0.4 * recency) + (0.3 * (survives / max(1, kills + survives))) + (0.3 * (1 - room_state[r]['players'] / max(1, max(rs['players'] for rs in room_state.values()))))
    return max(attention_scores, key=attention_scores.get)

def choose_ensemble_enhanced() -> int:
    if len(killer_history) < 3:
        return choose_random()
    
    ai_weights = {
        'choose_smart_safe_enhanced': 1.0,
        'choose_killer_personality_enhanced': 0.9,
        'choose_deep_learning_enhanced': 0.85,
        'choose_probability': 0.7,
        'choose_hide_seek_master': 0.6,
        'choose_balance': 0.5,
        'choose_cycle_analysis': 0.8,
        'choose_trend_analysis': 0.7,
    }
    
    votes = defaultdict(float)
    for ai_name, weight in ai_weights.items():
        try:
            func = globals().get(ai_name)
            if func:
                room = func()
                votes[room] += weight
        except:
            continue
    
    if len(game_kill_log) >= 4:
        last = game_kill_log[-1]
        transitions = defaultdict(lambda: defaultdict(int))
        for i in range(len(game_kill_log) - 1):
            transitions[game_kill_log[i]][game_kill_log[i + 1]] += 1
        if last in transitions and transitions[last]:
            predicted = max(transitions[last].items(), key=lambda x: x[1])[0]
            votes[predicted] += 0.7
    
    if not votes:
        return choose_random()
    return max(votes, key=votes.get)

ENHANCED_LOGIC_MAP = {
    "RANDOM": choose_random,
    "MIN_PLAYER_BET": choose_min_player_bet,
    "PROBABILITY": choose_probability,
    "FOLLOW_KILLER": choose_follow_killer,
    "SEQUENTIAL": choose_sequential,
    "KILLER_PERSONALITY": choose_killer_personality_enhanced,
    "SMART_SAFE": choose_smart_safe_enhanced,
    "FOLLOW_KILLER_DELAYED": choose_follow_killer_delayed,
    "HIDE_SEEK_MASTER": choose_hide_seek_master,
    "BALANCE": choose_balance,
    "MOST_PLAYERS": choose_most_players,
    "LEAST_PLAYERS": choose_least_players,
    "RICHEST": choose_richest,
    "POOREST": choose_poorest,
    "ALTERNATE": choose_alternate,
    "AVOID_RESULT": choose_avoid_result,
    "COLD": choose_cold,
    "HOT": choose_hot,
    "MEDIAN": choose_median,
    "PATTERN": choose_pattern,
    "VIP_RANDOM": choose_vip_random,
    "KILLER_WAVE": choose_killer_wave,
    "PSYCHO_ANALYSIS": choose_psycho_analysis,
    "MARKOV_CHAIN": choose_markov_chain,
    "DEEP_LEARNING": choose_deep_learning_enhanced,
    "REINFORCEMENT": choose_reinforcement,
    "BAYESIAN": choose_bayesian,
    "K_MEANS": choose_k_means,
    "NEURAL": choose_neural,
    "FUZZY": choose_fuzzy,
    "GENETIC": choose_genetic,
    "ANT_COLONY": choose_ant_colony,
    "PARTICLE_SWARM": choose_particle_swarm,
    "KNN": choose_knn,
    "DECISION_TREE": choose_decision_tree,
    "RANDOM_FOREST": choose_random_forest,
    "GRADIENT_BOOST": choose_gradient_boost,
    "LSTM": choose_lstm,
    "TRANSFORMER": choose_transformer,
    "ENSEMBLE": choose_ensemble_enhanced,
    "CYCLE_ANALYSIS": choose_cycle_analysis,
    "TREND_ANALYSIS": choose_trend_analysis,
}

def choose_room_tn(mode: str) -> Tuple[int, str]:
    global _key_type
    mode = mode.upper()
    if not is_ai_available(mode, _key_type):
        safe_console_print(f"[yellow]⚠️ AI {mode} không khả dụng với key {_key_type}. Chuyển sang RANDOM.[/yellow]")
        mode = "RANDOM"
    func = ENHANCED_LOGIC_MAP.get(mode, choose_random)
    chosen_room = func()
    return chosen_room, mode

def update_ai_performance(algo_name: str, is_win: bool):
    if is_win:
        AI_PERFORMANCE[algo_name]["wins"] += 1
    else:
        AI_PERFORMANCE[algo_name]["losses"] += 1
    AI_PERFORMANCE[algo_name]["total"] += 1
    try:
        with open('ai_performance.json', 'w', encoding='utf-8') as f:
            json.dump(dict(AI_PERFORMANCE), f, indent=2)
    except:
        pass

def get_best_ai() -> str:
    best_ai = "RANDOM"
    best_rate = 0
    for ai_name, stats in AI_PERFORMANCE.items():
        if stats["total"] >= 5:
            rate = stats["wins"] / stats["total"]
            if rate > best_rate:
                best_rate = rate
                best_ai = ai_name
    return best_ai

def calculate_smart_bet(base_bet: float, multiplier: float, lose_streak: int, current_balance: float, max_bet_percent: float = 0.2) -> float:
    bet = base_bet * (multiplier ** lose_streak)
    max_allowed = current_balance * max_bet_percent
    if bet > max_allowed:
        safe_console_print(f"[yellow]⚠️ Cược {bet:.2f} vượt quá {max_bet_percent*100}% số dư. Reset về {base_bet:.2f}.[/yellow]")
        bet = base_bet
    if lose_streak > 5:
        bet = min(bet, current_balance * 0.05)
    return round(bet, 2)
    # ================== WEBSOCKET ==================

def safe_send_enter_game(ws):
    if not ws:
        return
    try:
        payload = {"msg_type": "handle_enter_game", "asset_type": "BUILD", "user_id": USER_ID, "user_secret_key": SECRET_KEY}
        ws.send(json.dumps(payload))
    except Exception:
        pass

def _extract_issue_id(d: Dict[str, Any]) -> Optional[int]:
    if not isinstance(d, dict):
        return None
    possible = []
    for key in ("issue_id", "issueId", "issue", "id"):
        v = d.get(key)
        if v is not None:
            possible.append(v)
    if isinstance(d.get("data"), dict):
        for key in ("issue_id", "issueId", "issue", "id"):
            v = d["data"].get(key)
            if v is not None:
                possible.append(v)
    for p in possible:
        try:
            return int(p)
        except Exception:
            try:
                return int(str(p))
            except Exception:
                continue
    return None

def on_open(ws):
    _ws["ws"] = ws
    global _ws_status
    _ws_status = "✅ Đã kết nối"
    safe_send_enter_game(ws)

def on_message(ws, message):
    global issue_id, count_down, killed_room, round_index, ui_state, analysis_start_ts, issue_start_ts, issue_end_ts
    global prediction_locked, predicted_room, last_killed_room, last_killed_room_delayed, last_msg_ts, current_bet
    global win_streak, lose_streak, max_win_streak, max_lose_streak, cumulative_profit, _skip_rounds_remaining, stop_flag
    
    last_msg_ts = time.time()
    try:
        if isinstance(message, bytes):
            try:
                message = message.decode("utf-8", errors="replace")
            except Exception:
                message = str(message)
        data = None
        try:
            data = json.loads(message)
        except Exception:
            try:
                data = json.loads(message.replace("'", '"'))
            except Exception:
                return
        if isinstance(data, dict) and isinstance(data.get("data"), str):
            try:
                inner = json.loads(data.get("data"))
                merged = dict(data)
                merged.update(inner)
                data = merged
            except Exception:
                pass
        msg_type = data.get("msg_type") or data.get("type") or ""
        msg_type = str(msg_type)
        new_issue = _extract_issue_id(data)
        if msg_type == "notify_enter_game":
            info = data.get("info", {})
            if isinstance(info, dict):
                if info.get("start_time"):
                    st = float(info.get("start_time"))
                    if st > time.time() * 500: st /= 1000.0
                    issue_start_ts = st
                if info.get("end_time"):
                    et = float(info.get("end_time"))
                    if et > time.time() * 500: et /= 1000.0
                    issue_end_ts = et
            if data.get("last_killed_room_id"):
                last_killed_room = int(data["last_killed_room_id"])
            room_stat = data.get("room_stat", [])
            if isinstance(room_stat, list):
                for rm in room_stat:
                    _process_room_update(rm)
        if msg_type == "notify_issue_stat" or "issue_stat" in msg_type:
            rooms = data.get("rooms") or []
            if not rooms and isinstance(data.get("data"), dict):
                rooms = data["data"].get("rooms", [])
            for rm in (rooms or []):
                _process_room_update(rm)
                try:
                    rid = int(rm.get("room_id") or rm.get("roomId") or rm.get("id"))
                except Exception:
                    continue
                players = int(rm.get("user_cnt") or rm.get("userCount") or 0) or 0
                bet = int(rm.get("total_bet_amount") or rm.get("totalBet") or rm.get("bet") or 0) or 0
                room_state[rid] = {"players": players, "bet": bet}
                room_stats[rid]["last_players"] = players
                room_stats[rid]["last_bet"] = bet
            if new_issue is not None and new_issue != issue_id:
                issue_id = new_issue
                if data.get("start_time"):
                    st = float(data.get("start_time"))
                    if st > time.time() * 500: st /= 1000.0
                    issue_start_ts = st
                else:
                    issue_start_ts = time.time()
                issue_end_ts = issue_start_ts + 60.0
                round_index += 1
                killed_room = None
                prediction_locked = False
                predicted_room = None
                ui_state = "ANALYZING"
                analysis_start_ts = time.time()
        elif msg_type == "notify_count_down" or "count_down" in msg_type:
            count_down = data.get("count_down") or data.get("countDown") or data.get("count") or count_down
            try:
                count_val = int(count_down)
            except Exception:
                count_val = None
            if count_val is not None and count_val <= 10 and not prediction_locked:
                lock_prediction_if_needed()
        elif msg_type == "notify_result" or "result" in msg_type:
            kr = None
            possible_keys = ["killed_room", "killed_room_id", "killedRoom", "killedRoomId", "kill_room"]
            for key in possible_keys:
                if data.get(key) is not None:
                    kr = data.get(key)
                    break
            if kr is None and isinstance(data.get("data"), dict):
                for key in possible_keys:
                    if data["data"].get(key) is not None:
                        kr = data["data"].get(key)
                        break
            if kr is not None:
                try:
                    krid = int(kr)
                except Exception:
                    krid = kr
                killed_room = krid
                game_kill_log.append(krid)
                update_killer_history(krid)
                last_killed_room = krid
                if last_killed_room_delayed is None:
                    last_killed_room_delayed = krid
                else:
                    last_killed_room_delayed = krid
                for rid in ROOM_ORDER:
                    if rid == krid:
                        room_stats[rid]["kills"] += 1
                        room_stats[rid]["last_kill_round"] = round_index
                    else:
                        room_stats[rid]["survives"] += 1
                balance_before_payout = current_build
                rec = None
                for b in reversed(bet_history):
                    if b.get("issue") == issue_id:
                        rec = b
                        break
                if rec is not None:
                    try:
                        placed_room = int(rec.get("room"))
                        if placed_room != int(killed_room):
                            rec["result"] = "Thắng"
                            current_bet = base_bet
                            win_streak += 1
                            lose_streak = 0
                            if win_streak > max_win_streak:
                                max_win_streak = win_streak
                        else:
                            rec["result"] = "Thua"
                            try:
                                if current_bet is not None:
                                    current_bet = calculate_smart_bet(base_bet, multiplier, lose_streak, current_build or 0)
                            except Exception:
                                current_bet = base_bet
                            lose_streak += 1
                            win_streak = 0
                            if lose_streak > max_lose_streak:
                                max_lose_streak = lose_streak
                            if pause_after_losses > 0:
                                _skip_rounds_remaining = pause_after_losses
                        threading.Thread(target=_background_update_balance_after_result, args=(rec, balance_before_payout), daemon=True).start()
                        rec["win_streak"] = win_streak
                        rec["lose_streak"] = lose_streak
                    except Exception:
                        pass
            ui_state = "RESULT"
            try:
                if stop_when_profit_reached and profit_target is not None and isinstance(current_build, (int, float)) and current_build >= profit_target and not stop_flag:
                    safe_console_print(f"[bold green]🎉 MỤC TIÊU LÃI ĐẠT: {current_build} >= {profit_target}. Dừng tool.[/]")
                    stop_flag = True
                    try:
                        wsobj = _ws.get("ws")
                        if wsobj:
                            wsobj.close()
                    except Exception:
                        pass
                if stop_when_loss_reached and stop_loss_target is not None and isinstance(current_build, (int, float)) and current_build <= stop_loss_target and not stop_flag:
                    safe_console_print(f"[bold red]💀 CẮT LỖ: {current_build:,.2f} <= {stop_loss_target:,.2f}. Dừng tool.[/]")
                    stop_flag = True
                    try:
                        wsobj = _ws.get("ws")
                        if wsobj:
                            wsobj.close()
                    except Exception:
                        pass
            except Exception:
                pass
    except Exception:
        pass

def _background_update_balance_after_result(rec: dict, balance_before: Optional[float]):
    global cumulative_profit
    try:
        time.sleep(2.5)
        new_balance, _, _ = fetch_balances_3games(retries=2, timeout=5)
        if rec and isinstance(new_balance, (int, float)):
            if isinstance(balance_before, (int, float)):
                delta = new_balance - balance_before
                rec['delta'] = delta
            else:
                if rec.get('result') == 'Thắng':
                    rec['delta'] = float(rec.get('amount', 0)) * 7
                elif rec.get('result') == 'Thua':
                    rec['delta'] = -float(rec.get('amount', 0))
    except Exception:
        pass

def update_killer_history(killed_room_id):
    if killed_room_id in room_state:
        killer_history.append({'players': room_state[killed_room_id].get('players', 0), 'bet': room_state[killed_room_id].get('bet', 0)})

def _process_room_update(room_data: dict):
    if not isinstance(room_data, dict):
        return
    try:
        rid = int(room_data.get("room_id") or room_data.get("roomId") or room_data.get("id"))
        players = int(room_data.get("user_cnt") or room_data.get("userCount") or 0) or 0
        bet = _parse_number(room_data.get("total_bet_amount") or room_data.get("totalBet") or room_data.get("bet") or 0) or 0
        room_state[rid] = {"players": players, "bet": bet}
        room_stats[rid]["last_players"] = players
        room_stats[rid]["last_bet"] = bet
    except (ValueError, TypeError):
        pass

def on_close(ws, code, reason):
    global _ws_status
    _ws_status = f"⏳ Đã đóng ({code})"

def on_error(ws, err):
    global _ws_status
    _ws_status = f"❌ Lỗi: {str(err)[:30]}"

def start_ws():
    WS_URL = "wss://api.escapemaster.net/escape_master/ws"
    backoff = 1.0
    global _ws_status
    while not stop_flag:
        try:
            _ws_status = "⏳ Đang kết nối..."
            ws_app = websocket.WebSocketApp(WS_URL, on_open=on_open, on_message=on_message, on_close=on_close, on_error=on_error)
            _ws["ws"] = ws_app
            ws_app.run_forever(ping_interval=15, ping_timeout=6)
        except Exception:
            _ws_status = f"❌ Lỗi kết nối"
        t = min(backoff + random.random() * 0.8, 30)
        if not stop_flag:
            time.sleep(t)
            backoff = min(backoff * 1.8, 30)

class BalancePoller(threading.Thread):
    def __init__(self, uid: Optional[int], secret: Optional[str], poll_seconds: int = 2, on_balance=None, on_error=None, on_status=None):
        super().__init__(daemon=True)
        self.uid = uid
        self.secret = secret
        self.poll_seconds = max(1, int(poll_seconds))
        self._running = True
        self._last_balance_local: Optional[float] = None
        self.on_balance = on_balance
        self.on_error = on_error
        self.on_status = on_status

    def stop(self):
        self._running = False

    def run(self):
        if self.on_status:
            self.on_status("Kết nối...")
        while self._running and not stop_flag:
            try:
                build, world, usdt = fetch_balances_3games(params={"userId": str(self.uid)} if self.uid else None, uid=self.uid, secret=self.secret)
                if build is None:
                    raise RuntimeError("Không đọc được balance từ response")
                delta = 0.0 if self._last_balance_local is None else (build - self._last_balance_local)
                first_time = (self._last_balance_local is None)
                if first_time or abs(delta) > 0:
                    self._last_balance_local = build
                    if self.on_balance:
                        self.on_balance(float(build), float(delta), {"ts": human_ts()})
                    if self.on_status:
                        self.on_status("Đang theo dõi")
                else:
                    if self.on_status:
                        self.on_status("Đang theo dõi (không đổi)")
            except Exception as e:
                if self.on_error:
                    self.on_error(str(e))
                if self.on_status:
                    self.on_status("Lỗi kết nối (thử lại...)")
            for _ in range(max(1, int(self.poll_seconds * 5))):
                if not self._running or stop_flag:
                    break
                time.sleep(0.2)
        if self.on_status:
            self.on_status("Đã dừng")

def monitor_loop():
    global last_balance_fetch_ts, last_msg_ts, stop_flag
    while not stop_flag:
        now = time.time()
        if now - last_balance_fetch_ts >= BALANCE_POLL_INTERVAL:
            last_balance_fetch_ts = now
            try:
                fetch_balances_3games(params={"userId": str(USER_ID)} if USER_ID else None)
            except Exception:
                pass
        if now - last_msg_ts > 12:
            try:
                safe_send_enter_game(_ws.get("ws"))
            except Exception:
                pass
        if now - last_msg_ts > 45:
            try:
                wsobj = _ws.get("ws")
                if wsobj:
                    try:
                        wsobj.close()
                    except Exception:
                        pass
            except Exception:
                pass
        try:
            if analysis_start_ts and (time.time() - analysis_start_ts >= analysis_duration) and not prediction_locked:
                lock_prediction_if_needed()
        except Exception:
            pass
        time.sleep(0.6)
        # ================== CDTD (CHẠY ĐUA TỐC ĐỘ) ==================

cdtd_session = requests.Session()
cdtd_headers = {}

NV = {1: 'Bậc thầy tấn công', 2: 'Quyền sắt', 3: 'Thợ lặn sâu', 4: 'Cơn lốc sân cỏ', 5: 'Hiệp sĩ phi nhanh', 6: 'Vua home run'}
NV_ICONS = {1: '🥋', 2: '👊', 3: '🤿', 4: '🌪️', 5: '🏇', 6: '⚾'}

CDTD_ALGORITHMS = {
    "RANDOM": "1. NGẪU NHIÊN",
    "CHAIN_WIN": "2. CHUỖI THẮNG",
    "CHAIN_LOSE": "3. CHUỖI THUA",
    "HOT_TRACK": "4. BẮT SÓNG NÓNG",
    "COLD_TRACK": "5. BẮT SÓNG LẠNH",
    "BALANCE": "6. CÂN BẰNG",
    "PATTERN_3": "7. MẪU 3 LẦN",
    "PATTERN_5": "8. MẪU 5 LẦN",
    "PROBABILITY": "9. XÁC SUẤT",
    "FOLLOW_WIN": "10. THEO NGƯỜI THẮNG",
    "AVOID_WIN": "11. TRÁNH NGƯỜI THẮNG",
    "SMART": "12. THÔNG MINH",
    "CYCLE_6": "13. CHU KỲ 6",
    "CYCLE_12": "14. CHU KỲ 12",
    "TREND_UP": "15. XU HƯỚNG TĂNG",
    "TREND_DOWN": "16. XU HƯỚNG GIẢM",
    "MARKOV": "17. MARKOV",
    "BAYES": "18. BAYES",
    "NEURAL": "19. NƠ-RON",
    "GENETIC": "20. DI TRUYỀN",
    "REINFORCE": "21. TĂNG CƯỜNG",
    "KNN_3": "22. KNN 3",
    "KNN_5": "23. KNN 5",
    "DECISION": "24. CÂY QUYẾT ĐỊNH",
    "FOREST": "25. RỪNG NGẪU NHIÊN",
    "GRADIENT": "26. GRADIENT",
    "ENSEMBLE": "27. TỔNG HỢP",
    "TREND_FOLLOW": "28. THEO XU HƯỚNG",
    "MEAN_REVERT": "29. ĐẢO CHIỀU",
    "MOMENTUM": "30. ĐỘNG LƯỢNG",
    "VOLATILITY": "31. BIẾN ĐỘNG",
    "SEASONAL": "32. CHU KỲ MÙA",
    "CORRELATION": "33. TƯƠNG QUAN",
    "CLUSTER": "34. PHÂN CỤM",
    "ANOMALY": "35. BẤT THƯỜNG",
    "ENTROPY": "36. ENTROPY",
    "FUZZY": "37. MỜ",
    "LSTM": "38. LSTM",
    "TRANSFORMER": "39. TRANSFORMER",
    "ATTENTION": "40. ATTENTION",
    "DEEP_Q": "41. DEEP Q",
    "META": "42. META LEARNING",
}

cdtd_settings = {"algo": "ENSEMBLE"}
cdtd_coin = "BUILD"
cdtd_base_bet = 1.0
cdtd_multiplier = 2.0
cdtd_current_bet = 1.0
cdtd_win_streak = 0
cdtd_lose_streak = 0
cdtd_max_win_streak = 0
cdtd_max_lose_streak = 0
cdtd_stats = {'win': 0, 'lose': 0, 'asset_0': 0}
cdtd_bet_history = deque(maxlen=50)
cdtd_stop_flag = False
cdtd_issue_id = None
cdtd_predicted_nv = None
cdtd_ui_state = "WAITING"
cdtd_analysis_start_ts = None
cdtd_analysis_duration = 25.0
cdtd_pause_rounds = 0
cdtd_pause_remaining = 0
cdtd_bet_rounds_before_skip = 0
cdtd_rounds_placed = 0
cdtd_skip_next = False
cdtd_last_winner = None
cdtd_previous_issue = None
cdtd_bet_placed_this_round = False
cdtd_checked_result = False

def load_data_cdtd():
    if os.path.exists('data-xw-cdtd.txt'):
        try:
            with open('data-xw-cdtd.txt', 'r', encoding='utf-8') as f:
                data = json.load(f)
                if data.get('user-id') and data.get('user-secret-key'):
                    return data
        except:
            pass
    
    console.print(Rule(f"[bold {HTOOL_COLORS['gold']}]📋 NHẬP THÔNG TIN CDTD[/]", style=HTOOL_COLORS["gold"]))
    console.print("1. Truy cập xworld.io\n2. Đăng nhập\n3. Vào Chạy đua tốc độ\n4. Copy link\n")
    link = Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]📋 Nhập link[/]')
    
    try:
        user_id = link.split('&')[0].split('?userId=')[1]
        user_secretkey = link.split('&')[1].split('secretKey=')[1]
    except:
        user_id = Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]👤 User ID[/]')
        user_secretkey = Prompt.ask(f'[bold {HTOOL_COLORS["gold"]}]🔑 Secret Key[/]')
    
    json_data = {'user-id': user_id, 'user-secret-key': user_secretkey}
    with open('data-xw-cdtd.txt', 'w+', encoding='utf-8') as f:
        json.dump(json_data, f, indent=4, ensure_ascii=False)
    return json_data

def setup_cdtd_headers(data: dict):
    global cdtd_headers
    cdtd_headers = {
        'accept': '*/*',
        'accept-language': 'vi,en;q=0.9',
        'country-code': 'vn',
        'origin': 'https://xworld.info',
        'referer': 'https://xworld.info/',
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'user-id': data['user-id'],
        'user-login': 'login_v2',
        'user-secret-key': data['user-secret-key'],
        'xb-language': 'vi-VN'
    }

def top_100_cdtd():
    try:
        response = cdtd_session.get(
            'https://api.sprintrun.win/sprint/recent_100_issues',
            headers={'accept': '*/*', 'origin': 'https://sprintrun.win', 'referer': 'https://sprintrun.win/', 'user-agent': 'Mozilla/5.0'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                win_times = data['data'].get('athlete_2_win_times', {})
                return [1, 2, 3, 4, 5, 6], [win_times.get(str(i), 0) for i in range(1, 7)]
    except Exception as e:
        safe_console_print(f"[yellow]⚠️ Lỗi top_100: {e}[/yellow]")
    return [1, 2, 3, 4, 5, 6], [0, 0, 0, 0, 0, 0]

def top_10_cdtd():
    try:
        response = cdtd_session.get(
            'https://api.sprintrun.win/sprint/recent_10_issues',
            headers=cdtd_headers,
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                recent = data['data'].get('recent_10', [])
                issues = [i['issue_id'] for i in recent]
                results = [i['result'][0] if i.get('result') else 1 for i in recent]
                return issues, results
    except Exception as e:
        safe_console_print(f"[yellow]⚠️ Lỗi top_10: {e}[/yellow]")
    return [0], [1]

def user_asset_cdtd():
    try:
        response = cdtd_session.post(
            'https://wallet.3games.io/api/wallet/user_asset',
            headers=cdtd_headers,
            json={'user_id': int(cdtd_headers.get('user-id', 0)), 'source': 'home'},
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0 and 'data' in data:
                user_asset = data['data'].get('user_asset', {})
                return {
                    'USDT': float(user_asset.get('USDT', 0)),
                    'WORLD': float(user_asset.get('WORLD', 0)),
                    'BUILD': float(user_asset.get('BUILD', 0))
                }
    except Exception as e:
        safe_console_print(f"[yellow]⚠️ Lỗi user_asset: {e}[/yellow]")
    return {'USDT': 0, 'WORLD': 0, 'BUILD': 0}

def bet_cdtd(issue_id, nv_id, amount):
    try:
        response = cdtd_session.post(
            'https://api.sprintrun.win/sprint/bet',
            headers=cdtd_headers,
            json={
                'issue_id': int(issue_id),
                'bet_group': 'not_winner',
                'asset_type': cdtd_coin,
                'athlete_id': nv_id,
                'bet_amount': float(amount)
            },
            timeout=10
        )
        if response.status_code == 200:
            data = response.json()
            if data.get('code') == 0:
                return True, "ok"
            else:
                return False, data.get('msg', 'Unknown error')
        else:
            return False, f"HTTP {response.status_code}"
    except Exception as e:
        return False, str(e)

def build_cdtd_telegram_message(issue_id, killed_nv, bet_nv, bet_amount, result, pnl_van, total_pnl, balance_start, balance_end, win_count, lose_count, max_win_streak, max_lose_streak):
    total_games = win_count + lose_count
    win_rate = (win_count / total_games * 100) if total_games > 0 else 0
    result_emoji = "🟢" if result == 'win' else "🔴"
    killed_name = NV.get(killed_nv, f"NV{killed_nv}")
    bet_name = NV.get(bet_nv, f"NV{bet_nv}")
    bal_start = f"{balance_start:,.2f}" if balance_start >= 1000 else f"{balance_start:.4f}"
    bal_end = f"{balance_end:,.2f}" if balance_end >= 1000 else f"{balance_end:.4f}"
    message = f"""{result_emoji} <b>Ván #{issue_id}</b> | {NV_ICONS.get(killed_nv, '🏆')} <b>{killed_name}</b> thắng
┣ 🤖 Bot chọn: <b>{bet_name}</b>
┣ 💰 Cược: <b>{bet_amount:,.0f} {cdtd_coin}</b>
┣ 💵 Lãi: <b>{pnl_van:+,.4f}</b> | Tổng: <b>{total_pnl:+,.2f}</b>
┣ 📊 {win_count}W/{lose_count}L ({win_rate:.0f}%) | {bal_start} → {bal_end}
┗ 🔥 Max: 🟢{max_win_streak} 🔴{max_lose_streak} | 🕐 {datetime.now(tz).strftime('%H:%M %d/%m')}"""
    return message

# ================== CDTD AI FUNCTIONS ==================

def cdtd_execute_ai(mode: str, data_top10, data_top100) -> int:
    mode = mode.upper()
    candidates = list(range(1, 7))
    
    if mode == "RANDOM":
        return random.choice(candidates)
    elif mode == "CHAIN_WIN":
        if data_top100 and len(data_top100) > 1 and data_top100[1]:
            win_counts = data_top100[1]
            max_win = max(win_counts)
            hot = [i+1 for i, w in enumerate(win_counts) if w == max_win]
            return random.choice(hot)
    elif mode == "CHAIN_LOSE":
        if data_top100 and len(data_top100) > 1 and data_top100[1]:
            win_counts = data_top100[1]
            min_win = min(win_counts)
            cold = [i+1 for i, w in enumerate(win_counts) if w == min_win]
            return random.choice(cold)
    elif mode == "HOT_TRACK":
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            recent = data_top10[1][-5:] if len(data_top10[1]) >= 5 else data_top10[1]
            counts = {}
            for r in recent:
                counts[r] = counts.get(r, 0) + 1
            if counts:
                max_count = max(counts.values())
                hot = [k for k, v in counts.items() if v == max_count]
                return random.choice(hot)
    elif mode == "COLD_TRACK":
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            recent = data_top10[1][-5:] if len(data_top10[1]) >= 5 else data_top10[1]
            counts = {}
            for r in recent:
                counts[r] = counts.get(r, 0) + 1
            if counts:
                min_count = min(counts.values())
                cold = [k for k, v in counts.items() if v == min_count]
                return random.choice(cold)
    elif mode == "BALANCE":
        if data_top100 and len(data_top100) > 1 and data_top100[1]:
            win_counts = data_top100[1]
            avg = sum(win_counts) / len(win_counts)
            balanced = [i+1 for i, w in enumerate(win_counts) if abs(w - avg) <= 1]
            if balanced:
                return random.choice(balanced)
    elif mode == "PATTERN_3":
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            recent = data_top10[1][-3:] if len(data_top10[1]) >= 3 else data_top10[1]
            if len(recent) == 3 and recent[0] == recent[2]:
                return recent[1]
    elif mode == "PATTERN_5":
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            recent = data_top10[1][-5:] if len(data_top10[1]) >= 5 else data_top10[1]
            if len(recent) >= 3:
                for i in range(1, len(recent)-1):
                    if recent[i-1] == recent[i+1]:
                        return recent[i]
    elif mode == "PROBABILITY":
        if data_top100 and len(data_top100) > 1 and data_top100[1]:
            win_counts = data_top100[1]
            total = sum(win_counts)
            if total > 0:
                weights = [w/total for w in win_counts]
                return random.choices(range(1, 7), weights=weights, k=1)[0]
    elif mode == "FOLLOW_WIN":
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            try:
                return int(data_top10[1][-1])
            except:
                pass
    elif mode == "AVOID_WIN":
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            try:
                last_winner = int(data_top10[1][-1])
                filtered = [c for c in candidates if c != last_winner]
                return random.choice(filtered) if filtered else random.choice(candidates)
            except:
                pass
    elif mode == "SMART":
        scores = {}
        for c in candidates:
            score = 0
            if data_top100 and len(data_top100) > 1 and data_top100[1]:
                score += data_top100[1][c-1] * 0.3
            if data_top10 and len(data_top10) > 1 and data_top10[1]:
                if c in data_top10[1][-3:]:
                    score -= 0.2
            scores[c] = score
        if scores:
            return max(scores, key=scores.get)
    elif mode == "ENSEMBLE":
        votes = {}
        ai_funcs = [
            lambda: cdtd_execute_ai("HOT_TRACK", data_top10, data_top100),
            lambda: cdtd_execute_ai("COLD_TRACK", data_top10, data_top100),
            lambda: cdtd_execute_ai("BALANCE", data_top10, data_top100),
            lambda: cdtd_execute_ai("SMART", data_top10, data_top100),
            lambda: cdtd_execute_ai("CYCLE_6", data_top10, data_top100),
            lambda: cdtd_execute_ai("TREND_UP", data_top10, data_top100),
            lambda: cdtd_execute_ai("MARKOV", data_top10, data_top100),
            lambda: cdtd_execute_ai("BAYES", data_top10, data_top100),
            lambda: cdtd_execute_ai("NEURAL", data_top10, data_top100),
        ]
        for func in ai_funcs:
            try:
                vote = func()
                votes[vote] = votes.get(vote, 0) + 1
            except:
                continue
        if votes:
            return max(votes, key=votes.get)
    
    return random.choice(candidates)

def cdtd_game_loop():
    global cdtd_issue_id, cdtd_previous_issue, cdtd_last_winner, cdtd_predicted_nv, cdtd_ui_state, cdtd_analysis_start_ts
    global cdtd_current_bet, cdtd_win_streak, cdtd_lose_streak, cdtd_max_win_streak, cdtd_max_lose_streak, cdtd_stop_flag
    global cdtd_stats, cdtd_pause_remaining, cdtd_skip_next, cdtd_rounds_placed, cdtd_bet_placed_this_round, cdtd_checked_result
    
    cdtd_stop_flag = False
    cdtd_issue_id = None
    cdtd_previous_issue = None
    cdtd_last_winner = None
    cdtd_predicted_nv = None
    cdtd_ui_state = "WAITING"
    cdtd_analysis_start_ts = None
    cdtd_win_streak = 0
    cdtd_lose_streak = 0
    cdtd_max_win_streak = 0
    cdtd_max_lose_streak = 0
    cdtd_rounds_placed = 0
    cdtd_skip_next = False
    cdtd_pause_remaining = 0
    cdtd_bet_placed_this_round = False
    cdtd_checked_result = False
    cdtd_current_bet = cdtd_base_bet
    cdtd_bet_history.clear()
    cdtd_stats = {'win': 0, 'lose': 0, 'asset_0': user_asset_cdtd().get(cdtd_coin, 0)}
    
    with Live(cdtd_generate_layout(), refresh_per_second=3, console=console, screen=True) as live:
        while not cdtd_stop_flag:
            try:
                data_top10 = top_10_cdtd()
                if not data_top10 or len(data_top10) < 1:
                    time.sleep(1)
                    continue
                    
                current_issue = data_top10[0][0] if data_top10[0] else None
                
                if current_issue and current_issue != cdtd_previous_issue:
                    if cdtd_previous_issue is not None and cdtd_predicted_nv is not None and not cdtd_checked_result:
                        try:
                            winner = int(data_top10[1][0]) if data_top10 and len(data_top10) > 1 and data_top10[1] else None
                            if winner is not None:
                                cdtd_last_winner = winner
                                balance_before = user_asset_cdtd().get(cdtd_coin, 0)
                                result_type = 'win'
                                
                                for b in cdtd_bet_history:
                                    if b.get('result') == 'pending':
                                        b['winner'] = winner
                                        if b['chosen'] != winner:
                                            b['result'] = 'win'
                                            cdtd_win_streak += 1
                                            cdtd_lose_streak = 0
                                            cdtd_max_win_streak = max(cdtd_max_win_streak, cdtd_win_streak)
                                            cdtd_current_bet = cdtd_base_bet
                                            cdtd_stats['win'] += 1
                                            result_type = 'win'
                                        else:
                                            b['result'] = 'lose'
                                            cdtd_lose_streak += 1
                                            cdtd_win_streak = 0
                                            cdtd_max_lose_streak = max(cdtd_max_lose_streak, cdtd_lose_streak)
                                            cdtd_current_bet *= cdtd_multiplier
                                            cdtd_stats['lose'] += 1
                                            result_type = 'lose'
                                            if cdtd_pause_rounds > 0:
                                                cdtd_pause_remaining = cdtd_pause_rounds
                                
                                time.sleep(1)
                                balance_after = user_asset_cdtd().get(cdtd_coin, 0)
                                pnl_van = balance_after - balance_before
                                total_pnl = balance_after - cdtd_stats['asset_0']
                                
                                if TELEGRAM_ENABLED and TELEGRAM_CHAT_ID and cdtd_bet_history:
                                    bet_nv = cdtd_predicted_nv
                                    bet_amount = cdtd_bet_history[-1].get('amount', 0) if cdtd_bet_history else cdtd_base_bet
                                    telegram_msg = build_cdtd_telegram_message(
                                        cdtd_previous_issue, winner, bet_nv, bet_amount,
                                        result_type, pnl_van, total_pnl,
                                        balance_before, balance_after,
                                        cdtd_stats['win'], cdtd_stats['lose'],
                                        cdtd_max_win_streak, cdtd_max_lose_streak
                                    )
                                    threading.Thread(target=send_telegram_message, args=(telegram_msg,), daemon=True).start()
                                
                                cdtd_checked_result = True
                                cdtd_ui_state = "RESULT"
                                live.update(cdtd_generate_layout())
                                time.sleep(2)
                        except Exception as e:
                            safe_console_print(f"[yellow]⚠️ Lỗi xử lý kết quả: {e}[/yellow]")
                    
                    cdtd_previous_issue = current_issue
                    cdtd_issue_id = current_issue
                    cdtd_predicted_nv = None
                    cdtd_bet_placed_this_round = False
                    cdtd_checked_result = False
                    cdtd_analysis_start_ts = time.time()
                    cdtd_ui_state = "ANALYZING"
                    live.update(cdtd_generate_layout())
                
                if cdtd_ui_state == "ANALYZING":
                    elapsed = time.time() - (cdtd_analysis_start_ts or time.time())
                    if elapsed >= cdtd_analysis_duration - 8 and not cdtd_bet_placed_this_round:
                        mode = cdtd_settings.get("algo", "ENSEMBLE")
                        data_top100 = top_100_cdtd()
                        chosen = cdtd_execute_ai(mode, data_top10, data_top100)
                        
                        cdtd_predicted_nv = chosen
                        cdtd_ui_state = "PREDICTED"
                        live.update(cdtd_generate_layout())
                        
                        should_bet = True
                        if cdtd_pause_remaining > 0:
                            cdtd_pause_remaining -= 1
                            should_bet = False
                        if cdtd_skip_next:
                            cdtd_skip_next = False
                            should_bet = False
                        
                        if should_bet and cdtd_issue_id is not None:
                            next_issue = cdtd_issue_id + 1
                            bet_amount = cdtd_current_bet if cdtd_current_bet else cdtd_base_bet
                            asset = user_asset_cdtd()
                            if bet_amount > asset.get(cdtd_coin, 0):
                                cdtd_current_bet = cdtd_base_bet
                                bet_amount = cdtd_base_bet
                            
                            success, msg = bet_cdtd(next_issue, chosen, bet_amount)
                            if success:
                                cdtd_bet_history.append({
                                    'issue': next_issue,
                                    'chosen': chosen,
                                    'amount': bet_amount,
                                    'result': 'pending',
                                    'algo': mode
                                })
                                cdtd_rounds_placed += 1
                                cdtd_bet_placed_this_round = True
                                if cdtd_bet_rounds_before_skip > 0 and cdtd_rounds_placed >= cdtd_bet_rounds_before_skip:
                                    cdtd_skip_next = True
                                    cdtd_rounds_placed = 0
                            else:
                                safe_console_print(f"[red]❌ Đặt cược thất bại: {msg}[/red]")
                        
                        live.update(cdtd_generate_layout())
                    
                    elif elapsed >= cdtd_analysis_duration + 15:
                        cdtd_ui_state = "WAITING"
                        cdtd_issue_id = None
                        live.update(cdtd_generate_layout())
                
                live.update(cdtd_generate_layout())
                time.sleep(0.5)
                
            except KeyboardInterrupt:
                cdtd_stop_flag = True
                break
            except Exception as e:
                safe_console_print(f"[yellow]⚠️ Lỗi CDTD: {e}[/yellow]")
                time.sleep(3)
                # ================== GIAO DIỆN CDTD ==================

def build_cdtd_header():
    asset = user_asset_cdtd()
    info_table = Table(box=None, show_header=False, pad_edge=False, expand=True)
    info_table.add_column(style=f"bold {HTOOL_COLORS['gold']}", no_wrap=True, justify="right", width=18)
    info_table.add_column(style="white")
    info_table.add_row(f"{ICONS['user']} USER:", f"[bold {HTOOL_COLORS['platinum']}]{cdtd_headers.get('user-id', 'N/A')}[/]")
    info_table.add_row(f"{ICONS['money']} BALANCE:", f"[bold {HTOOL_COLORS['emerald']}]{asset.get(cdtd_coin, 0):.4f}[/] {cdtd_coin}")
    pnl = asset.get(cdtd_coin, 0) - cdtd_stats['asset_0']
    info_table.add_row(f"{ICONS['chart']} P&L:", f"[{HTOOL_COLORS['emerald'] if pnl >= 0 else HTOOL_COLORS['ruby']}]{pnl:+.4f} {cdtd_coin}[/]")
    streak_text = Text.assemble(("🔥 ", f"bold {HTOOL_COLORS['neon_orange']}"), (f"{cdtd_win_streak}", f"bold {HTOOL_COLORS['emerald']}"), (" | ", "dim"), ("💀 ", f"bold {HTOOL_COLORS['ruby']}"), (f"{cdtd_lose_streak}", f"bold {HTOOL_COLORS['ruby']}"))
    info_table.add_row("📊 STREAK:", streak_text)
    info_table.add_row(f"{ICONS['key']} KEY:", f"[bold {HTOOL_COLORS['gold'] if _key_type == 'vip' else 'white'}]{_key_type.upper()}[/]")
    info_table.add_row(f"{ICONS['brain']} AI:", f"[bold {HTOOL_COLORS['neon_pink']}]{CDTD_ALGORITHMS.get(cdtd_settings.get('algo', 'RANDOM'), 'N/A')}[/]")
    info_table.add_row(f"{ICONS['clock']} TIME:", f"[{HTOOL_COLORS['sapphire']}]{datetime.now(tz).strftime('%H:%M:%S')}[/]")
    info_table.add_row(f"{ICONS['target']} ISSUE:", f"[bold {HTOOL_COLORS['gold']}]{cdtd_issue_id or 'Waiting...'}[/]")
    info_table.add_row(f"{ICONS['bell']} TG:", f"[{'green' if TELEGRAM_ENABLED else 'dim'}] {'BẬT' if TELEGRAM_ENABLED else 'TẮT'}[/]")
    info_table.add_row(f"🌐 IP:", f"[dim]{_ip_info.get('public_ip', 'N/A')}[/dim]")
    info_table.add_row(f"🛡️ Anti-Detection:", f"[{'green' if _secure_mode else 'dim'}] {'ON' if _secure_mode else 'OFF'}[/]")
    return Panel(info_table, border_style=HTOOL_COLORS["gold"], box=box.HEAVY, padding=(1, 2))

def build_cdtd_racers():
    data_top100, data_top10 = top_100_cdtd(), top_10_cdtd()
    racer_panels = []
    for i in range(1, 7):
        wins = data_top100[1][i-1] if data_top100 and len(data_top100) > 1 and data_top100[1] else 0
        is_predicted = cdtd_predicted_nv == i
        is_last_winner = False
        if data_top10 and len(data_top10) > 1 and data_top10[1]:
            try:
                is_last_winner = int(data_top10[1][0]) == i
            except:
                pass
        
        if is_predicted:
            border, title_style, bg, glow = f"bold {HTOOL_COLORS['emerald']}", f"bold {HTOOL_COLORS['emerald']}", "on #003300", "✨⭐"
        elif is_last_winner:
            border, title_style, bg, glow = HTOOL_COLORS["gold"], HTOOL_COLORS["gold"], "on #332200", "🏆"
        else:
            border, title_style, bg, glow = HTOOL_COLORS["onyx"], "white", "", ""
        
        content = Text.assemble(
            ("\n", ""),
            (f"{glow} {NV_ICONS[i]}\n", "default"),
            (f"{NV[i]}\n", title_style),
            (f"🏆 {wins} wins", "dim"),
            ("\n", ""),
            justify="center"
        )
        racer_panels.append(Panel(
            Align.center(content, vertical="middle"),
            title=f"[{title_style}]#{i}[/{title_style}]",
            border_style=border,
            box=box.HEAVY,
            expand=True,
            height=6,
            style=bg
        ))
    return Panel(
        Columns(racer_panels, equal=True, expand=True),
        title=f"[bold {HTOOL_COLORS['neon_orange']}]🏎️ CHẠY ĐUA TỐC ĐỘ 🏎️[/]",
        box=box.HEAVY,
        border_style=HTOOL_COLORS["neon_orange"],
        expand=True
    )

def build_cdtd_mid():
    if cdtd_ui_state == "ANALYZING":
        elapsed = time.time() - (cdtd_analysis_start_ts or time.time())
        progress = min(1.0, elapsed / cdtd_analysis_duration)
        bar = "█" * int(30 * progress) + "░" * (30 - int(30 * progress))
        content = Text.assemble(
            ("\n🧠 ĐANG PHÂN TÍCH...\n\n", f"bold {HTOOL_COLORS['neon_blue']}"),
            (f"[{HTOOL_COLORS['gold']}]{bar}[/]\n\n", ""),
            (f"Tiến độ: {progress*100:.0f}%\n", HTOOL_COLORS['neon_pink']),
            (f"⏱️ Còn {max(0, int(cdtd_analysis_duration - elapsed))}s\n", "dim"),
            justify="center"
        )
        return Panel(content, border_style=HTOOL_COLORS["neon_blue"], box=box.HEAVY, expand=True)
    
    elif cdtd_ui_state == "PREDICTED":
        bet_amt = cdtd_current_bet or cdtd_base_bet
        content = Text.assemble(
            ("\n╔══════════════════════════════╗\n", HTOOL_COLORS["gold"]),
            ("║  🎯 DỰ ĐOÁN CỦA BOT  🎯    ║\n", HTOOL_COLORS["gold"]),
            ("║  ", HTOOL_COLORS["gold"]),
            (f"{NV_ICONS.get(cdtd_predicted_nv, '🤖')} {NV.get(cdtd_predicted_nv, 'N/A'):^20}", f"bold {HTOOL_COLORS['emerald']}"),
            ("  ║\n", HTOOL_COLORS["gold"]),
            ("║  💰 Cược: ", HTOOL_COLORS["gold"]),
            (f"{bet_amt:.2f} {cdtd_coin:<10}", f"bold {HTOOL_COLORS['gold']}"),
            ("  ║\n", HTOOL_COLORS["gold"]),
            ("╚══════════════════════════════╝\n", HTOOL_COLORS["gold"]),
            (f"\n📈 Chuỗi thắng: {cdtd_win_streak}  📉 Chuỗi thua: {cdtd_lose_streak}\n", "white"),
            justify="center"
        )
        return Panel(content, border_style=HTOOL_COLORS["emerald"], box=box.HEAVY, expand=True)
    
    elif cdtd_ui_state == "RESULT":
        last_bet = cdtd_bet_history[-1] if cdtd_bet_history else None
        if last_bet and last_bet.get('result') == 'win':
            result_text, result_color, border_color = "🎉 CHIẾN THẮNG! 🎉", HTOOL_COLORS["emerald"], HTOOL_COLORS["emerald"]
        elif last_bet and last_bet.get('result') == 'lose':
            result_text, result_color, border_color = "💀 THUA CUỘC! 💀", HTOOL_COLORS["ruby"], HTOOL_COLORS["ruby"]
        else:
            result_text, result_color, border_color = "⏳ ĐANG CHỜ...", HTOOL_COLORS["gold"], HTOOL_COLORS["gold"]
        
        content = Text.assemble(
            ("\n", ""),
            (f"{result_text}\n\n", f"bold {result_color}"),
            ("Người thắng: ", "white"),
            (f"{NV_ICONS.get(cdtd_last_winner, '🏆')} {NV.get(cdtd_last_winner, 'N/A')}\n", f"bold {HTOOL_COLORS['gold']}"),
            ("\n⏳ Đang chờ kỳ mới...", "dim"),
            justify="center"
        )
        return Panel(content, border_style=border_color, box=box.HEAVY, expand=True)
    
    return Panel(
        Align.center(Text("\n⏳ ĐANG CHỜ DỮ LIỆU...\n\n🔄 Đang kết nối...\n", justify="center")),
        border_style=HTOOL_COLORS["gold"],
        box=box.HEAVY,
        expand=True
    )

def build_cdtd_history():
    t = Table(title=f"[bold {HTOOL_COLORS['gold']}]📜 LỊCH SỬ CƯỢC[/]", box=box.ROUNDED, expand=True, border_style=HTOOL_COLORS["onyx"])
    t.add_column("Kỳ", style=HTOOL_COLORS["sapphire"], width=6)
    t.add_column("Chọn", style=HTOOL_COLORS["neon_blue"])
    t.add_column("Cược", justify="right", style=HTOOL_COLORS["gold"], width=10)
    t.add_column("KQ")
    
    for b in list(cdtd_bet_history)[-10:]:
        chosen = NV.get(b.get('chosen'), str(b.get('chosen', '-')))
        amount = f"{b.get('amount', 0):.2f}"
        if b.get('result') == 'win':
            result_text = Text("✅ THẮNG", style=f"bold {HTOOL_COLORS['emerald']}")
        elif b.get('result') == 'lose':
            result_text = Text("❌ THUA", style=f"bold {HTOOL_COLORS['ruby']}")
        else:
            result_text = Text("⏳", style=HTOOL_COLORS["gold"])
        t.add_row(str(b.get('issue', '-')), chosen, amount, result_text)
    
    return Panel(t, border_style=HTOOL_COLORS["sapphire"], box=box.HEAVY, expand=True)

def build_cdtd_stats():
    data_top100 = top_100_cdtd()
    t = Table(title=f"[bold {HTOOL_COLORS['neon_blue']}]📊 THỐNG KÊ 100 VÁN[/]", box=box.ROUNDED, expand=True, border_style=HTOOL_COLORS["neon_blue"])
    t.add_column("NV", style=HTOOL_COLORS["gold"], width=4)
    t.add_column("Tên", style="white")
    t.add_column("Thắng", justify="right", style=HTOOL_COLORS["emerald"], width=8)
    t.add_column("Tỷ lệ", justify="right", style=HTOOL_COLORS["neon_pink"], width=8)
    
    total_wins = sum(data_top100[1]) if data_top100 and len(data_top100) > 1 and data_top100[1] else 1
    for i in range(6):
        wins = data_top100[1][i] if data_top100 and len(data_top100) > 1 and data_top100[1] else 0
        t.add_row(
            f"{NV_ICONS.get(i+1, '🏆')}",
            NV.get(i+1, f'NV{i+1}'),
            str(wins),
            f"{wins/total_wins*100:.1f}%"
        )
    
    summary = Table(box=box.ROUNDED, expand=True, border_style=HTOOL_COLORS["gold"])
    summary.add_column("Chỉ số", style=HTOOL_COLORS["gold"])
    summary.add_column("Giá trị", style="white")
    summary.add_row("Tổng ván", str(cdtd_stats['win'] + cdtd_stats['lose']))
    summary.add_row("Thắng", f"[green]{cdtd_stats['win']}[/]")
    summary.add_row("Thua", f"[red]{cdtd_stats['lose']}[/]")
    summary.add_row("Max thắng", str(cdtd_max_win_streak))
    summary.add_row("Max thua", str(cdtd_max_lose_streak))
    pnl = user_asset_cdtd().get(cdtd_coin, 0) - cdtd_stats['asset_0']
    summary.add_row("P&L", f"[{'green' if pnl >= 0 else 'red'}]{pnl:+.4f} {cdtd_coin}[/]")
    
    return Panel(
        Columns([t, summary], equal=True, expand=True),
        border_style=HTOOL_COLORS["gold"],
        box=box.HEAVY,
        expand=True
    )

def build_cdtd_marquee():
    messages = [
        f"⚡ CDTD - 42 AI {ICONS['rocket']}",
        f"🧠 {CDTD_ALGORITHMS.get(cdtd_settings.get('algo', 'RANDOM'), 'N/A')} {ICONS['robot']}",
        f"💰 {cdtd_coin} | Cược: {cdtd_base_bet} | x{cdtd_multiplier}",
        f"🎯 W:{cdtd_stats['win']} L:{cdtd_stats['lose']} {ICONS['chart']}",
        f"⛏️ Mining: 10s = 0.1 xu",
    ]
    message = messages[int(time.time() / 5) % len(messages)]
    full_text = " " * 20 + message + " " * 20
    width = console.width or 80
    display_text = (full_text * 3)[int(time.time() * 3) % len(full_text) : int(time.time() * 3) % len(full_text) + width]
    return Panel(
        Text(display_text, style=f"bold {HTOOL_COLORS['neon_blue']}", no_wrap=True),
        box=box.ROUNDED,
        border_style=HTOOL_COLORS["onyx"],
        padding=0,
        expand=True
    )

def cdtd_generate_layout():
    main_grid = Table.grid(expand=True, pad_edge=False)
    main_grid.add_column("main", ratio=55)
    main_grid.add_column("side", ratio=45)
    
    right_grid = Table.grid(expand=True, pad_edge=False)
    right_grid.add_row(build_cdtd_mid())
    right_grid.add_row(build_cdtd_history())
    
    main_grid.add_row(build_cdtd_racers(), right_grid)
    
    root = Table.grid(expand=True, pad_edge=False)
    root.add_row(build_cdtd_header())
    root.add_row(build_cdtd_marquee())
    root.add_row(main_grid)
    root.add_row(build_cdtd_stats())
    
    return root

def cdtd_prompt_settings():
    global cdtd_base_bet, cdtd_multiplier, cdtd_coin, cdtd_current_bet, cdtd_pause_rounds, cdtd_bet_rounds_before_skip, cdtd_settings
    
    console.clear()
    header = Panel(
        Align.center(Text.assemble(
            (f"{ICONS['settings']} ", f"bold {HTOOL_COLORS['gold']}"),
            ("CẤU HÌNH CHẠY ĐUA TỐC ĐỘ", f"bold {HTOOL_COLORS['neon_blue']}")
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.DOUBLE
    )
    console.print(header)
    console.print()
    
    coin_choice = Prompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]💰 Chọn tiền: [1] USDT [2] BUILD [3] WORLD[/]\n   >>",
        choices=['1', '2', '3'],
        default='2'
    )
    cdtd_coin = {'1': 'USDT', '2': 'BUILD', '3': 'WORLD'}[coin_choice]
    
    cdtd_base_bet = FloatPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]💵 Cược gốc ({cdtd_coin})[/]\n   >>", default=1.0)
    cdtd_multiplier = FloatPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]📈 Hệ số nhân[/]\n   >>", default=2.0)
    cdtd_current_bet = cdtd_base_bet
    cdtd_bet_rounds_before_skip = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]🛡️ Nghỉ 1 ván sau N ván (0=không)[/]\n   >>", default=0)
    cdtd_pause_rounds = IntPrompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]⏸️ Nghỉ N ván sau khi thua (0=không)[/]\n   >>", default=0)
    
    console.clear()
    console.print(header)
    
    console.print(f"\n[bold {HTOOL_COLORS['neon_pink']}]🧠 Chọn AI (42 AI):[/]\n")
    
    algo_table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["neon_pink"])
    algo_table.add_column("#", style=HTOOL_COLORS["gold"], width=4)
    algo_table.add_column("Thuật toán", style=HTOOL_COLORS["neon_blue"])
    algo_table.add_column("Mô tả", style="dim")
    
    for i, (key, label) in enumerate(CDTD_ALGORITHMS.items(), 1):
        algo_table.add_row(str(i), label, "")
    
    console.print(algo_table)
    console.print()
    
    algo_choice = IntPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]>> Chọn số thứ tự (1-{len(CDTD_ALGORITHMS)})[/bold {HTOOL_COLORS['gold']}]",
        choices=[str(i) for i in range(1, len(CDTD_ALGORITHMS) + 1)],
        default=1
    )
    
    cdtd_settings["algo"] = list(CDTD_ALGORITHMS.keys())[algo_choice - 1]
    console.print(f'\n[green]✅ Đã chọn: {CDTD_ALGORITHMS[cdtd_settings["algo"]]}[/]')
    
    console.print(f"\n[bold {HTOOL_COLORS['gold']}]📱 Cấu hình Telegram? (y/n)[/]")
    if Prompt.ask("   >>", choices=['y', 'n'], default='n') == 'y':
        setup_telegram()
    
    console.print(f'\n[green]✅ Cấu hình hoàn tất![/]')
    time.sleep(1.5)
    return True

def main_cdtd_v3():
    console.clear()
    header = Panel(
        Align.center(Text.assemble(
            (f"{ICONS['rocket']} ", f"bold {HTOOL_COLORS['gold']}"),
            ("CHẠY ĐUA TỐC ĐỘ - 42 AI", f"bold {HTOOL_COLORS['neon_blue']}")
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.DOUBLE
    )
    console.print(header)
    console.print(f"[dim]💬 Support: @htool88 | 42 AI | Telegram[/dim]\n")
    
    data = load_data_cdtd()
    setup_cdtd_headers(data)
    
    if not cdtd_prompt_settings():
        return
    
    console.clear()
    console.print(f"[bold {HTOOL_COLORS['neon_orange']}]🏎️ KHỞI ĐỘNG VỚI 42 AI...[/]")
    
    with console.status(f"[bold {HTOOL_COLORS['gold']}]🔍 Đang kiểm tra...[/]", spinner="dots"):
        asset = user_asset_cdtd()
        time.sleep(1)
    
    if asset.get(cdtd_coin, 0) <= 0:
        console.print(f'[red]❌ Số dư {cdtd_coin} = 0![/]')
        time.sleep(2)
        return
    
    console.print(f'[green]✅ Số dư: {asset[cdtd_coin]:.4f} {cdtd_coin}[/]')
    if TELEGRAM_ENABLED:
        console.print(f'[green]✅ Telegram: BẬT[/]')
    
    time.sleep(2)
    cdtd_game_loop()
    
    console.clear()
    final_asset = user_asset_cdtd()
    pnl = final_asset.get(cdtd_coin, 0) - cdtd_stats['asset_0']
    summary = Panel(
        Align.center(Text.assemble(
            ("\n📊 TỔNG KẾT\n\n", f"bold {HTOOL_COLORS['gold']}"),
            (f"Thắng: {cdtd_stats['win']} | Thua: {cdtd_stats['lose']}\n", "white"),
            (f"P&L: {pnl:+.4f} {cdtd_coin}\n", HTOOL_COLORS["gold"] if pnl >= 0 else HTOOL_COLORS["ruby"])
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.DOUBLE
    )
    console.print(summary)
    console.print("\n[dim]Nhấn Enter để quay lại menu...[/]")
    input()
    # ================== LOGO / CẤU HÌNH / GAME FLOW ==================

def build_logo_with_gradient(logo: str) -> Text:
    """Render logo với màu gradient vàng."""
    text = Text()
    colors = [
        HTOOL_COLORS["gold"],
        HTOOL_COLORS["gold_dark"],
        HTOOL_COLORS["neon_orange"],
        HTOOL_COLORS["gold"],
    ]
    lines = logo.split("\n")
    for i, line in enumerate(lines):
        if not line.strip():
            text.append("\n")
            continue
        color = colors[i % len(colors)]
        text.append(line + "\n", style=f"bold {color}")
    return text


def save_strategy_config() -> bool:
    """Lưu cấu hình chiến lược ra file."""
    global base_bet, multiplier, run_mode, bet_rounds_before_skip
    global pause_after_losses, profit_target, stop_when_profit_reached
    global stop_loss_target, stop_when_loss_reached, analysis_duration, settings
    try:
        cfg = {
            "algo": settings.get("algo", "ENSEMBLE"),
            "base_bet": base_bet,
            "multiplier": multiplier,
            "run_mode": run_mode,
            "bet_rounds_before_skip": bet_rounds_before_skip,
            "pause_after_losses": pause_after_losses,
            "profit_target": profit_target,
            "stop_when_profit_reached": stop_when_profit_reached,
            "stop_loss_target": stop_loss_target,
            "stop_when_loss_reached": stop_when_loss_reached,
            "analysis_duration": analysis_duration,
        }
        with open(STRATEGY_CONFIG_FILE, "w", encoding="utf-8") as f:
            json.dump(cfg, f, indent=2, ensure_ascii=False)
        console.print(f"[green]✅ Đã lưu cấu hình vào {STRATEGY_CONFIG_FILE}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Lỗi lưu config: {e}[/red]")
        return False


def load_strategy_config() -> bool:
    """Load cấu hình chiến lược từ file."""
    global base_bet, multiplier, run_mode, bet_rounds_before_skip
    global pause_after_losses, profit_target, stop_when_profit_reached
    global stop_loss_target, stop_when_loss_reached, analysis_duration, settings, current_bet
    if not os.path.exists(STRATEGY_CONFIG_FILE):
        console.print(f"[yellow]⚠️ Chưa có file {STRATEGY_CONFIG_FILE}. Hãy SAVE CONFIG trước.[/yellow]")
        return False
    try:
        with open(STRATEGY_CONFIG_FILE, "r", encoding="utf-8") as f:
            cfg = json.load(f)
        settings["algo"] = cfg.get("algo", settings.get("algo", "ENSEMBLE"))
        base_bet = float(cfg.get("base_bet", base_bet))
        multiplier = float(cfg.get("multiplier", multiplier))
        run_mode = cfg.get("run_mode", run_mode)
        bet_rounds_before_skip = int(cfg.get("bet_rounds_before_skip", bet_rounds_before_skip))
        pause_after_losses = int(cfg.get("pause_after_losses", pause_after_losses))
        profit_target = cfg.get("profit_target")
        stop_when_profit_reached = bool(cfg.get("stop_when_profit_reached", False))
        stop_loss_target = cfg.get("stop_loss_target")
        stop_when_loss_reached = bool(cfg.get("stop_when_loss_reached", False))
        analysis_duration = float(cfg.get("analysis_duration", analysis_duration))
        current_bet = base_bet
        console.print(f"[green]✅ Đã load config: AI={settings['algo']} | Cược={base_bet} | x{multiplier}[/green]")
        return True
    except Exception as e:
        console.print(f"[red]❌ Lỗi load config: {e}[/red]")
        return False


def prompt_settings() -> bool:
    """Menu cấu hình chiến lược Vua Thoát Hiểm."""
    global base_bet, multiplier, run_mode, bet_rounds_before_skip
    global pause_after_losses, profit_target, stop_when_profit_reached
    global stop_loss_target, stop_when_loss_reached, analysis_duration, settings, current_bet, _key_type

    console.clear()
    header = Panel(
        Align.center(Text.assemble(
            (f"{ICONS['settings']} ", f"bold {HTOOL_COLORS['gold']}"),
            ("CẤU HÌNH VUA THOÁT HIỂM", f"bold {HTOOL_COLORS['neon_blue']}")
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.DOUBLE
    )
    console.print(header)
    console.print()

    base_bet = FloatPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]💵 Cược gốc (BUILD)[/]",
        default=float(base_bet or 1.0)
    )
    multiplier = FloatPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]📈 Hệ số gấp thếp[/]",
        default=float(multiplier or 2.0)
    )
    current_bet = base_bet

    mode_choice = Prompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]🎮 Chế độ: [1] AUTO [2] MANUAL[/]",
        choices=["1", "2"],
        default="1"
    )
    run_mode = "AUTO" if mode_choice == "1" else "MANUAL"

    bet_rounds_before_skip = IntPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]🛡️ Nghỉ 1 ván sau N ván (0=không)[/]",
        default=int(bet_rounds_before_skip or 0)
    )
    pause_after_losses = IntPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]⏸️ Nghỉ N ván sau khi thua (0=không)[/]",
        default=int(pause_after_losses or 0)
    )
    analysis_duration = FloatPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]⏱️ Thời gian phân tích (giây)[/]",
        default=float(analysis_duration or 45.0)
    )

    if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]🎯 Bật mục tiêu lãi? (y/n)[/]", choices=["y", "n"], default="n") == "y":
        stop_when_profit_reached = True
        profit_target = FloatPrompt.ask(f"[bold {HTOOL_COLORS['gold']}]Mục tiêu số dư BUILD[/]", default=0.0)
    else:
        stop_when_profit_reached = False
        profit_target = None

    if Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]💀 Bật cắt lỗ? (y/n)[/]", choices=["y", "n"], default="n") == "y":
        stop_when_loss_reached = True
        stop_loss_target = FloatPrompt.ask(f"[bold {HTOOL_COLORS['gold']}]Ngưỡng cắt lỗ BUILD[/]", default=0.0)
    else:
        stop_when_loss_reached = False
        stop_loss_target = None

    # Chọn AI
    available = get_available_ai_list(_key_type)
    console.print(f"\n[bold {HTOOL_COLORS['neon_pink']}]🧠 Chọn AI (key {_key_type.upper()} — {len(available)} AI):[/]\n")
    algo_table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["neon_pink"])
    algo_table.add_column("#", style=HTOOL_COLORS["gold"], width=4)
    algo_table.add_column("Thuật toán", style=HTOOL_COLORS["neon_blue"])
    for i, key in enumerate(available, 1):
        algo_table.add_row(str(i), SELECTION_MODES.get(key, key))
    console.print(algo_table)
    console.print()
    algo_idx = IntPrompt.ask(
        f"[bold {HTOOL_COLORS['gold']}]>> Chọn (1-{len(available)})[/]",
        choices=[str(i) for i in range(1, len(available) + 1)],
        default=1
    )
    settings["algo"] = available[algo_idx - 1]
    console.print(f"[green]✅ AI: {SELECTION_MODES.get(settings['algo'], settings['algo'])}[/green]")

    if Prompt.ask(f"\n[bold {HTOOL_COLORS['gold']}]📱 Cấu hình Telegram? (y/n)[/]", choices=["y", "n"], default="n") == "y":
        setup_telegram()

    console.print(f"\n[green]✅ Cấu hình hoàn tất![/green]")
    time.sleep(1)
    return True


def vth_generate_layout():
    """Layout live đơn giản cho Vua Thoát Hiểm."""
    asset_build = current_build if current_build is not None else 0.0
    pnl = cumulative_profit if cumulative_profit is not None else 0.0
    info = Table(box=None, show_header=False, expand=True)
    info.add_column(style=f"bold {HTOOL_COLORS['gold']}", width=16)
    info.add_column(style="white")
    info.add_row("USER", str(USER_ID or "N/A"))
    info.add_row("BUILD", f"{asset_build:,.4f}")
    info.add_row("P&L", f"{pnl:+,.4f}")
    info.add_row("STREAK", f"W:{win_streak} L:{lose_streak}")
    info.add_row("AI", SELECTION_MODES.get(settings.get("algo", "RANDOM"), settings.get("algo", "?")))
    info.add_row("ISSUE", str(issue_id or "—"))
    info.add_row("STATE", ui_state)
    info.add_row("WS", _ws_status)
    info.add_row("BET", f"{(current_bet or base_bet):.2f}")
    if predicted_room:
        info.add_row("DỰ ĐOÁN", f"PHÒNG {predicted_room} — {ROOM_NAMES.get(predicted_room, '')}")
    if killed_room:
        info.add_row("SÁT THỦ", f"PHÒNG {killed_room} — {ROOM_NAMES.get(killed_room, '')}")

    rooms = Table(title="Phòng", box=box.ROUNDED, expand=True)
    rooms.add_column("ID", width=4)
    rooms.add_column("Tên")
    rooms.add_column("Players", justify="right")
    rooms.add_column("Bet", justify="right")
    rooms.add_column("Kills", justify="right")
    for r in ROOM_ORDER:
        mark = "🎯" if predicted_room == r else ("💀" if killed_room == r else "")
        rooms.add_row(
            f"{mark}{r}",
            ROOM_NAMES.get(r, str(r)),
            str(room_state[r].get("players", 0)),
            str(room_state[r].get("bet", 0)),
            str(room_stats[r].get("kills", 0)),
        )

    hist = Table(title="Lịch sử cược", box=box.ROUNDED, expand=True)
    hist.add_column("Issue", width=8)
    hist.add_column("Room")
    hist.add_column("Amount", justify="right")
    hist.add_column("KQ")
    for b in list(bet_history)[-8:]:
        res = b.get("result", "Đang")
        style = "green" if res == "Thắng" else ("red" if res == "Thua" else "yellow")
        hist.add_row(str(b.get("issue", "")), str(b.get("room", "")), f"{b.get('amount', 0):.2f}", f"[{style}]{res}[/]")

    root = Table.grid(expand=True)
    root.add_row(Panel(info, title="VUA THOÁT HIỂM", border_style=HTOOL_COLORS["gold"], box=box.HEAVY))
    root.add_row(rooms)
    root.add_row(hist)
    return root


def start_game_flow():
    """Khởi động WebSocket + monitor + UI live Vua Thoát Hiểm."""
    global stop_flag, current_bet, starting_balance, cumulative_profit
    stop_flag = False
    current_bet = base_bet
    starting_balance = None
    cumulative_profit = None

    console.clear()
    console.print(f"[bold {HTOOL_COLORS['neon_green']}]🎯 KHỞI ĐỘNG VUA THOÁT HIỂM...[/]")
    console.print(f"[dim]AI: {SELECTION_MODES.get(settings.get('algo'), settings.get('algo'))} | Cược: {base_bet} | x{multiplier}[/dim]\n")

    # Fetch balance lần đầu
    try:
        fetch_balances_3games(retries=2, timeout=8)
    except Exception:
        pass

    ws_thread = threading.Thread(target=start_ws, daemon=True)
    ws_thread.start()
    mon_thread = threading.Thread(target=monitor_loop, daemon=True)
    mon_thread.start()

    try:
        with Live(vth_generate_layout(), refresh_per_second=2, console=console, screen=True) as live:
            while not stop_flag:
                live.update(vth_generate_layout())
                time.sleep(0.5)
    except KeyboardInterrupt:
        stop_flag = True
    finally:
        stop_flag = True
        try:
            wsobj = _ws.get("ws")
            if wsobj:
                wsobj.close()
        except Exception:
            pass

    console.clear()
    console.print(Panel(
        Align.center(Text.assemble(
            ("\n📊 KẾT THÚC PHIÊN\n\n", f"bold {HTOOL_COLORS['gold']}"),
            (f"W:{win_streak} L:{lose_streak} | MaxW:{max_win_streak} MaxL:{max_lose_streak}\n", "white"),
            (f"P&L: {(cumulative_profit or 0):+.4f} BUILD\n", HTOOL_COLORS["gold"]),
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.DOUBLE
    ))
    console.print("\n[dim]Nhấn Enter để quay lại menu...[/]")
    input()


# ================== ADMIN MENU (ẨN) ==================

def supabase_list_keys(limit: int = 50) -> list:
    """Lấy danh sách key từ Supabase."""
    try:
        url = f"{SUPABASE_URL}/rest/v1/keys?select=*&order=created_at.desc&limit={limit}"
        r = requests.get(url, headers=supabase_headers(), timeout=15)
        if r.status_code == 200:
            return r.json() if isinstance(r.json(), list) else []
        # fallback không có created_at
        url2 = f"{SUPABASE_URL}/rest/v1/keys?select=*&limit={limit}"
        r2 = requests.get(url2, headers=supabase_headers(), timeout=15)
        if r2.status_code == 200:
            return r2.json() if isinstance(r2.json(), list) else []
        return []
    except Exception as e:
        safe_console_print(f"[red]Lỗi list keys: {e}[/red]")
        return []


def supabase_deactivate_key(key_code: str) -> tuple:
    try:
        url = f"{SUPABASE_URL}/rest/v1/keys?key_code=eq.{key_code}"
        r = requests.patch(url, headers=supabase_headers(prefer="return=representation"),
                           json={"status": "inactive"}, timeout=15)
        if r.status_code in (200, 204):
            return True, "Đã vô hiệu hóa key"
        return False, f"HTTP {r.status_code}: {r.text[:200]}"
    except Exception as e:
        return False, str(e)


def admin_create_key_interactive(key_type: str = "free") -> None:
    """Admin tạo key FREE hoặc VIP trên Supabase."""
    prefix = "VIP_" if key_type == "vip" else "FREE_"
    default_ai = 42 if key_type == "vip" else 10
    default_hours = 720 if key_type == "vip" else 13  # VIP mặc định 30 ngày

    console.print(f"\n[bold]Tạo KEY {key_type.upper()}[/bold]")
    custom = Prompt.ask("Key code (Enter = tự sinh)", default="")
    if custom:
        key_code = custom.strip().upper()
    else:
        key_code = prefix + secrets.token_hex(5).upper()

    max_ai = IntPrompt.ask("max_ai", default=default_ai)
    hours = IntPrompt.ask("Thời hạn (giờ)", default=default_hours)
    note = Prompt.ask("Ghi chú", default=f"Admin tạo {key_type}")

    ok, result = create_key_on_supabase(
        key_code=key_code,
        key_type=key_type,
        max_ai=max_ai,
        duration_hours=hours,
        note=note,
    )
    if ok:
        console.print(Panel(
            Text.assemble(
                ("✅ TẠO KEY THÀNH CÔNG\n\n", "bold green"),
                ("KEY: ", "white"), (f"{key_code}\n", f"bold {HTOOL_COLORS['gold']}"),
                ("Loại: ", "white"), (f"{key_type.upper()}\n", "bold cyan"),
                ("AI: ", "white"), (f"{max_ai}\n", "bold"),
                ("Hạn: ", "white"), (f"{hours} giờ\n", "bold"),
            ),
            border_style="green", box=box.HEAVY
        ))
    else:
        console.print(f"[red]❌ {result}[/red]")


def admin_menu() -> None:
    """Menu admin ẩn — quản lý key qua Supabase."""
    while True:
        console.clear()
        console.print(Panel(
            Align.center(Text.assemble(
                ("🔐 ADMIN PANEL\n", f"bold {HTOOL_COLORS['ruby']}"),
                ("Kết nối Supabase · Quản lý key & user", "dim"),
            )),
            border_style=HTOOL_COLORS["ruby"],
            box=box.DOUBLE
        ))
        console.print("[1] 📋 Xem toàn bộ key (Supabase)")
        console.print("[2] 🔑 Thêm KEY FREE (10 AI, Lotto 5 AI)")
        console.print("[3] 👑 Thêm KEY VIP (toàn bộ AI)")
        console.print("[4] ❌ Vô hiệu hóa key")
        console.print("[5] 👥 Xem user local (xu/key)")
        console.print("[q] 🔙 Thoát admin")
        console.print()
        choice = Prompt.ask(">>", choices=["1", "2", "3", "4", "5", "q"], default="q")

        if choice == "q":
            break
        elif choice == "1":
            keys = supabase_list_keys(100)
            if not keys:
                console.print("[yellow]Không có key hoặc không đọc được Supabase.[/yellow]")
            else:
                t = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["gold"], title=f"Keys ({len(keys)})")
                t.add_column("key_code", style=HTOOL_COLORS["neon_blue"])
                t.add_column("type")
                t.add_column("status")
                t.add_column("max_ai", justify="right")
                t.add_column("expires")
                t.add_column("used", justify="right")
                t.add_column("note", style="dim")
                for k in keys:
                    t.add_row(
                        str(k.get("key_code", ""))[:24],
                        str(k.get("key_type", "")),
                        str(k.get("status", "")),
                        str(k.get("max_ai", "")),
                        str(k.get("expires_at", ""))[:19],
                        str(k.get("used_count", 0)),
                        str(k.get("note", ""))[:20],
                    )
                console.print(t)
            input("\n[dim]Enter...[/dim]")
        elif choice == "2":
            admin_create_key_interactive("free")
            input("\n[dim]Enter...[/dim]")
        elif choice == "3":
            admin_create_key_interactive("vip")
            input("\n[dim]Enter...[/dim]")
        elif choice == "4":
            kc = Prompt.ask("Nhập key_code cần khóa").strip()
            if kc:
                ok, msg = supabase_deactivate_key(kc)
                console.print(f"[green]✅ {msg}[/green]" if ok else f"[red]❌ {msg}[/red]")
            input("\n[dim]Enter...[/dim]")
        elif choice == "5":
            data = load_user_data_secure()
            if not data:
                console.print("[yellow]Chưa có user local.[/yellow]")
            else:
                t = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["sapphire"], title=f"Users ({len(data)})")
                t.add_column("ID")
                t.add_column("IP")
                t.add_column("Xu", justify="right")
                t.add_column("Keys", justify="right")
                t.add_column("Tạo lúc", style="dim")
                for uid, ud in data.items():
                    t.add_row(
                        str(uid)[:12],
                        str(ud.get("ip", ""))[:18],
                        f"{ud.get('coins', 0):.1f}",
                        str(len(ud.get("keys", []) or [])),
                        str(ud.get("created_at", ""))[:19],
                    )
                console.print(t)
            input("\n[dim]Enter...[/dim]")


# ================== MAIN MENU ==================

def build_main_menu():
    global _in_menu, _ws_status, _secure_mode
    _in_menu = True
    console.clear()
    logo_text = build_logo_with_gradient(LOGO)
    console.print(Align.center(logo_text))
    
    console.print()
    free_ai_n = len(FREE_AI_LIST)
    menu_panel = Panel(Align.center(Text.assemble(
        ("\n", ""),
        (f"  {ICONS['crown']}  ", f"bold {HTOOL_COLORS['gold']}"),
        ("HTOOL VIP PREMIUM v3.0", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f"  {ICONS['crown']}  ", f"bold {HTOOL_COLORS['gold']}"),
        ("\n", ""),
        ("╔════════════════════════════════════════════════════════════╗\n", f"dim {HTOOL_COLORS['gold']}"),
        ("║  [1]  🎯  VUA THOÁT HIỂM - PLAY & CONFIG                ║\n", f"bold {HTOOL_COLORS['neon_green']}"),
        ("║       ➜ Chọn tài khoản và thiết lập chiến lược chơi      ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [2]  🏎️  CHẠY ĐUA TỐC ĐỘ                               ║\n", f"bold {HTOOL_COLORS['neon_orange']}"),
        ("║       ➜ FREE: 10 AI | VIP: full AI                       ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [3]  🎰  WINHASH LOTTO                                  ║\n", f"bold {HTOOL_COLORS['gold']}"),
        ("║       ➜ FREE: 5 AI | VIP: full AI                        ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [4]  ➕  ADD ACCOUNT                                    ║\n", f"bold {HTOOL_COLORS['sapphire']}"),
        ("║       ➜ Thêm tài khoản mới vào danh sách                 ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [5]  🗑️  DELETE ACCOUNT                                 ║\n", f"bold {HTOOL_COLORS['ruby']}"),
        ("║       ➜ Xóa tài khoản khỏi danh sách                     ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [6]  ⚙️  SAVE CONFIG                                    ║\n", f"bold {HTOOL_COLORS['gold']}"),
        ("║       ➜ Lưu cấu hình hiện tại để dùng sau                ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [7]  🚀  PLAY WITH CONFIG                               ║\n", f"bold {HTOOL_COLORS['neon_pink']}"),
        ("║       ➜ Chơi ngay với cấu hình đã lưu                    ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [8]  🛡️  ANTI-DETECTION STATUS                          ║\n", f"bold {HTOOL_COLORS['emerald']}"),
        ("║       ➜ Xem trạng thái chống soi                        ║\n", "dim"),
        ("║                                                          ║\n", "dim"),
        ("║  [q]  👋  EXIT                                           ║\n", f"bold {HTOOL_COLORS['rose']}"),
        ("║       ➜ Thoát chương trình                               ║\n", "dim"),
        ("╚════════════════════════════════════════════════════════════╝\n", f"dim {HTOOL_COLORS['gold']}"),
        ("\n", ""),
        (f"  💬  Support: @htool88  | FREE AI: {free_ai_n} | Lotto FREE: 5\n", f"bold {HTOOL_COLORS['neon_blue']}"),
        (f"  🔗  WebSocket: {_ws_status}\n", "dim"),
        (f"  🌐  IP: {_ip_info.get('public_ip', 'N/A')}\n", "dim"),
        (f"  🛡️  Anti-Detection: {'✅ ON' if _secure_mode else '❌ OFF'}\n", "dim"),
        (f"  🔑  Key: {_key_type.upper() if _key_type else 'N/A'}\n", "dim"),
        ("\n", ""),
    )), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE, padding=(1, 2))
    console.print(menu_panel)
    console.print()
    raw = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Enter your choice[/bold {HTOOL_COLORS['gold']}]", default="q")
    # Menu admin ẩn: nhập đúng mã 9826665
    if raw.strip() == ADMIN_SECRET_CODE:
        admin_menu()
        return build_main_menu()
    choice = raw.strip().lower()
    if choice not in ["1", "2", "3", "4", "5", "6", "7", "8", "q"]:
        console.print("[red]Lựa chọn không hợp lệ[/red]")
        time.sleep(1)
        return "q"
    return choice

# ================== QUẢN LÝ TÀI KHOẢN ==================

def load_accounts() -> list:
    acc_file = Path("accounts.json")
    if not acc_file.exists():
        return []
    try:
        return json.loads(acc_file.read_text())
    except (json.JSONDecodeError, IOError):
        return []

def save_accounts(accounts: list):
    acc_file = Path("accounts.json")
    with acc_file.open("w", encoding="utf-8") as f:
        json.dump(accounts, f, indent=2)

def add_new_account(accounts: list) -> bool:
    console.clear()
    header = Panel(Align.center(Text.assemble((f"{ICONS['user']} ", f"bold {HTOOL_COLORS['gold']}"), ("ADD NEW ACCOUNT", f"bold {HTOOL_COLORS['neon_blue']}"), (f" {ICONS['user']}", f"bold {HTOOL_COLORS['gold']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
    console.print(header)
    console.print()
    console.print(Panel(Text.assemble((f"{ICONS['info']} ", "bold yellow"), ("Dán link trò chơi vào bên dưới", "white"), ("\n", ""), ("Ví dụ: ", "dim"), ("https://xworld.info/?userId=12345&secretKey=abc123", "dim cyan")), border_style=HTOOL_COLORS["sapphire"], box=box.ROUNDED))
    console.print()
    link = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Paste link[/bold {HTOOL_COLORS['gold']}]")
    if not link:
        console.print("[yellow]Cancelled.[/yellow]")
        time.sleep(1)
        return False
    try:
        parsed = urlparse(link)
        params = parse_qs(parsed.query)
        if 'userId' in params and 'secretKey' in params:
            uid = int(params.get('userId')[0])
            skey = params.get('secretKey', [None])[0]
            if any(acc.get('userId') == uid for acc in accounts):
                console.print(f"[yellow]⚠️ Account userId: {uid} already exists.[/yellow]")
                time.sleep(2)
                return False
            accounts.append({"userId": uid, "secretKey": skey})
            save_accounts(accounts)
            console.print(Panel(Align.center(Text.assemble((f"{ICONS['check']} ", "bold green"), (f"Added account: ", "bold white"), (f"{uid}", f"bold {HTOOL_COLORS['gold']}"))), border_style=HTOOL_COLORS["emerald"], box=box.ROUNDED))
            time.sleep(2)
            return True
        else:
            console.print("[red]❌ Invalid link! Missing 'userId' or 'secretKey'.[/red]")
            time.sleep(2)
            return False
    except Exception as e:
        console.print(f"[red]❌ Error: {e}[/red]")
        time.sleep(2)
        return False

def delete_account(accounts: list) -> bool:
    console.clear()
    header = Panel(Align.center(Text.assemble((f"{ICONS['fire']} ", f"bold {HTOOL_COLORS['ruby']}"), ("DELETE ACCOUNT", f"bold {HTOOL_COLORS['neon_blue']}"), (f" {ICONS['fire']}", f"bold {HTOOL_COLORS['ruby']}"))), border_style=HTOOL_COLORS["ruby"], box=box.DOUBLE)
    console.print(header)
    console.print()
    if not accounts:
        console.print("[yellow]No accounts to delete.[/yellow]")
        time.sleep(2)
        return False
    table = Table(box=box.ROUNDED, border_style=HTOOL_COLORS["ruby"])
    table.add_column("STT", style=f"bold {HTOOL_COLORS['gold']}", width=6)
    table.add_column("User ID", style=HTOOL_COLORS["neon_blue"])
    for i, acc in enumerate(accounts, 1):
        table.add_row(str(i), str(acc.get('userId')))
    console.print(table)
    console.print()
    choice_str = Prompt.ask(f"[bold {HTOOL_COLORS['ruby']}]>> Select account to delete[/bold {HTOOL_COLORS['ruby']}]", default="")
    if not choice_str:
        console.print("[yellow]Cancelled.[/yellow]")
        time.sleep(1)
        return False
    try:
        choice_idx = int(choice_str) - 1
        if 0 <= choice_idx < len(accounts):
            removed_acc = accounts.pop(choice_idx)
            save_accounts(accounts)
            console.print(f"[green]✅ Deleted account: {removed_acc.get('userId')}[/green]")
            time.sleep(2)
            return True
        else:
            console.print("[red]❌ Invalid selection.[/red]")
            time.sleep(1)
            return False
    except ValueError:
        console.print("[red]❌ Invalid input.[/red]")
        time.sleep(1)
        return False

def select_account_premium() -> bool:
    global USER_ID, SECRET_KEY
    while True:
        console.clear()
        header = Panel(Align.center(Text.assemble((f"{ICONS['user']} ", f"bold {HTOOL_COLORS['gold']}"), ("SELECT ACCOUNT", f"bold {HTOOL_COLORS['neon_blue']}"), (f" {ICONS['user']}", f"bold {HTOOL_COLORS['gold']}"))), border_style=HTOOL_COLORS["gold"], box=box.DOUBLE)
        console.print(header)
        console.print()
        accounts = load_accounts()
        if not accounts:
            console.print(Panel(Align.center(Text.assemble((f"{ICONS['warning']} ", "bold yellow"), ("Không có tài khoản nào!", "bold white"), ("\n", ""), ("Vui lòng dùng tùy chọn [5] để thêm tài khoản", "dim"))), border_style=HTOOL_COLORS["ruby"], box=box.ROUNDED))
            time.sleep(2)
            return False
        table = Table(title=f"[bold {HTOOL_COLORS['gold']}]📋 ACCOUNT LIST[/bold {HTOOL_COLORS['gold']}]", box=box.HEAVY, border_style=HTOOL_COLORS["sapphire"])
        table.add_column("STT", style=f"bold {HTOOL_COLORS['gold']}", width=6)
        table.add_column("User ID", style=HTOOL_COLORS["neon_blue"])
        table.add_column("Balance", justify="right")
        table.add_column("Status", justify="center")
        with console.status(f"[bold {HTOOL_COLORS['neon_blue']}]🔍 Checking balances...[/bold {HTOOL_COLORS['neon_blue']}]", spinner="dots") as status:
            for i, acc in enumerate(accounts, 1):
                uid = acc.get('userId')
                skey = acc.get('secretKey')
                status.update(f"[{HTOOL_COLORS['neon_blue']}]Checking account {uid}...[/{HTOOL_COLORS['neon_blue']}]")
                build, _, _ = fetch_balances_3games(uid=uid, secret=skey)
                if build is not None:
                    balance_str = f"[bold {HTOOL_COLORS['emerald']}]{build:,.4f}[/bold {HTOOL_COLORS['emerald']}]"
                    status_str = f"[{HTOOL_COLORS['emerald']}]✅ Online[/{HTOOL_COLORS['emerald']}]"
                else:
                    balance_str = f"[{HTOOL_COLORS['ruby']}]❌ Error[/{HTOOL_COLORS['ruby']}]"
                    status_str = f"[{HTOOL_COLORS['ruby']}]❌ Offline[/{HTOOL_COLORS['ruby']}]"
                table.add_row(str(i), str(uid), balance_str, status_str)
        console.print(table)
        console.print()
        choices = [str(i) for i in range(1, len(accounts) + 1)]
        choice_str = Prompt.ask(f"[bold {HTOOL_COLORS['gold']}]>> Select account number[/bold {HTOOL_COLORS['gold']}]", choices=choices, default="")
        if not choice_str:
            return False
        try:
            choice_idx = int(choice_str) - 1
            if 0 <= choice_idx < len(accounts):
                selected_account = accounts[choice_idx]
                USER_ID = selected_account['userId']
                SECRET_KEY = selected_account['secretKey']
                console.print(Panel(Align.center(Text.assemble((f"{ICONS['check']} ", "bold green"), (f"Đã chọn tài khoản: ", "bold white"), (f"{USER_ID}", f"bold {HTOOL_COLORS['gold']}"))), border_style=HTOOL_COLORS["emerald"], box=box.ROUNDED))
                time.sleep(1.5)
                return True
            else:
                console.print("[red]❌ Invalid selection![/red]")
                time.sleep(1)
                return False
        except ValueError:
            console.print("[red]❌ Invalid input![/red]")
            time.sleep(1)
            return False

# ================== MAIN PROGRAM ==================

def main_vth():
    global _in_menu, _is_authenticated, _user_key, _key_type

    migrate_old_data()

    while not _is_authenticated:
        success, key, key_type = show_auth_choice_menu()
        if success:
            _is_authenticated = True
            _user_key = key
            _key_type = key_type
            break

        console.print()
        retry = Prompt.ask(
            "[bold yellow]Bạn có muốn thử lại không? (y/n)[/bold yellow]",
            choices=['y', 'n'],
            default='y'
        )
        if retry.lower() == 'n':
            console.print("[red]👋 Tạm biệt![/red]")
            return

    console.clear()
    welcome = Panel(
        Align.center(Text.assemble(
            (f"{ICONS['crown']} ", f"bold {HTOOL_COLORS['gold']}"),
            ("WELCOME TO ", "bold white"),
            ("HTOOL VIP PREMIUM", f"bold {HTOOL_COLORS['neon_blue']}"),
            (f" {ICONS['crown']}", f"bold {HTOOL_COLORS['gold']}")
        )),
        border_style=HTOOL_COLORS["gold"],
        box=box.DOUBLE
    )
    console.print(welcome)
    console.print("[dim]💬 Support: @htool88 | Version 3.0 Premium[/dim]")
    console.print(f"[dim]🔑 Đã xác thực với key: {_user_key} ({_key_type})[/dim]")
    if _key_type == "free":
        console.print("[dim]📌 FREE: 10 AI · Lotto 5 AI[/dim]")
    console.print()
    time.sleep(1)

    while True:
        global stop_flag
        stop_flag = False
        choice = build_main_menu()

        if choice == '1':
            console.clear()
            if select_account_premium():
                if prompt_settings():
                    start_game_flow()

        elif choice == '2':
            main_cdtd_v3()

        elif choice == '3':
            console.print("[yellow]⚠️ Chức năng WINHASH LOTTO chưa có hàm xử lý trong file hiện tại.[/yellow]")
            console.print("[dim]FREE key: tối đa 5 AI Lotto | VIP: full AI[/dim]")
            time.sleep(2)

        elif choice == '4':
            accounts = load_accounts()
            add_new_account(accounts)

        elif choice == '5':
            accounts = load_accounts()
            delete_account(accounts)

        elif choice == '6':
            console.clear()
            if prompt_settings():
                save_strategy_config()
            time.sleep(2)

        elif choice == '7':
            console.clear()
            if select_account_premium():
                if load_strategy_config():
                    start_game_flow()
                else:
                    time.sleep(2)

        elif choice == '8':
            console.clear()
            if _secure_tool:
                _secure_tool.display_status()
            else:
                console.print("[yellow]🛡️ Anti-Detection chưa được bật.[/yellow]")
            input("\n[dim]Nhấn Enter để tiếp tục...[/dim]")

        elif choice == 'q':
            stop_heartbeat()
            stop_flag = True
            console.print(
                Panel(
                    Align.center(Text.assemble(
                        (f"{ICONS['crown']} ", "bold gold"),
                        ("THANK YOU FOR USING HTOOL VIP PREMIUM!", "bold white"),
                        (f" {ICONS['crown']}", "bold gold")
                    )),
                    border_style=HTOOL_COLORS["gold"],
                    box=box.DOUBLE
                )
            )
            break


if __name__ == "__main__":
    try:
        main_vth()
    except KeyboardInterrupt:
        stop_flag = True
        stop_heartbeat()
        console.print(
            f"\n[bold {HTOOL_COLORS['gold']}]Đã dừng. {ICONS['crown']}[/bold {HTOOL_COLORS['gold']}]"
        )
        sys.exit(0)
