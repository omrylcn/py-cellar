## Chapter 12-1: Yeni Bir Boyut: Vektör Veritabanlarının ve `pgvector`'ın Yükselişi

Önceki bölümlerde, veritabanımızı bir kütüphaneci hassasiyetiyle organize ettik. Her veriyi tam olarak nerede bulacağımızı biliyorduk. `id = 101` veya `email = 'test@example.com'` gibi sorgularla, kütüphanenin katalog sistemini kullanarak istediğimiz "kitaba" anında ulaşıyorduk.

Peki ya kütüphaneciye gidip, "Bana 'biraz hüzünlü ama umut dolu, deniz kenarında geçen' bir kitap verir misin?" diye sorsaydık? Geleneksel bir katalog (B-Tree index), bu sorgu karşısında çaresiz kalırdı. Çünkü bu sorgu, verinin **ne olduğuyla** değil, **ne hissettirdiğiyle** ve **ne anlama geldiğiyle** ilgilidir.

İşte bu, günümüz yapay zeka uygulamalarının çözmeye çalıştığı temel problemdir. Bu bölümde, bu anlamsal arama probleminin ne olduğunu, "vector embedding" adı verilen sihirli konsepti ve PostgreSQL'in bu yeni dünyaya `pgvector` ile nasıl adım attığını temelden anlayacağız.

### 1. Sorun: Anahtar Kelimelerin Sınırları

Geleneksel arama sistemleri, anahtar kelime eşleşmesine dayanır. "araba" diye aratırsanız, içinde "araba" geçen metinleri bulur. Ama kullanıcı aslında "otomobil", "taşıt", "jip" veya "sedan" kelimelerini içeren sonuçlarla da ilgileniyor olabilir. Sistem bunu bilemez. Bu temel sınırlamalar şunlardır:

* **Eşanlamlılık (Synonymy):** Farklı kelimeler aynı anlama gelebilir ("doktor" vs "hekim").
* **Çokanlamlılık (Polysemy):** Aynı kelime farklı anlamlara gelebilir ("yüz": surat, eylem, sayı).
* **Bağlam Eksikliği:** Sistem, kelimelerin bir araya geldiğinde oluşturduğu derin anlamı kavrayamaz.

Anlamsal arama (Semantic Search), bu sınırları aşarak kullanıcının **niyetini** anlamaya odaklanır.

### 2. Çözüm: Anlamı Matematiğe Dökmek - Vector Embeddings

Yapay zeka modellerinin (Large Language Models - LLM'ler) bize sunduğu en büyük devrimlerden biri, dili ve kavramları anlamalarını sağlayan **"embedding"** tekniğidir.

**Embedding Nedir?**
Bir embedding modeli, bir veri parçasını (bir kelime, bir cümle, bir ürün açıklaması, bir resim) alır ve onu, o verinin anlamsal özünü temsil eden yüzlerce veya binlerce sayıdan oluşan bir listeye, yani bir **vektöre** dönüştürür.

`"Kırmızı spor araba"` -> `[0.012, -0.456, 0.789, ..., -0.111]` (örneğin 1536 boyutlu bir vektör)

Bu sürecin asıl sihri, modelin bu vektörleri çok boyutlu bir "anlam uzayında" konumlandırmasıdır:

* `"Kırmızı spor araba"` vektörü ile `"Hızlı kırmızı otomobil"` vektörü, bu uzayda birbirine **çok yakın** noktalarda olacaktır.
* `"Mavi bisiklet"` vektörü biraz daha uzakta olacaktır.
* `"Lezzetli elma"` vektörü ise bambaşka bir bölgede, **çok uzakta** olacaktır.

Bu sayede, "anlam" artık soyut bir kavram olmaktan çıkıp, iki vektör arasındaki **matematiksel mesafe** ile ölçülebilir hale gelir. Birbirine yakın vektörler, birbirine yakın anlamlar demektir.

### 3. Sahne PostgreSQL'in: `pgvector` Nedir?

Geleneksel veritabanları bu uzun sayı dizilerini (vektörleri) nasıl saklayacaklarını veya arayacaklarını bilmezler. İşte `pgvector` burada devreye girer. `pgvector`, PostgreSQL'e üç temel yetenek kazandıran bir eklentidir:

1. **Yeni Veri Tipi (`vector`):** Vektörleri verimli bir şekilde saklamak için özel bir veri tipi ekler.
2. **Yeni Fonksiyonlar/Operatörler:** Vektörler arasındaki mesafeyi (benzerliği) hesaplamak için özel matematiksel operatörler sunar (`<=>`, `<->`, `<#>` gibi).
3. **Yeni Index Türleri (ANN):** Bu mesafe hesaplamalarını milyonlarca satır üzerinde ışık hızında yapabilmek için özel indexleme algoritmaları (HNSW, IVFFlat) ekler.

Kısacası, `pgvector` PostgreSQL'i, dünyanın en gelişmiş ilişkisel veritabanlarından biriyken, aynı zamanda yüksek performanslı bir **vektör veritabanına** dönüştürür.

### 4. Veri Akışı: Vektörler Nereden Geliyor?

Bu noktayı anlamak çok önemlidir: `pgvector` vektörleri **oluşturmaz**. Sadece onları saklar, yönetir ve arar. Vektörleri oluşturma süreci, sizin uygulamanızın sorumluluğundadır ve genellikle şöyle işler:

1. **Veri Oluşturma/Güncelleme Anı:** Uygulamanızda yeni bir ürün eklenir. Ürünün açıklaması: `"Yüksek kaliteli deriden yapılmış, kış ayları için ideal, su geçirmez bot."`
2. **Yapay Zeka Modeline Gönderme:** Uygulamanızın backend kodu, bu metni bir "Embedding API"ına gönderir. Bu API, OpenAI, Google (Gemini), Cohere veya Hugging Face'deki açık kaynaklı bir model olabilir.
3. **Vektörün Alınması:** API, size bu metnin anlamını temsil eden, önceden belirlediğiniz boyutta (örn: 1536) bir vektör `[0.789, 0.123, ...]` döndürür.
4. **Veritabanına Kaydetme:** Uygulamanız, ürünün diğer bilgileriyle (`urun_adi`, `fiyat` vb.) birlikte bu vektörü de PostgreSQL'deki `urunler` tablosunun `aciklama_vector` sütununa kaydeder.

Bu akış sayesinde, veritabanınızdaki her bir ürün açıklaması, artık anlamsal olarak aranabilir bir matematiksel kimliğe sahip olur.

Bu teorik temelleri attığımıza göre, bir sonraki bölümde kollarımızı sıvayıp `pgvector`'ı nasıl kuracağımızı, bu vektörleri kullanarak nasıl anlamsal sorgular yapacağımızı ve bu sorguları milyonlarca kayıt için nasıl optimize edeceğimizi pratik kod örnekleriyle göreceğiz.
