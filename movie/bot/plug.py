from movie.bot import Bot
from pyrogram.enums import MessagesFilter

def humanbytes(size):
    if not size:
        return ""
    power = 1024
    n = 0
    Dic_powerN = {0: ' ', 1: 'Ki', 2: 'Mi', 3: 'Gi', 4: 'Ti'}
    while size > power:
        size /= power
        n += 1
    return str(round(size, 2)) + " " + Dic_powerN[n] + 'B'

async def search_ids(name):
    data=[]
    async for i in Bot.search_messages(chat_id=-1001733288872,filter=MessagesFilter.DOCUMENT,):
        name=''.join(e for e in name if e.isalnum())
        if i.document:
            title=''.join(e for e in i.document.file_name if e.isalnum())
            if name in title:
                d={}
                d['file_id']=i.id
                d['file_name']=i.document.file_name
                d['file_size']=humanbytes(i.document.file_size)
                data.append(d)
            else:
                pass
        else:
            pass  
    return data
    

