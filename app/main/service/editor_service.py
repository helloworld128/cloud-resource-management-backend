from app.main import db
from app.main.model.status import Status
from app.main.config import datadir
import os


def read_file(taskid, userid, name):
    try:
        status = Status.query.filter_by(userid=userid, taskid=taskid).first()
        username = status.username
    except:
        response_object = {
            'status': 'fail',
            'message': 'Cannot read taskid or name from request.'
        }
        return response_object, 400
    try:
        content = open(os.path.join(datadir, taskid, username, name)).read()
    except:
        response_object = {
            'status': 'fail',
            'message': 'File does not exist.'
        }
        return response_object, 400
    response_object = {
        'status': 'success',
        'message': 'Successfully read file.',
        'content': content
    }
    return response_object, 200


def save_file(userid, data):
    try:
        taskid = data['id']
        name = data['name']
        content = data['content']
    except KeyError:
        response_object = {
            'status': 'fail',
            'message': 'Cannot get taskid, name or content from request.'
        }
        return response_object, 400
    status = Status.query.filter_by(userid=userid, taskid=taskid).first()
    username = status.username
    try:
        fp = open(os.path.join(datadir, taskid, username, name), 'w')
        fp.write(content)
        fp.close()
    except:
        response_object = {
            'status': 'fail',
            'message': 'Cannot write to file.'
        }
        return response_object, 400
    response_object = {
        'status': 'success',
        'message': 'File saved.'
    }
    return response_object, 200


def create_file(taskid, userid, name):
    status = Status.query.filter_by(userid=userid, taskid=taskid).first()
    username = status.username
    try:
        fp = open(os.path.join(datadir, taskid, username, name), 'w')
        fp.close()
    except:
        response_object = {
            'status': 'fail',
            'message': 'Cannot create file.'
        }
        return response_object, 400
    response_object = {
        'status': 'success',
        'message': 'File created.'
    }
    return response_object, 201


def delete_file(taskid, userid, name):
    status = Status.query.filter_by(userid=userid, taskid=taskid).first()
    username = status.username
    try:
        os.remove(os.path.join(datadir, taskid, username, name))
    except:
        response_object = {
            'status': 'fail',
            'message': 'Cannot delete file.'
        }
        return response_object, 400
    response_object = {
        'status': 'success',
        'message': 'File deleted.'
    }
    return response_object, 200


def get_tree(dirname):
    res = []
    for item in os.listdir(dirname):
        if os.path.isdir(os.path.join(dirname, item)):
            res.append({'label': item, 'children': get_tree(os.path.join(dirname, item))})
        else:
            res.append({'label': item})
    return res


def get_file_tree(taskid, userid):
    status = Status.query.filter_by(userid=userid, taskid=taskid).first()
    username = status.username
    try:
        d = os.path.join(datadir, taskid, username)
        tree = get_tree(d)
    except:
        response_object = {
            'status': 'fail',
            'message': 'Cannot read user directory.'
        }
        return response_object, 503
    response_object = {
        'status': 'success',
        'filetree': tree
    }
    return response_object, 200
