from datetime import datetime

class Domain():
	def __init__(self, nam_domain):
		self.nam_domain = nam_domain

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