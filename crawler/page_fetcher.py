from bs4 import BeautifulSoup
from threading import Thread
import requests
from urllib.parse import urlparse,urljoin

class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        self.obj_scheduler = obj_scheduler

    def request_url(self, obj_url):
        """
            Faz a requisição e retorna o conteúdo em binário da URL passada como parametro

            obj_url: Instancia da classe ParseResult com a URL a ser requisitada.
        """
        url_resp = obj_url.geturl()
        headers = {'user-agent': self.obj_scheduler.str_usr_agent}
        request = requests.get(url_resp, headers = headers)
        content = request.headers['content-type']
        
        if "html" in content:
            response = request
            return response.content
        else:
            return None

        return response.content

    def discover_links(self, obj_url, int_depth, bin_str_content):
        """
        Retorna os links do conteúdo bin_str_content da página já requisitada obj_url
        """
        soup = BeautifulSoup(bin_str_content, features="lxml")
        for link in soup.select('a'):
            try:
                url = link["href"]
            except:
                url = ""

            if not "http" in url:
                url = obj_url.geturl() + "/" + url
            
            obj_new_url = urlparse(url)
            
            if not obj_url.netloc in url:
                int_depth = -1
            
            int_new_depth = int_depth + 1
            
            yield obj_new_url,int_new_depth

    def crawl_new_url(self):
        """
            Coleta uma nova URL, obtendo-a do escalonador
        """
        url = self.obj_scheduler.get_next_url()

        if url == None:
            return;

        html = self.request_url(url[0])
        urls = self.discover_links(url[0], url[1], html)
        
        print("Origin url:")
        print(url[0].netloc)
        print("Discovered urls:")
        for index, (url_link, depth) in enumerate(urls):
            if (url_link != None):
                print(url_link.netloc + ": " + str(depth))

    def run(self):
        """
            Executa coleta enquanto houver páginas a serem coletadas
        """
        [self.obj_scheduler.add_new_page(url) for url in self.obj_scheduler.arr_urls_seeds]

        while self.obj_scheduler.dic_url_per_domain:
            print("START NEW URL SEARCH")
            self.crawl_new_url()
        
