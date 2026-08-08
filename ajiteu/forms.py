from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileAllowed
from wtforms import StringField, TextAreaField, TextAreaField, PasswordField, EmailField, MultipleFileField, SubmitField, SelectField
from wtforms.validators import DataRequired, EqualTo, Email, Length

#게시글 등록
class PostForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용을 입력해주세요')])
    image = MultipleFileField('', validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지파일만 업로드 가능합니다')])
    submit = SubmitField('등록하기')

#댓글 등록
class CommentForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용을 입력해주세요')])
    image = MultipleFileField(
        '',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지파일만 업로드 가능합니다')],
    )


class ImageUploadForm(FlaskForm):
    image = MultipleFileField(
        '',
        validators=[FileAllowed(['jpg', 'jpeg', 'png', 'gif'], '이미지파일만 업로드 가능합니다')],
    )

#댓글의 댓글 등록
class ReplyForm(FlaskForm):
    content = TextAreaField('내용', validators=[DataRequired('내용을 입력해주세요')])

# 회원가입 검증용 클래스 추가
class UserCreateForm(FlaskForm):
    username = StringField('사용자 이름', validators=[DataRequired(), Length(min=3, max=25)])
    password1 = PasswordField('비밀번호', validators=[
        DataRequired(),
        EqualTo('password2', message='비밀번호가 일치하지 않습니다.')
    ])
    password2 = PasswordField('비밀번호 확인', validators=[DataRequired()])
    email = EmailField('이메일', validators=[DataRequired(), Email()])


# 로그인 폼 클래스 추가
class UserLoginForm(FlaskForm):
    username  = StringField('사용자 이름', validators=[DataRequired()])
    password = PasswordField('비밀번호', validators=[DataRequired()])


class ProfileForm(FlaskForm):
    nickname = StringField('닉네임', validators=[DataRequired(), Length(max=20)])
    user_intro = TextAreaField('프로필 소개', validators=[Length(max=200)])
    image = FileField('프로필 사진', validators=[FileAllowed(['jpg', 'jpeg', 'png'], '이미지 파일만 업로드 가능합니다.')])