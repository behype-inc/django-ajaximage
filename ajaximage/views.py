import json
from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponse
from django.utils.text import slugify
from django.views.decorators.http import require_POST
from .forms import FileForm
from hypegallery.models import ProfileImage
import logging
from hypegallery.image_utils import create_hype_image
logger = logging.getLogger("profiles")
UPLOAD_PATH = getattr(settings, 'AJAXIMAGE_DIR', 'ajaximage/')
AUTH_TEST = getattr(settings, 'AJAXIMAGE_AUTH_TEST', lambda u: u.is_staff)
FILENAME_NORMALIZER = getattr(settings, 'AJAXIMAGE_FILENAME_NORMALIZER', slugify)


#image size to check 640 640
@require_POST
@login_required
def ajaximage(request, upload_to=None, max_width=None, max_height=None, crop=None, form_class=FileForm):
    form = form_class(request.POST, request.FILES)
    if form.is_valid():
        file_ = form.cleaned_data['file']

        image_types = ['image/png', 'image/jpg', 'image/jpeg', 'image/pjpeg',
                       'image/gif']

        if file_.content_type not in image_types:
            data = json.dumps({'error': 'Bad image format.'})
            return HttpResponse(data, content_type="application/json", status=403)
        logger.debug("creating thumbnails")
        try:
            hype_image = create_hype_image(file_,request.user)
            ProfileImage.objects.create(image=hype_image,profile=request.user.profile,order=ProfileImage.objects
                                        .filter(profile=request.user.profile).count())
            out = json.dumps({'url': hype_image.get_normal() , "pk":hype_image.pk})
            return HttpResponse(out, content_type="application/json")
        except Exception as e:
            logger.debug(str(e))
            return HttpResponse(status=500)
    return HttpResponse(status=403)
