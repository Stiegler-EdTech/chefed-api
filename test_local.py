import coe
import json

def test_parse_job(desc_or_url):
    
    response = coe.parse_job_posting(desc_or_url=desc_or_url)
    print(response)
    print(json.dumps(response.json(), indent=2))
    

if __name__ == "__main__":
    desc_or_url="https://www.indeed.com/viewjob?jk=8b7c696f002362d0&from=shareddesktop_copy"
    test_parse_job(desc_or_url)
