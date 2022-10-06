from flask import Flask, redirect, render_template, request
from flask_sqlalchemy import SQLAlchemy
from datetime import datetime
from sqlalchemy import desc
from encoder import make_taste_list, insert
import recipeSearch

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///frire.db'
db = SQLAlchemy(app)

class FridgeItem(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  itemName = db.Column(db.String(30), nullable=False)
  itemNum = db.Column(db.Integer, nullable=False)
  itemCost = db.Column(db.Integer)
  expiryDate = db.Column(db.DateTime, nullable=False)

class Recipes(db.Model):
  id = db.Column(db.Integer, primary_key=True, autoincrement=True)
  recipeName = db.Column(db.String(30), nullable=False)
  cookTime = db.Column(db.String(10), nullable=False)
  material = db.Column(db.String(100), nullable=False)
  recipeImg = db.Column(db.String(100))
  recommendPoint = db.Column(db.Float, nullable=False)
  expiryDate = db.Column(db.DateTime, nullable=False)


onClick = 0

@app.route('/')
def index():
  menu_titles = {'fridgeItem':"冷蔵庫の中身", 'recipe':"レシピ", 'calender':"食事カレンダー", 'goal':"あなたの目標", 'create':"食材登録", 'cost':"食材費"}
  return render_template('index.html', menu_titles=menu_titles)


@app.route('/fridgeItem', methods=['GET','POST'])
def fridgeItem():
  if request.method == 'GET':
    posts = FridgeItem.query.all()
    return render_template('fridgeItem.html', posts=posts)
  else:
    itemName = request.form.get('itemName')
    itemNum = request.form.get('itemNum')
    itemCost = request.form.get('itemCost')
    expiryDate = request.form.get('expiryDate')

    expiryDate = datetime.strptime(expiryDate, '%Y-%m-%d')
    new_post = FridgeItem(itemName=itemName, itemNum=itemNum, itemCost=itemCost, expiryDate=expiryDate)

    db.session.add(new_post)
    db.session.commit()
    recipeSearch.recipe_update(db, FridgeItem, Recipes)
    return redirect('/fridgeItem')
    

@app.route('/create')
def create():
  return render_template('create.html')

@app.route('/recipe', methods=['GET','POST'])
def recipe():
  global onClick
  if request.method == 'GET':
    if onClick == 1:
      posts = Recipes.query.order_by(desc(Recipes.recommendPoint)).all()
      onClick = 0
    else:
      posts = Recipes.query.order_by(Recipes.expiryDate).all()
    feellists = {'あっさり':'Plain meal','重め':'Heavy meal','軽め':'Light meal','さっぱり':'Healthy','しょっぱい':'Salty','甘い':'Sweet','辛め':'Spicy','酸っぱい':'Sour','脂っこい':'Greasy'}

    feelButtons = []
    for feel_key, feel_value in feellists.items():
      feel = f'<button type="submit" name="action" value="{feel_value}"> { feel_key } </button>' 
      feelButtons.append(feel)
    
    return render_template('recipe.html', recipe_items = posts, feelButtons = feelButtons)
  else:
    onClick = 1
    value = request.values["action"]
    taste = make_taste_list()
    recipe_items = Recipes.query.all()

    results = []
    for recipe_item in recipe_items:
      results.append(insert(taste[value], recipe_item.recipeName,recipe_item.recipeImg, 'url'))

    for result, recipe_item in zip(results,recipe_items):
      recommendPoint = result[2]
      recipe_item.recommendPoint = recommendPoint
    db.session.commit()
      
    return redirect('/recipe')

if __name__ == '__main__':
  app.run(debug=True)