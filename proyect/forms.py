from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed, FileSize
from wtforms import StringField, IntegerField, DecimalField, SubmitField, PasswordField, EmailField, BooleanField
from wtforms.validators import DataRequired, NumberRange, Length, Email, EqualTo, ValidationError
from models import Usuario

# Formulario para productos con validaciones para cada campo
class ProductoForm(FlaskForm):
    nombre = StringField('Nombre', validators=[DataRequired(), Length(max=120)])
    cantidad = IntegerField('Cantidad', validators=[DataRequired(), NumberRange(min=0)])
    precio = DecimalField('Precio', places=2, validators=[DataRequired(), NumberRange(min=0)])
    imagen = FileField('Imagen del Producto', validators=[
        FileAllowed(['jpg', 'jpeg', 'png', 'gif', 'webp'], 'Solo se permiten imágenes (JPG, JPEG, PNG, GIF, WEBP)'),
        FileSize(max_size=5*1024*1024, message='El archivo debe ser menor a 5MB')
    ])
    submit = SubmitField('Guardar')

# Formulario para registro de usuarios
class RegistroForm(FlaskForm):
    username = StringField('Nombre de Usuario', validators=[
        DataRequired(message='El nombre de usuario es obligatorio'),
        Length(min=3, max=80, message='El nombre de usuario debe tener entre 3 y 80 caracteres')
    ])
    email = EmailField('Correo Electrónico', validators=[
        DataRequired(message='El correo electrónico es obligatorio'),
        Email(message='Ingresa un correo electrónico válido'),
        Length(max=120, message='El correo electrónico es demasiado largo')
    ])
    nombre_completo = StringField('Nombre Completo', validators=[
        DataRequired(message='El nombre completo es obligatorio'),
        Length(min=2, max=120, message='El nombre completo debe tener entre 2 y 120 caracteres')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria'),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(message='Debes confirmar la contraseña'),
        EqualTo('password', message='Las contraseñas no coinciden')
    ])
    submit = SubmitField('Registrarse')

    def validate_username(self, username):
        usuario = Usuario.get_by_username(username.data)
        if usuario:
            raise ValidationError('Este nombre de usuario ya está en uso. Elige otro.')

    def validate_email(self, email):
        usuario = Usuario.get_by_email(email.data)
        if usuario:
            raise ValidationError('Este correo electrónico ya está registrado. Usa otro.')

# Formulario para inicio de sesión
class LoginForm(FlaskForm):
    username = StringField('Nombre de Usuario o Email', validators=[
        DataRequired(message='El nombre de usuario o email es obligatorio')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(message='La contraseña es obligatoria')
    ])
    remember_me = BooleanField('Recordarme')
    submit = SubmitField('Iniciar Sesión')
