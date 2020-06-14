import repository
import dialogflow_v2 as dialogflow
import os
import security
import secrets
import interpreter

def find(json_action, user):
    return repository.find_question(json_action, user)


def find_save(json_action, user):
    if repository.find_point(json_action) == 'save':
        repository.save_answer(json_action, user)
        return repository.find_question(json_action, user)


def process_test(message, user_id, comp_id):
    user = repository.find_user(comp_id, user_id)
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    df_answer = detect_intent_texts(project_id, user, message, 'ru')
    mes_text = df_answer['fulfillmentText']
    json_action = df_answer['action']
    repository.save_message(json_action, message, user)
    find_save(json_action, user)
    response_text = {
        "message": mes_text
    }

    return response_text


def process_web(message, user_id):
    project_id = os.getenv('DIALOGFLOW_PROJECT_ID')
    df_answer = detect_intent_texts(project_id, "unique", message, 'ru')
    mes_text = df_answer['fulfillmentText']
    json_action = df_answer['action']
    find_save(json_action, user_id)
    response_text = {
        "message": mes_text
    }
    return response_text


def detect_intent_texts(project_id, session_id, text, language_code):
    session_client = dialogflow.SessionsClient()
    session = session_client.session_path(project_id, session_id)

    if text:
        text_input = dialogflow.types.TextInput(
            text=text, language_code=language_code)
        query_input = dialogflow.types.QueryInput(text=text_input)
        df_response = session_client.detect_intent(
            session=session, query_input=query_input)

        response = {
            "fulfillmentText": df_response.query_result.fulfillment_text,
            'action': df_response.query_result.action,
            "session_id": session_id
        }

        return response


def get_profile(comp_id, user_id, test):
    user = repository.find_user_profile(comp_id, user_id)
    profile = repository.get_profile(user, test)
    if profile == "null":
        score_answer = repository.score_answer(user, test)
        score_const = repository.score_const(test)
        if score_const == score_answer:
            answer = repository.get_answer(user, test)
            result = interpreter.get_profile(user, test, answer)
            return repository.get_profile(user, test)
        else:
            return "Тест не завершен"
    else:
        return profile


def login(login, password):
    sec_password = security.hash_password(password)
    key = secrets.token_urlsafe(16)
    sec_key = security.encoded_key(key)
    repository.save_company(login, sec_password, sec_key)
    return "Ваш API Key: " + key


def sign(login, password):
    db_password = repository.get_password(login)
    return security.check_password(password, db_password)


def api_key(bool_pass):
    if str(bool_pass) == "True":
        key = secrets.token_urlsafe(16)
        return key
    elif str(bool_pass) == "False":
        return "no"


def check_key(key):
    enc_key = security.encoded_key(key)
    comp_id = repository.get_comp_id(enc_key)
    return comp_id


def new_api_key(login, new_key):
    enc_key = security.encoded_key(new_key)
    repository.update_key(login, enc_key)
