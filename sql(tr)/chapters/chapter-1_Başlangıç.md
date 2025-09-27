## Chapter 1: Veritabanı Dünyasına Giriş: PostgreSQL ile Sağlam Temeller Atmak

Modern dijital dünyada veriler, uygulamalarımızın kalbidir. Bir e-ticaret sitesindeki ürün bilgileri, sosyal medya platformundaki kullanıcı etkileşimleri, bankacılık uygulamalarındaki finansal işlemler... Tüm bunlar güvenli, hızlı ve tutarlı bir şekilde saklanmalı, işlenmeli ve erişilmelidir. İşte bu noktada **veritabanları** devreye girer.

Bu bölümde, veritabanı dünyasının temel kavramlarını öğrenecek, neden PostgreSQL'in modern uygulamalar için mükemmel bir seçim olduğunu anlayacak ve bu güçlü sistemin ardındaki felsefeyi kavrayacağız. Yolculuğumuzun temeli buradan başlıyor.

### Neden Veritabanına İhtiyacımız Var?

Verileri dosyalarda da saklayabiliriz, değil mi? Örneğin bir Excel dosyası veya JSON dosyası... Peki neden milyarlarca dolarlık bir endüstri veritabanları etrafında şekillenmiş?

**Basit Dosya Sistemlerinin Sorunları:**

- **Eş Zamanlı Erişim:** İki kullanıcı aynı anda aynı dosyayı değiştirirse ne olur?
- **Veri Tutarlılığı:** Elektrik kesilirse yarı yazılmış veri nasıl düzeltilir?
- **Performans:** Milyonlarca kayıt içinden belirli bir veriyi nasıl hızla buluruz?
- **Güvenlik:** Hassas verileri kim, nasıl erişim kontrolü ile koruruz?
- **Backup ve Kurtarma:** Veri kaybı durumunda sistemi nasıl geri getiririz?

Veritabanları, bu sorunların tamamına sistematik çözümler sunar.

### İlişkisel Veritabanı Modeli: Düzenin Gücü

**İlişkisel model**, 1970'de Edgar Codd tarafından önerilen ve bugün hala en yaygın kullanılan veri organizasyon yöntemidir. Temel prensipleri:

#### Tablo Yapısı

Veriler **tablolar** halinde organize edilir. Her tablo:

- **Satırlar (Rows/Records):** Gerçek veri kayıtları
- **Sütunlar (Columns/Fields):** Veri alanları, her sütunun belirli bir veri türü vardır
- **Şema (Schema):** Tablonun yapısını tanımlayan kurallar

```
kullanicilar tablosu:
+----+---------------+----------------------+---------------------+
| id | kullanici_adi | email                | kayit_tarihi        |
+----+---------------+----------------------+---------------------+
| 1  | johndoe       | john@example.com     | 2024-01-15 10:30:00 |
| 2  | alicesmith    | alice@example.com    | 2024-01-16 14:22:00 |
| 3  | bobwilson     | bob@example.com      | 2024-01-17 09:15:00 |
+----+---------------+----------------------+---------------------+
```

#### İlişkiler (Relationships)

Tablolar birbirleriyle **anahtarlar** aracılığıyla bağlanır:

- **Primary Key (Birincil Anahtar):** Her satırı benzersiz tanımlar
- **Foreign Key (Yabancı Anahtar):** Başka tablolara referans oluşturur

Bu yaklaşım, veri tekrarını önler ve tutarlılığı sağlar.

#### SQL: Evrensel Dil

**Structured Query Language (SQL)**, neredeyse tüm ilişkisel veritabanlarında kullanılan standart dildir. Bu, farklı sistemler arasında geçiş yapmayı kolaylaştırır.

### ACID Prensipleri: Güvenilirliğin Dört Temel Direği

İlişkisel veritabanlarının gücü, **ACID** adı verilen dört temel prensipte yatar. Bu prensipler, verilerinizin her koşulda güvenli ve tutarlı kalmasını garanti eder.

#### A - Atomicity (Atomiklik)

**Tümü ya da hiçbiri kuralı.** Bir işlem, ya tamamen başarılı olur ya da tamamen başarısız olur. Yarım kalan işlem olmaz.

**Örnek:** Banka hesabı transferi

```sql
BEGIN;
  UPDATE hesaplar SET bakiye = bakiye - 1000 WHERE hesap_no = 'A123';
  UPDATE hesaplar SET bakiye = bakiye + 1000 WHERE hesap_no = 'B456';
COMMIT;
```

Eğer ikinci UPDATE başarısız olursa, birinci UPDATE de otomatik olarak geri alınır. Para kaybolmaz veya kopyalanmaz.

#### C - Consistency (Tutarlılık)

**Veri bütünlüğü kuralları her zaman korunur.** Tanımladığınız kısıtlamalar (constraints) hiçbir koşulda ihlal edilemez.

**Örnek:** Yaş alanında negatif değer olmayacak şekilde kural koymuşsanız, hiçbir işlem bu kuralı çiğneyemez.

#### I - Isolation (İzolasyon)

**Eş zamanlı işlemler birbirini etkilemez.** Aynı anda çalışan işlemler, sanki tek başlarına çalışıyormuş gibi davranır.

**Örnek:** İki kullanıcı aynı anda bir ürünün son stok adedini satın almaya çalışsa bile, sistem bunları sırayla işler ve stok eksilmesini sağlar.

#### D - Durability (Kalıcılık)

**Onaylanan değişiklikler sonsuza kadar saklanır.** Sistem çökse bile, commit edilmiş veriler kaybolmaz.

### Transaction (İşlem): Atomik Çalışmanın Temeli

**Transaction**, bir veya birden fazla veritabanı işlemini tek bir "atomik birim" olarak gruplandırma yöntemidir.

#### Transaction Yaşam Döngüsü

```sql
BEGIN;                    -- Transaction başlat
  -- Bir dizi işlem
  INSERT INTO ...;
  UPDATE ...;
  DELETE FROM ...;
COMMIT;                   -- Değişiklikleri onayla ve kalıcı yap
-- Veya sorun çıkarsa: ROLLBACK;  -- Tüm değişiklikleri geri al
```

#### Isolation Levels (İzolasyon Seviyeleri)

PostgreSQL, eş zamanlı transaction'ların birbirini nasıl etkileyeceğini kontrol etmek için dört izolasyon seviyesi sunar:

1. **READ UNCOMMITTED:** En düşük izolasyon, nadir kullanılır
2. **READ COMMITTED:** PostgreSQL varsayılanı, çoğu uygulama için uygundur
3. **REPEATABLE READ:** Transaction boyunca tutarlı okuma garantisi
4. **SERIALIZABLE:** En yüksek izolasyon, transaction'lar sıralı çalışıyormuş gibi davranır

### PostgreSQL Nedir ve Neden Bu Kadar Güçlü?

**PostgreSQL**, "The World's Most Advanced Open Source Relational Database" sloganıyla tanınan, 30+ yıllık geliştirme geçmişine sahip, açık kaynaklı veritabanı sistemidir.

#### PostgreSQL'in Benzersiz Avantajları

**1. ACID Uyumluluğu ve Güvenilirlik**
PostgreSQL, ACID prensiplerini tam anlamıyla uygular. Bu, kritik uygulamalar için hayati önem taşır.

**2. Zengin Veri Türü Desteği**

- Standart SQL türleri (INTEGER, TEXT, DATE)
- Gelişmiş türler (UUID, JSONB, ARRAY)
- Özel türler (Network adresleri, Geometrik türler)
- Kullanıcı tanımlı türler

**3. Genişletilebilirlik**
Binlerce extension ile PostgreSQL'e yeni özellikler ekleyebilirsiniz:

- **PostGIS:** Coğrafi veri işleme
- **TimescaleDB:** Zaman serisi verileri
- **pg_stat_statements:** Performans analizi

**4. Gelişmiş Index Türleri**
B-tree, Hash, GIN, GiST, BRIN, SP-GiST... Her veri türü ve sorgu deseni için optimize index'ler.

**5. NoSQL Yetenekleri**
JSONB desteği ile ilişkisel ve dokümantal veritabanının avantajlarını birleştirir.

### PostgreSQL vs Diğer Veritabanları

| Özellik | PostgreSQL | MySQL | SQLite | MongoDB |
|---------|------------|-------|--------|---------|
| **ACID Uyumluluğu** | Tam | Kısmi (InnoDB ile) | Tam | Sınırlı |
| **JSON Desteği** | JSONB (native) | JSON (text-based) | JSON (extension) | Native |
| **Index Türleri** | 7+ çeşit | Sınırlı | B-tree ağırlıklı | B-tree, Text |
| **Eş Zamanlılık** | MVCC (mükemmel) | Karma | Sınırlı | Doküman seviyesi |
| **Lisans** | PostgreSQL (BSD-style) | GPL/Commercial | Public Domain | SSPL |
| **Öğrenme Eğrisi** | Orta | Kolay | Kolay | Farklı paradigma |

### Temel PostgreSQL Kavramları

#### Database Hiyerarşisi

```
PostgreSQL Cluster (Sunucu)
├── Database 1
│   ├── Schema 1 (public - varsayılan)
│   │   ├── Table 1
│   │   ├── Table 2
│   │   └── Index'ler, View'lar...
│   └── Schema 2
└── Database 2
```

#### SQL Komut Kategorileri

- **DDL (Data Definition Language):** CREATE, ALTER, DROP - Yapı tanımlama
- **DML (Data Manipulation Language):** INSERT, SELECT, UPDATE, DELETE - Veri işleme
- **DCL (Data Control Language):** GRANT, REVOKE - Yetki yönetimi
- **TCL (Transaction Control Language):** BEGIN, COMMIT, ROLLBACK - İşlem kontrol

### İlk PostgreSQL Kurulumu ve Bağlantı

#### Kurulum (Ubuntu/Debian)

```bash
# PostgreSQL kurulumu
sudo apt update
sudo apt install postgresql postgresql-contrib

# Servis başlatma
sudo systemctl start postgresql
sudo systemctl enable postgresql

# postgres kullanıcısına geçiş
sudo -u postgres psql
```

#### İlk Veritabanı ve Kullanıcı

```sql
-- Yeni kullanıcı oluştur
CREATE USER myapp_user WITH PASSWORD 'güçlü_şifre_123!';

-- Yeni veritabanı oluştur
CREATE DATABASE myapp_db OWNER myapp_user;

-- Kullanıcıya yetki ver
GRANT ALL PRIVILEGES ON DATABASE myapp_db TO myapp_user;
```

#### psql Komut Satırı Aracı

```bash
# Veritabanına bağlan
psql -h localhost -U myapp_user -d myapp_db

# Temel psql komutları
\l          -- Veritabanlarını listele
\dt         -- Tabloları listele
\d tablo    -- Tablo yapısını göster
\q          -- Çıkış
```

### Sonuç: Sağlam Temeller Üzerine İnşa Etmek

Bu bölümde, veritabanı dünyasının temel taşlarını öğrendik:

- **İlişkisel model** neden bu kadar güçlü ve yaygın
- **ACID prensipleri** nasıl veri güvenliğini sağlıyor
- **Transaction'lar** karmaşık işlemleri nasıl güvenli hale getiriyor
- **PostgreSQL** neden modern uygulamalar için ideal seçim

Bu temeller, ilerleyen bölümlerde öğreneceğimiz veri türleri, tablo tasarımı, index'leme ve optimizasyon tekniklerinin anlaşılmasında kritik rol oynayacak. Her bir kavram, diğerinin üzerine inşa edilecek ve sonunda size PostgreSQL'de uzman seviyesinde veritabanı yönetimi becerileri kazandıracak.
