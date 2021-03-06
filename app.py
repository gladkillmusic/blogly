"""Blogly application."""

from flask import Flask, redirect, render_template, request
from models import db, connect_db, User, Post

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql:///blogly'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['SQLALCHEMY_ECHO'] = True

connect_db(app)
db.create_all()


@app.route('/')
def get_index():
    """ Redirects to list of all Users """
    return redirect("/users")


@app.route('/users')
def show_users():
    """ List of all Users """
    users = User.query.all()
    return render_template(
        'userlisting.html',
        users=users
    )


@app.route('/users/new')
def create_new_user():
    """ Takes form info and creates new user """
    return render_template('newuserform.html')


@app.route('/users/new', methods=["POST"])
def post_new_user():
    """ Process add form, add a new user and go back to /users """
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"] or None

    new_user = User(
                    first_name=first_name,
                    last_name=last_name,
                    image_url=image_url)

    db.session.add(new_user)
    db.session.commit()

    return redirect("/users")


@app.route('/users/<int:user_id>')
def info_about_user(user_id):
    """  Shows information about the given user """
    current_user = User.query.filter_by(id=user_id).one()
    user_full_name = f"{current_user.first_name} {current_user.last_name}"
    user_image = current_user.image_url
    posts = Post.query.filter_by(user_id=user_id).all()

    return render_template(
                'userdetails.html', user=user_full_name,
                image_url=user_image, user_id=user_id, posts=posts)


@app.route('/users/<int:user_id>/edit')
def edit_user_html(user_id):
    """ Show Edit User Page  """
    user = User.query.filter_by(id=user_id).one()
    return render_template('useredit.html', user_id=user_id, user=user)


@app.route('/users/<int:user_id>/edit', methods=['POST'])
def process_edit_form(user_id):
    """ Process the edit form, return user to the /users page """
    first_name = request.form["first_name"]
    last_name = request.form["last_name"]
    image_url = request.form["image_url"] or None

    current_user = User.query.get_or_404(user_id)
    current_user.first_name = first_name
    current_user.last_name = last_name
    # Updating URL doesn't run through Model default
    # this IF checks if value is None
    if image_url is not None:
        current_user.image_url = image_url
    db.session.commit()

    return redirect('/users')


@app.route('/users/<int:user_id>/delete', methods=["POST"])
def delete_user(user_id):
    """ Deletes User """
    current_user = User.query.get_or_404(user_id)

    db.session.delete(current_user)
    db.session.commit()
    # if we wanted to track a deleted user, we would create a
    # separtetable for them
    return redirect('/users')

@app.route('/users/<int:user_id>/posts/new')
def new_post_page(user_id):
    """ adds new post by user """
    current_user = User.query.get_or_404(user_id)

    return render_template('addpostform.html', user_id=user_id, user=current_user)


@app.route('/users/<int:user_id>/posts/new', methods=["POST"])
def add_new_post(user_id):
    """creates post from  form   data, appends to user detail page"""
    post_title = request.form["title"]
    post_content = request.form["content"]

    new_post = Post(title=post_title, content=post_content, user_id=user_id )
    db.session.add(new_post)
    db.session.commit()

    return redirect(f"/users/{user_id}")

@app.route('/posts/<int:post_id>')
def show_posts(post_id):
    """shows a post by post id"""
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template("postdetailpage.html",
    post=post, user=user)

@app.route('/posts/<int:post_id>/edit')
def show_edit_post_page(post_id):
    """takes us to our post edit page"""
    post = Post.query.get_or_404(post_id)
    user = post.user
    return render_template("editpostform.html",
    post=post,user=user)

@app.route('/posts/<int:post_id>/edit', methods=["POST"])
def edit_post(post_id):
    """edits post then returns us  to the post page"""
    post_title = request.form["title"]
    post_content = request.form["content"]
    current_post = Post.query.get_or_404(post_id)
    


    current_post.title = post_title
    current_post.content = post_content

    db.session.commit()

    return redirect(f"/posts/{post_id}")

@app.route('/posts/<int:post_id>/delete', methods=["POST"])
def delete_post(post_id):
    current_post = Post.query.get_or_404(post_id)
    user = current_post.user
    db.session.delete(current_post)

    return redirect(f'/users/{user.id}')

