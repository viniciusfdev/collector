from .page_fetcher import *
from .scheduler import *

if __name__ == "__main__":
    arr_urls_seeds = [
        "https://www.uol.com.br/",
        "https://www.globo.com/",
        "https://www.terra.com.br/",
        "https://www.msn.com/pt-br",
        "https://www.techtudo.com.br/",
        "https://canaltech.com.br/",
        "https://github.com/",
        "https://pt.stackoverflow.com/",
        "https://pt.wix.com/",
        "https://br.wordpress.com/",
        "https://www.pathofexile.com/",
        "https://www.reddit.com",
        "https://www.r7.com/",
        "https://www.twitch.tv",
        "https://www.estadao.com.br/",
        "https://www.ig.com.br/",
        "https://www.portaldoholanda.com.br/",
        "https://www.gazetadopovo.com.br/",
        "https://www.naosalvo.com.br/"
    ]


    arr_urls_seeds = [urlparse(str_url) for str_url in arr_urls_seeds]
    
    scheduler = Scheduler(str_usr_agent="vinigorbot",
                                int_page_limit=10,
                                int_depth_limit=3,
                                arr_urls_seeds=arr_urls_seeds)

   
    fetchers = []

    for id in range(5):
        fetchers.append(PageFetcher(scheduler, id))
        fetchers[id].start()
        
    for fetcher in fetchers:
        fetcher.join()


    # page_fetcher_2 = PageFetcher(scheduler)
    # page_fetcher_3 = PageFetcher(scheduler)
    # page_fetcher_4 = PageFetcher(scheduler)
    # page_fetcher_5 = PageFetcher(scheduler)