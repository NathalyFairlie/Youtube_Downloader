from tkinter import *  # Importa todos os módulos do pacote tkinter, que é usado para criar interfaces gráficas
from tkinter import filedialog  # Importa o módulo filedialog, que permite abrir caixas de diálogo para selecionar arquivos ou diretórios
import yt_dlp  # Importa a biblioteca yt_dlp, que é usada para baixar vídeos de plataformas como o YouTube
import os  # Importa o módulo os, que fornece funções para interagir com o sistema operacional

# Cria a janela principal da aplicação
root = Tk()
root.configure(bg="lightgray") # Define a cor de fundo da janela principal como cinza claro
root.geometry('500x350')  # Define o tamanho da janela como 500x350 pixels. 
root.resizable(0,0)  # Impede que o usuário redimensione a janela
root.title("Download de Vídeos do YouTube")  # Define o título da janela


# --- Seção para inserir o link do vídeo ---
link = StringVar()  # Cria uma variável StringVar para armazenar o link do vídeo
Label(root, text='Cole o Link Aqui:', font='arial 15 bold').place(x=160, y=60)  # Cria um rótulo para instruir o usuário a colar o link
link_enter = Entry(root, width=70, textvariable=link).place(x=32, y=90)  # Cria uma caixa de entrada (Entry) onde o usuário pode colar o link

# --- Seção para selecionar o diretório de download ---
download_path = StringVar()  # Cria uma variável StringVar para armazenar o caminho do diretório de download
download_path.set(os.path.expanduser("~/Downloads"))  # Define o diretório padrão como a pasta "Downloads" do usuário

Label(root, text='Pasta de Download:', font='arial 15 bold').place(x=160, y=120)  # Cria um rótulo para indicar a pasta de download
path_entry = Entry(root, width=55, textvariable=download_path)  # Cria uma caixa de entrada para exibir e, opcionalmente, editar o caminho do diretório
path_entry.place(x=32, y=150)  # Posiciona a caixa de entrada na janela

# Função para abrir a caixa de diálogo de seleção de diretório
def browse_folder():
    folder = filedialog.askdirectory()  # Abre a caixa de diálogo para selecionar um diretório
    if folder:  # Verifica se um diretório foi selecionado
        download_path.set(folder)  # Define o caminho do diretório selecionado na variável download_path

browse_button = Button(root, text="Procurar",font='arial 10 bold', bg="lightblue", command=browse_folder)  # Cria um botão para abrir a caixa de diálogo de seleção de diretório
browse_button.place(x=400, y=150)  # Posiciona o botão na janela

# --- Seção para exibir o status do download ---
status_label = Label(root, text="", font='arial 12')  # Cria um rótulo para exibir mensagens de status
status_label.place(x=50, y=250)  # Posiciona o rótulo na janela
status_label.config(wraplength=400)  # Permite quebra de linha para mensagens longas

# --- Função para realizar o download do vídeo ---
def Downloader():
    url = str(link.get())  # Obtém o link do vídeo da variável link
    if not url:  # Verifica se o link está vazio
        status_label.config(text="Por favor, insira uma URL válida")  # Exibe uma mensagem de erro se o link estiver vazio
        return  # Sai da função

    try:  # Inicia um bloco try-except para lidar com possíveis erros durante o download
        status_label.config(text="Iniciando download...")  # Exibe uma mensagem de status
        root.update()  # Atualiza a interface gráfica para exibir a mensagem de status

        save_path = download_path.get()  # Obtém o caminho do diretório de download da variável download_path

        # Define as opções de configuração para o yt_dlp
        ydl_opts = {
            'format': 'best',  # Define o formato do vídeo como o melhor disponível
            'outtmpl': os.path.join(save_path, '%(title)s.%(ext)s'),  # Define o nome do arquivo de saída como o título do vídeo e a extensão
            'progress_hooks': [progress_hook],  # Define uma função de gancho para acompanhar o progresso do download
            'verbose': True  # Ativa o modo verbose para exibir informações detalhadas no console
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:  # Cria uma instância do YoutubeDL com as opções de configuração
            info = ydl.extract_info(url, download=False)  # Extrai informações do vídeo sem baixá-lo
            status_label.config(text=f"Baixando: {info.get('title', 'Vídeo')}...")  # Exibe o título do vídeo no rótulo de status
            root.update()  # Atualiza a interface gráfica
            ydl.download([url])  # Inicia o download do vídeo

        status_label.config(text="DOWNLOAD CONCLUÍDO!")  # Exibe uma mensagem de conclusão
    except Exception as e:  # Captura qualquer exceção que ocorra durante o download
        status_label.config(text=f"ERRO: {str(e)}")  # Exibe uma mensagem de erro
        print(f"Erro detalhado: {str(e)}")  # Imprime o erro detalhado no console

# Função para atualizar o rótulo de status com o progresso do download
def progress_hook(d):
    if d['status'] == 'downloading':  # Verifica se o status é "downloading"
        p = d.get('_percent_str', '0%')  # Obtém a porcentagem de progresso do download
        status_label.config(text=f"Baixando: {p}")  # Atualiza o rótulo de status com a porcentagem
        root.update()  # Atualiza a interface gráfica

# Cria um botão "DOWNLOAD" que chama a função Downloader quando clicado
Button(root, text='DOWNLOAD', font='arial 15 bold', bg="lightblue", padx=2, command=Downloader).place(x=180, y=200)

root.mainloop()  # Inicia o loop principal do tkinter, que mantém a janela aberta e responde aos eventos do usuário