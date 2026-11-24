import os
from datetime import datetime, timezone

from flask import Flask, render_template, redirect, url_for, flash
from flask_bootstrap import Bootstrap
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
from flask_wtf import FlaskForm
from wtforms import StringField, TextAreaField, SubmitField
from wtforms.validators import DataRequired, Length

basedir = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'chave-local-de-desenvolvimento')
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get(
    'DATABASE_URL', 'sqlite:///' + os.path.join(basedir, 'data.sqlite'))
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

bootstrap = Bootstrap(app)
moment = Moment(app)
db = SQLAlchemy(app)

ALUNO = 'Leandro Kauã dos Santos'
PRONTUARIO = 'PT3037649'


class Curso(db.Model):
    __tablename__ = 'cursos'
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(64), unique=True, index=True, nullable=False)
    descricao = db.Column(db.String(250))

    def __repr__(self):
        return f'<Curso {self.nome}>'


class CursoForm(FlaskForm):
    nome = StringField('Qual é o nome do curso?',
                       validators=[DataRequired(), Length(1, 64)])
    descricao = TextAreaField('Descrição (250 caracteres)',
                              validators=[Length(max=250)])
    submit = SubmitField('Cadastrar')


def agora_utc():
    # Flask-Moment espera datetime "ingênuo" em UTC e converte para o horário local do navegador
    return datetime.now(timezone.utc).replace(tzinfo=None)


with app.app_context():
    db.create_all()


@app.route('/')
def index():
    return render_template('index.html', aluno=ALUNO, prontuario=PRONTUARIO,
                           current_time=agora_utc())


@app.route('/cursos', methods=['GET', 'POST'])
def cursos():
    form = CursoForm()
    if form.validate_on_submit():
        nome = form.nome.data.strip()
        if Curso.query.filter_by(nome=nome).first():
            flash(f'O curso "{nome}" já está cadastrado.')
        else:
            db.session.add(Curso(nome=nome, descricao=form.descricao.data.strip()))
            db.session.commit()
            flash('Curso cadastrado com sucesso!')
        return redirect(url_for('cursos'))
    lista = Curso.query.order_by(Curso.id).all()
    return render_template('cursos.html', form=form, cursos=lista)


# Módulos não desenvolvidos (Professores, Disciplinas, Alunos, Ocorrências)
# não possuem rota: o tratamento de erro 404 exibe "Não disponível".
@app.errorhandler(404)
def page_not_found(e):
    return render_template('nao_disponivel.html', current_time=agora_utc()), 404


@app.errorhandler(500)
def internal_server_error(e):
    return render_template('500.html', current_time=agora_utc()), 500


if __name__ == '__main__':
    app.run(debug=True)
