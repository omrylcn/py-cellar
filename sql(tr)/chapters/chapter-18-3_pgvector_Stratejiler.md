## Chapter 12-3: Üretim Ortamında `pgvector`: İnce Ayar, Filtreleme ve Bakım Stratejileri

Önceki iki bölümde `pgvector`'ın ne olduğunu anladık ve temel anlamsal sorguları nasıl yapacağımızı öğrendik. Bir "proof of concept" (kavram kanıtlama) projesi için bu yeterli olabilir. Ancak sistemi canlıya aldığınızda, milyonlarca kullanıcıya hizmet verirken yeni ve daha karmaşık sorularla karşılaşırsınız:

  * "Benzer ürünleri getir AMA **sadece 'ayakkabı' kategorisinde olan ve fiyatı 500 TL'den az olanları**" nasıl verimli bir şekilde sorgularım?
  * Yaptığım aramanın **doğruluğu (recall)** ile **hızı (latency)** arasındaki dengeyi nasıl ayarlarım?
  * Kullandığım yapay zeka modeli güncellendiğinde, veritabanımdaki milyonlarca vektörü nasıl yöneteceğim?

Bu bölümde, `pgvector`'ı bir demo aracından çıkarıp, production seviyesinde, sağlam ve yönetilebilir bir sisteme dönüştüren ileri düzey teknikleri ve stratejileri ele alacağız.

### 1\. Cerrah Hassasiyeti: HNSW Index'lerinde İnce Ayar (Tuning)

Önceki bölümde `USING hnsw` ile bir index oluşturduk. Bu, çoğu zaman iyi bir başlangıçtır, ancak HNSW index'i, performans ve doğruluk arasında ince bir denge kurmanızı sağlayan ayar düğmelerine sahiptir.

**Temel Denge:** **Doğruluk (Recall)** vs. **Hız (Query Speed)**.

  * **Yüksek Doğruluk (High Recall):** Sorgunuza en uygun sonuçların neredeyse tamamını bulmak demektir.
  * **Yüksek Hız (High Speed):** Sorguya milisaniyeler içinde cevap vermek demektir.
    Bu ikisini aynı anda en üst seviyeye çıkarmak genellikle mümkün değildir. Birinden kazandığınızda diğerinden biraz kaybedersiniz.

**Ayarlayabileceğiniz Parametreler:**

1.  **İnşa Zamanı (`CREATE INDEX`):**

      * `m`: Bir graf düğümünün (vektörün) sahip olacağı maksimum komşu sayısıdır. Daha yüksek `m` değeri, daha yoğun ve daha kaliteli bir graf oluşturur. Bu, doğruluğu artırır ama index boyutunu ve inşa süresini de artırır.
      * `ef_construction`: Index inşa edilirken arama listesinin ne kadar büyük olacağını belirler. Daha yüksek değer, daha kaliteli bir index anlamına gelir ancak inşa süresini **ciddi şekilde** uzatır.

    <!-- end list -->

    ```sql
    -- Daha yüksek doğruluk hedefleyen bir index (daha yavaş inşa edilir)
    CREATE INDEX ON urunler USING hnsw (aciklama_embedding vector_cosine_ops)
    WITH (m = 32, ef_construction = 128);
    ```

2.  **Sorgu Zamanı (`SET` Komutu):**

      * `hnsw.ef_search`: Bu, en sık kullanacağınız ayardır. Her bir sorgu çalışmadan önce, o sorgu için arama listesinin ne kadar büyük olacağını belirler. Değeri ne kadar yüksek olursa, arama o kadar derine iner, doğruluk artar ama sorgu yavaşlar.

    <!-- end list -->

    ```sql
    BEGIN;
    -- Bu transaction içindeki sorgular için daha yüksek doğruluk hedefle
    SET LOCAL hnsw.ef_search = 100;
    -- Şimdi anlamsal arama sorgumuzu çalıştıralım
    SELECT id, urun_adi FROM urunler ORDER BY aciklama_embedding <=> :query_vector LIMIT 10;
    COMMIT;
    ```

Bu sayede, farklı kullanıcı senaryoları için farklı hız/doğruluk dengeleri kurabilirsiniz.

### 2\. En Güçlü Senaryo: Vektör Aramayı Metadata ile Filtreleme

Bu, `pgvector`'ın en önemli gerçek dünya kullanım senaryosudur. Kullanıcılar nadiren "bana benzer bir şey bul" derler. Genellikle, "bana **şu özelliklerdeki** benzer bir şey bul" derler.

**Problem:** `SELECT * FROM urunler WHERE kategori = 'Ayakkabı' AND stok_durumu = TRUE ORDER BY aciklama_embedding <=> :query_vector LIMIT 10;` sorgusunu nasıl verimli çalıştırırız?

**Çözüm:** `pgvector`'ın modern sürümleri (0.5.0 ve sonrası), HNSW index'lerinin bu tür geleneksel `WHERE` koşullarını **doğrudan desteklemesini** sağlar. Buna "pre-filtering" denir. `pgvector`, anlamsal arama yapmadan önce, index'i kullanarak sadece `kategori = 'Ayakkabı'` koşuluna uyan adayları verimli bir şekilde filtreleyebilir.

Bu özellik, `pgvector`'ı hibrit sorgular için inanılmaz derecede güçlü kılar. Artık iki adımlı (önce vektör ara, sonra filtrele) karmaşık sorgular yerine, tek bir temiz ve verimli SQL sorgusu yazabilirsiniz. Tek yapmanız gereken, `kategori` ve `stok_durumu` gibi filtreleme yapacağınız sütunlar üzerinde de standart B-Tree index'leri oluşturmaktır. Planlayıcı, en verimli yolu bulmak için her iki index'i de akıllıca kullanacaktır.

### 3\. Yaşam Döngüsü Yönetimi: Embedding'leri ve Index'leri Güncelleme

Yapay zeka dünyası hızla ilerliyor. Bugün kullandığınız embedding modeli, altı ay sonra yerini daha iyi ve daha verimli bir modele bırakabilir. Peki, yeni bir modele geçtiğinizde veritabanınızdaki milyonlarca eski vektörü ne yapacaksınız?

Bu, her `pgvector` kullanıcısının planlaması gereken bir **yaşam döngüsü yönetimi** stratejisidir.

**Önerilen Strateji (Sıfır Kesinti ile):**

1.  **Yeni Sütun Ekle:** Tablonuza, yeni modelin boyutuna uygun yeni bir vektör sütunu ekleyin.
    `ALTER TABLE urunler ADD COLUMN embedding_v2 vector(1024);`
2.  **Arka Plan İşlemi (Background Job):** Uygulamanızda, tablonuzdaki tüm satırları yavaş yavaş okuyan, `aciklama` metnini yeni modelin API'ına gönderen ve dönen vektörü `embedding_v2` sütununa yazan bir arka plan işlemi (script) oluşturun.
3.  **Yeni Index Oluştur:** Tüm veriler dönüştürüldükten sonra, yeni sütun üzerinde `CONCURRENTLY` seçeneği ile yeni HNSW index'inizi oluşturun.
    `CREATE INDEX CONCURRENTLY idx_urunler_embedding_v2 ON urunler USING hnsw (embedding_v2 vector_cosine_ops);`
4.  **Uygulamayı Güncelle:** Uygulama kodunuzdaki arama sorgularını, eski sütun yerine `embedding_v2` sütununu kullanacak şekilde güncelleyin ve canlıya alın.
5.  **Temizlik:** Her şeyin yolunda olduğundan emin olduktan sonra, eski vektör sütununu ve onun index'ini veritabanından kaldırarak disk alanını geri kazanın.
    `ALTER TABLE urunler DROP COLUMN aciklama_embedding;` (ilgili index otomatik olarak silinir).

### 4\. Maliyetler ve Dikkat Edilmesi Gerekenler

  * **API Maliyetleri:** Vektör oluşturmak için dış servisler (OpenAI vb.) kullanıyorsanız, her embedding bir API çağrısı ve dolayısıyla bir maliyet demektir. Milyonlarca kaydı yeniden index'leme sürecinin bütçesini planlamalısınız.
  * **Donanım (CPU & RAM):** Vektör araması, özellikle HNSW index'i, RAM'de çalışmayı sever. Index'inizin önemli bir kısmının RAM'e sığması, sorgu hızını ciddi şekilde etkiler. Bu, veritabanı sunucunuzun donanımını seçerken göz önünde bulundurmanız gereken bir faktördür.
  * **Depolama Maliyetleri:** Vektörler ve özellikle onların HNSW index'leri diskte önemli yer kaplayabilir. Yüksek boyutlu bir vektör verisinin index'i, verinin kendisinin 1.5-2 katı kadar yer tutabilir.

**Sonuç:** `pgvector`'ı production'da kullanmak, sadece `CREATE EXTENSION` demekten çok daha fazlasıdır. Bu, doğruluk ve hız arasında bilinçli kararlar vermeyi, modern filtreleme yeteneklerinden faydalanmayı ve verinin yaşam döngüsünü dikkatlice planlamayı gerektiren bir mühendislik disiplinidir. Bu stratejileri uygulayarak, PostgreSQL'i en zorlu yapay zeka uygulamaları için bile sağlam, ölçeklenebilir ve yönetilebilir bir temel olarak kullanabilirsiniz.