from flask_restplus import Api
from flask import Blueprint, url_for

from .main.controller.user_controller import api as user_ns
from .main.controller.auth_controller import api as auth_ns
from .main.controller.task_controller import api as task_ns
from .main.controller.editor_controller import api as editor_ns
from .main.controller.judge_controller import api as judge_ns

blueprint = Blueprint('api', __name__, url_prefix='/api')


class MyApi(Api):
    @property
    def specs_url(self):
        """Monkey patch for HTTPS"""
        scheme = 'http' if '5000' in self.base_url or '30303' in self.base_url else 'https'
        return url_for(self.endpoint('specs'), _external=True, _scheme=scheme)


api = MyApi(blueprint,
          title='API Documentation',
          version='1.0',
          description='API for cloud resource management'
          )

api.add_namespace(user_ns, path='/user')
api.add_namespace(auth_ns)
api.add_namespace(task_ns)
api.add_namespace(editor_ns)
api.add_namespace(judge_ns)