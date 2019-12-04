# Important Notice
    This project is not deployed on Gitlab CI/CD container because it has too many restrictions.
    To view API documents and try them out yourself, please [visit here](http://49.233.20.29:30303/api/).

# Run instructions
    To run on linux: `sh run-dev.sh`
    To run on local machine for testing:
    * `python manage.py db init` `python manage.py db migrate` `python manage.py db upgrade` for setting up database.
    * `python manage.py run` to run web server in development mode on port 5000.
    * `python wsserver.py` to run websocket server on port 30304.
    
# Notes
    admin authorization key for testing: TODO
    task for testing: TODO