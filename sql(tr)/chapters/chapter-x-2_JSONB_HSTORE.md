## HStore vs JSONB Karşılaştırması:

### HStore Özellikleri:
```sql
-- HStore örneği
CREATE EXTENSION hstore; -- Önce extension aktif edilmeli

CREATE TABLE products_old (
    id INTEGER,
    properties HSTORE
);

INSERT INTO products_old VALUES (
    1, 
    'brand=>Apple, color=>red, weight=>200'::hstore
);

-- Sadece string değerler
-- Nested yapı yok
-- Array yok
```

### Temel Farklar:

| Özellik | HStore | JSONB |
|---------|--------|-------|
| **Veri Yapısı** | Sadece flat key-value | Nested JSON objects/arrays |
| **Değer Türleri** | Sadece TEXT | String, Number, Boolean, null, Object, Array |
| **Syntax** | `'key=>value'` | `'{"key": "value"}'` |
| **Nested Support** | ❌ | ✅ |
| **Array Support** | ❌ | ✅ |
| **Performance** | Hafif, hızlı | Biraz daha ağır ama çok güçlü |
| **Index Desteği** | GIN | GIN + daha zengin |

### Pratik Fark Örnekleri:

```sql
-- HStore (eski, sınırlı)
'name=>John, age=>30, active=>true'::hstore

-- JSONB (modern, güçlü)
'{
  "name": "John",
  "age": 30,
  "active": true,
  "address": {
    "city": "Istanbul",
    "country": "Turkey"
  },
  "hobbies": ["reading", "coding"]
}'::jsonb
```

## Neden JSONB Tercih Edilmeli:

1. **Nested Yapılar:** HStore sadece tek seviyeli key-value, JSONB unlimited depth
2. **Veri Türleri:** HStore her şeyi string olarak saklar, JSONB native türleri destekler
3. **Standard Uyumluluk:** JSON evrensel standard, hstore PostgreSQL'e özgü
4. **Gelecek Geçerliliği:** Yeni özellikler JSONB'ye ekleniyor, hstore maintenance mode'da

## Migration Senaryosu:

Eğer eski bir projede hstore görürseniz:

```sql
-- Hstore'dan JSONB'ye migration
ALTER TABLE products_old 
ADD COLUMN properties_jsonb JSONB;

UPDATE products_old 
SET properties_jsonb = hstore_to_jsonb(properties);

-- Sonra eski sütunu kaldır
ALTER TABLE products_old DROP COLUMN properties;
```

**Sonuç:** HStore tarihsel bir araç. Modern projeler için JSONB çok daha güçlü ve esnek. Sadece çok basit key-value ihtiyaçlarınız varsa hstore'un hafif performansı cazip olabilir, ama genel tavsiye JSONB kullanmak.

