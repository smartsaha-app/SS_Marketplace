import cloudinary
import cloudinary.uploader
from cloudinary.utils import cloudinary_url

cloudinary.config( 
    cloud_name="dfavjwzwz", 
    api_key="615664517363892", 
    api_secret="vObjA2NuGj_jYX-FaxIY10Jvrvc", 
    secure=True
)

def upload_media(file, public_id=None):
    """
    Upload un fichier sur Cloudinary et retourne l'URL sécurisée optimisée.
    """
    upload_result = cloudinary.uploader.upload(file, public_id=public_id)
    media_url = upload_result["secure_url"]

    optimize_url, _ = cloudinary_url(public_id or upload_result["public_id"], fetch_format="auto", quality="auto")
    return optimize_url
