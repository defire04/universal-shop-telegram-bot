def safe_dict( row):
    if hasattr(row, 'keys'):
        return {key: row[key] for key in row.keys()}
    return dict(row) if isinstance(row, dict) else {}