## Chapter 6-1: SQL'in Gizli Süper Gücü: `WINDOW` Fonksiyonları ile Veri Analizinde Ustalık

Şimdiye kadar verilerimizi tasarlamayı, saklamayı ve temel yollarla sorgulamayı öğrendik. `GROUP BY` kullanarak özet raporlar oluşturabiliyoruz: "Her kategorinin ortalama ürün fiyatı nedir?", "Hangi gün ne kadar satış yapıldı?" gibi.

Peki ya size şöyle bir soru sorsaydım:
**"Her bir kategorideki en pahalı ilk 3 ürünü listeleyin."**
veya
**"Her bir çalışanın maaşını, kendi departmanının ortalama maaşıyla yan yana gösterin."**

Bu soruları geleneksel `GROUP BY`, `JOIN` ve alt sorgularla (subquery) çözmek, genellikle karmaşık, okunması zor ve yavaş çalışan SQL'ler yazmayı gerektirir. İşte bu noktada, SQL'in en zarif ve güçlü özelliklerinden biri olan **`WINDOW` Fonksiyonları** devreye girer.

Bu bölümde, bu fonksiyonların ne olduğunu, `GROUP BY`'dan temel farkını ve veri analizi yeteneklerinizi nasıl bir üst lige taşıyacağını pratik örneklerle keşfedeceğiz.

### 1\. `GROUP BY`'dan Farkı Ne? Temel Konsept

`GROUP BY` ve `WINDOW` fonksiyonları arasındaki farkı anlamak, konunun temelini kavramaktır.

  * **`GROUP BY` (Grupla ve Daralt):** Satırları birleştirerek, her bir grup için **tek bir özet satır** oluşturur. Orijinal satırların detayını kaybedersiniz.
  * **`WINDOW` Fonksiyonu (Grupla ve Genişlet):** Her bir satır için, o satırın ilişkili olduğu bir "pencere" (window) üzerinden hesaplama yapar ve sonucu **orijinal satırın yanına yeni bir sütun olarak** ekler. Orijinal satır sayısı asla değişmez.

**Görsel Bir Karşılaştırma:**
`satislar` adında bir tablomuz olsun:

| urun | kategori | fiyat |
| :--- | :--- | :---: |
| Laptop | Elektronik | 30000 |
| Klavye | Elektronik | 1000 |
| Monitör | Elektronik | 4000 |
| Roman | Kitap | 100 |
| Ansiklopedi| Kitap | 400 |

**`GROUP BY` ile kategori ortalaması:**

```sql
SELECT kategori, AVG(fiyat) FROM satislar GROUP BY kategori;
```

| kategori | avg |
| :--- | :---: |
| Elektronik | 11666 |
| Kitap | 250 |
*Sonuç: 2 satır. Ürün detayı kayboldu.*

**`WINDOW` Fonksiyonu ile kategori ortalaması:**

```sql
SELECT
    urun,
    kategori,
    fiyat,
    AVG(fiyat) OVER (PARTITION BY kategori) AS kategori_ortalamasi
FROM satislar;
```

| urun | kategori | fiyat | kategori\_ortalamasi |
| :--- | :--- | :---: | :---: |
| Laptop | Elektronik | 30000 | 11666 |
| Klavye | Elektronik | 1000 | 11666 |
| Monitör | Elektronik | 4000 | 11666 |
| Roman | Kitap | 100 | 250 |
| Ansiklopedi| Kitap | 400 | 250 |
*Sonuç: 5 satır. Hem her ürünün kendi detayını hem de ait olduğu grubun özet bilgisini aynı anda görüyoruz\!*

### 2\. `OVER()` Penceresini Anlamak

Bir `WINDOW` fonksiyonunun tüm sihri, `OVER()` anahtar kelimesiyle tanımlanan "pencere"nin içindedir.

`... OVER (PARTITION BY ... ORDER BY ...)`

  * **`PARTITION BY bolum`:** Bu, pencerenin sınırlarını çizer. `GROUP BY` gibi çalışır ama satırları daraltmaz. Hesaplamanın hangi alt gruba göre yapılacağını söyler. Yukarıdaki örnekte `PARTITION BY kategori` dediğimizde, "Elektronik" ve "Kitap" için iki ayrı pencere oluşturuldu ve `AVG()` her pencere için ayrı ayrı hesaplandı.
  * **`ORDER BY sira`:** Pencere içindeki satırların hangi sıraya göre işleneceğini belirler. Bu, özellikle sıralama ve sıra tabanlı fonksiyonlar (`ROW_NUMBER`, `LAG` vb.) için hayati önem taşır.

### 3\. En Yaygın `WINDOW` Fonksiyonları ve Pratik Kullanımları

#### a) Sıralama (Ranking) Fonksiyonları

Bu fonksiyonlar, bir grup içindeki her bir satıra bir sıra numarası vermek için kullanılır.

  * `ROW_NUMBER()`: Her satıra benzersiz bir sıra numarası verir (1, 2, 3, 4...).
  * `RANK()`: Değerler aynıysa aynı sırayı verir, ama sonraki sırada boşluk bırakır (1, 2, 2, 4...).
  * `DENSE_RANK()`: `RANK()` gibidir ama boşluk bırakmaz (1, 2, 2, 3...).

**Problem:** Her kategorideki en pahalı ilk 2 ürünü bulalım.

```sql
WITH UrunSiralama AS (
    SELECT
        urun,
        kategori,
        fiyat,
        ROW_NUMBER() OVER (PARTITION BY kategori ORDER BY fiyat DESC) AS sira
    FROM satislar
)
SELECT
    urun,
    kategori,
    fiyat
FROM UrunSiralama
WHERE sira <= 2;
```

| urun | kategori | fiyat |
| :--- | :--- | :---: |
| Laptop | Elektronik | 30000 |
| Monitör | Elektronik | 4000 |
| Ansiklopedi| Kitap | 400 |
| Roman | Kitap | 100 |
*Bu, geleneksel SQL ile çözmesi çok zor olan bir problemi, `WINDOW` fonksiyonu ile ne kadar zarif çözdüğümüzün kanıtıdır.*

#### b) Değer Kaydırma (Offset) Fonksiyonları

Bu fonksiyonlar, mevcut satıra göre bir önceki veya bir sonraki satırın değerine erişmenizi sağlar.

  * `LAG(sutun, n)`: Mevcut satırdan `n` önceki satırın değerini getirir.
  * `LEAD(sutun, n)`: Mevcut satırdan `n` sonraki satırın değerini getirir.

**Problem:** Her ayın satışını, bir önceki ayın satışıyla yan yana göstererek aylık büyümeyi hesaplayalım.

```sql
WITH AylikSatislar AS (
    -- Her ayın toplam satışını hesapladığımızı varsayalım
    SELECT ay, toplam_satis FROM ...
)
SELECT
    ay,
    toplam_satis,
    LAG(toplam_satis, 1) OVER (ORDER BY ay) AS onceki_ay_satis
FROM AylikSatislar;
```

| ay | toplam\_satis | onceki\_ay\_satis |
| :--- | :---: | :---: |
| 2025-01 | 10000 | NULL |
| 2025-02 | 12000 | 10000 |
| 2025-03 | 11000 | 12000 |
*Artık uygulama katmanında döngülerle uğraşmadan, doğrudan SQL içinde aylık büyüme yüzdesini (`(toplam_satis - onceki_ay_satis) / onceki_ay_satis`) hesaplayabiliriz.*

#### c) Kümülatif Toplam (Running Total) Gibi Toplama İşlemleri

`SUM()`, `AVG()` gibi bildiğimiz toplama fonksiyonları da `WINDOW` fonksiyonu olarak kullanılabilir. `ORDER BY` ile birleştirildiğinde, "kümülatif" hesaplamalar yapmamızı sağlarlar.

**Problem:** Bir aydaki günlük satışların kümülatif toplamını (ayın başından o güne kadar olan toplam satış) gösterelim.

```sql
SELECT
    gun,
    gunluk_satis,
    SUM(gunluk_satis) OVER (ORDER BY gun) AS kumulatif_satis
FROM GunlukSatislar;
```

| gun | gunluk\_satis | kumulatif\_satis |
| :--- | :---: | :---: |
| 2025-09-01 | 500 | 500 |
| 2025-09-02 | 700 | 1200 |
| 2025-09-03 | 600 | 1800 |
*Burada `PARTITION BY ay` ekleyerek, her ay için kümülatif toplamın yeniden başlamasını sağlayabilirdik.*

### Sonuç: Neden `WINDOW` Fonksiyonları Oyun Değiştiricidir?

`WINDOW` fonksiyonları, karmaşık veri analizi mantığını, yavaş ve hataya açık uygulama kodu döngülerinden alıp, verinin bulunduğu yer olan veritabanının kendisine, yani en hızlı işleneceği yere taşır. Karmaşık alt sorguları ve self-join'leri ortadan kaldırarak daha temiz, daha okunaklı ve genellikle çok daha performanslı SQL sorguları yazmanızı sağlarlar.

Bu fonksiyonlara hakim olmak, verilerinizden daha derin ve daha anlamlı içgörüler elde etmenizin anahtarıdır.