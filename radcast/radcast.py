#/usr/bin/env python2.7

import subprocess
import os
import time
import jinja2
import logging
import vimeo

# Requires jinja2, pyvimeo

__author__ = "Josh Wheeler"
__copyright__ = "Copyright 2007, Josh Wheeler"
__license__ = "MIT"
__maintainer__ = "Josh Wheeler"
__email__ = "mantlepro@gmail.com"
__status__ = "Development"

# open the clip
# choose in/out
# preview beginning and ending for a quick quality check
# hit the GO button

VIMEO_CLIENT_ID = '1a891bcce93f182903566f9757351c3a3d639788'
VIMEO_CLIENT_SECRET = 'nb8zjvrTjdjNhmBmfm9ObyovztYJd6TQBH01W4CweCHwebyElloUX6JOdCd8iz8xk1H0czC/cPajoMbfm3Cxh/jOBzHczk7SOlhbbN/sPgcje3vZ143a+Km/g8SRsSs4'
VIMEO_ACCESS_TOKEN = '48b5af17781ec2cd705b7cc4d07d9a38'

v = vimeo.VimeoClient(
    token=VIMEO_ACCESS_TOKEN,
    key=VIMEO_CLIENT_ID,
    secret=VIMEO_CLIENT_SECRET
)


def generate_melt(video_file, in_frame, out_frame):
    """Take user-defined in/out frames, and generate a melt file"""

    output_file = "edit.melt"

    try:

        loader = jinja2.PackageLoader("editty", "templates")
        env = jinja2.Environment(loader=self.loader)
        mlt_file = open(settings.title + ".melt", "w+")
        template_xml = self.env.get_template("serialize.melt")
        # set up template variables
        render = self.template_xml.render(
            video_file=video_file,
            in_frame=in_frame,
            out_frame=out_frame,
            )
        mlt_file.write(render)

    except:
        logging.error("Bummer! An exception occurred while generating the melt.")

    finally:
        logging.error("Reached cleanup stage of generate_melt.")
        mlt_file.close()


cwd = os.getcwd()

# set up logging
logging.basicConfig(
    filename='radcast.log',
    format='%(levelname)s: %(message)s',
    filemode="w",
    level=logging.DEBUG
)

logging.info("Started %s" % time.strftime("%a, %d %b %Y %T %Z"))


def encode_video(file):
    """Accept a MLT producer and encode video"""

    output_file = "test.mkv"
    mlt_profile = 'atsc_720p_2997'
    mlt_producer = file

    # TODO check for available space before encoding

    try:

        logging.debug("Encoding podcast video from %s" % mlt_producer)

        command = [
            'melt', '-profile', mlt_profile,
            '-producer', mlt_producer,
            '-consumer', 'avformat:' + output_file,
            'vcodec=libx264',
            'color_primaries=bt709',
            'preset=slower',
            'b=7500k',
            'movflags=+faststart',
            'acodec=aac',
            'ab=320k',
            'ac=2'
        ]

        subprocess.call(command)

    except:
        logging.error("Bummer! An exception occurred in the video encoding process.")

    finally:
        # run always, even if there are errors
        logging.debug("Reached encode_video post-processing / cleanup")
        pass


def encode_audio(file):
    """Encode audio to mp3"""

    # TODO check for available space before encoding

    input_file = file
    output_file = "test.mp3"

    try:

        logging.debug("Encoding podcast audio from %s" % input_file)

        command = [
            'ffmpeg', '-i', input_file,
            '-acodec', 'mp3',
            '-ab', '64k',
            '-ac', '1',
            output_file,
        ]
        subprocess.call(command)

    except:
        logging.error("Bummer! An exception occurred in the audio encoding process.")

    finally:
        # run always, even if there are errors
        logging.debug("Reached encode_audio post-processing / cleanup.")
        pass


def copy_to_cloud(destination):
    """Add media to cloud device at destination"""
    # check available space at destination


def send_notification():
    """Notify podcast admins that the podcast passed or failed"""
    logging.info("Sending notification.")


# def begin_vimeo_authenticate(vimeo_client):
#     """This section is used to determine where to direct the user."""
# 
#     v = vimeo_client
# 
#     vimeo_authorization_url = v.auth_url(['public', 'private'], 'https://example.com')
# 
#     # Your application should now redirect to vimeo_authorization_url.
# 
# 
# def complete_vimeo_authentication(vimeo_client):
#     """This section completes the authentication for the user."""
# 
#     # You should retrieve the "code" from the URL string Vimeo redirected to.
#     # Here that's named CODE_FROM_URL
#     try:
#         token, user, scope = v.exchange_code(CODE_FROM_URL, 'https://example.com')
# 
#     except vimeo.auth.GrantFailed:
#         # Handle the failure to get a token from the provided code and redirect.
#         pass
# 
#     # Store the token, scope and any additional user data you require in your database so users do not have to re-authorize your application repeatedly.


def upload_to_vimeo(vimeo_client, file, name=None, description=None, image=None):

    """Upload to Vimeo as a draft"""

    v = vimeo_client

    try:
        # use the following for oauth
        # token = v.load_client_credentials()

        video_uri = v.upload(file)
        logging.info("Uploading to vimeo at %s" % video_uri)

        # add metadata to video at vimeo_uri

        if name and description:
            v.patch(video_uri, data={
                'name': name,
                'description': description,
            })
            logging.info("Added title (%s) and description to %s" % name, video_uri)

        elif name:
            v.patch(video_uri, data={'name': name})
            logging.info("Added title (%s) to %s" % name, video_uri)

        if image:
            v.upload_picture(video_uri, image, activate=True)

    except vimeo.UploadTicketCreationFailure, e:
        logging.error("Error in upload_to_vimeo: %s" % e)

    except vimeo.auth.GrantFailed, e:
        # Handle the failure to get a token from the provided code and redirect.
        logging.error("Vimeo auth grant failed %s" % e)


# TODO if failed, try again n times before giving up altogether

# TODO archive original media to a storage device.

