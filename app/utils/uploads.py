"""Media upload helper — local disk + optional Cloudinary."""
import os
import uuid
from werkzeug.utils import secure_filename
from flask import current_app, url_for

ALLOWED = {'png', 'jpg', 'jpeg', 'gif', 'webp', 'avif', 'ico', 'svg'}


def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED


def _ext(filename):
    return filename.rsplit('.', 1)[1].lower() if '.' in filename else 'jpg'


def upload_file(file_storage, folder='general'):
    """
    Upload a FileStorage object.
    Returns public URL string, or None on failure.
    Uses Cloudinary when credentials are set; otherwise local static/uploads.
    """
    if not file_storage or not file_storage.filename:
        return None
    if not allowed_file(file_storage.filename):
        return None

    cloud_name = current_app.config.get('CLOUDINARY_CLOUD_NAME') or ''
    api_key = current_app.config.get('CLOUDINARY_API_KEY') or ''
    api_secret = current_app.config.get('CLOUDINARY_API_SECRET') or ''

    if cloud_name and api_key and api_secret:
        try:
            import cloudinary
            import cloudinary.uploader
            cloudinary.config(
                cloud_name=cloud_name,
                api_key=api_key,
                api_secret=api_secret,
                secure=True,
            )
            result = cloudinary.uploader.upload(
                file_storage,
                folder=f'darshan-nepal/{folder}',
                resource_type='image',
            )
            return result.get('secure_url')
        except Exception as e:
            current_app.logger.warning('Cloudinary upload failed, falling back to local: %s', e)

    # Local fallback
    upload_root = current_app.config.get('UPLOAD_FOLDER')
    dest_dir = os.path.join(upload_root, folder)
    os.makedirs(dest_dir, exist_ok=True)
    name = f'{uuid.uuid4().hex}.{_ext(file_storage.filename)}'
    path = os.path.join(dest_dir, name)
    file_storage.save(path)
    # URL relative to static
    return url_for('static', filename=f'uploads/{folder}/{name}')


def delete_local_if_needed(url):
    """Best-effort delete of local upload file from a URL path."""
    if not url or 'uploads/' not in url:
        return
    try:
        # url may be /static/uploads/folder/file
        marker = 'uploads/'
        idx = url.find(marker)
        if idx < 0:
            return
        rel = url[idx:]
        full = os.path.join(current_app.static_folder, rel)
        if os.path.isfile(full):
            os.remove(full)
    except Exception:
        pass
