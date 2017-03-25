#/usr/bin/env python2.7

"""radcast.py: main functionality of radcast"""

import subprocess
import os
import re
import jinja2
import logging
import vimeo

__copyright__ = "Copyright 2007, Josh Wheeler"
__license__ = "GPL"
__status__ = "Development"

#    radcast: radical podcast automation
#    Copyright (C) 2017 Josh Wheeler
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see <http://www.gnu.org/licenses/>.

VIMEO_CLIENT_ID = '1a891bcce93f182903566f9757351c3a3d639788'
VIMEO_CLIENT_SECRET = 'nb8zjvrTjdjNhmBmfm9ObyovztYJd6TQBH01W4CweCHwebyElloUX6JOdCd8iz8xk1H0czC/cPajoMbfm3Cxh/jOBzHczk7SOlhbbN/sPgcje3vZ143a+Km/g8SRsSs4'
VIMEO_ACCESS_TOKEN = '48b5af17781ec2cd705b7cc4d07d9a38'

cwd = os.getcwd()

v = vimeo.VimeoClient(
    token=VIMEO_ACCESS_TOKEN,
    key=VIMEO_CLIENT_ID,
    secret=VIMEO_CLIENT_SECRET
)


def generate_melt(template, media_file, in_frame, out_frame):
    """Take template, video file, in/out frames, and
    generate a melt file of template_name.melt"""

    output_file = template

    try:
        loader = jinja2.PackageLoader("radcast", "templates")
        env = jinja2.Environment(loader=loader)
        mlt_file = open(output_file, "w+")
        template_xml = env.get_template(template)
        # set up template variables
        render = template_xml.render(
            media_file=media_file,
            in_frame=in_frame,
            out_frame=out_frame,
            )
        mlt_file.write(render)

    except jinja2.TemplateNotFound, e:
        logging.error("Bummer! %s is missing from the template stack" % e)

    except:
        logging.error("Bummer! An exception occurred while generating the melt")

    finally:
        logging.error("Reached cleanup stage of melt generator")
        mlt_file.close()


def slugify(s):
    """
    Converts string to lowercase, removes non-alpha characters,
    and converts spaces to underscores.
    """
    s = re.sub('[^\w\s-]', '', s).strip().lower()
    s = re.sub('[-\s]+', '_', s)
    return s


def encode_video(file, title):
    """Accept MLT producer file and encode video"""

    mlt_profile = 'atsc_720p_2997'
    mlt_producer = file

    output_file = slugify(title) + ".mkv"

    # TODO check available space before encoding

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


def encode_audio(file, title):
    """Accept MLT producer file and encode audio"""

    mlt_producer = file

    output_file = slugify(title) + ".mp3"

    # TODO check available space before encoding

    try:

        logging.debug("Encoding podcast video from %s" % mlt_producer)

        command = [
            '-producer', mlt_producer,
            '-consumer', 'avformat:' + output_file,
            'ab=64k',
            'ac=1'
        ]

        subprocess.call(command)

    except:
        logging.error("Bummer! An exception occurred in the audio encoding process.")


def ffmpeg_encode_audio(file, title):
    """Encode audio to mp3 using ffmpeg"""

    # TODO check available space before encoding

    input_file = file
    output_file = slugify(title) + ".mp3"

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
    pass


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

# TODO archive original media to a storage device
