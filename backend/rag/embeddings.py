def build_document_text(item):
    return (
        f"Title: {item['title']}\n"
        f"Organization: {item['organization']}\n"
        f"Claim: {item['claim']}\n"
        f"Mechanism: {item['mechanism']}\n"
        f"Metrics: {', '.join(item['metrics'])}\n"
        f"Keywords: {item.get('keywords', '')}"
    )
