# Filtro Prebuy

App web (Streamlit) que recebe um extrato **CREATION** (Booking Report) ou **CHECK IN**
(Export) em Excel e devolve apenas as reservas cujo hotel está na lista de referência
correspondente:

- CREATION → comparado com a lista **YGG** (`data/hotel_list_ygg.csv`)
- CHECK IN → comparado com a lista **OMN** (`data/hotel_list_omn.csv`)

O tipo de arquivo é detectado automaticamente pelas colunas (não precisa escolher nada).

## Rodar localmente

```
pip install -r requirements.txt
streamlit run app.py
```

## Publicar no Streamlit Community Cloud (grátis, link compartilhável com a equipe)

1. Crie um repositório no GitHub (pode ser privado) e suba esta pasta:
   ```
   git remote add origin <URL_DO_SEU_REPO>
   git branch -M main
   git push -u origin main
   ```
2. Acesse https://share.streamlit.io e entre com sua conta GitHub.
3. Clique em "New app", escolha o repositório, branch `main` e arquivo `app.py`.
4. Clique em "Deploy". Em alguns minutos o app fica disponível em um link
   `https://<algo>.streamlit.app`, que pode ser compartilhado com a equipe.

## Atualizar as listas de referência (YGG / OMN)

As listas vêm da planilha `Filtro Prebuy_v26.xlsx`. Para atualizá-las, edite diretamente os
arquivos `data/hotel_list_ygg.csv` e `data/hotel_list_omn.csv` (mesmas colunas do original) e
faça commit/push novamente — o Streamlit Cloud redeploya sozinho a cada push.
