# Proje Durumu

**Son güncelleme:** 26 Eylül 2026  
**Dal:** `main`  
**Son kod commit’i:** `04aac99` — `Align mobile account menu`  
**Remote durumu:** `origin/main` ile senkron

## Mevcut faz

Proje **Faz 3 — Güvenli MVP pilotu** aşamasında.

Tamamlanan temel işler:

- Parola kurtarma ve oturum açmış kullanıcı için parola değiştirme.
- Şifreli `StudentSafetyProfile` ve ayrı güvenlik bilgileri ekranı.
- Audit kayıtları; öğrenci, yoklama, dışa aktarma, arşivleme ve parola değişikliği olayları.
- Öğrenci verisi dışa aktarma ve ilişkili geçmişi koruyan arşivleme.
- Çalışma alanı kapsamlı JSON yedekleme, yedek doğrulama ve boş veritabanına geri yükleme provası.
- Kullanıcı dostu Türkçe 404 sayfası.
- `DEBUG=0` durumunda Vercel proxy arkasında HTTPS yönlendirmesi ve güvenli oturum/CSRF çerezleri.
- `accounts.0002_auditlog` ve `students.0004_studentsafetyprofile` migration’ları Supabase’e uygulandı.
- Vercel preview ve production dağıtımları doğrulandı.
- Production adresi `https://patentakip.vercel.app` olarak ayarlandı; eski `paten-proje.vercel.app` aliası kaldırıldı.
- Production giriş sayfası, özel 404 sayfası ve statik dosya sunumu Vercel CLI bypass testiyle kontrol edildi.
- Vercel Standard Protection etkinleştirildi; production domain normal tarayıcıda herkese açık, preview/deployment adresleri korumalı.
- `https://patentakip.vercel.app/giris/` ve özel `/asdfa` 404 sayfası normal tarayıcıda doğrulandı.
- Mobil alt menüye Dersler ve Hesap menüsü eklendi; Hesap menüsünde Raporlar, Parola değiştir ve Çıkış yap seçenekleri bulunuyor.
- Mobil menü testi dahil 22 Django testi başarılı; `d4f183f` production’a dağıtıldı.
- Mobil alt menü beş eşit hücreli, taşmayı engelleyen düzene alındı; `47b66d8` production’a dağıtıldı.
- Hesap hücresi diğer mobil menü öğeleriyle aynı dikey hizaya alındı; `04aac99` production’a dağıtıldı.
- Gerçek telefonda mobil ders günü akışı test edildi; menüler ve kayıt işlemleri başarılı.
- Production ortamına `DATABASE_URL`, `DJANGO_SECRET_KEY` ve `FIELD_ENCRYPTION_KEY` gizli değişkenleri eklendi.
- Production yeniden dağıtımı sonrası kök URL’nin 302 giriş yönlendirmesi, `/giris/` sayfasının 200 yanıtı ve temiz çalışma zamanı logları doğrulandı; SQLite dosya erişimi kaynaklı 500 hatası giderildi.

## Doğrulama

- 22 Django testi başarılı.
- `manage.py check` başarılı.
- `manage.py check --deploy` başarılı; yalnızca isteğe bağlı HSTS uyarısı kaldı.
- Migration kontrolü temiz.
- Yedek geri yükleme provası test veritabanında başarılı.

## Sıradaki işler

1. Fotoğraf ve Supabase Storage özelliğini dosya güvenliği gereksinimleriyle birlikte pilot sonrasına bırakmak.

Bu dosya her commit ve push işleminden sonra güncellenecektir.
