#!/usr/bin/env python

# import os for file system functions
import os

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
        photos = gd_client.GetFeed(
            '/data/feed/api/user/%s/albumid/%s?kind=photo' % (
                username, albumid))
        for photo in photos.entry:
            print 'Photo title:', photo.title.text

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
