from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://blogz:hello@localhost:8889/blogz'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)
app.secret_key = 'blahfartblah1271'


class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)
    owner_id = db.Column(db.Integer, db.ForeignKey('user.id'))

    def __init__(self, title, body, owner):
        self.title = title
        self.body = body
        self.owner = owner

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(26))
    password = db.Column(db.String(50))
    blogs = db.relationship('Blog', backref='owner')

    def __init__(self, username, password):
        self.username = username
        self.password = password

@app.before_request
def require_login():
    allowed_routes = ['login', 'signup', 'blog', 'index', '/static/styles/main.css']
    if request.endpoint not in allowed_routes and 'username' not in session:
        return redirect('/login')

@app.route('/login', methods=['POST', 'GET'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()
        if user and user.password == password:
            session['username'] = username
            flash('Logged in')
            return redirect('/newpost')
        elif user and user.password != password:
            flash('Invalid password', 'error')
            return redirect('/login')
        elif not user:
            flash('Username does not exist', 'error')
            return redirect('/login')
    else:
        return render_template('login.html')


@app.route('/signup', methods=['POST', 'GET'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        verify = request.form['verify']
        existing_user = User.query.filter_by(username=username).first()
        if not username or not password or not verify:
            flash('One or more fields are empty', 'error')
            return redirect('/signup')
        elif len(password) < 3 or len(username) < 3:
            flash('Usernames and passwords must at least 3 characters long', 'error')
            return redirect('/signup')
        elif existing_user:
            flash('Username already exists', 'error')
            return redirect('/signup')
        elif password != verify:
            flash('Passwords do not match', 'error')
            return redirect('/signup')
        else:
            new_user = User(username, password)
            db.session.add(new_user)
            db.session.commit()
            session['username'] = username
            return redirect('/newpost')



    else:
        return render_template('signup.html')



@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']
        owner = User.query.filter_by(username=session['username']).first()

        title_error = ''
        body_error = ''
        
        if not blog_title:
            title_error = "Please enter a title"
            return render_template('newpost.html', body=blog_body, title_error=title_error, blog_body=blog_body)
        if not blog_body:
            body_error = "Please enter a blog post dummy!"
            return render_template('newpost.html', blog_title=blog_title, body_error=body_error)
        else:

            new_blog_post = Blog(blog_title, blog_body, owner)
            db.session.add(new_blog_post)
            db.session.commit()
            blog_id = new_blog_post.id
            blog = Blog.query.filter_by(id = blog_id).first()
            return render_template('singlepost.html', title='Newpost | Blogz', blog=blog)
    return render_template('newpost.html', title="Post New Blog")


@app.route('/blog', methods=['POST', 'GET'])
def blog():
    if request.args.get('id'):
        blog_id = request.args.get('id')
        blog = Blog.query.filter_by(id = blog_id).first()
        return render_template('singlepost.html', title='Blogs | Blogz', blog=blog)
    if request.args.get('user'):
        user_id= request.args.get('user')
        user = User.query.get(user_id)
        blogs = Blog.query.filter_by(owner=user).all()
        return render_template('blog.html', title='Blogs | Blogz', blogs=blogs)
    blogs = Blog.query.all()
    users = User.query.all()
    return render_template('blog.html', title='Blogs | Blogz', blogs=blogs, users=users)

@app.route('/logout')
def logout():
    del session['username']
    return redirect('/blog')

@app.route('/')
def index():
    users = User.query.all()
    return render_template('/index.html', title='Home | Blogz', users=users)




if __name__ == '__main__':
    app.run()