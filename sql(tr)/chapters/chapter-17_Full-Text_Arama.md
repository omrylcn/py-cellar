## Chapter 13: PostgreSQL ile Kendi Google'ınızı Kurun: Full-Text Search Derinlemesine Bakış

Şimdiye kadar verilerimizi tam eşleşmelerle (`id = 5`) veya basit kalıplarla (`ad LIKE 'Ahmet%'`) sorguladık. Peki ya kullanıcılarınızın bir blogda, bir ürün kataloğunda veya bir doküman arşivinde, tıpkı Google'da olduğu gibi, doğal bir dille arama yapmasını isterseniz ne olacak?

`LIKE '%arama kelimesi%'` kullanmak, bu iş için hem çok yavaş hem de çok "aptalca" bir yöntemdir. Çünkü `LIKE`:

* Index'leri verimli kullanamaz.
* Dilin kurallarını anlamaz. "Koşmak" diye arattığınızda, "koşuyor", "koştu" veya "koşan" kelimelerini bulamaz.
* Alaka düzeyini ölçemez. Bir kelimenin başlıkta mı yoksa metnin sonunda mı geçtiğini umursamaz.

İşte bu noktada, PostgreSQL'in kendi içinde gelen sofistike **Full-Text Search (FTS)** motoru devreye girer. Bu bölümde, FTS'nin nasıl çalıştığını, metinleri nasıl "anladığını" ve bu özelliği kullanarak uygulamalarınıza nasıl güçlü, hızlı ve dil-bilgisi kurallarına duyarlı bir arama yeteneği kazandıracağınızı öğreneceğiz.

### 1\. Full-Text Search'ün Anatomisi: Bir Metin Nasıl "Anlaşılır"?

PostgreSQL bir metni index'lemeden önce, onu bir dizi işlemden geçirir. Bu sürece "parsing" ve "lexing" denir.

**İşlem Adımları:**

1. **Parsing (Ayrıştırma):** Metin, "token" adı verilen temel birimlere (kelimeler, sayılar, e-posta adresleri vb.) ayrıştırılır.
2. **Normalization (Normalleştirme):** Her bir "token", "lexeme" adı verilen standartlaştırılmış bir forma dönüştürülür. Bu aşamada:
      * **Büyük/Küçük Harf Dönüşümü:** Tüm harfler küçültülür.
      * **Stop Word (Etkisiz Kelime) Elemesi:** "ve", "ile", "bir", "bu" gibi arama için anlam taşımayan yaygın kelimeler atılır.
      * **Stemming (Kök Bulma):** Kelimeler, dilin kurallarına göre eklerinden arındırılarak kök hallerine indirgenir. Bu, FTS'nin sihrinin gerçekleştiği yerdir. Örneğin, "aramalar", "arıyorum", "aranan" kelimelerinin hepsi "arama" köküne (lexeme) indirgenir.

Bu işlemler için iki temel fonksiyonumuz var:

* **`to_tsvector('dil', metin)`:** Bir metin bloğunu alır ve yukarıdaki işlemlerden geçirerek, arama için optimize edilmiş bir `tsvector` objesine dönüştürür. `tsvector`, her bir benzersiz "lexeme" ve onun orijinal metindeki pozisyonlarını içeren bir listedir.
* **`to_tsquery('dil', sorgu)`:** Kullanıcının arama metnini alır ve onu `&` (VE), `|` (VEYA), `!` (DEĞİL) gibi operatörlerle birleştirilmiş bir `tsquery` objesine dönüştürür.

<!-- end list -->

```sql
-- Bir metnin nasıl 'tsvector' haline geldiğini görelim
SELECT to_tsvector('turkish', 'PostgreSQL''de verimli aramalar yapmak harika!');
-- Çıktı: 'arama':4 'harika':6 'postgresql':1 'verimli':2 'yap':5

-- Bir sorgunun nasıl 'tsquery' haline geldiğini görelim
SELECT to_tsquery('turkish', 'verimli & arama');
-- Çıktı: 'verimli' & 'arama'
```

### 2\. Pratik Uygulama: FTS Sütunlarını Kurmak ve Doldurmak

Arama yapacağımız veriyi `tsvector` formatında tutmamız gerekir. Bunun için en iyi pratik, iki adımlı bir yöntemdir.

**Adım 1: `tsvector` Sütununu Tabloya Eklemek**
Arama yapılacak metinleri her sorguda yeniden `tsvector`'a çevirmek yerine, bu dönüşümün sonucunu tabloda ayrı bir sütunda saklamak çok daha performanslıdır.

```sql
ALTER TABLE makaleler ADD COLUMN tsv tsvector;
```

**Adım 2: Sütunu Otomatik Olarak Güncel Tutmak (Trigger Kullanımı)**
Bir makalenin başlığı veya içeriği değiştiğinde, `tsv` sütununun da otomatik olarak güncellenmesi gerekir. Bunun en sağlam yolu bir **trigger** kullanmaktır.

```sql
-- 1. Trigger'ın çalıştıracağı fonksiyonu oluştur
CREATE OR REPLACE FUNCTION makaleler_tsv_trigger() RETURNS trigger AS $$
BEGIN
    -- Başlık ve içeriği birleştirip 'turkish' dil kurallarına göre tsvector'a çevir
    -- ve yeni 'tsv' sütununa ata.
    -- coalesce, null değerleri boş metinle değiştirir.
    -- setweight, başlığa daha yüksek bir önem ("A") atar.
    new.tsv :=
        setweight(to_tsvector('turkish', coalesce(new.baslik, '')), 'A') ||
        setweight(to_tsvector('turkish', coalesce(new.icerik, '')), 'B');
    return new;
END
$$ LANGUAGE plpgsql;

-- 2. Trigger'ı oluştur
CREATE TRIGGER tsvectorupdate BEFORE INSERT OR UPDATE
    ON makaleler FOR EACH ROW EXECUTE PROCEDURE makaleler_tsv_trigger();
```

Bu trigger sayesinde, her yeni makale eklendiğinde veya güncellendiğinde, `tsv` sütunu otomatik olarak doğru `tsvector` değeriyle dolacaktır.

**Adım 3: Index Oluşturmak**
Son olarak, bu `tsv` sütunu üzerinde bir **GIN index'i** oluşturarak sorguları ışık hızına çıkarırız.

```sql
CREATE INDEX makaleler_tsv_idx ON makaleler USING GIN (tsv);
```

### 3\. Arama Sanatı: Sorgulama, Sıralama ve Vurgulama

Artık her şey hazır olduğuna göre, akıllı aramalar yapabiliriz.

* **Arama (`@@` operatörü):** `tsvector` ile `tsquery` arasındaki eşleşmeyi kontrol eden temel operatördür.
* **Sıralama (`ts_rank_cd` fonksiyonu):** Sonuçları, arama terimlerinin ne kadar sık ve ne kadar yakın geçtiğine göre bir "alaka puanı" vererek sıralar.
* **Vurgulama (`ts_headline` fonksiyonu):** Sonuçlarda, arama terimlerinin geçtiği yerleri, Google'daki gibi vurgulanmış bir metin parçası (snippet) olarak gösterir.

**Nihai Arama Sorgusu:**

```sql
-- Kullanıcının "veritabanı optimizasyonu" diye arattığını varsayalım
SELECT
    baslik,
    -- Sonuçları alaka düzeyine göre sıralamak için bir puan hesapla
    ts_rank_cd(tsv, to_tsquery('turkish', 'veritabanı & optimizasyon')) AS rank,
    -- Orijinal içerikte arama kelimelerinin geçtiği yeri vurgula
    ts_headline('turkish', icerik, to_tsquery('turkish', 'veritabanı & optimizasyon')) AS snippet
FROM
    makaleler
WHERE
    tsv @@ to_tsquery('turkish', 'veritabanı & optimizasyon')
ORDER BY
    rank DESC
LIMIT 10;
```

Bu tek sorgu, bize:

1. İçinde hem "veritabanı" hem de "optimizasyon" kelimelerinin (veya köklerinin) geçtiği makaleleri bulur.
2. Bu makaleleri, kelimelerin geçiş sıklığına ve yoğunluğuna göre en alakalıdan en alakasız olana doğru sıralar.
3. Her bir sonuç için, aranan kelimelerin etrafındaki metni vurgulayarak bir özet sunar.

**Sonuç:** PostgreSQL Full-Text Search, birçok uygulama için harici arama motorlarına (Elasticsearch gibi) ihtiyaç duymadan, doğrudan veritabanı içinde güçlü, hızlı ve dile duyarlı arama özellikleri oluşturmanıza olanak tanır. Doğru kurulduğunda ve index'lendiğinde, kullanıcılarınıza modern ve akıllı bir arama deneyimi sunmanın en verimli yollarından biridir.
