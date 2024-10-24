from flask import Flask, render_template, request, redirect
from models import db, Question

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///questions.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

with app.app_context():
    db.create_all()

@app.route('/')
def index():
    questions = Question.query.all()
    return render_template('index.html', questions=questions)

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    question = Question.query.get_or_404(question_id)
    if request.method == 'POST':
        answer = request.form['answer']
        print(f'User  answer: {answer}') 
        return redirect('/')
    return render_template('question.html', question=question)

@app.route('/add_question', methods=['GET', 'POST'])
def add_question():
    if request.method == 'POST':
        text = request.form['text']
        option1 = request.form['option1']
        option2 = request.form['option2']
        option3 = request.form['option3']
        option4 = request.form['option4']
        correct_answer = request.form['correct_answer']

        new_question = Question(text=text, option1=option1, option2=option2,
                                option3=option3, option4=option4,
                                correct_answer=correct_answer)
        db.session.add(new_question)
        db.session.commit()
        return redirect('/')
    return render_template('add_question.html')

@app.route('/delete_question/<int:question_id>', methods=['POST'])
def delete_question(question_id):
    question = Question.query.get_or_404(question_id)
    db.session.delete(question)
    db.session.commit()
    return redirect('/')


if __name__ == '__main__':
    app.run(debug=True)

