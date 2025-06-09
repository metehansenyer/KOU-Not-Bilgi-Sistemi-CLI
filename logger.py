#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Günlük Kaydı Modülü
Rich konsol entegrasyonu ile merkezi günlük kayıt sistemi
"""

import logging
from rich.console import Console
from rich.logging import RichHandler

from config import LOG_LEVEL, LOG_FILE, PRODUCTION_MODE, SHOW_USER_LOGS

# Güzel günlük kaydı için Rich konsolu
console = Console()

class KOULogger:
    """Üretim/geliştirme modları ile merkezi günlük kayıt sistemi"""
    
    def __init__(self, name: str = "KOU"):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, LOG_LEVEL.upper(), logging.INFO))
        self.production_mode = PRODUCTION_MODE
        
        # Mevcut işleyicileri temizle
        self.logger.handlers.clear()
        
        # Konsol için Rich işleyicisi (renkli çıktı)
        rich_handler = RichHandler(
            console=console,
            show_time=not self.production_mode,
            show_path=not self.production_mode,
            rich_tracebacks=True
        )
        
        # Konsol için uygun günlük seviyesini ayarla
        if self.production_mode:
            rich_handler.setLevel(logging.ERROR)  # Üretimde sadece hatalar
        else:
            rich_handler.setLevel(logging.INFO)
        
        # Kalıcı günlük kaydı için dosya işleyicisi
        if LOG_FILE:
            file_handler = logging.FileHandler(LOG_FILE, encoding='utf-8')
            file_handler.setLevel(logging.DEBUG)
            
            file_formatter = logging.Formatter(
                '%(asctime)s - %(name)s - %(levelname)s - %(filename)s:%(lineno)d - %(message)s'
            )
            file_handler.setFormatter(file_formatter)
            self.logger.addHandler(file_handler)
        
        console_formatter = logging.Formatter('%(message)s')
        rich_handler.setFormatter(console_formatter)
        self.logger.addHandler(rich_handler)
    
    def info(self, message: str):
        """Bilgi mesajını kaydet (üretimde gizlenir)"""
        if SHOW_USER_LOGS:
            self.logger.info(message)
    
    def error(self, message: str, exc_info: bool = False):
        """Hata mesajını kaydet (her zaman gösterilir)"""
        self.logger.error(message, exc_info=exc_info)
    
    def user_message(self, message: str, style: str = "cyan"):
        """Kullanıcıya temiz mesaj göster (her zaman gösterilir)"""
        console.print(f"[{style}]{message}[/{style}]")
    
    def user_success(self, message: str):
        """Kullanıcıya başarı mesajı göster (her zaman gösterilir)"""
        console.print(f"✅ [green]{message}[/green]")
    
    def user_error(self, message: str):
        """Kullanıcıya hata mesajı göster (her zaman gösterilir)"""
        console.print(f"❌ [red]{message}[/red]")
    
    def user_warning(self, message: str):
        """Kullanıcıya uyarı mesajı göster (her zaman gösterilir)"""
        console.print(f"⚠️ [yellow]{message}[/yellow]")
    
    def internal_progress(self, message: str):
        """İç ilerleme mesajı (üretimde gizlenir)"""
        if SHOW_USER_LOGS:
            console.print(f"⏳ [dim]{message}[/dim]")

# Global günlük kaydı örneği
logger = KOULogger()

# Kolaylık fonksiyonları
def log_info(message: str):
    """Bilgi mesajını kaydet"""
    logger.info(message)

def log_error(message: str, exc_info: bool = False):
    """Hata mesajını kaydet"""
    logger.error(message, exc_info=exc_info)

def user_message(message: str, style: str = "cyan"):
    """Kullanıcıya mesaj göster"""
    logger.user_message(message, style)

def user_success(message: str):
    """Kullanıcıya başarı mesajı göster"""
    logger.user_success(message)

def user_error(message: str):
    """Kullanıcıya hata mesajı göster"""
    logger.user_error(message)

def user_warning(message: str):
    """Kullanıcıya uyarı mesajı göster"""
    logger.user_warning(message)

def internal_progress(message: str):
    """İç ilerleme mesajı"""
    logger.internal_progress(message) 