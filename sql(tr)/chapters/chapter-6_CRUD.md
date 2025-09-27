## Chapter 10: PostgreSQL'de CRUD İşlemleri Mastery: Verinin Yaşam Döngüsünü Yönetmek

Şimdiye kadar mükemmel bir veritabanı mimarisi oluşturduk: sağlam tablolar, akıllı ilişkiler, hızlı index'ler ve performans izleme araçları. Ancak en güzel saray bile içinde yaşam olmadığı sürece sadece bir dekor parçasıdır. Bu bölümde, veritabanımıza hayat verecek, verinin doğumundan ölümüne kadar olan tüm yaşam döngüsünü yöneteceğimiz **CRUD (Create, Read, Update, Delete) işlemlerini** derinlemesine inceleyeceğiz.

CRUD, sadece dört basit komut değildir. Her biri, PostgreSQL'in gücünü ortaya çıkaran, performans tuzaklarından kaçınmanın ve veri güvenliğini sağlamanın anahtarlarını barındıran birer sanattır.

### 1. CREATE (INSERT) - Veri Yaratma Sanatı

#### Temel INSERT - İlk Adım

En basit haliyle, tablolarımıza yeni veri eklemek:

```sql
-- Tek satır ekleme
INSERT INTO kullanicilar (kullanici_adi, email, aktif) 
VALUES ('johnsmith', 'john@example.com', TRUE);

-- Birden fazla satır ekleme (Çok daha verimli)
INSERT INTO kullanicilar (kullanici_adi, email, aktif) 
VALUES 
    ('alice_w', 'alice@example.com', TRUE),
    ('bob_dev', 'bob@example.com', TRUE),
    ('charlie', 'charlie@example.com', FALSE);
```

#### RETURNING - Eklenen Veriyi Geri Almak

PostgreSQL'in en güçlü özelliklerinden biri, `INSERT` işleminden sonra eklenen satırın bilgilerini anında geri döndürebilmesidir. Bu özellikle web uygulamalarında, yeni oluşturulan kaydın ID'sini öğrenmek için hayati önem taşır.

```sql
-- Yeni eklenen kullanıcının ID'sini öğrenmek
INSERT INTO kullanicilar (kullanici_adi, email) 
VALUES ('newuser', 'new@example.com')
RETURNING id, kayit_tarihi;

-- Tüm sütunları geri döndürmek
INSERT INTO urunler (urun_adi, fiyat) 
VALUES ('Yeni Ürün', 29.99)
RETURNING *;
```

#### ON CONFLICT - Çakışmaları Zarif Şekilde Yönetmek (UPSERT)

Gerçek hayatta, aynı veriyi iki kez eklemeye çalışmak sık karşılaşılan bir durumdur. `ON CONFLICT` clause, bu durumları hata vermek yerine akıllıca yönetmenizi sağlar.

```sql
-- Eğer email zaten varsa, güncelle (UPSERT)
INSERT INTO kullanicilar (kullanici_adi, email, aktif) 
VALUES ('john_updated', 'john@example.com', TRUE)
ON CONFLICT (email) 
DO UPDATE SET 
    kullanici_adi = EXCLUDED.kullanici_adi,
    aktif = EXCLUDED.aktif,
    guncelleme_tarihi = NOW();

-- Eğer çakışma varsa, hiçbir şey yapma (ignore)
INSERT INTO etiketler (etiket_adi) 
VALUES ('postgresql')
ON CONFLICT (etiket_adi) DO NOTHING;
```

#### Bulk INSERT - Büyük Veri İçin Performans Teknikleri

Binlerce satır eklerken tek tek `INSERT` yapmak çok yavaştır. PostgreSQL, büyük veri yüklemeleri için özel optimizasyonlar sunar.

```sql
-- CSV dosyasından toplu veri yükleme (En hızlı yöntem)
COPY urunler (urun_adi, kategori_id, fiyat) 
FROM '/path/to/products.csv' 
WITH (FORMAT csv, HEADER true);

-- Çok satırlı VALUES ile batch insert
INSERT INTO siparis_detaylari (siparis_id, urun_id, miktar, birim_fiyat)
VALUES 
    (1, 101, 2, 29.99),
    (1, 102, 1, 49.99),
    (1, 103, 3, 19.99);
```

### 2. READ (SELECT) - Veri Keşfetme Yolculuğu

#### Temel Filtreleme ve Sıralama

```sql
-- Temel WHERE koşulları
SELECT kullanici_adi, email, kayit_tarihi 
FROM kullanicilar 
WHERE aktif = TRUE 
  AND kayit_tarihi >= '2024-01-01'
ORDER BY kayit_tarihi DESC 
LIMIT 50;

-- Pattern matching
SELECT * FROM urunler 
WHERE urun_adi ILIKE '%laptop%'  -- Büyük/küçük harf duyarsız
  OR urun_adi ~ '.*tablet.*';    -- Regex kullanımı
```

#### JOIN İşlemleri - Tabloları Birleştirme Ustası

Normalizasyonun gücünü ortaya çıkaran, ilişkili verileri birleştirme teknikleri:

```sql
-- INNER JOIN - Sadece eşleşen kayıtlar
SELECT 
    u.kullanici_adi,
    COUNT(s.id) AS siparis_sayisi,
    SUM(s.toplam_tutar) AS toplam_harcama
FROM kullanicilar u
INNER JOIN siparisler s ON u.id = s.musteri_id
WHERE u.aktif = TRUE
GROUP BY u.id, u.kullanici_adi
HAVING COUNT(s.id) > 5;

-- LEFT JOIN - Sol tablodaki tüm kayıtlar + eşleşenler
SELECT 
    u.kullanici_adi,
    COALESCE(COUNT(s.id), 0) AS siparis_sayisi  -- NULL yerine 0
FROM kullanicilar u
LEFT JOIN siparisler s ON u.id = s.musteri_id
WHERE u.kayit_tarihi >= '2024-01-01'
GROUP BY u.id, u.kullanici_adi;

-- Karmaşık çok tablolu JOIN
SELECT 
    u.kullanici_adi,
    p.urun_adi,
    sd.miktar,
    sd.birim_fiyat,
    s.siparis_tarihi
FROM kullanicilar u
JOIN siparisler s ON u.id = s.musteri_id
JOIN siparis_detaylari sd ON s.id = sd.siparis_id
JOIN urunler p ON sd.urun_id = p.id
WHERE s.siparis_tarihi >= CURRENT_DATE - INTERVAL '30 days';
```

#### Alt Sorgular ve CTE (Common Table Expressions)

Karmaşık sorguları parçalara bölerek okunabilir hale getirmenin yolları:

```sql
-- Alt sorgu (Subquery)
SELECT kullanici_adi, email
FROM kullanicilar
WHERE id IN (
    SELECT DISTINCT musteri_id 
    FROM siparisler 
    WHERE siparis_tarihi >= '2024-01-01'
);

-- CTE ile aynı sorgu (Daha okunabilir)
WITH aktif_musteriler AS (
    SELECT DISTINCT musteri_id 
    FROM siparisler 
    WHERE siparis_tarihi >= '2024-01-01'
)
SELECT u.kullanici_adi, u.email
FROM kullanicilar u
JOIN aktif_musteriler am ON u.id = am.musteri_id;

-- Recursive CTE - Hiyerarşik veriler için
WITH RECURSIVE kategori_agaci AS (
    -- Base case: Ana kategoriler
    SELECT id, kategori_adi, parent_id, 1 as seviye
    FROM kategoriler 
    WHERE parent_id IS NULL
    
    UNION ALL
    
    -- Recursive case: Alt kategoriler
    SELECT k.id, k.kategori_adi, k.parent_id, ka.seviye + 1
    FROM kategoriler k
    JOIN kategori_agaci ka ON k.parent_id = ka.id
)
SELECT * FROM kategori_agaci ORDER BY seviye, kategori_adi;
```

#### Window Functions - Analitik Sorguların Gücü

PostgreSQL'in en güçlü özelliklerinden biri olan pencere fonksiyonları:

```sql
-- Her müşterinin sipariş sıralaması
SELECT 
    kullanici_adi,
    siparis_tarihi,
    toplam_tutar,
    ROW_NUMBER() OVER (PARTITION BY musteri_id ORDER BY siparis_tarihi) as siparis_sirasi,
    SUM(toplam_tutar) OVER (PARTITION BY musteri_id) as musteri_toplam_harcama,
    LAG(toplam_tutar) OVER (PARTITION BY musteri_id ORDER BY siparis_tarihi) as onceki_siparis_tutari
FROM siparisler s
JOIN kullanicilar u ON s.musteri_id = u.id;

-- Running total (Kümülatif toplam)
SELECT 
    siparis_tarihi::date,
    SUM(toplam_tutar) as gunluk_satis,
    SUM(SUM(toplam_tutar)) OVER (ORDER BY siparis_tarihi::date) as kumulatif_satis
FROM siparisler
GROUP BY siparis_tarihi::date
ORDER BY siparis_tarihi::date;
```

### 3. UPDATE - Güvenli Veri Güncelleme Rehberi

#### Temel UPDATE İşlemleri

```sql
-- Tek satır güncelleme
UPDATE kullanicilar 
SET aktif = FALSE, 
    guncelleme_tarihi = NOW()
WHERE email = 'eskikullanici@example.com';

-- Koşullu güncelleme
UPDATE urunler 
SET fiyat = fiyat * 1.10  -- %10 zam
WHERE kategori_id = 1 
  AND fiyat < 100;
```

#### JOIN'li UPDATE - İlişkili Tablolardan Veri Kullanarak Güncelleme

```sql
-- Kategori bilgisine göre ürün güncelleme
UPDATE urunler 
SET indirim_orani = CASE 
    WHEN k.kategori_adi = 'Elektronik' THEN 0.15
    WHEN k.kategori_adi = 'Giyim' THEN 0.20
    ELSE 0.10
END
FROM kategoriler k
WHERE urunler.kategori_id = k.id;

-- Müşteri istatistiklerini güncelleme
UPDATE kullanicilar 
SET toplam_siparis_sayisi = siparis_stats.siparis_sayisi,
    toplam_harcama = siparis_stats.toplam_tutar
FROM (
    SELECT 
        musteri_id,
        COUNT(*) as siparis_sayisi,
        SUM(toplam_tutar) as toplam_tutar
    FROM siparisler
    GROUP BY musteri_id
) as siparis_stats
WHERE kullanicilar.id = siparis_stats.musteri_id;
```

#### Güvenli UPDATE Pratikleri

```sql
-- Güncelleme öncesi backup sorgusu
BEGIN;

-- Önce ne değişeceğini görelim
SELECT id, kullanici_adi, aktif 
FROM kullanicilar 
WHERE son_giris < NOW() - INTERVAL '1 year';

-- Güncellemeyi yapalım
UPDATE kullanicilar 
SET aktif = FALSE
WHERE son_giris < NOW() - INTERVAL '1 year'
RETURNING id, kullanici_adi, aktif;

-- Eğer sonuç beklendiği gibi değilse: ROLLBACK;
-- Eğer her şey yolundaysa: COMMIT;
COMMIT;
```

### 4. DELETE - Dikkatli Veri Silme Teknikleri

#### Temel DELETE İşlemleri

```sql
-- Basit silme
DELETE FROM siparis_detaylari 
WHERE siparis_id = 12345;

-- Koşullu toplu silme
DELETE FROM loglar 
WHERE created_at < NOW() - INTERVAL '1 year';
```

#### Soft Delete vs Hard Delete

```sql
-- Soft Delete (Önerilen yaklaşım)
UPDATE kullanicilar 
SET deleted_at = NOW(), 
    aktif = FALSE
WHERE id = 123;

-- Soft delete edilmiş kayıtları sorgulardan hariç tutma
SELECT * FROM kullanicilar 
WHERE deleted_at IS NULL;  -- Sadece aktif kayıtlar

-- Hard Delete (Dikkatli kullanın!)
DELETE FROM kullanicilar WHERE id = 123;
```

#### CASCADE Davranışları ve Güvenli Silme

```sql
-- Referential integrity kontrolü
DELETE FROM kategoriler WHERE id = 1;
-- HATA: foreign key constraint ihlali

-- Güvenli yaklaşım: Önce bağımlı kayıtları kontrol et
SELECT COUNT(*) FROM urunler WHERE kategori_id = 1;

-- Eğer bağımlı kayıt varsa, önce onları yönet
UPDATE urunler SET kategori_id = 2 WHERE kategori_id = 1;
DELETE FROM kategoriler WHERE id = 1;
```

### 5. Transaction Yönetimi - ACID Güvencesi

#### Temel Transaction Yapısı

```sql
BEGIN;  -- Transaction başlat

    INSERT INTO siparisler (musteri_id, toplam_tutar) 
    VALUES (1, 199.99);
    
    INSERT INTO siparis_detaylari (siparis_id, urun_id, miktar) 
    VALUES (currval('siparisler_id_seq'), 101, 2);
    
    UPDATE urunler SET stok_miktari = stok_miktari - 2 
    WHERE id = 101;

COMMIT;  -- Tüm değişiklikleri kalıcı yap
-- Hata durumunda: ROLLBACK;
```

#### Isolation Levels

```sql
-- Default: READ COMMITTED
BEGIN ISOLATION LEVEL READ COMMITTED;

-- Daha katı: REPEATABLE READ
BEGIN ISOLATION LEVEL REPEATABLE READ;

-- En katı: SERIALIZABLE (Dikkatli kullanın - performans etkisi)
BEGIN ISOLATION LEVEL SERIALIZABLE;
```

#### Savepoint'ler - Kısmi Geri Alma

```sql
BEGIN;
    INSERT INTO kullanicilar (kullanici_adi, email) 
    VALUES ('test_user', 'test@example.com');
    
    SAVEPOINT kullanici_eklendi;
    
    -- Riskli işlem
    UPDATE urunler SET fiyat = fiyat * 2;  -- Yanlış giderse...
    
    -- Sorun varsa sadece son işlemi geri al
    ROLLBACK TO SAVEPOINT kullanici_eklendi;
    
    -- Kullanıcı ekleme işlemi korundu, fiyat güncelleme iptal edildi
COMMIT;
```

### Performans İpuçları ve En İyi Pratikler

1. **Bulk İşlemler İçin:**
   - Tek tek INSERT yerine çok satırlı INSERT veya COPY kullanın
   - Büyük UPDATE'ler için batch'lere bölün

2. **Index Dostu Sorgular:**
   - WHERE koşullarınızda index'li sütunlar kullanın
   - Fonksiyonlardan kaçının (LOWER(), YEAR() vs.)

3. **Transaction Yönetimi:**
   - Transaction'ları mümkün olduğunca kısa tutun
   - Uzun işlemler için VACUUM'u engellemeyin

4. **Güvenlik:**
   - Parameterized query'ler kullanın (SQL injection'dan korunma)
   - DELETE işlemlerinde her zaman WHERE koşulu olduğundan emin olun
   - Soft delete'i hard delete'e tercih edin

### Sonuç

CRUD işlemleri, veritabanı becerilerinizin temelini oluşturur. Bu bölümde öğrendiğiniz teknikler, hem performanslı hem de güvenli uygulamalar geliştirmenin anahtarıdır. Bir sonraki adımımızda, bu bilgileri gerçek dünya senaryolarında nasıl uygulayacağımızı ve daha karmaşık veritabanı mimarileri oluşturmayı inceleyeceğiz.