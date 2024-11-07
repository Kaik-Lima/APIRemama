// Importa a classe Thread da linguagem Java para usar o método sleep (pausa)
var Thread = Java.type("java.lang.Thread");

// Define o tópico MQTT, o tempo de espera entre cada envio (2 segundos) e o número de iterações (100)
var topic = "sensores/dados"; // Tópico MQTT onde o payload será publicado
var waitTime = 2000; // Tempo de espera (em milissegundos) entre cada envio
var iterations = 9999999999; // Número de vezes que o payload será enviado

// Função principal que será executada quando o script rodar
function execute(action) {
    // Exibe uma mensagem indicando o início do script e o nome da ação executada
    out("Teste de Script: " + action.getName());
    
    // Loop que será executado 100 vezes (ou o valor definido em iterations)
    for (var i = 0; i < iterations; i++) {
        sendPayload(); // Chama a função que envia o payload com os dados
        Thread.sleep(waitTime); // Faz uma pausa de 2 segundos (waitTime) antes de continuar
    }

    // Define o código de saída da ação como 0 (indica sucesso) e o resultado final como "done"
    action.setExitCode(0);
    action.setResultText("done.");
    
    // Exibe uma mensagem indicando que o script terminou
    out("Test Script: Done");
    
    // Retorna o objeto action para encerrar a função principal
    return action;
}

// Função responsável por gerar e enviar o payload MQTT
function sendPayload() {
    // Gera valores aleatórios para oximetria, frequência cardíaca, temperatura, índice UV e dados inerciais
    var oximetroSaturacao = Math.floor(Math.random() * 100) + 1; // Saturação de oxigênio entre 1 e 100
    var oximetroFrequencia = Math.floor(Math.random() * 100) + 60; // Frequência de pulso entre 60 e 159
    var frequenciaCardiaca = Math.floor(Math.random() * 100) + 60; // Frequência cardíaca entre 60 e 159
    var temperatura = (Math.random() * (37 - 35) + 35).toFixed(1); // Temperatura entre 35 e 37
    var indiceUV = Math.floor(Math.random() * 10); // Índice UV entre 0 e 9

    // Gera dados para 6 sensores inerciais
    var sensoresInerciais = [];
    for (var j = 1; j <= 6; j++) {
        sensoresInerciais.push({
            id_sensor: j,
            acelerometro_eixo_x: (Math.random() * 0.1 - 0.05).toFixed(2), // Variação em torno de 0
            acelerometro_eixo_y: (Math.random() * 0.1 - 0.05).toFixed(2),
            acelerometro_eixo_z: (Math.random() * 0.1 + 0.9).toFixed(2), // Próximo de 1g
            giroscopio_eixo_x: (Math.random() * 1 - 0.5).toFixed(2), // Variação em torno de 0
            giroscopio_eixo_y: (Math.random() * 1 - 0.5).toFixed(2),
            giroscopio_eixo_z: (Math.random() * 1 - 0.5).toFixed(2)
        });
    }

    // Cria um objeto contendo os dados gerados
    var IoT_Payload = {
        id_paciente: '123456',
        timestamp: Date.now(),
        oximetro_saturacao_oxigenio: oximetroSaturacao,
        oximetro_frequencia_pulso: oximetroFrequencia,
        frequencia_cardiaca: frequenciaCardiaca,
        temperatura: temperatura,
        indice_uv: indiceUV,
        sensores_inerciais: sensoresInerciais
    };

    // Converte o objeto IoT_Payload em uma string no formato JSON
    var payload = JSON.stringify(IoT_Payload);

    // Publica o payload no tópico MQTT definido
    mqttManager.publish(topic, payload);
    
    // Exibe no console o tópico e o payload que foram enviados
    out("Tópico: " + topic);
    out("Payload enviado: " + payload);
}

// Função auxiliar para exibir mensagens no console
function out(message) {
    output.print(message); // Imprime a mensagem recebida na saída padrão
}