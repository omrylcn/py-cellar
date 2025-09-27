# PostgreSQL: Mimar & Mühendis Rehberi

**Sıfırdan Üretim Ortamına: Modern PostgreSQL Mimarisi ve Optimizasyonu**

## Bu Rehber Nedir ve Kimler İçindir?

Bu rehber, modern bir PostgreSQL veritabanını sıfırdan tasarlamak, inşa etmek ve optimize etmek için gereken tüm adımları kapsayan, bütüncül ve pratik bir yol haritasıdır. Sadece "nasıl" yapılacağını değil, aynı zamanda "neden" o şekilde yapılması gerektiğini de temelden anlatmayı hedefler.

**Hedef Kitle:**
- PostgreSQL'e yeni başlayan geliştiriciler
- SQL bilgisi olan ancak PostgreSQL'e geçiş yapan deneyimli geliştiriciler
- Veri odaklı uygulamalar tasarlayan backend geliştiricileri
- Veritabanı performansını iyileştirmek isteyen mühendisler

Amacımız, okuyucuyu basit bir "kullanıcı" olmaktan çıkarıp, veritabanının arkasındaki mekanikleri anlayan, performans sorunlarını teşhis edebilen ve veri büyümesini öngörerek ölçeklenebilir tasarımlar yapabilen bilinçli bir **"Mimar & Mühendis"** haline getirmektir.

## Neler Öğreneceksiniz?

Bu rehberi tamamladığınızda, aşağıdaki yetkinliklere sahip olacaksınız:

### Temel Beceriler
- **Veritabanı Temelleri:** ACID prensipleri, transaction'lar ve ilişkisel model
- **Veri Modelleme:** Doğru veri türü seçimi ve sağlam tablo tasarımı
- **İlişkisel Tasarım:** Normalizasyon ve constraint'lerle veri bütünlüğü
- **Temel Sorgulama:** Etkili CRUD işlemleri ve JOIN optimizasyonu

### Performans ve Optimizasyon
- **Index Stratejileri:** B-Tree'den ileri seviye index türlerine kadar
- **Sorgu Analizi:** EXPLAIN planlarını okuma ve performans sorunlarını tespit etme
- **Query Optimization:** Index dostu sorgular yazma ve JOIN optimizasyonu
- **Window Functions:** Gelişmiş veri analizi teknikleri

### Modern PostgreSQL Özellikleri
- **Esnek Veri Modelleme:** JSONB ile yarı-yapılandırılmış veriler
- **Zaman Serisi Verileri:** Partitioning ve TimescaleDB
- **Akıllı Arama:** Full-Text Search ve pgvector ile anlamsal arama
- **Yapay Zeka Entegrasyonu:** Vector embedding'ler ve modern AI uygulamaları

### Üretim Hazırlığı
- **Görünümler ve Raporlama:** MATERIALIZED VIEW ile performanslı raporlama
- **Veritabanı Bakımı:** İzleme, maintenance ve optimizasyon
- **Ölçeklendirme:** Büyük veri yönetimi ve partitioning stratejileri

## İçindekiler

### **🏗️ Temeller ve Tasarım (Chapter 1-6)**
*Sağlam veritabanı mimarisinin temelleri*

- **[Chapter 1](chapter-1_Başlangıç.md):** Veritabanı Dünyasına Giriş
- **[Chapter 2](chapter-2_Veri_Türleri.md):** Veri Türleri ve Doğru Seçimler
- **[Chapter 3](chapter-3_CREATE_TABLE.md):** Tablo Sanatı ve ID Yapıları
- **[Chapter 4](chapter-4_Constraints.md):** Constraints ile Veri Bütünlüğü
- **[Chapter 5](chapter-5_Normalizasyon.md):** Normalizasyon ve İlişki Tasarımı
- **[Chapter 6](chapter-6_CRUD.md):** Temel CRUD İşlemleri

### **⚡ Performans Optimizasyonu (Chapter 7-9)**
*Hız ve verimlilik için temel teknikler*

- **[Chapter 7](chapter-7_Temel_Index.md):** Temel Index Türleri
- **[Chapter 8](chapter-8_EXPLAIN_Komutu.md):** EXPLAIN ile Sorgu Analizi
- **[Chapter 9](chapter-9_Sorgu_Optimizasyonu.md):** Sorgu Optimizasyonunun Temelleri

### **🔬 Modern PostgreSQL Özellikleri (Chapter 10-12)**
*PostgreSQL'in güçlü ve modern yetenekleri*

- **[Chapter 10](chapter-10_JSONB.md):** JSONB ile Esnek Veri Modelleme
- **[Chapter 11](chapter-11_MATERIALIZED_VIEWS.md):** MATERIALIZED VIEWS ile Raporlama
- **[Chapter 12](chapter-12_Sağlık_Kontrolü.md):** Veritabanı Bakımı ve İzleme

### **🚀 İleri Seviye Konular (Chapter 13-15)**
*Uzman seviyesi teknikler ve optimizasyonlar*

- **[Chapter 13](chapter-13_Index_Türleri.md):** İleri Index Türleri
- **[Chapter 13](chapter-13_Partial_Index.md):** Partial ve Expression Index'ler
- **[Chapter 14](chapter-14_Window.md):** Window Functions ile Veri Analizi
- **[Chapter 15](chapter-15_EXPLAIN_Gelişmiş_Kullanım.md):** Gelişmiş EXPLAIN Analizi
- **[Chapter 15](chapter-15_Index_İzleme.md):** Index İzleme ve Optimizasyon

### **📊 Büyük Veri ve Zaman Serileri (Chapter 16-17)**
*Ölçeklendirme ve özel veri türleri*

- **[Chapter 16-1](chapter-16-1_Zaman_Verileri.md):** Partitioning ile Zaman Verileri
- **[Chapter 16-2](chapter-16-2_TimeScaleDB.md):** TimescaleDB ile Zaman Serisi Yönetimi
- **[Chapter 17](chapter-17_Full-Text_Arama.md):** Full-Text Search Derinlemesine

### **🤖 Yapay Zeka Entegrasyonu (Chapter 18)**
*PostgreSQL ile modern AI uygulamaları*

- **[Chapter 18-1](chapter-18-1_pgvector_Başlangıç.md):** pgvector'a Giriş
- **[Chapter 18-2](chapter-18-2_pgvector_Kullanım.md):** Anlamsal Sorgular ve Optimizasyon
- **[Chapter 18-3](chapter-18-3_pgvector_Stratejiler.md):** Üretim Ortamında pgvector
- **[Chapter 18-4](chapter-18-4_pgvector_Index.md):** pgvector Index Stratejileri

### **📚 Ek Kaynaklar**
- **[JSONB vs HStore](chapter-x-2_JSONB_HSTORE.md):** Tarihsel karşılaştırma ve migration

## Öğrenme Yolu Önerileri

### 🎯 Yeni Başlayanlar (3-4 hafta)
```
Hafta 1: Chapter 1-3 (Temeller)
Hafta 2: Chapter 4-6 (Tasarım ve CRUD)
Hafta 3: Chapter 7-9 (Performans temelleri)
Hafta 4: Chapter 10-12 (Modern özellikler)
```

### 🏃 Deneyimli Geliştiriciler (2 hafta)
```
Hafta 1: Chapter 7-12 (Performans ve modern özellikler)
Hafta 2: İhtiyaca göre Chapter 13-18 (İleri konular)
```

### 🎯 Spesifik İhtiyaçlar
- **Performans sorunları:** Chapter 7-9, 13, 15
- **Modern veri yapıları:** Chapter 10, 18
- **Büyük veri:** Chapter 16-17
- **AI uygulamaları:** Chapter 18
- **Raporlama:** Chapter 11, 14

## Gereksinimler

### Teknik Gereksinimler
- PostgreSQL 12+ (önerilen: 14+)
- psql komut satırı aracı
- Temel SQL bilgisi (SELECT, INSERT, UPDATE, DELETE)
- Komut satırı kullanım becerisi

### Kurulum
```bash
# Ubuntu/Debian
sudo apt update
sudo apt install postgresql postgresql-contrib

# macOS (Homebrew)
brew install postgresql

# Windows
# PostgreSQL'in resmi sitesinden installer indirin
```

### Eklentiler (İsteğe Bağlı)
```sql
-- TimescaleDB için
CREATE EXTENSION IF NOT EXISTS timescaledb;

-- pgvector için
CREATE EXTENSION IF NOT EXISTS vector;

-- Full-text search için (varsayılan olarak mevcut)
-- CREATE EXTENSION IF NOT EXISTS pg_trgm;
```

## Pratik Öğrenme

### Her Bölümde
- Kod örneklerini kendi ortamınızda çalıştırın
- "Pro-Tavsiye" kutularına özel dikkat edin
- Her bölüm sonunda küçük pratikler yapın

### Örnek Proje
Rehber boyunca bir e-ticaret veritabanı inşa edeceğiz:
- Kullanıcılar, ürünler, kategoriler
- Siparişler ve sipariş detayları
- İncelemeler ve puanlamalar
- Analitics ve raporlama

## Topluluk ve Katkı

### Katkıda Bulunma
- **Hata bildirimi:** Teknik hatalar için issue açın
- **İyileştirme önerileri:** Daha iyi açıklamalar önerebilirsiniz
- **Deneyim paylaşımı:** Gerçek projelerden örnekler


---
