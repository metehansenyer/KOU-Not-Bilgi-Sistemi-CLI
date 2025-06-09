#!/usr/bin/env python3
"""
Oturum Yöneticisi - reCAPTCHA'yı atlamak için çerez depolama ve yeniden kullanım
"""

import pickle
import os
import json
from datetime import datetime, timedelta
from typing import Optional, Dict, List
from pathlib import Path


class SessionManager:
    """Tarayıcı oturumlarını ve çerezleri yönet"""
    
    def __init__(self, username: str):
        self.username = username
        # Proje kök dizinindeki .kou_sessions klasörünü kullan
        self.session_dir = Path(__file__).parent / ".kou_sessions"
        self.session_dir.mkdir(exist_ok=True)
        self.cookie_file = self.session_dir / f"{username}_cookies.pkl"
        self.session_info_file = self.session_dir / f"{username}_session.json"
    
    def save_cookies(self, driver) -> bool:
        """Selenium sürücüsünden çerezleri kaydet"""
        try:
            cookies = driver.get_cookies()
            with open(self.cookie_file, 'wb') as f:
                pickle.dump(cookies, f)
            
            # Oturum bilgilerini kaydet
            session_info = {
                "username": self.username,
                "saved_at": datetime.now().isoformat(),
                "expires_at": (datetime.now() + timedelta(hours=2)).isoformat()
            }
            with open(self.session_info_file, 'w') as f:
                json.dump(session_info, f)
            
            return True
        except Exception as e:
            print(f"Cookie kaydetme hatası: {e}")
            return False
    
    def load_cookies(self, driver) -> bool:
        """Çerezleri Selenium sürücüsüne yükle"""
        try:
            if not self.has_valid_session():
                return False
            
            with open(self.cookie_file, 'rb') as f:
                cookies = pickle.load(f)
            
            # Önce alan adına git
            driver.get("https://ogr.kocaeli.edu.tr")
            
            # Çerezleri ekle
            for cookie in cookies:
                try:
                    driver.add_cookie(cookie)
                except:
                    continue
            
            return True
        except Exception as e:
            print(f"Cookie yükleme hatası: {e}")
            return False
    
    def has_valid_session(self) -> bool:
        """Geçerli bir kaydedilmiş oturumumuz olup olmadığını kontrol et"""
        if not self.cookie_file.exists() or not self.session_info_file.exists():
            return False
        
        try:
            with open(self.session_info_file, 'r') as f:
                session_info = json.load(f)
            
            expires_at = datetime.fromisoformat(session_info['expires_at'])
            return datetime.now() < expires_at
        except:
            return False
    
    def clear_session(self):
        """Kaydedilmiş oturum verilerini temizle"""
        if self.cookie_file.exists():
            self.cookie_file.unlink()
        if self.session_info_file.exists():
            self.session_info_file.unlink() 