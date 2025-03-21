# Download de Vídeos do YouTube (Tkinter)

## Descrição

Script Python com interface gráfica (Tkinter) para baixar vídeos do YouTube. Usa a biblioteca `yt-dlp` e permite baixar vídeos em formato de vídeo (mp4) ou áudio (mp3). Tenta também atualizar a data do arquivo baixado.

## Funcionalidades

*   Interface gráfica simples (Tkinter).
*   Entrada para URLs do YouTube.
*   Seleção da pasta de download.
*   Seleção do formato (vídeo ou áudio).
*   Exibe o progresso do download.
*   Tratamento de erros.
*   Tenta atualizar a data do arquivo baixado.
*   Inclui instalador automático do FFmpeg para Windows.

## Dependências

*   Python 3.x
*   Tkinter (geralmente já instalado com o Python)
*   `yt-dlp`: `pip install yt-dlp`
*   `audioclipextractor`: `pip install audioclipextractor`
*   `lameenc`: `pip install lameenc`
*   FFmpeg (necessário para extrair áudio - script de instalação para Windows incluído)

## Instalação

1.  Instale o Python 3.x: [https://www.python.org/](https://www.python.org/)
2.  Instale as dependências: `pip install yt-dlp audioclipextractor lameenc`
3.  Execute o script: `python nome_do_script.py`

## Uso

1.  Execute o script.
2.  Cole a URL do YouTube.
3.  Selecione a pasta de download.
4.  Escolha o formato (vídeo ou áudio).
5.  Clique em "DOWNLOAD".

## Notas

*   O instalador do FFmpeg é apenas para Windows. Em macOS ou Linux, instale o FFmpeg manualmente (ex: `brew install ffmpeg` ou `apt-get install ffmpeg`).
*   A atualização da data do arquivo pode não funcionar em todos os sistemas.
*   Verifique a interface gráfica para mensagens de erro ou progresso.
*   Use este script por sua conta e risco. Baixar conteúdo protegido por direitos autorais pode ser ilegal.
