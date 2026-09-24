# Paten Eğitmeni Yönetim Sistemi — Proje Planı

**Belge sürümü:** 1.1  
**Tarih:** 24 Eylül 2026  
**Durum:** Geliştirme öncesi analiz ve ana referans belgesi  
**İlk hedef:** Tek eğitmen için Türkçe, mobil öncelikli çalışan prototip  
**Kesin teknoloji seçimi:** Python + Django · Supabase PostgreSQL · Vercel · Django Templates + HTML/CSS/vanilla JavaScript

Bu belge ürün kapsamını, iş kurallarını, ekranları, veri modelini ve uygulama sırasını tanımlar. Bu aşamada yalnızca plan hazırlanır; uygulama kodu, veritabanı, altyapı veya bağımlılık kurulumu oluşturulmaz. Belgedeki yollar, veri alanları ve backend işlemleri ilerideki uygulama için tasarım önerileridir.

**Temel karar:** Önce giriş → öğrenci → ders → yoklama → kısa not akışını içeren çalışan bir prototip çıkarılacaktır. Paket ve ödeme sistemleri ürün kapsamından tamamen çıkarılmıştır. Aynı repo içinde Django HTML, sade CSS ve vanilla JavaScript kullanılacaktır.

**Belgeyi okuma kuralı:** Prototip, Faz 0–1 sonunda ortaya çıkan örnek verili ilk üründür. MVP sonraki fazlarda öğrenci, ders, yoklama, not, takvim, gelişim, rapor ve güvenlik ihtiyaçlarını kapsar. Paket ve ödeme hiçbir fazda yer almaz.

| Faz | Çıktı | Öncelik |
|---|---|---|
| 0 | Django temeli, tasarım dili, Supabase bağlantısı ve Vercel deneme yayını | Prototip hazırlığı |
| 1 | Öğrenci, günlük ders, yoklama ve notlarla çalışan prototip | **İlk teslim hedefi** |
| 2 | Görsel takvim, gelişim ve finans içermeyen raporlar | Prototip sonrası |
| 3 | Güvenli gerçek kullanım ve MVP pilotu | Canlı kullanım |
| 4 | V2 iyileştirmeleri | İhtiyaç oluşunca |
| 5 | SaaS ve entegrasyonlar | Gelecek |

Bu revizyon yalnızca planı günceller; kodlama, Supabase projesi oluşturma veya Vercel'e yayınlama başlatılmaz.

## 1. Proje özeti

Paten Eğitmeni Yönetim Sistemi, bir eğitmenin öğrencilerini, birebir ve grup derslerini, yoklamalarını, ders notlarını ve öğrenci gelişimini tek yerde yönetmesini sağlar. Öğrenciyle ilgili son çalışma ve ders geçmişi birkaç dokunuşla görülebilir.

- **Arayüz:** Türkçe; tarih, sayı ve para gösterimi `tr-TR`.
- **Saat dilimi:** İlk çalışma alanında `Europe/Istanbul`; parasal işlemlerde TRY.
- **Kullanım ortamı:** Telefon öncelikli; tablet ve masaüstünde uyarlanmış düzen.
- **Mimari:** Tek repo ve Django uygulaması; Django ORM ile Supabase PostgreSQL, Vercel üzerinde yayın. Ayrı frontend uygulaması yok.
- **İlk kullanıcı:** Tek eğitmen ve tek çalışma alanı; öğrenci giriş hesabı yok.
- **Çevrimdışı davranış:** MVP çevrimiçi çalışır. Bağlantı hatasında işlem tamamlandı gösterilmez; yeniden deneme çift kayıt yaratmaz.

Başarı, çok sayıda modülün varlığıyla değil, eğitmenin gerçek bir ders gününü başka bir kayıt aracına ihtiyaç duymadan yönetebilmesiyle ölçülür.

## 2. Problem tanımı

Manuel kayıtlar öğrenci bilgileri, ders programı, yoklama ve ders notlarını farklı yerlere dağıtır. Bunun sonuçları; unutulan dersler, çakışan randevular, eksik katılım kayıtları ve önceki derste yapılan çalışmanın hatırlanamamasıdır. Grup derslerinde öğrenci bazında katılım takibi özellikle hataya açıktır.

Uygulama şu sorunları çözer:

| Sorun | Ürünün yanıtı | Başarı işareti |
|---|---|---|
| Ders programı dağınık | Ortak ders listesi ve görsel takvim | Bugünün bütün dersleri tek ekranda |
| Yoklama unutuluyor | Ders bazlı öğrenci yoklaması | Her katılımcının durumu kayıtlı |
| Öğrencinin son çalışması bilinmiyor | Kronolojik ders notları ve beceri geçmişi | Son not ders ekranından erişilebilir |
| Telefonda veri girişi zor | Ders kartlarından kısa işlemler | Yoklama ve not girişi sahada kullanılabilir |
| Kişisel bilgiler kontrolsüz tutuluyor | Sınırlı veri, yetkilendirme, güvenli saklama | Hassas bilgiler listelere ve loglara sızmaz |

## 3. Hedef kullanıcı

### 3.1. Birincil kullanıcı

Tek başına çalışan, farklı alanlarda birebir veya küçük grup paten dersi veren eğitmen. Masaüstünde haftayı planlar, telefonda katılım işaretler ve ders sonunda kısa not yazar. Muhasebe veya teknik uzmanlık gerektirmeyen bir deneyim hedeflenir.

### 3.2. Sistemde kaydı bulunan kişiler

Öğrenciler yetişkin veya çocuk olabilir. Çocuk öğrenciler için gerektiğinde veli/yasal temsilci adı, yakınlık bilgisi ve iletişim telefonu tutulabilir. Veli ile acil durum kişisi aynı olmak zorunda değildir. İlk sürümde öğrenci veya veli sisteme giriş yapmaz.

### 3.3. Başlangıç varsayımları

- Tek çalışma alanı, tek aktif eğitmen ve tek saat dilimi vardır.
- Her katılım, ders süresinden bağımsız olarak bir ders hakkıdır; süreye göre kredi hesabı yoktur.
- Gelmedi ve izinli durumlarında otomatik hak düşülmez; istisna gerekçeli manuel hareketle yapılır.
- İlk kayıt için ad ve soyad yeterlidir; eksik telefon/acil durum bilgisi engel değil, tamamlama uyarısıdır.

Bu varsayımlar uygulanabilir başlangıç kararlarıdır. Pilot kullanımda değişen kararlar bu belgenin ilgili bölümüne işlenir; geliştirme sırasında sessizce farklı kurallar uygulanmaz.

## 4. MVP kapsamı

### İlk hedef: çalışan prototip — Faz 0–1

Test Supabase PostgreSQL veritabanında çalışan, Vercel preview'a alınabilen ve yaklaşık 10 kurgusal öğrenciyle gösterilebilen ilk ürün:

- Tek eğitmen girişi/çıkışı.
- Dashboard: bugünkü dersler, yaklaşan dersler, aktif öğrenci ve son eklenenler.
- Öğrenci CRUD, isim araması, aktif/pasif filtresi ve temel profil.
- Birebir/grup ders, lokasyon ve günlük ajanda.
- Öğrenci bazlı yoklama, ders tamamlama ve kısa ders notu.
- Mobil öncelikli sade HTML/CSS arayüzü.

Paket, ödeme, tahsilat, borç, fotoğraf, sağlık notu, gelişim, ayrıntılı rapor ve haftalık/aylık takvim prototipte yoktur. Sahte finansal kart gösterilmez.

### Sonraki fazlar

| Faz | İçerik |
|---|---|
| 0–1 | Temel prototip ve örnek veriler |
| 2 | Görsel takvim, gelişim ve finans içermeyen raporlar |
| 3 | Güvenli gerçek kullanım ve MVP pilotu |
| 4 | V2 iyileştirmeleri |
| 5 | Çoklu eğitmen/SaaS ve entegrasyonlar |

### Kesin kapsam dışı

Paket ve ödeme sistemleri, ilgili tüm entity'ler, tahsilat, borç, iade, online ödeme, fatura ve ödeme raporları tamamen çıkarılmıştır.

## 5. MVP dışında bırakılanlar

Paket/ödeme ve finansal süreçler; online ödeme, fatura/makbuz, muhasebe, çoklu eğitmen, öğrenci portalı, online rezervasyon, WhatsApp/SMS/e-posta entegrasyonları, native mobil uygulama, QR yoklama, çoklu şube, komisyon, tekrarlı dersler ve gelişmiş yapay zekâ özellikleri mevcut MVP'de yoktur. Yeni finans veya SaaS işi ayrı analiz gerektirir.

## 6. Kullanıcı senaryoları

### Öğrenci ve ders akışı

Eğitmen öğrenci ekler, profilini açar, ders planlar, ders günü her katılımcının yoklama durumunu seçer, kısa not girer ve dersi tamamlar. Grup dersinde her öğrencinin katılımı ayrı tutulur.

### Düzeltme ve günlük kullanım

Yanlış yoklama gerekçeli olarak düzeltilir; geçmiş satır silinmez. Pasif öğrenci geçmişini korur ve yeni ders seçimlerinde varsayılan olarak görünmez. Dashboard yaklaşan dersleri ve tamamlanmamış yoklamaları gösterir.

## 7. Sayfalar ve ekranlar

| Ekran | Faz | İçerik |
|---|---:|---|
| Giriş /giris | 0 | Tek eğitmen e-posta/parola |
| Dashboard / | 1 | Günün dersleri ve dört temel metrik |
| Öğrenciler /ogrenciler | 1 | Arama, filtre, ekleme |
| Öğrenci profili /ogrenciler/<id> | 1 | Bilgiler, dersler, notlar |
| Dersler /dersler | 1 | Günlük ajanda |
| Ders detayı /dersler/<id> | 1 | Katılımcılar, yoklama, not |
| Lokasyonlar /lokasyonlar | 1–2 | Ders alanları |
| Takvim /takvim | 2 | Gün/hafta/ay |
| Gelişim /ogrenciler/<id>/gelisim | 2 | Beceri geçmişi |
| Raporlar /raporlar | 2 | Ders ve öğrenci özetleri |
| Ayarlar /ayarlar | 3 | Profil, güvenlik, veri yönetimi |

Prototipte normal Django formları kullanılır. Türkçe hata/boş durumları, mobil geri dönüş ve başarı mesajları ortak davranışlardır.

## 8. Özellikler

Faz 1 dashboard'u bugünkü dersler, yaklaşan dersler, aktif öğrenci ve son eklenenleri gösterir. Hızlı işlemler Yeni öğrenci, Yeni ders ve Yoklama al'dır. Faz 2'de görsel takvim, gelişim, global arama ve finans içermeyen raporlar eklenir. Harici bildirim gönderilmez.

## 9. Öğrenci yönetimi

Faz 1 alanları: ad, soyad, telefon, e-posta, seviye, kısa not ve aktif/pasif. Profilde iletişim, son ders, toplam Katıldı sayısı, ders geçmişi ve kronolojik notlar bulunur. Fotoğraf, doğum tarihi, acil iletişim, veli ve hassas not Faz 3'e bırakılır. Mobil liste kart olarak gösterilir.

## 10. Ders ve takvim sistemi

Ders; tarih, başlangıç/bitiş, birebir/grup türü, öğrenciler, lokasyon, durum ve eğitmen notundan oluşur. Durumlar Planlandı, Tamamlandı, Öğrenci gelmedi ve İptal edildi; yoklama durumları Katıldı, Gelmedi, İzinli ve Ders iptal'dir. Dersler aynı eğitmen için çakışamaz. Faz 1 günlük ajanda, Faz 2 görsel takvimdir. Yoklama ve ders durumu transaction içinde kaydedilir; Attendance için ders/öğrenci benzersizdir.

## 11. Paket sistemi — kapsam dışı

Paket, ders hakkı, StudentPackage, PackageCreditMovement, paket bitişi ve paketle otomatik yoklama tüketimi yapılmayacaktır.

## 12. Ödeme sistemi — kapsam dışı

Payment, tahsilat, borç, iade, online ödeme, fatura ve ödeme raporları yapılmayacaktır. Dashboard'da ödeme veya borç kartı bulunmaz.

## 13. Gelişim takip sistemi

### 13.1. Beceri sözlüğü

Başlangıçta Denge, İleri kayma, Fren, Dönüş, Geri kayma, Slalom, Cross-over ve Tek ayak denge kayıtları çalışma alanına eklenir. Beceri adları uygulama kodundaki enum yerine `Skill` tablosunda tutulur. Böylece V2'de eğitmen kendi listesini düzenleyebilir; MVP'de yalnızca hazır liste gösterilir.

Durumlar: Öğrenilmedi, Çalışılıyor, Yapabiliyor, İyi, Ustalaştı. Henüz kayıt yoksa “Değerlendirilmedi” gösterilir; otomatik Öğrenilmedi sayılmaz.

### 13.2. Değerlendirme ve geçmiş

Eğitmen öğrenci, beceri, durum, değerlendirme tarihi ve isteğe bağlı kısa açıklama seçer. İlgili derse bağlayabilir. `StudentSkill` güncel durumu, `StudentSkillHistory` geçmiş kayıtları tutar; ikisi aynı transaction içinde güncellenir. Geçmiş tarihli yeni kayıt bugünkü durumu yanlışlıkla geriye çekmez; güncel durum en son geçerli değerlendirme tarihinden, eşitlikte kayıt zamanından türetilir.

Geriye gidiş mümkündür; beceri seviyesi yalnızca artmak zorunda değildir. Hatalı değerlendirme gerekçeli geçersizleştirme/düzeltmeyle ele alınır ve güncel görünüm yeniden hesaplanır. Genel Başlangıç/Temel/Orta/İleri seviyesi ayrı `StudentLevelHistory` ile izlenir; beceri durumlarından puan formülüyle otomatik atanmaz.

### 13.3. Ders notları

`LessonNote`, bir öğrenciye ve isteğe bağlı bir derse bağlanır. “Fren çalışıldı. Denge iyi ilerliyor. Bir sonraki derste dönüş çalışılacak.” gibi kısa düz metinler yeterlidir. Öğrenciye özel notlar profilinde ders/değerlendirme tarihine göre kronolojik gösterilir; kaydedilme zamanı ayrıca tutulur.

Grup dersinin ortak eğitmen notu Lesson üzerindedir; her öğrencinin bireysel notu ayrı LessonNote olur. Ortak not, katılımcıların profilinde ders üzerinden gösterilir, her öğrenciye kopyalanmaz. Böylece düzeltmeler çelişmez. Sağlık/güvenlik içeriği bu genel notlara yazılmamalı; ayrı hassas alan kullanılmalıdır.

Profilde sade beceri listesi ve tarihçe kullanılır. Radar grafik, video eki ve yapay zekâ değerlendirmesi MVP kapsamına alınmaz.

## 14. Veri modeli

| Faz | Modeller |
|---|---|
| 0 | Workspace, User, Django auth/session |
| 1 | Student, Location, Lesson, Attendance, LessonNote |
| 2 | Skill, StudentSkill, StudentSkillHistory, StudentLevelHistory |
| 3 | StudentSafetyProfile, FileAsset, PrivacyRecord, AuditLog |

Paket ve ödeme entity'leri yoktur. Tüm modeller workspace sınırında; Attendance ders/öğrenci benzersiz; yaştan türeyen bilgiler ayrı saklanmaz.

## 15. Veritabanı ilişkileri

Workspace → tüm kayıtlar 1:N; Student ↔ Lesson Attendance üzerinden N:M; Location → Lesson 1:N; Student → LessonNote 1:N; Student ↔ Skill Faz 2'de N:M. Sorgular oturumdaki workspace ile sınırlandırılır. Ders çakışması ortak transaction servisinde kontrol edilir. Kullanılmış kayıtlar doğrudan silinmez, arşivlenir.

## 16. Kullanılacak teknoloji stack'i

Teknoloji seçimi kullanıcı tarafından belirlenmiştir. Önceki alternatif stack önerileri bu revizyonla değiştirilmiştir.

### 16.1. Kesin seçimler

| Katman | Seçim | Uygulamadaki görevi |
|---|---|---|
| Dil | Python | Backend ve iş kuralları |
| Framework | Django | URL, view, form, ORM, authentication, session ve template |
| Veritabanı | Supabase üzerinde PostgreSQL | Kalıcı iş verisi ve Django oturumları |
| Yayın | Vercel | Django uygulaması ve statik dosyaların yayını |
| HTML | Django Templates | Sayfaları sunucuda üretme; ortak base template ve include parçaları |
| Stil | Sade CSS | CSS değişkenleri, Grid/Flexbox, media query ve projeye özel bileşenler |
| Etkileşim | Vanilla JavaScript | Menü, gerektiğinde dialog, kısa form etkileşimleri ve sınırlı fetch |
| Kimlik doğrulama | Django auth + DB session | Tek kullanıcı girişi; Supabase Auth kurulmaz |
| Veritabanı erişimi | Django ORM + Psycopg | Supabase PostgreSQL'e yalnız backend'den bağlantı |
| Form/validasyon | Django Forms / ModelForms | Sunucu validasyonu; frontend kontrolleri yalnız kullanım kolaylığı |
| Fotoğraf — Faz 4 | Supabase Storage, özel bucket | Yetkili görsel erişimi; prototipte yükleme yok |
| Takvim — Faz 3 | Gerekirse FullCalendar Standard'ın vanilla JS kullanımı | Gün/hafta/ay görünümü; ayrı frontend framework gerektirmez |
| Test | Django TestCase / TransactionTestCase; ileride Playwright Python | İlgili fazın kritik davranışlarını doğrulama |

Django 5.2 LTS'nin güncel güvenlik yaması başlangıç adayıdır; uygulamaya geçerken Vercel'in desteklediği Python sürümüyle uyumu doğrulanır ve bağımlılıklar sabitlenir. Daha yeni sürüm kullanmak prototip için başlı başına bir hedef değildir. [Django desteklenen sürümler](https://www.djangoproject.com/download/)

FullCalendar ancak görsel takvim fazında eklenir. Standart görünüm ve lisans kapsamı bağımlılık seçilirken tekrar kontrol edilir. [FullCalendar görünümleri](https://fullcalendar.io/docs/plugin-index), [FullCalendar lisansı](https://fullcalendar.io/license)

### 16.2. Basit Django yapısı

İstek yolu: **tarayıcı → Django URL/view → Form validasyonu ve yetki → gerekliyse iş servisi → Django ORM → Supabase PostgreSQL → HTML yanıtı**.

Normal liste/profil işlemlerinde view, form ve queryset yeterlidir. Birden fazla modelin birlikte değiştiği yoklama ve ders işlemleri küçük servis fonksiyonlarına alınır. Her özellik için repository/interface/factory katmanı kurulmaz.

Formlarda POST/Redirect/GET kullanılır; geri dönüldüğünde tarayıcı uyarısıyla yanlışlıkla işlem tekrarı azaltılır. Para ve hak işlemleri ayrıca işlem anahtarı ve transaction ile korunur; yalnız redirect çift kayıt güvenliği sayılmaz. JavaScript kapalıyken temel listeleme ve standart formlar kullanılabilir kalır. Fetch kullanılan mutasyonlar da CSRF ve oturum kontrolünden geçer.

İş kuralları Python tarafındadır. Dashboard ve raporlar ortak hesap fonksiyonlarını kullanır. HTML şablonları gösterim içindir; iş kurallarını ve ders durumunu hesaplamaz.

İlk prototip için ayrı REST API, Django REST Framework, JavaScript framework'ü, Node tabanlı frontend derlemesi veya CSS framework'ü gerekmez. Gerekli küçük JSON uçları Django JsonResponse ile eklenebilir. Harici istemci ihtiyacı doğduğunda API tasarlanır.

### 16.3. Supabase bağlantısı ve güvenlik sınırı

Supabase ilk aşamada yönetilen PostgreSQL hizmetidir; uygulamanın backend'i Django'dur. Tarayıcı Supabase tablolarına doğrudan erişmez. Veritabanı parolası ve daha sonra kullanılacak Storage yönetim anahtarı yalnız sunucu ortam değişkenlerinde tutulur.

Vercel çalışma zamanı için Supabase **transaction pooler** bağlantısı kullanılması planlanır. Sunucusuz iş yükü bağlantı havuzundan yararlanır; bağlantı adresi tahmin edilmez, projenin Connect ekranından alınır. Transaction pooling'de prepared statement desteği olmadığı için sürücü ayarı kontrol edilir. [Supabase bağlantı rehberi](https://supabase.com/docs/guides/database/connecting-to-postgres)

Başlangıç yapılandırma kararları:
- TLS zorunlu; çalışma zamanı için en az yetkili ayrı DB rolü.
- Django'da başlangıçta kalıcı bağlantı kapalı: `CONN_MAX_AGE=0`; ayrıca ikinci büyük istemci havuzu kurulmaz.
- Transaction pooler üzerinde `DISABLE_SERVER_SIDE_CURSORS=True`. Psycopg 3 otomatik prepared statement davranışı gerekirse `prepare_threshold=None` ile kapatılır ve gerçek bağlantıda doğrulanır. [Psycopg prepared statements](https://www.psycopg.org/psycopg3/docs/advanced/prepare.html)
- Şema migration'ı için ayrı bağlantı/değişken; erişilebilirliğe göre doğrudan veya session pooler bağlantısı.
- `transaction.atomic()` ve satır kilitleri aynı transaction içinde çalışır; bağlantılar arasında oturum durumuna güvenilmez.

Django, transaction pooling ile sunucu tarafı cursor kullanımına ilişkin özel ayar gerektirir. [Django veritabanı rehberi](https://docs.djangoproject.com/en/5.2/ref/databases/#transaction-pooling-and-server-side-cursors)

Django tabloları Supabase Data API üzerinden herkese açılmaz. Data API kullanılmıyorsa kapatılır veya uygulama tabloları exposed schema dışında tutulur. Public schema kullanılırsa anon/authenticated rolleri için erişim kapatılıp kontrol edilir. Django oturumu Supabase kullanıcı JWT'si değildir; Supabase RLS'nin Django çalışma rolünü kendiliğinden öğrenci sahibiyle eşleştirdiği varsayılmaz. Workspace yetkisi Django'da uygulanır. [Supabase API güvenliği](https://supabase.com/docs/guides/api/securing-your-api)

### 16.4. Vercel üzerinde yayın yaklaşımı

Vercel'in güncel Django desteği `manage.py` ve WSGI/ASGI girişini algılar. Bu proje için basit WSGI girişi yeterlidir. `STATIC_ROOT` yapılandırıldığında Vercel statik dosyaları build sırasında collectstatic ile toplar ve CDN'den sunar; ilk yayın testinde CSS/JS yolları doğrulanır. Ek WhiteNoise katmanı varsayılan gereksinim değildir. [Vercel Django rehberi](https://vercel.com/docs/frameworks/full-stack/django)

- Repo kökünde Django giriş dosyaları; HTML/CSS/JS aynı repoda. Ayrı frontend dağıtımı yok.
- Secret, DB bağlantısı, Django settings, ALLOWED_HOSTS ve CSRF_TRUSTED_ORIGINS ortama göre ayarlanır; localhost ve yayın alan adları birbirine karıştırılmaz.
- Preview ortamı yalnız kurgusal veri içeren ayrı Supabase test veritabanına bağlanır; üretim bağlantısı bütün preview'lara verilmez.
- Migration her HTTP isteğinde veya her paralel preview build'inde çalıştırılmaz. Hedef DB açıkça seçilerek tek kontrollü yayın adımında uygulanır.
- Veriler, oturumlar ve yüklenen dosyalar yerel uygulama diskine kalıcı olarak yazılmaz. DB Supabase'te, medya Faz 4'te özel Storage bucket'ındadır.
- İlk yayın doğrulaması Faz 0'da yapılır; platform uyumsuzluğu ürünün sonuna bırakılmaz.
- İlk fazlarda arka plan worker, zamanlayıcı ve uzun süren görev yoktur. Büyük dışa aktarma/gönderim ihtiyacı ilgili fazda yeniden değerlendirilir.
- Uygulama ve Supabase bölgeleri uygun yakınlıkta seçilir. Ücretsiz planın kota, yedek ve süreklilik özellikleri otomatik olarak yeterli sayılmaz; gerçek kullanıcı pilotunda doğrulanır.

### 16.5. Minimum bağımlılık yaklaşımı

Faz 0–1: Django, PostgreSQL sürücüsü ve gerekirse tek bir ortam değişkeni/DB URL yardımcı paketi. Yerel çalışma için Python sanal ortamı ve standart paket kurulumu yeterlidir. Docker veya ek frontend araç zinciri prototip ön koşulu değildir.

Faz 2: Önce Django'nun transaction ve ORM yetenekleri kullanılır; yeni paket ancak somut ihtiyaçla eklenir. Faz 3: Gerekirse takvim kütüphanesi. Faz 4: Güvenli fotoğraf işlemek için Pillow ve Supabase Storage'a uygun tek erişim yöntemi. Depolama için aynı anda birden fazla SDK/adapter kullanılmaz.

Model migration'ları Django'nun tek şema kaynağıdır. Supabase panelinden yapılan elle şema değişiklikleriyle migration geçmişi ayrıştırılmaz.

## 17. Proje klasör yapısı

Bu ağaç öneridir; şu anda oluşturulmaz. Tek repo içinde Django kodu, şablonlar ve statik dosyalar yer alır.

```text
/
├── PROJECT_PLAN.md
├── manage.py
├── requirements.txt
├── .env.example                    # Sadece değişken adları/örnekler; secret yok
├── config/
│   ├── settings.py
│   ├── urls.py
│   └── wsgi.py
├── apps/
│   ├── accounts/                   # User, Workspace, giriş
│   ├── students/                   # Öğrenci, temel profil
│   ├── lessons/                    # Location, Lesson, Attendance, LessonNote
│   ├── │   └── progress/                   # Faz 3: beceri ve seviye geçmişi
├── templates/
│   ├── base.html
│   ├── includes/                   # Menü, form alanı, badge, mesajlar
│   ├── registration/
│   ├── dashboard/
│   ├── students/
│   ├── lessons/
│   ├── │   └── progress/                   # Faz 3
├── static/
│   ├── css/
│   │   ├── tokens.css
│   │   ├── base.css
│   │   ├── components.css
│   │   └── pages.css
│   ├── js/
│   │   ├── app.js
│   │   └── lessons.js
│   └── images/                     # Yalnız marka/arayüz görselleri
└── tests/
    └── e2e/                        # İhtiyaç oldukça Playwright Python
```

Django app'leri standart `models.py`, `views.py`, `forms.py`, `urls.py`, `admin.py`, `tests.py` ve `migrations/` düzenini kullanır. Çok kayıtlı iş işlemleri gerektiğinde `services.py` içine alınır; boş soyutlama dosyaları eklenmez. Faz 2–3 klasörleri kendi fazları geldiğinde oluşturulur.

Prototipte lokasyon ve notlar ders app'i içinde kalabilir. Rapor ve veri yönetimi başlangıçta küçük view/servisler olabilir; yalnızca büyüdüklerinde ayrılır. Django Admin bakım ekranıdır; kritik ders/yoklama kurallarını atlayan düzenlemeler açılmaz.

Kullanıcı fotoğrafları `static/` içine veya Vercel uygulama diskine yazılmaz. `collectstatic` çıktısı üretilmiş dosyadır; repodaki kaynak CSS/JS ile karıştırılmaz. Vercel yapılandırması yalnız güncel entegrasyonun gerektirdiği kadar eklenir.

## 18. Authentication ve güvenlik

Faz 0–1'de giriş, yetki, CSRF, sunucu validasyonu, secret yönetimi ve güvenli yayın ayarları uygulanır. Dosya/hassas veri korumaları, ilgili özelliklerle birlikte Faz 4'te eklenir. Prototipte yalnızca kurgusal öğrenci verisi kullanılır; aşağıdaki tam operasyon gereksinimleri ilk arayüz gösterimini bekletmez.

### 18.1. Kimlik doğrulama ve yetkilendirme

- Açık kullanıcı kaydı kapalıdır; ilk eğitmen güvenli kurulum süreciyle oluşturulur. Depoya varsayılan parola yazılmaz.
- Django auth ile e-posta/parola ve veritabanı oturumu kullanılır. E-posta ile giriş için ilk migration'da AbstractUser tabanlı model ve giriş tanımı seçilir. Parolalar Django'nun güvenli hasher mekanizmasıyla saklanır; özel kripto yapılmaz. [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/default/)
- Çerezler HTTPS üzerinde Secure, HttpOnly ve uygun SameSite ayarlarıyla çalışır. Parola/oturum token'ı localStorage'a yazılmaz.
- Çıkış, parola değişimi ve hesap pasife alma ilgili oturumları iptal eder. Oturum süresi ve hareketsizlik sınırı açıkça yapılandırılır.
- Faz 4'te Django'nun parola kurtarma akışı süreli token ve işlem e-postasıyla açılır; hesap varlığı yanıttan ifşa edilmez. Prototipte geliştirici kontrollü Django parola yönetimi yeterlidir; sahte bir e-posta gönderim ekranı yapılmaz.
- Her Django view, JSON ucu, queryset ve kritik servis oturum + workspace yetkisini doğrular. Kullanıcı/öğrenci seçimi çalışma alanıyla filtrelenir. URL kimliğini değiştirmek başka workspace kaydını açamaz.
- Tüm dosya, arama, rapor ve dışa aktarma işlemleri de aynı sınırı uygular.
- Silme/dışa aktarma ve hassas ayar değişikliklerinde yakın zamanda yeniden kimlik doğrulama istenir.
- MFA ilk güvenlik iyileştirmeleri arasındadır; çoklu rol MVP'de yoktur.

DEBUG yayın ortamında kapalıdır; SECRET_KEY, Supabase DB parolası ve Storage yönetim anahtarı şablonlara/JavaScript'e verilmez. Django template autoescape açık tutulur; güvenilmeyen notlar safe filtresiyle HTML yapılmaz. HTTPS çerezleri, ALLOWED_HOSTS ve CSRF_TRUSTED_ORIGINS Vercel alan adına göre kontrol edilir. [Django deployment checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)

### 18.2. Girdi ve uygulama korumaları

Sunucu validasyonu; uzunluk, sayı aralığı, izinli durum geçişi, sahiplik ve tarih koşullarını kapsar. Notlar düz metindir; HTML çalıştırılmaz. SQL parametreli kullanılır, dinamik alan/sıralama whitelist ile sınırlandırılır. Django CSRF middleware'i ve formlarda CSRF token kullanılır; fetch ile yazma varsa CSRF başlığı gönderilir. CORS gereksiz yere açılmaz.

Giriş/kurtarma, arama, yazma ve dosya yükleme için ayrı rate limit ve boyut sınırı uygulanır. Vercel'de platform koruması veya DB destekli ortak sayaç kullanılır; Django'nun varsayılan olarak giriş denemelerini sınırladığı kabul edilmez. Yalnız process belleğine dayalı limit, değişen fonksiyon örnekleri arasında koruma sayılmaz. Sınır aşıldığında anlaşılır mesaj ve yeniden deneme bilgisi verilir.

Secret'lar ortam/secret yönetiminde tutulur, depoya yazılmaz. Veritabanı kullanıcısı minimum yetkili olur; migration ve çalışma hesabı mümkünse ayrılır. TLS, güvenlik başlıkları, bağımlılık açık taraması ve kontrollü güncelleme süreci yayın kontrolüne dahil edilir.

### 18.3. Dosya yükleme — Faz 4

Supabase Storage içinde özel bucket kullanılır. Django oturumu ve öğrenci sahipliği kontrol edildikten sonra erişim sağlanır; veritabanında dosyanın kendisi yerine nesne anahtarı saklanır. Storage anahtarı tarayıcıya verilmez. DB yedeğinin Storage içindeki dosyaları da içerdiği varsayılmaz; dosyaların yedeklenmesi ayrıca planlanır. [Supabase yedek kapsamı](https://supabase.com/docs/guides/platform/backups)

MVP sadece JPEG, PNG ve WebP fotoğraf kabul eder; SVG, HTML, PDF ve video yüklenmez. Başlangıç sınırı Vercel'in güncel istek boyutu ve form overhead'i doğrulanmak koşuluyla 3 MB ve en fazla 4.096 × 4.096 piksel olarak önerilir. Sunucu uzantı/MIME yanında gerçek içeriği kontrol eder; resmi yeniden kodlar, EXIF bilgisini çıkarır ve uygulamanın ürettiği nesne adıyla özel depoya yazar. Kaynak dosya adını depolama yolu olarak kullanmaz.

Fotoğraflar yetki kontrolünden sonra kısa ömürlü bağlantıyla veya kontrollü servis üzerinden gösterilir. Depo herkese açık değildir; erişim URL'leri loglanmaz. Hatalı/yarım yüklemeler ve eski fotoğraflar temizlenir. Bu yaklaşım OWASP'ın dosya türü, boyut, yetki ve depolama önerileriyle uyumludur. [OWASP File Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)

### 18.4. Hassas veriler ve KVKK'yı destekleyen teknik tasarım

Bu bölüm hukuki uygunluk kararı vermez; ürünün veri minimizasyonu, erişim ve veri yaşam döngüsünü uygulayabilmesini tanımlar. İşleme amaçları, hukuki dayanaklar, saklama süreleri ve gerekli izin metinleri canlı öncesi veri sorumlusu tarafından belirlenir. Kurumun veri güvenliği rehberi teknik kontrol tasarımı için başvuru kaynağıdır. [KVKK veri güvenliği rehberi ve açıklaması](https://www.kvkk.gov.tr/Icerik/2040/Veri-Guvenligine-Iliskin-Yukumlulukler)

- Kimlik numarası, teşhis listesi, ilaç dosyası, sağlık raporu veya biyometrik veri toplanmaz.
- Sağlık/güvenlik notu isteğe bağlı, kısa ve yalnız eğitmenin güvenli ders yürütmesi için gerekli bilgiyle sınırlıdır. Serbest alan yanında bu amaç açıklanır.
- Hassas not ayrı entity ve ayrı sorguda tutulur; genel liste, arama, bildirim, hata raporu ve analitik dışındadır.
- Güvenlik notu uygulama düzeyinde şifrelenir; anahtar DB'den ayrı secret/KMS yönetiminde tutulur. Anahtar döndürme ve geri yüklemede erişim planlanır.
- Fotoğraf, doğum tarihi, veli ve acil kişi bilgileri zorunlu yapılmaz. Çocuk öğrencide temsilci/izin kaydı desteklenir; yaş veya rıza eşiği yazılıma hukuki varsayım olarak gömülmez.
- Aydınlatma gösterimi ile açık rıza aynı kutu değildir. Gerekli görülen amaç bazlı rıza sürümü, zamanı, ilgili temsilci ve geri çekme kaydı tutulabilir; önceden işaretli kutu kullanılmaz.
- Fotoğraf/sağlık notu toplama özelliği, amaç ve gerekli süreç tanımlanıncaya kadar kapatılabilir. Temel öğrenci/ders kullanımı gereksiz veri paylaşımına bağlanmaz.
- Veri envanteri alan → amaç → erişim → sağlayıcı/bölge → saklama/silme eşleşmesini içerir. Hosting/depolama/e-posta sağlayıcısı ve veri aktarım düzeni canlıdan önce değerlendirilir.
- Silme akışı önce etki önizlemesi gösterir; kişisel alanlar, fotoğraf ve notlar kapsama alınır. Saklanması gereken işlem kaydı varsa kapsam ve gerekçe açıkça ayrılır; belirsiz gerekçeyle sonsuz soft delete yapılmaz.
- Dışa aktarma dosyaları kısa süreli ve özel erişimli olur; geçici çıktılar temizlenir. İstek, işlem zamanı ve sonuç içeriği kopyalamadan audit'e yazılır.
- Yedeklerdeki verinin süresi sonunda çıkması ve geri yükleme sonrası silme işlemlerinin yeniden uygulanması prosedürde tanımlanır.

### 18.5. Audit, loglama ve yedekleme

Audit olayları: giriş başarısızlığı/oturum iptali, ders ve yoklama düzeltmesi, hassas not erişimi, dışa aktarma ve silme. Loglarda parola, token, fotoğraf bağlantısı, sağlık metni ve gereksiz iletişim bilgileri bulunmaz. Uygulama rolü audit geçmişini normal ekranlardan değiştiremez.

Önerilen başlangıç işletim hedefi: günlük şifreli DB ve dosya yedeği, **en fazla 24 saat veri kaybı (RPO)** ve **4 saat içinde geri yükleme (RTO)**. Bunlar garantilenmiş hizmet seviyesi değil, sağlayıcı ve geri yükleme denemesiyle doğrulanacak hedeflerdir. Destekleniyorsa noktasal geri dönüş değerlendirilir. Saklama süresi veri politikasıyla belirlenir; başlangıç operasyon önerisi 30 gündür.

Canlı öncesi ayrı ortamda DB, dosya ve şifreleme anahtarı erişimini içeren gerçek geri yükleme yapılır. Sonrasında düzenli geri yükleme denemesi, yedek başarısızlığı uyarısı ve erişim denetimi uygulanır. Silinmiş kişisel verinin eski yedekten dönmemesi için silme kayıtları kontrollü biçimde tekrar işlenir.

## 19. Responsive/mobile UX yaklaşımı

### 19.1. Mobil bilgi mimarisi

Prototipte alt gezinme: **Ana sayfa**, **Dersler**, **Öğrenciler**. Diğer fazlarda Takvim, Gelişim, Raporlar ve Ayarlar eklenir; kapsam dışı finans menüleri gösterilmez. Alt menü en çok beş öğede tutulur. Sık kullanılan ekleme işlemi bulunduğu ekrana uygun, başparmakla erişilebilir bir düğmedir. Masaüstünde yan menü ve üst arama alanı kullanılır.

Ders kartında saat, tür, öğrenci/grup özeti, konum ve durum görünür. “Yoklama al”, “Dersi tamamla”, “Not ekle” ve “Öğrenci profili” işlemleri karttan erişilir. Birincil işlem dersin durumuna göre değişir; az kullanılan eylemler menüdedir. Grup kartında profiller katılımcı listesinden açılır.

### 19.2. Etkileşim kuralları

- Tasarım önce 360–430 px telefon genişliklerinde düşünülür; 320 px'te taşma testi yapılır.
- Dokunma hedefleri en az yaklaşık 44 × 44 CSS piksel; önemli metinler okunur boyuttadır.
- Mobil tablolar anlamlı kartlara dönüşür. Takvim haftası gibi kaçınılmaz geniş alanların yanında günlük liste alternatifi vardır.
- Yoklamada öğrenci başına net durum seçici ve sabit kaydet alanı; grup işlemlerinde kaydetmeden önce özet bulunur.
- “Herkes katıldı” kısayolu kullanılırsa mevcut özel durumları sessizce ezmez; önizleme ve onay ister.
- Sağlık notları kart yüzeyinde gösterilmez; eğitmenin bilinçli açtığı detayda görünür. Acil telefon tek dokunuşla arama bağlantısı olabilir.
- Finansal işlem ve hak düşümünde sunucu onayı gelmeden kesin başarı gösterilmez.
- Bağlantı hatasında form açık kalır, anlaşılır tekrar deneme sunulur; kişisel veriler kalıcı çevrimdışı cache'e alınmaz.
- Formdan ayrılma uyarısı, başarılı kayıttan sonra kısa geri bildirim ve güvenli geri alma/düzeltme yolu bulunur.

### 19.3. Görsel dil ve erişilebilirlik

**Görsel yön:** Paten sporunun hareket hissini taşıyan, sakin ve düzenli bir çalışma alanı. Açık zemin, koyu metin, turkuaz/yeşil vurgu ve az miktarda sıcak vurgu kullanılır. Saha kullanımında okunabilirlik, dekorasyondan önce gelir.

| Öğe | Prototip kararı |
|---|---|
| Sayfa zemini | Açık gri-beyaz, başlangıç rengi #F6F8FA |
| Kart yüzeyi | Beyaz, ince #E2E8F0 kenarlık, çok hafif gölge |
| Ana metin | Koyu lacivert #0F172A; ikincil metin #475569 |
| Ana işlem | Koyu turkuaz #0F766E zemin üzerinde beyaz metin |
| Enerjik küçük vurgu | Açık yeşil #D9F99D üzerinde koyu metin; okunur küçük etiketler |
| Uyarı | Soluk amber yüzey ve koyu metin; hata ve başarı ayrıca metin/ikonla |
| Köşeler/boşluk | Kartlarda 14–18 px radius; 8 px tabanlı sade boşluk düzeni |
| Yazı | Türkçe karakterleri iyi gösteren sistem fontları; gövde yaklaşık 16 px |
| İkon | Az sayıda tutarlı çizgi ikon; önemli işlemlerde metin etiketiyle |
| Hareket | Yalnız kısa açılma/odak geri bildirimleri; sürekli animasyon yok |

Bunlar ilk tasarım değerleridir; kontrast ve cihaz kontrolünden sonra ayarlanabilir. Yeni font servisi, büyük ikon paketi veya görsel üretim pipeline'ı prototip şartı değildir.

**Dashboard düzeni:** Üstte kısa karşılama ve tarih; altında bugünün ders akışı; yakında başlayacak ders belirgin; aktif öğrenci ve yaklaşan ders gibi küçük özetler ikinci sırada. Büyük boş dekoratif banner kullanılmaz. Öğrenci kartında baş harf avatarı, isim, seviye ve sonraki ders; ders kartında saat, öğrenci, konum ve tek belirgin eylem bulunur.

**Ekran durumu tasarımı:** Henüz öğrenci yoksa tek açıklama ve “İlk öğrenciyi ekle”; bugün ders yoksa sade boş gün durumu. Hata mesajları form alanında, başarı mesajı kısa ve görünür olur. Modern görünüm; tutarlı boşluk, iyi tipografi, dengeli kartlar ve doğru etkileşimle sağlanır.

Renk/boşluk/tipografi token'ları CSS değişkenleriyle tanımlanır; bileşenler doğrudan sabit renklerle doldurulmaz. Bu yaklaşım ileride dark mode eklenmesini kolaylaştırır. Karanlık tema ilk sürümde uygulanmaz.

Klavye ile gezinme, görünür odak, etiketli form alanları, ekran okuyucu açıklamaları, hata odağı ve azaltılmış hareket tercihi test edilir. Hedef erişilebilirlik seviyesi WCAG 2.2 AA'dır; otomatik tarama tek başına uygunluk kanıtı sayılmaz.

### 19.4. Performans ve kullanılabilirlik hedefleri

Pilot test hedefleri: ders kartından yoklama ekranına en çok 2 dokunuş; öğrenci aramasından profile en çok 2 işlem; sade ders sonu notunun yaklaşık 30 saniyede girilebilmesi. Prototipte standart Django sayfa geçişleri ve form sonrası yönlendirme kabul edilir; SPA akıcılığı zorunlu değildir. Gereksiz yükleme veya aynı formu tekrar doldurma ihtiyacı azaltılır.

Faz 1'de küçük kurgusal veriyle etkileşim kontrolü yapılır; yük testi prototip çıkış şartı değildir. Faz 4'te temsilî 500 öğrenci, 10.000 ders ve 50.000 katılım içeren test verisinde sayfalı liste ve takvim aralık sorguları ölçülür. Hedef, tanımlı test ortamında yaygın sunucu işlemlerinin p95'te 500 ms altında, ana mobil görünümün benzetilmiş orta hızlı 4G'de yaklaşık 3 saniyede kullanılabilir olmasıdır. Ortam ve ağ ölçümleriyle birlikte raporlanır; ölçülmemiş performans iddiası yapılmaz.

## 20. V2 özellikleri

Sürükle-bırak/tekrarlı ders, dark mode, CSV, özel beceri listesi, PWA, MFA, aktif oturum ekranı ve ders hatırlatmaları geri bildirimle seçilebilir. Paket ve ödeme bu listenin adayı değildir.

## 21. Gelecek geliştirmeler

Çoklu eğitmen/SaaS, öğrenci portalı, online rezervasyon, WhatsApp/SMS/e-posta/Google Calendar, native mobil, QR yoklama, çoklu şube, online ödeme ve muhasebe entegrasyonları ayrı analiz gerektiren gelecek kapsamıdır.

## 22. Geliştirme fazları

Kesin sıra: yerel → Supabase test → Vercel preview → canlı. İlk hedef Faz 0–1 prototipidir. Prototipte yaklaşık 10 kurgusal öğrenci ve örnek ders/yoklama/not bulunur.

### Faz 0 — Django temeli

- **Ne geliştirilecek?** Django, özel User/Workspace, auth/session, ayarlar ve ortak HTML/CSS.
- **Sayfalar:** Giriş ve boş dashboard.
- **Modeller:** Workspace, User, Django auth/session.
- **API/backend:** URL/view/form, Supabase bağlantısı ve erişim kontrolü.
- **Tamamlanma kriteri:** Yerelde giriş/çıkış ve responsive kabuk çalışır.

### Faz 1 — Çalışan prototip

- **Ne geliştirilecek?** Öğrenci, lokasyon, ders, yoklama, not ve dashboard.
- **Sayfalar:** Öğrenci listesi/profili, günlük ajanda, ders formu/detayı, dashboard.
- **Modeller:** Student, Location, Lesson, Attendance, LessonNote.
- **API/backend:** CRUD/forms, arama, filtre, çakışma, yoklama ve not.
- **Tamamlanma kriteri:** Örnek verilerle uçtan uca ders günü akışı telefonda çalışır.

### Faz 2 — Takvim, gelişim ve raporlar

- **Ne geliştirilecek?** Görsel takvim, beceriler, global arama ve finans içermeyen raporlar.
- **Sayfalar:** Takvim, Gelişim, Raporlar.
- **Modeller:** Skill, StudentSkill, StudentSkillHistory, StudentLevelHistory.
- **API/backend:** Takvim sorguları, gelişim geçmişi ve metrikler.
- **Tamamlanma kriteri:** Takvim ve raporlar örnek verilerle eşleşir.

### Faz 3 — Güvenli MVP pilotu

- **Ne geliştirilecek?** Fotoğraf, hassas not, parola kurtarma, dışa aktarma/silme, audit ve yedek.
- **Sayfalar:** Güvenlik/veri yönetimi ve ayarlar.
- **Modeller:** StudentSafetyProfile, FileAsset, PrivacyRecord, AuditLog.
- **API/backend:** Storage özel erişimi, veri yaşam döngüsü ve yayın kontrolleri.
- **Tamamlanma kriteri:** Gerçek veriye geçiş ve mobil pilot koşulları sağlanır.

### Faz 4 — V2 ve gelecek analizleri

Kullanıcı geri bildirimindeki özellikler tek tek ele alınır. Paket ve ödeme bu projeye geri eklenmez.

## 23. Test stratejisi

Paket/ödeme testleri oluşturulmaz.

| Faz | Doğrulama |
|---|---|
| 0 | Django system check, giriş, yetkisiz erişim, CSRF, Supabase smoke |
| 1 | Öğrenci/ders/yoklama/not, çakışma, örnek veri ve mobil görünüm |
| 2 | Takvim, gelişim ve rapor metrikleri |
| 3 | Dosya/hassas veri, dışa aktarma/silme, geri yükleme ve pilot |

Kritik akış: giriş → öğrenci → ders → yoklama → not. Başka workspace erişimi reddedilir.

## 24. Prototip ve MVP tamamlanma kriterleri

### Prototip — Faz 0–1

- [ ] Django, test Supabase ve Vercel preview çalışıyor.
- [ ] Giriş, CSRF, secret ve validasyon etkin.
- [ ] Öğrenci CRUD, arama ve aktiflik çalışıyor.
- [ ] Birebir/grup ders, çakışma kontrolü ve günlük ajanda çalışıyor.
- [ ] Öğrenci bazlı yoklama ve ders tamamlama çalışıyor.
- [ ] Kısa ders notu profilinde görünüyor.
- [ ] Yaklaşık 10 kurgusal öğrenciyle gösterim yapılmış.
- [ ] Telefon ve masaüstü görsel dil tutarlı.
- [ ] Paket/ödeme alanı, menüsü veya sahte kartı yok.

### MVP — Faz 3

- [ ] Takvim, gelişim ve finans içermeyen raporlar çalışıyor.
- [ ] Mobil ders günü gerçek cihazda tamamlanmış.
- [ ] Hassas veri, fotoğraf, dışa aktarma/silme ve audit güvenli.
- [ ] Yedek geri yükleme denenmiş.
- [ ] Django kontrolleri, testler, migration ve Vercel yayını geçiyor.

## 25. Karar kaydı ve uygulama öncesi netleştirilecek noktalar

### Kesinleşen kararlar — sürüm 1.2

| Konu | Karar |
|---|---|
| İlk hedef | Faz 0–1 örnek verili çalışan prototip |
| Backend/frontend | Python + Django + Templates + HTML/CSS/vanilla JavaScript |
| Veritabanı | Supabase PostgreSQL |
| Yayın sırası | Yerel → Supabase test → Vercel preview → canlı |
| Giriş | Tek eğitmen, e-posta/parola, Django auth/session |
| Paket sistemi | Tamamen kapsam dışı |
| Ödeme sistemi | Tamamen kapsam dışı |
| Görsel yön | Açık zemin, koyu metin, turkuaz/yeşil vurgu |
| Mobil | Günlük ders akışı öncelikli |
| Örnek veri | Yaklaşık 10 kurgusal öğrenci ve ders verisi |

Supabase test projesi ve Vercel hesabı hazır olmalıdır. Örnek parola repoya yazılmayacak, ortam değişkeniyle sağlanacaktır. Ürün adı/logo prototip için zorunlu değildir.

### Revizyon geçmişi

| Sürüm | Değişiklik |
|---|---|
| 1.0 | İlk kapsamlı analiz |
| 1.1 | Django/Supabase/Vercel ve frameworksüz frontend |
| 1.2 | Paket ve ödeme sistemleri tamamen çıkarıldı; örnek verili prototip ve yayın sırası kesinleştirildi |
## 26. Teknik başvuru kaynakları

- [Django Authentication](https://docs.djangoproject.com/en/5.2/topics/auth/default/)
- [Django Deployment Checklist](https://docs.djangoproject.com/en/5.2/howto/deployment/checklist/)
- [Supabase PostgreSQL bağlantıları](https://supabase.com/docs/guides/database/connecting-to-postgres)
- [Vercel Django yayını](https://vercel.com/docs/frameworks/full-stack/django)
- [OWASP File Upload](https://cheatsheetseries.owasp.org/cheatsheets/File_Upload_Cheat_Sheet.html)
- [KVKK veri güvenliği](https://www.kvkk.gov.tr/Icerik/2040/Veri-Guvenligine-Iliskin-Yukumlulukler)
