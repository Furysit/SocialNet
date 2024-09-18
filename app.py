from sweater import app,db,socketio

if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Создание всех таблиц, определенных в моделях
    socketio.run(app, host="localhost", port=5000, debug=True)
