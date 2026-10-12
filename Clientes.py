import socket

import cv2
import numpy as np

Grupo_Multicast = "239.1.1.1"
Porta = 12345
# Criação do socket UDP para o cliente
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
# Configuração do socket para permitir a reutilização do endereço
cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cliente_socket.bind(("", Porta))
# Limite de tempo para receber pacotes (em segundos)
cliente_socket.settimeout(0.02)

# Aqui convertemos o endereço do grupo multicast para o formato necessário 
# Adicionamos o cliente ao grupo
grupo = socket.inet_aton(Grupo_Multicast) + socket.inet_aton("0.0.0.0")
cliente_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, grupo)

print(f"Aguardando vídeo em {Grupo_Multicast}:{Porta}...")

# Criação da janela
cv2.namedWindow("Cliente Multicast - Recebendo Video", cv2.WINDOW_NORMAL)

try:
    while True:
        try:
            packet, endereco = cliente_socket.recvfrom(65535)
        except socket.timeout:
            packet = None

        if packet == b"END":
            print(f"Transmissão finalizada por {endereco}.")
            break

        if packet is not None:
            frame = cv2.imdecode(np.frombuffer(packet, dtype=np.uint8),cv2.IMREAD_COLOR)

            if frame is not None:
                cv2.imshow("Cliente Multicast - Recebendo Video", frame)
            else:
                print(f"Frame inválido recebido de {endereco}")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break
except KeyboardInterrupt:
    print("\nEncerrando o cliente...")
finally:
    cliente_socket.close()
    cv2.destroyAllWindows()
