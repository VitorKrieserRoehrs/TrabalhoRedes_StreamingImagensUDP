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

        # Pega as dimensões do frame pra dividir em 4 partes
        h, w, _ = frame.shape
        metade_h = h // 2
        metade_w = w // 2

        partes = [
            frame[0:metade_h, 0:metade_w],      # Top-Left (ID 0)
            frame[0:metade_h, metade_w:w],      # Top-Right (ID 1)
            frame[metade_h:h, 0:metade_w],      # Bottom-Left (ID 2)
            frame[metade_h:h, metade_w:w]       # Bottom-Right (ID 3)
        ]

        # Envia cada uma das 4 partes
        for id_parte, sub_frame in enumerate(partes):
            ok, buffer = cv2.imencode(".jpg", sub_frame, [int(cv2.IMWRITE_JPEG_QUALITY), 80])
            if not ok:
                raise RuntimeError(f"Não foi possível codificar a parte {id_parte} como JPEG.")

            # INJEÇÃO DO CABEÇALHO:
            # Cria um byte contendo o ID (0, 1, 2 ou 3) e junta com os bytes da imagem
            pacote_com_id = bytes([id_parte]) + buffer.tobytes()

            # O limite máximo do datagrama UDP v4 é 65507 bytes totais
            if len(pacote_com_id) > 65507:
                raise RuntimeError(
                    f"A parte {id_parte} excedeu o tamanho máximo de um datagrama UDP IPv4."
                )

            # Envia o pacote com o ID embutido
            servidor_socket.sendto(pacote_com_id, (Grupo_Multicast, Porta))

        next_frame_time += frame_interval
        time.sleep(max(0, next_frame_time - time.perf_counter()))

    servidor_socket.sendto(b"END", (Grupo_Multicast, Porta))
finally:
    Resized.release()
    servidor_socket.close()
