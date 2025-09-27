## Chapter 4: Veritabanınızın Sarsılmaz Bekçileri: PostgreSQL'de Kısıtlamalar (Constraints) Sanatı

Önceki bölümlerde tablolarımızı inşa ettik ve onlara birer kimlik (`PRIMARY KEY`) verdik. Ancak bir şehri sadece binalar oluşturmaz; o şehri yaşanabilir kılan kurallar, yasalar ve sınırlar vardır. İşte **kısıtlamalar (constraints)**, veritabanı şehrimizin sarsılmaz kanunlarıdır. Görevleri, içeriye sadece geçerli, tutarlı ve mantıklı verilerin girmesini sağlayarak veri bütünlüğünü korumak ve kaosu önlemektir.

Kısıtlamalar birer tavsiye değil, PostgreSQL'in bizzat kendisinin uyguladığı, aşılamaz kurallardır. Bu bölümde, veritabanımızın beş temel bekçisini yakından tanıyacağız.

### 1\. `NOT NULL` - Boşluğa Yer Yok\

En temel ve en sık kullanılan bekçimizdir.

* **Görevi Nedir?** Bir sütuna atandığında, o sütunun `NULL` (yani boş veya tanımsız) bir değer içermesini engeller.
* **Neden Önemli?** Kritik bilgilerin her zaman var olmasını garanti altına alır. Bir `kullanicilar` tablosunda `email` veya `kullanici_adi` alanlarının boş olabildiğini düşünsenize\! Sistemin temel işlevleri çalışmaz hale gelirdi. `NOT NULL`, bu tür "olmazsa olmaz" verileri güvence altına alır.

<!-- end list -->

```sql
CREATE TABLE kullanicilar (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- Bu iki alan boş bırakılırsa PostgreSQL hata verir.
    kullanici_adi VARCHAR(50) UNIQUE NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    -- Bu alan boş bırakılabilir (NULL olabilir).
    biyografi TEXT
);
```

### 2\. `UNIQUE` - Her Biri Eşsiz

Bu bekçi, kopyalara ve tekrar eden verilere karşıdır.

* **Görevi Nedir?** Bir sütundaki veya bir grup sütundaki tüm değerlerin, tablo genelinde benzersiz (eşsiz) olmasını zorunlu kılar.
* **Neden Önemli?** Veri tekrarını önler. Her kullanıcının e-posta adresi, her ürünün stok kodu (SKU), her vatandaşın kimlik numarası benzersiz olmalıdır. `UNIQUE` kısıtlaması, aynı e-posta ile ikinci bir üyelik açılmasını veritabanı seviyesinde engeller.

> **💡 Pro-Tavsiye:** `UNIQUE` kısıtlaması olan bir sütuna birden fazla `NULL` değer girebilirsiniz. Çünkü SQL standardına göre `NULL`, başka bir `NULL`'a eşit değildir (bilinmeyen, bilinmeyene eşit olamaz).

```sql
CREATE TABLE urunler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    urun_adi TEXT NOT NULL,
    -- Her ürünün stok kodu benzersiz olmalı.
    stok_kodu VARCHAR(20) UNIQUE,
    -- Fiyat benzersiz olmak zorunda değil.
    fiyat NUMERIC(10, 2) NOT NULL
);
```

### 3\. `PRIMARY KEY` (Birincil Anahtar) - Tablonun Kimliği

Chapter 3'te ID olarak bahsettiğimiz bu yapı, aslında en güçlü kısıtlamadır.

* **Görevi Nedir?** Bir tablodaki her bir satırı şüpheye yer bırakmayacak şekilde tekil olarak tanımlar. Teknik olarak, `NOT NULL` ve `UNIQUE` kısıtlamalarının bir birleşimidir. Bir tablonun yalnızca **bir tane** birincil anahtarı olabilir.
* **Neden Önemli?**
    1. Bir satıra doğrudan ve en hızlı şekilde erişmenin yoludur. PostgreSQL, `PRIMARY KEY` için otomatik olarak yüksek performanslı bir index oluşturur.
    2. Tablolar arasındaki ilişkilerin (Foreign Key) temelini oluşturur.

**a) Tek Sütunlu Primary Key (En Yaygın Kullanım):**

```sql
CREATE TABLE musteriler (
    -- 'id' sütunu bu tablonun birincil anahtarıdır.
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    musteri_kodu VARCHAR(20) UNIQUE NOT NULL,
    ad TEXT NOT NULL
);
```

**b) Bileşik Primary Key (Composite Primary Key):**

Bazen bir satırı tek bir sütun değil, birden fazla sütunun kombinasyonu benzersiz kılar. Bu durumlarda, bu sütunların tamamı birincil anahtarı oluşturur. Bu en çok "ilişki tablolarında" (junction/linking tables) karşımıza çıkar.

```sql
-- Bu tablo, hangi siparişte hangi üründen kaç tane olduğunu tutar.
CREATE TABLE siparis_detaylari (
    siparis_id BIGINT, -- siparisler tablosuna referans
    urun_id BIGINT,    -- urunler tablosuna referans
    miktar INTEGER CHECK (miktar > 0),

    -- Bir siparişte aynı üründen iki farklı satır olamaz.
    -- Bu yüzden (siparis_id, urun_id) kombinasyonu benzersiz olmalıdır.
    PRIMARY KEY (siparis_id, urun_id)
);
```

### 4\. `FOREIGN KEY` (Yabancı Anahtar) - Tablolar Arası Köprüler

Bu bekçi, tablolar arasındaki ilişkilerin tutarlılığını sağlar. Veritabanınızın "ilişkisel" (relational) olmasının ardındaki en temel mekanizmadır.

* **Görevi Nedir?** Bir tablodaki bir sütunun (`siparisler.musteri_id`), başka bir tablonun `PRIMARY KEY`'ine (`musteriler.id`) başvurmasını sağlar.
* **Neden Önemli?** **Referans Bütünlüğünü (Referential Integrity)** korur. Yani, "yetim" kayıtların oluşmasını engeller. Örneğin:
  * Sistemde var olmayan bir müşteriye (`musteriler` tablosunda ID'si olmayan) bir sipariş oluşturulmasını engeller.
  * İçinde en az bir siparişi olan bir müşterinin yanlışlıkla silinmesini engeller.

<!-- end list -->

```sql
CREATE TABLE siparisler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    -- Bu sütun, musteriler tablosundaki 'id' sütununa bağlanacak.
    musteri_id BIGINT,
    siparis_tarihi TIMESTAMPTZ DEFAULT NOW(),

    -- Kısıtlamanın tanımı:
    CONSTRAINT fk_siparis_musteri -- Kısıtlamaya bir isim veriyoruz
        FOREIGN KEY (musteri_id) REFERENCES musteriler(id)
        ON DELETE RESTRICT  -- Bağlı olduğu müşteri silinirse ne olacağını belirle
        ON UPDATE CASCADE   -- Bağlı olduğu müşteri ID'si güncellenirse ne olacağını belirle
);
```

#### `ON DELETE` ve `ON UPDATE` Davranışları

Foreign Key'in en güçlü yanı, referans verilen kayıt silindiğinde (`ON DELETE`) veya güncellendiğinde (`ON UPDATE`) ne olacağını belirleyebilmenizdir:

* **`RESTRICT` (veya `NO ACTION` - Varsayılan):** En güvenli seçenektir. Siparişleri olan bir müşteriyi silmeye çalıştığınızda PostgreSQL "Bu müşteriye bağlı siparişler var, silemezsin\!" diyerek hata verir.
* **`CASCADE`:** En güçlü ama en tehlikeli seçenektir. Bir müşteriyi silerseniz, o müşteriye ait **tüm siparişler de otomatik olarak silinir**. Dikkatli kullanılmalıdır. (Örn: Bir blog yazısı silindiğinde, ona ait tüm yorumların da silinmesi `CASCADE` için iyi bir örnektir).
* **`SET NULL`:** Bir müşteri silinirse, o müşteriye ait siparişlerdeki `musteri_id` alanı `NULL` olarak güncellenir. Bu, siparişlerin sistemde kalmasını ama artık bir sahibinin olmamasını sağlar. (Bu seçeneği kullanabilmek için `musteri_id` sütununun `NULL` olmasına izin verilmelidir).

### 5\. `CHECK` - Kendi Kurallarını Koy

En esnek ve en güçlü bekçimizdir. İş mantığınızı (business logic) doğrudan veritabanı seviyesine taşımanızı sağlar.

* **Görevi Nedir?** Bir sütuna veya satıra yazılan verinin, sizin belirlediğiniz bir koşulu (`boolean` bir ifadeyi) sağlamasını zorunlu kılar. Koşul sağlanmazsa, işlem hata verir.
* **Neden Önemli?** Veri geçerliliğini garanti altına almanın en sağlam yoludur. Uygulama kodunda unutulan veya atlanan kontroller, `CHECK` kısıtlaması sayesinde mutlaka veritabanı tarafından yakalanır.

<!-- end list -->

```sql
CREATE TABLE etkinlikler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    etkinlik_adi TEXT NOT NULL,
    katilimci_sayisi INTEGER CHECK (katilimci_sayisi >= 0), -- Katılımcı sayısı negatif olamaz.
    fiyat NUMERIC(10, 2) CHECK (fiyat > 0), -- Fiyat 0'dan büyük olmalı.
    durum VARCHAR(20) CHECK (durum IN ('planlandi', 'aktif', 'iptal', 'tamamlandi')), -- Durum sadece bu değerlerden biri olabilir.
    baslangic_tarihi DATE,
    bitis_tarihi DATE,
    -- İki sütunu birden kontrol eden bir kural:
    CHECK (bitis_tarihi >= baslangic_tarihi)
);
```

### Sonuç

Bu beş kısıtlama, veritabanınızın temel direkleridir. Onları kullanmak bir angarya değil, gelecekte sizi sayısız saatlik veri temizleme ve hata ayıklama zahmetinden kurtaracak bir sigortadır.
