from flask import Flask, request, jsonify, abort, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_marshmallow import Marshmallow
from passlib.apps import custom_app_context as pwd_context
import os



# init app
app = Flask(__name__)
basedir = os.path.abspath(os.path.dirname(__file__))




# database
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(basedir, 'db.sqlite')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

# User model
class User(db.Model):
    __tablename__ = 'users'
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(32), index=True)
    password_hash = db.Column(db.String(128))

    def hash_password(self, password):
        self.password_hash = pwd_context.encrypt(password)

    def verify_password(self, password):
        return pwd_context.verify(password, self.password_hash)
    





# marshmallow and schemas
ma = Marshmallow(app)

class UserSchema(ma.Schema):
    class Meta:
        fields = ('id', 'username')

user_schema = UserSchema()
users_schema = UserSchema(many=True)


    


# routes
@app.route('/api/users', methods=['POST'])
def new_user():
    username = request.json.get('username')
    password = request.json.get('password')
    if username is None or password is None:
        abort(400) # missing credentials
    if User.query.filter_by(username=username).first() is not None:
        abort(400) # this user already exists
    user = User(username=username)
    user.hash_password(password)
    db.session.add(user)
    db.session.commit()

    response = {'username':user.username}
    # return jsonify({ 'username': user.username }), 201, {'Location': url_for('get_user', id = user.id, _external = True)}
    return jsonify(response)


@app.route('/api/users', methods=['GET'])
def users_list():
    users = User.query.all()
    result = users_schema.dumps(users)
    return result
    
# runserver
if __name__ == "__main__":
    app.run(debug=True)