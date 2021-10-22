from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.fields.html5 import EmailField

class form_login():
    usuario = EmailField()
    password = PasswordField()
    btnIngreso = SubmitField()
    lnkRestablecer = SubmitField()
    btnRegistro = SubmitField()