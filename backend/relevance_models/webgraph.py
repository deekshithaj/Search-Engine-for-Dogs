# Python script to extract the inlinks and outlinks from the dump file and compute the hub, authority and pageRank scores
import networkx as nx
import json
import os

import chardet
 
def detect_encoding(file_path):
    with open(file_path, 'rb') as file:  # Open the file in binary mode
        raw_data = file.read(10000)  # Read the first 10,000 bytes
        result = chardet.detect(raw_data)
        return result['encoding']
 
# Example usage
file_path = 'part-r-00000/data.txt'
encoding = detect_encoding(file_path)
print("Detected encoding:", encoding)

# read inlinks
max_inlinks = -1
dir_path = "part-r-00000"
# /Users/deekshithajuvvadi/Desktop/IR/apache-nutch-1.19/runtime/local/crawl/linkdb/current
# read inlinks
max_inlinks = -1
with open("/Users/deekshithajuvvadi/Desktop/IR/apache-nutch-1.19/runtime/local/dump/part-r-00000", encoding = 'utf8') as f:
    inlinks = {}
    for line in f:
        line = line.strip()
        if line:
            if "Inlinks" in line:
                key = line.split("\t")[0]
                values = []
            elif "fromUrl" in line:
                values.append(line.split()[1])
        else:
            if values:  # checks if d_value is not empty before adding to dictionary
                inlinks[key] = values
                if len(values) > max_inlinks:
                    max_inlinks =  len(values)
print(max_inlinks)
# create outlinks
outlinks = {}
for key, urls in inlinks.items():
    for url in urls:
        outlinks.setdefault(url, []).append(key)

max_outlinks = -1
for i in outlinks:
    if len(outlinks[i]) > max_outlinks:
        max_outlinks = len(outlinks[i])

print(max_outlinks)


# HITS Algorithm
G = nx.Graph(outlinks)
print(G.number_of_edges())
print(G.number_of_nodes())

hubs, authorities = nx.hits(G, max_iter=10000, normalized=True)

# This code sorts the hubs and authorities dictionaries in descending order by their values.
hubs_sorted = dict(sorted(hubs.items(), key=lambda x:x[1], reverse=True))
authorities_sorted = dict(sorted(authorities.items(), key=lambda x:x[1], reverse=True))

# this code computes the hub and authority scores for each node in the graph and writes it into the json files
with open('results/hub_scores.txt', 'w') as convert_file:
    for i, (key, value) in enumerate(hubs_sorted.items()):
        if i == len(hubs_sorted) - 1: # if it's the last item
            convert_file.write(str(key) + ' ' + str(value)) # remove the newline
        else:
            convert_file.write(str(key) + ' ' + str(value) + '\n')

with open('results/authorities_scores.txt', 'w') as convert_file:
    for i, (key, value) in enumerate(authorities_sorted.items()):
        if i == len(hubs_sorted) - 1: # if it's the last item
            convert_file.write(str(key) + ' ' + str(value)) # remove the newline
        else:
            convert_file.write(str(key) + ' ' + str(value) + '\n')

print('Files have been pushed to results folder.')

# PageRank Algorithm
pageRank = nx.pagerank(G, alpha=0.85)

pageRank_sorted = dict(sorted(pageRank.items(), key=lambda x:x[1], reverse=True))
# This code is used to generate the page rank scores of the crawled pages. It is used to generate the page rank scores of the crawled pages. The page rank scores of the crawled pages are saved in a file named pageRank_scores.txt.
with open('results/pageRank_scores.txt', 'w') as convert_file:
    for i, (key, value) in enumerate(pageRank_sorted.items()):
        if i == len(hubs_sorted) - 1: # if it's the last item
            convert_file.write(str(key) + ' ' + str(value)) # remove the newline
        else:
            convert_file.write(str(key) + ' ' + str(value) + '\n')
