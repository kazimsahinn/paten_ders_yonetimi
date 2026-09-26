# Proje Durumu

**Son güncelleme:** 26 Eylül 2026  
**Dal:** `main`  
**Son kod commit’i:** `64b42e5` — `Harden preview HTTPS settings`  
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

## Doğrulama

- 21 Django testi başarılı.
- `manage.py check` başarılı.
- `manage.py check --deploy` başarılı; yalnızca isteğe bağlı HSTS uyarısı kaldı.
- Migration kontrolü temiz.
- Yedek geri yükleme provası test veritabanında başarılı.

## Sıradaki işler

1. Vercel preview yayını ve ortam değişkenlerinin doğrulanması (CLI hesabı giriş bekliyor).
2. Gerçek telefonla mobil ders günü akışının kontrolü.
3. Fotoğraf ve Supabase Storage özelliğinin, dosya güvenliği gereksinimleriyle birlikte sonraki fazda ele alınması.

Bu dosya her commit ve push işleminden sonra güncellenecektir.
