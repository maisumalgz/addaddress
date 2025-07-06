from flask import Flask, request, jsonify
from flask_cors import CORS  # << importar isso
import routeros_api
import os

app = Flask(__name__)
CORS(app)  # << ESSENCIAL: Ativar o CORS logo após o app

# Config MikroTik
MK_HOST = 'd4500ecb7a52.sn.mynetname.net'
MK_USER = 'admin'
MK_PASS = 'In3t@2018'
MK_PORT = 8728

def add_ip_to_list(ip):
    try:
        print(f"Tentando conectar ao MikroTik: {MK_HOST}")
        connection = routeros_api.RouterOsApiPool(
            MK_HOST, username=MK_USER, password=MK_PASS, port=MK_PORT, plaintext_login=True
        )
        api = connection.get_api()
        address_list = api.get_resource('/ip/firewall/address-list')
        existing = address_list.get()

        for entry in existing:
            if entry['address'] == ip and entry['list'] == 'liberados':
                print("IP já está na lista.")
                return False, "IP já está na lista."

        address_list.add({
            'address': ip,
            'list': 'liberados',
            'comment': 'Adicionado via web'
        })

        print("IP adicionado com sucesso.")
        return True, "IP adicionado com sucesso."

    except Exception as e:
        print("❌ Erro ao adicionar IP:", e)
        return False, "Erro ao se conectar ao MikroTik."

    finally:
        try:
            connection.disconnect()
        except:
            pass

@app.route('/')
def index():
    return "API está rodando!", 200

@app.route('/liberar', methods=['POST'])
def liberar():
    data = request.get_json()
    print("Recebido do front:", data)

    ip = data.get('ip')
    if not ip:
        return jsonify({'message': 'IP não informado'}), 400

    success, message = add_ip_to_list(ip)
    print("Resultado:", success, message)

    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'message': message}), 409

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
