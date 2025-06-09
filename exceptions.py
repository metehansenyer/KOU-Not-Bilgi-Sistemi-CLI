#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Özel İstisna Sınıfları
Daha iyi hata yönetimi için özelleştirilmiş istisna sınıfları
"""

class KOUException(Exception):
    """KOU Not Bilgi Sistemi için temel istisna sınıfı"""
    
    def __init__(self, message: str, error_code: str = None):
        self.message = message
        self.error_code = error_code
        super().__init__(self.message)
    
    def __str__(self):
        if self.error_code:
            return f"[{self.error_code}] {self.message}"
        return self.message


class AuthenticationError(KOUException):
    """Kimlik doğrulama ile ilgili hatalar"""
    
    def __init__(self, message: str = "Kimlik doğrulama hatası"):
        super().__init__(message, "AUTH_ERROR")


class LoginFailedError(AuthenticationError):
    """Giriş hatası"""
    
    def __init__(self, message: str = "Giriş başarısız - Kullanıcı adı veya şifre hatalı"):
        super().__init__(message)
        self.error_code = "LOGIN_FAILED"


class SessionError(KOUException):
    """Oturum yönetimi hataları"""
    
    def __init__(self, message: str = "Oturum hatası"):
        super().__init__(message, "SESSION_ERROR")


class SessionExpiredError(SessionError):
    """Oturum süresi dolması hatası"""
    
    def __init__(self, message: str = "Oturum süresi dolmuş - Yeniden giriş yapın"):
        super().__init__(message)
        self.error_code = "SESSION_EXPIRED"


class NetworkError(KOUException):
    """Ağ bağlantısı ile ilgili hatalar"""
    
    def __init__(self, message: str = "Ağ bağlantısı hatası"):
        super().__init__(message, "NETWORK_ERROR")


class DataError(KOUException):
    """Veri işleme hataları"""
    
    def __init__(self, message: str = "Veri işleme hatası"):
        super().__init__(message, "DATA_ERROR")


class ParseError(DataError):
    """HTML/Veri ayrıştırma hatası"""
    
    def __init__(self, message: str = "Veri ayrıştırma hatası"):
        super().__init__(message)
        self.error_code = "PARSE_ERROR"


class ValidationError(KOUException):
    """Giriş doğrulama hataları"""
    
    def __init__(self, message: str = "Geçersiz veri girişi"):
        super().__init__(message, "VALIDATION_ERROR")


class WebDriverError(KOUException):
    """WebDriver ile ilgili hatalar"""
    
    def __init__(self, message: str = "WebDriver hatası"):
        super().__init__(message, "WEBDRIVER_ERROR")


class CaptchaError(AuthenticationError):
    """reCAPTCHA ile ilgili hatalar"""
    
    def __init__(self, message: str = "reCAPTCHA doğrulaması başarısız"):
        super().__init__(message)
        self.error_code = "CAPTCHA_ERROR"


class TimeoutError(NetworkError):
    """İstek zaman aşımı hatası"""
    
    def __init__(self, message: str = "İstek zaman aşımına uğradı"):
        super().__init__(message)
        self.error_code = "TIMEOUT_ERROR"


class ServerError(NetworkError):
    """Sunucu hatası"""
    
    def __init__(self, message: str = "Sunucu hatası", status_code: int = None):
        super().__init__(message)
        self.status_code = status_code
        self.error_code = "SERVER_ERROR"
    
    def __str__(self):
        if self.status_code:
            return f"[{self.error_code}] {self.message} (HTTP {self.status_code})"
        return super().__str__()


class NoDataFoundError(DataError):
    """Veri bulunamama hatası"""
    
    def __init__(self, message: str = "Veri bulunamadı"):
        super().__init__(message)
        self.error_code = "NO_DATA_FOUND"


class ConfigurationError(KOUException):
    """Yapılandırma hataları"""
    
    def __init__(self, message: str = "Konfigürasyon hatası"):
        super().__init__(message, "CONFIG_ERROR")


class ElementNotFoundError(WebDriverError):
    """Web elementi bulunamama hatası"""
    
    def __init__(self, element: str, message: str = None):
        if not message:
            message = f"Web elementi bulunamadı: {element}"
        super().__init__(message)
        self.element = element
        self.error_code = "ELEMENT_NOT_FOUND"


class ExportError(KOUException):
    """Dışa aktarma ile ilgili hatalar"""
    
    def __init__(self, message: str = "Veri dışa aktarma hatası"):
        super().__init__(message, "EXPORT_ERROR")


# Yerelleştirme için hata kodu eşleştirmesi
ERROR_MESSAGES = {
    "AUTH_ERROR": "Kimlik doğrulama hatası",
    "LOGIN_FAILED": "Giriş başarısız",
    "CAPTCHA_ERROR": "reCAPTCHA doğrulaması başarısız",
    "SESSION_ERROR": "Oturum hatası",
    "SESSION_EXPIRED": "Oturum süresi dolmuş",
    "NETWORK_ERROR": "Ağ bağlantısı hatası",
    "TIMEOUT_ERROR": "Zaman aşımı hatası",
    "SERVER_ERROR": "Sunucu hatası",
    "DATA_ERROR": "Veri işleme hatası",
    "PARSE_ERROR": "Veri ayrıştırma hatası",
    "NO_DATA_FOUND": "Veri bulunamadı",
    "VALIDATION_ERROR": "Geçersiz veri girişi",
    "CONFIG_ERROR": "Konfigürasyon hatası",
    "WEBDRIVER_ERROR": "WebDriver hatası",
    "ELEMENT_NOT_FOUND": "Web elementi bulunamadı",
    "EXPORT_ERROR": "Veri dışa aktarma hatası"
}


def get_error_message(error_code: str) -> str:
    """Yerelleştirilmiş hata mesajını al"""
    return ERROR_MESSAGES.get(error_code, "Bilinmeyen hata")


def handle_exception(func):
    """İstisnaları uygun günlük kaydıyla ele alan dekoratör"""
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except KOUException:
            # KOU istisnalarını olduğu gibi yeniden fırlat
            raise
        except Exception as e:
            # Genel istisnaları KOUException'a dönüştür
            raise KOUException(f"Beklenmeyen hata: {str(e)}", "UNEXPECTED_ERROR") from e
    return wrapper 