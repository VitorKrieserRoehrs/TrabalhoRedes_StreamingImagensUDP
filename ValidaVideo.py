import cv2
import os
import sys

def Resize(caminho_video):
    os.makedirs('Trabalho Redes/Resized', exist_ok=True)

    Original = cv2.VideoCapture(caminho_video)
    if not Original.isOpened():
        print(f"ERRO: Não foi possível abrir o vídeo de origem em: {caminho_video}")
        return

    fps = Original.get(cv2.CAP_PROP_FPS)
    if fps <= 0:
        fps = 30.0

    Resized = cv2.VideoWriter('Resized/video_resized.mp4', cv2.VideoWriter_fourcc(*'mp4v'), fps, (640, 480))

    print("Processando e redimensionando o vídeo...")

    while True:
        ok, frame = Original.read()
        if not ok:
            break

        frame = cv2.resize(frame, (640, 480))
        Resized.write(frame)

    Original.release()
    Resized.release()
    print("Sucesso! Vídeo redimensionado salvo em: Trabalho Redes/Resized/video_resized.mp4")


def validar_e_iniciar_video(caminho_video):
    if not os.path.exists(caminho_video):
        print(f"ERRO: O arquivo {caminho_video} não foi encontrado.")
        sys.exit(1)

    tamanho_bytes = os.path.getsize(caminho_video)
    tamanho_mb = tamanho_bytes / (1024 * 1024)
    if tamanho_mb > 20.0:
        print(f"ERRO: O arquivo excede o limite de 20 MB (Tamanho atual: {tamanho_mb:.2f} MB)")
        sys.exit(1)

    Resized = cv2.VideoCapture(caminho_video)
    if not Resized.isOpened():
        print("ERRO: Não foi possível abrir o arquivo de vídeo.")
        sys.exit(1)

    largura = int(Resized.get(cv2.CAP_PROP_FRAME_WIDTH))
    altura = int(Resized.get(cv2.CAP_PROP_FRAME_HEIGHT))
    fps = Resized.get(cv2.CAP_PROP_FPS)
    total_frames = Resized.get(cv2.CAP_PROP_FRAME_COUNT)

    duracao = total_frames / fps if fps > 0 else 0

    print(f"--- Informações do Vídeo ---")
    print(f"Resolução: {largura}x{altura}")
    print(f"FPS: {fps:.2f} | Total de Frames: {total_frames}")
    print(f"Duração: {duracao:.2f} segundos")
    print(f"Tamanho do arquivo: {tamanho_mb:.2f} MB\n")

    if largura > 640 or altura > 480:
        print("ERRO: A resolução máxima permitida é 640x480.")
        Resized.release()
        sys.exit(1)

    if duracao > 30.0:
        print("ERRO: A duração máxima permitida é de 30 segundos.")
        Resized.release()
        sys.exit(1)

    return Resized, fps


if __name__ == "__main__":
    Resize("Video/video.mp4")
    validar_e_iniciar_video("Resized/video_resized.mp4")