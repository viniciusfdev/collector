from bs4 import BeautifulSoup
from threading import Thread
import requests
from urllib.parse import urlparse,urljoin

class PageFetcher(Thread):
    def __init__(self, obj_scheduler, id):
        super(PageFetcher, self).__init__()
        self.id = id
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
            _int_depth = int_depth
            url = ""
            if link.get("href"):
                url = link["href"]
                
            if not "http" in url:
                url = obj_url.geturl() + "/" + url
            
            obj_new_url = urlparse(url)
            
            if not obj_url.netloc in url:
                _int_depth = int_depth + 1
            else:
                _int_depth = 0
            

            yield obj_new_url, _int_depth

    def crawl_new_url(self):
        """
            Coleta uma nova URL, obtendo-a do escalonador
        """
        url = self.obj_scheduler.get_next_url()
        
        if url == None:
            return

        html = self.request_url(url[0])
        urls = self.discover_links(url[0], url[1], html)
        
        links = []
        auxLinks = []
        for _url in urls:
            if not _url[0].netloc in auxLinks:
                auxLinks.append(_url[0].netloc)
                links.append(_url)
        
        print(str(self.id) + ": Origin url: " + url[0].netloc)
        print(str(self.id) + ": Discovered urls:")

        for index, (url_link, depth) in enumerate(links):
            if (url_link != None):
                print(str(self.id) + ": " + url_link.netloc + ": " + str(depth))
                self.obj_scheduler.add_new_page(url_link, depth)


    def run(self):
        """
            Executa coleta enquanto houver páginas a serem coletadas
        """
        [self.obj_scheduler.add_new_page(url) for url in self.obj_scheduler.arr_urls_seeds]

        while not self.obj_scheduler.has_finished_crawl():
            print("START NEW URL SEARCH " + str(self.id))
            self.crawl_new_url()
            self.obj_scheduler.count_fetched_page()
        
        
