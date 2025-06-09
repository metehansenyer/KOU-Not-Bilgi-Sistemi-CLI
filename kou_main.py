#!/usr/bin/env python3
"""
KOU Not Bilgi Sistemi - Ultra-Hızlı Ana Uygulama
Anında çevrimdışı erişimle hız için optimize edilmiştir
"""

import time
from typing import Dict, Any, Optional
from pathlib import Path

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.prompt import Prompt, Confirm
from rich.columns import Columns
from rich.text import Text

# Optimize edilmiş modülleri içe aktar
from config import DATA_DIR
from logger import user_message, user_success, user_error, user_warning, internal_progress, console
from utils import (
    load_user_data, 
    save_user_data, 
    has_user_data, 
    get_user_data_info,
    clear_user_data,
    format_file_size,
    format_time_ago
)
from main_with_session import KOUDataCollector, LoginCredentials

__version__ = '6.1.4'


class KOUManager:
    """Çevrimdışı yeteneklerle ultra-hızlı KOU sistem yöneticisi"""
    
    def __init__(self):
        self.username = None
        self.cached_data = None
        self.data_info = None
        
    def show_banner(self):
        """Optimize edilmiş uygulama banner'ını görüntüle"""
        banner = f"""
[green]⚡ KOU HIZLI SİSTEM v{__version__}[/green]
[dim]• Tüm veri toplama
• Offline erişim (< 1 saniye) 
• Temiz arayüz, maksimum hız[/dim]
"""
        console.print(Panel(banner, border_style="blue"))

    def get_credentials(self) -> LoginCredentials:
        """Kullanıcı kimlik bilgilerini verimli bir şekilde al"""
        import getpass
        
        username = Prompt.ask("[cyan]Okul Numarası")
        password = getpass.getpass("Parola: ")
        
        self.username = username
        return LoginCredentials(username, password)

    def check_cached_data(self) -> bool:
        """Detaylı bilgilerle ultra-hızlı önbellek kontrolü"""
        if not self.username:
            return False
        
        # Yıldırım hızında varlık kontrolü
        if not has_user_data(self.username, DATA_DIR):
            return False
        
        # Görüntüleme için önbellek bilgisini al
        self.data_info = get_user_data_info(self.username, DATA_DIR)
        
        if self.data_info:
            size_str = format_file_size(self.data_info["file_size"])
            time_str = format_time_ago(self.data_info.get("last_updated"))
            
            # Önbellek bilgisini göster
            cache_info = f"""
[green]📂 Önbellek Bilgisi[/green]
• Boyut: {size_str}
• Dönem sayısı: {self.data_info.get('total_semesters', '—')}
• Ders sayısı: {self.data_info.get('total_courses', '—')}
• Son güncelleme: {time_str}
"""
            console.print(Panel(cache_info, border_style="green", title="[green]Veriler Mevcut[/green]"))
            return True
        
        return False

    def load_cached_data_fast(self) -> bool:
        """Performans metrikleriyle ultra-hızlı veri yükleme"""
        if not self.username:
            return False
        
        start_time = time.time()
        
        self.cached_data = load_user_data(self.username, DATA_DIR)
        
        load_time = time.time() - start_time
        
        if self.cached_data:
            semester_count = len(self.cached_data)
            course_count = sum(len(sem_data.get("courses", [])) for sem_data in self.cached_data.values())
            
            user_success(f"⚡ Veriler yüklendi: {semester_count} dönem, {course_count} ders ({load_time:.3f}s)")
            return True
        
        return False

    def collect_fresh_data(self, existing_credentials=None) -> bool:
        """İlerleme takibiyle taze veri toplama"""
        try:
            # Eğer kimlik bilgileri önceden alınmışsa tekrar istemiyoruz
            if existing_credentials:
                credentials = existing_credentials
            else:
                credentials = self.get_credentials()
            
            # Veri toplayıcıyı başlat
            collector = KOUDataCollector(headless=False)
            
            try:
                # Oturum yönetimiyle giriş yap
                if not collector.login_with_session(credentials):
                    user_error("Giriş başarısız!")
                    return False
                
                # İlerlemeyle tüm dönem verilerini topla
                all_data = collector.collect_all_semester_data()
                
                if all_data:
                    # Performans takibiyle kaydet
                    if save_user_data(self.username, all_data, DATA_DIR):
                        # Hemen kullanım için belleğe yükle
                        self.cached_data = all_data
                        user_success("Veri toplama ve kaydetme başarılı!")
                        user_message("Artık offline erişim modu aktif - sonraki kullanımlar çok hızlı olacak!")
                        return True
                    else:
                        user_error("Veri kaydetme başarısız!")
                        return False
                else:
                    user_error("Veri toplanamadı!")
                    return False
                    
            finally:
                collector.close()
                
        except Exception as e:
            user_error(f"Veri toplama hatası: {e}")
            return False

    def update_data(self) -> bool:
        """Önbelleğe alınmış verileri sunucudan gelen taze verilerle güncelle"""
        try:
            # Mevcut önbellek bilgisini göster
            if self.data_info:
                size_str = format_file_size(self.data_info["file_size"])
                time_str = format_time_ago(self.data_info.get("last_updated"))
                
                current_info = f"""
[yellow]📂 Mevcut Önbellek Bilgisi[/yellow]
• Boyut: {size_str}
• Dönem sayısı: {self.data_info.get('total_semesters', '—')}
• Ders sayısı: {self.data_info.get('total_courses', '—')}
• Son güncelleme: {time_str}
"""
                console.print(Panel(current_info, border_style="yellow", title="[yellow]Güncelleme Öncesi[/yellow]"))
            
            # Güncellemeyi onayla
            if not Confirm.ask("\n[cyan]Verileri sunucudan güncellemek istediğinizden emin misiniz?[/cyan]"):
                user_message("Güncelleme iptal edildi.")
                return False
            
            # Kullanıcı adı zaten kayıtlı, sadece parola isteyelim
            import getpass
            password = getpass.getpass("Parola: ")
            credentials = LoginCredentials(self.username, password)
            
            user_message("🔄 Veriler sunucudan güncelleniyor...")
            
            # Veri toplayıcıyı başlat
            collector = KOUDataCollector(headless=False)
            
            try:
                # Oturum yönetimiyle giriş yap
                login_attempts = 2
                login_success = False
                
                for attempt in range(login_attempts):
                    if collector.login_with_session(credentials):
                        login_success = True
                        break
                    elif attempt < login_attempts - 1:
                        user_warning("Giriş başarısız, tekrar deneniyor...")
                        time.sleep(1)
                    else:
                        user_error("Giriş başarısız! Güncelleme yapılamadı.")
                
                if not login_success:
                    return False
                
                # Taze veri topla
                all_data = collector.collect_all_semester_data()
                
                if all_data:
                    # Güncellenmiş verileri kaydet
                    if save_user_data(self.username, all_data, DATA_DIR):
                        # Bellekteki önbellek verilerini güncelle
                        self.cached_data = all_data
                        user_success("✅ Veri güncelleme başarılı!")
                        
                        # Güncellenmiş bilgileri göster
                        new_info = get_user_data_info(self.username, DATA_DIR)
                        if new_info:
                            new_size_str = format_file_size(new_info["file_size"])
                            updated_info = f"""
[green]📂 Güncellenmiş Önbellek Bilgisi[/green]
• Boyut: {new_size_str}
• Dönem sayısı: {new_info.get('total_semesters', '—')}
• Ders sayısı: {new_info.get('total_courses', '—')}
• Güncelleme zamanı: Şimdi
"""
                            console.print(Panel(updated_info, border_style="green", title="[green]Güncelleme Sonrası[/green]"))
                        
                        return True
                    else:
                        user_error("Güncellenmiş veri kaydetme başarısız!")
                        return False
                else:
                    user_error("Sunucudan veri alınamadı!")
                    return False
                    
            finally:
                collector.close()
                
        except Exception as e:
            user_error(f"Veri güncelleme hatası: {e}")
            return False

    def show_main_menu(self):
        """Düzenlenmiş ana menüyü görüntüle"""
        menu_items = [
            "[green]1.[/green] 📊 Güncel dönem notları",
            "[green]2.[/green] 📅 Dönem seçimi",
            "[green]3.[/green] 🔄 Verileri güncelle",
            "[green]4.[/green] ❌ Çıkış"
        ]
        
        # Önbellek durum bilgisini ekle
        if self.data_info:
            size_str = format_file_size(self.data_info["file_size"])
            cache_status = f"[dim]💾 Önbellek: {size_str}, {self.data_info.get('total_semesters', '—')} dönem[/dim]"
            menu_items.append(cache_status)
        
        menu_text = "\n".join(menu_items)
        console.print(Panel(menu_text, title="[cyan]Ana Menü[/cyan]", border_style="blue"))

    def get_current_semester_key(self) -> Optional[str]:
        """Verimli bir şekilde güncel dönem anahtarını al"""
        if not self.cached_data:
            return None
        
        # Dönem anahtarları genellikle azalan sıradadır, ilkini al
        semester_keys = list(self.cached_data.keys())
        if semester_keys:
            return semester_keys[0]
        
        return None

    def show_semester_selection(self) -> Optional[str]:
        """Hızlı dönem seçimini göster"""
        if not self.cached_data:
            user_error("Veri yüklü değil!")
            return None
        
        semesters = []
        for key, data in self.cached_data.items():
            semester_name = data.get("semester_name", key)
            course_count = len(data.get("courses", []))
            semesters.append({
                "key": key,
                "name": semester_name,
                "course_count": course_count
            })
        
        # Seçim menüsünü göster
        console.print("\n[cyan]📅 Dönem Seçimi[/cyan]")
        
        for i, semester in enumerate(semesters, 1):
            console.print(f"[green]{i}.[/green] {semester['name']} ([dim]{semester['course_count']} ders[/dim])")
        
        try:
            choice = Prompt.ask(
                f"\n[cyan]Dönem seçin (1-{len(semesters)})[/cyan]",
                choices=[str(i) for i in range(1, len(semesters) + 1)]
            )
            
            selected_semester = semesters[int(choice) - 1]
            return selected_semester["key"]
            
        except (ValueError, IndexError, KeyboardInterrupt):
            return None

    def display_courses_ultra_fast(self, semester_key: str):
        """Zengin biçimlendirmeyle ultra-hızlı ders görüntüleme"""
        if not self.cached_data or semester_key not in self.cached_data:
            user_error("Dönem verisi bulunamadı!")
            return
        
        start_time = time.time()
        
        semester_data = self.cached_data[semester_key]
        courses = semester_data.get("courses", [])
        semester_name = semester_data.get("semester_name", semester_key)
        
        if not courses:
            user_warning("Bu dönemde ders bulunamadı!")
            return
        
        # Yüksek performanslı tablo oluştur
        table = Table(title=f"📊 {semester_name} - Detaylı Görünüm", show_header=True, header_style="bold cyan")
        
        # Optimize edilmiş sütun kurulumu
        table.add_column("No", style="dim", width=3)
        table.add_column("Kod", style="yellow", width=8)
        table.add_column("Ders Adı", style="green", min_width=25)
        table.add_column("Öğr. Elemanı", style="blue", width=15)
        table.add_column("Devam", justify="center", width=6)
        table.add_column("YIO", justify="center", width=4)
        table.add_column("YYS", justify="center", width=4)
        table.add_column("BUT", justify="center", width=4)
        table.add_column("BN", justify="center", width=4)
        table.add_column("BD", justify="center", width=4)
        
        # Ultra-hızlı satır oluşturma
        for course in courses:
            # Hızlı veri çıkarma
            instructor = course.get("instructor", "—")
            if len(instructor) > 15:
                instructor = instructor[:12] + "..."
            
            # Not biçimlendirme
            def format_grade(grade):
                return grade if grade and grade != "—" else "[dim]—[/dim]"
            
            table.add_row(
                course.get("sequence", "—"),
                course.get("code", "—"),
                course.get("name", "—"),
                instructor,
                course.get("attendance", "—"),
                format_grade(course.get("yio", "—")),
                format_grade(course.get("yys", "—")),
                format_grade(course.get("but", "—")),
                format_grade(course.get("bn", "—")),
                format_grade(course.get("bd", "—"))
            )
        
        # Aktiviteleri olan dersler için gösterim
        courses_with_activities = [c for c in courses if c.get("activities")]
        
        display_time = time.time() - start_time
        
        console.print(table)
        
        # Performans bilgisi
        perf_info = f"[dim]⚡ {len(courses)} ders gösterildi ({display_time:.3f}s)[/dim]"
        console.print(perf_info)
        
        # Aktivite detayları varsa göster
        if courses_with_activities:
            console.print(f"\n[yellow]💡 {len(courses_with_activities)} dersin detaylı aktivite bilgisi mevcut[/yellow]")
            
            if Confirm.ask("Aktivite detaylarını göstermek ister misiniz?"):
                self.show_course_activities_fast(courses_with_activities)

    def show_course_activities_fast(self, courses_with_activities):
        """Optimize edilmiş formatta ders aktivitelerini göster"""
        for course in courses_with_activities:
            activities = course.get("activities", [])
            if not activities:
                continue
            
            # Ders başlığı
            course_header = f"[green]{course.get('code', 'N/A')} - {course.get('name', 'N/A')}[/green]"
            if course.get("instructor"):
                course_header += f" [dim]({course['instructor']})[/dim]"
            
            console.print(f"\n{course_header}")
            
            # Aktiviteler tablosu
            activity_table = Table(show_header=True, header_style="bold blue", box=None)
            activity_table.add_column("Aktivite", style="yellow")
            activity_table.add_column("Puan", justify="center", width=8)
            activity_table.add_column("Yüzde", justify="center", width=8)
            activity_table.add_column("Dönem Etkisi", justify="center", width=12)
            
            for activity in activities:
                activity_table.add_row(
                    activity.get("activity_type", "—"),
                    activity.get("score", "—"),
                    activity.get("percentage", "—"),
                    activity.get("semester_effect", "—")
                )
            
            console.print(activity_table)

    def run_main_loop(self):
        """Ultra-hızlı yanıtla ana uygulama döngüsü"""
        while True:
            try:
                console.print()
                self.show_main_menu()
                
                choice = Prompt.ask(
                    "[cyan]Seçiminizi yapın[/cyan]",
                    choices=["1", "2", "3", "4"],
                    default="1"
                )
                
                if choice == "1":
                    # Güncel dönem notları - ultra hızlı
                    start_time = time.time()
                    
                    current_semester = self.get_current_semester_key()
                    if current_semester:
                        self.display_courses_ultra_fast(current_semester)
                    else:
                        user_error("Güncel dönem verisi bulunamadı!")
                    
                    total_time = time.time() - start_time
                    internal_progress(f"⚡ Toplam işlem süresi: {total_time:.3f}s")
                
                elif choice == "2":
                    # Dönem seçimi - hızlı
                    semester_key = self.show_semester_selection()
                    if semester_key:
                        self.display_courses_ultra_fast(semester_key)
                
                elif choice == "3":
                    # Verileri güncelle
                    if self.update_data():
                        user_success("Veriler başarıyla güncellendi!")
                        # Önbellek bilgisini yenile
                        self.data_info = get_user_data_info(self.username, DATA_DIR)
                    else:
                        user_error("Veri güncellemesi başarısız!")
                
                elif choice == "4":
                    # Çıkış
                    if Confirm.ask("\n[yellow]Çıkmak istediğinizden emin misiniz?[/yellow]"):
                        console.print("[green]Görüşmek üzere! 👋[/green]")
                        break
                
            except KeyboardInterrupt:
                console.print("\n[yellow]Ana menüye dönülüyor...[/yellow]")
                continue
            except Exception as e:
                user_error(f"Beklenmeyen hata: {e}")
                continue

    def run(self):
        """Ana uygulama giriş noktası"""
        try:
            self.show_banner()
            
            # Önbellek kontrolü için kullanıcı adını al
            if self.username is None:
                username = Prompt.ask("[cyan]Okul Numarası[/cyan]")
                self.username = username
            
            # Ultra-hızlı önbellek kontrolü
            if self.check_cached_data():
                user_message("Offline mod aktif - veriler önbellekten yükleniyor...")
                
                if self.load_cached_data_fast():
                    # Önbelleğe alınmış verilerle ana uygulamayı çalıştır
                    self.run_main_loop()
                else:
                    user_error("Önbellek yüklenemedi, fresh data toplama gerekli!")
                    if Confirm.ask("Yeni veri toplamak ister misiniz?"):
                        # Kullanıcı bilgilerini bir kez alalım ve collect_fresh_data'ya aktaralım
                        import getpass
                        password = getpass.getpass("Parola: ")
                        credentials = LoginCredentials(self.username, password)
                        
                        if self.collect_fresh_data(existing_credentials=credentials):
                            self.run_main_loop()
            else:
                user_message("İlk kullanım veya önbellek yok - veri toplama başlatılıyor...")
                
                # Kullanıcı bilgilerini bir kez alalım ve collect_fresh_data'ya aktaralım
                import getpass
                password = getpass.getpass("Parola: ")
                credentials = LoginCredentials(self.username, password)
                
                if self.collect_fresh_data(existing_credentials=credentials):
                    self.run_main_loop()
                else:
                    user_error("Veri toplama başarısız!")
                    
        except KeyboardInterrupt:
            console.print("\n[yellow]İptal edildi.[/yellow]")
        except Exception as e:
            user_error(f"Uygulama hatası: {e}")


def main():
    """Uygulama giriş noktası"""
    manager = KOUManager()
    manager.run()


if __name__ == '__main__':
    main() 