# FastAPI WebSocket İletişiminin Adım Adım Çalışma Prensibi

Basit sunucu ve istemci kodumuzun her bir adımını ve çalışma prensibini detaylı olarak açıklayacağım.

## 1. Sunucu Tarafı (server.py)

### Kurulum ve Başlangıç Aşaması

```python
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

# Bağlı istemcileri takip etmek için basit liste
connected_clients = []
```

- **FastAPI ve WebSocket modüllerini import ediyoruz**: FastAPI web framework'ümüzü, WebSocket sınıfını da socket işlemleri için kullanacağız.
- **FastAPI uygulaması oluşturuyoruz**: `app = FastAPI()` ile uygulamamızı başlatıyoruz.
- **connected_clients listesi**: Bağlı tüm istemcileri takip etmek için basit bir liste oluşturuyoruz. Bu liste, aktif WebSocket bağlantılarını saklayacak.

### HTTP Endpoint

```python
@app.get("/")
async def root():
    return {"message": "WebSocket Sunucusu Çalışıyor", 
            "connected_clients": len(connected_clients)}
```

- Bu endpoint, normal bir HTTP GET isteğini karşılar ve sunucunun çalıştığını teyit eder.
- **connected_clients.length**: Kaç adet aktif bağlantı olduğunu bildirir.

### WebSocket Endpoint

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Bağlantıyı kabul et
    await websocket.accept()
    # Bağlantıyı listeye ekle
    connected_clients.append(websocket)
```

- **@app.websocket("/ws")**: Bu dekoratör, `/ws` URL'sine gelen WebSocket bağlantı isteklerini bu fonksiyona yönlendirir.
- **websocket parametresi**: FastAPI, bağlantı isteğini otomatik olarak bir `WebSocket` nesnesine dönüştürür.
- **await websocket.accept()**: WebSocket bağlantı isteğini kabul ediyoruz. Bu adım çok önemli - accept() çağrılmazsa bağlantı kurulmaz.
- **connected_clients.append(websocket)**: Kabul ettiğimiz bağlantıyı aktif bağlantılar listemize ekliyoruz.

### Ana İletişim Döngüsü

```python
try:
    while True:
        # İstemciden mesaj bekle
        data = await websocket.receive_text()
        print(f"Alınan mesaj: {data}")
        
        # İstemciye yanıt gönder
        await websocket.send_text(f"Mesajınız: {data}")
        
        # Diğer tüm istemcilere ilet
        for client in connected_clients:
            if client != websocket:  # Kendisi hariç
                await client.send_text(f"Başka bir istemciden: {data}")
```

- **try-except bloğu**: WebSocket bağlantısı sırasında oluşabilecek hataları yakalar.
- **while True döngüsü**: Bağlantı süresince sürekli olarak mesaj dinler.
- **await websocket.receive_text()**: Bu, istemciden mesaj gelene kadar bekler. Bu metot asenkrondur, yani mesaj gelene kadar başka işlemlere izin verir. İstemci mesaj gönderene kadar bu satırda bekler.
- **await websocket.send_text()**: İstemciye yanıt gönderir.
- **for client in connected_clients**: Bağlı diğer tüm istemcilere de bu mesajı iletir (yayın yapar).

### Bağlantı Sonlandırma

```python
except Exception as e:
    print(f"Hata: {e}")
finally:
    # Bağlantı kesildiğinde listeden çıkar
    if websocket in connected_clients:
        connected_clients.remove(websocket)
```

- **except bloğu**: Bağlantı kesilmesi veya hata durumunda çalışır.
- **finally bloğu**: Hata olsa da olmasa da çalışır, bağlantı kesildikten sonra temizlik yapar.
- **connected_clients.remove(websocket)**: Kapanan bağlantıyı aktif bağlantı listemizden çıkarırız.

### Sunucuyu Başlatma

```python
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

- **uvicorn.run()**: ASGI sunucusunu başlatır. "server:app" parametresi "server.py dosyasındaki app nesnesini çalıştır" anlamına gelir.
- **reload=True**: Kod değiştiğinde sunucuyu otomatik olarak yeniden başlatır (geliştirme için).

## 2. İstemci Tarafı (client.py)

### Kurulum ve HTML Tanımlama

```python
from fastapi import FastAPI, WebSocket
from fastapi.responses import HTMLResponse
import uvicorn
import websockets
import asyncio

app = FastAPI()

# HTML sayfa içeriği
html = """
<!DOCTYPE html>
...
"""
```

- **HTML içeriği**: Bir Web tarayıcısında kullanılacak basit bir WebSocket istemcisi için HTML sayfası tanımlıyoruz.

### HTML Endpoint

```python
@app.get("/")
async def get():
    return HTMLResponse(html)
```

- Bu endpoint, tanımladığımız HTML içeriğini döndürür.
- **HTMLResponse**: İçeriğin HTML olarak yorumlanmasını sağlar.

### API ile Mesaj Gönderme Endpoint'i

```python
@app.get("/send/{message}")
async def send_message(message: str):
    try:
        # Sunucuya WebSocket bağlantısı kur
        async with websockets.connect("ws://localhost:8000/ws") as websocket:
            # Mesaj gönder
            await websocket.send(message)
            # Yanıtı al
            response = await websocket.recv()
            return {"sent": message, "response": response}
    except Exception as e:
        return {"error": str(e)}
```

- **@app.get("/send/{message}")**: URL path'indeki mesaj parametresini alır.
- **websockets.connect()**: Sunucuya yeni bir WebSocket bağlantısı açar.
- **async with**: Bağlantının otomatik olarak kapatılmasını sağlar (context manager).
- **await websocket.send()**: Sunucuya mesaj gönderir.
- **await websocket.recv()**: Sunucudan yanıt bekler.

### İstemciyi Başlatma

```python
if __name__ == "__main__":
    uvicorn.run("client:app", host="0.0.0.0", port=8001, reload=True)
```

- İstemci uygulamasını 8001 portunda başlatır.

## 3. HTML/JavaScript WebSocket İstemcisi

```javascript
var ws = new WebSocket("ws://localhost:8000/ws");
ws.onmessage = function(event) {
    var messages = document.getElementById('messages');
    var message = document.createElement('li');
    var content = document.createTextNode(event.data);
    message.appendChild(content);
    messages.appendChild(message);
};
function sendMessage(event) {
    var input = document.getElementById("messageText");
    ws.send(input.value);
    input.value = '';
    event.preventDefault();
}
```

- **new WebSocket()**: JavaScript tarafında WebSocket bağlantısı oluşturur.
- **ws.onmessage**: Sunucudan mesaj geldiğinde çalışacak fonksiyon.
- **sendMessage()**: Form gönderildiğinde mesajı sunucuya ileten fonksiyon.

## 4. Adım Adım İletişim Süreci

### A. Bağlantı Kurma Aşaması

1. **İstemci:** Tarayıcı `ws://localhost:8000/ws` adresine WebSocket bağlantı isteği gönderir.
2. **Sunucu:** FastAPI bu isteği `websocket_endpoint` fonksiyonuna yönlendirir.
3. **Sunucu:** `await websocket.accept()` ile bağlantıyı kabul eder.
4. **Sunucu:** Aktif bağlantıyı `connected_clients` listesine ekler.
5. **İstemci:** Bağlantı kurulduğunda `ws.onopen` tetiklenir (kodumuzdaki HTML'de tanımlanmamış).

### B. Veri Alışverişi Aşaması

1. **İstemci:** Kullanıcı form aracılığıyla bir mesaj yazar ve gönderir.
2. **İstemci:** `ws.send(input.value)` ile mesaj WebSocket üzerinden sunucuya iletilir.
3. **Sunucu:** `await websocket.receive_text()` ile mesajı alır.
4. **Sunucu:** Mesajı konsola yazdırır.
5. **Sunucu:** `await websocket.send_text()` ile istemciye yanıt gönderir.
6. **Sunucu:** Diğer bağlı istemcilere de bu mesajı iletir.
7. **İstemci:** `ws.onmessage` tetiklenir ve gelen mesaj ekranda görüntülenir.

### C. Bağlantı Sonlandırma Aşaması

1. **İstemci:** Kullanıcı tarayıcı sayfasını kapatır veya ağ bağlantısı kesilir.
2. **Sunucu:** `websocket.receive_text()` beklerken WebSocketDisconnect istisnası oluşur.
3. **Sunucu:** Exception yakalanır ve finally bloğu çalışır.
4. **Sunucu:** Bağlantı, connected_clients listesinden çıkarılır.

## 5. Önemli Noktalar

### Bağlantı Süresi

- WebSocket bağlantıları, HTTP'nin aksine **kalıcıdır**. Bir kez kurulduktan sonra, taraflardan biri bağlantıyı kapatana kadar veya ağ kesintisi olana kadar açık kalır.
- Sunucu, `while True` döngüsüyle sürekli olarak istemciden mesaj bekler.
- Tarayıcı kapatılsa bile, sunucu tarafında bağlantının kapalı olduğu anlaşılana kadar kısa bir gecikme olabilir.

### Asenkron Yapı

- `await` anahtar kelimesi, WebSocket işlemlerinin asenkron olduğunu gösterir.
- Bu asenkron yapı sayesinde, tek bir thread'de binlerce eşzamanlı WebSocket bağlantısı yönetilebilir.
- Sunucu, bir istemciden mesaj beklerken diğer istemcilerden gelen mesajları da işleyebilir.

### Sürekli Bağlantının Avantajları

- HTTP'nin aksine, her yeni istek için bağlantı kurma ve sonlandırma maliyeti yoktur.
- Düşük gecikme süresi: Sunucu, istemciye anında (gerçek zamanlı) mesaj gönderebilir.
- İstemci, mesaj almak için sürekli sorgu (polling) yapmak zorunda değildir.

## 6. Özetleyecek Olursak

- WebSocket, HTTP üzerinden başlayan ancak sonrasında uzun süreli, çift yönlü bir iletişim kanalına dönüşen bir protokoldür.
- FastAPI, WebSocket desteğini yerleşik olarak sunar ve `websocket.accept()`, `websocket.receive_text()`, `websocket.send_text()` gibi metodlarla kolay kullanım sağlar.
- İstemci tarafında, tarayıcının WebSocket API'si veya `websockets` kütüphanesi kullanılabilir.
- Bağlantı kurulduğunda, bir "handshake" (el sıkışma) gerçekleşir ve sonrasında sürekli açık bir kanal oluşur.
- Mesajlar, bu açık kanal üzerinden her iki yönde de iletilir, yeni bağlantı kurmaya gerek kalmaz.
- Bağlantı koptuğunda veya kapatıldığında, temizlik işlemleri yapılır.

Bu basit ancak etkili model, sohbet uygulamaları, canlı bildirimleri, gerçek zamanlı veri akışları ve daha birçok etkileşimli uygulama için temel oluşturur.


# Part - 2

Harika sorular! WebSocket'lerin async/await yapısı ve akışını daha iyi anlamanıza yardımcı olacağım:

### `await websocket.accept()` Neden Var?

`await` anahtar kelimesi, asenkron bir işlemin tamamlanmasını beklemek için kullanılır. `websocket.accept()` metodu bir asenkron (coroutine) metottur.

**Eğer `await` olmasaydı:**
- Kod, `accept()` metodunun tamamlanmasını beklemeden hemen bir sonraki satıra geçerdi
- `accept()` işlemi bir "Coroutine" nesnesi döndürür, ancak gerçekte bağlantıyı kabul etme işlemi başlatılmazdı
- El sıkışma tamamlanmadan mesaj almaya çalışacaktık ki bu bir hatayla sonuçlanırdı

**Kodu nasıl değiştirirdi:**
```python
# Hatalı kod - await olmadan
websocket.accept()  # Bu sadece bir coroutine nesnesi döndürür ama çalıştırmaz
connected_clients.append(websocket)  # Bağlantı henüz kabul edilmemiş!

# Doğru kod
await websocket.accept()  # Bağlantı kabul edilene kadar bekler
connected_clients.append(websocket)  # Şimdi güvenle ekleyebiliriz
```

### Connected List ve Await İlişkisi

Evet, kesinlikle haklısınız! `await websocket.accept()` çağrısı tamamlanmadan listeye ekleme yapmıyoruz. Çünkü:

1. Önce bağlantının başarılı bir şekilde kurulduğundan emin olmak istiyoruz
2. `accept()` işlemi başarısız olabilir (örneğin ağ hatası nedeniyle)
3. Listeye sadece başarılı bağlantıları eklemek istiyoruz

Bu, asenkron programlamada "önce işlemi bekle, sonra sonucunu kullan" prensibinin bir örneğidir.

### `await websocket.receive_text()` Ne Demek?

Bu satır aslında asenkron programlamanın temel avantajını gösteriyor:

```python
data = await websocket.receive_text()
```

**"Başka işlemlere izin vermek" şu anlama gelir:**
- Bu bağlantı için mesaj bekliyorken, diğer bağlantılar da aynı zamanda mesaj alabilir/gönderebilir
- Bu noktada işlem "bloke olmaz" - yani Python, mesaj beklerken diğer bağlantılar için de aynı WebSocket endpoint fonksiyonunun farklı örneklerini çalıştırabilir
- Tek bir thread ile yüzlerce/binlerce bağlantıyı aynı anda yönetebilirsiniz

Bir benzetme yapmak gerekirse:
- Geleneksel (senkron) programlama: Bir müşterinin siparişini hazırlayana kadar diğer müşterileri bekletmek gibi
- Asenkron programlama: Bir siparişi hazırlarken, diğer müşterilerin de siparişlerini almak gibi

Bu "print" ile ilgisi yoktur - `await` noktasında, Python diğer bağlantılara hizmet vermek için bu fonksiyonun çalışmasını "duraklatır" ve mesaj geldiğinde tam olarak bıraktığı yerden devam eder.

### Bağlantıyı Nasıl Keserim?

**Sunucu tarafından bağlantıyı kesmek için:**
```python
await websocket.close(code=1000, reason="Normal closure")
```

**Kodlar ve nedenler:**
- 1000: Normal kapatma
- 1001: Uzak taraf kapandı
- 1002: Protokol hatası
- 1003: Kabul edilemez veri tipi
- 1008: Politika ihlali
- 1011: Sunucu hatası

**İstemci (JavaScript) tarafından bağlantıyı kesmek için:**
```javascript
ws.close(1000, "Normal closure");
```

Bağlantı kapatıldığında, sunucudaki `try-except-finally` bloğu çalışır ve `connected_clients` listesinden bağlantı kaldırılır.

### Sunucu Kendi Mesajını Göndermek İsterse?

Haklısınız, şu anda sunucu sadece gelen mesajlara yanıt veriyor. Sunucunun kendi inisiyatifiyle mesaj göndermesi için birkaç yaklaşım var:

1. **Zamanlayıcı ile periyodik mesaj gönderme:**
```python
async def send_periodic_updates():
    while True:
        message = f"Sunucu saati: {datetime.now().isoformat()}"
        for client in connected_clients:
            try:
                await client.send_text(message)
            except Exception:
                # Bağlantı kesilmiş olabilir, hata yönetimi
                pass
        await asyncio.sleep(60)  # 60 saniye bekle

# Uygulama başlangıcında bu görevi başlat
@app.on_event("startup")
async def startup_event():
    asyncio.create_task(send_periodic_updates())
```

2. **Harici bir olaya yanıt olarak mesaj gönderme:**
```python
# Örneğin başka bir HTTP endpoint aracılığıyla tüm bağlantılara mesaj gönderme
@app.post("/broadcast")
async def broadcast_to_all(message: str):
    for client in connected_clients:
        try:
            await client.send_text(message)
        except Exception:
            pass
    return {"status": "sent", "clients": len(connected_clients)}
```

WebSocket bağlantıları, kurulduktan sonra sunucunun herhangi bir zamanda mesaj göndermesine olanak tanır - bu gerçek zamanlı uygulamaların gücüdür. Sunucu, istemcinin bir istek yapmasını beklemeden herhangi bir zamanda mesaj gönderebilir.

# Part - 3
Haklısınız, tam olarak öyle! `await` ifadesi "ben burada duruyorum ve bekliyorum, ama diğer işlemlerin de çalışmasına izin veriyorum" anlamına gelir. İşte bunu daha iyi göstermek için sunucu kodumuza periyodik mesaj gönderen bir fonksiyon ekleyelim.

İşte nasıl yapacağımızı adım adım açıklayayım:

## 1. Rastgele Mesaj Gönderen Sunucu Kodu

```python
from fastapi import FastAPI, WebSocket
import uvicorn
import asyncio
import random
import datetime

app = FastAPI()

# Bağlı istemcileri takip etmek için basit liste
connected_clients = []

# Rastgele mesajlar listesi
random_messages = [
    "Sunucudan otomatik mesaj: Merhaba!",
    "Sunucudan bilgi: Sistem çalışıyor.",
    "Sunucudan uyarı: Bakım zamanı yaklaşıyor.",
    "Sunucudan duyuru: Yeni özellikler eklendi!",
    "Sunucudan bildirim: Şu an aktif kullanıcı sayısı artıyor."
]

# Periyodik olarak rastgele mesaj gönderen fonksiyon
async def send_random_messages():
    while True:
        if connected_clients:  # Bağlı istemci varsa
            # Rastgele bir mesaj seç
            message = random.choice(random_messages)
            # Zaman bilgisi ekle
            timed_message = f"{message} [{datetime.datetime.now().strftime('%H:%M:%S')}]"
            
            print(f"Rastgele mesaj gönderiliyor: {timed_message}")
            
            # Tüm bağlı istemcilere gönder
            for client in connected_clients:
                try:
                    await client.send_text(f"SUNUCU: {timed_message}")
                except Exception as e:
                    print(f"Mesaj gönderme hatası: {e}")
        
        # 5 saniye bekle
        await asyncio.sleep(5)

@app.get("/")
async def root():
    return {"message": "WebSocket Sunucusu Çalışıyor", 
            "connected_clients": len(connected_clients)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # Bağlantıyı kabul et
    await websocket.accept()
    print("Yeni istemci bağlandı!")
    
    # Bağlantıyı listeye ekle
    connected_clients.append(websocket)
    
    try:
        while True:
            # İstemciden mesaj bekle
            print("İstemciden mesaj bekleniyor...")
            data = await websocket.receive_text()
            print(f"Alınan mesaj: {data}")
            
            # İstemciye yanıt gönder
            await websocket.send_text(f"Mesajınız: {data}")
            
            # Diğer tüm istemcilere ilet
            for client in connected_clients:
                if client != websocket:  # Kendisi hariç
                    await client.send_text(f"Başka bir istemciden: {data}")
    
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        # Bağlantı kesildiğinde listeden çıkar
        if websocket in connected_clients:
            connected_clients.remove(websocket)
            print("İstemci bağlantısı kesildi")

# Uygulama başladığında periyodik mesaj gönderme görevini başlat
@app.on_event("startup")
async def startup():
    # Arka planda çalışacak bir görev olarak başlat
    asyncio.create_task(send_random_messages())
    print("Periyodik mesaj gönderme görevi başlatıldı")

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

## Bu Kodun Nasıl Çalıştığını Adım Adım Açıklayalım:

1. **Periyodik Mesaj Görevi Başlatma**:
   - Uygulama başlatıldığında `startup()` fonksiyonu çağrılır.
   - Bu fonksiyon `send_random_messages()` görevini arka planda başlatır.
   - `asyncio.create_task()` ile başlatılan görev, diğer işlemlerden bağımsız olarak çalışır.

2. **WebSocket Endpoint Çalışması**:
   - Her bağlantı için ayrı bir `websocket_endpoint()` örneği çalışır.
   - `await websocket.receive_text()` satırı, istemciden mesaj gelene kadar bekler.
   - Bu beklerken, diğer bağlantılar ve periyodik mesaj görevi çalışmaya devam eder.

3. **Periyodik Mesaj Gönderme**:
   - `send_random_messages()` fonksiyonu sürekli çalışır.
   - Her 5 saniyede bir, tüm bağlı istemcilere rastgele bir mesaj gönderir.
   - `await asyncio.sleep(5)` satırı, diğer görevlere çalışma fırsatı verir.

## İşte Bu Kodun Çalışma Akışı:

1. Sunucu başlar ve periyodik mesaj görevi arka planda çalışır.
2. Bir istemci bağlandığında:
   - Bağlantı kabul edilir ve listeye eklenir.
   - İstemci mesaj bekleme döngüsüne girer.
   - Aynı zamanda periyodik mesaj görevi de çalışmaya devam eder.
3. İstemci mesaj gönderdiğinde:
   - Mesaj alınır, işlenir ve yanıt gönderilir.
   - Sonra tekrar mesaj bekleme durumuna dönülür.
4. Periyodik görev 5 saniyede bir çalışır:
   - Tüm bağlı istemcilere rastgele mesaj gönderir.
   - Sonra tekrar bekler.

## Paralel İşlemlerin İlişkisi:

Bu kod, async/await'in gücünü gösterir:
- `websocket_endpoint` fonksiyonu istemciden mesaj beklerken bloke olmaz.
- Aynı anda onlarca/yüzlerce istemci bağlantısı aynı anda aktif olabilir.
- Periyodik mesaj görevi, istemci bağlantılarından bağımsız olarak çalışır.
- Tüm bu paralel işlemler tek bir thread'de gerçekleşir.

Buradan şunu anlıyoruz: `await` kullanıldığında, Python o noktada fonksiyonun yürütülmesini "durdurur" ve kontrol tekrar event loop'a döner. Bu sayede diğer asenkron görevler çalışabilir. İşlem tamamlandığında, fonksiyon kaldığı yerden devam eder.

Bu, bir restorandaki garsona benzer: Bir masanın siparişini alıp mutfağa götürdükten sonra, yemek hazırlanırken (`await`) diğer masalara hizmet verebilir. Yemek hazır olduğunda tekrar o masaya döner.