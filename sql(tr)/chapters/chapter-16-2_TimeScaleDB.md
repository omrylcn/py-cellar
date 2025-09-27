### **Chapter 14-2: Otomatik Pilotta Zaman Serisi: TimescaleDB ile PostgreSQL'i Güçlendirmek**

Önceki bölümde, PostgreSQL'in yerel bölümleme (native partitioning) özelliğiyle devasa tabloları nasıl yönetebileceğimizi gördük. Bu, veri büyümesiyle başa çıkmak için harika ve temel bir yöntemdir. Ancak bu süreç, yeni zaman dilimleri için yeni bölümleri manuel olarak oluşturmayı, eski bölümleri manuel olarak silmeyi ve karmaşık özet raporları kendimiz optimize etmeyi gerektirir.

Peki ya tüm bu işleri bizim için otomatikleştiren, üzerine zaman serisine özel süper güçler ekleyen bir sistem olsaydı?

İşte bu sistem, **TimescaleDB**'dir. TimescaleDB, PostgreSQL'in üzerine kurulan, onu birinci sınıf bir zaman serisi veritabanına dönüştüren açık kaynaklı bir eklentidir.

#### 1\. TimescaleDB Nedir? Temel Konseptler

TimescaleDB, PostgreSQL'in kanıtlanmış ve güvenilir altyapısını alır ve zaman serisi verilerinin getirdiği benzersiz zorlukları çözmek için onu genişletir.

**Hypertable (Hiper-Tablo):**
TimescaleDB'nin temel soyutlamasıdır. Dışarıdan bakıldığında, sorgu attığınız ve veri eklediğiniz normal bir PostgreSQL tablosu gibi görünür ve davranır. Ancak perde arkasında, TimescaleDB bu tabloyu zamana göre otomatik olarak küçük parçalara, yani \*\*"chunk"\*\*lara (yerel bölümlemenin "partition"larına karşılık gelir) böler.

**Otomatik Bölümleme:**
En büyük kolaylığı budur. Artık her ay veya her hafta için manuel olarak `CREATE TABLE ... PARTITION OF ...` komutunu çalıştırmanıza gerek yoktur. Siz sadece veriyi `INSERT` edersiniz; TimescaleDB, zamanı geldiğinde yeni "chunk"ları sizin için otomatik olarak oluşturur.

**Kurulum ve Kullanım:**

```sql
-- 1. Eklentiyi aktif et (eğer daha önce yapılmadıysa)
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- 2. NORMAL bir PostgreSQL tablosu oluştur
CREATE TABLE sensor_verileri (
    okuma_zamani TIMESTAMPTZ NOT NULL,
    cihaz_id TEXT NOT NULL,
    sicaklik DOUBLE PRECISION,
    nem DOUBLE PRECISION
);

-- 3. Sihirli komutu çalıştır: Bu tabloyu bir Hypertable'a dönüştür.
-- Her 7 günde bir yeni bir 'chunk' (bölüm) oluşturacak şekilde ayarla.
SELECT create_hypertable('sensor_verileri', 'okuma_zamani', chunk_time_interval => INTERVAL '7 days');
```

İşte bu kadar\! `sensor_verileri` tablosu artık bir Hiper-Tablodur. Siz veri ekledikçe, TimescaleDB arka planda bölümlemeyi sizin için yönetecektir.

#### 2\. Katil Özellik 1: Sürekli Toplamalar (Continuous Aggregates)

Bu, TimescaleDB'nin belki de en güçlü özelliğidir.
**Problem:** Bir dashboard'da, bir sensörün son bir aydaki "günlük ortalama sıcaklığını" göstermek istiyorsunuz. Milyarlarca ham veri satırını her sayfa yenilendiğinde taramak ve ortalamasını almak imkansızdır.

**TimescaleDB Çözümü:** Sürekli Toplamalar, zaman serisi verileri için tasarlanmış akıllı `MATERIALIZED VIEW`'lerdir. Belirlediğiniz bir zaman aralığındaki (saatlik, günlük vb.) özet verileri arka planda otomatik olarak hesaplar ve bir görünümde saklar. En önemlisi, bu hesaplamayı **artımlı (incrementally)** olarak yapar. Yani, sadece son gelen yeni veriyi işleyerek özeti günceller, tüm tabloyu baştan taramaz.

```sql
-- Her bir cihaz için günlük ortalama sıcaklık ve nemi hesaplayan
-- bir sürekli toplama oluşturalım.
CREATE MATERIALIZED VIEW gunluk_ozetler
WITH (timescaledb.continuous) AS
SELECT
    time_bucket('1 day', okuma_zamani) AS gun,
    cihaz_id,
    AVG(sicaklik) AS ort_sicaklik,
    MAX(sicaklik) AS max_sicaklik
FROM
    sensor_verileri
GROUP BY gun, cihaz_id;

-- Bu görünümün her saat başı otomatik olarak yenilenmesi için bir politika ekleyelim.
SELECT add_continuous_aggregate_policy('gunluk_ozetler',
    start_offset => INTERVAL '1 month',
    end_offset   => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
```

Artık dashboard sorgularınız, milyarlarca satırlık `sensor_verileri` tablosu yerine, çok daha küçük ve hızlı olan `gunluk_ozetler` görünümünü sorgulayabilir. `SELECT * FROM gunluk_ozetler WHERE cihaz_id = 'A-01';` sorgusu milisaniyeler içinde dönecektir.

#### 3\. Katil Özellik 2: Veri Yaşam Döngüsü Yönetimi

Zaman serisi verileri sonsuza kadar büyür. Eski verileri yönetmek kritik bir iştir. TimescaleDB bunu otomatikleştiren politikalar sunar.

**a) Veri Sıkıştırma (Compression):**
TimescaleDB, eski "chunk"lar için özel, sütun bazlı sıkıştırma algoritmaları sunar. Bu, genellikle artık güncellenmeyen eski verilerin diskte kapladığı alanı **%90'a varan oranlarda** azaltabilir. Sıkıştırılmış veri hala sorgulanabilirdir.

```sql
-- 1 aydan eski verileri otomatik olarak sıkıştırmak için bir politika ekleyelim.
SELECT add_compression_policy('sensor_verileri', compress_after => INTERVAL '1 month');
```

**b) Veri Saklama (Retention):**
Belirli bir süreden eski verileri veritabanından tamamen kaldırmak için kullanılır. Bu, yerel bölümlemedeki `DROP TABLE` gibi anında çalışır ve şişkinliğe neden olmaz.

```sql
-- 12 aydan eski verileri otomatik olarak silmek için bir politika ekleyelim.
SELECT add_retention_policy('sensor_verileri', drop_after => INTERVAL '12 months');
```

#### 4\. Stratejik Karar: Ne Zaman Yerel Bölümleme, Ne Zaman TimescaleDB?

| Senaryo | Tavsiye Edilen Çözüm | Neden? |
| :--- | :--- | :--- |
| **Zaman Serisi Olmayan** büyük tablo (örn: kullanıcıları ülkeye göre bölümleme) | **Yerel Bölümleme** | TimescaleDB zaman odaklıdır. Diğer bölümleme türleri için yerel özellikler daha uygundur. |
| **Basit** zaman serisi ihtiyaçları, **manuel kontrol** isteği | **Yerel Bölümleme** | Daha az bağımlılık, süreç üzerinde tam kontrol. |
| **Ciddi ve Büyüyen** zaman serisi yükü (IoT, loglar, finans) | **TimescaleDB** | Otomasyon, geliştirme hızı, sürekli toplamalar ve sıkıştırma gibi özel özellikler hayati önem kazanır. |
| **Hızlı ve karmaşık** zaman serisi analitiği ve raporlama ihtiyacı | **TimescaleDB** | Sürekli Toplamalar (Continuous Aggregates) bu senaryo için oyun değiştiricidir. |

**Sonuç:**
PostgreSQL'in yerel bölümleme özelliği, büyük tabloları yönetmek için güçlü ve genel amaçlı bir araçtır. Ancak, işiniz özellikle zaman serisi verileriyle ise, TimescaleDB bu süreci bir üst seviyeye taşır. Otomasyon, performans optimizasyonları ve veri yaşam döngüsü yönetimi gibi özellikleriyle, PostgreSQL'i bu alandaki en iyi veritabanlarından birine dönüştürür ve geliştiricilerin hayatını inanılmaz derecede kolaylaştırır.