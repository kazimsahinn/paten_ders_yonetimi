# Proje Durumu

**Son güncelleme:** 4 Ekim 2026  
**Dal:** `main`  
**Son kod commit’i:** `986719b` — `Güvenlik ve veri bütünlüğü açıklarını kapat`  
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
- `accounts.0002_auditlog`, `accounts.0003_auththrottle` ve `students.0004_studentsafetyprofile` migration’ları Supabase’e uygulandı.
- Vercel preview ve production dağıtımları doğrulandı.
- Production adresi `https://patentakip.vercel.app` olarak ayarlandı; `paten-proje.vercel.app` uyumluluk adresi de aynı son production dağıtımına yönlendirildi.
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
- Supabase `public` şemasındaki 22 Django tablosunda RLS etkinleştirildi; `anon` ve `authenticated` rollerine erişimi reddeden politikalar eklendi ve Security Advisor temizlendi.
- Giriş ve parola kurtarma uçlarına veritabanı destekli ortak istek sınırı eklendi; çıkış yalnız CSRF korumalı POST isteğine alındı.
- Yoklama düzeltmelerinde gerekçe ve öğrenci bazlı audit kaydı eklendi; tekrar gönderilen notların çoğalması ve iptal edilen derslerin çakışmalı yeniden açılması engellendi.
- Geçmiş tarihli gelişim kaydının güncel durumu geriye çekmesi önlendi; yedek geri yüklemesinden sonra PostgreSQL sayaçları sıfırlanıyor.

## Doğrulama

- 32 Django testi başarılı.
- `manage.py check` başarılı.
- `manage.py check --deploy` başarılı; yalnızca isteğe bağlı HSTS uyarısı kaldı.
- Migration kontrolü temiz.
- Canlı giriş akışı doğrulandı: ilk beş hatalı deneme 200, altıncı deneme 429 döndürdü ve çalışma zamanı loglarında yeni 500 hatası oluşmadı.
- Yedek geri yükleme provası test veritabanında başarılı.
- Supabase doğrulaması: 22/22 tablo RLS etkin, 22/22 tabloda politika mevcut, Security Advisor `lints: []`.

## Sıradaki işler

1. Fotoğraf ve Supabase Storage özelliğini dosya güvenliği gereksinimleriyle birlikte pilot sonrasına bırakmak.

Bu dosya her commit ve push işleminden sonra güncellenecektir.
