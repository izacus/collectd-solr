import collectd
import urllib2
import json
import itertools

SOLR_CORE_URL = "http://localhost:8080/solr/news"
SOLR_HANDLERS = {"query": "/select", "suggest": "/suggest", "simillar": "/mlt"}

def dispatch_value(value, value_name, value_type, type_instance=None):
    val = collectd.Values(plugin="solr_info")
    val.type = value_type

    if type_instance is not None:
       val.plugin_instance = value_name
       val.type_instance = type_instance
    else:
       val.type_instance = value_name
    val.values = [value]
    val.dispatch()

def fetch_data():
    global SOLR_CORE_URL, SOLR_HANDLERS
    stats_url = "%s/admin/mbeans?stats=true&wt=json" % (SOLR_CORE_URL, )
    stats = urllib2.urlopen(stats_url)
    solr_data = json.load(stats)

    # Searcher information
    solr_data = solr_data["solr-mbeans"]
    
    # Data is return in form of [ "TYPE", { DATA }, "TYPE", ... ] so pair them up
    solr_data_iter = iter(solr_data)
    solr_data = itertools.izip(solr_data_iter, solr_data_iter)
    
    data = { "cache": {}, "handler_stats": {}, "update_stats": {} }
    for module, module_data in solr_data:
        if module == "CORE":
            data["docs"] = module_data["searcher"]["stats"]["numDocs"]
        elif module == "CACHE":
            data["cache"]["size"] = module_data["fieldValueCache"]["stats"]["size"]
            data["cache"]["hitratio"] = module_data["fieldValueCache"]["stats"]["hitratio"]
            data["cache"]["evictions"] = module_data["fieldValueCache"]["stats"]["evictions"]
        elif module == "QUERYHANDLER":
            interesting_handlers = { endpoint: name for name, endpoint in SOLR_HANDLERS.iteritems() }
            for handler, handler_data in module_data.iteritems():
                if handler not in interesting_handlers:
                    continue
                
                handler_name = interesting_handlers[handler]
                data["handler_stats"][handler_name] = {}
                data["handler_stats"][handler_name]["requests"] = handler_data["stats"]["requests"]
                data["handler_stats"][handler_name]["errors"] = handler_data["stats"]["errors"] 
                data["handler_stats"][handler_name]["timeouts"] = handler_data["stats"]["timeouts"]
                data["handler_stats"][handler_name]["time_per_request"] = handler_data["stats"]["avgTimePerRequest"]                
                data["handler_stats"][handler_name]["requests_per_second"] = handler_data["stats"]["avgRequestsPerSecond"]
        elif module == "UPDATEHANDLER":
            data["update_stats"]["commits"] = module_data["updateHandler"]["stats"]["commits"]
            data["update_stats"]["autocommits"] = module_data["updateHandler"]["stats"]["autocommits"]
            data["update_stats"]["soft_autocommits"] = module_data["updateHandler"]["stats"]["soft autocommits"]
            data["update_stats"]["optimizes"] = module_data["updateHandler"]["stats"]["optimizes"]
            data["update_stats"]["rollbacks"] = module_data["updateHandler"]["stats"]["rollbacks"]
            data["update_stats"]["expunges"] = module_data["updateHandler"]["stats"]["expungeDeletes"]
            data["update_stats"]["pending_docs"] = module_data["updateHandler"]["stats"]["docsPending"]
            data["update_stats"]["adds"] = module_data["updateHandler"]["stats"]["adds"]
            data["update_stats"]["deletes_by_id"] = module_data["updateHandler"]["stats"]["deletesById"]
            data["update_stats"]["deletes_by_query"] = module_data["updateHandler"]["stats"]["deletesByQuery"]
            data["update_stats"]["errors"] = module_data["updateHandler"]["stats"]["errors"]
    return data

def read_callback():
    data = fetch_data()
    dispatch_value(data["docs"], "index", "gauge", "documents")
    dispatch_value(data["cache"]["size"], "cache", "gauge", "size")
    dispatch_value(data["cache"]["hitratio"], "cache_hitratio", "gauge", "hitratio")
    dispatch_value(data["cache"]["evictions"], "cache", "gauge", "evictions")

    for handler_name, handler_data in data["handler_stats"].iteritems():
        dispatch_value(handler_data["requests"], handler_name, "gauge", "requests")
        dispatch_value(handler_data["errors"], handler_name, "gauge", "errors")
        dispatch_value(handler_data["timeouts"], handler_name, "gauge", "timeouts")
        dispatch_value(handler_data["time_per_request"], "request_times", "gauge", handler_name)
        dispatch_value(handler_data["requests_per_second"], "requests_per_second", "gauge", handler_name)

    dispatch_value(data["update_stats"]["commits"], "update", "gauge", "commits")
    dispatch_value(data["update_stats"]["autocommits"], "update", "gauge", "autocommits")
    dispatch_value(data["update_stats"]["soft_autocommits"], "update", "gauge", "soft_autocommits")
    dispatch_value(data["update_stats"]["optimizes"], "update", "gauge", "optimizes")
    dispatch_value(data["update_stats"]["expunges"], "update", "gauge", "expunges")
    dispatch_value(data["update_stats"]["rollbacks"], "update", "gauge", "rollbacks")
    dispatch_value(data["update_stats"]["pending_docs"], "update", "gauge", "pending_docs")
    dispatch_value(data["update_stats"]["adds"], "update", "gauge", "adds")
    dispatch_value(data["update_stats"]["deletes_by_id"], "update", "gauge", "deletes_by_id")
    dispatch_value(data["update_stats"]["deletes_by_query"], "update", "gauge", "deletes_by_query")
    dispatch_value(data["update_stats"]["errors"], "update", "gauge", "errors")

collectd.register_read(read_callback)
