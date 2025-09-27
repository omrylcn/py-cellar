## Chapter 7: PostgreSQL'de Index Ustalığı: Partial, Expression ve Covering Index Sırları

Önceki bölümde veritabanımızın fihristleri olan temel index türlerini öğrendik. B-Tree, GIN, GiST gibi araçlarla sorgularımızı nasıl hızlandıracağımızı gördük. Ancak bazen, bir sütunun tamamını indexlemek bir baltayla fındık kırmaya benzer: işe yarar ama gereksiz yere ağır ve hantaldır.

Gerçek ustalık, index'leri birer cerrah neşteri gibi kullanarak, sadece ihtiyaç duyulan veriye, en verimli ve en küçük index'lerle ulaşmaktır. Bu bölümde, size bu hassasiyeti kazandıracak, PostgreSQL'in en güçlü ve en pratik ileri düzey indexleme tekniklerini inceleyeceğiz.

### 1\. Partial Index (Kısmi Index) - Sadece İhtiyacın Olanı Indexle

**Konsept:** Bir index'in, tablonun tamamını değil, yalnızca sizin belirlediğiniz bir `WHERE` koşuluna uyan satırlarını içermesidir.

**Neden Kullanılır? (Faydaları):**

1. **Daha Küçük Index Boyutu:** Index sadece satırların bir alt kümesini içerdiği için diskte çok daha az yer kaplar.
2. **Daha Hızlı Yazma İşlemleri:** Bir satır eklendiğinde veya güncellendiğinde, eğer satır `WHERE` koşuluna uymuyorsa, index'in güncellenmesine gerek kalmaz. Bu, `INSERT`/`UPDATE` performansını artırır.
3. **Daha Hızlı Okuma İşlemleri:** Daha küçük bir index, PostgreSQL'in taraması için daha az veri demektir, bu da sorgu performansını iyileştirir.

**Klasik Kullanım Senaryoları:**

**a) Duruma Göre Filtreleme:** Sadece "aktif" olan kullanıcılar arasında arama yapmanız gerekiyor. Pasif kullanıcıları index'lemek gereksizdir.

```sql
-- WHERE aktif = TRUE koşuluna uyan sorguları müthiş hızlandırır.
-- Ve sadece aktif kullanıcılar için bir index tutar.
CREATE INDEX idx_kullanicilar_aktif_email ON kullanicilar (email)
WHERE aktif = TRUE;
```

**b) İşlenmemiş Kayıtlar:** Bir "iş kuyruğu" tablonuz var ve arkaplan scriptleriniz sürekli `status = 'bekliyor'` olan kayıtları arıyor. İşlenmiş veya hatalı kayıtları index'e dahil etmenin bir anlamı yok.

```sql
CREATE INDEX idx_jobs_bekleyen ON jobs (id)
WHERE status = 'bekliyor';
```

**c) Yakın Tarihli Veriler:** Bir e-ticaret sitesinin admin paneli genellikle son 30 günün siparişlerini gösterir. Tüm sipariş geçmişini index'lemek yerine, sadece bu "sıcak" veriyi index'leyebilirsiniz.

```sql
CREATE INDEX idx_siparisler_son_30_gun ON siparisler (created_at)
WHERE created_at >= NOW() - INTERVAL '30 days';
```

### 2\. Expression Index (İfade Index'i) - Sütunun Kendisini Değil, Sonucunu Indexle

**Konsept:** Bir index'i doğrudan bir sütun üzerine değil, o sütuna uygulanmış bir fonksiyonun veya ifadenin **sonucu** üzerine kurmaktır.

**Neden Kullanılır?** Sorgularınızın `WHERE` kısmında bir fonksiyon kullanıyorsanız (`LOWER(email) = ...` gibi), PostgreSQL normal bir index'i kullanamaz. Çünkü index, ham `email` verisini tutarken, siz fonksiyonun çıktısını arıyorsunuz. Expression index, bu sorunu mükemmel bir şekilde çözer.

**Klasik Kullanım Senaryoları:**

**a) Büyük/Küçük Harf Duyarsız Arama (En Yaygın Kullanım):**
Kullanıcıların e-posta adreslerini ararken büyük/küçük harf fark etmemesini istersiniz.

```sql
-- Bu index sayesinde, aşağıdaki WHERE koşulu index kullanabilir:
-- WHERE LOWER(email) = 'test@example.com'
CREATE INDEX idx_kullanicilar_email_lower ON kullanicilar (LOWER(email));
```

**b) JSONB İçindeki Alanları Indexleme:**
Bu, PostgreSQL'in en güçlü özelliklerinden biridir. `JSONB` sütununuzun içindeki belirli bir anahtarın değerine göre hızlı arama yapmanızı sağlar.

```sql
-- WHERE (ozellikler ->> 'marka') = 'Logitech' sorgusunu hızlandırır.
-- ->> operatörü değeri 'text' olarak döndürdüğü için standart B-Tree index kullanabiliriz.
CREATE INDEX idx_urunler_ozellikler_marka ON urunler ((ozellikler ->> 'marka'));
```

**c) Tarih Fonksiyonları Üzerine Indexleme:**
Kayıtları oluşturuldukları güne göre gruplayan raporlama sorgularını hızlandırmak için.

```sql
-- SELECT COUNT(*), DATE_TRUNC('day', created_at) ... GROUP BY 2 sorgusunu hızlandırır.
CREATE INDEX idx_loglar_gunluk_kayit ON loglar (DATE_TRUNC('day', created_at));
```

### 3\. Covering Index (`INCLUDE`) - Cevabı Fihristte Bulmak (PostgreSQL 11+)

**Konsept:** Bir index'in, arama anahtarının yanı sıra, sorgularda sıkça ihtiyaç duyulan ek "payload" sütunlarını da içermesidir. Amacı **"Index-Only Scan" (Sadece Index Taraması)** elde etmektir.

**Index-Only Scan Nedir?** Normalde PostgreSQL bir index'i kullandığında süreç şöyledir:

1. Index'te aranan değeri bul.
2. Bu değerin işaret ettiği satırın disk adresini al.
3. Asıl tabloya (heap) gidip `SELECT` listesindeki diğer sütunları (`ad`, `soyad` vs.) oradan oku.

Bu 3. adıma **"heap fetch"** denir ve bir maliyeti vardır. Eğer sorgunun ihtiyaç duyduğu **tüm** sütunlar index'in kendisinde mevcutsa, PostgreSQL 3. adımı atlar ve cevabı doğrudan index'ten verir. Bu, bir sorgunun çalışabileceği en hızlı yoldur.

**`INCLUDE` Nasıl Yardımcı Olur?**
`INCLUDE` anahtar kelimesi, bu ek "payload" sütunlarını index'in arama yapısını (ağaç yapısını) büyütmeden, sadece yaprak düğümlere eklemenizi sağlar. Bu, index'i daha verimli kılar.

```sql
-- Bu sorguyu düşünün:
-- SELECT toplam_tutar, durum FROM siparisler WHERE musteri_id = 123;

-- Bu sorgu için mükemmel bir "Covering Index":
CREATE INDEX idx_siparisler_musteri_covering ON siparisler (musteri_id)
INCLUDE (toplam_tutar, durum);
```

Bu index sayesinde PostgreSQL, `musteri_id=123` olan kayıtları bulduğunda, `toplam_tutar` ve `durum` bilgilerini de index'in içinden okuyabilir ve asıl tabloya hiç gitmek zorunda kalmaz.

### 4\. Production İçin Hayati Teknikler

Canlı ve yoğun çalışan sistemlerde index oluştururken ekstra dikkatli olmalıyız.

#### `CREATE INDEX CONCURRENTLY` - Kesintisiz Index Oluşturma

**Problem:** Normal bir `CREATE INDEX` komutu, işlem bitene kadar tablo üzerinde ağır bir kilit (`lock`) uygular. Bu, büyük bir tabloda dakikalar hatta saatler sürebilir ve bu süre boyunca tablonuza `INSERT`, `UPDATE`, `DELETE` işlemleri yapılamaz. Kısacası, **sisteminiz kesintiye uğrar.**

**Çözüm:** `CONCURRENTLY` anahtar kelimesi, PostgreSQL'in tabloyu kilitlemeden, arka planda index'i oluşturmasını sağlar. Bu süreçte uygulamanız normal şekilde çalışmaya devam eder.

**Bedeli Nedir?**

* Daha yavaş tamamlanır ve daha fazla sistem kaynağı (CPU/IO) kullanır.
* Bir `BEGIN...COMMIT` bloğu, yani transaction içinde çalıştırılamaz.
* Eğer işlem sırasında bir hata olursa, geride "invalid" (geçersiz) bir index kalır. Bu index'i manuel olarak `DROP INDEX CONCURRENTLY invalid_index_adi;` komutuyla silip tekrar denemeniz gerekir.

<!-- end list -->

```sql
-- Production'da Milyonlarca satırlık bir tabloya index eklemenin TEK GÜVENLİ YOLU:
CREATE INDEX CONCURRENTLY idx_buyuk_tablo_kolon ON buyuk_tablo (kolon);
```

#### Partial Unique Index - Koşullu Benzersizlik

`UNIQUE` ve `Partial` index'in güçlerini birleştiren zarif bir çözümdür.

**Konsept:** Bir benzersizlik kuralının, tablonun tamamına değil, sadece belirli bir koşulu sağlayan satırlarına uygulanmasıdır.

**Klasik Kullanım Senaryosu ("Soft Delete"):**
Kayıtları veritabanından silmek yerine `deleted_at` gibi bir sütunu `NULL`'dan bir zaman damgasına güncelliyorsunuz. **Aktif** (yani `deleted_at` sütunu `NULL` olan) kullanıcıların e-postaları benzersiz olmalı, ancak silinmiş kayıtlar için bu kural geçerli olmamalıdır.

```sql
-- Bu index, sadece deleted_at alanı NULL olan satırlar arasında
-- email'in benzersiz olmasını garanti eder.
CREATE UNIQUE INDEX idx_kullanicilar_aktif_benzersiz_email
ON kullanicilar (email)
WHERE deleted_at IS NULL;
```

### Sonuç

Bu ileri teknikler, index stratejinizi genel çözümlerden, uygulamanızın ihtiyaçlarına özel olarak tasarlanmış yüksek performanslı çözümlere dönüştürmenizi sağlar.

* Daha az veri indexlemek için: **Partial Index**
* Daha akıllı veri indexlemek için: **Expression Index**
* Daha az veri okumak için: **Covering Index**
* Kullanıcılarınızı daha az etkilemek için: **`CONCURRENTLY`**
