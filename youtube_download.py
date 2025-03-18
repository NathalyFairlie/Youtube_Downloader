from tkinter import *
from tkinter import filedialog, messagebox
import yt_dlp
import os
import threading
import subprocess
import time

# Cria a janela principal da aplicação
root = Tk()
root.configure(bg="lightgray")
root.geometry('500x420')
root.resizable(0, 0)
root.title("Download de Vídeos do YouTube")

# --- Seção para inserir o link do vídeo ---
link = StringVar()
Label(root, text='Cole o Link Aqui:', font='arial 15 bold').place(x=160, y=60)
link_enter = Entry(root, width=70, textvariable=link).place(x=32, y=90)

# --- Seção para selecionar o diretório de download ---
download_path = StringVar()
download_path.set(os.path.expanduser("~/Downloads"))

Label(root, text='Pasta de Download:', font='arial 15 bold').place(x=160, y=120)
path_entry = Entry(root, width=55, textvariable=download_path)
path_entry.place(x=32, y=150)

# --- Seção para selecionar o formato de download ---
download_format = StringVar()
download_format.set("video")

Label(root, text='Formato:', font='arial 15 bold').place(x=215, y=180)
Radiobutton(root, text="Vídeo (mp4)", variable=download_format, value="video", bg="lightgray", font='arial 12').place(x=140, y=210)
Radiobutton(root, text="Áudio (MP3)", variable=download_format, value="audio", bg="lightgray", font='arial 12').place(x=260, y=210)

# --- Função para abrir a caixa de diálogo de seleção de diretório ---
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)

# Cria um botão para procurar pastas
browse_button = Button(root, text="Procurar", font='arial 10 bold', bg="lightblue", command=browse_folder)
browse_button.place(x=400, y=150)

# --- Seção para exibir o status do download ---
status_label = Label(root, text="", font='arial 12')
status_label.place(x=50, y=310)
status_label.config(wraplength=400)

# --- Função para forçar a data de modificação do arquivo ---
def force_file_date(file_path):
    """Força a data de modificação do arquivo para a data atual"""
    if not file_path or not os.path.exists(file_path):
        return False
    
    try:
        current_time = time.time()
        os.utime(file_path, (current_time, current_time))
        return True
    except Exception as e:
        print(f"Erro ao atualizar a data do arquivo: {str(e)}")
        return False

# --- Função para realizar o download ---
def download_thread():
    url = str(link.get())
    if not url:
        status_label.config(text="Por favor, insira uma URL válida")
        return

    try:
        status_label.config(text="Iniciando download...")
        root.update()

        save_path = download_path.get()
        format_choice = download_format.get()
        downloaded_file = None

        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'verbose': True,
            'updatetime': False
        }

        def my_hook(d):
            nonlocal downloaded_file
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%')
                status_label.config(text=f"Baixando: {p}")
                root.update()
            elif d['status'] == 'finished':
                downloaded_file = d['filename']
                status_label.config(text="Download concluído. Processando arquivo...")
                root.update()
                force_file_date(downloaded_file)

        ydl_opts['progress_hooks'] = [my_hook]

        if format_choice == "audio":
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': '192',
                }],
                'noplaylist': True,
            })
            status_label.config(text="Preparando para baixar áudio (MP3)...")
        else:
            ydl_opts.update({
                'format': 'best',
            })
            status_label.config(text="Preparando para baixar vídeo...")

        root.update()

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)
            title = info.get('title', 'Arquivo')
            status_label.config(text=f"Baixando: {title}...")
            root.update()
            ydl.download([url])

        status_label.config(text="DOWNLOAD CONCLUÍDO!")

    except Exception as e:
        status_label.config(text=f"ERRO: {str(e)}")
        print(f"Erro detalhado: {str(e)}")

# Função para iniciar o download em uma thread separada
def Downloader():
    threading.Thread(target=download_thread, daemon=True).start()

# Cria um botão "DOWNLOAD" que chama a função Downloader quando clicado
Button(root, text='DOWNLOAD', font='arial 15 bold', bg="lightblue", padx=2, command=Downloader).place(x=180, y=240)

# Inicia o loop principal da aplicação
root.mainloop()