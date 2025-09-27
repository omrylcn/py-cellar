## Chapter 2: PostgreSQL'de Veri Türleri: Doğru Seçimlerle Sağlam Temeller Atmak

Bir veritabanı tasarlarken attığımız her adım, tıpkı bir bina inşa etmek gibidir. Tablolar binanın odalarıysa, bu odalarda saklayacağımız verilerin türünü belirlemek de o binanın temelini atmakla eşdeğerdir. Yanlış atılmış bir temel, gelecekte başımızı ağrıtacak performans sorunlarına, veri tutarsızlıklarına ve beklenmedik hatalara yol açabilir.

PostgreSQL, bize son derece zengin bir veri türü yelpazesi sunar. Bu bölümde, sadece komutları sıralamak yerine, hangi veri türünü **neden** ve **ne zaman** seçmemiz gerektiğini pratik kod örnekleriyle inceleyeceğiz.

### 1\. Sayısal Türler: Rakamların Dünyası

Uygulamalarımızın kalbinde genellikle sayılar yatar: kullanıcı ID'leri, ürün fiyatları, stok miktarları... Doğru sayısal türü seçmek, hem veritabanında gereksiz yer kaplamanın önüne geçer hem de gelecekteki büyüme potansiyelinizi karşılar.

#### Tam Sayılar: Kırıksız Değerler

Bir sayının ondalık kısmı yoksa, o bir tam sayıdır. PostgreSQL bunun için üç temel seçenek sunar:

  * `SMALLINT`: **2 byte** yer kaplar ve -32,768 ile 32,767 arasında değer alabilir. (Örn: Çalışan yaşı)
  * `INTEGER`: **4 byte** yer kaplar ve yaklaşık -2 milyar ile +2 milyar arasında değer alabilir. (Örn: Orta ölçekli bir tablonun ID'si)
  * `BIGINT`: **8 byte** yer kaplar ve neredeyse hayal edilemeyecek kadar büyük sayılar tutabilir. (Örn: Tüm yeni tabloların ID'leri için en iyi pratik)

> **💡 Pro-Tavsiye:** Yeni oluşturduğunuz tüm tablolarda, otomatik artan ID kolonları için veri türü olarak `BIGINT` seçmeyi alışkanlık haline getirin. Bugün size gereksiz gibi görünen bu 8 byte'lık depolama, yarın sizi büyük bir veritabanı migrasyon operasyonundan kurtarabilir.

**Örnek Kod:**

```sql
CREATE TABLE envanter (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY, -- Modern uygulamalar için standart ID
    stok_kodu INTEGER UNIQUE NOT NULL, -- 2 milyar ürün kodu yeterliyse
    raf_numarasi SMALLINT, -- 32,767'den fazla rafımız olmayacaksa
    stok_miktari INTEGER DEFAULT 0
);
```

#### Ondalıklı Sayılar: Hassasiyet ve Hız Arasında Bir Tercih

  * `NUMERIC(precision, scale)`: **Kesin (exact) ondalık değerler** için kullanılır. Paranın olduğu her yerde bu zorunludur.
  * `REAL` ve `DOUBLE PRECISION`: **Kayan noktalı (floating-point)**, yani yaklaşık değerler için kullanılır. Bilimsel hesaplamalarda tercih edilir.

**⚠️ Önemli Uyarı:** Asla ve asla finansal verileri saklamak için `REAL` veya `DOUBLE PRECISION` kullanmayın. Kayan nokta aritmetiğindeki yuvarlama hataları, zamanla birikerek ciddi finansal tutarsızlıklara yol açabilir.

**Örnek Kod:**

```sql
CREATE TABLE urunler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    urun_adi TEXT NOT NULL,
    fiyat NUMERIC(10, 2) NOT NULL, -- 99,999,999.99'a kadar olan fiyatlar için
    agirlik_kg DOUBLE PRECISION, -- Ağırlıkta küçük hassasiyet kayıpları tolere edilebilir
    indirim_orani REAL -- Hızlı hesaplama için
);
```

### 2\. Metin Türleri: Kelimelerin Gücü

  * `CHAR(n)`: **Sabit uzunluklu** metin. Neredeyse hiç kullanılmaz.
  * `VARCHAR(n)`: **Değişken uzunluklu** ve **limitli** metin. Veritabanı seviyesinde limit zorunluluğu varsa kullanılır.
  * `TEXT`: **Değişken uzunluklu** ve **sınırsız** metin. Genel amaçlı kullanım için en iyi seçenektir.

> **💡 Pro-Tavsiye:** PostgreSQL'de `VARCHAR(n)` ile `TEXT` arasında **hiçbir performans farkı yoktur**. Genel kural olarak, özel bir nedeniniz yoksa metin alanları için `TEXT` kullanın.

**Örnek Kod:**

```sql
CREATE TABLE makaleler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ulke_kodu CHAR(2) NOT NULL, -- 'TR', 'US' gibi sabit uzunluklu veri
    baslik VARCHAR(255) NOT NULL, -- SEO veya başka bir nedenle başlığı 255 karakter ile sınırlayalım
    icerik TEXT, -- Makale içeriğinin bir sınırı olmamalı
    ozet TEXT
);
```

### 3\. Tarih ve Zaman: Zamanda Yolculuk

Bu noktadaki en kritik ayrım `TIMESTAMP` ve `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`) arasındadır.

> **🏆 Altın Kural: Her zaman `TIMESTAMP WITH TIME ZONE` kullanın.**
>
> `TIMESTAMPTZ`, zaman damgalarını her zaman evrensel saat olan **UTC** formatında saklar ve size gösterirken sizin oturum zaman diliminize çevirir. Bu, farklı coğrafyalardaki kullanıcılar ve sunucular arasındaki zaman karmaşasını tamamen ortadan kaldırır.

**Örnek Kod:**

```sql
CREATE TABLE kullanicilar (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kullanici_adi VARCHAR(50) UNIQUE NOT NULL,
    dogum_tarihi DATE, -- Saate ihtiyacımız yok, sadece gün/ay/yıl
    kayit_tarihi TIMESTAMP WITH TIME ZONE DEFAULT NOW(), -- Yeni kayıt anını zaman dilimiyle birlikte sakla
    son_giris TIMESTAMP WITH TIME ZONE
);
```

### 4\. PostgreSQL'e Özgü Zengin Veri Türleri

PostgreSQL'i diğer veritabanlarından ayıran en güçlü özelliklerinden biri, standart SQL türlerinin ötesinde sunduğu zengin veri türleridir.

  * `UUID`: Evrensel olarak benzersiz bir tanımlayıcı.
  * `JSONB`: Sorgulanabilir ve indexlenebilir, binary JSON formatı. **Her zaman `JSON` yerine bunu tercih edin.**
  * `ARRAY` (Diziler): Herhangi bir veri türünün dizisi. Örn: `TEXT[]`.
  * `BOOLEAN`: `TRUE`, `FALSE` veya `NULL` değerlerini alır.

**Örnek Kod:**

```sql
-- UUID kullanabilmek için bu eklentiyi etkinleştirmek gerekebilir.
CREATE EXTENSION IF NOT EXISTS "pgcrypto";

CREATE TABLE blog_yazilari (
    id UUID DEFAULT gen_random_uuid() PRIMARY KEY, -- Tahmin edilemez, dağıtık sistemlere uygun ID
    makale_id BIGINT REFERENCES makaleler(id),
    yazar_id BIGINT REFERENCES kullanicilar(id),
    yayinlandi BOOLEAN DEFAULT FALSE, -- Evet/Hayır durumu
    etiketler TEXT[], -- ['postgresql', 'database', 'tutorial'] gibi bir metin dizisi
    meta_veri JSONB -- {'seo_title': '...', 'views': 1024} gibi esnek veri
);
```

### Özet ve En İyi Pratikler

Doğru veri türünü seçmek, gelecekteki sizi teknik borçtan kurtaran bir yatırımdır. Aklınızda kalması gereken en önemli noktalar:

  * **ID'ler için:** Her zaman `BIGINT` kullanın.
  * **Parasal değerler için:** Daima `NUMERIC` tercih edin.
  * **Metinler için:** Özel bir uzunluk kısıtlamanız yoksa `TEXT` kullanın.
  * **Zaman damgaları için:** Tartışmasız `TIMESTAMP WITH TIME ZONE` (`TIMESTAMPTZ`) kullanın.
  * **Esnek/Şemasız veriler için:** `JSONB`'nin gücünden faydalanın.

Verilerimizin ne türde olacağına karar verdiğimize göre, bir sonraki bölümde bu verileri barındıracak sağlam ve ilişkili tabloları nasıl oluşturacağımızı inceleyeceğiz.