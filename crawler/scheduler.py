from urllib import robotparser
from urllib.parse import urlparse
from util.threads import synchronized
from collections import OrderedDict
from .domain import Domain
import time

class Scheduler():
    #tempo (em segundos) entre as requisições
    # tempo 20 ou 10
    TIME_LIMIT_BETWEEN_REQUESTS = 10

    def __init__(self,str_usr_agent,int_page_limit,int_depth_limit,arr_urls_seeds):
        """
            Inicializa o escalonador. Atributos:
                - `str_usr_agent`: Nome do `User agent`. Usualmente, é o nome do navegador, em nosso caso,  será o nome do coletor (usualmente, terminado em `bot`)
                - `int_page_limit`: Número de páginas a serem coletadas
                - `int_depth_limit`: Profundidade máxima a ser coletada
                - `int_page_count`: Quantidade de página já coletada
                - `dic_url_per_domain`: Fila de URLs por domínio (explicado anteriormente)
                - `set_discovered_urls`: Conjunto de URLs descobertas, ou seja, que foi extraída em algum HTML e já adicionadas na fila - mesmo se já ela foi retirada da fila. A URL armazenada deve ser uma string.
                - `dic_robots_per_domain`: Dicionário armazenando, para cada domínio, o objeto representando as regras obtidas no `robots.txt`
        """
        self.str_usr_agent = str_usr_agent
        self.int_page_limit = int_page_limit
        self.int_depth_limit = int_depth_limit
        self.int_page_count = 0

        self.dic_url_per_domain = OrderedDict()
        self.set_discovered_urls = set()
        self.dic_robots_per_domain = {}
        self.arr_urls_seeds = arr_urls_seeds 


    @synchronized
    def count_fetched_page(self):
        """
            Contabiliza o número de paginas já coletadas
        """
        self.int_page_count += 1

    @synchronized
    def has_finished_crawl(self):
        """
            Verifica se finalizou a coleta
        """
        if(self.int_page_count > self.int_page_limit):
            return True
        return False


    @synchronized
    def can_add_page(self, obj_url, int_depth):
        """
            Retorna verdadeiro caso  profundade for menor que a maxima
            e a url não foi descoberta ainda
        """
        if int_depth >= self.int_depth_limit or obj_url in self.set_discovered_urls:
            return False
        else:
            return True

    @synchronized
    def add_new_page(self, obj_url, int_depth = 0):
        """
            Adiciona uma nova página
            obj_url: Objeto da classe ParseResult com a URL a ser adicionada
            int_depth: Profundidade na qual foi coletada essa URL
        """
        domain = obj_url.netloc
        if self.can_add_page(obj_url, int_depth):
            if not domain in self.dic_url_per_domain:
                self.dic_url_per_domain[Domain(domain, self.TIME_LIMIT_BETWEEN_REQUESTS)] = []

            self.dic_url_per_domain[domain].append((obj_url, int_depth))
            self.set_discovered_urls.add(obj_url)

            return True
        else:
            return False

    @synchronized
    def get_next_url(self):
        """
        Obtem uma nova URL por meio da fila. Essa URL é removida da fila.
        Logo após, caso o servidor não tenha mais URLs, o mesmo também é removido.
        """

        # returna null se a lista de dominios estiver vazia
        if not self.dic_url_per_domain:
            return None

        while(True):
            domainsToRemove = []
            urlToRemove = None
            url_depth = None
            for domain in self.dic_url_per_domain:
                if domain.is_accessible():
                    if not self.dic_url_per_domain[domain]:
                        domainsToRemove.append(domain)
                        continue
                    domain.accessed_now()
                    urlToRemove = domain
                    break
            
            # remove empty domains
            for domain in domainsToRemove:
                print("deleting domain:")
                print(domain)
                del self.dic_url_per_domain[domain]

            # remove url
            if urlToRemove:
                url_depth = self.dic_url_per_domain[urlToRemove][0]
    
            # wait and call next url again if no url is provided
            if not url_depth:
                time.sleep(5)
            else:
                break

        return url_depth

    @synchronized
    def can_fetch_page(self, obj_url):
        """
        Verifica, por meio do robots.txt se uma determinada URL pode ser coletada
        """
        answer = False
        
        if not obj_url.netloc in self.dic_robots_per_domain:
            parser = robotparser.RobotFileParser()
            parser.set_url(obj_url.geturl())
            parser.read()
            answer = parser.can_fetch(self.str_usr_agent, obj_url.geturl())
            self.dic_robots_per_domain[
                Domain(obj_url.netloc, self.TIME_LIMIT_BETWEEN_REQUESTS)] = parser
            
            
        return answer
