from .. import db
import datetime


class Task(db.Model):
    """ 
    Task Model for storing task details, such as description, image, judge script.
    """
    __tablename__ = "tasks"

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)

    title = db.Column(db.String(64), nullable=False, unique=True)
    description = db.Column(db.String(512))
    max_execution_time = db.Column(db.Integer)
    max_memory_use = db.Column(db.Integer)

    resource_host = db.Column(db.String(100))
    resource_port = db.Column(db.Integer)
    image_name = db.Column(db.String(64))
    initial_file_dir = db.Column(db.String(128))
    judge_file_dir = db.Column(db.String(128))
    judge_command = db.Column(db.String(256))
    minimal_instance_num = db.Column(db.Integer, default=1)
    # max_user_per_container = db.Column(db.Integer, default=2)

    def __repr__(self):
        return "<Task '{}'>".format(self.id)
