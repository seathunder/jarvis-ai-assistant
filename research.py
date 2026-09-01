import requests
from bs4 import BeautifulSoup
import re
import json
import networkx as nx
from config import logger

def search_duckduckgo_lite(query, max_results=5):
    """
    Performs live search on DuckDuckGo Lite without external API keys.
    Returns a list of dicts with title, url, snippet.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36"
    }
    url = "https://lite.duckduckgo.com/lite/"
    data = {"q": query}
    
    results = []
    try:
        response = requests.post(url, data=data, headers=headers, timeout=10)
        if response.status_code == 200:
            soup = BeautifulSoup(response.text, 'html.parser')
            rows = soup.find_all('tr')
            
            curr_title = None
            curr_url = None
            
            for row in rows:
                link = row.find('a', class_='result-link')
                if link:
                    curr_title = link.get_text(strip=True)
                    curr_url = link['href']
                
                snippet_td = row.find('td', class_='result-snippet')
                if snippet_td and curr_title and curr_url:
                    snippet = snippet_td.get_text(strip=True)
                    results.append({
                        "title": curr_title,
                        "url": curr_url,
                        "snippet": snippet
                    })
                    curr_title, curr_url = None, None
                    if len(results) >= max_results:
                        break
    except Exception as e:
        logger.error(f"Error during DuckDuckGo search: {e}")
        
    return results

def scrape_webpage_text(url, max_chars=3000):
    """
    Scrapes main text content from a web page.
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
    }
    try:
        resp = requests.get(url, headers=headers, timeout=8)
        if resp.status_code == 200:
            soup = BeautifulSoup(resp.text, 'html.parser')
            # Remove scripts and styles
            for script in soup(["script", "style", "nav", "footer", "header"]):
                script.extract()
            text = soup.get_text(separator=' ', strip=True)
            # Clean up whitespace
            cleaned_text = re.sub(r'\s+', ' ', text)
            return cleaned_text[:max_chars]
    except Exception as e:
        logger.error(f"Failed to scrape {url}: {e}")
    return ""

class LocalGraphRAG:
    """
    Constructs a lightweight GraphRAG structure from scraped web text.
    Extracts entities & constructs relationship graph for complete model context.
    """
    def __init__(self):
        self.graph = nx.DiGraph()

    def build_graph_from_sources(self, query, search_results):
        self.graph.clear()
        self.graph.add_node("QUERY", type="root", text=query)
        
        for idx, item in enumerate(search_results):
            source_id = f"SOURCE_{idx+1}"
            self.graph.add_node(source_id, type="source", title=item["title"], url=item["url"])
            self.graph.add_edge("QUERY", source_id, relation="SEARCH_RESULT")
            
            # Scrape deep content
            page_text = scrape_webpage_text(item["url"])
            if page_text:
                content_id = f"CONTENT_{idx+1}"
                self.graph.add_node(content_id, type="content", text=page_text)
                self.graph.add_edge(source_id, content_id, relation="HAS_CONTENT")
                
                # Simple Entity extraction (capitalized words / key terms)
                entities = set(re.findall(r'\b[A-Z][a-zA-Z0-9_-]{2,}\b', page_text))
                for ent in list(entities)[:10]:
                    if ent not in self.graph:
                        self.graph.add_node(ent, type="entity")
                    self.graph.add_edge(content_id, ent, relation="MENTIONS")

    def format_full_context(self):
        """
        Formats the full graph & contents into structured JSON/Markdown payload for the LLM.
        """
        sources_data = []
        for node, data in self.graph.nodes(data=True):
            if data.get("type") == "source":
                # Find associated content
                content = ""
                for neighbor in self.graph.neighbors(node):
                    if self.graph.nodes[neighbor].get("type") == "content":
                        content = self.graph.nodes[neighbor].get("text", "")
                sources_data.append({
                    "title": data.get("title"),
                    "url": data.get("url"),
                    "content": content
                })
                
        context_payload = {
            "query": self.graph.nodes["QUERY"]["text"] if "QUERY" in self.graph else "",
            "graph_summary": {
                "total_nodes": self.graph.number_of_nodes(),
                "total_edges": self.graph.number_of_edges()
            },
            "sources": sources_data
        }
        return json.dumps(context_payload, indent=2)

def perform_local_research(query):
    """
    High-level handler: Searches locally, builds GraphRAG context, and returns full context.
    """
    logger.info(f"Initiating local research for: {query}")
    results = search_duckduckgo_lite(query, max_results=3)
    
    if not results:
        return json.dumps({"error": "No search results found.", "query": query})
        
    rag = LocalGraphRAG()
    rag.build_graph_from_sources(query, results)
    return rag.format_full_context()
