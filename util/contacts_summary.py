import rdflib
from rdflib.namespace import FOAF
g = rdflib.Graph()
g.parse('data/contacts-imported.ttl', format='turtle')

# Count contacts
contacts = list(g.subjects(rdflib.RDF.type, FOAF.Person))
print(f'Total contacts: {len(contacts)}')

# Count different types of data
emails = len(list(g.subjects(FOAF.mbox, None)))
phones = len(list(g.subjects(FOAF.phone, None)))
websites = len(list(g.subjects(FOAF.homepage, None)))

print(f'Contacts with emails: {emails}')
print(f'Contacts with phone numbers: {phones}')
print(f'Contacts with websites: {websites}')
