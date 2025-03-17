import tkinter as tk  # Importa o módulo tkinter com o alias tk para criar a interface gráfica
from tkinter import filedialog, messagebox  # Importa módulos para seleção de arquivos e mensagens
import yt_dlp  # Importa a biblioteca yt-dlp para download de vídeos e áudios
import os  # Importa o módulo os para interagir com o sistema operacional
import subprocess  # Importa o módulo subprocess para executar comandos externos
import threading  # Importa o módulo threading para executar tarefas em paralelo

def create_gui():
    """Cria a janela principal da interface gráfica."""
    root = tk.Tk()  # Cria a janela principal
    root.configure(bg="lightgray")  # Define a cor de fundo da janela
    root.geometry('500x420')  # Define o tamanho da janela
    root.resizable(0, 0)  # Impede o redimensionamento da janela
    root.title("Download de Vídeos do YouTube")  # Define o título da janela
    return root  # Retorna a janela criada

def create_link_section(root, link):
    """Cria a seção para inserir o link do vídeo."""
    tk.Label(root, text='Cole o Link Aqui:', font='arial 15 bold').place(x=160, y=60)  # Cria um rótulo
    tk.Entry(root, width=70, textvariable=link).place(x=32, y=90)  # Cria uma caixa de entrada para o link

def create_download_path_section(root, download_path):
    """Cria a seção para selecionar o diretório de download."""
    download_path.set(os.path.expanduser("~/Downloads"))  # Define o diretório padrão como "Downloads"
    tk.Label(root, text='Pasta de Download:', font='arial 15 bold').place(x=160, y=120)  # Cria um rótulo
    path_entry = tk.Entry(root, width=55, textvariable=download_path)  # Cria uma caixa de entrada para o caminho
    path_entry.place(x=32, y=150)  # Posiciona a caixa de entrada
    return path_entry  # Retorna a caixa de entrada

def create_format_section(root, download_format):
    """Cria a seção para selecionar o formato de download (vídeo ou áudio)."""
    download_format.set("video")  # Define o formato padrão como vídeo
    tk.Label(root, text='Formato:', font='arial 15 bold').place(x=215, y=180)  # Cria um rótulo
    tk.Radiobutton(root, text="Vídeo (mp4)", variable=download_format, value="video", bg="lightgray", font='arial 12').place(x=140, y=210)  # Cria um botão de rádio para vídeo
    tk.Radiobutton(root, text="Áudio (MP3)", variable=download_format, value="audio", bg="lightgray", font='arial 12').place(x=250, y=210)  # Cria um botão de rádio para áudio

def browse_folder(download_path):
    """Abre uma caixa de diálogo para selecionar o diretório de download."""
    folder = filedialog.askdirectory()  # Abre a caixa de diálogo
    if folder:  # Se um diretório foi selecionado
        download_path.set(folder)  # Define o caminho selecionado

def create_browse_button(root, download_path):
    """Cria o botão "Procurar" para selecionar o diretório."""
    browse_button = tk.Button(root, text="Procurar", font='arial 10 bold', bg="lightblue", command=lambda: browse_folder(download_path))  # Cria o botão
    browse_button.place(x=400, y=150)  # Posiciona o botão

def create_status_label(root):
    """Cria o rótulo para exibir o status do download."""
    status_label = tk.Label(root, text="", font='arial 12')  # Cria o rótulo
    status_label.place(x=50, y=310)  # Posiciona o rótulo
    status_label.config(wraplength=400)  # Define o comprimento máximo do texto
    return status_label  # Retorna o rótulo

def convert_to_mp3(input_file):
    """Converte um arquivo webm para mp3 usando pydub."""
    try:
        from pydub import AudioSegment  # Importa o módulo AudioSegment de pydub
        base_name = os.path.splitext(input_file)[0]  # Obtém o nome base do arquivo
        output_file = base_name + ".mp3"  # Define o nome do arquivo de saída
        audio = AudioSegment.from_file(input_file)  # Carrega o arquivo de áudio
        audio.export(output_file, format="mp3")  # Exporta para mp3
        os.remove(input_file)  # Remove o arquivo original
        return output_file  # Retorna o caminho do arquivo convertido
    except Exception as e:
        print(f"Erro na conversão: {str(e)}")  # Imprime erros de conversão
        return None  # Retorna None em caso de erro

def download_thread(link, download_path, download_format, status_label, root):
    """Executa o download do vídeo ou áudio em uma thread separada."""
    url = str(link.get())  # Obtém o link do vídeo
    if not url:  # Se o link estiver vazio
        status_label.config(text="Por favor, insira uma URL válida")  # Exibe mensagem de erro
        return

    try:
        status_label.config(text="Iniciando download...")  # Exibe mensagem de início de download
        root.update()  # Atualiza a interface gráfica

        save_path = download_path.get()  # Obtém o caminho de salvamento
        format_choice = download_format.get()  # Obtém o formato de download
        downloaded_file = None  # Inicializa a variável para o arquivo baixado

        ydl_opts = {  # Opções para o yt-dlp
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # Define o modelo de nome do arquivo
            'verbose': True  # Habilita mensagens detalhadas
        }

        def my_hook(d):
            nonlocal downloaded_file  # Permite modificar a variável externa
            if d['status'] == 'downloading':  # Se o download estiver em andamento
                p = d.get('_percent_str', '0%')  # Obtém a porcentagem de download
                status_label.config(text=f"Baixando: {p}")  # Atualiza o rótulo de status
                root.update()  # Atualiza a interface gráfica
            elif d['status'] == 'finished':  # Se o download estiver concluído
                downloaded_file = d['filename']  # Obtém o nome do arquivo baixado
                status_label.config(text="Download concluído. Processando arquivo...")  # Atualiza o rótulo
                root.update()  # Atualiza a interface

        ydl_opts['progress_hooks'] = [my_hook]  # Adiciona a função de hook às opções

        if format_choice == "audio":  # Se o formato for áudio
            ydl_opts.update({
                'format': 'bestaudio/best',  # Define o formato como melhor áudio
                'noplaylist': True,  # Desabilita o download de playlists
            })
            try:
                subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)  # Verifica se o FFmpeg está instalado
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',  # Extrai o áudio usando FFmpeg
                        'preferredcodec': 'mp3',  # Define o codec preferido como mp3
                        'preferredquality': '192',  # Define a qualidade preferida
                    }],
                })
                status_label.config(text="Preparando para baixar áudio (MP3 com FFmpeg)...")  # Atualiza o rótulo
            except (subprocess.SubprocessError, FileNotFoundError):  # Se o FFmpeg não estiver instalado
                status_label.config(text="Preparando para baixar áudio (sem FFmpeg)...")  # Atualiza o rótulo
        else:
            ydl_opts.update({'format': 'best'})  # Define o formato como melhor vídeo
            status_label.config(text="Preparando para baixar vídeo...")  # Atualiza o rótulo

        root.update()  # Atualiza a interface gráfica

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Inicializa o yt-dlp com as opções
            info = ydl.extract_info(url, download=False)  # Obtém informações do vídeo sem baixar
            title = info.get('title', 'Arquivo')  # Obtém o título do vídeo
            status_label.config(text=f"Baixando: {title}...")  # Atualiza o rótulo com o título
            root.update()  # Atualiza a interface gráfica
            ydl.download([url])  # Inicia o download

        if format_choice == "audio" and downloaded_file:  # Se o formato for áudio e o arquivo foi baixado
            if not downloaded_file.lower().endswith('.mp3'):  # Se o arquivo não for mp3
                status_label.config(text="Convertendo para MP3...")  # Atualiza o rótulo
                root.update()  # Atualiza a interface gráfica
                try:
                    mp3_file = convert_to_mp3(downloaded_file)  # Converte para mp3
                    if mp3_file:  # Se a conversão for bem-sucedida
                        status_label.config(text=f"DOWNLOAD E CONVERSÃO PARA MP3 CONCLUÍDOS!")  # Atualiza o rótulo
                    else:  # Se a conversão falhar
                        status_label.config(text=f"DOWNLOAD CONCLUÍDO! Não foi possível converter para MP3.")  # Atualiza o rótulo
                except ImportError:  # Se o pydub não estiver instalado
                    status_label.config(text=f"DOWNLOAD CONCLUÍDO! Para converter para MP3, instale a biblioteca pydub.")  # Atualiza o rótulo
                except Exception as e:  # Se ocorrer outro erro na conversão
                    status_label.config(text=f"DOWNLOAD CONCLUÍDO! Erro na conversão: {str(e)}")  # Atualiza o rótulo
            else:  # Se o arquivo já for mp3
                status_label.config(text=f"DOWNLOAD DO ÁUDIO (MP3) CONCLUÍDO!")  # Atualiza o rótulo
        else:  # Se o formato for vídeo ou áudio já em mp3
            status_label.config(text=f"DOWNLOAD DO {'ÁUDIO' if format_choice == 'audio' else 'VÍDEO'} CONCLUÍDO!")  # Atualiza o rótulo

    except Exception as e:  # Se ocorrer um erro durante o download
        status_label.config(text=f"ERRO: {str(e)}")  # Atualiza o rótulo com a mensagem de erro
        print(f"Erro detalhado: {str(e)}")  # Imprime o erro detalhado no console

def Downloader(link, download_path, download_format, status_label, root):
    """Inicia a thread de download."""
    threading.Thread(target=lambda: download_thread(link, download_path, download_format, status_label, root), daemon=True).start()  # Cria e inicia a thread

def create_download_button(root, link, download_path, download_format, status_label):
    """Cria o botão "DOWNLOAD"."""
    tk.Button(root, text='DOWNLOAD', font='arial 15 bold', bg="lightblue", padx=2, command=lambda: Downloader(link, download_path, download_format, status_label, root)).place(x=180, y=240)  # Cria e posiciona o botão

def main():
    """Função principal para criar e executar a interface gráfica."""
    root = create_gui()  # Cria a janela principal
    link = tk.StringVar()  # Cria uma variável para o link
    download_path = tk.StringVar()  # Cria uma variável para o caminho de download
    download_format = tk.StringVar()  # Cria uma variável para o formato de download

    create_link_section(root, link)  # Cria a seção do link
    create_download_path_section(root, download_path)  # Cria a seção do caminho de download
    create_format_section(root, download_format)  # Cria a seção do formato
    create_browse_button(root, download_path)  # Cria o botão de procurar pasta
    status_label = create_status_label(root)  # Cria o rótulo de status
    create_download_button(root, link, download_path, download_format, status_label)  # Cria o botão de download

    root.mainloop()  # Inicia o loop principal da interface gráfica

if __name__ == "__main__":
    main()  # Executa a função principal se o script for executado diretamente