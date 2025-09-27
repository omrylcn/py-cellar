## Chapter 12: PostgreSQL'in Beynine Yolculuk: İstatistikler ve Gelişmiş `EXPLAIN` Analizi

Önceki bölümlerde, `EXPLAIN` komutunun bize bir sorgunun nasıl çalışacağına dair yol haritası sunduğunu öğrendik. Bir plandaki `Seq Scan`'in genellikle kötü, `Index Scan`'in ise genellikle iyi olduğunu anladık.

Ama bu yolculukta daha derine inmemizi gerektiren sorularla karşılaşırız:

* *Neden* planlayıcı, bariz bir index varken `Seq Scan` yapmayı tercih etti?
* `EXPLAIN` çıktısında `rows=1` tahmini yaparken, sorgu neden `actual rows=50000` döndürdü ve bu yüzden yavaş çalıştı?
* Planda gördüğüm bu `Bitmap Heap Scan` de neyin nesi?

Bu bölümde, PostgreSQL'in beyni olan sorgu planlayıcısının zihnine gireceğiz. Kararlarını hangi bilgilere dayanarak verdiğini (**İstatistikler**) ve oluşturduğu daha karmaşık planların ne anlama geldiğini (**Gelişmiş `EXPLAIN`**) öğreneceğiz.

### 1\. Planlayıcının Gözleri: İstatistikler Nasıl Çalışır?

PostgreSQL sorgu planlayıcısı, falcı değildir. Hangi sorgu planının daha "ucuz" ve "hızlı" olacağına karar verirken, elindeki tek bir şeye güvenir: `ANALYZE` komutu tarafından toplanan istatistiklere. Eğer bu istatistikler yanlış veya eskiyse, planlayıcının vereceği karar da neredeyse kesin olarak yanlış olacaktır.

**`ANALYZE`'in Topladığı Gizli Bilgiler:**
`ANALYZE tablo_adi;` komutunu çalıştırdığınızda, PostgreSQL perde arkasında her bir sütun için şu gibi kritik bilgileri toplar ve `pg_statistic` kataloğunda saklar:

* **`most_common_vals` & `most_common_freqs`:** Bir sütundaki en sık tekrar eden değerler ve bunların yüzde kaç oranında göründüğü. Örneğin, `siparisler.durum` sütununda 'teslim edildi' değerinin %90 oranında geçtiğini bilebilir.
* **`histogram_bounds`:** Sık tekrar etmeyen değerlerin dağılımını gösteren bir nevi nüfus yoğunluğu haritası. Planlayıcının, `WHERE fiyat > 10000` gibi bir sorgunun tablonun yaklaşık yüzde kaçını döndüreceğini tahmin etmesini sağlar.
* **`n_distinct`:** Sütundaki tahmini benzersiz değer sayısı.
* **`correlation`:** Sütundaki verinin mantıksal sırası ile diskteki fiziksel sırası arasındaki ilişki. Değeri 1'e ne kadar yakınsa, planlayıcı bir index taramasının diskten sıralı okuma yapma ihtimalinin o kadar yüksek olduğunu düşünür ve maliyetini düşürür.

**İstatistikler Neden Yanlış Olur (ve Planlar Neden Kötüleşir)?**
En sık karşılaşılan sorun, `EXPLAIN (ANALYZE)` çıktısında, tahmin edilen satır sayısı (`rows=...`) ile gerçekte dönen satır sayısı (`actual rows=...`) arasında devasa bir fark olmasıdır. Bunun başlıca nedenleri:

1. **Eski İstatistikler:** Tabloya çok sayıda veri eklendi veya silindi ama `autovacuum` henüz `ANALYZE` çalıştırmadı.
2. **Yetersiz Örneklem:** `ANALYZE` varsayılan olarak tüm tabloyu okumaz, bir örneklem alır. Veri dağılımınız çok çarpıksa, bu örneklem yanıltıcı olabilir.

**Çözüm:** İstatistiklerin kalitesini artırmak için PostgreSQL'e daha fazla bilgi vermemiz gerekir.

```sql
-- PostgreSQL'in 'kullanici_tipi' sütunu için daha detaylı istatistik (daha çok 'bucket') tutmasını söyle
ALTER TABLE kullanicilar ALTER COLUMN kullanici_tipi SET STATISTICS 1000;

-- Şimdi güncel ve daha detaylı istatistikleri topla
ANALYZE kullanicilar;
```

### 2\. Gelişmiş `EXPLAIN` Operasyonlarını Deşifre Etmek

Bir sorgu planında `Seq Scan` ve `Index Scan`'den daha fazlasını göreceksiniz. İşte en yaygın olanlar:

#### a) `Bitmap Index Scan` + `Bitmap Heap Scan`

Bu ikiliyi her zaman birlikte görürsünüz ve genellikle çok verimli bir çalışma yöntemine işaret eder.

* **Analoji:** Bir araştırma için kütüphanedeki birden çok fihriste (index'e) bakıyorsunuz. Her fihristten bulduğunuz sayfa numaralarını bir kağıda (`bitmap`) not alıyorsunuz. Sonra, bu kağıttaki tüm sayfa numaralarını sıraya koyup, raflar arasında ileri geri gitmeden, kitapları tek bir geçişte (`Heap Scan`) topluyorsunuz.
* **Ne Zaman Görülür?**
  * Birden fazla index'in birleştirilmesi gerektiğinde (`WHERE kategori='A' OR stok_durumu=TRUE` gibi).
  * Bir index taramasının çok da seçici olmadığı, yani tablonun hatırı sayılır bir kısmını (%5-10 gibi) döndüreceği tahmin edildiğinde.
* **İyi mi Kötü mü?** Genellikle **iyidir**. Planlayıcının, veriye verimli bir şekilde erişmek için akıllı bir strateji kullandığını gösterir.

#### b) `Sort` (Sıralama)

* **Analoji:** Karışık bir deste oyun kartını sıraya dizmek. Zaman ve efor (bellek/disk) gerektirir.
* **Ne Zaman Görülür?** Sorgunuzda `ORDER BY`, `GROUP BY`, `DISTINCT` gibi sıralama gerektiren bir ifade olduğunda ve bu sıralamayı karşılayacak bir index olmadığında.
* **İyi mi Kötü mü?** Eğer `Sort` işlemi, `(actual rows=...)` değeri büyük olan bir grup veri üzerinde yapılıyorsa, bu genellikle sorgunuzdaki **en büyük performans katilidir.** `EXPLAIN (ANALYZE, BUFFERS)` çıktısında `Sort Method: external merge on disk` gibi bir ifade görüyorsanız, bu, verinin belleğe sığmadığı ve yavaş diskin kullanıldığı anlamına gelir ki bu bir felakettir.
* **Çözümü:** `ORDER BY` veya `GROUP BY` yaptığınız sütun(lar) için bir B-Tree index'i oluşturmak.

#### c) `Gather` / `Parallel ... Scan`

* **Analoji:** Büyük bir depoyu saymak için tek bir kişi göndermek yerine, üç kişilik bir ekip gönderip her birine farklı bir reyonu saydırmak ve sonra sonuçları birleştirmek.
* **Ne Zaman Görülür?** Planlayıcı, bir tablo taramasının veya başka bir operasyonun, işi birden fazla CPU çekirdeğine bölmeye değecek kadar büyük olduğuna karar verdiğinde.
* **İyi mi Kötü mü?** Genellikle **çok iyidir\!** Bu, PostgreSQL'in modern donanımınızdan tam olarak faydalandığını ve sorgunuzu paralelleştirerek hızlandırdığını gösterir.

### 3\. Pratik Vaka Analizi: Kötü Bir Planı İyileştirmek

**Problem:** `loglar` tablomuzda milyonlarca kayıt var ve aşağıdaki sorgu çok yavaş çalışıyor:
`SELECT * FROM loglar WHERE (payload->>'error_code')::int = 504;`

**Adım 1: `EXPLAIN ANALYZE`**
Çıktıda devasa bir maliyetle bir **`Parallel Seq Scan`** ve onun üzerinde bir **`Filter`** adımı görüyoruz. `(rows=10)` tahmini yaparken, gerçekte `(actual rows=85000)` döndüğünü fark ediyoruz.

**Adım 2: Teşhis**
Planlayıcı, `(payload->>'error_code')::int = 504` koşulunun ne kadar seçici olduğunu bilmiyor. `JSONB` içindeki bir ifadenin istatistiklerini varsayılan olarak tutmaz. Sadece 10 satır döneceğini varsaydığı için, index oluşturmaya veya kullanmaya değmeyeceğini düşünüp tüm tabloyu tarıyor.

**Adım 3: Çözüm - Planlayıcıyı "Eğitmek"**
Planlayıcıya, bu ifade hakkında özel olarak istatistik toplamasını söyleyebiliriz.

**a) Expression Index (Daha Önce Gördük):** Bu, hem istatistik toplar hem de sorguyu doğrudan hızlandırır.

```sql
CREATE INDEX idx_logs_error_code ON loglar (((payload->>'error_code')::int));
ANALYZE loglar;
```

Bu index'i oluşturduktan sonra `EXPLAIN` planı artık `Seq Scan` yerine hızlı bir `Index Scan` gösterecektir.

**b) Extended Statistics (Genişletilmiş İstatistikler):** Eğer bir index oluşturmak istemiyorsak ama sadece planlayıcının tahminini iyileştirerek başka planları (örn: daha iyi bir `JOIN` kararı) tetiklemesini istiyorsak:

```sql
CREATE STATISTICS s_logs_error_code ON ((payload->>'error_code')::int) FROM loglar;
ANALYZE loglar;
```

Bu komut, ifadenin sonuçları hakkında `n_distinct` gibi istatistikleri toplayarak planlayıcının satır sayısı tahminini çok daha isabetli hale getirir.

**Sonuç:** `EXPLAIN` sadece bir rapor değildir; sorgu planlayıcısıyla aranızdaki bir diyalogdur. Planın neden kötü olduğunu anlamak için tahmin (`rows`) ve gerçeklik (`actual rows`) arasındaki farklara odaklanın. Planlayıcıya eksik olan bilgiyi (genellikle bir index veya daha iyi istatistikler aracılığıyla) verdiğinizde, sizi neredeyse her zaman çok daha performanslı bir plana yönlendirecektir.
