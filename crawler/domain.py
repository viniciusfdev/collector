from collections import OrderedDict
from datetime import datetime

#chave objeto da classe Domain, Valor - lista de URLs
dicURLs = OrderedDict() 

class Domain():
	def __init__(self, nam_domain, int_time_limit_seconds):
		self.time_last_access = datetime(1970,1,1)
		self.nam_domain = nam_domain
		self.int_time_limit_seconds  = int_time_limit_seconds
	@property
	def time_since_last_access(self):
		return abs((datetime.now() - self.time_last_access).seconds)

	def accessed_now(self):
		self.time_last_access = datetime.now()

	def is_accessible(self):
		if self.time_since_last_access >= self.int_time_limit_seconds:
			return True
		return False

	def __hash__(self):
		return hash(self.nam_domain)

	def __eq__(self, domain):
		if isinstance(domain, Domain):
			return domain.nam_domain == self.nam_domain
		return domain == self.nam_domain

	def __str__(self):
		return self.nam_domain

	def __repr__(self):
		return f"{self.nam_domain}"