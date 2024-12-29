# YMusicToSpotify 🎵  
**YouTube Müzik Çalma Listelerinizi Spotify’a Kolayca Taşıyın**

**Easily Transfer Your YouTube Music Playlists to Spotify**

## Özellikler | Features  
- **YouTube Çalma Listesi Aktarımı:** YouTube çalma listelerini hızlıca Spotify'a aktarın.  
  **YouTube Playlist Transfer:** Transfer your YouTube playlists to Spotify effortlessly.  
- **Otomatik Şarkı Eşleştirme:** Şarkı başlıklarını analiz ederek en iyi eşleşmeyi bulur.  
  **Automatic Track Matching:** Analyzes song titles for the best match.  
- **Çok Dilli Destek:** İngilizce ve Türkçe dil seçenekleri mevcut.  
  **Language Support:** Offers English and Turkish options.  
- **Durum ve İlerleme Takibi:** Aktarım sırasında ilerleme çubuğu ile bilgi alabilirsiniz.  
  **Status and Progress Tracking:** Track the transfer progress with a status bar.  

---

## Kurulum | Installation  

### Gereksinimler | Requirements  
- Python 3.8 veya üzeri  
  **Python 3.8 or above**  
- Aşağıdaki kütüphaneler:  
  - `tkinter`  
  - `spotipy`  
  - `google-api-python-client`  
  - `Pillow`  

### Adımlar | Steps  
1. Bu projeyi klonlayın:  
   **Clone this project:**  
   ```bash  
   git clone https://github.com/kullaniciadi/YMusicToSpotify.git  
   cd YMusicToSpotify  
   ```  

2. Gereksinimleri yükleyin:  
   **Install dependencies:**  
   ```bash  
   pip install -r requirements.txt  
   ```  

3. `config.json` dosyasını oluşturun ve YouTube API Anahtarı, Spotify Client ID ve Client Secret bilgilerinizi girin:  
   **Create the `config.json` file and add your YouTube API Key, Spotify Client ID, and Client Secret:**  
   ```json  
   {  
       "youtube_api_key": "YOUR_YOUTUBE_API_KEY",  
       "spotify_client_id": "YOUR_SPOTIFY_CLIENT_ID",  
       "spotify_client_secret": "YOUR_SPOTIFY_CLIENT_SECRET",  
       "language": "en"  
   }  
   ```  

4. Uygulamayı çalıştırın:  
   **Run the application:**  
   ```bash  
   python YoutubeMusicToSpotify.py  
   ```  

---

## Kullanım | Usage  
1. Uygulamayı başlatın ve **Ayarlar** butonuna tıklayarak API bilgilerinizi girin.  
   **Launch the application and click the "Settings" button to enter your API details.**  

2. YouTube çalma listesi kimliğinizi ve Spotify için istediğiniz çalma listesi adını girin.  
   **Enter your YouTube playlist ID and the desired Spotify playlist name.**  

3. "Detayları Getir" butonuna tıklayın. Çalma listesi bilgileri kontrol edilir ve önizleme sunulur.  
   **Click "Fetch Details." Playlist details will be validated and previewed.**  

4. "Spotify’a Aktar" butonuna basarak aktarımı başlatın.  
   **Click "Transfer to Spotify" to start the transfer.**  

---

## Katkıda Bulunma | Contributing  
Katkıda bulunmak için lütfen bir `pull request` gönderin.  
**Feel free to submit a `pull request` for contributions.**  

---

## Lisans | License  
MIT Lisansı altında lisanslanmıştır.  
**Licensed under the MIT License.**