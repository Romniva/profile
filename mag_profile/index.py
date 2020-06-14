from flask import Flask, request, jsonify, render_template
import service
import utils

app = Flask(__name__)


@app.route('/')
def index():
    return render_template('index.html')


# run Flask app
if __name__ == "__main__":
    app.run(ssl_context=('cert.pem', 'key.pem'))


# получить сообщение клиента
@app.route('/df_profile/api/v1/question', methods=['POST'])
def send():
    req_json = request.get_json(silent=True)
    key = request.headers.get("Authorization")
    message = req_json['message']
    user_id = req_json['user_id']
    comp_id = service.check_key(key)
    if comp_id == "None":
        return "Аутентификация не пройдена"
    else:
        found = service.process_test(message, user_id, comp_id)
        # return "hgyudj"
        return jsonify(found)


# получить сообщение от DF
@app.route('/df_profile/api/v1/webhook', methods=['POST'])
def action():
    print("WEBHOOK")
    req_json = request.get_json(silent=True)

    session = req_json['session']
    user = utils.substring_after_last(session, '/')
    print(user)

    json_action = req_json['queryResult']['action']
    found_text = service.find(json_action, user)
    # service.find(json_action)
    reply = {
        "fulfillmentText": found_text
    }
    return jsonify(reply)


# передать профиль корпоративной системе
@app.route('/df_profile/api/v1/profile/<user_id>/<test>', methods=['GET'])
def get_profile(user_id, test):
    key = request.headers.get("Authorization")
    comp_id = service.check_key(key)
    if comp_id == "None":
        return "Аутентификация не пройдена"
    else:
        found = service.get_profile(comp_id, user_id, test)
        return found


# отправить сообщение из веб версии
@app.route('/send_message', methods=['POST'])
def send_message():
    message = request.form['message']
    user_id = "Web Test"
    found = service.process_web(message, user_id)
    return jsonify(found)


# зарегистрироваться и получить ключ доступа
@app.route('/df_profile/api/v1/login', methods=['POST'])
def login():
    req_json = request.get_json(silent=True)
    login = req_json['login']
    password = req_json['password']
    return jsonify(service.login(login, password))


# обновить API Key
@app.route('/df_profile/api/v1/update', methods=['POST'])
def update():
    req_json = request.get_json(silent=True)
    login = req_json['login']
    password = req_json['password']
    bool_check = str(service.sign(login, password))
    new_key = service.api_key(bool_check)
    if new_key == "no":
        return "Аутентификация не пройдена"
    else:
        service.new_api_key(new_key, login)
        return jsonify("Ваш API Key: " + new_key)
