import pydantic
from typing import Any, Dict, Iterable, List, Optional
from elasticsearch import Elasticsearch, helpers

# class ScholarshipFilterRequest(pydantic.BaseModel):
#     def __init__(self, **kwargs: Any):
#         super().__init__(**kwargs)

#         ## Nguyện vọng về học bổng - Đây là khi lần đầu vô trang tìm kiếm gợi ý học bổng.
#         self.desired_scholarship_type: Optional[list] = kwargs.get('Desired_Scholarship_Type')  # chính phủ, tư nhân, ...
#         self.desired_countries: Optional[list] = kwargs.get('Desired_Countries') # danh sách các quốc gia mong muốn
#         self.desired_funding_level: Optional[list] = kwargs.get('Desired_Funding_Level') # toàn phần, bán phần, cash...
#         self.desired_application_mode: Optional[list] = kwargs.get('Desired_Application_Mode') # thường niên, đột xuất, rolling...
#         self.desired_application_month: Optional[int] = kwargs.get('Desired_Application_Month') # tháng muốn nộp đơn
#         self.desired_field_of_study: Optional[list] = kwargs.get('Desired_Field_of_Study') # ngành học mong muốn

#         ## Khác - text box để ứng viên ghi chú thêm
#         self.notes: Optional[str] = kwargs.get('Notes') # ứng viên có thể ghi chú thêm gì đó như hoàn cảnh đặc biệt, khó khăn...

#     def filter_scholarships(self):
#         """Lọc học bổng dựa trên các tiêu chí trong form"""
        

def ensure_index(client: Elasticsearch, index: str) -> str:
    if not client.indices.exists(index=index):
        client.indices.create(
            index=index,
            settings={
                "analysis": {
                    "analyzer": {
                        "vi_std": {"type": "standard", "stopwords": "_none_"}
                    }
                }
            },
            mappings={
                "properties": {
                    "collection": {"type": "keyword"},
                    "__text": {"type": "text", "analyzer": "vi_std"},
                    "Scholarship_Name": {
                        "type": "text",
                        "analyzer": "vi_std",
                        "fields": {"raw": {"type": "keyword"}},
                    },
                    "Desired_Countries": {"type": "keyword"},
                    "Desired_Countries": {"type": "keyword"},
                    "Desired_Funding_Level": {"type": "keyword"},
                    "Desired_Application_Mode": {"type": "keyword"},
                    "Desired_Application_Month": {"type": "integer"},
                    "Desired_Field_of_Study": {"type": "keyword"},
                    "Notes": {
                        "type": "text", 
                        "analyzer": "vi_std"
                    },
                }
            },
        )
    return index

def _catch_all(doc: Dict[str, Any]) -> str:
    vals: List[str] = []

    def walk(x):
        if isinstance(x, dict):
            for v in x.values():
                walk(v)
        elif isinstance(x, list):
            for v in x:
                walk(v)
        else:
            if isinstance(x, (str, int, float, bool)):
                vals.append(str(x))

    walk(doc)
    return " ".join(vals)

def index_many(
    client: Elasticsearch,
    docs: Iterable[Dict[str, Any]],
    *,
    index: str,
    collection: Optional[str] = None,
    extra_fields: Optional[Dict[str, Any]] = None,  # dict chứa các field filter
) -> int:
    ensure_index(client, index)

    def gen():
        for d in docs:
            src = {**d, "__text": _catch_all(d)}

            # thêm collection nếu có
            if collection:
                src["collection"] = collection

            # thêm các filter field khác nếu có
            if extra_fields:
                for key, value in extra_fields.items():
                    if value is not None:  # chỉ thêm khi có giá trị
                        src[key] = value

            # Lấy id từ Firestore doc.id nếu có
            es_id = d.get("id") or d.get("doc_id")

            yield {"_op_type": "index", "_index": index, "_id": es_id, "_source": src}

    success, _ = helpers.bulk(client, gen(), stats_only=True)
    return success



def search_keyword(
    client: Elasticsearch,
    q: str,
    *,
    index: str,
    size: int = 10,
    offset: int = 0,
    collection: Optional[str] = None,
    extra_filters: Optional[Dict[str, Any]] = None,  # dict chứa các field filter
) -> Dict[str, Any]:
    ensure_index(client, index)

    must = [
        {
            "match": {
                "__text": {
                "query": q,
                "operator": "or",
                "fuzziness": "AUTO"
                }
            }
        }
    ]
    # thêm các filter field khác nếu có
    if extra_filters:
        for k, v in extra_filters.items():
            if v is not None:
                must.append({"term": {k: v}})
                
    # thêm collection nếu có
    if collection:
        must.append({"term": {"collection": collection}})

    res = client.search(
        index=index,
        query={"bool": {"must": must}},
        size=size,
        from_=offset,
    )
    hits = [
        {"id": h["_id"], "score": h["_score"], "source": h["_source"]}
        for h in res["hits"]["hits"]
    ]
    return {"total": res["hits"]["total"]["value"], "items": hits}