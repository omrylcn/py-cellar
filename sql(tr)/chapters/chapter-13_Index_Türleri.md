## Chapter 6.1: PostgreSQL Index Türleri Derinlemesine: Her Veri için Doğru Aracı Seçme Sanatı

Önceki bölümde index'lerin veritabanımızın fihristleri olduğunu ve B-Tree'nin varsayılan seçim olduğunu öğrendik. Ancak PostgreSQL'in gerçek gücü, her türlü veri yapısı ve sorgu desenine özel olarak tasarlanmış zengin index türü yelpazesinde yatar. Bu bölümde, her index türünün süper gücünü keşfedecek ve hangi durumda hangi silahı kullanacağımızı öğreneceğiz.

Bir index türünü seçmek, doğru aletli bir usta olmakla benzerdir. B-Tree bir çok amaçlı tornavida ise, diğer index türleri özel işler için tasarlanmış hassas aletlerdir. Doğru aleti seçmek, işi sadece hızlandırmakla kalmaz, bazen imkansız görünen sorguları bile mümkün kılar.

### 1. B-Tree Index - Güvenilir Çok Amaçlı Usta (Varsayılan)

**Nasıl Çalışır?**
Verilerinizi dengeli bir ağaç yapısında, sıralı olarak tutar. Her düğüm belirli sayıda anahtar ve alt düğüm işaretçisi içerir. Arama yaparken, ağacın tepesinden başlayarak doğru yöne ilerler ve logaritmik zamanda hedefe ulaşır.

**Süper Güçleri:**
- Eşitlik sorguları (`WHERE id = 123`)
- Aralık sorguları (`WHERE created_at BETWEEN '2024-01-01' AND '2024-12-31'`)
- Sıralama (`ORDER BY price ASC`)
- Önek aramaları (`WHERE name LIKE 'John%'`)

**Ne Zaman Kullanılır?**
%95 durumda ilk tercihiniz olmalıdır. `PRIMARY KEY` ve `UNIQUE` kısıtlamaları otomatik olarak B-Tree index oluşturur.

```sql
-- En yaygın kullanım senaryoları
CREATE INDEX idx_orders_customer_id ON orders(customer_id);
CREATE INDEX idx_products_price ON products(price);
CREATE INDEX idx_users_created_at ON users(created_at);

-- Bileşik index (sütun sırası önemli!)
CREATE INDEX idx_orders_customer_date ON orders(customer_id, order_date);
```

**⚠️ Dikkat:** Bileşik index'lerde sütun sırası kritiktir. `(customer_id, order_date)` index'i, sadece `customer_id`'ye göre sorguları da hızlandırabilir, ama sadece `order_date`'e göre sorguları hızlandıramaz.

### 2. Hash Index - Jet Hızında Eşitlik Uzmanı

**Nasıl Çalışır?**
Sütun değerinin bir hash fonksiyonundan geçirerek elde ettiği sabit boyutlu bir sayıyı kullanır. Bu hash değeri, verinin disk üzerindeki konumunu doğrudan gösterir.

**Süper Güçleri:**
- Lightning-fast eşitlik sorguları (`WHERE user_id = 12345`)
- B-Tree'ye göre marjinal performans artışı (çok büyük tablolarda)

**Zayıflıkları:**
- Sadece eşitlik (`=`) işlemi destekler
- Aralık sorguları (`>`, `<`) desteklemez
- `ORDER BY` için kullanılamaz

**Ne Zaman Kullanılır?**
Modern PostgreSQL'de nadiren ihtiyaç duyulur. B-Tree genellikle aynı hızda ve çok daha esnek çalışır. Sadece çok büyük tablolarda ve sadece eşitlik yapacağınız kesin durumlarda düşünülebilir.

```sql
-- Çok nadir kullanım senaryosu
CREATE INDEX idx_sessions_token_hash ON user_sessions USING HASH (session_token);
```

### 3. GIN (Generalized Inverted Index) - Çok Değerli Veriler İçin Süper Kahraman

**Nasıl Çalışır?**
Ters index mantığında çalışır. Her benzersiz "kelime" (dizi elemanı, JSON anahtarı, metin kelimesi) için, o kelimenin geçtiği tüm satırların listesini tutar. Kitap fihristine benzer: her kelime hangi sayfalarda geçiyorsa onları listeler.

**Süper Güçleri:**
- **Dizi aramaları:** `WHERE tags @> ARRAY['postgresql']`
- **JSONB aramaları:** `WHERE data @> '{"status": "active"}'`
- **Full-text search:** `WHERE to_tsvector(content) @@ to_tsquery('database')`
- **İçerme operatörleri** (`@>`, `<@`, `@`, `?`)

**Ne Zaman Kullanılır?**
- Blog yazılarındaki etiket dizilerinde arama
- JSON meta verilerde anahtar/değer arama
- E-ticaret sitelerinde ürün özelliklerinde filtreleme
- Tam metin arama sistemleri

```sql
-- Blog etiketleri için
CREATE INDEX idx_posts_tags_gin ON blog_posts USING GIN (tags);
-- Sorgu: WHERE tags @> ARRAY['postgresql', 'database']

-- JSONB meta veriler için
CREATE INDEX idx_products_metadata_gin ON products USING GIN (metadata);
-- Sorgu: WHERE metadata @> '{"color": "red", "size": "large"}'

-- Full-text search için
CREATE INDEX idx_articles_content_gin ON articles USING GIN (to_tsvector('turkish', content));
-- Sorgu: WHERE to_tsvector('turkish', content) @@ to_tsquery('veritabanı & postgresql')
```

### 4. GiST (Generalized Search Tree) - Coğrafya ve Geometri Ustası

**Nasıl Çalışır?**
B-Tree'nin genelleştirilmiş hali. Karmaşık veri türleri için "yakınlık", "kesişim", "içerme" gibi ilişkileri hızla bulabilir. Üst üste binen kutular mantığında çalışır.

**Süper Güçleri:**
- **Coğrafi sorgular:** "Bana en yakın 5 restoran"
- **Aralık kesişimleri:** "Bu tarih aralığıyla çakışan tüm rezervasyonlar"
- **Geometrik hesaplamalar:** PostGIS ile harita uygulamaları
- **K-Nearest Neighbor (KNN) sorguları**

**Ne Zaman Kullanılır?**
- Harita uygulamaları (restaurant locator, Uber benzeri servisler)
- Otel rezervasyon sistemleri (tarih çakışma kontrolü)
- Coğrafi analiz uygulamaları

```sql
-- PostGIS ile coğrafi veriler için
CREATE INDEX idx_restaurants_location_gist ON restaurants USING GIST (location);
-- Sorgu: WHERE ST_DWithin(location, ST_Point(41.0082, 28.9784), 1000) -- 1km yakın

-- Tarih aralıkları için
CREATE INDEX idx_bookings_date_range_gist ON hotel_bookings USING GIST (daterange(check_in, check_out));
-- Sorgu: WHERE daterange(check_in, check_out) && daterange('2024-06-01', '2024-06-10')
```

### 5. BRIN (Block Range Index) - Dev Tablolar İçin Hafif Çözüm

**Nasıl Çalışır?**
Her veri bloğu (binlerce satır) için sadece minimum ve maksimum değerleri saklar. Çok küçük yer kaplar ama yaklaşık sonuçlar verir.

**Süper Güçleri:**
- **Minimal depolama alanı:** GB'larca tablo için MB'lık index
- **Hızlı bakım:** `INSERT`/`UPDATE` operasyonlarını yavaşlatmaz
- **Zaman serisi veriler için ideal**

**Ne Zaman Kullanılır?**
- Log tablolarında (sürekli sona eklenen veriler)
- Milyarlarca satırlık zaman serisi veriler
- IoT sensor verileri
- Mali işlem kayıtları

**⚠️ Ön Şart:** Verinin fiziksel sıralanması ile index'lenen sütun arasında yüksek korelasyon olmalı. Rastgele dağılmış veriler için etkisizdir.

```sql
-- Milyonlarca log kaydı için
CREATE INDEX idx_logs_created_at_brin ON logs USING BRIN (created_at);
-- Disk alanı: ~8KB (normal B-Tree: ~100MB olabilirdi)

-- IoT sensor verileri için
CREATE INDEX idx_sensor_data_timestamp_brin ON sensor_readings USING BRIN (timestamp);
```

### 6. SP-GiST (Space-Partitioned GiST) - Düzensiz Veri Yapıları Uzmanı

**Nasıl Çalışır?**
Veri uzayını örtüşmeyen bölgelere ayırır. Her bölge kendi içinde organize olur. Quad-tree, k-d tree gibi veri yapılarını destekler.

**Süper Güçleri:**
- **Düzensiz dağılımlı veriler** için optimize
- **Telefon numaraları, IP adresleri** gibi hiyerarşik veriler
- **Coğrafi veriler** (bazı durumlarda GiST'ten daha hızlı)

**Ne Zaman Kullanılır?**
- Telefon rehberi uygulamaları
- IP adres blok yönetimi
- Düzensiz coğrafi dağılım olan veriler

```sql
-- IP adresleri için
CREATE INDEX idx_access_logs_ip_spgist ON access_logs USING SPGIST (client_ip);

-- Telefon numaraları için
CREATE INDEX idx_contacts_phone_spgist ON contacts USING SPGIST (phone_number);
```

### 7. Bloom Index - Çok Boyutlu Filtreleme Ustası

**Nasıl Çalışır?**
Bloom filter algoritmasını kullanır. Birden çok sütunu tek bir kompakt yapıda birleştirir. Yanlış pozitifler olabilir ama yanlış negatifler asla olmaz.

**Süper Güçleri:**
- **Çok sütunlu AND sorguları** için optimize
- **Çok küçük index boyutu**
- **Hızlı yazma performansı**

**Ne Zaman Kullanılır?**
- E-ticaret filtreleme (marka AND kategori AND fiyat aralığı)
- Log analizi (birden çok kritere göre filtreleme)
- Veri ambarı uygulamaları

```sql
-- E-ticaret ürün filtreleme için
CREATE INDEX idx_products_bloom ON products 
USING BLOOM (category_id, brand_id, price_range, availability)
WITH (length=80, col1=2, col2=2, col3=4, col4=4);

-- Sorgu: WHERE category_id = 1 AND brand_id = 5 AND price_range = 2
```

### Index Türü Seçim Rehberi

| Sorgu Türü | Önerilen Index | Alternatif |
|------------|----------------|------------|
| `WHERE id = 123` | B-Tree | Hash |
| `WHERE price BETWEEN 10 AND 50` | B-Tree | - |
| `WHERE tags @> ARRAY['tag1']` | GIN | - |
| `WHERE data ->> 'status' = 'active'` | GIN | B-Tree (expression) |
| `WHERE created_at > NOW() - INTERVAL '1 day'` | B-Tree | BRIN (çok büyük tablolar) |
| Coğrafi yakınlık sorguları | GiST | SP-GiST |
| `WHERE col1 = ? AND col2 = ? AND col3 = ?` | Bloom | B-Tree (composite) |

### Sonuç: Hangi Aletinizi Ne Zaman Kullanacağınızı Bilin

Index türü seçimi, veritabanı performansının kritik bir parçasıdır. En iyi strateji:

1. **%90 durumda B-Tree ile başlayın** - Güvenli ve çok yönlü
2. **Özel ihtiyaçlarınızı belirleyin** - JSON, coğrafi veri, çok büyük tablolar
3. **Test edin ve ölçün** - `EXPLAIN ANALYZE` ile performansı doğrulayın
4. **Basit tutun** - Karmaşık index'ler yerine sorguyu optimize etmeyi düşünün

Unutmayın: En iyi index, ihtiyacınıza tam uyan index'tir. PostgreSQL'in bu zengin seçenek yelpazesi, neredeyse her veri yapısı ve sorgu desenine mükemmel uyum sağlamanızı mümkün kılar.