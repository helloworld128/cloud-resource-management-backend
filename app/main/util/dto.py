from flask_restplus import Namespace, fields


class UserDto:
    api = Namespace('user', description='user related operations')
    user = api.model('user', {
        'email': fields.String(required=True, description='user email address'),
        'username': fields.String(required=True, description='user username'),
        'password': fields.String(required=True, description='user password'),
        'public_id': fields.String(description='user Identifier')
    })


class AuthDto:
    api = Namespace('auth', description='authentication related operations')
    user_auth = api.model('auth_details', {
        'email': fields.String(required=True, description='The email address'),
        'password': fields.String(required=True, description='The user password '),
    })

class TaskDto:
    api = Namespace('task', description='task related operations')
    task = api.model('task', {
        'id': fields.Integer(description='task id'),
        'title': fields.String(required=True, description='task title'),
        'description': fields.String(description='task description'),
    })
    taskAdmin = api.clone('taskAdmin', task, {
        'max_execution_time': fields.Integer(description='max execution time in ms'),
        'max_memory_use': fields.Integer(description='max memory use in MB'),
        'image_name': fields.String(required=True, description='image name'),
        'minimal_instance_num': fields.Integer(description='minimal number of instances running'),
        'judge_command': fields.String(required=True, description='judge command')
    })
    taskUser = api.clone('taskUser', task, {
        'socketid': fields.String(description='websocket id'),
        'status': fields.String(description='status of current task')
    })

