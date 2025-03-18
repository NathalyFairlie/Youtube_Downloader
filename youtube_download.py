from tkinter import *  # Importa todos os componentes do pacote tkinter para criar a interface gráfica
from tkinter import filedialog, messagebox  # Importa caixas de diálogo específicas para selecionar arquivos e mostrar mensagens
import yt_dlp  # Biblioteca para download de vídeos do YouTube
import os  # Módulo para operações relacionadas ao sistema de arquivos
import threading  # Módulo para executar tarefas em paralelo
import subprocess  # Módulo para executar comandos do sistema
import sys  # Módulo para acessar variáveis específicas do sistema
import importlib  # Módulo para verificar e importar outros módulos Python
import time  # Módulo para operações relacionadas a tempo e data

# Cria a janela principal da aplicação
root = Tk()  # Inicializa a janela principal
root.configure(bg="lightgray")  # Define a cor de fundo da janela
root.geometry('500x420')  # Define o tamanho inicial da janela (largura x altura)
root.resizable(0, 0)  # Impede que a janela seja redimensionada
root.title("Download de Vídeos do YouTube")  # Define o título da janela

# --- Seção para inserir o link do vídeo ---
link = StringVar()  # Variável para armazenar o link do vídeo
Label(root, text='Cole o Link Aqui:', font='arial 15 bold').place(x=160, y=60)  # Cria um rótulo de texto
link_enter = Entry(root, width=70, textvariable=link).place(x=32, y=90)  # Cria uma caixa de entrada para o link

# --- Seção para selecionar o diretório de download ---
download_path = StringVar()  # Variável para armazenar o caminho de download
download_path.set(os.path.expanduser("~/Downloads"))  # Define o diretório padrão como a pasta Downloads do usuário

Label(root, text='Pasta de Download:', font='arial 15 bold').place(x=160, y=120)  # Cria um rótulo de texto
path_entry = Entry(root, width=55, textvariable=download_path)  # Cria uma caixa de entrada para o caminho
path_entry.place(x=32, y=150)  # Posiciona a caixa de entrada na janela

# --- Seção para selecionar o formato de download ---
download_format = StringVar()  # Variável para armazenar o formato de download
download_format.set("video")  # Define "vídeo" como formato padrão

Label(root, text='Formato:', font='arial 15 bold').place(x=215, y=180)  # Cria um rótulo de texto
# Cria botões de opção para escolher entre vídeo e áudio
Radiobutton(root, text="Vídeo (mp4)", variable=download_format, value="video", bg="lightgray", font='arial 12').place(x=140, y=210)
Radiobutton(root, text="Áudio (MP3)", variable=download_format, value="audio", bg="lightgray", font='arial 12').place(x=260, y=210)

# --- Verificação de dependências ---
def check_module(module_name):
    """Verifica se um módulo Python está instalado"""
    try:
        importlib.import_module(module_name)  # Tenta importar o módulo
        return True  # Retorna True se o módulo estiver instalado
    except ImportError:
        return False  # Retorna False se o módulo não estiver instalado

def install_module(module_name):
    """Instala um módulo Python usando pip"""
    status_label.config(text=f"Instalando {module_name}... Aguarde...")  # Atualiza o rótulo de status
    root.update()  # Atualiza a interface gráfica
    
    try:
        # Executa o comando pip para instalar o módulo
        subprocess.check_call([sys.executable, "-m", "pip", "install", module_name])
        status_label.config(text=f"{module_name} instalado com sucesso!")  # Atualiza o rótulo de status
        root.update()  # Atualiza a interface gráfica
        return True  # Retorna True se a instalação for bem-sucedida
    except Exception as e:
        status_label.config(text=f"Erro ao instalar {module_name}: {str(e)}")  # Exibe mensagem de erro
        return False  # Retorna False se a instalação falhar

# --- Função para abrir a caixa de diálogo de seleção de diretório ---
def browse_folder():
    """Abre uma caixa de diálogo para selecionar a pasta de download"""
    folder = filedialog.askdirectory()  # Abre a caixa de diálogo de seleção de diretório
    if folder:  # Se um diretório for selecionado
        download_path.set(folder)  # Atualiza a variável de caminho de download

# Cria um botão para procurar pastas
browse_button = Button(root, text="Procurar", font='arial 10 bold', bg="lightblue", command=browse_folder)
browse_button.place(x=400, y=150)  # Posiciona o botão na janela

# --- Seção para exibir o status do download ---
status_label = Label(root, text="", font='arial 12')  # Cria um rótulo para exibir o status
status_label.place(x=50, y=310)  # Posiciona o rótulo na janela
status_label.config(wraplength=400)  # Configura a quebra de linha do texto

# --- Função para instalar dependências necessárias ---
def install_dependencies():
    """Instala as bibliotecas necessárias para converter áudio para MP3"""
    success = True  # Variável para controlar o sucesso da instalação
    
    # Verificar e instalar audioclipextractor
    if not check_module("audioclipextractor"):
        if messagebox.askyesno("Instalar Módulos", 
                             "Para converter áudio para MP3 sem FFmpeg, é necessário instalar algumas bibliotecas.\n\nDeseja instalar agora?"):
            success = install_module("audioclipextractor")  # Instala o módulo audioclipextractor
    
    # Verificar e instalar lameenc (necessário para MP3)
    if success and not check_module("lameenc"):
        success = install_module("lameenc")  # Instala o módulo lameenc
    
    if success:
        status_label.config(text="Todas as dependências instaladas com sucesso!")  # Atualiza o rótulo de status
    else:
        status_label.config(text="Falha ao instalar algumas dependências.")  # Exibe mensagem de erro
    
    return success  # Retorna o status da instalação

# Cria um botão para instalar dependências
Button(root, text='Instalar Dependências', font='arial 10 bold', bg="lightgreen", command=install_dependencies).place(x=170, y=290)

# --- Função para converter webm para mp3 usando audioclipextractor ---
def convert_to_mp3(input_file):
    """Converte um arquivo de áudio para formato MP3"""
    try:
        # Importa as bibliotecas necessárias
        import audioclipextractor
        import lameenc
        
        # Determina o nome do arquivo de saída (substitui a extensão por .mp3)
        base_name = os.path.splitext(input_file)[0]
        output_file = base_name + ".mp3"
        
        # Cria um extrator sem FFmpeg
        extractor = audioclipextractor.AudioClipExtractor()
        
        # Converte o arquivo
        extractor.extract_audio_clip(input_file, output_file)
        
        # Remove o arquivo original
        os.remove(input_file)
        
        return output_file  # Retorna o caminho do arquivo MP3
    except ImportError:
        # Se faltarem dependências, propõe instalá-las
        if messagebox.askyesno("Instalar Dependências", 
                            "É necessário instalar algumas bibliotecas para converter áudio.\n\nDeseja instalar agora?"):
            if install_dependencies():
                # Tenta novamente após instalar
                return convert_to_mp3(input_file)
        return None  # Retorna None se não conseguir instalar as dependências
    except Exception as e:
        print(f"Erro na conversão: {str(e)}")  # Exibe mensagem de erro
        return None  # Retorna None se ocorrer um erro na conversão

# --- Função para definir a data de modificação do arquivo para hoje ---
def update_file_timestamp(file_path):
    """Define a data de modificação do arquivo para a data atual"""
    if file_path and os.path.exists(file_path):
        current_time = time.time()  # Obtém o timestamp atual
        os.utime(file_path, (current_time, current_time))  # Define os timestamps de acesso e modificação
        return True
    return False

# --- Função para lidar com a atualização da data após o download ---
def force_file_date(file_path):
    """Força a data de modificação do arquivo para a data atual"""
    # Verifica se o arquivo existe
    if not file_path or not os.path.exists(file_path):
        return False
    
    try:
        # Tenta usar o comando touch no Linux/Mac ou em sistemas Windows com WSL
        if sys.platform.startswith('linux') or sys.platform == 'darwin':
            subprocess.run(['touch', file_path])
            return True
            
        # Para Windows, usa o método explicito de definir data/hora
        current_time = time.time()
        os.utime(file_path, (current_time, current_time))
        
        # Verifica se a data foi alterada corretamente
        if abs(os.path.getmtime(file_path) - current_time) < 2:  # Tolerância de 2 segundos
            return True
            
        # Tenta usar o comando touch do Windows (se disponível em alguns sistemas)
        try:
            subprocess.run(['cmd', '/c', 'touch', file_path], check=True)
            return True
        except:
            pass
            
        # Se ainda não conseguiu, tenta recriar o arquivo mantendo o conteúdo
        with open(file_path, 'rb') as f:
            content = f.read()
        with open(file_path, 'wb') as f:
            f.write(content)
        os.utime(file_path, (current_time, current_time))
        
        return True
    except Exception as e:
        print(f"Erro ao atualizar a data do arquivo: {str(e)}")
        return False

# --- Função para realizar o download ---
def download_thread():
    """Função principal que realiza o download do vídeo/áudio"""
    url = str(link.get())  # Obtém a URL do campo de entrada
    if not url:
        status_label.config(text="Por favor, insira uma URL válida")  # Exibe mensagem de erro
        return

    try:
        status_label.config(text="Iniciando download...")  # Atualiza o rótulo de status
        root.update()  # Atualiza a interface gráfica

        save_path = download_path.get()  # Obtém o caminho de salvamento
        format_choice = download_format.get()  # Obtém o formato escolhido
        
        # Variável para armazenar o caminho do arquivo baixado
        downloaded_file = None
        
        # Configuração do yt-dlp
        ydl_opts = {
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # Define o formato do nome do arquivo
            'verbose': True,  # Habilita mensagens detalhadas
            'updatetime': False  # Impede que o yt-dlp defina a data do arquivo
        }
        
        # Hooks para rastrear o progresso e o arquivo baixado
        def my_hook(d):
            nonlocal downloaded_file
            if d['status'] == 'downloading':
                p = d.get('_percent_str', '0%')  # Obtém a porcentagem de download
                status_label.config(text=f"Baixando: {p}")  # Atualiza o rótulo de status
                root.update()  # Atualiza a interface gráfica
            elif d['status'] == 'finished':
                downloaded_file = d['filename']  # Armazena o nome do arquivo baixado
                status_label.config(text="Download concluído. Processando arquivo...")  # Atualiza o rótulo de status
                root.update()  # Atualiza a interface gráfica
                
                # Atualiza a data de modificação imediatamente após o download
                force_file_date(downloaded_file)
        
        ydl_opts['progress_hooks'] = [my_hook]  # Adiciona o hook de progresso às opções
        
        # Configuração baseada na escolha do usuário
        if format_choice == "audio":
            # Tentar baixar em formato MP3 diretamente, se disponível
            ydl_opts.update({
                'format': 'bestaudio[ext=mp3]/bestaudio/best',  # Prioriza áudio em MP3
                'noplaylist': True,  # Não baixa playlists
            })
            
            # Verificar se FFmpeg está disponível como fallback
            ffmpeg_available = False
            try:
                subprocess.run(['ffmpeg', '-version'], stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                ffmpeg_available = True
                ydl_opts.update({
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                })
                status_label.config(text="Preparando para baixar áudio (MP3 com FFmpeg)...")  # Atualiza o rótulo de status
            except (subprocess.SubprocessError, FileNotFoundError):
                status_label.config(text="Preparando para baixar áudio (sem FFmpeg)...")  # Atualiza o rótulo de status
        else:
            ydl_opts.update({
                'format': 'best',  # Seleciona a melhor qualidade de vídeo
            })
            status_label.config(text="Preparando para baixar vídeo...")  # Atualiza o rótulo de status
        
        root.update()  # Atualiza a interface gráfica
        
        # Realizar o download
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=False)  # Obtém informações do vídeo
            title = info.get('title', 'Arquivo')  # Obtém o título do vídeo
            status_label.config(text=f"Baixando: {title}...")  # Atualiza o rótulo de status
            root.update()  # Atualiza a interface gráfica
            ydl.download([url])  # Inicia o download
        
        # Converter para MP3 se necessário e se FFmpeg não estava disponível
        mp3_file = None  # Inicializa a variável para o arquivo MP3
        if format_choice == "audio" and downloaded_file and not ffmpeg_available:
            if not downloaded_file.lower().endswith('.mp3'):
                status_label.config(text="Tentando converter para MP3...")  # Atualiza o rótulo de status
                root.update()  # Atualiza a interface gráfica
                
                # Verificar se audioclipextractor está disponível
                if check_module("audioclipextractor") and check_module("lameenc"):
                    mp3_file = convert_to_mp3(downloaded_file)  # Converte o arquivo para MP3
                    if mp3_file:
                        # Atualiza a data de modificação do arquivo MP3 para hoje
                        force_file_date(mp3_file)
                        status_label.config(text=f"DOWNLOAD E CONVERSÃO PARA MP3 CONCLUÍDOS!")  # Atualiza o rótulo de status
                    else:
                        status_label.config(text=f"DOWNLOAD CONCLUÍDO! Não foi possível converter para MP3.")  # Exibe mensagem de erro
                else:
                    if messagebox.askyesno("Instalar Dependências", 
                                         "É necessário instalar bibliotecas para converter para MP3.\n\nDeseja instalar agora?"):
                        if install_dependencies():
                            mp3_file = convert_to_mp3(downloaded_file)  # Converte o arquivo para MP3
                            if mp3_file:
                                # Atualiza a data de modificação do arquivo MP3 para hoje
                                force_file_date(mp3_file)
                                status_label.config(text=f"DOWNLOAD E CONVERSÃO CONCLUÍDOS!")  # Atualiza o rótulo de status
                            else:
                                status_label.config(text=f"Não foi possível converter para MP3.")  # Exibe mensagem de erro
                        else:
                            status_label.config(text=f"DOWNLOAD CONCLUÍDO! Para converter, instale as dependências.")  # Exibe mensagem de erro
                    else:
                        status_label.config(text=f"DOWNLOAD CONCLUÍDO! Para converter, instale as dependências.")  # Exibe mensagem de erro
            else:
                # Atualiza a data de modificação do arquivo MP3 para hoje
                force_file_date(downloaded_file)
                status_label.config(text=f"DOWNLOAD DO ÁUDIO (MP3) CONCLUÍDO!")  # Atualiza o rótulo de status
        else:
            # Atualiza a data de modificação do arquivo baixado para hoje (extra com redundância)
            if downloaded_file:
                force_file_date(downloaded_file)
                
            if format_choice == "audio":
                status_label.config(text=f"DOWNLOAD DO ÁUDIO CONCLUÍDO!")  # Atualiza o rótulo de status
            else:
                status_label.config(text=f"DOWNLOAD DO VÍDEO CONCLUÍDO!")  # Atualiza o rótulo de status
                
    except Exception as e:
        status_label.config(text=f"ERRO: {str(e)}")  # Exibe mensagem de erro
        print(f"Erro detalhado: {str(e)}")  # Exibe erro detalhado no console

# Função para iniciar o download em uma thread separada
def Downloader():
    """Inicia o download em uma thread separada para não bloquear a interface"""
    threading.Thread(target=download_thread, daemon=True).start()  # Cria e inicia uma nova thread

# Cria um botão "DOWNLOAD" que chama a função Downloader quando clicado
Button(root, text='DOWNLOAD', font='arial 15 bold', bg="lightblue", padx=2, command=Downloader).place(x=180, y=240)

# Inicia o loop principal da aplicação
root.mainloop()  # Mantém a janela aberta e aguarda eventos
