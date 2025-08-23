from app import create_app
from flask import redirect, url_for

app = create_app()

@app.route('/')
def index():
    return redirect(url_for('project.get_projects'))

if __name__ == '__main__':
    app.run(debug=True)

