import datetime
import random

from pymongo import MongoClient
import encoder
import configparser

config = configparser.ConfigParser()
config.read("settings.ini")

client = MongoClient(config["MongoDB"]["Client"])
mydb = client['hr_project']


def find_question(json_action, user):
    list_question = list(mydb.question.find({'action': json_action}))
    available_questions = []

    for question in list_question:
        q_number = question['number']
        q_test = question['test']
        q_answer = find_answer(number=q_number, test=q_test, user=user)
        if q_answer is None:
            available_questions.append(question)

    if len(available_questions) != 0:
        chosen_question = random.choice(available_questions)
        return chosen_question['text']
    else:
        return "Вопросов нет"


def find_answer(number, test, user):
    return mydb.answer.find_one({'number': number, "test": test, "user": user})


def save_answer(json_action, user):
    number = mydb.question.find_one({'action': json_action}, {'_id': 0, 'number': 1})['number']
    test = mydb.question.find_one({'action': json_action}, {'_id': 0, 'test': 1})['test']
    answer = mydb.question.find_one({'action': json_action}, {'_id': 0, 'answer': 1})['answer']
    json_answer = {
        "user": user,
        "number": number,
        "test": test,
        "answer": answer
    }
    mydb.answer.insert(json_answer, check_keys=False)


def find_point(json_action):
    return mydb.question.find_one({'action': json_action}, {'_id': 0, 'act': 1})['act']


def get_answer(user, test):
    bson_answer = list(
        mydb.answer.find({'test': test, 'user': user}, {'_id': 0, 'number': 1, 'answer': 1}).sort('number',
                                                                                                  1))
    json_answer = encoder.JSONEncoder().encode(bson_answer)
    return json_answer


def get_users():
    bson_users = list(mydb.user.find())
    json_users = encoder.JSONEncoder().encode(bson_users)
    return json_users


def save_profile(user, test):
    profile = {
        "user": user,
        "test": test,
        "result": "Результат"
    }
    mydb.profile.insert(profile, check_keys=False)


def get_profile(user, test):
    bson_profile = mydb.profile.find_one({"user": user, "test": test}, {"_id": 0, "test": 1, "result": 1})
    json_profile = encoder.JSONEncoder().encode(bson_profile)
    return json_profile


def get_login(login):
    bson = mydb.company.find_one({'login': login}, {'_id': 0, 'login': 1})['login']
    json = encoder.JSONEncoder().encode(bson)
    return json


def get_company(login):
    bson = mydb.company.find_one({'login': login}, {'_id': 0})
    json = encoder.JSONEncoder().encode(bson)
    return json


def get_id(login):
    bson = mydb.company.find_one({'login': login}, {'_id': 1})['_id']
    json = encoder.JSONEncoder().encode(bson)
    return json


def get_password(login):
    bson = mydb.company.find_one({'login': login}, {'_id': 0, 'password': 1})['password']
    json = encoder.JSONEncoder().encode(bson)
    return bson


def save_company(login, sec_password, sec_key):
    company = {
        "login": login,
        "password": sec_password,
        "key": sec_key

    }
    mydb.company.insert(company, check_keys=False)


def get_comp_id(enc_key):
    obj = mydb.company.find_one({'key': enc_key})
    if str(obj) == 'None':
        return str(obj)
    else:
        return str(mydb.company.find_one({'key': enc_key}, {'_id': 1})['_id'])


def save_message(json_action, message, user):
    mes = {
        "user": user,
        "action": json_action,
        "message": message,
        "date": datetime.datetime.utcnow()

    }

    mydb.discourse.insert(mes, check_keys=False)


def find_user(comp_id, user_id):
    data = mydb.user.find_one({'comp_id': comp_id, 'user_id': user_id})
    if str(data) == "None":
        return save_user(comp_id, user_id)
    else:
        return str(mydb.user.find_one({'comp_id': comp_id, 'user_id': user_id}, {'_id': 1})['_id'])


def save_user(comp_id, user_id):
    user = {
        "comp_id": comp_id,
        "user_id": user_id
    }
    mydb.user.insert(user, check_keys=True)
    return str(mydb.user.find_one({'comp_id': comp_id, 'user_id': user_id}, {'_id': 1})['_id'])


def find_user_profile(comp_id, user_id):
    return str(mydb.user.find_one({'comp_id': comp_id, 'user_id': user_id}, {'_id': 1})['_id'])

def update_key(login, enc_key):
    mydb.company.update({'login': login}, {"$set": {"key": enc_key}})


def score_answer(user, test):
    return str(mydb.answer.find({"test": test, "user": user}).count())


def score_const(test):
    return str(mydb.question.find_one({'test': test}, {'_id': 0, 'score': 1})['score'])
