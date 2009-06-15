#!/usr/bin/env python

"""
Script used to manage Tokyo Tyrant nodes.

Usage is:
    python manager.py -c config.py help
"""

import time
import re
import getopt, sys
import memcache
import os
import shutil
from os.path import dirname, join, realpath


config = {}


#--- Command line managers ----------------------------------------------
def help():
    print 'Script that is used to handle Tokyo Tyrant nodes.'
    print ''
    print 'Starting nodes:'
    print '   python manager.py -c config.py all start'
    print '   python manager.py -c config.py lookup1 start'
    print ''
    print 'Stopping nodes:'
    print '   python manager.py -c config.py all stop'
    print '   python manager.py -c config.py lookup1 stop'
    print ''
    print 'Status:'
    print '   python manager.py -c config.py all status '
    print '   python manager.py -c config.py lookup1 status'
    print ''
    print 'Misc:'
    print '   python manager.py -c config.py purge_logs'
    print '   python manager.py -c config.py delete_logs'
    print '   python manager.py -c config.py delete_data'
    print ''
    print '   python manager.py -c config.py hot_copy'
    print '   python manager.py -c config.py hot_restore hot_copy_1245046685.zip'
    print ''
    print 'View a sample config file in config.sample.py.'

    sys.exit(2)


def start(args, options):
    if 'all' in args:
        for node in nodes():
            start_node(node)
    else:
        start_node(node_by_name(args[0]))


def stop(args, options):
    if 'all' in args:
        for node in nodes():
            stop_node(node)
    else:
        stop_node(node_by_name(args[0]))


def status(args, options):
    if 'all' in args:
        for node in nodes():
            status_node(node)
    else:
        status_node(node_by_name(args[0]))



#--- Node managing ----------------------------------------------
def nodes():
    keys = config.get('NODES').keys()
    return [node_by_name(name) for name in sorted(keys)]


def node_by_name(name):
    """Returns node entry from config's NODES dictionary.
    Extra values are added such as name, host, m_host and data path"""

    node = config.get('NODES')[name]
    node['name'] = name

    node['full_host'] = node['host']
    node['host'], node['port'] = node['host'].split(':')

    node['m_host'], node['m_port'] = node['master'].split(':')

    node['data'] = config['DATA_DIR']
    return node


def get_port_pid(port):
    """Returns the pid of a ttserver running on `port`
    """
    cmd = 'ps aux | grep "ttserver" | grep "\-port %s" | grep -v "grep"' % port
    line = os.popen(cmd).read()

    if line:
        return  int(re.split('\s+', line)[1])
    else:
        return None


def start_node(node):
    """Starts `node`
    """
    log_dir = '%(data)s/logs/%(id)s/' % node
    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    os.popen("rm -f %(data)s/log_%(id)s" % node)
    os.popen("rm -f %(data)s/%(name)s.pid" % node)

    node['cur_pwd'] = os.getcwd()

    if config.get('DEBUG'):
        node['logging'] = '-ld -log %(data)s/logs/%(id)s/debug_log' % node
    else:
        node['logging'] = '-le'

    node['opts'] = config.get('TOKYO_SERVER_PARMS', '')
    command = "ttserver -host %(host)s -port %(port)s "\
              "%(master_cfg)s "\
              "-pid %(data)s/%(name)s.pid "\
              "-dmn "\
              " %(logging)s "\
              "-ulog %(data)s/logs/%(id)s/ -sid %(id)s "\
              "-rts %(data)s/data/%(id)s.rts "\
              "-ulim 128m "\
              "-ext %(cur_pwd)s/extensions/our.lua "\
              "-thnum 6 -tout 5 "\
              "%(data)s/data/%(id)s.tch%(opts)s"

    if config.get('USE_MASTER', False):
        node['master_cfg'] = "-mhost %(m_host)s -mport %(m_port)s "\
               % node
    else:
        node['master_cfg'] = ''

    command = command % node
    print command
    os.popen(command)

    print 'Starting node %s on: %s. Master node: %s' %\
            (node['name'], node['full_host'], node['master'])


def stop_node(node):
    """Stops `node`
    """
    pid = get_port_pid(node['port'])
    if pid:
        os.popen('kill %s' % pid)

    print 'Stopping node %s on: %s. Master node: %s' %\
            (node['name'], node['full_host'], node['master'])


def status_node(node):
    """Prints status about a node
    """
    #--- Determine if a node is running
    cmd = 'ps aux | grep "ttserver -host %(host)s -port %(port)s" | grep -v "grep"'
    cmd = cmd % node
    line = os.popen(cmd).read()
    is_running = line and True or False

    #--- Get server stats
    def get_stats(host, port):
        try:
            mc = memcache.Client(['%s:%s' % (host, port)])
            return mc.get_stats()[0][1]
        except:
            return None

    stats = get_stats(node['host'], node['port'])
    master_stats = get_stats(node.get('m_host'), node.get('m_port'))

    print '%s (%s:%s):' % (node['name'], node['host'], node['port'])

    def print_lines(lines):
        print '    %s' % ' - '.join(lines)

    #--- Print node info ----------------------------------------------
    lines = []

    if is_running:
        lines.append('node running')
    else:
        lines.append('NOT RUNNING')

    if stats:
        lines.append('node items: %s' % stats['curr_items'])
    print_lines(lines)

    #--- Print master info ----------------------------------------------
    lines = []
    if master_stats:
        lines.append('master %s running' % node['master'])
        lines.append('master items: %s' % master_stats['curr_items'])
    else:
        lines.append('master %s NOT REACHABLE' % node.get('master'))
    print_lines(lines)


#--- Logs, backups and data ----------------------------------------------
def hot_copy():
    """Takes a hot copy of all Tyrant nodes, without shutting them down.
    """
    import simplejson

    data_dir = '%s/data' % config['DATA_DIR']
    backup_dir = '%s/backup_dir/' % (config['DATA_DIR'])
    if not os.path.exists(backup_dir):
        os.mkdir(backup_dir)

    keys = config.get('NODES').keys()
    file_dir = os.path.abspath(os.path.dirname(__file__))
    ttbackup = '%s/ttbackup.sh' % file_dir

    #--- Do the backups ----------------------------------------------
    for name in sorted(keys):
        node = node_by_name(name)
        cmd = "tcrmgr copy -port %s %s '@.%s'" %\
                 (node['port'], node['host'], ttbackup)
        os.popen(cmd)
        print 'Done backup for %s:%s' % (node['host'], node['port'])

    #--- Move data into backup dir ----------------------------------------------
    for root, dirs, files in os.walk(data_dir):
        for file in files:
            try:
                id, ext, log_pos = file.split('.')
            except ValueError:
                continue
            os.popen('mv %s/%s %s' % (data_dir, file, backup_dir))
            print 'Moved %s to backup directory' % file

    #--- Pack them into a tar file ----------------------------------------------
    stamp = long(time.time())
    backup_file = '%s/hot_copy_%s.zip' % (config['DATA_DIR'], stamp)

    nodes = '%s/backup_dir/nodes.json' % (config['DATA_DIR'])
    open(nodes, 'w').write(simplejson.dumps(config['NODES']))

    os.popen('rm -f %s' % backup_file)
    os.popen('zip -jr %s %s' % (backup_file, backup_dir))
    os.popen('rm -rf %s' % backup_dir)

    print 'Created hot copy in %s' % (backup_file)


def hot_restore(args):
    """Restores `zip_file` in config['DATA_DIR']/restore_dir.
    Matches the slave nodes from the config file.
    """
    import simplejson
    zip_zip = args[1]

    #--- Create restore_dir ----------------------------------------------
    restore_dir = '%s/restore_dir' % (config['DATA_DIR'])
    if not os.path.exists(restore_dir):
        os.mkdir(restore_dir)

    os.popen('unzip %s -d %s' % (zip_zip, restore_dir))

    restore_dir = '%s' % (restore_dir)

    #--- Match slave id's and restore rts files ---------------------------
    copy_nodes = simplejson.loads( open('%s/nodes.json' % restore_dir).read() )

    def get_master_id(master_port):
        for node in copy_nodes.values():
            if int(node['port']) == int(master_port):
                return node
        return None

    #Create mappings
    master_mapping = {}
    for node in nodes():
        master_id = get_master_id(node['m_port'])['id']
        master_mapping[master_id] = node

    #Tranverse the restore_dir to change files
    for root, dirs, files in os.walk(restore_dir):
        for file in files:
            if not '.tch' in file:
                break

            id, ext, log_pos = file.split('.')
            id, log_pos = int(id), long(log_pos)

            local_node = master_mapping[id]
            mv_cmd = 'mv %s/%s %s/%s.tch' % (restore_dir, file, restore_dir, local_node['id'])
            os.popen(mv_cmd)
            os.popen('echo %s > %s/%s.rts' % (log_pos, restore_dir, local_node['id']))

        break

    print 'Restored hot copy of master in %s' % restore_dir
    os.popen('rm %s/%s' % (restore_dir, 'nodes.json'))


def delete_data():
    """Deletes all the data.
    """
    input = raw_input('Are you sure you want to delete all the data!?? [yes or no] ')
    if input != 'yes':
        print "Deletion canceled"
        sys.exit(0)

    path = config['DATA_DIR']

    try:
        paths = ['%s/data/' % path, '%s/logs/' % path]
        for p in paths:
            shutil.rmtree(p)
            os.mkdir(p)
    except:
        pass

    print 'Data is now deleted!'


def remove_logs():
    path = config['DATA_DIR']
    os.popen("rm -rf %s/logs" % path)
    os.popen("mkdir %s/logs" % path)
    for node in nodes():
        os.popen('rm %s/data/%s.rts' % (path, node['id']))
    print "Removed all logs"


def purge_logs():
    """Purges the logs, but leaves the 2 newest behind.
    """
    path = config['DATA_DIR']
    log_dir = '%s/logs' % path
    for root, dirs, files in os.walk(log_dir):
        if root != log_dir:
            files.sort()
            if len(files) > 4:
                delete_logs = files[:-4]
                for f in delete_logs:
                    print os.path.join(root, f)
                    os.remove(os.path.join(root, f))
            else:
                print "Only %s logs for %s" % (len(files), log_dir)


#--- Helpers ----------------------------------------------
def set_config(config_file):
    global config
    execfile(config_file, config)

try:
    set_config('config.py')
except Exception, e:
    print e

def ensure_dirs():
    data_dir = config['DATA_DIR']

    log_dir = os.path.join(data_dir, 'logs')
    data_dir = os.path.join(data_dir, 'data')

    if not os.path.exists(log_dir):
        os.mkdir(log_dir)

    if not os.path.exists(data_dir):
        os.mkdir(data_dir)


def main(argv):

    #--- Argument resolution ----------------------------------------------
    try:
        opts, args = getopt.getopt(argv, "hc:", ["help", 'config='])
    except getopt.GetoptError:
        help()

    #--- Parse options ----------------------------------------------
    for opt, arg in opts:
        if opt in ('-h', '--help'):
            help()
        elif opt in ('-c', '--config'):
            set_config(arg)

    if not config:
        print "Config file isn't set. Set it via python manager.py -c config.py"
        sys.exit(-1)

    if not config.has_key('NODES'):
        print "Config file is invalid, see a sample in config.sample.py."
        sys.exit(-1)

    ensure_dirs()


    #--- Commands ----------------------------------------------
    if len(args) < 1:
        help()

    if 'start' in args:
        start(args, opts)
    elif 'status' in args:
        status(args, opts)
    elif 'stop' in args:
        stop(args, opts)
    elif 'delete_data' in args:
        delete_data()
    elif 'purge_logs' in args:
        purge_logs()
    elif 'hot_copy' in args:
        hot_copy()
    elif 'hot_restore' in args:
        hot_restore(args)
    elif 'remove_logs' in args:
        remove_logs()

if __name__ == "__main__":
    main(sys.argv[1:])
