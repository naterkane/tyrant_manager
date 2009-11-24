<html>
<head>
<title>Tyrant Manager</title>
<style>
pre {
     	background: rgb(245, 245, 245);
        padding: 1em;
}
</style>
</head>
<body>
<h1>Tyrant Manager</h1>
<h3>configuration</h3>
<pre>
<?php
$configfilename = "python/config.py";
$confighandle = fopen($configfilename, "r");
$configcontent = fread($confighandle, filesize($configfilename));
fclose($confighandle);
print $configcontent; ?>
</pre>
<hr/>
<h3>status</h3>
<form method="post" action="<?php echo $_PHP['self'] ?>"><input type="hidden" name="start" value="true"/><button>start
server(s)</button></form>
<form method="post" action="<?php echo $_PHP['self'] ?>"><input type="hidden" name="stop" value="true"/><button>stop
server(s)</button></form>
<?php
if (!empty($_POST['start'])) {
        ?><pre><?php
        passthru('cd python; python manager.py -c config.py all start');//,$result);
        //echo $result;
        ?></pre><?php
}
if (!empty($_POST['stop'])) {
        ?><pre><?php
        passthru('cd python; python manager.py -c config.py all stop');
        ?></pre><?php
}
?>
<pre>
<?php system('cd python; python manager.py -c config.py all status'); ?>
</pre>
<hr/>
<h3>logs</h3>
<?php
$logpath = explode("'",$configcontent);
$logpath = $logpath[1];
$configcontent = explode("\n",$configcontent);
$logs = array();
foreach ($configcontent as $line){
	if (substr(trim($line),0,1) == "#"){
		continue;
	}
	if (stristr($line,"'id': ")){
		$line = explode("'id':",$line);
		$line = explode(",",trim($line[1]));
		$line = $line[0];
		array_push($logs, substr($line,0,1));
	}
}

//var_dump($configcontent);
//var_dump($logs);
foreach ($logs as $log){
	?><h4>Server <?php echo $log ?> at <code><?php echo $logpath . "/logs/".$log ?></code></h4>
	<pre>
	<?php system('ls -all '. $logpath . '/logs/'. $log); ?>
	</pre><?php
}
?>
<hr/>
<h3 id="backup">backup</h3>
<form action="<?php echo $_PHP['self'] ?>#backup" method="post"><input type="hidden" name="backup" value="true"/><button>backup
the data,
son.</button></form>
<?php
if ($_POST['backup'] == true) {
	?><pre><?php
	    //passthru("cd python; python; import simplejson, config; print simplejson.dumps(config['NODES'])",$nodes);
	    //var_dump($nodes);
	
        system('cd python; python manager.py backup hot_copy;');
        //echo "ok... I backed it up, son.<br/>";
	?>ok... I backed it up, son.</pre><?php
}
?>
<h4 id="currentbackups">current backups</h4>
<?php 
$backupdir = $logpath . "/backup/";
//$backupdir = opendir($logpath . '/backup'); 
if (is_dir($backupdir)) {
   // echo "it's a directory!";
    if ($dh = opendir($backupdir)) {
        ?>
        <table>
            <thead>
                <tr>
                    <th>Date</th>
                    <th>Backup File</th>
                    <th>Actions</th>
                </tr>
            </thead>
            <tbody>
        <?php
        while (($file = readdir($dh)) !== false) {
            if (!empty($_POST['restore']) && $_POST['restore'] == $file):
                // add call to restore method here
            endif; 
            if ($file != "." && $file != ".."):
                $stat = stat($backupdir . $file);
                ?>
                <tr>
                    <td></td>
                    <td><code><?php echo $file ?></code></td>
                    <td>
                        <form method="post" action="<?php echo $_PHP['self'] ?>#currentbackups">
                            <input type="hidden" name="restore" value="<?php echo $file ?>"/>
                            <button>restore from this backup</button>
                        </form>
                    </td>
                <?php
            endif;
        }
        ?></tbody></table><?php
        closedir($dh);
    }
}
?>


<!--<a href="?viewlogs=true">show me the logs, son.</a>-->
<hr/>
<h3>Help</h3>
<pre><?php
system('cd python; python manager.py -c config.py ');
?></pre>
</body>
</html>
