#!/usr/bin/env python

#
# This is a PicasaWeb photo exporter for OpenPhoto
#
# This program is Copyright (c) Olivier Berger <oberger@ouvaton.org>
# 
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#      http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# Code is heavily inspired by the flickr exporter

# import os for file system functions
import datetime
import os
import time
import json

import gdata.photos.service

def fetch(login, app_password, albumid = None):
    gd_client = gdata.photos.service.PhotosService()
    gd_client.email = login
    gd_client.password = app_password

    gd_client.source = 'openphoto-exporter-1'
    gd_client.ProgrammaticLogin()

    if not albumid :
        albums = gd_client.GetUserFeed()

        for album in albums.entry:
            print 'title: %s, number of photos: %s, id: %s' % (album.title.text,
                                                               album.numphotos.text, album.gphoto_id.text)
    else :
        username = 'default'
        albumentry = gd_client.GetFeed(
            '/data/feed/api/user/%s/albumid/%s' % (
                username, albumid))
        #print albumentry
        #print 'Access:', albumentry.access.text
        permission = 0
        if albumentry.access.text == 'public':
            permission = 1

        photos = gd_client.GetFeed(
            '/data/feed/api/user/%s/albumid/%s?kind=photo' % (
                username, albumid))

        for photo in photos.entry:

            p = {}

            photoid = photo.gphoto_id.text

            p['id'] = photoid
            p['permission'] = bool(permission)
            p['title'] = photo.title.text
            #p['license'] = 
            
            description = photo.summary.text
            if description is not None:
                p['description'] = description

            where = photo.geo.Point.pos.text
            if where :
                (latitude, longitude) = where.split(' ')
                p['latitude'] = float(latitude)
                p['longitude'] = float(longitude)

            tagsl = []
            tags = gd_client.GetFeed(photo.GetTagsUri())
            for tag in tags.entry:
                tagsl.append(tag.title.text)
            if tagsl :
                p['tags'] = ",".join(tagsl)
            
            epoch = float(photo.timestamp.text)/1000
            p['dateTaken'] = int(time.mktime(time.gmtime(epoch)))
            #print 'dateTaken:', photo.timestamp.isoformat()
            p['dateUploaded'] = int(time.mktime(time.strptime(photo.published.text, '%Y-%m-%dT%H:%M:%S.000Z')))
            
            p['photo'] = photo.media.content[0].url
            #print 'AlbumID:', photo.albumid.text
            # if photo.exif.make and photo.exif.model:
            #     camera = '%s %s' % (photo.exif.make.text, photo.exif.model.text)
            # else:
            #     camera = 'unknown'
            # print 'Camera:', camera
            # print 'First Thumbnail:', photo.media.thumbnail[0].url
            # if photo.commentCount.text != '0' :
            #     comments = gd_client.GetFeed(photo.GetCommentsUri())
            #     for comment in comments.entry:
            #         print 'Comment', comment.content.text
            #print photo
            
            #print p

            t = datetime.datetime.fromtimestamp(float(p['dateUploaded']))
            filename = '%s-%s' % (t.strftime('%Y%m%dT%H%M%S'), p['id'])

            print "  * Storing photo %s to fetched/%s.json" % (p['id'], filename),
            f = open("fetched/%s.json" % filename, 'w')
            f.write(json.dumps(p))
            f.close()
            print "OK"


# create a directory only if it doesn't already exist
def createDirectorySafe( name ):
  if not os.path.exists(name):
    os.makedirs(name)


if __name__ == '__main__':
  import argparse

  parser = argparse.ArgumentParser(description='Backup your PicasaWeb photos')
  parser.add_argument('--login', required=True, help='Google account email')
  parser.add_argument('--app-password', required=True, help='Application specific password')
  parser.add_argument('--album-id', required=False, help='Album id')

  config = parser.parse_args()

  # check if a fetched directory exist else create it
  createDirectorySafe('fetched')
  fetch(config.login, config.app_password, config.album_id)
