<em>this documentation reflects what can be found at <a href="http://opensource.plurk.com/LightCloud/Tyrant_manager/">http://opensource.plurk.com/LightCloud/Tyrant_manager/</a> it will be updated as Tyrant_manager gets ported to PHP</em>

## Overview

### Features

* Built on <a href="http://tokyocabinet.sourceforge.net/tyrantdoc/" target="_blank">Tokyo Tyrant</a>. One of the fastest key-value databases [<a href="http://tokyocabinet.sourceforge.net/benchmark.pdf" target="_blank">benchmark</a>]. Tokyo Tyrant has been in development for many years and is used in production by <a href="http://plurk.com" target="_blank">Plurk.com</a>, <a href="http://mixi.jp" target="_blank">mixi.jp</a>, <a href="http://scribd.com" target="_blank">scribd.com</a> and <a href="http://teamitup.com" target="_blank">teamitup.com</a> (to name a few)...
* Great performance (comparable to memcached!)
* Can store millions of keys on very few servers - tested in production
* Scale out by just adding nodes
* Nodes are replicated via master-master replication. Automatic failover and load balancing is supported from the start
* Ability to script and extend using <a href="http://lua.org" target="_blank">Lua</a>. Included extensions are incr and a fixed list
* Hot backups and restore: Take backups and restore servers without shutting them down
* Tyrant manager can control nodes, take backups and give you a status on how your nodes are doing
* Very small foot print (lightcloud client is around ~500 lines and manager about ~400)
* Python only, but Tyrant should be easy to port to other languages.
* <a href="http://github.com/mitchellh/lightcloud/tree/master" target="_blank">Ruby port under development</a>!

But that's not all, we also support <a href="http://code.google.com/p/redis/" target="_blank">Redis</a> (as an alternative to Tokyo Tyrant)!:

* Check benchmarks and more details about Redis in <a href="http://amix.dk/blog/viewEntry/19458" target="_blank">Tyrant adds support for Redis</a>.

### Stability

It's production ready and <a href="http://plurk.com" target="_blank">Plurk.com</a> is using it to store millions of keys on only two servers that run 3 lookup nodes and 6 storage nodes (these servers also run MySQL).

### How LightCloud differs from memcached and MySQL?

<a href="http://www.danga.com/memcached/" target="_blank">memcached</a> is used for caching, meaning that after some time items saved to memcached are deleted. Tyrant is persistent, meaning that once you save an item, it will be there forever (or until you delete/update it).

<a href="http://www.mysql.com/" target="_blank">MySQL</a> and other relational databases are not efficient for storing key-value pairs, a key-value database like Tyrant is.

The bottom line is that Tyrant is not a replacement for memcached or MySQL - it's a complement that can be used in situations where your data does not fit that well into the relational model.

### How LightCloud differs from redis and memcachedb?

Tyrant is a distributed and horizontal scaleable database. <a href="http://memcachedb.org/" target="_blank">memcachedb</a> or <a href="http://code.google.com/p/redis/" target="_blank">redis</a> aren't. This is pretty crucial to understand and we can read that many have not really understood this.

Basically, Tyrant could be built on top of memcachedb or redis - where the nodes would be memcachedb or redis instead of <a href="http://tokyocabinet.sourceforge.net/tyrantdoc/" target="_blank">Tokyo Tyrant</a>. The reason why Tokyo Tyrant was chosen is because it's the fastest key-value database around with the ability to do 1 million SETs and GETs under 1 second (see <a href="http://tokyocabinet.sourceforge.net/benchmark.pdf" target="_blank">benchmark</a>).

### Benchmark against memcached

Please do note that comparing to memcached is unfair as memcached is memory only - Tyrant has to hit the disk. That said, here is what it takes to do 10.000 gets and sets:

	Elapsed for 10000 gets: 1.74538516998 seconds [memcache]
	Elapsed for 10000 gets: 3.57339096069 seconds [lightcloud]

	Elapsed for 10000 sets: 1.88236999512 seconds [memcache]
	Elapsed for 10000 sets: 9.23674893379 seconds [lightcloud]

<a href="http://opensource.plurk.com/Tyrant/Benchmark_program/">Benchmark program</a>

If things were done in batches and time wasn't spent in Python and network layer, then Tokyo Tyrant would be able to perform much better. From the official Tokyo Cabinet <a href="http://tokyocabinet.sourceforge.net/benchmark.pdf" target="_blank">benchmark</a> you can see following stats:

* 1 million GETS in < 0.5 seconds
* 1 million SETS in < 0.5 seconds

These updates are not that realistic in practice.

### Useful links

Some useful links to Tyrant related sites:

* <a href="http://opensource.plurk.com/trac/">Plurk Open Source Trac</a>
* <a href="http://news.ycombinator.com/item?id=498581" target="_blank">Hacker news discussion</a>

Also do subscribe to Tyrant's mailing list:

<table style="border:1px solid #ccc; font-size:small; width: 500px;">  <tr>    <td rowspan="3">     <img src="http://groups.google.com/groups/img/groups_medium.gif" height="58" width="150" alt="Google Groups" />    </td>    <td colspan="2" align="center"><b>Subscribe to Tyrant Mailing list</b></td>  </tr>  <form action="http://groups.google.com/group/lightcloud/boxsubscribe" style="display: block !important">  <tr>    <td>Email: <input type="text" name="email" /></td>    <td>      <table style="padding:2px">      <tr>        <td>         <input type="submit" name="sub" value="Subscribe" />        </td>      </tr>      </table>    </td>  </tr>   </form>  <tr><td colspan="2" align="center">   <a href="http://groups.google.com/group/lightcloud">Browse Archives</a>  </td></tr></table>

### Lua extension

Like stated above you can script Tyrant nodes via Tokyo Tyrant's Lua extension support. This basically means that you can create your own extensions in a very easy manner (the speed is comparable to C).

Here is how you extend with a <span class="hl">incr</span> command:

<div class="highlight"><pre><span class="k">function</span> <span class="nf">incr</span><span class="p">(</span><span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span>
   <span class="n">value</span> <span class="o">=</span> <span class="nf">tonumber</span><span class="p">(</span><span class="n">value</span><span class="p">)</span>
   <span class="k">if</span> <span class="ow">not</span> <span class="n">value</span> <span class="k">then</span>
      <span class="k">return</span> <span class="kc">nil</span>
   <span class="k">end</span>
   <span class="kd">local</span> <span class="n">old</span> <span class="o">=</span> <span class="nf">tonumber</span><span class="p">(</span><span class="n">_get</span><span class="p">(</span><span class="n">key</span><span class="p">))</span>
   <span class="k">if</span> <span class="n">old</span> <span class="k">then</span>
      <span class="n">value</span> <span class="o">=</span> <span class="n">value</span> <span class="o">+</span> <span class="n">old</span>
   <span class="k">end</span>
   <span class="k">if</span> <span class="ow">not</span> <span class="n">_put</span><span class="p">(</span><span class="n">key</span><span class="p">,</span> <span class="n">value</span><span class="p">)</span> <span class="k">then</span>
      <span class="k">return</span> <span class="kc">nil</span>
   <span class="k">end</span>
   <span class="k">return</span> <span class="n">value</span>
<span class="k">end</span>
</pre></div>

And for something a bit more crazy:

* <a href="http://opensource.plurk.com/Tyrant/Inverted_index_by_the_Lua_extension_of_Tokyo_Tyrant/">Inverted index by the Lua extension of Tokyo Tyrant</a>

## Installation

In order to get Tyrant up and running you'll need to install the following components:

* <a href="http://1978th.net/tokyocabinet/">Tokyo Cabinet</a>
* <a href="http://1978th.net/tokyotyrant/">Tokyo Tyrant</a>

This should be supported on Windows, Linux and OS X. We'll only give a guide on how to install this on Linux (debian / ubuntu).

### Install Tokyo Cabinet

Download and extract: 

	$ sudo apt-get install wget
	$ sudo apt-get install zlib1g-dev libbz2-dev
	$ wget http://tokyocabinet.sourceforge.net/tokyocabinet-1.4.9.tar.gz
	$ tar -xvf tokyocabinet-1.4.9.tar.gz

Configure and install:

	$ ./configure
	$ make
	$ sudo make install

### Install Tokyo Tyrant

Download and extract:

	$ wget http://tokyocabinet.sourceforge.net/tyrantpkg/tokyotyrant-1.1.16.tar.gz
	$ tar -xvf tokyotyrant-1.1.16.tar.gz
	$ cd tokyotyrant-1.1.16

Configure and install:

	$ ./configure --with-lua --enable-lua
	$ make
	$ sudo make install

### Install Lua (optional)

This is only needed if you want to support scripting via Lua:

	$ sudo apt-get install libreadline5-dev
	$ wget http://www.lua.org/ftp/lua-5.1.4.tar.gz
	$ tar -xvf lua-5.1.4.tar.gz
	$ cd lua-5.1.4
	$ ./configure; make linux; sudo make install
	
### Install Redis (optional)
	
<a href="http://github.com/antirez/redis">Redis</a>, which is another key-value database, is fully supported by Tyrant and can be used as an replacement for Tokyo Tyrant.

Some unique features of Redis are:

* it's persistent (but one has to hold the dataset in the memory)
* it supports unique datatypes such as lists and sets
* it can do some very interesting stuff like union and intersection between sets
* it's very fast since everything is kept in memory

Benchmarks etc. can be read in Tyrant adds support for Redis.

To install Redis, simply do:

	$ wget http://redis.googlecode.com/files/redis-0.100.tar.gz
	$ tar -xvf redis-0.100.tar.gz
	$ cd redis-0.100
	$ make
	$ sudo ln -s /path/to/redis-0.100/redis-server /usr/bin/redis-server
	
## Getting the Tyrant Manager

Simply check out the Tyrant manager in a directory:

	$ git clone git@github.com:naterkane/tyrant_manager.git ~/tyrant_manager
	$ cd  ~/tyrant_manager

Create a config file
Create a config file <code>config.py</code>. A sample config file is included <code>~/tyrant_manager/config.sample.py</code>:

	DATA_DIR = '~/tyrant_manager/data'
	TOKYO_SERVER_PARMS = '#bnum=1000000#fpow=13#opts=ld'

	USE_MASTER = True

	NODES = {
	    #Lookup nodes
	    'lookup1_A': { 'id': 1, 'host': '127.0.0.1:41201', 'master': '127.0.0.1:51201' },
	    'lookup1_B': { 'id': 2, 'host': '127.0.0.1:51201', 'master': '127.0.0.1:41201' },

	    #Storage nodes
	    'storage1_A': { 'id': 5, 'host': '127.0.0.1:44201', 'master': '127.0.0.1:54201' },
	    'storage1_B': { 'id': 6, 'host': '127.0.0.1:54201', 'master': '127.0.0.1:44201' },
	}
	
The options of the manager

	$ python -m manager -c config.py
	Script that is used to handle Tokyo Tyrant nodes.

	Starting nodes:
	   python manager.py -c config.py all start
	   python manager.py -c config.py lookup1 start

	Stopping nodes:
	   python manager.py -c config.py all stop
	   python manager.py -c config.py lookup1 stop

	Status:
	   python manager.py -c config.py all status 
	   python manager.py -c config.py lookup1 status

	Misc:
	   python manager.py -c config.py purge_logs
	   python manager.py -c config.py delete_logs
	   python manager.py -c config.py delete_data

	   python manager.py -c config.py hot_copy
	   python manager.py -c config.py hot_restore hot_copy_23232.zip

	View a sample config file in config.sample.py.
	
Starting the nodes:

	$ python -m manager all start
	
Checking out status:

	$ python manager.py all status
	lookup1_A (127.0.0.1:41201):
	    node running - node items: 10306
	    master 127.0.0.1:51201 running - master items: 10306
	lookup1_B (127.0.0.1:51201):
	    node running - node items: 10306
	    master 127.0.0.1:41201 running - master items: 10306
	storage1_A (127.0.0.1:44201):
	    node running - node items: 10067
	    master 127.0.0.1:54201 running - master items: 10067
	storage1_B (127.0.0.1:54201):
	    node running - node items: 10067
	    master 127.0.0.1:44201 running - master items: 10067
	
### How to debug
	
If you run into problems, try to start a ttserver manually. python manager.py all start prints out the commands.

### How to take a hot backup and restore it
	
Tyrant Tyrant manager supports taking hot backups of your database, without shutting the database down. The interface is super simple as well.

To take a hot-copy, simply do following thing:

	$ python manager.py hot_copy
	...
	Created hot copy in ~/tyrant_manager/data/hot_copy_1245055938.zip
	
This creates a zip file of database files and their log positions.

To restore a hot copy simply do following:

	$ python manager.py hot_restore ~/tyrant_manager/data/hot_copy_1245055938.zip
	Restored hot copy of master in ~/tyrant_manager/data/restore_dir

You should inspect <code>~/tyrant_manager/data/restore_dir</code> and ensure that everything looks reasonable (i.e. you have all the database files [tch files] and their log positions [rts files]).

When you have ensured that everything looks reasonable, you can do following to swap the current data directory:

	$ python manager.py all stop
	$ mv ~/tyrant_manager/data/data ~/tyrant_manager/data/data_old
	$ mv ~/tyrant_manager/data/restore_dir ~/tyrant_manager/data/data
	$ python manager.py all start

You can then run status to check consistency:

	$ python manager.py all status
	lookup1_A (127.0.0.1:41201):
	    node running - node items: 10306
	    master 127.0.0.1:51201 running - master items: 10306
	lookup1_B (127.0.0.1:51201):
	    node running - node items: 10306
	    master 127.0.0.1:41201 running - master items: 10306
	storage1_A (127.0.0.1:44201):
	    node running - node items: 10067
	    master 127.0.0.1:54201 running - master items: 10067
	storage1_B (127.0.0.1:54201):
	    node running - node items: 10067
	    master 127.0.0.1:44201 running - master items: 10067
	
## License

LightCloud is copyrighted by Plurk Inc and is licensed under <a href="http://creativecommons.org/licenses/BSD/" target="_blank">the BSD license</a>.

LightCloud development is lead by <a href="http://amix.dk/" target="_blank">amix</a>.
