from flask import render_template, url_for, flash, redirect,request
from app import app,db, bcrypt
from app.forms import RegistrationForm, LoginForm,AnnouncementForm
from app.models import User,Post
from flask_login import login_user,current_user,logout_user,login_required


@app.route("/")
@app.route("/home")
def home():
    page = request.args.get('page', 1, type=int)
    posts = Post.query.order_by(Post.date_posted.desc()).paginate(page=page, per_page=4)
    return render_template('home.html', posts=posts)


@app.route("/signup", methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = RegistrationForm()
    if form.validate_on_submit():
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        user = User(username=form.username.data, email=form.email.data, password=hashed_password)
        db.session.add(user)
        db.session.commit()
        flash('Account successfully created,You are now able to log in', 'success')
        return redirect(url_for('login'))
    return render_template('signup.html', title='Signup', form=form)


@app.route("/login", methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return redirect(url_for('home'))
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user, remember=form.remember.data)
            next_page = request.args.get('next')
            return redirect(next_page) if next_page else redirect(url_for('home'))
        else:
            flash('Unsuccessful Login.Please check email and password', 'danger')
    return render_template('login.html', title='Login', form=form)

@app.route("/logout")
def logout():
    logout_user()
    return redirect(url_for('home'))


@app.route("/announcements/new", methods=['GET', 'POST'])
@login_required
def new_announcement():
    form = AnnouncementForm()
    if form.validate_on_submit():
        posts= Post(title=form.title.data, content=form.content.data, author=current_user)
        db.session.add(posts)
        db.session.commit()
        flash('Announcement successfully added!', 'success')
        return redirect(url_for('home'))
    return render_template('announcement.html', title='Announcements',form=form, legend=' Create An Announcement')


@app.route("/announcements/<int:post_id>")
def announcement (post_id):
    post = Post.query.get_or_404(post_id)
    return render_template('modify.html',post=post)

@app.route("/announcements/<int:post_id>/update", methods=['GET', 'POST'])
@login_required
def update_announcement(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    form = AnnouncementForm()
    if form.validate_on_submit():
        post.title = form.title.data
        post.content = form.content.data
        db.session.commit()
        flash('Annoucement successfully updated!', 'success')
        return redirect(url_for('announcement', post_id=post.id))
    elif request.method == 'GET':
        form.title.data = post.title
        form.content.data = post.content
    return render_template('announcement.html',form=form,legend='Update Announcement')


@app.route("/announcements/<int:post_id>/delete", methods=['POST'])
@login_required
def delete_announcement(post_id):
    post = Post.query.get_or_404(post_id)
    if post.author != current_user:
        abort(403)
    db.session.delete(post)
    db.session.commit()
    flash('Announcement deleted!', 'success')
    return redirect(url_for('home'))

@app.route("/admin/<string:username>")
def admin_announcements(username):
    page = request.args.get('page', 1, type=int)
    user = User.query.filter_by(username=username).first_or_404()
    posts = Post.query.filter_by(author=user).order_by(Post.date_posted.desc()).paginate(page=page, per_page=5)
    return render_template('admin.html', posts=posts, user=user)