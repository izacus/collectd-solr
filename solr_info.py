import collectd
import urllib2
import json
import itertools

SOLR_CORE_URL = "http://localhost:8983/solr/news"
SOLR_HANDLERS = {"query": "/select", "suggest": "/suggest", "simillar": "/mlt"}

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

# Used only for testing, remove when done!
if __name__ == "__main__":
   data = fetch_data() 
   print data
