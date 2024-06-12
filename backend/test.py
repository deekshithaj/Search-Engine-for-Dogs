from search_engine import get_results_from_solr, parse_solr_results

q = get_results_from_solr('opera concert', 10)
ans = parse_solr_results(q)
print(ans)