# karışık notlar

### article - 1

RabbitMQ, genelde aşağıdaki gibi temel kavramlar etrafında işler:

Producer (Üretici): Mesajları RabbitMQ'ya gönderen uygulama veya servislerdir.
Queue (Kuyruk): Mesajların depolandığı ve beklediği yerdir. Kuyruklar, üreticilerden gelen mesajları alır ve bunları işlemek için tüketicilere dağıtır.
Consumer (Tüketici): Kuyruklardan mesajları alan ve bu mesajları işleyen uygulama veya servislerdir.
Exchange (Değişim): Üreticilerden gelen mesajları alır ve belirli bir kuyruğa yönlendirir.

Exchange (Değişim) türleri, RabbitMQ'da mesajların nasıl yönlendirileceğini belirler. Bu türler, yayılma algoritmalarını ve kuyruklara iletilen mesajların nasıl yönlendirileceğini tanımlar. İşte bazı yaygın Exchange türleri:

Direct Exchange (Doğrudan Değişim): Bu tür, mesajları bir kuyruğa yönlendirmek için bir anahtar kullanır. Üretici, mesajı bir anahtarla etiketler ve bu anahtara sahip kuyruğa iletilir. Bu şekilde, mesajlar doğrudan belirli kuyruklara yönlendirilir.
Fanout Exchange (Yayın Değişimi): Bu tür, bir mesajı aldığında, o mesajı bağlı tüm kuyruklara kopyalar. Yani, Fanout Exchange, mesajı alır ve tüm kuyruklara iletir. Bu, geniş dağıtım ve yayınlama senaryoları için idealdir.
Topic Exchange (Konu Değişimi): Bu tür, mesajların bir veya daha fazla kuyruğa yönlendirilmesini sağlayan esnek bir mekanizma sunar. Mesajların belirli konulara (örneğin, "haber", "finans", "spor" gibi) göre yönlendirilmesini sağlar. Tüketiciler, kuyrukları belirli konulara abone olarak ilgili mesajları alabilirler.
Headers Exchange (Başlık Değişimi): Bu tür, mesajları bir dizi başlık/anahtar çiftine göre yönlendirir. Başlık ve anahtarlar, mesajlarla ilişkilendirilir ve kuyruklar bu başlıkların kombinasyonlarına göre eşleşir.

- https://www.linkedin.com/pulse/rabbitmq-nedir-%C3%B6zg%C3%BCr-sar%C4%B1kaya-h0sqf/

### article - 2
RabbitMQ mesaj kuyruğu (message queue) sistemidir. Yazdığımız programımız üzerinden yapılacak asenkron (asynchronous) işlemleri sıraya koyup, bunları sırayla kuyruktan çekip gerçekleyerek ilerleyen ölçeklenebilir ve performanslı bir sistemdir. RabbitMQ kullanımına potansiyel bir örnek verecek olursak, bulk mail gönderme işlemlerini Server’ı yormayacak bir sisteme çevirmek için RabbitMQ kullanabilirsiniz. RabbitMQ bir çok yazılım diline destek vermektedir, bir çok işletim sistemi üzerinde çalışabilmektedir ve open source’dur.

RabbitMQ Exchange ve Queue içerisinde barındıran yapıdır. Publish ve Receiver’ı ise biz oluşturuyoruz.

Publisher: Verinin RabbitMQ’ye gönderildiği yer.
Receiver: RabbitMQ Publisher’ları sıraya koyup ilgili Receiver’lara iletiyor.
Routing key: mesajlarımızı ilgili yerlere göndermek için eklediğimiz anahtar kelimeler, etiketler.
Exchange: Bu anahtar kelimelere göre ilgili kuyruğa veriyi göndermemizi sağlayan araçtır.
Queue: Görevi, Consumer’lara (receiver) verileri teker teker göndermek.
Channels: Publish ve Consumes kısımlarına channel denir.
Exchange Type: Route key’e göre belirli Queue’lara belirli verileri iletmek Exhange’in göreviydi. Peki exchange type nedir? Gelin buna birlikte göz atalım.


- https://furkangulsen.medium.com/rabbitmq-nedir-neden-kullanilir-73f319ba9a94


### article - 3

Şimdi sıra geldi RabbitMQ’nun çalışma mantığına ve bilinmesi gereken bazı terimlerine:

Producer: Mesajı atan kaynak yani uygulamadır. Redis’deki Pub/Sub düşünüldüğünde Publisher tarafıdır.
Queue : Gönderilen mesajlar alıcaya ulaştırılmadan önce bir sıraya konur. Gelen yoğunluğa göre veya alıcıya erişilemediği durumlarda, gelen tüm mesajlar Queue’de yani memory’de saklanır. Eğer bu süreç uzun sürer ise memory şişebilir. Ayrıca server’ın restart edilmesi durumunda ilgili mesajlar kaybolabilir.
Consumer: Gönderilen mesajı karşılayan sunucudur. Yani Redis Pub/Sub’daki Subscribe’dır. Kısaca ilgili kuyruğu(Queue)’yu dinleyen taraftır.
Fifo: RabbitMQ’da giden mesajların işlem sırası first in first out yani ilk giren ilk çıkar şeklindedir.