from aiohttp import web
from pyrogram import Client
import json
from movie.bot.plug import search_ids
from imdb import Cinemagoer
from movie.server.database import Movie_base
import langcodes
import pandas as pd
import time


db=Movie_base()
routes = web.RouteTableDef()
im=Cinemagoer()

async def html_view(text):
    return web.Response(text=text,content_type='text/html')

@routes.get('/')
async def home(request):
    movie=pd.read_sql("select * from movies",con=db.engine)
    movie['airdate'] = pd.to_datetime(movie['airdate'],format='%d-%m-%Y')
    movie=movie.sort_values(by='airdate',ascending=False)
    movie=movie[['Id','title','year','coverurl']]
    movie=movie.to_dict(orient='records')
    
    return web.json_response(movie)

@routes.get('/search')
async def home(request):
    if 's' in request.rel_url.query.keys():
        s=request.rel_url.query['s']
        movie=pd.read_sql("select * from movies",con=db.engine)
        movie['airdate'] = pd.to_datetime(movie['airdate'],format='%d-%m-%Y')
        movie=movie.sort_values(by='airdate',ascending=False)
        movie = movie[['Id', 'title', 'year','coverurl']]
        movie = movie.to_dict(orient='records')
        movies=[]
        for i in movie:
            if s.lower() in i['title'].lower():
                movies.append(i)
            else:
                pass
        
        return web.json_response(movies)
    else:
        return web.json_response()
@routes.get('/info/{id}')
async def info(request):
    id=int(request.match_info['id'])
    movies = pd.read_sql("select * from movies", con=db.engine)
    genres = pd.read_sql("select * from genres", con=db.engine)
    languages = pd.read_sql("select * from languages", con=db.engine)
    files = pd.read_sql("select * from files", con=db.engine)
    movie=movies[movies['Id']==id].to_dict(orient='records')
    genres=list(genres[genres['Id']==id].genre.unique())
    languages =list(languages[languages['Id'] == id].lang.unique())
    files=files[files['Id']==id].to_dict(orient='records')
    result={'movie':movie[0],'genres':genres,'languages':languages,'files':files}
    return web.json_response(result)



add_movie_form="""<form method='GET' action='/add'>
                <label>type Imdb name</label>
                <input name='{}' type='{}'>
                <input type=submit>
                </form>
                """

@routes.get('/add')
async def add_movie(request):
        
        if 'name' in request.rel_url.query.keys():
            name=request.rel_url.query['name']
            text=""
            for i in im.search_movie(name):
                id,title=i.getID(),i
                text=text+"<a href=/add?id={}>{}</a><br>".format(id,title)
            return await html_view(text=text)
        elif 'id' in request.rel_url.query.keys():
            if 'files' in request.rel_url.query.keys():
                id=request.rel_url.query['id']
                movies = pd.read_sql('select  * from movies', con=db.engine)['Id'].tolist()
                if int(id) in movies:
                    return web.json_response("already added")
                nonids=list(request.rel_url.query.values())
                ids=[]
                for i in nonids:
                    if '/' in i:
                        ids.append(int(i.replace('/','')))
                res=await db.insert_movie(id,ids)
                return web.json_response("added")
            id=request.rel_url.query['id']
            movies=pd.read_sql('select  * from movies',con=db.engine)['Id'].tolist()
            if int(id) in movies:
                return web.json_response("already added")
            movie=im.get_movie(id)
            data=await search_ids(name=movie.get("title"))
            text="<form method='get' action=/add> <input name='id' value={}><br>".format(id)
            t=''
            for i in data:
                 t=t+"<label>{}:{}</label><input type='checkbox' name='files' value={}/><br>".format(i['file_name'],i['file_size'],int(i['file_id']))
            text=text+t+"<input type='submit'></form>"
            return await html_view(text=text)

        return await html_view(text=add_movie_form.format('name','text'))
    

