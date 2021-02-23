from typing import Optional
from fastapi import FastAPI

app = FastAPI()


@app.get("/")
def read_root():
    return {"Message": "back-end is on"}


@app.get("/discourses/{discourse_id}")
def fetch_discource(discourse_id: str):
    return {
        "discourseId": discourse_id,
        "items": [
            {
                "id": "n0",
                "userId": "B",
                "text": """Dear all, how can I convert NCBI Transcribed RefSeq records (with NM_ or NR_ accession prefix) into gene names / sybols or gene IDs?
                    Transcribed RefSeq IDs have the following format:
                    <br>NM_001007095.3
                    <br>NM_001014465.3
                    <br>NM_001014478.2
                    <br>NM_001014496.3""",
                "createdAt": "12344",
            },
            {
                "id": "n1",
                "userId": "A",
                "text": "If you are an R user, check out biomart. Very easy to use. Here is the biomaRt package from Bioconductor: https://bit.ly/2Bq4vOt",
                "createdAt": "12344",
                "parentId": "n0",
            },
            {
                "id": "n2",
                "userId": "B",
                "text": "R is too complicated, a tool that is more straightforward would be more appropriate",
                "createdAt": "12344",
                "parentId": "n1",
            },
            {
                "id": "n3",
                "userId": "C",
                "text": """There is a python library. Biopython is pretty good for moving between IDs and names. Here's an example of something similar: https://bit.ly/2PIVgkX""",
                "createdAt": "12344",
                "parentId": "n0",
            },
            {
                "id": "n4",
                "userId": "B",
                "text": """Although the python solution is simpler, it would be nice if there was something that did not require the knowledge of a programming language""",
                "createdAt": "12344",
                "parentId": "n3",
            },
        ],
    }


@app.get("/items/{item_id}")
def read_item(item_id: int, q: Optional[str] = None):
    return {"item_id": item_id, "q": q}
