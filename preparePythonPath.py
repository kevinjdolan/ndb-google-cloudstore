import sys

# make sure to drop any appengine runtimes already on the path
for item in list(sys.path):
    if item.endswith('google_appengine'):
        sys.path.remove(item)

# add our custom runtimes to the path
sys.path.append('./google_appengine-1.9.25') # note: this contains a symlink to protobuf because i'm dumb
sys.path.append('./googledatastore-v1beta2-rev1-2.1.2')