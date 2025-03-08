# FastAPI WebSocket 

## İçindekiler

1. [WebSocket Nedir?](#1-websocket-nedir)
2. [FastAPI ile WebSocket Sunucusu Oluşturma](#2-fastapi-ile-websocket-sunucusu-oluşturma)
3. [WebSocket İstemcileri](#3-websocket-i̇stemcileri)
4. [Asenkron İletişimin Temelleri](#4-asenkron-i̇letişimin-temelleri)
5. [WebSocket ve Asyncio: Workflow Derinlemesine Analiz](#5-websocket-ve-asyncio-workflow-derinlemesine-analiz)
6. [İleri Seviye WebSocket Uygulamaları](#6-i̇leri-seviye-websocket-uygulamaları)
7. [En İyi Uygulamalar ve Sorun Giderme](#7-en-i̇yi-uygulamalar-ve-sorun-giderme)

## 1. WebSocket Nedir?

WebSocket, HTTP üzerinden başlayan ancak sonrasında uzun süreli, çift yönlü bir iletişim kanalına dönüşen bir protokoldür. Normal HTTP isteklerinden farklı olarak:

- **Kalıcı Bağlantı**: Bir kez kurulduktan sonra, bağlantı aktif olarak kapatılana kadar açık kalır.
- **Çift Yönlü İletişim**: Sunucu, istemcinin bir istek yapmasını beklemeden herhangi bir zamanda veri gönderebilir.
- **Düşük Gecikme**: Yeni istek/yanıt döngüsü oluşturma ihtiyacı olmadığından gerçek zamanlı iletişim için idealdir.

### WebSocket vs HTTP

| Özellik | HTTP | WebSocket |
|---------|------|-----------|
| Bağlantı | Her istek için yeni bağlantı | Tek, kalıcı bağlantı |
| İletişim | İstemci istekte bulunur, sunucu yanıt verir | Her iki taraf da istediği zaman mesaj gönderebilir |
| Uygulama Alanları | Sayfa yüklemeleri, API çağrıları | Sohbet uygulamaları, canlı güncellemeler, oyunlar |
| Durum | Durumsuz | Durumlu |

## 2. FastAPI ile WebSocket Sunucusu Oluşturma

### Kurulum ve Bağımlılıklar

```bash
pip install fastapi uvicorn websockets
```

### Temel WebSocket Sunucusu

Aşağıda, temel bir WebSocket sunucusunun uygulama yapısı bulunmaktadır:

```python
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

# Bağlı istemcileri takip etmek için liste
connected_clients = []

@app.get("/")
async def root():
    return {"message": "WebSocket Sunucusu Çalışıyor", 
            "connected_clients": len(connected_clients)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Bağlantıyı kabul et
    await websocket.accept()
    
    # 2. Bağlantıyı listeye ekle
    connected_clients.append(websocket)
    
    try:
        # 3. Sürekli mesaj dinleme döngüsü
        while True:
            # İstemciden mesaj bekle
            data = await websocket.receive_text()
            print(f"Alınan mesaj: {data}")
            
            # İstemciye yanıt gönder
            await websocket.send_text(f"Mesajınız: {data}")
            
            # Diğer tüm istemcilere ilet (broadcast)
            for client in connected_clients:
                if client != websocket:  # Kendisi hariç
                    await client.send_text(f"Başka bir istemciden: {data}")
    
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        # 4. Bağlantı kesildiğinde temizlik
        if websocket in connected_clients:
            connected_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

### WebSocket Endpoint'ini Anlamak

FastAPI'de WebSocket endpoint'i oluşturmak için `@app.websocket()` dekoratörünü kullanırız:

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # WebSocket işlemleri...
```

Bu dekoratör, `/ws` URL yoluna gelen WebSocket bağlantı isteklerini bu fonksiyona yönlendirir. Fonksiyon bir `WebSocket` nesnesi alır ve bu nesne üzerinden mesaj alıp gönderebiliriz.

### Sunucuyu Başlatma

FastAPI uygulamasını çalıştırmak için Uvicorn ASGI sunucusunu kullanırız:

```python
uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

- `"server:app"`: "server.py" dosyasındaki "app" nesnesini çalıştırır
- `host="0.0.0.0"`: Tüm ağ arayüzlerinden bağlantıları kabul eder
- `port=8000`: 8000 portunu dinler
- `reload=True`: Kod değişikliklerinde otomatik yeniden başlatır (geliştirme için)

## 3. WebSocket İstemcileri

WebSocket iletişiminde başarılı olmak için hem sunucu hem de istemci tarafının doğru yapılandırılması gerekir. Bu bölümde farklı istemci uygulamalarını inceleyeceğiz.

### 3.1 JavaScript İstemcisi: Derinlemesine İnceleme

JavaScript, tarayıcılarda WebSocket kullanımı için yerleşik destek sunar. Aşağıda ayrıntılı bir HTML/JavaScript istemcisi ve her bir bileşenin açıklaması bulunmaktadır:

```html
<!DOCTYPE html>
<html>
<head>
    <title>WebSocket İstemcisi</title>
    <style>
        body { font-family: Arial, sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; }
        #messageContainer { height: 300px; overflow-y: auto; border: 1px solid #ccc; margin-bottom: 10px; padding: 10px; }
        #messageForm { display: flex; }
        #messageText { flex-grow: 1; padding: 8px; }
        .error { color: red; }
        .received { color: blue; }
        .sent { color: green; }
        .system { color: gray; font-style: italic; }
    </style>
</head>
<body>
    <h1>WebSocket İstemcisi</h1>
    <div id="connectionStatus" class="system">Bağlantı bekleniyor...</div>
    <div id="messageContainer"></div>
    
    <form id="messageForm" onsubmit="sendMessage(event)">
        <input type="text" id="messageText" placeholder="Mesajınızı yazın..." autocomplete="off"/>
        <button type="submit">Gönder</button>
    </form>
    
    <script>
        // 1. Değişkenler ve DOM elementleri
        const messageContainer = document.getElementById('messageContainer');
        const connectionStatus = document.getElementById('connectionStatus');
        let ws = null;
        let reconnectAttempts = 0;
        const maxReconnectAttempts = 5;
        
        // 2. Yardımcı fonksiyonlar
        function addMessageToUI(message, type) {
            const messageElement = document.createElement('div');
            messageElement.textContent = message;
            messageElement.className = type;
            messageContainer.appendChild(messageElement);
            messageContainer.scrollTop = messageContainer.scrollHeight;
        }
        
        // 3. WebSocket bağlantısı kurma
        function connectWebSocket() {
            // WebSocket URL'si (sunucu adresi)
            ws = new WebSocket("ws://localhost:8000/ws");
            
            // 4. Bağlantı açıldığında tetiklenen olay
            ws.onopen = function(event) {
                connectionStatus.textContent = "Bağlantı aktif";
                connectionStatus.className = "system";
                addMessageToUI("Sunucuya bağlandı", "system");
                reconnectAttempts = 0;
            };
            
            // 5. Mesaj alındığında tetiklenen olay
            ws.onmessage = function(event) {
                // event.data içinde sunucudan gelen mesaj bulunur
                addMessageToUI(event.data, "received");
            };
            
            // 6. Bağlantı hatası oluştuğunda tetiklenen olay
            ws.onerror = function(event) {
                connectionStatus.textContent = "Bağlantı hatası!";
                connectionStatus.className = "error";
                addMessageToUI("Bağlantı hatası oluştu", "error");
            };
            
            // 7. Bağlantı kapandığında tetiklenen olay
            ws.onclose = function(event) {
                connectionStatus.textContent = "Bağlantı kapandı";
                connectionStatus.className = "system";
                addMessageToUI(`Bağlantı kapandı (Kod: ${event.code})`, "system");
                
                // 8. Yeniden bağlanma stratejisi
                if (reconnectAttempts < maxReconnectAttempts) {
                    const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
                    
                    addMessageToUI(`${timeout/1000} saniye sonra yeniden bağlanılacak...`, "system");
                    
                    setTimeout(() => {
                        reconnectAttempts++;
                        connectWebSocket();
                    }, timeout);
                } else {
                    addMessageToUI("Maksimum yeniden bağlanma denemesi aşıldı.", "error");
                }
            };
        }
        
        // 9. Mesaj gönderme fonksiyonu
        function sendMessage(event) {
            event.preventDefault();
            const input = document.getElementById("messageText");
            const message = input.value.trim();
            
            if (message && ws && ws.readyState === WebSocket.OPEN) {
                // Mesaj gönderme
                ws.send(message);
                addMessageToUI(`Gönderildi: ${message}`, "sent");
                input.value = '';
            } else if (!ws || ws.readyState !== WebSocket.OPEN) {
                addMessageToUI("Mesaj gönderilemedi: Bağlantı yok", "error");
            }
        }
        
        // 10. Bağlantıyı başlat
        connectWebSocket();
        
        // 11. Sayfa kapatıldığında temiz kapatma
        window.addEventListener('beforeunload', () => {
            if (ws && ws.readyState === WebSocket.OPEN) {
                // 1000: Normal kapatma kodu
                ws.close(1000, "Sayfa kapatıldı");
            }
        });
    </script>
</body>
</html>
```

#### JavaScript WebSocket API'sinin Detaylı İncelemesi

1. **WebSocket Nesnesi Oluşturma**

   ```javascript
   ws = new WebSocket("ws://localhost:8000/ws");
   ```

   Bu satır, WebSocket protokolünü kullanarak sunucuya bağlantı başlatır. "ws://" öneki, WebSocket protokolünü belirtir (HTTPS için "wss://").

2. **WebSocket Hazır Durumları**
   WebSocket nesnesi dört farklı durumda olabilir:

   ```javascript
   WebSocket.CONNECTING (0): Bağlantı henüz kurulmadı
   WebSocket.OPEN (1):       Bağlantı kuruldu ve iletişim hazır
   WebSocket.CLOSING (2):    Bağlantı kapatılıyor
   WebSocket.CLOSED (3):     Bağlantı kapalı
   ```

   Bu durumları kontrol etmek için:

   ```javascript
   if (ws.readyState === WebSocket.OPEN) {
       // Bağlantı açık, mesaj gönderebiliriz
   }
   ```

3. **Olay İşleyicileri (Event Handlers)**
   WebSocket API, bağlantının yaşam döngüsü boyunca çeşitli olaylar için işleyiciler sunar:

   - **onopen**: Bağlantı başarıyla kurulduğunda tetiklenir
   - **onmessage**: Sunucudan mesaj alındığında tetiklenir
   - **onerror**: Bir hata oluştuğunda tetiklenir
   - **onclose**: Bağlantı kapatıldığında tetiklenir

4. **Mesaj Gönderme**

   ```javascript
   ws.send("Merhaba Dünya!");
   ```

   `send()` metodu ile sunucuya metin, ArrayBuffer, Blob veya JSON verisi gönderebilirsiniz.

5. **Farklı Veri Tiplerini Gönderme ve Alma**

   **Metin (String):**

   ```javascript
   ws.send("Metin mesajı");
   ```

   **JSON:**

   ```javascript
   const data = { user: "Ali", message: "Merhaba", timestamp: Date.now() };
   ws.send(JSON.stringify(data));
   
   // Alırken:
   ws.onmessage = function(event) {
       const data = JSON.parse(event.data);
       console.log(data.user, data.message);
   };
   ```

   **Binary Data (ArrayBuffer veya Blob):**

   ```javascript
   // ArrayBuffer gönderme
   const buffer = new ArrayBuffer(4);
   const view = new Uint8Array(buffer);
   view[0] = 10; view[1] = 20; view[2] = 30; view[3] = 40;
   ws.send(buffer);
   
   // Blob gönderme
   const blob = new Blob(["Binary veri göndermek için Blob kullanılabilir"], {type: 'application/octet-stream'});
   ws.send(blob);
   ```

6. **Bağlantıyı Kapatma**

   ```javascript
   ws.close(1000, "İşlem tamamlandı");
   ```

   İlk parametre kapatma kodu (1000 normal kapatma), ikinci parametre ise kapatma nedenidir.

7. **Ping/Pong ve Bağlantı Kontrolü**
   WebSocket protokolü, bağlantının canlı olduğunu doğrulamak için ping/pong mekanizması içerir. Bu genellikle tarayıcı tarafından otomatik olarak yönetilir, ancak uzun süreli bağlantılarda kendi denetim mekanizmanızı ekleyebilirsiniz:

   ```javascript
   // Her 30 saniyede bir bağlantıyı kontrol et
   const heartbeatInterval = setInterval(() => {
       if (ws.readyState === WebSocket.OPEN) {
           ws.send(JSON.stringify({type: "heartbeat"}));
       } else {
           clearInterval(heartbeatInterval);
       }
   }, 30000);
   ```

### 3.2 Python İstemcisi

Python'da WebSocket istemcisi oluşturmak için `websockets` kütüphanesini kullanabiliriz:

```python
import asyncio
import websockets
import json

async def listen_for_messages(websocket):
    """Sunucudan gelen mesajları sürekli dinleyen fonksiyon"""
    try:
        while True:
            message = await websocket.recv()
            print(f"Sunucudan mesaj: {message}")
    except websockets.exceptions.ConnectionClosed:
        print("Bağlantı kapandı")

async def send_message(websocket):
    """Kullanıcıdan alınan mesajları sunucuya gönderen fonksiyon"""
    try:
        while True:
            message = input("Göndermek istediğiniz mesaj: ")
            if message.lower() == 'exit':
                break
            await websocket.send(message)
    except websockets.exceptions.ConnectionClosed:
        print("Bağlantı kapandı")

async def websocket_client():
    """Ana istemci fonksiyonu"""
    uri = "ws://localhost:8000/ws"
    
    async with websockets.connect(uri) as websocket:
        print(f"Bağlantı kuruldu: {uri}")
        
        # İki görevi paralel çalıştır
        listener_task = asyncio.create_task(listen_for_messages(websocket))
        sender_task = asyncio.create_task(send_message(websocket))
        
        # Herhangi bir görev tamamlanana kadar bekle
        done, pending = await asyncio.wait(
            [listener_task, sender_task],
            return_when=asyncio.FIRST_COMPLETED
        )
        
        # Bekleyen görevleri iptal et
        for task in pending:
            task.cancel()

# İstemciyi çalıştır
asyncio.run(websocket_client())
```

### 3.3 HTTP Endpoint Üzerinden WebSocket İstemcisi

FastAPI'de HTTP endpoint'leri aracılığıyla WebSocket mesajları göndermek de mümkündür:

```python
from fastapi import FastAPI, WebSocket, HTTPException
from fastapi.responses import HTMLResponse
import uvicorn
import websockets
import asyncio

app = FastAPI()

# HTML içeriği (yukarıdaki HTML kodu)
html = """<!DOCTYPE html>..."""

@app.get("/")
async def get():
    return HTMLResponse(html)

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
        raise HTTPException(status_code=500, detail=f"WebSocket hatası: {str(e)}")

if __name__ == "__main__":
    uvicorn.run("client:app", host="0.0.0.0", port=8001, reload=True)
```

## 4. Asenkron İletişimin Temelleri

### Async/Await Yapısının Önemi

FastAPI'de WebSocket işlemleri asenkron programlama modelini kullanır. Bu model, tek bir thread'de birden fazla işlemi eşzamanlı olarak yönetmeyi sağlar.

#### `await` Anahtar Kelimesinin İşlevi

`await` anahtar kelimesi şu anlama gelir: "Bu asenkron işlemin tamamlanmasını bekle, ama beklerken diğer işlemlerin de çalışmasına izin ver."

```python
# Bu satırda:
data = await websocket.receive_text()

# 1. İstemciden mesaj gelene kadar bekleriz
# 2. Ancak bu bekleme, diğer işlemlerin çalışmasını engellemez
# 3. Diğer WebSocket bağlantıları da aynı anda işlem görebilir
```

#### Asenkron Programlamanın Avantajları

1. **Yüksek Ölçeklenebilirlik**: Tek bir işlem (process) içinde binlerce bağlantıyı yönetebilirsiniz.
2. **Verimli Kaynak Kullanımı**: Thread'leri bloke etmeden I/O işlemleri gerçekleştirebilirsiniz.
3. **Gerçek Zamanlı Uygulama Desteği**: Düşük gecikme süresiyle çift yönlü iletişim kurabilirsiniz.

### Garson Benzetmesi

Asenkron programlama, bir restorandaki garsona benzer:

- Bir masanın siparişini alıp mutfağa götürdükten sonra
- Yemek hazırlanırken (`await`) diğer masalara hizmet verebilir
- Yemek hazır olduğunda tekrar ilk masaya döner

## 5. WebSocket ve Asyncio: Workflow Derinlemesine Analiz

Şimdi, temel bir WebSocket sunucu uygulamasının iç işleyişini satır satır inceleyerek, Python'un asenkron programlama modelinin websocket uygulamalarındaki rolünü daha iyi anlayalım.

```python
from fastapi import FastAPI, WebSocket
import uvicorn

app = FastAPI()

# Bağlı istemcileri takip etmek için liste
connected_clients = []

@app.get("/")
async def root():
    return {"message": "WebSocket Sunucusu Çalışıyor", 
            "connected_clients": len(connected_clients)}

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    # 1. Bağlantıyı kabul et
    await websocket.accept()
    
    # 2. Bağlantıyı listeye ekle
    connected_clients.append(websocket)
    
    try:
        # 3. Sürekli mesaj dinleme döngüsü
        while True:
            # İstemciden mesaj bekle
            data = await websocket.receive_text()
            print(f"Alınan mesaj: {data}")
            
            # İstemciye yanıt gönder
            await websocket.send_text(f"Mesajınız: {data}")
            
            # Diğer tüm istemcilere ilet (broadcast)
            for client in connected_clients:
                if client != websocket:  # Kendisi hariç
                    await client.send_text(f"Başka bir istemciden: {data}")
    
    except Exception as e:
        print(f"Hata: {e}")
    finally:
        # 4. Bağlantı kesildiğinde temizlik
        if websocket in connected_clients:
            connected_clients.remove(websocket)

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

### 5.1 Asenkron Fonksiyon ve Event Loop

```python
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
```

- **`async def` deklarasyonu**: Bu fonksiyonun bir coroutine olduğunu belirtir. Python'un asenkron programlama modelinde, coroutine'ler event loop tarafından yönetilen özel fonksiyonlardır.
- **Event Loop**: Python'un asyncio kütüphanesi, arka planda bir "event loop" (olay döngüsü) çalıştırır. Bu döngü, asenkron görevleri zamanlar ve yürütür.
- **Eş Zamanlı Bağlantılar**: Her yeni websocket bağlantısı için, FastAPI bu fonksiyonun yeni bir örneğini başlatır. Hepsi aynı event loop üzerinde çalışır, ancak her biri kendi yürütme bağlamına sahiptir.

### 5.2 Bağlantı Kurulma Süreci

```python
await websocket.accept()
connected_clients.append(websocket)
```

1. **Bağlantı İsteği**: İstemci `ws://sunucu/ws` adresine bir bağlantı isteği gönderir.
2. **HTTP Yükseltme**: WebSocket protokolü başlangıçta HTTP üzerinden bir "upgrade" (yükseltme) isteği gönderir:

   ```
   GET /ws HTTP/1.1
   Host: sunucu
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Key: dGhlIHNhbXBsZSBub25jZQ==
   ```

3. **FastAPI Yönlendirmesi**: FastAPI bu isteği `websocket_endpoint` fonksiyonuna yönlendirir ve bir `WebSocket` nesnesi oluşturur.
4. **Bağlantı Kabulü**: `await websocket.accept()` çağrısı, HTTP bağlantısını WebSocket protokolüne yükseltir ve istemciye aşağıdaki gibi bir yanıt gönderir:

   ```
   HTTP/1.1 101 Switching Protocols
   Upgrade: websocket
   Connection: Upgrade
   Sec-WebSocket-Accept: s3pPLMBiTxaQ9kYGzzhZRbK+xOo=
   ```

5. **Event Loop İlişkisi**: `await` ifadesi, fonksiyonun bu noktada "duraklatılmasını" sağlar. İşlem tamamlanana kadar kontrol event loop'a döner, böylece loop diğer görevleri (örneğin başka WebSocket bağlantılarını) yürütebilir.

### 5.3 Mesaj Alma Döngüsü ve Event Loop Etkileşimi

```python
while True:
    data = await websocket.receive_text()
    # İşlemler...
```

Bu sonsuz döngü, asenkron programlamanın önemini gösterir:

1. **Her İstemci İçin Tek "Thread"**: Her WebSocket bağlantısı için bir döngü çalışır, ancak her döngü kendi başına bir thread değildir.
2. **Cooperative Multitasking (İşbirlikçi Çoklu Görev)**: Her `await` ifadesi bir "yield point" (vazgeçme noktası) oluşturur - bu noktalarda fonksiyon kontrolü event loop'a geri verir.

### 5.4 Bir WebSocket İşleminin Yaşam Döngüsü

Tek bir WebSocket bağlantısının yaşam döngüsünü ve event loop etkileşimini adım adım inceleyelim:

1. **Bağlantı İsteği**: İstemci bağlantı isteği gönderir.
2. **Fonksiyon Başlatılır**: FastAPI, `websocket_endpoint` fonksiyonunu çalıştırır.
3. **İlk Await Noktası**: `await websocket.accept()` çağrısında:
   - Fonksiyon duraklatılır
   - Kontrol event loop'a döner
   - Event loop diğer görevleri işleyebilir
   - Kabul işlemi tamamlandığında, fonksiyon kaldığı yerden devam eder
4. **Listeye Ekleme**: `connected_clients.append(websocket)` çağrısı senkron olarak çalışır (await yok).
5. **Mesaj Bekleme Aşaması**: `await websocket.receive_text()` çağrısında:
   - Fonksiyon tekrar duraklatılır
   - Kontrol event loop'a döner
   - Event loop diğer görevleri işleyebilir
   - **Önemli**: İstemciden mesaj gelene kadar bu fonksiyon "uyanmaz"
   - Mesaj geldiğinde, fonksiyon kaldığı yerden devam eder
6. **Mesaj İşleme**: Mesaj alındıktan sonra işlemler yapılır.
7. **Broadcast**: Diğer istemcilere mesaj gönderilir.
8. **Döngü Tekrarı**: Yeni bir mesaj için bekleme durumuna geri dönülür.

### 5.5 Bağlantı Kapanma ve Hata Yönetimi

```python
try:
    # Döngü...
except Exception as e:
    print(f"Hata: {e}")
finally:
    if websocket in connected_clients:
        connected_clients.remove(websocket)
```

1. **Bağlantı Kopması**: İstemci bağlantıyı kapatırsa veya ağ hatası oluşursa
2. **Exception Oluşumu**: `websocket.receive_text()` çağrısı bir hata fırlatır
3. **Hata Yakalama**: Exception yakalanır ve işlenir
4. **Temizlik İşlemi**: `finally` bloğu her durumda çalışır ve bağlantıyı listeden kaldırır
5. **Fonksiyon Sonlanması**: WebSocket fonksiyonu sona erer ve kaynakları serbest bırakır

### 5.6 Asenkron ve Senkron Kod Karışımı

```python
data = await websocket.receive_text()  # Asenkron
print(f"Alınan mesaj: {data}")  # Senkron
await websocket.send_text(f"Mesajınız: {data}")  # Asenkron
```

- **Asenkron İşlemler**: `await` ifadesiyle işaretlenmiştir ve event loop ile etkileşime girer
- **Senkron İşlemler**: Normal çalışır ve event loop'u bloke etmez (kısa süreli olması koşuluyla)
- **Dikkat Edilmesi Gereken Nokta**: Uzun süren senkron işlemler tüm event loop'u bloke edebilir

### 5.7 Uvicorn ve Asenkron Web Sunucusu

```python
if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=8000, reload=True)
```

- **ASGI Sunucusu**: Uvicorn, asenkron web uygulamalarını çalıştırmak için tasarlanmış bir ASGI (Asynchronous Server Gateway Interface) sunucusudur.
- **Event Loop Yönetimi**: Uvicorn, arka planda asyncio event loop'unu yönetir.
- **Worker Modeli**: Varsayılan olarak tek bir işlem içinde event loop tabanlı eşzamanlılık kullanır.

### 5.8 WebSocket ve Asenkron Programlamanın Görsel Akışı

```
İstemci 1 ────────┐                 ┌─── Event Loop ───┐
                  │                 │                   │
İstemci 2 ────────┼───> FastAPI ───>│  websocket_1     │
                  │                 │  websocket_2     │
İstemci 3 ────────┘                 │  websocket_3     │
                                    │  ...             │
                                    └───────────────────┘
                                           ▲  │
                                           │  │
                             await duraklatma │  │ devam etme
                                           │  │
                                           │  ▼
                                    ┌───────────────────┐
                                    │    I/O İşlemleri  │
                                    │  (ağ, dosya, vb)  │
                                    └───────────────────┘
```

Bu görsel akış şunları gösterir:

- Tüm websocket bağlantıları aynı event loop içinde yönetilir
- Her bir bağlantı, `await` ifadelerinde duraklatılabilir
- Bir bağlantı duraklatıldığında, event loop diğer bağlantıları işleyebilir
- I/O işlemleri (ağ, dosya, vb.) tamamlandığında, duraklatılmış bağlantılar devam eder

### 5.9 Performans ve Ölçeklenebilirlik

Bu asenkron model sayesinde:

1. **Yüksek Eşzamanlılık**: Tek bir işlem binlerce WebSocket bağlantısını yönetebilir
2. **Düşük Kaynak Kullanımı**: Thread ve süreç ek yükü olmadan eşzamanlılık
3. **Verimli CPU Kullanımı**: I/O beklerken bile CPU kaynakları boş kalmaz
4. **İşlemci Çekirdekleri**: Python'un GIL (Global Interpreter Lock) kısıtlaması nedeniyle, çoklu işlemci çekirdeklerinden yararlanmak için çoklu işlem (multiprocessing) kullanılmalıdır

   ```python
   uvicorn.run("server:app", host="0.0.0.0", port=8000, workers=4)
   ```

### 5.10 Asenkron Programlama İlkeleri ve Temel Kurallar

1. **Await Kuralı**: Asenkron bir fonksiyonu çağırırken mutlaka `await` kullanın

   ```python
   # Yanlış
   websocket.accept()  # Bu sadece bir coroutine nesnesi döndürür
   
   # Doğru
   await websocket.accept()  # Bu fiilen işlemi başlatır ve tamamlanmasını bekler
   ```

2. **Bloke Etmeme İlkesi**: Asenkron bir fonksiyon içinde uzun süren senkron işlemler yapmayın

   ```python
   # Kötü (tüm event loop'u bloke eder)
   time.sleep(5)  # Senkron bekleme 
   
   # İyi (sadece bu coroutine'i duraklatır)
   await asyncio.sleep(5)  # Asenkron bekleme
   ```

3. **Tüm Asenkron İşlemleri Await'leyin**: Bir coroutine'i await ile çağırmazsanız, işlem asla çalışmaz

   ```python
   # Hiçbir şey yapmaz
   asyncio.sleep(1)
   
   # 1 saniye bekler
   await asyncio.sleep(1)
   ```

4. **Asyncio Görevleri**: Bağımsız görevler için `asyncio.create_task()` kullanın

   ```python
   # Arka planda çalışan bir görev
   task = asyncio.create_task(background_job())
   
   # İsteğe bağlı olarak görevin tamamlanmasını bekleyebilirsiniz
   await task
   ```

### 5.11 AsyncIO ve WebSocket: Bütünleşik Örnek

Bu ilkeleri FastAPI olmadan, saf asyncio kullanarak uygulamak isterseniz:

```python
import asyncio
import websockets

# Bağlı istemcileri takip etmek için set
connected_clients = set()

async def handle_connection(websocket, path):
    # Bağlantıyı kaydet
    connected_clients.add(websocket)
    try:
        async for message in websocket:
            print(f"Alınan mesaj: {message}")
            
            # Mesajı gönderen istemciye yanıt ver
            await websocket.send(f"Mesajınız: {message}")
            
            # Diğer tüm istemcilere broadcast yap
            websockets_tasks = []
            for client in connected_clients:
                if client != websocket:
                    task = asyncio.create_task(
                        client.send(f"Başka bir istemciden: {message}")
                    )
                    websockets_tasks.append(task)
            
            # İsteğe bağlı: tüm broadcast görevlerinin tamamlanmasını bekle
            if websockets_tasks:
                await asyncio.gather(*websockets_tasks)
                
    except websockets.exceptions.ConnectionClosed:
        print("Bağlantı kapandı")
    finally:
        connected_clients.remove(websocket)

# WebSocket sunucusunu başlat
start_server = websockets.serve(handle_connection, "localhost", 8765)

# Event loop'u çalıştır
asyncio.get_event_loop().run_until_complete(start_server)
asyncio.get_event_loop().run_forever()
```

Bu örnek, FastAPI'nin arka planda yaptığı işlemlerin basitleştirilmiş bir versiyonudur ve asyncio ile websockets kütüphanelerinin doğrudan kullanımını gösterir.

## 6. İleri Seviye WebSocket Uygulamaları

### 6.1 Odalar ve Özel Kanallar: Derinlemesine İnceleme

Gerçek dünya uygulamalarında, farklı kullanıcı grupları için ayrı iletişim kanalları oluşturmak sıklıkla gereklidir. "Odalar" veya "kanallar" konsepti, WebSocket iletişiminde hedeflenmiş mesajlaşmayı sağlar.

#### 6.1.1 Odalar ve Kanallar Nedir ve Neden Kullanılır?

**Tanım:**
Odalar ve kanallar, WebSocket bağlantılarını mantıksal gruplara ayırmak için kullanılan soyut kavramlardır. WebSocket protokolünün kendisinde odalar yoktur; bunlar sunucu tarafında uygulama seviyesinde yapılandırılır.

**Kullanım Nedenleri:**

1. **Hedefli İletişim**: Mesajları yalnızca belirli alıcılara gönderme (örneğin bir sohbet odasındaki kullanıcılar)
2. **Ölçeklenebilirlik**: Tüm kullanıcılara değil, yalnızca ilgili kullanıcılara mesaj göndererek kaynak tasarrufu
3. **Veri İzolasyonu**: Kullanıcıların yalnızca erişim hakkına sahip oldukları verileri almasını sağlama
4. **Uygulama Mantığı**: İş akışlarını veya kullanıcı deneyimini segmentlere ayırma (örneğin oyun odaları, departman kanalları)

#### 6.1.2 Oda Tabanlı WebSocket Yöneticisi Uygulaması

Aşağıda, oda özellikli tam bir WebSocket yöneticisi uygulaması bulunmaktadır:

```python
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Path, Query, Depends, HTTPException
from typing import Dict, List, Set, Optional
import asyncio
import json
import uuid

app = FastAPI()

# WebSocket bağlantı yöneticisi
class ConnectionManager:
    def __init__(self):
        # Tüm bağlantılar: {client_id: websocket}
        self.active_connections: Dict[str, WebSocket] = {}
        
        # Oda başına bağlantılar: {room_id: {client_id, client_id, ...}}
        self.rooms: Dict[str, Set[str]] = {}
        
        # İstemci bilgileri: {client_id: {"username": username, "rooms": [room_id, room_id, ...]}}
        self.client_info: Dict[str, Dict] = {}
    
    async def connect(self, websocket: WebSocket, client_id: str, username: str) -> None:
        """Yeni bir WebSocket bağlantısı kabul eder"""
        await websocket.accept()
        self.active_connections[client_id] = websocket
        self.client_info[client_id] = {"username": username, "rooms": set()}
    
    def disconnect(self, client_id: str) -> None:
        """Bir bağlantıyı kaldırır ve temizlik yapar"""
        if client_id in self.active_connections:
            # Bağlantıyı sil
            del self.active_connections[client_id]
            
            # İstemci bilgilerinden odaları al
            if client_id in self.client_info:
                client_rooms = list(self.client_info[client_id]["rooms"])
                
                # Her odadan istemciyi kaldır
                for room_id in client_rooms:
                    self.leave_room(client_id, room_id)
                
                # İstemci bilgilerini sil
                del self.client_info[client_id]
    
    async def join_room(self, client_id: str, room_id: str) -> None:
        """Bir istemciyi bir odaya ekler"""
        # Oda yoksa oluştur
        if room_id not in self.rooms:
            self.rooms[room_id] = set()
        
        # İstemciyi odaya ekle
        self.rooms[room_id].add(client_id)
        
        # İstemcinin oda listesini güncelle
        if client_id in self.client_info:
            self.client_info[client_id]["rooms"].add(room_id)
            
            # İstemciye katılma onayı gönder
            await self.send_personal_message(
                client_id,
                {"type": "system", "message": f"'{room_id}' odasına katıldınız"}
            )
            
            # Odadaki diğer üyelere bildirim gönder
            username = self.client_info[client_id]["username"]
            await self.broadcast_to_room(
                room_id,
                {"type": "system", "message": f"{username} odaya katıldı"},
                exclude_client=client_id
            )
    
    def leave_room(self, client_id: str, room_id: str) -> bool:
        """Bir istemciyi bir odadan çıkarır"""
        if room_id in self.rooms and client_id in self.rooms[room_id]:
            # İstemciyi odadan kaldır
            self.rooms[room_id].remove(client_id)
            
            # Oda boşsa odayı sil
            if not self.rooms[room_id]:
                del self.rooms[room_id]
            
            # İstemcinin oda listesinden odayı kaldır
            if client_id in self.client_info and room_id in self.client_info[client_id]["rooms"]:
                self.client_info[client_id]["rooms"].remove(room_id)
            
            return True
        return False
    
    async def broadcast_to_room(self, room_id: str, message: dict, exclude_client: Optional[str] = None) -> int:
        """Bir odadaki tüm istemcilere mesaj gönderir, exclude_client hariç"""
        message_count = 0
        
        if room_id in self.rooms:
            message_json = json.dumps(message)
            send_tasks = []
            
            for client_id in self.rooms[room_id]:
                if client_id != exclude_client and client_id in self.active_connections:
                    websocket = self.active_connections[client_id]
                    send_tasks.append(websocket.send_text(message_json))
                    message_count += 1
            
            if send_tasks:
                # Tüm gönderme işlemlerini paralel olarak çalıştır
                await asyncio.gather(*send_tasks)
        
        return message_count
    
    async def send_personal_message(self, client_id: str, message: dict) -> bool:
        """Belirli bir istemciye mesaj gönderir"""
        if client_id in self.active_connections:
            websocket = self.active_connections[client_id]
            await websocket.send_text(json.dumps(message))
            return True
        return False
    
    def get_room_members(self, room_id: str) -> List[Dict]:
        """Bir odadaki tüm üyelerin listesini döndürür"""
        members = []
        
        if room_id in self.rooms:
            for client_id in self.rooms[room_id]:
                if client_id in self.client_info:
                    members.append({
                        "client_id": client_id,
                        "username": self.client_info[client_id]["username"]
                    })
        
        return members

# Bağlantı yöneticisi örneği
manager = ConnectionManager()

# Oda listesini döndüren HTTP endpoint
@app.get("/rooms")
async def get_rooms():
    rooms_info = []
    
    for room_id, clients in manager.rooms.items():
        rooms_info.append({
            "room_id": room_id,
            "member_count": len(clients),
            "members": manager.get_room_members(room_id)
        })
    
    return {"rooms": rooms_info}

# WebSocket endpoint'i
@app.websocket("/ws/{client_id}")
async def websocket_endpoint(
    websocket: WebSocket,
    client_id: str = Path(...),
    username: str = Query(None)
):
    # İstemci ID boşsa rastgele oluştur
    if not client_id or client_id == "undefined":
        client_id = str(uuid.uuid4())
    
    # Kullanıcı adı boşsa varsayılan oluştur
    if not username:
        username = f"User-{client_id[:8]}"
    
    # Bağlantıyı kabul et
    await manager.connect(websocket, client_id, username)
    
    try:
        while True:
            # İstemciden mesaj bekle
            data = await websocket.receive_text()
            
            try:
                # JSON mesajı ayrıştır
                message_data = json.loads(data)
                message_type = message_data.get("type", "message")
                
                # Mesaj tipine göre işlem yap
                if message_type == "join_room":
                    # Odaya katılma işlemi
                    room_id = message_data.get("room_id")
                    if room_id:
                        await manager.join_room(client_id, room_id)
                
                elif message_type == "leave_room":
                    # Odadan ayrılma işlemi
                    room_id = message_data.get("room_id")
                    if room_id:
                        success = manager.leave_room(client_id, room_id)
                        if success:
                            await manager.send_personal_message(
                                client_id,
                                {"type": "system", "message": f"'{room_id}' odasından ayrıldınız"}
                            )
                
                elif message_type == "room_message":
                    # Odaya mesaj gönderme işlemi
                    room_id = message_data.get("room_id")
                    content = message_data.get("message", "")
                    
                    if room_id and client_id in manager.client_info and room_id in manager.client_info[client_id]["rooms"]:
                        username = manager.client_info[client_id]["username"]
                        
                        # Mesajı odaya yayınla
                        await manager.broadcast_to_room(
                            room_id,
                            {
                                "type": "chat",
                                "room_id": room_id,
                                "client_id": client_id,
                                "username": username,
                                "message": content,
                                "timestamp": datetime.datetime.now().isoformat()
                            }
                        )
                
                elif message_type == "get_rooms":
                    # İstemciye oda listesini gönder
                    rooms_info = []
                    for room_id, clients in manager.rooms.items():
                        rooms_info.append({
                            "room_id": room_id,
                            "member_count": len(clients)
                        })
                    
                    await manager.send_personal_message(
                        client_id,
                        {"type": "room_list", "rooms": rooms_info}
                    )
                
                elif message_type == "get_room_members":
                    # Oda üyelerini gönder
                    room_id = message_data.get("room_id")
                    if room_id:
                        members = manager.get_room_members(room_id)
                        await manager.send_personal_message(
                            client_id,
                            {"type": "room_members", "room_id": room_id, "members": members}
                        )
            
            except json.JSONDecodeError:
                # Düz metin mesajlarını kişisel mesaj olarak ele al
                await manager.send_personal_message(
                    client_id,
                    {"type": "error", "message": "JSON formatında mesaj göndermelisiniz"}
                )
    
    except WebSocketDisconnect:
        # Bağlantı kesilirse temizlik yap
        manager.disconnect(client_id)

if __name__ == "__main__":
    import uvicorn
    import datetime
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

#### 6.1.3 Neden Bu Yaklaşım?

1. **Esnek Üyelik Yapısı**:
   - Bir istemci birden fazla odaya katılabilir
   - Odalar dinamik olarak oluşturulup silinebilir
   - İstemciler ve odalar arasında çift yönlü eşleme

2. **Verimli Mesaj Dağıtımı**:
   - Mesajlar yalnızca ilgili alıcılara gönderilir
   - Broadcast işlemleri paralel olarak yürütülür (`asyncio.gather()`)
   - Belirli istemcileri hariç tutma yeteneği

3. **Kullanıcı Deneyimi**:
   - Oda üyeliği değişiklikleri hakkında bildirimler
   - Kullanıcı adı desteği
   - İstemci ve oda durumu hakkında bilgi alma yeteneği

4. **Hata Yönetimi ve Temizlik**:
   - Bağlantı kesildiğinde tüm oda üyeliklerini temizleme
   - Boş odaları otomatik olarak silme
   - Hatalı mesajları ele alma

#### 6.1.4 JavaScript İstemci Örneği

Oda tabanlı WebSocket sunucusuyla iletişim kuran bir JavaScript istemcisi:

```javascript
class RoomChatClient {
    constructor(serverUrl) {
        this.serverUrl = serverUrl;
        this.clientId = localStorage.getItem('clientId') || crypto.randomUUID();
        this.username = localStorage.getItem('username') || `User-${this.clientId.slice(0, 8)}`;
        this.ws = null;
        this.rooms = new Set(); // Katıldığım odalar
        this.onMessageCallbacks = [];
        this.onStatusChangeCallbacks = [];
        
        // İstemci ID'yi kaydet
        localStorage.setItem('clientId', this.clientId);
    }
    
    connect() {
        // WebSocket bağlantısı oluştur
        const url = `${this.serverUrl}/ws/${this.clientId}?username=${encodeURIComponent(this.username)}`;
        this.ws = new WebSocket(url);
        
        // Bağlantı açıldığında
        this.ws.onopen = () => {
            this._notifyStatusChange('connected');
            this._getRoomList(); // Oda listesini al
        };
        
        // Mesaj alındığında
        this.ws.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                this._handleMessage(data);
            } catch (error) {
                console.error('Mesaj işleme hatası:', error);
            }
        };
        
        // Bağlantı kapandığında
        this.ws.onclose = () => {
            this._notifyStatusChange('disconnected');
            // 3 saniye sonra yeniden bağlan
            setTimeout(() => this.connect(), 3000);
        };
        
        // Hata oluştuğunda
        this.ws.onerror = (error) => {
            console.error('WebSocket hatası:', error);
            this._notifyStatusChange('error');
        };
    }
    
    joinRoom(roomId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'join_room',
                room_id: roomId
            }));
            this.rooms.add(roomId);
            return true;
        }
        return false;
    }
    
    leaveRoom(roomId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'leave_room',
                room_id: roomId
            }));
            this.rooms.delete(roomId);
            return true;
        }
        return false;
    }
    
    sendRoomMessage(roomId, message) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'room_message',
                room_id: roomId,
                message: message
            }));
            return true;
        }
        return false;
    }
    
    getRoomMembers(roomId) {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'get_room_members',
                room_id: roomId
            }));
            return true;
        }
        return false;
    }
    
    _getRoomList() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.send(JSON.stringify({
                type: 'get_rooms'
            }));
            return true;
        }
        return false;
    }
    
    // Mesaj olayı için callback ekle
    onMessage(callback) {
        if (typeof callback === 'function') {
            this.onMessageCallbacks.push(callback);
        }
        return this;
    }
    
    // Durum değişikliği olayı için callback ekle
    onStatusChange(callback) {
        if (typeof callback === 'function') {
            this.onStatusChangeCallbacks.push(callback);
        }
        return this;
    }
    
    // Mesajları işle
    _handleMessage(data) {
        // Callbacks'leri çağır
        for (const callback of this.onMessageCallbacks) {
            callback(data);
        }
    }
    
    // Durum değişikliklerini bildir
    _notifyStatusChange(status) {
        for (const callback of this.onStatusChangeCallbacks) {
            callback(status);
        }
    }
    
    // Bağlantıyı kapat
    disconnect() {
        if (this.ws && this.ws.readyState === WebSocket.OPEN) {
            this.ws.close(1000, 'İstemci tarafından kapatıldı');
        }
    }
}

// Kullanımı:
const chatClient = new RoomChatClient('ws://localhost:8000');

chatClient
    .onStatusChange(status => {
        console.log('Bağlantı durumu:', status);
        // UI'ı güncelle
    })
    .onMessage(data => {
        console.log('Mesaj alındı:', data);
        
        if (data.type === 'chat') {
            // Sohbet mesajını UI'da göster
            displayChatMessage(data);
        } else if (data.type === 'room_list') {
            // Oda listesini UI'da güncelle
            updateRoomList(data.rooms);
        } else if (data.type === 'room_members') {
            // Oda üyelerini UI'da göster
            updateRoomMembers(data.room_id, data.members);
        } else if (data.type === 'system') {
            // Sistem mesajını göster
            displaySystemMessage(data.message);
        }
    });

// Bağlantıyı başlat
chatClient.connect();

// Örnek fonksiyonlar:
function joinRoom() {
    const roomId = document.getElementById('roomId').value;
    chatClient.joinRoom(roomId);
}

function sendMessage() {
    const roomId = document.getElementById('activeRoom').value;
    const message = document.getElementById('messageInput').value;
    
    if (roomId && message) {
        chatClient.sendRoomMessage(roomId, message);
        document.getElementById('messageInput').value = '';
    }
}
```

### 6.2 JSON Veri Alışverişi: Yapılandırılmış İletişim

Modern web uygulamalarında, istemci ve sunucu arasında yapılandırılmış veri alışverişi için JSON formatı yaygın olarak kullanılır. WebSocket üzerinden JSON kullanımı, hem esnek hem de güçlü bir iletişim yöntemi sunar.

#### 6.2.1 Neden JSON Kullanmalıyız?

1. **Yapılandırılmış Veri**:
   - Metin tabanlı düz mesajların aksine, JSON nesneleri karmaşık veri yapılarını taşıyabilir
   - İç içe nesneler, diziler ve farklı veri tipleri desteklenir

2. **Mesaj Türlerini Ayırma**:
   - `type` alanı ekleyerek farklı mesaj kategorileri tanımlanabilir
   - Her mesaj türü için özel işleme mantığı uygulanabilir

3. **Veri Doğrulama**:
   - Şema doğrulama kütüphaneleri (Pydantic gibi) ile gelen verilerin yapısı kontrol edilebilir
   - Hatalı veya eksik verileri yakalamak kolaylaşır

4. **Genişletilebilirlik**:
   - Mevcut mesaj formatlarına yeni alanlar eklemek kolaydır
   - Geriye dönük uyumluluk sağlanabilir

#### 6.2.2 Pydantic ile JSON Şema Doğrulama

FastAPI'nin güçlü özelliklerinden biri olan Pydantic, WebSocket mesajlarını doğrulamak için de kullanılabilir:

```python
from pydantic import BaseModel, Field, validator
from typing import Optional, List, Union, Literal
from datetime import datetime
import json

# Temel mesaj modeli
class BaseMessage(BaseModel):
    type: str
    timestamp: datetime = Field(default_factory=datetime.now)

# Sohbet mesaj modeli
class ChatMessage(BaseModel):
    type: Literal["chat"] = "chat"
    room_id: str
    user_id: str
    username: str
    message: str
    timestamp: datetime = Field(default_factory=datetime.now)
    
    @validator('message')
    def message_not_empty(cls, v):
        if not v or not v.strip():
            raise ValueError('Mesaj boş olamaz')
        return v

# Oda işlemleri mesaj modeli
class RoomActionMessage(BaseModel):
    type: Literal["join_room", "leave_room"]
    room_id: str

# Sistem mesajı modeli
class SystemMessage(BaseModel):
    type: Literal["system"] = "system"
    message: str
    level: Literal["info", "warning", "error"] = "info"

# Mesaj türlerini birleştiren Union tipi
MessageType = Union[ChatMessage, RoomActionMessage, SystemMessage]

# Gelen JSON mesajını doğrulama
def validate_message(message_json: str) -> Optional[MessageType]:
    try:
        # JSON'ı dict'e dönüştür
        data = json.loads(message_json)
        
        # Mesaj türünü kontrol et
        message_type = data.get("type", "")
        
        if message_type == "chat":
            return ChatMessage(**data)
        elif message_type in ["join_room", "leave_room"]:
            return RoomActionMessage(**data)
        elif message_type == "system":
            return SystemMessage(**data)
        else:
            return None
    except json.JSONDecodeError:
        return None
    except Exception as e:
        print(f"Doğrulama hatası: {e}")
        return None

# WebSocket endpoint'inde kullanımı
@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    
    try:
        while True:
            data = await websocket.receive_text()
            
            # Mesajı doğrula
            valid_message = validate_message(data)
            
            if valid_message:
                if isinstance(valid_message, ChatMessage):
                    # Sohbet mesajı işleme
                    print(f"Sohbet mesajı: {valid_message.message}")
                    await websocket.send_text(valid_message.json())
                
                elif isinstance(valid_message, RoomActionMessage):
                    # Oda işlemi
                    action = "katılma" if valid_message.type == "join_room" else "ayrılma"
                    print(f"Oda {action} işlemi: {valid_message.room_id}")
                    
                    # Yanıt mesajı
                    response = SystemMessage(
                        message=f"{valid_message.room_id} odasına {action} işlemi başarılı"
                    )
                    await websocket.send_text(response.json())
                
                elif isinstance(valid_message, SystemMessage):
                    # Sistem mesajı
                    print(f"Sistem mesajı: {valid_message.message}")
                    await websocket.send_text(valid_message.json())
            else:
                # Geçersiz mesaj
                error_msg = SystemMessage(
                    message="Geçersiz mesaj formatı",
                    level="error"
                )
                await websocket.send_text(error_msg.json())
    
    except Exception as e:
        print(f"Hata: {e}")
```

#### 6.2.3 JSON Veri Tiplerinin Verimli Kullanımı

JSON formatı, çeşitli veri tiplerini destekler. WebSocket uygulamalarında bu tipleri etkili şekilde kullanmak için öneriler:

1. **Tip Belirleyicileri**:

   ```json
   {
     "type": "chat_message",
     "data": {
       "user": "Ali",
       "message": "Merhaba dünya"
     }
   }
   ```

   Bu yapı, mesaj işleme mantığınızı basitleştirir ve kodun okunabilirliğini artırır.

2. **Veri Normalleştirme**:

   ```json
   {
     "type": "user_list",
     "users": {
       "user_123": { "name": "Ali", "status": "online" },
       "user_456": { "name": "Ayşe", "status": "away" }
     }
   }
   ```

   Anahtar/değer yapısı, büyük veri setlerinde arama ve güncelleme işlemlerini hızlandırır.

3. **Sayfalandırma ve Parçalı Veri**:

   ```json
   {
     "type": "message_history",
     "room_id": "room_789",
     "page": 1,
     "total_pages": 5,
     "messages": [...]
   }
   ```

   Büyük veri kümeleri için, tüm veriyi tek seferde göndermek yerine sayfalandırma kullanın.

4. **Zaman Damgaları ve Sıralama**:

   ```json
   {
     "type": "chat_message",
     "timestamp": "2023-06-15T14:30:45.123Z",
     "sequence": 42,
     "data": { ... }
   }
   ```

   ISO 8601 formatında zaman damgaları ve sıra numaraları, mesaj sıralamasını garanti eder.

#### 6.2.4 İstemcide JSON İşleme

JavaScript istemcilerinde JSON verilerini işlemek için:

```javascript
// Mesaj tipleri
const MESSAGE_TYPES = {
    CHAT: 'chat',
    SYSTEM: 'system',
    JOIN_ROOM: 'join_room',
    LEAVE_ROOM: 'leave_room',
    USER_LIST: 'user_list',
    ERROR: 'error'
};

// Mesaj işleyici sınıfı
class MessageHandler {
    constructor() {
        this.handlers = {};
        
        // Her mesaj tipi için varsayılan boş işleyici
        Object.values(MESSAGE_TYPES).forEach(type => {
            this.handlers[type] = () => {};
        });
    }
    
    // Bir mesaj tipi için işleyici kaydet
    registerHandler(type, handler) {
        if (typeof handler === 'function') {
            this.handlers[type] = handler;
        }
        return this;
    }
    
    // Gelen mesajı işle
    handleMessage(messageData) {
        try {
            // String ise JSON olarak ayrıştır
            const data = typeof messageData === 'string' 
                ? JSON.parse(messageData) 
                : messageData;
            
            const type = data.type || 'unknown';
            
            // Bu tip için bir işleyici var mı?
            if (this.handlers[type]) {
                this.handlers[type](data);
            } else {
                console.warn(`'${type}' tipi için işleyici bulunamadı:`, data);
            }
        } catch (error) {
            console.error('Mesaj işleme hatası:', error);
        }
    }
}

// Kullanım örneği
const messageHandler = new MessageHandler();

// İşleyicileri kaydet
messageHandler
    .registerHandler(MESSAGE_TYPES.CHAT, (data) => {
        // Sohbet mesajını göster
        appendChatMessage(data.username, data.message, data.timestamp);
    })
    .registerHandler(MESSAGE_TYPES.SYSTEM, (data) => {
        // Sistem mesajını göster
        showSystemNotification(data.message, data.level);
    })
    .registerHandler(MESSAGE_TYPES.ERROR, (data) => {
        // Hata mesajını göster
        showError(data.message);
    })
    .registerHandler(MESSAGE_TYPES.USER_LIST, (data) => {
        // Kullanıcı listesini güncelle
        updateUserList(data.users);
    });

// WebSocket bağlantısı
const ws = new WebSocket('ws://example.com/ws');

ws.onmessage = (event) => {
    // Gelen mesajı işleyiciye yönlendir
    messageHandler.handleMessage(event.data);
};
```

### 6.3 WebSocket Sunucudan Proaktif Mesaj Gönderme

WebSocket'lerin en güçlü özelliklerinden biri, sunucunun istemcilere proaktif olarak mesaj gönderebilmesidir. Bu, gerçek zamanlı bildirimler, güncellemeler ve veri akışları için idealdir.

```python
import asyncio
import random
import datetime

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

# Uygulama başladığında periyodik mesaj gönderme görevini başlat
@app.on_event("startup")
async def startup():
    # Arka planda çalışacak bir görev olarak başlat
    asyncio.create_task(send_random_messages())
    print("Periyodik mesaj gönderme görevi başlatıldı")
```

## 6. En İyi Uygulamalar ve Sorun Giderme

### Güvenlik Önlemleri

1. **WSS (WebSocket Secure) Kullanımı**

   ```javascript
   // İstemci tarafı (HTTPS üzerinden güvenli bağlantı)
   var ws = new WebSocket("wss://example.com/ws");
   ```

2. **Kimlik Doğrulama**

   ```python
   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket, token: str = Query(...)):
       # Token doğrulama
       if not is_valid_token(token):
           await websocket.close(code=1008, reason="Unauthorized")
           return
       
       await websocket.accept()
       # ...
   ```

3. **Mesaj Doğrulama**

   ```python
   try:
       data = await websocket.receive_json()
       # JSON şemasını doğrula, zararlı içeriği filtrele
   except ValueError:
       await websocket.send_text("Geçersiz veri formatı")
   ```

### Yeniden Bağlanma Stratejileri

İstemci tarafında bağlantı kopması durumunda yeniden bağlanma:

```javascript
let socket;
let reconnectAttempts = 0;
const maxReconnectAttempts = 5;

function connectWebSocket() {
    socket = new WebSocket("ws://localhost:8000/ws");
    
    socket.onopen = () => {
        console.log("Bağlantı kuruldu");
        reconnectAttempts = 0;
    };
    
    socket.onclose = (event) => {
        console.log("Bağlantı kesildi", event.code);
        
        if (reconnectAttempts < maxReconnectAttempts) {
            const timeout = Math.min(1000 * Math.pow(2, reconnectAttempts), 30000);
            console.log(`${timeout}ms sonra yeniden bağlanılacak...`);
            
            setTimeout(() => {
                reconnectAttempts++;
                connectWebSocket();
            }, timeout);
        }
    };
    
    // Mesaj alma ve gönderme işlemleri
    socket.onmessage = (event) => {
        console.log("Mesaj alındı:", event.data);
    };
}

// İlk bağlantıyı başlat
connectWebSocket();
```

### Yaygın Hatalar ve Çözümleri

1. **Bağlantı Kurulamıyor**
   - `await websocket.accept()` çağrısının yapıldığından emin olun
   - CORS ayarlarını kontrol edin
   - Güvenlik duvarı ve port erişimlerini kontrol edin

2. **Mesajlar Alınamıyor**
   - `try-except` bloğunun varlığını kontrol edin
   - Mesaj formatını doğrulayın (text/json)
   - Bağlantının hala açık olduğunu kontrol edin

3. **Yüksek CPU Kullanımı**
   - Sonsuz döngülerde mutlaka `await` ifadesi olduğundan emin olun
   - Büyük mesajları işlerken verimliliğe dikkat edin

4. **Bellek Sızıntıları**
   - Bağlantı kesildiğinde `connected_clients` listesinden çıkardığınızdan emin olun
   - Büyük veri yapılarını temizleyin

### Performans İpuçları

1. **Mesaj Boyutunu Optimize Edin**
   - Gereksiz bilgileri göndermeyin
   - Büyük verileri parçalara bölün

2. **İşlemi Dağıtın**
   - Ağır işlemleri ayrı bir görev olarak çalıştırın

   ```python
   result = await asyncio.create_task(heavy_computation(data))
   ```

3. **Rate Limiting Uygulayın**

   ```python
   last_message_time = {}
   
   @app.websocket("/ws")
   async def websocket_endpoint(websocket: WebSocket):
       client_id = id(websocket)
       await websocket.accept()
       
       try:
           while True:
               # Hız sınırlama kontrolü
               current_time = time.time()
               if client_id in last_message_time:
                   time_diff = current_time - last_message_time[client_id]
                   if time_diff < 0.1:  # 100ms başına en fazla 1 mesaj
                       await asyncio.sleep(0.1 - time_diff)
               
               data = await websocket.receive_text()
               last_message_time[client_id] = time.time()
               
               # Mesajı işle...
       except:
           pass
   ```
