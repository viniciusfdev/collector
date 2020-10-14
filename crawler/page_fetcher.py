from urllib.parse import urlparse,urljoin
from .scheduler import Scheduler
from bs4 import BeautifulSoup
from threading import Thread
import requests
import time

class PageFetcher(Thread):
    def __init__(self, obj_scheduler):
        super(PageFetcher, self).__init__()
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
        # se o conteudo do html é nulo entao é retornado
        # um conjunto vazio de urls descobertas
        if (bin_str_content == None):
            return []

        soup = BeautifulSoup(bin_str_content.decode('utf-8', 'ignore'), features="lxml")
        for link in soup.select('a'):
            _int_depth = int_depth
            url = ""
            if link.get("href"):
                url = link["href"]
                
            if not "http" in url:
                url = obj_url.geturl() + "/" + url
            
            obj_new_url = urlparse(url)
            
            # urls relativas
            if not obj_url.netloc in url:
                _int_depth = 0
            else:
                _int_depth = int_depth + 1
            

            yield obj_new_url, _int_depth

    def crawl_new_url(self):
        """
            Coleta uma nova URL, obtendo-a do escalonador
        """
        url = self.obj_scheduler.get_next_url()

        if url == None:
            # o page fetcher agora aguarda um tempo antes de permitir
            # uma nova chamada, o tempo aguardado convenientemente é o
            # mesmo tempo de limitação entre requisições do escalonador

            time.sleep(Scheduler.TIME_LIMIT_BETWEEN_REQUESTS)
            return 

        html = self.request_url(url[0])
        urls = self.discover_links(url[0], url[1], html)
        
        links = []
        auxLinks = []
        for _url in urls:
            if not _url[0].netloc in auxLinks:
                auxLinks.append(_url[0].netloc)
                links.append(_url)
        
        for index, (url_link, depth) in enumerate(links):
            if (url_link != None):
                # print discovery urls
                # print(": " + url_link.netloc + ": " + str(depth))
                self.obj_scheduler.add_new_page(url_link, depth)
        
        return True


    def run(self):
        """
            Executa coleta enquanto houver páginas a serem coletadas
        """
        [self.obj_scheduler.add_new_page(url) for url in self.obj_scheduler.arr_urls_seeds]

        while not self.obj_scheduler.has_finished_crawl():
            self.crawl_new_url()
            self.obj_scheduler.count_fetched_page()
        
        
