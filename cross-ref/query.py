from habanero import Crossref
import time

# Initialize Crossref API client
cr = Crossref(mailto="hujoshi2@illinois.edu", timeout=50)

def get_issn(response):
    if "ISBN" in response["message"]:
        return response["message"]["ISBN"][0]
    return None

def get_citation_count(response):
    return response["message"]["is-referenced-by-count"]

def get_date_time(response):
    return "/".join([str(i) for i in response["message"]["indexed"]["date-parts"][0]])

def get_first_author_name(response):
    if "author" in response["message"] and len(response["message"]["author"]) > 0:
        output = None
        if "given" in response["message"]["author"][0]:
            output = response["message"]["author"][0]["given"]
        if  "family" in response["message"]["author"][0]:
            output += " " + response["message"]["author"][0]["family"]
        return output
    return None

def get_first_author_affiliation(response):
    if "author" in response["message"] and len(response["message"]["author"]) > 0:
        return response["message"]["author"][0]["affiliation"]
    return None

def fetch_metadata(doi):
    # Fetch complete metadata for a DOI
    return cr.works(ids=doi)

def fetch_journal_metadata(issn):
    # Fetch metadata for a journal using ISSN
    response = None
    start = time.time_ns()
    try :
        response = cr.journals(ids=issn, works=True)
    except Exception:
        response = None
    return (response, time.time_ns() - start)

def search_authors(author_name):
    # Search for author information based on name
    response = None
    start = time.time_ns()
    try :
        response = cr.works(query_author=author_name)
    except Exception:
        response = None
    return (response, time.time_ns() - start)

def fetch_affiliation_data(affiliation):
    # Search for works related to a specific affiliation
    response = None
    start = time.time_ns()
    try :
        response = cr.works(query_affiliation=affiliation)
    except Exception:
        response = None
    return (response, time.time_ns() - start)

def resolve_doi(doi):
    # Resolve a DOI to get the direct link
    response = None
    start = time.time_ns()
    try :
        response = cr.works(ids=doi)
    except Exception:
        response = None

    return (response, time.time_ns() - start)

def fetch_citations(doi):
    # Fetch citation data for a DOI
    response = cr.works(doi=doi)
    return response["message"]["items"][0]["is-referenced-by-count"]

def search_abstracts(query):
    # Search for abstracts related to a specific query
    return cr.works(query=query, select=["DOI", "abstract"])

# Example usage
doi = "10.48550/arXiv.1706.03762"
issn = "979-8-4007-0436-9"
author_name = "Jakob Uszkoreit"
affiliation = "University of Wisconsin-Madison"
query = "reinforcement learning"

# print("Fetching Metadata:")
# print(fetch_metadata(doi))

# print("\nFetching Journal Metadata:")
# print(fetch_journal_metadata(issn))

# print("\nSearching Authors:")
# print(search_authors(author_name))

# print("\nFetching Affiliation Data:")
# print(fetch_affiliation_data(affiliation))

# print("\nResolving DOI:")
# print(resolve_doi(doi))

# print("\nFetching Citation Data:")
# print(fetch_citations(doi))

# print("\nSearching Abstracts:")
# print(search_abstracts(query))

def get_base_validity_object():
    return {"resolvedDoi": None, \
        "extractedISBN": None, \
        "journalMetadata": None, \
        "firstAuthorName": None, \
        "firstAuthorInfo": None, \
        "firstAuthorAffiliation": None, \
        "firstAuthorAffiliationInfo": None, \
        "citationCount": None, \
        "dateTime": None}

foundResults = []
with open("doi.txt", "r") as file:
    dois = file.readlines()
    for doi in dois:
        # resolve doi
        temp = get_base_validity_object()
        author = None
        (output, timeDoi) = resolve_doi(doi.strip())
        temp["resolvedDoi"] = (output, timeDoi)
        if (output):
            # check issn and search journal metadata by issn            
            issnValue = get_issn(output)
            temp["extractedISBN"] = issnValue
            
            (journalMetadata, timeJournalMetadata) = fetch_journal_metadata(issnValue)
            temp["journalMetadata"] = (journalMetadata, timeJournalMetadata)
            
            # get first author name
            author = get_first_author_name(output)
            temp["firstAuthorName"] = author
            
            if (author):
                (authorInfo, authorInfoTime) = search_authors(author_name)
                temp["firstAuthorInfo"] = (authorInfo, authorInfoTime)
                
                affiliation = get_first_author_affiliation(output)
                temp["firstAuthorAffiliation"] = affiliation
                
                (affilitationInfo, affiliationInfoTime) = fetch_affiliation_data(affiliation)
                temp["firstAuthorAffiliationInfo"] = (affilitationInfo, affiliationInfoTime)
                
            temp["citationCount"] = get_citation_count(output)
            temp["dateTime"] = get_date_time(output)
        
        foundResults.append({doi : temp})
        print(doi.strip())
        time.sleep(2)
    
with open("stats.json", "w", encoding='utf-8') as file:
    file.write(str(foundResults))