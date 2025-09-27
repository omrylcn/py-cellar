### Chapter 15: Raporlama Kabusuna Son: `MATERIALIZED VIEWS` ile Anında Sonuçlar

Uygulamanız büyüdükçe, veri de büyür. Ve veri büyüdükçe, ondan anlamlı özetler çıkaran raporlama sorguları yavaşlamaya başlar. Bir dashboard'da aylık satış özetini gösteren o sorgu, ilk başlarda milisaniyeler sürerken, artık veritabanını dakikalarca meşgul eden bir kabusa dönüşebilir.

Bu sorgular genellikle birden fazla tabloyu (`siparisler`, `musteriler`, `urunler`, `kategoriler`) `JOIN` eder, veriyi gruplar (`GROUP BY`), toplar (`SUM`), ortalamasını alır (`AVG`) ve sayar (`COUNT`). Her seferinde bu ağır işlemi baştan yapmak, hem kullanıcı için kötü bir deneyimdir hem de üretim (production) veritabanınızda ciddi bir yüke neden olur.

Bu bölümde, bu sorunu çözmek için PostgreSQL'in sunduğu iki tür "View" (Görünüm) yapısını ve özellikle `MATERIALIZED VIEW`'in bu sorunu nasıl sihirli bir şekilde çözdüğünü inceleyeceğiz.

#### 1\. Klasik `VIEW` - Bir Kısayoldan İbaret

Standart bir `VIEW`, aslında saklanmış bir `SELECT` sorgusudur. Karmaşık bir sorguyu, sanki basit bir tabloymuş gibi, tekrar tekrar yazmaktan kurtaran bir kısayol oluşturur.

**Analoji:** Bir `VIEW`, web tarayıcınızdaki bir yer imi (bookmark) gibidir. Yer imine tıkladığınızda, tarayıcı size kaydedilmiş bir sayfayı göstermez; o anki canlı sayfayı sunucudan yeniden ister.

**Örnek:** Aylık kategori bazlı satışları özetleyen karmaşık bir sorgumuz olsun.

```sql
-- Her seferinde bu uzun sorguyu yazmak yerine...
SELECT
    date_trunc('month', s.siparis_tarihi)::date AS ay,
    k.kategori_adi,
    COUNT(s.id) AS siparis_sayisi,
    SUM(sd.miktar * u.fiyat) AS toplam_ciro
FROM siparisler s
JOIN siparis_detaylari sd ON s.id = sd.siparis_id
JOIN urunler u ON sd.urun_id = u.id
JOIN kategoriler k ON u.kategori_id = k.id
GROUP BY ay, k.kategori_adi;

-- ...bir VIEW oluşturabiliriz:
CREATE VIEW aylik_kategori_ozeti AS
    -- ... yukarıdaki sorgunun aynısı ...
;
```

Artık bu karmaşık rapora erişmek çok kolay:
`SELECT * FROM aylik_kategori_ozeti WHERE ay = '2025-08-01';`

**Önemli Not:** Bu sorgu, perde arkasında hala orijinal, yavaş ve karmaşık sorguyu **her seferinde yeniden çalıştırır**. Bir `VIEW` kodu basitleştirir, ancak performansı **iyileştirmez**.

#### 2\. `MATERIALIZED VIEW` - Sorgu Sonucunu Fizikselleştirme

İşte sihrin gerçekleştiği yer burasıdır. Bir `MATERIALIZED VIEW`, yavaş bir sorgunun **sonucunu** fiziksel bir tablo gibi diskte saklar.

**Analoji:** Bir `MATERIALIZED VIEW`, bir web sayfasının ekran görüntüsünü almak veya PDF olarak kaydetmek gibidir. Kaydedilmiş bu kopyaya bakmak anlıktır, çünkü sunucuya yeniden gitmeniz gerekmez.

**Örnek:** Aynı raporu şimdi de materialized view olarak oluşturalım.

```sql
CREATE MATERIALIZED VIEW aylik_kategori_ozeti_mv AS
    -- ... yukarıdaki sorgunun aynısı ...
;
```

Artık bu rapora sorgu attığımızda:
`SELECT * FROM aylik_kategori_ozeti_mv WHERE ay = '2025-08-01';`

Bu sorgu, artık karmaşık `JOIN`'ler ve `GROUP BY`'lar çalıştırmaz. Sadece önceden hesaplanmış ve fiziksel olarak saklanan bir tablodan veri okur. Sonuç: **Anında\!**

#### 3\. Veriyi Güncel Tutmak: `REFRESH`'in Bedeli

Madem bu kadar harika, neden her şeyi materialized view yapmıyoruz? Çünkü "ekran görüntüsü"nün bir bedeli vardır: zamanla **bayatlar (stale)**. Orijinal `siparisler` tablosuna yeni veriler eklendikçe, `aylik_kategori_ozeti_mv` bu yeni verilerden haberdar olmaz.

**Çözüm:** Görünümü manuel olarak yenilemek (`REFRESH`).

```sql
REFRESH MATERIALIZED VIEW aylik_kategori_ozeti_mv;
```

**En Önemli Takas (Trade-off):** Bu komut, orijinal yavaş sorguyu **tekrar çalıştırır** ve materialized view'ın tüm içeriğini yeni sonuçlarla değiştirir. Eğer orijinal sorgu 30 dakika sürüyorsa, `REFRESH` işlemi de 30 dakika sürer ve bu süre boyunca materialized view kilitlenebilir.

**Üretim Ortamı İçin Çözüm: `CONCURRENTLY`**
Neyse ki PostgreSQL, bu yenileme işlemini, görünüm üzerinde okuma sorgularını engellemeden, arka planda yapmamızı sağlayan bir seçeneğe sahiptir.

```sql
-- CONCURRENTLY kullanabilmek için materialized view üzerinde en az bir UNIQUE index olmalıdır.
CREATE UNIQUE INDEX idx_aylik_kategori_ozeti_mv ON aylik_kategori_ozeti_mv (ay, kategori_adi);

-- Artık güvenle, sistemi kilitlemeden yenileyebiliriz:
REFRESH MATERIALIZED VIEW CONCURRENTLY aylik_kategori_ozeti_mv;
```

#### Stratejik Kullanım Alanları ve En İyi Pratikler

  * **Ne Zaman Kullanılır?**
      * Yavaş çalışan ve sık okunan analitik/raporlama sorguları için.
      * Kullanıcıların birkaç dakika veya saatlik "bayat" veriyi tolere edebileceği durumlar için (örn: günlük ciro dashboard'ları, haftalık kullanıcı aktivite raporları).
      * Harici BI (İş Zekası) araçlarına (Tableau, Power BI vb.) hızlı bir veri kaynağı sunmak için.
  * **En İyi Pratikler:**
      * `REFRESH` işlemini, `cron` veya `pg_cron` gibi bir zamanlayıcı ile veritabanı trafiğinin en az olduğu gece saatlerinde (örn: her gece 03:00'te) otomatik olarak çalışacak şekilde planlayın.
      * Üretim ortamındaki materialized view'ları yenilerken **her zaman** `CONCURRENTLY` seçeneğini kullanın.
      * Yenileme süresini (`REFRESH`'in ne kadar sürdüğünü) izleyin. Eğer yenileme süresi kabul edilemez derecede uzarsa, temel sorguyu optimize etmeniz veya başka stratejiler (partitioning gibi) düşünmeniz gerekebilir.

#### TimescaleDB'nin Sürekli Toplamaları ile Karşılaştırma

Önceki bölümde bahsettiğimiz **TimescaleDB'nin Sürekli Toplamaları (Continuous Aggregates)**, aslında bu konseptin zaman serisi verileri için ultra optimize edilmiş bir halidir. Standart bir materialized view'ı yenilemek için tüm ham veriyi baştan taramanız gerekirken, bir Continuous Aggregate, sadece son gelen yeni veriyi işleyerek kendini **artımlı (incrementally)** olarak günceller. Bu, onu sürekli akan veriler için çok daha verimli kılar.

**Karar:** Genel amaçlı ilişkisel raporlama için **`MATERIALIZED VIEW`** kullanın. Zaman serisi raporlaması için ise **TimescaleDB Continuous Aggregates** çok daha üstün bir çözümdür.

**Sonuç:** `MATERIALIZED VIEW`'ler, "anlık veri" ile "anlık sorgu performansı" arasında yapılan bilinçli bir takastır. Doğru kullanıldığında, uygulamanızın en yavaş raporlama sayfalarını en hızlı sayfalarından birine dönüştürebilir ve veritabanınızın üzerindeki analitik yükü önemli ölçüde azaltabilir.