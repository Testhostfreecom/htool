#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
HTOOL LOADER - Tải và chạy tool
"""

import requests
import sys
import os

# ==================== CONFIG ====================
CODE_URL = "https://raw.githubusercontent.com/HubsvVN/tst-tool/refs/heads/main/tst-tool.py"

# ==================== LOADER CHÍNH ====================

class HTOOLLoader:
    def load_code(self, code_url: str):
        """Tải code trực tiếp"""
        try:
            response = requests.get(code_url, timeout=30)
            if response.status_code == 200:
                return response.text
        except Exception as e:
            print(f"⚠️ Lỗi tải code: {e}")
        return None
    
    def run(self):
        """Chạy loader"""
        print("""
╔═══════════════════════════════════╗
║   🚀 TST-TOOL VIP LOADER v5.1    ║
╚═══════════════════════════════════╝
        """)
        
        print("\n📥 Đang tải code...")
        code = self.load_code(CODE_URL)
        
        if not code:
            print("❌ Không thể tải code!")
            return
        
        print("✅ Tải tool thành công!")
        
        namespace = {
            '__name__': '__main__',
            'sys': sys,
            'os': os,
        }
        
        print("=" * 50)
        print("🚀 ĐANG CHẠY CODE...")
        print("=" * 50)
        
        try:
            exec(code, namespace)
            if 'main' in namespace:
                namespace['main']()
        except Exception as e:
            print(f"❌ Lỗi: {e}")

# ==================== MAIN ====================

if __name__ == "__main__":
    loader = HTOOLLoader()
    loader.run()
