import sqlite3 as lite
import networkx as nx
from collections import defaultdict
from itertools import combinations
from matplotlib import pyplot as plt
import unicodedata
import simplejson as json
from datetime import *
import re
from community import community

# An important arbitrary constant is the upper bound of participation artist
# We certainly don't want to add connection for every artist participating in SXSW
# If a show has number of participating artist below this threshold
# we treat them as a collaboration connection (at least they should have talked with each other)
# Also helps scaling down our data.....
MAX_ARTIST = 10

# The minimum strength of connection to be added as edge
STRENGTH_THRESHOLD = 1

def create_artist_network(start_year, end_year, lastfm, wiki, write=False):
    
    valid_artists = set(lastfm.keys())&set(wiki.keys())
    
    con = lite.connect("lastfmDB.db")
    cur = con.cursor()
    
    # SQL to get event-artist connections of events that have at least 2 participating artists
    sql_all_connection = """
        select * from EVENT_ARTIST where event_id in
        (select event_id from EVENT_ARTIST  group by event_id having count(*) between ? and ? order by count(*))
     """
     
    #sql_numbers = """
    #    select event_id, count(*)  from EVENT_ARTIST  group by event_id having count(*)>1 order by count(*) DESC
    #"""
    #cur.execute(sql_numbers)
    
    print "Running sql"
    event_artists = defaultdict(list)
    # First, get a datastructure like {event: [person1, person2, ...], ...}
    for event, artist in cur.execute(sql_all_connection, (2, MAX_ARTIST)):
        event_artists[event].append(artist)
        
    print "Generating connection pairs"
    artist_connections = {}
    for event, artists in event_artists.iteritems():
        
        # Find out whether the event date
        cur.execute("""
            select strftime('%Y', start_date) as year 
            from EVENTS where id=?
            """, (event,))
        year = int(cur.fetchone()[0])
        
        # If date within our date range
        if year in range(start_year, end_year+1):
            # Get all combination of artists participating in the event
            pairs = combinations(artists, 2)
            for pair in pairs:
                # For each pair, update(init) their weight, i.e, strength of connection
                # Make sure pairs are unique (eliminate the reversed order pairs)
                if pair[0] > pair[1]:
                    sorted_pair = (pair[1], pair[0])
                else:
                    sorted_pair = (pair[0], pair[1])
                # Note the strength of connection is normalized by the total num of artists
                # Which means the connection is strongest (1) when only the 2 artists are present 
                artist_connections[sorted_pair] = artist_connections.get(sorted_pair, 0) + 2.0/len(artists)
    
    # Most collaborated artist pairs??
    print "Top 10 collaborations:", sorted(artist_connections.items(), key = lambda x:x[1], reverse = True)[:10]
    
    # Generating the graph
    G = nx.Graph()
    
    for (a, b), strength in artist_connections.iteritems():
        a = unicodedata.normalize('NFKD', a).encode('ASCII', 'ignore')
        b = unicodedata.normalize('NFKD', b).encode('ASCII', 'ignore')
        if a in valid_artists and b in valid_artists:
            # Filter by strength
            if strength> STRENGTH_THRESHOLD:
                G.add_edge(a, b, weight = 1/strength)
    
    G = nx.connected_component_subgraphs(G)[0]   
    
    print "###################"
    print "Nodes:", len(G.nodes())
    print "Edges:", len(G.edges())
    
    if write:
        print "#############\nWriting gml file"
        nx.write_gml(G, 'artist_collaboration_new.gml')
        
    return G
    #nx.draw(G)
    #plt.draw()
    #import ipdb; ipdb.set_trace()

def add_attributes(lastfm, wiki):
    g = nx.read_gml('artist_collaboration_new.gml')
    print "read gml, start to add attributes"
    for n in g.nodes():
        node = g.node[n]
        artist = node['label']
        #print artist
        
        try:
            years_active = wiki[artist]['Years active']
            
            years = re.findall(r'.*(\d\d\d\d).*', years_active)
            start = min(years)
            if years_active.find('present'):
                end = datetime.now().year 
            else:
                end = max(years)
            #years_active = wiki[artist]['Years active'].encode('UTF-8').replace('\xe2\x80\x93',',').replace('-',',') 
            #start, end = years_active.split(',')[0], years_active.split(',')[-1]
            #start = start.strip('s').strip(' ')
            #end = end.strip(' ')
            #if end == 'present':
            #    end = datetime.now().year 
            num_years_active = int(end) - int(start)
        except:
            num_years_active = 0
        
        try:
            state, country = wiki[artist]['Born'].split(',')[-2:] 
            state = unicodedata.normalize('NFKD', state).encode('ASCII', 'ignore').strip(' ')
            country = unicodedata.normalize('NFKD', country).encode('ASCII', 'ignore').strip(' ')
        except:
            state, country = "",""
        try:
            listeners = int(lastfm[artist]['artist']['stats']['listeners']  )
            playcount = int(lastfm[artist]['artist']['stats']['playcount']  )
        except:
            listeners, playcount = 0, 0
        node['num_years_active'] = num_years_active
        #node['state'] = state
        #node['country'] = country
        node['listeners'] = listeners
        node['playcount'] = playcount
        
    nx.write_gml(g, 'artist_collaboration_with_attr.gml')
    print 'complete'
    

def main():
    
    lastfm = {}
    wiki = {}
    
    with open('artists_json_lastfm.txt','rb') as h:
        for line in h:
            try:
                artist, json_str = line.strip().split('\t')
                lastfm[artist] = json.loads(json_str)
            except:
                print line
    print "Got lastfm info"
          
    with open('artists_json_wiki.txt','rb') as h:
        for line in h:
            artist, json_str = line.strip().split('\t')
            wiki[artist] = json.loads(json_str)
    print "got wiki info"
            
    
    g = create_artist_network(2000, 2013, lastfm, wiki, write=True)
    
    add_attributes(lastfm, wiki)
    
    """
    for i in g.nodes():
        print i
        with open("artists.txt", 'a') as h:
            h.write(g.node[i]['label']+'\n')
            """
    #import ipdb; ipdb.set_trace()

if __name__ == "__main__":
    main()