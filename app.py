import os
import re
from datetime import datetime

from flask import Flask, flash, redirect, render_template, request, session, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import func

BASE_DIR = os.path.abspath(os.path.dirname(__file__))

app = Flask(__name__)
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-secret-change-me")
app.config["SQLALCHEMY_DATABASE_URI"] = f"sqlite:///{os.path.join(BASE_DIR, 'travel_blog.db')}"
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

ADMIN_USERNAME = os.getenv("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD = os.getenv("ADMIN_PASSWORD", "admin123")

db = SQLAlchemy(app)


class Destination(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    country = db.Column(db.String(120), nullable=False)
    description = db.Column(db.Text, nullable=False)
    image_url = db.Column(db.String(300), nullable=False)


class Post(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    slug = db.Column(db.String(220), unique=True, nullable=False)
    excerpt = db.Column(db.String(280), nullable=False)
    content = db.Column(db.Text, nullable=False)
    cover_image = db.Column(db.String(300), nullable=False)
    published_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    destination_id = db.Column(db.Integer, db.ForeignKey("destination.id"), nullable=False)

    destination = db.relationship("Destination", backref=db.backref("posts", lazy=True))


class Comment(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120), nullable=False)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    post_id = db.Column(db.Integer, db.ForeignKey("post.id"), nullable=False)

    post = db.relationship("Post", backref=db.backref("comments", lazy=True, cascade="all,delete"))


class NewsletterSubscriber(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(200), unique=True, nullable=False)
    subscribed_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class ContactMessage(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    subject = db.Column(db.String(180), nullable=False)
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class TravelTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(180), nullable=False)
    content = db.Column(db.Text, nullable=False)
    destination_id = db.Column(db.Integer, db.ForeignKey("destination.id"), nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)

    destination = db.relationship("Destination", backref=db.backref("tips", lazy=True, cascade="all,delete"))


class GuestSatisfaction(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    guest_name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(200), nullable=False)
    rating = db.Column(db.Integer, nullable=False)
    highlight = db.Column(db.String(200), nullable=False)
    suggestion = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


class FreshTravelTip(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    author_name = db.Column(db.String(120), nullable=False)
    destination = db.Column(db.String(120), nullable=False)
    tip = db.Column(db.Text, nullable=False)
    likes = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)


def slugify(value: str) -> str:
    value = value.lower().strip()
    value = re.sub(r"[^a-z0-9]+", "-", value)
    return value.strip("-")


def make_unique_slug(title: str) -> str:
    base_slug = slugify(title)
    slug = base_slug
    count = 2

    while Post.query.filter_by(slug=slug).first() is not None:
        slug = f"{base_slug}-{count}"
        count += 1

    return slug


def seed_data() -> None:
    if Destination.query.count() > 0:
        return

    destinations = [
        Destination(
            name="Siargao",
            country="Philippines",
            description="Surf breaks, palm-lined roads, and relaxed island energy.",
            image_url="https://images.unsplash.com/photo-1518509562904-e7ef99cdcc86?auto=format&fit=crop&w=1200&q=80",
        ),
        Destination(
            name="Kyoto",
            country="Japan",
            description="Temples, tea houses, and neighborhoods full of seasonal color.",
            image_url="https://images.unsplash.com/photo-1493976040374-85c8e12f0c0e?auto=format&fit=crop&w=1200&q=80",
        ),
    ]

    for destination in destinations:
        db.session.add(destination)

    db.session.flush()

    sample_post = Post(
        title="Three Days in Siargao: Surf, Food, and Slow Mornings",
        slug="three-days-in-siargao-surf-food-and-slow-mornings",
        excerpt="A simple itinerary for first-time visitors who want both adventure and downtime.",
        content=(
            "Day 1 starts with island coffee and a tricycle ride to Cloud 9. "
            "Spend the afternoon at Maasin River for paddle boarding, then end your night with seafood by the beach.\n\n"
            "Day 2 is for island hopping: Naked Island, Daku, and Guyam. Bring water shoes and sunscreen.\n\n"
            "Day 3 is intentionally slow. Rent a scooter, follow the coastal road, and stop wherever the light looks good."
        ),
        cover_image="https://images.unsplash.com/photo-1473116763249-2faaef81ccda?auto=format&fit=crop&w=1400&q=80",
        destination_id=destinations[0].id,
    )

    db.session.add(sample_post)
    db.session.add(
        TravelTip(
            title="Best time to visit Cloud 9",
            content="Sunrise sessions are calmer and less crowded. Bring reef-safe sunscreen and water shoes.",
            destination_id=destinations[0].id,
        )
    )
    db.session.add(
        FreshTravelTip(
            author_name="Ari",
            destination="Siargao",
            tip="Carry a lightweight rain jacket even in sunny months for sudden tropical showers.",
            likes=3,
        )
    )
    db.session.commit()


def estimate_read_time(text: str) -> int:
    word_count = len(text.split())
    return max(1, round(word_count / 220))


def get_favorites() -> list[str]:
    return session.get("favorites", [])


def is_favorite_slug(slug: str) -> bool:
    return slug in get_favorites()


@app.route("/")
def home():
    search_query = request.args.get("q", "").strip()
    destination_filter = request.args.get("destination", "").strip()
    sort_by = request.args.get("sort", "latest")

    posts_query = Post.query.join(Destination)

    if search_query:
        like_pattern = f"%{search_query}%"
        posts_query = posts_query.filter(
            Post.title.ilike(like_pattern)
            | Post.excerpt.ilike(like_pattern)
            | Post.content.ilike(like_pattern)
            | Destination.name.ilike(like_pattern)
            | Destination.country.ilike(like_pattern)
        )

    if destination_filter:
        posts_query = posts_query.filter(Destination.name == destination_filter)

    if sort_by == "popular":
        posts_query = posts_query.outerjoin(Comment).group_by(Post.id).order_by(func.count(Comment.id).desc(), Post.published_at.desc())
    else:
        posts_query = posts_query.order_by(Post.published_at.desc())

    posts = posts_query.all()
    destinations = Destination.query.order_by(Destination.name.asc()).all()
    featured_post = posts[0] if posts else None

    destination_spotlight = (
        db.session.query(Destination, func.count(Post.id).label("post_count"))
        .outerjoin(Post)
        .group_by(Destination.id)
        .order_by(func.count(Post.id).desc(), Destination.name.asc())
        .limit(3)
        .all()
    )

    latest_tips = TravelTip.query.order_by(TravelTip.created_at.desc()).limit(4).all()
    fresh_tips = FreshTravelTip.query.order_by(FreshTravelTip.created_at.desc()).limit(4).all()
    avg_rating = db.session.query(func.avg(GuestSatisfaction.rating)).scalar() or 0
    satisfaction_count = GuestSatisfaction.query.count()

    favorites = get_favorites()
    return render_template(
        "home.html",
        posts=posts,
        destinations=destinations,
        featured_post=featured_post,
        destination_spotlight=destination_spotlight,
        favorites=favorites,
        search_query=search_query,
        destination_filter=destination_filter,
        sort_by=sort_by,
        latest_tips=latest_tips,
        fresh_tips=fresh_tips,
        avg_rating=round(avg_rating, 1),
        satisfaction_count=satisfaction_count,
    )


@app.route("/destinations/<int:destination_id>")
def destination_detail(destination_id):
    destination = Destination.query.get_or_404(destination_id)
    posts = Post.query.filter_by(destination_id=destination.id).order_by(Post.published_at.desc()).all()
    tips = TravelTip.query.filter_by(destination_id=destination.id).order_by(TravelTip.created_at.desc()).all()
    return render_template("destination_detail.html", destination=destination, posts=posts, tips=tips)


@app.route("/post/<slug>", methods=["GET", "POST"])
def post_detail(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()

    if request.method == "POST":
        author_name = request.form.get("author_name", "").strip()
        content = request.form.get("content", "").strip()

        if not author_name or not content:
            flash("Name and comment are required.", "error")
        else:
            comment = Comment(author_name=author_name, content=content, post_id=post.id)
            db.session.add(comment)
            db.session.commit()
            flash("Comment posted successfully.", "success")
            return redirect(url_for("post_detail", slug=slug))

    comments = Comment.query.filter_by(post_id=post.id).order_by(Comment.created_at.desc()).all()
    related_posts = (
        Post.query.filter(Post.destination_id == post.destination_id, Post.id != post.id)
        .order_by(Post.published_at.desc())
        .limit(3)
        .all()
    )
    return render_template(
        "post_detail.html",
        post=post,
        comments=comments,
        related_posts=related_posts,
        is_favorite=is_favorite_slug(post.slug),
        read_time=estimate_read_time(post.content),
    )


@app.route("/about")
def about():
    post_count = Post.query.count()
    destination_count = Destination.query.count()
    subscriber_count = NewsletterSubscriber.query.count()
    return render_template(
        "about.html",
        post_count=post_count,
        destination_count=destination_count,
        subscriber_count=subscriber_count,
    )


@app.route("/contact", methods=["GET", "POST"])
def contact():
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        email = request.form.get("email", "").strip().lower()
        subject = request.form.get("subject", "").strip()
        message = request.form.get("message", "").strip()

        if not all([name, email, subject, message]):
            flash("Please complete all fields.", "error")
        else:
            db.session.add(
                ContactMessage(
                    name=name,
                    email=email,
                    subject=subject,
                    message=message,
                )
            )
            db.session.commit()
            flash("Thanks for reaching out. We received your message.", "success")
            return redirect(url_for("contact"))

    return render_template("contact.html")


@app.route("/trip-planner", methods=["GET", "POST"])
def trip_planner():
    estimate = None

    if request.method == "POST":
        destination_name = request.form.get("destination_name", "").strip()
        days_raw = request.form.get("days", "").strip()
        style = request.form.get("style", "midrange").strip()

        if not destination_name or not days_raw.isdigit() or int(days_raw) <= 0:
            flash("Enter a destination and valid number of days.", "error")
        else:
            days = int(days_raw)
            daily_map = {
                "budget": 55,
                "midrange": 110,
                "comfort": 180,
                "luxury": 280,
            }
            daily_budget = daily_map.get(style, 110)
            subtotal = days * daily_budget
            misc = round(subtotal * 0.15)
            total = subtotal + misc
            estimate = {
                "destination": destination_name,
                "days": days,
                "style": style.title(),
                "daily_budget": daily_budget,
                "subtotal": subtotal,
                "misc": misc,
                "total": total,
            }

    return render_template("trip_planner.html", estimate=estimate)


@app.route("/guest-satisfaction", methods=["GET", "POST"])
def guest_satisfaction():
    if request.method == "POST":
        guest_name = request.form.get("guest_name", "").strip()
        email = request.form.get("email", "").strip().lower()
        rating_raw = request.form.get("rating", "").strip()
        highlight = request.form.get("highlight", "").strip()
        suggestion = request.form.get("suggestion", "").strip()

        if not all([guest_name, email, rating_raw, highlight, suggestion]):
            flash("Please complete all fields.", "error")
        elif not rating_raw.isdigit() or int(rating_raw) < 1 or int(rating_raw) > 5:
            flash("Rating must be between 1 and 5.", "error")
        else:
            db.session.add(
                GuestSatisfaction(
                    guest_name=guest_name,
                    email=email,
                    rating=int(rating_raw),
                    highlight=highlight,
                    suggestion=suggestion,
                )
            )
            db.session.commit()
            flash("Thank you for your feedback.", "success")
            return redirect(url_for("guest_satisfaction"))

    recent_feedback = GuestSatisfaction.query.order_by(GuestSatisfaction.created_at.desc()).limit(6).all()
    avg_rating = db.session.query(func.avg(GuestSatisfaction.rating)).scalar() or 0
    return render_template(
        "guest_satisfaction.html",
        recent_feedback=recent_feedback,
        avg_rating=round(avg_rating, 1),
    )


@app.route("/fresh-travel-tips", methods=["GET", "POST"])
def fresh_travel_tips():
    if request.method == "POST":
        author_name = request.form.get("author_name", "").strip()
        destination = request.form.get("destination", "").strip()
        tip = request.form.get("tip", "").strip()

        if not all([author_name, destination, tip]):
            flash("Please complete all fields.", "error")
        else:
            db.session.add(
                FreshTravelTip(
                    author_name=author_name,
                    destination=destination,
                    tip=tip,
                )
            )
            db.session.commit()
            flash("Fresh travel tip shared successfully.", "success")
            return redirect(url_for("fresh_travel_tips"))

    tips = FreshTravelTip.query.order_by(FreshTravelTip.created_at.desc()).all()
    return render_template("fresh_tips.html", tips=tips)


@app.route("/fresh-travel-tips/<int:tip_id>/like", methods=["POST"])
def like_fresh_tip(tip_id):
    tip = FreshTravelTip.query.get_or_404(tip_id)
    tip.likes += 1
    db.session.commit()
    flash("Thanks for supporting this tip.", "success")
    return redirect(request.referrer or url_for("fresh_travel_tips"))


@app.route("/subscribe", methods=["POST"])
def subscribe():
    email = request.form.get("email", "").strip().lower()

    if not email or "@" not in email:
        flash("Enter a valid email address.", "error")
        return redirect(request.referrer or url_for("home"))

    existing = NewsletterSubscriber.query.filter_by(email=email).first()
    if existing:
        flash("You are already subscribed.", "success")
    else:
        db.session.add(NewsletterSubscriber(email=email))
        db.session.commit()
        flash("Subscription successful. Welcome aboard.", "success")

    return redirect(request.referrer or url_for("home"))


@app.route("/favorites/toggle/<slug>", methods=["POST"])
def toggle_favorite(slug):
    post = Post.query.filter_by(slug=slug).first_or_404()

    favorites = get_favorites()
    if slug in favorites:
        favorites.remove(slug)
        flash(f"Removed '{post.title}' from favorites.", "success")
    else:
        favorites.append(slug)
        flash(f"Saved '{post.title}' to favorites.", "success")

    session["favorites"] = favorites
    return redirect(request.referrer or url_for("post_detail", slug=slug))


def is_admin_logged_in() -> bool:
    return session.get("is_admin", False)


@app.route("/admin/login", methods=["GET", "POST"])
def admin_login():
    if is_admin_logged_in():
        return redirect(url_for("admin_dashboard"))

    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")

        if username == ADMIN_USERNAME and password == ADMIN_PASSWORD:
            session["is_admin"] = True
            flash("Logged in successfully.", "success")
            return redirect(url_for("admin_dashboard"))

        flash("Invalid credentials.", "error")

    return render_template("admin_login.html")


@app.route("/admin/logout")
def admin_logout():
    session.pop("is_admin", None)
    flash("You are logged out.", "success")
    return redirect(url_for("home"))


@app.route("/admin")
def admin_dashboard():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    posts = Post.query.order_by(Post.published_at.desc()).all()
    destinations = Destination.query.order_by(Destination.name.asc()).all()
    recent_messages = ContactMessage.query.order_by(ContactMessage.created_at.desc()).limit(5).all()
    newsletter_count = NewsletterSubscriber.query.count()
    tips_count = TravelTip.query.count()
    guest_feedback_count = GuestSatisfaction.query.count()
    fresh_tip_count = FreshTravelTip.query.count()
    return render_template(
        "admin_dashboard.html",
        posts=posts,
        destinations=destinations,
        recent_messages=recent_messages,
        newsletter_count=newsletter_count,
        tips_count=tips_count,
        guest_feedback_count=guest_feedback_count,
        fresh_tip_count=fresh_tip_count,
    )


@app.route("/admin/destinations/new", methods=["GET", "POST"])
def admin_new_destination():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    if request.method == "POST":
        name = request.form.get("name", "").strip()
        country = request.form.get("country", "").strip()
        description = request.form.get("description", "").strip()
        image_url = request.form.get("image_url", "").strip()

        if not all([name, country, description, image_url]):
            flash("All fields are required.", "error")
        else:
            destination = Destination(
                name=name,
                country=country,
                description=description,
                image_url=image_url,
            )
            db.session.add(destination)
            db.session.commit()
            flash("Destination created.", "success")
            return redirect(url_for("admin_dashboard"))

    return render_template("destination_form.html")


@app.route("/admin/posts/new", methods=["GET", "POST"])
def admin_new_post():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    destinations = Destination.query.order_by(Destination.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        excerpt = request.form.get("excerpt", "").strip()
        content = request.form.get("content", "").strip()
        cover_image = request.form.get("cover_image", "").strip()
        destination_id = request.form.get("destination_id", "").strip()

        if not all([title, excerpt, content, cover_image, destination_id]):
            flash("All fields are required.", "error")
        else:
            post = Post(
                title=title,
                slug=make_unique_slug(title),
                excerpt=excerpt,
                content=content,
                cover_image=cover_image,
                destination_id=int(destination_id),
            )
            db.session.add(post)
            db.session.commit()
            flash("Post created.", "success")
            return redirect(url_for("admin_dashboard"))

    return render_template("post_form.html", destinations=destinations)


@app.route("/admin/tips/new", methods=["GET", "POST"])
def admin_new_tip():
    if not is_admin_logged_in():
        return redirect(url_for("admin_login"))

    destinations = Destination.query.order_by(Destination.name.asc()).all()

    if request.method == "POST":
        title = request.form.get("title", "").strip()
        content = request.form.get("content", "").strip()
        destination_id = request.form.get("destination_id", "").strip()

        if not all([title, content, destination_id]):
            flash("All fields are required.", "error")
        else:
            db.session.add(
                TravelTip(
                    title=title,
                    content=content,
                    destination_id=int(destination_id),
                )
            )
            db.session.commit()
            flash("Travel tip created.", "success")
            return redirect(url_for("admin_dashboard"))

    return render_template("tip_form.html", destinations=destinations)


if __name__ == "__main__":
    with app.app_context():
        db.create_all()
        seed_data()

    app.run(debug=True)
