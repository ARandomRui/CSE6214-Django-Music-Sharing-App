import os
import secrets
from sqlalchemy import or_
from PIL import Image
from flask import render_template, url_for, flash, redirect, request, abort, session
from ordermenu import app, db, bcrypt
from ordermenu.forms import (RegistrationForm, LoginForm, UpdateAccountForm,
                             AddfoodForm,ConfirmationOrderForm, TagFilterForm)
from ordermenu.models import User, Food, Tags, food_tags, Trueorderlist, Shoppingcart
from flask_login import login_user, current_user, logout_user, login_required

image_type = None #random variable to prevent errors whic shouldnt happen
form = None
orderlist = dict()
emptylist = []

@app.route("/")
@app.route("/home")
def home():
    return render_template('home.html')

@app.route("/register", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated: #flask_login func
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Your account has been created! You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('register.html', title='Register', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    global admin
    admin = False
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        try:
            user = User.query.filter_by(username=form.tryna_user.data).first()
            if form.tryna_user == "admin" and form.password == "123":
                admin = True             
            if user and bcrypt.check_password_hash(user.password, form.password.data):
                login_user(user, remember=form.remember.data)
                next_page = request.args.get('next')
                if admin:
                    return redirect(next_page) if next_page else redirect(url_for('adminhome'))
                else:    
                    return redirect(next_page) if next_page else redirect(url_for('home'))
            else:
                flash('Login Unsuccessful. Please check username and password', 'danger')
        except:
                flash('Login Unsuccessful. No such username', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))

def save_picture(form_picture, image_type):
    random_hex = secrets.token_hex(8)
    _, f_ext = os.path.splitext(form_picture.filename)
    picture_fn = random_hex + f_ext
    if image_type == "profile":
        picture_path = os.path.join(app.root_path, 'static/profile_pics', picture_fn)
    elif image_type =="Food":
        picture_path = os.path.join(app.root_path, 'static/food_pics', picture_fn)
    output_size = (125, 125)
    i = Image.open(form_picture)
    i.thumbnail(output_size)
    i.save(picture_path)

    return picture_fn

@app.route("/admin")
@login_required
def admin():
    return render_template('adminhome.html')   
    
@app.route("/account", methods=['GET', 'POST'])
@login_required
def account():
    form = UpdateAccountForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_type = "profile"
            picture_file = save_picture(form.picture.data, image_type)
            current_user.image_file = picture_file
        current_user.username = form.username.data
        current_user.email = form.email.data
        db.session.commit()
        flash('Your account has been updated!', 'success')
        return redirect(url_for('account'))
    elif request.method == 'GET':
        form.username.data = current_user.username
        form.email.data = current_user.email
    image_file = url_for('static', filename='profile_pics/' + current_user.image_file)
    return render_template('account.html', title='Account',
                           image_file=image_file, form=form)
    
'''Admin routes'''

@app.route("/adding_food", methods=['GET', 'POST'])
def new_food():
    form = AddfoodForm()
    if form.validate_on_submit():
        if form.picture.data:
            image_type = "Food"
            picture_file = save_picture(form.picture.data, image_type)
            food = Food(name=form.name.data, price=form.price.data, smoldescription=form.smoldescription.data,  
                        description = form.description.data, image_file = picture_file)
        else:
            food = Food(name=form.name.data, price=form.price.data, smoldescription=form.smoldescription.data,
                        description = form.description.data)
        for each in form.foodtag.data:
            tagtag = f"Tags(tagname = \"{each}\")"
            tagtag = eval(tagtag)
            food.tags.append(tagtag)
        db.session.add(food)
        db.session.commit()
        flash(f'Food, { form.name.data } has been successfully created!', 'success')
        return redirect(url_for('menu', formdata = form))
    return render_template('addfood.html', title='Adding Food', form=form)

@app.route("/view_orders")
@login_required
def list_orders():
    if current_user.username != "admin":
        abort(403)
    orders = Shoppingcart.query.all()
    return render_template('adminorderlist.html', orders = orders)

@app.route("/view_orders/delete/<order_id>", methods=['POST'])
@login_required
def delete_order(order_id):
    order = Shoppingcart.query.get_or_404(order_id)
    if current_user.username != "admin":
        abort(403)
    db.session.delete(order)
    db.session.commit()
    count = Shoppingcart.query.count()
    if count == 0:
        order.orderinglist.clear()
        Trueorderlist.query.delete()
        db.session.commit()
    flash('Your order has been deleted!', 'success')
    return redirect(url_for('list_orders'))


@app.route("/menu/orderingcart/added/<food>/", methods=['GET', 'POST'])
@login_required
def ordercart(food):
    try:
        totalprice=session["totalprice"]
    except:
        totalprice = 0
    form = ConfirmationOrderForm()
    if form.validate_on_submit():
        finalorder = Shoppingcart(tablenum = form.tableno.data, totalprice = totalprice)
        for each, every in orderlist.items():
            x = Trueorderlist(foodname = each, food_multiply = every)
            db.session.add(x)
            db.session.commit()
            finalorder.orderinglist.append(x)
        db.session.add(finalorder)
        session.pop("totalprice", None)
        db.session.commit()
        flash(f'Your order has been successfully made!', 'success')
        orderlist.clear()
        return redirect(url_for('menu'))
    if food in orderlist:
        orderlist[food] += 1
    else:
        orderlist[food] = 1
    foodquery = Food.query.filter_by(name = food).all()
    totalprice = float(totalprice) + foodquery[0].price
    session["totalprice"] = totalprice
    return render_template('ordercart.html', orderlist = orderlist, form=form, totalprice = totalprice)

@app.route("/orderingcart/delete", methods=['POST'])
@login_required
def clear_cart():
    orderlist.clear()
    session.pop("totalprice", None)
    flash('Your order has been deleted!', 'success')
    return redirect(url_for('menu'))

'''menu's route'''


@app.route("/menu")
def menu():
    tag = []
    temptag = Tags.query.all()
    for each in temptag:
        if each.tagname not in tag:
            tag.append(each.tagname)
    foodpage = request.args.get('page', 1, type=int)
    foodlist = Food.query.order_by(Food.id).paginate(page=foodpage, per_page=9)
    return render_template('menu.html', menulists=foodlist, tags = tag)

@app.route("/food/<int:food_id>")
def fooddetail(food_id):
    food = Food.query.get_or_404(food_id)
    return render_template('fooddetail.html', name=food.name, description=food.description, food=food)

@app.route("/food/<int:food_id>/delete", methods=['POST'])
@login_required
def delete_food(food_id):
    food = Food.query.get_or_404(food_id)
    if current_user.username != "admin":
        abort(403)
    db.session.delete(food)
    db.session.commit()
    flash('Your food has been deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/menu/food/<tag>")
def filtertag(tag):
    menutag = []
    temptag = Tags.query.all()
    for each in temptag:
        if each.tagname not in menutag:
            menutag.append(each.tagname)
    tagidlist = []
    taglist = [tag]
    if len(taglist) == 1:
        tagid = Tags.query.filter_by(tagname=tag).all()
        for each in tagid:
            tagidlist.append(each.id)
    food = Food.query.join(Food.tags).filter(Tags.id.in_(tagidlist)).all()
    tag = []
    temptag = Tags.query.all()
    for each in temptag:
        if each.tagname not in tag:
            tag.append(each.tagname)
    return render_template('filteredmenu.html', filteredlist=food, tags=tag)



@app.route("/filter", methods=['GET', 'POST'])
def filter_tags():
    form = TagFilterForm()
    if form.validate_on_submit():
        return redirect(url_for('filtered_menu', formtagdata=form.foodtag.data))
    return render_template('filtertag.html', title = "Filter Tags", form=form)

@app.route("/menu/filtered/<formtagdata>", methods=['GET', 'POST'])
def filtered_menu(formtagdata):
    halfway = []
    y = []
    listoftagname = []
    finallist = []
    formtagdata = eval(formtagdata)
    for each in formtagdata:
        x = Tags.query.filter_by(tagname = each).all()
        for each in x:
            listoftagname.append(each.tagname)
    listoftagname = list(set(listoftagname))
    for each in listoftagname:
        halfway.append(Food.query.join(Tags.foodtags).filter(Tags.tagname == each).all())
    for each in halfway:
        if each != emptylist:
            if len(each) != 0:
                for every in each:
                    if every not in y:
                        y.append(every)
            else:
                pass
    tag = []
    filteredlist = y
    temptag = Tags.query.all()
    for each in temptag:
        if each.tagname not in tag:
            tag.append(each.tagname)   
    for each in filteredlist:
        x = [tag.tagname for tag in each.tags]
        if all(ele in x for ele in formtagdata):
            finallist.append(each)          
    return render_template('filteredmenu.html', filteredlist = finallist, tags=tag)
                  
