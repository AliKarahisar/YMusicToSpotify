import tkinter as tk
from tkinter import ttk, messagebox
import threading
import requests
import json
from io import BytesIO
from PIL import Image, ImageTk
from spotipy.oauth2 import SpotifyOAuth
import spotipy
from googleapiclient.discovery import build
import os

CONFIG_FILE = "config.json"
LOCALES_DIR = "locales"

# Dil verileri için küresel değişken
i18n = {}


def load_config():
    try:
        with open(CONFIG_FILE, "r") as file:
            return json.load(file)
    except FileNotFoundError:
        return {}


def save_config(data):
    with open(CONFIG_FILE, "w") as file:
        json.dump(data, file)


def load_locale(language):
    global i18n
    try:
        with open(os.path.join(LOCALES_DIR, f"{language}.json"), "r", encoding="utf-8") as file:
            i18n = json.load(file)
    except FileNotFoundError:
        i18n = {}


def t(key):
    return i18n.get(key, key)


def authenticate_youtube(api_key):
    return build("youtube", "v3", developerKey=api_key)


def authenticate_spotify(client_id, client_secret, redirect_uri):
    return spotipy.Spotify(auth_manager=SpotifyOAuth(
        client_id=client_id,
        client_secret=client_secret,
        redirect_uri=redirect_uri,
        scope="playlist-modify-public"
    ))


def get_youtube_playlist_details(youtube, playlist_id):
    response = youtube.playlists().list(part="snippet", id=playlist_id).execute()
    if "items" in response and response["items"]:
        playlist = response["items"][0]
        title = playlist["snippet"]["title"]
        thumbnail_url = playlist["snippet"]["thumbnails"]["high"]["url"]
        return title, thumbnail_url
    raise ValueError(t("invalid_youtube_playlist_id"))


def get_youtube_playlist_tracks(youtube, playlist_id):
    tracks = []
    request = youtube.playlistItems().list(part="snippet", playlistId=playlist_id, maxResults=50)
    while request:
        response = request.execute()
        for item in response["items"]:
            title = item["snippet"]["title"]
            description = item["snippet"].get("description", "")
            tracks.append((title, description))
        request = youtube.playlistItems().list_next(request, response)
    return tracks


def create_spotify_playlist(sp, user_id, playlist_name, track_details, progress_callback):
    playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=True)
    playlist_id = playlist["id"]

    total_tracks = len(track_details)
    for index, (title, description) in enumerate(track_details, start=1):
        query = title

        # Sanatçı veya albüm bilgilerini tahmin etmeye çalışıyoruz
        if "-" in title:
            parts = title.split("-")
            if len(parts) >= 2:
                artist = parts[0].strip()
                track_name = parts[1].strip()
                query = f"track:{track_name} artist:{artist}"

        results = sp.search(q=query, limit=1, type="track")
        if results["tracks"]["items"]:
            track_id = results["tracks"]["items"][0]["id"]
            sp.playlist_add_items(playlist_id, [track_id])
        progress_callback(index, total_tracks, title)
    return playlist_id


class App:
    def __init__(self, root):
        self.root = root
        self.root.title("YMusicToSpotify by Ali Karahisar")
        self.root.resizable(False, False)  # Disable resizing
        self.center_window(700, 450)  # Uygulama başlangıcında ortala

        self.config = load_config()
        self.language = self.config.get("language", "en")
        load_locale(self.language)

        self.menu = tk.Menu(self.root)
        self.menu.add_command(label=t("settings"), command=self.open_settings)
        self.root.config(menu=self.menu)

        self.create_main_ui()

    def ensure_event_focus(self):
        def focus_fix(event):
            self.root.focus_force()

        self.root.bind("<Button-1>", focus_fix)  # Tıklama ile pencere odaklanmasını sağla
        self.root.bind("<Motion>", focus_fix)  # Fare hareketi ile pencere odaklanmasını kontrol et

    def center_window(self, width, height):
        screen_width = self.root.winfo_screenwidth()
        screen_height = self.root.winfo_screenheight()
        x = (screen_width - width) // 2
        y = (screen_height - height) // 2
        self.root.geometry(f"{width}x{height}+{x}+{y}")

    def ensure_event_focus(self):
        def focus_fix(event):
            self.root.focus_force()
            self.root.update_idletasks()  # Değişiklikleri uygula

        self.root.bind("<Button-1>", focus_fix)
        self.root.bind("<Motion>", focus_fix)

    def create_main_ui(self):
        self.frame = tk.Frame(self.root, padx=10, pady=10)
        self.frame.pack(fill="both", expand=True)

        tk.Label(self.frame, text=t("playlist_name"), anchor="w").grid(row=0, column=0, sticky="w")
        self.playlist_name_entry = tk.Entry(self.frame, width=40)
        self.playlist_name_entry.grid(row=0, column=1, pady=5)

        tk.Label(self.frame, text=t("youtube_playlist_id"), anchor="w").grid(row=1, column=0, sticky="w")
        self.playlist_id_entry = tk.Entry(self.frame, width=40)
        self.playlist_id_entry.grid(row=1, column=1, pady=5)

        self.fetch_button = tk.Button(self.frame, text=t("fetch_details"), command=self.fetch_playlist_details)
        self.fetch_button.grid(row=1, column=2, padx=5)

        self.settings_button = tk.Button(self.frame, text=t("settings"), command=self.open_settings)
        self.settings_button.grid(row=0, column=2, padx=5)

        self.thumbnail_label = tk.Label(self.frame)
        self.thumbnail_label.grid(row=2, column=1, pady=10)

        self.transfer_button = tk.Button(self.frame, text=t("transfer_to_spotify"),
                                         command=self.start_transfer_playlist, state="disabled")
        self.transfer_button.grid(row=3, column=1, pady=5)

        self.progress = ttk.Progressbar(self.frame, orient="horizontal", length=300, mode="determinate")
        self.progress.grid(row=4, column=1, pady=5)

        self.status_label = tk.Label(self.frame, text=t("status_waiting"), anchor="w")
        self.status_label.grid(row=5, column=0, columnspan=3, sticky="w")

    def update_ui_texts(self):
        """Uygulama içindeki metinleri seçilen dile göre günceller."""
        self.root.title(t("app_title"))
        self.menu.entryconfig(0, label=t("settings"))

        # Çerçevedeki bileşenlerin metinlerini güncelle
        for widget in self.frame.winfo_children():
            if isinstance(widget, tk.Label):
                if widget.cget("text") in i18n.values():  # Eski metni değiştir
                    key = [k for k, v in i18n.items() if v == widget.cget("text")][0]
                    widget.config(text=t(key))
            elif isinstance(widget, tk.Button):
                text = widget.cget("text")
                if text in i18n.values():  # Eski metni değiştir
                    key = [k for k, v in i18n.items() if v == text][0]
                    widget.config(text=t(key))

        # Özel durumlar: Durum etiketi ve dinamik metinler
        self.status_label.config(text=t("status_waiting"))
        self.fetch_button.config(text=t("fetch_details"))
        self.settings_button.config(text=t("settings"))
        self.transfer_button.config(text=t("transfer_to_spotify"))

    def open_settings(self):
        settings_window = tk.Toplevel(self.root)
        settings_window.title(t("settings"))
        settings_window.resizable(False, False)

        tk.Label(settings_window, text=t("youtube_api_key"), anchor="w").grid(row=0, column=0, sticky="w")
        youtube_api_entry = tk.Entry(settings_window, width=40)
        youtube_api_entry.insert(0, self.config.get("youtube_api_key", ""))
        youtube_api_entry.grid(row=0, column=1, pady=5)

        tk.Label(settings_window, text=t("spotify_client_id"), anchor="w").grid(row=1, column=0, sticky="w")
        spotify_client_id_entry = tk.Entry(settings_window, width=40)
        spotify_client_id_entry.insert(0, self.config.get("spotify_client_id", ""))
        spotify_client_id_entry.grid(row=1, column=1, pady=5)

        tk.Label(settings_window, text=t("spotify_client_secret"), anchor="w").grid(row=2, column=0, sticky="w")
        spotify_client_secret_entry = tk.Entry(settings_window, width=40)
        spotify_client_secret_entry.insert(0, self.config.get("spotify_client_secret", ""))
        spotify_client_secret_entry.grid(row=2, column=1, pady=5)

        tk.Label(settings_window, text=t("language"), anchor="w").grid(row=3, column=0, sticky="w")
        language_options = ["en", "tr"]
        language_var = tk.StringVar(value=self.language)
        language_menu = ttk.Combobox(settings_window, textvariable=language_var, values=language_options,
                                     state="readonly")
        language_menu.grid(row=3, column=1, pady=5)

        def save_settings():
            self.config["youtube_api_key"] = youtube_api_entry.get()
            self.config["spotify_client_id"] = spotify_client_id_entry.get()
            self.config["spotify_client_secret"] = spotify_client_secret_entry.get()
            self.config["language"] = language_var.get()
            save_config(self.config)
            load_locale(language_var.get())
            self.language = language_var.get()
            self.update_ui_texts()
            messagebox.showinfo(t("info"), t("settings_saved"))
            settings_window.destroy()


        save_button = tk.Button(settings_window, text=t("save"), command=save_settings)
        save_button.grid(row=4, column=0, columnspan=2, pady=10)

    def fetch_playlist_details(self):
        playlist_id = self.playlist_id_entry.get().strip()
        if not playlist_id:
            messagebox.showerror(t("error"), t("empty_playlist_id"))
            return

        youtube_api_key = self.config.get("youtube_api_key")
        if not youtube_api_key:
            messagebox.showerror(t("error"), t("missing_youtube_api_key"))
            return

        try:
            youtube = authenticate_youtube(youtube_api_key)
            title, thumbnail_url = get_youtube_playlist_details(youtube, playlist_id)

            response = requests.get(thumbnail_url)
            image = Image.open(BytesIO(response.content)).resize((200, 200))
            self.thumbnail_image = ImageTk.PhotoImage(image)
            self.thumbnail_label.config(image=self.thumbnail_image)

            self.playlist_name_entry.delete(0, tk.END)
            self.playlist_name_entry.insert(0, title)

            self.transfer_button.config(state="normal")
        except Exception as e:
            messagebox.showerror(t("error"), f"{t('fetch_playlist_error')}: {e}")

    def start_transfer_playlist(self):
        thread = threading.Thread(target=self.transfer_playlist)
        thread.start()

    def transfer_playlist(self):
        youtube_api_key = self.config.get("youtube_api_key")
        spotify_client_id = self.config.get("spotify_client_id")
        spotify_client_secret = self.config.get("spotify_client_secret")

        if not all([youtube_api_key, spotify_client_id, spotify_client_secret]):
            messagebox.showerror(t("error"), t("missing_api_keys"))
            return

        playlist_id = self.playlist_id_entry.get().strip()
        playlist_name = self.playlist_name_entry.get().strip()
        if not playlist_id or not playlist_name:
            messagebox.showerror(t("error"), t("empty_playlist_details"))
            return

        try:
            self.status_label.config(text=t("status_fetching_youtube"))
            youtube = authenticate_youtube(youtube_api_key)
            tracks = get_youtube_playlist_tracks(youtube, playlist_id)

            self.status_label.config(text=t("status_creating_spotify"))
            sp = authenticate_spotify(spotify_client_id, spotify_client_secret, "http://localhost:8888/callback")
            user_id = sp.current_user()["id"]

            def update_progress(current, total, track):
                self.progress["value"] = (current / total) * 100
                self.status_label.config(text=f"{t('status_transfer_progress')}: {current}/{total} - {track}")

            create_spotify_playlist(sp, user_id, playlist_name, tracks, update_progress)
            self.status_label.config(text=t("status_completed"))
        except Exception as e:
            messagebox.showerror(t("error"), f"{t('transfer_error')}: {e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()