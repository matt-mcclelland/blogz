from flask import Flask, request, redirect, render_template, session, flash
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'mysql+pymysql://build-a-blog:hello@localhost:8889/build-a-blog'
app.config['SQLALCHEMY_ECHO'] = True
db = SQLAlchemy(app)

class Blog(db.Model):

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(120))
    body = db.Column(db.Text)

    def __init__(self, title, body):
        self.title = title
        self.body = body

@app.route('/newpost', methods=['POST', 'GET'])
def newpost():
    if request.method == 'POST':
        blog_title = request.form['title']
        blog_body = request.form['body']

        title_error = ''
        body_error = ''
        
        if not blog_title:
            title_error = "Please enter a title"
            return render_template('newpost.html', body=blog_body, title_error=title_error, blog_body=blog_body)
        if not blog_body:
            body_error = "Please enter a blog post dummy!"
            return render_template('newpost.html', blog_title=blog_title, body_error=body_error)
        else:
            new_blog_post = Blog(blog_title, blog_body)
            db.session.add(new_blog_post)
            db.session.commit()
            return redirect('/blog')
    return render_template('newpost.html', title="Post New Blog")


@app.route('/blog')
def blog():
    blogs = Blog.query.all()
    return render_template('blog.html', title='Build a Blog', blogs=blogs)

@app.route('/')
def index():
    return redirect('/blog')




if __name__ == '__main__':
    app.run()