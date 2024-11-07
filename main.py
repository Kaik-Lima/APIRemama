from datetime import datetime, timezone
from sqlite3.dbapi2 import Timestamp
from flask import Flask, Response, jsonify, request
from flask_sqlalchemy import SQLAlchemy
import json
import paho.mqtt.client as mqtt

# ********************** CONEXÃO COM O BANCO DE DADOS **********************

app = Flask("sensores")     # Nome do aplicativo.

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False    # Configura o SQLAlchemy para rastrear modificações. 

app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql://root:senai%40134@127.0.0.1/bd_sensores'

mybd = SQLAlchemy(app)      # Cria uma instância do SQLAlchemy, passando a aplicação Flask como parâmetro. 

# *************************** CONEXÃO DOS SENSORES ***************************
mqtt_dados = {}

def conexao_sensor(client, userdata, flags, rc):
    client.subscribe("sensores/dados")


def msg_sensor(client, userdata, msg):
    global mqtt_dados
    
    valor = msg.payload.decode('utf-8')     # Decodificar a mensagem recebida de bytes para string
    mqtt_dados = json.loads(valor)          # Decodificar de string para JSON
    print(f'Mensagem recebida: {mqtt_dados}')

    with app.app_context():         # Correlação Banco de Dados com Sensor. 
        try:
            id_paciente = mqtt_dados.get('id_paciente')
            oximetro_saturacao_oxigenio = mqtt_dados.get('oximetro_saturacao_oxigenio')
            oximetro_frequencia_pulso = mqtt_dados.get('oximetro_frequencia_pulso')
            frequencia_cardiaca = mqtt_dados.get('frequencia_cardiaca')
            temperatura = mqtt_dados.get('temperatura')
            indice_uv = mqtt_dados.get('indice_uv')
            tempo_registro = mqtt_dados.get('timestamp')
            
            if tempo_registro is None:
                print("Timestamp não encontrado")
                return
            
            try:
                tempo_oficial = datetime.fromtimestamp(int(tempo_registro) / 1000, tz=timezone.utc)
            
            except (ValueError, TypeError) as e:
                print(f"Erro ao converter timestamp: {str(e)}")
                return
            # Criar para objeto que vai simular a tabela do banco. 
            novos_dados = Sensores(
                id_paciente = id_paciente,
                oximetro_saturacao_oxigenio = oximetro_saturacao_oxigenio,
                oximetro_frequencia_pulso = oximetro_frequencia_pulso,
                frequencia_cardiaca = frequencia_cardiaca,
                temperatura = temperatura,
                indice_uv = indice_uv,
                tempo_registro = tempo_oficial
            )
            
            # Adicionar novo registro ao banco.
            mybd.session.add(novos_dados)
            mybd.session.commit()
            print("Os dados foram inseridos com sucesso no banco de dados!")
        
        except Exception as e:
            print(f"Erro ao processar os dados do MQTT: {str(e)}")
            mybd.session.rollback()

mqtt_client = mqtt.Client()
mqtt_client.on_connect = conexao_sensor
mqtt_client.on_message = msg_sensor
mqtt_client.connect("test.mosquitto.org", 1883, 60)

def start_mqtt():
    mqtt_client.loop_start()
    
class Sensores(mybd.Model):
    __tablename__ = 'tb_dados'
    id = mybd.Column(mybd.Integer, primary_key=True, autoincrement=True)
    id_paciente = mybd.Column(mybd.String(50), nullable=False)
    tempo_registro = mybd.Column(mybd.DateTime)
    oximetro_saturacao_oxigenio = mybd.Column(mybd.Integer)
    oximetro_frequencia_pulso = mybd.Column(mybd.Integer)
    frequencia_cardiaca = mybd.Column(mybd.Integer)
    temperatura = mybd.Column(mybd.Float(precision=1))
    indice_uv = mybd.Column(mybd.Integer)

    def to_json(self):
        return {
            'id': float(self.id),
            'id_paciente': str(self.id_paciente),
            'tempo_registro': self.tempo_registro.isoformat(),
            'oximetro_saturacao_oxigenio': int(self.oximetro_saturacao_oxigenio),
            'oximetro_frequencia_pulso': int(self.oximetro_frequencia_pulso),
            'frequencia_cardiaca': int(self.frequencia_cardiaca),
            'temperatura': float(self.temperatura),
            'indice_uv': int(self.indice_uv)
        }

# Seleciona todos os registros
@app.route('/sensores', methods=['GET'])
def selecionar_registros():
    sensores = Sensores.query.all()
    sensores_json = [sensores.to_json() for sensores in sensores]
    
    return gera_response(200, 'sensores', sensores_json)


# Seleciona um registro por Id específico
@app.route('/sensores/<id>', methods=['GET'])
def selecionar_registro_por_id(id):
    sensores = Sensores.query.filter_by(id=id).first()
    
    if sensores:
        sensores_json = sensores.to_json()
        return gera_response(200, 'sensores', sensores_json)
    else:
        return gera_response(400, 'sensores', {}, 'Registro não encontrado')
    
# Deleta um registro por Id específico
@app.route('/sensores/<id>', methods=['DELETE'])
def deletar_registro_por_id(id):
    sensores = Sensores.query.filter_by(id=id).first()
    
    if sensores:
        try:
            mybd.session.delete(sensores)
            mybd.session.commit()
            return gera_response(200, 'sensores', sensores.to_json(), 'Registro deletado!')
        except Exception as error:
            print(f'Erro: {error}')
            mybd.session.rollback()
            return gera_response(400, 'sensores', {}, 'Erro ao deletar registro.')
    else:
        return gera_response(400, 'sensores', {}, 'Registro não encontrado.')
        

@app.route('/dados', methods=['GET'])
def busca_dados():
    return jsonify(mqtt_dados)        

    
@app.route('/dados', methods=['POST'])
def criar_dados():
    try:
        dados = request.get_json()
        
        if not dados:
            return jsonify({'error': 'Nenhum dado foi fornecido'}), 400   
        
        print(f'Dados Recebidos": {dados}')
        id_paciente = dados.get('id_paciente')
        oximetro_saturacao_oxigenio = dados.get('oximetro_saturacao_oxigenio')
        oximetro_frequencia_pulso = dados.get('oximetro_frequencia_pulso')
        frequencia_cardiaca = dados.get('frequencia_cardiaca')
        temperatura = dados.get('temperatura')
        indice_uv = dados.get('indice_uv')
        tempo_registro = dados.get('tempo_registro')
    
        try:
            tempo_oficial = datetime.fromtimestamp(int(Timestamp), tz=timezone.utc)
        except Exception as e:
            print('Erro', e)
            return jsonify({'error': 'Timestamp inválido'}), 400 
        
        novo_registro = Sensores(
            id_paciente=id_paciente,
            oximetro_saturacao_oxigenio=oximetro_saturacao_oxigenio,
            oximetro_frequencia_pulso=oximetro_frequencia_pulso,
            frequencia_cardiaca=frequencia_cardiaca,
            temperatura=temperatura,
            indice_uv=indice_uv,
            tempo_registro=tempo_oficial
        )
        
        mybd.session.add(novo_registro)
        print('Adicionando novo registro...')
        
        mybd.session.commit()
        print('Dados inseridos no banco de dados com sucesso!')
        
        return jsonify({'mensagem': 'Dados recebidos com sucesso'}), 201
        
    except Exception as e:
        print(f'Erro ao processar a solicitação', e)
        mybd.session.rollback()
        return jsonify({'erro': 'Falha ao processar os dados'}), 500
    
    
    
def gera_response(status, nome_conteudo, conteudo, mensagem=False):
    body = {}
    body[nome_conteudo] = conteudo

    if(mensagem):
        body["mensagem"] = mensagem

    return Response(json.dumps(body), status=status, mimetype="application/json")


      
if __name__ == '__main__':
    with app.app_context():
        mybd.create_all()
        
        start_mqtt()
        app.run(port=5000, host="localhost", debug=True)