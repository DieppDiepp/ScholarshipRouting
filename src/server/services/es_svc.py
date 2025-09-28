from typing import Any, Dict, Iterable, List, Optional, Literal
from elasticsearch import Elasticsearch, helpers

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


def index_one(
    client: Elasticsearch,
    doc: Dict[str, Any],
    *,
    index: str,
    id: Optional[str] = None,
    collection: Optional[str] = None,
) -> str:
    ensure_index(client, index)

    payload = dict(doc)
    payload["__text"] = _catch_all(payload)
    if collection:
        payload["collection"] = collection

    # Ưu tiên dùng Firestore doc.id để tránh trùng
    es_id = id or doc.get("id") or doc.get("doc_id")

    res = client.index(index=index, id=es_id, document=payload)
    return res["_id"]


def index_many(
    client: Elasticsearch,
    docs: Iterable[Dict[str, Any]],
    *,
    index: str,
    collection: Optional[str] = None,
) -> int:
    ensure_index(client, index)

    def gen():
        for d in docs:
            src = {**d, "__text": _catch_all(d)}
            if collection:
                src["collection"] = collection

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

def filter_advanced(
    client: Elasticsearch,
    *,
    index: str,
    filters: List[Dict[str, Any]],
    collection: Optional[str] = None,
    inter_field_operator: Literal["AND", "OR"] = "AND",
    size: int = 10,
    offset: int = 0,
) -> Dict[str, Any]:
    """
    Hàm lọc tổng quát, hỗ trợ logic kết hợp linh hoạt và lọc theo collection.
    """
    ensure_index(client, index)

    # Xây dựng các mệnh đề lọc từ input `filters`
    clauses = []
    for f in filters:
        field = f["field"]
        values = f["values"]
        intra_operator = f.get("operator", "OR").lower()
        query_text = " ".join(map(str, values))
        
        clauses.append(
            {"match": {field: {"query": query_text, "operator": intra_operator}}}
        )
    
    query_body: Dict[str, Any] = {"bool": {}}
    
    # Logic kết hợp các mệnh đề lọc chính
    if clauses:
        if inter_field_operator == "AND":
            query_body["bool"]["filter"] = clauses
        else: # inter_field_operator == "OR"
            query_body["bool"]["should"] = clauses
            query_body["bool"]["minimum_should_match"] = 1
            
    # Luôn áp dụng bộ lọc `collection` như một điều kiện AND (nếu có)
    # bằng cách thêm nó vào mệnh đề 'filter'.
    # Đây là cách hiệu quả nhất để kết hợp.
    if collection:
        # Nếu 'filter' chưa tồn tại, tạo mới
        if "filter" not in query_body["bool"]:
            query_body["bool"]["filter"] = []
        # Thêm điều kiện lọc collection
        query_body["bool"]["filter"].append({"term": {"collection": collection}})


    # Trả về rỗng nếu không có bất kỳ điều kiện nào
    if not query_body["bool"]:
        return {"total": 0, "items": []}

    # Thực thi query
    res = client.search(
        index=index,
        query=query_body,
        size=size,
        from_=offset,
    )
    hits = [
        {"id": h["_id"], "score": h["_score"], "source": h["_source"]}
        for h in res["hits"]["hits"]
    ]
    return {"total": res["hits"]["total"]["value"], "items": hits}
