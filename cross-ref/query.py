from habanero import Crossref
import time
import json 

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

def search_abstracts(query):
    # Search for abstracts related to a specific query
    response = None
    start = time.time_ns()
    try :
        response = cr.works(query=query, \
            select=["DOI", "abstract", "published"], \
            filter={"has-abstract": True, "from-pub-date": "2024-01-01", "until-pub-date": "2024-12-31"})
    except Exception:
        response = None

    return (response, time.time_ns() - start)

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

def evaluateDoiBasedQueries():
    with open("doi.txt", "r") as file:
        foundResults = []
        dois = file.readlines()
        for doi in dois:
            # resolve doi
            doi = doi.strip()
            temp = get_base_validity_object()
            author = None
            (output, timeDoi) = resolve_doi(doi)
            temp["resolvedDoi"] = {"output" : output, "time" : timeDoi}
            if (output):
                # check issn and search journal metadata by issn            
                issnValue = get_issn(output)
                temp["extractedISBN"] = issnValue
                
                if issnValue:
                    (journalMetadata, timeJournalMetadata) = fetch_journal_metadata(issnValue)
                    temp["journalMetadata"] = {"output": journalMetadata, "time" : timeJournalMetadata}
                
                # get first author name
                author = get_first_author_name(output)
                temp["firstAuthorName"] = author
                
                if (author):
                    (authorInfo, authorInfoTime) = search_authors(author)
                    temp["firstAuthorInfo"] = {"output": authorInfo, "time": authorInfoTime}
                    
                    affiliation = get_first_author_affiliation(output)
                    temp["firstAuthorAffiliation"] = affiliation
                    
                    (affilitationInfo, affiliationInfoTime) = fetch_affiliation_data(affiliation)
                    temp["firstAuthorAffiliationInfo"] = {"output": affilitationInfo, "time": affiliationInfoTime}
                    
                temp["citationCount"] = get_citation_count(output)
                temp["dateTime"] = get_date_time(output)
            
            foundResults.append(temp)
            print(doi.strip())
            time.sleep(2)
        
        with open("stats.json", "w", encoding='utf-8') as file:
            file.write(json.dumps(foundResults))
    
def evaluateTextSearch():
    with open("search.json", "w", encoding='utf-8') as file:
        queryItems = ["reinforcement learning", "fault injection", "distributed data processing", "Autonomous vehicle", "Network contention"]
        
        abstractResults = []
        
        for query in queryItems:
            (output, timeTaken) = search_abstracts(query)
            abstractResults.append({"query": query, "result": output, "time": timeTaken})
            print("Searched for ", {query})
            time.sleep(2)
        
        file.write(json.dumps(abstractResults))
        
if __name__ == '__main__':
    evaluateDoiBasedQueries()
    evaluateTextSearch()