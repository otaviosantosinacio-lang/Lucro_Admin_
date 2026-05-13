import logging

logger = logging.getLogger('lucroadmin.utils.code_string')


def code_string():
    string_code = str(input('Insira a url copiada do navegador: '))
    code_position = string_code.find('code=')
    code_ini = code_position + 5
    state_position = string_code.find('&state')
    state_ini = state_position + 7
    code = string_code[code_ini:state_position]
    state = string_code[state_ini:]
    logger.info('Code & State | Code e State foram retirados da URL')
    return {'code': code, 'state': state}
