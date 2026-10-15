import cv2
import socket
import time

Grupo_Multicast = "239.1.1.1"
Porta = 12345
# Criação do socket UDP para o servidor
servidor_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Configuração do socket para permitir o envio de pacotes multicast
servidor_socket.setsockopt(socket.IPPROTO_IP, socket.IP_MULTICAST_TTL, 1)

Resized = cv2.VideoCapture("Resized/video_resized.mp4")
if not Resized.isOpened():
    servidor_socket.close()
    raise RuntimeError("Não foi possível abrir Resized/video_resized.mp4")

fps = Resized.get(cv2.CAP_PROP_FPS)
if fps <= 0:
    Resized.release()
    servidor_socket.close()
    raise RuntimeError("O vídeo informa um FPS inválido.")

frame_interval = 1 / fps

print("Servidor pronto para transmitir...")
print("Transmissão começando em 5 segundos...")
time.sleep(5)

next_frame_time = time.perf_counter()
try:
    while True:
        ret, frame = Resized.read()
        if not ret:
            break

        # Aqui pega as dimensões do frame, para dividir o frame em partes menores
        h, w, _ = frame.shape
        metade_h = h // 2
        metade_w = w // 2

        # (Top-Left)
        # Vai do topo até a metade da altura, e do canto esquerdo até a metade da largura.
        parte1 = frame[0:metade_h, 0:metade_w]

        # (Top-Right)
        # Vai do topo até a metade da altura, e da metade da largura até o fim da imagem.
        parte2 = frame[0:metade_h, metade_w:w]

        # (Bottom-Left)
        # Vai da metade da altura até o chão (h), e do canto esquerdo (0) até a metade da largura.
        parte3 = frame[metade_h:h, 0:metade_w]

        # (Bottom-Right)
        # Vai da metade da altura até o chão (h), e da metade da largura até o fim da imagem (w).
        parte4 = frame[metade_h:h, metade_w:w]

        #Parte1
        ok, buffer = cv2.imencode(".jpg", parte1, [int(cv2.IMWRITE_JPEG_QUALITY), 80], )
        if not ok:
            raise RuntimeError("Não foi possível codificar um frame como JPEG.")

        bytes_frame = buffer.tobytes()
        if len(bytes_frame) > 65507:
            raise RuntimeError(
                "Um frame excede o tamanho máximo de um datagrama UDP IPv4."
            )
        servidor_socket.sendto(bytes_frame, (Grupo_Multicast, Porta))

        #Parte2
        ok, buffer = cv2.imencode(".jpg", parte2, [int(cv2.IMWRITE_JPEG_QUALITY), 80], )
        if not ok:
            raise RuntimeError("Não foi possível codificar um frame como JPEG.")

        bytes_frame = buffer.tobytes()
        if len(bytes_frame) > 65507:
            raise RuntimeError(
                "Um frame excede o tamanho máximo de um datagrama UDP IPv4."
            )
        servidor_socket.sendto(bytes_frame, (Grupo_Multicast, Porta))

        #Parte3
        ok, buffer = cv2.imencode(".jpg", parte3, [int(cv2.IMWRITE_JPEG_QUALITY), 80], )
        if not ok:
            raise RuntimeError("Não foi possível codificar um frame como JPEG.")

        bytes_frame = buffer.tobytes()
        if len(bytes_frame) > 65507:
            raise RuntimeError(
                "Um frame excede o tamanho máximo de um datagrama UDP IPv4."
            )
        servidor_socket.sendto(bytes_frame, (Grupo_Multicast, Porta))

        #Parte4
        ok, buffer = cv2.imencode(".jpg", parte4, [int(cv2.IMWRITE_JPEG_QUALITY), 80], )
        if not ok:
            raise RuntimeError("Não foi possível codificar um frame como JPEG.")

        bytes_frame = buffer.tobytes()
        if len(bytes_frame) > 65507:
            raise RuntimeError(
                "Um frame excede o tamanho máximo de um datagrama UDP IPv4."
            )
        servidor_socket.sendto(bytes_frame, (Grupo_Multicast, Porta))

        next_frame_time += frame_interval
        time.sleep(max(0, next_frame_time - time.perf_counter()))

    servidor_socket.sendto(b"END", (Grupo_Multicast, Porta))
finally:
    Resized.release()
    servidor_socket.close()
