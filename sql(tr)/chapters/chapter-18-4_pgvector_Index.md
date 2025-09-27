## Chapter 12-4: Vektör Uzayında Rota Çizmek: `pgvector` İçin Pratik Index Stratejileri

Önceki bölümlerde `pgvector`'ın ne olduğunu, nasıl sorgu atacağımızı ve onu hızlandırmak için HNSW ve IVFFlat gibi özel index'lere ihtiyacımız olduğunu öğrendik. Ancak üretim ortamında başarı, sadece `CREATE INDEX` komutunu bilmekten daha fazlasını gerektirir. Gerçek başarı, uygulamanızın özel ihtiyaçlarına göre doğru index türünü seçmek, bu index'i doğru şekilde ayarlamak ve onu geleneksel index'lerle akıllıca birleştirmekle gelir.

Bu bölümde, `pgvector` için bir index stratejisi geliştirmenin ardındaki mantığı ve takasları (trade-offs) inceleyeceğiz. Bu, demo projelerinden, production'da güvenle çalışacak sistemlere geçişin anahtarıdır.

### 1\. Stratejinin Kalbi: Hız, Doğruluk ve Maliyet Üçgeni

Bir `pgvector` index stratejisi seçerken, her zaman üç temel faktör arasında bir denge kurmaya çalışırsınız:

1. **Hız (Latency - Gecikme):** Bir arama sorgusunun sonuç döndürmesi ne kadar sürer? (Hedef: Mümkün olduğunca düşük).
2. **Doğruluk (Recall - Geri Çağırma):** Yaptığımız ANN (Yaklaşık) araması, teorik olarak mükemmel olan (ama yavaş olan) brute-force aramasının bulacağı en iyi sonuçların yüzde kaçını bulabildi? (Hedef: Mümkün olduğunca yüksek).
3. **Maliyet (Cost):** Bu, hem index'i oluşturma maliyeti (CPU, zaman) hem de onu diskte saklama maliyetidir (GB).

Bu üçünü aynı anda mükemmelleştiremezsiniz. Örneğin, doğruluğu %99'dan %99.9'a çıkarmak, sorgu hızınızı yarıya düşürebilir ve index boyutunu ikiye katlayabilir. İyi bir strateji, uygulamanız için "yeterince iyi" olan denge noktasını bulmaktır.

### 2\. Rakip Analizi: IVFFlat vs. HNSW - Ne Zaman Hangisi?

Her iki index türü de ANN problemini çözer, ancak farklı yaklaşımlara ve dolayısıyla farklı güçlü/zayıf yönlere sahiptirler.

**IVFFlat (Inverted File with Flat Compression)**

* **Nasıl Çalışır?** Vektör uzayını önceden belirlenmiş sayıda "kümeye" (`lists`) böler. Arama yaparken, önce sorgu vektörüne en yakın birkaç kümeyi (`probes`) belirler ve sadece bu kümelerin içindeki vektörleri tarar.
* **Ne Zaman Düşünülmeli?**
  * Veri setiniz büyük ölçüde **statikse** (çok sık ekleme/silme yapılmıyorsa).
  * Index'i oluşturduktan sonra veri eklemesi yapmayacaksanız veya nadiren yapacaksanız.
* **Dezavantajları:**
  * Yeni veri eklendikçe performansı ve doğruluğu düşebilir, çünkü yeni vektörler mevcut küme yapısına tam uymayabilir.
  * Ayarlanması gereken iki temel parametresi vardır (`lists` ve `probes`).

**HNSW (Hierarchical Navigable Small World)**

* **Nasıl Çalışır?** Vektörler arasında çok katmanlı bir "otoban" ağı (graf) oluşturur. Arama, en üst katmandaki uzun bağlantıları kullanarak hızla doğru bölgeye atlar ve ardından daha hassas bir arama için alt katmanlara iner.
* **Ne Zaman Kullanılmalı?**
  * Veri setiniz **dinamikse** (sürekli `INSERT`, `UPDATE`, `DELETE` işlemleri varsa).
  * Çoğu genel amaçlı modern uygulama için.
* **Avantajları:**
  * Yeni veri eklendiğinde bile performansını ve doğruluğunu çok daha iyi korur.
  * Genellikle aynı doğruluk seviyesi için IVFFlat'tan daha hızlıdır.

**Stratejik Karar:**

> **Varsayılan tercihiniz her zaman `HNSW` olmalıdır.** `pgvector` geliştiricilerinin de odaklandığı ve sürekli iyileştirdiği modern algoritma budur. Sadece çok özel, statik veri seti senaryolarınız varsa ve IVFFlat'ı ayarlama konusunda tecrübeliyseniz diğerini düşünün.

### 3\. Pratik Bir Kılavuz: HNSW Index'ini Ayarlama Stratejisi

`HNSW` index'ini oluştururken ve kullanırken, hız ve doğruluk dengesini ayarlamak için elinizde güçlü düğmeler bulunur.

**Strateji:**

1. **Adım: Makul Varsayılanlarla Başlayın.** Index'i oluştururken genellikle iyi bir başlangıç noktası olan standart parametreleri kullanın.

    ```sql
    CREATE INDEX ON urunler USING hnsw (aciklama_embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
    ```

2. **Adım: Önce Sorgu Zamanını (`ef_search`) Ayarlayın.** Index'i yeniden inşa etmek pahalıdır. İlk optimizasyon denemeniz her zaman, sorgu bazında değiştirebileceğiniz `ef_search` parametresi olmalıdır.
      * **Düşük `ef_search` (örn: 20):** Çok hızlı ama daha düşük doğruluk.
      * **Yüksek `ef_search` (örn: 200):** Daha yavaş ama çok daha yüksek doğruluk.
        Uygulamanızın ihtiyacı olan minimum doğruluk seviyesini sağlayan en düşük `ef_search` değerini bularak başlayın.
    <!-- end list -->
    ```sql
    SET hnsw.ef_search = 100; -- Bu değeri test ederek ayarlayın
    EXPLAIN ANALYZE SELECT id FROM urunler ORDER BY aciklama_embedding <=> :query_vector LIMIT 10;
    ```

3. **Adım: Gerekirse İnşa Zamanını (`m`) Ayarlayın.** Eğer istediğiniz doğruluk seviyesine ulaşmak için `ef_search`'ü çok yüksek değerlere çekmeniz gerekiyorsa ve bu da sorguyu yavaşlatıyorsa, bu, index'inizin graf yapısının yeterince kaliteli olmadığının bir işareti olabilir. Bu durumda, index'i daha yüksek bir `m` değeriyle (örn: `m = 24` veya `m = 32`) yeniden inşa etmeyi düşünebilirsiniz. Bu, daha kaliteli bir index oluşturur ve aynı doğruluk seviyesine daha düşük bir `ef_search` değeriyle ulaşmanızı sağlayabilir.

### 4\. Hibrit Stratejiler: Vektör Index'lerini B-Tree ile Birleştirmek

Bu, üretim ortamındaki en kritik stratejidir.

**Problem:** Kullanıcılar genellikle "anlamsal arama" ile "filtrelemeyi" birleştirmek ister. Örn: "Bana **'ayakkabı' kategorisindeki**, **stokta olan** ve **'yürüyüş' kelimesine benzer** ürünleri getir."

**Strateji: Entegre Filtreleme**

* **Index'ler:**
    1. Vektör sütunu üzerinde bir **HNSW index'i**.
    2. `kategori_id` ve `stok_durumu` gibi filtre sütunları üzerinde standart **B-Tree index'leri**.
* **Sorgu:**

    ```sql
    SELECT id, urun_adi FROM urunler
    WHERE kategori_id = 5 AND stok_durumu = TRUE
    ORDER BY aciklama_embedding <=> :query_vector
    LIMIT 10;
    ```

* **Neden Çalışır?** `pgvector`'ın modern sürümleri, bu sorguyu son derece verimli bir şekilde çalıştırmak için tasarlanmıştır. Sorgu planlayıcısı, önce B-Tree index'lerini kullanarak aday sayısını (örneğin milyonlarca ürün içinden sadece stoktaki ayakkabılara) düşürür. Ardından, HNSW index'i sadece bu çok daha küçük ve filtrelenmiş alt küme üzerinde anlamsal arama yapar. Bu, hem hızlı hem de doğru sonuçlar almanızı sağlayan en iyi yöntemdir.

**Sonuç:** `pgvector` index stratejisi, körü körüne bir index oluşturmaktan ibaret değildir. Bu, uygulamanızın hız, doğruluk ve maliyet gereksinimlerini anlamak; HNSW gibi modern algoritmaları bilinçli bir şekilde ayarlamak; ve en önemlisi, PostgreSQL'in ilişkisel gücünü (B-Tree index'leri ile filtreleme) vektör aramanın anlamsal gücüyle birleştirmektir. Bu stratejileri benimseyerek, PostgreSQL üzerinde gerçekten sağlam ve yüksek performanslı yapay zeka uygulamaları inşa edebilirsiniz.
