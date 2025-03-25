from tkinter import *  # Importa todas as funções do Tkinter
from tkinter import filedialog, messagebox, ttk  # Importa componentes específicos
import yt_dlp  # Biblioteca para baixar vídeos do YouTube
import os  # Módulo para manipulação de arquivos e diretórios
import threading  # Para rodar o download em uma thread separada
import time  # Para manipulação de tempo


root = Tk()  # Cria a janela principal
root.configure(bg="lightgray")  # Define a cor de fundo
root.geometry('500x600')  # Define o tamanho da janela
root.resizable(0, 0)  # Impede o redimensionamento
root.title("Download de Vídeos do YouTube")  # Define o título da janela



# Variável que armazena o link do vídeo
link = StringVar()  
Label(root, text='Cole o Link Aqui:', font='arial 15 bold').place(x=160, y=60)
link_enter = Entry(root, width=70, textvariable=link).place(x=32, y=90)


# Define pasta padrão como Downloads
download_path = StringVar()
download_path.set(os.path.expanduser("~/Downloads"))

Label(root, text='Pasta de Download:', font='arial 15 bold').place(x=160, y=120)
path_entry = Entry(root, width=55, textvariable=download_path)
path_entry.place(x=32, y=150)

# O botão "Procurar" abre um seletor de pastas para escolher onde salvar o vídeo.
browse_button = Button(root, text="Procurar", font='arial 10 bold', bg="lightblue", command=lambda: browse_folder())
browse_button.place(x=400, y=150)

# O usuário escolhe entre baixar um vídeo (MP4) ou apenas o áudio (MP3).
download_format = StringVar()
download_format.set("video")

Label(root, text='Formato:', font='arial 15 bold').place(x=215, y=180)
Radiobutton(root, text="Vídeo (mp4)", variable=download_format, value="video", bg="lightgray", font='arial 12').place(x=140, y=210)
Radiobutton(root, text="Áudio (MP3)", variable=download_format, value="audio", bg="lightgray", font='arial 12').place(x=260, y=210)

# Cria uma lista suspensa para escolher a qualidade do vídeo.
video_quality_options = [
    '1080p',
    '720p',
    '480p',
    '360p',
    '240p'
]
video_quality = StringVar()
video_quality.set('480p')


video_quality_label = Label(root, text='Qualidade do Vídeo:', font='arial 15 bold')
video_quality_frame = Frame(root, bg="lightgray")
video_quality_dropdown = ttk.Combobox(video_quality_frame, 
                                       textvariable=video_quality, 
                                       values=video_quality_options, 
                                       width=25, 
                                       state="readonly")
video_quality_dropdown.current(2)  # Default 
video_quality_dropdown.pack(expand=True, fill=BOTH)

# Se o usuário escolher MP3, ele pode selecionar a qualidade/Bitrate do áudio.
bitrate_options = [
    '48 kbps', 
    '96 kbps', 
    '128 kbps', 
    '192 kbps', 
    '256 kbps', 
    '320 kbps'
]
audio_bitrate = StringVar()
audio_bitrate.set('192 kbps')  # Default 


bitrate_label = Label(root, text='Qualidade do Audio:', font='arial 15 bold')
bitrate_frame = Frame(root, bg="lightgray")
bitrate_dropdown = ttk.Combobox(bitrate_frame, 
                                 textvariable=audio_bitrate, 
                                 values=bitrate_options, 
                                 width=15, 
                                 state="readonly")
bitrate_dropdown.current(3)  # Default
bitrate_dropdown.pack(expand=True, fill=BOTH)

# Exibir Opções Apropriadas com Base na Escolha do Formato
def toggle_sections(*args):
    if download_format.get() == "audio":
        # Mostra qualidade do audio, esconde qualidade do video
        bitrate_label.place(x=160, y=250)
        bitrate_frame.place(x=140, y=280, width=220, height=40)
        video_quality_label.place_forget()
        video_quality_frame.place_forget()
    else:
        # Mostra qualidade do video, qualidade do audio
        video_quality_label.place(x=160, y=250)
        video_quality_frame.place(x=140, y=280, width=220, height=40)
        bitrate_label.place_forget()
        bitrate_frame.place_forget()

# Adicionar observador para mudanças no formato de download.
download_format.trace('w', toggle_sections)

# Rótulo de Status
status_label = Label(root, text="", font='arial 12')
status_label.place(x=50, y=450)
status_label.config(wraplength=400)

# Função para abrir o explorador de arquivos para selecionar onde salvar os downloads.
def browse_folder():
    folder = filedialog.askdirectory()
    if folder:
        download_path.set(folder)

# Atualiza a data de modificação do arquivo baixado
def force_file_date(file_path):
    """Força a data de modificação do arquivo para o tempo atual."""
    if not file_path or not os.path.exists(file_path):
        return False
    
    try:
        current_time = time.time()
        os.utime(file_path, (current_time, current_time))
        return True
    except Exception as e:
        print(f"Erro ao atualizar a data do arquivo: {str(e)}")
        return False

# Valida se o link foi inserido antes de iniciar o download.
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
        
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),
            'verbose': True,
            'updatetime': False
        }

        def my_hook(d):
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
            # Configuração de Download de audio
            selected_bitrate = audio_bitrate.get().split()[0]
            ydl_opts.update({
                'format': 'bestaudio/best',
                'postprocessors': [{
                    'key': 'FFmpegExtractAudio',
                    'preferredcodec': 'mp3',
                    'preferredquality': selected_bitrate,
                }],
                'noplaylist': True,
            })
            status_label.config(text=f"Preparando para baixar áudio (MP3 - {selected_bitrate} kbps)...")
        else:
            # Configuração de Download de Video
            quality = video_quality.get()
            
            # Mapear a seleção de qualidade para códigos de formato específicos.
            if quality == 'Melhor Qualidade Disponível':
                ydl_opts['format'] = 'best'
            else:
                # Especificar preferência de resolução com alternativa.
                resolution_map = {
                    '1080p': 'bestvideo[height<=1080]+bestaudio/best[height<=1080]',
                    '720p': 'bestvideo[height<=720]+bestaudio/best[height<=720]',
                    '480p': 'bestvideo[height<=480]+bestaudio/best[height<=480]',
                    '360p': 'bestvideo[height<=360]+bestaudio/best[height<=360]',
                    '240p': 'bestvideo[height<=240]+bestaudio/best[height<=240]'
                }
                ydl_opts['format'] = resolution_map.get(quality, 'best')
            
            status_label.config(text=f"Preparando para baixar vídeo ({quality})...")

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

# Função para iniciar o download em uma thread separada.
def Downloader():
    threading.Thread(target=download_thread, daemon=True).start()

# Botão de Download
Button(root, text='DOWNLOAD', font='arial 15 bold', bg="lightblue", padx=2, command=Downloader).place(x=180, y=350)

# Configuração inicial da seção.
toggle_sections()

# Iniciar o loop principal da aplicação.
root.mainloop()