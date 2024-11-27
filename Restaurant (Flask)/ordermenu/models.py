from datetime import datetime
from itsdangerous.url_safe import URLSafeTimedSerializer as Serializer
from ordermenu import db, login_manager, app
from flask_login import UserMixin

    
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))


class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(20), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    password = db.Column(db.String(60), nullable=False)

    def get_reset_token(self):
        s = Serializer(app.config['SECRET_KEY'])
        return s.dumps({'user_id': self.id})

    @staticmethod
    def verify_reset_token(token):
        s = Serializer(app.config['SECRET_KEY'])
        try:
            user_id = s.loads(token)['user_id']
        except:
            return None
        return User.query.get(user_id)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}', '{self.image_file}', '{self.password})"

food_tags = db.Table('food_tag',
                    db.Column('food_id', db.Integer, db.ForeignKey('food.id')),
                    db.Column('tags_id', db.Integer, db.ForeignKey('tags.id'))
                    )
    
class Food(db.Model):
    id = db.Column(db.Integer, primary_key = True)
    name = db.Column(db.String(100), nullable=False, unique= True)
    price = db.Column(db.Float, nullable=False)
    description = db.Column(db.Text, nullable=False)
    smoldescription = db.Column(db.Text, nullable=False)
    image_file = db.Column(db.String(20), nullable=False, default='default.jpg')
    tags = db.relationship('Tags', secondary=food_tags, backref='foodtags',  lazy='dynamic')

    def __repr__(self):
        return f"Food('{self.id}','{self.name}', '{self.description}','{self.price}', '{self.image_file}')"
    
    
class Tags(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    tagname = db.Column(db.String(20), nullable=False)
    
    def __repr__(self):
        return f"Tag ('{self.id},{self.tagname}')" 
    
    
order_list = db.Table('order_list',
                    db.Column('shoppingcart', db.Integer, db.ForeignKey('shoppingcart.id')),
                    db.Column('trueorderlist', db.Integer, db.ForeignKey('trueorderlist.id'))
                    )

class Shoppingcart(db.Model):
    id = db.Column(db.Integer, primary_key = True, autoincrement=True)
    tablenum = db.Column(db.Integer, nullable = False)
    totalprice = db.Column(db.Integer, nullable = False)
    orderinglist = db.relationship("Trueorderlist", secondary=order_list, backref ="ShoppingCart")

    def __repr__(self):
        return f"Ordercart('{self.tablenum}', '{self.orderinglist}', '{self.totalprice}')"
    
    
class Trueorderlist(db.Model):    
    id = db.Column(db.Integer, primary_key = True)
    foodname = db.Column(db.String, nullable = False)
    food_multiply = db.Column(db.Integer, nullable = False)
    
    def __repr__(self):
        return f"Trueorderlist('{self.id}', '{self.foodname}', '{self.food_multiply}')"
    
    



    