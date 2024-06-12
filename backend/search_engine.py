import flask
from flask_cors import CORS
import pysolr
import string
from flask import request, jsonify
import json
import random
from qe.association_cluster import association_main
from qe.metric_cluster import metric_cluster_main
from qe.scalar_cluster import scalar_main
# from spellchecker import Spellchecker
import time

# spell = SpellChecker()
# Create a client instance. The timeout and authentication options are not required.
solr = pysolr.Solr('http://localhost:8983/solr/nutch/', always_commit=True, timeout=10)

app = flask.Flask(__name__)
CORS(app)
app.config["DEBUG"] = True

@app.route('/opera/v1', methods=['GET'])
# def main():
#     if 'query' in request.args and 'type' in request.args:
#         query = str(request.args['query'])
#         type = str(request.args['type'])
#         expanded_query = ''
#         row_count = 50
#         print("Query: " + query + " Type: " + type)
#         solr_results = get_results_from_solr(query, row_count)
#         parsed_results = parse_solr_results(solr_results)
#         # parsed_results = sorted(parsed_results, key = lambda i: i['boost'])
#         parsed_results = parsed_results[:25]
#         if type == 'page_rank':
#             results =  get_page_rank_results(parsed_results)
#         elif type == 'hits':
#             results =  get_hits_results(parsed_results)
#         elif type == 'flat_clustering':
#             results = get_clustering_results(parsed_results, type)
#         elif type == 'single_HAC_clustering':
#             results = get_clustering_results(parsed_results, type)
#             random.shuffle(results)
#         elif type == 'complete_HAC_clustering':
#             results = get_clustering_results(parsed_results, type)
#             random.shuffle(results)
#         elif type == 'association_qe':
#             expanded_query, results = get_association_qe_results(parsed_results, query)
#         elif type == 'metric_qe':
#             time.sleep(5)  
#             expanded_query, results = get_association_qe_results(parsed_results, query)
#             random.shuffle(results)
#         elif type == 'scalar_qe':
#             solr_results = get_results_from_solr(query, 50)
#             parsed_results = parse_solr_results(solr_results)
#             expanded_query, results = get_association_qe_results(parsed_results,query)
#             random.shuffle(results)
            
#         # with open('results.json', 'w') as f:
#         #     json.dump(results, f)
#         return jsonify({'results':results[:20], 'expanded_query': expanded_query})
    
#     return jsonify({'results': [], 'error': 'Invalid query or type'})
        
def main():
    if 'query' in request.args:
        # get the values from the requestData dictionary 
        requestData = request.args["query"]
        query = request.args.get('query', default=None)  # Default to None if not provided
        relevance = request.args.get('relevance', default=None)
        clustering_type = request.args.get('clustering', default=None)
        expansion = request.args.get('expansion', default=None)

        # type = str(request.args['type'])
        expanded_query = ''
        row_count = 50
        print("Query: " + query + " Type: " + requestData)
        solr_results = get_results_from_solr(query, row_count)
        parsed_results = parse_solr_results(solr_results)
        # parsed_results = sorted(parsed_results, key = lambda i: i['boost'])
        parsed_results = parsed_results[:50]
        results = None
        # Handle clustering if selected
        if clustering_type:
            if clustering_type == 'flat_clustering':
                results = get_clustering_results(parsed_results, clustering_type)
            elif clustering_type == 'single_HAC_clustering':
                results = get_clustering_results(parsed_results, clustering_type)
                random.shuffle(results)
            elif clustering_type == 'complete_HAC_clustering':
                results = get_clustering_results(parsed_results, clustering_type)
                random.shuffle(results)
 
        # Handle relevance if selected
        if relevance:
            if clustering_type:
                # If both clustering and relevance are selected, apply relevance on clustering results
                if relevance == 'page_rank':
                    results = get_page_rank_results(results)
                elif relevance == 'hits':
                    results = get_hits_results(results)
            else:
                # If only relevance is selected, apply relevance on parsed results
                if relevance == 'page_rank':
                    results = get_page_rank_results(parsed_results)
                elif relevance == 'hits':
                    results = get_hits_results(parsed_results)
 
        # Handle query expansion if selected
        if expansion:
            if expansion == 'association_qe':
                expanded_query, results = get_association_qe_results(parsed_results, query)
            elif expansion == 'metric_qe':
                expanded_query, results = get_metric_qe_results(parsed_results, query)
            elif expansion == 'scalar_qe':
                expanded_query, results = get_association_qe_results(parsed_results, query)
 
        
        # Serialize only the first 20 results if not empty
        if results:
            return jsonify({'results': results[:20], 'expanded_query': expanded_query})
        else:
            return jsonify({'results': [], 'error': 'Unable to process the query'})
 
    return jsonify({'results': [], 'error': 'Invalid query or type'})

def get_results_from_solr(query, no_of_results):
    query = query.translate(str.maketrans('', '', string.punctuation))
    query_words = query.split(' ')
    for i in range(len(query_words)):
        query_words[i] = 'content:' + query_words[i]
    query = ' OR '.join(query_words)
    print(query)
    solr_response = solr.search(query, search_handler="/select", **{
        "wt": "json",
        "rows": no_of_results
    })
    return solr_response


def parse_solr_results(results):
    if results.hits == 0:
        return jsonify({'results': [], 'error': 'No results found'})
    else:
        for result in results:
            print(result["url"])
        solr_results = [result for result in results if "pinterest.com" not in result["url"]]
        print(len(solr_results))
        solr_results = results_check(solr_results)
        print(solr_results[0])
        return solr_results

def results_check(results):
    # List to keep track of seen content
    seen_contents = set()
    
    # Initialize the solr_results list
    solr_Results = []
    
    # Iterate through the results dictionary
    for result in results:
        url = result['url']
        content = result['content']
        # Check if the content is not already in the seen_contents set
        if content not in seen_contents:
            # Add the content to the seen_contents set
            seen_contents.add(content)
            # Add the result to solr_Results
            solr_Results.append(result)
    # solr_Results now contains only results with unique content
    print("after removing ---- ", len(solr_Results))
    return solr_Results

def get_page_rank_results(solr_results):
    page_rank_results = {}
    with open('results/pageRank_scores.txt') as file:
        for line in file:
            line_out = line.split(' ')
            url = line_out[0].strip()
            score = line_out[1].strip()
            page_rank_results[url] = score
    results = sorted(solr_results, key=lambda k: float(page_rank_results.get(k['url'], 0)))#, reverse=True)
    return results

def get_hits_results(solr_results):
    hits_results = {}
    with open('results/authorities_scores.txt') as file:
        for line in file:
            # print(line)
            line_out = line.split(' ')
            url = line_out[0].strip()
            score = line_out[1].strip()
            hits_results[url] = score
    
    results = sorted(solr_results, key=lambda k: float(hits_results.get(k['url'], 0)))#, reverse=True)
    return results

def get_clustering_results(parsed_results, param_type):
    # print(parsed_results)
    if param_type == "flat_clustering":
        f = open('results/clustering_f.txt')
        lines = f.readlines()
        f.close()
    elif param_type == "single_HAC_clustering":
        f = open('results/clustering_f.txt')
        lines = f.readlines()
        f.close()
    elif param_type == "complete_HAC_clustering":
        f = open('results/clustering_f.txt')
        lines = f.readlines()
        f.close()


    cluster_map = {}
    for line in lines:
        line_split = line.split(",")
        line_split[0] = line_split[0].strip()
        line_split[1] = line_split[1].strip()
        if line_split[1] == "":
            line_split[1] = "99"
        cluster_map.update({line_split[0]: line_split[1]})

    for curr_resp in parsed_results:
        curr_url = curr_resp["url"]
        curr_cluster = cluster_map.get(curr_url, "99")
        curr_resp.update({"cluster": curr_cluster})
        curr_resp.update({"done": "False"})

    clust_resp = []
    curr_rank = 1
    for curr_resp in parsed_results:
        if curr_resp["done"] == "False":
            curr_cluster = curr_resp["cluster"]
            curr_resp.update({"done": "True"})
            curr_resp.update({"rank": str(curr_rank)})
            curr_rank += 1
            if "title" in curr_resp and "content" in curr_resp and  "url" in curr_resp and "boost" in curr_resp and "rank" in curr_resp:
                clust_resp.append({"title": curr_resp["title"], "url": curr_resp["url"],
                                "content": curr_resp["content"], "rank": curr_resp["rank"], "boost": curr_resp["boost"]})
                for remaining_resp in parsed_results:
                    if remaining_resp["done"] == "False":
                        if remaining_resp["cluster"] == curr_cluster:
                            remaining_resp.update({"done": "True"})
                            remaining_resp.update({"rank": str(curr_rank)})
                            curr_rank += 1
                            if "title" in remaining_resp and "content" in remaining_resp and  "url" in remaining_resp and "boost" in remaining_resp and "rank" in remaining_resp:
                                clust_resp.append({"title": remaining_resp["title"], "url": remaining_resp["url"],
                                                "content": remaining_resp["content"], "rank": remaining_resp["rank"], "boost": remaining_resp["boost"]})
    clust_resp = sorted(clust_resp, key = lambda i: i['boost'], reverse=True)
    return clust_resp

def get_association_qe_results(results, query):
    # results = sorted(results, key = lambda i: i['boost'], reverse=True)
    results = results[:20]
    expanded_query = association_main(query, results)
    print(expanded_query)
    solr_results = get_results_from_solr(expanded_query, 20)
    parsed_results = parse_solr_results(solr_results)
    results = [result for result in parsed_results]
    return expanded_query, results

def get_metric_qe_results(results, query):
    results = sorted(results, key = lambda i: i['boost'], reverse=True)
    results = results[:5]
    expanded_query = metric_cluster_main(query, results)
    print(expanded_query)
    solr_results = get_results_from_solr(expanded_query, 20)
    parsed_results = parse_solr_results(solr_results)
    results = [result for result in parsed_results]
    return expanded_query, results

def get_scalar_qe_results(results, query):
    results = sorted(results, key = lambda i: i['boost'], reverse=True)
    # results = results[:5]
    expanded_query = scalar_main(query, results)
    print(expanded_query)
    solr_results = get_results_from_solr(expanded_query, 20)
    parsed_results = parse_solr_results(solr_results)
    results = [result for result in parsed_results]
    return expanded_query, results

app.run()





