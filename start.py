#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Kullanıcı Başlatma Scripti
"""

import os
import sys

# Üretim modunu etkinleştir
os.environ['KOU_PRODUCTION'] = 'true'

# Ana programı başlat
if __name__ == '__main__':
    try:
        from kou_main import main
        main()
    except ImportError as e:
        print("❌ Gerekli modüller bulunamadı!")
        print("Lütfen 'pip install -r requirements.txt' komutunu çalıştırın")
        sys.exit(1)
    except Exception as e:
        print(f"❌ Program başlatılamadı: {e}")
        sys.exit(1) 