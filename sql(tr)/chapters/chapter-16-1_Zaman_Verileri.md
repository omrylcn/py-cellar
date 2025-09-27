### **Chapter 14-1: Zamanın Akışını Yönetmek: Dev Tablolar İçin Yerel Bölümleme (Native Partitioning)**

Bu serideki yolculuğumuz bizi giderek daha büyük veri hacimleriyle başa çıkmaya yönlendiriyor. Milyonlarca satırı aşan ve milyarlara doğru ilerleyen bir tablo, en iyi tasarlanmış index'lerle bile yavaşlamaya ve hantallaşmaya mahkumdur. Özellikle zamanla sürekli büyüyen log, sensör verisi veya olay kaydı gibi tablolarda bu sorun kaçınılmazdır.

Bu bölümde, PostgreSQL'in bu devasa yapılarla başa çıkmak için bize sunduğu en temel ve en güçlü aracı olan **Yerel Bölümleme (Native Partitioning)**'i inceleyeceğiz.

#### 1\. Temel Sorun: Tek ve Devasa Bir Tablonun Tehlikeleri

Milyarlarca satırlık tek bir tablo neden kötü bir fikirdir?

* **Index Verimsizliği:** `tarih` sütunu üzerinde bir B-Tree index'iniz olsa bile, bu index devasa boyutlara ulaşır. "Son 15 dakikanın verisini getir" gibi küçük bir aralığı sorgulamak bile, bu devasa index yapısı içinde arama yapmayı gerektirir ve yavaşlar.
* **Bakım Kabusu:** Böyle bir tabloda `VACUUM` çalıştırmak saatler, hatta günler sürebilir. Index'leri yeniden oluşturmak (`REINDEX`) haftasonu boyunca sürecek bir operasyon haline gelebilir.
* **Yavaş Veri Silme:** `DELETE FROM loglar WHERE tarih < '2024-01-01'` gibi bir komutla eski verileri silmeye çalışmak, hem aşırı yavaştır hem de veritabanında devasa bir şişkinliğe (bloat) neden olur.

#### 2\. Çözümün Anahtarı: Tablo Bölümleme (Table Partitioning)

Bu sorunun en temel ve en güçlü çözümü, "böl ve yönet" stratejisidir. PostgreSQL'in yerel bölümleme özelliği, devasa bir tabloyu, aslında perde arkasında yönetimi çok daha kolay olan onlarca veya yüzlerce küçük fiziksel tabloya ("bölüm" - "partition") ayırmamızı sağlar.

**Analoji:** Tüm Türkiye için tek, dev bir telefon rehberi hazırlamak yerine, her şehir için ayrı bir telefon rehberi (İstanbul rehberi, Ankara rehberi vb.) hazırlamak gibidir.

Zaman serisi verileri için en yaygın yöntem, **tarihe göre aralık bölümlemedir (Range Partitioning).**

* **`sensor_verileri` (Ana Tablo - Sanal):** Bu, sorgu attığınız ve `INSERT` yaptığınız ana tablodur. Kendisi veri tutmaz.
  * **`sensor_verileri_2025_09` (Bölüm - Fiziksel):** Sadece Eylül 2025 verilerini tutan gerçek bir tablodur.
  * **`sensor_verileri_2025_10` (Bölüm - Fiziksel):** Sadece Ekim 2025 verilerini tutan gerçek bir tablodur.
  * ... ve bu şekilde devam eder.

**Uygulama:**

```sql
-- 1. Ana, sanal (partitioned) tabloyu oluştur
-- PARTITION BY RANGE ile hangi sütuna göre bölüneceğini belirtiyoruz.
CREATE TABLE sensor_verileri (
    cihaz_id TEXT NOT NULL,
    okuma_zamani TIMESTAMPTZ NOT NULL,
    sicaklik DOUBLE PRECISION
) PARTITION BY RANGE (okuma_zamani);

-- 2. İlk bölümü (partition) oluştur
-- Her bölüm, kendi index'lerine sahip olabilir.
CREATE TABLE sensor_verileri_2025_09
    PARTITION OF sensor_verileri
    FOR VALUES FROM ('2025-09-01 00:00:00+03') TO ('2025-10-01 00:00:00+03');

CREATE INDEX idx_sensor_verileri_2025_09_cihaz_zaman ON sensor_verileri_2025_09 (cihaz_id, okuma_zamani);

-- 3. İkinci bölümü oluştur
CREATE TABLE sensor_verileri_2025_10
    PARTITION OF sensor_verileri
    FOR VALUES FROM ('2025-10-01 00:00:00+03') TO ('2025-11-01 00:00:00+03');

CREATE INDEX idx_sensor_verileri_2025_10_cihaz_zaman ON sensor_verileri_2025_10 (cihaz_id, okuma_zamani);
```

Artık `sensor_verileri` tablosuna bir `INSERT` yaptığınızda, PostgreSQL `okuma_zamani` değerine bakarak kaydı otomatik olarak doğru fiziksel tabloya yönlendirir.

**Önemli:** Gelecek aylar için yeni bölümleri (`sensor_verileri_2025_11` vb.) manuel olarak veya bir script aracılığıyla sizin oluşturmanız gerekir.

#### 3\. Yerel Bölümlemenin Süper Güçleri

1. **Sorgu Hızlandırma (Partition Pruning - Bölüm Eleme):**
    `WHERE okuma_zamani BETWEEN '2025-09-26 10:00' AND '2025-09-26 11:00'` gibi bir sorgu çalıştırdığınızda, PostgreSQL sorgu planlayıcısı bu tarih aralığının sadece `sensor_verileri_2025_09` bölümünün içinde olduğunu anlar. Diğer aylara ait milyarlarca satıra ve onların index'lerine **hiç bakmaz bile**. Bu, sorgu performansını dramatik bir şekilde artırır.

2. **Anında Veri Silme:** Bir yıldan eski verileri silmek mi gerekiyor? Yavaş ve masraflı `DELETE` komutu yerine, ilgili bölümü anında sistemden kaldırırsınız:

    ```sql
    -- Bu işlem saniyeler sürer ve veritabanında şişkinlik (bloat) oluşturmaz.
    DROP TABLE sensor_verileri_2024_09;
    ```

    Aynı şekilde, eski bir bölümü ana tablodan ayırıp (`DETACH PARTITION`) bir arşiv sistemine taşımak da çok kolaydır.

3. **Verimli Bakım:** Bakım işlemlerini ( `REINDEX`, `VACUUM` vb.) tüm devasa yapı yerine tek tek, küçük bölümler üzerinde çalıştırarak sistemi daha az yorarsınız ve kilitlenme sürelerini en aza indirirsiniz.

**Sonuç:**
PostgreSQL'in yerel bölümleme özelliği, veri büyümesiyle başa çıkmak için temel bir stratejidir. Büyük tabloları yönetilebilir, verimli ve hızlı sorgulanabilir parçalara ayırmanın en temel yoludur. Ancak, özellikle yoğun zaman serisi verileriyle çalışırken, bölümleri manuel olarak oluşturma ve yönetme sorumluluğu size aittir.

Peki ya tüm bu bölüm oluşturma, veri silme ve hatta özet raporlama işlemlerini bizim için otomatik hale getiren, üzerine zaman serisine özel daha birçok süper güç ekleyen bir sistem olsaydı? İşte bir sonraki bölümde, bu sorunun cevabı olan **TimescaleDB** eklentisini inceleyeceğiz.
