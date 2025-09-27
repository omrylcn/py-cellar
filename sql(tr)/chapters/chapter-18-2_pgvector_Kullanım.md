## Chapter 12-2: Uygulama Zamanı: `pgvector` ile Anlamsal Sorgular ve Performans Optimizasyonu

Önceki bölümde, anlamsal aramanın "neden" gerekli olduğunu ve "vector embedding"lerin bu sorunu nasıl çözdüğünü öğrendik. Artık teoriyi bir kenara bırakıp pratiğe dökme zamanı. Bu bölümde, `pgvector`'ı veritabanımıza nasıl kuracağımızı, anlamsal sorguları nasıl yazacağımızı ve en önemlisi, bu sorguları milyonlarca kayıt üzerinde milisaniyeler içinde çalışacak şekilde nasıl optimize edeceğimizi adım adım göreceğiz.

### 1\. Kurulum ve Tablo Yapılandırması

Her şeyden önce, `pgvector`'ı veritabanımızda çalışır hale getirmemiz gerekiyor.

**Adım 1: Eklentiyi Aktif Etmek**
Çoğu modern PostgreSQL hosting sağlayıcısı `pgvector`'ı destekler. Tek yapmanız gereken, veritabanınıza bağlanıp şu komutu çalıştırmaktır:

```sql
-- "vector" eklentisini mevcut veritabanında aktif et
CREATE EXTENSION IF NOT EXISTS vector;
```

**Adım 2: Vektör Sütununu Oluşturmak**
Şimdi, vektörlerimizi saklayacağımız sütunu tablomuza ekleyelim. Unutmayın, vektörün boyutunu (dimension) kullandığınız yapay zeka modeline göre belirtmeniz **zorunludur**. Popüler modellerden biri olan OpenAI'ın `text-embedding-3-small` modeli 1536 boyutlu vektörler üretir.

```sql
CREATE TABLE urunler (
    id BIGINT GENERATED ALWAYS AS IDENTITY PRIMARY KEY,
    urun_adi TEXT NOT NULL,
    aciklama TEXT,
    -- 1536 boyutlu vektörleri saklamak için bir sütun
    aciklama_embedding vector(1536)
);
```

**Adım 3: Veriyi Vektörlerle Doldurmak**
Daha önce de belirttiğimiz gibi, bu adım uygulamanızın backend'inde gerçekleşir. Ama veritabanında nasıl görüneceğini bilmek önemlidir.

```sql
-- UYGULAMA KATMANINDA:
-- 1. aciklama_metni = "Nefes alabilen kumaştan yapılmış, hafif koşu ayakkabısı."
-- 2. embedding_vektoru = OpenAI_API.get_embedding(aciklama_metni)
--    Sonuç: [0.0123, -0.4567, ..., 0.8910]

-- VERİTABANINA KAYDETME:
INSERT INTO urunler (urun_adi, aciklama, aciklama_embedding)
VALUES (
    'Hızlı Koşucu X2000',
    'Nefes alabilen kumaştan yapılmış, hafif koşu ayakkabısı.',
    -- PostgreSQL'e bir vektör (dizi) bu şekilde gönderilir
    ARRAY[0.0123, -0.4567, ..., 0.8910]::vector
);
```

### 2\. Anlamı Sorgulamak: Vektör Operatörleri

Verilerimizi vektörleştirdiğimize göre, şimdi aralarındaki anlamsal mesafeyi ölçebiliriz. Unutmayın: **düşük mesafe = yüksek benzerlik**.

`pgvector` bunun için üç temel operatör sunar:

* `<->` **L2 Mesafesi (Euclidean Distance):** İki vektör arasındaki en kısa, düz çizgi mesafesidir. Genellikle görsel (resim) aramalarda iyi çalışır.
* `<#>` **İç Çarpım (Inner Product):** İki vektörün ne kadar aynı yönde olduğunu ölçer.
* `<=>` **Kosinüs Mesafesi (Cosine Distance):** İki vektör arasındaki açıyı ölçer. Vektörlerin uzunluğunu önemsemeden sadece "yönlerine", yani "anlamlarına" odaklandığı için **metin benzerliği sorgularında endüstri standardı haline gelmiştir.**

**Pratik Bir Anlamsal Arama Sorgusu:**
Bir kullanıcı arama kutusuna **"ofis için rahat sandalye"** yazdı.

1. **Uygulama Tarafı:** `kullanici_sorgusu = "ofis için rahat sandalye"` metni alınır ve aynı embedding modeli kullanılarak bir sorgu vektörüne `(:kullanici_sorgu_vektoru)` dönüştürülür.
2. **Veritabanı Tarafı:** Bu vektör, veritabanındaki tüm ürün vektörleriyle karşılaştırılır.

<!-- end list -->

```sql
SELECT
    id,
    urun_adi,
    aciklama
FROM
    urunler
ORDER BY
    -- Her bir ürünün embedding'i ile kullanıcının sorgu embedding'i
    -- arasındaki kosinüs mesafesini hesapla ve ona göre sırala.
    aciklama_embedding <=> :kullanici_sorgu_vektoru
LIMIT 5; -- Benzerliği en yüksek (mesafesi en düşük) ilk 5 ürünü getir.
```

Bu sorgu, ürün açıklamasında "ofis", "rahat" veya "sandalye" kelimeleri geçmese bile, "ergonomik çalışma koltuğu" veya "bel destekli koltuk" gibi anlamsal olarak alakalı ürünleri en üst sıralarda getirecektir.

### 3\. Saniyelere Karşı Milisaniyeler: ANN Index'leri

Yukarıdaki sorgu sihirli gibi çalışır, ancak on binlerce satırdan sonra yavaşlamaya başlar. Çünkü PostgreSQL, doğru sıralamayı bulmak için kullanıcının sorgu vektörünü tablodaki **her bir** satırın vektörüyle karşılaştırmak zorundadır. Buna **brute-force** veya **Exact Nearest Neighbor** araması denir.

Çözüm, **Approximate Nearest Neighbor (ANN) index'leridir.** Bu index'ler, en yakın komşuların %100'ünü bulmak yerine %99'unu bulmayı hedefler, ancak bunu yaparken hızı **100 kat veya daha fazla** artırır. Çoğu uygulama için bu küçük doğruluk payı, devasa performans kazancının yanında kesinlikle kabul edilebilirdir.

`pgvector` iki ana ANN index türü sunar:

* **IVFFlat:** Vektörleri önceden "kümelere" (cluster) ayırır. Arama yaparken, sadece sorgu vektörüne en yakın birkaç kümeyi tarayarak arama uzayını büyük ölçüde daraltır.
* **HNSW (Hierarchical Navigable Small World):** Vektörler arasında bir "otoban sistemi" gibi çok katmanlı bir graf yapısı oluşturur. Bu sayede arama işlemi, alakasız bölgeleri hızla atlayarak doğru "anlam mahallesine" çok verimli bir şekilde ulaşabilir. **Genellikle daha yüksek performans ve daha iyi doğruluk sunduğu için modern `pgvector` sürümlerinde varsayılan olarak tavsiye edilen seçenektir.**

**HNSW Index'i Oluşturma:**

```sql
-- Kosinüs işlemleri için optimize edilmiş bir HNSW index'i oluşturalım.
CREATE INDEX ON urunler USING hnsw (aciklama_embedding vector_cosine_ops);
```

Bu index oluşturulduktan sonra, az önce yazdığımız `ORDER BY ... LIMIT` sorgusunun `EXPLAIN ANALYZE` çıktısı, artık yavaş bir `Sequential Scan` yerine, bu index'i kullanan ve çok daha hızlı olan bir `Index Scan` gösterecektir.

### 4\. Hibrit Arama: Anahtar Kelime + Anlam Gücü

Bazen kullanıcılar çok spesifik bir şey arar ("iPhone 15 Pro Mavi"). Bu durumda, anlamsal arama "benzer telefonlar" getirebilir, ancak kullanıcı tam olarak aradığını en üstte görmek ister. En iyi kullanıcı deneyimi genellikle **Hibrit Arama** ile elde edilir:

1. **Anlamsal Arama:** `pgvector` ile anlamsal olarak en alakalı 20 sonucu bulun.
2. **Anahtar Kelime Arama:** PostgreSQL'in kendi Full-Text Search özelliği ile "iPhone", "15", "Pro" kelimelerini içeren 20 sonucu bulun.
3. **Yeniden Sıralama (Re-ranking):** Uygulama katmanında, her iki listede de görünen sonuçlara öncelik vererek veya daha karmaşık sıralama algoritmaları kullanarak bu iki listeyi akıllıca birleştirin.

Bu yaklaşım, hem anlamsal keşif esnekliği hem de anahtar kelime kesinliği sunarak her iki dünyanın da en iyi yönlerini bir araya getirir.

**Sonuç:** `pgvector`, PostgreSQL'i geleneksel bir "kayıt sistemi" olmaktan çıkarıp, modern yapay zeka uygulamaları için veriyi "anlayan bir sisteme" dönüştürür. Doğru kullanıldığında, uygulamalarınıza daha önce mümkün olmayan, akıllı ve sezgisel özellikler katmanızı sağlar. Bu, PostgreSQL'in sadece bir veritabanı değil, eksiksiz bir veri platformu olduğunun en güçlü kanıtlarından biridir.
