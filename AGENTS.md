# Depo Katkı Rehberi

## Proje Yapısı ve Modül Organizasyonu

Bu depo, Paten Akış eğitmen paneli için geliştirilmiş küçük bir Django monolith uygulamasıdır. `config/` proje ayarlarını, URL yönlendirmelerini ve WSGI/ASGI giriş noktalarını içerir. Özellikler alanlarına göre ayrılmıştır:

- `accounts/`: çalışma alanı, eğitmen kullanıcısı, kimlik doğrulama ve demo veri komutu.
- `students/`: öğrenci modelleri, formlar, görünümler ve URL’ler.
- `lessons/`: dersler, lokasyonlar, yoklama, ders notları ve ilgili URL’ler.
- `templates/`: ortak yerleşim ile dashboard, öğrenci, ders ve giriş şablonları.
- `static/`: vanilla CSS ve JavaScript dosyaları.
- `PROJECT_PLAN.md`: ürün kapsamı ve fazlara ayrılmış yol haritası.

Veritabanı migration dosyaları her uygulamanın `migrations/` klasöründedir. Yerel geliştirmede `db.sqlite3`, Supabase PostgreSQL için ise `DATABASE_URL` kullanılır.

## Görev Öncesi Zorunlu Okuma

Her geliştirme, düzeltme, refactor veya planlama görevine başlamadan önce kök dizindeki [`PROJECT_PLAN.md`](PROJECT_PLAN.md) dosyasını okuyun. Yapılacak işi bu belgede tanımlanan kapsam, faz sırası, teknik kararlar ve paket/ödeme kapsam dışı kurallarıyla karşılaştırın. Planla çelişen bir değişiklik gerekiyorsa uygulamaya başlamadan önce planı güncelleyin ve çelişkiyi açıkça belirtin.

## Geliştirme, Test ve Çalıştırma Komutları

Windows’ta proje sanal ortamını kullanın:

```powershell
.\.venv\Scripts\python.exe manage.py runserver
.\.venv\Scripts\python.exe manage.py check
.\.venv\Scripts\python.exe manage.py makemigrations
.\.venv\Scripts\python.exe manage.py migrate
.\.venv\Scripts\python.exe manage.py seed_demo
```

`runserver` yerel uygulamayı başlatır, `check` Django yapılandırmasını doğrular, migration komutları şemayı günceller, `seed_demo` ise örnek eğitmen, öğrenci, ders ve yoklama verileri oluşturur.

## Kodlama Stili ve Adlandırma Kuralları

Standart Django/Python stilini izleyin: dört boşluk girinti, fonksiyon ve değişkenlerde `snake_case`, sınıflarda `PascalCase` ve açıklayıcı model alanları kullanın. Alan mantığını ilgili uygulama içinde tutun. Doğrulama için Django formlarını, veri değişiklikleri için POST/Redirect/GET yaklaşımını kullanın. Şablonlar sunucu tarafında oluşturulmalıdır; yeni bir frontend framework’ü eklemek yerine mevcut vanilla JavaScript ve CSS yapısını kullanın.

## Test Kuralları

Değişiklik göndermeden önce `manage.py check` çalıştırın ve önemli akışları Django test istemcisiyle kontrol edin. Testleri ilgili uygulamanın `tests.py` dosyasına ekleyin; örneğin `lessons/tests.py`. Test metotlarını `test_<davranis>` biçiminde adlandırın. Kimlik doğrulama, çalışma alanı sınırlandırması, form doğrulaması, yoklama güncellemesi ve silme işlemleri test edilmelidir.

## Commit ve Pull Request Kuralları

Kısa ve emir kipinde commit başlıkları kullanın: `Add student delete flow` veya `Fix lesson overlap validation` gibi. Pull request açıklamasında kullanıcıya görünen değişikliği, çalıştırılan doğrulama komutlarını, migration veya yapılandırma değişikliklerini belirtin. Arayüz değişikliklerinde ekran görüntüsü ekleyin. `PROJECT_PLAN.md` açıkça güncellenmediği sürece paket ve ödeme özelliklerini kapsam dışında tutun.

## Güvenlik ve Yapılandırma Notları

`.env` dosyasını, kimlik bilgilerini veya üretim veritabanı URL’lerini commit etmeyin. Yapılandırma şablonu olarak `.env.example` dosyasını kullanın. CSRF korumasını, kimlik doğrulama decorator’larını, çalışma alanı kapsamındaki sorguları ve sunucu tarafı doğrulamayı koruyun. Öğrenci iletişim ve güvenlik bilgilerini hassas kabul edin; demo verilerinde gerçek kişisel veri kullanmayın.
