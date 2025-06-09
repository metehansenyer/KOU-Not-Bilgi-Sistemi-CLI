#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Konfigürasyon Modülü
Merkezi ayar yönetimi için kullanılır
"""

import os
from pathlib import Path
from typing import Dict, Any

# Uygulama Bilgileri
APP_NAME = "KOU Student System"
APP_VERSION = "6.1.4"
APP_DESCRIPTION = "Kocaeli Üniversitesi öğrenci bilgi sistemi için otomatik not çekme aracı"

# Üretim/Geliştirme Modu
PRODUCTION_MODE = os.getenv('KOU_PRODUCTION', 'true').lower() == 'true'

# URL'ler
BASE_URL = 'https://ogr.kocaeli.edu.tr/KOUBS/ogrenci/index.cfm'
MAIN_PAGE_URL = 'https://ogr.kocaeli.edu.tr/KOUBS/Ogrenci/AnaGiris.cfm'

# Zaman Aşımları (saniye)
DEFAULT_TIMEOUT = 15
PAGE_LOAD_TIMEOUT = 30
SESSION_TIMEOUT_HOURS = 2

# Chrome Seçenekleri
CHROME_OPTIONS = {
    'headless': False,
    'no_sandbox': True,
    'disable_dev_shm_usage': True,
    'disable_gpu': True,
    'disable_extensions': True,
    'log_level': 3
}

# Kullanıcı Ajanı
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/137.0.7151.41 Safari/537.36'

# Oturum Yönetimi
# Ana dizin yerine yerel dizini kullan
PROJECT_ROOT = Path(__file__).parent
SESSION_DIR = PROJECT_ROOT / ".kou_sessions"
SESSION_DIR.mkdir(exist_ok=True)

# Veri Depolama
DATA_DIR = SESSION_DIR / "data"
DATA_DIR.mkdir(exist_ok=True)

# Günlük Kaydı Yapılandırması
if PRODUCTION_MODE:
    LOG_LEVEL = 'WARNING'
    SHOW_USER_LOGS = False
else:
    LOG_LEVEL = 'INFO'
    SHOW_USER_LOGS = True

LOG_FILE = SESSION_DIR / "kou_client.log"

# Dışa Aktarma Ayarları
DEFAULT_EXPORT_FORMAT = 'json'
EXPORT_TIMESTAMP = True

# Ortam Değişkenleri
def get_env_config() -> Dict[str, Any]:
    """Ortam değişkenlerinden yapılandırma bilgilerini al"""
    return {
        'headless': os.getenv('KOU_HEADLESS', 'false').lower() == 'true',
        'timeout': int(os.getenv('KOU_TIMEOUT', str(DEFAULT_TIMEOUT))),
        'production': PRODUCTION_MODE
    }

# Yapılandırmayı doğrula
def validate_config():
    """Yapılandırma ayarlarını doğrula"""
    if not SESSION_DIR.exists():
        SESSION_DIR.mkdir(parents=True, exist_ok=True)
    
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(parents=True, exist_ok=True)
    
    if DEFAULT_TIMEOUT <= 0:
        raise ValueError("Timeout değeri pozitif olmalı")

# Yapılandırmayı başlat
validate_config() 