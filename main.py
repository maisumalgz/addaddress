from flask import Flask, request, jsonify
import routeros_api

app = Flask(__name__)

# Configurações do MikroTik
MK_HOST = 'd4500ecb7a52.sn.mynetname.net'
MK_USER = 'admin'
MK_PASS = 'In3t@2018'
MK_PORT = 8728  # Porta API padrão (pode mudar)

def add_ip_to_list(ip):
    connection = routeros_api.RouterOsApiPool(
        MK_HOST, username=MK_USER, password=MK_PASS, port=MK_PORT, plaintext_login=True
    )
    api = connection.get_api()
    try:
        address_list = api.get_resource('/ip/firewall/address-list')
        existing = address_list.get()

        for entry in existing:
            if entry['address'] == ip and entry['list'] == 'liberados':
                return False, "IP já está na lista."

        address_list.add(address=ip, list='liberados', comment='Adicionado via web')
        return True, "IP adicionado com sucesso."
    finally:
        connection.disconnect()



@app.route('/liberar', methods=['POST'])
def liberar():
    data = request.get_json()
    ip = data.get('ip')
    if not ip:
        return jsonify({'message': 'IP não informado'}), 400

    success, message = add_ip_to_list(ip)
    if success:
        return jsonify({'message': message})
    else:
        return jsonify({'message': message}), 409

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
