import socket
import cv2
import numpy as np

Grupo_Multicast = "239.1.1.1"
Porta = 12345

# Criação do socket UDP para o cliente
cliente_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
cliente_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
cliente_socket.bind(("", Porta))
cliente_socket.settimeout(0.02)

grupo = socket.inet_aton(Grupo_Multicast) + socket.inet_aton("0.0.0.0")
cliente_socket.setsockopt(socket.IPPROTO_IP, socket.IP_ADD_MEMBERSHIP, grupo)

print(f"Aguardando vídeo em {Grupo_Multicast}:{Porta}...")

cv2.namedWindow("Cliente Multicast - Recebendo Video", cv2.WINDOW_NORMAL)

# Salva temporariamente as partes do frame
partes_frame = {}

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
            # O servidor tem que mandar o ID da parte no primeiro byte do pacote
            id_parte = packet[0] 
            dados_imagem = packet[1:] # O resto do pacote são os bytes da imagem

            # Decodifica a parte atual da imagem
            parte = cv2.imdecode(np.frombuffer(dados_imagem, dtype=np.uint8), cv2.IMREAD_COLOR)

            if parte is not None:
                # Salva a parte no nosso dicionário
                partes_frame[id_parte] = parte

                # Se já recebemos as 4 partes necessárias (IDs: 0, 1, 2 e 3)
                if len(partes_frame) == 4:
                    try:
                        # Pega cada parte na ordem correta
                        p1 = partes_frame[0] # Superior Esquerdo
                        p2 = partes_frame[1] # Superior Direito
                        p3 = partes_frame[2] # Inferior Esquerdo
                        p4 = partes_frame[3] # Inferior Direito

                        # Reconstroi usando o OPENCV
                        metade_superior = cv2.hconcat([p1, p2])
                        metade_inferior = cv2.hconcat([p3, p4])
                        frame_completo = cv2.vconcat([metade_superior, metade_inferior])

                        # Frame final montado
                        cv2.imshow("Cliente Multicast - Recebendo Video", frame_completo)
                    
                    except Exception as e:
                        print(f"Erro ao reconstruir o frame: {e}")
                    
                    finally:
                        # Limpa pra esperar as outras 4 partes do próximo frame
                        partes_frame.clear()
            else:
                print(f"Parte do frame inválida recebida de {endereco}")

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

except KeyboardInterrupt:
    print("\nEncerrando o cliente...")
finally:
    cliente_socket.close()
    cv2.destroyAllWindows()
