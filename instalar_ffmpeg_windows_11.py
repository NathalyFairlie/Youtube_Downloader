#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import os
import sys
import zipfile
import urllib.request
import subprocess
import ctypes
import tempfile
import shutil
from pathlib import Path

def is_admin():
    """Verifica se o script está sendo executado como administrador."""
    try:
        return ctypes.windll.shell32.IsUserAnAdmin()
    except:
        return False

def download_file(url, destination):
    """Baixa um arquivo da URL especificada para o destino fornecido usando urllib."""
    print(f"Baixando FFmpeg de {url}...")
    try:
        # Criar um opener com suporte a HTTPS
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-Agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        
        # Mostrar progresso do download
        def report_progress(block_num, block_size, total_size):
            downloaded = block_num * block_size
            if total_size > 0:
                percent = min(100, int(downloaded * 100 / total_size))
                # Mostrar barra de progresso
                done = int(50 * percent / 100)
                sys.stdout.write("\r[%s%s] %d%%" % ('=' * done, ' ' * (50 - done), percent))
                sys.stdout.flush()
        
        # Baixar o arquivo
        urllib.request.urlretrieve(url, destination, reporthook=report_progress)
        print("\nDownload concluído!")
        return True
    except Exception as e:
        print(f"Erro ao baixar arquivo: {e}")
        return False

def extract_zip(zip_path, extract_to):
    """Extrai um arquivo zip para o diretório especificado."""
    print(f"Extraindo arquivo zip para {extract_to}...")
    try:
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_to)
        print("Extração concluída!")
        return True
    except Exception as e:
        print(f"Erro ao extrair arquivo: {e}")
        return False

def add_to_path(directory):
    """Adiciona o diretório especificado à variável PATH do usuário."""
    print(f"Adicionando {directory} à variável PATH...")
    try:
        # Usando PowerShell para adicionar ao PATH
        cmd = f'setx PATH "%PATH%;{directory}"'
        subprocess.run(cmd, shell=True, check=True)
        print("Diretório adicionado ao PATH com sucesso!")
        return True
    except Exception as e:
        print(f"Erro ao adicionar ao PATH: {e}")
        return False

def install_ffmpeg():
    """Instala o FFmpeg no Windows."""
    # URL do FFmpeg (versão estática)
    ffmpeg_url = "https://github.com/BtbN/FFmpeg-Builds/releases/download/latest/ffmpeg-master-latest-win64-gpl.zip"
    
    # Diretórios para instalação
    app_data = os.environ.get('LOCALAPPDATA', os.path.join(os.environ['USERPROFILE'], 'AppData', 'Local'))
    install_dir = os.path.join(app_data, 'FFmpeg')
    temp_dir = tempfile.mkdtemp()
    
    # Nomes de arquivos
    zip_file = os.path.join(temp_dir, "ffmpeg.zip")
    
    try:
        # Criar diretório de instalação
        os.makedirs(install_dir, exist_ok=True)
        
        # Baixar FFmpeg
        if not download_file(ffmpeg_url, zip_file):
            return False
            
        # Extrair arquivo
        if not extract_zip(zip_file, temp_dir):
            return False
            
        # Encontrar pasta extraída (geralmente contém 'ffmpeg' no nome)
        extracted_dirs = [d for d in os.listdir(temp_dir) if os.path.isdir(os.path.join(temp_dir, d)) and 'ffmpeg' in d.lower()]
        if not extracted_dirs:
            print("Não foi possível encontrar a pasta extraída do FFmpeg")
            return False
            
        extracted_dir = os.path.join(temp_dir, extracted_dirs[0])
        
        # Copiar arquivos para o diretório de instalação
        # Geralmente, os binários estão em uma pasta 'bin'
        bin_source_dir = os.path.join(extracted_dir, 'bin')
        if not os.path.exists(bin_source_dir):
            bin_source_dir = extracted_dir
        
        # Limpar diretório de instalação se já existir
        if os.path.exists(install_dir):
            for item in os.listdir(install_dir):
                path = os.path.join(install_dir, item)
                try:
                    if os.path.isfile(path):
                        os.unlink(path)
                    elif os.path.isdir(path):
                        shutil.rmtree(path)
                except Exception as e:
                    print(f"Erro ao limpar diretório: {e}")
        
        # Copiar todos os arquivos
        print(f"Copiando arquivos para {install_dir}...")
        for item in os.listdir(bin_source_dir):
            s = os.path.join(bin_source_dir, item)
            d = os.path.join(install_dir, item)
            if os.path.isfile(s):
                shutil.copy2(s, d)
        
        # Adicionar ao PATH
        if not add_to_path(install_dir):
            return False
            
        print("\nFFmpeg instalado com sucesso!")
        print(f"Instalado em: {install_dir}")
        print("\nVocê precisará reiniciar qualquer prompt de comando aberto para usar o FFmpeg.")
        return True
        
    except Exception as e:
        print(f"Erro durante a instalação: {e}")
        return False
    finally:
        # Limpar arquivos temporários
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

def test_ffmpeg():
    """Testa se o FFmpeg foi instalado corretamente."""
    print("\nTestando instalação do FFmpeg...")
    try:
        result = subprocess.run(["ffmpeg", "-version"], 
                               stdout=subprocess.PIPE, 
                               stderr=subprocess.PIPE, 
                               text=True)
        
        if result.returncode == 0:
            print("FFmpeg está instalado e funcionando corretamente!")
            print(f"Versão instalada: {result.stdout.splitlines()[0]}")
            return True
        else:
            print("AVISO: FFmpeg instalado, mas você precisa reiniciar o prompt de comando para usá-lo.")
            return False
    except Exception as e:
        print(f"AVISO: FFmpeg instalado, mas você precisa reiniciar o prompt de comando para usá-lo.")
        return False

def main():
    print("===== Instalador Automático de FFmpeg para Windows =====")
    
    # Instalar FFmpeg (sem verificar privilégios de administrador)
    if install_ffmpeg():
        # Testar instalação
        test_ffmpeg()
        
        # Mostrar exemplo de como usar com Python
        print("\nExemplo de como usar FFmpeg com Python:")
        print("""
import subprocess

# Converter um vídeo
def converter_video(entrada, saida):
    comando = [
        'ffmpeg',
        '-i', entrada,
        '-c:v', 'libx264',
        '-crf', '23',
        '-c:a', 'aac',
        '-b:a', '128k',
        saida
    ]
    
    resultado = subprocess.run(comando, 
                             stdout=subprocess.PIPE, 
                             stderr=subprocess.PIPE)
    
    if resultado.returncode == 0:
        print(f"Vídeo convertido com sucesso: {saida}")
    else:
        print(f"Erro ao converter vídeo.")
        
# Exemplo:
# converter_video('video_entrada.mp4', 'video_saida.mp4')
        """)
    
    print("\nPressione Enter para sair...")
    input()

if __name__ == "__main__":
    main()