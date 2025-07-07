from flask import Flask, request, jsonify
from flask_cors import CORS
import routeros_api
import os

app = Flask(__name__)
CORS(app)

# Configs Render
MK_HOST = os.environ.get('MK_HOST')
MK_USER = os.environ.get('MK_USER')
MK_PASS = os.environ.get('MK_PASS')
MK_PORT = 8728
APP_USER = os.environ.get("APP_USER")
APP_PASS = os.environ.get("APP_PASS")

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

        address_list.add(**{
            'address': ip,
            'list': 'Liberados',
            'comment': 'Adicionado via web',
            'timeout': '1h'
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
        
@app.route('/verificar', methods=['POST'])
def verificar():
    data = request.get_json()
    ip = data.get('ip')
    if not ip:
        return jsonify({'liberado': False, 'message': 'IP não informado'}), 400

    try:
        connection = routeros_api.RouterOsApiPool(
            MK_HOST, username=MK_USER, password=MK_PASS, port=MK_PORT, plaintext_login=True
        )
        api = connection.get_api()
        address_list = api.get_resource('/ip/firewall/address-list')
        existing = address_list.get()

        for entry in existing:
            if entry['address'] == ip and entry['list'].lower() == 'liberados':
                timeout = entry.get('timeout', 'indefinido')
                return jsonify({
                    'liberado': True,
                    'message': 'IP já está liberado',
                    'timeout': timeout
                }), 200

        return jsonify({'liberado': False, 'message': 'IP não está liberado'}), 200

    except Exception as e:
        print("Erro ao verificar IP:", e)
        return jsonify({'liberado': False, 'message': 'Erro ao conectar ao MikroTik'}), 500

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

@app.route('/login', methods=['POST'])
def login():
    data = request.get_json()
    username = data.get('username')
    password = data.get('password')

    if username == APP_USER and password == APP_PASS:
        return jsonify({"success": True}), 200
    else:
        return jsonify({"success": False, "message": "Credenciais inválidas"}), 401

import os
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)