#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Oturum Yönetimi Versiyonu
"""

# Uyarıları bastır
import os
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '3'
os.environ['TF_ENABLE_ONEDNN_OPTS'] = '0'

import warnings
warnings.filterwarnings('ignore')

import time
import json
import concurrent.futures
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, asdict

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait, Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.action_chains import ActionChains
from selenium.common.exceptions import TimeoutException, NoSuchElementException, WebDriverException, StaleElementReferenceException
from webdriver_manager.chrome import ChromeDriverManager

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn

# Modülleri içe aktar
from config import BASE_URL, MAIN_PAGE_URL, CHROME_OPTIONS, USER_AGENT, DEFAULT_TIMEOUT, PAGE_LOAD_TIMEOUT, DATA_DIR
from logger import internal_progress, user_message, user_success, user_error, console
from session_manager import SessionManager
from utils import clean_text

__version__ = '6.1.4'

@dataclass
class LoginCredentials:
    """Kullanıcı giriş bilgileri"""
    username: str
    password: str

@dataclass
class CourseActivity:
    """Ders aktivite bilgileri"""
    activity_type: str
    score: str
    percentage: str
    semester_effect: str

@dataclass
class CourseInfo:
    """Tüm ders bilgileri"""
    sequence: str
    code: str
    name: str
    attendance: str
    language: str
    ects: str
    yio: str
    yys: str
    but: str
    bn: str
    bd: str
    instructor: str = ""
    activities: List[CourseActivity] = None
    semester_average: str = ""
    detail_params: str = ""  # Toplu işleme için
    
    def __post_init__(self):
        if self.activities is None:
            self.activities = []
    
    def to_dict(self):
        data = asdict(self)
        # İç işleme alanını kaldır
        if 'detail_params' in data:
            del data['detail_params']
        return data


class KOUDataCollector:
    """Tüm dönem verilerini toplamak için KOU oturumu"""
    
    def __init__(self, headless: bool = False):
        self.driver = None
        self.username = None
        self.headless = headless
        self.session_manager = None
        self.detail_cache = {}  # Ders detayları için önbellek
        self._setup_driver()
        
    def _setup_driver(self):
        """Chrome WebDriver'ı kur"""
        try:
            chrome_options = Options()
            
            if self.headless:
                chrome_options.add_argument('--headless')
            
            # Yapılandırmadan tüm seçenekleri ekle
            for option, value in CHROME_OPTIONS.items():
                if option == 'headless':
                    continue
                elif value is True:
                    chrome_options.add_argument(f'--{option.replace("_", "-")}')
                elif value is False:
                    chrome_options.add_argument(f'--disable-{option.replace("_", "-")}')
                else:
                    chrome_options.add_argument(f'--{option.replace("_", "-")}={value}')
            
            chrome_options.add_argument(f'--user-agent={USER_AGENT}')
            chrome_options.add_experimental_option("excludeSwitches", ["enable-automation", "enable-logging"])
            chrome_options.add_experimental_option('useAutomationExtension', False)
            
            # Sürücü günlüklerini bastır
            import logging
            logging.getLogger('WDM').setLevel(logging.NOTSET)
            os.environ['WDM_LOG'] = "false"
            
            service = Service(ChromeDriverManager().install())
            service.log_path = os.devnull
            
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            self.driver.set_page_load_timeout(PAGE_LOAD_TIMEOUT)
            self.driver.implicitly_wait(2)  # Hız için azaltıldı
            
            # Webdriver özelliğini kaldır
            self.driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
            
            internal_progress("Chrome WebDriver başlatıldı")
            
        except Exception as e:
            user_error(f"WebDriver kurulumu başarısız: {e}")
            raise
    
    def login_with_session(self, credentials: LoginCredentials) -> bool:
        """Oturum yönetimiyle giriş yap"""
        self.username = credentials.username
        self.session_manager = SessionManager(credentials.username)
        
        # Önce kaydedilmiş oturumu dene
        if self.session_manager.has_valid_session():
            user_message("Kaydedilmiş oturum bulundu, yükleniyor...")
            
            try:
                if self.session_manager.load_cookies(self.driver):
                    self.driver.get(MAIN_PAGE_URL)
                    time.sleep(1.5)  # Güvenilirlik için bekleme süresi artırıldı
                    
                    if self._check_login_status(credentials.username):
                        user_success("Kaydedilmiş oturumla giriş başarılı!")
                        return True
                    else:
                        user_message("Kaydedilmiş oturum süresi dolmuş, yeniden giriş yapılıyor...")
                        # Süresi dolmuş oturumu temizle ve giriş sayfasına geri dön
                        self.session_manager.clear_session()
                        self.driver.get(BASE_URL)  # Giriş sayfasına geri dön
                        time.sleep(1)  # Sayfanın yüklenmesi için bekle
            except Exception as e:
                internal_progress(f"Oturum yükleme hatası: {e}")
                user_message("Oturum bilgileri kullanılamıyor, yeni giriş yapılacak...")
                self.session_manager.clear_session()
                self.driver.get(BASE_URL)  # Giriş sayfasına geri dön
                time.sleep(1)  # Sayfanın yüklenmesi için bekle
        
        # Yedek olarak normal giriş
        return self._normal_login(credentials)
    
    def _check_login_status(self, username: str) -> bool:
        """Giriş yapılıp yapılmadığını kontrol et - sağlam uygulama"""
        try:
            # Mevcut URL ve sayfa kaynağını al
            try:
                current_url = self.driver.current_url
            except:
                return False
                
            try:
                page_source = self.driver.page_source
            except:
                page_source = ""
            
            # Giriş göstergelerini tanımla
            login_indicators = [
                "AnaGiris.cfm" in current_url,
                "Çıkış" in page_source,
                "Çıkış Yap" in page_source,
                username in page_source,
                "DersIslemleri" in page_source,
                "Ders İşlemleri" in page_source,
                "OgrenciBilgileri" in page_source
            ]
            
            # Çıkış göstergelerini tanımla
            logout_indicators = [
                "login.cfm" in current_url.lower(),
                "oturum açma" in page_source.lower(),
                "reCAPTCHA" in page_source,
                "OgrNo" in page_source and "Sifre" in page_source
            ]
            
            # Olumlu göstergeleri kontrol et
            if any(login_indicators):
                return True
                
            # Açık çıkış göstergelerini kontrol et
            if any(logout_indicators):
                return False
            
            # Son doğrulama olarak giriş-spesifik bir öğe bulmayı dene
            try:
                # Yalnızca giriş yapıldığında mevcut olan bir kullanıcı bilgisi veya menü öğesi bulmayı dene
                menu_exists = len(self.driver.find_elements(By.ID, "DersIslemleri")) > 0 or \
                             len(self.driver.find_elements(By.ID, "OgrenciBilgileri")) > 0
                if menu_exists:
                    return True
            except:
                pass
                
            return False
            
        except Exception as e:
            internal_progress(f"Login check error: {e}")
            return False
    
    def _normal_login(self, credentials: LoginCredentials) -> bool:
        """reCAPTCHA ile normal giriş"""
        max_retries = 2  # Maksimum giriş deneme sayısı
        for attempt in range(max_retries):
            try:
                internal_progress("KOU login sayfasına bağlanılıyor...")
                # Giriş sayfasında olduğumuzdan emin olalım
                current_url = self.driver.current_url
                if BASE_URL not in current_url:
                    self.driver.get(BASE_URL)
                    time.sleep(1.5)  # Sayfanın yüklenmesi için bekle
                
                # Kimlik bilgilerini gir
                username_field = WebDriverWait(self.driver, DEFAULT_TIMEOUT).until(
                    EC.presence_of_element_located((By.ID, "OgrNo"))
                )
                username_field.clear()
                username_field.send_keys(credentials.username)
                
                password_field = self.driver.find_element(By.ID, "Sifre")
                password_field.clear()
                password_field.send_keys(credentials.password)
                
                if not self.headless:
                    # Kullanıcı dostu mesajlar
                    captcha_message = "reCAPTCHA'yı tamamlayın ve Enter'a basın..."
                    if attempt > 0:
                        captcha_message = "reCAPTCHA'yı tekrar tamamlayın ve Enter'a basın..."
                    
                    user_message(captcha_message)
                    
                    try:
                        # Daha uzun bir zaman aşımı ile girişin tamamlanmasını bekle
                        WebDriverWait(self.driver, 180).until(
                            lambda driver: self._check_login_status(credentials.username)
                        )
                        
                        # Giriş durumunu tekrar kontrol et
                        time.sleep(1.5)  # Sayfanın stabilize olması için bir an bekle
                        if self._check_login_status(credentials.username):
                            user_success("Giriş başarılı!")
                            
                            # Oturumu kaydet
                            if self.session_manager.save_cookies(self.driver):
                                internal_progress("Oturum bilgileri kaydedildi")
                            
                            # Ana sayfada olduğumuzdan emin olalım
                            if "AnaGiris.cfm" not in self.driver.current_url:
                                self.driver.get(MAIN_PAGE_URL)
                                time.sleep(1)  # Sayfanın yüklenmesi için bekle
                            
                            return True
                        else:
                            user_error("Giriş başarısız. Sistem yanıt vermiyor.")
                            continue  # Deneme hakkımız kaldıysa tekrar dene
                    
                    except TimeoutException:
                        if attempt < max_retries - 1:  # Deneme hakkımız kaldıysa
                            user_error("Giriş zaman aşımına uğradı, tekrar deneniyor...")
                            # Çerezleri temizle ve tekrar dene
                            self.driver.delete_all_cookies()
                            self.driver.get(BASE_URL)
                            time.sleep(1)  # Sayfanın yüklenmesi için bekle
                            continue
                        else:
                            user_error("Giriş zaman aşımına uğradı, lütfen daha sonra tekrar deneyin.")
                            return False
                else:
                    user_error("reCAPTCHA için görünür mod gerekli!")
                    return False
                    
            except NoSuchElementException as e:
                user_error(f"Giriş formu bulunamadı: {e}")
                # Giriş formu bulunamazsa, sayfayı yenile ve tekrar dene
                if attempt < max_retries - 1:
                    self.driver.get(BASE_URL)
                    time.sleep(1.5)  # Sayfanın yüklenmesi için bekle
                    continue
                return False
                
            except Exception as e:
                user_error(f"Giriş hatası: {e}")
                if attempt < max_retries - 1:
                    user_message("Tekrar deneniyor...")
                    self.driver.get(BASE_URL)
                    time.sleep(1.5)  # Sayfanın yüklenmesi için bekle
                    continue
                return False
        
        return False  # Buraya ulaşırsak, tüm denemeler başarısız olmuş demektir
    
    def collect_all_semester_data(self) -> Dict[str, List[CourseInfo]]:
        """Tüm dönemlerden veri topla"""
        user_message("Tüm dönem verileri toplanıyor...")
        
        if not self._navigate_to_grades():
            return {}
        
        # Kullanılabilir dönemleri al
        semesters = self._get_available_semesters()
        if not semesters:
            user_error("Dönem bilgileri alınamadı")
            return {}
        
        all_data = {}
        
        with Progress(
            SpinnerColumn(),
            TextColumn("[progress.description]{task.description}"),
            BarColumn(),
            TextColumn("[progress.percentage]{task.percentage:>3.0f}%"),
            TimeElapsedColumn(),
            console=console
        ) as progress:
            
            main_task = progress.add_task("Dönemler işleniyor...", total=len(semesters))
            
            for semester in semesters:
                progress.update(main_task, description=f"İşleniyor: {semester['text']}")
                
                courses = self._load_semester_grades_fast(semester["value"])
                if courses:
                    # Hız için toplu detay çıkarma
                    self._batch_extract_details(courses, progress)
                    
                    all_data[semester["value"]] = {
                        "semester_name": semester["text"],
                        "courses": [course.to_dict() for course in courses]
                    }
                
                progress.update(main_task, advance=1)
        
        user_success(f"Toplam {len(all_data)} dönem verisi toplandı")
        return all_data
    
    def _navigate_to_grades(self) -> bool:
        """Not sayfasına git"""
        try:
            internal_progress("Notlar sayfasına navigasyon...")
            
            current_url = self.driver.current_url
            if "AnaGiris.cfm" not in current_url:
                self.driver.get(MAIN_PAGE_URL)
                time.sleep(1)  # Azaltılmış bekleme
            
            wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
            
            # "Ders İşlemleri" açılır menüsüne tıkla
            ders_islemleri = wait.until(EC.element_to_be_clickable((By.ID, "DersIslemleri")))
            ders_islemleri.click()
            time.sleep(0.3)  # Azaltılmış bekleme
            
            # "Yarıyıl Not Durumu" bağlantısına tıkla
            yaril_not = wait.until(EC.element_to_be_clickable((By.XPATH, "//a[@name='YariyilNotDurumuYeni/DersIslemleri']")))
            yaril_not.click()
            time.sleep(1.5)  # Azaltılmış bekleme
            
            # Sayfanın yüklenip yüklenmediğini kontrol et
            try:
                wait.until(EC.presence_of_element_located((By.ID, "Donem")))
                internal_progress("Notlar sayfası hazır")
                return True
            except TimeoutException:
                try:
                    wait.until(EC.presence_of_element_located((By.ID, "AlinanDersler")))
                    internal_progress("Notlar bölümü hazır")
                    return True
                except TimeoutException:
                    user_error("Notlar sayfası yüklenemedi")
                    return False
                
        except Exception as e:
            user_error(f"Navigasyon hatası: {e}")
            return False
    
    def _get_available_semesters(self) -> List[Dict[str, str]]:
        """Kullanılabilir dönemleri al"""
        try:
            wait = WebDriverWait(self.driver, 5)
            semester_select = wait.until(EC.presence_of_element_located((By.ID, "Donem")))
            
            semesters = []
            options = semester_select.find_elements(By.TAG_NAME, "option")
            
            for option in options:
                try:
                    value = option.get_attribute("value")
                    text = option.text.strip()
                    if value and text:
                        semesters.append({"value": value, "text": text})
                except:
                    continue
            
            return semesters
            
        except Exception as e:
            user_error(f"Dönem bilgileri hatası: {e}")
            return []
    
    def _load_semester_grades_fast(self, semester_value: str) -> List[CourseInfo]:
        """Belirli bir dönem için notları hızlı bir şekilde yükle"""
        try:
            wait = WebDriverWait(self.driver, DEFAULT_TIMEOUT)
            
            # Dönem seç
            semester_select = wait.until(EC.presence_of_element_located((By.ID, "Donem")))
            Select(semester_select).select_by_value(semester_value)
            time.sleep(1.5)  # AJAX için bekle
            
            # Tabloyu bul
            table_selectors = [
                "table.table.table-condensed",
                "table[border='1']",
                "div#AlinanDersler table",
                "table"
            ]
            
            table = None
            for selector in table_selectors:
                try:
                    tables = self.driver.find_elements(By.CSS_SELECTOR, selector)
                    for t in tables:
                        rows = t.find_elements(By.TAG_NAME, "tr")
                        if len(rows) > 1:
                            table = t
                            break
                    if table:
                        break
                except:
                    continue
            
            if not table:
                return []
            
            # JavaScript tabanlı hızlı ayrıştırma
            courses = self._fast_table_parse(table)
            return courses
            
        except Exception as e:
            internal_progress(f"Dönem yükleme hatası: {e}")
            return []
    
    def _fast_table_parse(self, table_element) -> List[CourseInfo]:
        """JavaScript kullanarak hızlı tablo ayrıştırma"""
        courses = []
        
        try:
            internal_progress("⚡ Hızlı tablo parsing...")
            
            # Ultra-hızlı çıkarma için JavaScript
            js_code = """
            var rows = arguments[0].getElementsByTagName('tr');
            var data = [];
            for (var i = 1; i < rows.length; i++) {
                var cells = rows[i].getElementsByTagName('td');
                if (cells.length >= 11) {
                    var nameCell = cells[2];
                    var nameText = nameCell.textContent.trim();
                    var linkElem = nameCell.querySelector('a');
                    var detailParams = linkElem ? linkElem.getAttribute('name') : '';
                    
                    data.push({
                        sequence: cells[0].textContent.trim(),
                        code: cells[1].textContent.trim(),
                        name: nameText.split('\\n')[0],
                        attendance: cells[3].textContent.trim(),
                        language: cells[4].textContent.trim(),
                        ects: cells[5].textContent.trim(),
                        yio: cells[6].textContent.trim(),
                        yys: cells[7].textContent.trim(),
                        but: cells[8].textContent.trim(),
                        bn: cells[9].textContent.trim(),
                        bd: cells[10].textContent.trim(),
                        detailParams: detailParams
                    });
                }
            }
            return data;
            """
            
            # Yıldırım hızında çıkarma için JavaScript çalıştır
            extracted_data = self.driver.execute_script(js_code, table_element)
            
            # CourseInfo nesnelerine dönüştür
            for data in extracted_data:
                course = CourseInfo(
                    sequence=clean_text(data['sequence']),
                    code=clean_text(data['code']),
                    name=clean_text(data['name']),
                    attendance=clean_text(data['attendance']),
                    language=clean_text(data['language']),
                    ects=clean_text(data['ects']),
                    yio=clean_text(data['yio']),
                    yys=clean_text(data['yys']),
                    but=clean_text(data['but']),
                    bn=clean_text(data['bn']),
                    bd=clean_text(data['bd']),
                    detail_params=data['detailParams']
                )
                
                if course.code and course.name:
                    courses.append(course)
            
            internal_progress(f"✅ Hızlı parsing tamamlandı: {len(courses)} ders")
            return courses
            
        except Exception as e:
            internal_progress(f"❌ Hızlı parsing hatası: {e}")
            return []
    
    def _batch_extract_details(self, courses: List[CourseInfo], progress: Progress) -> None:
        """Optimize edilmiş gruplarla paralel işleme ile ders detaylarını çıkar"""
        if not courses:
            return
        
        courses_with_details = [c for c in courses if c.detail_params]
        if not courses_with_details:
            return
        
        detail_task = progress.add_task("Ders detayları çekiliyor...", total=len(courses_with_details))
        
        for course in courses_with_details:
            try:
                # Süper hız için önce önbelleği kontrol et
                if course.detail_params in self.detail_cache:
                    cached_details = self.detail_cache[course.detail_params]
                    course.instructor = cached_details.get("instructor", "")
                    course.activities = cached_details.get("activities", [])
                    course.semester_average = cached_details.get("semester_average", "")
                    progress.update(detail_task, advance=1)
                    continue
                
                # Hızlı detay çıkarma
                details = self._quick_extract_course_details(course.detail_params)
                
                # Dersi güncelle
                course.instructor = details.get("instructor", "")
                course.activities = details.get("activities", [])
                course.semester_average = details.get("semester_average", "")
                
                # Gelecekte kullanım için önbelleğe al
                self.detail_cache[course.detail_params] = details
                
                progress.update(detail_task, advance=1)
                
            except Exception as e:
                progress.update(detail_task, advance=1)
                continue
    
    def _quick_extract_course_details(self, detail_params: str) -> Dict[str, Any]:
        """Ultra-hızlı ders detayı çıkarma"""
        details = {
            "instructor": "",
            "activities": [],
            "semester_average": ""
        }
        
        try:
            # Ders bağlantısını bul ve tıkla
            course_links = self.driver.find_elements(By.XPATH, f"//a[@name='{detail_params}']")
            if course_links:
                course_link = course_links[0]
                course_link.click()
                time.sleep(0.3)  # Minimum bekleme
                
                # Hızlı modal algılama ve çıkarma
                try:
                    wait = WebDriverWait(self.driver, 2)  # Kısa zaman aşımı
                    modal_body = wait.until(EC.presence_of_element_located((By.ID, "ModalBody")))
                    
                    # Ultra-hızlı öğretim elemanı çıkarma
                    try:
                        instructor_elements = modal_body.find_elements(By.CSS_SELECTOR, "h4.alert.alert-info")
                        if instructor_elements:
                            instructor_text = instructor_elements[0].text
                            if "Dersin Öğretim Elemanı:" in instructor_text:
                                details["instructor"] = instructor_text.replace("Dersin Öğretim Elemanı:", "").strip()
                    except:
                        pass
                    
                    # Yıldırım hızında aktivite çıkarma
                    try:
                        activity_rows = modal_body.find_elements(By.CSS_SELECTOR, "div.bg-warning")
                        
                        for row in activity_rows:
                            try:
                                columns = row.find_elements(By.CSS_SELECTOR, "div[class*='col-lg-']")
                                
                                if len(columns) >= 6:
                                    activity = CourseActivity(
                                        activity_type=clean_text(columns[0].text),
                                        score=clean_text(columns[1].text),
                                        percentage=clean_text(columns[3].text),
                                        semester_effect=clean_text(columns[5].text)
                                    )
                                    details["activities"].append(activity)
                            except:
                                continue
                    except:
                        pass
                    
                    # Süper hızlı modal kapatma
                    try:
                        self.driver.execute_script("$('#Modal').modal('hide');")
                        time.sleep(0.1)  # Minimum bekleme
                    except:
                        pass
                        
                except TimeoutException:
                    pass
        
        except:
            pass
        
        return details
    
    def close(self):
        """WebDriver'ı kapat"""
        try:
            if self.driver:
                self.driver.quit()
                internal_progress("Tarayıcı kapatıldı")
        except:
            pass


def show_banner():
    """Uygulama banner'ını görüntüle"""
    banner = f"""
[green]⚡ KOU HIZLI SİSTEM v{__version__}[/green]
[dim]• Session Management ile reCAPTCHA bypass
• JavaScript tabanlı ultra-hızlı parsing
• Paralel ders detayı çekme
• Akıllı cache sistemi[/dim]
"""
    console.print(Panel(banner, border_style="blue"))


def main():
    """Ana uygulama giriş noktası"""
    show_banner()
    
    collector = None
    
    try:
        collector = KOUDataCollector(headless=False)
        
        # Kimlik bilgilerini al
        from rich.prompt import Prompt
        import getpass
        
        username = Prompt.ask("[cyan]Okul Numarası")
        password = getpass.getpass("Parola: ")
        
        credentials = LoginCredentials(username, password)
        
        # Oturum yönetimiyle giriş yap
        if not collector.login_with_session(credentials):
            console.print("❌ [red]Giriş başarısız![/red]")
            return
        
        # İlerleme takibiyle tüm verileri topla
        all_data = collector.collect_all_semester_data()
        
        if all_data:
            # Verileri kaydet
            from utils import save_user_data
            save_user_data(username, all_data, DATA_DIR)
            user_success(f"Tüm veriler başarıyla kaydedildi ({len(all_data)} dönem)")
        else:
            user_error("Veri toplanamadı")
            
    except KeyboardInterrupt:
        console.print("\n[yellow]İptal edildi.[/yellow]")
    except Exception as e:
        console.print(f"❌ [red]Hata: {e}[/red]")
    finally:
        if collector:
            collector.close()


if __name__ == '__main__':
    main() 