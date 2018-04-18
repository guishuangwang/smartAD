from pymongo import MongoClient
from bson.objectid import ObjectId
import datetime

Client = MongoClient()
#project 'char',rename it in a new project
DB = Client.char
Tasks = DB.task

# define status:
# 'start': the task is starting
# 'gotimg': imgs have generated
# 'finish': finish all the job and build the models
# 'broke': job exception 

def newTask():
    newTask = {
        'status':'start',
        'createdAt':datetime.datetime.now(),
        'updatedAt':datetime.datetime.now()
    }
    taskId = Tasks.insert_one(newTask).inserted_id
    return str(taskId)
    
def checkTask(id):
    objId = ObjectId(id)
    task = Tasks.find_one({'_id':objId})
    return task

#if to is 'finished' : need provide the url so we can download it
def updateStatus(id,_from,_to,_url=None):
    objId = ObjectId(id)
    task = Tasks.find_one({'_id':objId})
    status = task.get('status')
    print 'check task'
    print task
    if status == _from :
        print 'check task in begin'
        print task
        task.update({
            'status':_to,
            'updatedAt':datetime.datetime.utcnow(),
            'url':_url
        })
        print 'check task in end'
        print task
        
        return True,_to,_url
    else :
        return False

def findAll():
    data = list()
    cursor = Tasks.find({})
    for doc in cursor:
        doc['_id'] = str(doc['_id'])
        doc['createdAt'] = str(doc.get('createdAt'))
        doc['updatedAt'] = str(doc.get('updatedAt'))
        data.append(doc)
    return data
