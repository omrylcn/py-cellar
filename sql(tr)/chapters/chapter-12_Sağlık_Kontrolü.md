## Chapter 12: Veritabanının Sağlık Kontrolü: Temel Bakım İşlemleri ve İzleme

Şimdiye kadar mükemmel bir veritabanı inşa ettik: sağlam tablolar, akıllı ilişkiler, hızlı index'ler ve optimize sorgular. Ancak bir veritabanı canlı bir organizma gibidir - zamanla büyür, değişir ve bakıma ihtiyaç duyar. En iyi tasarlanmış sistem bile düzenli bakım yapılmazsa yavaşlar, şişer ve sonunda sorun çıkarır.

Bu bölümde, PostgreSQL veritabanınızın uzun vadede sağlıklı ve performanslı kalması için ihtiyaç duyduğu temel bakım işlemlerini, izleme tekniklerini ve en iyi pratikleri öğreneceğiz. Buradaki bilgiler, veritabanınızı günlük üretim kullanımında sorunsuz çalıştırmanın anahtarıdır.

### 1. VACUUM: Veritabanının Çöp Toplayıcısı

PostgreSQL'in MVCC (Multi-Version Concurrency Control) mimarisi nedeniyle, eski ve güncellenmiş kayıtlar fiziksel olarak hemen silinmez. Bu "ölü satırlar" (dead tuples) zamanla birikir ve veritabanınızı yavaşlatır.

#### `VACUUM` Ne Yapar?

```sql
-- Belirli bir tabloda ölü satırları temizler
VACUUM urunler;

-- Tüm veritabanında temizlik yapar
VACUUM;

-- Daha detaylı çıktı için
VACUUM VERBOSE urunler;
```

**VACUUM işlemi:**
- Ölü satırları işaretleyerek yeniden kullanılabilir hale getirir
- Table bloat'ı (şişkinlik) azaltır
- FSM (Free Space Map) bilgilerini günceller
- Ancak disk alanını işletim sistemine geri vermez

#### `VACUUM FULL`: Köklü Temizlik

```sql
-- Tabloyu tamamen yeniden organize eder
VACUUM FULL urunler;
```

**⚠️ Önemli Uyarı:** `VACUUM FULL` tabloyu kilitler ve çok uzun sürebilir. Production ortamında çok dikkatli kullanılmalıdır.

#### Otomatik VACUUM (Autovacuum)

PostgreSQL varsayılan olarak otomatik VACUUM çalıştırır. Ayarlarını kontrol edin:

```sql
-- Autovacuum ayarlarını göster
SHOW autovacuum;
SHOW autovacuum_naptime;

-- Tabloya özel ayar yapmak
ALTER TABLE cok_degisen_tablo SET (
    autovacuum_vacuum_threshold = 50,
    autovacuum_vacuum_scale_factor = 0.1
);
```

### 2. ANALYZE: İstatistik Güncelleyicisi

Sorgu planlayıcısının doğru kararlar verebilmesi için güncel istatistiklere ihtiyacı vardır.

#### Temel ANALYZE Kullanımı

```sql
-- Bir tablonun istatistiklerini güncelle
ANALYZE kullanicilar;

-- Tüm veritabanının istatistiklerini güncelle
ANALYZE;

-- Detaylı çıktı ile
ANALYZE VERBOSE siparisler;
```

#### Ne Zaman ANALYZE Yapmalısınız?

- Büyük miktarda veri ekleme/silme/güncelleme sonrası
- Index oluşturduktan sonra
- Sorgu performansında beklenmedik düşüş olduğunda
- Yeni tablolar oluşturduktan sonra

```sql
-- Büyük veri operasyonu sonrası
INSERT INTO urunler SELECT * FROM import_tablosu; -- 100k kayıt eklendi
ANALYZE urunler; -- İstatistikleri hemen güncelle
```

### 3. REINDEX: Index Yenileme

Index'ler zamanla şişebilir (bloat) ve performansları düşebilir.

#### Index Yenileme Stratejileri

```sql
-- Tek bir index'i yenile
REINDEX INDEX idx_urunler_kategori;

-- Bir tablonun tüm index'lerini yenile
REINDEX TABLE urunler;

-- Production için güvenli yol: CONCURRENTLY
REINDEX INDEX CONCURRENTLY idx_urunler_kategori;
```

#### Ne Zaman REINDEX Gerekir?

```sql
-- Index bloat'ını kontrol etmek için
SELECT 
    schemaname,
    tablename,
    indexname,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_size,
    idx_scan,
    idx_tup_read,
    idx_tup_fetch
FROM pg_stat_user_indexes
ORDER BY pg_relation_size(indexrelid) DESC;
```

Eğer çok büyük ama az kullanılan index'ler görüyorsanız, REINDEX düşünebilirsiniz.

### 4. Disk Alanı İzleme

Veritabanınızın ne kadar yer kapladığını düzenli olarak kontrol etmek kritiktir.

#### Tablo ve Index Boyutları

```sql
-- En büyük tabloları listele
SELECT 
    schemaname,
    tablename,
    pg_size_pretty(pg_total_relation_size(schemaname||'.'||tablename)) AS total_size,
    pg_size_pretty(pg_relation_size(schemaname||'.'||tablename)) AS table_size,
    pg_size_pretty(pg_indexes_size(schemaname||'.'||tablename)) AS index_size
FROM pg_tables
WHERE schemaname = 'public'
ORDER BY pg_total_relation_size(schemaname||'.'||tablename) DESC
LIMIT 10;

-- Veritabanının toplam boyutu
SELECT pg_size_pretty(pg_database_size(current_database()));
```

#### Log Dosyalarını İzleme

```sql
-- Log dosyalarının yerini öğren
SHOW log_directory;
SHOW log_filename;

-- Bağlantı sayısını kontrol et
SELECT count(*) as active_connections 
FROM pg_stat_activity 
WHERE state = 'active';

-- En uzun süren sorgular
SELECT 
    pid,
    now() - pg_stat_activity.query_start AS duration,
    query 
FROM pg_stat_activity 
WHERE (now() - pg_stat_activity.query_start) > interval '5 minutes'
ORDER BY duration DESC;
```

### 5. Backup Stratejileri

Veri kaybı her an olabilir. Düzenli backup, veritabanı yönetiminin en kritik parçasıdır.

#### pg_dump ile Mantıksal Backup

```bash
# Tek veritabanı yedeği
pg_dump -h localhost -U kullanici_adi -d veritabani_adi > backup.sql

# Sıkıştırılmış backup
pg_dump -h localhost -U kullanici_adi -d veritabani_adi | gzip > backup.sql.gz

# Sadece şema (veri olmadan)
pg_dump --schema-only -h localhost -U kullanici_adi -d veritabani_adi > schema.sql

# Sadece veri (şema olmadan)
pg_dump --data-only -h localhost -U kullanici_adi -d veritabani_adi > data.sql
```

#### Backup'ı Geri Yükleme

```bash
# SQL backup'ından geri yükleme
psql -h localhost -U kullanici_adi -d veritabani_adi < backup.sql

# Sıkıştırılmış backup'ından geri yükleme
gunzip -c backup.sql.gz | psql -h localhost -U kullanici_adi -d veritabani_adi
```

#### Otomatik Backup Scripti

```bash
#!/bin/bash
# daily_backup.sh

DB_NAME="myapp_db"
BACKUP_DIR="/backups"
DATE=$(date +%Y%m%d_%H%M%S)

# Backup oluştur
pg_dump $DB_NAME | gzip > $BACKUP_DIR/backup_$DATE.sql.gz

# 7 günden eski backup'ları sil
find $BACKUP_DIR -name "backup_*.sql.gz" -mtime +7 -delete

echo "Backup completed: backup_$DATE.sql.gz"
```

Bu scripti cron ile otomatikleştirin:
```bash
# Her gün 02:00'da backup al
0 2 * * * /path/to/daily_backup.sh
```

### 6. Performans İzleme ve Log Analizi

#### Temel Performans Metrikleri

```sql
-- Yavaş sorguları bulmak için pg_stat_statements kullanın
-- (postgresql.conf'da shared_preload_libraries = 'pg_stat_statements' gerekli)

SELECT 
    query,
    calls,
    total_time,
    mean_time,
    rows
FROM pg_stat_statements
ORDER BY mean_time DESC
LIMIT 10;
```

#### Cache Hit Ratio Kontrolü

```sql
-- Buffer cache verimliliği (yüksek olması iyidir)
SELECT 
    sum(heap_blks_hit) / (sum(heap_blks_hit) + sum(heap_blks_read)) AS cache_hit_ratio
FROM pg_statio_user_tables;
```

%95'in üzerinde olması idealdir. Düşükse daha fazla RAM gerekebilir.

#### Connection Monitoring

```sql
-- Aktif bağlantılar ve durumları
SELECT 
    state,
    count(*) 
FROM pg_stat_activity 
GROUP BY state;

-- En uzun süren idle bağlantılar
SELECT 
    pid,
    usename,
    application_name,
    state,
    now() - state_change AS idle_duration
FROM pg_stat_activity 
WHERE state = 'idle'
ORDER BY idle_duration DESC;
```

### 7. Güvenlik ve Kullanıcı Yönetimi

#### Kullanıcı Yetkileri Kontrolü

```sql
-- Kullanıcıları ve yetkilerini listele
\du

-- Bir kullanıcının tablo yetkilerini kontrol et
SELECT 
    table_schema,
    table_name,
    privilege_type
FROM information_schema.table_privileges
WHERE grantee = 'kullanici_adi';
```

#### Güvenlik Best Practices

```sql
-- Güçlü şifre politikası
ALTER USER kullanici_adi PASSWORD 'güçlü_şifre_123!';

-- Gereksiz süper kullanıcı yetkilerini kaldır
ALTER USER app_user NOSUPERUSER;

-- Bağlantı limitini ayarla
ALTER USER app_user CONNECTION LIMIT 10;
```

### 8. Günlük Bakım Rutini

#### Haftalık Kontrol Listesi

```sql
-- 1. Otomatik vacuum çalışıyor mu?
SELECT 
    schemaname,
    tablename,
    last_vacuum,
    last_autovacuum,
    last_analyze,
    last_autoanalyze
FROM pg_stat_user_tables
WHERE last_autovacuum IS NULL OR last_autovacuum < now() - interval '1 week';

-- 2. Büyük tablolarda bloat var mı?
-- (Önceki bölümlerdeki disk alanı sorgularını kullanın)

-- 3. Backup'lar düzenli alınıyor mu?
-- (Backup scriptinin log'larını kontrol edin)

-- 4. Yavaş sorgular var mı?
-- (pg_stat_statements tablosunu kontrol edin)
```

#### Aylık Derin Kontrol

- Tüm index'lerin gerçekten kullanıldığını kontrol edin
- Log dosyalarında error pattern'leri arayın
- Disk alanı trendlerini inceleyin
- Backup geri yükleme testleri yapın

### Sonuç: Proaktif Yaklaşım

Veritabanı bakımı, yangın söndürme işi değil, yangın çıkmasını önleme işidir. Düzenli bakım:

- **Performans sorunlarını önceden tespit eder**
- **Veri güvenliğini sağlar** (backup'lar sayesinde)
- **Sistem kararlılığını artırır** (bloat, dead tuple temizliği)
- **Kapasite planlaması yapar** (disk alanı, connection monitoring)

Bu bakım rutinlerini otomatikleştirin ve düzenli olarak kontrol edin. Bir sonraki bölümde, bu temel bilgilerin üzerine inşa edeceğimiz daha ileri seviye konulara geçeceğiz.

**💡 Pro-Tavsiye:** Bu bakım işlemlerini production saatlerinde yapmayın. Gece veya hafta sonu gibi düşük trafik saatlerini tercih edin ve her zaman test ortamında önce deneyin.