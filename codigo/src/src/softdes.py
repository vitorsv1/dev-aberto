# -*- coding: utf-8 -*-
"""
Created on Wed Jun 28 09:00:39 2017

@author: rauli
"""

from datetime import datetime
import sqlite3
import hashlib
import numbers
from flask import Flask, request, render_template
from flask_httpauth import HTTPBasicAuth


DBNAME = './quiz.db'


def lambda_handler(event):
    """
        Function for running lambda
    """
    try:
        def not_equals(first, second):
            if isinstance(first, numbers.Number) and isinstance(second, numbers.Number):
                return abs(first - second) > 1e-3
            return first != second

        ndes = int(event['ndes'])
        code = event['code']
        args = event['args']
        resp = event['resp']
        diag = event['diag']
        exec(code, locals())

        test = []
        for index, arg in enumerate(args):
            if not 'desafio{0}'.format(ndes) in locals():
                return "Nome da função inválido. Usar 'def desafio{0}(...)'".format(ndes)

            if not_equals(eval('desafio{0}(*arg)'.format(ndes)), resp[index]):
                test.append(diag[index])

        return " ".join(test)
    except KeyError:
        return "Função inválida."


def convert_data(orig):
    """
        Converting Data format
    """
    return orig[8:10]+'/'+orig[5:7]+'/'+orig[0:4]+' '+orig[11:13]+':'+orig[14:16]+':'+orig[17:]


def get_quizes(user):
    """
        Get quizzes
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user in ('admin', 'fabioja'):
        cursor.execute("SELECT id, numb from QUIZ")
    else:
        cursor.execute("SELECT id, numb from QUIZ where release < '{0}'".format(
            datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
    info = list(cursor.fetchall())
    conn.close()
    return info


def get_user_quiz(userid, quizid):
    """
        Getting quiz info from user
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(
        '''SELECT sent,answer,result from USERQUIZ where userid = '{0}'
         and quizid = {1} order by sent desc'''.format(userid, quizid))
    info = list(cursor.fetchall())
    conn.close()
    return info


def set_user_quiz(userid, quizid, sent, answer, result):
    """
        Setting the table UserQuiz
    """

    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("insert into USERQUIZ(userid,quizid,sent,answer,result) values (?,?,?,?,?);",
                   (userid, quizid, sent, answer, result))
    conn.commit()
    conn.close()


def get_quiz(id_user, user):
    """
        Getting quiz from user
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    if user in ('admin', 'fabioja'):
        cursor.execute(
            '''SELECT id, release, expire, problem, tests, results, diagnosis, numb from
             QUIZ where id = {0}'''.format(id_user))
    else:
        cursor.execute(
            '''SELECT id, release, expire, problem, tests, results, diagnosis, numb
            from QUIZ where id = {0} and release < '{1}' '''.format(
                id_user, datetime.now().strftime("%Y-%m-%d-%H-%M-%S")))
    info = list(cursor.fetchall())
    conn.close()
    return info


def set_info(pwd, user):
    """
        Setting password from user in Database
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute("UPDATE USER set pass = ? where user = ?", (pwd, user))
    conn.commit()
    conn.close()


def get_info(user):
    """
        Getting password, type from user in Database
    """
    conn = sqlite3.connect(DBNAME)
    cursor = conn.cursor()
    cursor.execute(
        "SELECT pass, type from USER where user = '{0}'".format(user))
    print("SELECT pass, type from USER where user = '{0}'".format(user))
    info = [reg[0] for reg in cursor.fetchall()]
    conn.close()
    if len(info) == 0:
        return None
    return info[0]


auth = HTTPBasicAuth()
app = Flask(__name__, static_url_path='')
app.secret_key = 'A0Zr98j/3yX R~XHH!jmN]LWX/,?TX'


@app.route('/', methods=['GET', 'POST'])
@auth.login_required
def main():
    """
        Home page
    """
    msg = ''
    post = 1
    challenges = get_quizes(auth.username())
    sent = datetime.now().strftime("%Y-%m-%d-%H-%M-%S")

    if request.method == 'POST' and 'ID' in request.args:
        id_user = request.args.get('ID')
        quiz = get_quiz(id_user, auth.username())
        if len(quiz) == 0:
            msg = "Boa tentativa, mas não vai dar certo!"
            post = 2
            return render_template('index.html', username=auth.username(),
                                   challenges=challenges, p=post, msg=msg)

        quiz = quiz[0]
        if sent > quiz[2]:
            msg = "Sorry... Prazo expirado!"

        file_code = request.files['code']
        filename = './upload/{0}-{1}.py'.format(auth.username(), sent)
        file_code.save(filename)
        with open(filename, 'r', encoding="UTF-8") as file:
            answer = file.read()

        args = {"ndes": id_user, "code": answer, "args": eval(
            quiz[4]), "resp": eval(quiz[5]), "diag": eval(quiz[6])}

        feedback = lambda_handler(args)

        result = 'Erro'
        if len(feedback) == 0:
            feedback = 'Sem erros.'
            result = 'OK!'

        set_user_quiz(auth.username(), id_user, sent, feedback, result)

    if request.method == 'GET':
        if 'ID' in request.args:
            id_user = request.args.get('ID')
        else:
            id_user = 1

    if len(challenges) == 0:
        msg = "Ainda não há desafios! Volte mais tarde."
        post = 2
        return render_template('index.html', username=auth.username(),
                               challenges=challenges, p=post, msg=msg)
    quiz = get_quiz(id_user, auth.username())
    if len(quiz) == 0:
        msg = "Oops... Desafio invalido!"
        post = 2
        return render_template('index.html', username=auth.username(),
                               challenges=challenges, p=post, msg=msg)

    answers = get_user_quiz(auth.username(), id_user)

    return render_template('index.html', username=auth.username(),
                           challenges=challenges, quiz=quiz[0], e=(
                               sent > quiz[0][2]),
                           answers=answers, p=post, msg=msg, expi=convert_data(quiz[0][2]))


@app.route('/pass', methods=['GET', 'POST'])
@auth.login_required
def change():
    """
        Changing actual password
    """
    if request.method == 'POST':
        velha = request.form['old']
        nova = request.form['new']
        repet = request.form['again']

        post = 1
        msg = ''
        if nova != repet:
            msg = 'As novas senhas nao batem'
            post = 3
        elif get_info(auth.username()) != hashlib.md5(velha.encode()).hexdigest():
            msg = 'A senha antiga nao confere'
            post = 3
        else:
            set_info(hashlib.md5(nova.encode()).hexdigest(), auth.username())
            msg = 'Senha alterada com sucesso'
            post = 3
    else:
        msg = ''
        post = 3

    return render_template('index.html', username=auth.username(),
                           challenges=get_quizes(auth.username()), p=post, msg=msg)


@app.route('/logout')
def logout():
    """
        Logout the user
    """
    return render_template('index.html', p=2, msg="Logout com sucesso"), 401


@auth.get_password
def get_password(username):
    """
        Getting password from username
    """
    return get_info(username)


@auth.hash_password
def hash_pw(password):
    """
        Hashing password with MD5
    """
    return hashlib.md5(password.encode()).hexdigest()


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=80)
