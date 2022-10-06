import csv
import requests
import pandas as pd
import time

def recipe_update(db, FridgeItem, Recipes):
  fridge_items = FridgeItem.query.filter(FridgeItem.itemName != None)

  for fridge_item in fridge_items:
    df_rank = read_csv(fridge_item.itemName)
    expiryDate = fridge_item.expiryDate
    try:
      recipeNames = df_rank['recipeTitle']
      cookTimes = df_rank['recipeIndication']
      # materials = df_rank['recipeMaterial']
      recipeImgs = df_rank['foodImageUrl']
    except:
      pass

    recipeItems = zip(recipeNames, cookTimes, recipeImgs)
    recipeItems = delete_duplicationData(Recipes, recipeItems)

    for recipeName, cookTime, recipeImg in recipeItems:
      recipeImg = f'<img src="{recipeImg}" class="card-img-top" alt="">'
      new_post = Recipes(recipeName=recipeName, cookTime=cookTime, material="あいうえお", recipeImg=recipeImg, recommendPoint=1.0, expiryDate=expiryDate)
      db.session.add(new_post)

  db.session.commit()

def read_csv(keyword):
  foods = {}
  with open('static/csv/all_rank.csv',encoding="utf-8") as f:
      reader = csv.reader(f)
      for row in reader:
        if keyword == row[0]:
          foods["ItemName"] = row[0]
          foods["URL"] = row[1]
          foods["ID"] = split_url(foods["URL"])
          foods["parentCategoryId"] = row[2]
          foods["categoryId"] = row[3]
  try:
    search_recipe(foods["ID"])
  except KeyError:
    print("KeyError: "+ keyword)
    return 
  
  df_rank = search_recipe(foods["ID"])
  return df_rank

def split_url(url):
  sp_url = url.split('/')
  return sp_url[4]

def get_recipe_info(base_url, item_parameters):
  #jsonデータの取得
  #各カテゴリの4位までのレシピ情報取得
  r = requests.get(base_url, params=item_parameters)
  item_data = r.json()

  return item_data

def isEmpty(item_data):
  try:
    item_data['result']
  except KeyError:
    return True
  else:
    return False

def search_recipe(ID):
  #urlの作成
  base_url = 'https://app.rakuten.co.jp/services/api/Recipe/CategoryRanking/20170426?' #レシピランキングAPIのベースとなるURL
 
  item_parameters = {
              'applicationId': '1028435163160731300', #アプリID
              'format': 'json',
              'formatVersion': 2,
              'categoryId': ID 
  }

  #各レシピ情報の格納用に、データフレーム用意
  df_rank = pd.DataFrame(columns=[
      'rank', #順位
      'recipeId', #レシピID
      'recipeTitle', #レシピタイトル
      'recipeDescription', #レシピ説明文
      'recipeUrl', #レシピURL
      'foodImageUrl', #料理画像URL
      'recipeCost', #予算
      'recipeIndication', #料理時間
      'recipeMaterial',  #レシピ材料
      'recipePublishday' #レシピ発行日
  ])

  #各レシピの取得項目を抽出 
  item_data = get_recipe_info(base_url, item_parameters)
  while isEmpty(item_data) == True:
    time.sleep(5)
    print(ID+': keyerror')
    item_data = get_recipe_info(base_url, item_parameters)
    
  for recipe in item_data['result']:
    df_rank = df_rank.append(
      {'rank':recipe['rank'],
       'recipeId':recipe['recipeId'],
       'recipeTitle':recipe['recipeTitle'],
       'recipeDescription':recipe['recipeDescription'],
       'recipeUrl':recipe['recipeUrl'],
       'foodImageUrl':recipe['foodImageUrl'],
       'recipeCost':recipe['recipeCost'],
       'recipeIndication':recipe['recipeIndication'],
       'recipeMaterial':recipe['recipeMaterial'],
       'recipePublishday':recipe['recipePublishday'],},
       ignore_index=True)
  
  return df_rank

def delete_duplicationData(Recipes, newRecipeItems):
  recipeItems = Recipes.query.all()  
  
  recipeNames = []
  cookTimes = []
  recipeImgs = []
  if len(recipeItems) != 0:
    for recipeName, cookTime, recipeImg in newRecipeItems:
      for i,recipeItem in enumerate(recipeItems):
        if recipeItem.recipeName == recipeName:
          break
        elif(i == len(recipeItems)-1):
          recipeNames.append(recipeName)
          cookTimes.append(cookTime)
          recipeImgs.append(recipeImg)
  else:
    return newRecipeItems

  noDupNewRecipeItems = zip(recipeNames, cookTimes, recipeImgs)
  return noDupNewRecipeItems
