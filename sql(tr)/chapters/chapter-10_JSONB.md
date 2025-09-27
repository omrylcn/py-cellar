## Chapter 11: PostgreSQL'in İsviçre Çakısı: `JSONB` ile Esnek Veri Modelleme Sanatı

Şimdiye kadarki yolculuğumuzda, verilerimizi katı kuralları olan, iyi tanımlanmış sütunlara ve tablolara yerleştirdik. Bu, ilişkisel veritabanlarının temel gücüdür: yapı ve tutarlılık. Peki ya verilerimiz her zaman bu kadar düzenli değilse? Ya bir ürünün özellikleri kategoriden kategoriye tamamen değişiyorsa? Bir "telefon" için "ekran boyutu" önemliyken, bir "kitap" için "sayfa sayısı" önemlidir. Bu tür yarı-yapılandırılmış (semi-structured) verileri nasıl yönetiriz?

Cevap, PostgreSQL'in içinde barındırdığı NoSQL gücü olan `JSONB` veri türünde yatıyor. `JSONB`, size ilişkisel bir veritabanının ACID garantilerini ve sorgulama gücünü feda etmeden şema esnekliği sunan bir "İsviçre Çakısı"dır. Bu bölümde, `JSONB`'nin neden bu kadar devrimsel olduğunu, nasıl etkili bir şekilde kullanılacağını ve onu nasıl ışık hızında sorgulayacağımızı öğreneceğiz.

### 1\. Neden Israrla `JSONB`? `JSON`'dan Gerçek Farkı Ne?

Önceki bölümlerde `JSONB`'yi `JSON`'a tercih etmemiz gerektiğini söylemiştik. Şimdi bu konuyu netleştirelim.

* **`JSON` (Metin Tabanlı):** Girdiğiniz JSON verisini, boşlukları, anahtar sırasını ve formatını **olduğu gibi metin olarak** saklar.

  * **Avantajı:** Veri eklemek (`INSERT`) bir tık daha hızlıdır çünkü veritabanı veriyi analiz etmez.
  * **Dezavantajı:** Her sorguladığınızda, PostgreSQL'in bu metni baştan sona yeniden ayrıştırması (parse etmesi) gerekir. Bu, sorguları **çok yavaşlatır** ve etkili bir şekilde indexlenemez.

* **`JSONB` (Binary / İkili Format):** Girdiğiniz JSON verisini ayrıştırır, optimize eder ve verimli bir **binary formatta** saklar.

  * **Dezavantajı:** Veri eklemek, bu ilk ayrıştırma adımı nedeniyle bir tık daha yavaştır.
  * **Avantajı:** Veri zaten "anlaşılmış" bir formatta olduğu için sorgulamak **kat kat daha hızlıdır**. En önemlisi, içindeki her bir anahtar ve değeri index'lememizi sağlayan **GIN index'lerini** destekler.

> **🏆 Altın Kural:** Bir anlık yazma hızındaki o minicik kayıp, sorgulama hızında kazandığınız devasa avantaja her zaman değer. Özel bir nedeniniz yoksa, **her zaman ve sadece `JSONB` kullanın.**

### 2\. `JSONB` ile Veri Eklemek ve Güncellemek

Gelin `urunler` tablomuza, her ürünün kendine özgü özelliklerini tutacak bir `JSONB` sütunu ekleyelim.

```sql
CREATE TABLE urunler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    urun_adi TEXT NOT NULL,
    kategori_id INTEGER REFERENCES kategoriler(id),
    -- Esnek özellikler için JSONB sütunumuz
    ozellikler JSONB
);

-- Yeni bir ürün ekleyelim
INSERT INTO urunler (urun_adi, kategori_id, ozellikler)
VALUES (
    'ThinkBook 15 Gen 2',
    1, -- 'Elektronik' kategorisi
    '{
        "marka": "Lenovo",
        "islemci": "Intel i7",
        "ram_gb": 16,
        "disk": {"tip": "SSD", "boyut_gb": 512},
        "renkler": ["gri", "siyah"]
    }'::jsonb
);
```

**Mevcut Bir `JSONB`'yi Güncellemek:**

PostgreSQL, `JSONB` verisini değiştirmek için güçlü operatörler sunar.

* **`||` (Birleştirme Operatörü):** En sık kullanılan operatördür. Mevcut `JSONB`'ye yeni bir anahtar/değer ekler veya var olan bir anahtarın değerini günceller.

    ```sql
    -- Ürüne yeni özellikler ekleyelim (stok) ve işlemciyi güncelleyelim.
    UPDATE urunler
    SET ozellikler = ozellikler || '{"islemci": "Intel i9", "stok": 50}'::jsonb
    WHERE urun_adi = 'ThinkBook 15 Gen 2';
    ```

* **`-` (Silme Operatörü):** Üst seviye bir anahtarı siler.

    ```sql
    -- 'stok' anahtarını özelliklerden kaldıralım.
    UPDATE urunler
    SET ozellikler = ozellikler - 'stok'
    WHERE urun_adi = 'ThinkBook 15 Gen 2';
    ```

* **`jsonb_set` Fonksiyonu:** Daha karmaşık ve hedefli güncellemeler için kullanılır. Özellikle iç içe (nested) objeleri değiştirmek için harikadır.

### 3\. `JSONB`'yi Sorgulamak: Operatörler ve Fonksiyonlar

`JSONB`'nin asıl gücü, onu sorgulama yeteneğimizde ortaya çıkar. İşte en önemli operatörler:

* **`->` ve `->>` (Alan Çıkarma):**

  * `->`: Bir alana erişir ve sonucu **`JSONB`** olarak döndürür.
  * `->>`: Bir alana erişir ve sonucu **`TEXT`** olarak döndürür. Genellikle `WHERE` koşullarında karşılaştırma yapmak için bu kullanılır.

* **`#>` ve `#>>` (İç İçe Alan Çıkarma):**

  * `#>`: `{key1, key2}` gibi bir "yol" (path) kullanarak iç içe bir alana erişir ve sonucu **`JSONB`** olarak döndürür.
  * `#>>`: Aynı şekilde bir yola erişir ve sonucu **`TEXT`** olarak döndürür.

* **`@>` (Contains / İçeriyor mu?):** En güçlü sorgulama operatörüdür. Soldaki `JSONB` verisinin, sağdaki küçük `JSONB` parçasını içerip içermediğini kontrol eder. Bu, GIN index'lerinin hızlandırdığı temel operatördür.

* **`?` (Exists / Var mı?):** Üst seviyede belirli bir anahtarın var olup olmadığını kontrol eder.

**Örnek Sorgular:**

```sql
-- Markası 'Lenovo' olan tüm ürünleri bul (sonucu TEXT olarak al ve karşılaştır).
SELECT urun_adi FROM urunler WHERE ozellikler ->> 'marka' = 'Lenovo';

-- Disk tipi 'SSD' olan ürünleri bul (iç içe objeye erişim).
SELECT urun_adi FROM urunler WHERE ozellikler #>> '{disk, tip}' = 'SSD';

-- İçinde 'siyah' rengi olan ürünleri bul.
-- @> operatörü diziler için de çalışır!
SELECT urun_adi FROM urunler WHERE ozellikler -> 'renkler' @> '["siyah"]'::jsonb;

-- Hem işlemcisi 'Intel i7' olan HEM DE 16 GB RAM'e sahip ürünleri bul.
-- Bu, @> operatörünün gerçek gücüdür. Çoklu filtrelemeyi basitleştirir.
SELECT urun_adi FROM urunler
WHERE ozellikler @> '{"islemci": "Intel i7", "ram_gb": 16}'::jsonb;

-- 'stok' anahtarı olan tüm ürünleri listele.
SELECT urun_adi FROM urunler WHERE ozellikler ? 'stok';
```

### 4\. `JSONB`'yi Hızlandırmak: GIN Index'in Gücü

Yukarıdaki sorgular küçük tablolarda hızlı çalışır, ama milyonlarca ürününüz olduğunda yavaş kalırlar. Çözüm, `JSONB` için özel olarak tasarlanmış **GIN index**'idir.

**a) Genel GIN Index'i (Her şeyi index'ler):**
Bu, `JSONB` sütununun içindeki **tüm** anahtar ve değerleri index'ler. `@>`, `?`, `?|`, `?&` gibi varlık ve içerik kontrolü yapan operatörleri hızlandırmak için idealdir.

```sql
CREATE INDEX idx_urunler_ozellikler_gin ON urunler USING GIN (ozellikler);
```

**b) Expression Index (Belirli Bir Alanı Index'ler):**
Eğer sorgularınızın %90'ı `JSONB` içindeki tek bir alana göre yapılıyorsa (örneğin hep markaya göre arama yapıyorsanız), o alan üzerinde bir B-Tree index'i oluşturmak daha verimli olabilir.

```sql
-- Sadece 'marka' alanını index'ler. Bu, B-Tree olduğu için LIKE veya aralık
-- sorgularını da destekler (eğer alan sayısal olsaydı).
CREATE INDEX idx_urunler_ozellikler_marka_btree ON urunler ((ozellikler ->> 'marka'));
```

### 5\. Ne Zaman `JSONB` Kullanmalı (ve Ne Zaman Kullanmamalı)?

`JSONB` güçlü bir araçtır, ama her sorunun çözümü değildir.

**✅ İdeal Kullanım Alanları:**

* **Yarı-Yapılandırılmış Veriler:** Ürün özellikleri, farklı olay (event) log'ları, anket cevapları gibi alan sayısı ve tipi değişen veriler.
* **Kullanıcı Ayarları/Profilleri:** Her kullanıcı için farklı olabilecek ayarları tek bir alanda tutmak.
* **Hızlı Prototipleme:** Uygulamanın başlarında şema henüz tam oturmamışken esneklik sağlamak.

**❌ Kötü Kullanım Alanları (Anti-Pattern'ler):**

* **İlişkisel Veriyi Değiştirmek:** Bir kullanıcının `departman_id`'sini, siparişin `musteri_id`'sini `JSONB` içinde saklamak korkunç bir fikirdir. Eğer bir veri:
  * Her zaman varsa (`NOT NULL`),
  * Sabit bir veri tipine sahipse,
  * Sıkça `JOIN` işlemlerinde kullanılacaksa,
  * Üzerinde `FOREIGN KEY` gibi kısıtlamalar olacaksa,
        **O veri kesinlikle kendi normal sütununda olmalıdır.**
* **Her Şeyi `JSONB`'ye Koymak:** `id, data JSONB` şeklinde iki sütunlu tablolarla tüm uygulamayı tasarlamaya çalışmak, PostgreSQL'in ilişkisel gücünü (foreign key'ler, join verimliliği, kısıtlamalar) çöpe atmak demektir.

**En İyi Yaklaşım: Hibrit Model**
En güçlü ve yaygın kullanım, **hibrit modeldir**. Core (çekirdek), yapısal verilerinizi normal sütunlarda (`id`, `urun_adi`, `fiyat`, `kategori_id`), esnek ve yarı-yapılandırılmış verilerinizi ise `ozellikler` gibi bir `JSONB` sütununda saklayın. Bu size her iki dünyanın da en iyi yönlerini sunar: yapı ve esneklik bir arada.
