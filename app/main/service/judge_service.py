from app.main import db
from app.main.model.task import Task
from app.main.model.status import Status
from threading import Thread
from time import sleep
import shutil, os, sys
from app.main.config import datadir
try:
    from python_client.functions.python_client import judge
except ImportError as e:
    print(e.msg)
except TypeError as e:
    print(e)


def judgeFunc(taskid, userid):
    data = {'status': 'judging'}
    db.session.query(Status).filter_by(taskid=taskid, userid=userid).update(data)
    db.session.commit()

    # prepare files
    username = Status.query.filter_by(taskid=taskid, userid=userid).first().username
    shutil.copytree(os.path.join(datadir, taskid, 'init'), os.path.join(datadir, taskid, username + '_j', 'init'))
    shutil.copytree(os.path.join(datadir, taskid, 'judge'), os.path.join(datadir, taskid, username + '_j', 'judge'))
    shutil.copytree(os.path.join(datadir, taskid, username), os.path.join(datadir, taskid, username + '_j', 'user_data'))
    task = Task.query.filter_by(id=taskid).first()
    cmds = ['cd /mnt/%s_j\n' % username + task.judge_command + '\n']

    # actually judge the submission
    status, output, data['status'] = judge(taskid, task.image_name, cmds,
                        task.max_execution_time, task.max_memory_use, 0)
    # sys.stderr.write(str(output) + '\n')
    db.session.query(Status).filter_by(taskid=taskid, userid=userid).update(data)
    db.session.commit()

    # clean up
    shutil.rmtree(os.path.join(datadir, taskid, username + '_j'))
    response_object = {
        'status': 'success',
        'message': 'Submitted.'
    }
    return response_object, 200


def get_status(taskid, userid):
    try:
        status = Status.query.filter_by(userid=userid, taskid=taskid).first()
        status = status.status
    except:
        response_object = {
            'status': 'fail',
            'message': 'Cannot get status. Maybe this is a database error.'
        }
        return response_object, 503
    response_object = {
        'status': 'success',
        'data': status
    }
    return response_object, 200
