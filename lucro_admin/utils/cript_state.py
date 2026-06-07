def cript_state():
    import hashlib
    import logging
    import secrets
    from base64 import b64encode
    from datetime import datetime
    from urllib.parse import quote

    logger = logging.getLogger('lucroadmin.utils.cript_state')
    time = datetime.now()
    bytes_aleatórios = secrets.token_bytes(32)
    para_hash = f'{time}{bytes_aleatórios}'.encode('utf-8')
    hash_obj = hashlib.sha256(para_hash)
    state_bytes = hash_obj.digest()
    state_64 = b64encode(state_bytes).decode('utf-8')
    state_str = state_64.rstrip('=')
    state = quote(state_str, safe='')
    logger.info('Cript State | State cripitografado com sucesso')
    return state
