from fastapi import FastAPI
from lucro_admin.api.routers import auth, users

app = FastAPI(title='Lucro Admin API')
app.include_router(users.router)
app.include_router(auth.router)

@app.get('/')
def home():
    boas_vindas = {
        'Olá usuário, seja bem-vindo ao Lucro Admin, um sistema financeiro'
        ' para gerenciamento das suas vendas'
    }
    return boas_vindas
