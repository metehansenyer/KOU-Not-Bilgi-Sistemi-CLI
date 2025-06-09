#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Optimize Edilmiş Yardımcı Fonksiyonlar
Önbellekleme ve optimizasyonlarla yüksek performanslı yardımcı fonksiyonlar
"""

import os
import re
import json
import hashlib
import time
from pathlib import Path
from typing import Dict, Any, Optional

from logger import internal_progress, user_success, user_error


def clean_text(text: str) -> str:
    """Metni verimli bir şekilde temizle ve normalleştir"""
    if not text:
        return ""
    
    # Derlenmiş regex ile tek geçişli temizleme
    cleaned = re.sub(r'\s+', ' ', str(text)).strip()
    return cleaned.replace('\n', ' ').replace('\t', ' ')


def ensure_data_directory(data_dir: str) -> Path:
    """Veri dizininin optimize edilmiş oluşturma ile var olduğundan emin ol"""
    try:
        data_path = Path(data_dir)
        data_path.mkdir(parents=True, exist_ok=True)
        return data_path
    except Exception as e:
        user_error(f"Dizin oluşturma hatası: {e}")
        raise


def get_data_file_path(username: str, data_dir: str) -> Path:
    """Kullanıcı için optimize edilmiş veri dosyası yolunu al"""
    data_path = ensure_data_directory(data_dir)
    
    # Gizlilik ve dosya sistemi uyumluluğu için hash kullan
    username_hash = hashlib.md5(username.encode()).hexdigest()[:12]
    filename = f"user_{username_hash}.json"
    
    file_path = data_path / filename
    
    # Hata ayıklama için gerçek yolu günlüğe kaydet
    internal_progress(f"Veri dosya yolu: {file_path.absolute()}")
    
    return file_path


def save_user_data(username: str, data: Dict[str, Any], data_dir: str) -> bool:
    """Yüksek performans optimizasyonları ile kullanıcı verilerini kaydet"""
    try:
        file_path = get_data_file_path(username, data_dir)
        
        # Performans takibi için metadata ekle
        optimized_data = {
            "metadata": {
                "username": username,
                "last_updated": time.time(),
                "version": "6.1.4",
                "total_semesters": len(data),
                "total_courses": sum(len(semester_data.get("courses", [])) for semester_data in data.values())
            },
            "semesters": data
        }
        
        # Hızlı JSON serileştirme
        start_time = time.time()
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(optimized_data, f, ensure_ascii=False, indent=2, separators=(',', ':'))
        
        save_time = time.time() - start_time
        file_size = file_path.stat().st_size
        
        internal_progress(f"💾 Veri kaydedildi: {file_size/1024:.1f}KB ({save_time:.2f}s)")
        user_success(f"Veriler kaydedildi: {file_path.name}")
        
        return True
        
    except Exception as e:
        user_error(f"Veri kaydetme hatası: {e}")
        return False


def load_user_data(username: str, data_dir: str) -> Optional[Dict[str, Any]]:
    """Önbellekleme ve doğrulama ile kullanıcı verilerini yükle"""
    try:
        file_path = get_data_file_path(username, data_dir)
        
        if not file_path.exists():
            return None
        
        # Boyut kontrolü ile hızlı yükleme
        file_size = file_path.stat().st_size
        if file_size == 0:
            internal_progress("Boş veri dosyası siliniyor...")
            file_path.unlink()
            return None
        
        start_time = time.time()
        
        with open(file_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        load_time = time.time() - start_time
        
        # Veri yapısını doğrula
        if not isinstance(data, dict) or "semesters" not in data:
            internal_progress("Geçersiz veri formatı, siliniyor...")
            file_path.unlink()
            return None
        
        # Metadata kontrol et
        metadata = data.get("metadata", {})
        total_semesters = metadata.get("total_semesters", 0)
        total_courses = metadata.get("total_courses", 0)
        
        internal_progress(f"📂 Veri yüklendi: {file_size/1024:.1f}KB, {total_semesters} dönem, {total_courses} ders ({load_time:.3f}s)")
        
        return data["semesters"]
        
    except Exception as e:
        internal_progress(f"Veri yükleme hatası: {e}")
        return None


def has_user_data(username: str, data_dir: str) -> bool:
    """Kullanıcının önbelleğe alınmış verisi olup olmadığını hızlıca kontrol et"""
    try:
        file_path = get_data_file_path(username, data_dir)
        return file_path.exists() and file_path.stat().st_size > 0
    except:
        return False


def get_user_data_info(username: str, data_dir: str) -> Optional[Dict[str, Any]]:
    """Kullanıcının önbelleğe alınmış verisi hakkında hızlı bilgi al"""
    try:
        file_path = get_data_file_path(username, data_dir)
        
        if not file_path.exists():
            return None
        
        stat = file_path.stat()
        
        # Tam dosyayı yüklemeden metadata okumaya çalış
        with open(file_path, 'r', encoding='utf-8') as f:
            # Metadata'yı almak için sadece başlangıcı oku
            chunk = f.read(512)
            if '"metadata"' in chunk:
                f.seek(0)
                try:
                    data = json.load(f)
                    metadata = data.get("metadata", {})
                    
                    return {
                        "file_size": stat.st_size,
                        "last_modified": stat.st_mtime,
                        "last_updated": metadata.get("last_updated"),
                        "version": metadata.get("version"),
                        "total_semesters": metadata.get("total_semesters", 0),
                        "total_courses": metadata.get("total_courses", 0)
                    }
                except:
                    pass
        
        # Yedek bilgi
        return {
            "file_size": stat.st_size,
            "last_modified": stat.st_mtime,
            "total_semesters": "bilinmiyor",
            "total_courses": "bilinmiyor"
        }
        
    except:
        return None


def clear_user_data(username: str, data_dir: str) -> bool:
    """Kullanıcının önbelleğe alınmış verisini temizle"""
    try:
        file_path = get_data_file_path(username, data_dir)
        
        if file_path.exists():
            file_path.unlink()
            internal_progress("Önbellek temizlendi")
            return True
        
        return False
        
    except Exception as e:
        user_error(f"Önbellek temizleme hatası: {e}")
        return False


def format_file_size(size_bytes: int) -> str:
    """Dosya boyutunu görüntüleme için biçimlendir"""
    if size_bytes < 1024:
        return f"{size_bytes}B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes/1024:.1f}KB"
    else:
        return f"{size_bytes/(1024*1024):.1f}MB"


def format_time_ago(timestamp: float) -> str:
    """Zaman damgasını ne kadar zaman önce olarak biçimlendir"""
    if not timestamp:
        return "bilinmiyor"
    
    try:
        diff = time.time() - timestamp
        
        if diff < 60:
            return f"{int(diff)} saniye önce"
        elif diff < 3600:
            return f"{int(diff/60)} dakika önce"
        elif diff < 86400:
            return f"{int(diff/3600)} saat önce"
        else:
            return f"{int(diff/86400)} gün önce"
    except:
        return "bilinmiyor"


# Sık kullanılan işlemler için önbellek
_text_cache = {}

def cached_clean_text(text: str) -> str:
    """Tekrarlanan dizeler için clean_text'in önbellekli versiyonu"""
    if not text:
        return ""
    
    if text in _text_cache:
        return _text_cache[text]
    
    cleaned = clean_text(text)
    
    # Önbellek boyutunu sınırla
    if len(_text_cache) > 1000:
        _text_cache.clear()
    
    _text_cache[text] = cleaned
    return cleaned 