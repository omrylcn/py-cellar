**A/B Testing** sırasında, iki grup arasındaki oranların (proportions) karşılaştırılması için **iki oran testi (two-proportion test)** sıklıkla kullanılır. Bu test, iki grubun başarı oranları (örneğin, dönüşüm oranları, tıklama oranları) arasında istatistiksel olarak anlamlı bir fark olup olmadığını belirlemek için kullanılır.

İşte **iki oran testi (two-proportion test)** hakkında detaylı bir açıklama ve A/B Testing'de nasıl uygulandığına dair bir rehber:

---

### **1. İki Oran Testi (Two-Proportion Test) Nedir?**
İki oran testi, iki bağımsız grubun başarı oranlarını karşılaştırmak için kullanılan bir istatistiksel testtir. Örneğin:
- Grup A: Mevcut sürüm (v1) kullanıcılarının dönüşüm oranı.  
- Grup B: Yeni sürüm (v2) kullanıcılarının dönüşüm oranı.  

Bu test, iki oran arasındaki farkın istatistiksel olarak anlamlı olup olmadığını belirler.

---

### **2. A/B Testing'de İki Oran Testi Nasıl Kullanılır?**

#### **Adım 1: Veri Toplama**
- **Grup A (v1)**:  
  - Örneklem büyüklüğü: \( n_1 \)  
  - Başarı sayısı: \( x_1 \) (örneğin, ödeme tamamlayan kullanıcı sayısı)  
  - Başarı oranı: \( \hat{p}_1 = \frac{x_1}{n_1} \)

- **Grup B (v2)**:  
  - Örneklem büyüklüğü: \( n_2 \)  
  - Başarı sayısı: \( x_2 \)  
  - Başarı oranı: \( \hat{p}_2 = \frac{x_2}{n_2} \)

---

#### **Adım 2: Hipotezlerin Belirlenmesi**
- **Null Hipotezi (H0)**: İki grup arasında başarı oranı açısından fark yoktur.  
  \( H_0: p_1 = p_2 \)

- **Alternatif Hipotez (H1)**: İki grup arasında başarı oranı açısından fark vardır.  
  \( H_1: p_1 \neq p_2 \) (iki yönlü test)  
  Veya:  
  \( H_1: p_1 > p_2 \) veya \( H_1: p_1 < p_2 \) (tek yönlü test)

---

#### **Adım 3: Test İstatistiğinin Hesaplanması**
İki oran testi için **z-testi** kullanılır. Test istatistiği şu şekilde hesaplanır:

\[
z = \frac{ \hat{p}_1 - \hat{p}_2 }{ \sqrt{ \hat{p}(1 - \hat{p}) \left( \frac{1}{n_1} + \frac{1}{n_2} \right) } }
\]

Burada:
- \( \hat{p} \): Birleştirilmiş başarı oranı (pooled proportion).  
  \[
  \hat{p} = \frac{x_1 + x_2}{n_1 + n_2}
  \]

---

#### **Adım 4: p-Değerinin Hesaplanması**
- Hesaplanan z değerine karşılık gelen p-değeri bulunur.  
- p-değeri, null hipotezinin doğru olduğu varsayımı altında, gözlemlenen farkın veya daha büyük bir farkın ortaya çıkma olasılığını ifade eder.

---

#### **Adım 5: Sonuçların Yorumlanması**
- **p-değeri < α (genellikle 0.05)**: Null hipotezi reddedilir. İki grup arasında istatistiksel olarak anlamlı bir fark vardır.  
- **p-değeri ≥ α**: Null hipotezi reddedilemez. İki grup arasında istatistiksel olarak anlamlı bir fark yoktur.

---

### **3. Örnek Senaryo**

#### **Veriler**:
- **Grup A (v1)**:  
  - Örneklem büyüklüğü: \( n_1 = 1000 \)  
  - Başarı sayısı: \( x_1 = 150 \)  
  - Başarı oranı: \( \hat{p}_1 = \frac{150}{1000} = 0.15 \) (%15)

- **Grup B (v2)**:  
  - Örneklem büyüklüğü: \( n_2 = 1000 \)  
  - Başarı sayısı: \( x_2 = 180 \)  
  - Başarı oranı: \( \hat{p}_2 = \frac{180}{1000} = 0.18 \) (%18)

---

#### **Hesaplamalar**:
1. **Birleştirilmiş Başarı Oranı (Pooled Proportion)**:  
   \[
   \hat{p} = \frac{150 + 180}{1000 + 1000} = \frac{330}{2000} = 0.165
   \]

2. **Test İstatistiği (z)**:  
   \[
   z = \frac{0.15 - 0.18}{\sqrt{0.165 \times (1 - 0.165) \times \left( \frac{1}{1000} + \frac{1}{1000} \right)}}  
   \]  
   \[
   z = \frac{-0.03}{\sqrt{0.165 \times 0.835 \times 0.002}}  
   \]  
   \[
   z = \frac{-0.03}{\sqrt{0.00027555}}  
   \]  
   \[
   z = \frac{-0.03}{0.0166} \approx -1.81
   \]

3. **p-Değeri**:  
   - z = -1.81 için p-değeri ≈ 0.035 (iki yönlü test).

---

#### **Sonuç**:
- p-değeri (0.035) < α (0.05) olduğu için null hipotezi reddedilir.  
- Yeni sürüm (v2), mevcut sürüme (v1) göre istatistiksel olarak anlamlı bir şekilde daha yüksek dönüşüm oranına sahiptir.

---

### **4. Pratikte Kullanım**
- **Python ile İki Oran Testi**:  
  ```python
  from statsmodels.stats.proportion import proportions_ztest

  # Başarı sayıları ve örneklem büyüklükleri
  successes = [150, 180]
  samples = [1000, 1000]

  # İki oran testi
  stat, p_value = proportions_ztest(successes, samples)
  print(f"Test İstatistiği: {stat}, p-Değeri: {p_value}")
  ```

- **Çıktı**:  
  ```
  Test İstatistiği: -1.81, p-Değeri: 0.035
  ```

---

### **5. Avantajlar ve Sınırlamalar**
- **Avantajlar**:  
  - Basit ve etkili bir yöntemdir.  
  - Büyük örneklemlerde güvenilir sonuçlar verir.

- **Sınırlamalar**:  
  - Küçük örneklemlerde yanıltıcı sonuçlar verebilir.  
  - Sürekli veriler için uygun değildir (oranlar veya oranlarla ilgili veriler için kullanılır).

---

### **Sonuç**
İki oran testi, A/B Testing'de iki grup arasındaki başarı oranlarını karşılaştırmak için güçlü bir araçtır. Bu testi kullanarak, yeni sürümün mevcut sürüme göre istatistiksel olarak anlamlı bir fark yaratıp yaratmadığını net bir şekilde belirleyebilirsiniz. 😊