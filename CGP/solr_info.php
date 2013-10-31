<?php

/**
 * This is a plugin for Collect Graph Panel (http://pommi.nethuis.nl/category/cgp/) so the Solr graphs are rendered.
 * Copy to "plugins" folder of CGP distribution.
 */

require_once 'conf/common.inc.php';
require_once 'inc/collectd.inc.php';

switch (GET('pi')) {
	case "cache":		
		require_once 'type/GenericStacked.class.php';
		$obj = new Type_GenericStacked($CONFIG);
		$obj->ds_names = array('evictions' => 'Evictions', 'hitratio' => "Hit ratio", 'size' => 'Size');
		$obj->rrd_title = "Solr cache";
		$obj->rrd_format = "%5.0lf";
		break;
	case "cache_hitratio":		
		require_once 'type/GenericStacked.class.php';
		$obj = new Type_GenericStacked($CONFIG);
		$obj->ds_names = array('hitratio' => "Hit ratio");
		$obj->rrd_title = "Cache hitratio";
		$obj->rrd_format = "%1.2lf";
		break;
	case "request_times":	
		require_once 'type/Default.class.php';
		$obj = new Type_Default($CONFIG);
		$obj->rrd_title = "Average request times (ms)";
		$obj->rrd_vertical = "Avg. request time (ms)";
		$obj->rrd_format = "%5.2lf";
		break;
	case "update":
		require_once 'type/GenericStacked.class.php';
		$obj = new Type_GenericStacked($CONFIG);
		$obj->ds_names = array('commits' => 'Commits', 'autocommits' => 'Autocommits', 'soft_autocommits' => 'Soft autocommits',
								'optimizes' => 'Optimizes', 'expunges' => 'Expunges', 'rollbacks' => 'Rollbacks', 'pending_docs' => "Pending documents",
								'adds' => 'Adds', 'deletes_by_id' => 'Deletes by ID', 'deletes_by_query' => 'Deletes by query', 'errors' => 'Errors');
		$obj->rrd_title = "Update statistics";
		$obj->rrd_format = "%5.0lf";
		break;	
	case "requests_per_second":	
		require_once 'type/Default.class.php';
		$obj = new Type_Default($CONFIG);
		$obj->rrd_title = "Requests per second";
		$obj->rrd_vertical = "Avg. requests per second";
		$obj->rrd_format = "%3.4lf";
		break;
	case "index":
		require_once 'type/Default.class.php';
		$obj = new Type_Default($CONFIG);
		$obj->ds_names = array('documents' => 'Documents');
		$obj->rrd_title = "Documents in index";
		$obj->rrd_vertical = "Documents";
		$obj->rrd_format = "%5.0lf";
		break;
	default:
		require_once 'type/GenericStacked.class.php';
		$obj = new Type_GenericStacked($CONFIG);
		$obj->rrd_title = sprintf('%s handler', GET('pi'));
		$obj->ds_names = array('errors' => 'Errors', 'requests' => 'Requests', 'timeouts' => 'Timeouts');
		$obj->rrd_vertical = "Number";
		$obj->rrd_format = "%5.0lf";
		break;
}

collectd_flush($obj->identifiers);
$obj->rrd_graph();
