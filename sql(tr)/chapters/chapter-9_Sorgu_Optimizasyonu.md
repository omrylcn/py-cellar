## Chapter 9: Sorgu Optimizasyonunun Temelleri: Hızlı ve Verimli Sorgular Yazma Sanatı

Şimdiye kadar sağlam tablolar tasarladık, onları index'lerle hızlandırdık ve temel CRUD işlemlerini öğrendik. Ancak gerçek dünyada karşılaştığımız sorgular nadiren tek tablolu, basit yapılardır. Genellikle birden fazla tabloyu birleştiren (`JOIN`), karmaşık koşullarla filtreleyen (`WHERE`) ve büyük veri kümelerini işleyen sorgularla uğraşırız.

Bu bölümde, bu karmaşık sorguları yazarken düşebileceğimiz performans tuzaklarından nasıl kaçınacağımızı, PostgreSQL'in sorgu planlayıcısıyla nasıl işbirliği yapacağımızı ve günlük geliştirme sürecinde uygulayabileceğimiz pratik optimizasyon tekniklerini öğreneceğiz.

### 1. JOIN İşlemlerinin Anatomisi: Doğru Birleştirme Teknikleri

JOIN'ler, ilişkisel veritabanlarının kalbidir. Ancak yanlış yazılan bir JOIN, sisteminizi dize getirebilir. Gelin en yaygın JOIN türlerini ve her birinin ne zaman kullanılacağını inceleyelim.

#### INNER JOIN - Sadece Eşleşenler

En yaygın ve genellikle en hızlı JOIN türüdür. Sadece iki tabloda da karşılığı olan kayıtları döndürür.

```sql
-- Sipariş veren müşterileri listele
SELECT 
    m.kullanici_adi,
    COUNT(s.id) AS siparis_sayisi
FROM kullanicilar m
INNER JOIN siparisler s ON m.id = s.musteri_id
WHERE s.siparis_tarihi >= '2024-01-01'
GROUP BY m.id, m.kullanici_adi;
```

**Performans İpucu:** `INNER JOIN` kullanırken, `ON` koşulundaki sütunlarda index olduğundan emin olun. `s.musteri_id` için bir B-Tree index yoksa, bu sorgu çok yavaş çalışır.

#### LEFT JOIN - Sol Tablodaki Her Şey + Eşleşenler

Sol tablodaki tüm kayıtları, sağ tabloda karşılığı olmasa bile getirir. Sağ tabloda karşılığı olmayan yerler `NULL` olur.

```sql
-- Hiç sipariş vermemiş olan müşteriler dahil, tüm müşterileri listele
SELECT 
    m.kullanici_adi,
    COALESCE(COUNT(s.id), 0) AS siparis_sayisi
FROM kullanicilar m
LEFT JOIN siparisler s ON m.id = s.musteri_id
GROUP BY m.id, m.kullanici_adi;
```

**Dikkat Edilmesi Gereken:** `LEFT JOIN` kullanırken, `WHERE` koşullarınızı dikkatli yazın. Eğer `WHERE s.durum = 'tamamlandi'` gibi bir koşul eklerseniz, bu aslında `INNER JOIN` gibi davranır çünkü sipariş vermeyen müşterilerde `s.durum` `NULL` olacaktır.

#### Performans Katili: Cartesian Product (Kartezyen Çarpım)

Bu, en tehlikeli JOIN hatasıdır. `ON` koşulunu unutursanız veya yanlış yazarsanız, PostgreSQL iki tablonun tüm satırlarını birbiriyle çarpar.

```sql
-- ❌ ASLA BÖYLE YAPMAYIN!
SELECT * FROM kullanicilar, siparisler;
-- 1000 müşteri × 10000 sipariş = 10 milyon satır!
```

Her zaman `ON` koşulunuzu kontrol edin ve sorguyu çalıştırmadan önce `EXPLAIN` ile kaç satır döneceğini tahmin edin.

### 2. WHERE Koşullarında Verimlilik: Index Dostu Sorgular

Sorgunuzun hızını belirleyen en kritik faktör, `WHERE` koşullarınızın index'leri verimli kullanıp kullanmadığıdır.

#### Index Kullanan (Hızlı) Koşullar

```sql
-- ✅ Index kullanabilir
WHERE kayit_tarihi >= '2024-01-01'
WHERE kategori_id = 5
WHERE email = 'test@example.com'
WHERE fiyat BETWEEN 100 AND 500

-- ✅ Önek araması index kullanabilir
WHERE urun_adi LIKE 'laptop%'
```

#### Index Kullanamayan (Yavaş) Koşullar

```sql
-- ❌ Index kullanamaz - fonksiyon solda
WHERE YEAR(kayit_tarihi) = 2024
WHERE UPPER(email) = 'TEST@EXAMPLE.COM'

-- ❌ Index kullanamaz - joker karakterle başlayan LIKE
WHERE urun_adi LIKE '%laptop%'

-- ❌ Index kullanamaz - NOT operatörü
WHERE kategori_id != 5
```

#### Çözüm Stratejileri

**Problem:** `WHERE YEAR(kayit_tarihi) = 2024` yavaş.
**Çözüm:** Aralık kullanın:
```sql
WHERE kayit_tarihi >= '2024-01-01' AND kayit_tarihi < '2025-01-01'
```

**Problem:** `WHERE UPPER(email) = 'TEST@EXAMPLE.COM'` yavaş.
**Çözüm:** Expression index oluşturun:
```sql
CREATE INDEX idx_kullanicilar_email_upper ON kullanicilar (UPPER(email));
```

### 3. LIMIT ve ORDER BY: Sıralama Optimizasyonu

Büyük tablolarda `ORDER BY` ile sıralama yapmak çok maliyetli olabilir. Özellikle `LIMIT` ile birlikte kullanıldığında doğru index stratejisi kritiktir.

#### Verimli Sıralama

```sql
-- ✅ created_at sütununda index varsa çok hızlı
SELECT * FROM siparisler 
ORDER BY created_at DESC 
LIMIT 10;

-- ✅ Composite index ile daha da hızlı
-- CREATE INDEX idx_siparisler_musteri_tarih ON siparisler(musteri_id, created_at DESC);
SELECT * FROM siparisler 
WHERE musteri_id = 123
ORDER BY created_at DESC 
LIMIT 5;
```

#### Verimsiz Sıralama

```sql
-- ❌ Tüm tabloyu sıralayıp sonra ilk 10'unu alır
SELECT * FROM siparisler 
ORDER BY RANDOM() 
LIMIT 10;

-- ❌ Index olmayan sütuna göre sıralama
SELECT * FROM urunler 
ORDER BY aciklama 
LIMIT 20;
```

### 4. Subquery vs JOIN: Hangi Durum için Hangisi?

Aynı sonucu hem subquery (alt sorgu) hem de JOIN ile elde edebilirsiniz. Peki hangisi daha hızlı?

#### EXISTS ile Subquery (Genellikle Hızlı)

```sql
-- Sipariş veren müşterileri bul
SELECT kullanici_adi FROM kullanicilar m
WHERE EXISTS (
    SELECT 1 FROM siparisler s 
    WHERE s.musteri_id = m.id
);
```

#### JOIN ile Aynı Sonuç

```sql
-- Aynı sonuç, ama dikkat: DISTINCT gerekebilir
SELECT DISTINCT m.kullanici_adi 
FROM kullanicilar m
INNER JOIN siparisler s ON m.id = s.musteri_id;
```

**Genel Kural:** Sadece varlık kontrolü (`EXISTS`) yapıyorsanız, subquery genellikle daha hızlıdır. Sağ tablodaki verileri de kullanacaksanız, JOIN tercih edilmelidir.

### 5. Aggregate Fonksiyonları ve GROUP BY Optimizasyonu

Büyük veri kümelerinde `COUNT`, `SUM`, `AVG` gibi toplama işlemleri yavaşlayabilir.

#### Verimli Gruplama

```sql
-- ✅ Index'li sütunlara göre gruplamak hızlıdır
SELECT kategori_id, COUNT(*) 
FROM urunler 
GROUP BY kategori_id;

-- ✅ WHERE ile önce filtrelemek gruplamayı hızlandırır
SELECT kategori_id, AVG(fiyat)
FROM urunler 
WHERE aktif = TRUE 
GROUP BY kategori_id;
```

#### HAVING vs WHERE Farkı

```sql
-- ✅ Önce WHERE ile filtrele, sonra grupla
SELECT kategori_id, COUNT(*) AS adet
FROM urunler 
WHERE fiyat > 100  -- Gruplama öncesi filtre
GROUP BY kategori_id
HAVING COUNT(*) > 5;  -- Gruplama sonrası filtre
```

`WHERE` koşulları gruplama öncesi çalıştığı için daha az veriyly çalışır ve genellikle index kullanabilir. `HAVING` ise gruplama sonrası çalışır.

### 6. Günlük Geliştirmede Performans Kontrolleri

#### Sorgu Yazarken Kontrol Listesi

1. **Index Kontrolü:** `WHERE`, `JOIN`, `ORDER BY` sütunlarında index var mı?
2. **EXPLAIN Test:** Sorguyu çalıştırmadan önce planı kontrol et.
3. **LIMIT Kullanımı:** Test sırasında her zaman `LIMIT` ekle.
4. **Function Kontrolü:** `WHERE` koşullarında solda fonksiyon var mı?

#### Hızlı Performance Check

```sql
-- Sorgunuzun planını kontrol edin
EXPLAIN (ANALYZE, BUFFERS) 
SELECT ... FROM ... WHERE ...;

-- Çok yavaşsa (>100ms), index eksikliği olabilir
-- Seq Scan görüyorsanız, WHERE sütunlarına index ekleyin
```

### 7. N+1 Query Problemini Önlemek

Bu, uygulama katmanında sık karşılaşılan bir performans felaketidir.

#### ❌ N+1 Problem (Yavaş)
```sql
-- 1. Ana sorgu
SELECT id, kullanici_adi FROM kullanicilar LIMIT 100;

-- 2. Her kullanıcı için ayrı sorgu (100 kez!)
SELECT COUNT(*) FROM siparisler WHERE musteri_id = 1;
SELECT COUNT(*) FROM siparisler WHERE musteri_id = 2;
-- ... 100 kez tekrar
```

#### ✅ Çözüm: Tek Sorguda Birleştir
```sql
-- Tüm bilgiyi tek sorguda al
SELECT 
    m.id,
    m.kullanici_adi,
    COUNT(s.id) AS siparis_sayisi
FROM kullanicilar m
LEFT JOIN siparisler s ON m.id = s.musteri_id
GROUP BY m.id, m.kullanici_adi
LIMIT 100;
```

### Sonuç: Optimize Düşünmek

Sorgu optimizasyonu, kod yazmaya başladığınız andan itibaren düşünmeniz gereken bir konudur. Sorguyu yazarken "bu nasıl çalışacak?" sorusunu sormak, sonradan "neden yavaş?" sorunuyla uğraşmaktan çok daha verimlidir.

En önemli prensipler:
- **Index'lerinizi tanıyın** ve onlarla uyumlu sorgular yazın
- **JOIN'lerinizi dikkatli tasarlayın** ve her zaman `ON` koşulunu kontrol edin  
- **EXPLAIN'i alışkanlık haline getirin** - görmeden inanmayın
- **Test verisiyle değil, gerçek boyutlarda test edin** - 100 satırlık tabloda her şey hızlıdır

Bir sonraki bölümde, PostgreSQL'in modern özelliklerinden biri olan JSONB ile nasıl esnek veri modelleri oluşturacağımızı ve bunları da verimli şekilde nasıl sorgulayacağımızı öğreneceğiz.