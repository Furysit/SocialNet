from flask import redirect,render_template, url_for, request, flash, session, current_app, send_from_directory, jsonify
from flask_login import login_user,logout_user, login_required, current_user
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask_socketio import send
import os

from sweater import app,db, socketio
from sweater.models import User,News,Comment,Gender,User_info, Message

@app.route('/')
def index():
    if current_user.is_authenticated:
        return redirect(url_for('main'))
    return render_template('index.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
    login = request.form.get('login')
    password = request.form.get('password')
    if login and password:
        user = User.query.filter_by(login=login).first()
        if user and check_password_hash(user.password, password):
            login_user(user)
            return redirect(url_for('main'))
        else:
            flash(message='Ошибка, пароли не совпадают')
    else:
        flash(message='Ошибка, неправильные поля')
    return render_template('login.html')

@app.route('/register', methods = ['GET', 'POST'])
def register():
    login = request.form.get('login')
    email = request.form.get('email')
    password = request.form.get('password')
    if request.method == 'POST':
        if not (login or password or email):
            flash(message='Ошибка, неправильные поля')
        else:
            try:
                hash_pwd = generate_password_hash(password)
                new_user = User(login= login, email = email, password= hash_pwd)
                db.session.add(new_user)
                db.session.commit()
            except Exception as e:
                db.session.rollback()
                flash(message=f'Ошибка при сохранении в базу данных: {e}')
                return redirect(url_for('register'))
            flash(message='Успех')
            return redirect(url_for('login'))
    return render_template('register.html')

@login_required 
@app.route('/logout')
def logout():
    logout_user()
    return redirect(url_for('login'))

#######################################################################################################################################

@app.route('/main')
@login_required
def main():
    news = News.query.order_by(News.date.desc()).all()
    return render_template('main.html', username=current_user.login, news=news )


@app.route('/new/<int:news_id>', methods = ['GET','POST'])
@login_required
def show_new(news_id):
    new = News.query.get_or_404(news_id)

    if request.method == 'POST':
        comment_text = request.form['comment']
        comment = Comment(text=comment_text, news_id=new.id, user_id=current_user.id)
        try:
            db.session.add(comment)
            db.session.commit()
            flash('Комментарий добавлен.')
        except:
            db.session.rollback()
            flash('Ошибка при добавлении комментария.')
    
    comments = Comment.query.filter_by(news_id=new.id).all()
    return render_template('new.html', username=current_user.login, new=new, comments=comments)


@app.route('/chat')
@login_required
def chat():
    return render_template('chat.html', username=current_user.login)


@socketio.on('message')
def handle_message(data):
    # Проверяем, что данные содержат нужные поля
    if 'username' in data and 'text' in data:
        username = data['username']
        text = data['text']

        # Сохраняем сообщение в БД
        new_message = Message(username=username, text=text)
        db.session.add(new_message)
        db.session.commit()

        # Отправляем сообщение обратно всем подключенным клиентам
        send({
            'username': username,
            'text': text,
            'timestamp': new_message.timestamp.strftime('%A %H:%M')
        }, broadcast=True)
    else:
        print("Received malformed data:", data)

# Отправка последних 15 сообщений
@app.route('/messages')
def get_messages():
    messages = Message.query.order_by(Message.timestamp.desc()).limit(15).all()
    return jsonify([{
        'username': message.username,
        'text': message.text,
        'timestamp': message.timestamp.strftime('%A %H:%M')
    } for message in reversed(messages)])

@app.route('/user/<user>')
@login_required
def user(user):
    current_user = User.query.filter_by(login=user).first()

    if current_user is None:
        return url_for('main')# Если пользователь с таким логином не найден, возвращаем 404 ошибку или делаем что-то другое
          # Вернуть страницу 404

    # Теперь используем ID пользователя для получения новостей и информации
    user_news = News.query.filter_by(author_id=current_user.id).order_by(News.timestamp.desc()).all()
    user_info = User_info.query.filter_by(user_id=current_user.id).all()

    return render_template('user.html', user=current_user, news=user_news, user_info=user_info, email = current_user.email, username = user)


@app.route('/create_news', methods = ['POST', 'GET'])
@login_required
def create_news():
    # if request.method == "POST":
    #     title = request.form['title']
    #     text = request.form['text']
    #     new = News(title = title, text = text, author_id=current_user.id)

    #     try:
    #         db.session.add(new)
    #         db.session.commit()
    #         return redirect(url_for('main'))
    #     except:
    #         flash(message='Ошибка при добавлении')
    # else:
    #     flash(message='Ошибка')
    # return render_template('create_news.html')
    
    if request.method == "POST":
        title = request.form['title']
        text = request.form['text']
        
        media_file = request.files['media']
        if media_file and media_file.filename != '':
            # Генерируем безопасное имя файла
            filename = secure_filename(media_file.filename)
            # Определяем директорию для сохранения файла
            upload_folder = 'static/saved_images'
            file_path = os.path.join(upload_folder, filename)
            # Сохраняем файл
            media_file.save(os.path.join(current_app.root_path, file_path))
            
            # Сохраняем относительный путь без 'static/'
            relative_file_path = os.path.join('saved_images', filename)
            new = News(title=title, text=text, media_path=relative_file_path, author_id=current_user.id)
            db.session.add(new)
            db.session.commit()
            return redirect(url_for('main'))
        else:
            flash('Файл не был выбран или имя файла недопустимо')
    return render_template('create_news.html')

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in {'png', 'jpg', 'jpeg', 'gif'}


@app.route('/media/<filename>')
def media(filename):
    return send_from_directory('D:/PYTHON ALL/Flask-Projects/flask_socialnet/static/saved_images', filename)


@app.route('/delete_news/<int:news_id>', methods=['POST'])
@login_required
def delete_news(news_id):
    # Найти новость по идентификатору
    news_to_delete = News.query.get_or_404(news_id)

    # Проверить, что текущий пользователь является автором новости
    if news_to_delete.author_id != current_user.id:
        flash('Вы не можете удалить эту новость.')
        return redirect(url_for('main'))

    try:
        db.session.delete(news_to_delete)
        db.session.commit()
        flash('Новость успешно удалена.')
    except:
        db.session.rollback()
        flash('Ошибка при удалении новости.')

    return redirect(url_for('main'))


@app.route('/upgrade_news/<int:news_id>', methods=['POST', 'GET'])
@login_required
def upgrade_news(news_id):
    news_to_upgrade = News.query.get_or_404(news_id)

    if request.method == 'POST':
        # Найти новость по идентификатору
        news_to_upgrade.title = request.form['title']
        news_to_upgrade.text = request.form['text']

        try:
            db.session.commit()
            flash('Новость успешно изменена.')
            return redirect(url_for('main'))
        except:
            db.session.rollback()
            flash('Ошибка при изменении новости.')
    else:
        return render_template('upgrade_news.html', new=news_to_upgrade)

@app.route('/settings/<user>', methods = ['GET','POST'])
@login_required
def setting(user):
    
    return render_template('settings.html', user = user)

@app.route('/user_info', methods = ['GET','POST'])
@login_required
def user_info():
    if request.method == 'POST':
        user = User.query.filter_by(login=current_user.login).first()  # Исправлено на current_user.login
        if user:
            user_id = user.id
            user_info_to_upgrade = User_info.query.filter_by(user_id=user_id).first()

            if user_info_to_upgrade is None:
                birthday = request.form['birthday']
                sex = Gender(request.form['sex'])
                hobby = request.form['hobby']

                user_info = User_info(user_id=user_id, birthday=birthday, sex=sex, hobby=hobby)  # Добавлено user_id

                try:
                    db.session.add(user_info)
                    db.session.commit()
                    return redirect(url_for('setting', user=current_user.login))  # Перенаправление на страницу настроек
                except:
                    flash(message='Произошла ошибка при добавлении информации')
            else:
                user_info_to_upgrade.birthday = request.form['birthday']
                user_info_to_upgrade.sex = Gender(request.form['sex'])
                user_info_to_upgrade.hobby = request.form['hobby']

                try:
                    db.session.commit()
                    return redirect(url_for('setting', user=current_user.login))  # Перенаправление на страницу настроек
                except:
                    flash(message='Произошла ошибка при обновлении информации')

    return render_template('settings.html', user=current_user.login)

@app.route('/avatar', methods=['GET', 'POST'])
@login_required
def avatar():
    if request.method == 'POST':
        user = User.query.filter_by(login=current_user.login).first()
        
        if not user:
            flash('Пользователь не найден')
            return redirect(url_for('setting', user=current_user.login))

        media_file = request.files['media']
        
        if media_file and media_file.filename != '':
            # Генерируем безопасное имя файла
            filename = secure_filename(media_file.filename)
            # Определяем директорию для сохранения файла
            upload_folder = os.path.join(current_app.root_path, 'static', 'saved_images')
            
            # Проверяем, существует ли директория, и создаем её при необходимости
            if not os.path.exists(upload_folder):
                os.makedirs(upload_folder)

            # Полный путь к файлу
            file_path = os.path.join(upload_folder, filename)
            # Сохраняем файл
            media_file.save(file_path)

            # Сохраняем относительный путь (без 'static/')
            relative_file_path = os.path.join('saved_images', filename)

            # Обновляем поле media_path для текущего пользователя
            user.media_path = relative_file_path
            
            try:
                db.session.commit()  # Сохраняем изменения в базе данных
                flash('Аватарка успешно обновлена!')
                return redirect(url_for('setting', user=current_user.login))
            except Exception as e:
                flash(f'Ошибка при сохранении в базу данных: {e}')
                return redirect(url_for('setting', user=current_user.login))
        else:
            flash('Файл не выбран')
            return redirect(url_for('setting', user=current_user.login))
    else:
        flash('Неправильный метод запроса')
        return redirect(url_for('setting', user=current_user.login))
        



     
