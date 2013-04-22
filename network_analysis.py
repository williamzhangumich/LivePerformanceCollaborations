import networkx as nx
import pandas as pd
from community import community

def get_communities():
    
    print "Get communities\nReading gml....."
    g = nx.read_gml('artist_collaboration_with_attr.gml')
    
    print 'Partitioning'
    partition = community.best_partition(g)
    
    print 'Generating frame'
    data_for_frame = []
    for node_idx, group in partition.iteritems():
        node = g.node[node_idx]
        data_for_frame.append({'id':node_idx, 'name':node['label'],
                               'community':group,
                               'num_years_active': node['num_years_active'],
                               'listeners':node['listeners'],
                               'playcount':node['playcount']})
    
    frame_community = pd.DataFrame(data_for_frame)
    frame_community = frame_community[['id','name','community','num_years_active', 'listeners', 'playcount']]
    frame_community = frame_community.sort_index(by=('community','id'))
    
    #print 'write csv'
    #frame_community.to_csv('artist_collaboration_communities.csv')
    return frame_community

def generate_text_graph():
    print "Get communities\nReading gml....."
    g = nx.read_gml('artist_collaboration_with_attr.gml')
    
    print "read complete"
    for a,b in g.edges():
        weight = g.edge[a][b]['weight']
        with open('flat_graph.txt','a') as h:
            h.write("%d %d %f\n"%(a,b,weight))

def generate_all_centrality():
    print "Get communities\nReading gml....."
    g = nx.read_gml('artist_collaboration_with_attr.gml')
    print "read complete"
    
    betweeness = nx.betweenness_centrality(g, weight='weight')
    print 'between'
    closeness = nx.closeness_centrality(g,distance=True)
    print 'close'
    degree = nx.degree_centrality(g)
    print 'degree'
    pagerank = nx.pagerank(g, weight='weight')
    print 'pagerank'
    
    print 'getting dataframe'
    data_for_frame = []
    for n in g.nodes():
        b,c,d,p = betweeness[n], closeness[n], degree[n], pagerank[n]
        node = g.node[n]
    
        data_for_frame.append({'id':n, 'name':node['label'],
                               'betweeness':b,
                               'closeness':c,
                               'degree':d,
                               'pagerank':p,
                               'num_years_active': node['num_years_active'],
                               'listeners':node['listeners'],
                               'playcount':node['playcount']})    
    frame_community = pd.DataFrame(data_for_frame)
    
    print 'write csv'
    frame_community.to_csv('artist_collaboration_centralities.csv')
    #import ipdb;ipdb.set_trace()

def get_other_stats():
    print "Get communities\nReading gml....."
    g = nx.read_gml('artist_collaboration_with_attr.gml')
    print "read complete"
    
    """
    # avg shortest path analysis    
    sp_length = nx.average_shortest_path_length(g,weight='weight')
    print 'average shortest path length (weighted): ', sp_length
    sp_length = nx.average_shortest_path_length(g)
    print 'average shortest path length: ', sp_length
    """
    
    clustering_coefs = nx.clustering(g, weight='weight')
    frame = pd.DataFrame(clustering_coefs,index=['clustering_coef'])
    frame.T.to_csv('clustering_coefficients.csv')
    
    import ipdb; ipdb.set_trace()
    return
    
    """
    ## Assortativeness analysis
    # Set pagerank attribute
    for (a, b) in g.edges():
        g.edge[a][b]['weight_int'] = int(g.edge[a][b]['weight']*100)
    print "weighted degree assortativeness: ", nx.degree_assortativity_coefficient(g, weight = 'weight_int')
    
    print 'setting pageranek'
    pagerank = nx.pagerank(g, weight='weight')
    print 'setting between'
    betweeness = nx.betweenness_centrality(g, weight='weight')
    print 'setting close'
    closeness = nx.closeness_centrality(g,distance=True)
    print 'settingdegree'
    degree = nx.degree_centrality(g)
    
    for n in g.nodes():
        node = g.node[n]
        node['pagerank'] = int(pagerank[n]*10000)
        node['betweeness'] = int(betweeness[n]*10000)
        node['closeness'] = int(closeness[n]*100)
        node['degree'] = int(degree[n]*10000)
    
    print "Getting assorativeness"
    r_pagerank = nx.numeric_assortativity_coefficient(g, attribute='pagerank')
    r_betweeness = nx.numeric_assortativity_coefficient(g, attribute='betweeness')
    r_closeness = nx.numeric_assortativity_coefficient(g, attribute='closeness')
    r_degree = nx.numeric_assortativity_coefficient(g, attribute='degree')
    
    print "pagerank\tbetweenness\tcloseness\tdegree"
    print "%f\t%f\t%f\t%f"%(r_pagerank, r_betweeness, r_closeness, r_degree)
    """
    #clustering coefficient
    #average shortest path    
    # assortativeness

def add_community():
    h = open('artist_collaboration_communities.txt','r')
    h.readline()
    comm_dict = {}
    for line in h:
        id, com = line.split('\t')[0], line.split('\t')[3]
        comm_dict[int(id)] = com
    
    
    print "Get communities\nReading gml....."
    g = nx.read_gml('artist_collaboration_with_attr.gml')
    print "read complete"
    
    for n in g.nodes():
        g.node[n]['community'] = comm_dict[n]
        
    nx.write_gml(g, 'artist_collaboration_community.gml')
    return g
#frame_community = get_communities()
#generate_text_graph()
#generate_all_centrality()
#get_other_stats()
add_community()

