from app.main import db
from app.main.config import datadir
from app.main.model.task import Task
from app.main.model.status import Status
try:
    from python_client.functions.python_client import (
                    create_service, exec_command_by_list, add_pod,
                    delete_pod_by_list, delete_pod_by_service, 
                    exec_command_by_service, judge)
except ImportError as e:
    print(e.msg)
except TypeError as e:
    print(e)
import sys, os, shutil
from zipfile import ZipFile
from uuid import uuid4


def save_new_task(data):
    try:
        task = task = Task.query.filter_by(title=data['title']).first()
        if task:
            response_object = {
            'status': 'fail',
            'message': 'Title of task must be unique.'
            }
            return response_object, 409
        new_task = Task(
            title=data['title'],
            description=data.get('description', ''),
            max_execution_time=data.get('max_execution_time', 1),
            max_memory_use=data.get('max_memory_use', 128),
            image_name=data['image_name'],
            minimal_instance_num=data.get('minimal_instance_num', 1),
            judge_command=data['judge_command']
        )
        save_changes(new_task)
        task = Task.query.filter_by(title=data['title']).first()
        savedir = os.path.join(datadir, str(task.id))
        if not os.path.exists(savedir):
            os.mkdir(savedir)
        # TODO: create service and get ip
        # resource_host = db.Column(db.String(100))
        # resource_port = db.Column(db.Integer)
        status, ip, port = create_service(str(task.id), task.minimal_instance_num, task.image_name)
        if status != 'Success':
            response_object = {
                'status': 'fail',
                'message': 'Error in creating_service in k8s.',
            }
            Task.query.filter_by(id=task.id).delete()
            db.session.commit()
            return response_object, 503
        else:
            data = {
                'resource_host': ip,
                'resource_port': port
            }
            db.session.query(Task).filter_by(id=task.id).update(data)
            db.session.commit()
        response_object = {
            'status': 'success',
            'message': 'Task successfully created.',
            'id': task.id
        }
        return response_object, 201
    except KeyError:
        response_object = {
            'status': 'fail',
            'message': 'Required fields cannot be empty.'
        }
        return response_object, 400


def save_uploaded_files(files, id):
    if not files or len(files) != 2:
        response_object = {
            'status': 'fail',
            'message': 'You should upload exactly 2 zip files.'
        }
        return response_object, 400
    savedir = os.path.join(datadir, str(id))
    if not os.path.exists(savedir):
        os.mkdir(savedir)
    files[0].save(os.path.join(savedir, 'init.zip'))
    files[1].save(os.path.join(savedir, 'judge.zip'))
    with ZipFile(os.path.join(savedir, 'init.zip'), 'r') as initObj:
        initObj.extractall(os.path.join(savedir, 'init'))
    with ZipFile(os.path.join(savedir, 'judge.zip'), 'r') as judgeObj:
        judgeObj.extractall(os.path.join(savedir, 'judge'))
    # os.remove(os.path.join(savedir, 'init.zip'))
    # os.remove(os.path.join(savedir, 'judge.zip'))
    response_object = {
        'status': 'success',
        'message': 'File saved.'
    }
    return response_object, 200


def get_all_tasks():
    return Task.query.all()


def get_cmd(username, password):
    cmd1 = 'useradd -s /bin/bash -d /mnt/%s %s\n' % (username, username)
    cmd2 = "echo '%s:%s' | chpasswd\n" % (username, password)
    cmd3 = 'chmod -R 700 /mnt/%s\n' % username
    cmd4 = 'chown -R %s: /mnt/%s\n' % (username, username)
    return [cmd1 + cmd2 + cmd3 + cmd4]


def Add_pod(taskid, count):
    users = Status.query.filter_by(taskid=taskid).all()
    cmds = []
    for user in users:
        cmds.extend(get_cmd(user.username, user.password))
    # execute cmds in new pods
    image = Task.query.filter_by(id=taskid).first().image_name
    add_pod(taskid, count, image, [''.join(cmds)])


def check_add_del_pod(taskid):
    USER_COUNT_THRESHOLD_PER_POD = 3
    status, output = exec_command_by_service(taskid, ['w | wc -l\n'])
    sys.stderr.write(str(output) + '\n')
    tot = 0
    for key, val in output.items():
        tot += int(val[0]) - 2
    if tot > len(output) * USER_COUNT_THRESHOLD_PER_POD:
        Add_pod(taskid, len(output))


def create_new_user_in_container(userid, taskid):
    username, password = uuid4().hex[:8], uuid4().hex[:16]
    new_status = Status(
        userid=userid,
        taskid=taskid,
        status='    ',
        socketid=uuid4().int >> 100, # uuid4().int is a 128-bit integer, avoid database overflow
        username=username,
        password=password
    )
    try:
        shutil.copytree(os.path.join(datadir, taskid, 'init'), os.path.join(datadir, taskid, username))
    except:
        return 2
    # execute it in every pod
    try:
        status, output = exec_command_by_service(taskid, get_cmd(username, password))
    except:
        return -1
    check_add_del_pod(taskid)
    if status != 'Success':
        return 1
    save_changes(new_status)
    return 0


def get_a_task(userid, taskid):
    task = Task.query.filter_by(id=taskid).first()
    if not task:
        response_object = {
            'status': 'fail',
            'message': 'Task does not exist.'
        }
        return response_object, 404
    try:
        status = Status.query.filter_by(userid=userid, taskid=taskid).first()
    except:
        response_object = {
            'status': 'fail',
            'message': 'Database query error.'
        }
        return response_object, 503
    if not status:
        ret = create_new_user_in_container(userid, taskid)
        if ret != 0:
            err_msg = {
                1: 'function exec_command_by_service return "Failed" status.',
                -1: 'runtime error in function exec_command.',
                2: 'cannot copy init files into user directory.'
            }
            response_object = {
                'status': 'fail',
                'message': err_msg[ret]
            }
            return response_object, 503
        status = Status.query.filter_by(userid=userid, taskid=taskid).first()
    task.status = status.status
    task.socketid = status.socketid
    return task


def get_a_task_admin(taskid):
    task = Task.query.filter_by(id=taskid).first()
    if not task:
        response_object = {
            'status': 'fail',
            'message': 'Task does not exist.'
        }
        return response_object, 404
    return task


def modify_a_task(id, data):
    task = Task.query.filter_by(id=id).first()
    if not task:
        response_object = {
            'status': 'fail',
            'message': 'The task with given id does not exist.'
        }
        return response_object, 404
    try:
        data.pop('id', None)
        db.session.query(Task).filter_by(id=id).update(data)
        db.session.commit()
    except Exception as e:
        response_object = {
            'status': 'fail',
            'message': 'Update failed.'
        }
        return response_object, 503
    response_object = {
            'status': 'success',
            'message': 'Task successfully updated.'
        }
    return response_object, 200

    
    
def save_changes(data):
    db.session.add(data)
    db.session.commit()

