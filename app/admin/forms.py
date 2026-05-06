from flask_wtf import FlaskForm
from wtforms import StringField, SubmitField, FloatField, FileField, PasswordField
from wtforms.validators import DataRequired, Length
from flask_wtf.file import FileAllowed
from wtforms.validators import Optional  # Needed for optional image on edit


class AddItemForm(FlaskForm):
    name = StringField("Name", validators=[DataRequired(), Length(max=100)])

    price = FloatField("Price", validators=[DataRequired()])

    category = StringField("Category", validators=[DataRequired(), Length(max=100)])

    image = FileField(
        "Image",
        validators=[
            Optional(),  # Allows edit without re-upload
            FileAllowed(["jpg", "jpeg", "png", "webp"], "Images only!"),
        ],
    )

    details = StringField("Details", validators=[DataRequired(), Length(max=500)])

    submit = SubmitField("Save")


class AdminLoginForm(FlaskForm):
    email = StringField("Email", validators=[DataRequired()])
    password = PasswordField("Password", validators=[DataRequired()])
    submit = SubmitField("Login")
