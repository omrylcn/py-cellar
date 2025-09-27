## Chapter 10: Perde Arkası: PostgreSQL'de `EXPLAIN` ile Sorgu Optimizasyonunun Sırları

Veritabanımıza bir sorgu gönderdiğimizde, o basit SQL metninin veriye dönüşmesi sihirli bir şekilde olmaz. Arka planda, **Sorgu Planlayıcısı (Query Planner)** adında son derece sofistike bir program çalışır. Bu planlayıcının görevi, istediğiniz veriyi getirmenin olası onlarca, hatta yüzlerce farklı yolunu analiz etmek ve istatistiklere dayanarak en düşük maliyetli, en verimli yolu seçmektir.

`EXPLAIN` komutu, planlayıcının bu kararını bize anlattığı bir rapordur. Bize der ki: "İstediğin veriyi getirmek için izlemeyi düşündüğüm adımlar bunlardır." Bir sorgunun neden yavaş olduğunu anlamanın ve onu nasıl hızlandıracağımızı bulmanın yolu, bu planı okuyup yorumlamaktan geçer.

### 1\. `EXPLAIN` vs. `EXPLAIN (ANALYZE)` - Tahmin vs. Gerçeklik

`EXPLAIN`'i kullanmanın iki temel yolu vardır ve aralarındaki fark hayati önem taşır.

#### `EXPLAIN`: Planı Göster

Bu komut, sorguyu **çalıştırmadan**, sadece planlayıcının o anki istatistiklere göre nasıl bir yol izleyeceğini **tahmin ettiği** planı gösterir. Çok hızlıdır ve sisteme yük bindirmez. Bir sorgu hakkında hızlı bir fikir edinmek için harikadır.

```sql
EXPLAIN SELECT * FROM kullanicilar WHERE email = 'test@example.com';
```

#### `EXPLAIN (ANALYZE)`: Çalıştır ve Planı Göster

Bu, optimizasyon için kullanılan altın standarttır. Bu komut, sorguyu **gerçekten çalıştırır**, ardından hem planlayıcının tahminlerini hem de her bir adımın **gerçekte ne kadar sürdüğünü**, ne kadar bellek kullandığını ve kaç satır döndürdüğünü gösteren detaylı bir rapor sunar.

```sql
-- ANALYZE: Gerçek çalışma zamanlarını ve satır sayılarını ekler.
-- BUFFERS: Hangi verinin ne kadarının bellekten (cache), ne kadarının diskten okunduğunu gösterir.
EXPLAIN (ANALYZE, BUFFERS)
SELECT u.kullanici_adi, COUNT(s.id)
FROM kullanicilar u
LEFT JOIN siparisler s ON u.id = s.musteri_id
WHERE u.aktif = TRUE
GROUP BY u.kullanici_adi;
```

> **⚠️ Uyarı:** `EXPLAIN (ANALYZE)`, sorguyu gerçekten çalıştırdığı için, yavaş bir `UPDATE` veya `DELETE` sorgusunu analiz ediyorsanız, bu işlemlerin gerçekten yapılacağını unutmayın\!

### 2\. Bir `EXPLAIN` Planı Nasıl Okunur?

`EXPLAIN ANALYZE` çıktısı ilk bakışta karmaşık görünebilir, ama temel metrikleri anladığınızda çok anlamlı hale gelir.

**Altın Kural:** Planlar **içten dışa** ve **aşağıdan yukarıya** doğru okunur. En çok girintiye sahip olan işlem, ilk olarak çalışır.

**Önemli Metrikler:**

* `cost=1.23..45.67`: Planlayıcının tahmini maliyeti. İlk rakam ilk satırı getirme maliyeti, ikinci rakam tüm satırları getirme maliyetidir. **Bu değer milisaniye DEĞİLDİR**, sadece planlayıcının farklı planları karşılaştırmak için kullandığı keyfi bir birimdir.
* `rows=123`: Planlayıcının bu adımdan döneceğini **tahmin ettiği** satır sayısı.
* `actual time=0.123..0.456`: `(ANALYZE)` ile gelir. Bir işlemin **gerçekte** ne kadar sürdüğünü milisaniye cinsinden gösterir. Performans darboğazını bulacağınız yer burasıdır.
* `rows=100`: `(ANALYZE)` ile gelir. Bu adımdan **gerçekte** dönen satır sayısı.
    > **💡 Pro-Tavsiye:** Eğer tahmin edilen `rows` ile gerçek `rows` arasında dağlar kadar fark varsa (örn: `rows=1` ama `actual rows=50000`), bu, planlayıcının istatistiklerinin güncel olmadığının en büyük işaretidir. Çözüm: `ANALYZE tablo_adi;` komutunu çalıştırmaktır.
* `Buffers: shared hit=10 read=2`: `(BUFFERS)` ile gelir. Verinin ne kadarının PostgreSQL'in belleğinden/cache'inden (`hit`) hızlıca, ne kadarının ise yavaş olan diskten (`read`) okunduğunu gösterir. Yüksek `read` sayıları, sunucunuzun daha fazla RAM'e ihtiyacı olduğuna veya sık erişilen verilerin belleğe sığmadığına işaret edebilir.

### 3\. Sık Karşılaşılan Operasyonlar

Planınızda en sık göreceğiniz temel veri erişim ve birleştirme yöntemleri şunlardır:

* **`Seq Scan` (Sequential Scan):** Kitabın tamamını baştan sona okumak. Küçük tablolarda normaldir. Milyonlarca satırlık büyük bir tabloda bir `Seq Scan` görüyorsanız ve sorgunuz seçiciyse (az sayıda satır döndürmeyi hedefliyorsa), bu genellikle bir index eksikliğine veya index'in kullanılamamasına işaret eden **kırmızı bir bayraktır**.
* **`Index Scan`:** En yaygın index kullanımı. Planlayıcı, index'i kullanarak aradığı satırların adreslerini bulur ve sonra asıl tabloya giderek o satırları okur. Genellikle görmek istediğimiz budur.
* **`Index Only Scan`:** En hızlısı. Sorgunun ihtiyaç duyduğu tüm veriler index'in kendisinde (`Covering Index` sayesinde) bulunduğu için, planlayıcının asıl tabloya gitmesine gerek kalmaz.
* **Join Türleri (`Nested Loop`, `Hash Join`, `Merge Join`):** Planlayıcının tabloları birleştirmek için seçtiği farklı algoritmalardır. `EXPLAIN` planında bu join'lerin maliyetlerine bakarak, join performansını nerenin yavaşlattığını anlayabilirsiniz.

### 4\. Sorgu Optimizasyon İpuçları: Plana Bakarak Harekete Geçmek

`EXPLAIN` planını okudunuz ve bir `Seq Scan` veya yüksek maliyetli bir operasyon gördünüz. Ne yapmalısınız?

* **`WHERE` Koşullarınız Index Dostu mu?**
  * **Problem:** `WHERE YEAR(kayit_tarihi) = 2025` gibi bir sorgu, `kayit_tarihi` sütunundaki normal bir B-Tree index'ini kullanamaz. Çünkü index, ham `timestamp` değerlerini tutar, `YEAR()` fonksiyonunun sonucunu değil. `EXPLAIN` çıktısında `Seq Scan` görürsünüz.
  * **Çözüm 1 (Sorguyu Değiştir):** Sorguyu `WHERE kayit_tarihi >= '2025-01-01' AND kayit_tarihi < '2026-01-01'` şeklinde yeniden yazarak index'in kullanılabilir hale gelmesini sağlayın.
  * **Çözüm 2 (Expression Index):** `CREATE INDEX ON siparisler (YEAR(kayit_tarihi));` şeklinde bir ifade index'i oluşturun (Bkz. Chapter 7).
* **`JOIN` Performansı İçin Index'ler Yerinde mi?**
  * **Problem:** `JOIN siparisler s ON u.id = s.musteri_id` gibi bir join işleminde, eğer `siparisler.musteri_id` sütununda bir index yoksa, PostgreSQL her bir kullanıcı için tüm `siparisler` tablosunu taramak zorunda kalabilir. Bu çok yavaştır.
  * **Çözüm:** `FOREIGN KEY` olarak kullanılan tüm sütunlarda bir B-Tree index'i olduğundan emin olun.
* **`ORDER BY` Yavaş mı?**
  * **Problem:** Planınızda yüksek maliyetli bir `Sort` işlemi görüyorsanız, bu, veriyi sıralamanın sorguyu yavaşlattığı anlamına gelir.
  * **Çözüm:** `ORDER BY` ifadesinde kullandığınız sütun(lar) için bir index oluşturun. `ORDER BY kayit_tarihi DESC` kullanıyorsanız, `CREATE INDEX ... (kayit_tarihi DESC);` şeklinde, sıralama yönüyle uyumlu bir index oluşturmak en iyi sonucu verir.

### Serinin "Part 1" Özeti ve Gelecek Adımlar

Bu dokuz bölümlük yolculuğun sonuna geldik. Birlikte, PostgreSQL'de veri dünyasının temellerinden başlayarak uzman seviyesi optimizasyon tekniklerine kadar uzanan bir serüven yaşadık:

1. **Temelleri** atıp PostgreSQL'i kurduk.
2. **Veri Türleri** ile verimizin DNA'sını belirledik.
3. **Tablolar ve ID'ler** ile verimize sağlam bir ev inşa ettik.
4. **Kısıtlamalar** ile bu evin kurallarını koyduk.
5. **Normalizasyon** ile veri şehrimizin planını çizerek kaosu önledik.
6. **Temel Index'ler** ile şehrimize verimli bir ulaşım ağı kurduk.
7. **İleri Index Teknikleri** ile bu ağa özel, cerrahi çözümler ekledik.
8. **İzleme ve Bakım** ile şehrimizin sağlığını ve performansını güvence altına aldık.
9. Ve son olarak **`EXPLAIN`** ile şehrin trafik akışını izleyip darboğazları nasıl çözeceğimizi öğrendik.

