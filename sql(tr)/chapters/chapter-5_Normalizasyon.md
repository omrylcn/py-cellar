## Chapter 5: Veri Dünyasında Zen: Normalizasyon ve İlişki Tasarımı ile Kaostan Düzene

Şu ana kadar sağlam yapı malzemeleri (veri türleri), güvenli odalar (tablolar) ve bu odaların kurallarını (kısıtlamalar) öğrendik. Şimdi ise sıra mimarlıkta. Veri modelleme, bu odaları birbiriyle en mantıklı ve en verimli şekilde ilişkilendirerek veri tekrarını ortadan kaldırma ve veri bütünlüğünü en üst seviyeye çıkarma sanatıdır.

Bu sürecin merkezinde **Normalizasyon** adını verdiğimiz, veritabanını gereksiz tekrarlardan arındırma tekniği yer alır. Amacımız, dağınık bir Excel tablosu gibi görünen verileri, her bilginin tek bir doğru yerde saklandığı, düzenli bir kütüphaneye dönüştürmektir.

### Neden Normalizasyon ile Uğraşmalıyız?

Normalizasyon yapmadan tasarlanan bir veritabanı, üç temel "anomali" yani problemle karşılaşmaya mahkumdur:

1. **Güncelleme Anomalisi:** Aynı bilgi birden fazla yerde kayıtlıysa, bu bilgiyi güncellerken her bir kopyasını tek tek değiştirmek zorunda kalırsınız. Birini atlarsanız, veriniz tutarsız hale gelir.
2. **Ekleme Anomalisi:** Bir bilgiyi eklemek için, aslında onunla ilgisi olmayan başka bir bilginin varlığına ihtiyaç duyarsınız. (Örn: Henüz hiç çalışanı olmayan yeni bir departman açtınız ama departman adını kaydedebilmek için sisteme hayali bir çalışan eklemek zorunda kalıyorsunuz).
3. **Silme Anomalisi:** Bir kaydı sildiğinizde, aslında kaybetmek istemediğiniz başka bir bilgiyi de onunla birlikte istemeden silersiniz.

Normalizasyon, bu anomalileri ortadan kaldırmak için kanıtlanmış bir reçetedir. Gelin en yaygın üç normal formu (1NF, 2NF, 3NF) pratik örneklerle inceleyelim.

### Birinci Normal Form (1NF): Her Gözde Tek Bir Değer

**Kural:** Bir tablodaki her hücre (bir satır ve sütunun kesişimi) yalnızca tek bir "atomik" (bölünemez) değer içermelidir. Sütunlar, tekrar eden gruplar veya listeler içeremez.

**❌ Kötü Tasarım (1NF İhlali):**
Bir siparişteki ürünleri tek bir satırda tutmaya çalışalım.

```sql
CREATE TABLE kotu_siparis (
    siparis_id INTEGER,
    musteri_adi TEXT,
    urun1 TEXT, -- Tekrarlayan grup
    urun2 TEXT, -- Tekrarlayan grup
    urun3 TEXT  -- Tekrarlayan grup
);
```

**Problem:** Müşteri 4 ürün alırsa ne olacak? `urun4` sütunu mu ekleyeceğiz? Ya 50 ürün alırsa? Ayrıca "İçinde 'Monitor' olan tüm siparişleri bul" gibi bir sorgu yazmak kabusa dönüşür.

**✅ Doğru Tasarım (1NF'ye Uygun):**
Tekrar eden grubu (ürünleri) ayrı bir tabloya taşıyarak sorunu çözeriz.

```sql
CREATE TABLE siparisler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    musteri_id BIGINT REFERENCES musteriler(id),
    siparis_tarihi TIMESTAMPTZ DEFAULT NOW()
);

CREATE TABLE siparis_detaylari (
    siparis_id BIGINT REFERENCES siparisler(id),
    urun_id BIGINT REFERENCES urunler(id),
    miktar INTEGER,
    PRIMARY KEY (siparis_id, urun_id) -- Bileşik anahtar
);
```

Artık bir siparişe istediğimiz kadar ürün ekleyebiliriz. Her hücrede tek bir değer var.

### İkinci Normal Form (2NF): Her Şey Anahtarla İlgili Olmalı

**Kural:** Tablo 1NF'de olmalı ve **bileşik birincil anahtarı (composite primary key)** olan tablolardaki anahtar olmayan tüm sütunlar, anahtarın **tamamına** bağlı olmalıdır; sadece bir kısmına değil.

**❌ Kötü Tasarım (2NF İhlali - Kısmi Bağımlılık):**
`siparis_detaylari` tablosuna `urun_adi` bilgisini de ekleyelim. Birincil anahtarımız `(siparis_id, urun_id)`.

```sql
CREATE TABLE kotu_detay (
    siparis_id BIGINT,
    urun_id BIGINT,
    urun_adi TEXT, -- Sadece urun_id'ye bağımlı!
    miktar INTEGER,
    PRIMARY KEY (siparis_id, urun_id)
);
```

**Problem:** `miktar` sütunu, hangi siparişte (`siparis_id`) hangi üründen (`urun_id`) kaç tane olduğunu söyler; yani anahtarın tamamına bağlıdır. Ancak `urun_adi` sütunu, siparişin kimliğiyle ilgilenmez; **sadece `urun_id`'ye bağlıdır.** İşte bu bir **kısmi bağımlılıktır**. Eğer "Laptop" ürününün adını "Dizüstü Bilgisayar" olarak değiştirmek istersek, bu ürünün geçtiği **tüm** sipariş satırlarını tek tek güncellememiz gerekir. Bu, güncelleme anomalisinin ta kendisidir.

**✅ Doğru Tasarım (2NF'ye Uygun):**
Sadece anahtarın bir kısmına bağlı olan veriyi kendi tablosuna taşırız.

```sql
CREATE TABLE urunler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    urun_adi TEXT NOT NULL,
    fiyat NUMERIC(10, 2)
);

-- Bu tablo artık sadece anahtarın tamamına bağlı olan bilgiyi tutuyor.
CREATE TABLE siparis_detaylari (
    siparis_id BIGINT REFERENCES siparisler(id),
    urun_id BIGINT REFERENCES urunler(id),
    miktar INTEGER,
    PRIMARY KEY (siparis_id, urun_id)
);
```

### Üçüncü Normal Form (3NF): Dolaylı Yollara Sapma

**Kural:** Tablo 2NF'de olmalı ve anahtar olmayan hiçbir sütun, başka bir anahtar olmayan sütuna bağlı olmamalıdır. Yani anahtar olmayan sütunlar arasında **geçişli bağımlılık (transitive dependency)** bulunmamalıdır.

**❌ Kötü Tasarım (3NF İhlali - Geçişli Bağımlılık):**
Çalışanların departman bilgilerini tek bir tabloda tutalım. Anahtarımız `id`.

```sql
CREATE TABLE kotu_calisanlar (
    id BIGINT PRIMARY KEY,
    ad_soyad TEXT,
    departman_id INTEGER,
    departman_adi TEXT -- departman_id'ye geçişli bağımlı
);
```

**Problem:** `departman_adi`, birincil anahtar olan `id`'ye doğrudan bağlı değildir. `departman_adi`, `departman_id`'ye bağlıdır, `departman_id` de `id`'ye bağlıdır. (`id` -\> `departman_id` -\> `departman_adi`). Bu bir geçişli bağımlılıktır. "Pazarlama" departmanının adını "Marketing" olarak değiştirmek istediğimizde, bu departmandaki **tüm** çalışanların satırlarını tek tek güncellememiz gerekir.

**✅ Doğru Tasarım (3NF'ye Uygun):**
Geçişli bağımlılığı ortadan kaldırmak için departman bilgilerini kendi tablosuna alırız.

```sql
CREATE TABLE departmanlar (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    departman_adi TEXT NOT NULL
);

CREATE TABLE calisanlar (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    ad_soyad TEXT NOT NULL,
    departman_id INTEGER REFERENCES departmanlar(id)
);
```

Artık departman adını değiştirmek istediğimizde, `departmanlar` tablosunda sadece **tek bir satırı** güncellememiz yeterlidir.

### Temel İlişki Türleri - Tabloları Birbirine Bağlamak

Normalizasyon sonucunda ortaya çıkan temiz tablolarımızı şimdi birbirine bağlayalım.

#### One-to-One (Bire Bir)

Bir tablodaki tek bir kaydın, diğer tablodaki sadece tek bir kayda karşılık geldiği durumdur. Genellikle çok geniş tabloları bölmek, opsiyonel bilgileri ayırmak veya güvenlik katmanı oluşturmak için kullanılır.

```sql
CREATE TABLE kullanicilar (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    email TEXT UNIQUE NOT NULL,
    password_hash TEXT NOT NULL
);

-- Her kullanıcının sadece bir profili olabilir.
CREATE TABLE kullanici_profilleri (
    kullanici_id BIGINT PRIMARY KEY REFERENCES kullanicilar(id), -- Hem Primary Key hem Foreign Key
    ad TEXT,
    soyad TEXT,
    profil_resmi_url TEXT
);
```

#### One-to-Many (Bire Çok)

En yaygın ilişki türüdür. Bir tablodaki tek bir kayıt, diğer tablodaki birden çok kayda karşılık gelebilir.

```sql
CREATE TABLE kategoriler (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    kategori_adi TEXT NOT NULL
);

-- Bir kategoride birden çok ürün olabilir,
-- ama bir ürün sadece bir kategoriye aittir.
CREATE TABLE urunler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    urun_adi TEXT NOT NULL,
    kategori_id INTEGER REFERENCES kategoriler(id)
);
```

#### Many-to-Many (Çoka Çok)

Bir tablodaki bir kaydın diğer tablodaki birden çok kayda, ve tersinin de geçerli olduğu durumdur. Bu ilişkiyi kurmak için üçüncü bir **ilişki tablosuna (junction table)** ihtiyaç duyarız.

```sql
CREATE TABLE etiketler (
    id INTEGER GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    etiket_adi TEXT UNIQUE NOT NULL
);

-- Bir ürünün birden çok etiketi olabilir,
-- ve bir etiket birden çok ürüne atanabilir.
-- Bu ilişkiyi kuran Junction Tablosu:
CREATE TABLE urun_etiketleri (
    urun_id BIGINT REFERENCES urunler(id),
    etiket_id INTEGER REFERENCES etiketler(id),
    -- İki sütunun kombinasyonu anahtarı oluşturur:
    PRIMARY KEY (urun_id, etiket_id)
);
```

### Sonuç

Normalizasyon ve ilişki tasarımı, veritabanınızın iskeletini oluşturur. Bu prensiplere sadık kalmak, başta biraz daha fazla planlama gerektirse de, uzun vadede sizi veri tutarsızlıklarından, karmaşık sorgulardan ve bakım kabuslarından kurtarır. Genellikle, çoğu uygulama için **3NF** seviyesine ulaşmak, esneklik ve veri bütünlüğü arasında mükemmel bir denge sunar.
