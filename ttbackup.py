#!/usr/bin/env python
import os, sys
backup_dir = open('/tmp/tt_backup_dir').read()
srcpath = sys.argv[1]
only_filename = srcpath.split('/')[-1]
dest_path = '%s/%s.%s' % (backup_dir, only_filename, sys.argv[2])

os.popen('cp -f "%s" "%s"' % (srcpath, dest_path))
os.popen('echo "%s" > ~/test_t' % os.environ)
