import json
import os
import subprocess

import langcodes
import pandas as pd
from sqlalchemy import create_engine,Table,Integer,Column,Date,MetaData,Text,String
from imdb import Cinemagoer
from movie.bot import Bot
from movie.bot.plug import humanbytes
from videoprops import get_video_properties
import ffmpeg
month={'Jan':'01','Feb':'02','Mar':'03','Apr':'04','May':'05','Jun':'06','Jul':'07','Aug':'08','Sep':'09','Oct':'10','Nov':'11','Dec':'12'}
im=Cinemagoer()
class Movie_base:
    
    def __init__(self) -> None:
        self.engine=self.create_base()
        self.conn=self.engine.connect()
        return 
    

    def create_base(self):
        engine=create_engine("sqlite:///movie_base.db",echo=True)
        self.meta=MetaData()
        self.movies=Table('movies',self.meta,
                     Column('Id',Integer,primary_key=True),
                     Column('title',String),
                     Column('year',Integer),
                     Column('plot',String),
                     Column('airdate',String),
                     Column('runtimes',String),
                     Column('coverurl',String),
                     Column('fullcoverurl',String),)
        self.genres=Table('genres',self.meta,
                     Column('Id',Integer),
                     Column('genre',String),
                     )
        self.languages=Table('languages',self.meta,
                     Column('Id',Integer),
                     Column('lang',String))
        self.files=Table('files',self.meta,
                         Column('Id',Integer),
                         Column('file_id',Integer),
                         Column('file_name',String),
                         Column('size',String),
                         Column('height',Integer),
                         Column('width',Integer),
                         Column('audiolan',String))
        self.meta.create_all(engine)
        return engine
    
    async def insert_movie(self,id,files):
        movie=im.get_movie(id)
        date="-".join(month[movie.get('original air date').split(' ')[i]] if i==1 else movie.get('original air date').split(' ')[i] for i in range(3))
        
        m=[int(id),movie.get('title'),int(movie.get('year'))," ".join(e for e in movie.get('plot')),date,"".join(e for e in movie.get('runtimes')),movie.get('cover url'),movie.get('full-size cover url')]
        j= self.movies.columns.keys()
        k={}
        for e,i in zip(j,m):
           k[e]=i
        genres=movie.get('genres')
        add_genres=self.genres.insert()
        for genre in genres:
            self.conn.execute(add_genres,[{'Id':int(id),'genre':genre}])
        languages=movie.get('languages')
        add_languages=self.languages.insert()
        for lang in languages:
            self.conn.execute(add_languages,[{'Id':int(id),'lang':lang}])
        add_files=self.files.insert()
        for i in files:
            media=await self.mediainfo(int(i))
            self.conn.execute(add_files,[{'Id':id,'file_id':int(i),'file_name':media[0],'size':media[1],'width':media[2],'height':media[3],'audiolan':media[4]}])
        add_movies=self.movies.insert()
        self.conn.execute(add_movies,[k])
        self.conn.commit()

        
        return 'added'
    
    async def mediainfo(self,id):
        msg=await Bot.get_messages(chat_id=-1001733288872,message_ids=id)
        file_name=msg.document.file_name
        file_size=humanbytes(msg.document.file_size)
        with open(file_name,'wb') as a:
            async for chunk in Bot.stream_media(msg,limit=5):
                a.write(chunk)
            a.close()
        path=os.getcwd()
        path=os.path.join(path,file_name)
        mediainfo=json.loads(subprocess.check_output(['mediainfo', file_name, '--Output=JSON']).decode("utf-8"))
        os.remove(file_name)
        width, height = 0, 0
        lang = []
        for i in mediainfo['media']['track']:
    
            if i['@type'] == 'Video':
                width, height = int(i['Width']), int(i['Height'])
            elif i['@type'] == 'Audio':
                if 'Language' in i.keys():
                    lang.append(i['Language'])
            else:
                pass
        audiolan=','.join(langcodes.get(e).display_name() for e in lang)
        return file_name,file_size,width,height,audiolan
    
    
    