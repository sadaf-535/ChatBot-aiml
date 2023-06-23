from flask import Flask, render_template, request, jsonify
from nltk.sentiment import SentimentIntensityAnalyzer
import nlp_part
from aiml import Kernel
import os, pytholog
from py2neo import Graph
from mlnb import predict_gender
from relation import create_Node,relationships,create_relation
from Webscrapping import scrape_wikipedia
from datetime import datetime, date


app = Flask(__name__)
graph = Graph("bolt://localhost:7687",auth=("neo4j","12345678"))
knowledge_base = pytholog.KnowledgeBase('KB')
knowledge = [
    'father(X, Y):- male(X), parent(X, Y)',
    'mother(X, Y):- female(X), parent(X, Y)',
    'child(X, Y):- parent(Y, X)'
]
knowledge_base(knowledge)

check_siginday = False
total_days = 0
user = ''

def get_totaldays(cr_date):
    global total_days
    joining_date = date.fromisoformat(cr_date)
    current_date = date.today()
    total_days = (current_date - joining_date).days

@app.route('/')
def home():
    return render_template('login.html')
        
@app.route("/signup")
def sign_up():
    return render_template('signup.html')

@app.route('/bot')
def bot():
    return render_template('home.html')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        global check_siginday, user
        email = request.form.get('your_email')
        pass1 = request.form.get('your_pass')
        ipAdrres = nlp_part.getIpAdrress()
        signedin_date = str(date.today())
        cr_date = graph.run(
            f"MATCH (n:OWNER{{email: \"{email}\", password: \"{pass1}\"}}) return n.accout_creation_time")
        cr_date = list(cr_date)
        cr_date = cr_date[0][0]
        get_totaldays(cr_date[:10])
        last_date = graph.run(
            f"MATCH (n:OWNER{{email: \"{email}\", password: \"{pass1}\"}}) return n.signedin_at")
        last_date = list(last_date)
        last_signedin = last_date[0][0]
        print("last_signedin", last_signedin)
        if last_signedin == signedin_date:
            check_siginday = True
        email_ver0 = graph.run(
            f"MATCH (n:OWNER{{email: \"{email}\", password: \"{pass1}\"}}) set n.Ip= \"{ipAdrres}\" set n.signedin_at= \"{signedin_date}\" return n.email")
        usr_name = graph.run(
            f"MATCH (n:OWNER{{email: \"{email}\", password: \"{pass1}\"}}) return n.name")
        email_ver_list = list(email_ver0)
        email_ver = email_ver_list[0][0]
        usr_name = list(usr_name)
        username = usr_name[0][0]
        my_bot.setPredicate('name', username)
        user = username
        if email == email_ver:
            return render_template("home.html")
    return render_template("login.html")

    
@app.route('/signup', methods=['POST'])
def signup():
    if request.method == 'POST':
        username = str(request.form.get('name'))
        email = str(request.form.get('email'))
        pass1 = str(request.form.get('pass'))
        my_bot.setPredicate('name', username)
        created_at = str(datetime.now())[0:16]
        username = username.split(" ")
        print(username[0], type(username[0]))
        gender=predict_gender(username[0])
        graph.run(
            f"MERGE(n:OWNER{{name: \"{username[0]}\", email: \"{email}\", password: \"{pass1}\",gender: \"{gender}\" , accout_creation_time: \"{created_at}\"}})")
        return render_template("login.html")

my_bot = Kernel()
def load_aiml_files():
    aiml_directory = "data1"
    aiml_files = [os.path.join(aiml_directory, file) for file in os.listdir(aiml_directory) if file.endswith(".aiml")]
    for aiml_file in aiml_files:
        my_bot.learn(aiml_file)
load_aiml_files()
my_bot.respond('reset questions')
my_bot.respond('reset facts')
def set_fact(fact, value, value2=None):
    if value2:
        new_fact = fact + '(' + value.lower() + ',' + value2.lower() + ')'
    else:
        new_fact = fact + '(' + value.lower() + ')'

    knowledge.insert(0, new_fact)
    knowledge_base(knowledge)
    my_bot.respond('reset facts')


def query_kb(fact, value):
    my_bot.respond('reset questions')
    query = fact + '(X, ' + value.lower().strip() + ')'
    result = knowledge_base.query(pytholog.Expr(query))

    response = ''
    for value in result:
        try:
            response += value['X'].title() + ', '
        except:
            return None
    
    return response[:-2]

def check_predicates():
    male = my_bot.getPredicate('male')
    female = my_bot.getPredicate('female')
    parent = my_bot.getPredicate('parent')
    child = my_bot.getPredicate('child')
    father_of = my_bot.getPredicate('father_of')
    mother_of = my_bot.getPredicate('mother_of')
    child_of = my_bot.getPredicate('child_of')

    result = None

    if male != '':
        set_fact('male', male)
    elif female != '':
        set_fact('female', female)
    elif parent != '':
        set_fact('parent', parent, child)
    elif father_of != '':
        result = query_kb('father', father_of)
    elif mother_of != '':
        result = query_kb('mother', mother_of)
    elif child_of != '':
        result = query_kb('child', child_of)
    
    return result

def chat_bot(message):
    try:
        response = my_bot.respond(message)
        result = check_predicates()
        if result:
            response = result
        if response == "unknown":
            response = None
    except Exception as e:
        print("Error:", e)
        response = None
    return response

@app.route("/get")
def get_bot_response():
    global user
    query = request.args.get('msg')
    query = nlp_part.autospellcorrect(query)
    sents = nlp_part.sent_tokenize(query)
    values = nlp_part.chart(query)
    response = ''
    bot_response = ''
    # this is for social networking change it according to requiremnets
    # ipAdrres = nlp_part.getIpAdrress()
    # if random.random() < 0.2:
    #     try:
    #         relative_person = graph.run(
    #             f"MATCH (n:OWNER{{Ip: \"{ipAdrres}\"}}) where n.name <> \"{user}\" return n.name")
    #         relative_person = list(relative_person)
    #         relative_person = relative_person[0][0]
    #         if relative_person:
    #             try:
    #                 query = f"MATCH (person1:OWNER {{name: '{user}'}})-[r]-(person2:OWNER {{name: '{relative_person}'}})RETURN r"
    #                 result = graph.run(query)
    #                 result = str(result)
    #                 if result != "(No data)":
    #                     result = list(result)
    #                     result_Str = str(result[0][0])
    #                     relation = result_Str[result_Str.index(
    #                         ':')+1:result_Str.index('{')]
    #                     print(relation)
    #                 else:
    #                     response = response + \
    #                         f" Do you know {relative_person}? "
    #             except:
    #                 None
    #     except:
    #         None
    prev_response = ""
    for query in sents:
        query = nlp_part.autospellcorrect(query)
        nlp_part.Ner(query,user)
        print("query",query)
        bot_response = chat_bot(query)
        response = response + '' + bot_response
        # web scrapping and wordnet
        if response == '' or "unknown" in response or "I have never been asked that before." in response or "tried searching the web?" in response or "no answer for that" in response or "do not know" in  response or "deeper algorithm" in response or "My brain contains more than 22,000 patterns, but not one that matches your last input." in response or "do not recognize" in response or "I need time to formulate the reply." in response:
            response = ''
            web_resonse = scrape_wikipedia(query)
            if web_resonse:
                prev_response = prev_response +''+web_resonse
                response =response +""+ prev_response
            else:
                r =nlp_part.sent_tokenize(response)[0]
                Postags = nlp_part.pos_tag(nlp_part.word_tokenize(r))
                for tag in Postags:
                    if tag[1].startswith('N') or  tag[1].startswith('V') :
                        prev_response = prev_response + "" + nlp_part.get_definition(tag[0])
                        response =response +""+ prev_response
        else:
            prev_response +=response
            response = prev_response
        prev_response = response

    if check_siginday:
        filename = f"episode_{total_days}.txt"
        with open(f'chatting/{filename}', 'a') as chat:
            chat.write(f"{user} : {query}\n")
            chat.write(f"Bot : {response}\n")
    else:
        filename = f"episode_{total_days}.txt"
        with open(f'chatting/{filename}', 'a') as chat:
            chat.write(f"{user} : {query}\n")
            chat.write(f"Bot : {response}\n")
    reply = []
    if response:
        reply.append(response)
        reply.append(values)
        return jsonify(reply)
    else:
        reply.append(" : )")
        reply.append(values)
        return jsonify(reply)

if __name__ == "__main__":
    app.run(debug=True, host='0.0.0.0', port='8000')