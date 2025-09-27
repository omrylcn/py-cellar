## Chapter 8: Veritabanınızın Sağlık Kontrolü: PostgreSQL'de Index İzleme ve Optimizasyon

Şimdiye kadar veritabanı şehrimize binalar (tablolar) inşa ettik, yollar (ilişkiler) yaptık ve bu yolları kısaltan metro hatları (index'ler) döşedik. Peki bu metro hatları verimli kullanılıyor mu? Bazı hatlar hiç kullanılmıyor mu? Vagonlar zamanla eskidi ve yavaşladı mı? İşte bu bölümde, veritabanımızın "ulaşım ağını" denetleyen bir şehir plancısı gibi davranacak, index'lerimizin performansını izleyecek ve onların bakımını yapacağız.

Index'ler "bir kere oluştur, sonra unut" tarzı yapılar değildir. Zamanla bazıları işlevini yitirir, bazıları "bloat" dediğimiz problemle şişerek yavaşlar. Proaktif izleme ve bakım, veritabanınızın uzun vadede performanslı kalmasının anahtarıdır.

### 1\. PostgreSQL'in Gözleri: İstatistik Görünümleri

PostgreSQL, arka planda sürekli olarak veritabanı aktivitesini izleyen ve bunu `pg_stat_*` ile başlayan bir dizi sistem "görünümünde" (view) sunan bir istatistik toplayıcısına sahiptir. Bizim için en değerli olanı `pg_stat_user_indexes`'tır.

> **⚠️ Önemli Not:** Bu istatistikler, PostgreSQL sunucusu en son yeniden başlatıldığından veya istatistikler manuel olarak sıfırlandığından beri biriken **kümülatif** verilerdir. Sunucuyu yeniden başlatırsanız, bu sayaçlar sıfırlanır. Bu yüzden, yorum yaparken sunucunun ne kadar süredir çalıştığını (uptime) göz önünde bulundurun.

### 2\. Hayaletleri Avlamak: Kullanılmayan Index'leri Bulmak

**Problem:** Bir index'in en kötü hali, "kullanılmayan" bir index olmasıdır. Kullanılmayan bir index, `SELECT` sorgularına **hiçbir fayda sağlamaz** ama ait olduğu tabloya yapılan her `INSERT`, `UPDATE` ve `DELETE` işlemine **ek bir maliyet bindirir**. Yani, sadece sistem kaynaklarını ve disk alanını boşa harcayan bir parazittir.

**Çözüm:** `pg_stat_user_indexes` görünümünü sorgulayarak hiç kullanılmamış veya çok az kullanılmış index'leri tespit edebiliriz.

```sql
-- Hiç kullanılmamış index'leri bulmak için
SELECT
    schemaname || '.' || relname AS tablo_adi,
    indexrelname AS index_adi,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_boyutu
FROM
    pg_stat_user_indexes
WHERE
    -- idx_scan: Bu index'in kaç defa tarandığını gösterir.
    -- Sıfır olması, hiç kullanılmadığı anlamına gelir.
    idx_scan = 0
    AND indexrelname NOT LIKE '%_pkey'; -- PRIMARY KEY index'lerini hariç tut
ORDER BY
    pg_relation_size(indexrelid) DESC;
```

**Neden Primary Key'leri Hariç Tutuyoruz?** Birincil anahtar index'leri, sorgularda doğrudan kullanılmasalar bile veri bütünlüğünü (`UNIQUE` + `NOT NULL`) sağlamak ve `FOREIGN KEY` ilişkileri için zorunludurlar. Bu yüzden onları asla silmemeliyiz.

**Ne Yapmalı?** Bu sorgunun çıktısındaki index'ler, silinmek için bir numaralı adaylardır. Silmeden önce, bu index'in sadece yılda bir kez çalışan çok kritik bir rapor için oluşturulmadığından emin olun. Emin olduktan sonra, production ortamında güvenle silmek için:

```sql
DROP INDEX CONCURRENTLY index_adi;
```

### 3\. Yükleri Tartmak: Index Boyutlarını Analiz Etmek

**Problem:** Index'ler ne kadar yer kaplıyor? Devasa boyutlara ulaşmış bir index, yavaş taramalara veya "bloat" sorununa işaret ediyor olabilir.

**Çözüm:** Hangi index'in ne kadar yer kapladığını görmek, optimizasyon çabalarınızı nereye odaklamanız gerektiği konusunda size yol gösterir.

```sql
-- Tüm index'leri boyutlarına göre büyükten küçüğe sırala
SELECT
    schemaname || '.' || relname AS tablo_adi,
    indexrelname AS index_adi,
    pg_size_pretty(pg_relation_size(indexrelid)) AS index_boyutu,
    idx_scan AS kullanilma_sayisi
FROM
    pg_stat_user_indexes
ORDER BY
    pg_relation_size(indexrelid) DESC
LIMIT 20; -- En büyük 20 index'i göster
```

**Ne Yapmalı?** Bu listenin tepesinde, çok az kullanılan (`idx_scan` değeri düşük) ama çok büyük boyutlu bir index varsa, bu bir problem işaretidir. Belki de bu index, daha verimli bir **Partial Index** ile değiştirilebilir.

### 4\. Bahar Temizliği: Index Bakımı ve `REINDEX`

**Problem: Index Bloat (Şişkinliği)**
PostgreSQL'in MVCC mimarisi nedeniyle, özellikle sık `UPDATE` ve `DELETE` gören tablolarda, index'ler zamanla "ölü" kayıtlarla dolabilir. Bu, index'in disk üzerinde olması gerekenden çok daha fazla yer kaplamasına ve dolayısıyla daha yavaş taranmasına neden olur. Bu duruma **"bloat"** denir.

**Çözüm: `REINDEX`**
`REINDEX` komutu, bir index'i tablodaki güncel verilere göre sıfırdan, temiz, kompakt ve şişkinlikten arındırılmış bir şekilde yeniden oluşturur.

**En İyi Pratik:** Standart `REINDEX` komutu, işlem bitene kadar tabloyu kilitler, bu da production ortamında kesinti anlamına gelir. Bu yüzden **her zaman** `CONCURRENTLY` seçeneğini kullanmalıyız.

```sql
-- Sadece tek bir şişmiş (bloated) index'i yeniden oluşturmak için:
REINDEX INDEX CONCURRENTLY bozuk_index_adi;

-- Bir tablodaki TÜM index'leri yeniden oluşturmak için:
REINDEX TABLE CONCURRENTLY cok_kullanilan_tablo_adi;
```

### 5\. Planlayıcıyı Beslemek: `ANALYZE`'in Hayati Rolü

**Problem:** PostgreSQL'in sorgu planlayıcısı, bir sorguyu çalıştırmanın en verimli yoluna (örneğin hangi index'i kullanacağına veya index kullanmak yerine tüm tabloyu mu tarayacağına) karar verirken elindeki istatistiklere güvenir. Eğer bu istatistikler eskiyse, planlayıcı çok kötü kararlar verebilir.

**Çözüm: `ANALYZE`**
`ANALYZE` komutu, bir tabloyu ve onun index'lerini tarayarak içindeki verinin dağılımı hakkında (en yaygın değerler, benzersiz değer sayısı, vb.) istatistikler toplar ve bunları sistem kataloglarına yazar.

**En İyi Pratik:** Normal şartlarda, PostgreSQL'in `autovacuum` süreci `ANALYZE` işlemini periyodik olarak otomatik çalıştırır. Ancak, bir tabloya çok büyük miktarda veri eklediyseniz, sildiyseniz veya güncellediyseniz, planlayıcının en güncel bilgilere sahip olduğundan emin olmak için manuel olarak `ANALYZE` çalıştırmak harika bir fikirdir.

```sql
-- 'urunler' tablosunun istatistiklerini manuel olarak güncelle
ANALYZE VERBOSE urunler;
```

### Sonuç: Bakım Döngüsü

Veritabanı index'lerinizin sağlığını korumak için periyodik olarak şu adımları izleyin:

1. **İzle:** `pg_stat_user_indexes` ile index kullanımını ve boyutlarını düzenli olarak kontrol edin.
2. **Temizle:** Kullanılmayan index'leri tespit edip güvenle sistemden kaldırın.
3. **Bakım Yap:** Özellikle `UPDATE`/`DELETE` yükü ağır tablolarda index şişkinliğini (bloat) kontrol edin ve `REINDEX CONCURRENTLY` ile bakım yapın.
4. **Bilgilendir:** Büyük veri değişikliklerinden sonra `ANALYZE` ile sorgu planlayıcısını bilgilendirin.
