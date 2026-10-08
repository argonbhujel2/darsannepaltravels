from flask import Blueprint, render_template, request
from app.models import BlogPost

blog_bp = Blueprint('blog', __name__)


@blog_bp.route('/')
def list_posts():
    category = request.args.get('category', '')
    page = request.args.get('page', 1, type=int)
    query = BlogPost.query.filter_by(status='published')
    if category:
        query = query.filter_by(category=category)
    pagination = query.order_by(BlogPost.published_date.desc()).paginate(page=page, per_page=9, error_out=False)
    categories = ['Travel Guide', 'Destination Guide', 'Trekking', 'Pilgrimage', 'Travel Tips', 'Nepal Culture', 'Road Trips', 'Tour Updates']
    return render_template('blog/list.html', posts=pagination.items, pagination=pagination, categories=categories, active_category=category)


@blog_bp.route('/<slug>')
def post_detail(slug):
    post = BlogPost.query.filter_by(slug=slug, status='published').first_or_404()
    related = BlogPost.query.filter(
        BlogPost.status == 'published',
        BlogPost.id != post.id,
        BlogPost.category == post.category
    ).limit(3).all()
    return render_template('blog/detail.html', post=post, related=related)
