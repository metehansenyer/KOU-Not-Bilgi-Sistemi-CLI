# KOU Not Bilgi Sistemi CLI

Kocaeli Üniversitesi öğrenci bilgi sisteminden otomatik not çekme ve offline erişim aracı. Veri toplama ile hızlı offline erişim sağlar.

# İçerik

- [Kullanılan Araçlar](#kullanılan-araçlar)
- [Amaç](#amaç)
- [Proje Özellikleri](#proje-özellikleri)
- [Teknik Detaylar](#teknik-detaylar)
- [İndirme ve Çalıştırma](#i̇ndirme-ve-çalıştırma)
- [Kullanım](#kullanım)
- [Proje Yapısı](#proje-yapısı)
- [Not](#not)

## Kullanılan Araçlar

<p align="center">
  <a href="https://www.python.org/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/python/python-original.svg" alt="python" width="40" height="40"/> </a>
  <a href="https://selenium-python.readthedocs.io/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/selenium/selenium-original.svg" alt="selenium" width="40" height="40"/> </a>
  <a href="https://www.google.com/chrome/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/chrome/chrome-original.svg" alt="chrome" width="40" height="40"/> </a>
  <a href="https://code.visualstudio.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/vscode/vscode-original.svg" alt="vscode" width="40" height="40"/> </a>
  <a href="https://github.com/" target="_blank" rel="noreferrer"> <img src="https://raw.githubusercontent.com/devicons/devicon/master/icons/github/github-original.svg" alt="github" width="40" height="40"/> </a>
</p>

- **Web Automation**: Selenium WebDriver ile tarayıcı otomasyonu
- **UI Framework**: Rich library ile güzel konsol arayüzü
- **Data Processing**: BeautifulSoup ve JSON ile veri işleme
- **Session Management**: Cookie-based oturum yönetimi
- **Performance**: JavaScript tabanlı hızlı parsing

| Kullanılan Araç | Sürüm | Amaç |
|:---:|:---:|:---:|
| Python | 3.8+ | Ana programlama dili |
| Selenium | 4.15.0+ | Web otomasyonu |
| Rich | 13.7.0+ | Konsol arayüzü |
| Chrome WebDriver | Latest | Tarayıcı kontrolü |
| Requests | 2.31.0+ | HTTP istekleri |
| BeautifulSoup4 | 4.12.2+ | HTML parsing |

## Amaç

Bir hobi projesi olarak Öğrenci Bilgi Sisteminden verileri çekip çekemeyeceğimi kontrol etmek isterken kendimi burada buldum.

## Proje Özellikleri

```json
{
  "Veri Toplama": "Tüm dönemlerin verilerini toplar ve offline kullanım için saklar",
  "Session Management": "Cookie-based oturum saklama ve yeniden kullanım",
  "Ultra-Fast Offline Access": "Sonraki kullanımlarda < 1 saniye erişim",
  "On-Demand Data Update": "Menüden tek tıkla sunucudan fresh veri güncelleme",
  "Detaylı Ders Bilgileri": "Öğretim elemanı, etkinlikler, notlar ve tüm detaylar",
  "JavaScript-Based Parsing": "Ultra-hızlı veri çıkarma teknolojisi",
  "Rich Console Interface": "Güzel ve kullanıcı dostu konsol arayüzü",
  "Secure Data Storage": "Şifreler saklanmaz, sadece oturum bilgileri",
  "Automatic Cache Management": "Akıllı önbellek yönetimi",
  "Cross-Platform Support": "Windows, macOS, Linux desteği"
}
```

## Teknik Detaylar

| Özellik | Durum | Detay |
|:---:|:---:|:---:|
| Session Management ve reCAPTCHA Bypass | ✅ | İlk girişten sonra Cookie-based oturum saklama ve yeniden kullanım |
| Ultra-Fast Parsing | ✅ | JavaScript tabanlı DOM manipulation |
| Offline Data Access | ✅ | JSON formatında lokal veri saklama |
| Rich Console UI | ✅ | Progress bar, tablo ve renkli çıktılar |
| Error Handling | ✅ | Kapsamlı hata yönetimi ve user-friendly mesajlar |
| Performance Optimization | ✅ | Cache sistemi ve paralel işlem |
| Modular Architecture | ✅ | Temiz kod yapısı ve maintainability |

## İndirme ve Çalıştırma

Projeyi yerel ortamınızda çalıştırmak için aşağıdaki adımları izleyebilirsiniz:

1. **Repoyu klonlayın:**
```bash
git clone https://github.com/metehansenyer/KOU-Not-Bilgi-Sistemi-CLI.git
cd KOU-Not-Bilgi-Sistemi-CLI
```

2. **Sanal ortam (Virtual Environment) oluşturun ve etkinleştirin:**

**Windows için:**
```bash
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux için:**
```bash
python -m venv venv
source venv/bin/activate
```

3. **Gerekli paketleri yükleyin:**
```bash
pip install -r requirements.txt
```

4. **Chrome tarayıcısının güncel olduğundan emin olun** (WebDriver otomatik indirilir)

5. **Programı çalıştırın:**
```bash
python start.py
```

## Kullanım

### İlk Kullanım
1. Programı çalıştırın
2. KOU öğrenci numaranızı (9 haneli) girin
3. Parolanızı girin  
4. reCAPTCHA'yı çözün ve giriş yapın
5. Program tüm dönemlerinizin verilerini toplayacak (~2-5 dakika)
6. Veriler `.kou_sessions/data/` dizininde saklanır

### Sonraki Kullanımlar
1. Programı çalıştırın
2. Öğrenci numaranızı girin
3. **< 1 saniye** içinde verileriniz yüklenir
4. **4 ana menü seçeneği:**
   - **1.** 📊 Güncel dönem notları
   - **2.** 📅 Dönem seçerek görüntüleme
   - **3.** 🔄 Verileri güncelle
   - **4.** ❌ Çıkış

## Proje Yapısı

```
KOU-Not-Bilgi-Sistemi-CLI/
├── config.py              # Konfigürasyon ayarları
├── exceptions.py           # Özel hata sınıfları  
├── logger.py              # Loglama sistemi
├── utils.py               # Yardımcı fonksiyonlar
├── session_manager.py     # Session ve cookie yönetimi
├── main_with_session.py   # Selenium ile veri toplama
├── kou_main.py           # Ana program ve offline arayüz
├── start.py              # Production başlatıcı
├── requirements.txt      # Python bağımlılıkları
├── .gitignore           # Git ignore kuralları
├── LICENSE              # MIT lisansı
└── README.md            # Bu dosya
```

### Modül Açıklaması
- **`kou_main.py`**: Ana kullanıcı arayüzü ve offline veri erişimi
- **`main_with_session.py`**: Selenium ile KOU sistemine bağlanma ve veri toplama
- **`session_manager.py`**: Cookie'leri saklama ve oturum yönetimi
- **`utils.py`**: Veri saklama, yükleme ve temizleme fonksiyonları
- **`logger.py`**: Production/Development mod logging sistemi
- **`config.py`**: Tüm konfigürasyon ayarları

### Veri Depolama
```
.kou_sessions/
├── data/
│   └── user_a1b2c3d4e5f6.json    # Kullanıcı dosyası
├── username_cookies.pkl          # Session cookies
├── username_session.json         # Session metadata
└── kou_client.log               # Log dosyası
```

---

## Not
**Not**: Bu araç eğitim amaçlıdır ve KOU'nun resmi uygulaması değildir. Kullanım sorumluluğu kullanıcıya aittir. 