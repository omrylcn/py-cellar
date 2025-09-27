## Chapter 6: Veritabanında Işık Hızına Ulaşmak: PostgreSQL'de Temel Index Türleri Rehberi

Önceki bölümlerde verilerimiz için mükemmel bir yapı tasarladık. Tablolarımız normalleştirildi, ilişkilerimiz tutarlı. Ama milyonlarca satır veriye ulaştığımızda, en basit sorgu bile dakikalar sürebilir. Veritabanımız ne kadar iyi tasarlanmış olursa olsun, **index'ler olmadan yavaştır.**

Bir veritabanını index olmadan kullanmak, 1000 sayfalık bir kitabın içindekiler veya fihrist bölümü olmadan belirli bir konuyu bulmaya çalışmaya benzer. Tek çareniz, ilk sayfadan başlayıp son sayfaya kadar her şeyi tek tek okumaktır. İşte bu yavaş ve verimsiz işleme PostgreSQL'de **"Sequential Scan" (Sıralı Tarama)** denir.

Index ise, o kitabın sonundaki fihrist gibidir. Hangi bilginin, tablonun hangi fiziksel adresinde olduğunu tutan özel bir veri yapısıdır. Bir sorgu geldiğinde, PostgreSQL tüm tabloyu taramak yerine bu fihriste bakar ve aradığı veriye doğrudan, ışık hızında ulaşır.

> **⚠️ Altın Kural ve Ödünleşim (Trade-off):** Index'ler `SELECT` (okuma) sorgularını müthiş hızlandırır. Ancak bir bedeli vardır:
>
> 1. **Depolama Alanı:** Her index, diskte ek yer kaplar.
> 2. **Yazma Performansı:** `INSERT`, `UPDATE`, `DELETE` (yazma) işlemleri bir miktar yavaşlar. Çünkü PostgreSQL, sadece tablodaki veriyi değil, o veriye işaret eden tüm index'leri de güncellemek zorundadır.
>
> Bu yüzden amaç, her sütuna index atmak değil, **sadece sıkça sorgulanan, filtrelenen (`WHERE`), birleştirilen (`JOIN`) ve sıralanan (`ORDER BY`) sütunlara** stratejik olarak index eklemektir.

Gelin, PostgreSQL'in bize sunduğu temel index türlerini ve onların süper güçlerini keşfedelim.

### 1\. B-Tree Index - Her İşin Ustası (Varsayılan ve En Yaygın)

PostgreSQL'de (ve diğer birçok ilişkisel veritabanında) varsayılan, en çok kullanılan ve en çok yönlü index türüdür. Sadece `CREATE INDEX ...` yazdığınızda, arka planda bir B-Tree index'i oluşturulur.

* **Nasıl Çalışır?** Veriyi sıralı bir ağaç yapısında tutar. Bu sayede sadece eşitlik (`=`) için değil, aynı zamanda tüm aralık sorguları (`<`, `>`, `<=`, `>=`, `BETWEEN`), `IN` listeleri ve önek `LIKE` sorguları (`'kelime%'` gibi) için de son derece verimlidir.
* **Ne Zaman Kullanılır?** Neredeyse her zaman\! `PRIMARY KEY` ve `UNIQUE` kısıtlamaları otomatik olarak arkada bir B-Tree index'i oluşturur. Bunun dışında, uygulamanızda sıkça kullandığınız hemen hemen tüm filtreleme ve sıralama sütunları için ilk tercihiniz B-Tree olmalıdır.

**a) Tek Sütunlu Index:**

Kullanıcıları e-posta adreslerine göre hızlıca bulmak için idealdir.

```sql
-- WHERE email = '...' sorgularını hızlandırır.
CREATE INDEX idx_kullanicilar_email ON kullanicilar(email);
```

**b) Bileşik Index (Composite Index):**

Sorgularınız genellikle birden fazla sütunu birlikte filtreliyorsa, bu sütunlar için tek bir bileşik index oluşturmak çok daha verimlidir.

```sql
-- WHERE musteri_id = ? AND siparis_tarihi > ? sorgularını hızlandırır.
CREATE INDEX idx_siparisler_musteri_tarih ON siparisler(musteri_id, siparis_tarihi);
```

> **💡 Pro-Tavsiye (Sütun Sırası Önemlidir\!):** Bileşik index'lerde sütunların sırası hayati önem taşır. `(musteri_id, siparis_tarihi)` sırasıyla oluşturulmuş bir index, sadece `musteri_id`'ye göre yapılan sorguları da hızlandırabilir. Ancak, sadece `siparis_tarihi`'ne göre yapılan sorgularda **kullanılamaz**. Genel kural, sorgularınızda en çok ayrım yapan (en seçici olan) sütunu veya eşitlik (`=`) ile sorguladığınız sütunu başa koymaktır.

### 2\. Hash Index - Sadece Eşitlik İçin Jet Hızı

* **Nasıl Çalışır?** Sütun değerinin bir "hash"ini çıkarır ve bu hash'i bir arama tablosunda saklar.
* **Ne Zaman Kullanılır?** Sadece ve sadece eşitlik (`=`) sorguları yaptığınız ve çok büyük tablolarda B-Tree'ye göre marjinal bir hız kazanımı aradığınızda.
* **Dezavantajları:** Aralık (`> <`) veya sıralama (`ORDER BY`) sorgularında kullanılamaz. PostgreSQL'in modern versiyonlarında B-Tree o kadar verimlidir ki, Hash index'e olan ihtiyaç neredeyse kalmamıştır. Genellikle B-Tree daha güvenli ve çok yönlü bir seçimdir.

<!-- end list -->

```sql
CREATE INDEX idx_urunler_stok_kodu_hash ON urunler USING HASH (stok_kodu);
```

### 3\. PostgreSQL'in Süper Güçleri: Özel Index Türleri

PostgreSQL'i gerçekten özel kılan şey, standart B-Tree'nin ötesinde, belirli veri tipleri ve sorgu desenleri için tasarlanmış inanılmaz güçlü index türleri sunmasıdır.

#### GIN (Generalized Inverted Index) - İçini Arayan Index

GIN, bir sütunun içinde birden çok değer barındıran "bileşik" veri türlerini indexlemek için tasarlanmıştır. Kitap fihristi gibi çalışır: her bir "kelimeyi" (elemanı) ve o kelimenin geçtiği tüm "sayfaları" (satırları) listeler.

* **Ne Zaman Kullanılır?**
  * **Diziler (Arrays):** `etiketler TEXT[]` sütununda 'postgresql' etiketine sahip tüm blog yazılarını bulmak.
  * **JSONB:** `meta_veri JSONB` sütununda `{"renk": "kırmızı"}` anahtar/değer çiftini içeren tüm ürünleri bulmak. Bu, PostgreSQL'in en güçlü özelliklerinden biridir\!
  * **Full-Text Search:** Kullanıcıların metin içinde arama yapmasını sağlamak için.

<!-- end list -->

```sql
-- Dizideki bir elemanı bulmak için:
CREATE INDEX idx_blog_yazilari_etiketler_gin ON blog_yazilari USING GIN (etiketler);

-- JSONB içindeki bir anahtarı veya değeri bulmak için:
CREATE INDEX idx_urunler_meta_veri_gin ON urunler USING GIN (meta_veri);

-- Full-text search için (to_tsvector metni aranabilir kelimelere böler)
CREATE INDEX idx_makaleler_icerik_gin ON makaleler USING GIN (to_tsvector('turkish', icerik));
```

#### GiST (Generalized Search Tree) - Şekillerin ve Aralıkların Index'i

GiST, B-Tree'nin sıralı mantığının yetersiz kaldığı karmaşık veri türleri için tasarlanmıştır. "Kesişiyor mu?", "İçeriyor mu?", "Yakınında mı?" gibi soruları verimli bir şekilde cevaplar.

* **Ne Zaman Kullanılır?**
  * **Geometrik Veriler (PostGIS eklentisi ile):** Harita üzerinde belirli bir alanın içindeki tüm restoranları bulmak.
  * **Aralık Türleri (Range Types):** Belirli bir tarih aralığıyla çakışan tüm otel rezervasyonlarını bulmak.

<!-- end list -->

```sql
-- PostGIS ile coğrafi sorguları hızlandırmak için:
CREATE INDEX idx_mekanlar_konum_gist ON mekanlar USING GIST (koordinatlar);

-- Tarih aralıklarının kesişimini bulmak için:
CREATE INDEX idx_etkinlikler_tarih_araligi_gist ON etkinlikler USING GIST (tarih_araligi);
```

#### BRIN (Block Range Index) - Dev Tablolar İçin Hafif Çözüm

* **Nasıl Çalışır?** B-Tree gibi her satırı tek tek indexlemek yerine, disk üzerindeki büyük veri blokları (binlerce satır olabilir) için sadece minimum ve maksimum değerleri saklar.
* **Ne Zaman Kullanılır?** Milyarlarca satırlık çok büyük tablolarda, ve verinin fiziksel olarak sıralanma şekli ile indexlenen sütunun arasında doğal bir ilişki (korelasyon) olduğunda. En klasik örnek, sürekli sonuna yeni kayıt eklenen `loglar` tablosunun `created_at` zaman damgası sütunudur.
* **Avantajı:** B-Tree'ye göre **çok çok daha az** yer kaplar ve bakımı daha hızlıdır.

<!-- end list -->

```sql
-- Milyarlarca satırlık log tablosunun created_at sütununu indexlemek için:
CREATE INDEX idx_loglar_created_brin ON loglar USING BRIN (created_at);
```

### Sonuç

Doğru index'i seçmek, veritabanı performans optimizasyonunun temelidir.

* Her işiniz için güvenilir yardımcınız **B-Tree**'dir.
* Dizi, JSONB veya metin içi arama yapıyorsanız, süper gücünüz **GIN**'dir.
* Coğrafi veya aralık verileriyle çalışıyorsanız, **GiST** size yardımcı olacaktır.
* Milyarlarca sıralı veriniz varsa, **BRIN** ile yerden tasarruf edebilirsiniz.
